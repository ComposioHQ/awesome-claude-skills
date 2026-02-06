---
name: zendesk-automation
description: "Automate Zendesk tasks via Rube MCP (Composio): tickets, users, organizations, replies. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Zendesk Automation via Rube MCP

Automate Zendesk operations through Composio's Zendesk toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Zendesk connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `zendesk`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `zendesk`
3. If connection is not ACTIVE, follow the returned auth link to complete Zendesk auth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List and Search Tickets

**When to use**: User wants to view, filter, or search support tickets

**Tool sequence**:
1. `ZENDESK_LIST_ZENDESK_TICKETS` - List all tickets with pagination [Required]
2. `ZENDESK_GET_ZENDESK_TICKET_BY_ID` - Get specific ticket details [Optional]

**Key parameters**:
- `page`: Page number (1-based)
- `per_page`: Results per page (max 100)
- `sort_by`: Sort field ('created_at', 'updated_at', 'priority', 'status')
- `sort_order`: 'asc' or 'desc'
- `ticket_id`: Ticket ID for single retrieval

**Pitfalls**:
- LIST uses `page`/`per_page` pagination, NOT offset-based; check `next_page` in response
- Maximum 100 results per page; iterate with page numbers until `next_page` is null
- Deleted tickets are not returned by LIST; use GET_BY_ID which returns status 'deleted'
- Ticket comments and audits are included in GET_BY_ID but not in LIST responses

### 2. Create and Update Tickets

**When to use**: User wants to create new tickets or modify existing ones

**Tool sequence**:
1. `ZENDESK_SEARCH_ZENDESK_USERS` - Find requester/assignee [Prerequisite]
2. `ZENDESK_CREATE_ZENDESK_TICKET` - Create a new ticket [Required]
3. `ZENDESK_UPDATE_ZENDESK_TICKET` - Update ticket fields [Optional]
4. `ZENDESK_DELETE_ZENDESK_TICKET` - Delete a ticket [Optional]

**Key parameters**:
- `subject`: Ticket subject line
- `description`: Ticket body (for creation; becomes first comment)
- `priority`: 'urgent', 'high', 'normal', 'low'
- `status`: 'new', 'open', 'pending', 'hold', 'solved', 'closed'
- `type`: 'problem', 'incident', 'question', 'task'
- `assignee_id`: Agent user ID to assign
- `requester_id`: Requester user ID
- `tags`: Array of tag strings
- `ticket_id`: Ticket ID (for update/delete)

**Pitfalls**:
- Tags on UPDATE REPLACE existing tags entirely; merge with current tags to preserve them
- Use `safe_update` with `updated_stamp` to prevent concurrent modification conflicts
- DELETE is permanent and irreversible; tickets cannot be recovered
- `description` is only used on creation; use REPLY_ZENDESK_TICKET to add comments after creation
- Closed tickets cannot be updated; create a follow-up ticket instead

### 3. Reply to Tickets

**When to use**: User wants to add comments or replies to tickets

**Tool sequence**:
1. `ZENDESK_GET_ZENDESK_TICKET_BY_ID` - Get current ticket state [Prerequisite]
2. `ZENDESK_REPLY_ZENDESK_TICKET` - Add a reply/comment [Required]

**Key parameters**:
- `ticket_id`: Ticket ID to reply to
- `body`: Reply text content
- `public`: Boolean; true for public reply, false for internal note
- `author_id`: Author user ID (defaults to authenticated user)

**Pitfalls**:
- Set `public: false` for internal notes visible only to agents
- Default is public reply which sends email to requester
- HTML is supported in body text
- Replying can also update ticket status simultaneously

### 4. Manage Users

**When to use**: User wants to find or create Zendesk users (agents, end-users)

**Tool sequence**:
1. `ZENDESK_SEARCH_ZENDESK_USERS` - Search for users [Required]
2. `ZENDESK_CREATE_ZENDESK_USER` - Create a new user [Optional]
3. `ZENDESK_GET_ABOUT_ME` - Get authenticated user info [Optional]

**Key parameters**:
- `query`: Search string (matches name, email, phone, etc.)
- `name`: User's full name (required for creation)
- `email`: User's email address
- `role`: 'end-user', 'agent', or 'admin'
- `verified`: Whether email is verified

**Pitfalls**:
- User search is fuzzy; may return partial matches
- Creating a user with an existing email returns the existing user (upsert behavior)
- Agent and admin roles may require specific plan features

### 5. Manage Organizations

**When to use**: User wants to list, create, or manage organizations

**Tool sequence**:
1. `ZENDESK_GET_ALL_ZENDESK_ORGANIZATIONS` - List all organizations [Required]
2. `ZENDESK_GET_ZENDESK_ORGANIZATION` - Get specific organization [Optional]
3. `ZENDESK_CREATE_ZENDESK_ORGANIZATION` - Create organization [Optional]
4. `ZENDESK_UPDATE_ZENDESK_ORGANIZATION` - Update organization [Optional]
5. `ZENDESK_COUNT_ZENDESK_ORGANIZATIONS` - Get total count [Optional]

**Key parameters**:
- `name`: Organization name (unique, required for creation)
- `organization_id`: Organization ID for get/update
- `details`: Organization details text
- `notes`: Internal notes
- `domain_names`: Array of associated domains
- `tags`: Array of tag strings

**Pitfalls**:
- Organization names must be unique; duplicate names cause creation errors
- Tags on UPDATE REPLACE existing tags (same behavior as tickets)
- Domain names can be used for automatic user association

## Common Patterns

### Pagination

**List endpoints**:
- Use `page` (1-based) and `per_page` (max 100)
- Check `next_page` URL in response; null means last page
- `count` field gives total results

### Ticket Lifecycle

```
new -> open -> pending -> solved -> closed
                  |          ^
                  v          |
                hold --------+
```

- `new`: Unassigned ticket
- `open`: Assigned, being worked on
- `pending`: Waiting for customer response
- `hold`: Waiting for internal action
- `solved`: Resolved, can be reopened
- `closed`: Permanently closed, cannot be modified

### User Search for Assignment

```
1. Call ZENDESK_SEARCH_ZENDESK_USERS with query (name or email)
2. Extract user ID from results
3. Use user ID as assignee_id in ticket creation/update
```

## Known Pitfalls

**Tags Behavior**:
- Tags on update REPLACE all existing tags
- Always fetch current tags first and merge before updating
- Tags are lowercase, no spaces (use underscores)

**Safe Updates**:
- Use `safe_update: true` with `updated_stamp` (ISO 8601) to prevent conflicts
- Returns 409 if ticket was modified since the stamp

**Deletion**:
- Ticket deletion is permanent and irreversible
- Consider setting status to 'closed' instead of deleting
- Deleted tickets cannot be recovered via API

**Rate Limits**:
- Default: 400 requests per minute
- Varies by plan tier
- 429 responses include Retry-After header

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List tickets | ZENDESK_LIST_ZENDESK_TICKETS | page, per_page, sort_by |
| Get ticket | ZENDESK_GET_ZENDESK_TICKET_BY_ID | ticket_id |
| Create ticket | ZENDESK_CREATE_ZENDESK_TICKET | subject, description, priority |
| Update ticket | ZENDESK_UPDATE_ZENDESK_TICKET | ticket_id, status, tags |
| Reply to ticket | ZENDESK_REPLY_ZENDESK_TICKET | ticket_id, body, public |
| Delete ticket | ZENDESK_DELETE_ZENDESK_TICKET | ticket_id |
| Search users | ZENDESK_SEARCH_ZENDESK_USERS | query |
| Create user | ZENDESK_CREATE_ZENDESK_USER | name, email |
| My profile | ZENDESK_GET_ABOUT_ME | (none) |
| List orgs | ZENDESK_GET_ALL_ZENDESK_ORGANIZATIONS | page, per_page |
| Get org | ZENDESK_GET_ZENDESK_ORGANIZATION | organization_id |
| Create org | ZENDESK_CREATE_ZENDESK_ORGANIZATION | name |
| Update org | ZENDESK_UPDATE_ZENDESK_ORGANIZATION | organization_id, name |
| Count orgs | ZENDESK_COUNT_ZENDESK_ORGANIZATIONS | (none) |
