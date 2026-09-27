#!/usr/bin/env node
// check-report.mjs — 蓝军/第三方「缺陷总表」机检器（v2.5.0）
//
// 为什么需要："必须实证"写进 SKILL.md 也只是一句**散文约束**——模型想让
// 自己的高危结论有分量时，会直接声称"我跑过了"而根本没跑。v2.2 把定级与
// 实测绑定（未经实测不得定高危），而绑定规则若没有机器兜底，只会退化成
// 又一句口号。本检查只干一件事：让"编造的实测"变成**可被发现**的事。
//
// v2.3 修掉的一个真实绕过（外部评审 R1）：早先版本用"全文出现『复现命令』
// 四个汉字的次数 ≥ 声称实测的条数"当证据计数。于是一份正文里只写了
// `## 复现命令` 空标题、一条命令都没有的报告能判绿——**计数型校验天然可被
// 凑字数**，改成按条目就近匹配：每个 🔴/🟠 实测条目必须有自己的展开段落，
// 段落里的「复现命令」后面必须真的跟着一段命令（行内代码或围栏块 + 内容）。
//
// v2.4 修掉的两个绕过（外部评审第二轮 T1/T2）：v2.3 只验"有没有"，不验"像不像"，
// 于是 ① 行内代码只要 ≥3 个字符就算命令——写 `\`见附录\`` 即可盖章；② 取证窗口写成
// `end + 9`，命令可以塞进紧随其后的附录里被全部高危共用。**教训是同一类**：
// "存在某段代码块"这种判据永远能被占位词喂饱，判据必须落到内容形状上
// （commandish：命令名 + 参数，或含管道/重定向/路径），窗口必须封在本条目自己名下。
//
// v2.5 修掉的三个绕过（外部评审第三轮 U1/U2/U6）：v2.4 的"形状"判据其实只挡住了
// **中文**占位词——`see appendix`、`Run the script in the appendix…`、一段源码、
// 一行 npm 报错日志全都能盖章（U1/U6），而真命令 `make`、`pytest` 反被判红（U2）。
// **教训又升了一级**：占位词是语义问题，形状判据换个自然语言就失效；能收敛的只有
// 词法——首 token 必须是可执行程序名（或 `./x`、`x.sh` 这类带路径的脚本），
// 认不出的名字必须带一个参数形状。判据强度本身还配了 4 条"削弱型"突变靶子（P11–P14），
// 否则"退回旧实现"之外的第三种破坏方式无人看守（评审 U3）。
//
// 只管 🔴/🟠，不管 🟡（评审 R4）：模板规定 🟡 不展开，若要求 🟡 也贴命令，
// 完全合规的产出会被判红——而误报会让人直接关掉检查，比漏报更糟。
//
// 防"永远绿"（本项目核心信条）：找不到总表 / 总表零数据行 / 一个级别 emoji
// 都没解析到，一律判失败——提取错位导致的静默通过比报错危险得多。
//
// 用法：node check-report.mjs <报告.md> [更多报告.md]
// 退出码：0 = 全部合规；1 = 存在缺陷；2 = 用法错误（无参数）——用法错误不是检查失败
//
// 格式与 references/prompt-templates.md 模板 1/模板 2 的六列总表对齐：
//   | 编号 | 级别 | 定级依据 | 一句话 | 维度 | 位置（文件:行号） |
// 定级依据取值只能是 `实测` 或 `推理·待实测`；展开条目标签为 `复现命令`。

import { readFileSync } from "node:fs";

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error("用法：node check-report.mjs <报告.md> [更多报告.md]");
  process.exit(2);
}

const HIGH = ["🔴", "🟠"];
const LEVELS = ["🔴", "🟠", "🟡"];
const EMPTY_LOC = new Set(["", "-", "--", "...", "…", "N/A", "n/a", "TBD", "待补"]);

const splitRow = (line) =>
  line.replace(/^\s*\|/, "").replace(/\|\s*$/, "").split("|").map((c) => c.trim());
const isSep = (c) => c.length > 0 && c.every((x) => x === "" || /^:?-{2,}:?$/.test(x));

// 围栏代码块内的行不参与总表定位（模板本身就是被 ``` 包住的正文）；
// 但「复现命令」计数**要**连围栏内一起算——命令输出本来就是贴在围栏里的。
function fencedMask(lines) {
  const mask = new Array(lines.length).fill(false);
  let open = false;
  for (let i = 0; i < lines.length; i++) {
    if (/^\s*(```|~~~)/.test(lines[i])) open = !open;
    mask[i] = open;
  }
  return mask;
}

const HEADING = /^(\s{0,3})(#{1,6})\s+/;

// 条目小节的起点：`### B1 · 🔴 …`（允许前置级别 emoji）或 `**B1**` 开头的行。
// 只认"紧跟标题标记的 id"，否则 `### 修复 B1 引入的问题` 会被误当成 B1 的小节。
// id 后面不许再粘字母数字，否则 B1 会误命中 B10。
// id 必须先转义：编号写成 `B(1` 会让 RegExp 抛 Unterminated group（评审 T6，实测崩栈），
// 写成 `P(1)` 则 `(1)` 变成捕获组、静默匹配不上，反过来误报"没有展开段落"。
const reEscape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const anchorRe = (id) =>
  new RegExp(
    `^(?:\\s{0,3}#{1,6}\\s+(?:[\\u{1F300}-\\u{1FAFF}✅❌⚠️]\\s*)?|\\s*(?:[-*]\\s+)?\\*\\*)` +
      `${reEscape(id)}(?![0-9A-Za-z])`,
    "u"
  );

// 围栏块配对：opener -> closer（未闭合则到文末）。
// 只按"行首是否为围栏标记"逐行开合，因此块体可以被安全切片——这是下面
// fenceCommand 能在工作窗口内识别一个跨窗口边界的块的前提（评审 T7：
// 旧实现把"闭合围栏也必须落在窗口内"当条件，围栏块一超过 8 行就恒判无证据）。
function fencePairs(lines) {
  const pairs = new Map();
  const stack = [];
  for (let i = 0; i < lines.length; i++) {
    if (!/^\s*(```|~~~)/.test(lines[i])) continue;
    if (stack.length) pairs.set(stack.pop(), i);
    else stack.push(i);
  }
  for (const o of stack) pairs.set(o, lines.length);
  return pairs;
}

// 「像一条命令」判据（第三版，评审 U1/U2/U6）。
// v2.4 版只看形状（纯 ASCII + 多 token + 首 token 含点或斜杠），于是
// `see appendix`、`notes.md`、一段源码、一行 npm 报错日志全都能盖章（U1/U6），
// 而真命令 `make` / `pytest` 反被判红（U2）。占位词是**语义**问题，形状判据封不死，
// 所以改成：首 token 必须是常见可执行程序名（或 `./x`、`/usr/bin/x`、`install.sh` 这类带路径的脚本），
// 程序名之后还要跟得上参数/元字符/路径。宁可错杀不认识的裸命令，也不放过编造的英文短语——
// 报错信息会把这条要求原样写明白。
const EXEC = new Set(`
  node npm npx pnpm yarn bun deno tsx ts-node
  python python3 pip pip3 uv poetry pytest tox ruff mypy black flake8
  go cargo rustc make cmake gcc g++ clang meson ninja
  java javac kotlin kotlinc scala mvn gradle dotnet swift
  php composer ruby gem bundle rspec rails
  git gh glab svn hg
  bash sh zsh dash pwsh powershell cmd bat fish
  cat head tail less more wc sort uniq cut tr sed awk grep egrep fgrep rg fd find xargs
  ls ll pwd cd echo printf test diff patch comm
  tar zip unzip gzip gunzip xz 7z rsync scp cp mv rm mkdir touch chmod chown ln
  curl wget httpie jq yq awk
  docker podman nerdctl kubectl helm kind minikube terraform pulumi ansible
  openssl ssh sftp nc dig nslookup ping traceroute
  mysql psql sqlite3 redis-cli mongo
  tsc eslint prettier stylelint vitest jest mocha playwright cypress karma
  code idea vim vi nano emacs touch
  convert magick ffmpeg ffprobe imagemagick
  systemctl service journalctl ps kill killall top htop lsof df du free id whoami
  apt apt-get yum dnf pacman brew choco scoop winget
  ldd nm objdump gdb valgrind strace ltrace
  tree file which whereis man history alias env print
`.trim().split(/\s+/));
// 这些是"前缀命令"，本身不说明跑了什么，要看它后面那个 token
const WRAPPER = new Set(["sudo", "doas", "env", "time", "nohup", "command", "builtin"]);
const IDENT = /^[a-z][a-z0-9]*(?:[-+.][a-z0-9]+)*$/;
// `./x` `/usr/bin/x` `~/.local/bin/x` `foo.sh` `run.ps1` `main.py` `build.bat`
const PATHY = /^(?:[.~]?\/[\w.\/+-]+|[\w.+-]+\.(?:sh|bash|ps1|py|mjs|cjs|js|ts|rb|pl|php|bat|cmd|exe))$/;
// 参数形状：flag、路径、`~/x`。源码片段里的 `(x` / `===` / `{` 都不在此列
const ARGISH = /^[-./~@]/;
// 行首就长得像**程序输出**的（报错、traceback、栈帧），不是命令
const LOOKS_LIKE_OUTPUT =
  /^(?:[\w.$-]*Error\b|Traceback|panic:|fatal:|Exception\b|npm\s+ERR!|ERR!|\bat\s[\w.$<>]+\()/;

// 「必须是纯 ASCII」这条检查的作用是把 `见附录`、`make （见下一节）` 这类**说明文字**挡在证据之外。
// 但它不能连引号里的内容一起管：`sed -i 's/正文 173 行/正文 180 行/' README.md` 是我们自己 README
// 里的一条真命令，参数天生带中文。所以只看**引号之外**的字符（评审 U2 的误报面）。
function asciiOutsideQuotes(t) {
  return /^[\x20-\x7e]+$/.test(t.replace(/"[^"]*"|'[^']*'|`[^`]*`/g, '""'));
}

function commandish(raw) {
  const t = String(raw).trim().replace(/^[$>]\s+/, "").trim();
  if (!t) return false;
  if (!asciiOutsideQuotes(t)) return false; // 引号之外含中文/省略号 → 是说明文字，不是命令
  if (LOOKS_LIKE_OUTPUT.test(t)) return false;
  if (/^(?:TODO|TBD|FIXME|N\/A|none|null|\.{2,}|-+)$/i.test(t)) return false;
  const toks = t.split(/\s+/);
  let i = 0;
  while (i < toks.length && WRAPPER.has(toks[i].toLowerCase())) i += 1;
  const head = toks[i] || "";
  if (PATHY.test(head)) return true; // `./install.sh`、`/usr/bin/make`：带路径形状即真命令
  if (!IDENT.test(head)) return false; // 大写开头、带括号引号的（源码片段）一律不算
  // 认识的程序名：`make`、`pytest` 这类裸命令也必须认，否则就是误报（评审 U2）
  if (EXEC.has(head)) return true;
  // 认不出的名字：不猜，要求它至少带一个 flag/路径形状的参数
  return toks.slice(i + 1).some((x) => ARGISH.test(x));
}


const inlineCommands = (line) =>
  [...line.matchAll(/`([^`\n]+)`/g)].map((m) => m[1]);

// [from,to) 内**开始**的围栏块里是否真有一行像命令（闭合块体可以延伸出窗口）。
function fenceCommand(lines, pairs, from, to) {
  for (const [open, close] of pairs) {
    if (open < from || open >= to) continue;
    if (lines.slice(open + 1, close).some(commandish)) return true;
  }
  return false;
}

const REPRO_LABEL = /^\s*(?:[-*]\s+)?(?:\*\*)?\s*复现命令/;

// 全文有效证据处数（只用于输出行与"提取是否失效"的兜底，不再充当判据）。
// 就近窗口 = 到下一个标题或下一个「复现命令」标签为止。
function countEvidence(lines, fence, pairs) {
  let n = 0;
  for (let i = 0; i < lines.length; i++) {
    if (fence[i] || !REPRO_LABEL.test(lines[i])) continue;
    let to = lines.length;
    for (let k = i + 1; k < lines.length; k++) {
      if (!fence[k] && (HEADING.test(lines[k]) || REPRO_LABEL.test(lines[k]))) {
        to = k;
        break;
      }
    }
    if (inlineCommands(lines[i]).some(commandish) || fenceCommand(lines, pairs, i + 1, to)) n += 1;
  }
  return n;
}

// 返回 null = 证据成立；返回字符串 = 判红理由。
function entryEvidence(lines, fence, pairs, tableIdx, ids, id) {
  let start = -1;
  let level = 0;
  for (let i = tableIdx + 1; i < lines.length; i++) {
    if (fence[i] || !anchorRe(id).test(lines[i])) continue;
    start = i;
    const h = HEADING.exec(lines[i]);
    level = h ? h[2].length : 7;
    break;
  }
  if (start === -1)
    return `${id}：定级依据写的是"实测"，但报告里没有它名下的展开段落 —— ` +
      `需要形如 \`### ${id} · …\` 的小节，内含「复现命令」与原样可重跑的命令`;

  let end = lines.length;
  for (let i = start + 1; i < lines.length; i++) {
    if (fence[i]) continue;
    const h = HEADING.exec(lines[i]);
    if (h && h[2].length <= level) {
      end = i;
      break;
    }
    if (ids.some((other) => other !== id && anchorRe(other).test(lines[i]))) {
      end = i;
      break;
    }
  }

  for (let i = start; i < end; i++) {
    if (fence[i] || !REPRO_LABEL.test(lines[i])) continue;
    // 窗口止于 end：命令必须落在**本条目自己名下**（评审 T2）。旧实现写成
    // `end + 9`，于是把公共脚本放进紧随其后的"附录"就能一次性喂给全部高危——
    // 逐条取证当场退化回全文有一处就行。
    if (inlineCommands(lines[i]).some(commandish)) return null;
    if (fenceCommand(lines, pairs, i + 1, end)) return null;
    return `${id}：写了「复现命令」却没有一条像命令的内容 —— 行内代码/围栏块里要找的是` +
      `「可执行程序名（node / make / pytest / ./x.sh …）+ 参数或管道」这样的真命令；` +
      `\`见附录\`、\`see appendix\`、\`notes.md\`、源码片段、报错日志都不算证据`;
  }
  return `${id}：声称实测，但自己的展开段落里没有「复现命令」 —— 只在总表里写"实测"两个字不构成证据`;
}

function checkFile(path) {
  let text;
  try {
    text = readFileSync(path, "utf8").replace(/\r\n/g, "\n");
  } catch (e) {
    return { fatal: [`无法读取文件：${e.code || e.message}`] };
  }
  const lines = text.split("\n");
  const fence = fencedMask(lines);
  const pairs = fencePairs(lines);

  let hi = -1;
  let head = null;
  // 报告里常有多张表（验证表、T 项总表、合并执行清单）。优先取**含「定级依据」列**
  // 的那张；取不到再退回第一张 编号+级别 表，并在输出里声明取用了哪一张（评审 R15）。
  let firstCandidate = null;
  let preferred = null;
  for (let i = 0; i < lines.length; i++) {
    if (fence[i] || !/^\s*\|/.test(lines[i])) continue;
    const c = splitRow(lines[i]);
    if (!(c.some((x) => x.includes("编号")) && c.some((x) => x.includes("级别")))) continue;
    const cand = { i, c };
    firstCandidate ??= cand;
    if (c.some((x) => x.includes("定级依据"))) {
      preferred = cand;
      break;
    }
  }
  const chosen = preferred ?? firstCandidate;
  if (!chosen)
    return { fatal: ['未找到缺陷总表（表头需同时含"编号"与"级别"）—— 模板未落实或表头被改名'] };
  hi = chosen.i;
  head = chosen.c;
  const tableLine = hi + 1;

  const col = (kw) => head.findIndex((x) => x.includes(kw));
  const iId = col("编号");
  const iLv = col("级别");
  const iBs = col("定级依据");
  const iLoc = col("位置");

  const failures = [];
  if (iBs === -1)
    failures.push("缺陷总表缺少「定级依据」列 —— 未经实测不得定高危这条约束无法机检");
  if (iLoc === -1) failures.push("缺陷总表缺少「位置」列 —— 每条缺陷必须落到 文件:行号");

  let rows = 0;
  let levelSeen = 0;
  const measured = [];
  const highMeasured = [];
  const ids = [];
  for (let i = hi + 1; i < lines.length; i++) {
    if (fence[i]) continue;
    if (!/^\s*\|/.test(lines[i])) {
      if (rows > 0) break;
      continue;
    }
    const c = splitRow(lines[i]);
    if (isSep(c)) continue;
    const id = iId >= 0 ? c[iId] || "" : "";
    if (!id || id.includes("编号")) continue;
    rows += 1;
    ids.push(id);

    const lv = iLv >= 0 ? c[iLv] || "" : "";
    if (LEVELS.some((e) => lv.includes(e))) levelSeen += 1;
    const isHigh = HIGH.some((e) => lv.includes(e));
    const bs = iBs >= 0 ? c[iBs] || "" : "";
    // 「推理·待实测」含"实测"两字却不是实测——本行是最容易写错的一处判定。
    const claims = /(?<![待未无])实测/.test(bs);
    if (claims) measured.push(id);
    if (claims && isHigh) highMeasured.push(id);
    if (isHigh && !(claims && !bs.includes("推理")))
      failures.push(
        `${id}：定级为 ${lv || "(空)"} 但定级依据为"${bs || "(空)"}" —— ` +
          "未经实测不得定高危（推理所得最高 🟡）"
      );

    if (iLoc >= 0 && EMPTY_LOC.has(c[iLoc] || ""))
      failures.push(`${id}：位置列为空 —— 每条缺陷必须落到 文件:行号`);
  }

  if (rows === 0) failures.push("缺陷总表无数据行 —— 提取错位，本检查无法判定");
  else if (levelSeen === 0)
    failures.push("未解析到任何级别标记（🔴/🟠/🟡）—— 级别列格式变了，检查已失效");

  // 逐条就近取证（评审 R1）：声称实测的高危条目，必须在自己名下有**真的**命令。
  const nRepro = countEvidence(lines, fence, pairs);
  for (const id of highMeasured) {
    const why = entryEvidence(lines, fence, pairs, hi, ids, id);
    if (why) failures.push(why);
  }

  return { failures, rows, measured: measured.length, highMeasured: highMeasured.length, nRepro, tableLine };
}

let bad = 0;
for (const path of args) {
  console.log(`check-report: ${path}`);
  const r = checkFile(path);
  const fails = r.fatal || r.failures;
  if (fails.length) {
    bad += fails.length;
    for (const f of fails) console.error("  ✗ " + f);
  } else {
    console.log(
      `check-report: ${r.rows} 条缺陷（第 ${r.tableLine} 行的总表），${r.measured} 条声称实测` +
        `（其中高危 ${r.highMeasured} 条），逐条取证通过（全文有效「复现命令」${r.nRepro} 处）`
    );
  }
}
if (bad) {
  console.error(`check-report: ${bad} 处不符合「未经实测不得定高危」约束（高危须逐条取证）`);
  process.exit(1);
}
