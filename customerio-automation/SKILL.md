---
name: Customer.io Automation
description: "Automate customer engagement workflows including broadcast triggers, message analytics, segment management, and newsletter tracking through Customer.io via Composio"
requires:
  mcp:
    - rube
---

# Customer.io Automation

Automate customer engagement operations -- trigger targeted broadcasts, retrieve delivery metrics, manage audience segments, list newsletters and transactional templates, and inspect trigger execution history -- all orchestrated through the Composio MCP integration.

**Toolkit docs:** [composio.dev/toolkits/customerio](https://composio.dev/toolkits/customerio)

---

## Setup

1. Connect your Customer.io account through the Composio MCP server at `https://rube.app/mcp`
2. The agent will prompt you with an authentication link if no active connection exists
3. Once connected, all `CUSTOMERIO_*` tools become available for execution

---

## Core Workflows

### 1. Trigger a Broadcast
Manually fire a pre-configured broadcast to a specific audience with personalization data.

**Tool:** `CUSTOMERIO_TRIGGER_BROADCAST`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `broadcast_id` | integer | Yes | Broadcast ID from Customer.io Triggering Details |
| `ids` | array | No | List of customer IDs to target |
| `emails` | array | No | List of email addresses to target |
| `recipients` | object | No | Complex filter with `and`/`or`/`not`/`segment` operators |
| `per_user_data` | array | No | Per-user personalization with `id`/`email` + `data` |
| `data` | object | No | Global key-value data for Liquid template personalization |
| `data_file_url` | string | No | URL to JSON file with per-line user data |
| `email_add_duplicates` | boolean | No | Allow duplicate recipients (default: false) |
| `email_ignore_missing` | boolean | No | Skip people without emails (default: false) |
| `id_ignore_missing` | boolean | No | Skip people without customer IDs (default: false) |

**Important:** Provide exactly ONE audience option: `recipients`, `ids`, `emails`, `per_user_data`, or `data_file_url`. Rate limit: 1 request per 10 seconds per broadcast.

---

### 2. Retrieve Message Delivery Metrics
Fetch paginated delivery metrics for messages with filtering by campaign, type, and time window.

**Tool:** `CUSTOMERIO_GET_MESSAGES`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | No | Message type: `email`, `webhook`, `twilio`, `slack`, `push`, `in_app` |
| `metric` | string | No | Metric: `attempted`, `sent`, `delivered`, `opened`, `clicked`, `converted` |
| `campaign_id` | integer | No | Filter by campaign ID |
| `newsletter_id` | integer | No | Filter by newsletter ID |
| `action_id` | integer | No | Filter by action ID |
| `start_ts` | integer | No | Start of time window (Unix timestamp) |
| `end_ts` | integer | No | End of time window (Unix timestamp) |
| `limit` | integer | No | Results per page, 1-1000 (default: 50) |
| `start` | string | No | Pagination token from previous response `next` value |
| `drafts` | boolean | No | Return draft messages instead of active/sent |

---

### 3. List Audience Segments
Retrieve all segments defined in your workspace for audience analysis and broadcast targeting.

**Tool:** `CUSTOMERIO_GET_SEGMENTS`

```
No parameters required -- returns all segments with IDs and metadata.
```

Use segment IDs when targeting broadcasts via the `recipients.segment.id` filter.

---

### 4. List Newsletters
Paginate through all newsletter metadata for tracking and analysis.

**Tool:** `CUSTOMERIO_LIST_NEWSLETTERS`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Max per page, 1-100 |
| `sort` | string | No | `asc` (chronological) or `desc` (reverse) |
| `start` | string | No | Pagination cursor from previous response `next` value |

---

### 5. Discover Transactional Message Templates
List all transactional message templates to find IDs for sending via the API.

**Tool:** `CUSTOMERIO_LIST_TRANSACTIONAL_MESSAGES`

```
No parameters required -- returns template IDs and trigger names.
```

---

### 6. Inspect Broadcast Trigger History
Review all trigger executions for a broadcast and inspect individual trigger details.

**Tools:** `CUSTOMERIO_GET_TRIGGERS` and `CUSTOMERIO_GET_TRIGGER`

**List all triggers for a broadcast:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `broadcast_id` | integer | Yes | The broadcast/campaign ID |

**Get a specific trigger:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `broadcast_id` | integer | Yes | The campaign/broadcast ID |
| `trigger_id` | string | Yes | Trigger identifier (e.g., `456` or `5-37`) |

---

## Known Pitfalls

| Pitfall | Details |
|---------|---------|
| **Mutually exclusive audience params** | `CUSTOMERIO_TRIGGER_BROADCAST` requires exactly ONE of `recipients`, `ids`, `emails`, `per_user_data`, or `data_file_url` -- providing multiple causes errors |
| **Rate limiting on broadcasts** | Broadcasts are limited to 1 trigger request per 10 seconds per broadcast ID |
| **Unix timestamp format** | `start_ts` and `end_ts` in `CUSTOMERIO_GET_MESSAGES` must be Unix timestamps, not ISO strings |
| **Pagination tokens** | Messages and newsletters use cursor-based pagination via the `start` parameter -- use the `next` value from previous responses |
| **Segment ID resolution** | To target a segment in a broadcast, first fetch segment IDs via `CUSTOMERIO_GET_SEGMENTS`, then reference by ID in `recipients.segment.id` |

---

## Quick Reference

| Tool Slug | Purpose |
|-----------|---------|
| `CUSTOMERIO_TRIGGER_BROADCAST` | Trigger a broadcast to a defined audience |
| `CUSTOMERIO_GET_MESSAGES` | Retrieve message delivery metrics with filters |
| `CUSTOMERIO_GET_SEGMENTS` | List all audience segments |
| `CUSTOMERIO_GET_SEGMENT_DETAILS` | Get details for a specific segment |
| `CUSTOMERIO_LIST_NEWSLETTERS` | Paginate through newsletters |
| `CUSTOMERIO_LIST_TRANSACTIONAL_MESSAGES` | List transactional message templates |
| `CUSTOMERIO_GET_TRIGGERS` | List all trigger executions for a broadcast |
| `CUSTOMERIO_GET_TRIGGER` | Inspect a specific trigger execution |

---

*Powered by [Composio](https://composio.dev)*
