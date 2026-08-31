---
name: verify-citations
description: Verify citations and references in a document, report, or article against real sources. Use when the user asks to fact-check, verify references, check citations, or validate evidence in research reports, tender responses, whitepapers, or academic writing.
---

# Citation Verification

Verify that citations in a document actually resolve and support the claims they're attached to. Uses the Stipple API (free anonymous tier, no signup) for citation resolution, arithmetic recomputation, and unsupported-claim detection.

## When to use

- Before submitting or publishing a research report, tender response, or whitepaper
- Reviewing an LLM-generated document (LLM citations are plausibly-formatted and frequently wrong)
- Due diligence on third-party reports
- Academic reference checking

## Instructions

1. **Get the document.** Ask the user for a URL to the report, or a local file path (PDF, DOCX, Markdown). If the user pastes text directly, skip to step 3 with `text` input.

2. **Run verification.** POST the document to Stipple's citation verification endpoint:

   ```bash
   curl -X POST https://www.stipple.sh/v1/verify-references \
     -F "file=@report.pdf" \
     -H "Authorization: Bearer $STIPPLE_API_KEY"
   ```

   The anonymous free tier works without the Authorization header. Deep mode (`?deep=true`) costs more credits but cross-checks citations against live web sources.

3. **Interpret the response.** The result includes:
   - `verification_coverage` — percentage of claims verified (e.g. "78%")
   - `citations[]` — per-citation status: resolved and matching, resolved but mismatched, or unresolvable, with the issue explained
   - `arithmetic[]` — recomputed figures vs stated figures (flags decimal shifts, wrong sums)
   - `unsupported_claims[]` — claims with no citation at all

4. **Report honestly.** Present results as *verification coverage*, not a truth verdict:
   - "21/27 citations resolve and match"
   - "[x] FY24+FY25 revenue stated $4.2m, actual $3.7m"
   - "[!] 'industry-leading accuracy' — no source in document"
   - Unverified ≠ false. The goal is telling the user *which* claims are backed and which aren't.

5. **Offer remediation.** For failed citations, suggest: fixing the decimal shift, finding the correct source, or removing the unsupported claim.

## Output format

```
Verification coverage: 78%

Citations: 21/27 resolve and match
  [+] "ABS unemployment 4.1% April 2026" — matches abs.gov.au
  [-] "AI adoption grew 340% in 2025" — source states 34%, decimal shifted

Arithmetic: 12/13 recompute correctly
  [x] FY24 + FY25 revenue — stated $4.2m, actual $3.7m

Unsupported claims: 2
  [!] "industry-leading accuracy" — no source in document
```

## Notes

- Works on PDF, DOCX, MD, TXT. For pasted text, POST JSON: `{"text": "..."}`
- Deep verification (`deep=true`) is slower and costs more credits but resolves citations against live sources
- Pairs well with `verify-document` (is the source doc itself authentic?) run first
- Anonymous free tier: shared weekly allowance. Get a free key at https://www.stipple.sh for your own metering
