---
name: Capsule CRM Automation
description: "Automate Capsule CRM operations -- manage contacts (parties), run structured filter queries, track tasks and projects, log entries, and handle organizations -- using natural language through the Composio MCP integration."
category: crm
requires:
  mcp:
    - rube
---

# Capsule CRM Automation

Manage your Capsule CRM -- create and update contacts, run powerful filter queries on parties/opportunities/cases, track tasks and projects, browse activity entries, and organize team relationships -- all through natural language commands.

**Toolkit docs:** [composio.dev/toolkits/capsule_crm](https://composio.dev/toolkits/capsule_crm)

---

## Setup

1. Add the Composio MCP server to your client configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Capsule CRM account when prompted (OAuth authentication).
3. Start issuing natural language commands to manage your CRM.

---

## Core Workflows

### 1. Run Structured Filter Queries
Query parties, opportunities, or cases (projects) with multiple filter conditions, operators, and sorting.

**Tool:** `CAPSULE_CRM_RUN_FILTER_QUERY`

**Example prompt:**
> "Find all Capsule CRM contacts in California tagged as 'VIP' sorted by name"

**Key parameters:**
- `entity` (required) -- One of: `parties`, `opportunities`, `kases`
- `filter` (required) -- Filter object with:
  - `conditions` -- Array of conditions, each with:
    - `field` -- Field name (e.g., "name", "email", "state", "country", "tag", "owner", "jobTitle", "addedOn")
    - `operator` -- One of: "is", "is not", "starts with", "ends with", "contains", "is greater than", "is less than", "is after", "is before", "is older than", "is within last", "is within next"
    - `value` -- Value to compare against
  - `orderBy` -- Array of sort objects with `field` and `direction` ("ascending"/"descending")
- `embed` -- Additional data to include in response
- `page` / `perPage` -- Pagination (max 100 per page)

**Important field notes:**
- Address fields (`city`, `state`, `country`, `zip`) are top-level, NOT nested under "address"
- Country must be an ISO 3166-1 alpha-2 code (e.g., "US", "GB", "CA")
- Custom fields use `custom:{fieldId}` format
- Organization fields use `org.` prefix (e.g., `org.name`, `org.tag`)

---

### 2. List and Manage Contacts (Parties)
Retrieve all contacts with optional filtering by modification date and embedded related data.

**Tool:** `CAPSULE_CRM_LIST_PARTIES`

**Example prompt:**
> "List all Capsule CRM contacts modified since January 2025 with their tags and organizations"

**Key parameters:**
- `since` -- ISO8601 date to filter contacts changed after this date
- `embed` -- Additional data: "tags", "fields", "organisation", "missingImportantFields"
- `page` / `perPage` -- Pagination (max 100 per page, default 50)

---

### 3. Create New Contacts
Add people or organizations to your Capsule CRM with full details including emails, phones, addresses, tags, and custom fields.

**Tool:** `CAPSULE_CRM_CREATE_PARTY`

**Example prompt:**
> "Create a new person in Capsule CRM: John Smith, VP of Sales at Acme Corp, john@acme.com"

**Key parameters:**
- `type` (required) -- "person" or "organisation"
- For persons: `firstName`, `lastName`, `jobTitle`, `title`
- For organisations: `name`
- `emailAddresses` -- Array of `{address, type}` objects
- `phoneNumbers` -- Array of `{number, type}` objects
- `addresses` -- Array of address objects with `street`, `city`, `state`, `country`, `zip`, `type` (Home/Postal/Office/Billing/Shipping)
- `organisation` -- Link to org by `{id}` or `{name}` (creates if not found)
- `tags` -- Array of tags by `{name}` or `{id}`
- `fields` -- Custom field values with `{definition, value}`
- `websites` -- Array of `{address, service, type}` objects
- `owner` -- Assign owner user `{id}`

---

### 4. Update Existing Contacts
Modify any aspect of a party record including adding/removing emails, phones, tags, and custom fields.

**Tool:** `CAPSULE_CRM_UPDATE_PARTY`

**Example prompt:**
> "Update Capsule CRM party 11587: add a work email john.new@acme.com and remove tag 'prospect'"

**Key parameters:**
- `partyId` (required) -- Integer ID of the party to update
- `party` (required) -- Object with fields to update. Supports:
  - All creation fields (name, emails, phones, addresses, etc.)
  - `_delete: true` on sub-items to remove them (requires the item's `id`)
  - Tags: add by `{name}` or remove with `{id, _delete: true}`

---

### 5. Track Tasks
List tasks with filtering by status and embedded related data.

**Tool:** `CAPSULE_CRM_LIST_TASKS`

**Example prompt:**
> "Show all open tasks in Capsule CRM with their linked parties and owners"

**Key parameters:**
- `status` -- Filter by status: "open", "completed", "pending" (array)
- `embed` -- Additional data: "party", "opportunity", "kase", "owner", "nextTask"
- `page` / `perPage` -- Pagination (max 100 per page, default 50)

---

### 6. Browse Projects and Activity Entries
List projects (cases) and recent activity entries including notes, emails, and completed tasks.

**Tools:** `CAPSULE_CRM_LIST_PROJECTS`, `CAPSULE_CRM_LIST_ENTRIES_BY_DATE`

**Example prompt:**
> "Show all open projects in Capsule CRM" / "Show recent activity entries with party details"

**Key parameters for projects:**
- `status` -- Filter by "OPEN" or "CLOSED"
- `search` -- Search term for project names/descriptions
- `since` -- ISO8601 date for modifications after this date
- `embed` -- "tags,fields,party,opportunity,missingImportantFields"

**Key parameters for entries:**
- `embed` -- "party", "kase", "opportunity", "creator", "activityType"
- `page` / `perPage` -- Pagination (max 100 per page)

---

## Known Pitfalls

- **Address fields are top-level**: When filtering, use `state`, `city`, `country`, `zip` directly -- NOT `address.state` or nested syntax.
- **Country codes are ISO alpha-2**: Filter by "US", "GB", "CA" -- not "United States" or "United Kingdom".
- **Custom fields use special syntax**: Reference custom fields as `custom:{fieldId}` in filter conditions. For org-level custom fields, use `org.custom:{fieldId}`.
- **Projects are called "kases" in the API**: Despite being "projects" in the UI, the API entity type is `kases`. Use `kases` in filter queries.
- **Delete operations require item IDs**: When updating a party to remove sub-items (emails, phones, tags), you must include the item's `id` along with `_delete: true`. List the party first to get sub-item IDs.
- **Pagination defaults to 50**: All list endpoints default to 50 items per page with a max of 100. Always implement pagination for complete data retrieval.
- **Embed values vary by entity**: Not all embed options work for all entities. Check the documentation for supported embed values per endpoint.

---

## Quick Reference

| Action | Tool Slug | Required Params |
|---|---|---|
| Run filter query | `CAPSULE_CRM_RUN_FILTER_QUERY` | `entity`, `filter` |
| List contacts | `CAPSULE_CRM_LIST_PARTIES` | None (optional filters) |
| Create contact | `CAPSULE_CRM_CREATE_PARTY` | `type` |
| Update contact | `CAPSULE_CRM_UPDATE_PARTY` | `partyId`, `party` |
| Delete contact | `CAPSULE_CRM_DELETE_PARTY` | `party_id` |
| List tasks | `CAPSULE_CRM_LIST_TASKS` | None (optional filters) |
| List projects | `CAPSULE_CRM_LIST_PROJECTS` | None (optional filters) |
| List activity entries | `CAPSULE_CRM_LIST_ENTRIES_BY_DATE` | None (optional filters) |
| List org employees | `CAPSULE_CRM_LIST_ORG_EMPLOYEES` | Organisation ID |
| List deleted opportunities | `CAPSULE_CRM_LIST_DELETED_OPPORTUNITIES` | `since` |

---

*Powered by [Composio](https://composio.dev)*
