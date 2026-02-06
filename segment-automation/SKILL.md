---
name: segment-automation
description: "Automate Segment tasks via Rube MCP (Composio): track events, identify users, manage groups, page views, aliases, batch operations. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Segment Automation via Rube MCP

Automate Segment customer data platform operations through Composio's Segment toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Segment connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `segment`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `segment`
3. If connection is not ACTIVE, follow the returned auth link to complete Segment authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Track Events

**When to use**: User wants to send event data to Segment for downstream destinations

**Tool sequence**:
1. `SEGMENT_TRACK` - Send a single track event [Required]

**Key parameters**:
- `userId`: User identifier (required if no `anonymousId`)
- `anonymousId`: Anonymous identifier (required if no `userId`)
- `event`: Event name (e.g., 'Order Completed', 'Button Clicked')
- `properties`: Object with event-specific properties
- `timestamp`: ISO 8601 timestamp (optional; defaults to server time)
- `context`: Object with contextual metadata (IP, user agent, etc.)

**Pitfalls**:
- At least one of `userId` or `anonymousId` is required
- `event` name is required and should follow consistent naming conventions
- Properties are freeform objects; ensure consistent schema across events
- Timestamp must be ISO 8601 format (e.g., '2024-01-15T10:30:00Z')
- Events are processed asynchronously; successful API response means accepted, not delivered

### 2. Identify Users

**When to use**: User wants to associate traits with a user profile in Segment

**Tool sequence**:
1. `SEGMENT_IDENTIFY` - Set user traits and identity [Required]

**Key parameters**:
- `userId`: User identifier (required if no `anonymousId`)
- `anonymousId`: Anonymous identifier
- `traits`: Object with user properties (email, name, plan, etc.)
- `timestamp`: ISO 8601 timestamp
- `context`: Contextual metadata

**Pitfalls**:
- At least one of `userId` or `anonymousId` is required
- Traits are merged with existing traits, not replaced
- To remove a trait, set it to `null`
- Identify calls should be made before track calls for new users
- Avoid sending PII in traits unless destinations are configured for it

### 3. Batch Operations

**When to use**: User wants to send multiple events, identifies, or other calls in a single request

**Tool sequence**:
1. `SEGMENT_BATCH` - Send multiple Segment calls in one request [Required]

**Key parameters**:
- `batch`: Array of message objects, each with:
  - `type`: Message type ('track', 'identify', 'group', 'page', 'alias')
  - `userId` / `anonymousId`: User identifier
  - Additional fields based on type (event, properties, traits, etc.)

**Pitfalls**:
- Each message in the batch must have a valid `type` field
- Maximum batch size limit applies; check schema for current limit
- All messages in a batch are processed independently; one failure does not affect others
- Each message must independently satisfy its type's requirements (e.g., track needs event name)
- Batch is the most efficient way to send multiple calls; prefer over individual calls

### 4. Group Users

**When to use**: User wants to associate a user with a company, team, or organization

**Tool sequence**:
1. `SEGMENT_GROUP` - Associate user with a group [Required]

**Key parameters**:
- `userId`: User identifier (required if no `anonymousId`)
- `anonymousId`: Anonymous identifier
- `groupId`: Group/organization identifier (required)
- `traits`: Object with group properties (name, industry, size, plan)
- `timestamp`: ISO 8601 timestamp

**Pitfalls**:
- `groupId` is required; it identifies the company or organization
- Group traits are merged with existing traits for that group
- A user can belong to multiple groups
- Group traits update the group profile, not the user profile

### 5. Track Page Views

**When to use**: User wants to record page view events in Segment

**Tool sequence**:
1. `SEGMENT_PAGE` - Send a page view event [Required]

**Key parameters**:
- `userId`: User identifier (required if no `anonymousId`)
- `anonymousId`: Anonymous identifier
- `name`: Page name (e.g., 'Home', 'Pricing', 'Dashboard')
- `category`: Page category (e.g., 'Docs', 'Marketing')
- `properties`: Object with page-specific properties (url, title, referrer)

**Pitfalls**:
- At least one of `userId` or `anonymousId` is required
- `name` and `category` are optional but recommended for proper analytics
- Standard properties include `url`, `title`, `referrer`, `path`, `search`
- Page calls are often automated; manual use is for server-side page tracking

### 6. Alias Users and Manage Sources

**When to use**: User wants to merge anonymous and identified users, or manage source configuration

**Tool sequence**:
1. `SEGMENT_ALIAS` - Link two user identities together [Optional]
2. `SEGMENT_LIST_SCHEMA_SETTINGS_IN_SOURCE` - View source schema settings [Optional]
3. `SEGMENT_UPDATE_SOURCE` - Update source configuration [Optional]

**Key parameters**:
- For ALIAS:
  - `userId`: New user identifier (the identified ID)
  - `previousId`: Old user identifier (the anonymous ID)
- For source operations:
  - `sourceId`: Source identifier

**Pitfalls**:
- ALIAS is a one-way operation; cannot be undone
- `previousId` is the anonymous/old ID, `userId` is the new/identified ID
- Not all destinations support alias calls; check destination documentation
- ALIAS should be called once when a user first identifies (e.g., signs up)
- Source updates may affect data collection; review changes carefully

## Common Patterns

### User Lifecycle

Standard Segment user lifecycle:
```
1. Anonymous user visits -> PAGE call with anonymousId
2. User interacts -> TRACK call with anonymousId
3. User signs up -> ALIAS (anonymousId -> userId), then IDENTIFY with traits
4. User takes action -> TRACK call with userId
5. User joins org -> GROUP call linking userId to groupId
```

### Batch Optimization

For bulk data ingestion:
```
1. Collect events in memory (array of message objects)
2. Each message includes type, userId/anonymousId, and type-specific fields
3. Call SEGMENT_BATCH with the collected messages
4. Check response for any individual message errors
```

### Naming Conventions

Segment recommends consistent event naming:
- **Events**: Use "Object Action" format (e.g., 'Order Completed', 'Article Viewed')
- **Properties**: Use snake_case (e.g., 'order_total', 'product_name')
- **Traits**: Use snake_case (e.g., 'first_name', 'plan_type')

## Known Pitfalls

**Identity Resolution**:
- Always include `userId` or `anonymousId` on every call
- Use ALIAS only once per user identity merge
- Identify before tracking to ensure proper user association

**Data Quality**:
- Event names should be consistent across all sources
- Properties should follow a defined schema for downstream compatibility
- Avoid sending sensitive PII unless destinations are configured for it

**Rate Limits**:
- Use BATCH for bulk operations to stay within rate limits
- Individual calls are rate-limited per source
- Batch calls are more efficient and less likely to be throttled

**Response Parsing**:
- Successful responses indicate acceptance, not delivery to destinations
- Response data may be nested under `data` key
- Check for error fields in batch responses for individual message failures

**Timestamps**:
- Must be ISO 8601 format with timezone (e.g., '2024-01-15T10:30:00Z')
- Omitting timestamp uses server receive time
- Historical data imports should include explicit timestamps

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Track event | SEGMENT_TRACK | userId, event, properties |
| Identify user | SEGMENT_IDENTIFY | userId, traits |
| Batch calls | SEGMENT_BATCH | batch (array of messages) |
| Group user | SEGMENT_GROUP | userId, groupId, traits |
| Page view | SEGMENT_PAGE | userId, name, properties |
| Alias identity | SEGMENT_ALIAS | userId, previousId |
| Source schema | SEGMENT_LIST_SCHEMA_SETTINGS_IN_SOURCE | sourceId |
| Update source | SEGMENT_UPDATE_SOURCE | sourceId |
| Warehouses | SEGMENT_LIST_CONNECTED_WAREHOUSES_FROM_SOURCE | sourceId |
