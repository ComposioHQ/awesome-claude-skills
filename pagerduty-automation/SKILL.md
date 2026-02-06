---
name: pagerduty-automation
description: "Automate PagerDuty tasks via Rube MCP (Composio): manage incidents, services, schedules, escalation policies, and on-call rotations. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# PagerDuty Automation via Rube MCP

Automate PagerDuty incident management and operations through Composio's PagerDuty toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active PagerDuty connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `pagerduty`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `pagerduty`
3. If connection is not ACTIVE, follow the returned auth link to complete PagerDuty authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Manage Incidents

**When to use**: User wants to create, update, acknowledge, or resolve incidents

**Tool sequence**:
1. `PAGERDUTY_FETCH_INCIDENT_LIST` - List incidents with filters [Required]
2. `PAGERDUTY_RETRIEVE_INCIDENT_BY_INCIDENT_ID` - Get specific incident details [Optional]
3. `PAGERDUTY_CREATE_INCIDENT_RECORD` - Create a new incident [Optional]
4. `PAGERDUTY_UPDATE_INCIDENT_BY_ID` - Update incident status or assignment [Optional]
5. `PAGERDUTY_POST_INCIDENT_NOTE_USING_ID` - Add a note to an incident [Optional]
6. `PAGERDUTY_SNOOZE_INCIDENT_BY_DURATION` - Snooze an incident for a period [Optional]

**Key parameters**:
- `statuses[]`: Filter by status ('triggered', 'acknowledged', 'resolved')
- `service_ids[]`: Filter by service IDs
- `urgencies[]`: Filter by urgency ('high', 'low')
- `title`: Incident title (for creation)
- `service`: Service object with `id` and `type` (for creation)
- `status`: New status for update operations

**Pitfalls**:
- Incident creation requires a `service` object with both `id` and `type: 'service_reference'`
- Status transitions follow: triggered -> acknowledged -> resolved
- Cannot transition from resolved back to triggered directly
- `PAGERDUTY_UPDATE_INCIDENT_BY_ID` requires the incident ID as a path parameter
- Snooze duration is in seconds; the incident re-triggers after the snooze period

### 2. Inspect Incident Alerts and Analytics

**When to use**: User wants to review alerts within an incident or analyze incident metrics

**Tool sequence**:
1. `PAGERDUTY_GET_ALERTS_BY_INCIDENT_ID` - List alerts for an incident [Required]
2. `PAGERDUTY_GET_INCIDENT_ALERT_DETAILS` - Get details of a specific alert [Optional]
3. `PAGERDUTY_FETCH_INCIDENT_ANALYTICS_BY_ID` - Get incident analytics/metrics [Optional]

**Key parameters**:
- `incident_id`: The incident ID
- `alert_id`: Specific alert ID within the incident
- `statuses[]`: Filter alerts by status

**Pitfalls**:
- An incident can have multiple alerts; each alert has its own status
- Alert IDs are scoped to the incident
- Analytics data includes response times, engagement metrics, and resolution times

### 3. Manage Services

**When to use**: User wants to create, update, or list services

**Tool sequence**:
1. `PAGERDUTY_RETRIEVE_LIST_OF_SERVICES` - List all services [Required]
2. `PAGERDUTY_RETRIEVE_SERVICE_BY_ID` - Get service details [Optional]
3. `PAGERDUTY_CREATE_NEW_SERVICE` - Create a new technical service [Optional]
4. `PAGERDUTY_UPDATE_SERVICE_BY_ID` - Update service configuration [Optional]
5. `PAGERDUTY_CREATE_INTEGRATION_FOR_SERVICE` - Add an integration to a service [Optional]
6. `PAGERDUTY_CREATE_BUSINESS_SERVICE` - Create a business service [Optional]
7. `PAGERDUTY_UPDATE_BUSINESS_SERVICE_BY_ID` - Update a business service [Optional]

**Key parameters**:
- `name`: Service name
- `escalation_policy`: Escalation policy object with `id` and `type`
- `alert_creation`: Alert creation mode ('create_alerts_and_incidents' or 'create_incidents')
- `status`: Service status ('active', 'warning', 'critical', 'maintenance', 'disabled')

**Pitfalls**:
- Creating a service requires an existing escalation policy
- Business services are different from technical services; they represent business-level groupings
- Service integrations define how alerts are created (email, API, events)
- Disabling a service stops all incident creation for that service

### 4. Manage Schedules and On-Call

**When to use**: User wants to view or manage on-call schedules and rotations

**Tool sequence**:
1. `PAGERDUTY_GET_SCHEDULES` - List all schedules [Required]
2. `PAGERDUTY_RETRIEVE_SCHEDULE_BY_ID` - Get specific schedule details [Optional]
3. `PAGERDUTY_CREATE_NEW_SCHEDULE_LAYER` - Create a new schedule [Optional]
4. `PAGERDUTY_UPDATE_SCHEDULE_BY_ID` - Update an existing schedule [Optional]
5. `PAGERDUTY_RETRIEVE_ONCALL_LIST` - View who is currently on-call [Optional]
6. `PAGERDUTY_CREATE_SCHEDULE_OVERRIDES_CONFIGURATION` - Create temporary overrides [Optional]
7. `PAGERDUTY_DELETE_SCHEDULE_OVERRIDE_BY_ID` - Remove an override [Optional]
8. `PAGERDUTY_RETRIEVE_USERS_BY_SCHEDULE_ID` - List users in a schedule [Optional]
9. `PAGERDUTY_PREVIEW_SCHEDULE_OBJECT` - Preview schedule changes before saving [Optional]

**Key parameters**:
- `schedule_id`: Schedule identifier
- `time_zone`: Schedule timezone (e.g., 'America/New_York')
- `schedule_layers`: Array of rotation layer configurations
- `since`/`until`: Date range for on-call queries (ISO 8601)
- `override`: Override object with user, start, and end times

**Pitfalls**:
- Schedule layers define rotation order; multiple layers can overlap
- Overrides are temporary and take precedence over the normal schedule
- `since` and `until` are required for on-call queries to scope the time range
- Time zones must be valid IANA timezone strings
- Preview before saving complex schedule changes to verify correctness

### 5. Manage Escalation Policies

**When to use**: User wants to create or modify escalation policies

**Tool sequence**:
1. `PAGERDUTY_FETCH_ESCALATION_POLICES_LIST` - List all escalation policies [Required]
2. `PAGERDUTY_GET_ESCALATION_POLICY_BY_ID` - Get policy details [Optional]
3. `PAGERDUTY_CREATE_ESCALATION_POLICY` - Create a new policy [Optional]
4. `PAGERDUTY_UPDATE_ESCALATION_POLICY_BY_ID` - Update an existing policy [Optional]
5. `PAGERDUTY_AUDIT_ESCALATION_POLICY_RECORDS` - View audit trail for a policy [Optional]

**Key parameters**:
- `name`: Policy name
- `escalation_rules`: Array of escalation rule objects
- `num_loops`: Number of times to loop through rules before stopping (0 = no loop)
- `escalation_delay_in_minutes`: Delay between escalation levels

**Pitfalls**:
- Each escalation rule requires at least one target (user, schedule, or team)
- `escalation_delay_in_minutes` defines how long before escalating to the next level
- Setting `num_loops` to 0 means the policy runs once and stops
- Deleting a policy fails if services still reference it

### 6. Manage Teams

**When to use**: User wants to create or manage PagerDuty teams

**Tool sequence**:
1. `PAGERDUTY_CREATE_NEW_TEAM_WITH_DETAILS` - Create a new team [Required]

**Key parameters**:
- `name`: Team name
- `description`: Team description

**Pitfalls**:
- Team names must be unique within the account
- Teams are used to scope services, escalation policies, and schedules

## Common Patterns

### ID Resolution

**Service name -> Service ID**:
```
1. Call PAGERDUTY_RETRIEVE_LIST_OF_SERVICES
2. Find service by name in response
3. Extract id field
```

**Schedule name -> Schedule ID**:
```
1. Call PAGERDUTY_GET_SCHEDULES
2. Find schedule by name in response
3. Extract id field
```

### Incident Lifecycle

```
1. Incident triggered (via API, integration, or manual creation)
2. On-call user notified per escalation policy
3. User acknowledges -> status: 'acknowledged'
4. User resolves -> status: 'resolved'
```

### Pagination

- PagerDuty uses offset-based pagination
- Check response for `more` boolean field
- Use `offset` and `limit` parameters
- Continue until `more` is false

## Known Pitfalls

**ID Formats**:
- All PagerDuty IDs are alphanumeric strings (e.g., 'P1234AB')
- Service references require `type: 'service_reference'`
- User references require `type: 'user_reference'`

**Status Transitions**:
- Incidents: triggered -> acknowledged -> resolved (forward only)
- Services: active, warning, critical, maintenance, disabled

**Rate Limits**:
- PagerDuty API enforces rate limits per account
- Implement exponential backoff on 429 responses
- Bulk operations should be spaced out

**Response Parsing**:
- Response data may be nested under `data` or `data.data`
- Parse defensively with fallback patterns
- Pagination uses `offset`/`limit`/`more` pattern

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List incidents | PAGERDUTY_FETCH_INCIDENT_LIST | statuses[], service_ids[] |
| Get incident | PAGERDUTY_RETRIEVE_INCIDENT_BY_INCIDENT_ID | incident_id |
| Create incident | PAGERDUTY_CREATE_INCIDENT_RECORD | title, service |
| Update incident | PAGERDUTY_UPDATE_INCIDENT_BY_ID | incident_id, status |
| Add incident note | PAGERDUTY_POST_INCIDENT_NOTE_USING_ID | incident_id, content |
| Snooze incident | PAGERDUTY_SNOOZE_INCIDENT_BY_DURATION | incident_id, duration |
| Get incident alerts | PAGERDUTY_GET_ALERTS_BY_INCIDENT_ID | incident_id |
| Incident analytics | PAGERDUTY_FETCH_INCIDENT_ANALYTICS_BY_ID | incident_id |
| List services | PAGERDUTY_RETRIEVE_LIST_OF_SERVICES | (none) |
| Get service | PAGERDUTY_RETRIEVE_SERVICE_BY_ID | service_id |
| Create service | PAGERDUTY_CREATE_NEW_SERVICE | name, escalation_policy |
| Update service | PAGERDUTY_UPDATE_SERVICE_BY_ID | service_id |
| List schedules | PAGERDUTY_GET_SCHEDULES | (none) |
| Get schedule | PAGERDUTY_RETRIEVE_SCHEDULE_BY_ID | schedule_id |
| Get on-call | PAGERDUTY_RETRIEVE_ONCALL_LIST | since, until |
| Create schedule override | PAGERDUTY_CREATE_SCHEDULE_OVERRIDES_CONFIGURATION | schedule_id |
| List escalation policies | PAGERDUTY_FETCH_ESCALATION_POLICES_LIST | (none) |
| Create escalation policy | PAGERDUTY_CREATE_ESCALATION_POLICY | name, escalation_rules |
| Create team | PAGERDUTY_CREATE_NEW_TEAM_WITH_DETAILS | name, description |
