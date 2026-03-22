---
name: google-maps-automation
description: "Automate Google Maps tasks via Rube MCP (Composio): geocode addresses, search places, get directions, compute route matrices, reverse geocode, autocomplete, get place details. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Google Maps Automation via Rube MCP

Geocode addresses, search places, get directions, compute distance matrices, and retrieve place details using Google Maps via Rube MCP (Composio).

**Toolkit docs**: [composio.dev/toolkits/google_maps](https://composio.dev/toolkits/google_maps)

## Prerequisites
- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `google_maps`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup
**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.

1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `google_maps`
3. If connection is not ACTIVE, follow the returned auth link to complete setup
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Geocode an Address
Use `GOOGLE_MAPS_GEOCODING_API` to convert a street address into geographic coordinates (latitude/longitude).
```
Tool: GOOGLE_MAPS_GEOCODING_API
Parameters:
  - address: Street address or plus code to geocode
  - latlng: Lat/lng for reverse geocoding (e.g., "40.714224,-73.961452")
  - place_id: Place ID for place geocoding
  - language: Language for results
  - region: Region bias (ccTLD code)
  - bounds: Bounding box for viewport bias
  - components: Component filter (e.g., "postal_code:94043|country:US")
```

### 2. Search for Places
Use `GOOGLE_MAPS_TEXT_SEARCH` to find places using a free-text query.
```
Tool: GOOGLE_MAPS_TEXT_SEARCH
Parameters:
  - textQuery (required): Search text (e.g., "restaurants in London")
  - fieldMask: Fields to return (e.g., "displayName,formattedAddress,rating")
  - maxResultCount: Max results (1-20, default 10)
```

### 3. Get Directions Between Two Locations
Use `GOOGLE_MAPS_GET_ROUTE` to calculate routes with distance and duration.
```
Tool: GOOGLE_MAPS_GET_ROUTE
Parameters:
  - origin_address (required): Starting point (address or "lat,lng")
  - destination_address (required): End point (address or "lat,lng")
  - travelMode: DRIVE, BICYCLE, WALK, TWO_WHEELER, or TRANSIT
  - routingPreference: TRAFFIC_UNAWARE, TRAFFIC_AWARE, TRAFFIC_AWARE_OPTIMAL
  - computeAlternativeRoutes: Return alternative routes (boolean)
  - units: METRIC or IMPERIAL
  - languageCode: BCP-47 language code
  - routeModifiers_avoidTolls / avoidHighways / avoidFerries: Route preferences
```

### 4. Compute Distance Matrix
Use `GOOGLE_MAPS_COMPUTE_ROUTE_MATRIX` to calculate distances and durations between multiple origins and destinations.
```
Tool: GOOGLE_MAPS_COMPUTE_ROUTE_MATRIX
Parameters:
  - origins (required): Array of origin locations (address strings or lat/lng objects)
  - destinations (required): Array of destination locations
  - travelMode: DRIVE, BICYCLE, WALK, TWO_WHEELER, or TRANSIT
  - routingPreference: TRAFFIC_UNAWARE, TRAFFIC_AWARE, TRAFFIC_AWARE_OPTIMAL
  - fieldMask: Response fields to include
  - units: METRIC or IMPERIAL
```

### 5. Get Place Details
Use `GOOGLE_MAPS_GET_PLACE_DETAILS` to retrieve comprehensive information about a specific place.
```
Tool: GOOGLE_MAPS_GET_PLACE_DETAILS
Description: Retrieves comprehensive details for a place using its resource
  name (places/{place_id} format). Returns hours, contacts, reviews, etc.
Note: Call RUBE_SEARCH_TOOLS to get the full schema for this tool.
```

### 6. Search Nearby Places
Use `GOOGLE_MAPS_NEARBY_SEARCH` to find places within a circular area around a point.
```
Tool: GOOGLE_MAPS_NEARBY_SEARCH
Parameters:
  - latitude (required): Center latitude (-90 to 90)
  - longitude (required): Center longitude (-180 to 180)
  - radius (required): Search radius in meters (max 50000)
  - includedTypes: Place types to include (e.g., ["restaurant", "cafe"])
  - excludedTypes: Place types to exclude
  - fieldMask: Fields to return
  - maxResultCount: Max results (1-20)
```

## Common Patterns

- **Geocode then route**: Use `GOOGLE_MAPS_GEOCODING_API` to convert addresses to coordinates, then `GOOGLE_MAPS_GET_ROUTE` for directions between them.
- **Search then detail**: Use `GOOGLE_MAPS_TEXT_SEARCH` to find places, then `GOOGLE_MAPS_GET_PLACE_DETAILS` for richer metadata (hours, contacts, reviews).
- **Autocomplete UX**: Use `GOOGLE_MAPS_AUTOCOMPLETE` for type-ahead search suggestions as users type addresses or place names.
- **Reverse geocode**: Use `GOOGLE_MAPS_GEOCODE_LOCATION` to convert coordinates back to a human-readable address.
- **Batch distance calculation**: Use `GOOGLE_MAPS_COMPUTE_ROUTE_MATRIX` for many-to-many distance calculations instead of calling `GOOGLE_MAPS_GET_ROUTE` repeatedly.
- **Embed maps**: Use `GOOGLE_MAPS_MAPS_EMBED_API` to generate embeddable map URLs for places, directions, or search results.

## Known Pitfalls

- **Route matrix results structure**: `GOOGLE_MAPS_COMPUTE_ROUTE_MATRIX` returns results under `data.elements` with `originIndex` and `destinationIndex` plus `distanceMeters` and `duration` -- not a `routes[]` structure.
- **Duration format**: `GOOGLE_MAPS_GET_ROUTE` returns durations as strings like `"937s"` inside `data.response_data.routes`. You must parse these before numeric comparisons.
- **Place IDs for chaining**: Use place identifiers returned from `GOOGLE_MAPS_TEXT_SEARCH` when calling `GOOGLE_MAPS_GET_PLACE_DETAILS` for richer fields.
- **Reverse geocoding input**: `GOOGLE_MAPS_GEOCODE_LOCATION` is coordinate-driven. Ensure you pass lat/lng (not an address string) to avoid mismatched lookups.
- **Routing preference restrictions**: `routingPreference` cannot be set when `travelMode` is WALK, BICYCLE, or TRANSIT -- it must be omitted for these modes.
- **Nearby search type validity**: `"food"` is NOT a valid type for `GOOGLE_MAPS_NEARBY_SEARCH` (it is Table B). Use specific types like `restaurant`, `cafe`, `bakery`, `fast_food_restaurant` instead.
- **Embed API uses API keys only**: `GOOGLE_MAPS_MAPS_EMBED_API` requires an API key and does not support OAuth2.

## Quick Reference
| Action | Tool | Key Parameters |
|--------|------|----------------|
| Geocode address | `GOOGLE_MAPS_GEOCODING_API` | `address` or `latlng` or `place_id` |
| Reverse geocode | `GOOGLE_MAPS_GEOCODE_LOCATION` | (see full schema via RUBE_SEARCH_TOOLS) |
| Text search | `GOOGLE_MAPS_TEXT_SEARCH` | `textQuery`, `fieldMask`, `maxResultCount` |
| Nearby search | `GOOGLE_MAPS_NEARBY_SEARCH` | `latitude`, `longitude`, `radius`, `includedTypes` |
| Get directions | `GOOGLE_MAPS_GET_ROUTE` | `origin_address`, `destination_address`, `travelMode` |
| Distance matrix | `GOOGLE_MAPS_COMPUTE_ROUTE_MATRIX` | `origins`, `destinations`, `travelMode` |
| Place details | `GOOGLE_MAPS_GET_PLACE_DETAILS` | (see full schema via RUBE_SEARCH_TOOLS) |
| Autocomplete | `GOOGLE_MAPS_AUTOCOMPLETE` | `input`, `includedRegionCodes`, `locationBias` |
| Place photo | `GOOGLE_MAPS_PLACE_PHOTO` | (see full schema via RUBE_SEARCH_TOOLS) |
| Embed map | `GOOGLE_MAPS_MAPS_EMBED_API` | `mode`, plus mode-specific params |

---
*Powered by [Composio](https://composio.dev)*
