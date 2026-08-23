# Tasks toolset

Durable long-running exports, simulations, crawls, and campaign preparation. Connect only this group with `https://app.famulor.io/mcp?toolsets=tasks`.

This 2026-08-23 snapshot covers all 4 tools assigned to `tasks` in the canonical 282-tool registry. The live MCP `tools/list` response is authoritative for arguments, current availability, annotations, and plan or role gating. Never invent fields from this catalog.

| Tool | Effect | Accepted scope | Execution | Purpose snapshot |
| --- | --- | --- | --- | --- |
| `export_history_task` | Read | `calls:read` | required | Build a durable, private CSV export of workspace conversation history and return a short-lived download link. |
| `prepare_campaign_task` | Write/action | `campaigns:write or calls:write` | required | Validate and import a large audience into a paused campaign as a durable, cancellable preparation task. |
| `run_assistant_simulation_task` | Write/action | `assistants:write` | required | Run a durable assistant conversation simulation and return its provider-neutral test result when complete. |
| `run_knowledge_crawl_task` | Write/action | `knowledge:write or assistants:write` | required | Start a durable website knowledge crawl. The task can be polled, listed, or cancelled with the native MCP Tasks protocol. |
