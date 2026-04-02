---
name: property-inspection-workflow
description: Manage property inspection workflows with checklists, GPS-tagged photo documentation, and structured reports. Use this skill when you need to conduct a property inspection, perform a roof inspection, run a site survey, create an inspection checklist, execute a field inspection, document damage inspection findings, prepare adjuster documentation, or validate damage timelines against storm data.
---

# Property Inspection Workflow

Manage end-to-end property inspection workflows from checklist generation through report delivery. Includes GPS-tagged photo documentation, storm data cross-referencing, and insurance adjuster support.

## When to Use This Skill

- Conducting a roof or property inspection after a storm
- Performing a pre-sale or annual roof assessment
- Running a site survey for estimate preparation
- Creating standardized inspection checklists
- Documenting damage for insurance claims
- Validating reported damage against storm event timelines
- Preparing inspection packages for insurance adjusters

## Prerequisites

- Access to StormForge mobile app (for field data capture)
- GPS-enabled device with camera
- Access to the Forge workspace backend for storm data cross-referencing

## Workflow

### Step 1: Pre-Inspection Preparation

Before arriving on site, gather context:

1. **Property details**: Pull address, year built, and previous inspection history
   ```bash
   curl "http://localhost:8000/api/v1/year-built?address=123+Main+St&lat=35.467&lng=-97.516"
   ```

2. **Storm history**: Check which storm swaths affect the property
   ```bash
   curl "http://localhost:8000/api/v1/swaths/check?lat=35.467&lng=-97.516&months_back=6"
   ```

3. **Generate checklist**: Create an inspection checklist tailored to the damage types identified in storm data (hail, wind, tornado, mixed)

### Step 2: Inspection Checklist

Use the following standardized checklist, marking each item as Pass / Fail / N/A with notes:

#### Roof Components
- [ ] Shingles -- granule loss, cracking, curling, missing, creasing
- [ ] Hail impacts -- measure diameter, count per test square (10'x10')
- [ ] Wind damage -- lifted tabs, missing shingles, exposed underlayment
- [ ] Ridge caps -- cracking, displacement, missing pieces
- [ ] Valleys -- torn or displaced flashing, debris accumulation
- [ ] Flashing -- step, counter, chimney, wall -- lifting, rust, gaps
- [ ] Pipe boots and vents -- cracked, split, displaced
- [ ] Skylights -- cracked glass, damaged flashing, seal failure
- [ ] Fascia and soffit -- damage, rot, detachment

#### Gutter System
- [ ] Gutters -- dents, separation, misalignment, granule accumulation
- [ ] Downspouts -- damage, proper drainage, extensions
- [ ] Gutter guards -- displacement, damage

#### Building Exterior
- [ ] Siding -- cracks, dents, holes, displacement
- [ ] Windows -- cracked glass, damaged frames, screen damage
- [ ] Trim and paint -- peeling, chipping, impact marks
- [ ] Foundation visible damage

#### Other Structures
- [ ] Garage / outbuildings
- [ ] Fences
- [ ] A/C units and equipment
- [ ] Decks and patios

### Step 3: Photo Documentation Requirements

Every inspection photo must include:

| Requirement | Details |
|-------------|---------|
| GPS coordinates | Automatically tagged by device |
| Timestamp | Date and time embedded in EXIF |
| Compass direction | Cardinal direction the camera faces |
| Description | Brief note on what the photo shows |
| Reference marker | Chalk circle, coin, or ruler for scale (damage photos) |

**Required photo set:**

1. **Overview shots** (4 minimum)
   - Front, back, left side, right side of property
   - Full roof from ground level (each elevation)

2. **Roof surface** (minimum per facet)
   - Wide shot of each roof facet
   - Close-ups of damage (with scale reference)
   - Test squares showing hail impact density

3. **Detail shots**
   - Each type of damage found
   - Flashing conditions at all penetrations
   - Gutter/downspout conditions
   - Any pre-existing vs storm-caused damage

4. **Collateral damage**
   - Soft metals (A/C fins, mailbox, gutters) showing hail impacts
   - Window screens with impact marks
   - Fence and outbuilding damage

### Step 4: Cross-Reference with Storm Data

Validate the damage timeline by comparing inspection findings with storm records:

1. Pull storm events for the property location and date range
2. Compare observed damage type (hail vs wind) with storm swath `damageType`
3. Verify damage severity aligns with storm parameters:
   - Hail size from `metadata.hail_diameter_inches`
   - Wind speed from `metadata.max_wind_mph`
4. Flag any discrepancies:
   - Damage observed but no storm record for the area
   - Storm record exists but damage pattern inconsistent
   - Damage appears older than reported storm date (pre-existing)
   - Severity mismatch (e.g., minor storm but severe damage claimed)

### Step 5: Generate Inspection Report

Produce a structured report containing:

```
PROPERTY INSPECTION REPORT
==========================
Property: [Address]
Date: [Inspection date]
Inspector: [Name, certification]
Weather at inspection: [Conditions]

STORM CONTEXT
- Storm event: [Name, date]
- Damage types: [hail/wind/tornado]
- Severity: [minor/moderate/severe/extreme]

FINDINGS
- [Checklist results organized by component]
- [Each finding with severity rating]
- [Photo references for each finding]

DISCREPANCIES
- [Any timeline or severity mismatches]

RECOMMENDATIONS
- [Repair vs replace recommendations]
- [Priority items (leaks, structural)]
- [Estimated scope of work]

PHOTO LOG
- [Numbered list with GPS, timestamp, description]
```

### Step 6: Flag Discrepancies

Automatically flag and highlight:

- Damage that does not match any recorded storm event
- Pre-existing conditions (wear, age-related deterioration)
- Inconsistencies between homeowner's claim and observed damage
- Areas where storm damage and pre-existing damage overlap
- Missing documentation (photos without GPS, undocumented areas)

## Offline-First Data Capture

Following StormForge's offline-first architecture:

- All inspection data is captured locally using Hive storage
- Photos are stored on-device with metadata
- Data syncs to the backend when connectivity is available
- Inspection can proceed fully offline
- Conflict resolution follows last-write-wins for simple fields

## Integration with Other Skills

- **Storm Damage Analyzer**: Pull storm context before inspection
- **Roof Estimate Generator**: Feed inspection findings into estimate generation
- **Client Delivery Pipeline**: Package inspection report for client delivery

## Tips

- Complete the full checklist even if damage is obvious -- thoroughness protects against disputes
- Always photograph collateral damage (soft metals, fences) as corroborating evidence
- Use consistent naming for photos: `[address]_[component]_[number].jpg`
- Record ambient temperature and weather during inspection (affects material behavior)
- Note the age and type of existing roofing materials for estimate accuracy
- Mark test square locations on a roof diagram for reproducibility

## Error Handling

- If GPS is unavailable, manually record coordinates from a map
- If storm data API is unreachable, document the gap and cross-reference later
- If property access is limited, document which areas could not be inspected
- Flag incomplete inspections clearly in the report
