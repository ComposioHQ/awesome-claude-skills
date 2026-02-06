---
name: convertkit-automation
description: "Automate ConvertKit (Kit) tasks via Rube MCP (Composio): manage subscribers, tags, broadcasts, and broadcast stats. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# ConvertKit (Kit) Automation via Rube MCP

Automate ConvertKit (now known as Kit) email marketing operations through Composio's Kit toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Kit connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `kit`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `kit`
3. If connection is not ACTIVE, follow the returned auth link to complete Kit authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List and Search Subscribers

**When to use**: User wants to browse, search, or filter email subscribers

**Tool sequence**:
1. `KIT_LIST_SUBSCRIBERS` - List subscribers with filters and pagination [Required]

**Key parameters**:
- `status`: Filter by status ('active' or 'inactive')
- `email_address`: Exact email to search for
- `created_after`/`created_before`: Date range filter (YYYY-MM-DD)
- `updated_after`/`updated_before`: Date range filter (YYYY-MM-DD)
- `sort_field`: Sort by 'id', 'cancelled_at', or 'updated_at'
- `sort_order`: 'asc' or 'desc'
- `per_page`: Results per page (min 1)
- `after`/`before`: Cursor strings for pagination
- `include_total_count`: Set to 'true' to get total subscriber count

**Pitfalls**:
- If `sort_field` is 'cancelled_at', the `status` must be set to 'cancelled'
- Date filters use YYYY-MM-DD format (no time component)
- `email_address` is an exact match; partial email search is not supported
- Pagination uses cursor-based approach with `after`/`before` cursor strings
- `include_total_count` is a string 'true', not a boolean

### 2. Manage Subscriber Tags

**When to use**: User wants to tag subscribers for segmentation

**Tool sequence**:
1. `KIT_LIST_SUBSCRIBERS` - Find subscriber ID by email [Prerequisite]
2. `KIT_TAG_SUBSCRIBER` - Associate a subscriber with a tag [Required]
3. `KIT_LIST_TAG_SUBSCRIBERS` - List subscribers for a specific tag [Optional]

**Key parameters for tagging**:
- `tag_id`: Numeric tag ID (required)
- `subscriber_id`: Numeric subscriber ID (required)

**Pitfalls**:
- Both `tag_id` and `subscriber_id` must be positive integers
- Tag IDs must reference existing tags; tags are created via the Kit web UI
- Tagging an already-tagged subscriber is idempotent (no error)
- Subscriber IDs are returned from LIST_SUBSCRIBERS; use `email_address` filter to find specific subscribers

### 3. Unsubscribe a Subscriber

**When to use**: User wants to unsubscribe a subscriber from all communications

**Tool sequence**:
1. `KIT_LIST_SUBSCRIBERS` - Find subscriber ID [Prerequisite]
2. `KIT_DELETE_SUBSCRIBER` - Unsubscribe the subscriber [Required]

**Key parameters**:
- `id`: Subscriber ID (required, positive integer)

**Pitfalls**:
- This permanently unsubscribes the subscriber from ALL email communications
- The subscriber's historical data is retained but they will no longer receive emails
- Operation is idempotent; unsubscribing an already-unsubscribed subscriber succeeds without error
- Returns empty response (HTTP 204 No Content) on success
- Subscriber ID must exist; non-existent IDs return 404

### 4. List and View Broadcasts

**When to use**: User wants to browse email broadcasts or get details of a specific one

**Tool sequence**:
1. `KIT_LIST_BROADCASTS` - List all broadcasts with pagination [Required]
2. `KIT_GET_BROADCAST` - Get detailed information for a specific broadcast [Optional]
3. `KIT_GET_BROADCAST_STATS` - Get performance statistics for a broadcast [Optional]

**Key parameters for listing**:
- `per_page`: Results per page (1-500)
- `after`/`before`: Cursor strings for pagination
- `include_total_count`: Set to 'true' for total count

**Key parameters for details**:
- `id`: Broadcast ID (required, positive integer)

**Pitfalls**:
- `per_page` max is 500 for broadcasts
- Broadcast stats are only available for sent broadcasts
- Draft broadcasts will not have stats
- Broadcast IDs are numeric integers

### 5. Delete a Broadcast

**When to use**: User wants to permanently remove a broadcast

**Tool sequence**:
1. `KIT_LIST_BROADCASTS` - Find the broadcast to delete [Prerequisite]
2. `KIT_GET_BROADCAST` - Verify it is the correct broadcast [Optional]
3. `KIT_DELETE_BROADCAST` - Permanently delete the broadcast [Required]

**Key parameters**:
- `id`: Broadcast ID (required)

**Pitfalls**:
- Deletion is permanent and cannot be undone
- Deleting a sent broadcast removes it but does not unsend the emails
- Confirm the broadcast ID before deleting

## Common Patterns

### Subscriber Lookup by Email

```
1. Call KIT_LIST_SUBSCRIBERS with email_address='user@example.com'
2. Extract subscriber ID from the response
3. Use ID for tagging, unsubscribing, or other operations
```

### Pagination

Kit uses cursor-based pagination:
- Check response for `after` cursor value
- Pass cursor as `after` parameter in next request
- Continue until no more cursor is returned
- Use `include_total_count: 'true'` to track progress

### Tag-Based Segmentation

```
1. Create tags in Kit web UI
2. Use KIT_TAG_SUBSCRIBER to assign tags to subscribers
3. Use KIT_LIST_TAG_SUBSCRIBERS to view subscribers per tag
```

## Known Pitfalls

**ID Formats**:
- Subscriber IDs: positive integers (e.g., 3887204736)
- Tag IDs: positive integers
- Broadcast IDs: positive integers
- All IDs are numeric, not strings

**Status Values**:
- Subscriber statuses: 'active', 'inactive', 'cancelled'
- Some operations are restricted by status (e.g., sorting by cancelled_at requires status='cancelled')

**String vs Boolean Parameters**:
- `include_total_count` is a string 'true', not a boolean true
- `sort_order` is a string enum: 'asc' or 'desc'

**Rate Limits**:
- Kit API has per-account rate limits
- Implement backoff on 429 responses
- Bulk operations should be paced appropriately

**Response Parsing**:
- Response data may be nested under `data` or `data.data`
- Parse defensively with fallback patterns
- Cursor values are opaque strings; use exactly as returned

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List subscribers | KIT_LIST_SUBSCRIBERS | status, email_address, per_page |
| Tag subscriber | KIT_TAG_SUBSCRIBER | tag_id, subscriber_id |
| List tag subscribers | KIT_LIST_TAG_SUBSCRIBERS | tag_id |
| Unsubscribe | KIT_DELETE_SUBSCRIBER | id |
| List broadcasts | KIT_LIST_BROADCASTS | per_page, after |
| Get broadcast | KIT_GET_BROADCAST | id |
| Get broadcast stats | KIT_GET_BROADCAST_STATS | id |
| Delete broadcast | KIT_DELETE_BROADCAST | id |
