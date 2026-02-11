---
name: Toggl Automation
description: "Automate time tracking workflows in Toggl Track -- create time entries, manage projects, clients, tags, and workspaces through natural language commands."
requires:
  mcp:
    - rube
---

# Toggl Automation

Automate your Toggl Track time tracking operations directly from Claude Code. Log time, manage projects and clients, organize with tags, and control workspaces -- all without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/toggl](https://composio.dev/toolkits/toggl)

---

## Setup

1. Add the Rube MCP server to your Claude Code config with URL: `https://rube.app/mcp`
2. When prompted, authenticate your Toggl Track account through the connection link provided
3. Start automating your time tracking workflows with natural language

---

## Core Workflows

### 1. Create and Stop Time Entries

Log time with project, task, and tag associations, or start/stop timers.

**Tools:** `TOGGL_CREATE_TIME_ENTRY`, `TOGGL_PATCH_STOP_TIME_ENTRY`

```
Start a time entry in workspace 123456 for project 78910 tagged "meeting" and "design" with description "Design review session"
```

Key parameters for `TOGGL_CREATE_TIME_ENTRY`:
- `workspace_id` (required) -- target workspace
- `created_with` (required) -- client application name (e.g., `"api_client"`)
- `start` (required) -- ISO 8601 timestamp
- `stop` -- ISO 8601 end time; omit to leave the entry running
- `duration` -- duration in seconds; omit for running entries
- `project_id` -- associate with a project
- `task_id` -- associate with a task
- `tags` -- array of tag name strings (not IDs)
- `description` -- description of the work
- `billable` -- billable status

Key parameters for `TOGGL_PATCH_STOP_TIME_ENTRY`:
- `workspace_id` (required) and `time_entry_id` (required)

### 2. Manage Projects

Create new projects and list existing ones with client details and pagination.

**Tools:** `TOGGL_CREATE_PROJECT`, `TOGGL_GET_PROJECTS`, `TOGGL_GET_PROJECT_DETAILS`

```
Create a private billable project called "Q1 Marketing Campaign" in workspace 123456 for client 78910
```

Key parameters for `TOGGL_CREATE_PROJECT`:
- `workspace_id` (required) and `name` (required)
- `client_id`, `billable`, `is_private`, `active`, `color`
- `estimated_hours`, `rate`, `fixed_fee`, `currency` (premium features)

Key parameters for `TOGGL_GET_PROJECTS`:
- `workspace_id` (required)
- `page` / `page_size` (1-200) for pagination
- `since` / `until` -- Unix timestamps for modification filtering (last 3 months only)
- `clients: true` to include full client details

### 3. Manage Clients

Create and list clients within a workspace.

**Tools:** `TOGGL_CREATE_CLIENT`, `TOGGL_GET_LIST_CLIENTS`

```
List all active clients in workspace 123456, then create a new client called "Acme Corp"
```

- `TOGGL_CREATE_CLIENT` requires `workspace_id` and `name`; accepts `notes`, `external_reference`
- `TOGGL_GET_LIST_CLIENTS` requires `workspace_id`; supports `status` (`"active"`, `"archived"`, `"both"`) and `name` (case-insensitive search)

### 4. Tags and Workspace Preferences

Retrieve tags for categorization and check workspace settings.

**Tools:** `TOGGL_GET_TAGS`, `TOGGL_GET_WORKSPACE_PREFERENCES`

```
Show me all tags in workspace 123456 and the workspace preferences
```

- `TOGGL_GET_TAGS` requires `workspace_id`; returns tag IDs and names
- `TOGGL_GET_WORKSPACE_PREFERENCES` requires `workspace_id`; returns pricing plan and display settings

### 5. Workspace Discovery

List all workspaces the authenticated user belongs to.

**Tool:** `TOGGL_GET_USER_WORKSPACES`

```
What Toggl workspaces do I have access to?
```

- No parameters required
- Returns all workspaces with IDs, names, and metadata
- Use this first to discover workspace IDs for other operations

### 6. User Project Visibility

List projects visible to the authenticated user.

**Tool:** `TOGGL_GET_USER_PROJECTS`

```
Show me all projects I can see across my workspaces
```

- Returns projects the authenticated user has access to
- Use alongside `TOGGL_GET_PROJECTS` for workspace-scoped views

---

## Known Pitfalls

- **Tags use names, not IDs:** `TOGGL_CREATE_TIME_ENTRY` accepts tag names as strings in the `tags` array, unlike many APIs that use IDs. Use `TOGGL_GET_TAGS` to verify available tag names.
- **`created_with` is required:** Every time entry must include `created_with` (e.g., `"api_client"`). Missing this field causes silent failures.
- **Duration is in seconds:** The `duration` parameter on time entries is in seconds, not hours. 1 hour = 3600 seconds.
- **`since` timestamp restriction:** The `since` filter on `TOGGL_GET_PROJECTS` only allows timestamps within the last 3 months. Older queries will be rejected.
- **Premium features gated:** Custom colors, templates, fixed fees, and hourly rates on projects require a premium Toggl plan. Non-premium accounts will get errors when using these fields.
- **Workspace ID required everywhere:** Nearly all Toggl tools require `workspace_id`. Always call `TOGGL_GET_USER_WORKSPACES` first to resolve it.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `TOGGL_CREATE_TIME_ENTRY` | Create a time entry or running timer (requires `workspace_id`, `created_with`, `start`) |
| `TOGGL_PATCH_STOP_TIME_ENTRY` | Stop a running time entry (requires `workspace_id`, `time_entry_id`) |
| `TOGGL_GET_PROJECTS` | List projects in a workspace with pagination |
| `TOGGL_GET_PROJECT_DETAILS` | Get details for a specific project |
| `TOGGL_CREATE_PROJECT` | Create a new project (requires `workspace_id`, `name`) |
| `TOGGL_GET_LIST_CLIENTS` | List clients with status/name filters (requires `workspace_id`) |
| `TOGGL_CREATE_CLIENT` | Create a new client (requires `workspace_id`, `name`) |
| `TOGGL_GET_TAGS` | List all tags in a workspace (requires `workspace_id`) |
| `TOGGL_GET_WORKSPACE_PREFERENCES` | Get workspace settings (requires `workspace_id`) |
| `TOGGL_GET_USER_WORKSPACES` | List all workspaces for the authenticated user |
| `TOGGL_GET_USER_PROJECTS` | List projects visible to the authenticated user |

---

*Powered by [Composio](https://composio.dev)*
