---
name: googledocs-automation
description: "Automate Google Docs tasks via Rube MCP (Composio): create, edit, search, export, copy, and update documents. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Google Docs Automation via Rube MCP

Create, edit, search, export, and manage Google Docs documents programmatically using Rube MCP (Composio).

**Toolkit docs**: [composio.dev/toolkits/googledocs](https://composio.dev/toolkits/googledocs)

## Prerequisites
- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `googledocs`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup
**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.

1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `googledocs`
3. If connection is not ACTIVE, follow the returned auth link to complete setup
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create a New Document
Use `GOOGLEDOCS_CREATE_DOCUMENT` to create a new Google Doc with a title and initial text content.
```
Tool: GOOGLEDOCS_CREATE_DOCUMENT
Parameters:
  - title (required): Document filename/title
  - text (required): Initial text content to insert into the document
```

### 2. Search for Documents
Use `GOOGLEDOCS_SEARCH_DOCUMENTS` to find Google Docs by name, content, date, or sharing status.
```
Tool: GOOGLEDOCS_SEARCH_DOCUMENTS
Parameters:
  - query: Search query string
  - max_results: Limit number of results
  - modified_after / created_after: Filter by date
  - shared_with_me: Filter shared documents
  - starred_only: Filter starred documents
  - include_shared_drives: Search shared drives
  - order_by: Sort results
  - page_token: Pagination token
```

### 3. Update Document Content with Markdown
Use `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN` to replace the entire content of a document with Markdown-formatted text.
```
Tool: GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN
Parameters:
  - id (required): Document ID
  - markdown (required): Markdown content to replace entire document body
```

### 4. Find and Replace Text
Use `GOOGLEDOCS_REPLACE_ALL_TEXT` to replace all occurrences of a string in a document.
```
Tool: GOOGLEDOCS_REPLACE_ALL_TEXT
Parameters:
  - document_id (required): Target document ID
  - find_text (required): Text to search for
  - replace_text (required): Replacement text
  - match_case: Case-sensitive matching (boolean)
  - search_by_regex: Use regex for find_text
  - tab_ids: Specific tabs to search
```

### 5. Export Document as PDF
Use `GOOGLEDOCS_EXPORT_DOCUMENT_AS_PDF` to export a Google Doc to PDF format.
```
Tool: GOOGLEDOCS_EXPORT_DOCUMENT_AS_PDF
Parameters:
  - file_id (required): Document file ID
  - filename: Output PDF filename
```

### 6. Copy a Document
Use `GOOGLEDOCS_COPY_DOCUMENT` to duplicate an existing Google Doc.
```
Tool: GOOGLEDOCS_COPY_DOCUMENT
Parameters:
  - document_id (required): Source document ID to copy
  - title: Title for the new copy
  - include_shared_drives: Search shared drives for the source
```

## Common Patterns

- **Search then edit**: Use `GOOGLEDOCS_SEARCH_DOCUMENTS` to find a document by name, then use the returned document ID with `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN` or `GOOGLEDOCS_REPLACE_ALL_TEXT` to modify it.
- **Create from template**: Use `GOOGLEDOCS_COPY_DOCUMENT` to duplicate a template, then `GOOGLEDOCS_REPLACE_ALL_TEXT` to fill in placeholder text.
- **Retrieve then update**: Use `GOOGLEDOCS_GET_DOCUMENT_BY_ID` to read current content, then apply edits with `GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT`.
- **Batch text insertion**: Use `GOOGLEDOCS_INSERT_TEXT_ACTION` to insert text at specific positions (by index) or append to the end of a document.
- **Share documents**: Combine with `GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE` (googledrive toolkit) to share documents after creation.

## Known Pitfalls

- `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN` replaces the **entire** document content -- it does not append. Use it for full rewrites only.
- `GOOGLEDOCS_INSERT_TEXT_ACTION` requires a precise `insertion_index` (character position). Set `append_to_end: true` to safely add text at the end.
- `GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT` requires constructing an `editDocs` request body with raw Google Docs API batch update requests -- consult the API documentation for the correct structure.
- Document IDs and file IDs are the same value for Google Docs, but parameter names differ across tools (`id`, `document_id`, `file_id`).
- `GOOGLEDOCS_SEARCH_DOCUMENTS` uses Google Drive search syntax for the `query` parameter (e.g., `name contains 'report'`).

## Quick Reference
| Action | Tool | Key Parameters |
|--------|------|----------------|
| Create document | `GOOGLEDOCS_CREATE_DOCUMENT` | `title`, `text` |
| Search documents | `GOOGLEDOCS_SEARCH_DOCUMENTS` | `query`, `max_results`, `modified_after` |
| Get document by ID | `GOOGLEDOCS_GET_DOCUMENT_BY_ID` | `id` |
| Update with Markdown | `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN` | `id`, `markdown` |
| Programmatic edits | `GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT` | `document_id`, `editDocs` |
| Insert text | `GOOGLEDOCS_INSERT_TEXT_ACTION` | `document_id`, `text_to_insert`, `insertion_index` |
| Find and replace | `GOOGLEDOCS_REPLACE_ALL_TEXT` | `document_id`, `find_text`, `replace_text` |
| Export as PDF | `GOOGLEDOCS_EXPORT_DOCUMENT_AS_PDF` | `file_id`, `filename` |
| Copy document | `GOOGLEDOCS_COPY_DOCUMENT` | `document_id`, `title` |

---
*Powered by [Composio](https://composio.dev)*
