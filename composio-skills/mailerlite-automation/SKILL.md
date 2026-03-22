---
name: MailerLite Automation
description: "Automate email marketing workflows including subscriber management, campaign analytics, group segmentation, and account monitoring through MailerLite via Composio"
requires:
  mcp:
    - rube
---

# MailerLite Automation

Automate email marketing operations -- manage subscribers, analyze campaign performance, organize groups and segments, and monitor account health -- all orchestrated through the Composio MCP integration.

**Toolkit docs:** [composio.dev/toolkits/mailerlite](https://composio.dev/toolkits/mailerlite)

---

## Setup

1. Connect your MailerLite account through the Composio MCP server at `https://rube.app/mcp`
2. The agent will prompt you with an authentication link if no active connection exists
3. Once connected, all `MAILERLITE_*` tools become available for execution

---

## Core Workflows

### 1. Verify Account & Fetch Metadata
Retrieve account details including plan limits and timezone to ensure consistent reporting.

**Tool:** `MAILERLITE_GET_ACCOUNT_INFO`

```
No parameters required -- returns account metadata, plan details, and timezone configuration.
```

Always run this first to establish plan constraints and timezone for consistent time-windowed queries.

---

### 2. Get Account-Wide Performance Stats
Retrieve aggregate subscriber counts, sent email totals, and engagement metrics for a health snapshot.

**Tool:** `MAILERLITE_GET_ACCOUNT_STATS`

```
No parameters required -- returns overall subscriber counts, sent emails, and performance metrics.
```

---

### 3. List & Paginate Subscribers
Retrieve subscribers with optional status filtering and cursor-based pagination.

**Tool:** `MAILERLITE_GET_SUBSCRIBERS`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filter[status]` | string | No | Filter by: `active`, `unsubscribed`, `unconfirmed`, `bounced`, `junk` |
| `limit` | integer | No | Subscribers per page (default: 25) |
| `cursor` | string | No | Pagination cursor from previous response `meta.cursor` |
| `include` | string | No | Set to `groups` to include group memberships |

**Important:** Loop with `meta.next_cursor` until `null` to build a complete subscriber list.

---

### 4. List & Analyze Campaigns
Retrieve campaigns with optional status/type filters and page-based pagination.

**Tool:** `MAILERLITE_GET_CAMPAIGNS`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filter[status]` | string | No | Filter by: `sent`, `draft`, `ready` |
| `filter[type]` | string | No | Filter by: `regular`, `ab`, `resend`, `rss` |
| `limit` | integer | No | Items per page (default: 25) |
| `page` | integer | No | Page number (default: 1) |

**Important:** Paginate using `meta.last_page` to avoid omitting campaigns from historical analysis.

---

### 5. Manage Subscriber Groups
List, filter, and sort subscriber groups for audience organization.

**Tool:** `MAILERLITE_GET_GROUPS`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filter[name]` | string | No | Partial name match filter |
| `limit` | integer | No | Max groups to return |
| `page` | integer | No | Page number (starting from 1) |
| `sort` | string | No | Sort by: `name`, `total`, `open_rate`, `click_rate`, `created_at` (prefix `-` for descending) |

---

### 6. Retrieve Audience Segments & Custom Fields
Fetch segments and custom field definitions for advanced audience analysis.

**Tools:** `MAILERLITE_GET_SEGMENTS` and `MAILERLITE_GET_FIELDS`

**Segments:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Max segments to return (max 250) |
| `page` | integer | No | Page number (starting from 1) |

**Fields:** No parameters required -- returns all custom field definitions.

---

## Known Pitfalls

| Pitfall | Details |
|---------|---------|
| **Subscriber pagination is cursor-based** | `MAILERLITE_GET_SUBSCRIBERS` uses `meta.next_cursor` -- you must loop until `null` or counts will be incomplete |
| **Campaign pagination is page-based** | `MAILERLITE_GET_CAMPAIGNS` uses `page`/`limit` with `meta.last_page` -- stopping early omits campaigns and distorts trends |
| **Sampling bias** | Computing engagement metrics from only the first page introduces bias; always aggregate across all pages |
| **Nested response shape** | MailerLite payloads are nested under `results[i].response.data` with `data` and `meta` subkeys, not a flat `data` key -- parse accordingly |
| **API quotas** | Subscriber listing is limited by MailerLite Connect API quotas -- plan batch operations accordingly |

---

## Quick Reference

| Tool Slug | Purpose |
|-----------|---------|
| `MAILERLITE_GET_ACCOUNT_INFO` | Verify auth and review account metadata |
| `MAILERLITE_GET_ACCOUNT_STATS` | Get aggregate performance metrics |
| `MAILERLITE_GET_SUBSCRIBERS` | List subscribers with filtering and pagination |
| `MAILERLITE_GET_CAMPAIGNS` | List campaigns with status/type filters |
| `MAILERLITE_GET_GROUPS` | List and sort subscriber groups |
| `MAILERLITE_GET_SEGMENTS` | List audience segments |
| `MAILERLITE_GET_FIELDS` | Retrieve custom field definitions |

---

*Powered by [Composio](https://composio.dev)*
