---
name: Kommo Automation
description: "Automate Kommo CRM operations -- manage leads, pipelines, pipeline stages, tasks, and custom fields -- using natural language through the Composio MCP integration."
category: crm
requires:
  mcp:
    - rube
---

# Kommo Automation

Manage your Kommo CRM sales pipeline -- list and filter leads, navigate pipeline stages, create and update deals, assign tasks, and work with custom fields -- all through natural language commands.

**Toolkit docs:** [composio.dev/toolkits/kommo](https://composio.dev/toolkits/kommo)

---

## Setup

1. Add the Composio MCP server to your client configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Kommo account when prompted (OAuth authentication).
3. Start issuing natural language commands to manage your CRM.

---

## Core Workflows

### 1. Navigate Pipelines and Stages
List all lead pipelines, then drill into specific pipeline stages to understand your sales funnel structure.

**Tools:** `KOMMO_LIST_LEADS_PIPELINES`, `KOMMO_LIST_PIPELINE_STAGES`

**Example prompt:**
> "Show all my Kommo pipelines and the stages in my main sales pipeline"

**Key parameters for List Pipelines:** None required.

**Key parameters for List Stages:**
- `pipeline_id` (required) -- The pipeline ID to list stages for
- `with_description` -- Include stage descriptions in the response (boolean)

---

### 2. List and Filter Leads
Retrieve leads with powerful filtering by pipeline, status, date ranges, responsible users, price, and more.

**Tool:** `KOMMO_LIST_LEADS`

**Example prompt:**
> "Show all leads in pipeline 12345 created this week, sorted by newest first"

**Key parameters:**
- `query` -- Free-text search across all filled fields
- `filter_pipeline_ids` -- Filter by pipeline IDs (array of integers)
- `filter_status` -- Filter by status within a pipeline: `{"pipeline_id": 123, "status_id": 456}`
- `filter_responsible_user_ids` -- Filter by assigned user IDs
- `filter_names` -- Filter by lead names
- `filter_price` -- Filter by deal value
- `filter_created_at` -- Date range: `{"from": <unix_timestamp>, "to": <unix_timestamp>}`
- `filter_updated_at` -- Date range for last update
- `filter_closed_at` -- Date range for closure
- `order_by_created_at` -- Sort: "asc" or "desc"
- `order_by_updated_at` -- Sort by update date
- `limit` -- Max 250 per page
- `page` -- Page number for pagination
- `with_params` -- Additional data: "contacts", "loss_reason", "catalog_elements", "source_id"

---

### 3. Create New Leads
Add new deals to your Kommo pipeline with custom fields, tags, and pipeline placement.

**Tool:** `KOMMO_CREATE_LEAD`

**Example prompt:**
> "Create a new lead called 'Acme Corp Deal' worth $50,000 in pipeline 12345"

**Key parameters:**
- `name` (required) -- Name of the lead/deal
- `price` -- Deal value (integer)
- `pipeline_id` -- Pipeline to add the lead to
- `status_id` -- Stage within the pipeline (defaults to first stage of main pipeline)
- `responsible_user_id` -- Assigned user ID
- `custom_fields_values` -- Array of custom field value objects
- `tags_to_add` -- Array of tags (by name or ID)
- `created_by` -- User ID of creator (0 for robot)
- `loss_reason_id` -- Reason for loss (if applicable)

---

### 4. Update Existing Leads
Modify lead properties including name, price, pipeline stage, responsible user, tags, and custom fields.

**Tool:** `KOMMO_UPDATE_LEAD`

**Example prompt:**
> "Move lead 789 to stage 456 in pipeline 123 and update the price to $75,000"

**Key parameters:**
- Lead ID (required)
- Any combination of: `name`, `price`, `pipeline_id`, `status_id`, `responsible_user_id`, `tags_to_add`, `tags_to_delete`, `custom_fields_values`

---

### 5. Create Tasks
Assign follow-up tasks linked to leads, contacts, or companies.

**Tool:** `KOMMO_CREATE_TASK`

**Example prompt:**
> "Create a follow-up call task for lead 789 due tomorrow assigned to user 42"

**Key parameters:**
- Task text/description
- Entity type and ID (lead, contact, company)
- Responsible user ID
- Due date (Unix timestamp)
- Task type

---

### 6. Discover Custom Fields
List all custom fields for leads, contacts, or companies to understand your CRM schema.

**Tool:** `KOMMO_LIST_CUSTOM_FIELDS`

**Example prompt:**
> "What custom fields are available for leads in Kommo?"

**Key parameters:**
- Entity type (leads, contacts, companies)

---

## Known Pitfalls

- **Date filters use Unix timestamps**: All date range filters (`filter_created_at`, `filter_updated_at`, `filter_closed_at`) require Unix timestamp format in `{"from": <timestamp>, "to": <timestamp>}` structure, not ISO8601 strings.
- **Pipeline and stage IDs are required**: To filter leads by status, you need both `pipeline_id` and `status_id`. Always call `KOMMO_LIST_LEADS_PIPELINES` and `KOMMO_LIST_PIPELINE_STAGES` first to discover valid IDs.
- **Max 250 leads per page**: The `limit` parameter caps at 250. For large datasets, implement pagination using the `page` parameter.
- **Custom field values format**: Custom fields use a specific nested object format. Use `KOMMO_LIST_CUSTOM_FIELDS` to discover field IDs and expected value formats before setting values.
- **Status filter requires both IDs**: The `filter_status` parameter requires both `pipeline_id` and `status_id` as a combined object -- you cannot filter by status alone.
- **Created_by 0 means robot**: When setting `created_by` or `updated_by` to 0, the action is attributed to a robot/automation, not a human user.

---

## Quick Reference

| Action | Tool Slug | Required Params |
|---|---|---|
| List pipelines | `KOMMO_LIST_LEADS_PIPELINES` | None |
| List pipeline stages | `KOMMO_LIST_PIPELINE_STAGES` | `pipeline_id` |
| List leads | `KOMMO_LIST_LEADS` | None (optional filters) |
| Create lead | `KOMMO_CREATE_LEAD` | `name` |
| Update lead | `KOMMO_UPDATE_LEAD` | Lead ID |
| Create task | `KOMMO_CREATE_TASK` | Task details |
| List custom fields | `KOMMO_LIST_CUSTOM_FIELDS` | Entity type |

---

*Powered by [Composio](https://composio.dev)*
