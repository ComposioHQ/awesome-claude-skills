---
name: datadog-automation
description: "Automate Datadog tasks via Rube MCP (Composio): query metrics, search logs, manage monitors/dashboards, create events and downtimes. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Datadog Automation via Rube MCP

Automate Datadog monitoring and observability operations through Composio's Datadog toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Datadog connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `datadog`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `datadog`
3. If connection is not ACTIVE, follow the returned auth link to complete Datadog authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Query and Explore Metrics

**When to use**: User wants to query metric data or list available metrics

**Tool sequence**:
1. `DATADOG_LIST_METRICS` - List available metric names [Optional]
2. `DATADOG_QUERY_METRICS` - Query metric time series data [Required]

**Key parameters**:
- `query`: Datadog metric query string (e.g., `avg:system.cpu.user{host:web01}`)
- `from`: Start timestamp (Unix epoch seconds)
- `to`: End timestamp (Unix epoch seconds)
- `q`: Search string for listing metrics

**Pitfalls**:
- Query syntax follows Datadog's metric query format: `aggregation:metric_name{tag_filters}`
- `from` and `to` are Unix epoch timestamps in seconds, not milliseconds
- Valid aggregations: `avg`, `sum`, `min`, `max`, `count`
- Tag filters use curly braces: `{host:web01,env:prod}`
- Time range should not exceed Datadog's retention limits for the metric type

### 2. Search and Analyze Logs

**When to use**: User wants to search log entries or list log indexes

**Tool sequence**:
1. `DATADOG_LIST_LOG_INDEXES` - List available log indexes [Optional]
2. `DATADOG_SEARCH_LOGS` - Search logs with query and filters [Required]

**Key parameters**:
- `query`: Log search query using Datadog log query syntax
- `from`: Start time (ISO 8601 or Unix timestamp)
- `to`: End time (ISO 8601 or Unix timestamp)
- `sort`: Sort order ('asc' or 'desc')
- `limit`: Number of log entries to return

**Pitfalls**:
- Log queries use Datadog's log search syntax: `service:web status:error`
- Search is limited to retained logs within the configured retention period
- Large result sets require pagination; check for cursor/page tokens
- Log indexes control routing and retention; filter by index if known

### 3. Manage Monitors

**When to use**: User wants to create, update, mute, or inspect monitors

**Tool sequence**:
1. `DATADOG_LIST_MONITORS` - List all monitors with filters [Required]
2. `DATADOG_GET_MONITOR` - Get specific monitor details [Optional]
3. `DATADOG_CREATE_MONITOR` - Create a new monitor [Optional]
4. `DATADOG_UPDATE_MONITOR` - Update monitor configuration [Optional]
5. `DATADOG_MUTE_MONITOR` - Silence a monitor temporarily [Optional]
6. `DATADOG_UNMUTE_MONITOR` - Re-enable a muted monitor [Optional]

**Key parameters**:
- `monitor_id`: Numeric monitor ID
- `name`: Monitor display name
- `type`: Monitor type ('metric alert', 'service check', 'log alert', 'query alert', etc.)
- `query`: Monitor query defining the alert condition
- `message`: Notification message with @mentions
- `tags`: Array of tag strings
- `thresholds`: Alert threshold values (`critical`, `warning`, `ok`)

**Pitfalls**:
- Monitor `type` must match the query type; mismatches cause creation failures
- `message` supports @mentions for notifications (e.g., `@slack-channel`, `@pagerduty`)
- Thresholds vary by monitor type; metric monitors need `critical` at minimum
- Muting a monitor suppresses notifications but the monitor still evaluates
- Monitor IDs are numeric integers

### 4. Manage Dashboards

**When to use**: User wants to list, view, update, or delete dashboards

**Tool sequence**:
1. `DATADOG_LIST_DASHBOARDS` - List all dashboards [Required]
2. `DATADOG_GET_DASHBOARD` - Get full dashboard definition [Optional]
3. `DATADOG_UPDATE_DASHBOARD` - Update dashboard layout or widgets [Optional]
4. `DATADOG_DELETE_DASHBOARD` - Remove a dashboard (irreversible) [Optional]

**Key parameters**:
- `dashboard_id`: Dashboard identifier string
- `title`: Dashboard title
- `layout_type`: 'ordered' (grid) or 'free' (freeform positioning)
- `widgets`: Array of widget definition objects
- `description`: Dashboard description

**Pitfalls**:
- Dashboard IDs are alphanumeric strings (e.g., 'abc-def-ghi'), not numeric
- `layout_type` cannot be changed after creation; must recreate the dashboard
- Widget definitions are complex nested objects; get existing dashboard first to understand structure
- DELETE is permanent; there is no undo

### 5. Create Events and Manage Downtimes

**When to use**: User wants to post events or schedule maintenance downtimes

**Tool sequence**:
1. `DATADOG_LIST_EVENTS` - List existing events [Optional]
2. `DATADOG_CREATE_EVENT` - Post a new event [Required]
3. `DATADOG_CREATE_DOWNTIME` - Schedule a maintenance downtime [Optional]

**Key parameters for events**:
- `title`: Event title
- `text`: Event body text (supports markdown)
- `alert_type`: Event severity ('error', 'warning', 'info', 'success')
- `tags`: Array of tag strings

**Key parameters for downtimes**:
- `scope`: Tag scope for the downtime (e.g., `host:web01`)
- `start`: Start time (Unix epoch)
- `end`: End time (Unix epoch; omit for indefinite)
- `message`: Downtime description
- `monitor_id`: Specific monitor to downtime (optional, omit for scope-based)

**Pitfalls**:
- Event `text` supports Datadog's markdown format including @mentions
- Downtimes scope uses tag syntax: `host:web01`, `env:staging`
- Omitting `end` creates an indefinite downtime; always set an end time for maintenance
- Downtime `monitor_id` narrows to a single monitor; scope applies to all matching monitors

### 6. Manage Hosts and Traces

**When to use**: User wants to list infrastructure hosts or inspect distributed traces

**Tool sequence**:
1. `DATADOG_LIST_HOSTS` - List all reporting hosts [Required]
2. `DATADOG_GET_TRACE_BY_ID` - Get a specific distributed trace [Optional]

**Key parameters**:
- `filter`: Host search filter string
- `sort_field`: Sort hosts by field (e.g., 'name', 'apps', 'cpu')
- `sort_dir`: Sort direction ('asc' or 'desc')
- `trace_id`: Distributed trace ID for trace lookup

**Pitfalls**:
- Host list includes all hosts reporting to Datadog within the retention window
- Trace IDs are long numeric strings; ensure exact match
- Hosts that stop reporting are retained for a configured period before removal

## Common Patterns

### Monitor Query Syntax

**Metric alerts**:
```
avg(last_5m):avg:system.cpu.user{env:prod} > 90
```

**Log alerts**:
```
logs("service:web status:error").index("main").rollup("count").last("5m") > 10
```

### Tag Filtering

- Tags use `key:value` format: `host:web01`, `env:prod`, `service:api`
- Multiple tags: `{host:web01,env:prod}` (AND logic)
- Wildcard: `host:web*`

### Pagination

- Use `page` and `page_size` or offset-based pagination depending on endpoint
- Check response for total count to determine if more pages exist
- Continue until all results are retrieved

## Known Pitfalls

**Timestamps**:
- Most endpoints use Unix epoch seconds (not milliseconds)
- Some endpoints accept ISO 8601; check tool schema
- Time ranges should be reasonable (not years of data)

**Query Syntax**:
- Metric queries: `aggregation:metric{tags}`
- Log queries: `field:value` pairs
- Monitor queries vary by type; check Datadog documentation

**Rate Limits**:
- Datadog API has per-endpoint rate limits
- Implement backoff on 429 responses
- Batch operations where possible

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Query metrics | DATADOG_QUERY_METRICS | query, from, to |
| List metrics | DATADOG_LIST_METRICS | q |
| Search logs | DATADOG_SEARCH_LOGS | query, from, to, limit |
| List log indexes | DATADOG_LIST_LOG_INDEXES | (none) |
| List monitors | DATADOG_LIST_MONITORS | tags |
| Get monitor | DATADOG_GET_MONITOR | monitor_id |
| Create monitor | DATADOG_CREATE_MONITOR | name, type, query, message |
| Update monitor | DATADOG_UPDATE_MONITOR | monitor_id |
| Mute monitor | DATADOG_MUTE_MONITOR | monitor_id |
| Unmute monitor | DATADOG_UNMUTE_MONITOR | monitor_id |
| List dashboards | DATADOG_LIST_DASHBOARDS | (none) |
| Get dashboard | DATADOG_GET_DASHBOARD | dashboard_id |
| Update dashboard | DATADOG_UPDATE_DASHBOARD | dashboard_id, title, widgets |
| Delete dashboard | DATADOG_DELETE_DASHBOARD | dashboard_id |
| List events | DATADOG_LIST_EVENTS | start, end |
| Create event | DATADOG_CREATE_EVENT | title, text, alert_type |
| Create downtime | DATADOG_CREATE_DOWNTIME | scope, start, end |
| List hosts | DATADOG_LIST_HOSTS | filter, sort_field |
| Get trace | DATADOG_GET_TRACE_BY_ID | trace_id |
