---
name: Jotform Automation
description: "Automate Jotform form listing, user management, activity history, folder organization, and plan inspection through natural language commands"
requires:
  mcp:
    - rube
---

# Jotform Automation

Automate Jotform workflows -- list and search forms, inspect user details, browse activity history, manage folders and labels, and check plan limits -- all through natural language.

**Toolkit docs:** [composio.dev/toolkits/jotform](https://composio.dev/toolkits/jotform)

---

## Setup

1. Add the Rube MCP server to your environment: `https://rube.app/mcp`
2. Connect your Jotform account when prompted (API key auth via Composio)
3. Start issuing natural language commands for Jotform automation

---

## Core Workflows

### 1. List and Search Forms

Retrieve all forms created by the authenticated user with search, filtering, sorting, and pagination.

**Tool:** `JOTFORM_GET_USER_FORMS`

Key parameters:
- `search` -- search query to filter forms by name or content
- `limit` -- number of forms to return
- `offset` -- offset for pagination
- `orderby` -- field to order by
- `sorting` -- sorting direction: `ASC` or `DESC`
- `folder` -- filter by folder ID

Example prompt:
> "List all my Jotform forms that contain 'feedback' in the name, sorted by most recent"

---

### 2. Get User Account Details

Retrieve details about the authenticated user including account type, usage statistics, and limits.

**Tool:** `JOTFORM_GET_USER_DETAILS`

No parameters required. Returns account info such as username, email, account type, form count, submission count, and usage limits.

Example prompt:
> "Show me my Jotform account details and current usage"

---

### 3. Browse Activity History

Fetch user activity records for auditing, filtered by action type and date range.

**Tool:** `JOTFORM_GET_USER_HISTORY`

Key parameters:
- `action` -- filter by action type (e.g., `formCreation`, `userLogin`, `formUpdate`, `apiKeyCreated`, `userLogout`)
- `date` -- predefined date range: `lastWeek`, `lastMonth`, `last3Months`, `last6Months`, `lastYear`, `all`
- `startDate` -- custom start date in `MM/DD/YYYY` format
- `endDate` -- custom end date in `MM/DD/YYYY` format
- `sortBy` -- sort order: `ASC` or `DESC`

Example prompt:
> "Show me all form creation activity from the last month, sorted newest first"

---

### 4. Manage Folders and Labels

Browse the folder/label structure for organizing forms.

**Tool:** `JOTFORM_GET_USER_FOLDERS`

Key parameters:
- `add_resources` -- set to `true` to include label resources (forms) in the response
- `owner` -- owner username or workspace/team ID (conditionally required for some accounts)

> Jotform has migrated from folders to labels. This tool uses the `GET /user/labels` endpoint.

Example prompt:
> "List all my Jotform folders with their forms included"

---

### 5. Check Plan Limits and Pricing

Retrieve details about a specific Jotform system plan to understand limits and capabilities.

**Tool:** `JOTFORM_GET_SYSTEM_PLAN`

Key parameters:
- `planName` -- the plan to inspect (required): `FREE`, `BRONZE`, `SILVER`, `GOLD`, or `PLATINUM`

Example prompt:
> "What are the limits on the Jotform GOLD plan?"

---

### 6. Full Form Management Workflow

Combine tools for comprehensive form management:

1. **Discover**: `JOTFORM_GET_USER_DETAILS` -- check account type and usage limits
2. **Browse**: `JOTFORM_GET_USER_FORMS` -- list and search forms with filters
3. **Organize**: `JOTFORM_GET_USER_FOLDERS` -- view folder structure with `add_resources=true`
4. **Audit**: `JOTFORM_GET_USER_HISTORY` -- track form creation and modification activity
5. **Plan**: `JOTFORM_GET_SYSTEM_PLAN` -- compare plan features before upgrading

Example prompt:
> "Show me my account usage, list my recent forms, and tell me if I'm close to my plan limits"

---

## Known Pitfalls

| Pitfall | Details |
|---------|---------|
| API key authentication | Jotform uses API key auth, not OAuth -- ensure valid API key is configured in the connection |
| Folders migrated to labels | The folders endpoint now maps to Jotform's labels system; the API behavior may differ from legacy folder documentation |
| Date format for history | Custom date filters use `MM/DD/YYYY` format (e.g., `01/15/2026`), not ISO 8601 |
| Plan name must be exact | `planName` values are case-sensitive enum: `FREE`, `BRONZE`, `SILVER`, `GOLD`, `PLATINUM` |
| Pagination is offset-based | Forms use `limit`/`offset` pagination, not cursor or page-based |
| Owner field conditionally required | `JOTFORM_GET_USER_FOLDERS` may require the `owner` parameter for workspace/team accounts |

---

## Quick Reference

| Action | Tool Slug | Key Params |
|--------|-----------|------------|
| List forms | `JOTFORM_GET_USER_FORMS` | `search`, `limit`, `offset`, `orderby` |
| Get user details | `JOTFORM_GET_USER_DETAILS` | (none) |
| Activity history | `JOTFORM_GET_USER_HISTORY` | `action`, `date`, `startDate`, `endDate` |
| List folders/labels | `JOTFORM_GET_USER_FOLDERS` | `add_resources`, `owner` |
| Check plan | `JOTFORM_GET_SYSTEM_PLAN` | `planName` |

---

*Powered by [Composio](https://composio.dev)*
