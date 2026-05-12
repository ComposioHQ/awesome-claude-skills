---
name: cc-toolkit
description: 35+ zero-dependency CLI tools for Claude Code — analytics, safety auditing, cost forecasting, reporting, and more. All tools run instantly with npx, no config needed.
---

# cc-toolkit

A collection of 35+ zero-dependency CLI tools that help you understand, analyze, and improve how you use Claude Code. Every tool runs instantly via `npx` with no configuration — your data stays local.

## When to Use This Skill

- You want to understand your Claude Code usage patterns (session time, streaks, active days).
- You need to monitor AI autonomy ratio, burnout risk, or estimated API costs.
- You want a quick productivity score, developer archetype, or "Spotify Wrapped"-style summary.
- You need to audit context window usage, commit quality, or ghost days (commits with no CC sessions).

## What This Skill Does

1. **Time & Productivity**: Session stats, streaks, day-of-week patterns, weekly reports.
2. **Health & Wellbeing**: Burnout risk scoring, break monitoring, sustainable pace tracking.
3. **AI Autonomy**: Agent load ratio (you vs AI), tool usage breakdown, subagent tracking.
4. **Cost & Forecasting**: API cost estimates, month-end projections.
5. **Quality & Code**: Commit impact, ghost days, review queue analysis.
6. **Context Management**: Context window fill percentage, compact timing.

## How to Use

### Browser (no install)

Visit [yurukusa.github.io/cc-toolkit](https://yurukusa.github.io/cc-toolkit/) and drop your `~/.claude` folder into any of the web tools:

- [cc-wrapped](https://yurukusa.github.io/cc-wrapped/) — Spotify Wrapped for Claude Code
- [cc-score](https://yurukusa.github.io/cc-score/) — 0-100 productivity score
- [cc-roast](https://yurukusa.github.io/cc-roast/) — AI-generated roast of your usage
- [cc-health-check](https://yurukusa.github.io/cc-health-check/) — Burnout risk + recommendations

### CLI (via npx)

```bash
npx cc-session-stats    # Hours, active days, streaks
npx cc-agent-load       # You vs AI time split
npx cc-context-check    # Context window fill %
npx cc-burnout          # Burnout risk score
npx cc-personality      # Your developer archetype
npx cc-cost-check       # Estimated API cost so far
```

### Advanced Usage

```bash
npx cc-weekly-report    # Weekly summary with trends
npx cc-heatmap          # Activity heatmap by hour/day
npx cc-ghost-days       # Days with commits but no CC sessions
npx cc-review-queue     # Pending review items
```

## Example

**User**: `npx cc-session-stats`

**Output**:
```
Claude Code Session Stats
=========================
Total sessions:     3,580
Total hours:        142.3
Active days:        58 / 60
Longest streak:     23 days
Avg session length: 2.4 min
Peak hour:          02:00 (night owl)
```

**Inspired by:** Built over 60 days of running Claude Code autonomously 24/7 — these tools answer the questions the author kept asking: "How much time am I actually spending?" and "Is the AI doing more work than me now?"

## Tips

- All tools are zero-dependency and work offline. Nothing is uploaded.
- Data is read from your local `~/.claude` directory.
- Works on macOS, Linux, and WSL2.
- Combine multiple tools for a full usage audit before optimizing your workflow.

## Common Use Cases

- Running a quick health check before a long coding session.
- Generating a weekly report to track productivity trends over time.
- Checking estimated API costs to stay within budget.
- Identifying ghost days where code was committed without any Claude Code sessions.
- Getting a fun "Wrapped" summary to share with teammates.
