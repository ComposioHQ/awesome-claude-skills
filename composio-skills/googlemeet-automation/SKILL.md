---
name: googlemeet-automation
description: "Automate Google Meet tasks via Rube MCP (Composio): create Meet spaces, schedule video conferences via Calendar events, manage meeting access. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Google Meet Automation via Rube MCP

Create Google Meet video conferences, schedule meetings with Meet links, and manage meeting spaces using Rube MCP (Composio).

**Toolkit docs**: [composio.dev/toolkits/googlemeet](https://composio.dev/toolkits/googlemeet)

## Prerequisites
- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `googlemeet`
- For scheduling meetings with attendees, also connect the `googlecalendar` toolkit
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup
**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.

1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `googlemeet`
3. Optionally also connect `googlecalendar` for scheduling meetings with calendar events
4. If connection is not ACTIVE, follow the returned auth link to complete setup
5. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create a Standalone Meet Space
Use `GOOGLEMEET_CREATE_MEET` to create a new Google Meet meeting space with optional access configuration.
```
Tool: GOOGLEMEET_CREATE_MEET
Description: Creates a new Google Meet space, optionally configuring
  its access type and entry points.
Note: Call RUBE_SEARCH_TOOLS to get the full schema for this tool.
```

### 2. Schedule a Meeting with Google Meet Link
Use `GOOGLECALENDAR_CREATE_EVENT` to create a calendar event that automatically generates a Google Meet link (enabled by default).
```
Tool: GOOGLECALENDAR_CREATE_EVENT
Parameters:
  - start_datetime (required): ISO 8601 format (e.g., "2025-01-16T13:00:00")
  - summary: Meeting title
  - attendees: List of email addresses
  - timezone: IANA timezone (e.g., "America/New_York")
  - event_duration_hour: Duration hours (default: 0)
  - event_duration_minutes: Duration minutes (default: 30, max: 59)
  - create_meeting_room: true (default) -- generates Meet link
  - description: Meeting agenda/notes
  - location: Physical or virtual location
```

### 3. Find Available Time Slots
Use `GOOGLECALENDAR_FIND_FREE_SLOTS` before scheduling to find when participants are available.
```
Tool: GOOGLECALENDAR_FIND_FREE_SLOTS
Parameters:
  - items: List of calendar IDs to check (e.g., ["primary", "user@example.com"])
  - time_min: Start of time window (ISO format)
  - time_max: End of time window (ISO format)
  - timezone: IANA timezone
```

### 4. Update an Existing Meeting
Use `GOOGLECALENDAR_PATCH_EVENT` to modify meeting details, reschedule, or update attendees.
```
Tool: GOOGLECALENDAR_PATCH_EVENT
Parameters:
  - calendar_id (required): Calendar ID (use "primary")
  - event_id (required): Event ID (from search/list)
  - summary: Updated title
  - start_time / end_time: Rescheduled times
  - attendees: Updated attendee list (replaces existing)
  - send_updates: Notification preference ("all", "externalOnly", "none")
```

## Common Patterns

- **Quick meeting link**: Use `GOOGLEMEET_CREATE_MEET` for an instant meeting space without a calendar event.
- **Scheduled meeting with attendees**: Use `GOOGLECALENDAR_CREATE_EVENT` with `create_meeting_room: true` (default) to create a calendar event with an embedded Meet link. Workspace accounts get a Meet link automatically.
- **Check availability first**: Use `GOOGLECALENDAR_FIND_FREE_SLOTS` to find open time slots before scheduling with `GOOGLECALENDAR_CREATE_EVENT`.
- **Resolve names to emails**: Use `GMAIL_SEARCH_PEOPLE` (gmail toolkit) to look up email addresses from names before adding attendees.
- **Get current time**: Use `GOOGLECALENDAR_GET_CURRENT_DATE_TIME` with a timezone to get the current date/time for scheduling relative to "now".

## Known Pitfalls

- **Attendees must be email addresses**: `GOOGLECALENDAR_CREATE_EVENT` only accepts email addresses for attendees, not names. Use `GMAIL_SEARCH_PEOPLE` to resolve names to emails first.
- **Personal Gmail vs Workspace**: The `create_meeting_room` feature works best with Google Workspace accounts. Personal Gmail accounts will gracefully fallback to creating an event without a Meet link.
- **start_datetime format**: Must be exact ISO 8601 (e.g., `2025-01-16T13:00:00`). Natural language like "tomorrow at 3pm" is NOT supported.
- **Duration limits**: `event_duration_minutes` max is 59. For 1+ hour meetings, use `event_duration_hour` combined with `event_duration_minutes`.
- **Timezone is critical**: Always provide `timezone` as a valid IANA identifier (e.g., `America/New_York`). Abbreviations like "EST" or "PST" are NOT valid.
- **Event IDs are opaque**: To update or delete events, you must first retrieve the event ID using a search or list tool.

## Quick Reference
| Action | Tool | Key Parameters |
|--------|------|----------------|
| Create Meet space | `GOOGLEMEET_CREATE_MEET` | (see full schema via RUBE_SEARCH_TOOLS) |
| Schedule meeting | `GOOGLECALENDAR_CREATE_EVENT` | `start_datetime`, `summary`, `attendees`, `timezone` |
| Find free slots | `GOOGLECALENDAR_FIND_FREE_SLOTS` | `items`, `time_min`, `time_max`, `timezone` |
| Update meeting | `GOOGLECALENDAR_PATCH_EVENT` | `calendar_id`, `event_id`, `summary`, `start_time` |
| Get current time | `GOOGLECALENDAR_GET_CURRENT_DATE_TIME` | `timezone` |
| Look up contacts | `GMAIL_SEARCH_PEOPLE` | `query` |

---
*Powered by [Composio](https://composio.dev)*
