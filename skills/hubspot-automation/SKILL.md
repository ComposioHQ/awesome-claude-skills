---
name: hubspot-automation
description: Automate HubSpot CRM operations (contacts, companies, deals, tickets, properties) via Rube MCP using Composio integration.
requires:
  mcp: [rube]
---

# HubSpot CRM Automation via Rube MCP

Automate HubSpot CRM workflows including contact/company management, deal pipeline tracking, ticket search, and custom property creation through Composio's HubSpot toolkit.

**Toolkit docs**: [composio.dev/toolkits/hubspot](https://composio.dev/toolkits/hubspot)

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active HubSpot connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `hubspot`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `hubspot`
3. If connection is not ACTIVE, follow the returned auth link to complete HubSpot OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create and Manage Contacts

**When to use**: User wants to create new contacts or update existing ones in HubSpot CRM

**Tool sequence**:
1. `HUBSPOT_GET_ACCOUNT_INFO` - Verify connection and permissions (Prerequisite)
2. `HUBSPOT_SEARCH_CONTACTS_BY_CRITERIA` - Search for existing contacts to avoid duplicates (Prerequisite)
3. `HUBSPOT_READ_A_CRM_PROPERTY_BY_NAME` - Check property metadata for constrained values (Optional)
4. `HUBSPOT_CREATE_CONTACT` - Create a single contact (Required)
5. `HUBSPOT_CREATE_CONTACTS` - Batch create contacts up to 100 (Alternative)

**Key parameters**:
- `HUBSPOT_CREATE_CONTACT`: `properties` object with `email`, `firstname`, `lastname`, `phone`, `company`
- `HUBSPOT_CREATE_CONTACTS`: `inputs` array of `{properties}` objects, max 100 per batch
- `HUBSPOT_SEARCH_CONTACTS_BY_CRITERIA`: `filterGroups` array with `{filters: [{propertyName, operator, value}]}`, `properties` array of fields to return

**Pitfalls**:
- Max 100 records per batch; chunk larger imports
- 400 'Property values were not valid' if using incorrect property names or enum values
- Always search before creating to avoid duplicates
- Auth errors from GET_ACCOUNT_INFO mean all subsequent calls will fail

### 2. Manage Companies

**When to use**: User wants to create, search, or update company records

**Tool sequence**:
1. `HUBSPOT_SEARCH_COMPANIES` - Search existing companies (Prerequisite)
2. `HUBSPOT_CREATE_COMPANIES` - Batch create companies, max 100 (Required)
3. `HUBSPOT_UPDATE_COMPANIES` - Batch update existing companies (Alternative)
4. `HUBSPOT_GET_COMPANY` - Get single company details (Optional)
5. `HUBSPOT_BATCH_READ_COMPANIES_BY_PROPERTIES` - Bulk read companies by property values (Optional)

**Key parameters**:
- `HUBSPOT_CREATE_COMPANIES`: `inputs` array of `{properties}` objects, max 100
- `HUBSPOT_SEARCH_COMPANIES`: `filterGroups`, `properties`, `sorts`, `limit`, `after` (pagination cursor)

**Pitfalls**:
- Max 100 per batch; chunk larger sets
- Store returned IDs immediately for downstream operations
- Property values must match exact internal names, not display labels

### 3. Manage Deals and Pipeline

**When to use**: User wants to search deals, view pipeline stages, or track deal progress

**Tool sequence**:
1. `HUBSPOT_RETRIEVE_ALL_PIPELINES_FOR_SPECIFIED_OBJECT_TYPE` - Map pipeline and stage IDs/names (Prerequisite)
2. `HUBSPOT_SEARCH_DEALS` - Search deals with filters (Required)
3. `HUBSPOT_RETRIEVE_PIPELINE_STAGES` - Get stage details for one pipeline (Optional)
4. `HUBSPOT_RETRIEVE_OWNERS` - Get owner/rep details (Optional)
5. `HUBSPOT_GET_DEAL` - Get single deal details (Optional)
6. `HUBSPOT_LIST_DEALS` - List all deals without filters (Fallback)

**Key parameters**:
- `HUBSPOT_SEARCH_DEALS`: `filterGroups` with filters on `pipeline`, `dealstage`, `createdate`, `closedate`, `hubspot_owner_id`; `properties`, `sorts`, `limit`, `after`
- `HUBSPOT_RETRIEVE_ALL_PIPELINES_FOR_SPECIFIED_OBJECT_TYPE`: `objectType` set to `'deals'`

**Pitfalls**:
- Results nested under `response.data.results`; properties are often strings (amounts, dates)
- Stage IDs may be readable strings or opaque numeric IDs; use `label` field for display
- Filters must use internal property names (`pipeline`, `dealstage`, `createdate`), not display names
- Paginate via `paging.next.after` until absent

### 4. Search and Filter Tickets

**When to use**: User wants to find support tickets by status, date, or criteria

**Tool sequence**:
1. `HUBSPOT_SEARCH_TICKETS` - Search with filterGroups (Required)
2. `HUBSPOT_READ_ALL_PROPERTIES_FOR_OBJECT_TYPE` - Discover available property names (Fallback)
3. `HUBSPOT_GET_TICKET` - Get single ticket details (Optional)
4. `HUBSPOT_GET_TICKETS` - Bulk fetch tickets by IDs (Optional)

**Key parameters**:
- `HUBSPOT_SEARCH_TICKETS`: `filterGroups`, `properties` (only listed fields are returned), `sorts`, `limit`, `after`

**Pitfalls**:
- Incorrect `propertyName`/`operator` returns zero results without errors
- Date filtering may require epoch-ms bounds; mixing formats causes mismatches
- Only fields in the `properties` array are returned; missing ones break downstream logic
- Use READ_ALL_PROPERTIES to discover exact internal property names

### 5. Create and Manage Custom Properties

**When to use**: User wants to add custom fields to CRM objects

**Tool sequence**:
1. `HUBSPOT_READ_ALL_PROPERTIES_FOR_OBJECT_TYPE` - List existing properties (Prerequisite)
2. `HUBSPOT_READ_PROPERTY_GROUPS_FOR_OBJECT_TYPE` - List property groups (Optional)
3. `HUBSPOT_CREATE_PROPERTY_FOR_SPECIFIED_OBJECT_TYPE` - Create a single property (Required)
4. `HUBSPOT_CREATE_BATCH_OF_PROPERTIES` - Batch create properties (Alternative)
5. `HUBSPOT_UPDATE_SPECIFIC_CRM_PROPERTY` - Update existing property definition (Optional)

**Key parameters**:
- `HUBSPOT_CREATE_PROPERTY_FOR_SPECIFIED_OBJECT_TYPE`: `objectType`, `name`, `label`, `type` (string/number/date/enumeration), `fieldType`, `groupName`, `options` (for enumerations)

**Pitfalls**:
- Property names are immutable after creation; choose carefully
- Enumeration options must be pre-defined with `value` and `label`
- Group must exist before assigning properties to it

## Common Patterns

### ID Resolution
- **Property display name → internal name**: Use `HUBSPOT_READ_ALL_PROPERTIES_FOR_OBJECT_TYPE`
- **Pipeline name → pipeline ID**: Use `HUBSPOT_RETRIEVE_ALL_PIPELINES_FOR_SPECIFIED_OBJECT_TYPE`
- **Stage name → stage ID**: Extract from pipeline stages response
- **Owner name → owner ID**: Use `HUBSPOT_RETRIEVE_OWNERS`

### Pagination
- Search endpoints use cursor-based pagination
- Follow `paging.next.after` until absent
- Typical limit: 100 records per page
- Pass `after` value from previous response to get next page

### Batch Operations
- Most create/update endpoints support batching with max 100 records per call
- For larger datasets, chunk into groups of 100
- Store returned IDs from each batch before proceeding
- Use batch endpoints (`CREATE_CONTACTS`, `CREATE_COMPANIES`, `UPDATE_COMPANIES`) instead of single-record endpoints for efficiency

## Known Pitfalls

- **Property names**: All search/filter endpoints use internal property names, NOT display labels. Always call `READ_ALL_PROPERTIES_FOR_OBJECT_TYPE` to discover correct names
- **Batch limits**: Max 100 records per batch operation. Larger sets must be chunked
- **Response structure**: Search results are nested under `response.data.results` with properties as string values
- **Date formats**: Date properties may be epoch-ms or ISO strings depending on endpoint. Parse defensively
- **Immutable names**: Property names cannot be changed after creation. Plan naming conventions carefully
- **Cursor pagination**: Use `paging.next.after` cursor, not page numbers. Continue until `after` is absent
- **Duplicate prevention**: Always search before creating contacts/companies to avoid duplicates
- **Auth verification**: Run `HUBSPOT_GET_ACCOUNT_INFO` first; auth failures cascade to all subsequent calls

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Create contact | `HUBSPOT_CREATE_CONTACT` | `properties: {email, firstname, lastname}` |
| Batch create contacts | `HUBSPOT_CREATE_CONTACTS` | `inputs: [{properties}]` (max 100) |
| Search contacts | `HUBSPOT_SEARCH_CONTACTS_BY_CRITERIA` | `filterGroups, properties, limit, after` |
| Create companies | `HUBSPOT_CREATE_COMPANIES` | `inputs: [{properties}]` (max 100) |
| Search companies | `HUBSPOT_SEARCH_COMPANIES` | `filterGroups, properties, after` |
| Search deals | `HUBSPOT_SEARCH_DEALS` | `filterGroups, properties, after` |
| Get pipelines | `HUBSPOT_RETRIEVE_ALL_PIPELINES_FOR_SPECIFIED_OBJECT_TYPE` | `objectType: 'deals'` |
| Search tickets | `HUBSPOT_SEARCH_TICKETS` | `filterGroups, properties, after` |
| List properties | `HUBSPOT_READ_ALL_PROPERTIES_FOR_OBJECT_TYPE` | `objectType` |
| Create property | `HUBSPOT_CREATE_PROPERTY_FOR_SPECIFIED_OBJECT_TYPE` | `objectType, name, label, type, fieldType` |
| Get owners | `HUBSPOT_RETRIEVE_OWNERS` | None |
| Verify connection | `HUBSPOT_GET_ACCOUNT_INFO` | None |
---
*Powered by [Composio](https://composio.dev)*
