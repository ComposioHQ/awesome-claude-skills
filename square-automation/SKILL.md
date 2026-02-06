---
name: square-automation
description: "Automate Square tasks via Rube MCP (Composio): payments, orders, invoices, locations. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Square Automation via Rube MCP

Automate Square payment processing, order management, and invoicing through Composio's Square toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Square connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `square`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `square`
3. If connection is not ACTIVE, follow the returned auth link to complete Square OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List and Monitor Payments

**When to use**: User wants to view payment history or check payment status

**Tool sequence**:
1. `SQUARE_LIST_PAYMENTS` - Retrieve payments with optional filters [Required]
2. `SQUARE_CANCEL_PAYMENT` - Cancel a pending payment if needed [Optional]

**Key parameters**:
- `begin_time` / `end_time`: RFC 3339 timestamps for date range filtering
- `sort_order`: 'ASC' or 'DESC' for chronological ordering
- `cursor`: Pagination cursor from previous response
- `location_id`: Filter payments by specific location

**Pitfalls**:
- Timestamps must be RFC 3339 format (e.g., '2024-01-01T00:00:00Z')
- Pagination required for large result sets; follow `cursor` until absent
- Only pending payments can be cancelled; completed payments require refunds
- `SQUARE_CANCEL_PAYMENT` requires exact `payment_id` from list results

### 2. Search and Manage Orders

**When to use**: User wants to find orders by criteria or update order details

**Tool sequence**:
1. `SQUARE_LIST_LOCATIONS` - Get location IDs for filtering [Prerequisite]
2. `SQUARE_SEARCH_ORDERS` - Search orders with filters [Required]
3. `SQUARE_RETRIEVE_ORDER` - Get full details of a specific order [Optional]
4. `SQUARE_UPDATE_ORDER` - Modify order state or details [Optional]

**Key parameters**:
- `location_ids`: Array of location IDs to search within (required for search)
- `query`: Search filter object with date ranges, states, fulfillment types
- `order_id`: Specific order ID for retrieve/update operations
- `cursor`: Pagination cursor for search results

**Pitfalls**:
- `location_ids` is required for SEARCH_ORDERS; get IDs from LIST_LOCATIONS first
- Order states include: OPEN, COMPLETED, CANCELED, DRAFT
- UPDATE_ORDER requires the current `version` field to prevent conflicts
- Search results are paginated; follow `cursor` until absent

### 3. Manage Locations

**When to use**: User wants to view business locations or get location details

**Tool sequence**:
1. `SQUARE_LIST_LOCATIONS` - List all business locations [Required]

**Key parameters**:
- No required parameters; returns all accessible locations
- Response includes `id`, `name`, `address`, `status`, `timezone`

**Pitfalls**:
- Location IDs are required for most other Square operations (orders, payments)
- Always cache location IDs after first retrieval to avoid redundant calls
- Inactive locations may still appear in results; check `status` field

### 4. Invoice Management

**When to use**: User wants to list, view, or cancel invoices

**Tool sequence**:
1. `SQUARE_LIST_LOCATIONS` - Get location ID for filtering [Prerequisite]
2. `SQUARE_LIST_INVOICES` - List invoices for a location [Required]
3. `SQUARE_GET_INVOICE` - Get detailed invoice information [Optional]
4. `SQUARE_CANCEL_INVOICE` - Cancel a scheduled or unpaid invoice [Optional]

**Key parameters**:
- `location_id`: Required for listing invoices
- `invoice_id`: Required for get/cancel operations
- `cursor`: Pagination cursor for list results
- `limit`: Number of results per page

**Pitfalls**:
- `location_id` is required for LIST_INVOICES; resolve via LIST_LOCATIONS first
- Only SCHEDULED, UNPAID, or PARTIALLY_PAID invoices can be cancelled
- CANCEL_INVOICE requires the invoice `version` to prevent race conditions
- Cancelled invoices cannot be uncancelled

## Common Patterns

### ID Resolution

**Location name -> Location ID**:
```
1. Call SQUARE_LIST_LOCATIONS
2. Find location by name in response
3. Extract id field (e.g., 'L1234ABCD')
```

**Order lookup**:
```
1. Call SQUARE_SEARCH_ORDERS with location_ids and query filters
2. Extract order_id from results
3. Use order_id for RETRIEVE_ORDER or UPDATE_ORDER
```

### Pagination

- Check response for `cursor` field
- Pass cursor value in next request's `cursor` parameter
- Continue until `cursor` is absent or empty
- Use `limit` to control page size

### Date Range Filtering

- Use RFC 3339 format: `2024-01-01T00:00:00Z`
- For payments: `begin_time` and `end_time` parameters
- For orders: Use query filter with date_time_filter
- All timestamps are in UTC

## Known Pitfalls

**ID Formats**:
- Location IDs are alphanumeric strings (e.g., 'L1234ABCD')
- Payment IDs and Order IDs are longer alphanumeric strings
- Always resolve location names to IDs before other operations

**Versioning**:
- UPDATE_ORDER and CANCEL_INVOICE require current `version` field
- Fetch the resource first to get its current version
- Version mismatch returns a 409 Conflict error

**Rate Limits**:
- Square API has per-endpoint rate limits
- Implement backoff for bulk operations
- Pagination should include brief delays for large datasets

**Response Parsing**:
- Responses may nest data under `data` key
- Money amounts are in smallest currency unit (cents for USD)
- Parse defensively with fallbacks for optional fields

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List payments | SQUARE_LIST_PAYMENTS | begin_time, end_time, location_id, cursor |
| Cancel payment | SQUARE_CANCEL_PAYMENT | payment_id |
| Search orders | SQUARE_SEARCH_ORDERS | location_ids, query, cursor |
| Get order | SQUARE_RETRIEVE_ORDER | order_id |
| Update order | SQUARE_UPDATE_ORDER | order_id, version |
| List locations | SQUARE_LIST_LOCATIONS | (none) |
| List invoices | SQUARE_LIST_INVOICES | location_id, cursor |
| Get invoice | SQUARE_GET_INVOICE | invoice_id |
| Cancel invoice | SQUARE_CANCEL_INVOICE | invoice_id, version |
