---
name: google-admin-automation
description: "Automate Google Workspace Admin tasks via Rube MCP (Composio): manage users, groups, memberships, suspend accounts, create users, add aliases. Always search tools first for current schemas."
requires:
  mcp: [rube]
---

# Google Workspace Admin Automation via Rube MCP

Manage Google Workspace users, groups, memberships, and organizational settings programmatically using Rube MCP (Composio).

**Toolkit docs**: [composio.dev/toolkits/google_admin](https://composio.dev/toolkits/google_admin)

## Prerequisites
- Rube MCP must be connected (RUBE_SEARCH_TOOLS available)
- Active connection via `RUBE_MANAGE_CONNECTIONS` with toolkit `google_admin`
- Google Workspace admin privileges for the authenticated account
- Always call `RUBE_SEARCH_TOOLS` first to get current tool schemas

## Setup
**Get Rube MCP**: Add `https://rube.app/mcp` as an MCP server in your client configuration. No API keys needed — just add the endpoint and it works.

1. Verify Rube MCP is available by confirming `RUBE_SEARCH_TOOLS` responds
2. Call `RUBE_MANAGE_CONNECTIONS` with toolkit `google_admin`
3. If connection is not ACTIVE, follow the returned auth link to complete setup
4. Confirm connection status shows ACTIVE before running any workflows

## Core Workflows

### 1. List All Users
Use `GOOGLE_ADMIN_LIST_USERS` to retrieve Google Workspace users with optional filtering and pagination.
```
Tool: GOOGLE_ADMIN_LIST_USERS
Parameters:
  - customer: Customer ID or "my_customer" (default)
  - domain: Domain to list users from
  - query: Filter string (e.g., "orgName=Engineering", "isSuspended=false")
  - max_results: Maximum results (1-500, default 100)
  - order_by: Sort by "email", "givenName", or "familyName"
  - sort_order: "ASCENDING" or "DESCENDING"
  - page_token: Pagination token
```

### 2. Create a New User
Use `GOOGLE_ADMIN_CREATE_USER` to provision a new Google Workspace account.
```
Tool: GOOGLE_ADMIN_CREATE_USER
Parameters:
  - primary_email (required): User's email (e.g., "john.doe@company.com")
  - given_name (required): First name
  - family_name (required): Last name
  - password (required): Password meeting domain requirements
  - org_unit_path: Organizational unit (default: "/")
  - change_password_at_next_login: Force password change (default: true)
  - recovery_email: Recovery email address
  - recovery_phone: Recovery phone number
  - suspended: Whether account starts suspended (default: false)
```

### 3. List and Manage Groups
Use `GOOGLE_ADMIN_LIST_GROUPS` to list groups, and `GOOGLE_ADMIN_CREATE_GROUP` to create new ones.
```
Tool: GOOGLE_ADMIN_LIST_GROUPS
Parameters:
  - customer: "my_customer" (default)
  - domain: Filter by domain
  - query: Filter (e.g., "name=Engineering*")
  - max_results: Max results (1-200)
  - order_by: Sort by "email"
  - page_token: Pagination token

Tool: GOOGLE_ADMIN_CREATE_GROUP
Parameters:
  - email (required): Group email address (e.g., "engineering@company.com")
  - name (required): Display name (e.g., "Engineering Team")
  - description: Group purpose description
```

### 4. Add Users to Groups
Use `GOOGLE_ADMIN_ADD_USER_TO_GROUP` to manage group membership.
```
Tool: GOOGLE_ADMIN_ADD_USER_TO_GROUP
Parameters:
  - group_key (required): Group email or ID
  - user_key (required): User email or ID to add
  - role: "MEMBER" (default), "MANAGER", or "OWNER"
```

### 5. Suspend or Unsuspend Users
Use `GOOGLE_ADMIN_SUSPEND_USER` to toggle user account suspension.
```
Tool: GOOGLE_ADMIN_SUSPEND_USER
Parameters:
  - user_key (required): User's email or unique ID
  - suspended: true to suspend, false to unsuspend (default: true)
  - suspension_reason: Reason for suspension (optional)
```

### 6. Get User or Group Details
Use `GOOGLE_ADMIN_GET_USER` or `GOOGLE_ADMIN_GET_GROUP` to retrieve detailed information.
```
Tool: GOOGLE_ADMIN_GET_USER
Parameters:
  - user_key (required): User's email or unique ID

Tool: GOOGLE_ADMIN_GET_GROUP
Parameters:
  - group_key (required): Group's email or unique ID
```

## Common Patterns

- **Onboarding workflow**: Use `GOOGLE_ADMIN_CREATE_USER` to provision the account, then `GOOGLE_ADMIN_ADD_USER_TO_GROUP` to add them to relevant groups.
- **Offboarding workflow**: Use `GOOGLE_ADMIN_SUSPEND_USER` to disable access, or `GOOGLE_ADMIN_DELETE_USER` for permanent removal.
- **Audit group membership**: Use `GOOGLE_ADMIN_LIST_GROUPS` to find groups, then `GOOGLE_ADMIN_LIST_GROUP_MEMBERS` to review members.
- **Bulk user management**: List users with `GOOGLE_ADMIN_LIST_USERS` and filter queries, then iterate for updates.
- **Add email aliases**: Use `GOOGLE_ADMIN_ADD_USER_ALIAS` to add alternative email addresses for a user.
- **Look up user details**: Use `GOOGLE_ADMIN_GET_USER` to retrieve full profile information before making changes.

## Known Pitfalls

- **Admin privileges required**: All tools require the authenticated user to have Google Workspace administrator privileges. Non-admin accounts will receive permission errors.
- **Delete is permanent**: `GOOGLE_ADMIN_DELETE_USER` permanently removes a user account. This action cannot be undone.
- **user_key accepts email or ID**: The `user_key` parameter accepts both the user's primary email address and their unique numeric user ID.
- **Group membership replaces**: When adding to groups, the `role` parameter controls the member's role. There is no "update role" -- remove and re-add to change roles.
- **Customer ID**: Use `"my_customer"` as the `customer` parameter for the authenticated user's organization. Specific customer IDs look like `C01abc123`.
- **Pagination**: Both user and group list endpoints may return paginated results. Always check for `page_token` in responses for complete results.
- **Password requirements**: `GOOGLE_ADMIN_CREATE_USER` requires a password that meets the domain's password policy. Weak passwords will be rejected.

## Quick Reference
| Action | Tool | Key Parameters |
|--------|------|----------------|
| List users | `GOOGLE_ADMIN_LIST_USERS` | `customer`, `domain`, `query`, `max_results` |
| Get user details | `GOOGLE_ADMIN_GET_USER` | `user_key` |
| Create user | `GOOGLE_ADMIN_CREATE_USER` | `primary_email`, `given_name`, `family_name`, `password` |
| Delete user | `GOOGLE_ADMIN_DELETE_USER` | `user_key` |
| Suspend user | `GOOGLE_ADMIN_SUSPEND_USER` | `user_key`, `suspended` |
| Add user alias | `GOOGLE_ADMIN_ADD_USER_ALIAS` | (see full schema via RUBE_SEARCH_TOOLS) |
| List groups | `GOOGLE_ADMIN_LIST_GROUPS` | `customer`, `domain`, `query` |
| Get group details | `GOOGLE_ADMIN_GET_GROUP` | `group_key` |
| Create group | `GOOGLE_ADMIN_CREATE_GROUP` | `email`, `name`, `description` |
| Add to group | `GOOGLE_ADMIN_ADD_USER_TO_GROUP` | `group_key`, `user_key`, `role` |
| List group members | `GOOGLE_ADMIN_LIST_GROUP_MEMBERS` | (see full schema via RUBE_SEARCH_TOOLS) |

---
*Powered by [Composio](https://composio.dev)*
