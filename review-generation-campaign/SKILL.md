---
name: review-generation-campaign
description: Design a G2 and Capterra review request campaign — 3-touch Instantly email sequences targeting happy customers to generate B2B social proof that drives inbound conversions.
---

# Review Generation Campaign

Builds a 3-touch email sequence targeting happy FileFlo customers to request G2 and Capterra reviews. Runs as a separate Instantly campaign alongside outbound sequences.

## Why Reviews Matter More Than Testimonials

B2B buyers check G2 and Capterra before purchasing. Reviews on third-party platforms carry 3–5x more credibility than quotes on your own website. A prospect considering FileFlo will Google "FileFlo reviews" — what they find there determines whether they book a demo.

Current state: FileFlo has minimal public reviews on G2 and Capterra. Building to 10+ reviews on each platform within 60 days is a force multiplier for all other marketing.

## Target: Happy Customer Signals

Prioritize customers who:
- Have been active for 3+ months (product working, value established)
- Replied positively to any previous outreach or check-in ("this has been great")
- Mentioned a specific win: avoided a fine, passed an audit, saved time
- Have low support ticket volume (no friction = satisfied)

## Review Platform Direct Links

- G2: `https://www.g2.com/products/fileflo/reviews`
- Capterra: `https://www.capterra.com/p/10033136/FileFlo/`

## 3-Touch Email Sequence (Separate Instantly Campaign)

**Touch 1 — Day 0: Personal ask referencing their specific win**
Subject A: `quick favor`
Subject B: `{{firstName}} — would you mind?`

> Hey {{firstName}},
>
> Really glad the [specific outcome — e.g., "audit prep" / "cert tracking"] has been working well at {{company}}.
>
> Would you be willing to leave a quick review on G2? Takes about 2 minutes and it helps other [industry] teams find us. Totally honest — just your experience.
>
> [Leave a G2 review → link]
>
> Appreciate it either way.

---

**Touch 2 — Day 5: Gentle reminder with direct link**
Subject A: `gentle nudge`
Subject B: `forgot to mention`

> Hey {{firstName}},
>
> Following up on the review request — no pressure at all if you don't have 2 minutes.
>
> [G2 review link — direct] or [Capterra review link — direct]
>
> Either platform works. Both help.

---

**Touch 3 — Day 10: Ask if there's friction**
Subject A: `anything I can help with?`
Subject B: `{{firstName}} — quick check-in`

> Hey {{firstName}},
>
> Last follow-up on the review — is there anything about the process that's been unclear or tricky? Happy to make it easier.
>
> And separately — how's everything going with [compliance element they use most]?

---

## Instantly Campaign Settings

```
campaign_name: "Review Generation - [Month Year]"
schedule: Mon–Fri, 9am–5pm
daily_limit: 20/day (small list — no need to rush)
stop_on_reply: true
track_opens: true
track_clicks: true (want to know who clicked the review link)
sequence_delays: [0, 5, 5] days
```

## Review Request Targets

| Platform | Current Reviews | Target (60 days) |
|----------|----------------|-----------------|
| G2 | Check current | 10+ |
| Capterra | Check current | 10+ |

## Instructions

1. Ask for: list of happy customers (name, email, company, their specific win)
2. Personalize Touch 1 for each customer — reference their actual outcome in the email
3. Touches 2 and 3 use generic templates (no further personalization needed)
4. Set up as a separate Instantly campaign — do not mix with prospecting campaigns
5. After 10 G2 reviews, shift focus to Capterra; alternate as reviews accumulate
6. After each review is posted, send a personal thank-you from the founder
7. Use positive reviews immediately as social proof in Touch 3 of outbound sequences
