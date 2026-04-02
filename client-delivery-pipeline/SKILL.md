---
name: client-delivery-pipeline
description: Package and deliver professional reports, estimates, and inspection documents to clients through multiple channels. Use this skill when you need to deliver to a client, send a report, create a client package, run the delivery pipeline, export and send documents, prepare a client presentation, generate a professional deliverable, or compile an insurance claim package.
---

# Client Delivery Pipeline

Aggregate outputs from storm analysis, estimates, and inspections into professional, client-ready deliverables. Supports PDF generation, multiple delivery channels, and delivery tracking.

## When to Use This Skill

- Packaging storm analysis, estimates, and inspections for client delivery
- Generating professional PDF reports with company branding
- Creating client-facing summaries in non-technical language
- Compiling insurance claim documentation packages
- Sending deliverables via email, portal, or print
- Tracking delivery status and client acknowledgment

## Prerequisites

- Completed upstream outputs (storm analysis, estimate, inspection report)
- Access to RoofForge's PDF export system
- Company branding assets (logo, colors, fonts)
- Client contact information and preferred delivery method

## Workflow

### Step 1: Aggregate Upstream Outputs

Collect all documents from prior workflow stages:

| Source Skill | Document | Format |
|-------------|----------|--------|
| Storm Damage Analyzer | Storm analysis report | JSON + Markdown |
| Storm Damage Analyzer | Severity summary | JSON |
| Roof Estimate Generator | Line-item estimate | Structured data |
| Roof Estimate Generator | Insurance supplement | Xactimate-style items |
| Property Inspection Workflow | Inspection report | Markdown + photos |
| Property Inspection Workflow | Photo log with GPS data | JPEG + metadata |

Verify completeness:
- All required documents are present
- Photos are GPS-tagged and properly labeled
- Estimate totals are calculated and verified
- Storm data cross-references are included

### Step 2: Generate Client-Facing Summary

Transform technical findings into language the client understands:

**Technical (internal):**
> "Property located within severe hail swath (2.25" diameter) from StormEvent 2026-03-15. Inspection confirmed Class IV granule displacement across 73% of roof facets. 28 squares replacement scope with architectural shingles."

**Client-facing:**
> "Your home was in the path of the March 15th hailstorm. Our inspection found significant hail damage across most of your roof. Based on our assessment, your roof needs a full replacement. We have prepared a detailed estimate and all the documentation your insurance company will need."

Guidelines for client-facing language:
- Avoid industry jargon (squares, facets, swaths)
- Explain what the damage means for the homeowner
- Clearly state recommended next steps
- Include timeline expectations
- Be factual and avoid alarmist language

### Step 3: Generate Professional PDF Reports

Use RoofForge's PDF generation system to create branded documents:

**Cover Page:**
- Company logo and contact information
- Property address and client name
- Date of report
- Report type (Inspection Report, Estimate, Claim Package)

**Table of Contents:**
- Linked sections for easy navigation

**Executive Summary:**
- 1-2 paragraph overview in client-facing language
- Key findings and recommendations
- Estimated cost range

**Storm Analysis Section:**
- Storm event summary (date, type, severity)
- Map showing storm path relative to property
- NOAA/NWS data references

**Inspection Findings:**
- Organized by building component
- Photos embedded with captions
- Severity ratings for each finding
- Comparison of storm-caused vs pre-existing damage

**Estimate:**
- Line-item breakdown
- Material specifications
- Warranty information
- Payment terms

**Appendix:**
- Full photo log with GPS coordinates
- Raw storm data
- Inspector certifications
- Terms and conditions

### Step 4: Prepare Cover Letter

Include a personalized cover letter template:

```
[Company Letterhead]

[Date]

Dear [Client Name],

Thank you for choosing [Company Name] to inspect your property at
[Address] following the recent storm damage.

Enclosed you will find:
  1. Inspection Report -- detailed findings from our [Date] inspection
  2. Estimate -- itemized cost for recommended repairs/replacement
  3. Storm Documentation -- weather data supporting your claim

[If insurance claim]:
We have formatted all documentation to support your insurance claim.
Your next step is to contact your insurance company at [Phone] and
provide them with your claim number. We are happy to meet with your
adjuster on-site.

[If direct/retail]:
We have included a detailed estimate for your review. We offer
[financing options / payment plans] and can schedule work within
[timeline].

Please don't hesitate to contact us with any questions.

Sincerely,
[Name]
[Title]
[Phone / Email]
```

### Step 5: Package All Documents

Assemble the final deliverable:

```
client-package/
  [ClientName]_[Address]_[Date]/
    00_Cover_Letter.pdf
    01_Executive_Summary.pdf
    02_Inspection_Report.pdf
    03_Estimate.pdf
    04_Storm_Analysis.pdf
    05_Photos/
        overview/
        roof_damage/
        collateral_damage/
        detail_shots/
    06_Insurance_Supplement.pdf  (if applicable)
    07_Warranty_Information.pdf
```

### Step 6: Deliver Through Chosen Channel

Support multiple delivery methods:

| Channel | Method | Notes |
|---------|--------|-------|
| Email | Attach PDF package or send download link | Keep under 25MB; use link for large packages |
| Client portal | Upload to branded web portal | Provides tracking and e-signature |
| Print | Generate print-ready PDFs | Include in folder with business card |
| In-person | Present on tablet during meeting | Use RoofForge presentation mode |

### Step 7: Track Delivery and Acknowledgment

Record delivery status:

```json
{
  "client": "John Smith",
  "property": "123 Main St, Oklahoma City, OK",
  "package_contents": ["cover_letter", "inspection", "estimate", "storm_analysis", "photos"],
  "delivery_method": "email",
  "delivered_at": "2026-03-20T14:30:00Z",
  "acknowledged": false,
  "follow_up_date": "2026-03-23T10:00:00Z",
  "notes": "Client requested copy for insurance adjuster"
}
```

Follow-up schedule:
- Day 1: Delivery confirmation
- Day 3: Follow-up if no acknowledgment
- Day 7: Second follow-up with phone call
- Day 14: Final follow-up before closing

## Integration with RoofForge PDF System

RoofForge's PDF export capabilities:
- Located in `apps/roofforge/` desktop application
- Uses Flutter's PDF generation libraries
- Supports company branding customization (logo, colors, fonts)
- Generates print-ready and screen-optimized versions
- Handles photo embedding with automatic resizing

## Integration with Upstream Skills

This skill consumes outputs from:
- **Storm Damage Analyzer** -- storm context, severity data, affected area maps
- **Roof Estimate Generator** -- line-item estimates, insurance supplements
- **Property Inspection Workflow** -- inspection reports, photo documentation

## Tips

- Always review auto-generated client-facing language before sending
- Include a call-to-action in every deliverable (schedule follow-up, approve estimate)
- Keep PDF file sizes manageable by optimizing photo resolution (150 DPI for screen, 300 DPI for print)
- Save delivery templates to speed up future packages
- Maintain a delivery log for compliance and follow-up tracking
- For insurance packages, include a document checklist so adjusters can verify completeness

## Error Handling

- Verify all upstream documents exist before packaging
- Validate PDF generation succeeded (check file size > 0, page count correct)
- Confirm email delivery (check for bounce-backs)
- If portal upload fails, fall back to email delivery
- Log all delivery attempts for audit trail
