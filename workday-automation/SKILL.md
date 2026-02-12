---
name: Workday Automation
description: "Automate HR operations in Workday -- manage workers, time off requests, absence balances, and employee data through natural language commands."
requires:
  mcp:
    - rube
---

# Workday Automation

Automate your Workday HR operations directly from Claude Code. Look up workers, create time off requests, check absence balances, and validate time off eligibility -- all without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/workday](https://composio.dev/toolkits/workday)

---

## Setup

1. Add the Rube MCP server to your Claude Code config with URL: `https://rube.app/mcp`
2. When prompted, authenticate your Workday account through the connection link provided
3. Start automating your HR workflows with natural language

---

## Core Workflows

### 1. Search and List Workers

Retrieve worker information with search and pagination.

**Tool:** `WORKDAY_LIST_WORKERS`

```
Search for workers named "Sarah" and include terminated employees
```

Key parameters:
- `search` -- search by name or worker ID (case-insensitive, space-delimited for OR search)
- `includeTerminatedWorkers` -- include terminated workers in results
- `limit` (default 20, max 100) / `offset` -- pagination controls

### 2. Create Time Off Requests

Submit time off requests for workers with full business process support.

**Tool:** `WORKDAY_CREATE_TIME_OFF_REQUEST`

```
Create a vacation request for worker abc123 for March 15-17, 2026 (8 hours each day)
```

Key parameters:
- `ID` (required) -- Workday worker ID
- `businessProcessParameters` (required) -- must include `action` with `id` field (use `"d9e4223e446c11de98360015c5e6daf6"` for submit action)
- `days` (required) -- array of time off entries, each with:
  - `date` (required) -- date in `yyyy-mm-dd` format
  - `timeOffType` (required) -- object with `id` of the eligible absence type
  - `dailyQuantity` -- hours or days quantity
  - `comment`, `start`, `end`, `position`, `reason` -- optional fields
- `businessProcessParameters.comment` -- optional business process comment

### 3. Check Time Off Eligibility

Validate which dates a worker can take off before submitting a request.

**Tool:** `WORKDAY_GET_WORKER_VALID_TIME_OFF_DATES`

```
Check if worker abc123 is eligible to take time off on March 15, 2026
```

Key parameters:
- `ID` (required) -- Workday worker ID
- `date` -- specific date to validate (`yyyy-mm-dd`)
- `position` -- filter by specific position ID
- `timeOff` -- filter by specific time off plan/type ID
- `limit` (max 100) / `offset` -- pagination

### 4. View Absence Balances

Check remaining time off balances for workers across all plans.

**Tool:** `WORKDAY_LIST_ABSENCE_BALANCES`

```
Show me absence balances for all workers in the organization
```

- Retrieves balances for time off plans and leave of absence types
- Can be filtered by worker ID, category, and effective date

### 5. Get Current User Profile

Retrieve the authenticated worker's profile information.

**Tool:** `WORKDAY_GET_CURRENT_USER`

```
Show me my Workday profile information
```

- No parameters required
- Returns the authenticated worker's profile
- Use this first to get the worker ID for subsequent operations

### 6. View Time Off History

Retrieve time off details and history for a specific worker.

**Tool:** `WORKDAY_GET_WORKER_TIME_OFF_DETAILS`

```
Show me the time off history for worker abc123
```

- Retrieves a collection of time off details for the specified worker
- Useful for auditing time off usage and remaining balances

---

## Known Pitfalls

- **Worker ID resolution:** Always call `WORKDAY_GET_CURRENT_USER` or `WORKDAY_LIST_WORKERS` first to resolve Workday worker IDs. Worker IDs are Workday-specific UUIDs, not employee numbers.
- **Time off type IDs must be valid:** The `timeOffType.id` in `WORKDAY_CREATE_TIME_OFF_REQUEST` must reference a valid eligible absence type for that worker. Use the "Get Worker Eligible Absence Types" flow to discover valid type IDs.
- **Submit action ID:** The `businessProcessParameters.action.id` should be `"d9e4223e446c11de98360015c5e6daf6"` for the submit action. Using an incorrect ID will cause the business process to fail.
- **Date format:** All date fields use `yyyy-mm-dd` format. ISO 8601 with timestamps is not accepted for date-only fields.
- **Pagination limits:** The maximum `limit` is 100 across all Workday endpoints. Default is 20. Always paginate for complete datasets.
- **Business process approval:** Creating a time off request initiates the business process but does not guarantee approval. The request enters the normal approval workflow.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `WORKDAY_LIST_WORKERS` | Search and list workers with staffing info |
| `WORKDAY_GET_CURRENT_USER` | Get the authenticated worker's profile |
| `WORKDAY_CREATE_TIME_OFF_REQUEST` | Submit a time off request (requires `ID`, `businessProcessParameters`, `days`) |
| `WORKDAY_GET_WORKER_VALID_TIME_OFF_DATES` | Check time off date eligibility (requires `ID`) |
| `WORKDAY_LIST_ABSENCE_BALANCES` | Retrieve absence balances across time off plans |
| `WORKDAY_GET_WORKER_TIME_OFF_DETAILS` | Get time off history for a worker |

---

*Powered by [Composio](https://composio.dev)*
