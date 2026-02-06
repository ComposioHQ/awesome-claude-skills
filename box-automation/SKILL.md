---
name: box-automation
description: Automate Box cloud storage operations including file upload/download, search, folder management, sharing, collaborations, and metadata queries via Rube MCP (Composio). Always search tools first for current schemas.
requires:
  mcp: [rube]
---

# Box Automation via Rube MCP

Automate Box operations including file upload/download, content search, folder management, collaboration, metadata queries, and sign requests through Composio's Box toolkit.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Box connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `box`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `box`
3. If connection is not ACTIVE, follow the returned auth link to complete Box OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Upload and Download Files

**When to use**: User wants to upload files to Box or download files from it

**Tool sequence**:
1. `BOX_SEARCH_FOR_CONTENT` - Find the target folder if path is unknown [Prerequisite]
2. `BOX_GET_FOLDER_INFORMATION` - Verify folder exists and get folder_id [Prerequisite]
3. `BOX_LIST_ITEMS_IN_FOLDER` - Browse folder contents and discover file IDs [Optional]
4. `BOX_UPLOAD_FILE` - Upload a file to a specific folder [Required for upload]
5. `BOX_DOWNLOAD_FILE` - Download a file by file_id [Required for download]
6. `BOX_CREATE_ZIP_DOWNLOAD` - Bundle multiple files/folders into a zip [Optional]

**Key parameters**:
- `parent_id`: Folder ID for upload destination (use `"0"` for root folder)
- `file`: FileUploadable object with `s3key`, `mimetype`, and `name` for uploads
- `file_id`: Unique file identifier for downloads
- `version`: Optional file version ID for downloading specific versions
- `fields`: Comma-separated list of attributes to return

**Pitfalls**:
- Uploading to a folder with existing filenames can trigger conflict behavior; decide overwrite vs rename semantics
- Files over 50MB should use chunk upload APIs (not available via standard tools)
- The `attributes` part of upload must come before the `file` part or you get HTTP 400 with `metadata_after_file_contents`
- File IDs and folder IDs are numeric strings extractable from Box web app URLs (e.g., `https://*.app.box.com/files/123` gives file_id `"123"`)

### 2. Search and Browse Content

**When to use**: User wants to find files, folders, or web links by name, content, or metadata

**Tool sequence**:
1. `BOX_SEARCH_FOR_CONTENT` - Full-text search across files, folders, and web links [Required]
2. `BOX_LIST_ITEMS_IN_FOLDER` - Browse contents of a specific folder [Optional]
3. `BOX_GET_FILE_INFORMATION` - Get detailed metadata for a specific file [Optional]
4. `BOX_GET_FOLDER_INFORMATION` - Get detailed metadata for a specific folder [Optional]
5. `BOX_QUERY_FILES_FOLDERS_BY_METADATA` - Search by metadata template values [Optional]
6. `BOX_LIST_RECENTLY_ACCESSED_ITEMS` - List recently accessed items [Optional]

**Key parameters**:
- `query`: Search string supporting operators (`""` exact match, `AND`, `OR`, `NOT` - uppercase only)
- `type`: Filter by `"file"`, `"folder"`, or `"web_link"`
- `ancestor_folder_ids`: Limit search to specific folders (comma-separated IDs)
- `file_extensions`: Filter by file type (comma-separated, no dots)
- `content_types`: Search in `"name"`, `"description"`, `"file_content"`, `"comments"`, `"tags"`
- `created_at_range` / `updated_at_range`: Date filters as comma-separated RFC3339 timestamps
- `limit`: Results per page (default 30)
- `offset`: Pagination offset (max 10000)
- `folder_id`: For `LIST_ITEMS_IN_FOLDER` (use `"0"` for root)

**Pitfalls**:
- Queries with offset > 10000 are rejected with HTTP 400
- `BOX_SEARCH_FOR_CONTENT` requires either `query` or `mdfilters` parameter
- Misconfigured filters can silently omit expected items; validate with small test queries first
- Boolean operators (`AND`, `OR`, `NOT`) must be uppercase
- `BOX_LIST_ITEMS_IN_FOLDER` requires pagination via `marker` or `offset`/`usemarker`; partial listings are common
- Standard folders sort items by type first (folders before files before web links)

### 3. Manage Folders

**When to use**: User wants to create, update, move, copy, or delete folders

**Tool sequence**:
1. `BOX_GET_FOLDER_INFORMATION` - Verify folder exists and check permissions [Prerequisite]
2. `BOX_CREATE_FOLDER` - Create a new folder [Required for create]
3. `BOX_UPDATE_FOLDER` - Rename, move, or update folder settings [Required for update]
4. `BOX_COPY_FOLDER` - Copy a folder to a new location [Optional]
5. `BOX_DELETE_FOLDER` - Move folder to trash [Required for delete]
6. `BOX_PERMANENTLY_REMOVE_FOLDER` - Permanently delete a trashed folder [Optional]

**Key parameters**:
- `name`: Folder name (no `/`, `\`, trailing spaces, or `.`/`..`)
- `parent__id`: Parent folder ID (use `"0"` for root)
- `folder_id`: Target folder ID for operations
- `parent.id`: Destination folder ID for moves via `BOX_UPDATE_FOLDER`
- `recursive`: Set `true` to delete non-empty folders
- `shared_link`: Object with `access`, `password`, `permissions` for creating shared links on folders
- `description`, `tags`: Optional metadata fields

**Pitfalls**:
- `BOX_DELETE_FOLDER` moves to trash by default; use `BOX_PERMANENTLY_REMOVE_FOLDER` for permanent deletion
- Non-empty folders require `recursive: true` for deletion
- Root folder (ID `"0"`) cannot be copied or deleted
- Folder names cannot contain `/`, `\`, non-printable ASCII, or trailing spaces
- Moving folders requires setting `parent.id` via `BOX_UPDATE_FOLDER`

### 4. Share Files and Manage Collaborations

**When to use**: User wants to share files, manage access, or handle collaborations

**Tool sequence**:
1. `BOX_GET_FILE_INFORMATION` - Get file details and current sharing status [Prerequisite]
2. `BOX_LIST_FILE_COLLABORATIONS` - List who has access to a file [Required]
3. `BOX_UPDATE_COLLABORATION` - Change access level or accept/reject invitations [Required]
4. `BOX_GET_COLLABORATION` - Get details of a specific collaboration [Optional]
5. `BOX_UPDATE_FILE` - Create shared links, lock files, or update permissions [Optional]
6. `BOX_UPDATE_FOLDER` - Create shared links on folders [Optional]

**Key parameters**:
- `collaboration_id`: Unique collaboration identifier
- `role`: Access level (`"editor"`, `"viewer"`, `"co-owner"`, `"owner"`, `"previewer"`, `"uploader"`, `"viewer uploader"`, `"previewer uploader"`)
- `status`: `"accepted"`, `"pending"`, or `"rejected"` for collaboration invites
- `file_id`: File to share or manage
- `lock__access`: Set to `"lock"` to lock a file
- `permissions__can__download`: `"company"` or `"open"` for download permissions

**Pitfalls**:
- Only certain roles can invite collaborators; insufficient permissions cause authorization errors
- `can_view_path` increases load time for the invitee's "All Files" page; limit to 1000 per user
- Collaboration expiration requires enterprise admin settings to be enabled
- Nested parameter names use double underscores (e.g., `lock__access`, `parent__id`)

### 5. Box Sign Requests

**When to use**: User wants to manage document signature requests

**Tool sequence**:
1. `BOX_LIST_BOX_SIGN_REQUESTS` - List all signature requests [Required]
2. `BOX_GET_BOX_SIGN_REQUEST_BY_ID` - Get details of a specific sign request [Optional]
3. `BOX_CANCEL_BOX_SIGN_REQUEST` - Cancel a pending sign request [Optional]

**Key parameters**:
- `sign_request_id`: UUID of the sign request
- `shared_requests`: Set `true` to include requests where user is a collaborator (not owner)
- `senders`: Filter by sender emails (requires `shared_requests: true`)
- `limit` / `marker`: Pagination parameters

**Pitfalls**:
- Requires Box Sign to be enabled for the enterprise account
- Deleted sign files or parent folders cause requests to not appear in listings
- Only the creator can cancel a sign request
- Sign request statuses include: `converting`, `created`, `sent`, `viewed`, `signed`, `declined`, `cancelled`, `expired`, `error_converting`, `error_sending`

## Common Patterns

### ID Resolution
Box uses numeric string IDs for all entities:
- **Root folder**: Always ID `"0"`
- **File ID from URL**: `https://*.app.box.com/files/123` gives file_id `"123"`
- **Folder ID from URL**: `https://*.app.box.com/folder/123` gives folder_id `"123"`
- **Search to ID**: Use `BOX_SEARCH_FOR_CONTENT` to find items, then extract IDs from results
- **ETag**: Use `if_match` with file's ETag for safe concurrent delete operations

### Pagination
Box supports two pagination methods:
- **Offset-based**: Use `offset` + `limit` (max offset 10000)
- **Marker-based**: Set `usemarker: true` and follow `marker` from responses (preferred for large datasets)
- Always paginate to completion to avoid partial results

### Nested Parameters
Box tools use double underscore notation for nested objects:
- `parent__id` for parent folder reference
- `lock__access`, `lock__expires__at`, `lock__is__download__prevented` for file locks
- `permissions__can__download` for download permissions

## Known Pitfalls

### ID Formats
- All IDs are numeric strings (e.g., `"123456"`, not integers)
- Root folder is always `"0"`
- File and folder IDs can be extracted from Box web app URLs

### Rate Limits
- Box API has per-endpoint rate limits
- Search and list operations should use pagination responsibly
- Bulk operations should include delays between requests

### Parameter Quirks
- `fields` parameter changes response shape: when specified, only mini representation + requested fields are returned
- Search requires either `query` or `mdfilters`; both are optional individually but one must be present
- `BOX_UPDATE_FILE` with `lock` set to `null` removes the lock (raw API only)
- Metadata query `from` field format: `enterprise_{enterprise_id}.templateKey` or `global.templateKey`

### Permissions
- Deletions fail without sufficient permissions; always handle error responses
- Collaboration roles determine what operations are allowed
- Enterprise settings may restrict certain sharing options

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Search content | `BOX_SEARCH_FOR_CONTENT` | `query`, `type`, `ancestor_folder_ids` |
| List folder items | `BOX_LIST_ITEMS_IN_FOLDER` | `folder_id`, `limit`, `marker` |
| Get file info | `BOX_GET_FILE_INFORMATION` | `file_id`, `fields` |
| Get folder info | `BOX_GET_FOLDER_INFORMATION` | `folder_id`, `fields` |
| Upload file | `BOX_UPLOAD_FILE` | `file`, `parent_id` |
| Download file | `BOX_DOWNLOAD_FILE` | `file_id` |
| Create folder | `BOX_CREATE_FOLDER` | `name`, `parent__id` |
| Update folder | `BOX_UPDATE_FOLDER` | `folder_id`, `name`, `parent` |
| Copy folder | `BOX_COPY_FOLDER` | `folder_id`, `parent__id` |
| Delete folder | `BOX_DELETE_FOLDER` | `folder_id`, `recursive` |
| Permanently delete folder | `BOX_PERMANENTLY_REMOVE_FOLDER` | folder_id |
| Update file | `BOX_UPDATE_FILE` | `file_id`, `name`, `parent__id` |
| Delete file | `BOX_DELETE_FILE` | `file_id`, `if_match` |
| List collaborations | `BOX_LIST_FILE_COLLABORATIONS` | `file_id` |
| Update collaboration | `BOX_UPDATE_COLLABORATION` | `collaboration_id`, `role` |
| Get collaboration | `BOX_GET_COLLABORATION` | `collaboration_id` |
| Query by metadata | `BOX_QUERY_FILES_FOLDERS_BY_METADATA` | `from`, `ancestor_folder_id`, `query` |
| List collections | `BOX_LIST_ALL_COLLECTIONS` | (none) |
| List collection items | `BOX_LIST_COLLECTION_ITEMS` | `collection_id` |
| List sign requests | `BOX_LIST_BOX_SIGN_REQUESTS` | `limit`, `marker` |
| Get sign request | `BOX_GET_BOX_SIGN_REQUEST_BY_ID` | `sign_request_id` |
| Cancel sign request | `BOX_CANCEL_BOX_SIGN_REQUEST` | `sign_request_id` |
| Recent items | `BOX_LIST_RECENTLY_ACCESSED_ITEMS` | (none) |
| Create zip download | `BOX_CREATE_ZIP_DOWNLOAD` | item IDs |
