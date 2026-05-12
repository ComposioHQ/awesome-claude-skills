---
name: baserow-automation
description: >
  Create, read, update, and delete rows in Baserow tables, manage fields,
  and query records via Rube MCP (Composio). Use when the user mentions
  "Baserow", "no-code database", or needs to interact with Baserow tables,
  rows, or fields.
requires:
  mcp: [rube]
---

# Baserow Automation via Rube MCP

Automate Baserow operations through Composio's Baserow toolkit via Rube MCP.

**Toolkit docs**: [composio.dev/toolkits/baserow](https://composio.dev/toolkits/baserow)

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Baserow connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `baserow`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.

1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `baserow`
3. If connection is not ACTIVE, follow the returned auth link to complete setup
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflow

### Step 1: Discover tools

```
RUBE_SEARCH_TOOLS
queries: [{use_case: "list rows in a Baserow table", known_fields: ""}]
session: {generate_id: true}
```

### Step 2: Check connection

```
RUBE_MANAGE_CONNECTIONS
toolkits: ["baserow"]
session_id: "your_session_id"
```

Verify status is ACTIVE before continuing.

### Step 3: Execute

```
RUBE_MULTI_EXECUTE_TOOL
tools: [{
  tool_slug: "BASEROW_LIST_ROWS",
  arguments: {"table_id": 42, "page": 1, "size": 50}
}]
memory: {}
session_id: "your_session_id"
```

## Known Pitfalls

- **Always search first**: Tool schemas change. Never hardcode tool slugs or arguments without calling `RUBE_SEARCH_TOOLS`
- **Check connection**: Verify `RUBE_MANAGE_CONNECTIONS` shows ACTIVE status before executing tools
- **Schema compliance**: Use exact field names and types from the search results
- **Memory parameter**: Always include `memory` in `RUBE_MULTI_EXECUTE_TOOL` calls, even if empty (`{}`)
- **Session reuse**: Reuse session IDs within a workflow. Generate new ones for new workflows
- **Pagination**: Check responses for pagination tokens and continue fetching until complete

## Quick Reference

| Operation | Approach |
|-----------|----------|
| Find tools | `RUBE_SEARCH_TOOLS` with Baserow-specific use case |
| Connect | `RUBE_MANAGE_CONNECTIONS` with toolkit `baserow` |
| Execute | `RUBE_MULTI_EXECUTE_TOOL` with discovered tool slugs |
| Bulk ops | `RUBE_REMOTE_WORKBENCH` with `run_composio_tool()` |
| Full schema | `RUBE_GET_TOOL_SCHEMAS` for tools with `schemaRef` |

---
*Powered by [Composio](https://composio.dev)*
