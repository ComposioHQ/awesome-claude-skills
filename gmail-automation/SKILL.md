---
name: gmail-automation
description: "Automate Gmail tasks via Rube MCP (Composio): send/reply, search, labels, drafts, attachments. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Gmail Automation via Rube MCP

Automate Gmail operations through Composio's Gmail toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Gmail connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `gmail`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `gmail`
3. If connection is not ACTIVE, follow the returned auth link to complete Google OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Send an Email

**When to use**: User wants to compose and send a new email

**Tool sequence**:
1. `GMAIL_SEARCH_PEOPLE` - Resolve contact name to email address [Optional]
2. `GMAIL_SEND_EMAIL` - Send the email [Required]

**Key parameters**:
- `recipient_email`: Email address or 'me' for self
- `subject`: Email subject line
- `body`: Email content (plain text or HTML)
- `is_html`: Must be `true` if body contains HTML markup
- `cc`/`bcc`: Arrays of email addresses
- `attachment`: Object with `{s3key, mimetype, name}` from prior download

**Pitfalls**:
- At least one of `recipient_email`, `cc`, or `bcc` required
- At least one of `subject` or `body` required
- Attachment `mimetype` MUST contain '/' (e.g., 'application/pdf', not 'pdf')
- Total message size limit ~25MB after base64 encoding
- Use `from_email` only for verified aliases in Gmail 'Send mail as' settings

### 2. Reply to a Thread

**When to use**: User wants to reply to an existing email conversation

**Tool sequence**:
1. `GMAIL_FETCH_EMAILS` - Find the email/thread to reply to [Prerequisite]
2. `GMAIL_REPLY_TO_THREAD` - Send reply within the thread [Required]

**Key parameters**:
- `thread_id`: Hex string from FETCH_EMAILS (e.g., '169eefc8138e68ca')
- `message_body`: Reply content
- `recipient_email`: Reply recipient
- `is_html`: Set `true` for HTML content

**Pitfalls**:
- `thread_id` must be hex string; prefixes like 'msg-f:' are auto-stripped
- Legacy Gmail web UI IDs (e.g., 'FMfcgz...') are NOT supported
- Subject is inherited from original thread; setting it creates a new thread instead
- Do NOT include subject parameter to stay within thread

### 3. Search and Filter Emails

**When to use**: User wants to find specific emails by sender, subject, date, label, etc.

**Tool sequence**:
1. `GMAIL_FETCH_EMAILS` - Search with Gmail query syntax [Required]
2. `GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID` - Get full message details for selected results [Optional]

**Key parameters**:
- `query`: Gmail search syntax (from:, to:, subject:, is:unread, has:attachment, after:YYYY/MM/DD, before:YYYY/MM/DD)
- `max_results`: 1-500 messages per page
- `label_ids`: System IDs like 'INBOX', 'UNREAD'
- `include_payload`: Set `true` to get full message content
- `ids_only`: Set `true` for just message IDs
- `page_token`: For pagination (from `nextPageToken`)

**Pitfalls**:
- Returns max ~500 per page; follow `nextPageToken` via `page_token` until absent
- `resultSizeEstimate` is approximate, not exact count
- Use 'is:' for states (is:unread, is:snoozed, is:starred)
- Use 'label:' ONLY for user-created labels
- Common mistake: 'label:snoozed' is WRONG — use 'is:snoozed'
- `include_payload=true` on broad searches creates huge responses; default to metadata
- Custom labels require label ID (e.g., 'Label_123'), NOT label name

### 4. Manage Labels

**When to use**: User wants to create, modify, or organize labels

**Tool sequence**:
1. `GMAIL_LIST_LABELS` - List all labels to find IDs and detect conflicts [Required]
2. `GMAIL_CREATE_LABEL` - Create a new label [Optional]
3. `GMAIL_PATCH_LABEL` - Rename or change label colors/visibility [Optional]
4. `GMAIL_DELETE_LABEL` - Delete a user-created label (irreversible) [Optional]

**Key parameters**:
- `label_name`: Max 225 chars, no commas, '/' for nesting (e.g., 'Work/Projects')
- `background_color`/`text_color`: Hex values from Gmail's predefined palette
- `id`: Label ID for PATCH/DELETE operations

**Pitfalls**:
- 400/409 error if name is blank, duplicate, or reserved (INBOX, SPAM, CATEGORY_*)
- Color specs must use Gmail's predefined palette of 102 hex values
- DELETE is permanent and removes label from all messages
- Cannot delete system labels (INBOX, SENT, DRAFT, etc.)

### 5. Apply/Remove Labels on Messages

**When to use**: User wants to label, archive, or mark emails as read/unread

**Tool sequence**:
1. `GMAIL_LIST_LABELS` - Get label IDs for custom labels [Prerequisite]
2. `GMAIL_FETCH_EMAILS` - Find target messages [Prerequisite]
3. `GMAIL_BATCH_MODIFY_MESSAGES` - Bulk add/remove labels (up to 1000 messages) [Required]
4. `GMAIL_ADD_LABEL_TO_EMAIL` - Single-message label changes [Fallback]

**Key parameters**:
- `messageIds`: Array of message IDs (max 1000)
- `addLabelIds`: Array of label IDs to add
- `removeLabelIds`: Array of label IDs to remove
- `message_id`: 15-16 char hex string for single operations

**Pitfalls**:
- Max 1000 messageIds per BATCH call; chunk larger sets
- Use 'CATEGORY_UPDATES' not 'UPDATES'; full prefix required for category labels
- SENT, DRAFT, CHAT are immutable — cannot be added/removed
- To mark as read: REMOVE 'UNREAD'. To archive: REMOVE 'INBOX'
- `message_id` must be 15-16 char hex, NOT UUIDs or web UI IDs

### 6. Handle Drafts and Attachments

**When to use**: User wants to create, edit, or send email drafts, possibly with attachments

**Tool sequence**:
1. `GMAIL_CREATE_EMAIL_DRAFT` - Create a new draft [Required]
2. `GMAIL_UPDATE_DRAFT` - Edit draft content [Optional]
3. `GMAIL_LIST_DRAFTS` - List existing drafts [Optional]
4. `GMAIL_SEND_DRAFT` - Send a draft (requires explicit user approval) [Optional]
5. `GMAIL_GET_ATTACHMENT` - Download attachment from existing message [Optional]

**Key parameters**:
- `recipient_email`: Draft recipient
- `subject`: Draft subject (omit for reply drafts to stay in thread)
- `body`: Draft content
- `is_html`: Set `true` for HTML content
- `attachment`: Object with `{s3key, mimetype, name}`
- `thread_id`: For reply drafts (leave subject empty to stay in thread)

**Pitfalls**:
- Response includes `data.id` (draft_id) AND `data.message.id`; use `data.id` for draft operations
- Setting subject on a thread reply draft creates a NEW thread instead
- Attachment capped at ~25MB; base64 overhead can push near-limit files over
- UPDATE_DRAFT replaces entire content, not patches; include all fields you want to keep
- HTTP 429 on bulk draft creation; use exponential backoff

## Common Patterns

### ID Resolution

**Label name → Label ID**:
```
1. Call GMAIL_LIST_LABELS
2. Find label by name in response
3. Extract id field (e.g., 'Label_123')
```

**Contact name → Email**:
```
1. Call GMAIL_SEARCH_PEOPLE with query=contact_name
2. Extract emailAddresses from response
```

**Thread ID from search**:
```
1. Call GMAIL_FETCH_EMAILS or GMAIL_LIST_THREADS
2. Extract threadId (15-16 char hex string)
```

### Pagination

- Set `max_results` up to 500 per page
- Check response for `nextPageToken`
- Pass token as `page_token` in next request
- Continue until `nextPageToken` is absent or empty string
- `resultSizeEstimate` is approximate, not exact

### Gmail Query Syntax

**Operators**:
- `from:sender@example.com` - Emails from sender
- `to:recipient@example.com` - Emails to recipient
- `subject:"exact phrase"` - Subject contains exact phrase
- `is:unread` - Unread messages
- `is:starred` - Starred messages
- `is:snoozed` - Snoozed messages
- `has:attachment` - Has attachments
- `after:2024/01/01` - After date (YYYY/MM/DD)
- `before:2024/12/31` - Before date
- `label:custom_label` - User-created label (use label ID)
- `in:sent` - In sent folder
- `category:primary` - Primary category

**Combinators**:
- `AND` - Both conditions (default)
- `OR` - Either condition
- `NOT` - Exclude condition
- `()` - Group conditions

**Examples**:
- `from:boss@company.com is:unread` - Unread emails from boss
- `subject:invoice has:attachment after:2024/01/01` - Invoices with attachments this year
- `(from:alice OR from:bob) is:starred` - Starred emails from Alice or Bob

## Known Pitfalls

**ID Formats**:
- Custom label operations require label IDs (e.g., 'Label_123'), not display names
- Always call LIST_LABELS first to resolve names to IDs
- Message IDs are 15-16 char hex strings
- Do NOT use UUIDs, web UI IDs, or 'thread-f:' prefixes

**Query Syntax**:
- Use 'is:' for states (unread, snoozed, starred)
- Use 'label:' ONLY for user-created labels
- System labels use 'is:' or 'in:' (e.g., 'is:sent', 'in:inbox')

**Rate Limits**:
- BATCH_MODIFY_MESSAGES max 1000 messages per call
- Heavy use triggers 403/429 rate limits
- Implement exponential backoff for bulk operations

**Response Parsing**:
- Response data may be nested under `data_preview` or `data.messages`
- Parse defensively with fallbacks
- Timestamp `messageTimestamp` uses RFC3339 with 'Z' suffix
- Normalize to '+00:00' for parsing if needed

**Attachments**:
- Attachment `s3key` from prior download may expire
- Use promptly after retrieval
- Mimetype must include '/' separator

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Send email | GMAIL_SEND_EMAIL | recipient_email, subject, body, is_html |
| Reply to thread | GMAIL_REPLY_TO_THREAD | thread_id, message_body, recipient_email |
| Search emails | GMAIL_FETCH_EMAILS | query, max_results, label_ids, page_token |
| Get message details | GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID | message_id |
| List labels | GMAIL_LIST_LABELS | (none) |
| Create label | GMAIL_CREATE_LABEL | label_name, background_color, text_color |
| Modify labels bulk | GMAIL_BATCH_MODIFY_MESSAGES | messageIds, addLabelIds, removeLabelIds |
| Create draft | GMAIL_CREATE_EMAIL_DRAFT | recipient_email, subject, body, thread_id |
| Send draft | GMAIL_SEND_DRAFT | draft_id |
| Get attachment | GMAIL_GET_ATTACHMENT | message_id, attachment_id |
| Search contacts | GMAIL_SEARCH_PEOPLE | query |
| Get profile | GMAIL_GET_PROFILE | (none) |