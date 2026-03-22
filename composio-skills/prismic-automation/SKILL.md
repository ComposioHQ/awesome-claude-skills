---
name: Prismic Automation
description: "Automate headless CMS operations in Prismic -- query documents, search content, retrieve custom types, and manage repository refs through the Composio Prismic integration."
requires:
  mcp:
    - rube
---

# Prismic Automation

Manage your **Prismic** headless CMS directly from Claude Code. Query documents by type, full-text search content, inspect custom types, and work with repository refs for content versioning.

**Toolkit docs:** [composio.dev/toolkits/prismic](https://composio.dev/toolkits/prismic)

---

## Setup

1. Add the Composio MCP server to your configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Prismic account when prompted. The agent will provide an authentication link.
3. Most content queries require a `ref` token. Always start by calling `PRISMIC_REPOSITORY_API_GET_REFS` or `PRISMIC_REPOSITORY_API_GET_INFO` to obtain the master ref.

---

## Core Workflows

### 1. Get Repository Info and Refs

Retrieve comprehensive repository metadata including available refs (content versions), custom types, languages, tags, and bookmarks. This is typically your first API call.

**Tools:** `PRISMIC_REPOSITORY_API_GET_INFO`, `PRISMIC_REPOSITORY_API_GET_REFS`

No parameters required -- these endpoints return the full repository configuration. The `refs` field is critical since refs are required for all content queries.

Example prompt: *"Get my Prismic repository info and the current master ref"*

---

### 2. Query Documents with Predicates

Fetch documents using Prismic's predicate query syntax with full pagination and filtering support.

**Tool:** `PRISMIC_CONTENT_API_QUERY_DOCUMENTS`

Key parameters:
- `ref` (required) -- content release reference ID (typically the master ref)
- `q` -- predicate query, e.g., `[[at(document.type, "page")]]`
- `page` (min 1) and `pageSize` (1-100) -- pagination
- `lang` -- language code, e.g., `en-us` (default `*` for all)
- `orderings` -- sort order, e.g., `[my.article.date desc]`
- `fetch` -- comma-separated fields to fetch, reducing response size
- `fetchLinks` -- resolve linked document fields inline

Example prompt: *"Query all published blog posts in Prismic, sorted by date descending, in English"*

---

### 3. Fetch Documents by Type

Retrieve all documents of a specific custom type with automatic master ref resolution.

**Tool:** `PRISMIC_GET_DOCUMENTS_BY_TYPE`

Key parameters:
- `type` (required) -- custom type API ID, e.g., `blog_post`, `article`, `page`
- `page` (default 1) and `pageSize` (1-100, default 20)
- `lang` -- language code filter
- `orderings` -- sort order, e.g., `[my.article.date desc]`
- `after` -- cursor-based pagination for deep pagination beyond page 50

Example prompt: *"Get all blog_post documents in Prismic, 20 per page"*

---

### 4. Full-Text Search

Search across all text fields in documents for specified terms. Case-insensitive, matches on root words.

**Tool:** `PRISMIC_CONTENT_API_GET_DOCUMENTS_WITH_FULLTEXT_SEARCH`

Key parameters:
- `q` (required) -- full-text predicate, e.g., `[[fulltext(document, "machine learning")]]`
- `page`, `pageSize`, `lang`, `orderings` -- same pagination/filtering as other queries

Example prompt: *"Search all Prismic documents for 'machine learning'"*

---

### 5. Get a Single Document by ID

Retrieve a specific document by its unique identifier.

**Tool:** `PRISMIC_GET_DOCUMENT_BY_ID`

Key parameters:
- `document_id` (required) -- unique document identifier
- `ref` (required) -- content ref from repository
- `lang` -- optional language filter

Example prompt: *"Fetch Prismic document Xx2KLhEAAJljVWaA"*

---

### 6. List Custom Types

Discover all custom types (content models) defined in the repository, including their structure definitions.

**Tool:** `PRISMIC_TYPES_API_GET_TYPES`

Key parameters:
- `limit` -- max number of types to return per page
- `page` -- page number (1-indexed)
- `sort` -- sort order, e.g., `name`

Example prompt: *"List all custom types in my Prismic repository"*

---

## Known Pitfalls

- **Ref is required for all content queries:** You must obtain a valid `ref` (typically the master ref) from `PRISMIC_REPOSITORY_API_GET_REFS` or `PRISMIC_REPOSITORY_API_GET_INFO` before querying any documents. Queries without a ref will fail.
- **Predicate syntax requires double brackets:** Prismic queries use double square brackets: `[[at(document.type, "page")]]`. For multiple predicates, combine them: `[[at(document.type, "blog")][at(document.tags, ["featured"])]]`.
- **Deep pagination limit:** Standard page-based pagination may fail beyond page 50. For deep pagination, use the `after` parameter with the last document ID from your previous result set.
- **pageSize cap is 100:** Requesting more than 100 documents per page will be rejected. Use pagination to iterate through larger result sets.
- **Language filtering:** The default language filter is `*` (all languages). If you need documents in a specific locale, always pass `lang` explicitly (e.g., `en-us`, `fr-fr`).
- **Integration fields require separate ref:** When using `PRISMIC_CONTENT_API_GET_DOCUMENTS_WITH_INTEGRATION_FIELDS`, you need an `integrationFieldsRef` in addition to the standard content `ref`.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `PRISMIC_REPOSITORY_API_GET_INFO` | Get repository metadata, refs, types, languages |
| `PRISMIC_REPOSITORY_API_GET_REFS` | List all refs (master + releases) |
| `PRISMIC_TYPES_API_GET_TYPES` | List all custom types / content models |
| `PRISMIC_CONTENT_API_QUERY_DOCUMENTS` | Query documents with predicates and pagination |
| `PRISMIC_GET_DOCUMENTS_BY_TYPE` | Fetch documents filtered by custom type |
| `PRISMIC_GET_DOCUMENT_BY_ID` | Retrieve a single document by ID |
| `PRISMIC_CONTENT_API_GET_DOCUMENTS_WITH_FULLTEXT_SEARCH` | Full-text search across all documents |
| `PRISMIC_CONTENT_API_GET_DOCUMENTS_WITH_PREDICATES` | Filter documents with multiple predicate conditions |
| `PRISMIC_CONTENT_API_GET_DOCUMENTS_WITH_INTEGRATION_FIELDS` | Fetch documents with integration fields data |
| `PRISMIC_GET_DOCUMENTS_ORDERED` | Fetch documents sorted by specified fields |

---

*Powered by [Composio](https://composio.dev)*
