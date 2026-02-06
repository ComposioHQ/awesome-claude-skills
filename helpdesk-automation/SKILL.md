---
name: helpdesk-automation
description: "Automate HelpDesk tasks via Rube MCP (Composio): list tickets, manage views, use canned responses, and configure custom fields. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# HelpDesk Automation via Rube MCP

Automate HelpDesk ticketing operations through Composio's HelpDesk toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active HelpDesk connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `helpdesk`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `helpdesk`
3. If connection is not ACTIVE, follow the returned auth link to complete HelpDesk authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List and Browse Tickets

**When to use**: User wants to retrieve, browse, or paginate through support tickets

**Tool sequence**:
1. `HELPDESK_LIST_TICKETS` - List tickets with sorting and pagination [Required]

**Key parameters**:
- `silo`: Ticket folder - 'tickets', 'archive', 'trash', or 'spam' (default: 'tickets')
- `sortBy`: Sort field - 'createdAt', 'updatedAt', or 'lastMessageAt' (default: 'createdAt')
- `order`: Sort direction - 'asc' or 'desc' (default: 'desc')
- `pageSize`: Results per page, 1-100 (default: 20)
- `next.value`: Timestamp cursor for forward pagination
- `next.ID`: ID cursor for forward pagination
- `prev.value`: Timestamp cursor for backward pagination
- `prev.ID`: ID cursor for backward pagination

**Pitfalls**:
- Pagination uses cursor-based approach with timestamp + ID pairs
- Forward pagination requires both `next.value` and `next.ID` from previous response
- Backward pagination requires both `prev.value` and `prev.ID`
- `silo` determines which folder to list from; default is active tickets
- `pageSize` max is 100; default is 20
- Archived and trashed tickets are in separate silos

### 2. Manage Ticket Views

**When to use**: User wants to see saved agent views for organizing tickets

**Tool sequence**:
1. `HELPDESK_LIST_VIEWS` - List all agent views [Required]

**Key parameters**: (none required)

**Pitfalls**:
- Views are predefined saved filters configured by agents in the HelpDesk UI
- View definitions include filter criteria that can be used to understand ticket organization
- Views cannot be created or modified via API; they are managed in the HelpDesk UI

### 3. Use Canned Responses

**When to use**: User wants to list available canned (template) responses for tickets

**Tool sequence**:
1. `HELPDESK_LIST_CANNED_RESPONSES` - Retrieve all predefined reply templates [Required]

**Key parameters**: (none required)

**Pitfalls**:
- Canned responses are predefined templates for common replies
- They may include placeholder variables that need to be filled in
- Canned responses are managed through the HelpDesk UI
- Response content may include HTML formatting

### 4. Inspect Custom Fields

**When to use**: User wants to view custom field definitions for the account

**Tool sequence**:
1. `HELPDESK_LIST_CUSTOM_FIELDS` - List all custom field definitions [Required]

**Key parameters**: (none required)

**Pitfalls**:
- Custom fields extend the default ticket schema with organization-specific data
- Field definitions include field type, name, and validation rules
- Custom fields are configured in the HelpDesk admin panel
- Field values appear on tickets when the field has been populated

## Common Patterns

### Ticket Browsing Pattern

```
1. Call HELPDESK_LIST_TICKETS with desired silo and sortBy
2. Process the returned page of tickets
3. Extract next.value and next.ID from the response
4. Call HELPDESK_LIST_TICKETS with those cursor values for next page
5. Continue until no more cursor values are returned
```

### Ticket Folder Navigation

```
Active tickets:  silo='tickets'
Archived:        silo='archive'
Trashed:         silo='trash'
Spam:            silo='spam'
```

### Cursor-Based Pagination

```
Forward pagination:
  - Use next.value (timestamp) and next.ID from response
  - Pass as next.value and next.ID parameters in next call

Backward pagination:
  - Use prev.value (timestamp) and prev.ID from response
  - Pass as prev.value and prev.ID parameters in next call
```

## Known Pitfalls

**Cursor Pagination**:
- Both timestamp and ID are required for cursor navigation
- Cursor values are timestamps in ISO 8601 date-time format
- Mixing forward and backward cursors in the same request is undefined behavior

**Silo Filtering**:
- Tickets are physically separated into silos (folders)
- Moving tickets between silos is done in the HelpDesk UI
- Each silo query is independent; there is no cross-silo search

**Read-Only Operations**:
- Current Composio toolkit provides list/read operations
- Ticket creation, update, and reply operations may require additional tools
- Check RUBE_SEARCH_TOOLS for any newly available tools

**Rate Limits**:
- HelpDesk API has per-account rate limits
- Implement backoff on 429 responses
- Keep page sizes reasonable to avoid timeouts

**Response Parsing**:
- Response data may be nested under `data` or `data.data`
- Parse defensively with fallback patterns
- Ticket IDs are strings

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List tickets | HELPDESK_LIST_TICKETS | silo, sortBy, order, pageSize |
| List views | HELPDESK_LIST_VIEWS | (none) |
| List canned responses | HELPDESK_LIST_CANNED_RESPONSES | (none) |
| List custom fields | HELPDESK_LIST_CUSTOM_FIELDS | (none) |
