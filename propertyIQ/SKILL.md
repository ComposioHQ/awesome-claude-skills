---
name: PropertyIQ
slash_command: propertyiq
description: >
  Full property underwriting skill for small residential investment properties (SFR and
  multifamily up to 20 units). Use this whenever a user provides a real estate listing URL
  (Zillow, Realtor.com, Redfin, LoopNet, Crexi, MLS, etc.) and wants to analyze whether buying it
  makes financial sense. Also triggers when the user says things like "analyze this deal", "run the
  numbers on this property", "is this a good investment", "underwrite this listing", or pastes any
  property address with a purchase price. Can also be invoked directly with /propertyiq [URL or
  address]. Produces a detailed underwriting memo including rent comps, debt service, NOI, cash
  flow, key metrics, a Safety Index with crime data for the zip code, risk flags, and a
  plain-English verdict. Covers SFR, duplexes, triplexes, quadplexes, and 5–20 unit multifamily.
  Use this skill even when the user just pastes a URL with no other context.
---

# PropertyIQ — Small Residential Investment Underwriter

## Slash Command
This skill can be invoked directly with:
  /propertyiq [listing URL]
  /propertyiq [address] [asking price]
  /propertyiq (no argument — prompts user for URL or address)

When called via slash command, skip the ambient trigger detection and proceed directly to
Step 1 with whatever the user provided after the command.

## Scope
PropertyIQ covers **small residential investment properties only**:
- Single-Family Rentals (SFR) — 1 unit
- Small Multifamily — Duplex, Triplex, Quadplex (2–4 units)
- Mid Multifamily — 5–20 units

**Out of scope (not handled by this skill):**
- Large multifamily (21+ units) — requires agency debt underwriting, T-12 actuals, loss-to-lease
- Mobile home parks — land-only income model, pad rent structure
- Short-term rentals (Airbnb/VRBO) — requires ADR/occupancy modeling, platform fees
- Student housing — per-bed pricing, academic-year lease structure
- Commercial / mixed-use — entirely different income and expense framework

If a user provides a property type that is out of scope, tell them clearly and explain
what type of analysis would be needed instead.

---

## Step 1 — Scrape the Listing

Use `web_fetch` on the URL the user provides. Extract:

**Property facts:**
- Address, city, state, zip
- Property type (SFR, duplex, triplex, quadplex, 5–20 unit, mixed-use)
- Number of units
- Year built
- Square footage (total and per unit if available)
- Bedrooms/bathrooms per unit
- Asking price
- Listed rents (if shown) — current and/or pro-forma
- Listed expenses (taxes, insurance, HOA if any)
- Utilities structure (tenant-paid vs. owner-paid — list which ones)
- Parking, laundry, amenities notes
- Days on market, price history if visible
- Any mentioned cap rate or GRM from the listing

If the page is behind a login or returns incomplete data, use `web_search` to look up the address
directly (e.g. `"123 Main St Springfield IL" site:zillow.com OR site:realtor.com`) and try
`web_fetch` on the best result.

---

## Step 2 — Fill Gaps with Market Research

### 2a. Rent Comps (ALWAYS run this if listing rents are missing or unverified)

Search for comparable rents in the same zip or neighborhood:

```
web_search: "[city] [state] [bed/bath] rental price [year]"
web_search: "[zip code] average rent [unit type]"
web_search: "rentometer [city] [state] [bedroom count]"
```

Pull 2–3 data points. Use the **median** of comps as your rent estimate. Note the range.
If the listing already shows rents, still search comps to validate — flag a delta >15% as a risk.

### 2b. Local Property Tax
If not on the listing, search: `"[address] property tax"` or `"[county] property tax rate"`.
Use assessed value × mill rate if you find it. Estimate conservatively if uncertain.

### 2c. Insurance Estimate
If not listed, use regional benchmarks from `references/insurance-benchmarks.md`.

### 2d. Safety Index — Crime & Neighborhood Data

ALWAYS run this step for every analysis. Search for crime and safety data for the
property's zip code and neighborhood. This data directly affects vacancy risk, tenant
quality, insurance premiums, and long-term appreciation — all of which are investor concerns.

**Search queries to run:**
```
web_search: "[zip code] crime rate statistics [year]"
web_search: "[city] [neighborhood] crime index safety score"
web_search: "NeighborhoodScout [zip code] crime"
web_search: "SpotCrime OR CrimeGrade [zip code]"
```

**Data points to collect (use what's available — not all will be found):**
- Overall crime index / safety score (e.g. CrimeGrade letter grade A–F, NeighborhoodScout
  percentile, SpotCrime score)
- Violent crime rate (per 1,000 residents) vs. national average
- Property crime rate (per 1,000 residents) vs. national average — most relevant for landlords
- Trend: is crime increasing, decreasing, or stable over last 3 years?
- Any neighborhood-specific context (proximity to high-crime areas, gentrification, etc.)

**Grading scale to apply consistently:**
  A (Very Safe):    Crime well below national avg — top 20% safest nationally
  B (Safe):         Crime meaningfully below national avg
  C (Average):      Near national avg — acceptable but flag for investor awareness
  D (Below Average):Crime above national avg — elevated vacancy/tenant/insurance risk
  F (High Risk):    Crime significantly above national avg — major investment risk flag

**Investor impact framing — always include at least one of these observations:**
- High property crime → elevated insurance premiums, higher vacancy, tenant turnover risk
- High violent crime → impacts tenant demand, lender scrutiny, appreciation drag
- Improving trend (crime declining) → positive for appreciation; potential value-add signal
  if buying ahead of neighborhood improvement; note gentrification may displace existing tenants
- Worsening trend (crime rising) → increasing vacancy risk, insurance pressure, value drag

**If data is unavailable:** Note "Safety data unavailable for this zip — recommend
checking CrimeGrade.org, NeighborhoodScout.com, or local PD crime map before proceeding."

---

## Step 3 — Confirm Assumptions with User

Before running numbers, present the scraped data and proposed assumptions in a brief confirmation
block. Example:

```
I found the following from the listing. Please confirm or correct before I run the analysis:

  Address:          123 Main St, Trenton, NJ 08611
  Property Type:    Triplex (3 units)
  Year Built:       1922
  Asking Price:     $485,000
  Unit Mix:         3x 2BR/1BA (~750 sqft each)
  Current Rents:    $1,400/unit/mo (listing)
  Rent Comps:       $1,350–$1,550/mo (Zillow/Rentometer median ~$1,450)
  Property Tax:     $9,200/yr (public record)
  Utilities:        Tenant-paid (all)

  Financing Defaults I'll use:
    Down Payment:     25% ($121,250)
    Interest Rate:    7.25% (current 30yr commercial avg)
    Amortization:     25 years
    Vacancy:          7% (multifamily standard)
    CapEx Reserve:    $125/unit/mo ($4,500/yr)
    Maintenance:      $60/unit/mo ($2,160/yr)
    Mgmt Fee:         8% of EGI (standard 3rd-party)
    Points:           0 (conventional loan)

  Override anything? Or type "run it" to proceed.
```

If the user says "run it" or provides no corrections, proceed with defaults.

---

## Step 4 — Run the Underwriting Calculations

### Industry-Standard Defaults by Property Type

Read `references/defaults-by-property-type.md` for the full table. Summary:

| Metric | SFR | 2–4 Unit | 5–20 Unit |
|---|---|---|---|
| Down Payment | 25% | 25% | 25–30% |
| Interest Rate | current 30yr conv. | current 30yr conv. | current commercial avg |
| Amortization | 30 yr | 25 yr | 25 yr |
| Vacancy | 5% | 7% | 8% |
| CapEx Reserve | 5–8% gross rent | $100–150/unit/mo | $75–100/unit/mo |
| Maintenance | $75–125/mo | $50–75/unit/mo | $40–60/unit/mo |
| Mgmt Fee | 10% EGI | 10% EGI | 8% EGI |
| OpEx Ratio Target | 45–55% | 45–55% | 45–55% |

Always use the **midpoint or conservative end** of ranges — these are feasibility screens, not
best-case projections.

### Calculations to Perform

```
Gross Potential Income (GPI)      = sum of all unit monthly rents × 12
Vacancy Loss                      = GPI × vacancy rate
Effective Gross Income (EGI)      = GPI − Vacancy Loss
Operating Expenses                = Taxes + Insurance + Mgmt Fee + CapEx Reserve
                                    + Maintenance/Repairs + Other
  NOTE: CapEx Reserve and Maintenance are SEPARATE line items:
    CapEx Reserve   = major capital items (roof, HVAC, appliances) — set aside, not spent annually
                      SFR: 5–8% gross rent | 2–4 unit: $100–150/unit/mo | 5–20 unit: $75–100/unit/mo
    Maintenance     = ongoing minor repairs
                      SFR: $75–125/mo | 2–4 unit: $50–75/unit/mo | 5–20 unit: $40–60/unit/mo
Net Operating Income (NOI)        = EGI − Operating Expenses
Annual Debt Service               = monthly P&I × 12  [use standard amortization formula]
Annual Cash Flow                  = NOI − Annual Debt Service
Monthly Cash Flow                 = Annual Cash Flow / 12

Cap Rate                          = NOI / Purchase Price
Cash-on-Cash Return (CoC)         = Annual Cash Flow / Total Cash Invested
  Show TWO versions:
    CoC (Down Payment only)       = Annual Cash Flow / Down Payment
    CoC (All-In)                  = Annual Cash Flow / (Down Payment + Closing Costs + Points)
  Primary CoC = down payment only (matches investor convention).
  Total Cash to Close = Down Payment + Closing Costs + Origination Points
    Closing Costs = 2.5% (SFR/2–4 unit) or 3% (5–20 unit) of purchase price
    Origination Points = 0 for conventional | 1–2% of loan amount for commercial/DSCR loans
Debt Service Coverage Ratio (DSCR)= NOI / Annual Debt Service
Loan-to-Value (LTV)               = Loan Amount / Purchase Price
Gross Rent Multiplier (GRM)       = Purchase Price / GPI
Break-Even Rent/Unit              = (Annual Debt Service + Operating Expenses) / (units × 12)
Price Per Unit                    = Purchase Price / units
1% Rule Check                     = (Monthly Rent / Purchase Price) × 100
  ≥1.0%  → passes quick screen; worth full underwriting
  0.7–1.0% → borderline; depends on market and appreciation thesis
  <0.7%  → fails rule; cash flow very unlikely at conventional financing
  Note: 1% rule is a blunt filter, not a decision — always run full NOI regardless
```

For monthly P&I use: M = P × [r(1+r)^n] / [(1+r)^n − 1]
  where P = loan amount, r = monthly rate, n = amortization months

---

## Step 5 — Build the Report

Output the report in this exact format. Do not skip sections. Do not use markdown headers —
use the ASCII formatting style shown.

```
========================================================================
PROPERTY UNDERWRITING: [ADDRESS]
REPORT DATE: [today's date]
========================================================================

--- PROPERTY OVERVIEW ---
Type:                   [SFR / Duplex / Triplex / etc.]
Year Built:             [year]
Units:                  [count]
Unit Mix:               [e.g. 3x 2BR/1BA ~750 sqft]
Utilities:              [Tenant-paid / Owner-paid (list which)]
Days on Market:         [if known]

--- CORE ASSUMPTIONS ---
Purchase Price:         $[X]
Down Payment:           $[X] ([X]%)
Loan Amount:            $[X]
Interest Rate:          [X]%
Amortization:           [X] Years
Vacancy Rate:           [X]%
CapEx Reserve:          $[X]/unit/mo ($[X] Annual)
Maintenance/Repairs:    $[X]/unit/mo ($[X] Annual)
Property Management:    [X]% of EGI ($[X] Annual)
Closing Cost Estimate:  $[X] ([X]%)
Origination Points:     $[X] ([X] pts on $[X] loan) [0 if conventional]
Total Cash to Close:    $[X]

--- RENT ROLL ---
Unit            Type            Monthly Rent        Annual Rent
---------------------------------------------------------------
[for each unit]
---------------------------------------------------------------
GROSS TOTAL     [sum mo]                            $[sum ann]

--- RENT COMP ANALYSIS ---
Source 1: [source] → $[X]–$[X]/mo for [bed/bath] in [area]
Source 2: [source] → $[X]–$[X]/mo
Median Market Rent:    $[X]/unit/mo
Listing Rent vs. Market: [X]% [above/below/in-line with] market
[Flag if >15% variance: "⚠ ABOVE-MARKET RENTS — verify lease terms"]

--- INCOME & EXPENSE CALCULATION ---
Gross Potential Income:             $[X]
Vacancy Adjustment ([X]%):        -($[X])
-----------------------------------------------
EFFECTIVE GROSS INCOME (EGI):       $[X]

Property Taxes:                   -($[X])
Insurance:                        -($[X])
Property Management ([X]%):       -($[X])
CapEx Reserve:                    -($[X])
Maintenance/Repairs:              -($[X])
[Other expense lines if applicable]
-----------------------------------------------
TOTAL OPERATING EXPENSES:         -($[X])
Operating Expense Ratio:            [X]%

NET OPERATING INCOME (NOI):         $[X]

--- DEBT SERVICE & CASH FLOW ---
Annual Debt Service (P&I):          $[X]
Monthly Debt Service:               $[X]
-----------------------------------------------
ANNUAL CASH FLOW:                   [+/−]$[X]
MONTHLY CASH FLOW:                  [+/−]$[X]

STATUS: [POSITIVE CASH FLOW / BREAK-EVEN / NEGATIVE CASH FLOW]

--- KEY PERFORMANCE METRICS ---
Cap Rate:                           [X]%
Cash-on-Cash Return (Down Pmt):     [X]%
Cash-on-Cash Return (All-In):       [X]%  (incl. closing costs + points)
Debt Service Coverage Ratio:        [X]x  [lender min: 1.20x]
Loan-to-Value (LTV):                [X]%
Gross Rent Multiplier (GRM):        [X]x
Price Per Unit:                     $[X]
1% Rule:                            [X]%  [passes / borderline / fails]
Break-Even Rent Per Unit:           $[X]/mo
Current Rent vs. Break-Even:        $[X] [above/below]

--- MARKET BENCHMARKS ([city/state]) ---
Typical Cap Rate (this market):     [X]–[X]%  → Deal is [above/below/in-line]
Typical GRM:                        [X]–[X]x
Target CoC (investor standard):     8–12%     → Deal is [above/below]
DSCR Lender Minimum:                1.20x     → Deal [passes/fails]

--- SAFETY INDEX: [zip code] ---
Overall Safety Grade:       [A/B/C/D/F]  ([source])
Violent Crime Rate:         [X] per 1,000 residents  (national avg: ~4/1,000)
Property Crime Rate:        [X] per 1,000 residents  (national avg: ~19/1,000)
Safer than:                 [X]% of U.S. cities/zip codes
Crime Trend (3yr):          [Improving / Stable / Worsening]
Key Finding:                [1–2 sentence plain-English summary of what this means
                             for the investor — vacancy risk, insurance, tenant demand]
Source(s):                  [CrimeGrade / NeighborhoodScout / SpotCrime / local PD / etc.]
[If data unavailable: "Safety data not found for [zip]. Recommend checking CrimeGrade.org
 or NeighborhoodScout.com before proceeding."]

--- BREAKEVEN & UPSIDE SCENARIOS ---
* Current Status: $[X]/unit/mo [above/below] break-even rent
* At $[+$25/unit]: NOI ~$[X] | Cash Flow ~[+/−]$[X]/yr
* Rent Growth (+5%): Rent ~$[X]/unit | Cash Flow ~[+/−]$[X]/yr
* Value at Current Cap ([X]%): $[X]  ([above/below] ask by $[X])
* Value at Market Cap ([X]%): $[X]

--- RISK FLAGS ---
[Generate 3–6 specific flags based on the actual property data. Examples:]
1. HIGH LEVERAGE: [X]% LTV → limited equity buffer; sensitive to value declines.
2. VINTAGE CONSTRUCTION: [year] build → elevated CapEx risk (roof, plumbing, electrical).
3. VACANCY CONCENTRATION: [X] units → one vacancy = [X]% income loss.
4. ABOVE-MARKET RENTS: Listing rents $[X] vs. $[X] market median → renewal risk.
5. NEGATIVE CASH FLOW: Deal requires rent growth to service debt.
6. [Any property-specific flags: flood zone, deferred maintenance mentions, etc.]

--- BOTTOM LINE ---
[3–5 sentence plain-English verdict. Cover: Is the deal feasible at asking price? What would
make it work? Is this an appreciation play, cash flow play, or value-add? What's the #1 risk?
What's the realistic path to positive returns?]

========================================================================
[Add at end if data was incomplete:]
DATA GAPS: [list anything that couldn't be confirmed — e.g. "Insurance estimate used; actual
quote needed." / "Rent comps limited; recommend Rentometer report for zip [XXXXX]."]
========================================================================
```

---

## Step 6 — Data Quality Notes

At the end, be transparent about confidence level:
- **HIGH**: All key inputs scraped or confirmed from public records
- **MEDIUM**: 1–2 inputs estimated (flag which)
- **LOW**: Rents or expenses are estimated — flag prominently and recommend user verification

---

## References

- `references/defaults-by-property-type.md` — Full default assumptions table by property type
- `references/insurance-benchmarks.md` — Regional insurance cost estimates
- `references/cap-rate-benchmarks.md` — Market cap rate ranges by metro tier

Read these reference files when you need the detailed benchmarks. They are not loaded by default
to keep context lean — pull them as needed.
