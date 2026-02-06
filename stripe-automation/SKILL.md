---
name: stripe-automation
description: "Automate Stripe tasks via Rube MCP (Composio): customers, charges, subscriptions, invoices, products, refunds. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Stripe Automation via Rube MCP

Automate Stripe payment operations through Composio's Stripe toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Stripe connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `stripe`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `stripe`
3. If connection is not ACTIVE, follow the returned auth link to complete Stripe connection
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Manage Customers

**When to use**: User wants to create, update, search, or list Stripe customers

**Tool sequence**:
1. `STRIPE_SEARCH_CUSTOMERS` - Search customers by email/name [Optional]
2. `STRIPE_LIST_CUSTOMERS` - List all customers [Optional]
3. `STRIPE_CREATE_CUSTOMER` - Create a new customer [Optional]
4. `STRIPE_POST_CUSTOMERS_CUSTOMER` - Update a customer [Optional]

**Key parameters**:
- `email`: Customer email
- `name`: Customer name
- `description`: Customer description
- `metadata`: Key-value metadata pairs
- `customer`: Customer ID for updates (e.g., 'cus_xxx')

**Pitfalls**:
- Stripe allows duplicate customers with the same email; search first to avoid duplicates
- Customer IDs start with 'cus_'

### 2. Manage Charges and Payments

**When to use**: User wants to create charges, payment intents, or view charge history

**Tool sequence**:
1. `STRIPE_LIST_CHARGES` - List charges with filters [Optional]
2. `STRIPE_CREATE_PAYMENT_INTENT` - Create a payment intent [Optional]
3. `STRIPE_CONFIRM_PAYMENT_INTENT` - Confirm a payment intent [Optional]
4. `STRIPE_POST_CHARGES` - Create a direct charge [Optional]
5. `STRIPE_CAPTURE_CHARGE` - Capture an authorized charge [Optional]

**Key parameters**:
- `amount`: Amount in smallest currency unit (e.g., cents for USD)
- `currency`: Three-letter ISO currency code (e.g., 'usd')
- `customer`: Customer ID
- `payment_method`: Payment method ID
- `description`: Charge description

**Pitfalls**:
- Amounts are in smallest currency unit (100 = $1.00 for USD)
- Currency codes must be lowercase (e.g., 'usd' not 'USD')
- Payment intents are the recommended flow over direct charges

### 3. Manage Subscriptions

**When to use**: User wants to create, list, update, or cancel subscriptions

**Tool sequence**:
1. `STRIPE_LIST_SUBSCRIPTIONS` - List subscriptions [Optional]
2. `STRIPE_POST_CUSTOMERS_CUSTOMER_SUBSCRIPTIONS` - Create subscription [Optional]
3. `STRIPE_RETRIEVE_SUBSCRIPTION` - Get subscription details [Optional]
4. `STRIPE_UPDATE_SUBSCRIPTION` - Modify subscription [Optional]

**Key parameters**:
- `customer`: Customer ID
- `items`: Array of price items (price_id and quantity)
- `subscription`: Subscription ID for retrieval/update (e.g., 'sub_xxx')

**Pitfalls**:
- Subscriptions require a valid customer with a payment method
- Price IDs (not product IDs) are used for subscription items
- Cancellation can be immediate or at period end

### 4. Manage Invoices

**When to use**: User wants to create, list, or search invoices

**Tool sequence**:
1. `STRIPE_LIST_INVOICES` - List invoices [Optional]
2. `STRIPE_SEARCH_INVOICES` - Search invoices [Optional]
3. `STRIPE_CREATE_INVOICE` - Create an invoice [Optional]

**Key parameters**:
- `customer`: Customer ID for invoice
- `collection_method`: 'charge_automatically' or 'send_invoice'
- `days_until_due`: Days until invoice is due

**Pitfalls**:
- Invoices auto-finalize by default; use `auto_advance: false` for draft invoices

### 5. Manage Products and Prices

**When to use**: User wants to list or search products and their pricing

**Tool sequence**:
1. `STRIPE_LIST_PRODUCTS` - List products [Optional]
2. `STRIPE_SEARCH_PRODUCTS` - Search products [Optional]
3. `STRIPE_LIST_PRICES` - List prices [Optional]
4. `STRIPE_GET_PRICES_SEARCH` - Search prices [Optional]

**Key parameters**:
- `active`: Filter by active/inactive status
- `query`: Search query for search endpoints

**Pitfalls**:
- Products and prices are separate objects; a product can have multiple prices
- Price IDs (e.g., 'price_xxx') are used for subscriptions and checkout

### 6. Handle Refunds

**When to use**: User wants to issue refunds on charges

**Tool sequence**:
1. `STRIPE_LIST_REFUNDS` - List refunds [Optional]
2. `STRIPE_POST_CHARGES_CHARGE_REFUNDS` - Create a refund [Optional]
3. `STRIPE_CREATE_REFUND` - Create refund via payment intent [Optional]

**Key parameters**:
- `charge`: Charge ID for refund
- `amount`: Partial refund amount (omit for full refund)
- `reason`: Refund reason ('duplicate', 'fraudulent', 'requested_by_customer')

**Pitfalls**:
- Refunds can take 5-10 business days to appear on customer statements
- Amount is in smallest currency unit

## Common Patterns

### Amount Formatting

Stripe uses smallest currency unit:
- USD: $10.50 = 1050 cents
- EUR: 10.50 = 1050 cents
- JPY: 1000 = 1000 (no decimals)

### Pagination

- Use `limit` parameter (max 100)
- Check `has_more` in response
- Pass `starting_after` with last object ID for next page
- Continue until `has_more` is false

## Known Pitfalls

**Amount Units**:
- Always use smallest currency unit (cents for USD/EUR)
- Zero-decimal currencies (JPY, KRW) use the amount directly

**ID Prefixes**:
- Customers: `cus_`, Charges: `ch_`, Subscriptions: `sub_`
- Invoices: `in_`, Products: `prod_`, Prices: `price_`
- Payment Intents: `pi_`, Refunds: `re_`

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Create customer | STRIPE_CREATE_CUSTOMER | email, name |
| Search customers | STRIPE_SEARCH_CUSTOMERS | query |
| Update customer | STRIPE_POST_CUSTOMERS_CUSTOMER | customer, fields |
| List charges | STRIPE_LIST_CHARGES | customer, limit |
| Create payment intent | STRIPE_CREATE_PAYMENT_INTENT | amount, currency |
| Confirm payment | STRIPE_CONFIRM_PAYMENT_INTENT | payment_intent |
| List subscriptions | STRIPE_LIST_SUBSCRIPTIONS | customer |
| Create subscription | STRIPE_POST_CUSTOMERS_CUSTOMER_SUBSCRIPTIONS | customer, items |
| Update subscription | STRIPE_UPDATE_SUBSCRIPTION | subscription, fields |
| List invoices | STRIPE_LIST_INVOICES | customer |
| Create invoice | STRIPE_CREATE_INVOICE | customer |
| Search invoices | STRIPE_SEARCH_INVOICES | query |
| List products | STRIPE_LIST_PRODUCTS | active |
| Search products | STRIPE_SEARCH_PRODUCTS | query |
| List prices | STRIPE_LIST_PRICES | product |
| Search prices | STRIPE_GET_PRICES_SEARCH | query |
| List refunds | STRIPE_LIST_REFUNDS | charge |
| Create refund | STRIPE_CREATE_REFUND | charge, amount |
| Payment methods | STRIPE_LIST_CUSTOMER_PAYMENT_METHODS | customer |
| Checkout session | STRIPE_CREATE_CHECKOUT_SESSION | line_items |
| List payment intents | STRIPE_LIST_PAYMENT_INTENTS | customer |
