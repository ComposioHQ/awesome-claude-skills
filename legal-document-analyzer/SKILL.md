---
name: legal-document-analyzer
description: Analyzes legal documents, contracts, and NDAs to identify risks, key clauses, obligations, and hidden requirements without requiring legal expertise.
---

# Legal Document Analyzer

This skill empowers non-lawyers to understand legal documents by identifying risks, extracting key terms, highlighting obligations, and flagging potential issues before signing.

## When to Use This Skill

- Reviewing contracts before signing (employment, vendor, client agreements)
- Analyzing Non-Disclosure Agreements (NDAs) and confidentiality terms
- Understanding Terms of Service or Privacy Policies
- Comparing multiple contract versions to spot changes
- Identifying payment terms, liability clauses, and termination conditions
- Reviewing partnership or investment agreements
- Checking for one-sided clauses in commercial contracts
- Preparing talking points for contract negotiations
- Understanding your legal obligations in customer agreements
- Due diligence before business transactions

## What This Skill Does

1. **Risk Identification**: Flags unusual, one-sided, or restrictive clauses
2. **Key Terms Extraction**: Pulls important dates, amounts, parties, and conditions
3. **Obligation Mapping**: Lists what you must do vs. what the other party must do
4. **Jargon Translation**: Explains legal terms in plain English
5. **Red Flag Detection**: Highlights concerning language patterns
6. **Comparison Analysis**: Shows changes between document versions
7. **Negotiation Guidance**: Suggests which clauses to negotiate
8. **Compliance Checking**: Notes potential compliance risks

## How to Use

### Basic Document Review

```
Upload or paste a contract and ask:
"Analyze this contract for risks and obligations."
```

### Specific Focus Areas

```
"Review this NDA and highlight any overly broad confidentiality requirements."
```

### Comparison Analysis

```
"Compare these two versions of the agreement and highlight what changed."
```

### Negotiation Prep

```
"Identify the 5 most important clauses to negotiate in this employment contract."
```

## Instructions

When a user requests document analysis:

1. **Understand the Context**
   
   Ask clarifying questions:
   - What type of agreement is this? (employment, vendor, client, NDA, etc.)
   - Who are the parties involved?
   - What's your main concern? (payment terms, liability, confidentiality, etc.)
   - Is this a first-time relationship or renewal?
   - What's your leverage position? (critical vendor? employer?)

2. **Perform Initial Scan**
   
   Create a standardized analysis:
   
   ```markdown
   # Document Analysis: [Agreement Type]
   
   ## Document Overview
   - **Type**: [agreement type]
   - **Parties**: [your company] ↔ [other party]
   - **Key Dates**: 
     - Effective Date: [date]
     - Term: [duration]
     - Renewal/Termination: [details]
   - **Document Age**: [when was it last updated]
   
   ## Quick Risk Assessment
   - **Overall Risk Level**: Low / Medium / High / Critical
   - **Primary Concerns**: [3-5 main issues]
   ```

3. **Extract Key Terms**
   
   Create a structured summary:
   
   ```markdown
   ## Key Terms at a Glance
   
   ### Parties & Scope
   | Element | Details |
   |---------|---------|
   | Provider/Vendor | [name] |
   | Client/Buyer | [name] |
   | Scope of Services | [brief description] |
   | Territory | [geographic scope] |
   
   ### Financial Terms
   | Term | Amount/Details |
   |------|--------|
   | Total Contract Value | $[amount] |
   | Payment Schedule | [terms] |
   | Minimum Purchase | $[amount] |
   | Late Payment Penalty | [% or amount] |
   | Currency | [USD/other] |
   
   ### Timeline
   | Milestone | Date/Duration |
   |-----------|------------|
   | Start Date | [date] |
   | Contract Term | [length] |
   | Renewal Terms | [auto-renew? how?] |
   | Termination Notice | [days required] |
   ```

4. **Identify Risks & Red Flags**
   
   Categorize and explain each risk:
   
   ```markdown
   ## Risk Assessment
   
   ### 🚨 CRITICAL RISKS
   
   **1. Unlimited Indemnification Clause (Section 8.2)**
   - What it says: You agree to defend and pay for any claims against the other party
   - Why it's risky: This could expose you to unlimited liability
   - Suggested fix: Add cap like "up to the amount paid under this agreement"
   - How common: Unusual in vendor agreements, common in service contracts
   
   **2. Non-Compete Clause (Section 5.1)**
   - Duration: 3 years post-termination
   - Scope: Any work in [industry] globally
   - Why concerning: Extremely broad, could limit your career options
   - Negotiation point: Reduce to 1 year, limit to specific product categories
   
   ### ⚠️ MEDIUM RISKS
   
   **3. Auto-Renewal with 90-Day Notice**
   - Automatic renewal unless you provide 90-day notice
   - Why risky: Easy to miss the notice deadline
   - Suggestion: Request 180-day notice or calendar alert required
   
   **4. Unilateral Price Increase Rights (Section 3.4)**
   - Other party can increase prices up to 10% annually
   - Your recourse: Only termination for convenience
   - Consider: Cap price increases at inflation rate or add mutual negotiation clause
   
   ### ℹ️ INFORMATIONAL ITEMS
   
   **5. Indemnification Cap Timing (Section 8.3)**
   - Notice period before indemnification kicks in: 30 days
   - This is standard and reasonable
   
   ```

5. **Translate Jargon**
   
   Explain complex legal terms plainly:
   
   ```markdown
   ## Legal Terms Explained
   
   | Term | Plain English | In This Contract |
   |------|---|---|
   | **Indemnification** | You agree to pay for legal costs and damages if the other party gets sued | Section 8: You pay for any lawsuits against us |
   | **Force Majeure** | Unforeseeable events that neither party could prevent | Section 12: Covers acts of God, pandemics, wars |
   | **Severability** | If one part is invalid, the rest still counts | Section 15: If any clause is illegal, the agreement continues |
   | **Counterparty** | The other business/person you're contracting with | [Company Name] |
   | **Perpetual** | Lasts forever, even after contract ends | Section 6.3: Confidentiality obligations continue forever |
   ```

6. **Map Obligations** (Your vs. Theirs)
   
   Create clear comparison:
   
   ```markdown
   ## What Each Party Must Do
   
   ### YOUR OBLIGATIONS
   - [ ] Pay invoices within 30 days
   - [ ] Maintain software systems 
   - [ ] Provide quarterly reports by the 15th
   - [ ] Keep data confidential for 5 years after contract ends
   - [ ] Notify them of breaches within 24 hours
   - [ ] Maintain minimum insurance coverage ($2M)
   
   ### THEIR OBLIGATIONS
   - [ ] Deliver services by specific SLAs (99.9% uptime)
   - [ ] Notify you of changes in advance
   - [ ] Keep your data secure
   - [ ] Provide 24/7 support
   - [ ] Not sell your data to third parties
   
   ### MISMATCHES TO ADDRESS
   - ❌ They get 60 days to notify you of changes, but you give them 24 hours for breach notice
   - ❌ You maintain insurance but they don't have equivalent requirement
   - ✅ Mutual confidentiality obligations are balanced
   ```

7. **Provide Negotiation Strategy**
   
   Actionable recommendations:
   
   ```markdown
   ## Negotiation Recommendations
   
   ### MUST CHANGE (Deal Breakers)
   
   1. **Unlimited Liability Cap**
     - Current: "Indemnification without limits"
     - Propose: "Indemnification capped at 12 months of fees paid"
     - Rationale: Standard in most B2B contracts
     - If Rejected: High red flag—walk away or require executive sign-off
   
   2. **Overly Broad Non-Compete**
     - Current: "3-year global restriction on any work in healthcare"
     - Propose: "1-year restriction in [specific service area] in North America"
     - Rationale: You need reasonable career flexibility
   
   ### SHOULD CHANGE (Important)
   
   3. **Auto-Renewal with Short Notice**
     - Current: 90-day notice required
     - Propose: 180-day notice or automatic termination
     - Reason: Easier to remember
   
   4. **Unilateral Price Increase**
     - Current: "Up to 10% annually at their discretion"
     - Propose: "Price increases limited to CPI or mutual agreement"
     - Reason: Budget predictability
   
   ### NICE TO CHANGE (Negotiable)
   
   5. **SLA Response Time**
     - Current: "Best efforts"
     - Propose: "Initial response within 4 business hours"
     - Reason: Clearer expectations
   
   ### TALKING POINTS
   
   ✓ "We'll agree to mutual indemnification with equal caps"
   ✓ "Can we reduce the non-compete to 1 year?"
   ✓ "Industry standard is CPI-based pricing adjustments"
   ✓ "We need 180 days notice to find alternatives"
   ✓ "Can we make the confidentiality mutual?"
   ```

8. **Generate Executive Summary**
   
   One-page decision brief:
   
   ```markdown
   ## Executive Summary
   
   **Bottom Line**: [Recommended action: Sign / Negotiate / Reject]
   
   **Key Numbers**:
   - Total Value: $[amount]
   - Term: [length]
   - Early Exit Cost: $[amount] or [conditions]
   
   **Top 3 Concerns**:
   1. [Concern 1 and impact]
   2. [Concern 2 and impact]
   3. [Concern 3 and impact]
   
   **Top 3 Favorable Terms**:
   1. [Good term 1]
   2. [Good term 2]
   3. [Good term 3]
   
   **Next Steps**:
   - [ ] Negotiate [specific clause]
   - [ ] Require [legal review of specific section]
   - [ ] Get approval from [stakeholder]
   - [ ] Return marked-up version by [date]
   ```

## Examples

### Example 1: Employment Agreement Review

**User**: "Review this job offer letter for any red flags."

**Document Analysis Output**:
```markdown
# Employment Agreement Analysis: Job Offer

## Quick Risk Assessment
- Overall Risk Level: MEDIUM
- Primary Concerns:
  - Non-compete extends 2 years (very long)
  - Clawback clause for signing bonus
  - Vague "forfeiture of accumulated shares" language

## Key Terms
- Base Salary: $150,000
- Sign-on Bonus: $20,000 (clawback if you leave in 1 year)
- Stock Options: 2,000 vesting over 4 years
- Vesting Cliff: 1 year
- Non-Compete: 2 years post-termination
- Geographic Scope: Worldwide

## Red Flags
🚨 **Clawback Provision (Section 2.3)**
- You must repay entire $20,000 if you leave within 12 months
- Why risky: Creates artificial lock-in
- Negotiation: Ask for gradual clawback (50% after 6 months, 0% after 12 months)

⚠️ **Broad Non-Compete (Section 7)**
- 2-year restriction on "any work in technology"
- This is industry-wide; you couldn't join a competitor, startup, or consulting firm
- Consider: Negotiate to 1 year and specific product categories
```

### Example 2: SaaS Service Agreement

**User**: "I need to understand the liability and SLA terms in this vendor contract."

**Extracted Obligations**:
```markdown
## What We're Obligated To Do
- Maintain 99.9% uptime (with exceptions for maintenance)
- Respond to support tickets within 4 hours
- Implement security patches within 30 days
- Keep data encrypted in transit and at rest

## What They're Obligated To Do
- Pay within net 30
- Keep login credentials secure
- Accept monthly billing for overages
- Cannot publicly disclose service usage

## Critical Issue Identified
❌ Liability Mismatch:
- They cap their liability at $50,000
- But you can be sued for unlimited damages for data breaches
- FIX: Ask for equal caps OR require cyber insurance
```

### Example 3: Comparing Two Contract Versions

**User**: "What changed in this new version of the vendor agreement?"

**Comparison Output**:
```markdown
## Version Comparison: Key Changes

### 🚨 UNFAVORABLE CHANGES
1. Payment Terms: 30 days → 15 days (requires faster payment)
2. Price Increase: "CPI adjustment" → "vendor's discretion, up to 20%"
3. Termination: "30-day notice" → "90-day notice required"

### ✅ FAVORABLE CHANGES
1. SLA: "Best efforts" → "99.9% uptime guaranteed"
2. Renewal: "Auto-renews for 2 years" → "Requires mutual agreement"

### ⚠️ NEUTRAL CHANGES
1. Added section on GDPR compliance (required by law anyway)
2. Enhanced data retention policies

## RECOMMENDATION
The unfavorable changes outweigh the benefits. Request:
- Revert payment terms to 30 days
- Cap price increases at CPI +5%
- Keep 30-day termination notice
- Accept the SLA improvement
```

## Workflows

### Contract Approval Workflow
1. Upload new contract
2. Get risk summary and key terms
3. Review specific high-risk sections
4. Develop negotiation strategy
5. Get executive sign-off with confidence

### Comparison Workflow
1. Upload original contract
2. Upload new version
3. Get change highlights marked
4. Understand impact of each change
5. Decide which changes are acceptable

### NDAssement Workflow
1. Paste NDA terms
2. Get plain English explanation
3. Identify any unusually restrictive language
4. Get negotiation suggestions
5. Determine acceptable confidentiality scope

## Pro Tips

1. **Always Get Legal Review**: This skill is for understanding, not replacing lawyers
2. **Focus on Context**: Tell us your business relationship and leverage position
3. **Request Marked-Up Versions**: Ask for changes highlighted, not just summary
4. **Escalate Serious Issues**: Red flag anything about liability, ownership, or disputes
5. **Never Sign Under Pressure**: Take time to analyze before accepting
6. **Use for Preparation**: Come prepared to negotiations with this analysis
7. **Document Your Concerns**: Have specific objections ready

## File Organization

Store contracts systematically:

```
~/Contracts/
├── Employment/
│   ├── offer-letter-v1.pdf
│   ├── offer-letter-v2-marked.pdf
│   └── analysis-employment.md
├── Vendors/
│   ├── SaaS-Provider-Y/
│   │   ├── agreement-2024.pdf
│   │   └── analysis-vendor.md
├── Clients/
│   ├── NDA-Client-X.pdf
│   └── analysis-nda.md
└── Archive/
    └── 2023-contracts/
```

## Best Practices

### Before Analysis
- Provide full document context (is this a renewal? new relationship?)
- Mention your concerns upfront
- Note any special circumstances (startup funding requirement, emergency need?)

### During Analysis
- Ask specific questions about unclear clauses
- Request comparison analysis if you have old versions
- Get negotiation strategy tailored to your situation

### After Analysis
- Use talking points for actual negotiation
- Flag any changes the other party makes
- Follow up with legal counsel on critical items

## Related Use Cases

- Contract negotiation preparation
- Legal review prioritization
- Risk assessment for M&A diligence
- Vendor compliance checking
- Employment offer evaluation
- Partnership agreement understanding

## Limitations

- Not a substitute for legal counsel (always have lawyers review before signing)
- Cannot provide legal advice specific to your jurisdiction
- Should not be used for regulatory compliance interpretation alone
- Cannot predict how courts would interpret specific clauses

---

**Inspired by**: Common business challenges where non-lawyers must understand contracts quickly without legal bill costs

