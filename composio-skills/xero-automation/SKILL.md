---
name: Xero Automation
description: "Xero Automation: manage invoices, contacts, payments, bank transactions, and accounts in Xero for cloud-based bookkeeping"
requires:
  mcp: [rube]
---

# Xero Automation

Automate Xero accounting operations including managing invoices, contacts, payments, bank transactions, and chart of accounts for small business bookkeeping.

**Toolkit docs:** [composio.dev/toolkits/xero](https://composio.dev/toolkits/xero)

---

## Setup

This skill requires the **Rube MCP server** connected at `https://rube.app/mcp`.

Before executing any tools, ensure an active connection exists for the `xero` toolkit. If no connection is active, initiate one via `RUBE_MANAGE_CONNECTIONS`.

**Multi-tenant:** If you manage multiple Xero organizations, first call `XERO_GET_CONNECTIONS` to list active tenants and obtain the correct `tenant_id` for subsequent calls.

---

## Core Workflows

### 1. List and Filter Invoices

Retrieve invoices with filtering by status, contact, date range, and pagination.

**Tool:** `XERO_LIST_INVOICES`

**Key Parameters:**
- `Statuses` -- Comma-separated status filter: `"DRAFT"`, `"SUBMITTED"`, `"AUTHORISED"`, `"PAID"`
- `ContactIDs` -- Comma-separated Contact IDs to filter by
- `InvoiceIDs` -- Comma-separated Invoice IDs to filter by
- `where` -- OData-style filter, e.g., `"Status==\"AUTHORISED\" AND Total>100"`
- `order` -- Sort expression, e.g., `"Date DESC"`, `"InvoiceNumber ASC"`
- `page` -- Page number for pagination
- `If-Modified-Since` -- UTC timestamp; returns only invoices modified since this date
- `tenant_id` -- Xero organization ID (uses first tenant if omitted)

**Example:**
```
Tool: XERO_LIST_INVOICES
Arguments:
  Statuses: "AUTHORISED,PAID"
  order: "Date DESC"
  page: 1
```

---

### 2. Manage Contacts

Retrieve and search contacts for use in invoices and transactions.

**Tool:** `XERO_GET_CONTACTS`

**Key Parameters:**
- `searchTerm` -- Case-insensitive search across Name, FirstName, LastName, Email, ContactNumber
- `ContactID` -- Fetch a single contact by ID
- `where` -- OData filter, e.g., `"ContactStatus==\"ACTIVE\""`
- `page`, `pageSize` -- Pagination controls
- `order` -- Sort, e.g., `"UpdatedDateUTC DESC"`
- `includeArchived` -- Include archived contacts when `true`
- `summaryOnly` -- Lightweight response when `true`

**Example:**
```
Tool: XERO_GET_CONTACTS
Arguments:
  searchTerm: "acme"
  page: 1
  pageSize: 25
```

> **Note:** On high-volume accounts, some `where` filters (e.g., `IsCustomer`, `IsSupplier`) may be rejected by Xero. Fall back to `searchTerm` or pagination.

---

### 3. Create Payments

Link an invoice to a bank account by creating a payment record.

**Tool:** `XERO_CREATE_PAYMENT`

**Key Parameters:**
- `InvoiceID` (required) -- Xero Invoice ID the payment applies to
- `AccountID` (required) -- Bank account ID for the payment
- `Amount` (required) -- Payment amount (number)
- `Date` -- Payment date in `YYYY-MM-DD` format
- `Reference` -- Payment reference or description
- `CurrencyRate` -- Exchange rate for foreign currency payments

**Example:**
```
Tool: XERO_CREATE_PAYMENT
Arguments:
  InvoiceID: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  AccountID: "b2c3d4e5-f6a7-8901-bcde-f12345678901"
  Amount: 1500.00
  Date: "2026-02-11"
  Reference: "Payment for INV-0042"
```

---

### 4. Create Bank Transactions

Record spend (payments out) or receive (money in) bank transactions.

**Tool:** `XERO_CREATE_BANK_TRANSACTION`

**Key Parameters:**
- `Type` (required) -- `"SPEND"` (payment out) or `"RECEIVE"` (money in)
- `ContactID` (required) -- Xero Contact ID
- `BankAccountCode` (required) -- Bank account code from chart of accounts
- `LineItems` (required) -- Array of line items, each with:
  - `Description` (required) -- Line item description
  - `UnitAmount` (required) -- Unit price
  - `AccountCode` (required) -- Account code for categorization
  - `Quantity` -- Quantity (default 1)
  - `TaxType` -- Tax type: `"OUTPUT"`, `"INPUT"`, `"NONE"`
- `Date` -- Transaction date in `YYYY-MM-DD` format
- `Reference` -- Transaction reference
- `Status` -- `"AUTHORISED"` or `"DELETED"`
- `CurrencyCode` -- e.g., `"USD"`, `"EUR"`

**Example:**
```
Tool: XERO_CREATE_BANK_TRANSACTION
Arguments:
  Type: "SPEND"
  ContactID: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  BankAccountCode: "090"
  LineItems: [
    {
      "Description": "Office supplies",
      "UnitAmount": 75.00,
      "AccountCode": "429",
      "Quantity": 1,
      "TaxType": "INPUT"
    }
  ]
  Date: "2026-02-11"
  Reference: "Feb office supplies"
```

---

### 5. List Payments and Bank Transactions

Review existing payments and bank transaction history.

**Tools:**
- `XERO_LIST_PAYMENTS` -- List payments linking invoices to bank transactions
- `XERO_LIST_BANK_TRANSACTIONS` -- List spend/receive bank transactions

**Common Parameters:**
- `where` -- OData filter, e.g., `"Status==\"AUTHORISED\""`
- `order` -- Sort expression, e.g., `"Date DESC"`
- `page` -- Page number for pagination
- `If-Modified-Since` -- Incremental updates since timestamp
- `tenant_id` -- Organization ID

---

### 6. View Chart of Accounts and Connections

**Tools:**
- `XERO_LIST_ACCOUNTS` -- Retrieve all account codes for categorizing transactions
- `XERO_GET_CONNECTIONS` -- List active Xero tenant connections
- `XERO_LIST_ATTACHMENTS` -- List attachments on an entity (invoice, contact, etc.)

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| **Multi-tenant routing** | If `tenant_id` is omitted, the first connected tenant is used. Always verify the correct tenant with `XERO_GET_CONNECTIONS` when managing multiple organizations. |
| **High-volume filter rejection** | On large accounts, some `where` filters like `IsCustomer`/`IsSupplier` may be rejected. Fall back to `searchTerm` with pagination. |
| **OData filter syntax** | Use double-equals (`==`) in OData filters, e.g., `Status==\"AUTHORISED\"`. Single `=` causes errors. |
| **Pagination required** | Most list endpoints paginate results. Always check for additional pages and continue fetching until complete. |
| **Date format** | All dates must be in `YYYY-MM-DD` format. Timestamps for `If-Modified-Since` must be full ISO 8601 UTC datetime. |
| **Bank account codes** | `BankAccountCode` in bank transactions must match a valid code from the chart of accounts. Use `XERO_LIST_ACCOUNTS` to discover valid codes. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `XERO_LIST_INVOICES` | List invoices with filtering and pagination |
| `XERO_GET_CONTACTS` | Retrieve and search contacts |
| `XERO_CREATE_PAYMENT` | Create a payment linking invoice to bank account |
| `XERO_CREATE_BANK_TRANSACTION` | Record a spend or receive bank transaction |
| `XERO_LIST_PAYMENTS` | List payment records |
| `XERO_LIST_BANK_TRANSACTIONS` | List bank transactions |
| `XERO_LIST_ACCOUNTS` | Retrieve chart of accounts |
| `XERO_GET_CONNECTIONS` | List active Xero tenant connections |
| `XERO_LIST_ATTACHMENTS` | List attachments on an entity |

---

*Powered by [Composio](https://composio.dev)*
