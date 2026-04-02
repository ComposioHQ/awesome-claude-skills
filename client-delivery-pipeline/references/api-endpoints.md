# Client Delivery Pipeline - API Endpoints

Base URL (dev): `http://localhost:8000/api/v1`

## Primary Endpoints

### GET `/storms`
Fetch storm event data for inclusion in client reports.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `from` | ISO date | 90 days ago | Start of date range |
| `to` | ISO date | now | End of date range |

**Response**: Array of `StormEvent` objects with nested swaths.

### GET `/swaths/check`
Verify storm impact on a property (for report generation).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | float | yes | Property latitude |
| `lng` | float | yes | Property longitude |
| `months_back` | int | no | Months of history |

**Response**: Array of `WeatherSwath` objects affecting the location.

### GET `/geocode`
Resolve addresses for report headers and maps.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | yes | Address to geocode |

**Response**: `{ lat, lng, display_name }`

### GET `/health`
Verify backend availability before generating reports that depend on live data.

**Response**: `{ status, uptime, storm_count }`

## RoofForge PDF Export System

The client delivery pipeline depends on RoofForge's desktop PDF generation:

| Component | Location | Purpose |
|-----------|----------|---------|
| Estimate Screen | `apps/roofforge/lib/screens/` | Estimate PDF generation |
| Settings Screen | `apps/roofforge/lib/screens/` | Company branding configuration |
| PDF Templates | `apps/roofforge/` | Branded report layouts |

### PDF Generation Capabilities

- Company-branded cover pages (logo, colors, contact info)
- Multi-page reports with table of contents
- Embedded photos with captions and GPS metadata
- Line-item estimate tables with subtotals
- Print-ready (300 DPI) and screen-optimized (150 DPI) output
- Automatic page numbering and headers/footers

## Upstream Skill Outputs Consumed

| Skill | Output | Used For |
|-------|--------|----------|
| storm-damage-analyzer | JSON summary + markdown report | Storm context section |
| storm-damage-analyzer | Severity distribution | Executive summary stats |
| roof-estimate-generator | Line-item estimate | Estimate section of package |
| roof-estimate-generator | Insurance supplement | Adjuster documentation |
| property-inspection-workflow | Inspection report | Findings section |
| property-inspection-workflow | GPS-tagged photos | Photo appendix |

## Environment Configuration

| Environment | Base URL | Notes |
|-------------|----------|-------|
| dev | `http://localhost:8000/api/v1` | Local development |
| tailscale | `http://100.89.65.121:8000/api/v1` | Private tunnel |
| prod | `https://api.storm.estimap.com/api/v1` | Requires `API_KEY` env var |
