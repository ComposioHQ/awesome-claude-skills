---
name: icp-builder
description: Build a detailed Ideal Customer Profile with buyer personas, pain-point hierarchy, trigger events, and Apollo.io search parameters for targeted B2B outreach.
---

# ICP Builder

Produces a structured ICP document optimized for Apollo.io list-building and signal-based outreach. Output is ready to paste directly into Apollo search filters and use as the foundation for cold email sequences.

## When to Use This Skill
- Before starting any new outreach campaign or targeting a new vertical
- When refining an underperforming campaign's targeting
- When entering a new geographic market

## Output Structure

### 1. Firmographics
- Industry (NAICS codes + SIC codes for Apollo filtering)
- Employee range + estimated revenue range
- Geography: states/regions prioritized by regulatory enforcement density
- Technologies used (for technographic filtering in Apollo)

### 2. Buyer Personas (2–3 per vertical)
For each persona:
- Job title variations (exact strings to use in Apollo people search)
- Seniority level + department
- Day-to-day pain points (3–5 bullets)
- Nightmare scenario (the specific audit or fine that keeps them up at night)
- Current solution (what they do today — the status quo to displace)
- What "winning" looks like for them personally

### 3. Trigger Events (Buying Signals)
Events indicating they are in-market RIGHT NOW:
- Regulatory announcements in their state/region (OSHA blitz, DOT enforcement uptick)
- Job postings for HR/Safety/Compliance roles (actively building or fixing compliance)
- Construction permit pulls or company expansions (growing = more compliance exposure)
- Recent OSHA inspection records — public at osha.gov/pls/imis/establishment.search
- DOT violation records — public at safer.fmcsa.dot.gov
- News of industry-specific fines in their state or city

### 4. Apollo.io Filter Block (ready to paste)
```
INDUSTRY: [NAICS/SIC codes and category names]
JOB_TITLES: [exact title strings, comma-separated]
SENIORITY: [manager, director, owner, vp]
EMPLOYEE_COUNT: min–max
GEOGRAPHY: [state abbreviations]
KEYWORDS: [optional — regulatory terms specific to vertical]
```

### 5. Messaging Angles (ranked by pain acuity)
Rank from most to least visceral for this vertical:
1. Fear/audit risk angle (specific fine amounts + probability)
2. Time wasted on manual compliance work (hours per week)
3. Competitive displacement (peers using automated compliance, winning contracts)
4. ROI/dollar math (cost of FileFlo vs cost of one violation)

## Instructions

1. Ask: product name, one-sentence value prop, price, and target vertical
2. Research public enforcement data for that vertical:
   - OSHA: search "[vertical] OSHA violations [year] [state]"
   - DOT: search "FMCSA enforcement [year]" for transportation
   - State agencies: search "[state] [industry] compliance fines [year]"
3. Identify 2–3 personas with distinct pain profiles (e.g., Safety Manager ≠ HR Manager)
4. Map each persona to exact Apollo title search strings
5. Identify 3+ trigger events specific to this vertical and geography
6. Rank messaging angles by which pain produces the most visceral response
7. Output the full ICP document in the structured format above
8. Note: never use full Apollo enrichment JSON in Claude — it overflows context. Output is for human Apollo UI use + CSV export only.
