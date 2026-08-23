# Platform toolset

Authorized white-label reseller customer administration, delegated tokens, and credit transfers. Connect only this group with `https://app.famulor.io/mcp?toolsets=platform`.

This 2026-08-23 snapshot covers all 6 tools assigned to `platform` in the canonical 282-tool registry. The live MCP `tools/list` response is authoritative for arguments, current availability, annotations, and plan or role gating. Never invent fields from this catalog.

| Tool | Effect | Accepted scope | Execution | Purpose snapshot |
| --- | --- | --- | --- | --- |
| `create_platform_user_token` | Write/action | `platform:write` | Immediate | Mint an API key for one of your platform's customers, identified by user_id or email. This is the CUSTOMER's own platform credential (created_by = the customer, not you) — it stops working automatically if the customer ever leaves their workspace. The plaintext key is returned EXACTLY ONCE and is never shown or stored again; hand it to the customer or store it immediately. |
| `get_platform_user` | Read | `platform:read` | Immediate | Fetch a single platform customer's detail: profile, every workspace they have in your scope, and balances. |
| `list_platform_users` | Read | `platform:read` | Immediate | List your platform's end-user customers: a reseller's own child workspaces, or — for a platform admin — every platform root workspace (never another reseller's customers). Supports limit/offset pagination and a name/email search (q). |
| `logout_platform_user` | Delete/destructive | `platform:write` | Immediate | Revoke every active API key and OAuth token belonging to one of your platform's customers, across all of their workspaces in your scope (never a workspace under a different reseller). Idempotent — logging out an already-logged-out customer returns zero counts. |
| `register_platform_user` | Write/action | `platform:write` | Immediate | Create a new customer account on your platform. mode 'invite' (default) emails an invite with no password required; mode 'password' requires an 8+ character password. Fails with a generic 'account already exists' error whether the email is already used inside or outside your scope (anti-enumeration). |
| `transfer_platform_credits` | Write/action | `platform:write` | Immediate | Move in-app service credits (usage units — never money) between your own workspace and a customer's workspace, identified by user_id or email. Positive credits grants from you to the customer; negative credits reclaims back from the customer. A reclaim fails with an error if the customer's wallet does not hold enough to cover it — balances never go below zero. |
