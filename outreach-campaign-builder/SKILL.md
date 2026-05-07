---
name: outreach-campaign-builder
description: Orchestrate a complete multi-channel B2B outreach campaign — Apollo email export, HeyGen AI video generation, and Instantly campaign setup. Context-window safe by design.
requires:
  mcp: [rube]
---

# Outreach Campaign Builder

Runs a full campaign setup: Apollo (emails only, no enrichment) → HeyGen (one video per vertical) → Instantly (sequences). Designed to avoid context window overflow — never pipes raw Apollo enrichment JSON through Claude.

## Context Window Warning

Do NOT use `APOLLO_BULK_PEOPLE_ENRICHMENT` or `APOLLO_ORGANIZATION_SEARCH` inside Claude. These return multi-kilobyte JSON payloads per contact and will overflow the context window on any list larger than ~20 contacts.

Correct architecture:
- Apollo: pull name, email, title, company, city only (minimal fields)
- Enrichment: skip entirely — web search is cheaper and context-safe
- HeyGen: generate ONE video per vertical, reuse link for all prospects
- Instantly import: pass file path from GitHub marketing repo, not raw CSV content

## Full Workflow

### Phase 1 — List Building (Apollo, minimal fields only)

1. Always search for available tools first: call `RUBE_SEARCH_TOOLS` with query "apollo people search" to get current schema
2. Use `APOLLO_PEOPLE_SEARCH` with these fields only: `first_name`, `last_name`, `email`, `title`, `organization_name`, `city`
3. Apply ICP filters: industry, job titles, seniority, employee count, geography
4. Do NOT call `APOLLO_BULK_PEOPLE_ENRICHMENT` — export the list from Apollo UI as CSV instead
5. Commit the CSV to the fileflo-marketing GitHub repo: `leads/[vertical]-[date].csv`
6. For personalization, web-search 10–20 companies (50-word snippets only) → write custom first lines → store as `customVar1` in Instantly

### Phase 2 — HeyGen Video (Touch 3 of the sequence)

7. `HEYGEN_V2_TEMPLATES` → list available templates, select most professional avatar for vertical
8. `HEYGEN_RETRIEVE_TEMPLATE_DETAILS_V3` → get exact variable structure (required before generation)
9. `HEYGEN_V2_TEMPLATE_GENERATE` → generate one 30-second video using vertical-specific script
10. Poll `HEYGEN_RETRIEVE_VIDEO_STATUS_DETAILS` until status = complete
11. `HEYGEN_RETRIEVE_SHARABLE_VIDEO_URL` → get public link
12. Use ONE video URL for all prospects in this vertical — no per-contact personalization (cost-prohibitive)
13. Embed video link in Touch 3 email with thumbnail text: `[▶ Watch the 30-sec demo]`

### Phase 3 — Instantly Campaign Setup

14. Search tools: `RUBE_SEARCH_TOOLS` with "instantly create campaign" to confirm current schema
15. `INSTANTLY_CREATE_CAMPAIGN` with:
    ```
    campaign_name: "[Vertical] - [Month Year]"
    schedule: Mon–Fri, 08:00–17:00 prospect local time
    daily_limit: 50 per sending account
    stop_on_reply: true
    track_opens: true
    track_clicks: false
    ```
16. Add the 8-touch sequence with delays: 0, 2, 2, 3, 3, 3, 4, 3 days
17. `INSTANTLY_ADD_LEADS_BULK` → import from the Apollo CSV in the marketing repo
18. Confirm with `INSTANTLY_GET_CAMPAIGN` → verify sequence step count, delays, and settings

## Quality Gates (check after first 50 sends)

| Metric | Target | Action |
|--------|--------|--------|
| Open rate | ≥ 35% | Below 25% → pause, rewrite subject lines |
| Reply rate | 3–5% | Below 1% at 100 sends → rewrite T1 body |
| Bounce rate | < 3% | Hard stop — clean list before resuming |
| Spam complaints | < 0.1% | Immediate campaign pause |

## A/B Test Protocol

- Split first 200 recipients equally between Subject A and Subject B
- Wait 48 hours (open rates stabilize in 24–48h)
- Pick winner if one variant has ≥20% higher open rate
- Apply winning variant to all remaining contacts
- Document winner + reason in `fileflo-marketing/reports/`

## Known Pitfalls

| Pitfall | Fix |
|---------|-----|
| Apollo enrichment floods context | Never call enrichment inside Claude — use web search instead |
| HeyGen template variables missing | Always call `HEYGEN_RETRIEVE_TEMPLATE_DETAILS_V3` before generation |
| HeyGen video URL expires in 7 days | Regenerate by calling `HEYGEN_RETRIEVE_VIDEO_STATUS_DETAILS` again |
| Instantly timezone errors | Specify prospect timezone explicitly — do not leave blank |
| Sequence incomplete on creation | All 8 steps must be included in the initial `INSTANTLY_CREATE_CAMPAIGN` call |
