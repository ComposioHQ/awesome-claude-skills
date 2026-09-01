---
name: talent-search
description: Technical-recruiting talent search. For AI and quant roles, searches the whole public web for candidates (school bar configurable: China C9 / Hong Kong / overseas; location, seniority and other constraints customizable). Input a candidate persona or JD; output is a cross-verified Excel candidate list plus a full search log. Use this skill whenever the user asks to find candidates, do talent sourcing or headhunting, build a talent map, find people similar to a benchmark persona, or provides a JD asking to "find people like this" — even without the word "search", as long as the goal is filling a role. 中文触发词：找候选人、人才检索、猎头寻访、人才 mapping、按对标画像找人、找类似的人。
---

# talent-search — Technical Headhunting Talent Search

## Positioning

Full-web talent sourcing for AI / quant roles. Input is a candidate persona or JD; outputs are:

1. **Excel candidate list** (`talent-research/<topic>/candidates-YYYYMMDD.xlsx`)
2. **Search log** (`search-log.md` in the same folder; template in Step 3)
3. **Candidate library** (`talent-research/_db/candidates.jsonl`, accumulates across tasks — every round queries the library first for incremental updates, so it gets thicker with use)
4. **Lessons file** (`talent-research/_lessons/YYYY-MM.md`, appended after every retrospective — source effectiveness / rejection patterns / network pitfalls / process improvements; the skill improves itself through use)

## Host adaptation

This skill is tool-agnostic. Adapt it to the host agent as follows:

- **Web search**: use the host's built-in search/fetch tools (WebSearch / WebFetch or equivalent). Paper search can hit arXiv API, Semantic Scholar API, OpenAlex API directly; the GitHub API can be requested directly.
- **Sites requiring login** (Maimai, LinkedIn, Jike, Xiaohongshu, etc.): use a locally available browser-automation skill (e.g. agent-browser) or an equivalent tool, with the account logged in compliantly.
- **Proxies**: if outbound access times out, configure `https_proxy` per your network; most `.edu.cn` sites actually work better without a proxy.
- **Node.js runtime**: `scripts/gen_excel.mjs` is zero-dependency and runs on Node.js ≥ 18.
- **Sub-agents**: if the host supports parallel sub-agents (an Agent tool), dispatch the channels of Step 1 in parallel; otherwise run channels serially on the main thread.

## Step 0: Parse the persona, lock the search parameters

Read the persona / JD the user provided (it may be a file path, a benchmark-persona markdown, or plain text). Extract the parameters below; ask the user **once** about anything ambiguous, make reasonable inferences where possible and record them in the search log:

| Parameter | Notes |
|------|------|
| Direction keywords | Bilingual, e.g. "LLM pretraining data / pretraining data curation", "quant strategy / quant research" |
| School hard bar | E.g. China C9 / Hong Kong / overseas (tier table in `references/school-list.md`); degree level (PhD / Master / Bachelor) |
| Graduation window | E.g. "PhD 2021–2023, 3–5 years in industry" |
| Target companies / teams | The pool the candidate's current or past role should come from (frontier LLM labs, top quant funds, etc.) |
| Location constraint | Default none; the user may restrict geography (e.g. "only candidates currently working in China"). Then the search must verify current work location; anyone outside the region is dropped and logged as "rejected (location)" |
| Bonus / exclusion items | E.g. "vision-to-LLM data", "Chinese-speaking candidates only", "exclude pure academia" |
| Target count | Default 20; user-adjustable |

Benchmark-persona format example: `examples/persona.example.md` (three sections: resume facts, persona traits, search-target profile). If the user gave no file, draft a persona in that structure first, have the user glance at it, then search.

**Incremental library check (mandatory if a library exists)**: if `talent-research/_db/candidates.jsonl` exists, query it before casting the net:

```bash
node scripts/db_upsert.mjs talent-research/_db/candidates.jsonl search <direction keyword / company / name>
```

Turn this round into an incremental update by these rules:

- In library with `last_verified` ≤ 90 days ago → reuse directly (only fill missing fields); do not re-search the whole web
- `last_verified` more than 90 days ago (search results carry a ⚠ stale flag) → re-verify only current role and work location
- `status` is `rejected` (with reason recorded) → skip this round unless the user names them for review
- Focus this round's four-channel firepower on library gaps: new directions, new companies, new graduation cohorts

**Read recent lessons**: if `talent-research/_lessons/` exists, read this month's and last month's lesson files (source effectiveness, rejection patterns, network pitfalls, process improvements) and tune channel priorities and query combinations accordingly. If a rejection pattern is relevant to the current persona, proactively flag it to the user (e.g. "last month 8/12 rejects in this direction failed the school bar — should we adjust the bar this round?").

## Step 1: Four-channel parallel search

First read `references/source-playbook.md` (channel strategy + contact-collection rules), then dispatch 4 sub-agents in parallel, one per channel:

1. **Academia channel**: paper authors, research groups, advisor lab pages, competition winners
2. **GitHub channel**: contributors to relevant open-source projects, authors of official paper implementations
3. **Company channel**: target companies' AI / research team pages, tech-blog authors, corporate open-source org members
4. **Community channel**: Zhihu / WeChat official accounts / tech forums / public LinkedIn pages (the main channel for Chinese-speaking candidate leads)

Sub-agent prompt template (goal-oriented, does not prescribe specific means; keep the tools sentence and substitute the host's actual tool names):

```
You are a talent-search sub-agent. Task: from the [<channel>] channel, find candidate leads for the persona below.
Persona: <direction keywords / school bar / graduation window / target companies / bonus-exclusion items / location constraint if any>
Use the host's web-search tools (e.g. WebSearch/WebFetch) to search public information; if browser operations are needed
(sites requiring login, e.g. Maimai, LinkedIn), load a locally available browser-automation skill and follow its guidance.
Requirements:
- Stop after 8–15 candidate leads; do not chase exhaustiveness
- Return one card per lead (markdown):
  ## Name (Chinese and English)
  - Inferred education: school / degree / year (mark "unverified" if not confirmed)
  - Current-role clue: company / title / dates / work location (mark "unverified" if unsure)
  - Homepage: URL or not found
  - GitHub: URL or not found
  - Contact clue: email / LinkedIn or not found
  - Sources: evidence URL for every item above
- Record public information only; mark uncertain items "unverified"; never fabricate
```

Each sub-agent returns its card list as the final reply to the lead agent. **Do not write files.**

## Step 2: Consolidate, dedupe, cross-verify

> **Verification-depth standard**: the **single-pass verification mode** is the mandatory baseline — every shortlisted candidate must pass at least one round of cross-verification; unverified candidates never make the list. If the user wants higher confidence and has time, the **five-pass verification mode** is an optional deep-dive.

### Single-pass verification mode (standard / mandatory)

1. **Dedupe**: merge cross-channel duplicates by "name + homepage/GitHub URL" into a shortlist
2. **Single pass**: for each shortlisted person, fetch the personal homepage / academic page directly (primary sources) and verify **education (school/degree/year), graduation window, current role, work location (if constrained), contact info**. Anything unverifiable is marked "unverified", and the search log notes "single-pass only"
3. **School-bar check**: grade the school against `references/school-list.md`. **Primary sources only** (LinkedIn education section, personal homepage, paper authorship, PhD thesis title page, GitHub org); search aggregators and secondhand reports are locating clues, never verification evidence. Below-bar candidates are dropped with the reason recorded in the log (keep the "rejected (reason)" wording)
4. **Fill per person**: current role, internships/jobs, homepage, GitHub, public contact info. Anything unavailable is "not obtained" — never fabricate and never pass inference off as fact
5. **First-author papers**: count **first-author** papers only; write the count first, then up to 5 representative titles (with venue and year). Titles only as verified from the paper itself, per authorship lists and Google Scholar
6. **University-lab experience**: verified well-known university labs only, formatted "school + lab/group name (year range)"; criteria in `references/school-list.md`; leave blank if none
7. **Match highlight**: one sentence per person on why they match (representative work, key experience, direction fit)

### Five-pass verification mode (optional / deep)

For users who explicitly ask for deep verification, or for critical-role candidates. Every shortlisted person is cross-verified across five independent source dimensions, checking the same core facts (name, education, experience, current role, first-author papers). **Dispatch one verification sub-agent per candidate**, running all five passes in order:

| Pass | Source dimension | Verify focus |
|------|---------|---------|
| 1 | Academia: paper authorship, Google Scholar, arXiv, conference proceedings, PhD thesis, lab pages | Education, first-author papers, lab |
| 2 | GitHub: profile, contribution timeline, org membership, profile email | Experience, current role, contact |
| 3 | Professional platforms: Maimai, LinkedIn, Liepin/Boss public profiles | Experience, current role (login-walled sites via browser automation) |
| 4 | Company / institution primary sources: official team pages, press releases, tech blogs, corporate open-source orgs | Current role and tenure |
| 5 | Personal homepage / social media: personal site, Zhihu, WeChat account, X, Jike | Corroboration + contact info |

Verification sub-agent prompt template (goal-oriented; substitute the host's actual tool names):

```
You are a candidate-verification sub-agent. Task: run five-pass cross-verification on the candidate below.
Candidate lead: <name + existing lead card>
Use the host's web-search tools (e.g. WebSearch/WebFetch) to search public information; if browser operations are needed
(sites requiring login, e.g. Maimai, LinkedIn), load a locally available browser-automation skill and follow its guidance.
Five passes (in order, each an independent source dimension):
1. Academia (paper authorship / Scholar / arXiv / conferences / PhD thesis / lab pages) — arXiv API, Semantic Scholar API, OpenAlex API are fetchable
2. GitHub (profile / contribution timeline / orgs / email) — GitHub API is fetchable
3. Professional platforms (Maimai / LinkedIn / Liepin public profiles; login-walled ones via browser automation)
4. Company / institution primary sources (official team pages / press releases / tech blogs / corporate open-source orgs)
5. Personal homepage / social media (personal site / Zhihu / WeChat account / X / Jike)
Each pass verifies the same facts: name, education (school/degree/year), experience (company/title/dates), current role, work location (if constrained).
Requirements:
- When passes conflict, primary sources win; record the conflict and the ruling in a "conflicts" section
- If a location constraint is set and the current work location clearly violates it, mark "rejected (location)"
- Mark unavailable info "not obtained"; never fabricate
Return (markdown):
## Verification result
- Name (Chinese and English)
- Education
- Experience
- Current role
- First-author papers: count + titles (≤5, with venue and year)
- University-lab experience
- Homepage / GitHub / contact info
## Five-pass record
Per pass: what was queried, what was found, conflicts with other passes
```

The sub-agent returns the verification result as the final reply to the lead agent. **Do not write files.**

### Write back to the candidate library (mandatory)

After shortlist verification, upsert **all** candidates (including rejected ones) back into the shared library `talent-research/_db/candidates.jsonl` for incremental reuse by later tasks:

```bash
node scripts/db_upsert.mjs talent-research/_db/candidates.jsonl upsert <candidates.json>
```

The input JSON is fully compatible with `gen_excel.mjs`'s candidates array, plus library-level fields:

| Field | Required | Notes |
|------|------|------|
| `direction` | recommended | This round's direction tag (e.g. `llm-pretraining-data`), the index for same-direction library queries |
| `last_verified` | auto | Last verification date; defaults to today |
| `verify_depth` | auto | `single` / `five` — the depth actually executed this round |
| `status` | recommended | `active` (shortlisted) or `rejected` (dropped); rejections must carry `reject_reason` so next round won't re-mine them |

Dedup keys are GitHub URL > homepage URL > name (URLs case-insensitive, trailing slashes ignored); on upsert, non-empty new fields overwrite old ones, empty fields keep old values. Full schema in the script's header comment and `examples/db-candidates.example.jsonl`. The library contains personal information and is excluded by `.gitignore` — **never commit it to git**.

**Library entry bar and contact rules:**

- Entry hard bar: identity must be **bi-directionally verified between homepage ↔ GitHub (or an authoritative institution page)** — one-way information or search-engine-only hits never enter the library
- Contact info is tiered into the `notes` field: public phone / WeChat (self-published on their own homepage/README/public card only) > public email > no direct contact
- **Maimai direct links**: if a candidate has a publicly accessible Maimai profile page (`maimai.cn/u/...` format), record it separately in the `maimai` field for one-click reach; **article pages on Maimai (article/detail) are not personal profiles** — never mislabel them
- Compliance red line: phone / WeChat / Maimai info comes from **public channels only** — no scraping of private chats, no bought data, no closed groups

## Step 3: Produce outputs

Produce two files under `talent-research/<topic>/`:

### candidates-YYYYMMDD.xlsx

Generate with `scripts/gen_excel.mjs` from this skill's directory (zero-dependency, runs on Node ≥ 18):

```bash
node scripts/gen_excel.mjs candidates.json output-path.xlsx
```

The structure of `candidates.json` and column definitions are in the script's header comment; an example is `examples/candidates.example.json`. Fixed 9 columns:

| Column | Content |
|----|------|
| Name | Chinese and English names |
| Education | School / degree / year; multiple degrees on separate lines |
| Internships / jobs | Company / title / dates, one per line |
| Personal homepage | URL (or "not obtained") |
| GitHub | URL (or "not obtained") |
| First-author papers | Count + representative titles (≤5, with venue and year), one per line |
| University-lab experience | "School + lab/group name (year range)"; blank if none |
| Match highlight | One-sentence match rationale |
| Notes (CV / contact) | CV link, LinkedIn, email and other public contact info (or "not obtained") |

### search-log.md

Follow this template:

```markdown
# Search log: <topic> (benchmark: <benchmark person>)

> Date established: YYYY-MM-DD
> Search methods: <tools actually used>

## Task requirements
- <persona summary + all constraints (including mid-round additions, timestamped)>
- Verification method: single-pass mandatory; five-pass optional deep verification

## Search process
| Time | Query / action | Result and decision |
|------|-----------|-----------|
| ...  | ...       | ... (including "rejected" with reason, conflicts found during verification and how they were ruled on) |

## Network environment notes
- <newly discovered pitfalls this round>

## TODO
- [ ] ...
```

## Step 4: Retrospective and lessons (mandatory)

After outputs are done, the lead agent runs a short retrospective on this round's search log and appends **reusable** lessons to `talent-research/_lessons/<current-month>.md` — create it per `references/lessons-template.md` if absent (the directory is excluded by `.gitignore` and never enters the repo).

Retrospective inputs: the search log (per-channel hit counts, rejection-reason distribution, time sinks) + the output list + constraints the user added mid-round.

One line per lesson, one of four types:

| Type | What to write |
|------|--------|
| **Source effectiveness** | Which source hit / failed (with data), how to re-rank next round |
| **Rejection pattern** | What the rejection distribution says about the persona, and suggested adjustments |
| **Network pitfall** | Newly discovered site-reachability issues and workarounds |
| **Process improvement** | The slowest / hardest-to-verify steps and how to fix them |

Discipline:

- Only reusable conclusions, no task diary (the diary belongs in the search log)
- Date and direction tag on every entry
- New lessons conflicting with old ones never delete the old entry — append and note "conflicts with <date> entry; this one wins"

## Maintenance and evaluation: required for every revision

Before merging any substantive change to this skill (SKILL.md flow, `references/` search strategy and lessons), run the evaluation baseline first — **self-modification without evaluation is driving blindfolded**:

1. **Build a golden set** (one-time, 10–20 people per direction): pick confirmed-correct candidates from past verified outputs, write them to `talent-research/_eval/golden.jsonl` (covered by `.gitignore`, never committed). Each entry has name + github/homepage + education/current ground truth; format in `examples/golden.example.jsonl`
2. **Run the baseline**: do one full cold run over the directions covered by the golden set (no candidate-library increment), get the result JSON, then score:

   ```bash
   node scripts/eval_recall.mjs talent-research/_eval/golden.jsonl <result.json> [result2.json ...]
   ```

   Metrics: recall (pass bar defaults to 0.8, adjustable via the `RECALL_MIN` env var), education/current-role field accuracy of hits (normalized mutual-containment matching), misses list. Below bar exits with code 1
3. **Merge decision**: only merge if recall ≥ the bar and field accuracy is no lower than the last recorded run; otherwise fix and re-test. Script usage and metric definitions are in the script's header comment
4. **Keep records**: log every run in `talent-research/_eval/records.md` (date, recall, field accuracy, change summary) as the evidence chain that "evolution never regresses"

## Proactive radar (scheduled monitoring, optional)

Upgrade from "search when asked" to "scan on schedule": configure once, get a weekly incremental talent-signal report.

1. **Configure**: copy `examples/radar-config.example.json` to `<workspace>/talent-research/_radar/config.json`; fill in the direction tag, paper-search keywords (English phrases), and the target GitHub org list

   Field-tested China LLM-team GitHub org lookup (one wrong letter in an org name means zero results — trust this table and re-verify before filling):

   | Team | org | Public-member signal |
   |------|-----|------|
   | Alibaba · Qwen | `QwenLM` | strong |
   | Alibaba · ModelScope | `ModelScope` | weak (~2) |
   | Alibaba · Tongyi Lab | `Alibaba-NLP` | medium |
   | DeepSeek | `deepseek-ai` | weak (~1) |
   | Zhipu | `THUDM` / `zai-org` | strong |
   | Moonshot · Kimi | `MoonshotAI` | weak (~2) |
   | Tencent ARC Lab | `TencentARC` | medium |
   | Tencent Hunyuan | `Tencent-Hunyuan` | none (members not public; keep as placeholder) |
   | ByteDance Seed | `ByteDance-Seed` | none (members not public; keep as placeholder) |
   | Baidu PaddlePaddle | `PaddlePaddle` | strongest (~35) |
   | Huawei Noah's Ark | `huawei-noah` | medium |
   | Huawei MindSpore | `mindspore-ai` (note: not `mindspore`) | none (members not public; keep as placeholder) |
   | Meituan | `meituan` | medium |
   | JD | `jd-opensource` | medium |
   | Xiaohongshu | `xiaohongshu-pub` | very weak (the company barely uses GitHub) |

2. **Run** (with the workspace root as cwd):

   ```bash
   node scripts/radar_scan.mjs talent-research/_radar/config.json
   ```

   The first run establishes the baseline; every later run is an incremental diff, with the report written to `talent-research/_radar/radar-YYYY-MM-DD.md`: new public GitHub org members (talent-flow signals) + new OpenAlex papers in the direction (with first author and institution — first authors are candidate leads)
3. **Schedule**: run weekly via the host's scheduler (cron / automation). After each run, quickly verify the new signals through the single-pass flow, upsert them into the candidate library, and write the lessons (which orgs / keywords have high signal density) into `_lessons/`
4. **Boundaries**: public information only (GitHub public members, OpenAlex public metadata); unauthenticated GitHub API is rate-limited to 60 req/hour, keep the org list under ~20 (each org costs ~1-2 requests per round); use OpenAlex for papers instead of the arXiv API (the latter's https is unreachable on some networks)
5. **Weak-signal note**: some companies (Tencent Hunyuan, ByteDance Seed, Huawei MindSpore) keep GitHub member lists fully private — an org scanning 0 people is normal. Keeping them costs almost nothing: the moment someone publicizes their membership, the radar catches it. Xiaohongshu has minimal GitHub presence; its signal comes mainly through the paper channel

## Data-quality bottom lines

- Primary sources first: search engines are for discovering leads; verification must go back to official sites / homepages / papers / GitHub originals
- Contact info from **public** sources only (GitHub profile email, personal-homepage email, paper corresponding-author email, public LinkedIn pages) — no bought data, no paid-database scraping, no closed groups
- Every key fact for every candidate must be traceable to a source URL in the search log
- **Every shortlisted candidate must pass at least one round of cross-verification**: unverified candidates never make the list
- If a location constraint is set: drop anyone whose current work location cannot be verified or clearly violates it, with the reason in the search log
- Better empty than fabricated: candidates who cannot be verified against primary sources are marked "unverified", never filled with guesses

## References

| File | When to read |
|------|--------|
| `references/source-playbook.md` | Mandatory before Step 1 (channel strategy, contact-collection rules) |
| `references/school-list.md` | Mandatory during Step 2 school-bar verification |
| `references/lessons-template.md` | Read before appending lessons in Step 4 (entry format and discipline) |
