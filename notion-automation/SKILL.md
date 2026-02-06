---
name: notion-automation
description: "Automate Notion tasks via Rube MCP (Composio): pages, databases, blocks, comments, users. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Notion Automation via Rube MCP

Automate Notion operations through Composio's Notion toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Notion connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `notion`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `notion`
3. If connection is not ACTIVE, follow the returned auth link to complete Notion OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create and Manage Pages

**When to use**: User wants to create, update, or archive Notion pages

**Tool sequence**:
1. `NOTION_SEARCH_NOTION_PAGE` - Find parent page or existing page [Prerequisite]
2. `NOTION_CREATE_NOTION_PAGE` - Create a new page under a parent [Optional]
3. `NOTION_RETRIEVE_PAGE` - Get page metadata/properties [Optional]
4. `NOTION_UPDATE_PAGE` - Update page properties, title, icon, cover [Optional]
5. `NOTION_ARCHIVE_NOTION_PAGE` - Soft-delete (archive) a page [Optional]

**Key parameters**:
- `query`: Search text for SEARCH_NOTION_PAGE
- `parent_id`: Parent page or database ID
- `page_id`: Page ID for retrieval/update/archive
- `properties`: Page property values matching parent schema

**Pitfalls**:
- RETRIEVE_PAGE returns only metadata/properties, NOT body content; use FETCH_BLOCK_CONTENTS for page body
- ARCHIVE_NOTION_PAGE is a soft-delete (sets archived=true), not permanent deletion
- Broad searches can look incomplete unless has_more/next_cursor is fully paginated

### 2. Query and Manage Databases

**When to use**: User wants to query database rows, insert entries, or update records

**Tool sequence**:
1. `NOTION_SEARCH_NOTION_PAGE` - Find the database by name [Prerequisite]
2. `NOTION_FETCH_DATABASE` - Inspect schema and properties [Prerequisite]
3. `NOTION_QUERY_DATABASE` / `NOTION_QUERY_DATABASE_WITH_FILTER` - Query rows [Required]
4. `NOTION_INSERT_ROW_DATABASE` - Add new entries [Optional]
5. `NOTION_UPDATE_ROW_DATABASE` - Update existing entries [Optional]

**Key parameters**:
- `database_id`: Database ID (from search or URL)
- `filter`: Filter object matching Notion filter syntax
- `sorts`: Array of sort objects
- `start_cursor`: Pagination cursor from previous response
- `properties`: Property values matching database schema for inserts/updates

**Pitfalls**:
- 404 object_not_found usually means wrong database_id or the database is not shared with the integration
- Results are paginated; ignoring has_more/next_cursor silently truncates reads
- Schema mismatches or missing required properties cause 400 validation_error
- Formula and read-only fields cannot be set via INSERT_ROW_DATABASE
- Property names in filters must match schema exactly (case-sensitive)

### 3. Manage Blocks and Page Content

**When to use**: User wants to read, append, or modify content blocks in a page

**Tool sequence**:
1. `NOTION_FETCH_BLOCK_CONTENTS` - Read child blocks of a page [Required]
2. `NOTION_ADD_MULTIPLE_PAGE_CONTENT` - Append blocks to a page [Optional]
3. `NOTION_APPEND_TEXT_BLOCKS` - Append text-only blocks [Optional]
4. `NOTION_REPLACE_PAGE_CONTENT` - Replace all page content [Optional]
5. `NOTION_DELETE_BLOCK` - Remove a specific block [Optional]

**Key parameters**:
- `block_id` / `page_id`: Target page or block ID
- `content_blocks`: Array of block objects (NOT child_blocks)
- `text`: Plain text content for APPEND_TEXT_BLOCKS

**Pitfalls**:
- Use `content_blocks` parameter, NOT `child_blocks` -- the latter fails validation
- ADD_MULTIPLE_PAGE_CONTENT fails on archived pages; unarchive via UPDATE_PAGE first
- Created blocks are in response.data.results; persist block IDs for later edits
- DELETE_BLOCK is archival (archived=true), not permanent deletion

### 4. Manage Database Schema

**When to use**: User wants to create databases or modify their structure

**Tool sequence**:
1. `NOTION_FETCH_DATABASE` - Inspect current schema [Prerequisite]
2. `NOTION_CREATE_DATABASE` - Create a new database [Optional]
3. `NOTION_UPDATE_SCHEMA_DATABASE` - Modify database properties [Optional]

**Key parameters**:
- `parent_id`: Parent page ID for new databases
- `title`: Database title
- `properties`: Property definitions with types and options
- `database_id`: Database ID for schema updates

**Pitfalls**:
- Cannot change property types via UPDATE_SCHEMA; must create new property and migrate data
- Formula, rollup, and relation properties have complex configuration requirements

### 5. Manage Users and Comments

**When to use**: User wants to list workspace users or manage comments on pages

**Tool sequence**:
1. `NOTION_LIST_USERS` - List all workspace users [Optional]
2. `NOTION_GET_ABOUT_ME` - Get current authenticated user [Optional]
3. `NOTION_CREATE_COMMENT` - Add a comment to a page [Optional]
4. `NOTION_FETCH_COMMENTS` - List comments on a page [Optional]

**Key parameters**:
- `page_id`: Page ID for comments (also called `discussion_id`)
- `rich_text`: Comment content as rich text array

**Pitfalls**:
- Comments are linked to pages, not individual blocks
- User IDs from LIST_USERS are needed for people-type property filters

## Common Patterns

### ID Resolution

**Page/Database name -> ID**:
```
1. Call NOTION_SEARCH_NOTION_PAGE with query=name
2. Paginate with has_more/next_cursor until found
3. Extract id from matching result
```

**Database schema inspection**:
```
1. Call NOTION_FETCH_DATABASE with database_id
2. Extract properties object for field names and types
3. Use exact property names in queries and inserts
```

### Pagination

- Set `page_size` for results per page (max 100)
- Check response for `has_more` boolean
- Pass `start_cursor` or `next_cursor` in next request
- Continue until `has_more` is false

### Notion Filter Syntax

**Single filter**:
```json
{"property": "Status", "select": {"equals": "Done"}}
```

**Compound filter**:
```json
{"and": [
  {"property": "Status", "select": {"equals": "In Progress"}},
  {"property": "Assignee", "people": {"contains": "user-id"}}
]}
```

## Known Pitfalls

**Integration Sharing**:
- Pages and databases must be shared with the Notion integration to be accessible
- Title queries can return 0 when the item is not shared with the integration

**Property Types**:
- Property names are case-sensitive and must match schema exactly
- Formula, rollup, and created_time fields are read-only
- Select/multi-select values must match existing options unless creating new ones

**Response Parsing**:
- Response data may be nested under `data_preview` or `data.results`
- Parse defensively with fallbacks for different nesting levels

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Search pages/databases | NOTION_SEARCH_NOTION_PAGE | query |
| Create page | NOTION_CREATE_NOTION_PAGE | parent_id, properties |
| Get page metadata | NOTION_RETRIEVE_PAGE | page_id |
| Update page | NOTION_UPDATE_PAGE | page_id, properties |
| Archive page | NOTION_ARCHIVE_NOTION_PAGE | page_id |
| Duplicate page | NOTION_DUPLICATE_PAGE | page_id |
| Get page blocks | NOTION_FETCH_BLOCK_CONTENTS | block_id |
| Append blocks | NOTION_ADD_MULTIPLE_PAGE_CONTENT | page_id, content_blocks |
| Append text | NOTION_APPEND_TEXT_BLOCKS | page_id, text |
| Replace content | NOTION_REPLACE_PAGE_CONTENT | page_id, content_blocks |
| Delete block | NOTION_DELETE_BLOCK | block_id |
| Query database | NOTION_QUERY_DATABASE | database_id, filter, sorts |
| Query with filter | NOTION_QUERY_DATABASE_WITH_FILTER | database_id, filter |
| Insert row | NOTION_INSERT_ROW_DATABASE | database_id, properties |
| Update row | NOTION_UPDATE_ROW_DATABASE | page_id, properties |
| Get database schema | NOTION_FETCH_DATABASE | database_id |
| Create database | NOTION_CREATE_DATABASE | parent_id, title, properties |
| Update schema | NOTION_UPDATE_SCHEMA_DATABASE | database_id, properties |
| List users | NOTION_LIST_USERS | (none) |
| Create comment | NOTION_CREATE_COMMENT | page_id, rich_text |
| List comments | NOTION_FETCH_COMMENTS | page_id |
