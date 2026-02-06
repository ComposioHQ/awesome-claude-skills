---
name: jira-automation
description: "Automate Jira tasks via Rube MCP (Composio): issues, projects, sprints, boards, comments, users. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Jira Automation via Rube MCP

Automate Jira operations through Composio's Jira toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Jira connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `jira`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `jira`
3. If connection is not ACTIVE, follow the returned auth link to complete Jira OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Search and Filter Issues

**When to use**: User wants to find issues using JQL or browse project issues

**Tool sequence**:
1. `JIRA_SEARCH_FOR_ISSUES_USING_JQL_POST` - Search with JQL query [Required]
2. `JIRA_GET_ISSUE` - Get full details of a specific issue [Optional]

**Key parameters**:
- `jql`: JQL query string (e.g., `project = PROJ AND status = "In Progress"`)
- `maxResults`: Max results per page (default 50, max 100)
- `startAt`: Pagination offset
- `fields`: Array of field names to return
- `issueIdOrKey`: Issue key like 'PROJ-123' for GET_ISSUE

**Pitfalls**:
- JQL field names are case-sensitive and must match Jira configuration
- Custom fields use IDs like `customfield_10001`, not display names
- Results are paginated; check `total` vs `startAt + maxResults` to continue

### 2. Create and Edit Issues

**When to use**: User wants to create new issues or update existing ones

**Tool sequence**:
1. `JIRA_GET_ALL_PROJECTS` - List projects to find project key [Prerequisite]
2. `JIRA_GET_FIELDS` - Get available fields and their IDs [Prerequisite]
3. `JIRA_CREATE_ISSUE` - Create a new issue [Required]
4. `JIRA_EDIT_ISSUE` - Update fields on an existing issue [Optional]
5. `JIRA_ASSIGN_ISSUE` - Assign issue to a user [Optional]

**Key parameters**:
- `project`: Project key (e.g., 'PROJ')
- `issuetype`: Issue type name (e.g., 'Bug', 'Story', 'Task')
- `summary`: Issue title
- `description`: Issue description (Atlassian Document Format or plain text)
- `issueIdOrKey`: Issue key for edits

**Pitfalls**:
- Issue types and required fields vary by project; use GET_FIELDS to check
- Custom fields require exact field IDs, not display names
- Description may need Atlassian Document Format (ADF) for rich content

### 3. Manage Sprints and Boards

**When to use**: User wants to work with agile boards, sprints, and backlogs

**Tool sequence**:
1. `JIRA_LIST_BOARDS` - List all boards [Prerequisite]
2. `JIRA_LIST_SPRINTS` - List sprints for a board [Required]
3. `JIRA_MOVE_ISSUE_TO_SPRINT` - Move issue to a sprint [Optional]
4. `JIRA_CREATE_SPRINT` - Create a new sprint [Optional]

**Key parameters**:
- `boardId`: Board ID from LIST_BOARDS
- `sprintId`: Sprint ID for move operations
- `name`: Sprint name for creation
- `startDate`/`endDate`: Sprint dates in ISO format

**Pitfalls**:
- Boards and sprints are specific to Jira Software (not Jira Core)
- Only one sprint can be active at a time per board

### 4. Manage Comments

**When to use**: User wants to add or view comments on issues

**Tool sequence**:
1. `JIRA_LIST_ISSUE_COMMENTS` - List existing comments [Optional]
2. `JIRA_ADD_COMMENT` - Add a comment to an issue [Required]

**Key parameters**:
- `issueIdOrKey`: Issue key like 'PROJ-123'
- `body`: Comment body (supports ADF for rich text)

**Pitfalls**:
- Comments support ADF (Atlassian Document Format) for formatting
- Mentions use account IDs, not usernames

### 5. Manage Projects and Users

**When to use**: User wants to list projects, find users, or manage project roles

**Tool sequence**:
1. `JIRA_GET_ALL_PROJECTS` - List all projects [Optional]
2. `JIRA_GET_PROJECT` - Get project details [Optional]
3. `JIRA_FIND_USERS` / `JIRA_GET_ALL_USERS` - Search for users [Optional]
4. `JIRA_GET_PROJECT_ROLES` - List project roles [Optional]
5. `JIRA_ADD_USERS_TO_PROJECT_ROLE` - Add user to role [Optional]

**Key parameters**:
- `projectIdOrKey`: Project key
- `query`: Search text for FIND_USERS
- `roleId`: Role ID for role operations

**Pitfalls**:
- User operations use account IDs (not email or display name)
- Project roles differ from global permissions

## Common Patterns

### JQL Syntax

**Common operators**:
- `project = "PROJ"` - Filter by project
- `status = "In Progress"` - Filter by status
- `assignee = currentUser()` - Current user's issues
- `created >= -7d` - Created in last 7 days
- `labels = "bug"` - Filter by label
- `priority = High` - Filter by priority
- `ORDER BY created DESC` - Sort results

**Combinators**:
- `AND` - Both conditions
- `OR` - Either condition
- `NOT` - Negate condition

### Pagination

- Use `startAt` and `maxResults` parameters
- Check `total` in response to determine remaining pages
- Continue until `startAt + maxResults >= total`

## Known Pitfalls

**Field Names**:
- Custom fields use IDs like `customfield_10001`
- Use JIRA_GET_FIELDS to discover field IDs and names
- Field names in JQL may differ from API field names

**Authentication**:
- Jira Cloud uses account IDs, not usernames
- Site URL must be configured correctly in the connection

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Search issues (JQL) | JIRA_SEARCH_FOR_ISSUES_USING_JQL_POST | jql, maxResults |
| Get issue | JIRA_GET_ISSUE | issueIdOrKey |
| Create issue | JIRA_CREATE_ISSUE | project, issuetype, summary |
| Edit issue | JIRA_EDIT_ISSUE | issueIdOrKey, fields |
| Assign issue | JIRA_ASSIGN_ISSUE | issueIdOrKey, accountId |
| Add comment | JIRA_ADD_COMMENT | issueIdOrKey, body |
| List comments | JIRA_LIST_ISSUE_COMMENTS | issueIdOrKey |
| List projects | JIRA_GET_ALL_PROJECTS | (none) |
| Get project | JIRA_GET_PROJECT | projectIdOrKey |
| List boards | JIRA_LIST_BOARDS | (none) |
| List sprints | JIRA_LIST_SPRINTS | boardId |
| Move to sprint | JIRA_MOVE_ISSUE_TO_SPRINT | sprintId, issues |
| Create sprint | JIRA_CREATE_SPRINT | name, boardId |
| Find users | JIRA_FIND_USERS | query |
| Get fields | JIRA_GET_FIELDS | (none) |
| List filters | JIRA_LIST_FILTERS | (none) |
| Project roles | JIRA_GET_PROJECT_ROLES | projectIdOrKey |
| Project versions | JIRA_GET_PROJECT_VERSIONS | projectIdOrKey |
