---
name: postmark-automation
description: "Automate Postmark email delivery tasks via Rube MCP (Composio): send templated emails, manage templates, monitor delivery stats and bounces. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Postmark Automation via Rube MCP

Automate Postmark transactional email operations through Composio's Postmark toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Postmark connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `postmark`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `postmark`
3. If connection is not ACTIVE, follow the returned auth link to complete Postmark authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Send Templated Batch Emails

**When to use**: User wants to send templated emails to multiple recipients in one call

**Tool sequence**:
1. `POSTMARK_LIST_TEMPLATES` - Find available templates and their IDs [Prerequisite]
2. `POSTMARK_VALIDATE_TEMPLATE` - Validate template with model data before sending [Optional]
3. `POSTMARK_SEND_BATCH_WITH_TEMPLATES` - Send batch emails using a template [Required]

**Key parameters**:
- `TemplateId` or `TemplateAlias`: Identifier for the template to use
- `Messages`: Array of message objects with `From`, `To`, `TemplateModel`
- `TemplateModel`: Key-value pairs matching template variables

**Pitfalls**:
- Maximum 500 messages per batch call
- Either `TemplateId` or `TemplateAlias` is required, not both
- `TemplateModel` keys must match template variable names exactly (case-sensitive)
- Sender address must be a verified Sender Signature or from a verified domain

### 2. Manage Email Templates

**When to use**: User wants to create, edit, or inspect email templates

**Tool sequence**:
1. `POSTMARK_LIST_TEMPLATES` - List all templates with IDs and names [Required]
2. `POSTMARK_GET_TEMPLATE` - Get full template details including HTML/text body [Optional]
3. `POSTMARK_EDIT_TEMPLATE` - Update template content or settings [Optional]
4. `POSTMARK_VALIDATE_TEMPLATE` - Test template rendering with sample data [Optional]

**Key parameters**:
- `TemplateId`: Numeric template ID for GET/EDIT operations
- `Name`: Template display name
- `Subject`: Email subject line (supports template variables)
- `HtmlBody`: HTML content of the template
- `TextBody`: Plain text fallback content
- `TemplateType`: 'Standard' or 'Layout'

**Pitfalls**:
- Template IDs are numeric integers, not strings
- Editing a template replaces the entire content; include all fields you want to keep
- Layout templates wrap Standard templates; changing a layout affects all linked templates
- Validate before sending to catch missing variables early

### 3. Monitor Delivery Statistics

**When to use**: User wants to check email delivery health, open/click rates, or outbound overview

**Tool sequence**:
1. `POSTMARK_GET_DELIVERY_STATS` - Get bounce counts by type [Required]
2. `POSTMARK_GET_OUTBOUND_OVERVIEW` - Get sent/opened/clicked/bounced summary [Required]
3. `POSTMARK_GET_TRACKED_EMAIL_COUNTS` - Get tracked email volume over time [Optional]

**Key parameters**:
- `fromdate`: Start date for filtering stats (YYYY-MM-DD)
- `todate`: End date for filtering stats (YYYY-MM-DD)
- `tag`: Filter stats by message tag
- `messagestreamid`: Filter by message stream (e.g., 'outbound', 'broadcast')

**Pitfalls**:
- Date parameters use YYYY-MM-DD format without time component
- Stats are aggregated; individual message tracking requires separate API calls
- `messagestreamid` defaults to all streams if not specified

### 4. Manage Bounces and Complaints

**When to use**: User wants to review bounced emails or spam complaints

**Tool sequence**:
1. `POSTMARK_GET_BOUNCES` - List bounced messages with details [Required]
2. `POSTMARK_GET_SPAM_COMPLAINTS` - List spam complaint records [Optional]
3. `POSTMARK_GET_DELIVERY_STATS` - Get bounce summary counts [Optional]

**Key parameters**:
- `count`: Number of records to return per page
- `offset`: Pagination offset for results
- `type`: Bounce type filter (e.g., 'HardBounce', 'SoftBounce', 'SpamNotification')
- `fromdate`/`todate`: Date range filters
- `emailFilter`: Filter by recipient email address

**Pitfalls**:
- Bounce types include: HardBounce, SoftBounce, SpamNotification, SpamComplaint, Transient, and others
- Hard bounces indicate permanent delivery failures; these addresses should be removed
- Spam complaints affect sender reputation; monitor regularly
- Pagination uses `count` and `offset`, not page tokens

### 5. Configure Server Settings

**When to use**: User wants to view or modify Postmark server configuration

**Tool sequence**:
1. `POSTMARK_GET_SERVER` - Retrieve current server settings [Required]
2. `POSTMARK_EDIT_SERVER` - Update server configuration [Optional]

**Key parameters**:
- `Name`: Server display name
- `SmtpApiActivated`: Enable/disable SMTP API access
- `BounceHookUrl`: Webhook URL for bounce notifications
- `InboundHookUrl`: Webhook URL for inbound email processing
- `TrackOpens`: Enable/disable open tracking
- `TrackLinks`: Link tracking mode ('None', 'HtmlAndText', 'HtmlOnly', 'TextOnly')

**Pitfalls**:
- Server edits affect all messages sent through that server
- Webhook URLs must be publicly accessible HTTPS endpoints
- Changing `SmtpApiActivated` affects SMTP relay access immediately
- Track settings apply to future messages only, not retroactively

## Common Patterns

### Template Variable Resolution

```
1. Call POSTMARK_GET_TEMPLATE with TemplateId
2. Inspect HtmlBody/TextBody for {{variable}} placeholders
3. Build TemplateModel dict with matching keys
4. Call POSTMARK_VALIDATE_TEMPLATE to verify rendering
```

### Pagination

- Set `count` for results per page (varies by endpoint)
- Use `offset` to skip previously fetched results
- Increment offset by count each page until results returned < count
- Total records may be returned in response metadata

## Known Pitfalls

**Authentication**:
- Postmark uses server-level API tokens, not account-level
- Each server has its own token; ensure correct server context
- Sender addresses must be verified Sender Signatures or from verified domains

**Rate Limits**:
- Batch send limited to 500 messages per call
- API rate limits vary by endpoint; implement backoff on 429 responses

**Response Parsing**:
- Response data may be nested under `data` or `data.data`
- Parse defensively with fallback patterns
- Template IDs are always numeric integers

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Send batch templated emails | POSTMARK_SEND_BATCH_WITH_TEMPLATES | Messages, TemplateId/TemplateAlias |
| List templates | POSTMARK_LIST_TEMPLATES | Count, Offset, TemplateType |
| Get template details | POSTMARK_GET_TEMPLATE | TemplateId |
| Edit template | POSTMARK_EDIT_TEMPLATE | TemplateId, Name, Subject, HtmlBody |
| Validate template | POSTMARK_VALIDATE_TEMPLATE | TemplateId, TemplateModel |
| Delivery stats | POSTMARK_GET_DELIVERY_STATS | (none or date filters) |
| Outbound overview | POSTMARK_GET_OUTBOUND_OVERVIEW | fromdate, todate, tag |
| Get bounces | POSTMARK_GET_BOUNCES | count, offset, type, emailFilter |
| Get spam complaints | POSTMARK_GET_SPAM_COMPLAINTS | count, offset, fromdate, todate |
| Tracked email counts | POSTMARK_GET_TRACKED_EMAIL_COUNTS | fromdate, todate, tag |
| Get server config | POSTMARK_GET_SERVER | (none) |
| Edit server config | POSTMARK_EDIT_SERVER | Name, TrackOpens, TrackLinks |
