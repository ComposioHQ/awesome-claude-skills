---
name: confluence-automation
description: Automate Confluence page creation, content search, space management, labels, and hierarchy navigation via Rube MCP (Composio). Always search tools first for current schemas.
requires:
  mcp: [rube]
---

# Confluence Automation via Rube MCP

Automate Confluence operations including page creation and updates, content search with CQL, space management, label tagging, and page hierarchy navigation through Composio's Confluence toolkit.

**Toolkit docs**: [composio.dev/toolkits/confluence](https://composio.dev/toolkits/confluence)

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Confluence connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `confluence`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `confluence`
3. If connection is not ACTIVE, follow the returned auth link to complete Confluence OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create and Update Pages

**When to use**: User wants to create new documentation or update existing Confluence pages

**Tool sequence**:
1. `CONFLUENCE_GET_SPACES` - List spaces to find the target space ID [Prerequisite]
2. `CONFLUENCE_SEARCH_CONTENT` - Find existing page to avoid duplicates or locate parent [Optional]
3. `CONFLUENCE_GET_PAGE_BY_ID` - Get current page content and version number before updating [Prerequisite for updates]
4. `CONFLUENCE_CREATE_PAGE` - Create a new page in a space [Required for creation]
5. `CONFLUENCE_UPDATE_PAGE` - Update an existing page with new content and incremented version [Required for updates]
6. `CONFLUENCE_ADD_CONTENT_LABEL` - Tag the page with labels after creation [Optional]

**Key parameters**:
- `spaceId`: Space ID or key (e.g., `"DOCS"`, `"12345678"`) -- space keys are auto-converted to IDs
- `title`: Page title (must be unique within a space)
- `parentId`: Parent page ID for creating child pages; omit to place under space homepage
- `body.storage.value`: HTML/XHTML content in Confluence storage format
- `body.storage.representation`: Must be `"storage"` for create operations
- `version.number`: For updates, must be current version + 1
- `version.message`: Optional change description

**Pitfalls**:
- Confluence enforces unique page titles per space; creating a page with a duplicate title will fail
- `UPDATE_PAGE` requires `version.number` set to current version + 1; always fetch current version first with `GET_PAGE_BY_ID`
- Content must be in Confluence storage format (XHTML), not plain text or Markdown
- `CREATE_PAGE` uses `body.storage.value` while `UPDATE_PAGE` uses `body.value` with `body.representation`
- `GET_PAGE_BY_ID` requires a numeric long ID, not a UUID or string

### 2. Search Content

**When to use**: User wants to find pages, blog posts, or content across Confluence

**Tool sequence**:
1. `CONFLUENCE_SEARCH_CONTENT` - Keyword search with intelligent relevance ranking [Required]
2. `CONFLUENCE_CQL_SEARCH` - Advanced search using Confluence Query Language [Alternative]
3. `CONFLUENCE_GET_PAGE_BY_ID` - Hydrate full content for selected search results [Optional]
4. `CONFLUENCE_GET_PAGES` - Browse pages sorted by date when search relevance is weak [Fallback]

**Key parameters for SEARCH_CONTENT**:
- `query`: Search text matched against page titles with intelligent ranking
- `spaceKey`: Limit search to a specific space
- `limit`: Max results (default 25, max 250)
- `start`: Pagination offset (0-based)

**Key parameters for CQL_SEARCH**:
- `cql`: CQL query string (e.g., `text ~ "API docs" AND space = DOCS AND type = page`)
- `expand`: Comma-separated properties (e.g., `content.space`, `content.body.storage`)
- `excerpt`: `highlight`, `indexed`, or `none`
- `limit`: Max results (max 250; reduced to 25-50 when using body expansions)

**CQL operators and fields**:
- Fields: `text`, `title`, `label`, `space`, `type`, `creator`, `lastModified`, `created`, `ancestor`
- Operators: `=`, `!=`, `~` (contains), `!~`, `>`, `<`, `>=`, `<=`, `IN`, `NOT IN`
- Functions: `currentUser()`, `now("-7d")`, `now("-30d")`
- Example: `title ~ "meeting" AND lastModified > now("-7d") ORDER BY lastModified DESC`

**Pitfalls**:
- `CONFLUENCE_SEARCH_CONTENT` fetches up to 300 pages and applies client-side filtering -- not a true full-text search
- `CONFLUENCE_CQL_SEARCH` is the real full-text search; use `text ~ "term"` for content body search
- HTTP 429 rate limits can occur; throttle to ~2 requests/second with backoff
- Using body expansions in CQL_SEARCH may reduce max results to 25-50
- Search indexing is not immediate; recently created pages may not appear

### 3. Manage Spaces

**When to use**: User wants to list, create, or inspect Confluence spaces

**Tool sequence**:
1. `CONFLUENCE_GET_SPACES` - List all spaces with optional filtering [Required]
2. `CONFLUENCE_GET_SPACE_BY_ID` - Get detailed metadata for a specific space [Optional]
3. `CONFLUENCE_CREATE_SPACE` - Create a new space with key and name [Optional]
4. `CONFLUENCE_GET_SPACE_PROPERTIES` - Retrieve custom metadata stored as space properties [Optional]
5. `CONFLUENCE_GET_SPACE_CONTENTS` - List pages, blog posts, or attachments in a space [Optional]
6. `CONFLUENCE_GET_LABELS_FOR_SPACE` - List labels on a space [Optional]

**Key parameters**:
- `key`: Space key -- alphanumeric only, no underscores or hyphens (e.g., `DOCS`, `PROJECT1`)
- `name`: Human-readable space name
- `type`: `global` or `personal`
- `status`: `current` (active) or `archived`
- `spaceKey`: For GET_SPACE_CONTENTS, filters by space key
- `id`: Numeric space ID for GET_SPACE_BY_ID (NOT the space key)

**Pitfalls**:
- Space keys must be alphanumeric only (no underscores, hyphens, or special characters)
- `GET_SPACE_BY_ID` requires numeric space ID, not the space key; use `GET_SPACES` to find numeric IDs
- Clickable space URLs may need assembly: join `_links.webui` (relative) with `_links.base`
- Default pagination is 25; set `limit` explicitly (max 200 for spaces)

### 4. Navigate Page Hierarchy and Labels

**When to use**: User wants to explore page trees, child pages, ancestors, or manage labels

**Tool sequence**:
1. `CONFLUENCE_SEARCH_CONTENT` - Find the target page ID [Prerequisite]
2. `CONFLUENCE_GET_CHILD_PAGES` - List direct children of a parent page [Required]
3. `CONFLUENCE_GET_PAGE_ANCESTORS` - Get the full ancestor chain for a page [Optional]
4. `CONFLUENCE_GET_LABELS_FOR_PAGE` - List labels on a specific page [Optional]
5. `CONFLUENCE_ADD_CONTENT_LABEL` - Add labels to a page [Optional]
6. `CONFLUENCE_GET_LABELS_FOR_SPACE_CONTENT` - List labels across all content in a space [Optional]
7. `CONFLUENCE_GET_PAGE_VERSIONS` - Audit edit history for a page [Optional]

**Key parameters**:
- `id`: Page ID for child pages, ancestors, labels, and versions
- `cursor`: Opaque pagination cursor for GET_CHILD_PAGES (from `_links.next`)
- `limit`: Items per page (max 250 for child pages)
- `sort`: Child page sort options: `id`, `-id`, `created-date`, `-created-date`, `modified-date`, `-modified-date`, `child-position`, `-child-position`

**Pitfalls**:
- `GET_CHILD_PAGES` only returns direct children, not nested descendants; recurse for full tree
- Pagination for GET_CHILD_PAGES uses cursor-based pagination (not start/limit)
- Verify the correct page ID from search before using as parent; search can return similar titles
- `GET_PAGE_VERSIONS` requires the page ID, not a version number

## Common Patterns

### ID Resolution
Always resolve human-readable names to IDs before operations:
- **Space key -> Space ID**: `CONFLUENCE_GET_SPACES` with `spaceKey` filter, or `CREATE_PAGE` accepts space keys directly
- **Page title -> Page ID**: `CONFLUENCE_SEARCH_CONTENT` with `query` param, then extract page ID
- **Space ID from URL**: Extract numeric ID from Confluence URLs or use GET_SPACES

### Pagination
Confluence uses two pagination styles:
- **Offset-based** (most endpoints): `start` (0-based offset) + `limit` (page size). Increment `start` by `limit` until fewer results than `limit` are returned.
- **Cursor-based** (GET_CHILD_PAGES, GET_PAGES): Use the `cursor` from `_links.next` in the response. Continue until no `next` link is present.

### Content Formatting
- Pages use Confluence storage format (XHTML), not Markdown
- Basic elements: `<p>`, `<h1>`-`<h6>`, `<strong>`, `<em>`, `<code>`, `<ul>`, `<ol>`, `<li>`
- Tables: `<table><tbody><tr><th>` / `<td>` structure
- Macros: `<ac:structured-macro ac:name="code">` for code blocks, etc.
- Always wrap content in proper XHTML tags

## Known Pitfalls

### ID Formats
- Space IDs are numeric (e.g., `557060`); space keys are short strings (e.g., `DOCS`)
- Page IDs are numeric long values for GET_PAGE_BY_ID; some tools accept UUID format
- `GET_SPACE_BY_ID` requires numeric ID, not the space key
- `GET_PAGE_BY_ID` takes an integer, not a string

### Rate Limits
- HTTP 429 can occur on search endpoints; honor Retry-After header
- Throttle to ~2 requests/second with exponential backoff and jitter
- Body expansion in CQL_SEARCH reduces result limits to 25-50

### Content Format
- Content must be Confluence storage format (XHTML), not Markdown or plain text
- Invalid XHTML will cause page creation/update to fail
- `CREATE_PAGE` nests body under `body.storage.value`; `UPDATE_PAGE` uses `body.value` + `body.representation`

### Version Conflicts
- Updates require exact next version number (current + 1)
- Concurrent edits can cause version conflicts; always fetch current version immediately before updating
- Title changes during update must still be unique within the space

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List spaces | `CONFLUENCE_GET_SPACES` | `type`, `status`, `limit` |
| Get space by ID | `CONFLUENCE_GET_SPACE_BY_ID` | `id` |
| Create space | `CONFLUENCE_CREATE_SPACE` | `key`, `name`, `type` |
| Space contents | `CONFLUENCE_GET_SPACE_CONTENTS` | `spaceKey`, `type`, `status` |
| Space properties | `CONFLUENCE_GET_SPACE_PROPERTIES` | `id`, `key` |
| Search content | `CONFLUENCE_SEARCH_CONTENT` | `query`, `spaceKey`, `limit` |
| CQL search | `CONFLUENCE_CQL_SEARCH` | `cql`, `expand`, `limit` |
| List pages | `CONFLUENCE_GET_PAGES` | `spaceId`, `sort`, `limit` |
| Get page by ID | `CONFLUENCE_GET_PAGE_BY_ID` | `id` (integer) |
| Create page | `CONFLUENCE_CREATE_PAGE` | `title`, `spaceId`, `body` |
| Update page | `CONFLUENCE_UPDATE_PAGE` | `id`, `title`, `body`, `version` |
| Delete page | `CONFLUENCE_DELETE_PAGE` | `id` |
| Child pages | `CONFLUENCE_GET_CHILD_PAGES` | `id`, `limit`, `sort` |
| Page ancestors | `CONFLUENCE_GET_PAGE_ANCESTORS` | `id` |
| Page labels | `CONFLUENCE_GET_LABELS_FOR_PAGE` | `id` |
| Add label | `CONFLUENCE_ADD_CONTENT_LABEL` | content ID, label |
| Page versions | `CONFLUENCE_GET_PAGE_VERSIONS` | `id` |
| Space labels | `CONFLUENCE_GET_LABELS_FOR_SPACE` | space ID |

---
*Powered by [Composio](https://composio.dev)*
