---
name: storm-damage-analyzer
description: Analyze storm damage data and generate severity reports using spatial queries against property locations. Use this skill when you need to analyze storm damage, generate a storm report, perform a hail damage assessment, conduct weather impact analysis, run storm swath analysis, evaluate storm severity, assess property damage from weather events, or create damage summaries for insurance claims.
---

# Storm Damage Analyzer

Analyze storm damage data from weather events and generate structured severity reports by correlating storm swath polygons with property locations using spatial queries.

## When to Use This Skill

- Analyzing storm damage across a geographic area
- Generating storm reports for insurance workflows
- Performing hail damage assessments after severe weather
- Conducting weather impact analysis for a region
- Running storm swath analysis against property databases
- Evaluating damage severity for claims processing
- Summarizing affected property counts and severity distributions

## Prerequisites

- Access to the Forge workspace Rust/Axum backend (default: `localhost:8000`)
- Storm event data loaded in the database (via NOAA/NWS feeds or manual entry)
- Property locations available for spatial cross-referencing

## Workflow

### Step 1: Identify the Storm Event

Query available storm events within the target timeframe:

```bash
# Fetch storms from the last 90 days (default)
curl http://localhost:8000/api/v1/storms

# Fetch storms in a specific date range
curl "http://localhost:8000/api/v1/storms?from=2026-03-01&to=2026-03-31"
```

Each `StormEvent` contains:
- `id`, `name` -- unique identifier and human-readable name
- `startTime`, `endTime` -- event duration
- `swaths` -- list of `WeatherSwath` polygons with damage data
- `isLive` -- whether the event is still active

### Step 2: Retrieve Storm Swaths for the Area

Query swaths within the geographic bounding box of interest:

```bash
# Get swaths in a bounding box
curl "http://localhost:8000/api/v1/swaths/area?north=36.0&south=35.0&east=-96.0&west=-97.5&since=2026-03-01"
```

Each `WeatherSwath` contains:
- `damageType` -- one of: `hail`, `wind`, `tornado`, `mixed`
- `severity` -- one of: `minor`, `moderate`, `severe`, `extreme`
- `polygon` -- list of `LatLng` points defining the affected area
- `metadata` -- additional parameters: `hail_diameter_inches`, `max_wind_mph`

### Step 3: Check Properties Against Swaths

For each property, determine if it falls within any storm swath:

```bash
# Point-in-polygon check for a single address
curl "http://localhost:8000/api/v1/swaths/check?lat=35.4676&lng=-97.5164&months_back=3"
```

The backend uses a ray-casting algorithm (implemented in both Dart and Rust) to determine point-in-polygon containment.

### Step 4: Classify Damage Severity

Apply severity classification based on storm parameters:

| Parameter | Minor | Moderate | Severe | Extreme |
|-----------|-------|----------|--------|---------|
| Hail diameter | < 1" | 1" - 1.75" | 1.75" - 2.5" | > 2.5" |
| Wind speed | < 60 mph | 60 - 80 mph | 80 - 110 mph | > 110 mph |
| Tornado | -- | EF0-EF1 | EF2-EF3 | EF4-EF5 |

When multiple damage types overlap, use the highest severity from any swath affecting the property.

### Step 5: Generate the Damage Report

Produce two outputs:

**JSON Summary:**
```json
{
  "storm_event": "Spring Hailstorm 2026-03-15",
  "analysis_date": "2026-03-16T10:00:00Z",
  "area_analyzed": { "north": 36.0, "south": 35.0, "east": -96.0, "west": -97.5 },
  "total_properties_checked": 1250,
  "affected_properties": 847,
  "severity_distribution": {
    "minor": 312,
    "moderate": 298,
    "severe": 189,
    "extreme": 48
  },
  "damage_types": {
    "hail": 623,
    "wind": 178,
    "mixed": 46
  }
}
```

**Markdown Report:**
- Executive summary with storm name, date, and area
- Severity breakdown with property counts and percentages
- Map of affected area (reference swath polygon coordinates)
- Damage type distribution
- Recommendations for next steps (inspections, estimates)

## Working with Core Models

### WeatherSwath (from stormforge_core)

```dart
enum DamageType { hail, wind, tornado, mixed }
enum Severity { minor, moderate, severe, extreme }

class WeatherSwath {
  String id;
  DamageType damageType;
  Severity severity;
  List<LatLng> polygon;
  DateTime eventTime;
  Map<String, dynamic>? metadata;  // { hail_diameter_inches, max_wind_mph }
  bool containsPoint(LatLng point);  // Ray-casting algorithm
}
```

### StormEvent (from stormforge_core)

```dart
class StormEvent {
  String id, name;
  DateTime startTime;
  DateTime? endTime;
  List<WeatherSwath> swaths;
  bool isLive;
  Severity get worstSeverity;
  Set<DamageType> get damageTypes;
}
```

## Tips

- Use the WebSocket endpoint (`/ws/storms/live`) to monitor live storm events in real time
- Batch property checks by iterating through addresses and calling `/swaths/check` for each
- For large-scale analysis, query `/swaths/area` once and perform point-in-polygon checks locally
- Cross-reference with `/year-built` data to prioritize older roofs that are more vulnerable
- Cache geocode results (the backend caches for 30 days automatically)
- Use the `worstSeverity` computed property on `StormEvent` for quick triage

## Error Handling

- If the backend is unreachable, check that the Rust server is running (`cargo run` in `server/`)
- Rate limit geocode lookups to 1 request/second (enforced server-side)
- Handle empty swath results gracefully -- not all storms produce swath data immediately
