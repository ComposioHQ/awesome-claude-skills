---
name: communication-protocol-setup
description: "Set up AI communication style via interactive Q&A. Use when a user wants to configure or calibrate how an AI assistant talks to them."
---

# Communication Protocol Setup

Turns "how an AI should talk to a user" from a static document into an interactive Q&A. The user answers a few plain-language questions, the AI generates a customized communication protocol, and guides the user to apply it to any AI tool (Claude Code, Codex, Cursor, ChatGPT, Hermes). Built for non-technical users who don't know what they don't know.

## Overview

When a non-technical user sets up an AI assistant, the biggest pain is that the AI doesn't know how to talk to them: it either overuses jargon, asks for confirmation at every step, or delivers something that isn't what they wanted. This skill fixes that by turning "how the AI should communicate" into an interactive questionnaire. The user answers plain-language questions by feel; the AI translates those answers into a concrete communication protocol and guides the user to apply it.

## When to Use

- The user asks to configure or calibrate how an AI communicates with them ("帮我配置沟通协议", "怎么用你", "新手配置").
- The user switches to a new AI tool/agent and wants to establish rapport quickly.
- The user feels the AI's communication style is wrong and wants to recalibrate.
- The user is a non-technical person setting up an AI assistant for the first time.

Do NOT use for technical users who already know exactly how they want the AI to behave, or when the user just wants a one-off answer.

## Core Workflow

### 1. Interactive Q&A (one or two questions at a time)

Ask the 8 questions in order, each in plain language. Never dump all 8 at once — it overwhelms non-technical users.

- **Q1 Technical background**: "你是程序员/技术人，还是普通用户？" → technical = use jargon; non-technical = explain terms.
- **Q2 Goal style**: "你交代任务时，喜欢给大概方向还是讲清每一步？" → big-picture = AI asks more rounds to translate into a plan; detailed = AI executes directly.
- **Q3 Acceptance style**: "AI 做完东西你希望：A) 直接给结果 B) 做几个版本让你挑 C) 先看方案再动手？" → B = AI makes multiple samples, user picks by feel; C = AI proposes first, confirms, then acts.
- **Q4 Proactivity**: "你希望 AI 多主动还是多问？" → proactive = technical things done directly, reversible things done directly; ask-first = confirm every step.
- **Q5 Feedback style**: "不满意时你能说清哪里不对，还是只能说'感觉不对'？" → only-feel = AI diagnoses, feedback is direction not blueprint.
- **Q6 Reply length**: "你希望 AI 回复：A) 简短结论 B) 详细报告 C) 看情况？" → short = conclusion first; detailed = structured expansion.
- **Q7 Red lines (always ask)**: "AI 做哪些事之前必须问你？比如删文件、重启、花钱、改配置。" → user answers freely, AI compiles into a red-line list.
- **Q8 Cost**: "你担心 AI 花钱吗？有预算上限吗？" → not-worried = ignore cost; worried = AI reports before spending.

Pacing rules:
- After each answer, restate in one sentence ("所以你是普通用户，希望我多主动，对吧？"), let the user confirm or correct.
- If the user answers vaguely, offer 2-3 options to pick from (by feel, no description needed).
- If the user says "随便/你定", use the defaults and say so.
- When all questions are answered, summarize into a protocol and let the user review.

### 2. Generate the protocol

Output a customized communication protocol with this structure:

```markdown
# 沟通协议（定制版）

## 一句话判断标准
能反悔直接干，不能反悔先问。

## 沟通方式
1. **目标**：<per Q2>
2. **验收**：<per Q3>
3. **反馈**：<per Q5>
4. **主动性**：<per Q4>
5. **术语**：<per Q1>
6. **回复**：<per Q6>
7. **过程透明**：简单说为什么；完整过程存档可查
8. **语气**：无所谓，核心是听懂
9. **汇报节奏**：关键节点
10. **记忆**：AI 主动记偏好
11. **平等纠错**：用户也会错，AI 可直接指出

## 红线（不可逾越）
<per Q7>

## 边界判断
| 情况 | 动作 |
|---|---|
| 能反悔（改配置、写文件、跑任务） | 直接干 |
| 不能反悔（删数据、覆盖、杀进程、花钱） | 先问 |
| 用户喊停 | 立即停，不辩解 |

## 成本
<per Q8>
```

### 3. Apply the protocol (guide the user)

Guide the user to apply the protocol to their target tool(s). When the tool has no config surface, guide manual setup:

1. **Claude Code / Codex / Cursor**: store as `CLAUDE.md` / `AGENTS.md` in the project root; the AI auto-loads it.
2. **Claude.ai / ChatGPT (web)**: store as a text block pasted at conversation start, or in Custom Instructions.
3. **Hermes**: store in `memories/USER.md` (user prefs) or `memories/MEMORY.md` (AI rules).
4. **Other agents**: check their docs for an "instructions file" or "system prompt" entry point.

Tell the user exactly which file to store the protocol in, with the full path. If the user can't operate files, the AI writes the file for them (reversible, just do it).

### 4. Multi-tool sync

Users often use several AI tools together (Hermes for heavy work, ChatGPT for chat, Claude for code). The protocol should be **generated once, exported in multiple copies**, synced to all tools.

Export:
1. **Main config** (full markdown) — for humans, the single source of truth.
2. **AGENTS.md version** — for file-reading project tools (Claude Code / Codex / Cursor).
3. **Custom-instructions version** — for web tools (Claude.ai / ChatGPT Custom Instructions).
4. **Paste-able version** — for tools with no config entry, pasted at conversation start.

Sync principle: the main config is the only source of truth; change only it, then re-export the others. Tell the user: "改配置只改主配置，其他份我帮你重新生成".

### 5. Recalibration (config goes stale)

Communication style isn't fixed once. The user will find "this rule is wrong" or "I want to change that". Provide a recalibration mode.

Trigger: user says "上次配的哪条不对", "我想改沟通方式", "重新校准".

Flow:
1. Read the existing config first.
2. Ask "哪条不对?" — the user may only say "感觉不对"; list the current rules one by one for them to pick.
3. **Change only the rule the user points at**, keep everything else (never redo it all).
4. Re-export all copies after the change (multi-tool sync).
5. Remind the user: run verification after the change to see if that rule actually improved.

### 6. Verification (metric-driven, not standard tests)

After configuring/improving, **tell the user which metrics to watch**; the user decides how to test. After improvement, these experience metrics should visibly improve.

Metrics to tell the user (per protocol dimension):
- **Goal**: does the AI ask "你到底要什么" less, and drift off-target less?
- **Acceptance**: does the AI make multiple samples for you to pick, instead of one result?
- **Feedback**: when you say "感觉不对", does the AI diagnose instead of asking for details?
- **Proactivity**: does the AI act more directly instead of asking every step?
- **Terms**: does the AI explain when it should, and not over-explain when it shouldn't?
- **Reply**: is it conclusion-first, not verbose, readable?
- **Red lines**: has the AI never crossed a line (asked before deleting/killing/spending)?

Tell the user: "配置后正常用几天，看这些指标有没有明显变好". The user decides how to test (they know their own usage best). Metrics are direction, not hard scores.

## Defaults (when the user says "随便/你定")

For non-technical users:
- Goal: user gives big-picture, AI asks more rounds to translate into a plan, confirms, then executes.
- Acceptance: AI makes multiple samples, user picks by feel.
- Feedback: user only gives feel, AI diagnoses.
- Proactivity: AI proactive, technical things done directly.
- Terms: don't assume the user understands; explain when needed.
- Reply: conclusion first, not too long.
- Red lines: read-only check first / ask before stop-restart-kill / always ask before delete-overwrite.
- Cost: subscription is enough, ignore for now; report before new paid additions.

## Anti-Patterns

- **Don't dump all 8 questions at once.** Ask one or two at a time; dumping overwhelms non-technical users.
- **Don't assume the user knows what they want.** The whole point of Q&A is that users answer by feel; the AI translates into rules.
- **Don't redo the whole protocol on recalibration.** Change only the rule the user points at; redoing everything wastes the user's trust.
- **Don't use standard tests for verification.** The user judges by experience metrics, not test scores.
- **Don't treat the protocol as one user's config.** It's a general, reusable setup for any non-technical user across tools.

## Cross-References

- For writing AI-facing docs and skills, see the `writing-for-agents` skill (pointer-based, disclosure-first).
- For one-three-one decision briefs, see the `one-three-one-rule` skill.

## Example

User: "帮我配置沟通协议，我是普通用户，不太懂技术。"

Agent: "好，我们一步步来。先问第一个：你交代任务时，是喜欢给一个大概方向让 AI 自己琢磨，还是喜欢把每一步都讲清楚？"

User: "大概方向吧，我不懂细节。"

Agent: "明白，你给大方向，AI 多问几轮翻译成计划，确认后再动手。下一个问题：AI 做完东西，你希望它直接给一个结果，还是做几个版本让你挑？"

... (continues through the 8 questions, then generates the protocol and guides application)