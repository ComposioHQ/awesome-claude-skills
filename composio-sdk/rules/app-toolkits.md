---
title: Toolkit Management
impact: MEDIUM
description: Discover and query toolkits, categories, and authentication requirements for application integration
tags: [toolkits, discovery, metadata, categories, apps]
---

# Toolkit Management

Toolkits are collections of related tools (GitHub, Gmail, Slack). Use the `toolkits` API to discover and query toolkit metadata.

**Important:** `toolkits.get()` returns an **array**, not an object with `.items`. Access directly: `toolkits[0]`, `toolkits.length`, etc.

## Get Toolkit Metadata

```typescript
// Get specific toolkit
const github = await composio.toolkits.get('github');
console.log(github.name); // GitHub
console.log(github.authConfigDetails); // Auth details
console.log(github.meta.toolsCount); // Number of tools
console.log(github.meta.triggersCount); // Number of triggers

// Get all toolkits
const all = await composio.toolkits.get();
console.log(all.length); // Number of toolkits
```

**Toolkit properties:**
- `name`, `slug` - Display name and identifier
- `meta` - toolsCount, triggersCount, createdAt, updatedAt
- `authConfigDetails` - Available auth schemes and required fields
- `composioManagedAuthSchemes` - Composio-managed auth
- `baseUrl` - API base URL
- `getCurrentUserEndpoint` - User info endpoint

## Query Parameters

All available filters for `toolkits.get()`:

```typescript
const toolkits = await composio.toolkits.get({
  category: 'developer-tools',           // Filter by category ID
  managedBy: 'composio',                // 'all' | 'composio' | 'project'
  sortBy: 'usage',                      // 'usage' | 'alphabetically'
  limit: 10,                            // Results per page
  cursor: 'next_page_cursor',           // Pagination
});
```

### Examples

```typescript
// Composio-managed only
const composio = await composio.toolkits.get({ managedBy: 'composio' });

// By category
const devTools = await composio.toolkits.get({ category: 'developer-tools' });

// Popular toolkits
const popular = await composio.toolkits.get({ sortBy: 'usage', limit: 10 });

// Paginated
const page1 = await composio.toolkits.get({ limit: 10 });
const page2 = await composio.toolkits.get({ limit: 10, cursor: page1Cursor });
```

## List Categories

```typescript
const categories = await composio.toolkits.listCategories();
console.log(categories.items);
// [
//   { id: 'developer-tools', name: 'Developer Tools' },
//   { id: 'communication', name: 'Communication' },
//   { id: 'productivity', name: 'Productivity' },
// ]
```

## Auth Requirements

### Get Auth Config Creation Fields

Find fields needed to create custom auth config:

```typescript
// All fields for GitHub OAuth2
const fields = await composio.toolkits.getAuthConfigCreationFields(
  'github',
  'OAUTH2'
);

// Only required fields
const required = await composio.toolkits.getAuthConfigCreationFields(
  'github',
  'OAUTH2',
  { requiredOnly: true }
);

console.log(fields);
// [
//   { name: 'client_id', displayName: 'Client ID', type: 'string', required: true },
//   { name: 'client_secret', displayName: 'Client Secret', type: 'string', required: true },
//   { name: 'scopes', displayName: 'Scopes', type: 'string', default: 'repo,user', required: false }
// ]
```

### Get Connected Account Initiation Fields

Find fields needed when calling `initiate()` with custom auth:

```typescript
const fields = await composio.toolkits.getConnectedAccountInitiationFields(
  'zendesk',
  'OAUTH2'
);

// Only required fields
const required = await composio.toolkits.getConnectedAccountInitiationFields(
  'zendesk',
  'OAUTH2',
  { requiredOnly: true }
);

console.log(fields);
// [
//   { name: 'subdomain', displayName: 'Subdomain', type: 'string', required: true }
// ]
```

**Use case:** Some services (Zendesk, PostHog) require extra parameters during OAuth. These fields tell you what's needed.

## Common Patterns

### Build Toolkit Selection UI

```typescript
const toolkits = await composio.toolkits.get({
  sortBy: 'alphabetically'
});

const toolkitOptions = toolkits.map(tk => ({
  value: tk.slug,
  label: tk.name,
  toolCount: tk.meta.toolsCount,
  authSchemes: tk.composioManagedAuthSchemes,
}));
```

### Check If OAuth Requires Extra Fields

```typescript
async function needsExtraParams(toolkit: string, authScheme: string) {
  const fields = await composio.toolkits.getConnectedAccountInitiationFields(
    toolkit,
    authScheme
  );
  return fields.length > 0;
}

// Usage
if (await needsExtraParams('zendesk', 'OAUTH2')) {
  // Show form to collect subdomain
}
```

### Filter Toolkits by Category

```typescript
async function getToolkitsByCategory(categoryId: string) {
  return await composio.toolkits.get({
    category: categoryId,
    sortBy: 'usage',
  });
}
```

## Key Points

- **Returns array** - Not `.items`, access directly
- **managedBy filter** - 'all', 'composio', or 'project'
- **sortBy options** - 'usage' or 'alphabetically'
- **Auth field queries** - Know what's required before creating configs
- **Extra OAuth params** - Some services need subdomain, region, etc.
