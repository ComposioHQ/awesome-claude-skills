# 访谈模式访谈脚本（Mom Test 风格）Interview Script (Mom Test style)

访谈是**可选**环节，不是打分前提：起步阶段没有访谈是正常的，不构成低分理由。
访谈的作用是把「定义清晰但未核对」升级为「深度对齐 + 已核对」，支撑 7 分以上。
Interviews are **optional** and NOT a scoring prerequisite — a solo founder naturally has none at the start.
Their role is upgrading "clearly defined but not cross-checked" into "aligned + cross-checked", supporting 7+.

## 硬性纪律 Hard Rules
- 少于 3 个真实目标用户访谈，不得在证据里写「已访谈 / interviewed」；只能写「访谈 1-2 人，方向待验证」。
  Fewer than 3 real target-user interviews: never claim "interviewed"; write "1-2 interviews, direction unverified".
- 访谈对象必须符合目标用户定义（人群 + 决策状态 + 场景），不是朋友/家人/泛泛的「感兴趣的人」。
  Interviewees must match the target definition (segment + decision state + scenario) — not friends, family, or "interested people".
- 禁止把「我想要」当「用户想要」：只记录用户关于自己生活的原话。
  Never treat "I want it" as "the user wants it": record only what users say about their own life.
- 用户说的未来行为不算证据，过去的实际行为才算；是否式回答不算证据，具体故事才算。
  Future intent is not evidence; past behavior is. Yes/no answers are not evidence; concrete stories are.
- 访谈中不推销、不提你的产品（Mom Test 原则：谈他们的生活，不谈你的想法）。
  Do not pitch or mention your product (Mom Test: talk about their life, not your idea).

## 对象筛选 Recruiting
- 从哪找：现有渠道（社区、竞品用户、邮件列表、冷启动名单）找 5-10 个符合画像的人。
  Where: existing channels (communities, competitor users, email lists, cold-start lists); find 5-10 people matching the persona.
- 筛选问题：你最近一次（做这件事）是什么时候？怎么做的？有真实场景才算目标用户。
  Screen question: when did you last <do the thing>? How? A real scenario means they qualify.

## 问题集 Question Bank（按环节分组，一对一逐题问）
### 真实需求 Real Demand
- 你最近一次遇到这个问题是什么时候？（时间与场景） When did you last hit this problem?
- 当时你是怎么解决的？（具体做法） How did you solve it then (concretely)?
- 现在的做法哪里让你不满意？ What do you dislike about the current approach?
- 这个问题多久发生一次？每次要花多少时间/钱？ How often, and what does it cost each time?

### 付费意愿与习惯 Willingness to Pay & Habits
- 你现在为这类问题花过钱吗？花在哪、每月/年多少？ Have you paid for this before? How much?
- 你订阅过哪些软件/服务？有没有取消过？为什么？ What do you subscribe to? Ever cancelled? Why?
- 如果有个方案能（说核心价值），你觉得值多少钱？（先谈历史，再谈锚定） If a solution could <core value>, what would it be worth?

### 竞品与替代 Competitors & Alternatives
- 你现在用什么工具/方法？除了它还考虑过什么？ What do you use today? What else did you consider?
- 为什么最后选了现在的方案？ Why did you pick the current one?
- 现在方案最让你抓狂的是什么？ What drives you crazy about it?

### 渠道 Channels
- 你一般在哪搜索/讨论这类信息？关注哪些社区、博主、邮件？ Where do you search/discuss this?
- 你推荐过这类工具给别人吗？怎么推荐的？ Ever recommended a similar tool? How?

## 好问题 vs 坏问题 Good vs Bad Questions
| 坏问题（避免） Bad (avoid) | 好问题（用） Good (use) |
| --- | --- |
| 你会用这个产品吗？ Would you use this? | 你最近一次遇到这个问题是什么时候？ When did you last hit it? |
| 如果便宜你会买吗？ Would you buy if cheaper? | 你现在为这类问题花多少钱？ What do you pay today? |
| 你觉得这个功能重要吗？ Is this feature important? | 你最近为这件事做了什么？ What did you last do about it? |
| 你会推荐给朋友吗？ Would you refer friends? | 你上次推荐类似工具是什么时候？ When did you last recommend one? |

## 记录模板 Interview Log
每用户一段：用户（脱敏）、状态（人群+决策状态+场景）、原话证据（引号保留）、涉及的环节、结论（验证/推翻哪个假设）。
One block per user: who (anonymized), state (segment + decision state + scenario), verbatim evidence (quoted), related stage(s), conclusion (which assumption was verified or falsified).

## 证据落地 Feeding Evidence Back
- 把每段记录整理成 evidence_fill_form.json 里对应指标的 evidence 条目：
  Feed each log into evidence_fill_form.json as an evidence item, e.g.:
  {"source": "interview", "url": "访谈记录-用户A", "title": "<原话摘要>", "snippet": "<原话>", "date": "2026-xx-xx"}
- 完成后运行 python references/market_research.py --score-only evidence_fill_form.json 复检市场调研分数，再重新逐环节打分。
  Then re-run --score-only to refresh the research scores, and re-score all stages.
- 访谈证据在打分中可支撑 strong（深度对齐 + 外部核对），但须满足硬性纪律（至少 3 人）。
  Interview evidence can support strong (aligned + cross-checked) only if the hard rules hold (3+ people).

## AI 扮演访谈教练 Coach Mode
用户说「帮我做访谈」或「访谈加深」时，AI 按上述规则执行：
When the user asks for "interview" or "deep-dive", the AI:
1. 先确认目标用户画像（人群+决策状态+场景），不合格先补定义。 Confirm the persona first; fix it if unclear.
2. 每次只问一个问题（按环节顺序），追问细节，不替用户回答。 One question at a time, follow up, never answer for the user.
3. 若用户回答落入坏问题陷阱（替 AI 设计、推销式回答），给一句简短提示。 Flag traps briefly.
4. 访谈结束后，整理成 Interview Log 与 evidence 条目，提示用户复检。 Consolidate the log + evidence, then suggest a re-check.