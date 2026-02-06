---
name: airtable-automation
description: "Automate Airtable tasks via Rube MCP (Composio): records, bases, tables, fields, views. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Airtable Automation via Rube MCP

Automate Airtable operations through Composio's Airtable toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Airtable connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `airtable`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `airtable`
3. If connection is not ACTIVE, follow the returned auth link to complete Airtable auth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create and Manage Records

**When to use**: User wants to create, read, update, or delete records

**Tool sequence**:
1. `AIRTABLE_LIST_BASES` - Discover available bases [Prerequisite]
2. `AIRTABLE_GET_BASE_SCHEMA` - Inspect table structure [Prerequisite]
3. `AIRTABLE_LIST_RECORDS` - List/filter records [Optional]
4. `AIRTABLE_CREATE_RECORD` / `AIRTABLE_CREATE_RECORDS` - Create records [Optional]
5. `AIRTABLE_UPDATE_RECORD` / `AIRTABLE_UPDATE_MULTIPLE_RECORDS` - Update records [Optional]
6. `AIRTABLE_DELETE_RECORD` / `AIRTABLE_DELETE_MULTIPLE_RECORDS` - Delete records [Optional]

**Key parameters**:
- `baseId`: Base ID (starts with 'app', e.g., 'appXXXXXXXXXXXXXX')
- `tableIdOrName`: Table ID (starts with 'tbl') or table name
- `fields`: Object mapping field names to values
- `recordId`: Record ID (starts with 'rec') for updates/deletes
- `filterByFormula`: Airtable formula for filtering
- `typecast`: Set true for automatic type conversion

**Pitfalls**:
- pageSize capped at 100; uses offset pagination; changing filters between pages can skip/duplicate rows
- CREATE_RECORDS hard limit of 10 records per request; chunk larger imports
- Field names are CASE-SENSITIVE and must match schema exactly
- 422 UNKNOWN_FIELD_NAME when field names are wrong; 403 for permission issues
- INVALID_MULTIPLE_CHOICE_OPTIONS may require typecast=true

### 2. Search and Filter Records

**When to use**: User wants to find specific records using formulas

**Tool sequence**:
1. `AIRTABLE_GET_BASE_SCHEMA` - Verify field names and types [Prerequisite]
2. `AIRTABLE_LIST_RECORDS` - Query with filterByFormula [Required]
3. `AIRTABLE_GET_RECORD` - Get full record details [Optional]

**Key parameters**:
- `filterByFormula`: Airtable formula (e.g., `{Status}='Done'`)
- `sort`: Array of sort objects
- `fields`: Array of field names to return
- `maxRecords`: Max total records across all pages
- `offset`: Pagination cursor from previous response

**Pitfalls**:
- Field names in formulas must be wrapped in `{}` and match schema exactly
- String values must be quoted: `{Status}='Active'` not `{Status}=Active`
- 422 INVALID_FILTER_BY_FORMULA for bad syntax or non-existent fields
- Airtable rate limit: ~5 requests/second per base; handle 429 with Retry-After

### 3. Manage Fields and Schema

**When to use**: User wants to create or modify table fields

**Tool sequence**:
1. `AIRTABLE_GET_BASE_SCHEMA` - Inspect current schema [Prerequisite]
2. `AIRTABLE_CREATE_FIELD` - Create a new field [Optional]
3. `AIRTABLE_UPDATE_FIELD` - Rename/describe a field [Optional]
4. `AIRTABLE_UPDATE_TABLE` - Update table metadata [Optional]

**Key parameters**:
- `name`: Field name
- `type`: Field type (singleLineText, number, singleSelect, etc.)
- `options`: Type-specific options (choices for select, precision for number)
- `description`: Field description

**Pitfalls**:
- UPDATE_FIELD only changes name/description, NOT type/options; create a replacement field and migrate
- Computed fields (formula, rollup, lookup) cannot be created via API
- 422 when type options are missing or malformed

### 4. Manage Comments

**When to use**: User wants to view or add comments on records

**Tool sequence**:
1. `AIRTABLE_LIST_COMMENTS` - List comments on a record [Required]

**Key parameters**:
- `baseId`: Base ID
- `tableIdOrName`: Table identifier
- `recordId`: Record ID (17 chars, starts with 'rec')
- `pageSize`: Comments per page (max 100)

**Pitfalls**:
- Record IDs must be exactly 17 characters starting with 'rec'

## Common Patterns

### Airtable Formula Syntax

**Comparison**:
- `{Status}='Done'` - Equals
- `{Priority}>1` - Greater than
- `{Name}!=''` - Not empty

**Functions**:
- `AND({A}='x', {B}='y')` - Both conditions
- `OR({A}='x', {A}='y')` - Either condition
- `FIND('test', {Name})>0` - Contains text
- `IS_BEFORE({Due Date}, TODAY())` - Date comparison

**Escape rules**:
- Single quotes in values: double them (`{Name}='John''s Company'`)

### Pagination

- Set `pageSize` (max 100)
- Check response for `offset` string
- Pass `offset` to next request unchanged
- Keep filters/sorts/view stable between pages

## Known Pitfalls

**ID Formats**:
- Base IDs: `appXXXXXXXXXXXXXX` (17 chars)
- Table IDs: `tblXXXXXXXXXXXXXX` (17 chars)
- Record IDs: `recXXXXXXXXXXXXXX` (17 chars)
- Field IDs: `fldXXXXXXXXXXXXXX` (17 chars)

**Batch Limits**:
- CREATE_RECORDS: max 10 per request
- UPDATE_MULTIPLE_RECORDS: max 10 per request
- DELETE_MULTIPLE_RECORDS: max 10 per request

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List bases | AIRTABLE_LIST_BASES | (none) |
| Get schema | AIRTABLE_GET_BASE_SCHEMA | baseId |
| List records | AIRTABLE_LIST_RECORDS | baseId, tableIdOrName |
| Get record | AIRTABLE_GET_RECORD | baseId, tableIdOrName, recordId |
| Create record | AIRTABLE_CREATE_RECORD | baseId, tableIdOrName, fields |
| Create records | AIRTABLE_CREATE_RECORDS | baseId, tableIdOrName, records |
| Update record | AIRTABLE_UPDATE_RECORD | baseId, tableIdOrName, recordId, fields |
| Update records | AIRTABLE_UPDATE_MULTIPLE_RECORDS | baseId, tableIdOrName, records |
| Delete record | AIRTABLE_DELETE_RECORD | baseId, tableIdOrName, recordId |
| Create field | AIRTABLE_CREATE_FIELD | baseId, tableIdOrName, name, type |
| Update field | AIRTABLE_UPDATE_FIELD | baseId, tableIdOrName, fieldId |
| Update table | AIRTABLE_UPDATE_TABLE | baseId, tableIdOrName, name |
| List comments | AIRTABLE_LIST_COMMENTS | baseId, tableIdOrName, recordId |
