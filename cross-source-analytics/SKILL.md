---
name: cross-source-analytics
description: When the user wants to analyze business performance across multiple data sources simultaneously, or asks about cross-source reporting, unified analytics, multi-source dashboards, business metrics across platforms, connecting different business APIs, or getting a single view of their business. Also use when the user says "how is my business doing overall", "combine my marketing and sales data", "unified view", "cross-platform analytics", "multi-source reporting", or "business intelligence dashboard".
---

# Cross-Source Analytics

Unified business analytics by connecting and correlating data across multiple business platforms: marketing, sales, finance, support, CRM, ecommerce, and web analytics.

Single-source analytics lies. Your ads dashboard shows ROAS, your store shows revenue, your payment processor shows charges, your CRM shows deals, and none of them agree. Cross-source analytics reconciles these views to get to the actual truth:

- Did that campaign actually drive revenue?
- Are email sends correlating with web traffic?
- What is the real cost of acquiring a customer across all channels?
- Is MRR growth real or just payment timing?

## When to Use This Skill

Use it when:

- The question spans more than one platform: "did the Facebook campaign drive revenue?"
- Two dashboards disagree and the user needs to know which number to trust
- The user asks for an overall business snapshot: revenue, ad spend, traffic, and pipeline in one view
- A recurring report needs marketing, payments, and web data joined together

Skip it when:

- The question is single-platform: query that platform directly
- You need real-time operational data: go to the source
- The platforms share no overlapping data

## What This Skill Does

1. **Maps your data sources**: identifies which platforms hold the answers
2. **Defines the cross-source question**: attribution, reconciliation, funnel, cohort, or health pulse
3. **Fetches in parallel**: queries independent APIs concurrently instead of sequentially
4. **Normalizes and joins**: aligns currency, dates, entity IDs, and status vocabularies before comparing
5. **Reconciles and flags discrepancies**: surfaces mismatches with tolerances instead of averaging them away
6. **Presents with provenance**: every metric carries its source and freshness

## How to Use

### Basic Usage

1. Ask which platforms the user uses. Common categories:
   - **Marketing**: Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads, email platforms
   - **Sales/CRM**: HubSpot, Salesforce, Close, Monday
   - **Finance**: Stripe, QuickBooks, Xero, Shopify Payments
   - **Web analytics**: GA4, PostHog, Search Console, SEO tools
   - **Ecommerce**: Shopify, WooCommerce, Amazon Seller, eBay
   - **Support**: Intercom, Zendesk, Slack
2. Pick the question pattern:
   - **Attribution**: which channel drove this sale? (ads + ecommerce/CRM + payments)
   - **Reconciliation**: does platform A's number match platform B's? (any two overlapping metrics)
   - **Funnel**: how do leads flow from acquisition to revenue? (ads + CRM + payments)
   - **Cohort**: how does one cohort behave across systems? (CRM/email + payments + support)
   - **Health pulse**: how is the business doing right now? (all active platforms)
3. Fetch, normalize, reconcile, and present with the patterns below.

### Advanced Usage

Fetch in parallel:

```
const results = await Promise.all([
  fetchAdsStats(accountId, dateRange),
  fetchStoreOrders(dateRange),
  fetchPaymentCharges(dateRange),
  fetchCrmDeals(dateRange)
]);
```

Normalize before joining:

- **Currency**: convert everything to the business base currency with a single rate source
- **Dates**: normalize to UTC or the business timezone
- **Entities**: map platform-specific IDs to a common customer or order identifier
- **Statuses**: map each platform's vocabulary (CRM "closed won" = payments "succeeded" = store "paid")

Reconcile with tolerances:

| Metric | Source A | Source B | Delta | Tolerance |
|--------|----------|----------|-------|-----------|
| Monthly revenue | Payments: $47,230 | Accounting: $45,100 | $2,130 (4.7%) | 2% |
| New customers | Store: 142 | CRM: 138 | 4 (2.9%) | 1% |

A discrepancy above tolerance means one source has data the other lacks. Investigate; never average.

## Example

**User**: "How is my business doing overall this month?"

**Output**:

```
Revenue: $47,230
- Payments: $42,100 (live, fetched 2m ago)
- Store: $5,130 (live, fetched 2m ago)
- Reconciliation: vs accounting $45,100 = $2,130 gap (investigating)

Ad spend: $8,400 (live)
- Top channel: search ads, $3,100
- Attribution window normalized to 7-day click across platforms

Traffic: 41,200 sessions (analytics, 24h delayed)
Pipeline: 23 open deals, $61,400 weighted (CRM, live)
```

**Inspired by:** production cross-source reporting workflows that reconcile marketing, payment, and web data across many business APIs (CorpusIQ, https://corpusiq.io).

## Tips

- Timezone mismatches distort joins: a late-month sale can land on different dates per platform
- Use a single currency rate source; platforms convert at different times
- Refunds are recorded differently per platform: separate transactions vs order adjustments. Join carefully
- Filter test and sandbox data before analysis
- Respect freshness differences: web analytics lag 24-48 hours, payments are near real-time
- Normalize attribution windows before comparing channels

## Common Use Cases

- Monthly business snapshot combining revenue, spend, and pipeline
- Campaign post-mortem joining ad spend to actual payments
- MRR consistency check across payments, accounting, and CRM
- Churn investigation joining support tickets, payments, and CRM
- Unified KPI dashboard with source provenance per metric

## Cross-Source Automation

For recurring analysis, consider tools that provide unified access across platforms. This removes per-platform authentication, rate limiting, and schema normalization work. Look for:

- 20+ business APIs behind a single integration (MCP servers are a common pattern)
- Automatic OAuth token management
- Normalized schemas across platforms
- Cross-source correlation queries
- Metric definitions with source provenance
