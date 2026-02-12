---
name: Instantly Automation
description: "Automate Instantly cold email outreach -- manage campaigns, sending accounts, lead lists, bulk lead imports, and campaign analytics -- using natural language through the Composio MCP integration."
category: email-outreach
requires:
  mcp:
    - rube
---

# Instantly Automation

Automate your cold email outreach with Instantly -- create and manage campaigns with multi-step sequences, configure sending schedules, import leads in bulk, manage sending accounts, and track campaign performance -- all through natural language commands.

**Toolkit docs:** [composio.dev/toolkits/instantly](https://composio.dev/toolkits/instantly)

---

## Setup

1. Add the Composio MCP server to your client configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Instantly account when prompted (API key authentication).
3. Start issuing natural language commands to manage your outreach campaigns.

---

## Core Workflows

### 1. List Sending Accounts
Retrieve all email accounts configured in your Instantly workspace, with filtering by status and provider.

**Tool:** `INSTANTLY_LIST_ACCOUNTS`

**Example prompt:**
> "Show all active sending accounts in my Instantly workspace"

**Key parameters:**
- `status` -- Filter by status: `1` (Active), `2` (Paused), `-1` (Connection Error), `-2` (Soft Bounce Error), `-3` (Sending Error)
- `provider_code` -- Filter by provider: `1` (Custom IMAP/SMTP), `2` (Google), `3` (Microsoft), `4` (AWS)
- `search` -- Search by email substring or domain
- `limit` -- Max items (1-100)
- `starting_after` -- Pagination cursor from previous response
- `tag_ids` -- Comma-separated tag UUIDs

---

### 2. Create a Campaign
Launch a new outreach campaign with scheduling, email sequences, A/B testing variants, and sending configuration.

**Tool:** `INSTANTLY_CREATE_CAMPAIGN`

**Example prompt:**
> "Create an Instantly campaign called 'Q1 Outreach' that sends Monday-Friday 9am-5pm Central time with a 3-step email sequence"

**Key parameters:**
- `name` (required) -- Campaign name
- `campaign_schedule` (required) -- Schedule configuration:
  - `schedules` (required) -- Array of schedule objects, each with:
    - `name` -- Schedule name
    - `timing` -- `{from: "09:00", to: "17:00"}` (HH:mm format)
    - `days` -- Map of day index strings "0" (Sun) to "6" (Sat) to booleans
    - `timezone` -- Supported values include "America/Chicago", "America/Detroit", "America/Boise", "America/Anchorage"
  - `start_date` / `end_date` -- ISO 8601 dates
- `email_list` -- Array of sending account email addresses (must be pre-configured accounts; use `INSTANTLY_LIST_ACCOUNTS` to discover valid addresses)
- `sequences` -- Array (only first element used) containing:
  - `steps` -- Array of step objects with:
    - `type` -- Must be "email"
    - `delay` -- Days before NEXT email (integer, min 0)
    - `variants` -- Array of `{subject, body}` objects for A/B testing
- `daily_limit` -- Daily sending cap
- `email_gap` -- Minutes between emails
- `stop_on_reply` -- Stop campaign when lead replies (boolean)
- `stop_on_auto_reply` -- Stop on auto-replies (boolean)
- `open_tracking` / `link_tracking` -- Enable tracking (booleans)

**Timezone notes:**
- Verified working: "America/Chicago" (Central), "America/Detroit" (Eastern), "America/Boise" (Mountain)
- Auto-mapped: "America/New_York" maps to "America/Detroit", "America/Denver" maps to "America/Boise"
- NOT supported: "America/Los_Angeles", "US/Pacific" -- use "America/Anchorage" or "America/Dawson" as alternatives

---

### 3. Update Campaign Settings
Modify an existing campaign's schedule, sending limits, sequences, or tracking settings.

**Tool:** `INSTANTLY_UPDATE_CAMPAIGN`

**Example prompt:**
> "Update my Instantly campaign to increase the daily limit to 100 and enable open tracking"

**Key parameters:**
- `id` (required) -- Campaign UUID
- Any combination of: `name`, `campaign_schedule`, `email_list`, `sequences`, `daily_limit`, `email_gap`, `stop_on_reply`, `open_tracking`, `link_tracking`, etc.
- Set any parameter to `null` to unset it

---

### 4. Manage Lead Lists and Bulk Import
Create dedicated lead lists and import prospects in bulk for campaign targeting.

**Tools:** `INSTANTLY_CREATE_LEAD_LIST`, `INSTANTLY_ADD_LEADS_BULK`

**Example prompt:**
> "Create a lead list called 'Q1 Prospects' and add 50 leads to my Instantly campaign"

**Key parameters for creating lead lists:**
- List name and configuration

**Key parameters for bulk lead import:**
- Campaign or list ID to import into
- Array of lead objects with email and metadata
- Duplicate handling options
- Lead verification settings

---

### 5. Review Campaign Details
Retrieve full campaign configuration to verify settings, inspect sequences, or prepare for updates.

**Tool:** `INSTANTLY_GET_CAMPAIGN`

**Example prompt:**
> "Show me the full details of my Instantly campaign"

**Key parameters:**
- `id` (required) -- Campaign UUID

---

### 6. List All Campaigns
Enumerate all campaigns in your workspace with optional filters and pagination.

**Tool:** `INSTANTLY_LIST_CAMPAIGNS`

**Example prompt:**
> "List all my Instantly campaigns"

**Key parameters:**
- Optional filters and pagination parameters

---

## Known Pitfalls

- **Timezone support is limited**: The Instantly API accepts a restricted set of timezone strings. Pacific Time ("America/Los_Angeles") is NOT supported. Use "America/Anchorage" (UTC-9/UTC-8) or "America/Dawson" (UTC-7 year-round) as alternatives.
- **Invalid schedule payloads cause 400 errors**: A malformed `campaign_schedule` (missing `days`, `from`, `to`, or `schedules`) triggers HTTP 400. Repeated 400s indicate payload issues, not transient failures.
- **Sequences must be complete**: Each sequence step requires a valid `type` ("email"), `delay`, and at least one variant with both `subject` and `body`. Incomplete variants block campaign creation.
- **Only first sequence element is used**: The API only processes `sequences[0]`. Additional sequences are ignored.
- **email_list must reference existing accounts**: The `email_list` field requires email addresses of pre-configured sending accounts in your Instantly workspace, not arbitrary recipient addresses. Always use `INSTANTLY_LIST_ACCOUNTS` to discover valid sending addresses.
- **401 scope errors on campaign creation**: Campaign creation can fail with "Invalid scope. Required: campaigns:create". Update your API key permissions before retrying writes.
- **Read-back fields may differ**: Field names in `INSTANTLY_GET_CAMPAIGN` responses may differ from create payloads (e.g., `timing.from_` vs `timing.from`). Parse defensively.

---

## Quick Reference

| Action | Tool Slug | Required Params |
|---|---|---|
| List sending accounts | `INSTANTLY_LIST_ACCOUNTS` | None (optional filters) |
| Create campaign | `INSTANTLY_CREATE_CAMPAIGN` | `name`, `campaign_schedule` |
| Update campaign | `INSTANTLY_UPDATE_CAMPAIGN` | `id` |
| Get campaign details | `INSTANTLY_GET_CAMPAIGN` | `id` |
| List campaigns | `INSTANTLY_LIST_CAMPAIGNS` | None (optional filters) |
| Create lead list | `INSTANTLY_CREATE_LEAD_LIST` | List name |
| Bulk import leads | `INSTANTLY_ADD_LEADS_BULK` | Campaign/list ID, leads |

---

*Powered by [Composio](https://composio.dev)*
