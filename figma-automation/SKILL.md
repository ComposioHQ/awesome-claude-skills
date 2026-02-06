---
name: figma-automation
description: "Automate Figma tasks via Rube MCP (Composio): files, components, design tokens, comments, exports. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Figma Automation via Rube MCP

Automate Figma operations through Composio's Figma toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Figma connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `figma`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `figma`
3. If connection is not ACTIVE, follow the returned auth link to complete Figma auth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Get File Data and Components

**When to use**: User wants to inspect Figma design files or extract component information

**Tool sequence**:
1. `FIGMA_DISCOVER_FIGMA_RESOURCES` - Extract IDs from Figma URLs [Prerequisite]
2. `FIGMA_GET_FILE_JSON` - Get file data (simplified by default) [Required]
3. `FIGMA_GET_FILE_NODES` - Get specific node data [Optional]
4. `FIGMA_GET_FILE_COMPONENTS` - List published components [Optional]
5. `FIGMA_GET_FILE_COMPONENT_SETS` - List component sets [Optional]

**Key parameters**:
- `file_key`: File key from URL (e.g., 'abc123XYZ' from figma.com/design/abc123XYZ/...)
- `ids`: Comma-separated node IDs (NOT an array)
- `depth`: Tree traversal depth (2 for pages and top-level children)
- `simplify`: True for AI-friendly format (70%+ size reduction)

**Pitfalls**:
- Only supports Design files; FigJam boards and Slides return 400 errors
- `ids` must be a comma-separated string, not an array
- Node IDs may be dash-formatted (1-541) in URLs but need colon format (1:541) for API
- Broad ids/depth can trigger oversized payloads (413); narrow scope or reduce depth
- Response data may be in `data_preview` instead of `data`

### 2. Export and Render Images

**When to use**: User wants to export design assets as images

**Tool sequence**:
1. `FIGMA_GET_FILE_JSON` - Find node IDs to export [Prerequisite]
2. `FIGMA_RENDER_IMAGES_OF_FILE_NODES` - Render nodes as images [Required]
3. `FIGMA_DOWNLOAD_FIGMA_IMAGES` - Download rendered images [Optional]
4. `FIGMA_GET_IMAGE_FILLS` - Get image fill URLs [Optional]

**Key parameters**:
- `file_key`: File key
- `ids`: Comma-separated node IDs to render
- `format`: 'png', 'svg', 'jpg', or 'pdf'
- `scale`: Scale factor (0.01-4.0) for PNG/JPG
- `images`: Array of {node_id, file_name, format} for downloads

**Pitfalls**:
- Images return as node_id-to-URL map; some IDs may be null (failed renders)
- URLs are temporary (valid ~30 days)
- Images capped at 32 megapixels; larger requests auto-scaled down

### 3. Extract Design Tokens

**When to use**: User wants to extract design tokens for development

**Tool sequence**:
1. `FIGMA_EXTRACT_DESIGN_TOKENS` - Extract colors, typography, spacing [Required]
2. `FIGMA_DESIGN_TOKENS_TO_TAILWIND` - Convert to Tailwind config [Optional]

**Key parameters**:
- `file_key`: File key
- `include_local_styles`: Include local styles (default true)
- `include_variables`: Include Figma variables
- `tokens`: Full tokens object from extraction (for Tailwind conversion)

**Pitfalls**:
- Tailwind conversion requires the full tokens object including total_tokens and sources
- Do not strip fields from the extraction response before passing to conversion

### 4. Manage Comments and Versions

**When to use**: User wants to view or add comments, or inspect version history

**Tool sequence**:
1. `FIGMA_GET_COMMENTS_IN_A_FILE` - List all file comments [Optional]
2. `FIGMA_ADD_A_COMMENT_TO_A_FILE` - Add a comment [Optional]
3. `FIGMA_GET_REACTIONS_FOR_A_COMMENT` - Get comment reactions [Optional]
4. `FIGMA_GET_VERSIONS_OF_A_FILE` - Get version history [Optional]

**Key parameters**:
- `file_key`: File key
- `as_md`: Return comments in Markdown format
- `message`: Comment text
- `comment_id`: Comment ID for reactions

**Pitfalls**:
- Comments can be positioned on specific nodes using client_meta
- Reply comments cannot be nested (only one level of replies)

### 5. Browse Projects and Teams

**When to use**: User wants to list team projects or files

**Tool sequence**:
1. `FIGMA_GET_PROJECTS_IN_A_TEAM` - List team projects [Optional]
2. `FIGMA_GET_FILES_IN_A_PROJECT` - List project files [Optional]
3. `FIGMA_GET_TEAM_STYLES` - List team published styles [Optional]

**Key parameters**:
- `team_id`: Team ID from URL (figma.com/files/team/TEAM_ID/...)
- `project_id`: Project ID

**Pitfalls**:
- Team ID cannot be obtained programmatically; extract from Figma URL
- Only published styles/components are returned by team endpoints

## Common Patterns

### URL Parsing

Extract IDs from Figma URLs:
```
1. Call FIGMA_DISCOVER_FIGMA_RESOURCES with figma_url
2. Extract file_key, node_id, team_id from response
3. Convert dash-format node IDs (1-541) to colon format (1:541)
```

### Node Traversal

```
1. Call FIGMA_GET_FILE_JSON with depth=2 for overview
2. Identify target nodes from the response
3. Call again with specific ids and higher depth for details
```

## Known Pitfalls

**File Type Support**:
- GET_FILE_JSON only supports Design files (figma.com/design/ or figma.com/file/)
- FigJam boards (figma.com/board/) and Slides (figma.com/slides/) are NOT supported

**Node ID Formats**:
- URLs use dash format: `node-id=1-541`
- API uses colon format: `1:541`

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Parse URL | FIGMA_DISCOVER_FIGMA_RESOURCES | figma_url |
| Get file JSON | FIGMA_GET_FILE_JSON | file_key, ids, depth |
| Get nodes | FIGMA_GET_FILE_NODES | file_key, ids |
| Render images | FIGMA_RENDER_IMAGES_OF_FILE_NODES | file_key, ids, format |
| Download images | FIGMA_DOWNLOAD_FIGMA_IMAGES | file_key, images |
| Get component | FIGMA_GET_COMPONENT | file_key, node_id |
| File components | FIGMA_GET_FILE_COMPONENTS | file_key |
| Component sets | FIGMA_GET_FILE_COMPONENT_SETS | file_key |
| Design tokens | FIGMA_EXTRACT_DESIGN_TOKENS | file_key |
| Tokens to Tailwind | FIGMA_DESIGN_TOKENS_TO_TAILWIND | tokens |
| File comments | FIGMA_GET_COMMENTS_IN_A_FILE | file_key |
| Add comment | FIGMA_ADD_A_COMMENT_TO_A_FILE | file_key, message |
| File versions | FIGMA_GET_VERSIONS_OF_A_FILE | file_key |
| Team projects | FIGMA_GET_PROJECTS_IN_A_TEAM | team_id |
| Project files | FIGMA_GET_FILES_IN_A_PROJECT | project_id |
| Team styles | FIGMA_GET_TEAM_STYLES | team_id |
| File styles | FIGMA_GET_FILE_STYLES | file_key |
| Image fills | FIGMA_GET_IMAGE_FILLS | file_key |
