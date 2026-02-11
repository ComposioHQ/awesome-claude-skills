---
name: Zoho Desk Automation
description: "Zoho Desk automation via Rube MCP -- toolkit not currently available in Composio; no ZOHO_DESK_ tools found"
requires:
  mcp:
    - rube
---

# Zoho Desk Automation

> **Status: Toolkit Not Available** -- RUBE_SEARCH_TOOLS returned no `zoho_desk`-specific tools. The Zoho Desk toolkit is not currently available in Composio's tool catalog. Searches returned tools from unrelated helpdesk and CRM toolkits instead.

**Toolkit docs:** [composio.dev/toolkits/zoho_desk](https://composio.dev/toolkits/zoho_desk)

---

## Setup

1. Add the Rube MCP server to your environment: `https://rube.app/mcp`
2. Check availability by calling `RUBE_SEARCH_TOOLS` with Zoho Desk-related queries
3. If `ZOHO_DESK_*` tools appear in the future, connect via `RUBE_MANAGE_CONNECTIONS` with toolkit `zoho_desk`

---

## Current Status

As of the last tool discovery scan, no `ZOHO_DESK_*` tool slugs were returned by RUBE_SEARCH_TOOLS. Queries for Zoho Desk ticket management, contacts, agents, and departments all returned tools from other toolkits:

- Ticket creation queries returned **Freshdesk** (`FRESHDESK_CREATE_TICKET`), **HubSpot** (`HUBSPOT_CREATE_TICKET`), and **Zendesk** (`ZENDESK_CREATE_ZENDESK_TICKET`) tools
- Contact listing queries returned **Zoho Invoice** (`ZOHO_INVOICE_LIST_CONTACTS`) tools
- Agent/department queries returned **Zoho CRM** (`ZOHO_GET_ZOHO_USERS`) tools

This indicates the `zoho_desk` toolkit either has no tools registered or is not yet integrated into the Composio platform.

---

## Alternatives

If you need helpdesk and support ticket automation, consider these available toolkits:

| Need | Alternative Toolkit | Example Tools |
|------|-------------------|---------------|
| Ticket management | Freshdesk | `FRESHDESK_CREATE_TICKET`, `FRESHDESK_UPDATE_TICKET` |
| Ticket management | Zendesk | `ZENDESK_CREATE_ZENDESK_TICKET` |
| Ticket management | HubSpot | `HUBSPOT_CREATE_TICKET`, `HUBSPOT_LIST_TICKETS` |
| CRM records | Zoho CRM | `ZOHO_CREATE_ZOHO_RECORD`, `ZOHO_GET_ZOHO_USERS` |
| Contact management | Zoho Invoice | `ZOHO_INVOICE_LIST_CONTACTS` |

---

## When Tools Become Available

Once Zoho Desk tools are added to Composio, this skill should be updated with real tool slugs, schemas, and pitfalls following the same pattern as other automation skills in this collection.

---

*Powered by [Composio](https://composio.dev)*
