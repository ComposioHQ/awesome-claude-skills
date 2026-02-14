---
name: zoom-automation
description: Automate Zoom meeting creation, management, recordings, webinars, and participant tracking via Rube MCP (Composio). Always search tools first for current schemas.
requires:
  mcp: [rube]
---

# Zoom Automation via Rube MCP

Automate Zoom operations including meeting scheduling, webinar management, cloud recording retrieval, participant tracking, and usage reporting through Composio's Zoom toolkit.

**Toolkit docs**: [composio.dev/toolkits/zoom](https://composio.dev/toolkits/zoom)

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Zoom connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `zoom`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas
- Most features require a paid Zoom account (Pro plan or higher)

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `zoom`
3. If connection is not ACTIVE, follow the returned auth link to complete Zoom OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create and Schedule Meetings

**When to use**: User wants to create a new Zoom meeting with specific time, duration, and settings

**Tool sequence**:
1. `ZOOM_GET_USER` - Verify authenticated user and check license type [Prerequisite]
2. `ZOOM_CREATE_A_MEETING` - Create the meeting with topic, time, duration, and settings [Required]
3. `ZOOM_GET_A_MEETING` - Retrieve full meeting details including join_url [Optional]
4. `ZOOM_UPDATE_A_MEETING` - Modify meeting settings or reschedule [Optional]
5. `ZOOM_ADD_A_MEETING_REGISTRANT` - Register participants for registration-enabled meetings [Optional]

**Key parameters**:
- `userId`: Always use `"me"` for user-level apps
- `topic`: Meeting subject line
- `type`: `1` (instant), `2` (scheduled), `3` (recurring no fixed time), `8` (recurring fixed time)
- `start_time`: ISO 8601 format (`yyyy-MM-ddTHH:mm:ssZ` for UTC or `yyyy-MM-ddTHH:mm:ss` with timezone field)
- `timezone`: Timezone ID (e.g., `"America/New_York"`)
- `duration`: Duration in minutes
- `settings__auto_recording`: `"none"`, `"local"`, or `"cloud"`
- `settings__waiting_room`: Boolean to enable waiting room
- `settings__join_before_host`: Boolean (disabled when waiting room is enabled)
- `settings__meeting_invitees`: Array of invitee objects with email addresses

**Pitfalls**:
- `start_time` must be in the future; Zoom stores and returns times in UTC regardless of input timezone
- If no `start_time` is set for type `2`, it becomes an instant meeting that expires after 30 days
- The `join_url` for participants and `start_url` for host come from the create response - persist these
- `start_url` expires in 2 hours (or 90 days for `custCreate` users)
- Meeting creation is rate-limited to 100 requests/day
- Setting names use double underscores for nesting (e.g., `settings__host_video`)

### 2. List and Manage Meetings

**When to use**: User wants to view upcoming, live, or past meetings

**Tool sequence**:
1. `ZOOM_LIST_MEETINGS` - List meetings by type (scheduled, live, upcoming, previous) [Required]
2. `ZOOM_GET_A_MEETING` - Get detailed info for a specific meeting [Optional]
3. `ZOOM_UPDATE_A_MEETING` - Modify meeting details [Optional]

**Key parameters**:
- `userId`: Use `"me"` for authenticated user
- `type`: `"scheduled"` (default), `"live"`, `"upcoming"`, `"upcoming_meetings"`, `"previous_meetings"`
- `page_size`: Records per page (default 30)
- `next_page_token`: Pagination token from previous response
- `from` / `to`: Date range filters

**Pitfalls**:
- `ZOOM_LIST_MEETINGS` excludes instant meetings and only shows unexpired scheduled meetings
- For past meetings, use `type: "previous_meetings"`
- Pagination: always follow `next_page_token` until empty to get complete results
- Token expiration: `next_page_token` expires after 15 minutes
- Meeting IDs can exceed 10 digits; store as long integers, not standard integers

### 3. Manage Recordings

**When to use**: User wants to list, retrieve, or delete cloud recordings

**Tool sequence**:
1. `ZOOM_LIST_ALL_RECORDINGS` - List all cloud recordings for a user within a date range [Required]
2. `ZOOM_GET_MEETING_RECORDINGS` - Get recordings for a specific meeting [Optional]
3. `ZOOM_DELETE_MEETING_RECORDINGS` - Move recordings to trash or permanently delete [Optional]
4. `ZOOM_LIST_ARCHIVED_FILES` - List archived meeting/webinar files [Optional]

**Key parameters**:
- `userId`: Use `"me"` for authenticated user
- `from` / `to`: Date range in `yyyy-mm-dd` format (max 1 month range)
- `meetingId`: Meeting ID or UUID for specific recording retrieval
- `action`: `"trash"` (recoverable) or `"delete"` (permanent) for deletion
- `include_fields`: Set to `"download_access_token"` to get JWT for downloading recordings
- `trash`: Set `true` to list recordings from trash

**Pitfalls**:
- Date range maximum is 1 month; API auto-adjusts `from` if range exceeds this
- Cloud Recording must be enabled on the account
- UUIDs starting with `/` or containing `//` must be double URL-encoded
- `ZOOM_DELETE_MEETING_RECORDINGS` defaults to `"trash"` action (recoverable); `"delete"` is permanent
- Download URLs require the OAuth token in the Authorization header for passcode-protected recordings
- Requires Pro plan or higher

### 4. Get Meeting Participants and Reports

**When to use**: User wants to see who attended a past meeting or get usage statistics

**Tool sequence**:
1. `ZOOM_GET_PAST_MEETING_PARTICIPANTS` - List attendees of a completed meeting [Required]
2. `ZOOM_GET_A_MEETING` - Get meeting details and registration info for upcoming meetings [Optional]
3. `ZOOM_GET_DAILY_USAGE_REPORT` - Get daily usage statistics (meetings, participants, minutes) [Optional]
4. `ZOOM_GET_A_MEETING_SUMMARY` - Get AI-generated meeting summary [Optional]

**Key parameters**:
- `meetingId`: Meeting ID (latest instance) or UUID (specific occurrence)
- `page_size`: Records per page (default 30)
- `next_page_token`: Pagination token for large participant lists

**Pitfalls**:
- `ZOOM_GET_PAST_MEETING_PARTICIPANTS` only works for completed meetings on paid plans
- Solo meetings (no other participants) return empty results
- UUID encoding: UUIDs starting with `/` or containing `//` must be double-encoded
- Always paginate with `next_page_token` until empty to avoid dropping attendees
- `ZOOM_GET_A_MEETING_SUMMARY` requires a paid plan with AI Companion enabled; free accounts get 400 errors
- `ZOOM_GET_DAILY_USAGE_REPORT` has a Heavy rate limit; avoid frequent calls

### 5. Manage Webinars

**When to use**: User wants to list webinars or register participants for webinars

**Tool sequence**:
1. `ZOOM_LIST_WEBINARS` - List scheduled or upcoming webinars [Required]
2. `ZOOM_GET_A_WEBINAR` - Get detailed webinar information [Optional]
3. `ZOOM_ADD_A_WEBINAR_REGISTRANT` - Register a participant for a webinar [Optional]

**Key parameters**:
- `userId`: Use `"me"` for authenticated user
- `type`: `"scheduled"` (default) or `"upcoming"`
- `page_size`: Records per page (default 30)
- `next_page_token`: Pagination token

**Pitfalls**:
- Webinar features require Pro plan or higher with Webinar add-on
- Free/basic accounts cannot use webinar tools
- Only shows unexpired webinars
- Registration must be enabled on the webinar for `ZOOM_ADD_A_WEBINAR_REGISTRANT` to work

## Common Patterns

### ID Resolution
- **User ID**: Always use `"me"` for user-level apps to refer to the authenticated user
- **Meeting ID**: Numeric ID (store as long integer); use for latest instance
- **Meeting UUID**: Use for specific occurrence of recurring meetings; double-encode if starts with `/` or contains `//`
- **Occurrence ID**: Use with recurring meetings to target a specific occurrence

### Pagination
Most Zoom list endpoints use token-based pagination:
- Follow `next_page_token` until it is empty or missing
- Token expires after 15 minutes
- Set explicit `page_size` (default 30, varies by endpoint)
- Do not use `page_number` (deprecated on many endpoints)

### Time Handling
- Zoom stores all times in UTC internally
- Provide `timezone` field alongside `start_time` for local time input
- Use ISO 8601 format: `yyyy-MM-ddTHH:mm:ssZ` (UTC) or `yyyy-MM-ddTHH:mm:ss` (with timezone field)
- Date-only fields use `yyyy-mm-dd` format

## Known Pitfalls

### Plan Requirements
- Most recording and participant features require Pro plan or higher
- Webinar features require Webinar add-on
- AI meeting summaries require AI Companion feature enabled
- Archived files require "Meeting and Webinar Archiving" enabled by Zoom Support

### Rate Limits
- Meeting creation: 100 requests/day, 100 updates per meeting in 24 hours
- `ZOOM_GET_PAST_MEETING_PARTICIPANTS`: Moderate throttle; add delays for batch processing
- `ZOOM_GET_DAILY_USAGE_REPORT`: Heavy rate limit
- `ZOOM_GET_A_MEETING`, `ZOOM_GET_MEETING_RECORDINGS`: Light rate limit
- `ZOOM_LIST_MEETINGS`, `ZOOM_LIST_ALL_RECORDINGS`: Medium rate limit

### Parameter Quirks
- Nested settings use double underscore notation (e.g., `settings__waiting_room`)
- `start_url` expires in 2 hours; renew via API if needed
- `join_before_host` is automatically disabled when `waiting_room` is `true`
- Recurring meeting fields (`recurrence__*`) only apply to type `3` and `8`
- `password` field has max 10 characters with alphanumeric and `@`, `-`, `_`, `*` only

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Create meeting | `ZOOM_CREATE_A_MEETING` | `userId`, `topic`, `start_time`, `type` |
| Get meeting details | `ZOOM_GET_A_MEETING` | `meetingId` |
| Update meeting | `ZOOM_UPDATE_A_MEETING` | `meetingId`, fields to update |
| List meetings | `ZOOM_LIST_MEETINGS` | `userId`, `type`, `page_size` |
| Get user info | `ZOOM_GET_USER` | `userId` |
| List recordings | `ZOOM_LIST_ALL_RECORDINGS` | `userId`, `from`, `to` |
| Get recording | `ZOOM_GET_MEETING_RECORDINGS` | `meetingId` |
| Delete recording | `ZOOM_DELETE_MEETING_RECORDINGS` | `meetingId`, `action` |
| Past participants | `ZOOM_GET_PAST_MEETING_PARTICIPANTS` | `meetingId`, `page_size` |
| Daily usage report | `ZOOM_GET_DAILY_USAGE_REPORT` | date params |
| Meeting summary | `ZOOM_GET_A_MEETING_SUMMARY` | `meetingId` |
| List webinars | `ZOOM_LIST_WEBINARS` | `userId`, `type` |
| Get webinar | `ZOOM_GET_A_WEBINAR` | webinar ID |
| Register for meeting | `ZOOM_ADD_A_MEETING_REGISTRANT` | `meetingId`, participant details |
| Register for webinar | `ZOOM_ADD_A_WEBINAR_REGISTRANT` | webinar ID, participant details |
| List archived files | `ZOOM_LIST_ARCHIVED_FILES` | `from`, `to` |

---
*Powered by [Composio](https://composio.dev)*
