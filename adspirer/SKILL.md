---
name: adspirer
description: Manage Google Ads and Meta (Facebook/Instagram) advertising campaigns — create, analyze, and optimize ads. Use this skill when the user wants to work with Google Ads or Meta Ads: creating campaigns, analyzing performance, writing ad copy, optimizing budgets, or troubleshooting ad issues.
---

# Adspirer — Google & Meta Ads Management

Manage and optimize Google Ads and Meta Ads campaigns.

## Capabilities

- Analyze campaign performance and surface insights
- Write high-converting ad copy (headlines, descriptions, CTAs)
- Recommend targeting, bidding, and budget strategies
- Diagnose underperforming campaigns
- Build campaign structures for new products/promotions
- Interpret ad metrics and suggest optimizations

## Key Metrics Reference

### Google Ads
| Metric | Good benchmark |
|--------|---------------|
| CTR (Search) | > 3-5% |
| CTR (Display) | > 0.35% |
| Quality Score | 7-10 |
| Conversion Rate | Varies by industry; compare vs account average |
| ROAS | Depends on margins; typically target > 3x |
| CPA | Below target CPA set for campaign |

### Meta Ads
| Metric | Good benchmark |
|--------|---------------|
| CTR (Link) | > 1% |
| CPM | Varies by audience/placement |
| Frequency | Keep < 3-4 for conversion campaigns |
| ROAS | Target varies; compare vs blended |
| Relevance Score / Quality Ranking | Above average |

## Campaign Structure

### Google Ads
```
Account
  └── Campaign (budget, bidding, location, device targets)
        └── Ad Group (keyword/audience theme)
              ├── Keywords (match types: broad, phrase, exact)
              └── Ads (RSA, Performance Max, Display)
```

### Meta Ads
```
Account
  └── Campaign (objective: Awareness, Traffic, Conversions, etc.)
        └── Ad Set (audience, budget, schedule, placement)
              └── Ads (creative: image, video, carousel)
```

## Ad Copywriting

### Google Search Ad (RSA)
- **Headlines**: Up to 15 headlines (30 chars each) — include keyword, benefit, CTA
- **Descriptions**: Up to 4 descriptions (90 chars each) — expand on benefits, USP
- **Best practices**: Pin headline 1 to brand/keyword, use all 15 headlines

Example:
```
Headline 1: [Keyword-based] "Buy Running Shoes Online"
Headline 2: [Benefit] "Free Shipping on Orders $50+"
Headline 3: [CTA] "Shop Top Brands Today"
Headline 4: [Social proof] "50,000+ Happy Customers"

Description 1: "Discover our wide selection of running shoes from top brands. Find your perfect fit with free returns."
Description 2: "Shop Nike, Adidas, Brooks & more. Fast shipping available. Order by 3pm for same-day dispatch."
```

### Meta Ad
- **Primary text**: 125 chars visible before "See more" (key message first)
- **Headline**: 40 chars — punchy benefit or offer
- **Description**: 30 chars — supporting detail
- **CTA button**: Match to action (Shop Now, Learn More, Sign Up, etc.)

## Audience Targeting

### Google Ads
- **Search**: Keywords define audience intent — use negative keywords to exclude irrelevant traffic
- **Performance Max**: Asset-based; uses Google's signals
- **Audiences**: Remarketing, Customer Match, Similar Audiences, In-Market, Affinity

### Meta Ads
- **Core audiences**: Demographics, interests, behaviors
- **Custom audiences**: Website visitors (pixel), email lists, app users, video views
- **Lookalike audiences**: 1-10% lookalike from Custom Audience source
- **Best practice**: Start with 3-5% lookalike from buyers; narrow with interest stacking

## Optimization Workflow

When asked to optimize a campaign:

1. **Audit performance** — identify top/bottom performers at campaign, ad set, and ad level
2. **Budget allocation** — shift budget toward top performers
3. **Bid adjustments** — device, location, time-of-day adjustments
4. **Pause underperformers** — cut ad sets/ads below CPA threshold (after sufficient data)
5. **Test new creative** — if CTR low, test new headlines/images
6. **Audience refinement** — narrow or expand based on performance data
7. **Negative keywords** (Google) — review Search Terms report weekly

## Troubleshooting Common Issues

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| High CPC, low CTR | Low Quality Score / irrelevant audience | Improve ad relevance to keywords; tighten targeting |
| Good CTR, low conversions | Landing page issue | A/B test landing page; check tracking |
| Ads not delivering | Low budget, disapproved ads, narrow audience | Increase budget; fix policy issues; broaden audience |
| ROAS declining | Audience fatigue / increased competition | Refresh creative; test new audiences |
| Meta ads approved but no delivery | Audience too small, bid too low | Broaden audience; use Advantage+ placements |

## Notes for Claude

- Always ask for the user's goal before recommending (awareness vs leads vs sales vs ROAS)
- Ask for current metrics before optimization — don't recommend without data
- Budgets, bids, and targeting should be treated as hypotheses to test, not permanent decisions
- Follow platform policies — flag any creative that risks disapproval (misleading claims, restricted categories)
