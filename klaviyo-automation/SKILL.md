---
name: klaviyo-automation
description: "Automate Klaviyo tasks via Rube MCP (Composio): manage email/SMS campaigns, inspect campaign messages, track tags, and monitor send jobs. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Klaviyo Automation via Rube MCP

Automate Klaviyo email and SMS marketing operations through Composio's Klaviyo toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Klaviyo connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `klaviyo`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `klaviyo`
3. If connection is not ACTIVE, follow the returned auth link to complete Klaviyo authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List and Filter Campaigns

**When to use**: User wants to browse, search, or filter marketing campaigns

**Tool sequence**:
1. `KLAVIYO_GET_CAMPAIGNS` - List campaigns with channel and status filters [Required]

**Key parameters**:
- `channel`: Campaign channel - 'email' or 'sms' (required by Klaviyo API)
- `filter`: Additional filter string (e.g., `equals(status,"draft")`)
- `sort`: Sort field with optional `-` prefix for descending (e.g., '-created_at', 'name')
- `page_cursor`: Pagination cursor for next page
- `include_archived`: Include archived campaigns (default: false)

**Pitfalls**:
- `channel` is required; omitting it can produce incomplete or unexpected results
- Pagination is mandatory for full coverage; a single call returns only one page (default ~10)
- Follow `page_cursor` until exhausted to get all campaigns
- Status filtering via `filter` (e.g., `equals(status,"draft")`) can return mixed statuses; always validate `data[].attributes.status` client-side
- Status strings are case-sensitive and can be compound (e.g., 'Cancelled: No Recipients')
- Response shape is nested: `response.data.data` with status at `data[].attributes.status`

### 2. Get Campaign Details

**When to use**: User wants detailed information about a specific campaign

**Tool sequence**:
1. `KLAVIYO_GET_CAMPAIGNS` - Find campaign to get its ID [Prerequisite]
2. `KLAVIYO_GET_CAMPAIGN` - Retrieve full campaign details [Required]

**Key parameters**:
- `campaign_id`: Campaign ID string (e.g., '01GDDKASAP8TKDDA2GRZDSVP4H')
- `include_messages`: Include campaign messages in response
- `include_tags`: Include tags in response

**Pitfalls**:
- Campaign IDs are alphanumeric strings, not numeric
- `include_messages` and `include_tags` add related data to the response via Klaviyo's include mechanism
- Campaign details include audiences, send strategy, tracking options, and scheduling info

### 3. Inspect Campaign Messages

**When to use**: User wants to view the email/SMS content of a campaign

**Tool sequence**:
1. `KLAVIYO_GET_CAMPAIGN` - Find campaign and its message IDs [Prerequisite]
2. `KLAVIYO_GET_CAMPAIGN_MESSAGE` - Get message content details [Required]

**Key parameters**:
- `id`: Message ID string
- `fields__campaign__message`: Sparse fieldset for message attributes (e.g., 'content.subject', 'content.from_email', 'content.body')
- `fields__campaign`: Sparse fieldset for campaign attributes
- `fields__template`: Sparse fieldset for template attributes
- `include`: Related resources to include ('campaign', 'template')

**Pitfalls**:
- Message IDs are separate from campaign IDs; extract from campaign response
- Sparse fieldset syntax uses dot notation for nested fields: 'content.subject', 'content.from_email'
- Email messages have content fields: subject, preview_text, from_email, from_label, reply_to_email
- SMS messages have content fields: body
- Including 'template' provides the HTML/text content of the email

### 4. Manage Campaign Tags

**When to use**: User wants to view tags associated with campaigns for organization

**Tool sequence**:
1. `KLAVIYO_GET_CAMPAIGN_RELATIONSHIPS_TAGS` - Get tag IDs for a campaign [Required]

**Key parameters**:
- `id`: Campaign ID string

**Pitfalls**:
- Returns only tag IDs, not tag names/details
- Tag IDs can be used with Klaviyo's tag endpoints for full details
- Rate limit: 3/s burst, 60/m steady (stricter than other endpoints)

### 5. Monitor Campaign Send Jobs

**When to use**: User wants to check the status of a campaign send operation

**Tool sequence**:
1. `KLAVIYO_GET_CAMPAIGN_SEND_JOB` - Check send job status [Required]

**Key parameters**:
- `id`: Send job ID

**Pitfalls**:
- Send job IDs are returned when a campaign send is initiated
- Job statuses indicate whether the send is queued, in progress, complete, or failed
- Rate limit: 10/s burst, 150/m steady

## Common Patterns

### Campaign Discovery Pattern

```
1. Call KLAVIYO_GET_CAMPAIGNS with channel='email'
2. Paginate through all results via page_cursor
3. Filter by status client-side for accuracy
4. Extract campaign IDs for detailed inspection
```

### Sparse Fieldset Pattern

Klaviyo supports sparse fieldsets to reduce response size:
```
fields__campaign__message=['content.subject', 'content.from_email', 'send_times']
fields__campaign=['name', 'status', 'send_time']
fields__template=['name', 'html', 'text']
```

### Pagination

- Klaviyo uses cursor-based pagination
- Check response for `page_cursor` in the pagination metadata
- Pass cursor as `page_cursor` in next request
- Default page size is ~10 campaigns
- Continue until no more cursor is returned

### Filter Syntax

```
- equals(status,"draft") - Campaigns in draft status
- equals(name,"Newsletter") - Campaign named "Newsletter"
- greater-than(created_at,"2024-01-01T00:00:00Z") - Created after date
```

## Known Pitfalls

**API Version**:
- Klaviyo API uses versioned endpoints (e.g., v2024-07-15)
- Response schemas may change between API versions
- Tool responses follow the version configured in the Composio integration

**Response Nesting**:
- Data is nested: `response.data.data[].attributes`
- Campaign status at `data[].attributes.status`
- Mis-parsing the nesting yields empty or incorrect results
- Always navigate through the full path defensively

**Rate Limits**:
- Burst: 10/s (3/s for tag endpoints)
- Steady: 150/m (60/m for tag endpoints)
- Required scope: campaigns:read
- Implement backoff on 429 responses

**Status Values**:
- Status strings are case-sensitive
- Compound statuses exist (e.g., 'Cancelled: No Recipients')
- Server-side filtering may return mixed statuses; always validate client-side

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List campaigns | KLAVIYO_GET_CAMPAIGNS | channel, filter, sort, page_cursor |
| Get campaign details | KLAVIYO_GET_CAMPAIGN | campaign_id, include_messages, include_tags |
| Get campaign message | KLAVIYO_GET_CAMPAIGN_MESSAGE | id, fields__campaign__message |
| Get campaign tags | KLAVIYO_GET_CAMPAIGN_RELATIONSHIPS_TAGS | id |
| Get send job status | KLAVIYO_GET_CAMPAIGN_SEND_JOB | id |
