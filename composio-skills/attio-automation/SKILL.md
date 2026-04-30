---
name: Attio Automation
description: "Automate Attio CRM operations -- search records, query contacts and companies with advanced filters, manage notes, list attributes, and navigate your relationship data -- using natural language through the Composio MCP integration."
category: crm
requires:
  mcp:
    - rube
---

# Attio Automation

Manage your Attio CRM workspace -- fuzzy search across people and companies, run complex filtered queries, browse notes, discover object schemas, and list records -- all through natural language commands.

**Toolkit docs:** [composio.dev/toolkits/attio](https://composio.dev/toolkits/attio)

---

## Setup

1. Add the Composio MCP server to your client configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Attio account when prompted (OAuth authentication).
3. Start issuing natural language commands to manage your CRM data.

---

## Core Workflows

### 1. Fuzzy Search Across Records
Search for people, companies, deals, or any object by name, domain, email, phone, or social handle.

**Tool:** `ATTIO_SEARCH_RECORDS`

**Example prompt:**
> "Search Attio for anyone named Alan Mathis"

**Key parameters (all required):**
- `query` -- Search string (max 256 characters). Empty string returns default results.
- `objects` -- Array of object slugs to search (e.g., `["people"]`, `["people", "companies"]`, `["deals"]`)
- `request_as` -- Context: use `{"type": "workspace"}` for full workspace search, or specify a workspace member

---

### 2. Advanced Filtered Queries
Query records with server-side filtering, sorting, and complex conditions -- far more powerful than fuzzy search.

**Tool:** `ATTIO_QUERY_RECORDS`

**Example prompt:**
> "Find all companies in Attio created after January 2025 sorted by name"

**Key parameters:**
- `object` (required) -- Object slug or UUID (e.g., "people", "companies", "deals")
- `filter` -- Attio filter object with operators like `$eq`, `$contains`, `$gte`, `$and`, `$or`
- `sorts` -- Array of sort specifications with `direction` ("asc"/"desc") and `attribute`
- `limit` -- Max records to return (up to 500)
- `offset` -- Pagination offset

**Filter examples:**
```json
{"name": {"first_name": {"$contains": "John"}}}
{"email_addresses": {"$contains": "@example.com"}}
{"created_at": {"$gte": "2025-01-01T00:00:00.000Z"}}
```

---

### 3. Find Records by ID or Attributes
Look up a specific record by its unique ID or search by unique attribute values.

**Tool:** `ATTIO_FIND_RECORD`

**Example prompt:**
> "Find the Attio company with domain example.com"

**Key parameters:**
- `object_id` (required) -- Object type slug: "people", "companies", "deals", "users", "workspaces"
- `record_id` -- Direct lookup by UUID (optional)
- `attributes` -- Dictionary of attribute filters (e.g., `{"email_addresses": "john@example.com"}`)
- `limit` -- Max records (up to 1000)
- `offset` -- Pagination offset

---

### 4. Browse and Filter Notes
List notes across the workspace or filter by specific parent objects and records.

**Tool:** `ATTIO_LIST_NOTES`

**Example prompt:**
> "Show the last 10 notes on the Acme Corp company record in Attio"

**Key parameters:**
- `parent_object` -- Object slug (e.g., "people", "companies", "deals") -- requires `parent_record_id`
- `parent_record_id` -- UUID of the parent record -- requires `parent_object`
- `limit` -- Max notes to return (1-50, default 10)
- `offset` -- Number of results to skip

---

### 5. Discover Object Schemas and Attributes
Understand your workspace structure by listing objects and their attribute definitions.

**Tools:** `ATTIO_GET_OBJECT`, `ATTIO_LIST_ATTRIBUTES`

**Example prompt:**
> "What attributes does the companies object have in Attio?"

**Key parameters for Get Object:**
- `object_id` -- Object slug or UUID

**Key parameters for List Attributes:**
- `target` -- "objects" or "lists"
- `identifier` -- Object or list ID/slug

---

### 6. List All Records
Retrieve records from a specific object type with simple pagination, returned in creation order.

**Tool:** `ATTIO_LIST_RECORDS`

**Example prompt:**
> "List the first 100 people records in Attio"

**Key parameters:**
- Object type identifier
- Pagination parameters

---

## Known Pitfalls

- **Timestamp format is critical**: ALL timestamp comparisons (`created_at`, `updated_at`, custom timestamps) MUST use ISO8601 string format (e.g., `2025-01-01T00:00:00.000Z`). Unix timestamps or numeric values cause "Invalid timestamp value" errors.
- **Name attributes must be nested**: The `name` attribute has sub-properties (`first_name`, `last_name`, `full_name`) that MUST be nested under `name`. Correct: `{"name": {"first_name": {"$contains": "John"}}}`. Wrong: `{"first_name": {...}}` -- this fails with "unknown_filter_attribute_slug".
- **Email operators are limited**: `email_addresses` supports `$eq`, `$contains`, `$starts_with`, `$ends_with` but NOT `$not_empty`.
- **Record-reference attributes need path filtering**: For attributes that reference other records (e.g., "team", "company"), use path-based filtering, not nested syntax. Example: `{"path": [["companies", "team"], ["people", "name"]], "constraints": {"first_name": {"$eq": "John"}}}`.
- **"lists" is not an object type**: Do not use "lists" as an `object_id`. Use list-specific actions for list operations.
- **Search is eventually consistent**: `ATTIO_SEARCH_RECORDS` returns eventually consistent results. For guaranteed up-to-date results, use `ATTIO_QUERY_RECORDS` instead.
- **Attribute slugs vary by workspace**: System attributes (e.g., "email_addresses", "name") are consistent, but custom attributes vary. Use `ATTIO_LIST_ATTRIBUTES` to discover valid slugs for your workspace.

---

## Quick Reference

| Action | Tool Slug | Required Params |
|---|---|---|
| Fuzzy search records | `ATTIO_SEARCH_RECORDS` | `query`, `objects`, `request_as` |
| Query with filters | `ATTIO_QUERY_RECORDS` | `object` |
| Find record by ID/attributes | `ATTIO_FIND_RECORD` | `object_id` |
| List notes | `ATTIO_LIST_NOTES` | None (optional filters) |
| Get object schema | `ATTIO_GET_OBJECT` | `object_id` |
| List attributes | `ATTIO_LIST_ATTRIBUTES` | `target`, `identifier` |
| List records | `ATTIO_LIST_RECORDS` | Object type |

---

*Powered by [Composio](https://composio.dev)*
