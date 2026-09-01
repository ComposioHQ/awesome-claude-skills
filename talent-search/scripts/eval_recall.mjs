#!/usr/bin/env node
/**
 * eval_recall.mjs — golden set 评测脚本（talent-search 专用，零依赖）
 * 用法:
 *   node eval_recall.mjs <golden.jsonl> <result.json> [result2.json ...]
 *   及格线可用环境变量调整: RECALL_MIN=0.9 node eval_recall.mjs ...（默认 0.8）
 *
 * golden.jsonl 每行一条（从历次已验证产出中挑选的「标准答案」候选人）:
 *   {"name": "...", "github": "...", "homepage": "...", "education": "...", "current": "...", "direction": "..."}
 *   github/homepage 至少有一项与真实产出一致，name 为必填；education/current 为期望事实（可空）
 *
 * result.json: {"candidates": [...]} 或裸数组（与 gen_excel.mjs 输入同构，可传多份合并计分）
 *
 * 指标:
 *   recall      = 命中 golden 人数 / golden 总数（多份 result 合并去重后计算）
 *   字段准确率  = 命中者中 education / current 与 golden 一致（归一化互含匹配）的占比（golden 该字段非空才计入）
 *   misses      = 未命中的 golden 条目名单
 *   extras      = result 中不在 golden 内的条目数（信息项：golden 非穷尽，不扣分）
 *
 * 退出码: recall ≥ 及格线 → 0；否则 → 1（可接入后续流程做改版门禁）
 */

import { readFileSync, existsSync } from 'node:fs';

const USAGE = '用法: node eval_recall.mjs <golden.jsonl> <result.json> [result2.json ...]';
const RECALL_MIN = parseFloat(process.env.RECALL_MIN || '0.8');

const die = (msg) => { console.error('错误: ' + msg); console.error(USAGE); process.exit(2); };

const normUrl = (u) => (typeof u === 'string' && u.trim() && !u.includes('未获取') ? u.trim().replace(/\/+$/, '').toLowerCase() : '');
const normText = (s) => String(s || '').replace(/\s+/g, '').toLowerCase();

function keyOf(rec) {
  return normUrl(rec.github) || normUrl(rec.homepage) || (rec.name ? rec.name.trim() : '');
}

function looseMatch(a, b) {
  const na = normText(a), nb = normText(b);
  if (!na || !nb) return null; // 任一为空不计入
  return na === nb || na.includes(nb) || nb.includes(na);
}

function loadGolden(path) {
  if (!existsSync(path)) die(`golden set 文件不存在: ${path}`);
  const out = [];
  for (const line of readFileSync(path, 'utf8').split('\n')) {
    const s = line.trim();
    if (!s) continue;
    let rec;
    try { rec = JSON.parse(s); } catch { console.warn(`警告: 跳过无法解析的 golden 行: ${s.slice(0, 50)}...`); continue; }
    if (!rec.name) { console.warn(`警告: 跳过缺少 name 的 golden 行`); continue; }
    if (!normUrl(rec.github) && !normUrl(rec.homepage)) console.warn(`警告: golden 条目 ${rec.name} 无 github/homepage，将仅按姓名匹配`);
    out.push(rec);
  }
  if (!out.length) die(`golden set 为空: ${path}`);
  return out;
}

function loadResults(paths) {
  const map = new Map();
  for (const p of paths) {
    if (!existsSync(p)) die(`result 文件不存在: ${p}`);
    const data = JSON.parse(readFileSync(p, 'utf8'));
    const list = Array.isArray(data) ? data : Array.isArray(data.candidates) ? data.candidates : null;
    if (!list) die(`${p} 既不是数组也不含 candidates 数组`);
    for (const c of list) {
      const k = keyOf(c);
      if (k && !map.has(k)) map.set(k, c);
    }
  }
  return map;
}

const [goldenPath, ...resultPaths] = process.argv.slice(2);
if (!goldenPath || !resultPaths.length) die('缺少参数');

const golden = loadGolden(goldenPath);
const results = loadResults(resultPaths);

let hit = 0;
const misses = [];
let eduTotal = 0, eduOk = 0, curTotal = 0, curOk = 0;

for (const g of golden) {
  const r = results.get(keyOf(g));
  if (!r) { misses.push(g.name); continue; }
  hit++;
  const edu = looseMatch(r.education, g.education);
  if (edu !== null) { eduTotal++; if (edu) eduOk++; }
  const cur = looseMatch(r.current || String(r.experience || '').split('\n')[0], g.current);
  if (cur !== null) { curTotal++; if (cur) curOk++; }
}

const recall = hit / golden.length;
const eduAcc = eduTotal ? eduOk / eduTotal : null;
const curAcc = curTotal ? curOk / curTotal : null;
const extras = results.size - hit;

const pct = (x) => (x === null ? '—' : (x * 100).toFixed(1) + '%');

console.log(`golden set: ${golden.length} 人 ｜ result: ${results.size} 人（${resultPaths.length} 份合并去重）`);
console.log(`recall: ${hit}/${golden.length} = ${pct(recall)}（及格线 ${pct(RECALL_MIN)}）`);
console.log(`字段准确率（命中者）: 学历 ${pct(eduAcc)}（${eduOk}/${eduTotal}） ｜ 现职 ${pct(curAcc)}（${curOk}/${curTotal}）`);
console.log(`extras（result 中 golden 外条目，信息项）: ${Math.max(0, extras)}`);
if (misses.length) {
  console.log('misses（未命中）:');
  for (const m of misses) console.log(`  - ${m}`);
}
if (recall < RECALL_MIN) {
  console.error(`\n✗ recall ${pct(recall)} 低于及格线 ${pct(RECALL_MIN)}，改版不予合入`);
  process.exit(1);
}
console.log(`\n✓ 达标：recall ≥ ${pct(RECALL_MIN)}`);
