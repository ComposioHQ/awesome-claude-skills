---
name: lendtrain-mortgage
description: AI-native mortgage refinance quoting with real-time institutional pricing, state-specific closing costs, and regulatory compliance.
---

# LendTrain Mortgage Refinance

An AI-native mortgage refinance plugin for Claude Code that delivers real-time institutional pricing, state-specific closing costs, FHA Streamline/VA IRRRL detection, weighted recommendation scoring, and full regulatory compliance. No API key required.

## When to Use This Skill

- When a borrower or loan officer needs a mortgage refinance rate quote
- When comparing refinance options across different loan programs (Conventional, FHA, VA, USDA)
- When evaluating whether a borrower qualifies for FHA Streamline or VA IRRRL
- When generating compliant rate disclosures for mortgage transactions

## What This Skill Does

1. **Real-Time Rate Pricing**: Connects to institutional pricing engine for live rate/fee combinations
2. **State-Specific Closing Costs**: Calculates transfer taxes, recording fees, and title costs by state
3. **Loan Program Detection**: Automatically identifies FHA Streamline, VA IRRRL, and other special programs
4. **Weighted Recommendation Scoring**: Ranks options by break-even period, monthly savings, and total cost
5. **Regulatory Compliance**: Generates NMLS-compliant disclosures with proper licensing information

## How to Use

### Installation

```bash
claude plugin add lendtrain/mortgage
```

### Basic Usage

```
/refi-quote
```

Then provide your loan details when prompted (property state, current balance, estimated home value, current rate, loan type).

## Example

**User**: "/refi-quote"

**Output**: Interactive refinance quote workflow that collects loan parameters, queries live rates, and presents ranked options with monthly savings, break-even analysis, and regulatory disclosures.

## Tips

- Works best when you know your current loan balance, estimated home value, and current interest rate
- The plugin automatically detects FHA Streamline and VA IRRRL eligibility
- All quotes include NMLS disclosures and state licensing information

## Common Use Cases

- Homeowners exploring refinance options
- Loan officers generating quick rate comparisons
- Financial advisors evaluating refinance scenarios for clients
