---
name: campaign-analytics-reporter
description: Pull Instantly campaign metrics, benchmark performance against targets, identify winning and losing elements, and produce a weekly report with prioritized next actions.
requires:
  mcp: [rube]
---

# Campaign Analytics Reporter

Pulls live data from all active Instantly campaigns and produces a weekly performance report. Identifies what's working, what needs to be killed or rewritten, and what to do next week.

## When to Use This Skill

Run every Friday. Takes 5–10 minutes to produce a complete weekly report.

## Full Workflow

### Step 1 — Pull Campaign Data

Always search for current tool schemas first:
```
RUBE_SEARCH_TOOLS query: "instantly list campaigns"
RUBE_SEARCH_TOOLS query: "instantly get campaign"
```

1. `INSTANTLY_LIST_CAMPAIGNS` → get all campaign IDs and names
2. For each active campaign: `INSTANTLY_GET_CAMPAIGN` → pull metrics:
   - emails_sent, emails_delivered, emails_opened, emails_clicked, emails_replied, emails_bounced, emails_spam

### Step 2 — Calculate Performance Metrics

For each campaign:
```
open_rate = emails_opened / emails_delivered × 100
reply_rate = emails_replied / emails_delivered × 100
bounce_rate = emails_bounced / emails_sent × 100
spam_rate = emails_spam / emails_delivered × 100
```

### Step 3 — Benchmark Against Targets

| Metric | Target | Warning | Hard Stop |
|--------|--------|---------|-----------|
| Open rate | ≥ 35% | 25–35% (rewrite subjects) | < 25% (pause) |
| Reply rate | 3–5% | 1–3% (rewrite T1) | < 1% at 100 sends (rewrite everything) |
| Bounce rate | < 2% | 2–3% (clean list) | > 3% (hard pause) |
| Spam rate | < 0.05% | 0.05–0.1% (audit content) | > 0.1% (immediate pause) |

### Step 4 — Touch-Level Analysis

Identify which touch is generating the most replies (if Instantly provides this data):
- If T1 reply rate > 2%: scale this vertical — add 50 more contacts/week
- If T3 (video) generates replies: document the video angle that worked
- If touches T5–T8 generate zero replies: consider shortening sequence to 6 touches

### Step 5 — Subject Line A/B Results

For campaigns running A/B tests:
- Which subject line variant won? By what margin?
- Document the winner and reason (curiosity? specificity? brevity?)
- Apply winning variant to all remaining contacts

### Step 6 — Weekly Report Output

Produce a structured markdown report with:

```markdown
# FileFlo Campaign Report — Week [N] ([Date])

## Overall Performance
[Table: Campaign | Sent | Open% | Reply% | Bounce% | Status]

## 🟢 Winning (scale these)
[List campaigns at/above target]

## 🟡 Warning (optimize these)
[List campaigns in warning zone + specific fix]

## 🔴 Pause/Kill (action required)
[List campaigns at hard stop + required action]

## Subject Line Winners This Week
[A/B results]

## Action Items for Next Week
1. [Specific, prioritized action]
2. ...
3. ...

## Leads Needed
[Calculation: campaigns to scale × 50 leads/week = total Apollo pulls needed]
```

7. Save report to fileflo-marketing repo as `reports/week-[N]-[YYYY-MM-DD].md`

## Known Pitfalls

| Pitfall | Fix |
|---------|-----|
| Low open rate ≠ bad list | Check deliverability first — SPF/DKIM/DMARC configured? |
| Zero replies after T1 | Check if emails landing in spam (send test to Gmail/Outlook) |
| High open rate, zero replies | Subject line works, body copy doesn't — rewrite T1 body |
| Bounce rate creeping up | Clean list with Hunter.io verify before next import |
