---
name: Harvest Automation
description: "Automate time tracking, project management, and invoicing workflows in Harvest -- log hours, manage projects, clients, and tasks through natural language commands."
requires:
  mcp:
    - rube
---

# Harvest Automation

Automate your Harvest time tracking operations directly from Claude Code. Log time entries, manage projects and clients, create tasks, and pull reporting data -- all without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/harvest](https://composio.dev/toolkits/harvest)

---

## Setup

1. Add the Rube MCP server to your Claude Code config with URL: `https://rube.app/mcp`
2. When prompted, authenticate your Harvest account through the connection link provided
3. Start automating your time tracking workflows with natural language

---

## Core Workflows

### 1. Log and Manage Time Entries

Create, list, update, and retrieve time entries for accurate billing and reporting.

**Tools:** `HARVEST_CREATE_TIME_ENTRY`, `HARVEST_LIST_TIME_ENTRIES`, `HARVEST_GET_TIME_ENTRY`, `HARVEST_UPDATE_TIME_ENTRY`

```
Log 3.5 hours of development work on project 12345, task 67890 for today
```

Key parameters for `HARVEST_CREATE_TIME_ENTRY`:
- `project_id` (required) -- the project to log against
- `task_id` (required) -- the task must be assigned to the project
- `spent_date` (required) -- date in YYYY-MM-DD format
- `hours` -- total hours (for duration-based accounts)
- `started_time` / `ended_time` -- for timestamp-based accounts
- `notes` -- description of work performed

Key parameters for `HARVEST_LIST_TIME_ENTRIES`:
- `from_date` / `to` -- date range filters (YYYY-MM-DD)
- `project_id`, `client_id`, `task_id`, `user_id` -- entity filters
- `is_billed` / `is_running` -- status filters
- `page` / `per_page` (max 2000) -- pagination

### 2. Manage Projects

Create new projects and list existing ones with client and billing configuration.

**Tools:** `HARVEST_CREATE_PROJECT`, `HARVEST_LIST_PROJECTS`, `HARVEST_GET_PROJECT`

```
Create a billable project called "Website Redesign" for client 456 with Tasks billing and project budget
```

Key parameters for `HARVEST_CREATE_PROJECT`:
- `name`, `client_id`, `is_billable`, `bill_by`, `budget_by` (all required)
- `bill_by` options: `"Project"`, `"Tasks"`, `"People"`, `"none"`
- `budget_by` options: `"project"`, `"project_cost"`, `"task"`, `"task_fees"`, `"person"`, `"none"`
- Optional: `budget`, `hourly_rate`, `starts_on`, `ends_on`, `is_fixed_fee`

### 3. Manage Clients

Create and list clients that projects are organized under.

**Tools:** `HARVEST_CREATE_CLIENT`, `HARVEST_LIST_CLIENTS`

```
List all active clients in our Harvest account
```

- `HARVEST_CREATE_CLIENT` requires `name`; accepts `address`, `currency`, `is_active`
- `HARVEST_LIST_CLIENTS` supports `is_active` filter and pagination (`per_page` max 2000)

### 4. Manage Tasks

Create and list reusable task types for time tracking.

**Tools:** `HARVEST_CREATE_TASK`, `HARVEST_LIST_TASKS`

```
Create a new billable task called "Code Review" with a default rate of $150/hr
```

- `HARVEST_CREATE_TASK` requires `name`; accepts `billable_by_default`, `default_hourly_rate`, `is_active`, `is_default`
- `HARVEST_LIST_TASKS` supports `is_active`, `is_default` filters and pagination (`per_page` max 100)
- Task names must be unique across all tasks (active and archived)

### 5. Time Entry Reporting

Pull time entries with date ranges and filters for billing summaries and utilization reports.

**Tools:** `HARVEST_LIST_TIME_ENTRIES`, `HARVEST_GET_TIME_ENTRY`

```
Show me all unbilled time entries for project 789 from January 2026
```

- Use `from_date` and `to` for date windowing
- Filter with `is_billed: false` for unbilled entries
- Combine `project_id`, `user_id`, `client_id` for cross-dimensional reporting
- Paginate with `page` and `per_page` to gather complete datasets

### 6. Update and Correct Time Entries

Modify existing time entries to fix hours, reassign projects, or update notes.

**Tools:** `HARVEST_UPDATE_TIME_ENTRY`

```
Update time entry 123456 to change the hours to 4.0 and add the note "Completed API integration"
```

- Requires `time_entry_id`
- Supports partial updates -- only include fields you want to change
- Can update `hours`, `notes`, `project_id`, `task_id`, `spent_date`, `started_time`, `ended_time`

---

## Known Pitfalls

- **Task assignment matters:** When creating time entries, the `task_id` must correspond to a task that is actually assigned to the specified `project_id`. Use project task assignments endpoint to verify, not just `HARVEST_LIST_TASKS` (which returns global tasks).
- **Duration vs. timestamp tracking:** Harvest accounts are configured for either duration-based or timestamp-based tracking. `hours` is ignored on timestamp accounts; `started_time`/`ended_time` are ignored on duration accounts.
- **Pagination limits vary:** `HARVEST_LIST_TIME_ENTRIES` and `HARVEST_LIST_CLIENTS` support up to 2000 per page, but `HARVEST_LIST_PROJECTS` and `HARVEST_LIST_TASKS` cap at 100 per page.
- **Date format consistency:** All date parameters must use `YYYY-MM-DD` format. ISO 8601 with timezone is used for `updated_since` filters.
- **Required fields for projects:** `HARVEST_CREATE_PROJECT` requires five fields: `name`, `client_id`, `is_billable`, `bill_by`, and `budget_by`. Missing any will cause a validation error.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `HARVEST_LIST_TIME_ENTRIES` | List time entries with date, project, client, user filters |
| `HARVEST_CREATE_TIME_ENTRY` | Log a new time entry (requires `project_id`, `task_id`, `spent_date`) |
| `HARVEST_GET_TIME_ENTRY` | Retrieve a specific time entry by ID |
| `HARVEST_UPDATE_TIME_ENTRY` | Update an existing time entry (requires `time_entry_id`) |
| `HARVEST_LIST_PROJECTS` | List projects with optional client filter |
| `HARVEST_CREATE_PROJECT` | Create a new project with billing config |
| `HARVEST_GET_PROJECT` | Retrieve a specific project by ID |
| `HARVEST_LIST_CLIENTS` | List clients with active/inactive filter |
| `HARVEST_CREATE_CLIENT` | Create a new client (requires `name`) |
| `HARVEST_LIST_TASKS` | List reusable task types |
| `HARVEST_CREATE_TASK` | Create a new task type (requires `name`) |

---

*Powered by [Composio](https://composio.dev)*
