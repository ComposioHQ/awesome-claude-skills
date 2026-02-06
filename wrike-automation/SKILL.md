---
name: wrike-automation
description: "Automate Wrike project management via Rube MCP (Composio): create tasks/folders, manage projects, assign work, and track progress. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Wrike Automation via Rube MCP

Automate Wrike project management operations through Composio's Wrike toolkit via Rube MCP.

## Prerequisites

- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active Wrike connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `wrike`
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup

**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.


1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `wrike`
3. If connection is not ACTIVE, follow the returned auth link to complete Wrike OAuth
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. Create and Manage Tasks

**When to use**: User wants to create, assign, or update tasks in Wrike

**Tool sequence**:
1. `WRIKE_GET_FOLDERS` - Find the target folder/project [Prerequisite]
2. `WRIKE_GET_ALL_CUSTOM_FIELDS` - Get custom field IDs if needed [Optional]
3. `WRIKE_CREATE_TASK` - Create a new task [Required]
4. `WRIKE_MODIFY_TASK` - Update task properties [Optional]

**Key parameters**:
- `folderId`: Parent folder ID where the task will be created
- `title`: Task title
- `description`: Task description (supports HTML)
- `responsibles`: Array of user IDs to assign
- `status`: 'Active', 'Completed', 'Deferred', 'Cancelled'
- `importance`: 'High', 'Normal', 'Low'
- `customFields`: Array of {id, value} objects
- `dates`: Object with type, start, due, duration

**Pitfalls**:
- folderId is required; tasks must belong to a folder
- responsibles requires Wrike user IDs, not emails or names
- Custom field IDs must be obtained from GET_ALL_CUSTOM_FIELDS
- priorityBefore and priorityAfter are mutually exclusive
- Status field may not be available on Team plan
- dates.start and dates.due use 'YYYY-MM-DD' format

### 2. Manage Folders and Projects

**When to use**: User wants to create, modify, or organize folders and projects

**Tool sequence**:
1. `WRIKE_GET_FOLDERS` - List existing folders [Required]
2. `WRIKE_CREATE_FOLDER` - Create a new folder/project [Optional]
3. `WRIKE_MODIFY_FOLDER` - Update folder properties [Optional]
4. `WRIKE_LIST_SUBFOLDERS_BY_FOLDER_ID` - List subfolders [Optional]
5. `WRIKE_DELETE_FOLDER` - Delete a folder permanently [Optional]

**Key parameters**:
- `folderId`: Parent folder ID for creation; target folder ID for modification
- `title`: Folder name
- `description`: Folder description
- `customItemTypeId`: Set to create as a project instead of a folder
- `shareds`: Array of user IDs or emails to share with
- `project`: Filter for projects (true) or folders (false) in GET_FOLDERS

**Pitfalls**:
- DELETE_FOLDER is permanent and removes ALL contents (tasks, subfolders, documents)
- Cannot modify rootFolderId or recycleBinId as parents
- Folder creation auto-shares with the creator
- customItemTypeId converts a folder into a project
- GET_FOLDERS with descendants=true returns folder tree (may be large)

### 3. Retrieve and Track Tasks

**When to use**: User wants to find tasks, check status, or monitor progress

**Tool sequence**:
1. `WRIKE_FETCH_ALL_TASKS` - List tasks with optional filters [Required]
2. `WRIKE_GET_TASK_BY_ID` - Get detailed info for a specific task [Optional]

**Key parameters**:
- `status`: Filter by task status ('Active', 'Completed', etc.)
- `dueDate`: Filter by due date range (start/end/equal)
- `fields`: Additional response fields to include
- `page_size`: Results per page (1-100)
- `taskId`: Specific task ID for detailed retrieval
- `resolve_user_names`: Auto-resolve user IDs to names (default true)

**Pitfalls**:
- FETCH_ALL_TASKS paginates at max 100 items per page
- dueDate filter supports 'equal', 'start', and 'end' fields
- Date format: 'yyyy-MM-dd' or 'yyyy-MM-ddTHH:mm:ss'
- GET_TASK_BY_ID returns read-only detailed information
- customFields are returned by default for single task queries

### 4. Launch Task Blueprints

**When to use**: User wants to create tasks from predefined templates

**Tool sequence**:
1. `WRIKE_LIST_TASK_BLUEPRINTS` - List available blueprints [Prerequisite]
2. `WRIKE_LIST_SPACE_TASK_BLUEPRINTS` - List blueprints in a specific space [Alternative]
3. `WRIKE_LAUNCH_TASK_BLUEPRINT_ASYNC` - Launch a blueprint [Required]

**Key parameters**:
- `task_blueprint_id`: ID of the blueprint to launch
- `title`: Title for the root task
- `parent_id`: Parent folder/project ID (OR super_task_id)
- `super_task_id`: Parent task ID (OR parent_id)
- `reschedule_date`: Target date for task rescheduling
- `reschedule_mode`: 'RescheduleStartDate' or 'RescheduleFinishDate'
- `entry_limit`: Max tasks to copy (1-250)

**Pitfalls**:
- Either parent_id or super_task_id is required, not both
- Blueprint launch is asynchronous; tasks may take time to appear
- reschedule_date requires reschedule_mode to be set
- entry_limit caps at 250 tasks/folders per blueprint launch
- copy_descriptions defaults to false; set true to include task descriptions

### 5. Manage Workspace and Members

**When to use**: User wants to manage spaces, members, or invitations

**Tool sequence**:
1. `WRIKE_GET_SPACE` - Get space details [Optional]
2. `WRIKE_GET_CONTACTS` - List workspace contacts/members [Optional]
3. `WRIKE_CREATE_INVITATION` - Invite a user to the workspace [Optional]
4. `WRIKE_DELETE_SPACE` - Delete a space permanently [Optional]

**Key parameters**:
- `spaceId`: Space identifier
- `email`: Email for invitation
- `role`: User role ('Admin', 'Regular User', 'External User')
- `firstName`/`lastName`: Invitee name

**Pitfalls**:
- DELETE_SPACE is irreversible and removes all space contents
- userTypeId and role/external are mutually exclusive in invitations
- Custom email subjects/messages require a paid Wrike plan
- GET_CONTACTS returns workspace-level contacts, not task-specific assignments

## Common Patterns

### Folder ID Resolution

```
1. Call WRIKE_GET_FOLDERS (optionally with project=true for projects only)
2. Navigate folder tree to find target
3. Extract folder id (e.g., 'IEAGKVLFK4IHGQOI')
4. Use as folderId in task/folder creation
```

### Custom Field Setup

```
1. Call WRIKE_GET_ALL_CUSTOM_FIELDS to get definitions
2. Find field by name, extract id and type
3. Format value according to type (text, dropdown, number, date)
4. Include as {id: 'FIELD_ID', value: 'VALUE'} in customFields array
```

### Task Assignment

```
1. Call WRIKE_GET_CONTACTS to find user IDs
2. Use user IDs in responsibles array when creating tasks
3. Or use addResponsibles/removeResponsibles when modifying tasks
```

### Pagination

- FETCH_ALL_TASKS: Use page_size (max 100) and check for more results
- GET_FOLDERS: Use nextPageToken when descendants=false and pageSize is set
- LIST_TASK_BLUEPRINTS: Use next_page_token and page_size (default 100)

## Known Pitfalls

**ID Formats**:
- Wrike IDs are opaque alphanumeric strings (e.g., 'IEAGTXR7I4IHGABC')
- Task IDs, folder IDs, space IDs, and user IDs all use this format
- Custom field IDs follow the same pattern
- Never guess IDs; always resolve from list/search operations

**Permissions**:
- Operations depend on user role and sharing settings
- Shared folders/tasks are visible only to shared users
- Admin operations require appropriate role
- Some features (custom statuses, billing types) are plan-dependent

**Deletion Safety**:
- DELETE_FOLDER removes ALL contents permanently
- DELETE_SPACE removes the entire space and contents
- Consider using MODIFY_FOLDER to move to recycle bin instead
- Restore from recycle bin is possible via MODIFY_FOLDER with restore=true

**Date Handling**:
- Dates use 'yyyy-MM-dd' format
- DateTime uses 'yyyy-MM-ddTHH:mm:ssZ' or with timezone offset
- Task dates include type ('Planned', 'Actual'), start, due, duration
- Duration is in minutes

## Quick Reference

| Task | Tool Slug | Key Params |
|------|-----------|------------|
| Create task | WRIKE_CREATE_TASK | folderId, title, responsibles, status |
| Modify task | WRIKE_MODIFY_TASK | taskId, title, status, addResponsibles |
| Get task by ID | WRIKE_GET_TASK_BY_ID | taskId |
| Fetch all tasks | WRIKE_FETCH_ALL_TASKS | status, dueDate, page_size |
| Get folders | WRIKE_GET_FOLDERS | project, descendants |
| Create folder | WRIKE_CREATE_FOLDER | folderId, title |
| Modify folder | WRIKE_MODIFY_FOLDER | folderId, title, addShareds |
| Delete folder | WRIKE_DELETE_FOLDER | folderId |
| List subfolders | WRIKE_LIST_SUBFOLDERS_BY_FOLDER_ID | folderId |
| Get custom fields | WRIKE_GET_ALL_CUSTOM_FIELDS | (none) |
| List blueprints | WRIKE_LIST_TASK_BLUEPRINTS | limit, page_size |
| Launch blueprint | WRIKE_LAUNCH_TASK_BLUEPRINT_ASYNC | task_blueprint_id, title, parent_id |
| Get space | WRIKE_GET_SPACE | spaceId |
| Delete space | WRIKE_DELETE_SPACE | spaceId |
| Get contacts | WRIKE_GET_CONTACTS | (none) |
| Invite user | WRIKE_CREATE_INVITATION | email, role |
