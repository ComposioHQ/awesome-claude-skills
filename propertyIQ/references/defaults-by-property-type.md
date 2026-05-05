# Default Underwriting Assumptions by Property Type

These represent industry-standard, conservative (not optimistic) inputs for feasibility screening.
Always disclose which defaults are being used and invite the user to override.

---

## Single-Family Rental (SFR)

| Assumption | Conservative Default | Notes |
|---|---|---|
| Down Payment | 25% | Investment property conventional minimum |
| Interest Rate | Current 30yr investment conv. (search if unsure) | Add ~0.75% to primary home rate |
| Amortization | 30 years | Standard |
| Vacancy | 5% | SFR turnover avg; use 8% in soft markets |
| CapEx Reserve | 5–8% of gross rent | Major capital items only: roof, HVAC, appliances. Set aside, not spent annually |
| Maintenance/Repairs | $75–125/mo | Ongoing minor repairs, separate from CapEx |
| Property Mgmt | 10% of EGI | Standard SFR PM rate |
| Insurance | $1,200–$2,500/yr | Varies by region/size; see insurance-benchmarks.md |
| Closing Costs | 2.5% of purchase price | Includes inspection, title, origination |
| OpEx Ratio Target | 45–55% | Flag if model shows <40% — likely understated (high-tax states routinely hit 60%+) |

---

## 2–4 Unit Multifamily (Small Multifamily)

| Assumption | Conservative Default | Notes |
|---|---|---|
| Down Payment | 25% | Investment property; 3.5% FHA if owner-occupied |
| Interest Rate | Current 30yr investment conv. | Similar to SFR if < 5 units |
| Amortization | 25–30 years | Use 25yr for conservative model |
| Vacancy | 7% | Higher turnover risk per unit vs. larger buildings |
| CapEx Reserve | $100–150/unit/mo | Major capital items only; separate from maintenance |
| Maintenance/Repairs | $50–75/unit/mo | Ongoing minor repairs, separate from CapEx |
| Property Mgmt | 8–10% of EGI | Use 10% if not self-managed |
| Insurance | $800–1,500/unit/yr | See insurance-benchmarks.md |
| Closing Costs | 2.5% of purchase price | |
| OpEx Ratio Target | 45–55% | Expenses higher per unit in small MF |

---

## 5–20 Unit Multifamily

| Assumption | Conservative Default | Notes |
|---|---|---|
| Down Payment | 25–30% | Commercial loan territory; use 25% if DSCR-eligible |
| Interest Rate | Current commercial/DSCR rate (~7.0–8.5% in 2025) | Search current rates |
| Amortization | 25 years | Standard commercial |
| Vacancy | 8% | Industry standard for stabilized 5–20 unit |
| CapEx Reserve | $75–100/unit/mo | Major capital items only; separate from maintenance |
| Maintenance/Repairs | $40–60/unit/mo | Ongoing minor repairs, separate from CapEx |
| Property Mgmt | 8% of EGI | Professional management expected at this size |
| Insurance | $600–1,000/unit/yr | Bulk rate benefit |
| Closing Costs | 3% of purchase price + 1–2 points | Points = 1–2% of loan amount; add on top of base closing costs |
| OpEx Ratio Target | 45–55% | Flag if <40% — likely understated |

---

## Utility Ownership — Owner-Paid Expense Estimates

When utilities are owner-paid, add these to expenses:

| Utility | Per-Unit Annual Estimate |
|---|---|
| Water/Sewer | $600–$1,200/unit |
| Trash | $200–$400/unit |
| Gas (heat) | $800–$1,500/unit |
| Electric (common) | $300–$600/unit total |
| Lawn/Snow | $500–$2,000/year total |

---

## Notes on Interest Rates

Always search for current rates rather than using a hardcoded number:
```
web_search: "current investment property mortgage rate [year]"
web_search: "DSCR loan rates today [year]"
```

As of early 2025, typical investment property 30yr rates: 7.0–7.75%
Commercial 5/1 ARM or DSCR loans: 7.25–8.5%

These change — always verify before presenting to user.
