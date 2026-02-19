---
name: FreshBooks Automation
description: "FreshBooks Automation: manage businesses, projects, time tracking, and billing in FreshBooks cloud accounting"
requires:
  mcp: [rube]
---

# FreshBooks Automation

Automate FreshBooks operations including listing businesses, managing projects, tracking time, and monitoring budgets for small and medium-sized business accounting.

**Toolkit docs:** [composio.dev/toolkits/freshbooks](https://composio.dev/toolkits/freshbooks)

---

## Setup

This skill requires the **Rube MCP server** connected at `https://rube.app/mcp`.

Before executing any tools, ensure an active connection exists for the `freshbooks` toolkit. If no connection is active, initiate one via `RUBE_MANAGE_CONNECTIONS`.

---

## Core Workflows

### 1. List Businesses

Retrieve all businesses associated with the authenticated user. The `business_id` from this response is required for most other FreshBooks API calls.

**Tool:** `FRESHBOOKS_LIST_BUSINESSES`

**Parameters:** None required.

**Example:**
```
Tool: FRESHBOOKS_LIST_BUSINESSES
Arguments: {}
```

**Output:** Returns business membership information including all businesses the user has access to, along with their role in each business.

> **Important:** Always call this first to obtain a valid `business_id` before performing project-specific operations.

---

### 2. List and Filter Projects

Retrieve all projects for a business with comprehensive filtering and sorting options.

**Tool:** `FRESHBOOKS_LIST_PROJECTS`

**Key Parameters:**
- `business_id` (required) -- Business ID obtained from `FRESHBOOKS_LIST_BUSINESSES`
- `active` -- Filter by active status: `true` (active only), `false` (inactive only), omit for all
- `complete` -- Filter by completion: `true` (completed), `false` (incomplete), omit for all
- `sort_by` -- Sort order: `"created_at"`, `"due_date"`, or `"title"`
- `updated_since` -- UTC datetime in RFC3339 format, e.g., `"2026-01-01T00:00:00Z"`
- `include_logged_duration` -- `true` to include total logged time (in seconds) per project
- `skip_group` -- `true` to omit team member/invitation data (reduces response size)

**Example:**
```
Tool: FRESHBOOKS_LIST_PROJECTS
Arguments:
  business_id: 123456
  active: true
  complete: false
  sort_by: "due_date"
  include_logged_duration: true
```

**Use Cases:**
- Get all projects for time tracking or invoicing
- Find projects by client, status, or date range
- Monitor project completion and budget tracking
- Retrieve team assignments and project groups

---

### 3. Monitor Active Projects

Track project progress and budgets by filtering for active, incomplete projects.

**Steps:**
1. Call `FRESHBOOKS_LIST_BUSINESSES` to get `business_id`
2. Call `FRESHBOOKS_LIST_PROJECTS` with `active: true`, `complete: false`, `include_logged_duration: true`
3. Analyze logged duration vs. budget for each project

---

### 4. Review Recently Updated Projects

Check for recent project activity using the `updated_since` filter.

**Steps:**
1. Call `FRESHBOOKS_LIST_BUSINESSES` to get `business_id`
2. Call `FRESHBOOKS_LIST_PROJECTS` with `updated_since` set to your cutoff datetime
3. Review returned projects for recent changes

**Example:**
```
Tool: FRESHBOOKS_LIST_PROJECTS
Arguments:
  business_id: 123456
  updated_since: "2026-02-01T00:00:00Z"
  sort_by: "created_at"
```

---

## Recommended Execution Plan

1. **Get the business ID** by calling `FRESHBOOKS_LIST_BUSINESSES`
2. **List projects** using `FRESHBOOKS_LIST_PROJECTS` with the obtained `business_id`
3. **Filter as needed** using `active`, `complete`, `updated_since`, and `sort_by` parameters

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| **business_id required** | Most FreshBooks operations require a `business_id`. Always call `FRESHBOOKS_LIST_BUSINESSES` first to obtain it. |
| **Date format** | The `updated_since` parameter must be in RFC3339 format: `"2026-01-01T00:00:00Z"`. Other formats will fail. |
| **Paginated results** | Project list responses are paginated. Check for additional pages in the response. |
| **Empty results** | Returns an empty list if no projects exist or match the applied filters. This is not an error. |
| **Logged duration units** | When `include_logged_duration` is true, the duration is returned in seconds. Convert to hours (divide by 3600) for display. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `FRESHBOOKS_LIST_BUSINESSES` | List all businesses for the authenticated user |
| `FRESHBOOKS_LIST_PROJECTS` | List projects with filtering and sorting for a business |

---

*Powered by [Composio](https://composio.dev)*
