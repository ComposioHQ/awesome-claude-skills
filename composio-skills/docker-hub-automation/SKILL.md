---
name: Docker Hub Automation
description: "Automate Docker Hub operations -- manage organizations, repositories, teams, members, and webhooks via the Composio MCP integration."
requires:
  mcp:
    - rube
---

# Docker Hub Automation

Automate your Docker Hub workflows -- create and manage organizations, repositories, teams, add members, set up image push webhooks, and list container images.

**Toolkit docs:** [composio.dev/toolkits/docker_hub](https://composio.dev/toolkits/docker_hub)

---

## Setup

1. Add the Composio MCP server to your client: `https://rube.app/mcp`
2. Connect your Docker Hub account when prompted (JWT/token authentication)
3. Start using the workflows below

---

## Core Workflows

### 1. List Organizations

Use `DOCKER_HUB_LIST_ORGANIZATIONS` to discover which organizations the authenticated user belongs to.

```
Tool: DOCKER_HUB_LIST_ORGANIZATIONS
Inputs:
  - page: integer (1-indexed, default 1)
  - page_size: integer (1-100, default 25)
```

### 2. Create an Organization

Use `DOCKER_HUB_CREATE_ORGANIZATION` to programmatically create a new Docker Hub organization.

```
Tool: DOCKER_HUB_CREATE_ORGANIZATION
Inputs:
  - orgname: string (required) -- lowercase, letters/numbers/._- only, min 2 chars
  - company: string (optional) -- company name associated with the org
```

**Note:** Requires JWT authentication obtained via `/v2/users/login` and may have restricted access.

### 3. Get Organization Details and Repositories

Use `DOCKER_HUB_GET_ORGANIZATION` to retrieve namespace info and its repositories. Works with any public namespace.

```
Tool: DOCKER_HUB_GET_ORGANIZATION
Inputs:
  - organization: string (required) -- e.g., "docker", "bitnami", "library"
```

### 4. Create a Repository

Use `DOCKER_HUB_CREATE_REPOSITORY` to create public or private repositories under a namespace.

```
Tool: DOCKER_HUB_CREATE_REPOSITORY
Inputs:
  - namespace: string (required) -- Docker Hub username or org name
  - name: string (required) -- lowercase; letters, numbers, ._- allowed
  - description: string (optional) -- max 100 characters
  - full_description: string (optional) -- Markdown README content
  - is_private: boolean (default false) -- private repos require paid plan
```

### 5. List Repositories with Filtering

Use `DOCKER_HUB_LIST_REPOSITORIES` to enumerate repos within a namespace with sorting and content-type filtering.

```
Tool: DOCKER_HUB_LIST_REPOSITORIES
Inputs:
  - namespace: string (required) -- e.g., "library", "myorg"
  - ordering: "name" | "last_updated" | "pull_count" (prefix with - for descending)
  - page: integer (default 1)
  - page_size: integer (1-100, default 25)
  - content_types: string (comma-separated, e.g., "image,artifact")
```

### 6. Manage Teams, Members, and Webhooks

Use `DOCKER_HUB_LIST_TEAMS` to list teams within an org, `DOCKER_HUB_ADD_ORG_MEMBER` to invite users, and `DOCKER_HUB_CREATE_WEBHOOK` for push notifications.

```
Tool: DOCKER_HUB_LIST_TEAMS
  - Lists all teams/groups within a Docker Hub organization

Tool: DOCKER_HUB_ADD_ORG_MEMBER
  - Invite a user to join an organization by Docker ID or email
  - Requires owner or admin permissions

Tool: DOCKER_HUB_CREATE_WEBHOOK
  - Create a webhook on a repository for image push notifications
  - Two-step process: create webhook, then add hook URL
  - Requires admin permissions on the repository
```

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| JWT authentication | `DOCKER_HUB_CREATE_ORGANIZATION` requires JWT auth from `/v2/users/login` -- standard API tokens may not suffice. |
| Private repo limits | Creating private repos (`is_private: true`) requires a paid Docker Hub plan. |
| Org name constraints | Organization names must be lowercase, at least 2 characters, containing only letters, numbers, `.`, `_`, or `-`. |
| Webhook two-step | `DOCKER_HUB_CREATE_WEBHOOK` is a two-step process: first create the webhook with a name, then add a hook URL to it. |
| Pagination | All list endpoints use page-based pagination -- iterate pages until results are exhausted. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `DOCKER_HUB_LIST_ORGANIZATIONS` | List orgs the user belongs to |
| `DOCKER_HUB_CREATE_ORGANIZATION` | Create a new Docker Hub organization |
| `DOCKER_HUB_GET_ORGANIZATION` | Get org details and repository list |
| `DOCKER_HUB_CREATE_REPOSITORY` | Create a repository under a namespace |
| `DOCKER_HUB_LIST_REPOSITORIES` | List repos with filtering and sorting |
| `DOCKER_HUB_LIST_TEAMS` | List teams/groups within an org |
| `DOCKER_HUB_ADD_ORG_MEMBER` | Invite a user to an organization |
| `DOCKER_HUB_CREATE_WEBHOOK` | Create push-notification webhook on a repo |

---

*Powered by [Composio](https://composio.dev)*
