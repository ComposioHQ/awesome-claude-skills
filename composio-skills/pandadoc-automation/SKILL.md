---
name: PandaDoc Automation
description: "Automate document workflows with PandaDoc -- create documents from files, manage contacts, organize folders, set up webhooks, create templates, and track document status through the Composio PandaDoc integration."
requires:
  mcp:
    - rube
---

# PandaDoc Automation

Manage **PandaDoc** document workflows directly from Claude Code. Create documents from uploaded files, manage recipients and contacts, organize with folders, set up event webhooks, create templates, and track document status without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/pandadoc](https://composio.dev/toolkits/pandadoc)

---

## Setup

1. Add the Composio MCP server to your configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your PandaDoc account when prompted. The agent will provide an OAuth link to authenticate.
3. Ensure your PandaDoc workspace has the appropriate plan for the features you need (e.g., e-signatures, templates, webhooks).

---

## Core Workflows

### 1. Create a Document from File

Upload a PDF, DOCX, or RTF file to create a new PandaDoc document with designated recipients for signing and tracking.

**Tool:** `PANDADOC_CREATE_DOCUMENT_FROM_FILE`

Key parameters:
- `name` (required) -- document name
- `recipients` (required) -- array of recipient objects, each with:
  - `email` (required) -- recipient email
  - `first_name`, `last_name` -- recipient name
  - `role` -- `signer` (default), `approver`, or `cc` (must be unique per recipient)
  - `signing_order` -- numeric order (if set for one, must be set for all)
- `file` -- uploaded file object with `name`, `mimetype`, and `s3key`
- `url` -- alternatively, a public HTTPS URL to the file
- `parse_form_fields` (default false) -- parse PDF form fields
- `tags` -- array of strings for categorization
- `owner` -- document owner (email or membership_id)

Example prompt: *"Create a PandaDoc document from contract.pdf with john@example.com as signer and jane@example.com as approver"*

---

### 2. Get Document Details

Fetch comprehensive metadata for a document including recipients, fields, tokens, pricing, tags, and content-block references.

**Tool:** `PANDADOC_GET_DOCUMENT_DETAILS`

Key parameters:
- `id` (required) -- the unique document identifier (e.g., `BhVzRcxH9Z2LgfPPGXFUqa`)

Use this to check document status, inspect recipient completion, review field values, or gather metadata for reporting.

Example prompt: *"Get the full details and status for PandaDoc document BhVzRcxH9Z2LgfPPGXFUqa"*

---

### 3. Manage Contacts

Create new contacts or update existing ones in PandaDoc. Contacts are matched by email -- if a contact with the given email exists, it gets updated; otherwise, a new one is created.

**Tool:** `PANDADOC_CREATE_OR_UPDATE_CONTACT`

Key parameters:
- `email` (required) -- contact email address
- `first_name`, `last_name` -- contact name
- `company` -- company name
- `job_title` -- role/title
- `phone` -- phone number
- `street_address`, `city`, `state`, `postal_code`, `country` -- address fields

Example prompt: *"Create a PandaDoc contact for john.doe@example.com at Acme Corp as Software Engineer"*

---

### 4. Organize with Folders

Create folders and move documents to organize your PandaDoc workspace.

**Tools:** `PANDADOC_CREATE_FOLDER`, `PANDADOC_LIST_DOCUMENT_FOLDERS`, `PANDADOC_MOVE_DOCUMENT_TO_FOLDER`

For creating folders:
- `name` (required) -- folder name
- `parent_uuid` -- parent folder UUID for nested structures

Example prompt: *"Create a 'Q1 2026 Contracts' folder in PandaDoc and move document BhVzRcxH9Z to it"*

---

### 5. Set Up Webhooks

Create webhook subscriptions to receive real-time notifications when document events occur.

**Tool:** `PANDADOC_CREATE_WEBHOOK`

Key parameters:
- `name` (required) -- descriptive name for the webhook
- `url` (required) -- endpoint URL for notifications
- `triggers` (required) -- event types: `document_state_changed`, `recipient_completed`, `document_updated`, etc.
- `active` (default true) -- enable/disable the webhook
- `payload` -- additional data to include: `fields`, `products`, `metadata`, `tokens`, `pricing`

Example prompt: *"Set up a PandaDoc webhook to notify https://api.example.com/hooks when documents change state or recipients complete"*

---

### 6. Create Templates

Create reusable templates from PDF files or from scratch with structured content blocks.

**Tool:** `PANDADOC_CREATE_TEMPLATE`

Key parameters:
- `name` (required) -- template name
- `file_path` -- path to PDF file for template creation
- `content` -- structured content object with `title` and `blocks` array for building from scratch
- `description` -- template description
- `tags` -- categorization tags

Example prompt: *"Create a PandaDoc template called 'Standard NDA' from the nda-template.pdf file"*

---

## Known Pitfalls

- **Unique recipient roles:** PandaDoc API does not allow duplicate roles within a single document. Each recipient must have a unique `role` value (e.g., `signer`, `signer_2`, `approver`, `cc`).
- **Signing order consistency:** If you specify `signing_order` for any recipient, you must specify it for ALL recipients in the document. Partial ordering will cause errors.
- **File upload requirements:** Either `file` (with `s3key`) or `url` must be provided for document creation, not both. The URL must be publicly accessible HTTPS.
- **Contact upsert behavior:** `PANDADOC_CREATE_OR_UPDATE_CONTACT` matches by email. If you need to update a contact's email itself, you must create a new contact and handle the old one separately.
- **Document ID format:** Document IDs are alphanumeric strings (e.g., `BhVzRcxH9Z2LgfPPGXFUqa`). They are returned when documents are created and can be found via the PandaDoc dashboard.
- **Webhook event naming:** Trigger event names must match exactly (e.g., `document_state_changed`, not `stateChanged` or `state_changed`). Check PandaDoc API docs for the complete list.
- **Folder operations require UUIDs:** Moving documents requires both the document ID and the destination folder UUID. List folders first to get the correct UUID.
- **Template content blocks:** When creating templates from scratch, the `blocks` array must contain valid content block objects per PandaDoc's schema. Check their API documentation for supported block types.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `PANDADOC_CREATE_DOCUMENT_FROM_FILE` | Create a document from PDF/DOCX/RTF with recipients |
| `PANDADOC_GET_DOCUMENT_DETAILS` | Get full document metadata, status, and fields |
| `PANDADOC_CREATE_OR_UPDATE_CONTACT` | Create or update a contact by email |
| `PANDADOC_CREATE_FOLDER` | Create a folder for document organization |
| `PANDADOC_LIST_DOCUMENT_FOLDERS` | List all document folders |
| `PANDADOC_MOVE_DOCUMENT_TO_FOLDER` | Move a document to a specific folder |
| `PANDADOC_CREATE_WEBHOOK` | Set up event notification webhooks |
| `PANDADOC_CREATE_TEMPLATE` | Create a reusable document template |

---

*Powered by [Composio](https://composio.dev)*
