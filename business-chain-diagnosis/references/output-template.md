# 商业链路诊断报告模板 Output Template

按以下结构输出完整报告（语言跟随用户提问语言）。
Output the full report in this structure (language follows the language of the user).

## 0. 报告信息 Report Info
- 模式 Mode：自检 Self-Check / 项目检查 Project Inspection
- 对象归属 Ownership：自己的项目 Your own / 他人的项目 Projects of others
- 证据来源 Evidence sources：列出实际依据（你的回答、README、官网、定价页、访谈记录、数据等）list the actual basis (your answers, README, website, pricing page, interviews, data, etc.)

## 1. 产品画像 Product Snapshot
一句话总结：目标用户、解决什么痛点、如何收费。
One-sentence summary: target users, the problem solved, how you charge.

## 2. 逐环节诊断 Per-Stage Diagnosis
市场调研环节直接引用 references/market_research.py 输出的 8 指标分数与证据来源；其余环节输出 Per stage:
- 判断 Judgment（1-2 句 1-2 sentences）
- 依据 Basis（注明来源 + 证据档 strong / weak / none，如「访谈 20 人」「无付费用户」；state the source and evidence tier, e.g., 20 interviews, no paying users）
- 分数 Score（0-10）
- 证据不足标记 Evidence flag（如有：列出需补充的信息 if any: list what to supply）

## 3. 总分与结论 Verdict
- 各环节分数表（七环 + 平均分）Score table (7 stages + average)
- 结论 Verdict：链路打通 Loop Closed / 接近打通 Nearly Closed / 未打通 Not Closed，附一句理由 with a one-line reason
- 他人项目 Projects of others：结论前注明「基于公开证据，不代表产品真实状态」prefix "based on public evidence, not the true state of the product"

## 4. 问题清单 Problem List
按优先级排序：断裂环节问题 → 薄弱环节问题。每条包含：环节、问题、影响。
Ordered by priority: broken-stage problems → weak-stage problems. Each item: stage, problem, impact.

## 5. 修复方案 Fix Plan
对应每个问题给出**完整修改方案**：目标、具体改动、实施步骤、验收标准。AI 只提供方案，由用户自己执行修改。
For each problem, give a **complete fix plan**: goal, concrete changes, steps, acceptance criteria. The AI provides plans only; the user executes the changes.

## 6. 行动清单 Action Plan
Top 3-5 行动：动作、针对环节、预期影响、所需信息或资源。
Top 3-5 actions: action, target stage, expected impact, needed info or resources.

## 7. 修复进度 Repair Progress
逐项列出：问题/环节、状态（待修复 / 执行中 / 已完成）、产出物（修改方案）、执行人（用户）、复检结果（分数变化）。
Itemized: problem/stage, status (pending / in progress / done), deliverable (fix plan), executor (user), re-check result (score delta).

## 8. 导出与分享 Export
- 默认生成 Markdown 报告文件：保存到当前工作目录 business-chain-report.md，可直接分享。 By default generate a Markdown report: save as business-chain-report.md in the working directory, shareable.
- 文件结构 = 本模板全部章节（0-7）。 File structure = all sections of this template (0-7).
- 需要 PDF / DOCX 等其他格式时，按用户要求转换输出。 Convert to PDF/DOCX or other formats on request.


