---
name: salesforce-automation
description: "Automate Salesforce tasks via Rube MCP (Composio): leads, contacts, accounts, opportunities, SOQL queries. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Salesforce Automation via Rube MCP

Automate Salesforce CRM operations through Composio's Salesforce toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Salesforce connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `salesforce`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `salesforce`
3. If connection is not ACTIVE, follow the returned auth link to complete Salesforce OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Manage Leads

**When to use**: User wants to create, search, update, or list leads

**Tool sequence**:
1. `SALESFORCE_SEARCH_LEADS` - Search leads by criteria [Optional]
2. `SALESFORCE_LIST_LEADS` - List all leads [Optional]
3. `SALESFORCE_CREATE_LEAD` - Create a new lead [Optional]
4. `SALESFORCE_UPDATE_LEAD` - Update lead fields [Optional]
5. `SALESFORCE_ADD_LEAD_TO_CAMPAIGN` - Add lead to campaign [Optional]
6. `SALESFORCE_APPLY_LEAD_ASSIGNMENT_RULES` - Apply assignment rules [Optional]

**Key parameters**:
- `LastName`: Required for lead creation
- `Company`: Required for lead creation
- `Email`, `Phone`, `Title`: Common lead fields
- `lead_id`: Lead ID for updates
- `campaign_id`: Campaign ID for campaign operations

**Pitfalls**:
- LastName and Company are required fields for lead creation
- Lead IDs are 15 or 18 character Salesforce IDs

### 2. Manage Contacts and Accounts

**When to use**: User wants to manage contacts and their associated accounts

**Tool sequence**:
1. `SALESFORCE_SEARCH_CONTACTS` - Search contacts [Optional]
2. `SALESFORCE_LIST_CONTACTS` - List contacts [Optional]
3. `SALESFORCE_CREATE_CONTACT` - Create a new contact [Optional]
4. `SALESFORCE_SEARCH_ACCOUNTS` - Search accounts [Optional]
5. `SALESFORCE_CREATE_ACCOUNT` - Create a new account [Optional]
6. `SALESFORCE_ASSOCIATE_CONTACT_TO_ACCOUNT` - Link contact to account [Optional]

**Key parameters**:
- `LastName`: Required for contact creation
- `Name`: Account name for creation
- `AccountId`: Account ID to associate with contact
- `contact_id`, `account_id`: IDs for association

**Pitfalls**:
- Contact requires at least LastName
- Account association requires both valid contact and account IDs

### 3. Manage Opportunities

**When to use**: User wants to track and manage sales opportunities

**Tool sequence**:
1. `SALESFORCE_SEARCH_OPPORTUNITIES` - Search opportunities [Optional]
2. `SALESFORCE_LIST_OPPORTUNITIES` - List all opportunities [Optional]
3. `SALESFORCE_GET_OPPORTUNITY` - Get opportunity details [Optional]
4. `SALESFORCE_CREATE_OPPORTUNITY` - Create new opportunity [Optional]
5. `SALESFORCE_RETRIEVE_OPPORTUNITIES_DATA` - Retrieve opportunity data [Optional]

**Key parameters**:
- `Name`: Opportunity name (required)
- `StageName`: Sales stage (required)
- `CloseDate`: Expected close date (required)
- `Amount`: Deal value
- `AccountId`: Associated account

**Pitfalls**:
- Name, StageName, and CloseDate are required for creation
- Stage names must match exactly what is configured in Salesforce

### 4. Run SOQL Queries

**When to use**: User wants to query Salesforce data with custom SOQL

**Tool sequence**:
1. `SALESFORCE_RUN_SOQL_QUERY` / `SALESFORCE_QUERY` - Execute SOQL [Required]

**Key parameters**:
- `query`: SOQL query string

**Pitfalls**:
- SOQL syntax differs from SQL; uses Salesforce object and field API names
- Field API names may differ from display labels (e.g., `Account.Name` not `Account Name`)
- Results are paginated for large datasets

### 5. Manage Tasks

**When to use**: User wants to create, search, update, or complete tasks

**Tool sequence**:
1. `SALESFORCE_SEARCH_TASKS` - Search tasks [Optional]
2. `SALESFORCE_UPDATE_TASK` - Update task fields [Optional]
3. `SALESFORCE_COMPLETE_TASK` - Mark task as complete [Optional]

**Key parameters**:
- `task_id`: Task ID for updates
- `Status`: Task status value
- `Subject`: Task subject

**Pitfalls**:
- Task status values must match picklist options in Salesforce

## Common Patterns

### SOQL Syntax

**Basic query**:
```
SELECT Id, Name, Email FROM Contact WHERE LastName = 'Smith'
```

**With relationships**:
```
SELECT Id, Name, Account.Name FROM Contact WHERE Account.Industry = 'Technology'
```

**Date filtering**:
```
SELECT Id, Name FROM Lead WHERE CreatedDate = TODAY
SELECT Id, Name FROM Opportunity WHERE CloseDate = NEXT_MONTH
```

### Pagination

- SOQL queries with large results return pagination tokens
- Use `SALESFORCE_QUERY` with nextRecordsUrl for pagination
- Check `done` field in response; if false, continue paging

## Known Pitfalls

**Field API Names**:
- Always use API names, not display labels
- Custom fields end with `__c` suffix
- Use SALESFORCE_GET_ALL_CUSTOM_OBJECTS to discover custom objects

**ID Formats**:
- Salesforce IDs are 15 (case-sensitive) or 18 (case-insensitive) characters
- Both formats are accepted in most operations

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Create lead | SALESFORCE_CREATE_LEAD | LastName, Company |
| Search leads | SALESFORCE_SEARCH_LEADS | query |
| List leads | SALESFORCE_LIST_LEADS | (filters) |
| Update lead | SALESFORCE_UPDATE_LEAD | lead_id, fields |
| Create contact | SALESFORCE_CREATE_CONTACT | LastName |
| Search contacts | SALESFORCE_SEARCH_CONTACTS | query |
| Create account | SALESFORCE_CREATE_ACCOUNT | Name |
| Search accounts | SALESFORCE_SEARCH_ACCOUNTS | query |
| Link contact | SALESFORCE_ASSOCIATE_CONTACT_TO_ACCOUNT | contact_id, account_id |
| Create opportunity | SALESFORCE_CREATE_OPPORTUNITY | Name, StageName, CloseDate |
| Get opportunity | SALESFORCE_GET_OPPORTUNITY | opportunity_id |
| Search opportunities | SALESFORCE_SEARCH_OPPORTUNITIES | query |
| Run SOQL | SALESFORCE_RUN_SOQL_QUERY | query |
| Query | SALESFORCE_QUERY | query |
| Search tasks | SALESFORCE_SEARCH_TASKS | query |
| Update task | SALESFORCE_UPDATE_TASK | task_id, fields |
| Complete task | SALESFORCE_COMPLETE_TASK | task_id |
| Get user info | SALESFORCE_GET_USER_INFO | (none) |
| Custom objects | SALESFORCE_GET_ALL_CUSTOM_OBJECTS | (none) |
| Create record | SALESFORCE_CREATE_A_RECORD | object_type, fields |
| Transfer ownership | SALESFORCE_MASS_TRANSFER_OWNERSHIP | records, new_owner |
