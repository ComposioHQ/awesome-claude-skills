---
name: outlook-automation
description: "Automate Outlook tasks via Rube MCP (Composio): emails, calendar, contacts, folders, attachments. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Outlook Automation via Rube MCP

Automate Microsoft Outlook operations through Composio's Outlook toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Outlook connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `outlook`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `outlook`
3. If connection is not ACTIVE, follow the returned auth link to complete Microsoft OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Search and Filter Emails

**When to use**: User wants to find specific emails across their mailbox

**Tool sequence**:
1. `OUTLOOK_SEARCH_MESSAGES` - Search with KQL syntax across all folders [Required]
2. `OUTLOOK_GET_MESSAGE` - Get full message details [Optional]
3. `OUTLOOK_LIST_OUTLOOK_ATTACHMENTS` - List message attachments [Optional]
4. `OUTLOOK_DOWNLOAD_OUTLOOK_ATTACHMENT` - Download attachment [Optional]

**Key parameters**:
- `query`: KQL search string (from:, to:, subject:, received:, hasattachment:)
- `from_index`: Pagination start (0-based)
- `size`: Results per page (max 25)
- `message_id`: Message ID (use hitId from search results)

**Pitfalls**:
- Only works with Microsoft 365/Enterprise accounts (not @hotmail.com/@outlook.com)
- Pagination relies on hitsContainers[0].moreResultsAvailable; stop only when false
- Use hitId from search results as message_id for downstream calls, not resource.id
- Index latency: very recent emails may not appear immediately
- Inline images appear as attachments; filter by mimetype for real documents

### 2. Query Emails in a Folder

**When to use**: User wants to list emails in a specific folder with OData filters

**Tool sequence**:
1. `OUTLOOK_LIST_MAIL_FOLDERS` - List mail folders to get folder IDs [Prerequisite]
2. `OUTLOOK_QUERY_EMAILS` - Query emails with structured filters [Required]

**Key parameters**:
- `folder`: Folder name ('inbox', 'sentitems', 'drafts') or folder ID
- `filter`: OData filter (e.g., `isRead eq false and importance eq 'high'`)
- `top`: Max results (1-1000)
- `orderby`: Sort field and direction
- `select`: Array of fields to return

**Pitfalls**:
- QUERY_EMAILS searches a SINGLE folder only; use SEARCH_MESSAGES for cross-folder search
- Custom folders require folder IDs, not display names; use LIST_MAIL_FOLDERS
- Always check response['@odata.nextLink'] for pagination
- Cannot filter by recipient or body content; use SEARCH_MESSAGES for that

### 3. Manage Calendar Events

**When to use**: User wants to list, search, or inspect calendar events

**Tool sequence**:
1. `OUTLOOK_LIST_EVENTS` - List events with filters [Optional]
2. `OUTLOOK_GET_CALENDAR_VIEW` - Get events in a time window [Optional]
3. `OUTLOOK_GET_EVENT` - Get specific event details [Optional]
4. `OUTLOOK_LIST_CALENDARS` - List available calendars [Optional]
5. `OUTLOOK_GET_SCHEDULE` - Get free/busy info [Optional]

**Key parameters**:
- `filter`: OData filter (use start/dateTime, NOT receivedDateTime)
- `start_datetime`/`end_datetime`: ISO 8601 for calendar view
- `timezone`: IANA timezone (e.g., 'America/New_York')
- `calendar_id`: Optional non-primary calendar ID
- `select`: Fields to return

**Pitfalls**:
- Use calendar event properties only (start/dateTime, end/dateTime), NOT email properties (receivedDateTime)
- Calendar view requires start_datetime and end_datetime
- Recurring events need `expand_recurring_events=true` to see individual occurrences
- Decline status is per-attendee via attendees[].status.response

### 4. Manage Contacts

**When to use**: User wants to list, create, or organize contacts

**Tool sequence**:
1. `OUTLOOK_LIST_CONTACTS` - List contacts [Optional]
2. `OUTLOOK_CREATE_CONTACT` - Create a new contact [Optional]
3. `OUTLOOK_GET_CONTACT_FOLDERS` - List contact folders [Optional]
4. `OUTLOOK_CREATE_CONTACT_FOLDER` - Create contact folder [Optional]

**Key parameters**:
- `givenName`/`surname`: Contact name
- `emailAddresses`: Array of email objects
- `displayName`: Full display name
- `contact_folder_id`: Optional folder for contacts

**Pitfalls**:
- Contact creation supports many fields but only givenName or surname is needed

### 5. Manage Mail Folders

**When to use**: User wants to organize mail folders

**Tool sequence**:
1. `OUTLOOK_LIST_MAIL_FOLDERS` - List top-level folders [Required]
2. `OUTLOOK_LIST_CHILD_MAIL_FOLDERS` - List subfolders [Optional]
3. `OUTLOOK_CREATE_MAIL_FOLDER` - Create a new folder [Optional]

**Key parameters**:
- `parent_folder_id`: Well-known name or folder ID
- `displayName`: New folder name
- `include_hidden_folders`: Show hidden folders

**Pitfalls**:
- Well-known folder names: 'inbox', 'sentitems', 'drafts', 'deleteditems', 'junkemail', 'archive'
- Custom folder operations require the folder ID, not display name

## Common Patterns

### KQL Search Syntax

**Property filters**:
- `from:user@example.com` - From sender
- `to:recipient@example.com` - To recipient
- `subject:invoice` - Subject contains
- `received>=2025-01-01` - Date filter
- `hasattachment:yes` - Has attachments

**Combinators**:
- `AND` - Both conditions
- `OR` - Either condition
- Parentheses for grouping

### OData Filter Syntax

**Email filters**:
- `isRead eq false` - Unread emails
- `importance eq 'high'` - High importance
- `hasAttachments eq true` - Has attachments
- `receivedDateTime ge 2025-01-01T00:00:00Z` - Date filter

**Calendar filters**:
- `start/dateTime ge '2025-01-01T00:00:00Z'` - Events after date
- `contains(subject, 'Meeting')` - Subject contains text

## Known Pitfalls

**Account Types**:
- SEARCH_MESSAGES requires Microsoft 365/Enterprise accounts
- Personal accounts (@hotmail.com, @outlook.com) have limited API access

**Field Confusion**:
- Email properties (receivedDateTime) differ from calendar properties (start/dateTime)
- Do NOT use email fields in calendar queries or vice versa

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Search emails | OUTLOOK_SEARCH_MESSAGES | query, from_index, size |
| Query folder | OUTLOOK_QUERY_EMAILS | folder, filter, top |
| Get message | OUTLOOK_GET_MESSAGE | message_id |
| List attachments | OUTLOOK_LIST_OUTLOOK_ATTACHMENTS | message_id |
| Download attachment | OUTLOOK_DOWNLOAD_OUTLOOK_ATTACHMENT | message_id, attachment_id |
| List folders | OUTLOOK_LIST_MAIL_FOLDERS | (none) |
| Child folders | OUTLOOK_LIST_CHILD_MAIL_FOLDERS | parent_folder_id |
| List events | OUTLOOK_LIST_EVENTS | filter, timezone |
| Calendar view | OUTLOOK_GET_CALENDAR_VIEW | start_datetime, end_datetime |
| Get event | OUTLOOK_GET_EVENT | event_id |
| List calendars | OUTLOOK_LIST_CALENDARS | (none) |
| Free/busy | OUTLOOK_GET_SCHEDULE | schedules, times |
| List contacts | OUTLOOK_LIST_CONTACTS | top, filter |
| Create contact | OUTLOOK_CREATE_CONTACT | givenName, emailAddresses |
| Contact folders | OUTLOOK_GET_CONTACT_FOLDERS | (none) |
