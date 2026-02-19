---
name: Lemon Squeezy Automation
description: "Automate Lemon Squeezy store management -- products, orders, subscriptions, customers, discounts, and checkout tracking -- using natural language through the Composio MCP integration."
category: e-commerce
requires:
  mcp:
    - rube
---

# Lemon Squeezy Automation

Manage your Lemon Squeezy digital products business -- track orders, monitor subscriptions, analyze customers, review discounts, and audit checkouts -- all through natural language commands.

**Toolkit docs:** [composio.dev/toolkits/lemon_squeezy](https://composio.dev/toolkits/lemon_squeezy)

---

## Setup

1. Add the Composio MCP server to your client configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Lemon Squeezy account when prompted (API key authentication).
3. Start issuing natural language commands to manage your store.

---

## Core Workflows

### 1. Discover Stores and Products
List all stores to get store IDs, then retrieve products and variants for a specific store.

**Tools:** `LEMON_SQUEEZY_LIST_ALL_STORES`, `LEMON_SQUEEZY_LIST_ALL_PRODUCTS`, `LEMON_SQUEEZY_LIST_ALL_VARIANTS`

**Example prompt:**
> "List all my Lemon Squeezy stores and their products"

**Key parameters:**
- `LEMON_SQUEEZY_LIST_ALL_STORES` -- No parameters required
- `LEMON_SQUEEZY_LIST_ALL_PRODUCTS` -- Filter by `filter[store_id]`
- `LEMON_SQUEEZY_LIST_ALL_VARIANTS` -- Filter by `filter[product_id]`, `filter[status]` (pending/draft/published)

---

### 2. Track Orders and Order Items
Retrieve all orders with optional filtering by store, user email, or order number, and drill into individual order items.

**Tools:** `LEMON_SQUEEZY_LIST_ALL_ORDERS`, `LEMON_SQUEEZY_LIST_ALL_ORDER_ITEMS`

**Example prompt:**
> "Show all orders from johndoe@example.com in my Lemon Squeezy store"

**Key parameters for orders:**
- `filter[store_id]` -- Filter by store ID
- `filter[user_email]` -- Filter by customer email
- `filter[order_number]` -- Filter by specific order number
- `page[number]` / `page[size]` -- Pagination (max 100 per page)

**Key parameters for order items:**
- `filter[order_id]`, `filter[product_id]`, `filter[variant_id]` -- Filter by related entity

---

### 3. Monitor Subscriptions
List all subscriptions with rich filtering options to track recurring revenue.

**Tool:** `LEMON_SQUEEZY_LIST_ALL_SUBSCRIPTIONS`

**Example prompt:**
> "Show all active subscriptions in my Lemon Squeezy store"

**Key parameters:**
- `filter[status]` -- Filter by status (e.g., `active`, `cancelled`)
- `filter[store_id]` -- Filter by store
- `filter[product_id]` -- Filter by product
- `filter[user_email]` -- Filter by subscriber email
- `filter[variant_id]` -- Filter by variant
- `page[number]` / `page[size]` -- Pagination (max 100 per page)

---

### 4. Manage Customers
Retrieve customer records with details including email, MRR, total revenue, and customer portal URLs.

**Tool:** `LEMON_SQUEEZY_LIST_ALL_CUSTOMERS`

**Example prompt:**
> "Find the Lemon Squeezy customer with email johndoe@example.com"

**Key parameters:**
- `filter[email]` -- Filter by exact email address
- `filter[store_id]` -- Filter by store ID
- `page[number]` / `page[size]` -- Pagination (max 100 per page)

---

### 5. Audit Discounts and Redemptions
List all discount codes and track how they have been redeemed across orders.

**Tools:** `LEMON_SQUEEZY_LIST_ALL_DISCOUNTS`, `LEMON_SQUEEZY_LIST_ALL_DISCOUNT_REDEMPTIONS`

**Example prompt:**
> "Show all discounts for store 12345 and their redemption history"

**Key parameters for discounts:**
- `filter[store_id]` -- Filter by store
- `page[number]` / `page[size]` -- Pagination

**Key parameters for redemptions:**
- `filter[discount_id]` -- Filter by discount
- `filter[order_id]` -- Filter by order

---

### 6. Review Checkouts
List all checkout sessions with optional filtering by store or variant.

**Tool:** `LEMON_SQUEEZY_LIST_ALL_CHECKOUTS`

**Example prompt:**
> "Show all checkouts for variant 42 in my Lemon Squeezy store"

**Key parameters:**
- `filter[store_id]` -- Filter by store ID
- `filter[variant_id]` -- Filter by variant ID

---

## Known Pitfalls

- **Store ID is foundational**: Most filters require a `store_id`. Always call `LEMON_SQUEEZY_LIST_ALL_STORES` first to discover valid store IDs before filtering other resources.
- **Pagination is mandatory for large datasets**: All list endpoints use `page[number]` / `page[size]` pagination (max 100 per page). Do not assume the first page is complete.
- **Filter parameter naming**: Lemon Squeezy uses bracket notation for filters (e.g., `filter[store_id]`, `page[number]`). Ensure exact parameter names are used.
- **Subscription invoices vs. orders**: Subscription invoices (`LEMON_SQUEEZY_LIST_ALL_SUBSCRIPTION_INVOICES`) are separate from one-time orders. Use the appropriate endpoint for your use case.

---

## Quick Reference

| Action | Tool Slug | Required Params |
|---|---|---|
| List stores | `LEMON_SQUEEZY_LIST_ALL_STORES` | None |
| List products | `LEMON_SQUEEZY_LIST_ALL_PRODUCTS` | None (optional filters) |
| List variants | `LEMON_SQUEEZY_LIST_ALL_VARIANTS` | None (optional filters) |
| List orders | `LEMON_SQUEEZY_LIST_ALL_ORDERS` | None (optional filters) |
| List order items | `LEMON_SQUEEZY_LIST_ALL_ORDER_ITEMS` | None (optional filters) |
| List subscriptions | `LEMON_SQUEEZY_LIST_ALL_SUBSCRIPTIONS` | None (optional filters) |
| List customers | `LEMON_SQUEEZY_LIST_ALL_CUSTOMERS` | None (optional filters) |
| List discounts | `LEMON_SQUEEZY_LIST_ALL_DISCOUNTS` | None (optional filters) |
| List discount redemptions | `LEMON_SQUEEZY_LIST_ALL_DISCOUNT_REDEMPTIONS` | None (optional filters) |
| List checkouts | `LEMON_SQUEEZY_LIST_ALL_CHECKOUTS` | None (optional filters) |

---

*Powered by [Composio](https://composio.dev)*
