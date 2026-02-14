---
title: User Context and ID Patterns for Applications
impact: HIGH
description: Critical patterns for user identification, multi-tenancy, and data isolation in production applications
tags: [user-context, security, multi-tenancy, isolation, production]
---

# User Context and ID Patterns

Every Composio operation requires a `userId` parameter for security and data isolation. Users can only access their own connected accounts.

## The 'default' User ID

`default` refers to your project's default account.

**Only use 'default' for:**
- Testing and development
- Single-user applications
- Internal tools with no external users

**Never use in production multi-user apps** - it bypasses user isolation.

## Production User ID Patterns

### Database UUID (Recommended)

Use your database's primary key:

```typescript
const userId = user.id; // "550e8400-e29b-41d4-a716-446655440000"

await composio.tools.execute('GITHUB_GET_REPO', {
  userId: userId,
  arguments: { owner: 'example', repo: 'repo' },
});
```

**Pros:** Stable, immutable, already exists, no mapping needed

### External Auth ID (Acceptable)

Use IDs from Auth0, Firebase, etc:

```typescript
const userId = user.externalId; // "auth0|507f1f77bcf86cd799439011"
// Or with prefix
const userId = `user_${user.id}`; // "user_12345"
```

**Pros:** Works with external auth, human-readable, allows namespacing
**Cons:** May require mapping, usernames can change

### Email (Not Recommended)

```typescript
const userId = user.email; // "user@example.com"
```

**Only use when:**
- Email is guaranteed immutable
- No other unique identifier available
- SSO requires email-based identification

**Cons:** Emails can change, privacy concerns

## Organization-Based Applications

For team/org-wide tool access, use organization ID as `userId`:

```typescript
// All users in org share same connected accounts
const userId = organization.id; // "org_550e8400..."

await composio.tools.execute('SLACK_SEND_MESSAGE', {
  userId: userId, // organization ID, not individual user
  arguments: { channel: '#general', text: 'Team message' },
});
```

**Use organization IDs when:**
- Team/org tools (Slack, MS Teams, Jira)
- Enterprise apps with IT admin connections
- Shared resources across users
- Role-based access at org level

**Example:**

```typescript
// Admin connects Slack for entire org
async function connectOrgToSlack(orgId: string) {
  const request = await composio.connectedAccounts.link(orgId, 'slack');
  return request.redirectUrl;
}

// Any user in org can use connected tools
async function sendMessage(orgId: string, message: string) {
  return await composio.tools.execute('SLACK_SEND_MESSAGE', {
    userId: orgId,
    arguments: { channel: '#general', text: message },
  });
}

// Check org connections
async function listOrgConnections(orgId: string) {
  return await composio.connectedAccounts.list({
    userIds: [orgId],
  });
}
```

## Shared vs. Isolated Connections

### Isolated (User-Level)

Each user has their own connections:

```typescript
await composio.connectedAccounts.link('user_123', 'github_config');
await composio.connectedAccounts.link('user_456', 'github_config');

// Each execution uses that user's account
await composio.tools.execute('GITHUB_GET_REPO', {
  userId: 'user_123', // Uses user_123's GitHub
  arguments: { ... },
});
```

**Use for:** Personal integrations, individual credentials, privacy-critical

### Shared (Organization-Level)

All users share organization connections:

```typescript
await composio.connectedAccounts.link('org_acme', 'github_config');

// All org users use same connection
await composio.tools.execute('GITHUB_GET_REPO', {
  userId: 'org_acme', // All users share
  arguments: { ... },
});
```

**Use for:** Org-wide access, centralized credentials, simplified administration

## Security Best Practices

### Never Expose User IDs to Frontend

```typescript
// ❌ DON'T: Allow frontend to specify userId
app.post('/execute-tool', async (req, res) => {
  await composio.tools.execute(req.body.tool, {
    userId: req.body.userId, // SECURITY RISK
    arguments: req.body.arguments,
  });
});

// ✅ DO: Derive userId from authenticated session
app.post('/execute-tool', async (req, res) => {
  const userId = req.user.id; // From auth session
  await composio.tools.execute(req.body.tool, {
    userId: userId,
    arguments: req.body.arguments,
  });
});
```

### Validate User Ownership

```typescript
async function executeForUser(authenticatedUserId, targetUserId, tool, args) {
  if (authenticatedUserId !== targetUserId) {
    throw new Error('Unauthorized');
  }
  return await composio.tools.execute(tool, {
    userId: targetUserId,
    arguments: args,
  });
}
```

## Common Patterns

### Express Middleware

```typescript
app.use((req, res, next) => {
  req.userId = req.user.id; // From authenticated session
  next();
});

app.post('/execute-tool', async (req, res) => {
  const result = await composio.tools.execute(req.body.tool, {
    userId: req.userId,
    arguments: req.body.arguments,
  });
  res.json(result);
});
```

### Debug User Context

```typescript
const accounts = await composio.connectedAccounts.list({
  userIds: [userId],
});

console.log(`User ${userId} has ${accounts.items.length} accounts`);
accounts.items.forEach(account => {
  console.log(`- ${account.toolkit.slug}: ${account.status}`);
});
```

## Key Points

- **Use database UUIDs** - Most stable and reliable
- **Never expose userId** - Always derive from authenticated session
- **Validate ownership** - Ensure users only access their data
- **Use consistent format** - Pick one pattern and stick to it
- **Organization IDs** - For team-wide tool access
- **Handle changes gracefully** - Maintain mapping if IDs can change
