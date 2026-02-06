---
name: google-analytics-automation
description: "Automate Google Analytics tasks via Rube MCP (Composio): run reports, list accounts/properties, funnels, pivots, key events. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Google Analytics Automation via Rube MCP

Automate Google Analytics 4 (GA4) reporting and property management through Composio's Google Analytics toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Google Analytics connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `google_analytics`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `google_analytics`
3. If connection is not ACTIVE, follow the returned auth link to complete Google OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List Accounts and Properties

**When to use**: User wants to discover available GA4 accounts and properties

**Tool sequence**:
1. `GOOGLE_ANALYTICS_LIST_ACCOUNTS` - List all accessible GA4 accounts [Required]
2. `GOOGLE_ANALYTICS_LIST_PROPERTIES` - List properties under an account [Required]

**Key parameters**:
- `pageSize`: Number of results per page
- `pageToken`: Pagination token from previous response
- `filter`: Filter expression for properties (e.g., `parent:accounts/12345`)

**Pitfalls**:
- Property IDs are numeric strings prefixed with 'properties/' (e.g., 'properties/123456')
- Account IDs are prefixed with 'accounts/' (e.g., 'accounts/12345')
- Always list accounts first, then properties under each account
- Pagination required for organizations with many properties

### 2. Run Standard Reports

**When to use**: User wants to query metrics and dimensions from GA4 data

**Tool sequence**:
1. `GOOGLE_ANALYTICS_LIST_PROPERTIES` - Get property ID [Prerequisite]
2. `GOOGLE_ANALYTICS_GET_METADATA` - Discover available dimensions and metrics [Optional]
3. `GOOGLE_ANALYTICS_CHECK_COMPATIBILITY` - Verify dimension/metric compatibility [Optional]
4. `GOOGLE_ANALYTICS_RUN_REPORT` - Execute the report query [Required]

**Key parameters**:
- `property`: Property ID (e.g., 'properties/123456')
- `dateRanges`: Array of date range objects with `startDate` and `endDate`
- `dimensions`: Array of dimension objects with `name` field
- `metrics`: Array of metric objects with `name` field
- `dimensionFilter` / `metricFilter`: Filter expressions
- `orderBys`: Sort order configuration
- `limit`: Maximum rows to return
- `offset`: Row offset for pagination

**Pitfalls**:
- Date format is 'YYYY-MM-DD' or relative values like 'today', 'yesterday', '7daysAgo', '30daysAgo'
- Not all dimensions and metrics are compatible; use CHECK_COMPATIBILITY first
- Use GET_METADATA to discover valid dimension and metric names
- Maximum 9 dimensions per report request
- Row limit defaults vary; set explicitly for large datasets
- `offset` is for result pagination, not date pagination

### 3. Run Batch Reports

**When to use**: User needs multiple different reports from the same property in one call

**Tool sequence**:
1. `GOOGLE_ANALYTICS_LIST_PROPERTIES` - Get property ID [Prerequisite]
2. `GOOGLE_ANALYTICS_BATCH_RUN_REPORTS` - Execute multiple reports at once [Required]

**Key parameters**:
- `property`: Property ID (required)
- `requests`: Array of individual report request objects (same structure as RUN_REPORT)

**Pitfalls**:
- Maximum 5 report requests per batch call
- All reports in a batch must target the same property
- Each individual report has the same dimension/metric limits as RUN_REPORT
- Batch errors may affect all reports; check individual report responses

### 4. Run Pivot Reports

**When to use**: User wants cross-tabulated data (rows vs columns) like pivot tables

**Tool sequence**:
1. `GOOGLE_ANALYTICS_LIST_PROPERTIES` - Get property ID [Prerequisite]
2. `GOOGLE_ANALYTICS_RUN_PIVOT_REPORT` - Execute pivot report [Required]

**Key parameters**:
- `property`: Property ID (required)
- `dateRanges`: Date range objects
- `dimensions`: All dimensions used in any pivot
- `metrics`: Metrics to aggregate
- `pivots`: Array of pivot definitions with `fieldNames`, `limit`, and `orderBys`

**Pitfalls**:
- Dimensions used in pivots must also be listed in top-level `dimensions`
- Pivot `fieldNames` reference dimension names from the top-level list
- Complex pivots with many dimensions can produce very large result sets
- Each pivot has its own independent `limit` and `orderBys`

### 5. Run Funnel Reports

**When to use**: User wants to analyze conversion funnels and drop-off rates

**Tool sequence**:
1. `GOOGLE_ANALYTICS_LIST_PROPERTIES` - Get property ID [Prerequisite]
2. `GOOGLE_ANALYTICS_RUN_FUNNEL_REPORT` - Execute funnel analysis [Required]

**Key parameters**:
- `property`: Property ID (required)
- `dateRanges`: Date range objects
- `funnel`: Funnel definition with `steps` array
- `funnelBreakdown`: Optional dimension to break down funnel by

**Pitfalls**:
- Funnel steps are ordered; each step defines a condition users must meet
- Steps use filter expressions similar to dimension/metric filters
- Open funnels allow entry at any step; closed funnels require sequential progression
- Funnel reports may take longer to process than standard reports

### 6. Manage Key Events

**When to use**: User wants to view or manage conversion events (key events) in GA4

**Tool sequence**:
1. `GOOGLE_ANALYTICS_LIST_PROPERTIES` - Get property ID [Prerequisite]
2. `GOOGLE_ANALYTICS_LIST_KEY_EVENTS` - List all key events for the property [Required]

**Key parameters**:
- `parent`: Property resource name (e.g., 'properties/123456')
- `pageSize`: Number of results per page
- `pageToken`: Pagination token

**Pitfalls**:
- Key events were previously called "conversions" in GA4
- Property must have key events configured to return results
- Key event names correspond to GA4 event names

## Common Patterns

### ID Resolution

**Account name -> Account ID**:
```
1. Call GOOGLE_ANALYTICS_LIST_ACCOUNTS
2. Find account by displayName
3. Extract name field (e.g., 'accounts/12345')
```

**Property name -> Property ID**:
```
1. Call GOOGLE_ANALYTICS_LIST_PROPERTIES with filter
2. Find property by displayName
3. Extract name field (e.g., 'properties/123456')
```

### Dimension/Metric Discovery

```
1. Call GOOGLE_ANALYTICS_GET_METADATA with property ID
2. Browse available dimensions and metrics
3. Call GOOGLE_ANALYTICS_CHECK_COMPATIBILITY to verify combinations
4. Use verified dimensions/metrics in RUN_REPORT
```

### Pagination

- Reports: Use `offset` and `limit` for row pagination
- Accounts/Properties: Use `pageToken` from response
- Continue until `pageToken` is absent or `rowCount` reached

### Common Dimensions and Metrics

**Dimensions**: `date`, `city`, `country`, `deviceCategory`, `sessionSource`, `sessionMedium`, `pagePath`, `pageTitle`, `eventName`

**Metrics**: `activeUsers`, `sessions`, `screenPageViews`, `eventCount`, `conversions`, `totalRevenue`, `bounceRate`, `averageSessionDuration`

## Known Pitfalls

**Property IDs**:
- Always use full resource name format: 'properties/123456'
- Numeric ID alone will cause errors
- Resolve property names to IDs via LIST_PROPERTIES

**Date Ranges**:
- Format: 'YYYY-MM-DD' or relative ('today', 'yesterday', '7daysAgo', '30daysAgo')
- Data processing delay means today's data may be incomplete
- Maximum date range varies by property configuration

**Compatibility**:
- Not all dimensions work with all metrics
- Always verify with CHECK_COMPATIBILITY before complex reports
- Custom dimensions/metrics have specific naming patterns

**Response Parsing**:
- Report data is nested in `rows` array with `dimensionValues` and `metricValues`
- Values are returned as strings; parse numbers explicitly
- Empty reports return no `rows` key (not an empty array)

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List accounts | GOOGLE_ANALYTICS_LIST_ACCOUNTS | pageSize, pageToken |
| List properties | GOOGLE_ANALYTICS_LIST_PROPERTIES | filter, pageSize |
| Get metadata | GOOGLE_ANALYTICS_GET_METADATA | property |
| Check compatibility | GOOGLE_ANALYTICS_CHECK_COMPATIBILITY | property, dimensions, metrics |
| Run report | GOOGLE_ANALYTICS_RUN_REPORT | property, dateRanges, dimensions, metrics |
| Batch reports | GOOGLE_ANALYTICS_BATCH_RUN_REPORTS | property, requests |
| Pivot report | GOOGLE_ANALYTICS_RUN_PIVOT_REPORT | property, dateRanges, pivots |
| Funnel report | GOOGLE_ANALYTICS_RUN_FUNNEL_REPORT | property, dateRanges, funnel |
| List key events | GOOGLE_ANALYTICS_LIST_KEY_EVENTS | parent, pageSize |
