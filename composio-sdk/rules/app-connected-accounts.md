---
title: Connected Accounts Management
impact: HIGH
description: Comprehensive guide to CRUD operations on connected accounts with emphasis on secure authentication flows
tags: [connected-accounts, authentication, oauth, crud, security]
---

# Connected Accounts Management

> **Using Tool Router?** If you're using Tool Router, you can use `session.toolkits()` to view the auth configs and connected accounts being used by the Tool Router. You only need to use the methods below if you're managing connected accounts outside of Tool Router.

Connected accounts store authentication tokens for external services. Use the `connectedAccounts` API for CRUD operations.

## Create Connected Accounts

### Recommended: link() - Composio-Hosted Authentication

Use `link()` for most flows. Composio handles security, OAuth, and form rendering.

```typescript
const connectionRequest = await composio.connectedAccounts.link(
  'user_123',
  'auth_config_123',
  { callbackUrl: 'https://your-app.com/callback' }
);

// Redirect user to authentication page
window.location.href = connectionRequest.redirectUrl;

// Wait for completion
const account = await connectionRequest.waitForConnection();
```

**Why use link():**
- Handles OAuth security and form UI
- Works with 200+ services
- Whitelabel with your app name/logo (Project Settings on dashboard)
- No custom UI needed

### Advanced: initiate() - Custom Authentication UI

Only use when building custom auth interfaces:

```typescript
// API Key (custom form)
const connection = await composio.connectedAccounts.initiate(
  'user_123',
  'auth_config_456',
  {
    config: AuthScheme.ApiKey({ api_key: apiKey }),
  }
);

// OAuth with extra params (Zendesk, PostHog, etc.)
const connection = await composio.connectedAccounts.initiate(
  'user_123',
  'zendesk_config',
  {
    config: AuthScheme.OAuth2({ subdomain: "your_subdomain" })
  }
);
window.location.href = connection.redirectUrl;
```

**AuthScheme helpers:**
- `AuthScheme.OAuth2({ subdomain: 'example' })`
- `AuthScheme.ApiKey({ api_key: 'key123' })`
- `AuthScheme.Basic({ username: 'user', password: 'pass' })`
- `AuthScheme.BearerToken({ token: 'token123' })`

**Use initiate() only when:**
- Building custom authentication UI
- Handling credentials directly in backend
- OAuth requires extra parameters before redirect

## Read Connected Accounts

```typescript
// List all
const allAccounts = await composio.connectedAccounts.list();

// Filter by user
const userAccounts = await composio.connectedAccounts.list({
  userIds: ['user_123'],
});

// Filter by toolkit
const githubAccounts = await composio.connectedAccounts.list({
  toolkitSlugs: ['github'],
});

// Filter by status
const activeAccounts = await composio.connectedAccounts.list({
  statuses: ['ACTIVE']
});

// Filter by auth config
const configAccounts = await composio.connectedAccounts.list({
  authConfigIds: ['auth_config_123']
});

// Combine filters
const filtered = await composio.connectedAccounts.list({
  userIds: ['user_123'],
  toolkitSlugs: ['github', 'slack'],
  statuses: ['ACTIVE']
});

// Get specific account
const account = await composio.connectedAccounts.get('conn_abc123');
```

**Available filters:**
- `userIds` - Filter by user IDs
- `toolkitSlugs` - Filter by toolkit slugs
- `statuses` - Filter by connection statuses (see below for values)
- `authConfigIds` - Filter by auth config IDs
- `limit` - Results per page
- `cursor` - Pagination cursor
- `orderBy` - 'created_at' or 'updated_at'

## Update Connected Accounts

```typescript
// Enable/disable
await composio.connectedAccounts.enable('conn_abc123');
await composio.connectedAccounts.disable('conn_abc123');

// Refresh credentials (expired OAuth tokens)
await composio.connectedAccounts.refresh('conn_abc123');
```

## Delete Connected Accounts

```typescript
await composio.connectedAccounts.delete('conn_abc123');
```

**Warning:** Permanent deletion. User must re-authenticate.

## Wait for Connection Completion

For async OAuth flows:

```typescript
// Default timeout (60 seconds)
const account = await composio.connectedAccounts.waitForConnection('conn_123');

// Custom timeout (2 minutes)
const account = await composio.connectedAccounts.waitForConnection('conn_123', 120000);
```

**Errors:**
- `ComposioConnectedAccountNotFoundError` - Account doesn't exist
- `ConnectionRequestFailedError` - Connection failed/expired
- `ConnectionRequestTimeoutError` - Timeout exceeded

## Common Patterns

### OAuth Flow

```typescript
// Create connection
async function connectUser(userId, authConfigId) {
  const request = await composio.connectedAccounts.link(
    userId,
    authConfigId,
    { callbackUrl: 'https://app.com/callback' }
  );
  return { redirectUrl: request.redirectUrl };
}

// Handle callback
async function handleCallback(connectionId) {
  try {
    const account = await composio.connectedAccounts.waitForConnection(
      connectionId,
      180000
    );
    return { success: true, account };
  } catch (error) {
    if (error.name === 'ConnectionRequestTimeoutError') {
      return { error: 'Timeout. Please try again.' };
    }
    throw error;
  }
}
```

### Check Active Connections

```typescript
// Filter by status using statuses parameter
async function getUserActiveConnections(userId) {
  const accounts = await composio.connectedAccounts.list({
    userIds: [userId],
    statuses: ['ACTIVE']
  });
  return accounts.items;
}

// Check multiple statuses
async function getUserConnectionsByStatus(userId) {
  const accounts = await composio.connectedAccounts.list({
    userIds: [userId],
    statuses: ['ACTIVE', 'EXPIRED', 'FAILED']
  });
  return accounts.items;
}

async function isToolkitConnected(userId, toolkit) {
  const accounts = await composio.connectedAccounts.list({
    userIds: [userId],
    toolkitSlugs: [toolkit],
    statuses: ['ACTIVE']
  });
  return accounts.items.length > 0;
}
```

**Available statuses:**
- `INITIALIZING` - Connection being set up
- `INITIATED` - Connection initiated, awaiting completion
- `ACTIVE` - Connection active and ready to use
- `FAILED` - Connection failed
- `EXPIRED` - Credentials expired
- `INACTIVE` - Connection disabled

## Key Points

- **Prefer link()** - Security, UI, and whitelabeling handled
- **Store account IDs** - Save in your database, associate with users
- **Check status** - Verify ACTIVE before use, refresh on errors
- **Handle lifecycle** - Disable instead of delete when possible
