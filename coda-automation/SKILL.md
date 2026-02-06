---
name: coda-automation
description: "Automate Coda tasks via Rube MCP (Composio): manage docs, pages, tables, rows, formulas, permissions, and publishing. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Coda Automation via Rube MCP

Automate Coda document and data operations through Composio's Coda toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Coda connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `coda`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `coda`
3. If connection is not ACTIVE, follow the returned auth link to complete Coda authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Search and Browse Documents

**When to use**: User wants to find, list, or inspect Coda documents

**Tool sequence**:
1. `CODA_SEARCH_DOCS` or `CODA_LIST_AVAILABLE_DOCS` - Find documents [Required]
2. `CODA_RESOLVE_BROWSER_LINK` - Resolve a Coda URL to doc/page/table IDs [Alternative]
3. `CODA_LIST_PAGES` - List pages within a document [Optional]
4. `CODA_GET_A_PAGE` - Get specific page details [Optional]

**Key parameters**:
- `query`: Search term for finding documents
- `isOwner`: Filter to docs owned by the user
- `docId`: Document ID for page operations
- `pageIdOrName`: Page identifier or name
- `url`: Browser URL for resolve operations

**Pitfalls**:
- Document IDs are alphanumeric strings (e.g., 'AbCdEfGhIj')
- `CODA_RESOLVE_BROWSER_LINK` is the best way to convert a Coda URL to API IDs
- Page names may not be unique within a doc; prefer page IDs
- Search results include docs shared with the user, not just owned docs

### 2. Work with Tables and Data

**When to use**: User wants to read, write, or query table data

**Tool sequence**:
1. `CODA_LIST_TABLES` - List tables in a document [Prerequisite]
2. `CODA_LIST_COLUMNS` - Get column definitions for a table [Prerequisite]
3. `CODA_LIST_TABLE_ROWS` - List all rows with optional filters [Required]
4. `CODA_SEARCH_ROW` - Search for specific rows by query [Alternative]
5. `CODA_GET_A_ROW` - Get a specific row by ID [Optional]
6. `CODA_UPSERT_ROWS` - Insert or update rows in a table [Optional]
7. `CODA_GET_A_COLUMN` - Get details of a specific column [Optional]

**Key parameters**:
- `docId`: Document ID containing the table
- `tableIdOrName`: Table identifier or name
- `query`: Filter query for searching rows
- `rows`: Array of row objects for upsert operations
- `keyColumns`: Column IDs used for matching during upsert
- `sortBy`: Column to sort results by
- `useColumnNames`: Use column names instead of IDs in row data

**Pitfalls**:
- Table names may contain spaces; URL-encode if needed
- `CODA_UPSERT_ROWS` does insert if no match on `keyColumns`, update if match found
- `keyColumns` must reference columns that have unique values for reliable upserts
- Column IDs are different from column names; list columns first to map names to IDs
- `useColumnNames: true` allows using human-readable names in row data
- Row data values must match the column type (text, number, date, etc.)

### 3. Manage Formulas

**When to use**: User wants to list or evaluate formulas in a document

**Tool sequence**:
1. `CODA_LIST_FORMULAS` - List all named formulas in a doc [Required]
2. `CODA_GET_A_FORMULA` - Get a specific formula's current value [Optional]

**Key parameters**:
- `docId`: Document ID
- `formulaIdOrName`: Formula identifier or name

**Pitfalls**:
- Formulas are named calculations defined in the document
- Formula values are computed server-side; results reflect the current state
- Formula names are case-sensitive

### 4. Export Document Content

**When to use**: User wants to export a document or page to HTML or Markdown

**Tool sequence**:
1. `CODA_BEGIN_CONTENT_EXPORT` - Start an export job [Required]
2. `CODA_CONTENT_EXPORT_STATUS` - Poll export status until complete [Required]

**Key parameters**:
- `docId`: Document ID to export
- `outputFormat`: Export format ('html' or 'markdown')
- `pageIdOrName`: Specific page to export (optional, omit for full doc)
- `requestId`: Export request ID for status polling

**Pitfalls**:
- Export is asynchronous; poll status until `status` is 'complete'
- Large documents may take significant time to export
- Export URL in the completed response is temporary; download promptly
- Polling too frequently may hit rate limits; use 2-5 second intervals

### 5. Manage Permissions and Sharing

**When to use**: User wants to view or manage document access

**Tool sequence**:
1. `CODA_GET_SHARING_METADATA` - View current sharing settings [Required]
2. `CODA_GET_ACL_SETTINGS` - Get access control list settings [Optional]
3. `CODA_ADD_PERMISSION` - Grant access to a user or email [Optional]

**Key parameters**:
- `docId`: Document ID
- `access`: Permission level ('readonly', 'write', 'comment')
- `principal`: Object with email or user ID of the recipient
- `suppressEmail`: Whether to skip the sharing notification email

**Pitfalls**:
- Permission levels: 'readonly', 'write', 'comment'
- Adding permission sends an email notification by default; use `suppressEmail` to prevent
- Cannot remove permissions via API in all cases; check ACL settings

### 6. Publish and Customize Documents

**When to use**: User wants to publish a document or manage custom domains

**Tool sequence**:
1. `CODA_PUBLISH_DOC` - Publish a document publicly [Required]
2. `CODA_UNPUBLISH_DOC` - Unpublish a document [Optional]
3. `CODA_ADD_CUSTOM_DOMAIN` - Add a custom domain for published doc [Optional]
4. `CODA_GET_DOC_CATEGORIES` - Get doc categories for discovery [Optional]

**Key parameters**:
- `docId`: Document ID
- `slug`: Custom URL slug for the published doc
- `categoryIds`: Category IDs for discoverability

**Pitfalls**:
- Publishing makes the document accessible to anyone with the link
- Custom domains require DNS configuration
- Unpublishing removes public access but retains shared access

## Common Patterns

### ID Resolution

**Doc URL -> Doc ID**:
```
1. Call CODA_RESOLVE_BROWSER_LINK with the Coda URL
2. Extract docId from the response
```

**Table name -> Table ID**:
```
1. Call CODA_LIST_TABLES with docId
2. Find table by name, extract id
```

**Column name -> Column ID**:
```
1. Call CODA_LIST_COLUMNS with docId and tableIdOrName
2. Find column by name, extract id
```

### Pagination

- Coda uses cursor-based pagination with `pageToken`
- Check response for `nextPageToken`
- Pass as `pageToken` in next request until absent
- Default page sizes vary by endpoint

### Row Upsert Pattern

```
1. Call CODA_LIST_COLUMNS to get column IDs
2. Build row objects with column ID keys and values
3. Set keyColumns to unique identifier column(s)
4. Call CODA_UPSERT_ROWS with rows and keyColumns
```

## Known Pitfalls

**ID Formats**:
- Document IDs: alphanumeric strings
- Table/column/row IDs: prefixed strings (e.g., 'grid-abc', 'c-xyz')
- Use RESOLVE_BROWSER_LINK to convert URLs to IDs

**Data Types**:
- Row values must match column types
- Date columns expect ISO 8601 format
- Select/multi-select columns expect exact option values
- People columns expect email addresses

**Rate Limits**:
- Coda API has per-token rate limits
- Implement backoff on 429 responses
- Bulk row operations via UPSERT_ROWS are more efficient than individual updates

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Search docs | CODA_SEARCH_DOCS | query |
| List docs | CODA_LIST_AVAILABLE_DOCS | isOwner |
| Resolve URL | CODA_RESOLVE_BROWSER_LINK | url |
| List pages | CODA_LIST_PAGES | docId |
| Get page | CODA_GET_A_PAGE | docId, pageIdOrName |
| List tables | CODA_LIST_TABLES | docId |
| List columns | CODA_LIST_COLUMNS | docId, tableIdOrName |
| List rows | CODA_LIST_TABLE_ROWS | docId, tableIdOrName |
| Search rows | CODA_SEARCH_ROW | docId, tableIdOrName, query |
| Get row | CODA_GET_A_ROW | docId, tableIdOrName, rowIdOrName |
| Upsert rows | CODA_UPSERT_ROWS | docId, tableIdOrName, rows, keyColumns |
| Get column | CODA_GET_A_COLUMN | docId, tableIdOrName, columnIdOrName |
| Push button | CODA_PUSH_A_BUTTON | docId, tableIdOrName, rowIdOrName, columnIdOrName |
| List formulas | CODA_LIST_FORMULAS | docId |
| Get formula | CODA_GET_A_FORMULA | docId, formulaIdOrName |
| Begin export | CODA_BEGIN_CONTENT_EXPORT | docId, outputFormat |
| Export status | CODA_CONTENT_EXPORT_STATUS | docId, requestId |
| Get sharing | CODA_GET_SHARING_METADATA | docId |
| Add permission | CODA_ADD_PERMISSION | docId, access, principal |
| Publish doc | CODA_PUBLISH_DOC | docId, slug |
| Unpublish doc | CODA_UNPUBLISH_DOC | docId |
| List packs | CODA_LIST_PACKS | (none) |
