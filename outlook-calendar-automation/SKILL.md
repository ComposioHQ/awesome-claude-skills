---
name: outlook-calendar-automation
description: "Automate Outlook Calendar tasks via Rube MCP (Composio): create events, manage attendees, find meeting times, and handle invitations. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Outlook Calendar Automation via Rube MCP

Automate Outlook Calendar operations through Composio's Outlook toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Outlook connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `outlook`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `outlook`
3. If connection is not ACTIVE, follow the returned auth link to complete Microsoft OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create Calendar Events

**When to use**: User wants to schedule a new event on their Outlook calendar

**Tool sequence**:
1. `OUTLOOK_LIST_CALENDARS` - List available calendars [Optional]
2. `OUTLOOK_CALENDAR_CREATE_EVENT` - Create the event [Required]

**Key parameters**:
- `subject`: Event title
- `start_datetime`: ISO 8601 start time (e.g., '2025-01-03T10:00:00')
- `end_datetime`: ISO 8601 end time (must be after start)
- `time_zone`: IANA or Windows timezone (e.g., 'America/New_York', 'Pacific Standard Time')
- `attendees_info`: Array of email strings or attendee objects
- `body`: Event description (plain text or HTML)
- `is_html`: Set true if body contains HTML
- `location`: Physical location string
- `is_online_meeting`: Set true for Teams meeting link
- `online_meeting_provider`: 'teamsForBusiness' for Teams integration
- `show_as`: 'free', 'tentative', 'busy', 'oof'

**Pitfalls**:
- start_datetime must be chronologically before end_datetime
- time_zone is required and must be a valid IANA or Windows timezone name
- Adding attendees can trigger invitation emails immediately
- To generate a Teams meeting link, set BOTH is_online_meeting=true AND online_meeting_provider='teamsForBusiness'
- user_id defaults to 'me'; use email or UUID for other users' calendars

### 2. List and Search Events

**When to use**: User wants to find events on their calendar

**Tool sequence**:
1. `OUTLOOK_GET_MAILBOX_SETTINGS` - Get user timezone for accurate queries [Prerequisite]
2. `OUTLOOK_LIST_EVENTS` - Search events with filters [Required]
3. `OUTLOOK_GET_EVENT` - Get full details for a specific event [Optional]
4. `OUTLOOK_GET_CALENDAR_VIEW` - Get events active during a time window [Alternative]

**Key parameters**:
- `filter`: OData filter string (e.g., "start/dateTime ge '2024-07-01T00:00:00Z'")
- `select`: Array of properties to return
- `orderby`: Sort criteria (e.g., ['start/dateTime desc'])
- `top`: Results per page (1-999)
- `timezone`: Display timezone for results
- `start_datetime`/`end_datetime`: For CALENDAR_VIEW time window (UTC with Z suffix)

**Pitfalls**:
- OData filter datetime values require single quotes and Z suffix
- Use 'start/dateTime' for event start filtering, NOT 'receivedDateTime' (that is for emails)
- 'createdDateTime' supports orderby/select but NOT filtering
- Pagination: follow @odata.nextLink until all pages are collected
- CALENDAR_VIEW is better for "what's on my calendar today" queries (includes spanning events)
- LIST_EVENTS is better for keyword/category filtering
- Response events have start/end nested as start.dateTime and end.dateTime

### 3. Update Events

**When to use**: User wants to modify an existing calendar event

**Tool sequence**:
1. `OUTLOOK_LIST_EVENTS` - Find the event to update [Prerequisite]
2. `OUTLOOK_UPDATE_CALENDAR_EVENT` - Update the event [Required]

**Key parameters**:
- `event_id`: Unique event identifier (from LIST_EVENTS)
- `subject`: New event title (optional)
- `start_datetime`/`end_datetime`: New times (optional)
- `time_zone`: Timezone for new times
- `attendees`: Updated attendee list (replaces existing if provided)
- `body`: Updated description with contentType and content
- `location`: Updated location

**Pitfalls**:
- UPDATE merges provided fields with existing event; unspecified fields are preserved
- Providing attendees replaces the ENTIRE attendee list; include all desired attendees
- Providing categories replaces the ENTIRE category list
- Updating times may trigger re-sends to attendees
- event_id is required; obtain from LIST_EVENTS first

### 4. Delete Events and Decline Invitations

**When to use**: User wants to remove an event or decline a meeting invitation

**Tool sequence**:
1. `OUTLOOK_DELETE_EVENT` - Delete an event [Optional]
2. `OUTLOOK_DECLINE_EVENT` - Decline a meeting invitation [Optional]

**Key parameters**:
- `event_id`: Event to delete or decline
- `send_notifications`: Send cancellation notices to attendees (default true)
- `comment`: Reason for declining (for DECLINE_EVENT)
- `proposedNewTime`: Suggest alternative time when declining

**Pitfalls**:
- Deletion with send_notifications=true sends cancellation emails
- Declining supports proposing a new time with start/end in ISO 8601 format
- Deleting a recurring event master deletes all occurrences
- sendResponse in DECLINE_EVENT controls whether the organizer is notified

### 5. Find Available Meeting Times

**When to use**: User wants to find optimal meeting slots across multiple people

**Tool sequence**:
1. `OUTLOOK_FIND_MEETING_TIMES` - Get meeting time suggestions [Required]
2. `OUTLOOK_GET_SCHEDULE` - Check free/busy for specific people [Alternative]

**Key parameters**:
- `attendees`: Array of attendee objects with email and type
- `meetingDuration`: ISO 8601 duration (e.g., 'PT1H' for 1 hour, 'PT30M' for 30 min)
- `timeConstraint`: Time slots to search within
- `minimumAttendeePercentage`: Minimum confidence threshold (0-100)
- `Schedules`: Email array for GET_SCHEDULE
- `StartTime`/`EndTime`: Time window for schedule lookup (max 62 days)

**Pitfalls**:
- FIND_MEETING_TIMES searches within work hours by default; use activityDomain='unrestricted' for 24/7
- Time constraint time slots require dateTime and timeZone for both start and end
- GET_SCHEDULE period cannot exceed 62 days
- Meeting suggestions respect attendee availability but may return suboptimal times for complex groups

## Common Patterns

### Event ID Resolution

```
1. Call OUTLOOK_LIST_EVENTS with time-bound filter
2. Find target event by subject or other criteria
3. Extract event id (e.g., 'AAMkAGI2TAAA=')
4. Use in UPDATE, DELETE, or GET_EVENT calls
```

### OData Filter Syntax for Calendar

**Time range filter**:
```
filter: "start/dateTime ge '2024-07-01T00:00:00Z' and start/dateTime le '2024-07-31T23:59:59Z'"
```

**Subject contains**:
```
filter: "contains(subject, 'Project Review')"
```

**Combined**:
```
filter: "contains(subject, 'Review') and categories/any(c:c eq 'Work')"
```

### Timezone Handling

- Get user timezone: `OUTLOOK_GET_MAILBOX_SETTINGS` with select=['timeZone']
- Use consistent timezone in filter datetime values
- Calendar View requires UTC timestamps with Z suffix
- LIST_EVENTS filter accepts timezone in datetime values

### Online Meeting Creation

```
1. Set is_online_meeting: true
2. Set online_meeting_provider: 'teamsForBusiness'
3. Create event with OUTLOOK_CALENDAR_CREATE_EVENT
4. Teams join link available in response onlineMeeting field
5. Or retrieve via OUTLOOK_GET_EVENT for the full join URL
```

## Known Pitfalls

**DateTime Formats**:
- ISO 8601 format required: '2025-01-03T10:00:00'
- Calendar View requires UTC with Z: '2025-01-03T10:00:00Z'
- Filter values need single quotes: "'2025-01-03T00:00:00Z'"
- Timezone mismatches shift event boundaries; always resolve user timezone first

**OData Filter Errors**:
- 400 Bad Request usually indicates filter syntax issues
- Not all event properties support filtering (createdDateTime does not)
- Retry with adjusted syntax/bounds on 400 errors
- Valid filter fields: start/dateTime, end/dateTime, subject, categories, isAllDay

**Attendee Management**:
- Adding attendees triggers invitation emails
- Updating attendees replaces the full list; include all desired attendees
- Attendee types: 'required', 'optional', 'resource'
- Calendar delegation affects which calendars are accessible

**Response Structure**:
- Events nested at response.data.value
- Event times at event.start.dateTime and event.end.dateTime
- Calendar View may nest at data.results[i].response.data.value
- Parse defensively with fallbacks for different nesting levels

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Create event | OUTLOOK_CALENDAR_CREATE_EVENT | subject, start_datetime, end_datetime, time_zone |
| List events | OUTLOOK_LIST_EVENTS | filter, select, top, timezone |
| Get event details | OUTLOOK_GET_EVENT | event_id |
| Calendar view | OUTLOOK_GET_CALENDAR_VIEW | start_datetime, end_datetime |
| Update event | OUTLOOK_UPDATE_CALENDAR_EVENT | event_id, subject, start_datetime |
| Delete event | OUTLOOK_DELETE_EVENT | event_id, send_notifications |
| Decline event | OUTLOOK_DECLINE_EVENT | event_id, comment |
| Find meeting times | OUTLOOK_FIND_MEETING_TIMES | attendees, meetingDuration |
| Get schedule | OUTLOOK_GET_SCHEDULE | Schedules, StartTime, EndTime |
| List calendars | OUTLOOK_LIST_CALENDARS | user_id |
| Mailbox settings | OUTLOOK_GET_MAILBOX_SETTINGS | select |
