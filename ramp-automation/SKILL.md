---
name: Ramp Automation
description: "Ramp Automation: manage corporate card transactions, reimbursements, users, and expense tracking via the Ramp platform"
requires:
  mcp: [rube]
---

# Ramp Automation

Automate Ramp corporate finance operations including retrieving transactions, managing reimbursements, searching expenses, viewing card details, and listing users for expense management and accounting workflows.

**Toolkit docs:** [composio.dev/toolkits/ramp](https://composio.dev/toolkits/ramp)

---

## Setup

This skill requires the **Rube MCP server** connected at `https://rube.app/mcp`.

Before executing any tools, ensure an active connection exists for the `ramp` toolkit. If no connection is active, initiate one via `RUBE_MANAGE_CONNECTIONS`.

---

## Core Workflows

### 1. List All Transactions

Retrieve all corporate card transactions with comprehensive filtering options.

**Tool:** `RAMP_GET_ALL_TRANSACTIONS`

**Key Parameters:**
- `from_date` -- Transactions after this date (ISO 8601 datetime)
- `to_date` -- Transactions before this date (ISO 8601 datetime, default: today)
- `user_id` -- Filter by user UUID
- `card_id` -- Filter by physical card UUID
- `department_id` -- Filter by department UUID
- `merchant_id` -- Filter by merchant UUID
- `entity_id` -- Filter by business entity UUID
- `min_amount` / `max_amount` -- Amount range filter (USD)
- `state` -- Transaction state; set to `"ALL"` to include declined transactions
- `approval_status` -- Filter by approval status
- `sync_status` -- Filter by ERP sync status (supersedes `sync_ready` and `has_no_sync_commits`)
- `has_no_sync_commits` -- `true` for unsynced transactions
- `sync_ready` -- `true` for transactions ready to sync to ERP
- `requires_memo` -- `true` for transactions missing required memos
- `include_merchant_data` -- `true` to include full purchase data from merchant
- `page_size` -- Results per page (2--100, default: 20)
- `start` -- Pagination cursor: ID of last entity from previous page
- `order_by_date_desc` / `order_by_date_asc` -- Sort by date
- `order_by_amount_desc` / `order_by_amount_asc` -- Sort by amount

**Example:**
```
Tool: RAMP_GET_ALL_TRANSACTIONS
Arguments:
  from_date: "2026-02-01T00:00:00Z"
  to_date: "2026-02-11T23:59:59Z"
  page_size: 50
  order_by_date_desc: true
```

---

### 2. Search Transactions

Search transactions by merchant name, memo, or other transaction details.

**Tool:** `RAMP_SEARCH_TRANSACTIONS`

**Key Parameters:**
- `query` (required) -- Search text for merchant name, memo, or other details
- All filter parameters from `RAMP_GET_ALL_TRANSACTIONS` are also available

**Example:**
```
Tool: RAMP_SEARCH_TRANSACTIONS
Arguments:
  query: "AWS"
  from_date: "2026-01-01T00:00:00Z"
  page_size: 25
```

---

### 3. Get Transaction Details

Retrieve complete details of a specific transaction including merchant details, receipts, accounting codes, and dispute information.

**Tool:** `RAMP_GET_TRANSACTION`

**Key Parameters:**
- `transaction_id` (required) -- ID of the transaction

**Example:**
```
Tool: RAMP_GET_TRANSACTION
Arguments:
  transaction_id: "txn_abc123def456"
```

---

### 4. Manage Reimbursements

List and retrieve reimbursement records for approval workflows and expense analysis.

**Tools:**
- `RAMP_LIST_REIMBURSEMENTS` -- List reimbursements with filtering
- `RAMP_GET_REIMBURSEMENT` -- Get complete details of a specific reimbursement

**Key Parameters for `RAMP_LIST_REIMBURSEMENTS`:**
- `user_id` -- Filter by employee UUID
- `entity_id` -- Filter by business entity UUID
- `from_date` / `to_date` -- Date range for creation date
- `from_submitted_at` / `to_submitted_at` -- Date range for submission date
- `from_transaction_date` / `to_transaction_date` -- Underlying transaction date range
- `awaiting_approval_by_user_id` -- Filter for reimbursements pending a specific approver
- `sync_status` -- Filter by ERP sync status
- `has_no_sync_commits` -- `true` for unsynced reimbursements
- `sync_ready` -- `true` for reimbursements ready to sync
- `direction` -- `"BUSINESS_TO_USER"` (default) or `"USER_TO_BUSINESS"` (repayments)
- `page_size` -- Results per page (2--100, default: 20)
- `start` -- Pagination cursor

**Example:**
```
Tool: RAMP_LIST_REIMBURSEMENTS
Arguments:
  from_date: "2026-02-01T00:00:00Z"
  sync_ready: true
  page_size: 50
```

---

### 5. List Users and Get My Transactions

View organization users and personal transaction history.

**Tools:**
- `RAMP_LIST_USERS` -- List users with filtering by department, role, location, entity
- `RAMP_GET_MY_TRANSACTIONS` -- Get transactions for the authenticated user

**Key Parameters for `RAMP_LIST_USERS`:**
- `department_id` -- Filter by department UUID
- `role` -- Filter by user role
- `email` -- Filter by email address
- `employee_id` -- Filter by employee ID
- `entity_id` -- Filter by business entity UUID
- `location_id` -- Filter by location UUID
- `page_size` -- Results per page (2--100, default: 20)

**Example:**
```
Tool: RAMP_LIST_USERS
Arguments:
  role: "ADMIN"
  page_size: 50
```

---

### 6. View Card Details and Accounting Fields

Retrieve card information and custom accounting field configurations.

**Tools:**
- `RAMP_GET_CARD` -- Get detailed card information (spending limits, cardholder, fulfillment status)
- `RAMP_FETCH_CUSTOM_ACCOUNTING_FIELD` -- Fetch custom accounting field definitions

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| **Pagination required** | All list endpoints return paginated results. Use the `start` parameter with the ID of the last entity from the previous page to iterate. |
| **Date format** | All date parameters must be ISO 8601 datetime format (e.g., `"2026-02-11T00:00:00Z"`). Plain date strings will fail. |
| **sync_status priority** | When `sync_status` is set, it supersedes both `has_no_sync_commits` and `sync_ready` parameters. |
| **Amount filters in USD** | `min_amount` and `max_amount` are in USD. Ensure correct currency context when filtering. |
| **state=ALL for declined** | By default, declined transactions are excluded. Set `state: "ALL"` to include them in results. |
| **page_size bounds** | Must be between 2 and 100. Default is 20. Values outside this range cause errors. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `RAMP_GET_ALL_TRANSACTIONS` | List all transactions with filtering |
| `RAMP_SEARCH_TRANSACTIONS` | Search transactions by text query |
| `RAMP_GET_TRANSACTION` | Get details of a specific transaction |
| `RAMP_GET_MY_TRANSACTIONS` | Get authenticated user's transactions |
| `RAMP_LIST_REIMBURSEMENTS` | List reimbursements with filtering |
| `RAMP_GET_REIMBURSEMENT` | Get details of a specific reimbursement |
| `RAMP_LIST_USERS` | List organization users |
| `RAMP_GET_CARD` | Get card details |
| `RAMP_FETCH_CUSTOM_ACCOUNTING_FIELD` | Fetch custom accounting field config |

---

*Powered by [Composio](https://composio.dev)*
