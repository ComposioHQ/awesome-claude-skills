---
name: bitbucket-automation
description: Automate Bitbucket repositories, pull requests, branches, issues, and workspace management via Rube MCP (Composio). Always search tools first for current schemas.
requires:
  mcp: [rube]
---

# Bitbucket Automation via Rube MCP

Automate Bitbucket operations including repository management, pull request workflows, branch operations, issue tracking, and workspace administration through Composio's Bitbucket toolkit.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Bitbucket connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `bitbucket`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `bitbucket`
3. If connection is not ACTIVE, follow the returned auth link to complete Bitbucket OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Manage Pull Requests

**When to use**: User wants to create, review, or inspect pull requests

**Tool sequence**:
1. `BITBUCKET_LIST_WORKSPACES` - Discover accessible workspaces [Prerequisite]
2. `BITBUCKET_LIST_REPOSITORIES_IN_WORKSPACE` - Find the target repository [Prerequisite]
3. `BITBUCKET_LIST_BRANCHES` - Verify source and destination branches exist [Prerequisite]
4. `BITBUCKET_CREATE_PULL_REQUEST` - Create a new PR with title, source branch, and optional reviewers [Required]
5. `BITBUCKET_LIST_PULL_REQUESTS` - List PRs filtered by state (OPEN, MERGED, DECLINED) [Optional]
6. `BITBUCKET_GET_PULL_REQUEST` - Get full details of a specific PR by ID [Optional]
7. `BITBUCKET_GET_PULL_REQUEST_DIFF` - Fetch unified diff for code review [Optional]
8. `BITBUCKET_GET_PULL_REQUEST_DIFFSTAT` - Get changed files with lines added/removed [Optional]

**Key parameters**:
- `workspace`: Workspace slug or UUID (required for all operations)
- `repo_slug`: URL-friendly repository name
- `source_branch`: Branch with changes to merge
- `destination_branch`: Target branch (defaults to repo main branch if omitted)
- `reviewers`: List of objects with `uuid` field for reviewer assignment
- `state`: Filter for LIST_PULL_REQUESTS - `OPEN`, `MERGED`, or `DECLINED`
- `max_chars`: Truncation limit for GET_PULL_REQUEST_DIFF to handle large diffs

**Pitfalls**:
- `reviewers` expects an array of objects with `uuid` key, NOT usernames: `[{"uuid": "{...}"}]`
- UUID format must include curly braces: `{123e4567-e89b-12d3-a456-426614174000}`
- `destination_branch` defaults to the repo's main branch if omitted, which may not be `main`
- `pull_request_id` is an integer for GET/DIFF operations but comes back as part of PR listing
- Large diffs can overwhelm context; always set `max_chars` (e.g., 50000) on GET_PULL_REQUEST_DIFF

### 2. Manage Repositories and Workspaces

**When to use**: User wants to list, create, or delete repositories or explore workspaces

**Tool sequence**:
1. `BITBUCKET_LIST_WORKSPACES` - List all accessible workspaces [Required]
2. `BITBUCKET_LIST_REPOSITORIES_IN_WORKSPACE` - List repos with optional BBQL filtering [Required]
3. `BITBUCKET_CREATE_REPOSITORY` - Create a new repo with language, privacy, and project settings [Optional]
4. `BITBUCKET_DELETE_REPOSITORY` - Permanently delete a repository (irreversible) [Optional]
5. `BITBUCKET_LIST_WORKSPACE_MEMBERS` - List members for reviewer assignment or access checks [Optional]

**Key parameters**:
- `workspace`: Workspace slug (find via LIST_WORKSPACES)
- `repo_slug`: URL-friendly name for create/delete
- `q`: BBQL query filter (e.g., `name~"api"`, `project.key="PROJ"`, `is_private=true`)
- `role`: Filter repos by user role: `member`, `contributor`, `admin`, `owner`
- `sort`: Sort field with optional `-` prefix for descending (e.g., `-updated_on`)
- `is_private`: Boolean for repository visibility (defaults to `true`)
- `project_key`: Bitbucket project key; omit to use workspace's oldest project

**Pitfalls**:
- `BITBUCKET_DELETE_REPOSITORY` is **irreversible** and does not affect forks
- BBQL string values MUST be enclosed in double quotes: `name~"my-repo"` not `name~my-repo`
- `repository` is NOT a valid BBQL field; use `name` instead
- Default pagination is 10 results; set `pagelen` explicitly for complete listings
- `CREATE_REPOSITORY` defaults to private; set `is_private: false` for public repos

### 3. Manage Issues

**When to use**: User wants to create, update, list, or comment on repository issues

**Tool sequence**:
1. `BITBUCKET_LIST_ISSUES` - List issues with optional filters for state, priority, kind, assignee [Required]
2. `BITBUCKET_CREATE_ISSUE` - Create a new issue with title, content, priority, and kind [Required]
3. `BITBUCKET_UPDATE_ISSUE` - Modify issue attributes (state, priority, assignee, etc.) [Optional]
4. `BITBUCKET_CREATE_ISSUE_COMMENT` - Add a markdown comment to an existing issue [Optional]
5. `BITBUCKET_DELETE_ISSUE` - Permanently delete an issue [Optional]

**Key parameters**:
- `issue_id`: String identifier for the issue
- `title`, `content`: Required for creation
- `kind`: `bug`, `enhancement`, `proposal`, or `task`
- `priority`: `trivial`, `minor`, `major`, `critical`, or `blocker`
- `state`: `new`, `open`, `resolved`, `on hold`, `invalid`, `duplicate`, `wontfix`, `closed`
- `assignee`: Bitbucket username for CREATE; `assignee_account_id` (UUID) for UPDATE
- `due_on`: ISO 8601 format date string

**Pitfalls**:
- Issue tracker must be enabled on the repository (`has_issues: true`) or API calls will fail
- `CREATE_ISSUE` uses `assignee` (username string), but `UPDATE_ISSUE` uses `assignee_account_id` (UUID) -- they are different fields
- `DELETE_ISSUE` is permanent with no undo
- `state` values include spaces: `"on hold"` not `"on_hold"`
- Filtering by `assignee` in LIST_ISSUES uses account ID, not username; use `"null"` string for unassigned

### 4. Manage Branches

**When to use**: User wants to create branches or explore branch structure

**Tool sequence**:
1. `BITBUCKET_LIST_BRANCHES` - List branches with optional BBQL filter and sorting [Required]
2. `BITBUCKET_CREATE_BRANCH` - Create a new branch from a specific commit hash [Required]

**Key parameters**:
- `name`: Branch name without `refs/heads/` prefix (e.g., `feature/new-login`)
- `target_hash`: Full SHA1 commit hash to branch from (must exist in repo)
- `q`: BBQL filter (e.g., `name~"feature/"`, `name="main"`)
- `sort`: Sort by `name` or `-target.date` (descending commit date)
- `pagelen`: 1-100 results per page (default is 10)

**Pitfalls**:
- `CREATE_BRANCH` requires a full commit hash, NOT a branch name as `target_hash`
- Do NOT include `refs/heads/` prefix in branch names
- Branch names must follow Bitbucket naming conventions (alphanumeric, `/`, `.`, `_`, `-`)
- BBQL string values need double quotes: `name~"feature/"` not `name~feature/`

### 5. Review Pull Requests with Comments

**When to use**: User wants to add review comments to pull requests, including inline code comments

**Tool sequence**:
1. `BITBUCKET_GET_PULL_REQUEST` - Get PR details and verify it exists [Prerequisite]
2. `BITBUCKET_GET_PULL_REQUEST_DIFF` - Review the actual code changes [Prerequisite]
3. `BITBUCKET_GET_PULL_REQUEST_DIFFSTAT` - Get list of changed files [Optional]
4. `BITBUCKET_CREATE_PULL_REQUEST_COMMENT` - Post review comments [Required]

**Key parameters**:
- `pull_request_id`: String ID of the PR
- `content_raw`: Markdown-formatted comment text
- `content_markup`: Defaults to `markdown`; also supports `plaintext`
- `inline`: Object with `path`, `from`, `to` for inline code comments
- `parent_comment_id`: Integer ID for threaded replies to existing comments

**Pitfalls**:
- `pull_request_id` is a string in CREATE_PULL_REQUEST_COMMENT but an integer in GET_PULL_REQUEST
- Inline comments require `inline.path` at minimum; `from`/`to` are optional line numbers
- `parent_comment_id` creates a threaded reply; omit for top-level comments
- Line numbers in inline comments reference the diff, not the source file

## Common Patterns

### ID Resolution
Always resolve human-readable names to IDs before operations:
- **Workspace**: `BITBUCKET_LIST_WORKSPACES` to get workspace slugs
- **Repository**: `BITBUCKET_LIST_REPOSITORIES_IN_WORKSPACE` with `q` filter to find repo slugs
- **Branch**: `BITBUCKET_LIST_BRANCHES` to verify branch existence before PR creation
- **Members**: `BITBUCKET_LIST_WORKSPACE_MEMBERS` to get UUIDs for reviewer assignment

### Pagination
Bitbucket uses page-based pagination (not cursor-based):
- Use `page` (starts at 1) and `pagelen` (items per page) parameters
- Default page size is typically 10; set `pagelen` explicitly (max 50 for PRs, 100 for others)
- Check response for `next` URL or total count to determine if more pages exist
- Always iterate through all pages for complete results

### BBQL Filtering
Bitbucket Query Language is available on list endpoints:
- String values MUST use double quotes: `name~"pattern"`
- Operators: `=` (exact), `~` (contains), `!=` (not equal), `>`, `>=`, `<`, `<=`
- Combine with `AND` / `OR`: `name~"api" AND is_private=true`

## Known Pitfalls

### ID Formats
- Workspace: slug string (e.g., `my-workspace`) or UUID in braces (`{uuid}`)
- Reviewer UUIDs must include curly braces: `{123e4567-e89b-12d3-a456-426614174000}`
- Issue IDs are strings; PR IDs are integers in some tools, strings in others
- Commit hashes must be full SHA1 (40 characters)

### Parameter Quirks
- `assignee` vs `assignee_account_id`: CREATE_ISSUE uses username, UPDATE_ISSUE uses UUID
- `state` values for issues include spaces: `"on hold"`, not `"on_hold"`
- `destination_branch` omission defaults to repo main branch, not `main` literally
- BBQL `repository` is not a valid field -- use `name`

### Rate Limits
- Bitbucket Cloud API has rate limits; large batch operations should include delays
- Paginated requests count against rate limits; minimize unnecessary page fetches

### Destructive Operations
- `BITBUCKET_DELETE_REPOSITORY` is irreversible and does not remove forks
- `BITBUCKET_DELETE_ISSUE` is permanent with no recovery option
- Always confirm with the user before executing delete operations

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List workspaces | `BITBUCKET_LIST_WORKSPACES` | `q`, `sort` |
| List repos | `BITBUCKET_LIST_REPOSITORIES_IN_WORKSPACE` | `workspace`, `q`, `role` |
| Create repo | `BITBUCKET_CREATE_REPOSITORY` | `workspace`, `repo_slug`, `is_private` |
| Delete repo | `BITBUCKET_DELETE_REPOSITORY` | `workspace`, `repo_slug` |
| List branches | `BITBUCKET_LIST_BRANCHES` | `workspace`, `repo_slug`, `q` |
| Create branch | `BITBUCKET_CREATE_BRANCH` | `workspace`, `repo_slug`, `name`, `target_hash` |
| List PRs | `BITBUCKET_LIST_PULL_REQUESTS` | `workspace`, `repo_slug`, `state` |
| Create PR | `BITBUCKET_CREATE_PULL_REQUEST` | `workspace`, `repo_slug`, `title`, `source_branch` |
| Get PR details | `BITBUCKET_GET_PULL_REQUEST` | `workspace`, `repo_slug`, `pull_request_id` |
| Get PR diff | `BITBUCKET_GET_PULL_REQUEST_DIFF` | `workspace`, `repo_slug`, `pull_request_id`, `max_chars` |
| Get PR diffstat | `BITBUCKET_GET_PULL_REQUEST_DIFFSTAT` | `workspace`, `repo_slug`, `pull_request_id` |
| Comment on PR | `BITBUCKET_CREATE_PULL_REQUEST_COMMENT` | `workspace`, `repo_slug`, `pull_request_id`, `content_raw` |
| List issues | `BITBUCKET_LIST_ISSUES` | `workspace`, `repo_slug`, `state`, `priority` |
| Create issue | `BITBUCKET_CREATE_ISSUE` | `workspace`, `repo_slug`, `title`, `content` |
| Update issue | `BITBUCKET_UPDATE_ISSUE` | `workspace`, `repo_slug`, `issue_id` |
| Comment on issue | `BITBUCKET_CREATE_ISSUE_COMMENT` | `workspace`, `repo_slug`, `issue_id`, `content` |
| Delete issue | `BITBUCKET_DELETE_ISSUE` | `workspace`, `repo_slug`, `issue_id` |
| List members | `BITBUCKET_LIST_WORKSPACE_MEMBERS` | `workspace` |
