# Automations toolset

Automations, CRM synchronization, external connections, routines, and run history. Connect only this group with `https://app.famulor.io/mcp?toolsets=automations`.

This 2026-08-23 snapshot covers all 28 tools assigned to `automations` in the canonical 282-tool registry. The live MCP `tools/list` response is authoritative for arguments, current availability, annotations, and plan or role gating. Never invent fields from this catalog.

| Tool | Effect | Accepted scope | Execution | Purpose snapshot |
| --- | --- | --- | --- | --- |
| `create_automation` | Write/action | `automations:write or calls:write` | Immediate | Create a native automation. For call.completed / call.variables, trigger.assistant_id is required before status=active. For call.variables, end the graph with variables.return. |
| `create_automation_connection` | Write/action | `automations:write or calls:write` | Immediate | Store a reusable workspace credential for an external CRM (HubSpot, HighLevel, Salesforce, Pipedrive, Close, Zoho, Attio, Keap, or Twenty), SMTP relay, or an MCP endpoint. `credentials` values are AES-256-GCM encrypted at rest. |
| `create_crm_sync` | Write/action | `automations:write or calls:write` | Immediate | Create a recurring CRM sync. Direction can import CRM records into Audience, push Audience contacts to the CRM, or both on the same schedule. Combined {{field}} expressions are import-only; outbound needs a 1:1 phone or email mapping. |
| `create_routine` | Write/action | `routines:write` | Immediate | Create a scheduled AI copilot routine: a prompt that runs unattended in the background on a schedule (or only on demand, for schedule_type 'manual'), billed like a normal copilot turn. |
| `delete_automation` | Delete/destructive | `automations:write or calls:write` | Immediate | Delete an automation and unbind any assistant webhook links. |
| `delete_automation_connection` | Delete/destructive | `automations:write or calls:write` | Immediate | Delete an automation connection. |
| `delete_crm_sync` | Delete/destructive | `automations:write or calls:write` | Immediate | Delete a CRM sync configuration and its memberships. Imported Audience contacts are kept. |
| `delete_routine` | Delete/destructive | `routines:write` | Immediate | Permanently delete a scheduled AI copilot routine. It stops running immediately; past run transcripts already on record are unaffected. This cannot be undone. |
| `discover_crm_sync` | Read | `automations:read or calls:read` | Immediate | Discover importable objects, fields, optional list/view/filter sources, and an optional read-only mapped preview without exposing credentials. |
| `get_automation` | Read | `automations:read or calls:read` | Immediate | Get one automation and recent runs. |
| `get_automation_connection` | Read | `automations:read or calls:read` | Immediate | Get one automation connection (secrets masked as '•••'). |
| `get_automation_platform` | Read | `automations:read or calls:read` | Immediate | Get the workspace's native automation platform entitlement, monthly run allowance, and usage. |
| `get_crm_sync` | Read | `automations:read or calls:read` | Immediate | Get one CRM sync and its recent durable run history. |
| `get_routine` | Read | `routines:read` | Immediate | Get one scheduled AI copilot routine. |
| `list_acuity_connections` | Read | `integrations:read or assistants:read` | Immediate | List Acuity Scheduling accounts connected to this workspace through OAuth. Tokens and secrets are never returned. |
| `list_automation_connections` | Read | `automations:read or calls:read` | Immediate | List workspace-scoped CRM / SMTP / MCP credentials that automation nodes can reference. Secrets are never returned; masked as '•••'. |
| `list_automations` | Read | `automations:read or calls:read` | Immediate | List native workspace automations (graph workflows). |
| `list_calendly_connections` | Read | `integrations:read or assistants:read` | Immediate | List Calendly accounts connected to this workspace through OAuth. Tokens and secrets are never returned. |
| `list_crm_syncs` | Read | `automations:read or calls:read` | Immediate | List CRM sync configurations and their current status. Provider credentials are never returned. |
| `list_routine_runs` | Read | `routines:read` | Immediate | List recent runs of one routine, most recent first — status, trigger, credits charged, and timing. |
| `list_routines` | Read | `routines:read` | Immediate | List this workspace's scheduled AI copilot routines: schedule, enabled state, next run, and the last run's status. |
| `run_crm_sync` | Write/action | `automations:write or calls:write` | Immediate | Queue a durable manual run for a CRM sync. |
| `run_routine` | Write/action | `routines:write` | Immediate | Trigger one routine right now as a background run, independent of its schedule. Starts an unattended AI copilot turn billed like a normal copilot turn, and returns immediately with the new run's id and status while it keeps executing in the background. |
| `trigger_automation` | Write/action | `automations:write or calls:write` | Immediate | Manually start an automation run with an optional JSON payload. |
| `update_automation` | Write/action | `automations:write or calls:write` | Immediate | Update name, status, trigger, graph, or tags of an automation. |
| `update_automation_connection` | Write/action | `automations:write or calls:write` | Immediate | Patch an automation connection. Sending '•••' for a secret keeps the stored value; omit to leave a field unchanged. |
| `update_crm_sync` | Write/action | `automations:write or calls:write` | Immediate | Update composed mapping, source, default phone country, interval, direction, outbound create, policies, or active/paused status. |
| `update_routine` | Write/action | `routines:write` | Immediate | Update a routine's name, prompt, schedule, timezone, or enabled state — only pass the fields that change. |
