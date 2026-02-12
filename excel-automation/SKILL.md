---
name: Excel Automation
description: "Excel Automation: create workbooks, manage worksheets, read/write cell data, and format spreadsheets via Microsoft Excel and Google Sheets integration"
requires:
  mcp: [rube]
---

# Excel Automation

Automate spreadsheet operations including creating workbooks, writing data, formatting cells, upserting rows, and managing worksheets. Works with Microsoft Excel (OneDrive) and Google Sheets.

**Toolkit docs:** [composio.dev/toolkits/excel](https://composio.dev/toolkits/excel)

---

## Setup

This skill requires the **Rube MCP server** connected at `https://rube.app/mcp`.

Before executing any tools, ensure an active connection exists for the `excel` (and optionally `googlesheets`) toolkit. If no connection is active, initiate one via `RUBE_MANAGE_CONNECTIONS`.

---

## Core Workflows

### 1. Create a New Excel Workbook

Use `EXCEL_CREATE_WORKBOOK` to generate a new `.xlsx` file and upload it to OneDrive.

**Tool:** `EXCEL_CREATE_WORKBOOK`

**Steps:**
1. Call `EXCEL_CREATE_WORKBOOK` with worksheet names and data
2. The tool creates a `.xlsx` file and uploads it to OneDrive
3. Use the returned file path/URL for subsequent operations

---

### 2. Write Data to a Spreadsheet

Use `GOOGLESHEETS_BATCH_UPDATE` to write values to a specific range or append rows.

**Tool:** `GOOGLESHEETS_BATCH_UPDATE`

**Key Parameters:**
- `spreadsheet_id` (required) -- The spreadsheet ID from the URL (44-char alphanumeric string)
- `sheet_name` (required) -- Tab name, e.g., `"Sheet1"`, `"Sales Data"`
- `values` (required) -- 2D array of cell values, e.g., `[["Name","Amount"],["Alice",100]]`
- `first_cell_location` -- Starting cell in A1 notation (e.g., `"A1"`, `"D3"`). Omit to append rows
- `valueInputOption` -- `"USER_ENTERED"` (default, parses formulas) or `"RAW"` (stores as-is)

**Example:**
```
Tool: GOOGLESHEETS_BATCH_UPDATE
Arguments:
  spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  sheet_name: "Sheet1"
  values: [["Item","Cost","Stocked"],["Wheel",20.50,true],["Screw",0.50,true]]
  first_cell_location: "A1"
```

---

### 3. Upsert Rows by Key Column

Use `GOOGLESHEETS_UPSERT_ROWS` to update existing rows by matching a key column, or append new rows if no match is found. Ideal for CRM syncs, inventory updates, and deduplication.

**Tool:** `GOOGLESHEETS_UPSERT_ROWS`

**Key Parameters:**
- `spreadsheetId` (required) -- The spreadsheet ID
- `sheetName` (required) -- Tab name
- `rows` (required) -- 2D array of data rows (min 1 row). If `headers` is omitted, the first row is treated as headers
- `headers` -- Column names for the data, e.g., `["Email","Phone","Status"]`
- `keyColumn` -- Column header to match on, e.g., `"Email"`, `"SKU"`, `"Lead ID"`
- `strictMode` -- `true` (default) errors on mismatched columns; `false` truncates silently

**Example:**
```
Tool: GOOGLESHEETS_UPSERT_ROWS
Arguments:
  spreadsheetId: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  sheetName: "Contacts"
  keyColumn: "Email"
  headers: ["Email","Phone","Status"]
  rows: [["john@example.com","555-0101","Active"],["jane@example.com","555-0102","Pending"]]
```

---

### 4. Format Cells

Use `GOOGLESHEETS_FORMAT_CELL` to apply bold, italic, font size, and background colors to ranges.

**Tool:** `GOOGLESHEETS_FORMAT_CELL`

**Key Parameters:**
- `spreadsheet_id` (required) -- The spreadsheet ID
- `range` -- Cell range in A1 notation, e.g., `"A1:D1"`, `"B2:B10"` (recommended over index-based)
- `sheet_name` -- Worksheet name, e.g., `"Sheet1"`
- `bold` -- `true`/`false`
- `italic` -- `true`/`false`
- `fontSize` -- Font size in points, e.g., `12`
- `red`, `green`, `blue` -- Background color components (0.0--1.0 float scale, NOT 0--255)

**Example (bold header row with blue background):**
```
Tool: GOOGLESHEETS_FORMAT_CELL
Arguments:
  spreadsheet_id: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  range: "A1:D1"
  sheet_name: "Sheet1"
  bold: true
  fontSize: 12
  red: 0.2
  green: 0.4
  blue: 0.9
```

---

### 5. Add New Worksheet Tabs

Use `GOOGLESHEETS_ADD_SHEET` to create new tabs within an existing spreadsheet.

**Tool:** `GOOGLESHEETS_ADD_SHEET`

**Key Parameters:**
- `spreadsheetId` (required) -- The spreadsheet ID
- `title` -- Name for the new tab, e.g., `"Q4 Report"`
- `forceUnique` -- `true` (default) auto-appends suffix if name exists

**Example:**
```
Tool: GOOGLESHEETS_ADD_SHEET
Arguments:
  spreadsheetId: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
  title: "Q4 Report"
  forceUnique: true
```

---

### 6. Read Data and Verify Content

Use `GOOGLESHEETS_BATCH_GET` to retrieve data from specified cell ranges for validation or further processing.

**Tool:** `GOOGLESHEETS_BATCH_GET`

**Steps:**
1. Call `GOOGLESHEETS_BATCH_GET` with the spreadsheet ID and target ranges
2. Validate headers and data alignment
3. Use results to inform subsequent write or update operations

**Supporting Tools:**
- `GOOGLESHEETS_GET_SHEET_NAMES` -- List all tab names in a spreadsheet
- `GOOGLESHEETS_GET_SPREADSHEET_INFO` -- Get metadata (sheet IDs, properties)
- `GOOGLESHEETS_FIND_WORKSHEET_BY_TITLE` -- Check if a specific tab exists

---

## Recommended Execution Plan

1. **Create or locate the spreadsheet** using `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` or reuse an existing `spreadsheetId`
2. **Confirm the destination tab** using `GOOGLESHEETS_GET_SHEET_NAMES` or `GOOGLESHEETS_FIND_WORKSHEET_BY_TITLE`; create it with `GOOGLESHEETS_ADD_SHEET` if missing
3. **Read existing headers** (optional) using `GOOGLESHEETS_BATCH_GET` to align columns
4. **Write or upsert data** using `GOOGLESHEETS_BATCH_UPDATE` or `GOOGLESHEETS_UPSERT_ROWS`
5. **Apply formatting** (optional) using `GOOGLESHEETS_FORMAT_CELL`
6. **Verify results** (optional) using `GOOGLESHEETS_BATCH_GET`
7. **Fallback:** If Google Sheets creation is blocked (HTTP 403), use `EXCEL_CREATE_WORKBOOK` for local `.xlsx` output

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| **HTTP 403 on sheet creation** | `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` fails when Drive create scope is missing. Reuse an existing `spreadsheetId` or fall back to `EXCEL_CREATE_WORKBOOK`. |
| **Cell limit and rate throttling** | Google Sheets has a ~5,000,000 cell limit per spreadsheet. Excessive write frequency triggers HTTP 429. Batch changes and chunk large writes (~500 rows/call). |
| **Format range off-by-one** | `GOOGLESHEETS_FORMAT_CELL` uses 0-based, endIndex-exclusive ranges when using index mode. Background color uses 0--1 float RGB, NOT 0--255 integer RGB. |
| **Sheet title uniqueness** | Sheet titles are not guaranteed unique across API responses. Prefer operating by numeric `sheetId` and verify the resolved tab before writing. |
| **Upsert payload shape** | `GOOGLESHEETS_UPSERT_ROWS` requires headers + 2D rows array. Sending list-of-dicts or empty `rows` causes validation errors. Ensure at least 1 data row. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `EXCEL_CREATE_WORKBOOK` | Create a new `.xlsx` workbook and upload to OneDrive |
| `GOOGLESHEETS_BATCH_UPDATE` | Write values to a range or append new rows |
| `GOOGLESHEETS_UPSERT_ROWS` | Update existing rows by key or append new ones |
| `GOOGLESHEETS_FORMAT_CELL` | Apply text/background formatting to cell ranges |
| `GOOGLESHEETS_ADD_SHEET` | Add a new worksheet tab to a spreadsheet |
| `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` | Create a new Google Spreadsheet in Drive |
| `GOOGLESHEETS_GET_SHEET_NAMES` | List all worksheet names in a spreadsheet |
| `GOOGLESHEETS_GET_SPREADSHEET_INFO` | Retrieve spreadsheet metadata |
| `GOOGLESHEETS_FIND_WORKSHEET_BY_TITLE` | Check if a worksheet exists by title |
| `GOOGLESHEETS_BATCH_GET` | Read data from specified cell ranges |

---

*Powered by [Composio](https://composio.dev)*
