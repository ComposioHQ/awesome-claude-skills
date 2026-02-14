---
name: mailchimp-automation
description: Automate Mailchimp email marketing including campaigns, audiences, subscribers, segments, and analytics via Rube MCP (Composio). Always search tools first for current schemas.
requires:
  mcp: [rube]
---

# Mailchimp Automation via Rube MCP

Automate Mailchimp email marketing workflows including campaign creation and sending, audience/list management, subscriber operations, segmentation, and performance analytics through Composio's Mailchimp toolkit.

**Toolkit docs**: [composio.dev/toolkits/mailchimp](https://composio.dev/toolkits/mailchimp)

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Mailchimp connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `mailchimp`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `mailchimp`
3. If connection is not ACTIVE, follow the returned auth link to complete Mailchimp OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create and Send Email Campaigns

**When to use**: User wants to create, configure, test, and send an email campaign.

**Tool sequence**:
1. `MAILCHIMP_GET_LISTS_INFO` - List available audiences and get list_id [Prerequisite]
2. `MAILCHIMP_ADD_CAMPAIGN` - Create a new campaign with type, audience, subject, from name [Required]
3. `MAILCHIMP_SET_CAMPAIGN_CONTENT` - Set HTML content for the campaign [Required]
4. `MAILCHIMP_SEND_TEST_EMAIL` - Send preview to reviewers before live send [Optional]
5. `MAILCHIMP_SEND_CAMPAIGN` - Send the campaign immediately [Required]
6. `MAILCHIMP_SCHEDULE_CAMPAIGN` - Schedule for future delivery instead of immediate send [Optional]

**Key parameters for MAILCHIMP_ADD_CAMPAIGN**:
- `type`: "regular", "plaintext", "rss", or "variate" (required)
- `recipients__list__id`: Audience/list ID for recipients
- `settings__subject__line`: Email subject line
- `settings__from__name`: Sender display name
- `settings__reply__to`: Reply-to email address (required for sending)
- `settings__title`: Internal campaign title
- `settings__preview__text`: Preview text shown in inbox

**Key parameters for MAILCHIMP_SET_CAMPAIGN_CONTENT**:
- `campaign_id`: Campaign ID from creation step (required)
- `html`: Raw HTML content for the email
- `plain_text`: Plain-text version (auto-generated if omitted)
- `template__id`: Use a pre-built template instead of raw HTML

**Pitfalls**:
- `MAILCHIMP_SEND_CAMPAIGN` is irreversible; always send a test email first and get explicit user approval
- Campaign must be in "save" (draft) status with valid audience, subject, from name, verified email, and content before sending
- `MAILCHIMP_SCHEDULE_CAMPAIGN` requires a valid future datetime; past timestamps fail
- Templates and HTML content must include compliant footer/unsubscribe merge tags
- Mailchimp uses double-underscore notation for nested params (e.g., `settings__subject__line`)

### 2. Manage Audiences and Subscribers

**When to use**: User wants to view audiences, list subscribers, or check subscriber details.

**Tool sequence**:
1. `MAILCHIMP_GET_LISTS_INFO` - List all audiences with member counts [Required]
2. `MAILCHIMP_GET_LIST_INFO` - Get details for a specific audience [Optional]
3. `MAILCHIMP_LIST_MEMBERS_INFO` - List members with status filter and pagination [Required]
4. `MAILCHIMP_SEARCH_MEMBERS` - Search by email or name across lists [Optional]
5. `MAILCHIMP_GET_MEMBER_INFO` - Get detailed profile for a specific subscriber [Optional]
6. `MAILCHIMP_LIST_SEGMENTS` - List segments within an audience [Optional]

**Key parameters for MAILCHIMP_LIST_MEMBERS_INFO**:
- `list_id`: Audience ID (required)
- `status`: "subscribed", "unsubscribed", "cleaned", "pending", "transactional", "archived"
- `count`: Records per page (default 10, max 1000)
- `offset`: Pagination offset (default 0)
- `sort_field`: "timestamp_opt", "timestamp_signup", or "last_changed"
- `fields`: Comma-separated list to limit response size

**Pitfalls**:
- `stats.avg_open_rate` and `stats.avg_click_rate` are 0-1 fractions, NOT 0-100 percentages
- Always use `status="subscribed"` to filter active subscribers; omitting returns all statuses
- Must paginate using `count` and `offset` until collected members match `total_items`
- Large list responses may be truncated; data is under `response.data.members`

### 3. Add and Update Subscribers

**When to use**: User wants to add new subscribers, update existing ones, or bulk-manage list membership.

**Tool sequence**:
1. `MAILCHIMP_GET_LIST_INFO` - Validate target audience exists [Prerequisite]
2. `MAILCHIMP_SEARCH_MEMBERS` - Check if contact already exists [Optional]
3. `MAILCHIMP_ADD_OR_UPDATE_LIST_MEMBER` - Upsert subscriber (create or update) [Required]
4. `MAILCHIMP_ADD_MEMBER_TO_LIST` - Add new subscriber (create only) [Optional]
5. `MAILCHIMP_BATCH_ADD_OR_REMOVE_MEMBERS` - Bulk manage segment membership [Optional]

**Key parameters for MAILCHIMP_ADD_OR_UPDATE_LIST_MEMBER**:
- `list_id`: Audience ID (required)
- `subscriber_hash`: MD5 hash of lowercase email (required)
- `email_address`: Subscriber email (required)
- `status_if_new`: Status for new subscribers: "subscribed", "pending", etc. (required)
- `status`: Status for existing subscribers
- `merge_fields`: Object with merge tag keys (e.g., `{"FNAME": "John", "LNAME": "Doe"}`)
- `tags`: Array of tag strings

**Key parameters for MAILCHIMP_ADD_MEMBER_TO_LIST**:
- `list_id`: Audience ID (required)
- `email_address`: Subscriber email (required)
- `status`: "subscribed", "pending", "unsubscribed", "cleaned", "transactional" (required)

**Pitfalls**:
- `subscriber_hash` must be MD5 of the **lowercase** email; incorrect casing causes 404s or duplicates
- Use `MAILCHIMP_ADD_OR_UPDATE_LIST_MEMBER` (upsert) instead of `MAILCHIMP_ADD_MEMBER_TO_LIST` to avoid duplicate errors
- `status_if_new` determines status only for new contacts; existing contacts use `status`
- Use `skip_merge_validation: true` to bypass required merge field validation
- `MAILCHIMP_BATCH_ADD_OR_REMOVE_MEMBERS` manages static segment membership, not list membership

### 4. View Campaign Reports and Analytics

**When to use**: User wants to review campaign performance, open rates, click rates, or subscriber engagement.

**Tool sequence**:
1. `MAILCHIMP_LIST_CAMPAIGNS` - List sent campaigns with report summaries [Required]
2. `MAILCHIMP_SEARCH_CAMPAIGNS` - Find campaigns by name, subject, or content [Optional]
3. `MAILCHIMP_GET_CAMPAIGN_REPORT` - Get detailed performance report for a campaign [Required]
4. `MAILCHIMP_LIST_CAMPAIGN_REPORTS` - Bulk fetch reports across multiple campaigns [Optional]
5. `MAILCHIMP_LIST_CAMPAIGN_DETAILS` - Get link-level click statistics [Optional]
6. `MAILCHIMP_GET_CAMPAIGN_LINK_DETAILS` - Drill into specific link click data [Optional]
7. `MAILCHIMP_LIST_CLICKED_LINK_SUBSCRIBERS` - See who clicked a specific link [Optional]
8. `MAILCHIMP_GET_SUBSCRIBER_EMAIL_ACTIVITY` - Get per-subscriber campaign activity [Optional]
9. `MAILCHIMP_GET_CAMPAIGN_CONTENT` - Retrieve campaign HTML content [Optional]

**Key parameters for MAILCHIMP_LIST_CAMPAIGNS**:
- `status`: "save", "paused", "schedule", "sending", "sent"
- `count` / `offset`: Pagination (default 10, max 1000)
- `since_send_time` / `before_send_time`: ISO 8601 date range filter
- `sort_field`: "create_time" or "send_time"
- `fields`: Limit response fields for performance

**Key parameters for MAILCHIMP_GET_CAMPAIGN_REPORT**:
- `campaign_id`: Campaign ID (required)
- Returns: opens, clicks, bounces, unsubscribes, timeseries, industry_stats

**Pitfalls**:
- `MAILCHIMP_LIST_CAMPAIGNS` only returns high-level `report_summary`; use `MAILCHIMP_GET_CAMPAIGN_REPORT` for detailed metrics
- Draft/unsent campaigns lack meaningful report data
- When using `fields` parameter on LIST_CAMPAIGNS, explicitly request `send_time` and `report_summary` subfields
- Pagination defaults are low (10 records); iterate with `count` and `offset` until `total_items` is covered
- `send_time` is ISO 8601 with timezone; parse carefully

## Common Patterns

### ID Resolution
Always resolve names to IDs before operations:
- **Audience name -> list_id**: `MAILCHIMP_GET_LISTS_INFO` and match by name
- **Subscriber email -> subscriber_hash**: Compute MD5 of lowercase email in code
- **Campaign name -> campaign_id**: `MAILCHIMP_SEARCH_CAMPAIGNS` with query
- **Segment name -> segment_id**: `MAILCHIMP_LIST_SEGMENTS` with list_id

### Pagination
Mailchimp uses offset-based pagination:
- Use `count` (page size, max 1000) and `offset` (skip N records)
- Continue until collected records match `total_items` from the response
- Default `count` is 10; always set explicitly for bulk operations
- Search endpoints max at 10 pages (300 results for 30/page)

### Subscriber Hash
Many endpoints require `subscriber_hash` (MD5 of lowercase email):
```
import hashlib
subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
```

## Known Pitfalls

### ID Formats
- `list_id` (audience ID) is a short alphanumeric string (e.g., "abc123def4")
- `campaign_id` is an alphanumeric string
- `subscriber_hash` is an MD5 hex string (32 characters)
- Segment IDs are integers

### Rate Limits
- Mailchimp enforces API rate limits; use batching for bulk subscriber operations
- High-volume use of GET_MEMBER_INFO and ADD_OR_UPDATE_LIST_MEMBER can trigger throttling
- Use `MAILCHIMP_BATCH_ADD_OR_REMOVE_MEMBERS` for bulk segment operations

### Parameter Quirks
- Nested parameters use double-underscore notation: `settings__subject__line`, `recipients__list__id`
- `avg_open_rate` and `avg_click_rate` are 0-1 fractions, not percentages
- `status_if_new` only applies to new contacts in upsert operations
- `subscriber_hash` must be MD5 of lowercase email; wrong casing creates phantom records
- Campaign `type` is required for creation; most common is "regular"
- `MAILCHIMP_SEND_CAMPAIGN` returns HTTP 204 on success (no body)

### Content and Compliance
- Campaign HTML must include unsubscribe link and physical address (merge tags)
- Content must be set via `MAILCHIMP_SET_CAMPAIGN_CONTENT` before sending
- Test emails require campaign to have content already set

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List audiences | `MAILCHIMP_GET_LISTS_INFO` | `count`, `offset` |
| Get audience details | `MAILCHIMP_GET_LIST_INFO` | `list_id` |
| Create campaign | `MAILCHIMP_ADD_CAMPAIGN` | `type`, `recipients__list__id`, `settings__subject__line` |
| Set campaign content | `MAILCHIMP_SET_CAMPAIGN_CONTENT` | `campaign_id`, `html` |
| Send test email | `MAILCHIMP_SEND_TEST_EMAIL` | `campaign_id`, `test_emails` |
| Send campaign | `MAILCHIMP_SEND_CAMPAIGN` | `campaign_id` |
| Schedule campaign | `MAILCHIMP_SCHEDULE_CAMPAIGN` | `campaign_id`, `schedule_time` |
| Get campaign info | `MAILCHIMP_GET_CAMPAIGN_INFO` | `campaign_id` |
| Search campaigns | `MAILCHIMP_SEARCH_CAMPAIGNS` | `query` |
| List campaigns | `MAILCHIMP_LIST_CAMPAIGNS` | `status`, `count`, `offset` |
| Replicate campaign | `MAILCHIMP_REPLICATE_CAMPAIGN` | `campaign_id` |
| List subscribers | `MAILCHIMP_LIST_MEMBERS_INFO` | `list_id`, `status`, `count`, `offset` |
| Search members | `MAILCHIMP_SEARCH_MEMBERS` | `query`, `list_id` |
| Get member info | `MAILCHIMP_GET_MEMBER_INFO` | `list_id`, `subscriber_hash` |
| Add subscriber | `MAILCHIMP_ADD_MEMBER_TO_LIST` | `list_id`, `email_address`, `status` |
| Upsert subscriber | `MAILCHIMP_ADD_OR_UPDATE_LIST_MEMBER` | `list_id`, `subscriber_hash`, `email_address`, `status_if_new` |
| Batch members | `MAILCHIMP_BATCH_ADD_OR_REMOVE_MEMBERS` | `list_id`, `segment_id` |
| List segments | `MAILCHIMP_LIST_SEGMENTS` | `list_id` |
| Campaign report | `MAILCHIMP_GET_CAMPAIGN_REPORT` | `campaign_id` |
| All reports | `MAILCHIMP_LIST_CAMPAIGN_REPORTS` | `count`, `offset` |
| Link click details | `MAILCHIMP_LIST_CAMPAIGN_DETAILS` | `campaign_id`, `count` |
| Subscriber activity | `MAILCHIMP_GET_SUBSCRIBER_EMAIL_ACTIVITY` | `campaign_id`, `subscriber_hash` |
| Member recent activity | `MAILCHIMP_VIEW_RECENT_ACTIVITY` | `list_id`, `subscriber_hash` |
| Campaign content | `MAILCHIMP_GET_CAMPAIGN_CONTENT` | `campaign_id` |

---
*Powered by [Composio](https://composio.dev)*
