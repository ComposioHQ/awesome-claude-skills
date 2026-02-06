---
name: google-drive-automation
description: Automate Google Drive file operations (upload, download, search, share, organize) via Rube MCP (Composio). Upload/download files, manage folders, share with permissions, and search across drives programmatically.
requires:
  mcp: [rube]
---

# Google Drive Automation via Rube MCP

Automate Google Drive workflows including file upload/download, search, folder management, sharing/permissions, and organization through Composio's Google Drive toolkit.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Google Drive connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `googledrive`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `googledrive`
3. If connection is not ACTIVE, follow the returned auth link to complete Google OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Upload and Download Files

**When to use**: User wants to upload files to or download files from Google Drive

**Tool sequence**:
1. `GOOGLEDRIVE_FIND_FILE` - Locate target folder for upload [Prerequisite]
2. `GOOGLEDRIVE_UPLOAD_FILE` - Upload a file (max 5MB) [Required]
3. `GOOGLEDRIVE_RESUMABLE_UPLOAD` - Upload large files [Fallback]
4. `GOOGLEDRIVE_DOWNLOAD_FILE` - Download a file by ID [Required]
5. `GOOGLEDRIVE_DOWNLOAD_FILE_OPERATION` - Track long-running downloads [Fallback]
6. `GOOGLEDRIVE_GET_FILE_METADATA` - Verify file after upload/download [Optional]

**Key parameters**:
- `file_to_upload`: Object with `name`, `mimetype`, and `s3key` (file must be in internal storage)
- `folder_to_upload_to`: Target folder ID (optional; uploads to root if omitted)
- `file_id`: ID of file to download
- `mime_type`: Export format for Google Workspace files only (omit for native files)

**Pitfalls**:
- `GOOGLEDRIVE_UPLOAD_FILE` requires `file_to_upload.s3key`; files must already be in internal storage
- For non-Google formats (Excel, PDF), do NOT set `mime_type`; it causes errors for native files
- Download responses provide a temporary URL at `data.downloaded_file_content.s3url`, not inline bytes
- Use `GOOGLEDRIVE_RESUMABLE_UPLOAD` for files >5MB or when basic uploads fail

### 2. Search and List Files

**When to use**: User wants to find specific files or browse Drive contents

**Tool sequence**:
1. `GOOGLEDRIVE_FIND_FILE` - Search by name, content, type, date, or folder [Required]
2. `GOOGLEDRIVE_LIST_FILES` - Browse files with folder scoping [Alternative]
3. `GOOGLEDRIVE_LIST_SHARED_DRIVES` - Enumerate shared drives [Optional]
4. `GOOGLEDRIVE_GET_FILE_METADATA` - Get detailed file info [Optional]
5. `GOOGLEDRIVE_GET_ABOUT` - Check storage quota and supported formats [Optional]

**Key parameters**:
- `q`: Drive query string (e.g., "name contains 'report'", "mimeType = 'application/pdf'")
- `corpora`: Search scope ('user', 'domain', 'drive', 'allDrives')
- `fields`: Response fields to include (e.g., 'files(id,name,mimeType)')
- `orderBy`: Sort key ('modifiedTime desc', 'name', 'quotaBytesUsed desc')
- `pageSize`: Results per page (max 1000)
- `pageToken`: Pagination cursor from `nextPageToken`
- `folder_id`: Scope search to a specific folder

**Pitfalls**:
- 403 PERMISSION_DENIED if OAuth scopes insufficient for shared drives
- Pagination required; files are in `response.data.files`; follow `nextPageToken` until exhausted
- `corpora="domain"` may trigger 400; try `"allDrives"` with `includeItemsFromAllDrives=true`
- Query complexity limits: >5-10 OR clauses may error "The query is too complex"
- Wildcards (*) NOT supported in `name`; use `contains` for partial matching
- 'My Drive' is NOT searchable by name; use `folder_id='root'` for root folder
- User email searches: use `'user@example.com' in owners` (NOT `owner:user@example.com`)

### 3. Share Files and Manage Permissions

**When to use**: User wants to share files or manage access permissions

**Tool sequence**:
1. `GOOGLEDRIVE_FIND_FILE` - Locate the file to share [Prerequisite]
2. `GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE` - Set sharing permission [Required]
3. `GOOGLEDRIVE_LIST_PERMISSIONS` - View current permissions [Optional]
4. `GOOGLEDRIVE_GET_PERMISSION` - Inspect a specific permission [Optional]
5. `GOOGLEDRIVE_UPDATE_PERMISSION` - Modify existing permission [Optional]
6. `GOOGLEDRIVE_DELETE_PERMISSION` - Revoke access [Optional]

**Key parameters**:
- `file_id`: ID of file to share
- `type`: 'user', 'group', 'domain', or 'anyone'
- `role`: 'owner', 'organizer', 'fileOrganizer', 'writer', 'commenter', 'reader'
- `email_address`: Required for type='user' or 'group'
- `domain`: Required for type='domain'
- `transfer_ownership`: Required when role='owner'

**Pitfalls**:
- Invalid type/email combinations trigger 4xx errors
- Using `type='anyone'` or powerful roles is risky; get explicit user confirmation
- Org policies may block certain sharing types, causing 403
- Permission changes may take time to propagate
- Use `GMAIL_SEARCH_PEOPLE` to resolve contact names to emails before sharing

### 4. Create and Organize Folders

**When to use**: User wants to create folder structures or move files between folders

**Tool sequence**:
1. `GOOGLEDRIVE_FIND_FILE` - Check if folder already exists [Prerequisite]
2. `GOOGLEDRIVE_CREATE_FOLDER` - Create a new folder [Required]
3. `GOOGLEDRIVE_GET_FILE_METADATA` - Verify created folder [Optional]
4. `GOOGLEDRIVE_MOVE_FILE` - Move files between folders [Optional]
5. `GOOGLEDRIVE_UPDATE_FILE_PUT` - Update file metadata/parents [Alternative]

**Key parameters**:
- `name`: Folder name
- `parent_id`: Parent folder ID (NOT name); omit for root
- `file_id`: File to move
- `add_parents`: Destination folder ID for move
- `remove_parents`: Source folder ID to remove from

**Pitfalls**:
- `GOOGLEDRIVE_CREATE_FOLDER` requires `parent_id` as an ID, not a folder name
- Using `parent_id="root"` creates at top level; for nested paths, chain folder IDs
- `GOOGLEDRIVE_FIND_FILE` returns ~100 items/page; follow `nextPageToken` for large drives
- Move operations can leave items with multiple parents; use `remove_parents` for true moves
- Always verify parent folder exists before creating children

## Common Patterns

### ID Resolution
- **File/folder name -> ID**: `GOOGLEDRIVE_FIND_FILE` with `q` parameter
- **Root folder**: Use `folder_id='root'` or `'root' in parents`
- **Shared drive -> driveId**: `GOOGLEDRIVE_LIST_SHARED_DRIVES`
- **Contact name -> email**: `GMAIL_SEARCH_PEOPLE` (for sharing)

### Query Syntax
Google Drive uses a specific query language:
- Name search: `"name contains 'report'"` or `"name = 'exact.pdf'"`
- Type filter: `"mimeType = 'application/pdf'"` or `"mimeType = 'application/vnd.google-apps.folder'"`
- Folder scoping: `"'FOLDER_ID' in parents"`
- Date filter: `"modifiedTime > '2024-01-01T00:00:00'"`
- Combine with `and`/`or`/`not`: `"name contains 'report' and trashed = false"`
- Boolean filters: `"sharedWithMe = true"`, `"starred = true"`, `"trashed = false"`

### Pagination
- Follow `nextPageToken` until absent for complete results
- Set `pageSize` explicitly (default 100, max 1000)
- De-duplicate results if running multiple searches

### Export Formats
For Google Workspace files, set `mime_type` to export:
- **Docs**: `application/pdf`, `text/plain`, `text/html`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **Sheets**: `text/csv`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Slides**: `application/pdf`, `application/vnd.openxmlformats-officedocument.presentationml.presentation`

## Known Pitfalls

- **Internal storage required**: Upload requires files in internal S3 storage (s3key)
- **Export vs download**: Set `mime_type` ONLY for Google Workspace files; omit for native files
- **Temporary URLs**: Downloaded content via `s3url` is temporary; fetch promptly
- **Query complexity**: >5-10 OR clauses may error; split complex searches into multiple queries
- **Shared drive scoping**: Missing drive permissions yield empty results; verify access first
- **No wildcards**: Use `contains` operator instead of `*` for partial name matching
- **Folder creation chains**: Always pass folder IDs (not names) as `parent_id`
- **Multiple parents**: Move operations may leave items with multiple parents; use `remove_parents`
- **Rate limits**: Heavy searches/exports can trigger 403/429; implement backoff

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Search files | `GOOGLEDRIVE_FIND_FILE` | `q`, `corpora`, `pageSize` |
| List files | `GOOGLEDRIVE_LIST_FILES` | `folderId`, `q`, `orderBy` |
| Upload file | `GOOGLEDRIVE_UPLOAD_FILE` | `file_to_upload`, `folder_to_upload_to` |
| Resumable upload | `GOOGLEDRIVE_RESUMABLE_UPLOAD` | file data |
| Download file | `GOOGLEDRIVE_DOWNLOAD_FILE` | `file_id`, `mime_type` (Workspace only) |
| File metadata | `GOOGLEDRIVE_GET_FILE_METADATA` | `fileId`, `fields` |
| Create folder | `GOOGLEDRIVE_CREATE_FOLDER` | `name`, `parent_id` |
| Move file | `GOOGLEDRIVE_MOVE_FILE` | `file_id`, `add_parents`, `remove_parents` |
| Share file | `GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE` | `file_id`, `role`, `type`, `email_address` |
| List permissions | `GOOGLEDRIVE_LIST_PERMISSIONS` | `fileId` |
| Update permission | `GOOGLEDRIVE_UPDATE_PERMISSION` | file_id, permission_id |
| Delete permission | `GOOGLEDRIVE_DELETE_PERMISSION` | file_id, permission_id |
| List shared drives | `GOOGLEDRIVE_LIST_SHARED_DRIVES` | `pageSize` |
| Drive info | `GOOGLEDRIVE_GET_ABOUT` | (none) |
| Create shortcut | `GOOGLEDRIVE_CREATE_SHORTCUT_TO_FILE` | target file_id |
