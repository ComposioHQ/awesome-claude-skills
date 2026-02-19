---
name: Snowflake Automation
description: "Automate Snowflake data warehouse operations -- list databases, schemas, and tables, execute SQL statements, and manage data workflows via the Composio MCP integration."
requires:
  mcp:
    - rube
---

# Snowflake Automation

Automate your Snowflake data warehouse workflows -- discover databases, browse schemas and tables, execute arbitrary SQL (SELECT, DDL, DML), and integrate Snowflake data operations into cross-app pipelines.

**Toolkit docs:** [composio.dev/toolkits/snowflake](https://composio.dev/toolkits/snowflake)

---

## Setup

1. Add the Composio MCP server to your client: `https://rube.app/mcp`
2. Connect your Snowflake account when prompted (account credentials or key-pair authentication)
3. Start using the workflows below

---

## Core Workflows

### 1. List Databases

Use `SNOWFLAKE_SHOW_DATABASES` to discover available databases with optional filtering and Time Travel support.

```
Tool: SNOWFLAKE_SHOW_DATABASES
Inputs:
  - like_pattern: string (SQL wildcard, e.g., "%test%") -- case-insensitive
  - starts_with: string (e.g., "PROD") -- case-sensitive
  - limit: integer (max 10000)
  - history: boolean (include dropped databases within Time Travel retention)
  - terse: boolean (return subset of columns: created_on, name, kind, database_name, schema_name)
  - role: string (role to use for execution)
  - warehouse: string (optional, not required for SHOW DATABASES)
  - timeout: integer (seconds)
```

### 2. Browse Schemas

Use `SNOWFLAKE_SHOW_SCHEMAS` to list schemas within a database or across the account.

```
Tool: SNOWFLAKE_SHOW_SCHEMAS
Inputs:
  - database: string (database context)
  - in_scope: "ACCOUNT" | "DATABASE" | "<specific_database_name>"
  - like_pattern: string (SQL wildcard filter)
  - starts_with: string (case-sensitive prefix)
  - limit: integer (max 10000)
  - history: boolean (include dropped schemas)
  - terse: boolean (subset columns only)
  - role, warehouse, timeout: string/integer (optional)
```

### 3. List Tables

Use `SNOWFLAKE_SHOW_TABLES` to discover tables with metadata including row counts, sizes, and clustering keys.

```
Tool: SNOWFLAKE_SHOW_TABLES
Inputs:
  - database: string (database context)
  - schema: string (schema context)
  - in_scope: "ACCOUNT" | "DATABASE" | "SCHEMA" | "<specific_name>"
  - like_pattern: string (e.g., "%customer%")
  - starts_with: string (e.g., "FACT", "DIM", "TEMP")
  - limit: integer (max 10000)
  - history: boolean (include dropped tables)
  - terse: boolean (subset columns only)
  - role, warehouse, timeout: string/integer (optional)
```

### 4. Execute SQL Statements

Use `SNOWFLAKE_EXECUTE_SQL` for SELECT queries, DDL (CREATE/ALTER/DROP), and DML (INSERT/UPDATE/DELETE) with parameterized bindings.

```
Tool: SNOWFLAKE_EXECUTE_SQL
Inputs:
  - statement: string (required) -- SQL statement(s), semicolon-separated for multi-statement
  - database: string (case-sensitive, falls back to DEFAULT_NAMESPACE)
  - schema_name: string (case-sensitive)
  - warehouse: string (case-sensitive, required for compute-bound queries)
  - role: string (case-sensitive, falls back to DEFAULT_ROLE)
  - bindings: object (parameterized query values to prevent SQL injection)
  - parameters: object (Snowflake session-level parameters)
  - timeout: integer (seconds; 0 = max 604800s)
```

**Examples:**
- `"SELECT * FROM my_table LIMIT 100;"`
- `"CREATE TABLE test (id INT, name STRING);"`
- `"ALTER SESSION SET QUERY_TAG='mytag'; SELECT COUNT(*) FROM my_table;"`

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| Case sensitivity | Database, schema, warehouse, and role names are case-sensitive in `SNOWFLAKE_EXECUTE_SQL`. |
| Warehouse required for compute | SELECT and DML queries require a running warehouse. SHOW commands do not. |
| Multi-statement execution | Multiple statements separated by semicolons execute in sequence automatically. |
| SQL injection prevention | Always use the `bindings` parameter for user-supplied values to prevent injection attacks. |
| Pagination with LIMIT | `SHOW` commands support `limit` (max 10000) and `from_name` for cursor-based pagination. |
| Time Travel | Set `history: true` to include dropped objects still within the retention period. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `SNOWFLAKE_SHOW_DATABASES` | List databases with filtering and Time Travel support |
| `SNOWFLAKE_SHOW_SCHEMAS` | List schemas within a database or account-wide |
| `SNOWFLAKE_SHOW_TABLES` | List tables with metadata (row count, size, clustering) |
| `SNOWFLAKE_EXECUTE_SQL` | Execute SQL: SELECT, DDL, DML with parameterized bindings |

---

*Powered by [Composio](https://composio.dev)*
