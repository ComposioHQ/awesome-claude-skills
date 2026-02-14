---
name: gitlab-automation
description: Automate GitLab project management, issues, merge requests, pipelines, branches, and user operations via Rube MCP (Composio). Always search tools first for current schemas.
requires:
  mcp: [rube]
---

# GitLab Automation via Rube MCP

Automate GitLab operations including project management, issue tracking, merge request workflows, CI/CD pipeline monitoring, branch management, and user administration through Composio's GitLab toolkit.

**Toolkit docs**: [composio.dev/toolkits/gitlab](https://composio.dev/toolkits/gitlab)

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active GitLab connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `gitlab`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `gitlab`
3. If connection is not ACTIVE, follow the returned auth link to complete GitLab OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Manage Issues

**When to use**: User wants to create, update, list, or search issues in a GitLab project

**Tool sequence**:
1. `GITLAB_GET_PROJECTS` - Find the target project and get its ID [Prerequisite]
2. `GITLAB_LIST_PROJECT_ISSUES` - List and filter issues for a project [Required]
3. `GITLAB_CREATE_PROJECT_ISSUE` - Create a new issue [Required for create]
4. `GITLAB_UPDATE_PROJECT_ISSUE` - Update an existing issue (title, labels, state, assignees) [Required for update]
5. `GITLAB_LIST_PROJECT_USERS` - Find user IDs for assignment [Optional]

**Key parameters**:
- `id`: Project ID (integer) or URL-encoded path (e.g., `"my-group/my-project"`)
- `title`: Issue title (required for creation)
- `description`: Issue body text (max 1,048,576 characters)
- `labels`: Comma-separated label names (e.g., `"bug,critical"`)
- `add_labels` / `remove_labels`: Add or remove labels without replacing all
- `state`: Filter by `"all"`, `"opened"`, or `"closed"`
- `state_event`: `"close"` or `"reopen"` to change issue state
- `assignee_ids`: Array of user IDs; use `[0]` to unassign all
- `issue_iid`: Internal issue ID within the project (required for updates)
- `milestone`: Filter by milestone title
- `search`: Search in title and description
- `scope`: `"created_by_me"`, `"assigned_to_me"`, or `"all"`
- `page` / `per_page`: Pagination (default per_page: 20)

**Pitfalls**:
- `id` accepts either integer project ID or URL-encoded path; wrong IDs yield 4xx errors
- `issue_iid` is the project-internal ID (shown as #42), different from the global issue ID
- Labels in `labels` field replace ALL existing labels; use `add_labels`/`remove_labels` for incremental changes
- Setting `assignee_ids` to empty array does NOT unassign; use `[0]` instead
- `updated_at` field requires administrator or project/group owner rights

### 2. Manage Merge Requests

**When to use**: User wants to list, filter, or review merge requests in a project

**Tool sequence**:
1. `GITLAB_GET_PROJECT` - Get project details and verify access [Prerequisite]
2. `GITLAB_GET_PROJECT_MERGE_REQUESTS` - List and filter merge requests [Required]
3. `GITLAB_GET_REPOSITORY_BRANCHES` - Verify source/target branches [Optional]
4. `GITLAB_LIST_ALL_PROJECT_MEMBERS` - Find reviewers/assignees [Optional]

**Key parameters**:
- `id`: Project ID or URL-encoded path
- `state`: `"opened"`, `"closed"`, `"locked"`, `"merged"`, or `"all"`
- `scope`: `"created_by_me"` (default), `"assigned_to_me"`, or `"all"`
- `source_branch` / `target_branch`: Filter by branch names
- `author_id` / `author_username`: Filter by MR author
- `assignee_id`: Filter by assignee (use `None` for unassigned, `Any` for assigned)
- `reviewer_id` / `reviewer_username`: Filter by reviewer
- `labels`: Comma-separated label filter
- `search`: Search in title and description
- `wip`: `"yes"` for draft MRs, `"no"` for non-draft
- `order_by`: `"created_at"` (default), `"title"`, `"merged_at"`, `"updated_at"`
- `view`: `"simple"` for minimal fields
- `iids[]`: Filter by specific MR internal IDs

**Pitfalls**:
- Default `scope` is `"created_by_me"` which limits results; use `"all"` for complete listings
- `author_id` and `author_username` are mutually exclusive
- `reviewer_id` and `reviewer_username` are mutually exclusive
- `approved` filter requires the `mr_approved_filter` feature flag (disabled by default)
- Large MR histories can be noisy; use filters and moderate `per_page` values

### 3. Manage Projects and Repositories

**When to use**: User wants to list projects, create new projects, or manage branches

**Tool sequence**:
1. `GITLAB_GET_PROJECTS` - List all accessible projects with filters [Required]
2. `GITLAB_GET_PROJECT` - Get detailed info for a specific project [Optional]
3. `GITLAB_LIST_USER_PROJECTS` - List projects owned by a specific user [Optional]
4. `GITLAB_CREATE_PROJECT` - Create a new project [Required for create]
5. `GITLAB_GET_REPOSITORY_BRANCHES` - List branches in a project [Required for branch ops]
6. `GITLAB_CREATE_REPOSITORY_BRANCH` - Create a new branch [Optional]
7. `GITLAB_GET_REPOSITORY_BRANCH` - Get details of a specific branch [Optional]
8. `GITLAB_LIST_REPOSITORY_COMMITS` - View commit history [Optional]
9. `GITLAB_GET_PROJECT_LANGUAGES` - Get language breakdown [Optional]

**Key parameters**:
- `name` / `path`: Project name and URL-friendly path (both required for creation)
- `visibility`: `"private"`, `"internal"`, or `"public"`
- `namespace_id`: Group or user ID for project placement
- `search`: Case-insensitive substring search for projects
- `membership`: `true` to limit to projects user is a member of
- `owned`: `true` to limit to user-owned projects
- `project_id`: Project ID for branch operations
- `branch_name`: Name for new branch
- `ref`: Source branch or commit SHA for new branch creation
- `order_by`: `"id"`, `"name"`, `"path"`, `"created_at"`, `"updated_at"`, `"star_count"`, `"last_activity_at"`

**Pitfalls**:
- `GITLAB_GET_PROJECTS` pagination is required for complete coverage; stopping at first page misses projects
- Some responses place items under `data.details`; parse the actual returned list structure
- Most follow-up calls depend on correct `project_id`; verify with `GITLAB_GET_PROJECT` first
- Invalid `branch_name`/`ref`/`sha` causes client errors; verify branch existence via `GITLAB_GET_REPOSITORY_BRANCHES` first
- Both `name` and `path` are required for `GITLAB_CREATE_PROJECT`

### 4. Monitor CI/CD Pipelines

**When to use**: User wants to check pipeline status, list jobs, or monitor CI/CD runs

**Tool sequence**:
1. `GITLAB_GET_PROJECT` - Verify project access [Prerequisite]
2. `GITLAB_LIST_PROJECT_PIPELINES` - List pipelines with filters [Required]
3. `GITLAB_GET_SINGLE_PIPELINE` - Get detailed info for a specific pipeline [Optional]
4. `GITLAB_LIST_PIPELINE_JOBS` - List jobs within a pipeline [Optional]

**Key parameters**:
- `id`: Project ID or URL-encoded path
- `status`: Filter by `"created"`, `"waiting_for_resource"`, `"preparing"`, `"pending"`, `"running"`, `"success"`, `"failed"`, `"canceled"`, `"skipped"`, `"manual"`, `"scheduled"`
- `scope`: `"running"`, `"pending"`, `"finished"`, `"branches"`, `"tags"`
- `ref`: Branch or tag name
- `sha`: Specific commit SHA
- `source`: Pipeline source (use `"parent_pipeline"` for child pipelines)
- `order_by`: `"id"` (default), `"status"`, `"ref"`, `"updated_at"`, `"user_id"`
- `created_after` / `created_before`: ISO 8601 date filters
- `pipeline_id`: Specific pipeline ID for job listing
- `include_retried`: `true` to include retried jobs (default `false`)

**Pitfalls**:
- Large pipeline histories can be noisy; use `status`, `ref`, and date filters to narrow results
- Use moderate `per_page` values to keep output manageable
- Pipeline job `scope` accepts single status string or array of statuses
- `yaml_errors: true` returns only pipelines with invalid configurations

### 5. Manage Users and Members

**When to use**: User wants to find users, list project members, or check user status

**Tool sequence**:
1. `GITLAB_GET_USERS` - Search and list GitLab users [Required]
2. `GITLAB_GET_USER` - Get details for a specific user by ID [Optional]
3. `GITLAB_GET_USERS_ID_STATUS` - Get user status message and availability [Optional]
4. `GITLAB_LIST_ALL_PROJECT_MEMBERS` - List all project members (direct + inherited) [Required for member listing]
5. `GITLAB_LIST_PROJECT_USERS` - List project users with search filter [Optional]

**Key parameters**:
- `search`: Search by name, username, or public email
- `username`: Get specific user by username
- `active` / `blocked`: Filter by user state
- `id`: Project ID for member listing
- `query`: Filter members by name, email, or username
- `state`: Filter members by `"awaiting"` or `"active"` (Premium/Ultimate)
- `user_ids`: Filter by specific user IDs

**Pitfalls**:
- Many user filters (admins, auditors, extern_uid, two_factor) are admin-only
- `GITLAB_LIST_ALL_PROJECT_MEMBERS` includes direct, inherited, and invited members
- User search is case-insensitive but may not match partial email domains
- Premium/Ultimate features (state filter, seat info) are not available on free plans

## Common Patterns

### ID Resolution
GitLab uses two identifier formats for projects:
- **Numeric ID**: Integer project ID (e.g., `123`)
- **URL-encoded path**: Namespace/project format (e.g., `"my-group%2Fmy-project"` or `"my-group/my-project"`)
- **Issue IID vs ID**: `issue_iid` is the project-internal number (#42); the global `id` is different
- **User ID**: Numeric; resolve via `GITLAB_GET_USERS` with `search` or `username`

### Pagination
GitLab uses offset-based pagination:
- Set `page` (starting at 1) and `per_page` (1-100, default 20)
- Continue incrementing `page` until response returns fewer items than `per_page` or is empty
- Total count may be available in response headers (`X-Total`, `X-Total-Pages`)
- Always paginate to completion for accurate results

### URL-Encoded Paths
When using project paths as identifiers:
- Forward slashes must be URL-encoded: `my-group/my-project` becomes `my-group%2Fmy-project`
- Some tools accept unencoded paths; check schema for each tool
- Prefer numeric IDs when available for reliability

## Known Pitfalls

### ID Formats
- Project `id` field accepts both integer and string (URL-encoded path)
- Issue `issue_iid` is project-scoped; do not confuse with global issue ID
- Pipeline IDs are project-scoped integers
- User IDs are global integers across the GitLab instance

### Rate Limits
- GitLab has per-user rate limits (typically 300-2000 requests/minute depending on plan)
- Large pipeline/issue histories should use date and status filters to reduce result sets
- Paginate responsibly with moderate `per_page` values

### Parameter Quirks
- `labels` field replaces ALL labels; use `add_labels`/`remove_labels` for incremental changes
- `assignee_ids: [0]` unassigns all; empty array does nothing
- `scope` defaults vary: `"created_by_me"` for MRs, `"all"` for issues
- `author_id` and `author_username` are mutually exclusive in MR filters
- Date parameters use ISO 8601 format: `"2024-01-15T10:30:00Z"`

### Plan Restrictions
- Some features require Premium/Ultimate: `epic_id`, `weight`, `iteration_id`, `approved_by_ids`, member `state` filter
- Admin-only features: user management filters, `updated_at` override, custom attributes
- The `mr_approved_filter` feature flag is disabled by default

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List projects | `GITLAB_GET_PROJECTS` | `search`, `membership`, `visibility` |
| Get project details | `GITLAB_GET_PROJECT` | `id` |
| User's projects | `GITLAB_LIST_USER_PROJECTS` | `id`, `search`, `owned` |
| Create project | `GITLAB_CREATE_PROJECT` | `name`, `path`, `visibility` |
| List issues | `GITLAB_LIST_PROJECT_ISSUES` | `id`, `state`, `labels`, `search` |
| Create issue | `GITLAB_CREATE_PROJECT_ISSUE` | `id`, `title`, `description`, `labels` |
| Update issue | `GITLAB_UPDATE_PROJECT_ISSUE` | `id`, `issue_iid`, `state_event` |
| List merge requests | `GITLAB_GET_PROJECT_MERGE_REQUESTS` | `id`, `state`, `scope`, `labels` |
| List branches | `GITLAB_GET_REPOSITORY_BRANCHES` | `project_id`, `search` |
| Get branch | `GITLAB_GET_REPOSITORY_BRANCH` | `project_id`, `branch_name` |
| Create branch | `GITLAB_CREATE_REPOSITORY_BRANCH` | `project_id`, `branch_name`, `ref` |
| List commits | `GITLAB_LIST_REPOSITORY_COMMITS` | project ID, branch ref |
| Project languages | `GITLAB_GET_PROJECT_LANGUAGES` | project ID |
| List pipelines | `GITLAB_LIST_PROJECT_PIPELINES` | `id`, `status`, `ref` |
| Get pipeline | `GITLAB_GET_SINGLE_PIPELINE` | `project_id`, `pipeline_id` |
| List pipeline jobs | `GITLAB_LIST_PIPELINE_JOBS` | `id`, `pipeline_id`, `scope` |
| Search users | `GITLAB_GET_USERS` | `search`, `username`, `active` |
| Get user | `GITLAB_GET_USER` | user ID |
| User status | `GITLAB_GET_USERS_ID_STATUS` | user ID |
| List project members | `GITLAB_LIST_ALL_PROJECT_MEMBERS` | `id`, `query`, `state` |
| List project users | `GITLAB_LIST_PROJECT_USERS` | `id`, `search` |

---
*Powered by [Composio](https://composio.dev)*
