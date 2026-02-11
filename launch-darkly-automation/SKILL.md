---
name: LaunchDarkly Automation
description: "Automate LaunchDarkly feature flag management -- list projects and environments, create and delete trigger workflows, and track code references via the Composio MCP integration."
requires:
  mcp:
    - rube
---

# LaunchDarkly Automation

Automate your LaunchDarkly feature flag workflows -- enumerate projects and environments, create webhook-driven flag triggers, manage trigger lifecycle, and audit code references across repositories.

**Toolkit docs:** [composio.dev/toolkits/launch_darkly](https://composio.dev/toolkits/launch_darkly)

---

## Setup

1. Add the Composio MCP server to your client: `https://rube.app/mcp`
2. Connect your LaunchDarkly account when prompted (API key authentication)
3. Start using the workflows below

---

## Core Workflows

### 1. List Projects

Use `LAUNCH_DARKLY_LIST_PROJECTS` to discover all projects and their keys for subsequent operations.

```
Tool: LAUNCH_DARKLY_LIST_PROJECTS
Inputs:
  - filter: string (e.g., "query:myproject" or "keys:proj1,proj2" or "tags:mytag")
  - expand: string (e.g., "environments" to include env list per project)
  - limit: integer (default 20)
  - offset: integer (pagination start index)
  - sort: string (e.g., "name" or "-name" for descending)
```

### 2. Get Environments for a Project

Use `LAUNCH_DARKLY_GET_ENVIRONMENTS` to list all environments within a project (production, staging, test, etc.).

```
Tool: LAUNCH_DARKLY_GET_ENVIRONMENTS
Inputs:
  - project_key: string (required) -- e.g., "my-project", "default"
  - filter: string (e.g., "query:production")
  - limit: integer (default 20)
  - offset: integer (pagination)
  - sort: string (e.g., "name" or "-name")
```

### 3. Create a Flag Trigger Workflow

Use `LAUNCH_DARKLY_CREATE_TRIGGER_WORKFLOW` to set up automated flag toggles triggered by external events (webhooks, Datadog alerts, etc.).

```
Tool: LAUNCH_DARKLY_CREATE_TRIGGER_WORKFLOW
Inputs:
  - project_key: string (required)
  - feature_flag_key: string (required) -- e.g., "new-feature", "enable-dark-mode"
  - environment_key: string (required) -- e.g., "production", "staging"
  - integration_key: string (default "generic-trigger") -- or "datadog", "honeycomb", "dynatrace"
  - instructions: array of objects (optional):
      - kind: "flag_action" (fixed)
      - action: "turnFlagOn" | "turnFlagOff"
  - comment: string (optional) -- description of the trigger purpose
```

The trigger generates a unique webhook URL that can be called to execute the configured flag action.

### 4. Delete a Flag Trigger Workflow

Use `LAUNCH_DARKLY_DELETE_TRIGGER_WORKFLOW` to permanently remove a trigger and its URL.

```
Tool: LAUNCH_DARKLY_DELETE_TRIGGER_WORKFLOW
Inputs:
  - project_key: string (required)
  - feature_flag_key: string (required)
  - environment_key: string (required)
  - id: string (required) -- the trigger ID returned during creation
```

**Warning:** Deletion is irreversible. The trigger and its URL cannot be recovered.

### 5. List Code Reference Repositories

Use `LAUNCH_DARKLY_LIST_CODE_REFERENCE_REPOSITORIES` to track where feature flags are used in your codebase.

```
Tool: LAUNCH_DARKLY_LIST_CODE_REFERENCE_REPOSITORIES
Inputs:
  - projKey: string (optional) -- filter by project key
  - flagKey: string (optional) -- filter by feature flag key
  - withBranches: string (any value to include branch data)
  - withReferencesForDefaultBranch: string (any value to include code refs for default branch)
```

**Note:** Code references is an Enterprise feature requiring `code-reference-repository` write permissions.

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| Project key discovery | Always use `LAUNCH_DARKLY_LIST_PROJECTS` first to find valid project keys before calling other tools. |
| Environment key format | Environment keys are lowercase slugs (e.g., "production", "test"), not display names. |
| Trigger deletion is permanent | Once deleted via `LAUNCH_DARKLY_DELETE_TRIGGER_WORKFLOW`, the trigger URL is unrecoverable. |
| Enterprise-only code refs | `LAUNCH_DARKLY_LIST_CODE_REFERENCE_REPOSITORIES` requires Enterprise plan and write permissions. |
| Trigger instructions format | Each instruction object requires `kind: "flag_action"` (fixed constant) and `action` as either `turnFlagOn` or `turnFlagOff`. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `LAUNCH_DARKLY_LIST_PROJECTS` | List all projects with filtering and pagination |
| `LAUNCH_DARKLY_GET_ENVIRONMENTS` | List environments within a project |
| `LAUNCH_DARKLY_CREATE_TRIGGER_WORKFLOW` | Create a webhook-driven flag trigger |
| `LAUNCH_DARKLY_DELETE_TRIGGER_WORKFLOW` | Permanently delete a flag trigger |
| `LAUNCH_DARKLY_LIST_CODE_REFERENCE_REPOSITORIES` | List repos with code references to flags |

---

*Powered by [Composio](https://composio.dev)*
