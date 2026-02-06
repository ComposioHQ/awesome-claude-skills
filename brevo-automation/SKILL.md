---
name: brevo-automation
description: "Automate Brevo (Sendinblue) tasks via Rube MCP (Composio): manage email campaigns, create/edit templates, track senders, and monitor campaign performance. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Brevo Automation via Rube MCP

Automate Brevo (formerly Sendinblue) email marketing operations through Composio's Brevo toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Brevo connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `brevo`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `brevo`
3. If connection is not ACTIVE, follow the returned auth link to complete Brevo authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Manage Email Campaigns

**When to use**: User wants to list, review, or update email campaigns

**Tool sequence**:
1. `BREVO_LIST_EMAIL_CAMPAIGNS` - List all campaigns with filters [Required]
2. `BREVO_UPDATE_EMAIL_CAMPAIGN` - Update campaign content or settings [Optional]

**Key parameters for listing**:
- `type`: Campaign type ('classic' or 'trigger')
- `status`: Campaign status ('suspended', 'archive', 'sent', 'queued', 'draft', 'inProcess', 'inReview')
- `startDate`/`endDate`: Date range filter (YYYY-MM-DDTHH:mm:ss.SSSZ format)
- `statistics`: Stats type to include ('globalStats', 'linksStats', 'statsByDomain')
- `limit`: Results per page (max 100, default 50)
- `offset`: Pagination offset
- `sort`: Sort order ('asc' or 'desc')
- `excludeHtmlContent`: Set `true` to reduce response size

**Key parameters for update**:
- `campaign_id`: Numeric campaign ID (required)
- `name`: Campaign name
- `subject`: Email subject line
- `htmlContent`: HTML email body (mutually exclusive with `htmlUrl`)
- `htmlUrl`: URL to HTML content
- `sender`: Sender object with `name`, `email`, or `id`
- `recipients`: Object with `listIds` and `exclusionListIds`
- `scheduledAt`: Scheduled send time (YYYY-MM-DDTHH:mm:ss.SSSZ)

**Pitfalls**:
- `startDate` and `endDate` are mutually required; provide both or neither
- Date filters only work when `status` is not passed or set to 'sent'
- `htmlContent` and `htmlUrl` are mutually exclusive
- Campaign `sender` email must be a verified sender in Brevo
- A/B testing fields (`subjectA`, `subjectB`, `splitRule`, `winnerCriteria`) require `abTesting: true`
- `scheduledAt` uses full ISO 8601 format with timezone

### 2. Create and Manage Email Templates

**When to use**: User wants to create, edit, list, or delete email templates

**Tool sequence**:
1. `BREVO_GET_ALL_EMAIL_TEMPLATES` - List all templates [Required]
2. `BREVO_CREATE_OR_UPDATE_EMAIL_TEMPLATE` - Create a new template or update existing [Required]
3. `BREVO_DELETE_EMAIL_TEMPLATE` - Delete an inactive template [Optional]

**Key parameters for listing**:
- `templateStatus`: Filter active (`true`) or inactive (`false`) templates
- `limit`: Results per page (max 1000, default 50)
- `offset`: Pagination offset
- `sort`: Sort order ('asc' or 'desc')

**Key parameters for create/update**:
- `templateId`: Include to update; omit to create new
- `templateName`: Template display name (required for creation)
- `subject`: Email subject line (required for creation)
- `htmlContent`: HTML template body (min 10 characters; use this or `htmlUrl`)
- `sender`: Sender object with `name` and `email`, or `id` (required for creation)
- `replyTo`: Reply-to email address
- `isActive`: Activate or deactivate the template
- `tag`: Category tag for the template

**Pitfalls**:
- When `templateId` is provided, the tool updates; when omitted, it creates
- For creation, `templateName`, `subject`, and `sender` are required
- `htmlContent` must be at least 10 characters
- Template personalization uses `{{contact.ATTRIBUTE}}` syntax
- Only inactive templates can be deleted
- `htmlContent` and `htmlUrl` are mutually exclusive

### 3. Manage Senders

**When to use**: User wants to view authorized sender identities

**Tool sequence**:
1. `BREVO_GET_ALL_SENDERS` - List all verified senders [Required]

**Key parameters**: (none required)

**Pitfalls**:
- Senders must be verified before they can be used in campaigns or templates
- Sender verification is done through the Brevo web interface, not via API
- Sender IDs can be used in `sender.id` fields for campaigns and templates

### 4. Configure A/B Testing Campaigns

**When to use**: User wants to set up or modify A/B test settings on a campaign

**Tool sequence**:
1. `BREVO_LIST_EMAIL_CAMPAIGNS` - Find the target campaign [Prerequisite]
2. `BREVO_UPDATE_EMAIL_CAMPAIGN` - Configure A/B test settings [Required]

**Key parameters**:
- `campaign_id`: Campaign to configure
- `abTesting`: Set to `true` to enable A/B testing
- `subjectA`: Subject line for variant A
- `subjectB`: Subject line for variant B
- `splitRule`: Percentage split for the test (1-99)
- `winnerCriteria`: 'open' or 'click' for determining the winner
- `winnerDelay`: Hours to wait before selecting winner (1-168)

**Pitfalls**:
- A/B testing must be enabled (`abTesting: true`) before setting variant fields
- `splitRule` is the percentage of contacts that receive variant A
- `winnerDelay` defines how long to test before sending the winner to remaining contacts
- Only works with 'classic' campaign type

## Common Patterns

### Campaign Lifecycle

```
1. Create campaign (status: draft)
2. Set recipients (listIds)
3. Configure content (htmlContent or htmlUrl)
4. Optionally schedule (scheduledAt)
5. Send or schedule via Brevo UI (API update can set scheduledAt)
```

### Pagination

- Use `limit` (page size) and `offset` (starting index)
- Default limit is 50; max varies by endpoint (100 for campaigns, 1000 for templates)
- Increment `offset` by `limit` each page
- Check `count` in response to determine total available

### Template Personalization

```
- First name: {{contact.FIRSTNAME}}
- Last name: {{contact.LASTNAME}}
- Custom attribute: {{contact.CUSTOM_ATTRIBUTE}}
- Mirror link: {{mirror}}
- Unsubscribe link: {{unsubscribe}}
```

## Known Pitfalls

**Date Formats**:
- All dates use ISO 8601 with milliseconds: YYYY-MM-DDTHH:mm:ss.SSSZ
- Pass timezone in the date-time format for accurate results
- `startDate` and `endDate` must be used together

**Sender Verification**:
- All sender emails must be verified in Brevo before use
- Unverified senders cause campaign creation/update failures
- Use GET_ALL_SENDERS to check available verified senders

**Rate Limits**:
- Brevo API has rate limits per account plan
- Implement backoff on 429 responses
- Template operations have lower limits than read operations

**Response Parsing**:
- Response data may be nested under `data` or `data.data`
- Parse defensively with fallback patterns
- Campaign and template IDs are numeric integers

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List campaigns | BREVO_LIST_EMAIL_CAMPAIGNS | type, status, limit, offset |
| Update campaign | BREVO_UPDATE_EMAIL_CAMPAIGN | campaign_id, subject, htmlContent |
| List templates | BREVO_GET_ALL_EMAIL_TEMPLATES | templateStatus, limit, offset |
| Create template | BREVO_CREATE_OR_UPDATE_EMAIL_TEMPLATE | templateName, subject, htmlContent, sender |
| Update template | BREVO_CREATE_OR_UPDATE_EMAIL_TEMPLATE | templateId, htmlContent |
| Delete template | BREVO_DELETE_EMAIL_TEMPLATE | templateId |
| List senders | BREVO_GET_ALL_SENDERS | (none) |
