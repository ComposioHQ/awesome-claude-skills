---
name: roof-estimate-generator
description: Generate detailed roofing estimates and proposals with materials, labor, insurance line items, and PDF export. Use this skill when you need to generate an estimate, create a roof estimate, write a roofing proposal, calculate roof cost, produce a pricing estimate, build an insurance claim estimate, create Xactimate-style line items, or batch-generate estimates for multiple properties.
---

# Roof Estimate Generator

Generate comprehensive roofing estimates with line-item breakdowns for materials, labor, permits, overhead, and profit. Supports insurance supplement workflows and batch processing.

## When to Use This Skill

- Generating a roofing estimate for a single property
- Creating a formal roofing proposal for a client
- Calculating roof replacement or repair costs
- Producing insurance claim estimates with Xactimate-style line items
- Batch-generating estimates for multiple properties after a storm
- Creating supplement documentation for insurance adjusters
- Looking up material pricing and labor rates

## Prerequisites

- Access to RoofForge desktop application or its pricing database
- Roof measurements (manual, satellite, or from inspection data)
- Regional labor rates configured in the pricing management system

## Workflow

### Step 1: Gather Roof Measurements

Collect or calculate the following measurements:

| Measurement | Description | Source |
|-------------|-------------|--------|
| Total roof area | Square footage of the roof surface | Satellite imagery, manual measurement, or inspection report |
| Pitch/slope | Rise over run (e.g., 6/12) | Field measurement or satellite estimation |
| Number of facets | Distinct roof planes | Aerial view or inspection |
| Ridge length | Linear feet of ridgeline | Measurement or calculation |
| Valley length | Linear feet of valleys | Measurement or calculation |
| Eave/drip edge | Linear feet of eaves | Perimeter measurement |
| Penetrations | Count of vents, pipes, skylights | Inspection data |

### Step 2: Apply Pitch Multiplier and Waste Factor

Convert flat-area measurements to actual roof area:

| Pitch | Multiplier | Typical Waste Factor |
|-------|-----------|---------------------|
| 4/12 | 1.054 | 10% |
| 5/12 | 1.083 | 10% |
| 6/12 | 1.118 | 12% |
| 7/12 | 1.158 | 12% |
| 8/12 | 1.202 | 15% |
| 9/12 | 1.250 | 15% |
| 10/12 | 1.302 | 15% |
| 12/12 | 1.414 | 18% |

```
actual_area = measured_area * pitch_multiplier
material_area = actual_area * (1 + waste_factor)
squares = material_area / 100
```

### Step 3: Look Up Material Pricing

Reference the RoofForge pricing management system (in `apps/roofforge/lib/screens/`). Standard material categories:

**Shingles (per square):**
- 3-tab architectural: $90 - $120
- Dimensional/laminate: $120 - $180
- Premium/designer: $180 - $350
- Impact-resistant (Class 4): $150 - $250

**Underlayment and accessories (per square or linear foot):**
- Synthetic underlayment
- Ice and water shield
- Starter strip
- Hip and ridge caps
- Drip edge
- Flashing (step, counter, valley)
- Pipe boots and vent covers
- Nails/fasteners

### Step 4: Calculate Labor Costs

Labor rates vary by region. Base calculation:

```
labor_cost = squares * labor_rate_per_square
```

Adjust for complexity factors:
- Steep pitch (> 8/12): +20-40%
- Multiple stories: +10-25% per additional story
- Tear-off required: +$50-100 per square
- Complex geometry (many facets/valleys): +15-30%
- Access difficulty: +10-20%

### Step 5: Build the Line-Item Estimate

Structure the estimate with these categories:

```
1. MATERIALS
   - Shingles (quantity x unit price)
   - Underlayment
   - Ice & water shield
   - Starter strip
   - Hip & ridge caps
   - Drip edge
   - Flashing
   - Pipe boots / vent covers
   - Nails and fasteners

2. LABOR
   - Tear-off and disposal
   - Installation
   - Steep pitch premium
   - Story premium

3. ADDITIONAL
   - Permits
   - Dumpster rental
   - Wood replacement (if needed, per sheet)

4. OVERHEAD & PROFIT
   - Overhead (typically 10%)
   - Profit (typically 10%)

TOTAL ESTIMATE: $XX,XXX.XX
```

### Step 6: Insurance Supplement Workflow (Xactimate-Style)

For insurance claims, format line items using industry-standard codes:

| Code | Description | Unit | Quantity |
|------|-------------|------|----------|
| RFG-250 | Remove roofing - comp shingles | SQ | XX |
| RFG-260 | Roofing felt - 15# | SQ | XX |
| RFG-310 | Shingles - laminated/architectural | SQ | XX |
| RFG-120 | Drip edge - aluminum | LF | XX |
| RFG-140 | Ice & water shield | SQ | XX |
| RFG-400 | Ridge cap - shingles | LF | XX |
| FLT-100 | Step flashing | EA | XX |

Include:
- Overhead and profit (O&P) at standard rates
- Tax on materials
- Code upgrade items if applicable
- Supplemental items missed in initial adjuster scope

### Step 7: Export as PDF

Use RoofForge's PDF generation system to produce professional estimates:

- Company branding (logo, colors, contact info)
- Property details (address, owner, insurance info)
- Detailed line items with quantities and pricing
- Material specifications
- Warranty information
- Terms and conditions
- Signature lines

### Batch Estimates

For storm-affected areas with multiple properties:

1. Pull affected properties from storm damage analysis
2. Use satellite measurements for roof dimensions where available
3. Apply consistent pricing from the regional pricing database
4. Generate individual PDFs for each property
5. Create a batch summary report with totals

## Integration with RoofForge

RoofForge screens relevant to estimates:
- **Estimate Screen** -- main estimate creation and editing interface
- **Pricing Screen** -- material and labor rate management
- **Settings Screen** -- company branding, default values, regional config

The desktop app uses Riverpod for state management and Hive for local storage of estimate data.

## Tips

- Always verify measurements before generating final estimates
- Update pricing database regularly to reflect current material costs
- Include photos from inspections to support line items
- For insurance work, match the adjuster's scope before adding supplements
- Save estimate templates for common roof types to speed up batch processing
- Use the `/year-built` endpoint to determine if code upgrades are required

## Error Handling

- Validate all measurements are positive numbers before calculating
- Warn if pitch multiplier seems outside normal range (< 1.0 or > 1.5)
- Flag estimates that fall outside typical price-per-square ranges for the region
- Check that material quantities align with roof area calculations
