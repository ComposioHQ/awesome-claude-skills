---
title: Choose User IDs Carefully for Security and Isolation
impact: CRITICAL
description: Use proper user IDs to ensure data isolation, security, and correct session management
tags: [tool-router, user-id, security, authentication, multi-tenant]
---

# Choose User IDs Carefully for Security and Isolation

User IDs are the **foundation of Tool Router isolation**. They determine which user's connections, data, and permissions are used for tool execution. Choose them carefully to ensure security and proper data isolation.

## ❌ Incorrect

```typescript
// DON'T: Use 'default' in production multi-user apps
async function handleUserRequest(req: Request) {
  const session = await composio.create('default', {
    toolkits: ['gmail', 'slack']
  });

  // ❌ All users share the same session
  // ❌ No data isolation
  // ❌ Security nightmare
  // ❌ User A can access User B's emails!
}
```

```python
# DON'T: Use 'default' in production multi-user apps
async def handle_user_request(req):
    session = composio.tool_router.create(
        user_id="default",
        toolkits=["gmail", "slack"]
    )

    # ❌ All users share the same session
    # ❌ No data isolation
    # ❌ Security nightmare
    # ❌ User A can access User B's emails!
```

```typescript
// DON'T: Use email addresses as user IDs
async function handleUserRequest(req: Request) {
  const session = await composio.create(req.user.email, {
    toolkits: ['github']
  });

  // ❌ Emails can change
  // ❌ Breaks session continuity
  // ❌ Historical data loss
}
```

## ✅ Correct - Use Database User IDs

```typescript
// DO: Use your database user ID (UUID, primary key, etc.)
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';

const composio = new Composio({
  provider: new VercelProvider()
});

async function handleUserRequest(req: Request) {
  // Get user ID from your auth system
  const userId = req.user.id; // e.g., "550e8400-e29b-41d4-a716-446655440000"

  // Create isolated session for this user
  const session = await composio.create(userId, {
    toolkits: ['gmail', 'slack']
  });

  const tools = await session.tools();

  // ✅ Each user gets their own session
  // ✅ Complete data isolation
  // ✅ User A cannot access User B's data
  // ✅ Connections tied to correct user
  return await agent.run(req.message, tools);
}
```

```python
# DO: Use your database user ID (UUID, primary key, etc.)
from composio import Composio
from composio_openai import OpenAIProvider

composio = Composio(provider=OpenAIProvider())

async def handle_user_request(req):
    # Get user ID from your auth system
    user_id = req.user.id  # e.g., "550e8400-e29b-41d4-a716-446655440000"

    # Create isolated session for this user
    session = composio.tool_router.create(
        user_id=user_id,
        toolkits=["gmail", "slack"]
    )

    tools = session.tools()

    # ✅ Each user gets their own session
    # ✅ Complete data isolation
    # ✅ User A cannot access User B's data
    # ✅ Connections tied to correct user
    return await agent.run(req.message, tools)
```

## ✅ Correct - Use Auth Provider IDs

```typescript
// DO: Use IDs from your auth provider
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';

const composio = new Composio({
  provider: new VercelProvider()
});

async function handleClerkUser(userId: string) {
  // Using Clerk user ID
  // e.g., "user_2abc123def456"
  const session = await composio.create(userId, {
    toolkits: ['github']
  });

  return session;
}

async function handleAuth0User(userId: string) {
  // Using Auth0 user ID
  // e.g., "auth0|507f1f77bcf86cd799439011"
  const session = await composio.create(userId, {
    toolkits: ['gmail']
  });

  return session;
}

async function handleSupabaseUser(userId: string) {
  // Using Supabase user UUID
  // e.g., "d7f8b0c1-1234-5678-9abc-def012345678"
  const session = await composio.create(userId, {
    toolkits: ['slack']
  });

  return session;
}
```

```python
# DO: Use IDs from your auth provider
from composio import Composio
from composio_openai import OpenAIProvider

composio = Composio(provider=OpenAIProvider())

async def handle_clerk_user(user_id: str):
    # Using Clerk user ID
    # e.g., "user_2abc123def456"
    session = composio.tool_router.create(
        user_id=user_id,
        toolkits=["github"]
    )
    return session

async def handle_auth0_user(user_id: str):
    # Using Auth0 user ID
    # e.g., "auth0|507f1f77bcf86cd799439011"
    session = composio.tool_router.create(
        user_id=user_id,
        toolkits=["gmail"]
    )
    return session

async def handle_supabase_user(user_id: str):
    # Using Supabase user UUID
    # e.g., "d7f8b0c1-1234-5678-9abc-def012345678"
    session = composio.tool_router.create(
        user_id=user_id,
        toolkits=["slack"]
    )
    return session
```

## ✅ Correct - Organization-Level Applications

```typescript
// DO: Use organization ID for org-level apps
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';

const composio = new Composio({
  provider: new VercelProvider()
});

// When apps are connected at organization level (not individual users)
async function handleOrgLevelApp(req: Request) {
  // Use organization ID, NOT individual user ID
  const organizationId = req.user.organizationId;

  const session = await composio.create(organizationId, {
    toolkits: ['slack', 'github'], // Org-wide tools
    manageConnections: true
  });

  // All users in the organization share these connections
  // Perfect for team collaboration tools
  const tools = await session.tools();
  return await agent.run(req.message, tools);
}

// Example: Slack workspace integration
async function createWorkspaceSession(workspaceId: string) {
  // Workspace ID as user ID
  const session = await composio.create(`workspace_${workspaceId}`, {
    toolkits: ['slack', 'notion', 'linear']
  });

  return session;
}
```

```python
# DO: Use organization ID for org-level apps
from composio import Composio
from composio_openai import OpenAIProvider

composio = Composio(provider=OpenAIProvider())

# When apps are connected at organization level (not individual users)
async def handle_org_level_app(req):
    # Use organization ID, NOT individual user ID
    organization_id = req.user.organization_id

    session = composio.tool_router.create(
        user_id=organization_id,
        toolkits=["slack", "github"],  # Org-wide tools
        manage_connections=True
    )

    # All users in the organization share these connections
    # Perfect for team collaboration tools
    tools = session.tools()
    return await agent.run(req.message, tools)

# Example: Slack workspace integration
async def create_workspace_session(workspace_id: str):
    # Workspace ID as user ID
    session = composio.tool_router.create(
        user_id=f"workspace_{workspace_id}",
        toolkits=["slack", "notion", "linear"]
    )
    return session
```

## When to Use 'default'

The `'default'` user ID should **ONLY** be used in these scenarios:

### ✅ Development and Testing
```typescript
// Testing locally
const session = await composio.create('default', {
  toolkits: ['gmail']
});
```

### ✅ Single-User Applications
```typescript
// Personal automation script
// Only YOU use this app
const session = await composio.create('default', {
  toolkits: ['github', 'notion']
});
```

### ✅ Demos and Prototypes
```typescript
// Quick demo for investors
const session = await composio.create('default', {
  toolkits: ['hackernews']
});
```

### ❌ NEVER in Production Multi-User Apps
```typescript
// Production API serving multiple users
// ❌ DON'T DO THIS
const session = await composio.create('default', {
  toolkits: ['gmail']
});
```

## User ID Best Practices

### 1. **Use Stable, Immutable Identifiers**

✅ **Good:**
- Database primary keys (UUIDs)
- Auth provider user IDs
- Immutable user identifiers

❌ **Bad:**
- Email addresses (can change)
- Usernames (can be modified)
- Phone numbers (can change)

```typescript
// ✅ Good: Stable UUID
const userId = user.id; // "550e8400-e29b-41d4-a716-446655440000"

// ❌ Bad: Email (mutable)
const userId = user.email; // "john@example.com" -> changes to "john@newdomain.com"

// ❌ Bad: Username (mutable)
const userId = user.username; // "john_doe" -> changes to "john_smith"
```

### 2. **Ensure Uniqueness**

```typescript
// ✅ Good: Guaranteed unique
const userId = database.users.findById(id).id;

// ✅ Good: Auth provider guarantees uniqueness
const userId = auth0.user.sub; // "auth0|507f1f77bcf86cd799439011"

// ❌ Bad: Not guaranteed unique
const userId = user.firstName; // Multiple "John"s exist
```

### 3. **Match Your Authentication System**

```typescript
// Express.js with Passport
app.post('/api/agent', authenticateUser, async (req, res) => {
  const userId = req.user.id; // From Passport
  const session = await composio.create(userId, config);
});

// Next.js with Clerk
export async function POST(req: NextRequest) {
  const { userId } = auth(); // From Clerk
  const session = await composio.create(userId!, config);
}

// FastAPI with Auth0
@app.post("/api/agent")
async def agent_endpoint(user: User = Depends(get_current_user)):
    user_id = user.id  # From Auth0
    session = composio.tool_router.create(user_id=user_id, **config)
```

### 4. **Namespace for Multi-Tenancy**

```typescript
// When you have multiple applications/workspaces per user
const userId = `app_${appId}_user_${user.id}`;
// e.g., "app_saas123_user_550e8400"

const session = await composio.create(userId, {
  toolkits: ['gmail']
});

// Each app instance gets isolated connections
```

### 5. **Be Consistent Across Your Application**

```typescript
// ✅ Good: Same user ID everywhere
async function handleRequest(req: Request) {
  const userId = req.user.id;

  // Use same ID for Tool Router
  const session = await composio.create(userId, config);

  // Use same ID for direct tool execution
  await composio.tools.execute('GMAIL_SEND_EMAIL', {
    userId: userId,
    arguments: { to: 'user@example.com', subject: 'Test' }
  });

  // Use same ID for connected accounts
  await composio.connectedAccounts.get(userId, 'gmail');
}
```

## Security Implications

### ⚠️ User ID Leakage
```typescript
// ❌ DON'T: Expose user IDs to client
app.get('/api/session', (req, res) => {
  res.json({
    sessionId: session.sessionId,
    userId: req.user.id // ❌ Sensitive information
  });
});

// ✅ DO: Keep user IDs server-side only
app.get('/api/session', (req, res) => {
  res.json({
    sessionId: session.sessionId
    // Don't send userId to client
  });
});
```

### ⚠️ User ID Validation
```typescript
// ✅ Always validate user IDs match authenticated user
app.post('/api/agent/:userId', authenticateUser, async (req, res) => {
  const requestedUserId = req.params.userId;
  const authenticatedUserId = req.user.id;

  // Validate user can only access their own data
  if (requestedUserId !== authenticatedUserId) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  const session = await composio.create(authenticatedUserId, config);
});
```

## Common Patterns

### Pattern 1: User-Level Isolation (Most Common)
```typescript
// Each user has their own connections
// Use user ID from your database/auth system
const session = await composio.create(req.user.id, {
  toolkits: ['gmail', 'github']
});
```

### Pattern 2: Organization-Level Sharing
```typescript
// All org members share connections
// Use organization ID
const session = await composio.create(req.user.organizationId, {
  toolkits: ['slack', 'notion']
});
```

### Pattern 3: Hybrid (User + Org)
```typescript
// Personal tools use user ID
const personalSession = await composio.create(req.user.id, {
  toolkits: ['gmail'] // Personal Gmail
});

// Team tools use org ID
const teamSession = await composio.create(req.user.organizationId, {
  toolkits: ['slack', 'jira'] // Team Slack/Jira
});
```

## Key Principles

1. **Never use 'default' in production multi-user apps**
2. **Use stable, immutable identifiers** (UUIDs, not emails)
3. **Match your authentication system's user IDs**
4. **Validate user IDs server-side** for security
5. **Be consistent** across Tool Router and direct tool usage
6. **Use org IDs** for organization-level applications
7. **Namespace when needed** for multi-tenancy

## Reference

- [Tool Router Sessions](https://docs.composio.dev/sdk/typescript/api/tool-router#creating-sessions)
- [User ID Security](https://docs.composio.dev/sdk/typescript/core-concepts#user-ids)
- [Connected Accounts](https://docs.composio.dev/sdk/typescript/api/connected-accounts)
