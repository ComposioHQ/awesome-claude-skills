# Billing toolset

Balance, usage, transactions, invoice payments, billing recovery, and referrals. Connect only this group with `https://app.famulor.io/mcp?toolsets=billing`.

This 2026-08-23 snapshot covers all 7 tools assigned to `billing` in the canonical 282-tool registry. The live MCP `tools/list` response is authoritative for arguments, current availability, annotations, and plan or role gating. Never invent fields from this catalog.

| Tool | Effect | Accepted scope | Execution | Purpose snapshot |
| --- | --- | --- | --- | --- |
| `create_billing_portal_link` | Write/action | `billing:read or calls:read` | Immediate | Create a short-lived first-party link for viewing invoices, updating payment methods, and managing cancellation. Plan changes remain available only in the application. |
| `create_invoice_payment_link` | Write/action | `billing:read or calls:read` | Immediate | Create a short-lived first-party link for paying the workspace's outstanding subscription invoice. The link contains no payment-provider or internal resource identifiers. |
| `get_balance` | Read | `billing:read or calls:read` | Immediate | Get the workspace's current minutes and credits balance plus a customer-facing summary of the active plan, included minutes, and additional usage price in the resolved presentation currency. |
| `get_referrals` | Read | `billing:read or calls:read` | Immediate | Get the workspace Refer and Earn share link, reward amounts, and referral history. Only available on the main platform. Friend emails are masked. Required scope: billing:read or calls:read. |
| `get_tool_usage` | Read | `assistants:read` | Immediate | Show which assistants currently reference a central tool. |
| `get_usage_summary` | Read | `calls:read` | Immediate | Monthly call-minute usage of the account for the last months. Returns minutes and call-record counts per month plus totals. For the credit balance and plan details use get_balance; for individual charges use list_transactions. |
| `list_transactions` | Read | `billing:read or calls:read` | Immediate | List the workspace balance ledger, newest first. Notes are customer-facing descriptions such as Credit top-up, Automatic top-up or Plan payment; payment-provider and internal reconciliation references are never returned. |
