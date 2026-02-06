---
name: close-automation
description: "Automate Close CRM tasks via Rube MCP (Composio): create leads, manage calls/SMS, handle tasks, and track notes. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Close CRM Automation via Rube MCP

Automate Close CRM operations through Composio's Close toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Close connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `close`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `close`
3. If connection is not ACTIVE, follow the returned auth link to complete Close API authentication
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create and Manage Leads

**When to use**: User wants to create new leads or manage existing lead records

**Tool sequence**:
1. `CLOSE_CREATE_LEAD` - Create a new lead in Close [Required]

**Key parameters**:
- `name`: Lead/company name
- `contacts`: Array of contact objects associated with the lead
- `custom`: Custom field values as key-value pairs
- `status_id`: Lead status ID

**Pitfalls**:
- Leads in Close represent companies/organizations, not individual people
- Contacts are nested within leads; create the lead first, then contacts are included
- Custom field keys use the custom field ID (e.g., 'custom.cf_XXX'), not display names
- Duplicate lead detection is not automatic; check before creating

### 2. Log Calls

**When to use**: User wants to log a phone call activity against a lead

**Tool sequence**:
1. `CLOSE_CREATE_CALL` - Log a call activity [Required]

**Key parameters**:
- `lead_id`: ID of the associated lead
- `contact_id`: ID of the contact called
- `direction`: 'outbound' or 'inbound'
- `status`: Call status ('completed', 'no-answer', 'busy', etc.)
- `duration`: Call duration in seconds
- `note`: Call notes

**Pitfalls**:
- lead_id is required; calls must be associated with a lead
- Duration is in seconds, not minutes
- Call direction affects reporting and analytics
- contact_id is optional but recommended for tracking

### 3. Send SMS Messages

**When to use**: User wants to send or log SMS messages through Close

**Tool sequence**:
1. `CLOSE_CREATE_SMS` - Send or log an SMS message [Required]

**Key parameters**:
- `lead_id`: ID of the associated lead
- `contact_id`: ID of the contact
- `direction`: 'outbound' or 'inbound'
- `text`: SMS message content
- `status`: Message status

**Pitfalls**:
- SMS functionality requires Close phone/SMS integration to be configured
- lead_id is required for all SMS activities
- Outbound SMS may require a verified sending number
- Message length limits may apply depending on carrier

### 4. Manage Tasks

**When to use**: User wants to create or manage follow-up tasks

**Tool sequence**:
1. `CLOSE_CREATE_TASK` - Create a new task [Required]

**Key parameters**:
- `lead_id`: Associated lead ID
- `text`: Task description
- `date`: Due date for the task
- `assigned_to`: User ID of the assignee
- `is_complete`: Whether the task is completed

**Pitfalls**:
- Tasks are associated with leads, not contacts
- Date format should follow ISO 8601
- assigned_to requires the Close user ID, not email or name
- Tasks without a date appear in the 'no due date' section

### 5. Manage Notes

**When to use**: User wants to add or retrieve notes on leads

**Tool sequence**:
1. `CLOSE_GET_NOTE` - Retrieve a specific note [Required]

**Key parameters**:
- `note_id`: ID of the note to retrieve

**Pitfalls**:
- Notes are associated with leads
- Note IDs are required for retrieval; search leads first to find note references
- Notes support plain text and basic formatting

### 6. Delete Activities

**When to use**: User wants to remove call records or other activities

**Tool sequence**:
1. `CLOSE_DELETE_CALL` - Delete a call activity [Required]

**Key parameters**:
- `call_id`: ID of the call to delete

**Pitfalls**:
- Deletion is permanent and cannot be undone
- Only the call creator or admin can delete calls
- Deleting a call removes it from all reports and timelines

## Common Patterns

### Lead and Contact Relationship

```
Close data model:
- Lead = Company/Organization
  - Contact = Person (nested within Lead)
  - Activity = Call, SMS, Email, Note (linked to Lead)
  - Task = Follow-up item (linked to Lead)
  - Opportunity = Deal (linked to Lead)
```

### ID Resolution

**Lead ID**:
```
1. Search for leads using the Close search API
2. Extract lead_id from results (format: 'lead_XXXXXXXXXXXXX')
3. Use lead_id in all activity creation calls
```

**Contact ID**:
```
1. Retrieve lead details to get nested contacts
2. Extract contact_id (format: 'cont_XXXXXXXXXXXXX')
3. Use in call/SMS activities for accurate tracking
```

### Activity Logging Pattern

```
1. Identify the lead_id and optionally contact_id
2. Create the activity (call, SMS, note) with lead_id
3. Include relevant metadata (duration, direction, status)
4. Create follow-up tasks if needed
```

## Known Pitfalls

**ID Formats**:
- Lead IDs: 'lead_XXXXXXXXXXXXX'
- Contact IDs: 'cont_XXXXXXXXXXXXX'
- Activity IDs vary by type: 'acti_XXXXXXXXXXXXX', 'call_XXXXXXXXXXXXX'
- Custom field IDs: 'custom.cf_XXXXXXXXXXXXX'
- Always use the full ID string

**Rate Limits**:
- Close API has rate limits based on your plan
- Implement delays between bulk operations
- Monitor response headers for rate limit status
- 429 responses require backoff

**Custom Fields**:
- Custom fields are referenced by their API ID, not display name
- Different lead statuses may have different required custom fields
- Custom field types (text, number, date, dropdown) enforce value formats

**Data Integrity**:
- Leads are the primary entity; contacts and activities are linked to leads
- Deleting a lead may cascade to its contacts and activities
- Bulk operations should validate IDs before executing

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Create lead | CLOSE_CREATE_LEAD | name, contacts, custom |
| Log call | CLOSE_CREATE_CALL | lead_id, direction, status, duration |
| Send SMS | CLOSE_CREATE_SMS | lead_id, text, direction |
| Create task | CLOSE_CREATE_TASK | lead_id, text, date, assigned_to |
| Get note | CLOSE_GET_NOTE | note_id |
| Delete call | CLOSE_DELETE_CALL | call_id |
