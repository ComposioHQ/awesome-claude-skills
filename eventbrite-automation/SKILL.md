---
name: Eventbrite Automation
description: "Automate Eventbrite event management, attendee tracking, organization discovery, and category browsing through natural language commands"
requires:
  mcp:
    - rube
---

# Eventbrite Automation

Automate Eventbrite event management workflows -- list organization events, track attendees, browse categories and formats, and manage organizations -- all through natural language.

**Toolkit docs:** [composio.dev/toolkits/eventbrite](https://composio.dev/toolkits/eventbrite)

---

## Setup

1. Add the Rube MCP server to your environment: `https://rube.app/mcp`
2. Connect your Eventbrite account when prompted (OAuth flow via Composio)
3. Start issuing natural language commands for Eventbrite automation

---

## Core Workflows

### 1. Discover Your Organizations

Retrieve the organizations the authenticated user belongs to. This is a prerequisite for most other Eventbrite operations since `organization_id` is required.

**Tool:** `EVENTBRITE_LIST_USER_ORGANIZATIONS`

No parameters required. Returns organization IDs, names, and metadata.

> Always call this first to obtain the `organization_id` needed by event and attendee endpoints.

Example prompt:
> "List my Eventbrite organizations"

---

### 2. List and Search Organization Events

Browse events owned by a specific organization with filtering by status, time period, and pagination.

**Tool:** `EVENTBRITE_LIST_ORGANIZATION_EVENTS`

Key parameters:
- `organization_id` -- the organization whose events to list (required; get from `EVENTBRITE_LIST_USER_ORGANIZATIONS`)
- `status` -- filter by `live`, `draft`, `canceled`, `started`, `ended`, `completed`, or `all`
- `time_filter` -- filter by `current_future` or `past`
- `order_by` -- sort by `start_asc`, `start_desc`, `created_asc`, `created_desc`, `name_asc`, `name_desc`
- `page_size` -- number of events per page
- `continuation` -- pagination token from previous response
- `expand` -- comma-separated fields to expand: `organizer`, `venue`, `ticket_classes`

Example prompt:
> "Show me all live events for my organization, sorted by start date"

---

### 3. Track Event Attendees

Retrieve the attendee list for any event, with optional status filtering and pagination.

**Tool:** `EVENTBRITE_LIST_EVENT_ATTENDEES`

Key parameters:
- `event_id` -- the event to retrieve attendees for (required)
- `status` -- filter by `attending`, `not_attending`, or `cancelled`
- `changed_since` -- ISO 8601 timestamp to get only recently changed attendees
- `continuation` -- pagination token for subsequent pages

Example prompt:
> "Get all attending attendees for event 123456789 who changed since January 1st"

---

### 4. Browse Event Categories

Retrieve available event categories for use when creating or filtering events.

**Tool:** `EVENTBRITE_GET_EVENT_CATEGORIES`

Key parameters:
- `locale` -- BCP-47 locale for localized names (e.g., `en_US`, `es_ES`)

Follow up with `EVENTBRITE_GET_EVENT_SUBCATEGORIES` to get subcategories within a selected category.

Example prompt:
> "List all Eventbrite event categories in English"

---

### 5. List Event Formats

Retrieve all available event format types (conference, seminar, workshop, etc.).

**Tool:** `EVENTBRITE_GET_EVENT_FORMATS`

No parameters required. Returns format IDs and display names.

Example prompt:
> "What event formats are available on Eventbrite?"

---

### 6. Browse Event Subcategories

Retrieve subcategories for more granular event classification.

**Tool:** `EVENTBRITE_GET_EVENT_SUBCATEGORIES`

Key parameters:
- `locale` -- BCP-47 locale for localized names (e.g., `en_US`)

Example prompt:
> "List all Eventbrite event subcategories"

---

## Known Pitfalls

| Pitfall | Details |
|---------|---------|
| Organization ID required | Most event operations require `organization_id` -- always call `EVENTBRITE_LIST_USER_ORGANIZATIONS` first |
| Pagination via continuation | Results use continuation-token pagination, not page numbers -- pass the `continuation` value from the previous response to get the next page |
| Event ID discovery | You need to list events first via `EVENTBRITE_LIST_ORGANIZATION_EVENTS` to get `event_id` values for attendee queries |
| Status values are specific | Event status values (`live`, `draft`, `canceled`, `started`, `ended`, `completed`) must match exactly |
| Expand fields are comma-separated | The `expand` parameter takes a comma-separated string, not an array (e.g., `"organizer,venue"`) |
| changed_since format | The `changed_since` parameter must be in ISO 8601 format (e.g., `2024-01-01T00:00:00Z`) |

---

## Quick Reference

| Action | Tool Slug | Key Params |
|--------|-----------|------------|
| List organizations | `EVENTBRITE_LIST_USER_ORGANIZATIONS` | (none) |
| List events | `EVENTBRITE_LIST_ORGANIZATION_EVENTS` | `organization_id`, `status`, `time_filter` |
| List attendees | `EVENTBRITE_LIST_EVENT_ATTENDEES` | `event_id`, `status`, `changed_since` |
| Get categories | `EVENTBRITE_GET_EVENT_CATEGORIES` | `locale` |
| Get subcategories | `EVENTBRITE_GET_EVENT_SUBCATEGORIES` | `locale` |
| Get formats | `EVENTBRITE_GET_EVENT_FORMATS` | (none) |

---

*Powered by [Composio](https://composio.dev)*
