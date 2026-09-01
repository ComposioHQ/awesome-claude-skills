#!/usr/bin/env node
/**
 * db_upsert.mjs — 零依赖候选人库（jsonl）维护脚本（talent-search 专用）
 * 用法:
 *   node db_upsert.mjs <db.jsonl> upsert <candidates.json>    批量新增/更新候选人
 *   node db_upsert.mjs <db.jsonl> search <关键词> [关键词...]   按姓名/方向/公司/亮点等字段搜索（多关键词为 AND）
 *   node db_upsert.mjs <db.jsonl> stats                       库统计（总量/方向分布/状态/过期数）
 *
 * candidates.json 结构（与 gen_excel.mjs 输入兼容，可整体复用其 candidates 数组，另支持以下库字段）:
 * {
 *   "direction": "llm-pretraining-data",     // 本轮检索方向标签（可选）
 *   "verify_depth": "single" | "five",       // 验证深度，默认 single
 *   "status": "active" | "rejected",         // 默认 active；rejected 建议附 reject_reason
 *   "reject_reason": "学历不达标",            // status=rejected 时的作废原因
 *   "last_verified": "2026-09-01",           // 最后验证日期，缺省取当天
 *   "sources": ["https://..."],              // 核实证据 URL 列表（可选）
 *   "candidates": [
 *     { "name": "...", "education": "...", "experience": "...", "homepage": "...",
 *       "github": "...", "papers": "...", "labs": "...", "highlight": "...",
 *       "notes": "...", "current": "公司/职位（可选，缺省取 experience 首行）" }
 *   ]
 * }
 * 也接受裸数组 [ {...}, {...} ]。
 *
 * 去重键（优先级）: github URL > homepage URL > 姓名完全一致（URL 忽略末尾斜杠与大小写）
 * upsert 语义: 命中同键记录时，输入中的非空字段覆盖旧字段，空字段保留旧值；
 *              last_verified / verify_depth / direction 总是更新；status 仅在显式给出时更新。
 * 库文件不存在则自动创建。注意：库含个人信息，切勿提交进 git（.gitignore 已排除 talent-research/）。
 */

import { readFileSync, writeFileSync, existsSync } from 'node:fs';

const USAGE = '用法: node db_upsert.mjs <db.jsonl> upsert <candidates.json> | search <关键词...> | stats';
const STALE_DAYS = 90;

const die = (msg) => { console.error('错误: ' + msg); console.error(USAGE); process.exit(1); };

function today() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function daysAgo(dateStr) {
  const t = Date.parse(dateStr);
  if (Number.isNaN(t)) return Infinity;
  return Math.floor((Date.now() - t) / 86400000);
}

const normUrl = (u) => (typeof u === 'string' && u.trim() && !u.includes('未获取') ? u.trim().replace(/\/+$/, '').toLowerCase() : '');

function loadDb(path) {
  if (!existsSync(path)) return [];
  const out = [];
  for (const line of readFileSync(path, 'utf8').split('\n')) {
    const s = line.trim();
    if (!s) continue;
    try { out.push(JSON.parse(s)); } catch { console.warn(`警告: 跳过无法解析的行: ${s.slice(0, 50)}...`); }
  }
  return out;
}

function saveDb(path, records) {
  writeFileSync(path, records.map((r) => JSON.stringify(r)).join('\n') + '\n', 'utf8');
}

function keyOf(rec) {
  return normUrl(rec.github) || normUrl(rec.homepage) || (rec.name ? rec.name.trim() : '') || '';
}

function loadInput(path) {
  const data = JSON.parse(readFileSync(path, 'utf8'));
  const list = Array.isArray(data) ? data : Array.isArray(data.candidates) ? data.candidates : null;
  if (!list) die(`输入文件 ${path} 既不是数组也不含 candidates 数组`);
  const meta = Array.isArray(data) ? {} : data;
  return { list, meta };
}

function toRecord(cand, meta) {
  const rec = { ...cand };
  if (!rec.current) {
    const first = String(rec.experience || '').split('\n').find((l) => l.trim());
    if (first) rec.current = first.trim();
  }
  if (!rec.name) die('候选记录缺少 name 字段');
  rec.direction = meta.direction || rec.direction || '';
  rec.verify_depth = meta.verify_depth || rec.verify_depth || 'single';
  rec.status = meta.status || rec.status || 'active';
  if (rec.status === 'rejected' && meta.reject_reason) rec.reject_reason = meta.reject_reason;
  rec.last_verified = meta.last_verified || rec.last_verified || today();
  if (meta.sources || rec.sources) rec.sources = [...new Set([...(rec.sources || []), ...(meta.sources || [])])];
  return rec;
}

function upsert(dbPath, inputPath) {
  const { list, meta } = loadInput(inputPath);
  const records = loadDb(dbPath);
  const index = new Map(records.map((r, i) => [keyOf(r), i]));
  let added = 0, updated = 0;
  for (const cand of list) {
    const rec = toRecord(cand, meta);
    const k = keyOf(rec);
    if (!k) die(`候选 ${rec.name} 缺少可用的去重键（github/homepage/name 均为空）`);
    if (index.has(k)) {
      const old = records[index.get(k)];
      for (const [f, v] of Object.entries(rec)) {
        if (v === '' || v === undefined || v === null) continue;
        if (f === 'status' && !cand.status && !meta.status) continue; // status 未显式给出则保留旧值
        old[f] = v;
      }
      updated++;
    } else {
      records.push(rec);
      index.set(k, records.length - 1);
      added++;
    }
  }
  saveDb(dbPath, records);
  console.log(`已写入 ${dbPath}: 新增 ${added}，更新 ${updated}，总库 ${records.length} 人`);
}

function search(dbPath, keywords) {
  if (!keywords.length) die('search 需要至少一个关键词');
  const kws = keywords.map((k) => k.toLowerCase());
  const records = loadDb(dbPath);
  const fields = ['name', 'direction', 'current', 'highlight', 'education', 'experience', 'papers', 'labs', 'notes', 'maimai'];
  const hits = records.filter((r) => kws.every((k) => fields.some((f) => String(r[f] || '').toLowerCase().includes(k))));
  if (!hits.length) { console.log(`未命中（关键词: ${keywords.join(' + ')}），库共 ${records.length} 人`); return; }
  console.log(`命中 ${hits.length} / ${records.length} 人（关键词: ${keywords.join(' + ')}）\n`);
  for (const r of hits) {
    const stale = daysAgo(r.last_verified) > STALE_DAYS ? ' ⚠过期' : '';
    const status = r.status === 'rejected' ? ` [作废: ${r.reject_reason || '未注明'}]` : '';
    console.log(`- ${r.name}${status}${stale}`);
    console.log(`  现职: ${r.current || '未获取'} ｜ 方向: ${r.direction || '-'} ｜ 验证: ${r.verify_depth || '-'} @ ${r.last_verified || '-'}`);
    if (r.github) console.log(`  GitHub: ${r.github}`);
    if (r.homepage) console.log(`  主页: ${r.homepage}`);
  }
}

function stats(dbPath) {
  const records = loadDb(dbPath);
  if (!records.length) { console.log(`库为空（${dbPath}）`); return; }
  const byDir = {}, byStatus = { active: 0, rejected: 0 };
  let stale = 0;
  for (const r of records) {
    const d = r.direction || '（未标注）';
    byDir[d] = (byDir[d] || 0) + 1;
    byStatus[r.status === 'rejected' ? 'rejected' : 'active']++;
    if (daysAgo(r.last_verified) > STALE_DAYS) stale++;
  }
  console.log(`库 ${dbPath}: 共 ${records.length} 人`);
  console.log(`状态: active ${byStatus.active} / rejected ${byStatus.rejected}`);
  console.log(`验证过期（>${STALE_DAYS}天）: ${stale} 人`);
  console.log('方向分布:');
  for (const [d, n] of Object.entries(byDir).sort((a, b) => b[1] - a[1])) console.log(`  ${d}: ${n}`);
}

const [dbPath, cmd, ...rest] = process.argv.slice(2);
if (!dbPath || !cmd) die('缺少参数');
if (cmd === 'upsert') { if (!rest[0]) die('upsert 需要输入 JSON 文件路径'); upsert(dbPath, rest[0]); }
else if (cmd === 'search') search(dbPath, rest);
else if (cmd === 'stats') stats(dbPath);
else die(`未知子命令: ${cmd}`);
