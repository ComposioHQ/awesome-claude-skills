---
name: Claude Ecom
description: Turn order or sales CSV data into ecommerce business reviews with KPI decomposition, prioritized findings, and concrete next actions.
---

# Claude Ecom

Turn any orders/sales CSV into a business review — executive summary, multi-horizon KPI dashboard, revenue decomposition, prioritized findings, and an action plan. One command.

## When to Use This Skill

- Monthly or quarterly business reviews for an ecommerce store
- Investigating why revenue dropped (or spiked) and need a structured breakdown
- Checking customer retention and repeat purchase health
- Preparing data-backed recommendations for stakeholders
- Getting a consultant-quality report without hiring a consultant

## What This Skill Does

1. **Multi-horizon KPIs** — automatically analyzes 30-day, 90-day, and 365-day trailing windows so you see the pulse, momentum, and structural trends at once.
2. **Revenue decomposition** — splits revenue into new vs. returning customers, shows AOV, order frequency, and flags where growth is coming from (or leaking).
3. **Health checks** — runs 15+ checks across Revenue, Customer, and Product categories, each returning pass / watch / fail with business context.
4. **Prioritized action plan** — findings are ranked by impact, each with "what happened / why it matters / what to do next" and concrete deadlines.

## How to Use

### Install

```bash
curl -fsSL https://raw.githubusercontent.com/takechanman1228/claude-ecom/v0.1.3/install.sh | bash
```

Requires: Claude Code CLI, Python 3.10+, and git.

### Run

```
/ecom review              → full business review (auto 30d/90d/365d)
/ecom review 90d          → focused on last 90 days
/ecom review How's retention?  → answers a specific question from the data
```

### Input

Any ecommerce/retail orders CSV. Required columns: order ID, order date, customer ID or email, revenue. Optional: quantity, SKU/product name, discount amount.

## Example

```
# Business Review
> Revenue reached $9.37M for the year, essentially flat YoY (-1.7%), despite strong
> short-term momentum — the last 90 days surged 84% and November posted +28.5%...
```

```
           30d Pulse       90d Momentum     365d Structure
Revenue    $1.47M (+ 28%)  $3.73M (+ 84%)   $9.37M (= -2%)
Orders     3,499 (+ 26%)   8,814 (+ 60%)    24,812 (- 11%)
AOV        $419 (+ 2%)     $424 (+ 15%)     $378 (+ 10%)
Customers  1,676 (+ 11%)   2,918 (+ 51%)    4,296 (= flat)
```

```
Revenue $9.37M (YoY: -1.7%)
├── New Customer Revenue $1.45M (15.5%)
│   ├── New Customers: 1,559 (-57.8%)
│   └── New Customer AOV: $305
└── Existing Customer Revenue $7.92M (84.5%)
    ├── Returning Customers: 2,737 (+345%)
    ├── Returning AOV: $395
    └── Repeat Purchase Rate: 75.4%
```

Executive summary → Multi-horizon dashboard → KPI trees → Findings with "what / why / what to do" → Prioritized action plan.

[See a full example report →](https://github.com/takechanman1228/claude-ecom/blob/main/examples/online-retail-ii/REVIEW.md)

## Tips

- Drop your CSV into the working directory before starting Claude Code — the skill auto-detects it.
- Use the question form (`/ecom review How's retention?`) to get a focused answer instead of a full report.
- For multi-store analysis, run each CSV separately and compare the generated `REVIEW.md` files.
- The Python backend owns all number crunching; Claude interprets. Numbers are always precise.

## Related Use Cases

- Monthly reporting for D2C brands, retail, or marketplace sellers
- Board or stakeholder decks backed by structured data
- Quick diagnostics when a metric moves unexpectedly
- Onboarding new analysts to a store's performance patterns

## Links

- [GitHub Repository](https://github.com/takechanman1228/claude-ecom)
- By [@takechanman1228](https://github.com/takechanman1228)
