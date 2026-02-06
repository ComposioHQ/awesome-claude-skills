---
name: google-calendar-automation
description: Automate Google Calendar events, scheduling, availability checks, and attendee management via Rube MCP (Composio). Create events, find free slots, manage attendees, and list calendars programmatically.
requires:
  mcp: [rube]
---

# Google Calendar Automation via Rube MCP

Automate Google Calendar workflows including event creation, scheduling, availability checks, attendee management, and calendar browsing through Composio's Google Calendar toolkit.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Google Calendar connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `googlecalendar`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `googlecalendar`
3. If connection is not ACTIVE, follow the returned auth link to complete Google OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create and Manage Events

**When to use**: User wants to create, update, or delete calendar events

**Tool sequence**:
1. `GOOGLECALENDAR_LIST_CALENDARS` - Identify target calendar ID [Prerequisite]
2. `GOOGLECALENDAR_GET_CURRENT_DATE_TIME` - Get current time with proper timezone [Optional]
3. `GOOGLECALENDAR_FIND_FREE_SLOTS` - Check availability before booking [Optional]
4. `GOOGLECALENDAR_CREATE_EVENT` - Create the event [Required]
5. `GOOGLECALENDAR_PATCH_EVENT` - Update specific fields of an existing event [Alternative]
6. `GOOGLECALENDAR_UPDATE_EVENT` - Full replacement update of an event [Alternative]
7. `GOOGLECALENDAR_DELETE_EVENT` - Delete an event [Optional]

**Key parameters**:
- `calendar_id`: Use 'primary' for main calendar, or specific calendar ID
- `start_datetime`: ISO 8601 format 'YYYY-MM-DDTHH:MM:SS' (NOT natural language)
- `timezone`: IANA timezone name (e.g., 'America/New_York', NOT 'EST' or 'PST')
- `event_duration_hour`: Hours (0+)
- `event_duration_minutes`: Minutes (0-59 only; NEVER use 60+)
- `summary`: Event title
- `attendees`: Array of email addresses (NOT names)
- `location`: Free-form text for event location

**Pitfalls**:
- `start_datetime` must be ISO 8601; natural language like 'tomorrow' is rejected
- `event_duration_minutes` max is 59; use `event_duration_hour=1` instead of `event_duration_minutes=60`
- `timezone` must be IANA identifier; abbreviations like 'EST', 'PST' are NOT valid
- `attendees` only accepts email addresses, not names; resolve names first
- Google Meet link creation defaults to true; may fail on personal Gmail accounts (graceful fallback)
- Organizer is auto-added as attendee unless `exclude_organizer=true`

### 2. List and Search Events

**When to use**: User wants to find or browse events on their calendar

**Tool sequence**:
1. `GOOGLECALENDAR_LIST_CALENDARS` - Get available calendars [Prerequisite]
2. `GOOGLECALENDAR_FIND_EVENT` - Search by title/keyword with time bounds [Required]
3. `GOOGLECALENDAR_EVENTS_LIST` - List events in a time range [Alternative]
4. `GOOGLECALENDAR_EVENTS_INSTANCES` - List instances of a recurring event [Optional]

**Key parameters**:
- `query` / `q`: Free-text search (matches summary, description, location, attendees)
- `timeMin`: Lower bound (RFC3339 with timezone offset, e.g., '2024-01-01T00:00:00-08:00')
- `timeMax`: Upper bound (RFC3339 with timezone offset)
- `singleEvents`: true to expand recurring events into instances
- `orderBy`: 'startTime' (requires singleEvents=true) or 'updated'
- `maxResults`: Results per page (max 2500)

**Pitfalls**:
- **Timezone warning**: UTC timestamps (ending in 'Z') don't align with local dates; use local timezone offsets instead
- Example: '2026-01-19T00:00:00Z' covers 2026-01-18 4pm to 2026-01-19 4pm in PST
- Omitting `timeMin`/`timeMax` scans the full calendar and can be slow
- `pageToken` in response means more results; paginate until absent
- `orderBy='startTime'` requires `singleEvents=true`

### 3. Manage Attendees and Invitations

**When to use**: User wants to add, remove, or update event attendees

**Tool sequence**:
1. `GOOGLECALENDAR_FIND_EVENT` or `GOOGLECALENDAR_EVENTS_LIST` - Find the event [Prerequisite]
2. `GOOGLECALENDAR_PATCH_EVENT` - Add attendees (replaces entire attendees list) [Required]
3. `GOOGLECALENDAR_REMOVE_ATTENDEE` - Remove a specific attendee by email [Required]

**Key parameters**:
- `event_id`: Unique event identifier (opaque string, NOT the event title)
- `attendees`: Full list of attendee emails (PATCH replaces entire list)
- `attendee_email`: Email to remove
- `send_updates`: 'all', 'externalOnly', or 'none'

**Pitfalls**:
- `event_id` is a technical identifier, NOT the event title; always search first to get the ID
- `PATCH_EVENT` attendees field replaces the entire list; include existing attendees to avoid removing them
- Attendee names cannot be resolved; always use email addresses
- Use `GMAIL_SEARCH_PEOPLE` to resolve names to emails before managing attendees

### 4. Check Availability and Free/Busy Status

**When to use**: User wants to find available time slots or check busy periods

**Tool sequence**:
1. `GOOGLECALENDAR_LIST_CALENDARS` - Identify calendars to check [Prerequisite]
2. `GOOGLECALENDAR_GET_CURRENT_DATE_TIME` - Get current time with timezone [Optional]
3. `GOOGLECALENDAR_FIND_FREE_SLOTS` - Find free intervals across calendars [Required]
4. `GOOGLECALENDAR_FREE_BUSY_QUERY` - Get raw busy periods for computing gaps [Fallback]
5. `GOOGLECALENDAR_CREATE_EVENT` - Book a confirmed slot [Required]

**Key parameters**:
- `items`: List of calendar IDs to check (e.g., ['primary'])
- `time_min`/`time_max`: Query interval (defaults to current day if omitted)
- `timezone`: IANA timezone for interpreting naive timestamps
- `calendarExpansionMax`: Max calendars (1-50)
- `groupExpansionMax`: Max members per group (1-100)

**Pitfalls**:
- Maximum span ~90 days per Google Calendar freeBusy API limit
- Very long ranges or inaccessible calendars yield empty/invalid results
- Only calendars with at least freeBusyReader access are visible
- Free slots responses may normalize to UTC ('Z'); check offsets
- `GOOGLECALENDAR_FREE_BUSY_QUERY` requires RFC3339 timestamps with timezone

## Common Patterns

### ID Resolution
- **Calendar name -> calendar_id**: `GOOGLECALENDAR_LIST_CALENDARS` to enumerate all calendars
- **Event title -> event_id**: `GOOGLECALENDAR_FIND_EVENT` or `GOOGLECALENDAR_EVENTS_LIST`
- **Attendee name -> email**: `GMAIL_SEARCH_PEOPLE`

### Timezone Handling
- Always use IANA timezone identifiers (e.g., 'America/Los_Angeles')
- Use `GOOGLECALENDAR_GET_CURRENT_DATE_TIME` to get current time in user's timezone
- When querying events for a local date, use timestamps with local offset, NOT UTC
- Example: '2026-01-19T00:00:00-08:00' for PST, NOT '2026-01-19T00:00:00Z'

### Pagination
- `GOOGLECALENDAR_EVENTS_LIST` returns `nextPageToken`; iterate until absent
- `GOOGLECALENDAR_LIST_CALENDARS` also paginates; use `page_token`

## Known Pitfalls

- **Natural language dates**: NOT supported; all dates must be ISO 8601 or RFC3339
- **Timezone mismatch**: UTC timestamps don't align with local dates for filtering
- **Duration limits**: `event_duration_minutes` max 59; use hours for longer durations
- **IANA timezones only**: 'EST', 'PST', etc. are NOT valid; use 'America/New_York'
- **Event IDs are opaque**: Always search to get event_id; never guess or construct
- **Attendees as emails**: Names cannot be used; resolve with GMAIL_SEARCH_PEOPLE
- **PATCH replaces attendees**: Include all desired attendees in the array, not just new ones
- **Conference limitations**: Google Meet may fail on personal accounts (graceful fallback)
- **Rate limits**: High-volume searches can trigger 403/429; throttle between calls

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List calendars | `GOOGLECALENDAR_LIST_CALENDARS` | `max_results` |
| Create event | `GOOGLECALENDAR_CREATE_EVENT` | `start_datetime`, `timezone`, `summary` |
| Update event | `GOOGLECALENDAR_PATCH_EVENT` | `calendar_id`, `event_id`, fields to update |
| Delete event | `GOOGLECALENDAR_DELETE_EVENT` | `calendar_id`, `event_id` |
| Search events | `GOOGLECALENDAR_FIND_EVENT` | `query`, `timeMin`, `timeMax` |
| List events | `GOOGLECALENDAR_EVENTS_LIST` | `calendarId`, `timeMin`, `timeMax` |
| Recurring instances | `GOOGLECALENDAR_EVENTS_INSTANCES` | `calendarId`, `eventId` |
| Find free slots | `GOOGLECALENDAR_FIND_FREE_SLOTS` | `items`, `time_min`, `time_max`, `timezone` |
| Free/busy query | `GOOGLECALENDAR_FREE_BUSY_QUERY` | `timeMin`, `timeMax`, `items` |
| Remove attendee | `GOOGLECALENDAR_REMOVE_ATTENDEE` | `event_id`, `attendee_email` |
| Get current time | `GOOGLECALENDAR_GET_CURRENT_DATE_TIME` | `timezone` |
| Get calendar | `GOOGLECALENDAR_GET_CALENDAR` | `calendar_id` |
