---
name: Coinbase Automation
description: "Coinbase Automation: list and manage cryptocurrency wallets, accounts, and portfolio data via Coinbase CDP SDK"
requires:
  mcp: [rube]
---

# Coinbase Automation

Automate Coinbase operations including listing cryptocurrency wallets, paginating through wallet collections, and retrieving portfolio data.

**Toolkit docs:** [composio.dev/toolkits/coinbase](https://composio.dev/toolkits/coinbase)

---

## Setup

This skill requires the **Rube MCP server** connected at `https://rube.app/mcp`.

Before executing any tools, ensure an active connection exists for the `coinbase` toolkit. If no connection is active, initiate one via `RUBE_MANAGE_CONNECTIONS`.

---

## Core Workflows

### 1. List All Wallets

Retrieve all wallets from Coinbase with pagination support.

**Tool:** `COINBASE_LIST_WALLETS`

**Key Parameters:**
- `limit` -- Results per page (1--100, default: 25)
- `order` -- Sort order: `"asc"` (ascending) or `"desc"` (descending, default)
- `starting_after` -- Cursor for forward pagination: ID of the last wallet from the previous page
- `ending_before` -- Cursor for backward pagination: ID of the first wallet from the previous page

**Example (first page):**
```
Tool: COINBASE_LIST_WALLETS
Arguments:
  limit: 50
  order: "desc"
```

**Example (next page):**
```
Tool: COINBASE_LIST_WALLETS
Arguments:
  limit: 50
  order: "desc"
  starting_after: "wallet_abc123_last_id_from_prev_page"
```

---

### 2. Paginate Through All Wallets

To retrieve a complete wallet inventory, iterate through pages.

**Steps:**
1. Call `COINBASE_LIST_WALLETS` with desired `limit` and `order`
2. If the response contains more results, note the ID of the last wallet returned
3. Call `COINBASE_LIST_WALLETS` again with `starting_after` set to that last wallet ID
4. Repeat until no more results are returned

---

### 3. Audit Wallet Portfolio

Retrieve wallet data for portfolio analysis and reporting.

**Steps:**
1. Call `COINBASE_LIST_WALLETS` with `limit: 100` to maximize per-page results
2. Collect wallet balances and metadata from each page
3. Aggregate data across all pages for a complete portfolio view

---

### 4. Monitor Wallet Changes

Periodically list wallets to detect new additions or changes.

**Steps:**
1. Call `COINBASE_LIST_WALLETS` with `order: "desc"` to get newest wallets first
2. Compare against previously stored wallet IDs to identify new entries
3. Schedule periodic checks for continuous monitoring

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| **Pagination required** | Wallet lists are paginated. Always check for additional pages using cursor-based pagination (`starting_after`/`ending_before`). |
| **Limit bounds** | The `limit` parameter accepts 1--100. Values outside this range cause errors. Default is 25. |
| **Cursor-based pagination** | Uses wallet IDs as cursors, not page numbers. You must extract the last/first wallet ID from each response to navigate pages. |
| **CDP SDK scope** | This tool uses the Coinbase CDP SDK. Available operations depend on the API key permissions granted during connection setup. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `COINBASE_LIST_WALLETS` | List cryptocurrency wallets with pagination |

---

*Powered by [Composio](https://composio.dev)*
