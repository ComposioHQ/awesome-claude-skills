---
name: docusign-automation
description: "Automate DocuSign tasks via Rube MCP (Composio): templates, envelopes, signatures, document management. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# DocuSign Automation via Rube MCP

Automate DocuSign e-signature workflows through Composio's DocuSign toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active DocuSign connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `docusign`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `docusign`
3. If connection is not ACTIVE, follow the returned auth link to complete DocuSign OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Browse and Select Templates

**When to use**: User wants to find available document templates for sending

**Tool sequence**:
1. `DOCUSIGN_LIST_ALL_TEMPLATES` - List all available templates [Required]
2. `DOCUSIGN_GET_TEMPLATE` - Get detailed template information [Optional]

**Key parameters**:
- For listing: Optional search/filter parameters
- For details: `templateId` (from list results)
- Response includes template `templateId`, `name`, `description`, roles, and fields

**Pitfalls**:
- Template IDs are GUIDs (e.g., '12345678-abcd-1234-efgh-123456789012')
- Templates define recipient roles with signing tabs; understand roles before creating envelopes
- Large template libraries require pagination; check for continuation tokens
- Template access depends on account permissions

### 2. Create and Send Envelopes from Templates

**When to use**: User wants to send documents for signature using a pre-built template

**Tool sequence**:
1. `DOCUSIGN_LIST_ALL_TEMPLATES` - Find the template to use [Prerequisite]
2. `DOCUSIGN_GET_TEMPLATE` - Review template roles and fields [Optional]
3. `DOCUSIGN_CREATE_ENVELOPE_FROM_TEMPLATE` - Create the envelope [Required]
4. `DOCUSIGN_SEND_ENVELOPE` - Send the envelope for signing [Required]

**Key parameters**:
- For CREATE_ENVELOPE_FROM_TEMPLATE:
  - `templateId`: Template to use
  - `templateRoles`: Array of role assignments with `roleName`, `name`, `email`
  - `status`: 'created' (draft) or 'sent' (send immediately)
  - `emailSubject`: Custom subject line for the signing email
  - `emailBlurb`: Custom message in the signing email
- For SEND_ENVELOPE:
  - `envelopeId`: Envelope ID from creation response

**Pitfalls**:
- `templateRoles` must match the role names defined in the template exactly (case-sensitive)
- Setting `status` to 'sent' during creation sends immediately; use 'created' for drafts
- If status is 'sent' at creation, no need to call SEND_ENVELOPE separately
- Each role requires at minimum `roleName`, `name`, and `email`
- `emailSubject` overrides the template's default email subject

### 3. Monitor Envelope Status

**When to use**: User wants to check the status of sent envelopes or track signing progress

**Tool sequence**:
1. `DOCUSIGN_GET_ENVELOPE` - Get envelope details and status [Required]

**Key parameters**:
- `envelopeId`: Envelope identifier (GUID)
- Response includes `status`, `recipients`, `sentDateTime`, `completedDateTime`

**Pitfalls**:
- Envelope statuses: 'created', 'sent', 'delivered', 'signed', 'completed', 'declined', 'voided'
- 'delivered' means the email was opened, not that the document was signed
- 'completed' means all recipients have signed
- Recipients array shows individual signing status per recipient
- Envelope IDs are GUIDs; always resolve from creation or search results

### 4. Add Templates to Existing Envelopes

**When to use**: User wants to add additional documents or templates to an existing envelope

**Tool sequence**:
1. `DOCUSIGN_GET_ENVELOPE` - Verify envelope exists and is in draft state [Prerequisite]
2. `DOCUSIGN_ADD_TEMPLATES_TO_DOCUMENT_IN_ENVELOPE` - Add template to envelope [Required]

**Key parameters**:
- `envelopeId`: Target envelope ID
- `documentId`: Document ID within the envelope
- `templateId`: Template to add

**Pitfalls**:
- Envelope must be in 'created' (draft) status to add templates
- Cannot add templates to already-sent envelopes
- Document IDs are sequential within an envelope (starting from '1')
- Adding a template merges its fields and roles into the existing envelope

### 5. Manage Envelope Lifecycle

**When to use**: User wants to send, void, or manage draft envelopes

**Tool sequence**:
1. `DOCUSIGN_GET_ENVELOPE` - Check current envelope status [Prerequisite]
2. `DOCUSIGN_SEND_ENVELOPE` - Send a draft envelope [Optional]

**Key parameters**:
- `envelopeId`: Envelope to manage
- For sending: envelope must be in 'created' status with all required recipients

**Pitfalls**:
- Only 'created' (draft) envelopes can be sent
- Sent envelopes cannot be unsent; they can only be voided
- Voiding an envelope notifies all recipients
- All required recipients must have valid email addresses before sending

## Common Patterns

### ID Resolution

**Template name -> Template ID**:
```
1. Call DOCUSIGN_LIST_ALL_TEMPLATES
2. Find template by name in results
3. Extract templateId (GUID format)
```

**Envelope tracking**:
```
1. Store envelopeId from CREATE_ENVELOPE_FROM_TEMPLATE response
2. Call DOCUSIGN_GET_ENVELOPE periodically to check status
3. Check recipient-level status for individual signing progress
```

### Template Role Mapping

When creating an envelope from a template:
```
1. Call DOCUSIGN_GET_TEMPLATE to see defined roles
2. Map each role to actual recipients:
   {
     "roleName": "Signer 1",     // Must match template role name exactly
     "name": "John Smith",
     "email": "john@example.com"
   }
3. Include ALL required roles in templateRoles array
```

### Envelope Status Flow

```
created (draft) -> sent -> delivered -> signed -> completed
                       \-> declined
                       \-> voided (by sender)
```

## Known Pitfalls

**Template Roles**:
- Role names are case-sensitive; must match template definition exactly
- All required roles must be assigned when creating an envelope
- Missing role assignments cause envelope creation to fail

**Envelope Status**:
- 'delivered' means email opened, NOT document signed
- 'completed' is the final successful state (all parties signed)
- Status transitions are one-way; cannot revert to previous states

**GUIDs**:
- All DocuSign IDs (templates, envelopes) are GUID format
- Always resolve names to GUIDs via list/search endpoints
- Do not hardcode GUIDs; they are unique per account

**Rate Limits**:
- DocuSign API has per-account rate limits
- Bulk envelope creation should be throttled
- Polling envelope status should use reasonable intervals (30-60 seconds)

**Response Parsing**:
- Response data may be nested under `data` key
- Recipient information is nested within envelope response
- Date fields use ISO 8601 format
- Parse defensively with fallbacks for optional fields

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| List templates | DOCUSIGN_LIST_ALL_TEMPLATES | (optional filters) |
| Get template | DOCUSIGN_GET_TEMPLATE | templateId |
| Create envelope | DOCUSIGN_CREATE_ENVELOPE_FROM_TEMPLATE | templateId, templateRoles, status |
| Send envelope | DOCUSIGN_SEND_ENVELOPE | envelopeId |
| Get envelope status | DOCUSIGN_GET_ENVELOPE | envelopeId |
| Add template to envelope | DOCUSIGN_ADD_TEMPLATES_TO_DOCUMENT_IN_ENVELOPE | envelopeId, documentId, templateId |
