---
name: webflow-automation
description: Automate Webflow CMS collections, site publishing, page management, asset uploads, and ecommerce orders via Rube MCP (Composio). Always search tools first for current schemas.
requires:
  mcp: [rube]
---

# Webflow Automation via Rube MCP

Automate Webflow operations including CMS collection management, site publishing, page inspection, asset uploads, and ecommerce order retrieval through Composio's Webflow toolkit.

**Toolkit docs**: [composio.dev/toolkits/webflow](https://composio.dev/toolkits/webflow)

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Webflow connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `webflow`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `webflow`
3. If connection is not ACTIVE, follow the returned auth link to complete Webflow OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Manage CMS Collection Items

**When to use**: User wants to create, update, list, or delete items in Webflow CMS collections (blog posts, products, team members, etc.)

**Tool sequence**:
1. `WEBFLOW_LIST_WEBFLOW_SITES` - List sites to find the target site_id [Prerequisite]
2. `WEBFLOW_LIST_COLLECTIONS` - List all collections for the site [Prerequisite]
3. `WEBFLOW_GET_COLLECTION` - Get collection schema to find valid field slugs [Prerequisite for create/update]
4. `WEBFLOW_LIST_COLLECTION_ITEMS` - List existing items with filtering and pagination [Optional]
5. `WEBFLOW_GET_COLLECTION_ITEM` - Get a specific item's full details [Optional]
6. `WEBFLOW_CREATE_COLLECTION_ITEM` - Create a new item with field data [Required for creation]
7. `WEBFLOW_UPDATE_COLLECTION_ITEM` - Update an existing item's fields [Required for updates]
8. `WEBFLOW_DELETE_COLLECTION_ITEM` - Permanently remove an item [Optional]
9. `WEBFLOW_PUBLISH_SITE` - Publish changes to make them live [Optional]

**Key parameters for CREATE_COLLECTION_ITEM**:
- `collection_id`: 24-character hex string from LIST_COLLECTIONS
- `field_data`: Object with field slug keys (NOT display names); must include `name` and `slug`
- `field_data.name`: Display name for the item
- `field_data.slug`: URL-friendly identifier (lowercase, hyphens, no spaces)
- `is_draft`: Boolean to create as draft (default false)

**Key parameters for UPDATE_COLLECTION_ITEM**:
- `collection_id`: Collection identifier
- `item_id`: 24-character hex MongoDB ObjectId of the existing item
- `fields`: Object with field slug keys and new values
- `live`: Boolean to publish changes immediately (default false)

**Field value types**:
- Text/Email/Link/Date: string
- Number: integer or float
- Boolean: true/false
- Image: `{"url": "...", "alt": "...", "fileId": "..."}`
- Multi-reference: array of reference ID strings
- Multi-image: array of image objects
- Option: option ID string

**Pitfalls**:
- Field keys must use the exact field `slug` from the collection schema, NOT display names
- Always call `GET_COLLECTION` first to retrieve the schema and identify correct field slugs
- `CREATE_COLLECTION_ITEM` requires `name` and `slug` in `field_data`
- `UPDATE_COLLECTION_ITEM` cannot create new items; it requires a valid existing `item_id`
- `item_id` must be a 24-character hexadecimal MongoDB ObjectId
- Slug must be lowercase alphanumeric with hyphens: `^[a-z0-9]+(?:-[a-z0-9]+)*$`
- CMS items are staged; use `PUBLISH_SITE` or set `live: true` to push to production

### 2. Manage Sites and Publishing

**When to use**: User wants to list sites, inspect site configuration, or publish staged changes

**Tool sequence**:
1. `WEBFLOW_LIST_WEBFLOW_SITES` - List all accessible sites [Required]
2. `WEBFLOW_GET_SITE_INFO` - Get detailed site metadata including domains and settings [Optional]
3. `WEBFLOW_PUBLISH_SITE` - Deploy all staged changes to live site [Required for publishing]

**Key parameters for PUBLISH_SITE**:
- `site_id`: Site identifier from LIST_WEBFLOW_SITES
- `custom_domains`: Array of custom domain ID strings (from GET_SITE_INFO)
- `publish_to_webflow_subdomain`: Boolean to publish to `{shortName}.webflow.io`
- At least one of `custom_domains` or `publish_to_webflow_subdomain` must be specified

**Pitfalls**:
- `PUBLISH_SITE` republishes ALL staged changes for selected domains -- verify no unintended drafts are pending
- Rate limit: 1 successful publish per minute
- For sites without custom domains, must set `publish_to_webflow_subdomain: true`
- `custom_domains` expects domain IDs (hex strings), not domain names
- Publishing is a production action -- always confirm with the user first

### 3. Manage Pages

**When to use**: User wants to list pages, inspect page metadata, or examine page DOM structure

**Tool sequence**:
1. `WEBFLOW_LIST_WEBFLOW_SITES` - Find the target site_id [Prerequisite]
2. `WEBFLOW_LIST_PAGES` - List all pages for a site with pagination [Required]
3. `WEBFLOW_GET_PAGE` - Get detailed metadata for a specific page [Optional]
4. `WEBFLOW_GET_PAGE_DOM` - Get the DOM/content node structure of a static page [Optional]

**Key parameters**:
- `site_id`: Site identifier (required for list pages)
- `page_id`: 24-character hex page identifier
- `locale_id`: Optional locale filter for multi-language sites
- `limit`: Max results per page (max 100)
- `offset`: Pagination offset

**Pitfalls**:
- `LIST_PAGES` paginates via offset/limit; iterate when sites have many pages
- Page IDs are 24-character hex strings matching pattern `^[0-9a-fA-F]{24}$`
- `GET_PAGE_DOM` returns the node structure, not rendered HTML
- Pages include both static and CMS-driven pages

### 4. Upload Assets

**When to use**: User wants to upload images, files, or other assets to a Webflow site

**Tool sequence**:
1. `WEBFLOW_LIST_WEBFLOW_SITES` - Find the target site_id [Prerequisite]
2. `WEBFLOW_UPLOAD_ASSET` - Upload a file with base64-encoded content [Required]

**Key parameters**:
- `site_id`: Site identifier
- `file_name`: Name of the file (e.g., `"logo.png"`)
- `file_content`: Base64-encoded binary content of the file (NOT a placeholder or URL)
- `content_type`: MIME type (e.g., `"image/png"`, `"image/jpeg"`, `"application/pdf"`)
- `md5`: MD5 hash of the raw file bytes (32-character hex string)
- `asset_folder_id`: Optional folder placement

**Pitfalls**:
- `file_content` must be actual base64-encoded data, NOT a variable reference or placeholder
- `md5` must be computed from the raw bytes, not from the base64 string
- This is a two-step process internally: generates an S3 pre-signed URL, then uploads
- Large files may encounter timeouts; keep uploads reasonable in size

### 5. Manage Ecommerce Orders

**When to use**: User wants to view ecommerce orders from a Webflow site

**Tool sequence**:
1. `WEBFLOW_LIST_WEBFLOW_SITES` - Find the site with ecommerce enabled [Prerequisite]
2. `WEBFLOW_LIST_ORDERS` - List all orders with optional status filtering [Required]
3. `WEBFLOW_GET_ORDER` - Get detailed information for a specific order [Optional]

**Key parameters**:
- `site_id`: Site identifier (must have ecommerce enabled)
- `order_id`: Specific order identifier for detailed retrieval
- `status`: Filter orders by status

**Pitfalls**:
- Ecommerce must be enabled on the Webflow site for order endpoints to work
- Order endpoints are read-only; no create/update/delete for orders through these tools

## Common Patterns

### ID Resolution
Webflow uses 24-character hexadecimal IDs throughout:
- **Site ID**: `WEBFLOW_LIST_WEBFLOW_SITES` -- find by name, capture `id`
- **Collection ID**: `WEBFLOW_LIST_COLLECTIONS` with `site_id`
- **Item ID**: `WEBFLOW_LIST_COLLECTION_ITEMS` with `collection_id`
- **Page ID**: `WEBFLOW_LIST_PAGES` with `site_id`
- **Domain IDs**: `WEBFLOW_GET_SITE_INFO` -- found in `customDomains` array
- **Field slugs**: `WEBFLOW_GET_COLLECTION` -- found in collection `fields` array

### Pagination
Webflow uses offset-based pagination:
- `offset`: Starting index (0-based)
- `limit`: Items per page (max 100)
- Increment offset by limit until fewer results than limit are returned
- Available on: LIST_COLLECTION_ITEMS, LIST_PAGES

### CMS Workflow
Typical CMS content creation flow:
1. Get site_id from LIST_WEBFLOW_SITES
2. Get collection_id from LIST_COLLECTIONS
3. Get field schema from GET_COLLECTION (to learn field slugs)
4. Create/update items using correct field slugs
5. Publish site to make changes live

## Known Pitfalls

### ID Formats
- All Webflow IDs are 24-character hexadecimal strings (MongoDB ObjectIds)
- Example: `580e63fc8c9a982ac9b8b745`
- Pattern: `^[0-9a-fA-F]{24}$`
- Invalid IDs return 404 errors

### Field Slugs vs Display Names
- CMS operations require field `slug` values, NOT display names
- A field with displayName "Author Name" might have slug `author-name`
- Always call `GET_COLLECTION` to discover correct field slugs
- Using wrong field names silently ignores the data or causes validation errors

### Publishing
- `PUBLISH_SITE` deploys ALL staged changes, not just specific items
- Rate limited to 1 publish per minute
- Must specify at least one domain target (custom or webflow subdomain)
- This is a production-affecting action; always confirm intent

### Authentication Scopes
- Different operations require different OAuth scopes: `sites:read`, `cms:read`, `cms:write`, `pages:read`
- A 403 error typically means missing OAuth scopes
- Check connection permissions if operations fail with authorization errors

### Destructive Operations
- `DELETE_COLLECTION_ITEM` permanently removes CMS items
- `PUBLISH_SITE` makes all staged changes live immediately
- Always confirm with the user before executing these actions

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List sites | `WEBFLOW_LIST_WEBFLOW_SITES` | (none) |
| Get site info | `WEBFLOW_GET_SITE_INFO` | `site_id` |
| Publish site | `WEBFLOW_PUBLISH_SITE` | `site_id`, `custom_domains` or `publish_to_webflow_subdomain` |
| List collections | `WEBFLOW_LIST_COLLECTIONS` | `site_id` |
| Get collection schema | `WEBFLOW_GET_COLLECTION` | `collection_id` |
| List collection items | `WEBFLOW_LIST_COLLECTION_ITEMS` | `collection_id`, `limit`, `offset` |
| Get collection item | `WEBFLOW_GET_COLLECTION_ITEM` | `collection_id`, `item_id` |
| Create collection item | `WEBFLOW_CREATE_COLLECTION_ITEM` | `collection_id`, `field_data` |
| Update collection item | `WEBFLOW_UPDATE_COLLECTION_ITEM` | `collection_id`, `item_id`, `fields` |
| Delete collection item | `WEBFLOW_DELETE_COLLECTION_ITEM` | `collection_id`, `item_id` |
| List pages | `WEBFLOW_LIST_PAGES` | `site_id`, `limit`, `offset` |
| Get page | `WEBFLOW_GET_PAGE` | `page_id` |
| Get page DOM | `WEBFLOW_GET_PAGE_DOM` | `page_id` |
| Upload asset | `WEBFLOW_UPLOAD_ASSET` | `site_id`, `file_name`, `file_content`, `content_type`, `md5` |
| List orders | `WEBFLOW_LIST_ORDERS` | `site_id`, `status` |
| Get order | `WEBFLOW_GET_ORDER` | `site_id`, `order_id` |

---
*Powered by [Composio](https://composio.dev)*
