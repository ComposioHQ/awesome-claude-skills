# Roof Estimate Generator - API Endpoints

Base URL (dev): `http://localhost:8000/api/v1`

## Primary Endpoints

### GET `/year-built`
Look up property year-built to determine code upgrade requirements and roof age.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `address` | string | no | Property address |
| `lat` | float | no | Latitude |
| `lng` | float | no | Longitude |

**Response**: `{ year_built, source, confidence }`

### GET `/geocode`
Geocode a property address to coordinates for spatial lookups.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | yes | Address to geocode |

**Response**: `{ lat, lng, display_name }`

### GET `/swaths/check`
Verify storm damage at a property location (supports insurance claim justification).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | float | yes | Latitude |
| `lng` | float | yes | Longitude |
| `months_back` | int | no | Months of storm history to check |

**Response**: Array of `WeatherSwath` objects affecting the property.

## RoofForge Desktop Application Components

These are not REST endpoints but relevant application screens in `apps/roofforge/lib/screens/`:

| Screen | Purpose |
|--------|---------|
| Estimate | Main estimate creation, editing, line-item management |
| Pricing | Material and labor rate database management |
| Settings | Company branding, regional defaults, export configuration |
| RoofViewer | Visual roof measurement and facet editing |
| StormForge | Integrated storm data viewer within the desktop app |

## PDF Export System

RoofForge generates PDFs through its desktop application:
- Branded estimate documents with company logo
- Line-item detail pages
- Material specification sheets
- Warranty documentation
- Terms and conditions pages

## Environment Configuration

| Environment | Base URL | Notes |
|-------------|----------|-------|
| dev | `http://localhost:8000/api/v1` | Local development |
| tailscale | `http://100.89.65.121:8000/api/v1` | Private tunnel |
| prod | `https://api.storm.estimap.com/api/v1` | Requires `API_KEY` env var |
