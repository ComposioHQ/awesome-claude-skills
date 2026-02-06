---
name: vercel-automation
description: "Automate Vercel tasks via Rube MCP (Composio): manage deployments, domains, DNS, env vars, projects, and teams. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Vercel Automation via Rube MCP

Automate Vercel platform operations through Composio's Vercel toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Vercel connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `vercel`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `vercel`
3. If connection is not ACTIVE, follow the returned auth link to complete Vercel OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Monitor and Inspect Deployments

**When to use**: User wants to list, inspect, or debug deployments

**Tool sequence**:
1. `VERCEL_LIST_ALL_DEPLOYMENTS` or `VERCEL_GET_DEPLOYMENTS` - List deployments with filters [Required]
2. `VERCEL_GET_DEPLOYMENT` or `VERCEL_GET_DEPLOYMENT_DETAILS` - Get specific deployment info [Optional]
3. `VERCEL_GET_DEPLOYMENT_LOGS` or `VERCEL_GET_RUNTIME_LOGS` - View build/runtime logs [Optional]
4. `VERCEL_GET_DEPLOYMENT_EVENTS` - Get deployment event timeline [Optional]
5. `VERCEL_LIST_DEPLOYMENT_CHECKS` - View deployment check results [Optional]

**Key parameters**:
- `projectId`: Filter deployments by project
- `state`: Filter by deployment state (e.g., 'READY', 'ERROR', 'BUILDING')
- `limit`: Number of deployments to return
- `target`: Filter by environment ('production', 'preview')
- `deploymentId` or `idOrUrl`: Specific deployment identifier

**Pitfalls**:
- Deployment IDs and URLs are both accepted as identifiers in most endpoints
- Build logs and runtime logs are separate; use the appropriate tool
- `VERCEL_GET_DEPLOYMENT_LOGS` returns build logs; `VERCEL_GET_RUNTIME_LOGS` returns serverless function logs
- Deployment events include status transitions and are useful for debugging timing issues

### 2. Create and Manage Deployments

**When to use**: User wants to trigger a new deployment

**Tool sequence**:
1. `VERCEL_LIST_PROJECTS` - Find the target project [Prerequisite]
2. `VERCEL_CREATE_NEW_DEPLOYMENT` - Trigger a new deployment [Required]
3. `VERCEL_GET_DEPLOYMENT` - Monitor deployment progress [Optional]

**Key parameters**:
- `name`: Project name for the deployment
- `target`: Deployment target ('production' or 'preview')
- `gitSource`: Git repository source with ref/branch info
- `files`: Array of file objects for file-based deployments

**Pitfalls**:
- Either `gitSource` or `files` must be provided, not both
- Git-based deployments require proper repository integration
- Production deployments update the production domain alias automatically
- Deployment creation is asynchronous; poll with GET_DEPLOYMENT for status

### 3. Manage Environment Variables

**When to use**: User wants to add, list, or remove environment variables for a project

**Tool sequence**:
1. `VERCEL_LIST_PROJECTS` - Find the project ID [Prerequisite]
2. `VERCEL_LIST_ENV_VARIABLES` - List existing env vars [Required]
3. `VERCEL_ADD_ENVIRONMENT_VARIABLE` - Add a new env var [Optional]
4. `VERCEL_DELETE_ENVIRONMENT_VARIABLE` - Remove an env var [Optional]

**Key parameters**:
- `projectId`: Target project identifier
- `key`: Environment variable name
- `value`: Environment variable value
- `target`: Array of environments ('production', 'preview', 'development')
- `type`: Variable type ('plain', 'secret', 'encrypted', 'sensitive')

**Pitfalls**:
- Environment variable names must be unique per target environment
- `type: 'secret'` variables cannot be read back after creation; only the ID is returned
- Deleting an env var requires both `projectId` and the env var `id` (not the key name)
- Changes require a new deployment to take effect

### 4. Manage Domains and DNS

**When to use**: User wants to configure custom domains or manage DNS records

**Tool sequence**:
1. `VERCEL_GET_DOMAIN` - Check domain status and configuration [Required]
2. `VERCEL_GET_DOMAIN_CONFIG` - Get DNS/SSL configuration details [Optional]
3. `VERCEL_LIST_PROJECT_DOMAINS` - List domains attached to a project [Optional]
4. `VERCEL_GET_DNS_RECORDS` - List DNS records for a domain [Optional]
5. `VERCEL_CREATE_DNS_RECORD` - Add a new DNS record [Optional]
6. `VERCEL_UPDATE_DNS_RECORD` - Modify an existing DNS record [Optional]

**Key parameters**:
- `domain`: Domain name (e.g., 'example.com')
- `name`: DNS record name/subdomain
- `type`: DNS record type ('A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SRV')
- `value`: DNS record value
- `ttl`: Time-to-live in seconds

**Pitfalls**:
- Domain must be added to the Vercel account before DNS management
- SSL certificates are auto-provisioned but may take time for new domains
- CNAME records at the apex domain are not supported; use A records instead
- MX records require priority values

### 5. Manage Projects

**When to use**: User wants to list, inspect, or update project settings

**Tool sequence**:
1. `VERCEL_LIST_PROJECTS` - List all projects [Required]
2. `VERCEL_GET_PROJECT` - Get detailed project information [Optional]
3. `VERCEL_UPDATE_PROJECT` - Modify project settings [Optional]

**Key parameters**:
- `idOrName`: Project ID or name for lookup
- `name`: Project name for updates
- `framework`: Framework preset (e.g., 'nextjs', 'vite', 'remix')
- `buildCommand`: Custom build command override
- `rootDirectory`: Root directory if not repo root

**Pitfalls**:
- Project names are globally unique within a team/account
- Changing framework settings affects subsequent deployments
- `rootDirectory` is relative to the repository root

### 6. Team Management

**When to use**: User wants to view team info or list team members

**Tool sequence**:
1. `VERCEL_LIST_TEAMS` - List all teams the user belongs to [Required]
2. `VERCEL_GET_TEAM` - Get detailed team information [Optional]
3. `VERCEL_GET_TEAM_MEMBERS` - List members of a specific team [Optional]

**Key parameters**:
- `teamId`: Team identifier
- `limit`: Number of results per page
- `role`: Filter members by role

**Pitfalls**:
- Team operations require appropriate team-level permissions
- Personal accounts have no teams; team endpoints return empty results
- Member roles include 'OWNER', 'MEMBER', 'DEVELOPER', 'VIEWER'

## Common Patterns

### ID Resolution

**Project name -> Project ID**:
```
1. Call VERCEL_LIST_PROJECTS
2. Find project by name in response
3. Extract id field for subsequent operations
```

**Domain -> DNS Records**:
```
1. Call VERCEL_GET_DNS_RECORDS with domain name
2. Extract record IDs for update/delete operations
```

### Pagination

- Use `limit` parameter to control page size
- Check response for pagination tokens or `next` fields
- Continue fetching until no more pages are indicated

## Known Pitfalls

**Deployment States**:
- States include: INITIALIZING, ANALYZING, BUILDING, DEPLOYING, READY, ERROR, CANCELED, QUEUED
- Only READY deployments are live and serving traffic
- ERROR deployments should be inspected via logs for failure details

**Environment Variables**:
- Secret type vars are write-only; values cannot be retrieved after creation
- Env vars are scoped to environments (production, preview, development)
- A redeployment is needed for env var changes to take effect

**Rate Limits**:
- Vercel API has rate limits per endpoint
- Implement backoff on 429 responses
- Batch operations where possible to reduce API calls

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List projects | VERCEL_LIST_PROJECTS | limit |
| Get project details | VERCEL_GET_PROJECT | idOrName |
| Update project | VERCEL_UPDATE_PROJECT | idOrName, name, framework |
| List deployments | VERCEL_LIST_ALL_DEPLOYMENTS | projectId, state, limit |
| Get deployment | VERCEL_GET_DEPLOYMENT | idOrUrl |
| Create deployment | VERCEL_CREATE_NEW_DEPLOYMENT | name, target, gitSource |
| Deployment logs | VERCEL_GET_DEPLOYMENT_LOGS | deploymentId |
| Runtime logs | VERCEL_GET_RUNTIME_LOGS | deploymentId |
| List env vars | VERCEL_LIST_ENV_VARIABLES | projectId |
| Add env var | VERCEL_ADD_ENVIRONMENT_VARIABLE | projectId, key, value, target |
| Delete env var | VERCEL_DELETE_ENVIRONMENT_VARIABLE | projectId, id |
| Get domain | VERCEL_GET_DOMAIN | domain |
| Get domain config | VERCEL_GET_DOMAIN_CONFIG | domain |
| List DNS records | VERCEL_GET_DNS_RECORDS | domain |
| Create DNS record | VERCEL_CREATE_DNS_RECORD | domain, name, type, value |
| Update DNS record | VERCEL_UPDATE_DNS_RECORD | domain, recordId |
| List project domains | VERCEL_LIST_PROJECT_DOMAINS | projectId |
| List teams | VERCEL_LIST_TEAMS | (none) |
| Get team | VERCEL_GET_TEAM | teamId |
| Get team members | VERCEL_GET_TEAM_MEMBERS | teamId, limit |
