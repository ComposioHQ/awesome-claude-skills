---
name: pipedrive-automation
description: Automate Pipedrive CRM operations including deals, contacts, organizations, activities, notes, and pipeline management via Rube MCP (Composio). Always search tools first for current schemas.
requires:
  mcp: [rube]
---

# Pipedrive Automation via Rube MCP

Automate Pipedrive CRM workflows including deal management, contact and organization operations, activity scheduling, notes, and pipeline/stage queries through Composio's Pipedrive toolkit.

**Toolkit docs**: [composio.dev/toolkits/pipedrive](https://composio.dev/toolkits/pipedrive)

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Pipedrive connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `pipedrive`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `pipedrive`
3. If connection is not ACTIVE, follow the returned auth link to complete Pipedrive OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create and Manage Deals

**When to use**: User wants to create a new deal, update an existing deal, or review deal details in the sales pipeline.

**Tool sequence**:
1. `PIPEDRIVE_SEARCH_ORGANIZATIONS` - Find existing org to link to the deal [Optional]
2. `PIPEDRIVE_ADD_AN_ORGANIZATION` - Create organization if none found [Optional]
3. `PIPEDRIVE_SEARCH_PERSONS` - Find existing contact to link [Optional]
4. `PIPEDRIVE_ADD_A_PERSON` - Create contact if none found [Optional]
5. `PIPEDRIVE_GET_ALL_PIPELINES` - Resolve pipeline ID [Prerequisite]
6. `PIPEDRIVE_GET_ALL_STAGES` - Resolve stage ID within the pipeline [Prerequisite]
7. `PIPEDRIVE_ADD_A_DEAL` - Create the deal with title, value, org_id, person_id, stage_id [Required]
8. `PIPEDRIVE_UPDATE_A_DEAL` - Modify deal properties after creation [Optional]
9. `PIPEDRIVE_ADD_A_PRODUCT_TO_A_DEAL` - Attach line items/products [Optional]

**Key parameters**:
- `title`: Deal title (required for creation)
- `value`: Monetary value of the deal
- `currency`: 3-letter ISO currency code (e.g., "USD")
- `pipeline_id` / `stage_id`: Numeric IDs for pipeline placement
- `org_id` / `person_id`: Link to organization and contact
- `status`: "open", "won", or "lost"
- `expected_close_date`: Format YYYY-MM-DD

**Pitfalls**:
- `title` is the only required field for `PIPEDRIVE_ADD_A_DEAL`; all others are optional
- Custom fields appear as long hash keys in responses; use dealFields endpoint to map them
- `PIPEDRIVE_UPDATE_A_DEAL` requires the numeric `id` of the deal
- Setting `status` to "lost" requires also providing `lost_reason`

### 2. Manage Contacts (Persons and Organizations)

**When to use**: User wants to create, update, search, or list contacts and companies in Pipedrive.

**Tool sequence**:
1. `PIPEDRIVE_SEARCH_PERSONS` - Search for existing person by name, email, or phone [Prerequisite]
2. `PIPEDRIVE_ADD_A_PERSON` - Create new contact if not found [Required]
3. `PIPEDRIVE_UPDATE_A_PERSON` - Modify existing contact details [Optional]
4. `PIPEDRIVE_GET_DETAILS_OF_A_PERSON` - Retrieve full contact record [Optional]
5. `PIPEDRIVE_SEARCH_ORGANIZATIONS` - Search for existing organization [Prerequisite]
6. `PIPEDRIVE_ADD_AN_ORGANIZATION` - Create new organization if not found [Required]
7. `PIPEDRIVE_UPDATE_AN_ORGANIZATION` - Modify organization properties [Optional]
8. `PIPEDRIVE_GET_DETAILS_OF_AN_ORGANIZATION` - Retrieve full org record [Optional]

**Key parameters**:
- `name`: Required for both person and organization creation
- `email`: Array of objects with `value`, `label`, `primary` fields for persons
- `phone`: Array of objects with `value`, `label`, `primary` fields for persons
- `org_id`: Link a person to an organization
- `visible_to`: 1 = owner only, 3 = entire company
- `term`: Search term for SEARCH_PERSONS / SEARCH_ORGANIZATIONS (minimum 2 characters)

**Pitfalls**:
- `PIPEDRIVE_ADD_AN_ORGANIZATION` may auto-merge with an existing org; check `response.additional_data.didMerge`
- Email and phone fields are arrays of objects, not plain strings: `[{"value": "test@example.com", "label": "work", "primary": true}]`
- `PIPEDRIVE_SEARCH_PERSONS` wildcards like `*` or `@` are NOT supported; use `PIPEDRIVE_GET_ALL_PERSONS` to list all
- Deletion via `PIPEDRIVE_DELETE_A_PERSON` or `PIPEDRIVE_DELETE_AN_ORGANIZATION` is soft-delete with 30-day retention, then permanent

### 3. Schedule and Track Activities

**When to use**: User wants to create calls, meetings, tasks, or other activities linked to deals, contacts, or organizations.

**Tool sequence**:
1. `PIPEDRIVE_SEARCH_PERSONS` or `PIPEDRIVE_GET_DETAILS_OF_A_DEAL` - Resolve linked entity IDs [Prerequisite]
2. `PIPEDRIVE_ADD_AN_ACTIVITY` - Create the activity with subject, type, due date [Required]
3. `PIPEDRIVE_UPDATE_AN_ACTIVITY` - Modify activity details or mark as done [Optional]
4. `PIPEDRIVE_GET_DETAILS_OF_AN_ACTIVITY` - Retrieve activity record [Optional]
5. `PIPEDRIVE_GET_ALL_ACTIVITIES_ASSIGNED_TO_A_PARTICULAR_USER` - List user's activities [Optional]

**Key parameters**:
- `subject`: Activity title (required)
- `type`: Activity type key string, e.g., "call", "meeting", "task", "email" (required)
- `due_date`: Format YYYY-MM-DD
- `due_time`: Format HH:MM
- `duration`: Format HH:MM (e.g., "00:30" for 30 minutes)
- `deal_id` / `person_id` / `org_id`: Link to related entities
- `done`: 0 = not done, 1 = done

**Pitfalls**:
- Both `subject` and `type` are required for `PIPEDRIVE_ADD_AN_ACTIVITY`
- `type` must match an existing ActivityTypes key_string in the account
- `done` is an integer (0 or 1), not a boolean
- Response includes `more_activities_scheduled_in_context` in additional_data

### 4. Add and Manage Notes

**When to use**: User wants to attach notes to deals, persons, organizations, leads, or projects.

**Tool sequence**:
1. `PIPEDRIVE_SEARCH_PERSONS` or `PIPEDRIVE_GET_DETAILS_OF_A_DEAL` - Resolve entity ID [Prerequisite]
2. `PIPEDRIVE_ADD_A_NOTE` - Create note with HTML content linked to an entity [Required]
3. `PIPEDRIVE_UPDATE_A_NOTE` - Modify note content [Optional]
4. `PIPEDRIVE_GET_ALL_NOTES` - List notes filtered by entity [Optional]
5. `PIPEDRIVE_GET_ALL_COMMENTS_FOR_A_NOTE` - Retrieve comments on a note [Optional]

**Key parameters**:
- `content`: Note body in HTML format (required)
- `deal_id` / `person_id` / `org_id` / `lead_id` / `project_id`: At least one entity link required
- `pinned_to_deal_flag` / `pinned_to_person_flag`: Filter pinned notes when listing

**Pitfalls**:
- `content` is required and supports HTML; plain text works but is sanitized server-side
- At least one of `deal_id`, `person_id`, `org_id`, `lead_id`, or `project_id` must be provided
- `PIPEDRIVE_GET_ALL_NOTES` returns notes across all entities by default; filter with entity ID params

### 5. Query Pipelines and Stages

**When to use**: User wants to view sales pipelines, stages, or deals within a pipeline/stage.

**Tool sequence**:
1. `PIPEDRIVE_GET_ALL_PIPELINES` - List all pipelines and their IDs [Required]
2. `PIPEDRIVE_GET_ONE_PIPELINE` - Get details and deal summary for a specific pipeline [Optional]
3. `PIPEDRIVE_GET_ALL_STAGES` - List all stages, optionally filtered by pipeline [Required]
4. `PIPEDRIVE_GET_ONE_STAGE` - Get details for a specific stage [Optional]
5. `PIPEDRIVE_GET_DEALS_IN_A_PIPELINE` - List all deals across stages in a pipeline [Optional]
6. `PIPEDRIVE_GET_DEALS_IN_A_STAGE` - List deals in a specific stage [Optional]

**Key parameters**:
- `id`: Pipeline or stage ID (required for single-item endpoints)
- `pipeline_id`: Filter stages by pipeline
- `totals_convert_currency`: 3-letter currency code or "default_currency" for converted totals
- `get_summary`: Set to 1 for deal summary in pipeline responses

**Pitfalls**:
- `PIPEDRIVE_GET_ALL_PIPELINES` takes no parameters; returns all pipelines
- `PIPEDRIVE_GET_ALL_STAGES` returns stages for ALL pipelines unless `pipeline_id` is specified
- Deal counts in pipeline summaries use `per_stages_converted` only when `totals_convert_currency` is set

## Common Patterns

### ID Resolution
Always resolve display names to numeric IDs before operations:
- **Organization name -> org_id**: `PIPEDRIVE_SEARCH_ORGANIZATIONS` with `term` param
- **Person name -> person_id**: `PIPEDRIVE_SEARCH_PERSONS` with `term` param
- **Pipeline name -> pipeline_id**: `PIPEDRIVE_GET_ALL_PIPELINES` then match by name
- **Stage name -> stage_id**: `PIPEDRIVE_GET_ALL_STAGES` with `pipeline_id` then match by name

### Pagination
Most list endpoints use offset-based pagination:
- Use `start` (offset) and `limit` (page size) parameters
- Check `additional_data.pagination.more_items_in_collection` to know if more pages exist
- Use `additional_data.pagination.next_start` as the `start` value for the next page
- Default limit is ~500 for some endpoints; set explicitly for predictable paging

## Known Pitfalls

### ID Formats
- All entity IDs (deal, person, org, activity, pipeline, stage) are numeric integers
- Lead IDs are UUID strings, not integers
- Custom field keys are long alphanumeric hashes (e.g., "a1b2c3d4e5f6...")

### Rate Limits
- Pipedrive enforces per-company API rate limits; bulk operations should be paced
- `PIPEDRIVE_GET_ALL_PERSONS` and `PIPEDRIVE_GET_ALL_ORGANIZATIONS` can return large datasets; always paginate

### Parameter Quirks
- Email and phone on persons are arrays of objects, not plain strings
- `visible_to` is numeric: 1 = owner only, 3 = entire company, 5 = specific groups
- `done` on activities is integer 0/1, not boolean true/false
- Organization creation may auto-merge duplicates silently; check `didMerge` in response
- `PIPEDRIVE_SEARCH_PERSONS` requires minimum 2 characters and does not support wildcards

### Response Structure
- Custom fields appear as hash keys in responses; map them via the respective Fields endpoints
- Responses often nest data under `response.data.data` in wrapped executions
- Search results are under `response.data.items`, not top-level

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Create deal | `PIPEDRIVE_ADD_A_DEAL` | `title`, `value`, `org_id`, `stage_id` |
| Update deal | `PIPEDRIVE_UPDATE_A_DEAL` | `id`, `status`, `value`, `stage_id` |
| Get deal details | `PIPEDRIVE_GET_DETAILS_OF_A_DEAL` | `id` |
| Search persons | `PIPEDRIVE_SEARCH_PERSONS` | `term`, `fields` |
| Add person | `PIPEDRIVE_ADD_A_PERSON` | `name`, `email`, `phone`, `org_id` |
| Update person | `PIPEDRIVE_UPDATE_A_PERSON` | `id`, `name`, `email` |
| Get person details | `PIPEDRIVE_GET_DETAILS_OF_A_PERSON` | `id` |
| List all persons | `PIPEDRIVE_GET_ALL_PERSONS` | `start`, `limit`, `filter_id` |
| Search organizations | `PIPEDRIVE_SEARCH_ORGANIZATIONS` | `term`, `fields` |
| Add organization | `PIPEDRIVE_ADD_AN_ORGANIZATION` | `name`, `visible_to` |
| Update organization | `PIPEDRIVE_UPDATE_AN_ORGANIZATION` | `id`, `name`, `address` |
| Get org details | `PIPEDRIVE_GET_DETAILS_OF_AN_ORGANIZATION` | `id` |
| Add activity | `PIPEDRIVE_ADD_AN_ACTIVITY` | `subject`, `type`, `due_date`, `deal_id` |
| Update activity | `PIPEDRIVE_UPDATE_AN_ACTIVITY` | `id`, `done`, `due_date` |
| Get activity details | `PIPEDRIVE_GET_DETAILS_OF_AN_ACTIVITY` | `id` |
| List user activities | `PIPEDRIVE_GET_ALL_ACTIVITIES_ASSIGNED_TO_A_PARTICULAR_USER` | `user_id`, `start`, `limit` |
| Add note | `PIPEDRIVE_ADD_A_NOTE` | `content`, `deal_id` or `person_id` |
| List notes | `PIPEDRIVE_GET_ALL_NOTES` | `deal_id`, `person_id`, `start`, `limit` |
| List pipelines | `PIPEDRIVE_GET_ALL_PIPELINES` | (none) |
| Get pipeline details | `PIPEDRIVE_GET_ONE_PIPELINE` | `id` |
| List stages | `PIPEDRIVE_GET_ALL_STAGES` | `pipeline_id` |
| Deals in pipeline | `PIPEDRIVE_GET_DEALS_IN_A_PIPELINE` | `id`, `stage_id` |
| Deals in stage | `PIPEDRIVE_GET_DEALS_IN_A_STAGE` | `id`, `start`, `limit` |
| Add product to deal | `PIPEDRIVE_ADD_A_PRODUCT_TO_A_DEAL` | `id`, `product_id`, `item_price` |

---
*Powered by [Composio](https://composio.dev)*
