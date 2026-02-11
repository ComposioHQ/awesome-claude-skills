---
name: Clockify Automation
description: "Automate time tracking workflows in Clockify -- create and manage time entries, workspaces, and users through natural language commands."
requires:
  mcp:
    - rube
---

# Clockify Automation

Automate your Clockify time tracking operations directly from Claude Code. Log time entries, query historical data, manage workspaces, and audit team activity -- all without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/clockify](https://composio.dev/toolkits/clockify)

---

## Setup

1. Add the Rube MCP server to your Claude Code config with URL: `https://rube.app/mcp`
2. When prompted, authenticate your Clockify account through the connection link provided
3. Start automating your time tracking workflows with natural language

---

## Core Workflows

### 1. Create Time Entries

Log time with project, task, and tag associations, plus billable status.

**Tool:** `CLOCKIFY_CREATE_TIME_ENTRY`

```
Log 2 hours of work on project 64a687e2 in workspace 64a687e3 starting at 9am UTC today with description "API development"
```

Key parameters:
- `workspaceId` (required) -- workspace where the entry is created
- `start` (required) -- ISO 8601 start time (e.g., `2026-02-11T09:00:00Z`)
- `end` -- ISO 8601 end time; omit to create a running timer
- `projectId` -- associate with a project
- `taskId` -- associate with a task
- `description` -- work description (0-3000 chars)
- `tagIds` -- array of tag IDs
- `billable` -- whether the entry is billable
- `customFieldValues` -- array of custom field entries with `customFieldId` and `value`

### 2. Query Time Entries

Retrieve historical time entries for reporting, auditing, and invoicing.

**Tool:** `CLOCKIFY_GET_TIME_ENTRIES`

```
Get all time entries for user abc123 in workspace xyz789 from January 2026
```

Key parameters:
- `workspaceId` (required) -- workspace to query
- `userId` (required) -- user whose entries to retrieve
- `start` / `end` -- ISO 8601 date range filters
- `project` -- filter by project ID
- `task` -- filter by task ID
- `tags` -- comma-separated tag IDs
- `description` -- text filter (partial match)
- `hydrated` -- set `true` to get full project/task/tag objects instead of just IDs
- `in-progress` -- set `true` to return only the running timer
- `page` / `page-size` -- pagination (default 50 per page)

### 3. Delete Time Entries

Remove erroneous, duplicate, or cancelled time entries.

**Tool:** `CLOCKIFY_DELETE_TIME_ENTRY`

```
Delete time entry 5b715448 from workspace 64a687e3
```

- Requires `workspaceId` and `id` (the time entry ID)
- Use for cleanup of bad imports or duplicates

### 4. Manage Workspaces

List all workspaces the authenticated user belongs to.

**Tool:** `CLOCKIFY_GET_ALL_MY_WORKSPACES`

```
Show me all my Clockify workspaces
```

- Optional `roles` filter -- array of roles like `["WORKSPACE_ADMIN", "OWNER"]`
- Use this to discover workspace IDs before creating or querying entries

### 5. User Information

Retrieve current user details and list workspace members.

**Tools:** `CLOCKIFY_GET_CURRENTLY_LOGGED_IN_USER_INFO`, `CLOCKIFY_FIND_ALL_USERS_ON_WORKSPACE`

```
Who am I logged in as? Then list all users in workspace 64a687e3
```

- `CLOCKIFY_GET_CURRENTLY_LOGGED_IN_USER_INFO` returns the authenticated user's profile (no parameters needed)
- `CLOCKIFY_FIND_ALL_USERS_ON_WORKSPACE` requires `workspaceId`; supports `name`, `email` filters and pagination (`page`, `page-size` max 100)

### 6. Running Timer Management

Start a timer by omitting `end` in create, or check for running entries.

**Tools:** `CLOCKIFY_CREATE_TIME_ENTRY`, `CLOCKIFY_GET_TIME_ENTRIES`

```
Start a timer on project abc in workspace xyz with description "Working on bug fix"
```

- Create without `end` to start a running timer
- Use `CLOCKIFY_GET_TIME_ENTRIES` with `in-progress: true` to check if a timer is running

---

## Known Pitfalls

- **Workspace and user IDs are required:** Most Clockify tools require both `workspaceId` and `userId`. Always call `CLOCKIFY_GET_ALL_MY_WORKSPACES` and `CLOCKIFY_GET_CURRENTLY_LOGGED_IN_USER_INFO` first to resolve these IDs.
- **ISO 8601 timestamps:** All time parameters must be in ISO 8601 format with timezone (e.g., `2026-02-11T09:00:00Z`). Omitting the timezone causes unpredictable behavior.
- **Running timers:** Only one timer can run at a time. Creating a new entry without `end` will fail if another timer is already active. Stop the existing timer first.
- **Pagination defaults:** `CLOCKIFY_GET_TIME_ENTRIES` defaults to 50 entries per page. For full exports, loop through pages until no more results are returned.
- **Tag IDs are workspace-scoped:** Tag IDs from one workspace cannot be used in another. Always resolve tags within the target workspace context.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `CLOCKIFY_CREATE_TIME_ENTRY` | Create a time entry or start a timer (requires `workspaceId`, `start`) |
| `CLOCKIFY_GET_TIME_ENTRIES` | List time entries with filters (requires `workspaceId`, `userId`) |
| `CLOCKIFY_DELETE_TIME_ENTRY` | Delete a time entry (requires `workspaceId`, `id`) |
| `CLOCKIFY_GET_ALL_MY_WORKSPACES` | List all workspaces for the authenticated user |
| `CLOCKIFY_GET_CURRENTLY_LOGGED_IN_USER_INFO` | Get current user profile info |
| `CLOCKIFY_FIND_ALL_USERS_ON_WORKSPACE` | List all users in a workspace (requires `workspaceId`) |

---

*Powered by [Composio](https://composio.dev)*
