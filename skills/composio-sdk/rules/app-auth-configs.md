---
title: Auth Config Management
impact: MEDIUM
description: Advanced programmatic management of authentication configurations for multi-tenant applications
tags: [auth-config, authentication, oauth, api-key, advanced]
---

# Auth Config Management

> **Note:** This is an **advanced use case**. Most users should create and manage auth configs through the Composio dashboard at [platform.composio.dev](https://platform.composio.dev). Use the SDK methods below only when you need programmatic auth config management.

> **Using Tool Router?** If you're using Tool Router, you can use `session.toolkits()` to view the auth configs and connected accounts being used by the Tool Router. You only need to use the methods below if you're creating custom auth configs to be used with Tool Router.

Auth configs define how authentication works for a toolkit. They specify the authentication scheme (OAuth2, API Key, etc.) and control which tools can be accessed.

## When to Use the SDK

Use these methods when you need to:
- Programmatically create auth configs for multi-tenant applications
- Dynamically manage auth configs based on user actions
- Automate auth config creation in CI/CD pipelines

For most cases, **use the dashboard** instead.

## Read Auth Configs

### List auth configs

```typescript
// List all auth configs
const configs = await composio.authConfigs.list();

// List for a specific toolkit
const githubConfigs = await composio.authConfigs.list({
  toolkit: 'github',
});

// Filter by Composio-managed
const managedConfigs = await composio.authConfigs.list({
  isComposioManaged: true,
});
```

### Get a specific auth config

```typescript
const authConfig = await composio.authConfigs.get('auth_config_123');
console.log(authConfig.name);
console.log(authConfig.authScheme); // 'OAUTH2', 'API_KEY', etc.
console.log(authConfig.toolkit.slug);
```

## Create Auth Configs

### Composio-Managed Authentication (Recommended)

Use Composio's OAuth credentials (simplest option):

```typescript
const authConfig = await composio.authConfigs.create('github', {
  type: 'use_composio_managed_auth',
  name: 'GitHub Auth Config',
});
```

### Custom OAuth Credentials

Use your own OAuth app credentials:

```typescript
const authConfig = await composio.authConfigs.create('slack', {
  type: 'use_custom_auth',
  name: 'My Slack Auth',
  authScheme: 'OAUTH2',
  credentials: {
    client_id: 'your_client_id',
    client_secret: 'your_client_secret',
  }
});
```

### Custom API Key Authentication

For services using API keys:

```typescript
const authConfig = await composio.authConfigs.create('openai', {
  type: 'use_custom_auth',
  name: 'OpenAI API Key Auth',
  authScheme: 'API_KEY',
  credentials: {
    api_key: 'your_api_key',
  }
});
```

## Update Auth Configs

### Update custom auth credentials

```typescript
const updated = await composio.authConfigs.update('auth_config_123', {
  type: 'custom',
  credentials: {
    client_id: 'new_client_id',
    client_secret: 'new_client_secret',
  }
});
```

### Update OAuth scopes

```typescript
const updated = await composio.authConfigs.update('auth_config_456', {
  type: 'default',
  scopes: 'read:user,repo'
});
```

### Restrict tools (for security)

```typescript
const restricted = await composio.authConfigs.update('auth_config_789', {
  type: 'custom',
  credentials: { /* ... */ },
  toolAccessConfig: {
    toolsAvailableForExecution: ['SLACK_SEND_MESSAGE', 'SLACK_GET_CHANNEL']
  }
});
```

## Enable/Disable Auth Configs

```typescript
// Enable an auth config
await composio.authConfigs.enable('auth_config_123');

// Disable an auth config
await composio.authConfigs.disable('auth_config_123');
```

## Delete Auth Configs

```typescript
await composio.authConfigs.delete('auth_config_123');
```

**Warning:** Deleting an auth config will affect all connected accounts using it.

## Available Parameters

### List Parameters

- `toolkit` (string) - Filter by toolkit slug
- `isComposioManaged` (boolean) - Filter Composio-managed vs custom
- `limit` (number) - Results per page
- `cursor` (string) - Pagination cursor

### Create Parameters

**For `use_composio_managed_auth`:**
- `type`: `'use_composio_managed_auth'`
- `name` (optional): Display name
- `credentials` (optional): Object with `scopes` field
- `toolAccessConfig` (optional): Tool restrictions
- `isEnabledForToolRouter` (optional): Enable for Tool Router

**For `use_custom_auth`:**
- `type`: `'use_custom_auth'`
- `authScheme`: `'OAUTH2'`, `'API_KEY'`, `'BASIC_AUTH'`, etc.
- `name` (optional): Display name
- `credentials`: Object with auth-specific fields (client_id, client_secret, api_key, etc.)
- `toolAccessConfig` (optional): Tool restrictions
- `isEnabledForToolRouter` (optional): Enable for Tool Router

### Update Parameters

**For custom type:**
```typescript
{
  type: 'custom',
  credentials: { /* auth fields */ },
  toolAccessConfig: {
    toolsAvailableForExecution: ['TOOL_SLUG_1', 'TOOL_SLUG_2']
  }
}
```

**For default type:**
```typescript
{
  type: 'default',
  scopes: 'scope1,scope2',
  toolAccessConfig: {
    toolsAvailableForExecution: ['TOOL_SLUG_1', 'TOOL_SLUG_2']
  }
}
```

## Best Practices

1. **Use the dashboard for manual setup**
   - Easier to configure
   - Visual interface for OAuth setup
   - Less error-prone

2. **Use SDK for automation only**
   - Multi-tenant app provisioning
   - CI/CD integration
   - Dynamic configuration

3. **Prefer Composio-managed auth**
   - No OAuth app setup required
   - Maintained by Composio
   - Works out of the box

4. **Restrict tools for security**
   - Limit `toolsAvailableForExecution`
   - Implements least privilege
   - Reduces risk

5. **Name configs clearly**
   - Include environment: "Production GitHub", "Staging Slack"
   - Makes debugging easier
