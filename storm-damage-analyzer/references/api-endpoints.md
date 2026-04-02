# Storm Damage Analyzer - API Endpoints

Base URL (dev): `http://localhost:8000/api/v1`

## Primary Endpoints

### GET `/storms`
Fetch storm events with nested swaths.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `from` | ISO date | 90 days ago | Start of date range |
| `to` | ISO date | now | End of date range |

**Response**: Array of `StormEvent` objects, each containing a `swaths` array of `WeatherSwath` objects.

### GET `/swaths/area`
Query swaths within a geographic bounding box.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `north` | float | yes | Northern latitude bound |
| `south` | float | yes | Southern latitude bound |
| `east` | float | yes | Eastern longitude bound |
| `west` | float | yes | Western longitude bound |
| `since` | ISO date | no | Filter swaths after this date |

**Response**: Array of `WeatherSwath` objects intersecting the bounding box.

### GET `/swaths/check`
Point-in-polygon check for a single location.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | float | yes | Latitude of the point |
| `lng` | float | yes | Longitude of the point |
| `months_back` | int | no | How many months of history to search |

**Response**: Array of `WeatherSwath` objects containing the given point.

### GET `/geocode`
Geocode an address to lat/lng coordinates (Nominatim proxy, cached 30 days).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | yes | Address to geocode |

**Response**: `{ lat, lng, display_name }`

### WS `/ws/storms/live`
WebSocket endpoint for real-time storm swath broadcasts.

**Messages**: JSON-encoded `WeatherSwath` objects as new data arrives.

## Supporting Endpoints

### GET `/health`
Server status including uptime and storm event count.

### GET `/year-built`
Property year-built lookup from county assessors and Census ACS data.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `address` | string | no | Property address |
| `lat` | float | no | Latitude |
| `lng` | float | no | Longitude |

## Environment Configuration

| Environment | Base URL | Notes |
|-------------|----------|-------|
| dev | `http://localhost:8000/api/v1` | Local development |
| tailscale | `http://100.89.65.121:8000/api/v1` | Private tunnel |
| prod | `https://api.storm.estimap.com/api/v1` | Requires `API_KEY` env var |
