---
name: dropbox-automation
description: Automate Dropbox file management, sharing, search, uploads, downloads, and folder operations via Rube MCP (Composio). Always search tools first for current schemas.
requires:
  mcp: [rube]
---

# Dropbox Automation via Rube MCP

Automate Dropbox operations including file upload/download, search, folder management, sharing links, batch operations, and metadata retrieval through Composio's Dropbox toolkit.

**Toolkit docs**: [composio.dev/toolkits/dropbox](https://composio.dev/toolkits/dropbox)

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Dropbox connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `dropbox`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `dropbox`
3. If connection is not ACTIVE, follow the returned auth link to complete Dropbox OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Search for Files and Folders

**When to use**: User wants to find files or folders by name, content, or type

**Tool sequence**:
1. `DROPBOX_SEARCH_FILE_OR_FOLDER` - Search by query string with optional path scope and filters [Required]
2. `DROPBOX_SEARCH_CONTINUE` - Paginate through additional results using cursor [Required if has_more]
3. `DROPBOX_GET_METADATA` - Validate and get canonical path for a search result [Optional]
4. `DROPBOX_READ_FILE` - Read file content to verify it is the intended document [Optional]

**Key parameters**:
- `query`: Search string (case-insensitive, 1+ non-whitespace characters)
- `options.path`: Scope search to a folder (e.g., `"/Documents"`); empty string for root
- `options.file_categories`: Filter by type (`"image"`, `"document"`, `"pdf"`, `"folder"`, etc.)
- `options.file_extensions`: Filter by extension (e.g., `["jpg", "png"]`)
- `options.filename_only`: Set `true` to match filenames only (not content)
- `options.max_results`: Results per page (default 100, max 1000)

**Pitfalls**:
- Search returns `has_more: true` with a `cursor` when more results exist; MUST continue to avoid silently missing matches
- Maximum 10,000 matches total across all pages of search + search_continue
- `DROPBOX_GET_METADATA` returned `path_display` may differ in casing from user input; always use the returned canonical path
- File content from `DROPBOX_READ_FILE` may be returned as base64-encoded `file_content_bytes`; decode before parsing

### 2. Upload and Download Files

**When to use**: User wants to upload files to Dropbox or download files from it

**Tool sequence**:
1. `DROPBOX_UPLOAD_FILE` - Upload a file to a specified path [Required for upload]
2. `DROPBOX_READ_FILE` - Download/read a file from Dropbox [Required for download]
3. `DROPBOX_DOWNLOAD_ZIP` - Download an entire folder as a zip file [Optional]
4. `DROPBOX_SAVE_URL` - Save a file from a public URL directly to Dropbox [Optional]
5. `DROPBOX_GET_SHARED_LINK_FILE` - Download a file from a shared link URL [Optional]
6. `DROPBOX_EXPORT_FILE` - Export non-downloadable files like Dropbox Paper to markdown/HTML [Optional]

**Key parameters**:
- `path`: Dropbox path (must start with `/`, e.g., `"/Documents/report.pdf"`)
- `mode`: `"add"` (default, fail on conflict) or `"overwrite"` for uploads
- `autorename`: `true` to auto-rename on conflict instead of failing
- `content`: FileUploadable object with `s3key`, `mimetype`, and `name` for uploads
- `url`: Public URL for `DROPBOX_SAVE_URL`
- `export_format`: `"markdown"`, `"html"`, or `"plain_text"` for Paper docs

**Pitfalls**:
- `DROPBOX_SAVE_URL` is asynchronous and may take up to 15 minutes for large files
- `DROPBOX_DOWNLOAD_ZIP` folder must be under 20 GB with no single file over 4 GB and fewer than 10,000 entries
- `DROPBOX_READ_FILE` content may be base64-encoded; check response format
- Shared link downloads via `DROPBOX_GET_SHARED_LINK_FILE` may require `link_password` for protected links

### 3. Share Files and Manage Links

**When to use**: User wants to create sharing links or manage existing shared links

**Tool sequence**:
1. `DROPBOX_GET_METADATA` - Confirm file/folder exists and get canonical path [Prerequisite]
2. `DROPBOX_LIST_SHARED_LINKS` - Check for existing shared links to avoid duplicates [Prerequisite]
3. `DROPBOX_CREATE_SHARED_LINK` - Create a new shared link [Required]
4. `DROPBOX_GET_SHARED_LINK_METADATA` - Resolve a shared link URL to metadata [Optional]
5. `DROPBOX_LIST_SHARED_FOLDERS` - List all shared folders the user has access to [Optional]

**Key parameters**:
- `path`: File or folder path for link creation
- `settings.audience`: `"public"`, `"team"`, or `"no_one"`
- `settings.access`: `"viewer"` or `"editor"`
- `settings.expires`: ISO 8601 expiration date (e.g., `"2026-12-31T23:59:59Z"`)
- `settings.require_password` / `settings.link_password`: Password protection
- `settings.allow_download`: Boolean for download permission
- `direct_only`: For `LIST_SHARED_LINKS`, set `true` to only return direct links (not parent folder links)

**Pitfalls**:
- `DROPBOX_CREATE_SHARED_LINK` fails with 409 Conflict if a shared link already exists for the path; check with `DROPBOX_LIST_SHARED_LINKS` first
- Always validate path with `DROPBOX_GET_METADATA` before creating links to avoid `path/not_found` errors
- Reuse existing links from `DROPBOX_LIST_SHARED_LINKS` instead of creating duplicates
- `requested_visibility` is deprecated; use `audience` for newer implementations

### 4. Manage Folders (Create, Move, Delete)

**When to use**: User wants to create, move, rename, or delete files and folders

**Tool sequence**:
1. `DROPBOX_CREATE_FOLDER` - Create a single folder [Required for create]
2. `DROPBOX_CREATE_FOLDER_BATCH` - Create multiple folders at once [Optional]
3. `DROPBOX_MOVE_FILE_OR_FOLDER` - Move or rename a single file/folder [Required for move]
4. `DROPBOX_MOVE_BATCH` - Move multiple items at once [Optional]
5. `DROPBOX_DELETE_FILE_OR_FOLDER` - Delete a single file or folder [Required for delete]
6. `DROPBOX_DELETE_BATCH` - Delete multiple items at once [Optional]
7. `DROPBOX_COPY_FILE_OR_FOLDER` - Copy a file or folder to a new location [Optional]
8. `DROPBOX_CHECK_MOVE_BATCH` / `DROPBOX_CHECK_FOLDER_BATCH` - Poll async batch job status [Required for batch ops]

**Key parameters**:
- `path`: Target path (must start with `/`, case-sensitive)
- `from_path` / `to_path`: Source and destination for move/copy operations
- `autorename`: `true` to auto-rename on conflict
- `entries`: Array of `{from_path, to_path}` for batch moves; array of paths for batch creates
- `allow_shared_folder`: Set `true` to allow moving shared folders
- `allow_ownership_transfer`: Set `true` if move changes ownership

**Pitfalls**:
- All paths are case-sensitive and must start with `/`
- Paths must NOT end with `/` or whitespace
- Batch operations may be asynchronous; poll with `DROPBOX_CHECK_MOVE_BATCH` or `DROPBOX_CHECK_FOLDER_BATCH`
- `DROPBOX_FILES_MOVE_BATCH` (v1) has "all or nothing" behavior - if any entry fails, entire batch fails
- `DROPBOX_MOVE_BATCH` (v2) is preferred over `DROPBOX_FILES_MOVE_BATCH` (v1)
- Maximum 1000 entries per batch delete/move; 10,000 paths per batch folder create
- Case-only renaming is not supported in batch move operations

### 5. List Folder Contents

**When to use**: User wants to browse or enumerate files in a Dropbox folder

**Tool sequence**:
1. `DROPBOX_LIST_FILES_IN_FOLDER` - List contents of a folder [Required]
2. `DROPBOX_LIST_FOLDERS` - Alternative folder listing with deleted entries support [Optional]
3. `DROPBOX_GET_METADATA` - Get details for a specific item [Optional]

**Key parameters**:
- `path`: Folder path (empty string `""` for root)
- `recursive`: `true` to list all nested contents
- `limit`: Max results per request (default/max 2000)
- `include_deleted`: `true` to include deleted but recoverable items
- `include_media_info`: `true` to get photo/video metadata

**Pitfalls**:
- Use empty string `""` for root folder, not `"/"`
- Recursive listings can be very large; use `limit` to control page size
- Results may paginate via cursor even with small limits
- `DROPBOX_LIST_FILES_IN_FOLDER` returns 409 Conflict with `path/not_found` for incorrect paths

## Common Patterns

### ID Resolution
- **Path-based**: Most Dropbox tools use path strings (e.g., `"/Documents/file.pdf"`)
- **ID-based**: Some tools accept `id:...` format (e.g., `"id:4g0reWVRsAAAAAAAAAAAQ"`)
- **Canonical path**: Always use `path_display` or `path_lower` from `DROPBOX_GET_METADATA` responses for subsequent calls
- **Shared link URL**: Use `DROPBOX_GET_SHARED_LINK_METADATA` to resolve URLs to paths/IDs

### Pagination
Dropbox uses cursor-based pagination across most endpoints:
- Search: Follow `has_more` + `cursor` with `DROPBOX_SEARCH_CONTINUE` (max 10,000 total matches)
- Folder listing: Follow cursor from response until no more pages
- Shared links: Follow `has_more` + `cursor` in `DROPBOX_LIST_SHARED_LINKS`
- Batch job status: Poll with `DROPBOX_CHECK_MOVE_BATCH` / `DROPBOX_CHECK_FOLDER_BATCH`

### Async Operations
Several Dropbox operations run asynchronously:
- `DROPBOX_SAVE_URL` - returns job ID; poll or set `wait: true` (up to 120s default)
- `DROPBOX_MOVE_BATCH` / `DROPBOX_FILES_MOVE_BATCH` - may return job ID
- `DROPBOX_CREATE_FOLDER_BATCH` - may return job ID
- `DROPBOX_DELETE_BATCH` - returns job ID

## Known Pitfalls

### Path Formats
- All paths must start with `/` (except empty string for root in some endpoints)
- Paths must NOT end with `/` or contain trailing whitespace
- Paths are case-sensitive for write operations
- `path_display` from API may differ in casing from user input; always prefer API-returned paths

### Rate Limits
- Dropbox API has per-endpoint rate limits; batch operations help reduce call count
- Search is limited to 10,000 total matches across all pagination
- `DROPBOX_SAVE_URL` has a 15-minute timeout for large files

### File Content
- `DROPBOX_READ_FILE` may return content as base64-encoded `file_content_bytes`
- Non-downloadable files (Dropbox Paper, Google Docs) require `DROPBOX_EXPORT_FILE` instead
- Download URLs from shared links require proper authentication headers

### Sharing
- Creating a shared link when one already exists returns a 409 Conflict error
- Always check `DROPBOX_LIST_SHARED_LINKS` before creating new links
- Shared folder access may not appear in standard path listings; use `DROPBOX_LIST_SHARED_FOLDERS`

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Search files | `DROPBOX_SEARCH_FILE_OR_FOLDER` | `query`, `options.path` |
| Continue search | `DROPBOX_SEARCH_CONTINUE` | `cursor` |
| List folder | `DROPBOX_LIST_FILES_IN_FOLDER` | `path`, `recursive`, `limit` |
| List folders | `DROPBOX_LIST_FOLDERS` | `path`, `recursive` |
| Get metadata | `DROPBOX_GET_METADATA` | `path` |
| Read/download file | `DROPBOX_READ_FILE` | `path` |
| Upload file | `DROPBOX_UPLOAD_FILE` | `path`, `content`, `mode` |
| Save URL to Dropbox | `DROPBOX_SAVE_URL` | `path`, `url` |
| Download folder zip | `DROPBOX_DOWNLOAD_ZIP` | `path` |
| Export Paper doc | `DROPBOX_EXPORT_FILE` | `path`, `export_format` |
| Download shared link | `DROPBOX_GET_SHARED_LINK_FILE` | `url` |
| Create shared link | `DROPBOX_CREATE_SHARED_LINK` | `path`, `settings` |
| List shared links | `DROPBOX_LIST_SHARED_LINKS` | `path`, `direct_only` |
| Shared link metadata | `DROPBOX_GET_SHARED_LINK_METADATA` | `url` |
| List shared folders | `DROPBOX_LIST_SHARED_FOLDERS` | `limit` |
| Create folder | `DROPBOX_CREATE_FOLDER` | `path` |
| Create folders batch | `DROPBOX_CREATE_FOLDER_BATCH` | `paths` |
| Move file/folder | `DROPBOX_MOVE_FILE_OR_FOLDER` | `from_path`, `to_path` |
| Move batch | `DROPBOX_MOVE_BATCH` | `entries` |
| Delete file/folder | `DROPBOX_DELETE_FILE_OR_FOLDER` | `path` |
| Delete batch | `DROPBOX_DELETE_BATCH` | `entries` |
| Copy file/folder | `DROPBOX_COPY_FILE_OR_FOLDER` | `from_path`, `to_path` |
| Check batch status | `DROPBOX_CHECK_MOVE_BATCH` | `async_job_id` |

---
*Powered by [Composio](https://composio.dev)*
