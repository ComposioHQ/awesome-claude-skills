# Migration toolset

Preview and import of supported Famulor 1.0 resources. Connect only this group with `https://app.famulor.io/mcp?toolsets=migration`.

This 2026-08-23 snapshot covers all 2 tools assigned to `migration` in the canonical 282-tool registry. The live MCP `tools/list` response is authoritative for arguments, current availability, annotations, and plan or role gating. Never invent fields from this catalog.

| Tool | Effect | Accepted scope | Execution | Purpose snapshot |
| --- | --- | --- | --- | --- |
| `import_famulor_1_data` | Write/action | `assistants:write or knowledge:write or campaigns:write or automations:write or calls:write` | Immediate | Import selected Famulor 1.0 resources into this workspace. Campaigns and automations are always created as inactive drafts; unsupported automation steps become visible review nodes. Preview first. |
| `preview_famulor_1_migration` | Read | `assistants:read or campaigns:read or automations:read or calls:read` | Immediate | Read a Famulor 1.0 account and return a migration preview with mappings and warnings. The source API key is used only for this request and is never persisted or returned. |
