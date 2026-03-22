---
name: Neon Automation
description: "Automate Neon serverless Postgres operations -- manage projects, branches, databases, roles, and connection URIs via the Composio MCP integration."
requires:
  mcp:
    - rube
---

# Neon Automation

Automate your Neon serverless Postgres workflows -- list projects and branches, inspect databases, retrieve connection URIs, manage roles, and integrate Neon database operations into cross-app pipelines.

**Toolkit docs:** [composio.dev/toolkits/neon](https://composio.dev/toolkits/neon)

---

## Setup

1. Add the Composio MCP server to your client: `https://rube.app/mcp`
2. Connect your Neon account when prompted (API key authentication)
3. Start using the workflows below

---

## Core Workflows

### 1. List Projects

Use `NEON_RETRIEVE_PROJECTS_LIST` to discover all projects associated with the authenticated user.

```
Tool: NEON_RETRIEVE_PROJECTS_LIST
Inputs:
  - org_id: string (REQUIRED when using a personal API key)
  - limit: integer (1-400, default 10)
  - cursor: string (pagination cursor from previous response)
  - search: string (search by project name or ID, supports partial match)
  - timeout: integer (milliseconds; returns partial results on timeout)
```

**Important:** When using a personal API key, `org_id` is required. Retrieve it first via `NEON_GET_USER_ORGANIZATIONS`.

### 2. Get Project Details

Use `NEON_ACCESS_PROJECT_DETAILS_BY_ID` to inspect project configuration, owner info, and consumption metrics.

```
Tool: NEON_ACCESS_PROJECT_DETAILS_BY_ID
Inputs:
  - project_id: string (required) -- format: "adjective-noun-number", e.g., "dry-smoke-26258271"
```

### 3. List Branches for a Project

Use `NEON_GET_BRANCHES_FOR_PROJECT` to enumerate branches (development stages) within a project.

```
Tool: NEON_GET_BRANCHES_FOR_PROJECT
Inputs:
  - project_id: string (required)
  - search: string (optional, search by branch name or ID)
```

### 4. List Databases on a Branch

Use `NEON_FETCH_DATABASE_FOR_BRANCH` to inventory databases within a specific project and branch.

```
Tool: NEON_FETCH_DATABASE_FOR_BRANCH
Inputs:
  - project_id: string (required)
  - branch_id: string (required)
```

### 5. Get Connection URI

Use `NEON_GET_PROJECT_CONNECTION_URI` to obtain a Postgres connection string for a project/branch/database.

```
Tool: NEON_GET_PROJECT_CONNECTION_URI
Inputs:
  - project_id: string (required)
  - database_name: string (required) -- e.g., "neondb"
  - role_name: string (required) -- e.g., "neondb_owner"
  - branch_id: string (optional, defaults to project default branch)
  - endpoint_id: string (optional, defaults to read-write endpoint)
  - pooled: boolean (optional, adds -pooler for connection pooling)
```

**Security:** The returned URI includes credentials. Treat it as a secret -- do not log or share it.

### 6. Inspect Database Details and Roles

Use `NEON_RETRIEVE_BRANCH_DATABASE_DETAILS` to verify a database before connecting, and `NEON_GET_BRANCH_ROLES_FOR_PROJECT` to list available roles.

```
Tool: NEON_RETRIEVE_BRANCH_DATABASE_DETAILS
Inputs:
  - project_id: string (required)
  - branch_id: string (required)
  - database_name: string (required)

Tool: NEON_GET_BRANCH_ROLES_FOR_PROJECT
Inputs:
  - project_id: string (required)
  - branch_id: string (required)
```

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| org_id required | `NEON_RETRIEVE_PROJECTS_LIST` returns HTTP 400 "org_id is required" when using a personal API key. Call `NEON_GET_USER_ORGANIZATIONS` first. |
| Incomplete pagination | Project lists may be incomplete without pagination. Iterate using `cursor` until it is empty. |
| Rate limiting | `NEON_RETRIEVE_PROJECTS_LIST` returns HTTP 429 on bursty listing. Avoid redundant calls and back off before retrying. |
| Invalid role/database pairing | `NEON_GET_PROJECT_CONNECTION_URI` returns 401/403 when the database_name/role_name pairing is invalid. Use `NEON_GET_BRANCH_ROLES_FOR_PROJECT` to select an allowed role. |
| Connection URI is a secret | The returned URI includes credentials. Never log, display, or share it in plain text. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `NEON_RETRIEVE_PROJECTS_LIST` | List all Neon projects with pagination and search |
| `NEON_ACCESS_PROJECT_DETAILS_BY_ID` | Get project configuration and consumption metrics |
| `NEON_GET_BRANCHES_FOR_PROJECT` | List branches within a project |
| `NEON_FETCH_DATABASE_FOR_BRANCH` | List databases on a specific branch |
| `NEON_GET_PROJECT_CONNECTION_URI` | Get a Postgres connection URI (with credentials) |
| `NEON_RETRIEVE_BRANCH_DATABASE_DETAILS` | Inspect database metadata and settings |
| `NEON_GET_USER_ORGANIZATIONS` | List organizations for the authenticated user |
| `NEON_CREATE_API_KEY_FOR_ORGANIZATION` | Create a new API key for an organization |
| `NEON_GET_BRANCH_ROLES_FOR_PROJECT` | List roles available on a branch |

---

*Powered by [Composio](https://composio.dev)*
