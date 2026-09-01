#!/usr/bin/env node
/**
 * radar_scan.mjs — 主动雷达扫描脚本（talent-search 专用，零依赖，Node ≥ 18 内置 fetch）
 * 用法:
 *   node radar_scan.mjs <config.json>
 *
 * 做两件事（只碰公开信息）:
 *   1. GitHub 通道: 拉取配置中各 org 的 public members，与上次快照 diff → 新成员即人才流动信号
 *   2. 论文通道: OpenAlex API 按方向关键词查最新论文（含一作与机构），与上次快照 diff → 新论文（一作即候选线索）
 *      （不直接调 arXiv API：export.arxiv.org 的 https 在部分网络环境不可达，OpenAlex 数据覆盖 arXiv 且无需认证）
 *
 * config.json:
 * {
 *   "direction": "llm-pretraining-data",          // 方向标签（写进报告）
 *   "keywords": ["pretraining data", "data curation"],  // 论文检索词（英文短语）
 *   "orgs": ["QwenLM", "deepseek-ai", "zai-org"],       // GitHub org 列表
 *   "paperMax": 30,                                // 每个关键词拉取条数上限
 *   "dataDir": "talent-research/_radar"            // 快照与报告目录（相对 cwd）
 * }
 *
 * 产物:
 *   <dataDir>/snapshot.json            快照（orgs 成员 + 论文 id 集合 + lastRun）
 *   <dataDir>/radar-YYYY-MM-DD.md      本次雷达报告（新成员 / 新论文 / 后续动作建议）
 * 首次运行建立基线（不做 diff，只记录现状）；此后每次运行为增量 diff。
 * GitHub API 未认证限额 60 次/小时；OpenAlex 免认证限额宽松（礼貌池建议带 mailto）。
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const MAILTO = 'talent-search-radar@example.com';
const die = (msg) => { console.error('错误: ' + msg); process.exit(1); };
const today = () => new Date().toISOString().slice(0, 10);

function loadConfig(path) {
  if (!existsSync(path)) die(`config 不存在: ${path}`);
  const cfg = JSON.parse(readFileSync(path, 'utf8'));
  for (const k of ['direction', 'keywords', 'orgs']) if (!cfg[k]) die(`config 缺少 ${k}`);
  cfg.dataDir = cfg.dataDir || 'talent-research/_radar';
  cfg.paperMax = cfg.paperMax || 30;
  return cfg;
}

async function githubJson(url) {
  const res = await fetch(url, { headers: { 'User-Agent': 'talent-search-radar', Accept: 'application/vnd.github+json' } });
  if (!res.ok) throw new Error(`GitHub ${res.status}: ${url}`);
  return res.json();
}

async function fetchOrgMembers(org) {
  const all = [];
  for (let page = 1; page <= 3; page++) {
    const batch = await githubJson(`https://api.github.com/orgs/${org}/public_members?per_page=100&page=${page}`);
    if (!Array.isArray(batch) || !batch.length) break;
    all.push(...batch.map((u) => ({ login: u.login, profile: u.html_url })));
    if (batch.length < 100) break;
  }
  return all;
}

async function fetchPapers(keyword, max) {
  // 过滤: 短语匹配标题/摘要 + 计算机科学领域(concepts.id C41008148) + 仅论文/预印本(排除数据集、书籍章节)
  const filter = `title_and_abstract.search:${encodeURIComponent(`"${keyword}"`)},concepts.id:C41008148,type:article|preprint`;
  const url = `https://api.openalex.org/works?filter=${filter}&sort=publication_date:desc&per-page=${max}&select=id,doi,title,publication_date,authorships&mailto=${MAILTO}`;
  const res = await fetch(url, { headers: { 'User-Agent': 'talent-search-radar' } });
  if (!res.ok) throw new Error(`OpenAlex ${res.status}`);
  const data = await res.json();
  const papers = [];
  for (const w of data.results || []) {
    const as = w.authorships || [];
    const authors = as.map((a) => a.author?.display_name).filter(Boolean);
    const first = as.find((a) => a.author_position === 'first')?.author?.display_name || authors[0] || '未知';
    const insts = [...new Set(as.flatMap((a) => (a.institutions || []).map((i) => i.display_name)).filter(Boolean))].slice(0, 3);
    papers.push({ id: w.doi || String(w.id), title: w.title || '(无题)', published: (w.publication_date || '').slice(0, 10), authors, first, insts });
  }
  return papers;
}

const [configPath] = process.argv.slice(2);
if (!configPath) die('用法: node radar_scan.mjs <config.json>');

const cfg = loadConfig(configPath);
mkdirSync(cfg.dataDir, { recursive: true });
const snapPath = join(cfg.dataDir, 'snapshot.json');
const snapshot = existsSync(snapPath) ? JSON.parse(readFileSync(snapPath, 'utf8')) : null;
const baseline = !snapshot;
const TODAY = today();
const CUTOFF30 = new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10);

const report = [];
const newSnap = { lastRun: TODAY, orgs: {}, papers: {} };
const signals = { members: [], papers: [] };

for (const org of cfg.orgs) {
  try {
    const members = await fetchOrgMembers(org);
    newSnap.orgs[org] = members;
    if (!baseline) {
      const oldLogins = new Set((snapshot.orgs?.[org] || []).map((m) => m.login));
      const fresh = members.filter((m) => !oldLogins.has(m.login));
      if (fresh.length) signals.members.push({ org, fresh });
    }
    console.log(`GitHub ${org}: ${members.length} 名公开成员`);
  } catch (e) {
    console.warn(`警告: GitHub ${org} 拉取失败（${e.message}），跳过`);
    newSnap.orgs[org] = snapshot?.orgs?.[org] || [];
  }
}

const seenIds = new Set();
const seenTitles = new Set();
const allPapers = [];
for (let i = 0; i < cfg.keywords.length; i++) {
  const kw = cfg.keywords[i];
  if (i > 0) await new Promise((r) => setTimeout(r, 1000));
  try {
    const papers = await fetchPapers(kw, cfg.paperMax);
    for (const p of papers) {
      const titleKey = p.title.toLowerCase().replace(/[^a-z0-9]/g, '');
      if (seenIds.has(p.id) || seenTitles.has(titleKey)) continue; // 按标题去重（同一工作的多版本 DOI）
      seenIds.add(p.id);
      seenTitles.add(titleKey);
      allPapers.push({ ...p, keyword: kw });
    }
    console.log(`论文 "${kw}": ${papers.length} 篇`);
  } catch (e) {
    console.warn(`警告: 论文 "${kw}" 拉取失败（${e.message}），跳过`);
  }
}
for (const p of allPapers) newSnap.papers[p.id] = { title: p.title, published: p.published };

// 有效论文窗口: 30 天前 ~ 今天（排除未来日期的脏数据）
const inWindow = (p) => p.published && p.published <= TODAY && p.published >= CUTOFF30;
if (!baseline) {
  const prevIds = new Set(Object.keys(snapshot.papers || {}));
  signals.papers = allPapers
    .filter((p) => !prevIds.has(p.id) && inWindow(p) && p.published >= snapshot.lastRun)
    .sort((a, b) => b.published.localeCompare(a.published));
}

report.push(`# 人才雷达报告 ${TODAY}（${cfg.direction}）`);
report.push('');
report.push(baseline ? '> 首次运行：建立基线，本次不做 diff。' : `> 上次扫描：${snapshot.lastRun} ｜ 本次为增量扫描`);
report.push('');
report.push(`## GitHub org 公开成员${baseline ? '（基线）' : ''}`);
report.push('');
for (const [org, members] of Object.entries(newSnap.orgs)) {
  report.push(`- **${org}**: ${members.length} 人`);
}
if (!baseline && signals.members.length) {
  report.push('');
  report.push('### 新增成员（人才流动信号）');
  report.push('');
  for (const { org, fresh } of signals.members) {
    for (const m of fresh) report.push(`- ${org} 新增: [${m.login}](${m.profile})`);
  }
}
report.push('');
report.push(`## 方向论文${baseline ? '（基线，近 30 天）' : `（自 ${snapshot.lastRun} 新增）`}`);
report.push('');
const paperList = baseline ? allPapers.filter(inWindow).sort((a, b) => b.published.localeCompare(a.published)).slice(0, 20) : signals.papers;
if (!paperList.length) report.push('- 无新增');
for (const p of paperList) {
  report.push(`- ${p.published} ｜ **一作 ${p.first}** ｜ ${p.insts.join(' / ') || '机构未知'} ｜ ${p.title}`);
  if (p.id.startsWith('http')) report.push(`  ${p.id}`);
}
report.push('');
report.push('## 后续动作建议');
report.push('');
if (baseline) {
  report.push('- 基线已建立。下周起本报告只列增量：org 新成员 + 方向新论文（一作即候选线索）。');
} else {
  report.push('- 新成员与论文一作 → 按 talent-search 流程单轮验证后 upsert 进候选人库（db_upsert.mjs）');
  report.push('- 相关经验（哪个 org/关键词信号密度高）→ 追加进 _lessons/');
  report.push(`- 本轮新信号: org 新增 ${signals.members.reduce((n, s) => n + s.fresh.length, 0)} 人 ｜ 新论文 ${signals.papers.length} 篇`);
}
report.push('');

const reportPath = join(cfg.dataDir, `radar-${TODAY}.md`);
writeFileSync(reportPath, report.join('\n'), 'utf8');
writeFileSync(snapPath, JSON.stringify(newSnap, null, 2), 'utf8');
console.log(`\n已产出: ${reportPath}`);
console.log(`快照已更新: ${snapPath}`);
