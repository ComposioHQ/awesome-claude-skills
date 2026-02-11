---
name: googlesheets-automation
description: Automate Google Sheets operations (read, write, format, filter, manage spreadsheets) via Rube MCP (Composio). Read/write data, manage tabs, apply formatting, and search rows programmatically.
requires:
  mcp: [rube]
---

# Google Sheets Automation via Rube MCP

Automate Google Sheets workflows including reading/writing data, managing spreadsheets and tabs, formatting cells, filtering rows, and upserting records through Composio's Google Sheets toolkit.

**Toolkit docs**: [composio.dev/toolkits/googlesheets](https://composio.dev/toolkits/googlesheets)

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Google Sheets connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `googlesheets`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `googlesheets`
3. If connection is not ACTIVE, follow the returned auth link to complete Google OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Read and Write Data

**When to use**: User wants to read data from or write data to a Google Sheet

**Tool sequence**:
1. `GOOGLESHEETS_SEARCH_SPREADSHEETS` - Find spreadsheet by name if ID unknown [Prerequisite]
2. `GOOGLESHEETS_GET_SHEET_NAMES` - Enumerate tab names to target the right sheet [Prerequisite]
3. `GOOGLESHEETS_BATCH_GET` - Read data from one or more ranges [Required]
4. `GOOGLESHEETS_BATCH_UPDATE` - Write data to a range or append rows [Required]
5. `GOOGLESHEETS_VALUES_UPDATE` - Update a single specific range [Alternative]
6. `GOOGLESHEETS_SPREADSHEETS_VALUES_APPEND` - Append rows to end of table [Alternative]

**Key parameters**:
- `spreadsheet_id`: Alphanumeric ID from the spreadsheet URL (between '/d/' and '/edit')
- `ranges`: A1 notation array (e.g., 'Sheet1!A1:Z1000'); always use bounded ranges
- `sheet_name`: Tab name (case-insensitive matching supported)
- `values`: 2D array where each inner array is a row
- `first_cell_location`: Starting cell in A1 notation (omit to append)
- `valueInputOption`: 'USER_ENTERED' (parsed) or 'RAW' (literal)

**Pitfalls**:
- Mis-cased or non-existent tab names error "Sheet 'X' not found"
- Empty ranges may omit `valueRanges[i].values`; treat missing as empty array
- `GOOGLESHEETS_BATCH_UPDATE` values must be a 2D array (list of lists), even for a single row
- Unbounded ranges like 'A:Z' on sheets with >10,000 rows may cause timeouts; always bound with row limits
- Append follows the detected `tableRange`; use returned `updatedRange` to verify placement

### 2. Create and Manage Spreadsheets

**When to use**: User wants to create a new spreadsheet or manage tabs within one

**Tool sequence**:
1. `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` - Create a new spreadsheet [Required]
2. `GOOGLESHEETS_ADD_SHEET` - Add a new tab/worksheet [Required]
3. `GOOGLESHEETS_UPDATE_SHEET_PROPERTIES` - Rename, hide, reorder, or color tabs [Optional]
4. `GOOGLESHEETS_GET_SPREADSHEET_INFO` - Get full spreadsheet metadata [Optional]
5. `GOOGLESHEETS_FIND_WORKSHEET_BY_TITLE` - Check if a specific tab exists [Optional]

**Key parameters**:
- `title`: Spreadsheet or sheet tab name
- `spreadsheetId`: Target spreadsheet ID
- `forceUnique`: Auto-append suffix if tab name exists (default true)
- `properties.gridProperties`: Set row/column counts, frozen rows

**Pitfalls**:
- Sheet names must be unique within a spreadsheet
- Default sheet names are locale-dependent ('Sheet1' in English, 'Hoja 1' in Spanish)
- Don't use `index` when creating multiple sheets in parallel (causes 'index too high' errors)
- `GOOGLESHEETS_GET_SPREADSHEET_INFO` can return 403 if account lacks access

### 3. Search and Filter Rows

**When to use**: User wants to find specific rows or apply filters to sheet data

**Tool sequence**:
1. `GOOGLESHEETS_LOOKUP_SPREADSHEET_ROW` - Find first row matching exact cell value [Required]
2. `GOOGLESHEETS_SET_BASIC_FILTER` - Apply filter/sort to a range [Alternative]
3. `GOOGLESHEETS_CLEAR_BASIC_FILTER` - Remove existing filter [Optional]
4. `GOOGLESHEETS_BATCH_GET` - Read filtered results [Optional]

**Key parameters**:
- `query`: Exact text value to match (matches entire cell content)
- `range`: A1 notation range to search within
- `case_sensitive`: Boolean for case-sensitive matching (default false)
- `filter.range`: Grid range with sheet_id for basic filter
- `filter.criteria`: Column-based filter conditions
- `filter.sortSpecs`: Sort specifications

**Pitfalls**:
- `GOOGLESHEETS_LOOKUP_SPREADSHEET_ROW` matches entire cell content, not substrings
- Sheet names with spaces must be single-quoted in ranges (e.g., "'My Sheet'!A:Z")
- Bare sheet names without ranges are not supported for lookup; always specify a range

### 4. Upsert Rows by Key

**When to use**: User wants to update existing rows or insert new ones based on a unique key column

**Tool sequence**:
1. `GOOGLESHEETS_UPSERT_ROWS` - Update matching rows or append new ones [Required]

**Key parameters**:
- `spreadsheetId`: Target spreadsheet ID
- `sheetName`: Tab name
- `keyColumn`: Column header name used as unique identifier (e.g., 'Email', 'SKU')
- `headers`: List of column names for the data
- `rows`: 2D array of data rows
- `strictMode`: Error on mismatched column counts (default true)

**Pitfalls**:
- `keyColumn` must be an actual header name, NOT a column letter (e.g., 'Email' not 'A')
- If `headers` is NOT provided, first row of `rows` is treated as headers
- With `strictMode=true`, rows with more values than headers cause an error
- Auto-adds missing columns to the sheet

### 5. Format Cells

**When to use**: User wants to apply formatting (bold, colors, font size) to cells

**Tool sequence**:
1. `GOOGLESHEETS_GET_SPREADSHEET_INFO` - Get numeric sheetId for target tab [Prerequisite]
2. `GOOGLESHEETS_FORMAT_CELL` - Apply formatting to a range [Required]
3. `GOOGLESHEETS_UPDATE_SHEET_PROPERTIES` - Change frozen rows, column widths [Optional]

**Key parameters**:
- `spreadsheet_id`: Spreadsheet ID
- `worksheet_id`: Numeric sheetId (NOT tab name); get from GET_SPREADSHEET_INFO
- `range`: A1 notation (e.g., 'A1:F1') - preferred over index fields
- `bold`, `italic`, `underline`, `strikethrough`: Boolean formatting options
- `red`, `green`, `blue`: Background color as 0.0-1.0 floats (NOT 0-255 ints)
- `fontSize`: Font size in points

**Pitfalls**:
- Requires numeric `worksheet_id`, not tab title; get from spreadsheet metadata
- Color channels are 0-1 floats (e.g., 1.0 for full red), NOT 0-255 integers
- Responses may return empty reply objects ([{}]); verify formatting via readback
- Format one range per call; batch formatting requires separate calls

## Common Patterns

### ID Resolution
- **Spreadsheet name -> ID**: `GOOGLESHEETS_SEARCH_SPREADSHEETS` with `query`
- **Tab name -> sheetId**: `GOOGLESHEETS_GET_SPREADSHEET_INFO`, extract from sheets metadata
- **Tab existence check**: `GOOGLESHEETS_FIND_WORKSHEET_BY_TITLE`

### Rate Limits
Google Sheets enforces strict rate limits:
- Max 60 reads/minute and 60 writes/minute
- Exceeding limits causes errors; batch operations where possible
- Use `GOOGLESHEETS_BATCH_GET` and `GOOGLESHEETS_BATCH_UPDATE` for efficiency

### Data Patterns
- Always read before writing to understand existing layout
- Use `GOOGLESHEETS_UPSERT_ROWS` for CRM syncs, inventory updates, and dedup scenarios
- Append mode (omit `first_cell_location`) is safest for adding new records
- Use `GOOGLESHEETS_CLEAR_VALUES` to clear content while preserving formatting

## Known Pitfalls

- **Tab names**: Locale-dependent defaults; 'Sheet1' may not exist in non-English accounts
- **Range notation**: Sheet names with spaces need single quotes in A1 notation
- **Unbounded ranges**: Can timeout on large sheets; always specify row bounds (e.g., 'A1:Z10000')
- **2D arrays**: All value parameters must be list-of-lists, even for single rows
- **Color values**: Floats 0.0-1.0, not integers 0-255
- **Formatting IDs**: `FORMAT_CELL` needs numeric sheetId, not tab title
- **Rate limits**: 60 reads/min and 60 writes/min; batch to stay within limits
- **Delete dimension**: `GOOGLESHEETS_DELETE_DIMENSION` is irreversible; double-check bounds

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Search spreadsheets | `GOOGLESHEETS_SEARCH_SPREADSHEETS` | `query`, `search_type` |
| Create spreadsheet | `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` | `title` |
| List tabs | `GOOGLESHEETS_GET_SHEET_NAMES` | `spreadsheet_id` |
| Add tab | `GOOGLESHEETS_ADD_SHEET` | `spreadsheetId`, `title` |
| Read data | `GOOGLESHEETS_BATCH_GET` | `spreadsheet_id`, `ranges` |
| Read single range | `GOOGLESHEETS_VALUES_GET` | `spreadsheet_id`, `range` |
| Write data | `GOOGLESHEETS_BATCH_UPDATE` | `spreadsheet_id`, `sheet_name`, `values` |
| Update range | `GOOGLESHEETS_VALUES_UPDATE` | `spreadsheet_id`, `range`, `values` |
| Append rows | `GOOGLESHEETS_SPREADSHEETS_VALUES_APPEND` | `spreadsheetId`, `range`, `values` |
| Upsert rows | `GOOGLESHEETS_UPSERT_ROWS` | `spreadsheetId`, `sheetName`, `keyColumn`, `rows` |
| Lookup row | `GOOGLESHEETS_LOOKUP_SPREADSHEET_ROW` | `spreadsheet_id`, `query` |
| Format cells | `GOOGLESHEETS_FORMAT_CELL` | `spreadsheet_id`, `worksheet_id`, `range` |
| Set filter | `GOOGLESHEETS_SET_BASIC_FILTER` | `spreadsheetId`, `filter` |
| Clear values | `GOOGLESHEETS_CLEAR_VALUES` | `spreadsheet_id`, range |
| Delete rows/cols | `GOOGLESHEETS_DELETE_DIMENSION` | `spreadsheet_id`, `sheet_name`, dimension |
| Spreadsheet info | `GOOGLESHEETS_GET_SPREADSHEET_INFO` | `spreadsheet_id` |
| Update tab props | `GOOGLESHEETS_UPDATE_SHEET_PROPERTIES` | `spreadsheetId`, properties |

---
*Powered by [Composio](https://composio.dev)*
