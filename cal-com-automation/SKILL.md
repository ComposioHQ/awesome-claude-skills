---
name: cal-com-automation
description: "Automate Cal.com tasks via Rube MCP (Composio): manage bookings, check availability, configure webhooks, and handle teams. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Cal.com Automation via Rube MCP

Automate Cal.com scheduling operations through Composio's Cal toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Cal.com connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `cal`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `cal`
3. If connection is not ACTIVE, follow the returned auth link to complete Cal.com authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Manage Bookings

**When to use**: User wants to list, create, or review bookings

**Tool sequence**:
1. `CAL_FETCH_ALL_BOOKINGS` - List all bookings with filters [Required]
2. `CAL_POST_NEW_BOOKING_REQUEST` - Create a new booking [Optional]

**Key parameters for listing**:
- `status`: Filter by booking status ('upcoming', 'recurring', 'past', 'cancelled', 'unconfirmed')
- `afterStart`: Filter bookings after this date (ISO 8601)
- `beforeEnd`: Filter bookings before this date (ISO 8601)

**Key parameters for creation**:
- `eventTypeId`: Event type ID for the booking
- `start`: Booking start time (ISO 8601)
- `end`: Booking end time (ISO 8601)
- `name`: Attendee name
- `email`: Attendee email
- `timeZone`: Attendee timezone (IANA format)
- `language`: Attendee language code
- `metadata`: Additional metadata object

**Pitfalls**:
- Date filters use ISO 8601 format with timezone (e.g., '2024-01-15T09:00:00Z')
- `eventTypeId` must reference a valid, active event type
- Booking creation requires matching an available slot; check availability first
- Time zone must be a valid IANA timezone string (e.g., 'America/New_York')
- Status filter values are specific strings; invalid values return empty results

### 2. Check Availability

**When to use**: User wants to find free/busy times or available booking slots

**Tool sequence**:
1. `CAL_RETRIEVE_CALENDAR_BUSY_TIMES` - Get busy time blocks [Required]
2. `CAL_GET_AVAILABLE_SLOTS_INFO` - Get specific available slots [Required]

**Key parameters**:
- `dateFrom`: Start date for availability check (YYYY-MM-DD)
- `dateTo`: End date for availability check (YYYY-MM-DD)
- `eventTypeId`: Event type to check slots for
- `timeZone`: Timezone for the availability response
- `loggedInUsersTz`: Timezone of the requesting user

**Pitfalls**:
- Busy times show when the user is NOT available
- Available slots are specific to an event type's duration and configuration
- Date range should be reasonable (not months in advance) to get accurate results
- Timezone affects how slots are displayed; always specify explicitly
- Availability reflects calendar integrations (Google Calendar, Outlook, etc.)

### 3. Configure Webhooks

**When to use**: User wants to set up or manage webhook notifications for booking events

**Tool sequence**:
1. `CAL_RETRIEVE_WEBHOOKS_LIST` - List existing webhooks [Required]
2. `CAL_GET_WEBHOOK_BY_ID` - Get specific webhook details [Optional]
3. `CAL_UPDATE_WEBHOOK_BY_ID` - Update webhook configuration [Optional]
4. `CAL_DELETE_WEBHOOK_BY_ID` - Remove a webhook [Optional]

**Key parameters**:
- `id`: Webhook ID for GET/UPDATE/DELETE operations
- `subscriberUrl`: Webhook endpoint URL
- `eventTriggers`: Array of event types to trigger on
- `active`: Whether the webhook is active
- `secret`: Webhook signing secret

**Pitfalls**:
- Webhook URLs must be publicly accessible HTTPS endpoints
- Event triggers include: 'BOOKING_CREATED', 'BOOKING_RESCHEDULED', 'BOOKING_CANCELLED', etc.
- Inactive webhooks do not fire; toggle `active` to enable/disable
- Webhook secrets are used for payload signature verification

### 4. Manage Teams

**When to use**: User wants to create, view, or manage teams and team event types

**Tool sequence**:
1. `CAL_GET_TEAMS_LIST` - List all teams [Required]
2. `CAL_GET_TEAM_INFORMATION_BY_TEAM_ID` - Get specific team details [Optional]
3. `CAL_CREATE_TEAM_IN_ORGANIZATION` - Create a new team [Optional]
4. `CAL_RETRIEVE_TEAM_EVENT_TYPES` - List event types for a team [Optional]

**Key parameters**:
- `teamId`: Team identifier
- `name`: Team name (for creation)
- `slug`: URL-friendly team identifier

**Pitfalls**:
- Team creation may require organization-level permissions
- Team event types are separate from personal event types
- Team slugs must be URL-safe and unique within the organization

### 5. Organization Management

**When to use**: User wants to view organization details

**Tool sequence**:
1. `CAL_GET_ORGANIZATION_ID` - Get the organization ID [Required]

**Key parameters**: (none required)

**Pitfalls**:
- Organization ID is needed for team creation and org-level operations
- Not all Cal.com accounts have organizations; personal plans may return errors

## Common Patterns

### Booking Creation Flow

```
1. Call CAL_GET_AVAILABLE_SLOTS_INFO to find open slots
2. Present available times to the user
3. Call CAL_POST_NEW_BOOKING_REQUEST with selected slot
4. Confirm booking creation response
```

### ID Resolution

**Team name -> Team ID**:
```
1. Call CAL_GET_TEAMS_LIST
2. Find team by name in response
3. Extract id field
```

### Webhook Setup

```
1. Call CAL_RETRIEVE_WEBHOOKS_LIST to check existing hooks
2. Create or update webhook with desired triggers
3. Verify webhook fires on test booking
```

## Known Pitfalls

**Date/Time Formats**:
- Booking times: ISO 8601 with timezone (e.g., '2024-01-15T09:00:00Z')
- Availability dates: YYYY-MM-DD format
- Always specify timezone explicitly to avoid confusion

**Event Types**:
- Event type IDs are numeric integers
- Event types define duration, location, and booking rules
- Disabled event types cannot accept new bookings

**Permissions**:
- Team operations require team membership or admin access
- Organization operations require org-level permissions
- Webhook management requires appropriate access level

**Rate Limits**:
- Cal.com API has rate limits per API key
- Implement backoff on 429 responses

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List bookings | CAL_FETCH_ALL_BOOKINGS | status, afterStart, beforeEnd |
| Create booking | CAL_POST_NEW_BOOKING_REQUEST | eventTypeId, start, end, name, email |
| Get busy times | CAL_RETRIEVE_CALENDAR_BUSY_TIMES | dateFrom, dateTo |
| Get available slots | CAL_GET_AVAILABLE_SLOTS_INFO | eventTypeId, dateFrom, dateTo |
| List webhooks | CAL_RETRIEVE_WEBHOOKS_LIST | (none) |
| Get webhook | CAL_GET_WEBHOOK_BY_ID | id |
| Update webhook | CAL_UPDATE_WEBHOOK_BY_ID | id, subscriberUrl, eventTriggers |
| Delete webhook | CAL_DELETE_WEBHOOK_BY_ID | id |
| List teams | CAL_GET_TEAMS_LIST | (none) |
| Get team | CAL_GET_TEAM_INFORMATION_BY_TEAM_ID | teamId |
| Create team | CAL_CREATE_TEAM_IN_ORGANIZATION | name, slug |
| Team event types | CAL_RETRIEVE_TEAM_EVENT_TYPES | teamId |
| Get org ID | CAL_GET_ORGANIZATION_ID | (none) |
