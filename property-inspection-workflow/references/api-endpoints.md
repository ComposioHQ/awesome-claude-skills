# Property Inspection Workflow - API Endpoints

Base URL (dev): `http://localhost:8000/api/v1`

## Primary Endpoints

### GET `/swaths/check`
Check if a property location falls within any storm swath (pre-inspection context).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | float | yes | Property latitude |
| `lng` | float | yes | Property longitude |
| `months_back` | int | no | Months of storm history to check |

**Response**: Array of `WeatherSwath` objects containing the point, including `damageType`, `severity`, and `metadata`.

### GET `/storms`
Fetch storm events for timeline cross-referencing during inspections.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `from` | ISO date | 90 days ago | Start of date range |
| `to` | ISO date | now | End of date range |

**Response**: Array of `StormEvent` objects with nested swaths.

### GET `/year-built`
Look up property age to assess roof condition expectations.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `address` | string | no | Property address |
| `lat` | float | no | Latitude |
| `lng` | float | no | Longitude |

**Response**: `{ year_built, source, confidence }`

### GET `/geocode`
Resolve property address to coordinates for spatial queries.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | yes | Address to geocode |

**Response**: `{ lat, lng, display_name }`

### GET `/swaths/area`
Query all swaths in an area (useful for multi-property inspection routes).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `north` | float | yes | Northern latitude bound |
| `south` | float | yes | Southern latitude bound |
| `east` | float | yes | Eastern longitude bound |
| `west` | float | yes | Western longitude bound |
| `since` | ISO date | no | Filter swaths after this date |

**Response**: Array of `WeatherSwath` objects in the bounding box.

## StormForge Mobile App Components

Relevant to field inspection data capture (in `apps/stormforge/lib/`):

| Component | Location | Purpose |
|-----------|----------|---------|
| MapScreen | `screens/` | Visual property and swath mapping |
| ListScreen | `screens/` | Storm event listing and filtering |
| SwathStorageService | via `stormforge_core` | Offline Hive cache for swath data |
| WeatherApiService | via `stormforge_core` | API client with offline fallback |
| GeocodingService | `services/` | Address lookup via backend proxy |

### Offline-First Architecture

StormForge uses Hive for local storage:
- Inspection data captured locally first
- Syncs to backend when connectivity is available
- Swath data cached for offline point-in-polygon checks
- Geocode results cached both client-side (Hive) and server-side (SQLite, 30 days)

## Environment Configuration

| Environment | Base URL | Notes |
|-------------|----------|-------|
| dev | `http://localhost:8000/api/v1` | Local development |
| tailscale | `http://100.89.65.121:8000/api/v1` | Private tunnel |
| prod | `https://api.storm.estimap.com/api/v1` | Requires `API_KEY` env var |
