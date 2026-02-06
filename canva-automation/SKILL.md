---
name: canva-automation
description: "Automate Canva tasks via Rube MCP (Composio): designs, exports, folders, brand templates, autofill. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Canva Automation via Rube MCP

Automate Canva design operations through Composio's Canva toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Canva connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `canva`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `canva`
3. If connection is not ACTIVE, follow the returned auth link to complete Canva OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List and Browse Designs

**When to use**: User wants to find existing designs or browse their Canva library

**Tool sequence**:
1. `CANVA_LIST_USER_DESIGNS` - List all designs with optional filters [Required]

**Key parameters**:
- `query`: Search term to filter designs by name
- `continuation`: Pagination token from previous response
- `ownership`: Filter by 'owned', 'shared', or 'any'
- `sort_by`: Sort field (e.g., 'modified_at', 'title')

**Pitfalls**:
- Results are paginated; follow `continuation` token until absent
- Deleted designs may still appear briefly; check design status
- Search is substring-based, not fuzzy matching

### 2. Create and Design

**When to use**: User wants to create a new Canva design from scratch or from a template

**Tool sequence**:
1. `CANVA_ACCESS_USER_SPECIFIC_BRAND_TEMPLATES_LIST` - Browse available brand templates [Optional]
2. `CANVA_CREATE_CANVA_DESIGN_WITH_OPTIONAL_ASSET` - Create a new design [Required]

**Key parameters**:
- `design_type`: Type of design (e.g., 'Presentation', 'Poster', 'SocialMedia')
- `title`: Name for the new design
- `asset_id`: Optional asset to include in the design
- `width` / `height`: Custom dimensions in pixels

**Pitfalls**:
- Design type must match Canva's predefined types exactly
- Custom dimensions have minimum and maximum limits
- Asset must be uploaded first via CANVA_CREATE_ASSET_UPLOAD_JOB before referencing

### 3. Upload Assets

**When to use**: User wants to upload images or files to Canva for use in designs

**Tool sequence**:
1. `CANVA_CREATE_ASSET_UPLOAD_JOB` - Initiate the asset upload [Required]
2. `CANVA_FETCH_ASSET_UPLOAD_JOB_STATUS` - Poll until upload completes [Required]

**Key parameters**:
- `name`: Display name for the asset
- `url`: Public URL of the file to upload (for URL-based uploads)
- `job_id`: Upload job ID returned from step 1 (for status polling)

**Pitfalls**:
- Upload is asynchronous; you MUST poll the job status until it completes
- Supported formats include PNG, JPG, SVG, MP4, GIF
- File size limits apply; large files may take longer to process
- The `job_id` from CREATE returns the ID needed for status polling
- Status values: 'in_progress', 'success', 'failed'

### 4. Export Designs

**When to use**: User wants to download or export a Canva design as PDF, PNG, or other format

**Tool sequence**:
1. `CANVA_LIST_USER_DESIGNS` - Find the design to export [Prerequisite]
2. `CANVA_CREATE_CANVA_DESIGN_EXPORT_JOB` - Start the export process [Required]
3. `CANVA_GET_DESIGN_EXPORT_JOB_RESULT` - Poll until export completes and get download URL [Required]

**Key parameters**:
- `design_id`: ID of the design to export
- `format`: Export format ('pdf', 'png', 'jpg', 'svg', 'mp4', 'gif', 'pptx')
- `pages`: Specific page numbers to export (array)
- `quality`: Export quality ('regular', 'high')
- `job_id`: Export job ID for polling status

**Pitfalls**:
- Export is asynchronous; you MUST poll the job result until it completes
- Download URLs from completed exports expire after a limited time
- Large designs with many pages take longer to export
- Not all formats support all design types (e.g., MP4 only for animations)
- Poll interval: wait 2-3 seconds between status checks

### 5. Organize with Folders

**When to use**: User wants to create folders or organize designs into folders

**Tool sequence**:
1. `CANVA_POST_FOLDERS` - Create a new folder [Required]
2. `CANVA_MOVE_ITEM_TO_SPECIFIED_FOLDER` - Move designs into folders [Optional]

**Key parameters**:
- `name`: Folder name
- `parent_folder_id`: Parent folder for nested organization
- `item_id`: ID of the design or asset to move
- `folder_id`: Target folder ID

**Pitfalls**:
- Folder names must be unique within the same parent folder
- Moving items between folders updates their location immediately
- Root-level folders have no parent_folder_id

### 6. Autofill from Brand Templates

**When to use**: User wants to generate designs by filling brand template placeholders with data

**Tool sequence**:
1. `CANVA_ACCESS_USER_SPECIFIC_BRAND_TEMPLATES_LIST` - List available brand templates [Required]
2. `CANVA_INITIATE_CANVA_DESIGN_AUTOFILL_JOB` - Start autofill with data [Required]

**Key parameters**:
- `brand_template_id`: ID of the brand template to use
- `title`: Title for the generated design
- `data`: Key-value mapping of placeholder names to replacement values

**Pitfalls**:
- Template placeholders must match exactly (case-sensitive)
- Autofill is asynchronous; poll for completion
- Only brand templates support autofill, not regular designs
- Data values must match the expected type for each placeholder (text, image URL)

## Common Patterns

### Async Job Pattern

Many Canva operations are asynchronous:
```
1. Initiate job (upload, export, autofill) -> get job_id
2. Poll status endpoint with job_id every 2-3 seconds
3. Check for 'success' or 'failed' status
4. On success, extract result (asset_id, download_url, design_id)
```

### ID Resolution

**Design name -> Design ID**:
```
1. Call CANVA_LIST_USER_DESIGNS with query=design_name
2. Find matching design in results
3. Extract id field
```

**Brand template name -> Template ID**:
```
1. Call CANVA_ACCESS_USER_SPECIFIC_BRAND_TEMPLATES_LIST
2. Find template by name
3. Extract brand_template_id
```

### Pagination

- Check response for `continuation` token
- Pass token in next request's `continuation` parameter
- Continue until `continuation` is absent or empty

## Known Pitfalls

**Async Operations**:
- Uploads, exports, and autofills are all asynchronous
- Always poll job status; do not assume immediate completion
- Download URLs from exports expire; use them promptly

**Asset Management**:
- Assets must be uploaded before they can be used in designs
- Upload job must reach 'success' status before the asset_id is valid
- Supported formats vary; check Canva documentation for current limits

**Rate Limits**:
- Canva API has rate limits per endpoint
- Implement exponential backoff for bulk operations
- Batch operations where possible to reduce API calls

**Response Parsing**:
- Response data may be nested under `data` key
- Job status responses include different fields based on completion state
- Parse defensively with fallbacks for optional fields

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List designs | CANVA_LIST_USER_DESIGNS | query, continuation |
| Create design | CANVA_CREATE_CANVA_DESIGN_WITH_OPTIONAL_ASSET | design_type, title |
| Upload asset | CANVA_CREATE_ASSET_UPLOAD_JOB | name, url |
| Check upload | CANVA_FETCH_ASSET_UPLOAD_JOB_STATUS | job_id |
| Export design | CANVA_CREATE_CANVA_DESIGN_EXPORT_JOB | design_id, format |
| Get export | CANVA_GET_DESIGN_EXPORT_JOB_RESULT | job_id |
| Create folder | CANVA_POST_FOLDERS | name, parent_folder_id |
| Move to folder | CANVA_MOVE_ITEM_TO_SPECIFIED_FOLDER | item_id, folder_id |
| List templates | CANVA_ACCESS_USER_SPECIFIC_BRAND_TEMPLATES_LIST | (none) |
| Autofill template | CANVA_INITIATE_CANVA_DESIGN_AUTOFILL_JOB | brand_template_id, data |
