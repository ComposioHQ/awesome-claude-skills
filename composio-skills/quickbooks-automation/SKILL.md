---
name: QuickBooks Automation
description: "QuickBooks Automation: manage invoices, customers, accounts, and payments in QuickBooks Online for streamlined bookkeeping"
requires:
  mcp: [rube]
---

# QuickBooks Automation

Automate QuickBooks Online operations including creating invoices, managing customers, querying accounts, and listing invoices for financial reporting.

**Toolkit docs:** [composio.dev/toolkits/quickbooks](https://composio.dev/toolkits/quickbooks)

---

## Setup

This skill requires the **Rube MCP server** connected at `https://rube.app/mcp`.

Before executing any tools, ensure an active connection exists for the `quickbooks` toolkit. If no connection is active, initiate one via `RUBE_MANAGE_CONNECTIONS`.

---

## Core Workflows

### 1. Create an Invoice

Create a new invoice for a customer with line items.

**Tool:** `QUICKBOOKS_CREATE_INVOICE`

**Key Parameters:**
- `customer_id` (required) -- ID of the customer (CustomerRef.value)
- `lines` (required) -- Array of line item objects. Each must include:
  - `DetailType` -- e.g., `"SalesItemLineDetail"`
  - `Amount` -- Line item total
  - `SalesItemLineDetail` -- Object with `ItemRef` containing `value` (item ID)
- `minorversion` -- Optional API version parameter

**Example:**
```
Tool: QUICKBOOKS_CREATE_INVOICE
Arguments:
  customer_id: "21"
  lines: [
    {
      "DetailType": "SalesItemLineDetail",
      "Amount": 150.00,
      "SalesItemLineDetail": {
        "ItemRef": {"value": "1", "name": "Services"}
      }
    }
  ]
```

**Prerequisites:** Resolve the customer ID using `QUICKBOOKS_READ_CUSTOMER` or create one with `QUICKBOOKS_CREATE_CUSTOMER`. Resolve item/account IDs using `QUICKBOOKS_QUERY_ACCOUNT`.

---

### 2. Manage Customers

Create and read customer records.

**Tools:**
- `QUICKBOOKS_CREATE_CUSTOMER` -- Create a new customer
- `QUICKBOOKS_READ_CUSTOMER` -- Read a customer by ID

**Key Parameters for `QUICKBOOKS_CREATE_CUSTOMER`:**
- `display_name` -- Display name (must be unique across customers, vendors, employees; max 500 chars)
- `given_name` -- First name (max 100 chars)
- `family_name` -- Last name (max 100 chars)
- `middle_name` -- Middle name (max 100 chars)
- `title` -- Title, e.g., `"Mr."`, `"Dr."` (max 16 chars)
- `suffix` -- Name suffix, e.g., `"Jr."` (max 16 chars)

> At least one of `display_name`, `title`, `given_name`, `middle_name`, `family_name`, or `suffix` is required.

**Key Parameters for `QUICKBOOKS_READ_CUSTOMER`:**
- `customer_id` (required) -- ID of the customer to read

**Example:**
```
Tool: QUICKBOOKS_CREATE_CUSTOMER
Arguments:
  display_name: "Acme Corporation"
  given_name: "John"
  family_name: "Doe"
```

---

### 3. Query and Read Accounts

Retrieve account information for use in invoice line items and financial reporting.

**Tools:**
- `QUICKBOOKS_QUERY_ACCOUNT` -- Execute a query against accounts
- `QUICKBOOKS_READ_ACCOUNT` -- Read a specific account by ID

**Key Parameters for `QUICKBOOKS_QUERY_ACCOUNT`:**
- `query` (required) -- SQL-like query string, e.g., `"SELECT * FROM Account WHERE AccountType = 'Income'"`

**Example:**
```
Tool: QUICKBOOKS_QUERY_ACCOUNT
Arguments:
  query: "SELECT * FROM Account WHERE AccountType = 'Income' MAXRESULTS 10"
```

---

### 4. List and Filter Invoices

Retrieve invoices with optional pagination and filtering.

**Tool:** `QUICKBOOKS_LIST_INVOICES`

**Steps:**
1. Call `QUICKBOOKS_LIST_INVOICES` with pagination parameters
2. Use `start_position` and `max_results` to page through results
3. Filter by specific criteria as needed

---

## Recommended Execution Plan

1. **Resolve the customer** using `QUICKBOOKS_READ_CUSTOMER` (if you have a customer ID) or create one with `QUICKBOOKS_CREATE_CUSTOMER`
2. **Resolve item/revenue accounts** using `QUICKBOOKS_QUERY_ACCOUNT` and `QUICKBOOKS_READ_ACCOUNT` to get account or item IDs for invoice line items
3. **Create the invoice** using `QUICKBOOKS_CREATE_INVOICE` with the resolved `customer_id` and well-formed line items
4. **Verify creation** using `QUICKBOOKS_LIST_INVOICES` to locate the new invoice by ID or DocNumber

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| **Invalid references** | `QUICKBOOKS_CREATE_INVOICE` fails if `customer_id` or `ItemRef.value` point to non-existent or inactive records. Always resolve IDs first. |
| **Line item validation** | Incorrect `DetailType` or missing `SalesItemLineDetail` fields cause schema/validation errors during invoice creation. |
| **Pagination** | `QUICKBOOKS_LIST_INVOICES` uses `start_position` and `max_results`. Incomplete pagination settings can miss invoices in larger books. |
| **Sync tokens** | Any later edits require the latest `SyncToken` from a fresh invoice read. Stale sync tokens cause update rejections. |
| **Rate limits** | QuickBooks enforces per-minute and daily API caps. High-volume runs should include backoff to avoid throttling errors. |
| **DisplayName uniqueness** | Customer `display_name` must be unique across all Customer, Vendor, and Employee objects. Duplicates cause creation failures. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `QUICKBOOKS_CREATE_INVOICE` | Create a new invoice with line items |
| `QUICKBOOKS_READ_CUSTOMER` | Read a customer record by ID |
| `QUICKBOOKS_CREATE_CUSTOMER` | Create a new customer record |
| `QUICKBOOKS_QUERY_ACCOUNT` | Query accounts with SQL-like syntax |
| `QUICKBOOKS_READ_ACCOUNT` | Read a specific account by ID |
| `QUICKBOOKS_LIST_INVOICES` | List invoices with pagination |

---

*Powered by [Composio](https://composio.dev)*
