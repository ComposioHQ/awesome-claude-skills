---
name: tax-transaction-classifier
description: Classifies bank statement transactions into tax categories (VAT, income tax deductions, personal) and produces a working paper summary ready for an accountant to review.
---

# Tax Transaction Classifier

This skill helps freelancers and small-business owners turn a messy bank or card export into a structured working paper: each line gets a tax treatment, a confidence label, and plain-language notes for an accountant. It is designed for **preparation and review support**, not for filing a return on its own.

> **Disclaimer:** This is not tax or legal advice. Rates, thresholds, and form lines change by country and year. The model must verify amounts and rules against official guidance for the user's jurisdiction and period. A qualified professional must review outputs before filing.

## When to Use This Skill

- You have a CSV (or pasteable table) of bank or card transactions and need them grouped for VAT/GST/sales tax and income tax.
- You want every line labeled as business vs personal, deductible vs non-deductible, or VAT treatment (standard / exempt / reverse charge / out of scope).
- You need a **reviewer-facing** summary: assumptions, open questions, and items that need receipts or invoices.
- You are working **through an example jurisdiction** (the US is used below as a worked pattern); the same workflow applies elsewhere once the user supplies or loads local rules.

## What This Skill Does

1. **Ingests transactions** from CSV, pasted tables, or OCR text, normalizing dates, amounts, currency, and counterparty names.
2. **Classifies each line** using explicit outcome labels: **Classified**, **Assumed**, or **Needs Input** (see below).
3. **Applies conservative defaults** when information is missing (assume less favorable tax treatment and disclose the assumption).
4. **Produces four outputs**: working paper (line by line), reviewer brief (assumptions and citations to user-provided or official rules), action list (what to collect or fix), and a short review checklist.
5. **Stays portable**: no external files required; optional links to official sources the user asks you to verify.

## Classification Contract

Every transaction receives **exactly one** of these outcomes:

| Outcome | Meaning |
|--------|---------|
| **Classified** | Enough facts to apply a rule; no reviewer flag unless the user wants spot checks. |
| **Assumed** | A fact is missing; a **conservative** default was applied. State the assumption and estimated cash impact. |
| **Needs Input** | Cannot proceed without one targeted question (e.g., "Was this trip 100% business?"). |

## Conservative Defaults Principle

When uncertain, choose the treatment that tends to **increase tax or reduce deductions** relative to the alternative, and say so explicitly. Reviewers can unwind an over-conservative line; they cannot always fix an aggressive one from incomplete data.

## Instructions

When the user asks you to classify transactions for tax prep:

1. **Confirm scope**
   Ask (if not given): jurisdiction, tax year or period, entity type (sole trader, company, etc.), and whether they are VAT/GST registered. If they decline, default to **Needs Input** for any line that depends on that fact.

2. **Normalize the ledger**
   Build an internal table: date, description, payee, amount in/out, currency, running balance if provided. Flag duplicates, obvious transfers between own accounts, and FX if multi-currency.

3. **Classify in passes**
   - **Pass A — Mechanical:** fees, interest, taxes, payroll, loan principal/repayments using clear labels.
   - **Pass B — Supplier heuristics:** match common merchants (utilities, software subscriptions, fuel) to likely categories; if ambiguous, **Assumed** or **Needs Input**, not a silent guess.
   - **Pass C — VAT logic (if registered):** identify sales vs purchases, exempt supplies, reverse charge indicators (e.g., foreign SaaS invoices), and missing invoices.

4. **Never invent statute**
   If the user has not supplied country skill text, state general principles only and mark rates/thresholds as **"verify with official guidance"**. Prefer **Needs Input** over a precise percentage you are unsure about.

5. **Outputs (always produce all four)**
   - **Working paper:** table with columns: Date | Description | Amount | Category | Tax treatment | Outcome | Notes for reviewer.
   - **Reviewer brief:** grouped assumptions, sorted by approximate money impact.
   - **Action list:** documents to fetch, registrations to confirm, corrections to bank labels.
   - **Review checklist:** yes/no items for the accountant (e.g., "Confirmed home office apportionment").

6. **Privacy**
   Redact account numbers in examples. Do not store or transmit unnecessary PII.

## How to Use

### Basic Usage

```
Here is my bank statement CSV for 2025. I'm a freelance developer filing Schedule C in the US.
Classify every line for income tax and give me the four outputs.
```

### Advanced Usage

```
Same file, but:
- Treat all lines containing "TRANSFER" between my Chase accounts as non-P&L.
- Flag anything over $600 that might need a 1099 check.
- Produce totals grouped by Schedule C line (gross income, advertising, office, utilities, other).
```

## Example

**User:** "Classify these lines for my 2025 taxes (USD). I'm a freelance developer filing Schedule C."

| Date | Description | Amount |
|------|-------------|--------:|
| 2025-03-02 | ZELLE FROM ACME CORP | 4,500.00 |
| 2025-03-05 | COMCAST BUSINESS INTERNET | -89.99 |
| 2025-03-12 | VERIZON WIRELESS | -65.00 |
| 2025-03-15 | AMZN MKTP US*AWS | -142.00 |
| 2025-03-22 | STARBUCKS STORE 1847 | -7.25 |

**Output** (abbreviated working paper — full run must still include reviewer brief, action list, and checklist):

| Date | Description | Amount | Category | Schedule C line | Outcome | Notes |
|------|-------------|-------:|----------|-----------------|---------|-------|
| 2025-03-02 | ZELLE FROM ACME CORP | 4,500.00 | Client receipt | Line 1 — Gross receipts | **Needs Input** | Confirm this is business income; check if Acme issues a 1099-NEC. |
| 2025-03-05 | COMCAST BUSINESS INTERNET | -89.99 | Utilities / internet | Line 25 — Utilities | **Assumed** | Assumed 100% business use; if home office, apportion by sq ft or time. |
| 2025-03-12 | VERIZON WIRELESS | -65.00 | Phone / telecom | Line 25 — Utilities | **Assumed** | Assumed business phone; if personal line, apportion business %. |
| 2025-03-15 | AMZN MKTP US*AWS | -142.00 | Cloud / software | Line 18 — Office expense or Line 27a — Other | **Classified** | AWS hosting for business — deductible; keep invoice. |
| 2025-03-22 | STARBUCKS STORE 1847 | -7.25 | Meals | 50% deductible (meals) or personal | **Needs Input** | Was this a client meeting? If yes, 50% deductible; if personal, exclude. |

**Inspired by:** OpenAccountants open-source tax skills ([GitHub](https://github.com/openaccountants/openaccountants)).

## Sample CSV for manual testing (Claude Code)

Save as `us-sample.csv`, attach in chat, then ask for the four outputs.

```csv
date,description,amount,currency
2025-03-02,"ZELLE FROM ACME CORP",4500.00,USD
2025-03-05,"COMCAST BUSINESS INTERNET",-89.99,USD
2025-03-12,"VERIZON WIRELESS",-65.00,USD
2025-03-15,"AMZN MKTP US*AWS",-142.00,USD
2025-03-22,"STARBUCKS STORE 1847",-7.25,USD
```

## Tips

- Run **monthly** so missing invoices are easier to find than at year-end.
- Keep **original bank files** immutable; work in a copy or derived spreadsheet.
- Attach **receipts or invoices** for any line where a deduction is claimed.
- For multi-service spend (AWS, Stripe, ads), prefer **Needs Input** until the user provides the platform's invoice or summary.

## Common Use Cases

- Freelancer preparing Schedule C / self-employment figures for a CPA.
- Small-business owner separating deductible vs personal on a shared card.
- VAT/GST return prep (non-US): mapping lines to sales, purchases, exempt, reverse charge.
- First pass after OCR of paper statements or bank CSV export.
