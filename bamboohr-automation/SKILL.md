---
name: bamboohr-automation
description: "Automate BambooHR tasks via Rube MCP (Composio): employees, time-off, benefits, dependents, employee updates. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# BambooHR Automation via Rube MCP

Automate BambooHR human resources operations through Composio's BambooHR toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active BambooHR connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `bamboohr`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `bamboohr`
3. If connection is not ACTIVE, follow the returned auth link to complete BambooHR authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List and Search Employees

**When to use**: User wants to find employees or get the full employee directory

**Tool sequence**:
1. `BAMBOOHR_GET_ALL_EMPLOYEES` - Get the employee directory [Required]
2. `BAMBOOHR_GET_EMPLOYEE` - Get detailed info for a specific employee [Optional]

**Key parameters**:
- For GET_ALL_EMPLOYEES: No required parameters; returns directory
- For GET_EMPLOYEE:
  - `id`: Employee ID (numeric)
  - `fields`: Comma-separated list of fields to return (e.g., 'firstName,lastName,department,jobTitle')

**Pitfalls**:
- Employee IDs are numeric integers
- GET_ALL_EMPLOYEES returns basic directory info; use GET_EMPLOYEE for full details
- The `fields` parameter controls which fields are returned; omitting it may return minimal data
- Common fields: firstName, lastName, department, division, jobTitle, workEmail, status
- Inactive/terminated employees may be included; check `status` field

### 2. Track Employee Changes

**When to use**: User wants to detect recent employee data changes for sync or auditing

**Tool sequence**:
1. `BAMBOOHR_EMPLOYEE_GET_CHANGED` - Get employees with recent changes [Required]

**Key parameters**:
- `since`: ISO 8601 datetime string for change detection threshold
- `type`: Type of changes to check (e.g., 'inserted', 'updated', 'deleted')

**Pitfalls**:
- `since` parameter is required; use ISO 8601 format (e.g., '2024-01-15T00:00:00Z')
- Returns IDs of changed employees, not full employee data
- Must call GET_EMPLOYEE separately for each changed employee's details
- Useful for incremental sync workflows; cache the last sync timestamp

### 3. Manage Time-Off

**When to use**: User wants to view time-off balances, request time off, or manage requests

**Tool sequence**:
1. `BAMBOOHR_GET_META_TIME_OFF_TYPES` - List available time-off types [Prerequisite]
2. `BAMBOOHR_GET_TIME_OFF_BALANCES` - Check current balances [Optional]
3. `BAMBOOHR_GET_TIME_OFF_REQUESTS` - List existing requests [Optional]
4. `BAMBOOHR_CREATE_TIME_OFF_REQUEST` - Submit a new request [Optional]
5. `BAMBOOHR_UPDATE_TIME_OFF_REQUEST` - Modify or approve/deny a request [Optional]

**Key parameters**:
- For balances: `employeeId`, time-off type ID
- For requests: `start`, `end` (date range), `employeeId`
- For creation:
  - `employeeId`: Employee to request for
  - `timeOffTypeId`: Type ID from GET_META_TIME_OFF_TYPES
  - `start`: Start date (YYYY-MM-DD)
  - `end`: End date (YYYY-MM-DD)
  - `amount`: Number of days/hours
  - `notes`: Optional notes for the request
- For update: `requestId`, `status` ('approved', 'denied', 'cancelled')

**Pitfalls**:
- Time-off type IDs are numeric; resolve via GET_META_TIME_OFF_TYPES first
- Date format is 'YYYY-MM-DD' for start and end dates
- Balances may be in hours or days depending on company configuration
- Request status updates require appropriate permissions (manager/admin)
- Creating a request does NOT auto-approve it; separate approval step needed

### 4. Update Employee Information

**When to use**: User wants to modify employee profile data

**Tool sequence**:
1. `BAMBOOHR_GET_EMPLOYEE` - Get current employee data [Prerequisite]
2. `BAMBOOHR_UPDATE_EMPLOYEE` - Update employee fields [Required]

**Key parameters**:
- `id`: Employee ID (numeric, required)
- Field-value pairs for the fields to update (e.g., `department`, `jobTitle`, `workPhone`)

**Pitfalls**:
- Only fields included in the request are updated; others remain unchanged
- Some fields are read-only and cannot be updated via API
- Field names must match BambooHR's expected field names exactly
- Updates are audited; changes appear in the employee's change history
- Verify current values with GET_EMPLOYEE before updating to avoid overwriting

### 5. Manage Dependents and Benefits

**When to use**: User wants to view employee dependents or benefit coverage

**Tool sequence**:
1. `BAMBOOHR_DEPENDENTS_GET_ALL` - List all dependents [Required]
2. `BAMBOOHR_BENEFIT_GET_COVERAGES` - Get benefit coverage details [Optional]

**Key parameters**:
- For dependents: Optional `employeeId` filter
- For benefits: Depends on schema; check RUBE_SEARCH_TOOLS for current parameters

**Pitfalls**:
- Dependent data includes sensitive PII; handle with appropriate care
- Benefit coverages may include multiple plan types per employee
- Not all BambooHR plans include benefits administration; check account features
- Data access depends on API key permissions

## Common Patterns

### ID Resolution

**Employee name -> Employee ID**:
```
1. Call BAMBOOHR_GET_ALL_EMPLOYEES
2. Find employee by name in directory results
3. Extract id (numeric) for detailed operations
```

**Time-off type name -> Type ID**:
```
1. Call BAMBOOHR_GET_META_TIME_OFF_TYPES
2. Find type by name (e.g., 'Vacation', 'Sick Leave')
3. Extract id for time-off requests
```

### Incremental Sync Pattern

For keeping external systems in sync with BambooHR:
```
1. Store last_sync_timestamp
2. Call BAMBOOHR_EMPLOYEE_GET_CHANGED with since=last_sync_timestamp
3. For each changed employee ID, call BAMBOOHR_GET_EMPLOYEE
4. Process updates in external system
5. Update last_sync_timestamp
```

### Time-Off Workflow

```
1. GET_META_TIME_OFF_TYPES -> find type ID
2. GET_TIME_OFF_BALANCES -> verify available balance
3. CREATE_TIME_OFF_REQUEST -> submit request
4. UPDATE_TIME_OFF_REQUEST -> approve/deny (manager action)
```

## Known Pitfalls

**Employee IDs**:
- Always numeric integers
- Resolve names to IDs via GET_ALL_EMPLOYEES
- Terminated employees retain their IDs

**Date Formats**:
- Time-off dates: 'YYYY-MM-DD'
- Change detection: ISO 8601 with timezone
- Inconsistent formats between endpoints; check each endpoint's schema

**Permissions**:
- API key permissions determine accessible fields and operations
- Some operations require admin or manager-level access
- Time-off approvals require appropriate role permissions

**Sensitive Data**:
- Employee data includes PII (names, addresses, SSN, etc.)
- Handle all responses with appropriate security measures
- Dependent data is especially sensitive

**Rate Limits**:
- BambooHR API has rate limits per API key
- Bulk operations should be throttled
- GET_ALL_EMPLOYEES is more efficient than individual GET_EMPLOYEE calls

**Response Parsing**:
- Response data may be nested under `data` key
- Employee fields vary based on `fields` parameter
- Empty fields may be omitted or returned as null
- Parse defensively with fallbacks

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List all employees | BAMBOOHR_GET_ALL_EMPLOYEES | (none) |
| Get employee details | BAMBOOHR_GET_EMPLOYEE | id, fields |
| Track changes | BAMBOOHR_EMPLOYEE_GET_CHANGED | since, type |
| Time-off types | BAMBOOHR_GET_META_TIME_OFF_TYPES | (none) |
| Time-off balances | BAMBOOHR_GET_TIME_OFF_BALANCES | employeeId |
| List time-off requests | BAMBOOHR_GET_TIME_OFF_REQUESTS | start, end, employeeId |
| Create time-off request | BAMBOOHR_CREATE_TIME_OFF_REQUEST | employeeId, timeOffTypeId, start, end |
| Update time-off request | BAMBOOHR_UPDATE_TIME_OFF_REQUEST | requestId, status |
| Update employee | BAMBOOHR_UPDATE_EMPLOYEE | id, (field updates) |
| List dependents | BAMBOOHR_DEPENDENTS_GET_ALL | employeeId |
| Benefit coverages | BAMBOOHR_BENEFIT_GET_COVERAGES | (check schema) |
