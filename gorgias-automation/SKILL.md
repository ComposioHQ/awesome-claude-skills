---
name: Gorgias Automation
description: "Automate e-commerce customer support workflows in Gorgias -- manage tickets, customers, tags, and teams through natural language commands."
requires:
  mcp:
    - rube
---

# Gorgias Automation

Automate your Gorgias helpdesk operations directly from Claude Code. Create, update, and triage support tickets, manage customers, and organize your support team -- all without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/gorgias](https://composio.dev/toolkits/gorgias)

---

## Setup

1. Add the Rube MCP server to your Claude Code config with URL: `https://rube.app/mcp`
2. When prompted, authenticate your Gorgias account through the connection link provided
3. Start automating your support workflows with natural language

---

## Core Workflows

### 1. List and Filter Tickets

Retrieve tickets with filtering by status, channel, assignee, date range, and more.

**Tool:** `GORGIAS_LIST_TICKETS`

```
List all open tickets from the email channel created in the last 7 days
```

Key parameters:
- `status` -- filter by ticket status (e.g., "open", "closed")
- `channel` -- filter by channel (e.g., "email", "chat")
- `assignee_user_id` / `assignee_team_id` -- filter by assigned agent or team
- `created_from` / `created_to` -- ISO date range filters
- `limit` (max 100) / `offset` -- pagination controls
- `order_by` / `order_dir` -- sorting options

### 2. Create and Update Tickets

Create new tickets or update existing ones with assignment, priority, and status changes.

**Tools:** `GORGIAS_CREATE_TICKET`, `GORGIAS_UPDATE_TICKET`, `GORGIAS_GET_TICKET`

```
Create a high-priority ticket for customer 12345 about a missing order with subject "Order #9876 not delivered"
```

- `GORGIAS_CREATE_TICKET` requires `customer_id`; accepts `subject`, `status`, `priority`, `channel`, `messages`, `tags`
- `GORGIAS_UPDATE_TICKET` requires `ticket_id`; all other fields are optional partial updates
- `GORGIAS_GET_TICKET` retrieves full ticket details by `ticket_id`

### 3. Manage Ticket Tags

Add tags to tickets for categorization, routing, and reporting.

**Tools:** `GORGIAS_ADD_TICKET_TAGS`, `GORGIAS_LIST_TICKET_TAGS`

```
Add tags 101 and 202 to ticket 5678, then show me all tags on that ticket
```

- `GORGIAS_ADD_TICKET_TAGS` requires `ticket_id` and `tag_ids` (array of integers)
- `GORGIAS_LIST_TICKET_TAGS` requires `ticket_id` to retrieve current tags

### 4. Customer Management

Create new customers or merge duplicate customer records.

**Tools:** `GORGIAS_CREATE_CUSTOMER`, `GORGIAS_MERGE_CUSTOMERS`, `GORGIAS_LIST_CUSTOMERS`

```
Create a new customer named "Jane Doe" with email jane@example.com and phone channel
```

- `GORGIAS_CREATE_CUSTOMER` requires `name`; accepts `email`, `channels` (array with `type` and `value`), `external_id`, `address`, `data`
- `GORGIAS_MERGE_CUSTOMERS` requires `source_customer_id` and `target_customer_id` -- source is merged into target
- `GORGIAS_LIST_CUSTOMERS` retrieves customers with filtering options

### 5. Team and Account Operations

List teams, retrieve account info, and inspect ticket custom fields.

**Tools:** `GORGIAS_LIST_TEAMS`, `GORGIAS_GET_TEAM`, `GORGIAS_GET_ACCOUNT`, `GORGIAS_LIST_TICKET_FIELD_VALUES`

```
Show me all support teams in our Gorgias account
```

- `GORGIAS_GET_ACCOUNT` returns account-level metrics and configuration
- `GORGIAS_LIST_TEAMS` / `GORGIAS_GET_TEAM` manage team lookup
- `GORGIAS_LIST_TICKET_FIELD_VALUES` returns custom field values for a given ticket

### 6. Activity and Event Tracking

Monitor ticket activity and customer event history.

**Tools:** `GORGIAS_LIST_EVENTS`

```
List recent events to see what activity has happened across our support queue
```

- `GORGIAS_LIST_EVENTS` provides an activity timeline with filtering options

---

## Known Pitfalls

- **Pagination required:** `GORGIAS_LIST_TICKETS` uses `limit`/`offset` pagination. Failing to loop through pages will miss older tickets and produce incomplete data.
- **Filter specificity:** Missing or overly broad filters on `GORGIAS_LIST_TICKETS` can overload the export or omit the desired reporting window. Always set `created_from`/`created_to` for time-bound queries.
- **Custom fields are separate:** Key business KPIs may only exist in custom fields. You must query `GORGIAS_LIST_TICKET_FIELD_VALUES` explicitly to include them.
- **Rate limits:** High-volume exports across `GORGIAS_LIST_TICKETS` and related endpoints can hit Gorgias rate limits. Add backoff and resume from the last offset.
- **Auth errors:** 401/403 responses on any Gorgias tool indicate token or permission issues. Do not treat partial data as a complete dataset.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `GORGIAS_LIST_TICKETS` | List tickets with filters (status, channel, date, assignee) |
| `GORGIAS_GET_TICKET` | Retrieve a specific ticket by ID |
| `GORGIAS_CREATE_TICKET` | Create a new ticket (requires `customer_id`) |
| `GORGIAS_UPDATE_TICKET` | Update ticket fields (requires `ticket_id`) |
| `GORGIAS_ADD_TICKET_TAGS` | Add tags to a ticket |
| `GORGIAS_LIST_TICKET_TAGS` | List all tags on a ticket |
| `GORGIAS_LIST_TICKET_FIELD_VALUES` | List custom field values for a ticket |
| `GORGIAS_CREATE_CUSTOMER` | Create a new customer (requires `name`) |
| `GORGIAS_MERGE_CUSTOMERS` | Merge two customer records |
| `GORGIAS_LIST_CUSTOMERS` | List customers with filters |
| `GORGIAS_LIST_TEAMS` | List all teams |
| `GORGIAS_GET_TEAM` | Retrieve a specific team |
| `GORGIAS_GET_ACCOUNT` | Retrieve account information |
| `GORGIAS_LIST_EVENTS` | List activity events with filters |

---

*Powered by [Composio](https://composio.dev)*
