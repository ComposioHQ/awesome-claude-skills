# 商业链路模型与评分细则 Framework & Scoring

## 两种模式下的证据含义 Evidence in Two Modes
- 项目检查（他人项目）：证据 = 公开材料。公开材料里没有 → 标「证据不足」，该环节最高 3 分；报告不得把「没公开」当「没做」。
  Project Inspection (projects of others): evidence = public materials. Not in public materials → mark "insufficient evidence", cap the stage at 3; never treat "not published" as "not done".
- 自检（自己项目）：证据 = 创造者的回答。答不出、没想清楚 = 真实的薄弱/断裂信号，按深度封顶规则打分。
  Self-Check (your own project): evidence = the answers given by the creator. Cannot answer / not thought through = a real weak/broken signal; score with depth caps.

## 链路模型（7 环节）The Loop Model (7 stages)
市场调研 → 真实需求 → 价值主张 → 获客 → 付费转化 → 交付与体验 → 复购与传播
Market Research → Real Demand → Value Proposition → Acquisition → Paid Conversion → Delivery & Experience → Retention & Referral

参考框架（仅用于补充判断要点，不改变本模型）Reference frameworks (supplement the checks only; they do not change this model):
- 精益画布 Lean Canvas：Problem, Customer Segments, Value Proposition, Channels, Revenue Streams, Unfair Advantage
- 商业模式画布 Business Model Canvas：Revenue Streams, Customer Relationships, Key Resources
- AARRR：Acquisition, Activation, Retention, Revenue, Referral
- 增长飞轮 Growth Flywheel：留存-推荐-复购 的自我强化循环 a self-reinforcing loop of retention, referral and repurchase

## 自检提问清单 Self-Check Questions
自检模式（或项目检查中确认是自己的项目后）按环节提问，默认一次一个问题；答不上来就记为「未想清楚/未设计」并继续。
In Self-Check mode (or after confirming the project is yours during inspection), ask stage by stage, one question at a time by default; unanswered questions are recorded as "not thought through / undesigned" and you continue.

### 1. 市场调研 Market Research（先跑调研，再谈需求；不要求访谈，桌面研究即可）
- 是否已对目标市场做了全网桌面研究？用户画像、群体范围、痛点、付费意愿、付费习惯、竞品、市场规模、渠道分布，8 项指标查证了吗？ Has desk research (web search) been done for the target market? Persona, market scope, pain points, willingness to pay, payment habits, competitors, market size, channels — all 8 metrics verified?
- 有 API key 时：运行 `python references/market_research.py --product "<产品描述>"`，程序自动联网搜索并按指标打分、附证据来源。 With an API key: run the script for live search and per-metric scores with evidence sources.
- 无 API key 时：程序生成检索计划与 evidence_fill_form.json，由 agent 用自身联网搜索补完证据，再运行 `--score-only` 计算分数。 Without an API key: the program generates a search plan and evidence_fill_form.json; the agent completes evidence with its own web search, then runs `--score-only`.
- 调研结果与你的产品主张一致吗？不一致的地方就是风险点。 Do the findings agree with your product claims? Discrepancies are risk points.
- 社区信号核对了吗？读一读报告「社区信号」板块里目标用户聚集社区的真实讨论，区分「想要」与「愿意付费」。 Did you read the real community discussions in the report's "Community Signals" section? Distinguish "want it" from "willing to pay".

### 2. 真实需求 Real Demand（先对齐，再谈其他）
- 你的目标用户处于什么状态：还没决定要不要做？决定做了但没选方案？已在用方案但不满意？ What state is your target user in: undecided about doing it? decided but choosing a solution? already using one but dissatisfied?
- 相邻人群区分了吗？「还没决定要不要出海」和「已决定出海、在选工具」需求不同，你服务哪一类？ Are adjacent segments distinguished? "Undecided about going overseas" and "decided, choosing a tool" have different needs — which one do you serve?
- 他们现在怎么解决？在哪里讨论、搜索（社区 / 竞品评论 / 公开报告）？ How do they solve it today? Where do they discuss or search (communities / competitor reviews / public reports)?
- 你去社区、竞品评论或公开报告核对过需求吗？（桌面研究即可，不要求访谈） Have you cross-checked demand via communities, competitor reviews or public reports? (desk research is enough; interviews are not required)
- 他们愿意为「解决这个问题」付费吗？验证过吗？ Would they pay to solve it? Have you verified this?
- 市场有多大？替代方案和竞争对手有哪些？ How big is the market? What are the alternatives and competitors?

### 3. 价值主张 Value Proposition
- 一句话说清：为谁（含决策状态）、解决什么、为什么是你？ Say it in one sentence: for whom (incl. decision state), what problem, why you?
- 相比现有方案（包括「什么都不做」），你的独特优势是什么？ Compared with existing solutions (including "do nothing"), what is your unique edge?
- 用户 30 秒内能感知价值吗？ Can users perceive the value within 30 seconds?
- 你有什么别人不易抄走的东西（技术、资源、渠道、数据、网络效应）？ What is hard to copy (tech, resources, channels, data, network effects)?

### 4. 获客 Acquisition
- 第一批用户在哪里？具体渠道是什么（他们真的会去的地方）？ Where are the first users? Which exact channel (where they actually are)?
- 渠道能规模化吗？获客成本（CAC）估算过吗？ Is the channel scalable? Have you estimated CAC?
- 有落地页 / 试用入口吗？从知道到用上的路径通了吗？ Is there a landing page / trial entry? Is the path from awareness to usage complete?
- 获客方式适合你的产品形态吗（PLG / SLG / 渠道合作）？ Does acquisition fit your product shape (PLG / SLG / partnerships)?

### 5. 付费转化 Conversion & Monetization
- 用户为什么付费、在什么节点付费？ Why do users pay, and at which moment?
- 定价与商业模式定了吗（订阅 / 买断 / 免费增值 / 按用量）？ Pricing and business model decided (subscription / one-time / freemium / usage-based)?
- 免费与付费的边界在哪？升级理由充分吗？ Where is the free/paid line? Is the upgrade reason strong?
- 付费入口与支付流程设计好了吗？ Is the payment entry and checkout flow designed?
- 有付费意愿的间接证据吗（对标价格、同类付费产品、社区反馈）？ Any indirect willingness-to-pay evidence (benchmark prices, similar paid products, community feedback)?
- 单位经济算过吗（LTV/CAC、毛利率）？有数字就运行 python references/economics.py 测算：
LTV/CAC>=3 健康、1-3 需优化、<1 断裂信号；说不出数字按「未测算」记，不臆测。
Unit economics estimated (LTV/CAC, gross margin)? With numbers, run python references/economics.py:
LTV/CAC >=3 healthy, 1-3 needs work, <1 broken; no numbers = "not measured", never guess.

### 6. 交付与体验 Delivery & Activation
- 用户第一次使用后，多久能感受到核心价值（Aha moment）？ After first use, how soon do users feel the core value (aha moment)?
- 新手引导 / 模板有吗？ Onboarding / templates?
- 激活指标定义了吗？ Activation metric defined?
- 客服 / FAQ / 故障响应怎么安排？ Support / FAQ / incident response?

### 7. 复购与传播 Retention & Referral
- 什么机制让用户回来（内容更新、习惯循环、续费提醒、会员体系）？ What brings users back (content updates, habit loops, renewal reminders, membership)?
- 什么机制让用户帮你传播（推荐奖励、可炫耀点、分享路径）？ What makes users spread the word (referral rewards, shareable wins, sharing paths)?
- 流失预警和召回怎么做？ Churn warning and win-back?
- 留存指标定义了吗（留存率、复购率、NPS）？ Retention metrics defined (retention rate, repurchase rate, NPS)?

## 访谈模式（可选加深证据）Interview Mode (optional evidence deep-dive)
访谈是可选环节，不是打分前提：起步阶段没有访谈是正常的，不构成低分理由。用户要求「访谈 / 访谈加深」时，
AI 扮演访谈教练，按 references/interview.md 逐题提问（一次一问）、记录证据，并落地到 evidence_fill_form.json 后复检。
Interviews are optional, not a scoring prerequisite — a solo founder naturally has none at the start.
On request ("interview" / "deep-dive"), the AI coaches per references/interview.md: one question at a time,
log evidence, feed it into evidence_fill_form.json, then re-check.
- 硬性纪律 Hard rules：少于 3 个真实目标用户不得声称「已访谈」；对象必须符合「人群+决策状态+场景」；
  只记录过去实际行为，不做推销；禁止把「我想要」当「用户想要」。
  Fewer than 3 real target users = never claim "interviewed"; interviewees must match segment+decision state+scenario;
  record past behavior only; never pitch; never treat "I want it" as "the user wants it".
- 证据作用 Evidence role：访谈 + 社区/竞品核对可支撑 strong（深度对齐 + 外部核对）；未访谈不算低分，
  但「说不出用户、零核对」要按模糊/未对齐封顶（<=3）。 Interviews + community/competitor cross-checks can support strong;
  no interviews is NOT a low-score reason, but "cannot state the user, zero cross-checks" caps at vague (<=3).

## 打分细则（每环节 0-10 分，按判断深度）Scoring (0-10 per stage, by judgment depth)
分数 = 定义深度 × 外部核对。判断是否严格，看的是「想得够不够深、需求有没有对齐」，而不是有没有访谈或使用数据——个人做工具在起步阶段没有这些是正常的。
Score = definition depth × external cross-checking. Strictness is about how deeply and precisely the creator has thought (aligned demand), not whether interviews/data exist — a solo founder naturally has no interviews or usage data at the start.

**深度三档 Depth tiers:**
- 深度对齐 aligned（strong）：目标用户精确到「人群 + 决策状态 + 场景」，相邻人群已区分，需求与方案对齐；并经外部核对（桌面研究：社区讨论 / 竞品评论 / 公开报告，不要求访谈）→ 可评 7-10
  Target user precise (segment + decision state + scenario), adjacent segments distinguished, demand aligned with the solution, and cross-checked externally (desk research: community discussions / competitor reviews / public reports; interviews not required) → 7-10 allowed
- 定义清晰 unverified（weak）：定义清晰但未做任何外部核对 → 最高 6 分
  Clearly defined but no external cross-checking → cap at 6
- 模糊/未对齐 vague（none）：说不清用户是谁，或相邻人群混淆（如「还没决定要不要出海」与「已决定出海、在选方案」混为一谈），或需求与方案不匹配 → 最高 3 分
  Cannot state who the user is, adjacent segments conflated (e.g., mixing "undecided about going overseas" with "decided, choosing a solution"), or demand mismatched with the solution → cap at 3

**各环节深度门槛 Depth gates per stage（不满足直接封顶）:**
市场调研 Market Research：未运行调研程序或证据收集未完成 → ≤3；已调研但证据少 / 主要指标未覆盖 → ≤6
- 真实需求 Real Demand：目标用户模糊或相邻人群未区分 → ≤4；未定义决策状态/使用场景 → ≤6 Target user vague or adjacent segments not distinguished → ≤4; decision state / scenario undefined → ≤6
- 价值主张 Value Proposition：不能一句话说清「为谁（含决策状态）解决什么、为什么是你」→ ≤4；无差异化 → ≤6 Cannot state in one sentence "for whom (incl. decision state), what problem, why you" → ≤4; no differentiation → ≤6
- 获客 Acquisition：说不出目标用户在哪、渠道与人群不匹配 → ≤4；有渠道但无落地页/入口 → ≤6 Cannot say where the target users are or channel mismatched → ≤4; channel exists but no landing page / entry → ≤6
- 付费转化 Paid Conversion：说不出用户为什么/何时付费 → ≤4；无定价设计 → ≤3 Cannot explain why/when users pay → ≤4; no pricing design → ≤3
- 交付与体验 Delivery & Experience：未定义首次使用激活路径 → ≤5 No first-use activation path defined → ≤5
- 复购与传播 Retention & Referral：无任何留存或传播设计 → ≤2 No retention or referral design → ≤2

设计档参考 Design band reference（在封顶内 within caps）:
- 9-10 强闭环：深度对齐 + 核对到位 + 执行到位 strong loop: aligned, cross-checked and executed
- 7-8 基本打通：深度对齐且已核对 verified alignment → executable
- 5-6 有设计但未核对 design exists but not cross-checked
- 3-4 仅有想法，模糊或未对齐 idea only, vague or misaligned
- 0-2 缺失 missing

## 每环节检查项 Per-Stage Checklists

### 1. 市场调研 Market Research（证据先行 evidence first）
- 8 项指标是否都查证过：用户画像、群体范围、痛点需求、付费意愿、付费习惯、竞品分析、市场规模、渠道分布？ All 8 metrics researched: user persona, market scope, pain points, willingness to pay, payment habits, competitors, market size, channels?
- 证据是否有来源 URL 可追溯？是否包含具体数字/实体（人群规模、定价、增长率）？ Evidence traceable with URLs? Concrete numbers/entities (segment size, pricing, growth rates)?
- 调研结论与产品主张是否一致？矛盾点是否被记录？ Do findings match the product claims? Discrepancies recorded?
- 是否区分「搜索到的行业信息」与「该产品特有的证据」？ Industry-level findings vs product-specific evidence distinguished?
- 参考 Reference：市场调研引擎 references/market_research.py

### 2. 真实需求 Real Demand（最难判断 → 先看对齐 hardest to judge → alignment first）
- 目标用户是否具体（细分人群 + 决策状态 + 使用场景）？ Is the target user specific (segment + decision state + scenario)?
- 是否区分相邻但需求不同的人群（如「还没决定要不要做」与「已决定做、在选方案」）？ Are adjacent segments with different needs distinguished (e.g., "undecided" vs "decided, choosing a solution")?
- 痛点是否具体到频率与场景？有无社区反馈 / 竞品评论 / 公开数据佐证？ Is the pain specific to frequency and scenario? Any community feedback / competitor reviews / public data?
- 是否区分「想要」与「愿意付费解决」？ Does it distinguish "want it" from "willing to pay"?
- 是否了解市场容量与竞争格局（TAM/SAM、替代方案）？ Market size and competition known (TAM/SAM, alternatives)?
- 参考 Reference：精益画布 Lean Canvas Problem / Customer Segments

### 3. 价值主张 Value Proposition
- 能否一句话说清「为谁（含决策状态）、解决什么、为什么是你」？ Can you say in one sentence "for whom (incl. decision state), what problem, why you"?
- 与替代方案（包括「什么都不做」）相比是否有独特优势？ Unique advantage vs alternatives (including "do nothing")?
- 用户能否在 30 秒内感知价值？ Can users perceive the value in 30 seconds?
- 是否有不公平优势（技术、资源、渠道、网络效应、数据）？ Any unfair advantage (tech, resources, channels, network effects, data)?
- 参考 Reference：精益画布 Lean Canvas Value Proposition / Unfair Advantage；价值主张画布 Value Proposition Canvas

### 4. 获客 Acquisition
- 主获客渠道是否明确，且与目标用户（他们实际在的地方）匹配？ Is the main channel clear and matched to where the target users actually are?
- 渠道是否可规模化？获客成本（CAC）有无估算？ Is the channel scalable? CAC estimated?
- 有无落地页 / 试用入口 / 激活路径？ Any landing page / trial entry / activation path?
- 是否考虑 PLG / SLG / 混合策略？ PLG / SLG / hybrid strategy considered?
- 参考 Reference：AARRR Acquisition；精益画布 Lean Canvas Channels

### 5. 付费转化 Conversion & Monetization（最难判断 → 先看付费逻辑 hardest to judge → payment logic first）
- 用户为什么付费、在什么节点付费？ Why do users pay, and at which moment?
- 定价与商业模式是否明确（订阅 / 买断 / 免费增值 / 按用量）？ Pricing and business model clear (subscription / one-time / freemium / usage-based)?
- 免费与付费边界是否清晰、升级理由是否充分？ Free/paid boundary clear, upgrade reasons strong?
- 转化路径有无明确的付费触点？支付流程是否顺畅？ Clear payment touchpoints in the conversion path? Smooth checkout?
- 有无付费意愿的间接证据（对标价格、同类付费产品、社区反馈）？ Indirect willingness-to-pay evidence (benchmark prices, similar paid products, community feedback)?
- 单位经济是否测算过（LTV/CAC、毛利率）？ Unit economics estimated (LTV/CAC, gross margin)?
- 参考 Reference：商业模式画布 Business Model Canvas Revenue Streams；AARRR Revenue

### 6. 交付与体验 Delivery & Activation
- 核心价值能否在首次使用后快速兑现（Aha moment）？ Can the core value land quickly after first use (aha moment)?
- 上手引导 / 模板是否降低学习成本？ Do onboarding / templates lower the learning cost?
- 有无激活指标定义与监控？ Activation metric defined and monitored?
- 服务与支持（客服、FAQ、故障响应）是否到位？ Support (CS, FAQ, incident response) in place?
- 参考 Reference：AARRR Activation

### 7. 复购与传播 Retention & Referral（最容易断 → 无设计即断裂 breaks most easily → no design means broken）
- 有无留存机制（内容更新、习惯循环、续费提醒、会员体系）？ Retention mechanics (content updates, habit loops, renewal reminders, membership)?
- 有无传播设计（推荐奖励、分享动机、可炫耀点、社交传播路径）？ Referral design (rewards, sharing motives, bragging points, social paths)?
- 有无流失预警与召回路径？ Churn warning and win-back paths?
- 是否定义留存指标（留存率、复购率、NPS）？ Retention metrics defined (retention rate, repurchase rate, NPS)?
- 参考 Reference：AARRR Retention / Referral；增长飞轮 Growth Flywheel

## 判定规则 Verdict Rules
- 单环节 Per stage：7 分及以上 = 健康 healthy；5-6.9 = 薄弱 weak；低于 5 = 断裂 broken。
- 总体结论 Overall verdict：
  - 链路打通 Loop Closed：全部环节 ≥7 且平均分 ≥7.5 all stages ≥7 and average ≥7.5
  - 接近打通 Nearly Closed：无环节低于 5，平均分 ≥7，但存在低于 7 的环节 no stage <5, average ≥7, but some stage <7
  - 未打通 Not Closed：任一环节低于 5，或平均分低于 7 any stage <5, or average <7
- 注意：7 分以上必须「深度对齐 + 外部核对」。因此「链路打通」意味着有核对支撑的对齐闭环，而非纸面设计。 Note: 7+ requires aligned, externally cross-checked demand, so a "Loop Closed" verdict means an evidence-backed loop, not paper design.
- 他人项目 Projects of others：结论前注明「基于公开证据」，低分环节标注「证据不足」或「设计缺失」。 Prefix the verdict with "based on public evidence"; mark low stages as "insufficient evidence" or "missing design".
- 行动优先级 Action priority：断裂环节（分数低者先）→ 薄弱环节（分数低者先）→ 若全部健康，优先寻找复购与传播的增长杠杆。 Broken stages (lowest score first) → weak stages (lowest first) → if all healthy, prioritize growth levers in Retention & Referral.

### 市场调研环节分 ↔ 8 指标机器分 Mapping the research engine to the stage score
先跑 references/market_research.py，得到 8 项指标的机器证据分与总体分 E。
Run references/market_research.py first: it outputs per-metric machine evidence scores and an overall score E.
- 覆盖率 Coverage C = 有公开证据的指标数 / 8。Coverage C = metrics with evidence / 8.
- 一致性 Consistency：调研结论是否与产品主张一致（AI 判断；矛盾视为不一致）。Findings consistent with the product claims? (AI judgment; contradictions count as inconsistent)
- 换算 Conversion：市场调研环节分 = round(E)，并按以下封顶 Conversion: stage score = round(E), capped by:
  - C=1 且一致 → evidence=strong，不封顶（可 7-10；若 E<7，证据虽全但弱，不建议超过 E）
    C=1 & consistent → strong, no cap (7-10; if E<7 the evidence is thin, keep near E)
  - 0.5≤C<1 → evidence=weak，≤6
  - C<0.5 或未跑调研 → evidence=none，≤3
- 机器 E 是「证据强度」，不是「市场好坏」；0 分 = 未找到公开证据，不代表市场不存在。E measures evidence strength, not market quality; 0 means no public evidence was found.

## 打分计算器 Scoring Calculator（可选 optional）
为保证打分与判定一致，可先用脚本校验：将七环分数写入 JSON 文件，运行 `python references/scoring.py <file>`，脚本输出平均分、逐环状态、结论与行动优先级；加 `--json` 可输出机器可读结果。
To keep scoring and verdicts consistent, verify with the script first: write the seven scores to a JSON file and run `python references/scoring.py <file>`; it outputs the average, per-stage status, verdict and action priority. Add `--json` for machine-readable output.
JSON 必须包含 scores 对象，键为七环：market_research / real_demand / value_proposition / acquisition / paid_conversion / delivery / retention_referral，取值 0-10；evidence 可选（strong / weak / none，兼容 verified / partial），含义为定义深度与核对强度。封顶：none→3、weak/partial→6、strong/verified 不限。
The JSON must contain a scores object with the seven keys: market_research / real_demand / value_proposition / acquisition / paid_conversion / delivery / retention_referral, values 0-10; evidence is optional (strong / weak / none; verified / partial accepted as aliases) and means definition depth & cross-checking strength. Caps: none→3, weak/partial→6, strong/verified unlimited.
- 证据表单保护：运行 market_research.py（非 --score-only）会保留已填证据、只更新检索词；表单属于其他产品时拒绝覆盖并提示 --force。
  Evidence form protection: re-running the research script preserves filled evidence and only refreshes queries; it refuses to overwrite a form belonging to another product unless --force is given.

## 修复模式工作法 Repair Mode
修复按「断裂 → 薄弱 → 增长杠杆」顺序逐项进行。AI 不直接修改用户产品，而是为每项输出**完整修改方案**：目标 → 具体改动 → 实施步骤 → 验收标准；用户确认后自行执行，执行完成可要求复检。
Fixes proceed item by item in the order "broken → weak → growth levers". The AI does not modify the product; for each item it outputs a **complete fix plan**: goal → concrete changes → implementation steps → acceptance criteria; the user executes after confirming and may request a re-check when done.
各环节常见修复杠杆（作为方案内容素材）Common repair levers per stage (material for the plans):
市场调研 Market Research：配置搜索 API key 后重跑调研（TAVILY_API_KEY / SERPER_API_KEY / BING_API_KEY）；补齐缺失指标；把行业数据落进画像、定价与渠道选择；读「社区信号」核对真实需求；用 references/interview.md 做 3-5 个目标用户访谈
- 真实需求 Real Demand：目标人群与决策状态定义模板、相邻人群区分表、桌面研究清单（社区/竞品/公开报告） target-segment & decision-state definition template, adjacent-segment distinction table, desk-research checklist (communities/competitors/public reports)
- 价值主张 Value Proposition：一句话价值主张模板（为谁含决策状态/解决什么/为什么是你）、落地页首屏文案、与替代方案对比表 one-sentence value proposition template, landing-page above-the-fold copy, comparison table vs alternatives
- 获客 Acquisition：种子用户获取计划（渠道 + 话术 + 数量目标）、落地页结构、内容选题清单、用 references/growth-experiments.md 设计渠道与文案 A/B 实验 seed-user acquisition plan (channels + scripts + targets), landing page structure, content topic list, A/B experiments via references/growth-experiments.md
- 付费转化 Paid Conversion：3 档定价方案、免费/付费边界定义、支付流程清单、用 references/economics.py 测算 LTV/CAC 与回本周期 3-tier pricing, free/paid boundary, checkout checklist, LTV/CAC model via references/economics.py
- 交付与体验 Delivery & Experience：激活路径设计（3 步内兑现核心价值）、新手引导文案、激活指标定义 activation path (core value within 3 steps), onboarding copy, activation metric definition
- 复购传播 Retention & Referral：留存机制设计（习惯循环/内容更新/续费提醒）、推荐奖励方案、流失召回路径、用 references/growth-experiments.md 设计留存/推荐 A/B 实验 retention mechanics (habit loops/updates/renewal reminders), referral rewards, win-back paths, A/B experiments via references/growth-experiments.md

## 产品化输出（可选交付物）Productize (optional deliverable)
用户诊断后可要求「产品化输出」：AI 按 references/pitch-template.md 生成 30 秒 pitch、一句话价值主张、
落地页首屏结构与文案、三档定价卡、冷启动渠道清单。产出的是给用户的材料，不直接修改用户产品。
On request the AI produces pitch / value proposition / landing-page hero / pricing cards / cold-start channels
per references/pitch-template.md — materials FOR the user, never direct edits to their product.

## 增长实验（可选验证工具）Growth Experiments (optional validation)
修复「获客 / 复购与传播」时，AI 按 references/growth-experiments.md 输出实验卡（假设、指标、样本、门槛、决策规则）；
实验结果回填证据档（A/B 达标且可重复 = strong、单次观察 = weak、未测 = none）并作为复检依据。
When fixing Acquisition or Retention & Referral, the AI outputs experiment cards per references/growth-experiments.md;
outcomes update evidence tiers (replicated A/B hit = strong, single observation = weak, untested = none) and drive re-checks.

## 复检规则 Re-check
用户可随时要求「复检」：用当前证据重新逐环节打分，对比上次分数，更新结论与剩余行动。
The user may request a "re-check" anytime: re-score each stage with current evidence, compare with the previous scores, and update the verdict and remaining actions.
复检输出：分数对比表（上次/本次/变化）+ 更新后的结论 + 剩余行动。分数提升说明修复有效；未提升的环节继续进入修复队列。
Re-check output: score comparison (previous/current/delta) + updated verdict + remaining actions. Improvements show the fix worked; unchanged stages stay in the repair queue.
- 状态持久化：每次出报告时，把七环分数与结论同时保存到工作目录 dandelion-scores.json；复检时先读取该文件作为「上次分数」基线，避免跨会话丢失对比依据。
  Persistence: every report also writes the seven scores to dandelion-scores.json in the working directory; re-checks read it as the previous-score baseline.

