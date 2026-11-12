---
name: Productboard Automation
description: "Automate product management workflows in Productboard -- manage features, notes, objectives, components, and releases through natural language commands."
requires:
  mcp:
    - rube
---

# Productboard Automation

Automate your Productboard product management operations directly from Claude Code. Create notes from customer feedback, browse features and objectives, link entities, and track releases -- all without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/productboard](https://composio.dev/toolkits/productboard)

---

## Setup

1. Add the Rube MCP server to your Claude Code config with URL: `https://rube.app/mcp`
2. When prompted, authenticate your Productboard account through the connection link provided
3. Start automating your product management workflows with natural language

---

## Core Workflows

### 1. Manage Customer Notes

Create notes from customer feedback and organize them with tags, links, and followers.

**Tools:** `PRODUCTBOARD_CREATE_NOTE`, `PRODUCTBOARD_LIST_NOTES`, `PRODUCTBOARD_ADD_NOTE_TAG`, `PRODUCTBOARD_ADD_NOTE_FOLLOWERS`, `PRODUCTBOARD_CREATE_NOTE_LINK`

```
Create a note titled "Mobile app crash report" with content from customer feedback, tagged "bug" and linked to feature abc-123
```

Key parameters for `PRODUCTBOARD_CREATE_NOTE`:
- `title` (required) and `content` (required) -- note title and body
- `customer_email` or `user.email` -- attribute to a customer/user
- `tags` -- array of tag strings for categorization
- `display_url` -- URL linked from the note title
- `source` -- origin system with `origin` and `record_id`
- `company` -- associate with a company

Key parameters for `PRODUCTBOARD_LIST_NOTES`:
- `createdFrom` / `createdTo` -- ISO 8601 date range
- `last` -- relative time window (e.g., `"6m"`, `"10d"`, `"24h"`)
- `term` -- full-text search by title or content
- `allTags` / `anyTag` -- filter by tags (cannot combine both)
- `featureId`, `companyId`, `ownerEmail`, `source` -- entity filters
- `pageLimit` (max 100) / `pageCursor` -- pagination

### 2. Browse and Retrieve Features

List all features/subfeatures and retrieve detailed information.

**Tools:** `PRODUCTBOARD_LIST_FEATURES`, `PRODUCTBOARD_RETRIEVE_FEATURE`

```
List the first 50 features in Productboard, then get details on feature abc-def-123
```

- `PRODUCTBOARD_LIST_FEATURES` supports `pageLimit` (default 100) and `pageOffset` for pagination
- `PRODUCTBOARD_RETRIEVE_FEATURE` requires feature `id` (UUID) to get complete details

### 3. Objectives and Key Results (OKRs)

List objectives, view feature-objective links, and browse key results.

**Tools:** `PRODUCTBOARD_LIST_OBJECTIVES`, `PRODUCTBOARD_LIST_FEATURE_OBJECTIVES`, `PRODUCTBOARD_LIST_KEY_RESULTS`

```
Show me all in-progress objectives owned by alice@example.com
```

Key parameters for `PRODUCTBOARD_LIST_OBJECTIVES`:
- `status.name` -- filter by status (e.g., `"In Progress"`)
- `owner.email` -- filter by owner email
- `parent.id` -- filter by parent objective
- `archived` -- filter by archived state

`PRODUCTBOARD_LIST_FEATURE_OBJECTIVES`:
- Requires `id` (UUID) of a **top-level feature** (not subfeatures)
- Supports `pageCursor` for pagination

### 4. Component Management

List product components for organizing features and the product hierarchy.

**Tool:** `PRODUCTBOARD_LIST_COMPONENTS`

```
List all components in our Productboard workspace
```

- Supports `page_limit` and `page_offset` for pagination
- Follow `links.next` for additional pages

### 5. Release Tracking

View feature-release assignments with state and date filters.

**Tool:** `PRODUCTBOARD_LIST_FEATURE_RELEASE_ASSIGNMENTS`

```
Show all active release assignments for feature abc-123
```

- Filter by `feature.id`, `release.id`, `release.state` (planned, active, closed)
- Date range filters: `release.timeframe.endDate.from` and `release.timeframe.endDate.to` (YYYY-MM-DD)

### 6. Link Notes to Features

Connect customer feedback notes to product features for insight aggregation.

**Tool:** `PRODUCTBOARD_CREATE_NOTE_LINK`

```
Link note 3fa85f64-5717 to feature 1b6c8c76-8f5d for tracking
```

- Requires `noteId` (UUID) and `entityId` (UUID of feature, component, or product)
- Use after creating notes to ensure feedback is connected to the right product areas

---

## Known Pitfalls

- **Top-level features only for objectives:** `PRODUCTBOARD_LIST_FEATURE_OBJECTIVES` only works with top-level feature IDs, not subfeature IDs. Use `PRODUCTBOARD_LIST_FEATURES` to identify which features are top-level.
- **Tag filter exclusivity:** `allTags` and `anyTag` cannot be combined in `PRODUCTBOARD_LIST_NOTES`. Choose one filter strategy per query.
- **Relative vs. absolute dates:** The `last` parameter (e.g., `"24h"`) cannot be combined with `createdFrom`/`createdTo` in `PRODUCTBOARD_LIST_NOTES`. Use one approach, not both.
- **Cursor-based pagination:** Follow `links.next` or use `pageCursor` from responses for multi-page results. Offset-based and cursor-based pagination are used on different endpoints -- check each tool.
- **Note attribution:** Either `user.email` or `customer_email` must be provided in `PRODUCTBOARD_CREATE_NOTE` to attribute feedback. Without it, the note will have no customer association.
- **UUID formats required:** All entity IDs (features, notes, components) must be valid UUIDs. Passing malformed IDs causes 400 errors.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `PRODUCTBOARD_CREATE_NOTE` | Create a customer feedback note (requires `title`, `content`) |
| `PRODUCTBOARD_LIST_NOTES` | List notes with search, date, and tag filters |
| `PRODUCTBOARD_ADD_NOTE_TAG` | Add a tag to a note |
| `PRODUCTBOARD_ADD_NOTE_FOLLOWERS` | Add followers to a note by email |
| `PRODUCTBOARD_CREATE_NOTE_LINK` | Link a note to a feature/component (requires `noteId`, `entityId`) |
| `PRODUCTBOARD_LIST_FEATURES` | List all features with pagination |
| `PRODUCTBOARD_RETRIEVE_FEATURE` | Get detailed feature info by UUID |
| `PRODUCTBOARD_LIST_OBJECTIVES` | List objectives with status/owner filters |
| `PRODUCTBOARD_LIST_FEATURE_OBJECTIVES` | List objectives linked to a top-level feature |
| `PRODUCTBOARD_LIST_KEY_RESULTS` | List key results for objectives |
| `PRODUCTBOARD_LIST_COMPONENTS` | List product components with pagination |
| `PRODUCTBOARD_LIST_FEATURE_RELEASE_ASSIGNMENTS` | List feature-release assignments with filters |

---

*Powered by [Composio](https://composio.dev)*
