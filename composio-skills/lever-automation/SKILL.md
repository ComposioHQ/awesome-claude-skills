---
name: Lever Automation
description: "Automate recruiting workflows in Lever ATS -- manage opportunities, job postings, requisitions, pipeline stages, and candidate tags through the Composio Lever integration."
requires:
  mcp:
    - rube
---

# Lever Automation

Automate your recruiting operations in **Lever ATS** directly from Claude Code. Manage job postings, track candidate pipelines, update requisitions, and query opportunities without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/lever](https://composio.dev/toolkits/lever)

---

## Setup

1. Add the Composio MCP server to your configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Lever account when prompted by running any Lever command. The agent will provide an OAuth link to authenticate.
3. Ensure your Lever API key has sufficient scopes for the operations you need (read/write access to postings, opportunities, requisitions).

---

## Core Workflows

### 1. List and Filter Job Postings

Retrieve all job postings with optional filtering by state, team, department, location, or commitment type.

**Tool:** `LEVER_LIST_POSTINGS`

Key parameters:
- `state` -- filter by `published`, `internal`, `closed`, `draft`, `pending`, `rejected`
- `team`, `department`, `location`, `commitment` -- narrow results by organizational attributes
- `limit` (1-100) and `offset` -- paginate through large posting sets
- `tag` -- filter by posting tag

Example prompt: *"List all published engineering job postings in Lever"*

---

### 2. Browse Candidate Opportunities

List all opportunities in the hiring pipeline with rich filtering for pipeline analysis and candidate tracking.

**Tool:** `LEVER_LIST_OPPORTUNITIES`

Key parameters:
- `posting_id`, `stage_id`, `tag` -- filter by posting, pipeline stage, or tag
- `email`, `contact_id` -- find opportunities for a specific candidate
- `archived` -- filter by archived status (`true`/`false`)
- `created_at_start`, `created_at_end` -- date range filtering (ISO 8601)
- `expand` -- expand `applications`, `contact`, `owner`, `stage`, `stageChanges`, `sources`, `sourcedBy` into full objects

Example prompt: *"Show me all active opportunities for the Senior Engineer posting, expanded with contact details"*

---

### 3. Get Opportunity Details

Fetch comprehensive details about a single candidate opportunity including contact info, stage progression, sources, and applications.

**Tool:** `LEVER_GET_OPPORTUNITY`

Key parameters:
- `opportunity` (required) -- the unique opportunity UID
- `expand` -- comma-separated fields to expand: `contact`, `stage`, `owner`

Example prompt: *"Get full details for opportunity 31c9716c-d4e3-47e8-a6a1-54078a1151d6 with contact and stage expanded"*

---

### 4. Manage Requisitions

Create, list, update, and delete requisitions to track headcount and hiring needs.

**Tools:** `LEVER_LIST_REQUISITIONS`, `LEVER_GET_REQUISITION`, `LEVER_UPDATE_REQUISITION`, `LEVER_DELETE_REQUISITION`

Update requires these fields:
- `requisition` (required) -- UUID of the requisition
- `requisitionCode` (required) -- unique code like `REQ-001`
- `name` (required) -- requisition title
- `headcountTotal` (required) -- number of positions (minimum 1)
- `status` -- `open` or `closed`
- Optional: `hiringManager`, `owner`, `department`, `team`, `location`, `compensationBand`

Example prompt: *"Update requisition REQ-001 to increase headcount to 3 and change status to open"*

---

### 5. View Pipeline Stages

Retrieve all hiring pipeline stages configured in your Lever account.

**Tool:** `LEVER_LIST_STAGES`

Key parameters:
- `limit` (1-100) -- max items per page
- `offset` -- pagination token from previous response

Example prompt: *"List all pipeline stages in our Lever account"*

---

### 6. Manage Tags

List all tags used to categorize candidates, opportunities, and postings.

**Tool:** `LEVER_LIST_TAGS`

Key parameters:
- `limit` -- max items per page
- `offset` -- pagination token

Example prompt: *"Show all candidate tags in Lever"*

---

## Known Pitfalls

- **Pagination required for large datasets:** `LEVER_LIST_OPPORTUNITIES` and `LEVER_LIST_POSTINGS` default to 100 results max per page. Always check for an `offset` token in the response and iterate to get complete results.
- **Expand parameter format:** The `expand` field on `LEVER_LIST_OPPORTUNITIES` accepts an array of strings, while on `LEVER_GET_OPPORTUNITY` and `LEVER_GET_REQUISITION` it accepts a comma-separated string. Follow the exact schema for each tool.
- **Requisition updates are full replacements:** `LEVER_UPDATE_REQUISITION` requires all mandatory fields (`requisitionCode`, `name`, `headcountTotal`) even if you only want to change one field. Always fetch the current requisition first with `LEVER_GET_REQUISITION`.
- **Timestamps:** Opportunity date filters use ISO 8601 format, while `LEVER_LIST_POSTINGS` uses Unix timestamps in milliseconds for `updated_at_start`.
- **Connection scopes:** Write operations (update/delete requisitions) will fail if your API token lacks the necessary permissions, even if reads succeed.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `LEVER_LIST_POSTINGS` | List all job postings with filtering by state, team, department |
| `LEVER_LIST_OPPORTUNITIES` | List candidate opportunities with pipeline filtering |
| `LEVER_GET_OPPORTUNITY` | Get detailed info for a single opportunity |
| `LEVER_GET_REQUISITION` | Retrieve a single requisition by ID |
| `LEVER_LIST_REQUISITIONS` | List all requisitions with status/code filtering |
| `LEVER_UPDATE_REQUISITION` | Update an existing requisition (full replacement) |
| `LEVER_DELETE_REQUISITION` | Delete/archive a requisition |
| `LEVER_LIST_STAGES` | List all pipeline stages |
| `LEVER_LIST_TAGS` | List all tags for categorization |

---

*Powered by [Composio](https://composio.dev)*
