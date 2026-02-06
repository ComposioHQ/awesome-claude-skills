---
name: miro-automation
description: "Automate Miro tasks via Rube MCP (Composio): boards, items, sticky notes, frames, sharing, connectors. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Miro Automation via Rube MCP

Automate Miro whiteboard operations through Composio's Miro toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Miro connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `miro`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `miro`
3. If connection is not ACTIVE, follow the returned auth link to complete Miro OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List and Browse Boards

**When to use**: User wants to find boards or get board details

**Tool sequence**:
1. `MIRO_GET_BOARDS2` - List all accessible boards [Required]
2. `MIRO_GET_BOARD` - Get detailed info for a specific board [Optional]

**Key parameters**:
- `query`: Search term to filter boards by name
- `sort`: Sort by 'default', 'last_modified', 'last_opened', 'last_created', 'alphabetically'
- `limit`: Number of results per page (max 50)
- `offset`: Pagination offset
- `board_id`: Specific board ID for detailed retrieval

**Pitfalls**:
- Pagination uses offset-based approach, not cursor-based
- Maximum 50 boards per page; iterate with offset for full list
- Board IDs are long alphanumeric strings; always resolve by search first

### 2. Create Boards and Items

**When to use**: User wants to create a new board or add items to an existing board

**Tool sequence**:
1. `MIRO_CREATE_BOARD` - Create a new empty board [Optional]
2. `MIRO_CREATE_STICKY_NOTE_ITEM` - Add sticky notes to a board [Optional]
3. `MIRO_CREATE_FRAME_ITEM2` - Add frames to organize content [Optional]
4. `MIRO_CREATE_ITEMS_IN_BULK` - Add multiple items at once [Optional]

**Key parameters**:
- `name` / `description`: Board name and description (for CREATE_BOARD)
- `board_id`: Target board ID (required for all item creation)
- `data`: Content object with `content` field for sticky note text
- `style`: Styling object with `fillColor` for sticky note color
- `position`: Object with `x` and `y` coordinates
- `geometry`: Object with `width` and `height`

**Pitfalls**:
- `board_id` is required for ALL item operations; resolve via GET_BOARDS2 first
- Sticky note colors use hex codes (e.g., '#FF0000') in the `fillColor` field
- Position coordinates use the board's coordinate system (origin at center)
- BULK create has a maximum items-per-request limit; check current schema
- Frame items require `geometry` with both width and height

### 3. Browse and Manage Board Items

**When to use**: User wants to view, find, or organize items on a board

**Tool sequence**:
1. `MIRO_GET_BOARD_ITEMS` - List all items on a board [Required]
2. `MIRO_GET_CONNECTORS2` - List connections between items [Optional]

**Key parameters**:
- `board_id`: Target board ID (required)
- `type`: Filter by item type ('sticky_note', 'shape', 'text', 'frame', 'image', 'card')
- `limit`: Number of items per page
- `cursor`: Pagination cursor from previous response

**Pitfalls**:
- Results are paginated; follow `cursor` until absent for complete item list
- Item types must match Miro's predefined types exactly
- Large boards may have thousands of items; use type filtering to narrow results
- Connectors are separate from items; use GET_CONNECTORS2 for relationship data

### 4. Share and Collaborate on Boards

**When to use**: User wants to share a board with team members or manage access

**Tool sequence**:
1. `MIRO_GET_BOARDS2` - Find the board to share [Prerequisite]
2. `MIRO_SHARE_BOARD` - Share the board with users [Required]
3. `MIRO_GET_BOARD_MEMBERS` - Verify current board members [Optional]

**Key parameters**:
- `board_id`: Board to share (required)
- `emails`: Array of email addresses to invite
- `role`: Access level ('viewer', 'commenter', 'editor')
- `message`: Optional invitation message

**Pitfalls**:
- Email addresses must be valid; invalid emails cause the entire request to fail
- Role must be one of the predefined values; case-sensitive
- Sharing with users outside the organization may require admin approval
- GET_BOARD_MEMBERS returns all members including the owner

### 5. Create Visual Connections

**When to use**: User wants to connect items on a board with lines or arrows

**Tool sequence**:
1. `MIRO_GET_BOARD_ITEMS` - Find items to connect [Prerequisite]
2. `MIRO_GET_CONNECTORS2` - View existing connections [Optional]

**Key parameters**:
- `board_id`: Target board ID
- `startItem`: Object with `id` of the source item
- `endItem`: Object with `id` of the target item
- `style`: Connector style (line type, color, arrows)

**Pitfalls**:
- Both start and end items must exist on the same board
- Item IDs are required for connections; resolve via GET_BOARD_ITEMS first
- Connector styles vary; check available options in schema
- Self-referencing connections (same start and end) are not allowed

## Common Patterns

### ID Resolution

**Board name -> Board ID**:
```
1. Call MIRO_GET_BOARDS2 with query=board_name
2. Find board by name in results
3. Extract id field
```

**Item lookup on board**:
```
1. Call MIRO_GET_BOARD_ITEMS with board_id and optional type filter
2. Find item by content or position
3. Extract item id for further operations
```

### Pagination

- Boards: Use `offset` and `limit` (offset-based)
- Board items: Use `cursor` and `limit` (cursor-based)
- Continue until no more results or cursor is absent
- Default page sizes vary by endpoint

### Coordinate System

- Board origin (0,0) is at the center
- Positive X is right, positive Y is down
- Items positioned by their center point
- Use `position: {x: 0, y: 0}` for center of board
- Frames define bounded areas; items inside inherit frame position

## Known Pitfalls

**Board IDs**:
- Board IDs are required for virtually all operations
- Always resolve board names to IDs via GET_BOARDS2 first
- Do not hardcode board IDs; they vary by account

**Item Creation**:
- Each item type has different required fields
- Sticky notes need `data.content` for text
- Frames need `geometry.width` and `geometry.height`
- Position defaults to (0,0) if not specified; items may overlap

**Rate Limits**:
- Miro API has rate limits per token
- Bulk operations preferred over individual item creation
- Use MIRO_CREATE_ITEMS_IN_BULK for multiple items

**Response Parsing**:
- Response data may be nested under `data` key
- Item types determine which fields are present in response
- Parse defensively; optional fields may be absent

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List boards | MIRO_GET_BOARDS2 | query, sort, limit, offset |
| Get board details | MIRO_GET_BOARD | board_id |
| Create board | MIRO_CREATE_BOARD | name, description |
| Add sticky note | MIRO_CREATE_STICKY_NOTE_ITEM | board_id, data, style, position |
| Add frame | MIRO_CREATE_FRAME_ITEM2 | board_id, data, geometry, position |
| Bulk add items | MIRO_CREATE_ITEMS_IN_BULK | board_id, items |
| Get board items | MIRO_GET_BOARD_ITEMS | board_id, type, cursor |
| Share board | MIRO_SHARE_BOARD | board_id, emails, role |
| Get members | MIRO_GET_BOARD_MEMBERS | board_id |
| Get connectors | MIRO_GET_CONNECTORS2 | board_id |
