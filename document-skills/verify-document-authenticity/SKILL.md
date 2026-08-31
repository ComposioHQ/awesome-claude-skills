---
name: verify-document
description: Check whether a document (PDF or image) shows signs of tampering or forgery before you rely on it. Use when the user asks to verify a payslip, invoice, bank statement, ID document, contract, or any document where authenticity matters.
---

# Document Verification

Inspect a document for forensic authenticity signals — not a fraud verdict, but a risk band with the evidence behind it. Uses the Stipple API (free anonymous tier, no signup).

## When to use

- Before onboarding a tenant, contractor, or employee from uploaded documents
- Before paying an invoice that arrived by email
- Before relying on a bank statement, payslip, or certificate in any workflow
- Reviewing documents in due diligence, claims processing, or loan applications

## Instructions

1. **Get the document.** URL or local file path (PDF, PNG, JPEG, BMP, TIFF).

2. **Optionally check the cache first.** If the user has the file's SHA-256, check whether it's already been inspected (free):

   ```bash
   curl "https://www.stipple.sh/v1/warrants/check?sha256=<hash>"
   ```

3. **Run verification.** POST the document:

   ```bash
   curl -X POST https://www.stipple.sh/v1/warrants \
     -F "file=@payslip.pdf" \
     -H "Authorization: Bearer $STIPPLE_API_KEY"
   ```

   Add `?fresh=true` to force re-inspection of a previously cached document. Add `?deep=true` for deep inspection (more thorough, more credits).

4. **Interpret the response.** Two independent axes — read both:

   | Axis | Question it answers |
   |---|---|
   | `risk_band` | Does anything look tampered? (low / medium / high) |
   | `inspection_quality` | Could the engine actually see enough to judge? (thorough / limited / poor) |

   A clean phone photo of a real payslip is commonly `low` risk + `limited` quality — **low coverage is not risk**. Per-signal `evidence` includes: amount/words mismatch, font discontinuity in values, date anomalies, document label integrity, identifier checksums (ABN/ACN/TFN), table arithmetic.

5. **Report honestly.** This is a *signal with evidence*, not a verdict:
   - "risk_band: LOW — nothing looks tampered"
   - "inspection_quality: limited — couldn't inspect everything; low coverage is NOT fraud"
   - Show the per-signal evidence for anything flagged

6. **Pair with related checks.** For identity documents, follow with a 100-point identity check (`/v1/identity-check`). For extraction, use `extract-document-data`.

## Output format

```
risk_band:           LOW — Nothing looks tampered.
inspection_quality:  limited
recommended action:  review_before_action

evidence (signals):
  [pass] Amount words/figure mismatch: Spelled-out amounts agree with figures.
  [pass] Font discontinuity in value: Numeric values share the font of surrounding text.
  [skip] Identifier checksum: No checksummable identifier (ABN/ACN/TFN) present.
```

## Notes

- Document types the engine recognizes (payslips, invoices, bank statements) get type-specific checks; unrecognized types get generic checks only — say so in your report
- Identical files are cached by content hash — re-checking the same bytes returns instantly and free
- This measures *forensic integrity*, not *authorship style* — for "was this written by AI", use AI-text detection instead
- Anonymous free tier: shared weekly allowance. Free key at https://www.stipple.sh
