---
name: render-automation
description: "Automate Render tasks via Rube MCP (Composio): services, deployments, projects. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Render Automation via Rube MCP

Automate Render cloud platform operations through Composio's Render toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Render connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `render`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `render`
3. If connection is not ACTIVE, follow the returned auth link to complete Render authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List and Browse Services

**When to use**: User wants to find or inspect Render services (web services, static sites, workers, cron jobs)

**Tool sequence**:
1. `RENDER_LIST_SERVICES` - List all services with optional filters [Required]

**Key parameters**:
- `name`: Filter services by name substring
- `type`: Filter by service type ('web_service', 'static_site', 'private_service', 'background_worker', 'cron_job')
- `limit`: Maximum results per page (default 20, max 100)
- `cursor`: Pagination cursor from previous response

**Pitfalls**:
- Service types must match exact enum values: 'web_service', 'static_site', 'private_service', 'background_worker', 'cron_job'
- Pagination uses cursor-based approach; follow `cursor` until absent
- Name filter is substring-based, not exact match
- Service IDs follow the format 'srv-xxxxxxxxxxxx'
- Default limit is 20; set higher for comprehensive listing

### 2. Trigger Deployments

**When to use**: User wants to manually deploy or redeploy a service

**Tool sequence**:
1. `RENDER_LIST_SERVICES` - Find the service to deploy [Prerequisite]
2. `RENDER_TRIGGER_DEPLOY` - Trigger a new deployment [Required]
3. `RENDER_RETRIEVE_DEPLOY` - Monitor deployment progress [Optional]

**Key parameters**:
- For TRIGGER_DEPLOY:
  - `serviceId`: Service ID to deploy (required, format: 'srv-xxxxxxxxxxxx')
  - `clearCache`: Set `true` to clear build cache before deploying
- For RETRIEVE_DEPLOY:
  - `serviceId`: Service ID
  - `deployId`: Deploy ID from trigger response (format: 'dep-xxxxxxxxxxxx')

**Pitfalls**:
- `serviceId` is required; resolve via LIST_SERVICES first
- Service IDs start with 'srv-' prefix
- Deploy IDs start with 'dep-' prefix
- `clearCache: true` forces a clean build; takes longer but resolves cache-related issues
- Deployment is asynchronous; use RETRIEVE_DEPLOY to poll status
- Triggering a deploy while another is in progress may queue the new one

### 3. Monitor Deployment Status

**When to use**: User wants to check the progress or result of a deployment

**Tool sequence**:
1. `RENDER_RETRIEVE_DEPLOY` - Get deployment details and status [Required]

**Key parameters**:
- `serviceId`: Service ID (required)
- `deployId`: Deployment ID (required)
- Response includes `status`, `createdAt`, `updatedAt`, `finishedAt`, `commit`

**Pitfalls**:
- Both `serviceId` and `deployId` are required
- Deploy statuses include: 'created', 'build_in_progress', 'update_in_progress', 'live', 'deactivated', 'build_failed', 'update_failed', 'canceled'
- 'live' indicates successful deployment
- 'build_failed' or 'update_failed' indicate deployment errors
- Poll at reasonable intervals (10-30 seconds) to avoid rate limits

### 4. Manage Projects

**When to use**: User wants to list and organize Render projects

**Tool sequence**:
1. `RENDER_LIST_PROJECTS` - List all projects [Required]

**Key parameters**:
- `limit`: Maximum results per page (max 100)
- `cursor`: Pagination cursor from previous response

**Pitfalls**:
- Projects group related services together
- Pagination uses cursor-based approach
- Project IDs are used for organizational purposes
- Not all services may be assigned to a project

## Common Patterns

### ID Resolution

**Service name -> Service ID**:
```
1. Call RENDER_LIST_SERVICES with name=service_name
2. Find service by name in results
3. Extract id (format: 'srv-xxxxxxxxxxxx')
```

**Deployment lookup**:
```
1. Store deployId from RENDER_TRIGGER_DEPLOY response
2. Call RENDER_RETRIEVE_DEPLOY with serviceId and deployId
3. Check status for completion
```

### Deploy and Monitor Pattern

```
1. RENDER_LIST_SERVICES -> find service by name -> get serviceId
2. RENDER_TRIGGER_DEPLOY with serviceId -> get deployId
3. Loop: RENDER_RETRIEVE_DEPLOY with serviceId + deployId
4. Check status: 'live' = success, 'build_failed'/'update_failed' = error
5. Continue polling until terminal state reached
```

### Pagination

- Use `cursor` from response for next page
- Continue until `cursor` is absent or results are empty
- Both LIST_SERVICES and LIST_PROJECTS use cursor-based pagination
- Set `limit` to max (100) for fewer pagination rounds

## Known Pitfalls

**Service IDs**:
- Always prefixed with 'srv-' (e.g., 'srv-abcd1234efgh')
- Deploy IDs prefixed with 'dep-' (e.g., 'dep-d2mqkf9r0fns73bham1g')
- Always resolve service names to IDs via LIST_SERVICES

**Service Types**:
- Must use exact enum values when filtering
- Available types: web_service, static_site, private_service, background_worker, cron_job
- Different service types have different deployment behaviors

**Deployment Behavior**:
- Deployments are asynchronous; always poll for completion
- Clear cache deploys take longer but resolve stale cache issues
- Failed deploys do not roll back automatically; the previous version stays live
- Concurrent deploy triggers may be queued

**Rate Limits**:
- Render API has rate limits
- Avoid rapid polling; use 10-30 second intervals
- Bulk operations should be throttled

**Response Parsing**:
- Response data may be nested under `data` key
- Timestamps use ISO 8601 format
- Parse defensively with fallbacks for optional fields

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List services | RENDER_LIST_SERVICES | name, type, limit, cursor |
| Trigger deploy | RENDER_TRIGGER_DEPLOY | serviceId, clearCache |
| Get deploy status | RENDER_RETRIEVE_DEPLOY | serviceId, deployId |
| List projects | RENDER_LIST_PROJECTS | limit, cursor |
