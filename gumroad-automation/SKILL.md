---
name: Gumroad Automation
description: "Automate Gumroad product management, sales tracking, license verification, and webhook subscriptions using natural language through the Composio MCP integration."
category: e-commerce
requires:
  mcp:
    - rube
---

# Gumroad Automation

Automate your Gumroad storefront -- list products, track sales, verify licenses, and manage real-time webhooks -- all through natural language commands.

**Toolkit docs:** [composio.dev/toolkits/gumroad](https://composio.dev/toolkits/gumroad)

---

## Setup

1. Add the Composio MCP server to your client configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Gumroad account when prompted (API key authentication).
3. Start issuing natural language commands to manage your Gumroad store.

---

## Core Workflows

### 1. List All Products
Retrieve every product in your authenticated Gumroad account to get product IDs for downstream operations.

**Tool:** `GUMROAD_LIST_PRODUCTS`

**Example prompt:**
> "List all my Gumroad products"

**Parameters:** None required -- returns all products for the authenticated account.

---

### 2. Track Sales with Filters
Retrieve successful sales with optional filtering by email, date range, product, or pagination.

**Tool:** `GUMROAD_GET_SALES`

**Example prompt:**
> "Show me all Gumroad sales from January 2025 for product prod_ABC123"

**Key parameters:**
- `after` -- ISO8601 date/time to filter sales after (e.g., `2025-01-01T00:00:00Z`)
- `before` -- ISO8601 date/time to filter sales before
- `email` -- Filter by customer email address
- `product_id` -- Filter by specific product ID
- `page` -- Page number for paginated results (minimum 1)

---

### 3. Verify License Keys
Check if a license key is valid against a specific product, inspect usage count, or verify membership entitlement.

**Tool:** `GUMROAD_VERIFY_LICENSE`

**Example prompt:**
> "Verify license key ABCD-EFGH-IJKL-MNOP for product prod_ABC123"

**Key parameters (all required):**
- `product_id` -- The product ID to verify against (required for products created on/after Jan 9, 2023)
- `license_key` -- The license key string (e.g., `ABCD-EFGH-IJKL-MNOP`)
- `increment_uses_count` -- Whether to increment usage count (defaults to true)

---

### 4. Subscribe to Webhook Events
Set up real-time event notifications by subscribing your endpoint URL to specific Gumroad resource events.

**Tool:** `GUMROAD_SUBSCRIBE_TO_RESOURCE`

**Example prompt:**
> "Subscribe my webhook https://example.com/hook to Gumroad sale events"

**Key parameters (all required):**
- `resource_name` -- One of: `sale`, `refund`, `dispute`, `dispute_won`, `cancellation`, `subscription_updated`, `subscription_ended`, `subscription_restarted`
- `post_url` -- Your endpoint URL that receives HTTP POST notifications

---

### 5. List Active Webhook Subscriptions
Review existing webhook subscriptions for a given resource type before adding new ones to avoid duplicates.

**Tool:** `GUMROAD_GET_RESOURCE_SUBSCRIPTIONS`

**Example prompt:**
> "Show all my active Gumroad webhook subscriptions for sale events"

**Key parameters (required):**
- `resource_name` -- One of the eight supported event types (e.g., `sale`, `refund`)

---

## Known Pitfalls

- **Product ID required for license verification**: Products created on or after January 9, 2023 require the `product_id` parameter. Older products may work without it but providing it is recommended.
- **Pagination on sales**: Sales results are paginated. Always check if more pages exist by incrementing the `page` parameter.
- **Webhook deduplication**: Before subscribing to a resource, use `GUMROAD_GET_RESOURCE_SUBSCRIPTIONS` to check for existing subscriptions and avoid duplicate webhooks.
- **ISO8601 date format**: Date filters on sales must use ISO8601 format (e.g., `2025-01-01T00:00:00Z`), not plain dates.

---

## Quick Reference

| Action | Tool Slug | Required Params |
|---|---|---|
| List products | `GUMROAD_LIST_PRODUCTS` | None |
| Get sales | `GUMROAD_GET_SALES` | None (all optional filters) |
| Verify license | `GUMROAD_VERIFY_LICENSE` | `product_id`, `license_key` |
| Subscribe to events | `GUMROAD_SUBSCRIBE_TO_RESOURCE` | `resource_name`, `post_url` |
| List webhook subs | `GUMROAD_GET_RESOURCE_SUBSCRIPTIONS` | `resource_name` |

---

*Powered by [Composio](https://composio.dev)*
