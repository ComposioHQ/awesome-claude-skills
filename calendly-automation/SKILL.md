---
name: calendly-automation
description: Automate Calendly scheduling, event management, invitee tracking, availability checks, and organization administration via Rube MCP (Composio). Always search tools first for current schemas.
requires:
  mcp: [rube]
---

# Calendly Automation via Rube MCP

Automate Calendly operations including event listing, invitee management, scheduling link creation, availability queries, and organization administration through Composio's Calendly toolkit.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Calendly connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `calendly`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas
- Many operations require the user's Calendly URI, obtained via `CALENDLY_GET_CURRENT_USER`

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `calendly`
3. If connection is not ACTIVE, follow the returned auth link to complete Calendly OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List and View Scheduled Events

**When to use**: User wants to see their upcoming, past, or filtered Calendly events

**Tool sequence**:
1. `CALENDLY_GET_CURRENT_USER` - Get authenticated user URI and organization URI [Prerequisite]
2. `CALENDLY_LIST_EVENTS` - List events scoped by user, organization, or group [Required]
3. `CALENDLY_GET_EVENT` - Get detailed info for a specific event by UUID [Optional]

**Key parameters**:
- `user`: Full Calendly API URI (e.g., `https://api.calendly.com/users/{uuid}`) - NOT `"me"`
- `organization`: Full organization URI for org-scoped queries
- `status`: `"active"` or `"canceled"`
- `min_start_time` / `max_start_time`: UTC timestamps (e.g., `2024-01-01T00:00:00.000000Z`)
- `invitee_email`: Filter events by invitee email (filter only, not a scope)
- `sort`: `"start_time:asc"` or `"start_time:desc"`
- `count`: Results per page (default 20)
- `page_token`: Pagination token from previous response

**Pitfalls**:
- Exactly ONE of `user`, `organization`, or `group` must be provided - omitting or combining scopes fails
- The `user` parameter requires the full API URI, not `"me"` - use `CALENDLY_GET_CURRENT_USER` first
- `invitee_email` is a filter, not a scope; you still need one of user/organization/group
- Pagination uses `count` + `page_token`; loop until `page_token` is absent for complete results
- Admin rights may be needed for organization or group scope queries

### 2. Manage Event Invitees

**When to use**: User wants to see who is booked for events or get invitee details

**Tool sequence**:
1. `CALENDLY_LIST_EVENTS` - Find the target event(s) [Prerequisite]
2. `CALENDLY_LIST_EVENT_INVITEES` - List all invitees for a specific event [Required]
3. `CALENDLY_GET_EVENT_INVITEE` - Get detailed info for a single invitee [Optional]

**Key parameters**:
- `uuid`: Event UUID (for `LIST_EVENT_INVITEES`)
- `event_uuid` + `invitee_uuid`: Both required for `GET_EVENT_INVITEE`
- `email`: Filter invitees by email address
- `status`: `"active"` or `"canceled"`
- `sort`: `"created_at:asc"` or `"created_at:desc"`
- `count`: Results per page (default 20)

**Pitfalls**:
- The `uuid` parameter for `CALENDLY_LIST_EVENT_INVITEES` is the event UUID, not the invitee UUID
- Paginate using `page_token` until absent for complete invitee lists
- Canceled invitees are excluded by default; use `status: "canceled"` to see them

### 3. Create Scheduling Links and Check Availability

**When to use**: User wants to generate a booking link or check available time slots

**Tool sequence**:
1. `CALENDLY_GET_CURRENT_USER` - Get user URI [Prerequisite]
2. `CALENDLY_LIST_USER_S_EVENT_TYPES` - List available event types [Required]
3. `CALENDLY_LIST_EVENT_TYPE_AVAILABLE_TIMES` - Check available slots for an event type [Optional]
4. `CALENDLY_CREATE_SCHEDULING_LINK` - Generate a single-use scheduling link [Required]
5. `CALENDLY_LIST_USER_AVAILABILITY_SCHEDULES` - View user's availability schedules [Optional]

**Key parameters**:
- `owner`: Event type URI (e.g., `https://api.calendly.com/event_types/{uuid}`)
- `owner_type`: `"EventType"` (default)
- `max_event_count`: Must be exactly `1` for single-use links
- `start_time` / `end_time`: UTC timestamps for availability queries (max 7-day range)
- `active`: Boolean to filter active/inactive event types
- `user`: User URI for event type listing

**Pitfalls**:
- `CALENDLY_CREATE_SCHEDULING_LINK` can return 403 if token lacks rights or owner URI is invalid
- `CALENDLY_LIST_EVENT_TYPE_AVAILABLE_TIMES` requires UTC timestamps and max 7-day range; split longer searches
- Available times results are NOT paginated - all results returned in one response
- Event type URIs must be full API URIs (e.g., `https://api.calendly.com/event_types/...`)

### 4. Cancel Events

**When to use**: User wants to cancel a scheduled Calendly event

**Tool sequence**:
1. `CALENDLY_LIST_EVENTS` - Find the event to cancel [Prerequisite]
2. `CALENDLY_GET_EVENT` - Confirm event details before cancellation [Prerequisite]
3. `CALENDLY_LIST_EVENT_INVITEES` - Check who will be affected [Optional]
4. `CALENDLY_CANCEL_EVENT` - Cancel the event [Required]

**Key parameters**:
- `uuid`: Event UUID to cancel
- `reason`: Optional cancellation reason (may be included in notification to invitees)

**Pitfalls**:
- Cancellation is IRREVERSIBLE - always confirm with the user before calling
- Cancellation may trigger notifications to invitees
- Only active events can be canceled; already-canceled events return errors
- Get explicit user confirmation before executing `CALENDLY_CANCEL_EVENT`

### 5. Manage Organization and Invitations

**When to use**: User wants to invite members, manage organization, or handle org invitations

**Tool sequence**:
1. `CALENDLY_GET_CURRENT_USER` - Get user and organization context [Prerequisite]
2. `CALENDLY_GET_ORGANIZATION` - Get organization details [Optional]
3. `CALENDLY_LIST_ORGANIZATION_INVITATIONS` - Check existing invitations [Optional]
4. `CALENDLY_CREATE_ORGANIZATION_INVITATION` - Send an org invitation [Required]
5. `CALENDLY_REVOKE_USER_S_ORGANIZATION_INVITATION` - Revoke a pending invitation [Optional]
6. `CALENDLY_REMOVE_USER_FROM_ORGANIZATION` - Remove a member [Optional]

**Key parameters**:
- `uuid`: Organization UUID
- `email`: Email address of user to invite
- `status`: Filter invitations by `"pending"`, `"accepted"`, or `"declined"`

**Pitfalls**:
- Only org owners/admins can manage invitations and removals; others get authorization errors
- Duplicate active invitations for the same email are rejected - check existing invitations first
- Organization owners cannot be removed via `CALENDLY_REMOVE_USER_FROM_ORGANIZATION`
- Invitation statuses include pending, accepted, declined, and revoked - handle each appropriately

## Common Patterns

### ID Resolution
Calendly uses full API URIs as identifiers, not simple IDs:
- **Current user URI**: `CALENDLY_GET_CURRENT_USER` returns `resource.uri` (e.g., `https://api.calendly.com/users/{uuid}`)
- **Organization URI**: Found in current user response at `resource.current_organization`
- **Event UUID**: Extract from event URI or list responses
- **Event type URI**: From `CALENDLY_LIST_USER_S_EVENT_TYPES` response

Important: Never use `"me"` as a user parameter in list/filter endpoints. Always resolve to the full URI first.

### Pagination
Most Calendly list endpoints use token-based pagination:
- Set `count` for page size (default 20)
- Follow `page_token` from `pagination.next_page_token` until absent
- Sort with `field:direction` format (e.g., `start_time:asc`, `created_at:desc`)

### Time Handling
- All timestamps must be in UTC format: `yyyy-MM-ddTHH:mm:ss.ffffffZ`
- Use `min_start_time` / `max_start_time` for date range filtering on events
- Available times queries have a maximum 7-day range; split longer searches into multiple calls

## Known Pitfalls

### URI Formats
- All entity references use full Calendly API URIs (e.g., `https://api.calendly.com/users/{uuid}`)
- Never pass bare UUIDs where URIs are expected, and never pass `"me"` to list endpoints
- Extract UUIDs from URIs when tools expect UUID parameters (e.g., `CALENDLY_GET_EVENT`)

### Scope Requirements
- `CALENDLY_LIST_EVENTS` requires exactly one scope (user, organization, or group) - no more, no less
- Organization/group scoped queries may require admin privileges
- Token scope determines which operations are available; 403 errors indicate insufficient permissions

### Data Relationships
- Events have invitees (attendees who booked)
- Event types define scheduling pages (duration, availability rules)
- Organizations contain users and groups
- Scheduling links are tied to event types, not directly to events

### Rate Limits
- Calendly API has rate limits; avoid tight loops over large datasets
- Paginate responsibly and add delays for batch operations

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Get current user | `CALENDLY_GET_CURRENT_USER` | (none) |
| Get user by UUID | `CALENDLY_GET_USER` | `uuid` |
| List events | `CALENDLY_LIST_EVENTS` | `user`, `status`, `min_start_time` |
| Get event details | `CALENDLY_GET_EVENT` | `uuid` |
| Cancel event | `CALENDLY_CANCEL_EVENT` | `uuid`, `reason` |
| List invitees | `CALENDLY_LIST_EVENT_INVITEES` | `uuid`, `status`, `email` |
| Get invitee | `CALENDLY_GET_EVENT_INVITEE` | `event_uuid`, `invitee_uuid` |
| List event types | `CALENDLY_LIST_USER_S_EVENT_TYPES` | `user`, `active` |
| Get event type | `CALENDLY_GET_EVENT_TYPE` | `uuid` |
| Check availability | `CALENDLY_LIST_EVENT_TYPE_AVAILABLE_TIMES` | event type URI, `start_time`, `end_time` |
| Create scheduling link | `CALENDLY_CREATE_SCHEDULING_LINK` | `owner`, `max_event_count` |
| List availability schedules | `CALENDLY_LIST_USER_AVAILABILITY_SCHEDULES` | user URI |
| Get organization | `CALENDLY_GET_ORGANIZATION` | `uuid` |
| Invite to org | `CALENDLY_CREATE_ORGANIZATION_INVITATION` | `uuid`, `email` |
| List org invitations | `CALENDLY_LIST_ORGANIZATION_INVITATIONS` | `uuid`, `status` |
| Revoke org invitation | `CALENDLY_REVOKE_USER_S_ORGANIZATION_INVITATION` | org UUID, invitation UUID |
| Remove from org | `CALENDLY_REMOVE_USER_FROM_ORGANIZATION` | membership UUID |
