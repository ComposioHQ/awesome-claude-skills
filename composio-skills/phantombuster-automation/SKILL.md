---
name: PhantomBuster Automation
description: "Automate lead generation, web scraping, and social media data extraction workflows through PhantomBuster's cloud platform via Composio"
requires:
  mcp:
    - rube
---

# PhantomBuster Automation

Automate cloud-based data extraction and lead generation -- manage agents and scripts, monitor organization resources and usage, track container execution, and solve captcha challenges -- all orchestrated through the Composio MCP integration.

**Toolkit docs:** [composio.dev/toolkits/phantombuster](https://composio.dev/toolkits/phantombuster)

---

## Setup

1. Connect your PhantomBuster account through the Composio MCP server at `https://rube.app/mcp`
2. The agent will prompt you with an authentication link if no active connection exists
3. Once connected, all `PHANTOMBUSTER_*` tools become available for execution

---

## Core Workflows

### 1. List All Agents
Fetch every agent associated with your account or organization to inventory automation workflows.

**Tool:** `PHANTOMBUSTER_GET_AGENTS_FETCH_ALL`

```
No parameters required -- returns all agents with IDs and metadata.
Authenticate your API key first.
```

Use agent IDs from this response when fetching containers or monitoring specific automations.

---

### 2. List All Scripts
Retrieve all scripts available under your account (without code bodies) for script management.

**Tool:** `PHANTOMBUSTER_GET_SCRIPTS_FETCH_ALL`

```
No parameters required -- returns script metadata without source code.
```

---

### 3. Monitor Organization Resources & Quotas
Check your organization's current resource usage and quota limits to plan automation capacity.

**Tool:** `PHANTOMBUSTER_GET_ORGS_FETCH_RESOURCES`

```
No parameters required -- returns resource allocation and current usage metrics.
```

---

### 4. Retrieve Agent Containers
Fetch all execution containers for a specific agent to monitor run history and status.

**Tool:** `PHANTOMBUSTER_GET_CONTAINERS_FETCH_ALL`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agentId` | string | Yes | Agent ID from `PHANTOMBUSTER_GET_AGENTS_FETCH_ALL` |

---

### 5. Export Agent Usage Report
Download a CSV report of all agents' run statistics for your organization.

**Tool:** `PHANTOMBUSTER_GET_ORGS_EXPORT_AGENT_USAGE`

```
Returns a downloadable CSV with comprehensive agent execution statistics.
```

---

### 6. Solve hCaptcha Challenges
Obtain a valid hCaptcha token for automated form submissions or scraping flows that require captcha solving.

**Tool:** `PHANTOMBUSTER_POST_HCAPTCHA`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `siteKey` | string | Yes | Public site key of the hCaptcha widget |
| `pageUrl` | string | Yes | Full URL of the page with the captcha |
| `proxy` | string | No | Proxy URL (e.g., `http://user:pass@host:port`) |
| `userAgent` | string | No | Custom User-Agent string to simulate |

---

## Known Pitfalls

| Pitfall | Details |
|---------|---------|
| **Agent ID required for containers** | `PHANTOMBUSTER_GET_CONTAINERS_FETCH_ALL` requires a valid `agentId` -- always resolve it first via `PHANTOMBUSTER_GET_AGENTS_FETCH_ALL` |
| **API key authentication** | All PhantomBuster tools require a valid API key connection -- verify authentication before calling any tools |
| **Script bodies not included** | `PHANTOMBUSTER_GET_SCRIPTS_FETCH_ALL` returns metadata only, not source code |
| **Organization scope** | Resource and usage tools operate at the organization level tied to your API key -- ensure the correct org is targeted |
| **Branch operations** | `PHANTOMBUSTER_GET_BRANCHES_FETCH_ALL` and `PHANTOMBUSTER_GET_BRANCHES_DIFF` are for advanced script versioning -- use them to assess staging vs. release changes before deployment |

---

## Quick Reference

| Tool Slug | Purpose |
|-----------|---------|
| `PHANTOMBUSTER_GET_AGENTS_FETCH_ALL` | List all agents in your account |
| `PHANTOMBUSTER_GET_SCRIPTS_FETCH_ALL` | List all scripts (metadata only) |
| `PHANTOMBUSTER_GET_ORGS_FETCH_RESOURCES` | Check organization resource usage and quotas |
| `PHANTOMBUSTER_GET_CONTAINERS_FETCH_ALL` | Get all containers for a specific agent |
| `PHANTOMBUSTER_GET_ORGS_EXPORT_AGENT_USAGE` | Export agent usage as CSV |
| `PHANTOMBUSTER_POST_HCAPTCHA` | Solve hCaptcha challenges for automation |
| `PHANTOMBUSTER_GET_ORGS_FETCH` | Fetch organization details |
| `PHANTOMBUSTER_GET_ORGS_FETCH_AGENT_GROUPS` | Get agent groups and ordering |
| `PHANTOMBUSTER_GET_BRANCHES_FETCH_ALL` | List all script branches |
| `PHANTOMBUSTER_GET_BRANCHES_DIFF` | Compare staging vs. release branches |

---

*Powered by [Composio](https://composio.dev)*
