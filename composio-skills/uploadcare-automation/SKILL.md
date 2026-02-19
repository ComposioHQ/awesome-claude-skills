---
name: Uploadcare Automation
description: "Automate Uploadcare file management including listing, storing, inspecting, downloading, and organizing file groups through natural language commands"
requires:
  mcp:
    - rube
---

# Uploadcare Automation

Automate Uploadcare file handling workflows -- list project files, permanently store uploads, retrieve file metadata, get download URLs, and manage file groups -- all through natural language.

**Toolkit docs:** [composio.dev/toolkits/uploadcare](https://composio.dev/toolkits/uploadcare)

---

## Setup

1. Add the Rube MCP server to your environment: `https://rube.app/mcp`
2. Connect your Uploadcare account when prompted (API key auth via Composio)
3. Start issuing natural language commands for Uploadcare automation

---

## Core Workflows

### 1. List Project Files

Browse uploaded files in your Uploadcare project with filtering, sorting, and pagination.

**Tool:** `UPLOADCARE_LIST_FILES`

Key parameters:
- `stored` -- filter by storage status: `"true"` for stored, `"false"` for unstored
- `removed` -- filter by removal status: `"true"` for removed, `"false"` for active
- `ordering` -- sort by `datetime_uploaded` (ascending) or `-datetime_uploaded` (descending)
- `limit` -- files per page, 1-1000 (default 100)
- `offset` -- zero-based pagination offset
- `from_date` -- ISO 8601 timestamp to filter files uploaded after this date
- `to_date` -- ISO 8601 timestamp to filter files uploaded before this date
- `include` -- set to `"total"` to include total file count in response

Example prompt:
> "List the 50 most recently uploaded stored files in my Uploadcare project"

---

### 2. Store a File Permanently

Mark an uploaded file as permanently stored. By default, Uploadcare files are temporary and will be deleted after 24 hours unless stored.

**Tool:** `UPLOADCARE_STORE_FILE`

Key parameters:
- `uuid` -- UUID of the file to store (required); must be in `8-4-4-4-12` hex format (e.g., `3e55317b-23d1-4f35-9b4c-b9accb7b53f4`)

> Always store files after upload to prevent automatic deletion.

Example prompt:
> "Permanently store the file with UUID 3e55317b-23d1-4f35-9b4c-b9accb7b53f4"

---

### 3. Get File Metadata

Retrieve detailed information about a specific file including size, MIME type, CDN URL, image dimensions, and more.

**Tool:** `UPLOADCARE_GET_FILE_INFO`

Key parameters:
- `uuid` -- the UUID of the file to inspect (required); format: `8-4-4-4-12` hex

Returns: filename, size, MIME type, CDN URL, upload date, storage status, image info (dimensions, color mode), and more.

Example prompt:
> "Get the metadata and dimensions for file 3e0923f2-e05a-4b37-9f0d-343b981c9d70"

---

### 4. Get a Temporary Download URL

Retrieve a temporary direct download link for a specific file.

**Tool:** `UPLOADCARE_GET_FILE_DOWNLOAD_URL`

Key parameters:
- `file_id` -- the unique file identifier (required)

Returns a time-limited URL that can be used for direct file download.

Example prompt:
> "Get a download link for file 3e0923f2-e05a-4b37-9f0d-343b981c9d70"

---

### 5. Browse File Groups

List file groups in your project. Groups are collections of files uploaded together.

**Tool:** `UPLOADCARE_LIST_GROUPS`

Key parameters:
- `limit` -- groups per page, 1-1000 (default 20)
- `offset` -- zero-based pagination offset (default 0)
- `ordering` -- sort by `datetime_created` (ascending) or `-datetime_created` (descending)

Example prompt:
> "List my 10 most recent file groups"

---

### 6. File Lifecycle Workflow

Combine tools for end-to-end file management:

1. **Upload**: Files are uploaded via Uploadcare's upload API or widget (outside this toolkit)
2. **Store**: `UPLOADCARE_STORE_FILE` -- mark files as permanent to prevent auto-deletion
3. **Inspect**: `UPLOADCARE_GET_FILE_INFO` -- verify metadata, check dimensions and MIME type
4. **Share**: `UPLOADCARE_GET_FILE_DOWNLOAD_URL` -- generate a temporary download link
5. **Browse**: `UPLOADCARE_LIST_FILES` -- audit all files with status and date filters
6. **Groups**: `UPLOADCARE_LIST_GROUPS` -- review batch uploads

Example prompt:
> "Store file abc-123, then get its metadata and a download link"

---

## Known Pitfalls

| Pitfall | Details |
|---------|---------|
| Auto-deletion of unstored files | Uploaded files are temporary by default and deleted after 24 hours -- always call `UPLOADCARE_STORE_FILE` to persist them |
| UUID format strict | File UUIDs must be in exact `8-4-4-4-12` hex format (e.g., `3e55317b-23d1-4f35-9b4c-b9accb7b53f4`); invalid formats will be rejected |
| Filter values are strings | The `stored` and `removed` parameters accept string values `"true"` or `"false"`, not booleans |
| Temporary download URLs | URLs from `UPLOADCARE_GET_FILE_DOWNLOAD_URL` are time-limited and will expire |
| Pagination is offset-based | Use `offset` + `limit` for pagination; there are no cursor-based pagination tokens |
| No upload tool | File uploads happen through Uploadcare's upload API or widget, not through this toolkit -- these tools manage already-uploaded files |

---

## Quick Reference

| Action | Tool Slug | Key Params |
|--------|-----------|------------|
| List files | `UPLOADCARE_LIST_FILES` | `stored`, `ordering`, `limit`, `offset` |
| Store file | `UPLOADCARE_STORE_FILE` | `uuid` |
| Get file info | `UPLOADCARE_GET_FILE_INFO` | `uuid` |
| Get download URL | `UPLOADCARE_GET_FILE_DOWNLOAD_URL` | `file_id` |
| List groups | `UPLOADCARE_LIST_GROUPS` | `limit`, `offset`, `ordering` |

---

*Powered by [Composio](https://composio.dev)*
