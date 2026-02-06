---
name: posthog-automation
description: "Automate PostHog tasks via Rube MCP (Composio): events, feature flags, projects, user profiles, annotations. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# PostHog Automation via Rube MCP

Automate PostHog product analytics and feature flag management through Composio's PostHog toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active PostHog connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `posthog`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `posthog`
3. If connection is not ACTIVE, follow the returned auth link to complete PostHog authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Capture Events

**When to use**: User wants to send event data to PostHog for analytics tracking

**Tool sequence**:
1. `POSTHOG_CAPTURE_EVENT` - Send one or more events to PostHog [Required]

**Key parameters**:
- `event`: Event name (e.g., '$pageview', 'user_signed_up', 'purchase_completed')
- `distinct_id`: Unique user identifier (required)
- `properties`: Object with event-specific properties
- `timestamp`: ISO 8601 timestamp (optional; defaults to server time)

**Pitfalls**:
- `distinct_id` is required for every event; identifies the user/device
- PostHog system events use `$` prefix (e.g., '$pageview', '$identify')
- Custom events should NOT use the `$` prefix
- Properties are freeform; maintain consistent schemas across events
- Events are processed asynchronously; ingestion delay is typically seconds

### 2. List and Filter Events

**When to use**: User wants to browse or search through captured events

**Tool sequence**:
1. `POSTHOG_LIST_AND_FILTER_PROJECT_EVENTS` - Query events with filters [Required]

**Key parameters**:
- `project_id`: PostHog project ID (required)
- `event`: Filter by event name
- `person_id`: Filter by person ID
- `after`: Events after this ISO 8601 timestamp
- `before`: Events before this ISO 8601 timestamp
- `limit`: Maximum events to return
- `offset`: Pagination offset

**Pitfalls**:
- `project_id` is required; resolve via LIST_PROJECTS first
- Date filters use ISO 8601 format (e.g., '2024-01-15T00:00:00Z')
- Large event volumes require pagination; use `offset` and `limit`
- Results are returned in reverse chronological order by default
- Event properties are nested; parse carefully

### 3. Manage Feature Flags

**When to use**: User wants to create, view, or manage feature flags

**Tool sequence**:
1. `POSTHOG_LIST_AND_MANAGE_PROJECT_FEATURE_FLAGS` - List existing feature flags [Required]
2. `POSTHOG_RETRIEVE_FEATURE_FLAG_DETAILS` - Get detailed flag configuration [Optional]
3. `POSTHOG_CREATE_FEATURE_FLAGS_FOR_PROJECT` - Create a new feature flag [Optional]

**Key parameters**:
- For listing: `project_id` (required)
- For details: `project_id`, `id` (feature flag ID)
- For creation:
  - `project_id`: Target project
  - `key`: Flag key (e.g., 'new-dashboard-beta')
  - `name`: Human-readable name
  - `filters`: Targeting rules and rollout percentage
  - `active`: Whether the flag is enabled

**Pitfalls**:
- Feature flag `key` must be unique within a project
- Flag keys should use kebab-case (e.g., 'my-feature-flag')
- `filters` define targeting groups with properties and rollout percentages
- Creating a flag with `active: true` immediately enables it for matching users
- Flag changes take effect within seconds due to PostHog's polling mechanism

### 4. Manage Projects

**When to use**: User wants to list or inspect PostHog projects and organizations

**Tool sequence**:
1. `POSTHOG_LIST_PROJECTS_IN_ORGANIZATION_WITH_PAGINATION` - List all projects [Required]

**Key parameters**:
- `organization_id`: Organization identifier (may be optional depending on auth)
- `limit`: Number of results per page
- `offset`: Pagination offset

**Pitfalls**:
- Project IDs are numeric; used as parameters in most other endpoints
- Organization ID may be required; check your PostHog setup
- Pagination is offset-based; iterate until results are empty
- Project settings include API keys and configuration details

### 5. User Profile and Authentication

**When to use**: User wants to check current user details or verify API access

**Tool sequence**:
1. `POSTHOG_WHOAMI` - Get current API user information [Optional]
2. `POSTHOG_RETRIEVE_CURRENT_USER_PROFILE` - Get detailed user profile [Optional]

**Key parameters**:
- No required parameters for either call
- Returns current authenticated user's details, permissions, and organization info

**Pitfalls**:
- WHOAMI is a lightweight check; use for verifying API connectivity
- User profile includes organization membership and permissions
- These endpoints confirm the API key's access level and scope

## Common Patterns

### ID Resolution

**Organization -> Project ID**:
```
1. Call POSTHOG_LIST_PROJECTS_IN_ORGANIZATION_WITH_PAGINATION
2. Find project by name in results
3. Extract id (numeric) for use in other endpoints
```

**Feature flag name -> Flag ID**:
```
1. Call POSTHOG_LIST_AND_MANAGE_PROJECT_FEATURE_FLAGS with project_id
2. Find flag by key or name
3. Extract id for detailed operations
```

### Feature Flag Targeting

Feature flags support sophisticated targeting:
```json
{
  "filters": {
    "groups": [
      {
        "properties": [
          {"key": "email", "value": "@company.com", "operator": "icontains"}
        ],
        "rollout_percentage": 100
      },
      {
        "properties": [],
        "rollout_percentage": 10
      }
    ]
  }
}
```
- Groups are evaluated in order; first matching group determines the rollout
- Properties filter users by their traits
- Rollout percentage determines what fraction of matching users see the flag

### Pagination

- Events: Use `offset` and `limit` (offset-based)
- Feature flags: Use `offset` and `limit` (offset-based)
- Projects: Use `offset` and `limit` (offset-based)
- Continue until results array is empty or smaller than `limit`

## Known Pitfalls

**Project IDs**:
- Required for most API endpoints
- Always resolve project names to numeric IDs first
- Multiple projects can exist in one organization

**Event Naming**:
- System events use `$` prefix ($pageview, $identify, $autocapture)
- Custom events should NOT use `$` prefix
- Event names are case-sensitive; maintain consistency

**Feature Flags**:
- Flag keys must be unique within a project
- Use kebab-case for flag keys
- Changes propagate within seconds
- Deleting a flag is permanent; consider disabling instead

**Rate Limits**:
- Event ingestion has throughput limits
- Batch events where possible for efficiency
- API endpoints have per-minute rate limits

**Response Parsing**:
- Response data may be nested under `data` or `results` key
- Paginated responses include `count`, `next`, `previous` fields
- Event properties are nested objects; access carefully
- Parse defensively with fallbacks for optional fields

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Capture event | POSTHOG_CAPTURE_EVENT | event, distinct_id, properties |
| List events | POSTHOG_LIST_AND_FILTER_PROJECT_EVENTS | project_id, event, after, before |
| List feature flags | POSTHOG_LIST_AND_MANAGE_PROJECT_FEATURE_FLAGS | project_id |
| Get flag details | POSTHOG_RETRIEVE_FEATURE_FLAG_DETAILS | project_id, id |
| Create flag | POSTHOG_CREATE_FEATURE_FLAGS_FOR_PROJECT | project_id, key, filters |
| List projects | POSTHOG_LIST_PROJECTS_IN_ORGANIZATION_WITH_PAGINATION | organization_id |
| Who am I | POSTHOG_WHOAMI | (none) |
| User profile | POSTHOG_RETRIEVE_CURRENT_USER_PROFILE | (none) |
