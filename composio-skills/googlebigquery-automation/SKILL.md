---
name: googlebigquery-automation
description: "Automate Google BigQuery tasks via Rube MCP (Composio): run SQL queries, explore datasets and metadata, execute MBQL queries via Metabase integration. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Google BigQuery Automation via Rube MCP

Run SQL queries, explore database schemas, and analyze datasets through the Metabase integration using Rube MCP (Composio).

**Toolkit docs**: [composio.dev/toolkits/googlebigquery](https://composio.dev/toolkits/googlebigquery)

## Prerequisites
- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `metabase`
- A Metabase instance connected to your BigQuery data source
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup
**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.

1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `metabase`
3. If connection is not ACTIVE, follow the returned auth link to complete setup
4. Confirm connection status shows ACTIVE before running any workflows

> **Note**: BigQuery data is accessed through Metabase, a business intelligence tool that connects to BigQuery as a data source. The tools below execute queries and retrieve metadata through Metabase's API.

## Core Workflows

### 1. Run a Native SQL Query
Use `METABASE_POST_API_DATASET` with type `native` to execute raw SQL queries against your BigQuery database.
```
Tool: METABASE_POST_API_DATASET
Parameters:
  - database (required): Metabase database ID (integer)
  - type (required): "native" for SQL queries
  - native (required): Object with "query" string
    - query: Raw SQL string (e.g., "SELECT * FROM users LIMIT 10")
    - template_tags: Parameterized query variables (optional)
  - constraints: { "max-results": 1000 } (optional)
```

### 2. Run a Structured MBQL Query
Use `METABASE_POST_API_DATASET` with type `query` for Metabase Query Language queries with built-in aggregation and filtering.
```
Tool: METABASE_POST_API_DATASET
Parameters:
  - database (required): Metabase database ID
  - type (required): "query" for MBQL
  - query (required): Object with:
    - source-table: Table ID (integer)
    - aggregation: e.g., [["count"]] or [["sum", ["field", 5, null]]]
    - breakout: Group-by fields
    - filter: Filter conditions
    - limit: Max rows
    - order-by: Sort fields
```

### 3. Get Query Metadata
Use `METABASE_POST_API_DATASET_QUERY_METADATA` to retrieve metadata about databases, tables, and fields available for querying.
```
Tool: METABASE_POST_API_DATASET_QUERY_METADATA
Parameters:
  - database (required): Metabase database ID
  - type (required): "query" or "native"
  - query (required): Query object (e.g., {"source-table": 1})
```

### 4. Convert Query to Native SQL
Use `METABASE_POST_API_DATASET_NATIVE` to convert an MBQL query into its native SQL representation.
```
Tool: METABASE_POST_API_DATASET_NATIVE
Parameters:
  - database (required): Metabase database ID
  - type (required): "native"
  - native (required): Object with "query" and optional "template_tags"
  - parameters: Query parameter values (optional)
```

### 5. List Available Databases
Use `METABASE_GET_API_DATABASE` to discover all database connections configured in Metabase.
```
Tool: METABASE_GET_API_DATABASE
Description: Retrieves a list of all Database instances configured in Metabase.
Note: Call RUBE_SEARCH_TOOLS to get the full schema for this tool.
```

### 6. Get Database Schema Metadata
Use `METABASE_GET_API_DATABASE_ID_METADATA` to retrieve complete table and field information for a specific database.
```
Tool: METABASE_GET_API_DATABASE_ID_METADATA
Description: Retrieves complete metadata for a specific database including
  all tables and fields.
Note: Call RUBE_SEARCH_TOOLS to get the full schema for this tool.
```

## Common Patterns

- **Discover then query**: Use `METABASE_GET_API_DATABASE` to find database IDs, then `METABASE_GET_API_DATABASE_ID_METADATA` to explore tables and fields, then `METABASE_POST_API_DATASET` to run queries.
- **SQL-first approach**: Use `METABASE_POST_API_DATASET` with `type: "native"` and write standard SQL queries for maximum flexibility.
- **Parameterized queries**: Use `template_tags` in native queries for safe parameterization (e.g., `SELECT * FROM users WHERE id = {{user_id}}`).
- **Schema exploration**: Use `METABASE_POST_API_DATASET_QUERY_METADATA` to understand table structures before building complex queries.
- **Get parameter values**: Use `METABASE_POST_API_DATASET_PARAMETER_VALUES` to retrieve possible values for filter dropdowns.

## Known Pitfalls

- The `database` parameter is a Metabase-internal **integer ID**, not the BigQuery project or dataset name. Use `METABASE_GET_API_DATABASE` to find valid database IDs first.
- `source-table` in MBQL queries is also a Metabase-internal integer, not the BigQuery table name. Discover table IDs via metadata tools.
- Native SQL queries use BigQuery SQL dialect (Standard SQL). Ensure your syntax is BigQuery-compatible.
- `max-results` in constraints defaults can limit returned rows. Set explicitly for large result sets.
- Responses from `METABASE_POST_API_DATASET` contain results nested under `data` -- parse carefully as the structure may be deeply nested.
- Metabase field IDs used in MBQL `aggregation`, `breakout`, and `filter` arrays must be integers obtained from metadata responses.

## Quick Reference
| Action | Tool | Key Parameters |
|--------|------|----------------|
| Run SQL query | `METABASE_POST_API_DATASET` | `database`, `type: "native"`, `native.query` |
| Run MBQL query | `METABASE_POST_API_DATASET` | `database`, `type: "query"`, `query` |
| Get query metadata | `METABASE_POST_API_DATASET_QUERY_METADATA` | `database`, `type`, `query` |
| Convert to SQL | `METABASE_POST_API_DATASET_NATIVE` | `database`, `type`, `native` |
| Get parameter values | `METABASE_POST_API_DATASET_PARAMETER_VALUES` | `parameter`, `field_ids` |
| List databases | `METABASE_GET_API_DATABASE` | (see full schema via RUBE_SEARCH_TOOLS) |
| Get database metadata | `METABASE_GET_API_DATABASE_ID_METADATA` | (see full schema via RUBE_SEARCH_TOOLS) |

---
*Powered by [Composio](https://composio.dev)*
