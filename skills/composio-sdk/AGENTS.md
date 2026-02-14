---
name: composio
description: Build AI agents and apps with Composio - access 200+ external tools with Tool Router or direct execution
tags: [composio, tool-router, agents, mcp, tools, api, automation]
---

# composio

Build AI agents and apps with Composio - access 200+ external tools with Tool Router or direct execution

## Table of Contents

1. [Building Agents](#building-agents)
   1.1. [User ID Best Practices](#user-id-best-practices)
   1.2. [Creating Basic Sessions](#creating-basic-sessions)
   1.3. [Session Lifecycle Best Practices](#session-lifecycle-best-practices)
   1.4. [Session Configuration](#session-configuration)
   1.5. [Using Native Tools](#using-native-tools)
   1.6. [Framework Integration](#framework-integration)
   1.7. [Auto Authentication in Chat](#auto-authentication-in-chat)
   1.8. [Manual Authorization](#manual-authorization)
   1.9. [Connection Management](#connection-management)
   1.10. [Building Chat UIs](#building-chat-uis)
   1.11. [Query Toolkit States](#query-toolkit-states)
   1.12. [Creating Triggers](#creating-triggers)
   1.13. [Subscribing to Events](#subscribing-to-events)
   1.14. [Webhook Verification](#webhook-verification)
   1.15. [Managing Triggers](#managing-triggers)

2. [Building Apps with Composio Tools](#building-apps-with-composio-tools)
   2.1. [Fetching Tools](#fetching-tools)
   2.2. [Direct Tool Execution](#direct-tool-execution)
   2.3. [Tool Version Management](#tool-version-management)
   2.4. [Connected Accounts CRUD](#connected-accounts-crud)
   2.5. [Auth Config Management](#auth-config-management)
   2.6. [Toolkit Management](#toolkit-management)
   2.7. [Creating Custom Tools](#creating-custom-tools)
   2.8. [Tool Modifiers](#tool-modifiers)
   2.9. [Creating Triggers](#creating-triggers)
   2.10. [Subscribing to Events](#subscribing-to-events)
   2.11. [Webhook Verification](#webhook-verification)
   2.12. [Managing Triggers](#managing-triggers)
   2.13. [User ID Patterns](#user-id-patterns)

---

## 1. Building Agents

<a name="building-agents"></a>

### 1.1. User ID Best Practices

<a name="user-id-best-practices"></a>

**Impact:** 🔴 CRITICAL

> Use proper user IDs to ensure data isolation, security, and correct session management

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

---

### 1.2. Creating Basic Sessions

<a name="creating-basic-sessions"></a>

**Impact:** 🟠 HIGH

> Essential pattern for initializing Tool Router sessions with proper user isolation

# Create Basic Tool Router Sessions

Always create isolated Tool Router sessions per user to ensure proper data isolation and scoped tool access.

## ❌ Incorrect

```typescript
// DON'T: Using shared session for multiple users
const sharedSession = await composio.create('default', {
  toolkits: ['gmail']
});
// All users share the same session - security risk!
```

```python
# DON'T: Using shared session for multiple users
shared_session = composio.tool_router.create(
    user_id="default",
    toolkits=["gmail"]
)
# All users share the same session - security risk!
```

## ✅ Correct

```typescript
// DO: Create per-user sessions for isolation
import { Composio } from '@composio/core';

const composio = new Composio();

// Each user gets their own isolated session
const session = await composio.create('user_123', {
  toolkits: ['gmail', 'slack']
});

console.log('Session ID:', session.sessionId);
console.log('MCP URL:', session.mcp.url);
```

```python
# DO: Create per-user sessions for isolation
from composio import Composio

composio = Composio()

# Each user gets their own isolated session
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack"]
)

print(f"Session ID: {session.session_id}")
print(f"MCP URL: {session.mcp.url}")
```

## Key Points

- **User Isolation**: Each user must have their own session
- **Toolkit Scoping**: Specify which toolkits the session can access
- **Session ID**: Store the session ID to retrieve it later
- **MCP URL**: Use this URL with any MCP-compatible AI framework

## Reference

- [Tool Router API Docs](https://docs.composio.dev/sdk/typescript/api/tool-router)
- [Creating Sessions](https://docs.composio.dev/sdk/typescript/api/tool-router#creating-sessions)

---

### 1.3. Session Lifecycle Best Practices

<a name="session-lifecycle-best-practices"></a>

**Impact:** 🔴 CRITICAL

> Create new sessions frequently for better logging, debugging, and configuration management

# Treat Sessions as Short-Lived and Disposable

Tool Router sessions should be **short-lived and disposable**. Create new sessions frequently rather than caching or reusing them across different contexts.

## ❌ Incorrect

```typescript
// DON'T: Cache and reuse sessions across messages
class AgentService {
  private sessionCache = new Map<string, ToolRouterSession>();

  async handleMessage(userId: string, message: string) {
    // BAD: Reusing cached session
    let session = this.sessionCache.get(userId);

    if (!session) {
      session = await composio.create(userId, {
        toolkits: ['gmail', 'slack']
      });
      this.sessionCache.set(userId, session);
    }

    // ❌ Configuration changes won't be reflected
    // ❌ Logs mixed across different conversations
    // ❌ Stale toolkit connections
    const tools = await session.tools();
  }
}
```

```python
# DON'T: Cache and reuse sessions across messages
class AgentService:
    def __init__(self):
        self.session_cache = {}

    async def handle_message(self, user_id: str, message: str):
        # BAD: Reusing cached session
        if user_id not in self.session_cache:
            session = composio.tool_router.create(
                user_id=user_id,
                toolkits=["gmail", "slack"]
            )
            self.session_cache[user_id] = session

        session = self.session_cache[user_id]

        # ❌ Configuration changes won't be reflected
        # ❌ Logs mixed across different conversations
        # ❌ Stale toolkit connections
        tools = session.tools()
```

## ✅ Correct - Create New Session Per Message

```typescript
// DO: Create fresh session for each message
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';

const composio = new Composio({
  provider: new VercelProvider()
});

async function handleUserMessage(
  userId: string,
  message: string,
  config: { toolkits: string[] }
) {
  // Create new session for this message
  const session = await composio.create(userId, {
    toolkits: config.toolkits,
    manageConnections: true
  });

  const tools = await session.tools();

  // Use tools with agent...
  const response = await runAgent(message, tools);

  // ✅ Fresh configuration
  // ✅ Clean logs grouped by session
  // ✅ Latest connection states
  return response;
}

// Each message gets a new session
await handleUserMessage('user_123', 'Check my emails', { toolkits: ['gmail'] });
await handleUserMessage('user_123', 'Send a slack message', { toolkits: ['slack'] });
```

```python
# DO: Create fresh session for each message
from composio import Composio
from composio_openai import OpenAIProvider

composio = Composio(provider=OpenAIProvider())

async def handle_user_message(
    user_id: str,
    message: str,
    config: dict
):
    # Create new session for this message
    session = composio.tool_router.create(
        user_id=user_id,
        toolkits=config["toolkits"],
        manage_connections=True
    )

    tools = session.tools()

    # Use tools with agent...
    response = await run_agent(message, tools)

    # ✅ Fresh configuration
    # ✅ Clean logs grouped by session
    # ✅ Latest connection states
    return response

# Each message gets a new session
await handle_user_message("user_123", "Check my emails", {"toolkits": ["gmail"]})
await handle_user_message("user_123", "Send a slack message", {"toolkits": ["slack"]})
```

## ✅ Correct - Single Session Per Conversation (When Config Stable)

```typescript
// DO: Use one session for entire conversation if config doesn't change
async function handleConversation(
  userId: string,
  conversationId: string,
  config: { toolkits: string[] }
) {
  // Create ONE session for this conversation/thread
  const session = await composio.create(userId, {
    toolkits: config.toolkits,
    manageConnections: true
  });

  const tools = await session.tools();

  console.log(`Session ${session.sessionId} for conversation ${conversationId}`);

  // Use the same session for all messages in this conversation
  for await (const message of conversationStream) {
    const response = await runAgent(message, tools);

    // ✅ All tool executions logged under same session
    // ✅ Easy to debug entire conversation flow
    // ✅ Grouped logs in monitoring tools
  }
}
```

```python
# DO: Use one session for entire conversation if config doesn't change
async def handle_conversation(
    user_id: str,
    conversation_id: str,
    config: dict
):
    # Create ONE session for this conversation/thread
    session = composio.tool_router.create(
        user_id=user_id,
        toolkits=config["toolkits"],
        manage_connections=True
    )

    tools = session.tools()

    print(f"Session {session.session_id} for conversation {conversation_id}")

    # Use the same session for all messages in this conversation
    async for message in conversation_stream:
        response = await run_agent(message, tools)

        # ✅ All tool executions logged under same session
        # ✅ Easy to debug entire conversation flow
        # ✅ Grouped logs in monitoring tools
```

## When to Create New Sessions

### ✅ Always Create New Session When:

1. **Configuration Changes**
   ```typescript
   // User connects new toolkit
   if (userConnectedSlack) {
     // Create new session with updated toolkits
     const session = await composio.create(userId, {
       toolkits: ['gmail', 'slack'] // Added slack
     });
   }
   ```

2. **Connected Accounts Change**
   ```typescript
   // User disconnected and reconnected Gmail
   const session = await composio.create(userId, {
     toolkits: ['gmail'],
     // Will use latest connection
   });
   ```

3. **Different Toolkit Requirements**
   ```typescript
   // Message needs different toolkits
   const emailSession = await composio.create(userId, {
     toolkits: ['gmail']
   });

   const codeSession = await composio.create(userId, {
     toolkits: ['github', 'linear']
   });
   ```

4. **New Conversation/Thread**
   ```typescript
   // Starting a new conversation thread
   const session = await composio.create(userId, {
     toolkits: config.toolkits,
     // Fresh session for clean log grouping
   });
   ```

### ✅ Can Reuse Session When:

1. **Same conversation/thread**
2. **Configuration unchanged**
3. **No toolkit connections changed**
4. **Actively ongoing interaction**

## Benefits of Short-Lived Sessions

### 1. **Clean Log Grouping**
```typescript
// All tool executions in one session are grouped together
const session = await composio.create(userId, {
  toolkits: ['gmail', 'slack']
});

// These executions are grouped under session.sessionId
await agent.run('Check emails'); // Logs: session_abc123
await agent.run('Send slack message'); // Logs: session_abc123

// Easy to trace entire conversation flow in monitoring
console.log(`View logs: /sessions/${session.sessionId}`);
```

### 2. **Fresh Configuration**
```typescript
// Always get latest toolkit connections and auth states
const session = await composio.create(userId, {
  toolkits: ['gmail']
});

// ✅ Uses current connected account
// ✅ Reflects any new connections user made
// ✅ Picks up toolkit updates
```

### 3. **Easier Debugging**
```typescript
// Session ID becomes your debug trace ID
console.log(`Processing message in session ${session.sessionId}`);

// All logs tagged with session ID:
// [session_abc123] Executing GMAIL_FETCH_EMAILS
// [session_abc123] Executed GMAIL_FETCH_EMAILS
// [session_abc123] Executing SLACK_SEND_MESSAGE

// Filter all logs for this specific interaction
```

### 4. **Simplified Error Tracking**
```typescript
try {
  const session = await composio.create(userId, config);
  const result = await runAgent(message, session);
} catch (error) {
  // Session ID in error context
  logger.error('Agent failed', {
    sessionId: session.sessionId,
    userId,
    error
  });
}
```

## Pattern: Per-Message Sessions

```typescript
// Recommended pattern for most applications
export async function handleAgentRequest(
  userId: string,
  message: string,
  toolkits: string[]
) {
  // 1. Create fresh session
  const session = await composio.create(userId, {
    toolkits,
    manageConnections: true
  });

  // 2. Log session start
  logger.info('Session started', {
    sessionId: session.sessionId,
    userId,
    toolkits
  });

  try {
    // 3. Get tools and run agent
    const tools = await session.tools();
    const response = await agent.run(message, tools);

    // 4. Log session completion
    logger.info('Session completed', {
      sessionId: session.sessionId
    });

    return response;
  } catch (error) {
    // 5. Log session error
    logger.error('Session failed', {
      sessionId: session.sessionId,
      error
    });
    throw error;
  }
}
```

## Pattern: Per-Conversation Sessions

```typescript
// For long-running conversations with stable config
export class ConversationSession {
  private session: ToolRouterSession;

  async start(userId: string, config: SessionConfig) {
    // Create session once for conversation
    this.session = await composio.create(userId, config);

    logger.info('Conversation session started', {
      sessionId: this.session.sessionId
    });
  }

  async handleMessage(message: string) {
    // Reuse session for all messages
    const tools = await this.session.tools();
    return await agent.run(message, tools);
  }

  async end() {
    logger.info('Conversation session ended', {
      sessionId: this.session.sessionId
    });
  }
}
```

## Key Principles

1. **Don't cache sessions** - Create new ones as needed
2. **Session = Unit of work** - One session per task or conversation
3. **Short-lived is better** - Fresh state, clean logs, easier debugging
4. **Session ID = Trace ID** - Use for log correlation and debugging
5. **Create on demand** - No need to pre-create or warm up sessions

## Reference

- [Tool Router Sessions](https://docs.composio.dev/sdk/typescript/api/tool-router#creating-sessions)
- [Session Properties](https://docs.composio.dev/sdk/typescript/api/tool-router#session-properties)
- [Best Practices](https://docs.composio.dev/sdk/typescript/api/tool-router#best-practices)

---

### 1.4. Session Configuration

<a name="session-configuration"></a>

**Impact:** 🟡 MEDIUM

> Use session configuration options to control toolkit access, tools, and behavior

# Configure Tool Router Sessions Properly

Tool Router sessions support rich configuration for fine-grained control over toolkit and tool access.

## ❌ Incorrect

```typescript
// DON'T: Enable all toolkits without restrictions
const session = await composio.create('user_123', {
  // No toolkit restrictions - exposes everything!
});

// DON'T: Mix incompatible configuration patterns
const session = await composio.create('user_123', {
  toolkits: { enable: ['gmail'] },
  toolkits: ['slack']  // This will override the first one!
});
```

```python
# DON'T: Enable all toolkits without restrictions
session = composio.tool_router.create(
    user_id="user_123"
    # No toolkit restrictions - exposes everything!
)
```

## ✅ Correct - Basic Configuration

```typescript
// DO: Explicitly specify toolkits
import { Composio } from '@composio/core';

const composio = new Composio();

// Simple toolkit list
const session = await composio.create('user_123', {
  toolkits: ['gmail', 'slack', 'github']
});

// Explicit enable
const session2 = await composio.create('user_123', {
  toolkits: { enable: ['gmail', 'slack'] }
});

// Disable specific toolkits (enable all others)
const session3 = await composio.create('user_123', {
  toolkits: { disable: ['calendar'] }
});
```

```python
# DO: Explicitly specify toolkits
from composio import Composio

composio = Composio()

# Simple toolkit list
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack", "github"]
)

# Explicit enable
session2 = composio.tool_router.create(
    user_id="user_123",
    toolkits={"enable": ["gmail", "slack"]}
)
```

## ✅ Correct - Fine-Grained Tool Control

```typescript
// DO: Control specific tools per toolkit
const session = await composio.create('user_123', {
  toolkits: ['gmail', 'slack'],
  tools: {
    // Only allow reading emails, not sending
    gmail: ['GMAIL_FETCH_EMAILS', 'GMAIL_SEARCH_EMAILS'],

    // Or use enable/disable
    slack: {
      disable: ['SLACK_DELETE_MESSAGE'] // Safety: prevent deletions
    }
  }
});
```

```python
# DO: Control specific tools per toolkit
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack"],
    tools={
        # Only allow reading emails, not sending
        "gmail": ["GMAIL_FETCH_EMAILS", "GMAIL_SEARCH_EMAILS"],

        # Or use enable/disable
        "slack": {
            "disable": ["SLACK_DELETE_MESSAGE"]  # Safety: prevent deletions
        }
    }
)
```

## ✅ Correct - Tag-Based Filtering

```typescript
// DO: Use tags to filter by behavior
const session = await composio.create('user_123', {
  toolkits: ['gmail', 'github'],
  // Global tags: only read-only tools
  tags: ['readOnlyHint'],

  // Override tags per toolkit
  tools: {
    github: {
      tags: ['readOnlyHint', 'idempotentHint']
    }
  }
});
```

```python
# DO: Use tags to filter by behavior
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "github"],
    # Global tags: only read-only tools
    tags=["readOnlyHint"],

    # Override tags per toolkit
    tools={
        "github": {
            "tags": ["readOnlyHint", "idempotentHint"]
        }
    }
)
```

## Available Tags

- `readOnlyHint` - Tools that only read data
- `destructiveHint` - Tools that modify or delete data
- `idempotentHint` - Tools safe to retry
- `openWorldHint` - Tools operating in open contexts

## Configuration Best Practices

1. **Least Privilege**: Only enable toolkits/tools needed
2. **Tag Filtering**: Use tags to restrict dangerous operations
3. **Per-Toolkit Tools**: Fine-tune access per toolkit
4. **Auth Configs**: Map toolkits to specific auth configurations

## Reference

- [Configuration Options](https://docs.composio.dev/sdk/typescript/api/tool-router#configuration-options)
- [Tool Tags](https://docs.composio.dev/sdk/typescript/api/tool-router#tags)

---

### 1.5. Using Native Tools

<a name="using-native-tools"></a>

**Impact:** 🟠 HIGH

> Prefer native tools over MCP for faster execution, full control, and modifier support

# Use Native Tools for Performance and Control

Tool Router supports two approaches: **Native tools (recommended)** for performance and control, or MCP clients for framework independence.

## ❌ Incorrect

```typescript
// DON'T: Use MCP when you need logging, modifiers, or performance
const composio = new Composio(); // No provider
const { mcp } = await composio.create('user_123', {
  toolkits: ['gmail']
});

const client = await createMCPClient({
  transport: { type: 'http', url: mcp.url }
});

// ❌ No control over tool execution
// ❌ No modifier support
// ❌ Extra API calls via MCP server
// ❌ Slower execution
const tools = await client.tools();
```

```python
# DON'T: Use MCP when you need logging, modifiers, or performance
composio = Composio()  # No provider
session = composio.tool_router.create(user_id="user_123")

# ❌ No control over tool execution
# ❌ No modifier support
# ❌ Extra API calls via MCP server
# ❌ Slower execution
```

## ✅ Correct - Use Native Tools (Recommended)

```typescript
// DO: Use native tools for performance and control
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';

// Add provider for native tools
const composio = new Composio({
  provider: new VercelProvider()
});

const session = await composio.create('user_123', {
  toolkits: ['gmail', 'slack']
});

// ✅ Direct tool execution (no MCP overhead)
// ✅ Full modifier support
// ✅ Logging and telemetry
// ✅ Faster performance
const tools = await session.tools();
```

```python
# DO: Use native tools for performance and control
from composio import Composio
from composio_openai import OpenAIProvider

# Add provider for native tools
composio = Composio(provider=OpenAIProvider())

session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack"]
)

# ✅ Direct tool execution (no MCP overhead)
# ✅ Full modifier support
# ✅ Logging and telemetry
# ✅ Faster performance
tools = session.tools()
```

## ✅ Correct - Native Tools with Modifiers

```typescript
// DO: Use modifiers for logging and control
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';
import { SessionExecuteMetaModifiers } from '@composio/core';

const composio = new Composio({
  provider: new VercelProvider()
});

const session = await composio.create('user_123', {
  toolkits: ['gmail']
});

// Add modifiers for logging during execution
const modifiers: SessionExecuteMetaModifiers = {
  beforeExecute: ({ toolSlug, sessionId, params }) => {
    console.log(`[${sessionId}] Executing ${toolSlug}`);
    console.log('Parameters:', JSON.stringify(params, null, 2));
    return params;
  },
  afterExecute: ({ toolSlug, sessionId, result }) => {
    console.log(`[${sessionId}] Completed ${toolSlug}`);
    console.log('Success:', result.successful);
    return result;
  }
};

const tools = await session.tools(modifiers);

// Now when agent executes tools, you see:
// [session_abc123] Executing GMAIL_FETCH_EMAILS
// Parameters: { "maxResults": 10, "query": "from:user@example.com" }
// [session_abc123] Completed GMAIL_FETCH_EMAILS
// Success: true
```

```typescript
// Advanced: Add telemetry and schema customization
const advancedModifiers: SessionExecuteMetaModifiers = {
  beforeExecute: ({ toolSlug, sessionId, params }) => {
    // Send to analytics
    analytics.track('tool_execution_started', {
      tool: toolSlug,
      session: sessionId,
      params
    });

    // Validate parameters
    if (!params) {
      throw new Error(`Missing parameters for ${toolSlug}`);
    }

    return params;
  },
  afterExecute: ({ toolSlug, sessionId, result }) => {
    // Track completion and duration
    analytics.track('tool_execution_completed', {
      tool: toolSlug,
      session: sessionId,
      success: result.successful
    });

    // Handle errors
    if (!result.successful) {
      console.error(`Tool ${toolSlug} failed:`, result.error);
    }

    return result;
  },
  modifySchema: ({ toolSlug, schema }) => {
    // Simplify schemas for better AI understanding
    if (toolSlug === 'GMAIL_SEND_EMAIL') {
      // Remove optional fields for simpler usage
      delete schema.parameters.properties.cc;
      delete schema.parameters.properties.bcc;
    }
    return schema;
  }
};
```

```python
# DO: Use modifiers for logging, validation, and telemetry
from composio import Composio
from composio_openai import OpenAIProvider

composio = Composio(provider=OpenAIProvider())

session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail"]
)

# Add modifiers for full control over tool execution
def before_execute(context):
    print(f"[{context['session_id']}] Executing {context['tool_slug']}")
    print(f"Parameters: {context['params']}")
    # Add custom validation, logging, telemetry
    return context['params']

def after_execute(context):
    print(f"[{context['session_id']}] Completed {context['tool_slug']}")
    print(f"Result: {context['result']}")
    # Transform results, handle errors, track metrics
    return context['result']

tools = session.tools(
    modifiers={
        "before_execute": before_execute,
        "after_execute": after_execute
    }
)
```

## Performance Comparison

| Feature | Native Tools | MCP |
|---------|-------------|-----|
| Execution Speed | **Fast** (direct) | Slower (extra HTTP calls) |
| API Overhead | **Minimal** | Additional MCP server roundtrips |
| Modifier Support | **✅ Full support** | ❌ Not available |
| Logging & Telemetry | **✅ beforeExecute/afterExecute** | ❌ Limited visibility |
| Schema Customization | **✅ modifySchema** | ❌ Not available |
| Framework Lock-in | Yes (provider-specific) | No (universal) |

## When to Use Each

### ✅ Use Native Tools (Recommended) When:
- **Performance matters**: Direct execution, no MCP overhead
- **Need logging**: Track tool execution, parameters, results
- **Need control**: Validate inputs, transform outputs, handle errors
- **Production apps**: Telemetry, monitoring, debugging
- **Single framework**: You're committed to one AI framework

### Use MCP Only When:
- **Multiple frameworks**: Switching between Claude, Vercel AI, LangChain
- **Framework flexibility**: Not committed to one provider yet
- **Prototyping**: Quick testing across different AI tools

## Modifier Use Cases

With native tools, modifiers enable:

1. **Logging**: Track every tool execution with parameters and results
2. **Telemetry**: Send metrics to Datadog, New Relic, etc.
3. **Validation**: Check parameters before execution
4. **Error Handling**: Catch and transform errors
5. **Rate Limiting**: Control tool execution frequency
6. **Caching**: Cache results for repeated calls
7. **Schema Customization**: Simplify schemas for specific AI models

## Key Insight

**Native tools eliminate the MCP server middleman**, resulting in faster execution and giving you full control over the tool execution lifecycle. The only trade-off is framework lock-in, which is acceptable in production applications where you've already chosen your AI framework.

## Reference

- [Session Modifiers](https://docs.composio.dev/sdk/typescript/api/tool-router#using-modifiers)
- [SessionExecuteMetaModifiers](https://docs.composio.dev/sdk/typescript/api/tool-router#sessionexecutemetamodifiers-v040)
- [Tool Router Performance](https://docs.composio.dev/sdk/typescript/api/tool-router#best-practices)

---

### 1.6. Framework Integration

<a name="framework-integration"></a>

**Impact:** 🟠 HIGH

> Connect Tool Router sessions with popular AI frameworks using MCP or native tools

# Integrate Tool Router with AI Frameworks

Tool Router works with any AI framework through two methods: **Native Tools** (recommended for speed) or **MCP** (for framework flexibility). Choose native tools when available for better performance and control.

## Integration Methods

| Method | Pros | Cons | When to Use |
|--------|------|------|-------------|
| **Native Tools** | ✅ Faster execution<br>✅ Full control with modifiers<br>✅ No MCP overhead | ❌ Framework lock-in | Single framework, production apps |
| **MCP** | ✅ Framework independent<br>✅ Works with any MCP client<br>✅ Easy framework switching | ⚠️ Slower (extra API roundtrip)<br>⚠️ Less control | Multi-framework, prototyping |

## MCP Headers Configuration

When using MCP, the `session.mcp.headers` object contains the authentication headers required to connect to the Composio MCP server:

```typescript
{
  "x-api-key": "your_composio_api_key"
}
```

### Using with MCP Clients

When configuring MCP clients (like Claude Desktop), you need to provide the Composio API key in the headers:

```json
{
  "mcpServers": {
    "composio": {
      "type": "http",
      "url": "https://mcp.composio.dev/session/your_session_id",
      "headers": {
        "x-api-key": "your_composio_api_key"
      }
    }
  }
}
```

**Where to find your Composio API key:**
- Login to [Composio Platform](https://platform.composio.dev)
- Select your project
- Navigate to Settings to find your API keys
- Or set it via environment variable: `COMPOSIO_API_KEY`

When using Tool Router sessions programmatically, the headers are automatically included in `session.mcp.headers`.

## ❌ Incorrect - Using Tools Without Tool Router

```typescript
// DON'T: Use tools directly without session isolation
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';

const composio = new Composio({ provider: new VercelProvider() });

// ❌ No user isolation
// ❌ Tools not scoped per user
// ❌ All users share same tools
const tools = await composio.tools.get('default', {
  toolkits: ['gmail']
});
```

```python
# DON'T: Use tools directly without session isolation
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider

composio = Composio(provider=OpenAIAgentsProvider())

# ❌ No user isolation
# ❌ Tools not scoped per user
# ❌ All users share same tools
tools = composio.tools.get(
    user_id="default",
    toolkits=["gmail"]
)
```

## ✅ Correct - Vercel AI SDK (Native Tools)

```typescript
// DO: Use Tool Router with native tools for best performance
import { openai } from '@ai-sdk/openai';
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';
import { streamText } from 'ai';

// Initialize Composio with Vercel provider
const composio = new Composio({
  provider: new VercelProvider()
});

async function runAgent(userId: string, prompt: string) {
  // Create isolated session for user
  const session = await composio.create(userId, {
    toolkits: ['gmail'],
    manageConnections: true
  });

  // Get native Vercel-formatted tools
  const tools = await session.tools();

  // Stream response with tools
  const stream = await streamText({
    model: openai('gpt-4o'),
    prompt,
    tools,
    maxSteps: 10
  });

  // ✅ Fast execution (no MCP overhead)
  // ✅ User-isolated tools
  // ✅ Native Vercel format

  for await (const textPart of stream.textStream) {
    process.stdout.write(textPart);
  }
}

await runAgent('user_123', 'Fetch my last email from Gmail');
```

```python
# DO: Use Tool Router with native tools for best performance
from composio import Composio
from composio_vercel import VercelProvider
from ai import streamText, openai

# Initialize Composio with Vercel provider
composio = Composio(provider=VercelProvider())

async def run_agent(user_id: str, prompt: str):
    # Create isolated session for user
    session = composio.create(
        user_id=user_id,
        toolkits=["gmail"],
        manage_connections=True
    )

    # Get native Vercel-formatted tools
    tools = session.tools()

    # Stream response with tools
    stream = streamText(
        model=openai("gpt-4o"),
        prompt=prompt,
        tools=tools,
        max_steps=10
    )

    # ✅ Fast execution (no MCP overhead)
    # ✅ User-isolated tools
    # ✅ Native Vercel format

    async for text_part in stream.text_stream:
        print(text_part, end="")

await run_agent("user_123", "Fetch my last email from Gmail")
```

## ✅ Correct - Vercel AI SDK (MCP)

```typescript
// DO: Use MCP when framework flexibility is needed
import { openai } from '@ai-sdk/openai';
import { experimental_createMCPClient as createMCPClient } from '@ai-sdk/mcp';
import { Composio } from '@composio/core';
import { streamText } from 'ai';

const composio = new Composio();

async function runAgentMCP(userId: string, prompt: string) {
  // Create session (MCP URL only, no provider needed)
  const session = await composio.create(userId, {
    toolkits: ['gmail'],
    manageConnections: true
  });

  // Create MCP client
  const client = await createMCPClient({
    transport: {
      type: 'http',
      url: session.mcp.url,
      headers: session.mcp.headers
    }
  });

  // Get tools from MCP server
  const tools = await client.tools();

  // Stream response
  const stream = await streamText({
    model: openai('gpt-4o'),
    prompt,
    tools,
    maxSteps: 10
  });

  // ✅ Framework independent
  // ✅ User-isolated tools
  // ⚠️ Slower (MCP overhead)

  for await (const textPart of stream.textStream) {
    process.stdout.write(textPart);
  }
}

await runAgentMCP('user_123', 'Fetch my last email');
```

## ✅ Correct - OpenAI Agents SDK (Native Tools)

```typescript
// DO: Use native tools with OpenAI Agents
import { Composio } from '@composio/core';
import { OpenAIAgentsProvider } from '@composio/openai-agents';
import { Agent, run } from '@openai/agents';

const composio = new Composio({
  provider: new OpenAIAgentsProvider()
});

async function createAssistant(userId: string) {
  // Create session with native tools
  const session = await composio.create(userId, {
    toolkits: ['gmail', 'slack']
  });

  // Get native OpenAI Agents formatted tools
  const tools = await session.tools();

  // Create agent with tools
  const agent = new Agent({
    name: 'Personal Assistant',
    model: 'gpt-4o',
    instructions: 'You are a helpful assistant. Use tools to help users.',
    tools
  });

  // ✅ Fast execution
  // ✅ Native OpenAI Agents format
  // ✅ Full control

  return agent;
}

const agent = await createAssistant('user_123');
const result = await run(agent, 'Check my emails and send a summary to Slack');
console.log(result.finalOutput);
```

```python
# DO: Use native tools with OpenAI Agents
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider
from agents import Agent, Runner

composio = Composio(provider=OpenAIAgentsProvider())

async def create_assistant(user_id: str):
    # Create session with native tools
    session = composio.create(
        user_id=user_id,
        toolkits=["gmail", "slack"]
    )

    # Get native OpenAI Agents formatted tools
    tools = session.tools()

    # Create agent with tools
    agent = Agent(
        name="Personal Assistant",
        model="gpt-4o",
        instructions="You are a helpful assistant. Use tools to help users.",
        tools=tools
    )

    # ✅ Fast execution
    # ✅ Native OpenAI Agents format
    # ✅ Full control

    return agent

agent = await create_assistant("user_123")
result = await Runner.run(
    starting_agent=agent,
    input="Check my emails and send a summary to Slack"
)
print(result.final_output)
```

## ✅ Correct - OpenAI Agents SDK (MCP)

```typescript
// DO: Use MCP with OpenAI Agents for flexibility
import { Composio } from '@composio/core';
import { Agent, run, hostedMcpTool } from '@openai/agents';

const composio = new Composio();

async function createAssistantMCP(userId: string) {
  // Create session
  const { mcp } = await composio.create(userId, {
    toolkits: ['gmail']
  });

  // Create agent with MCP tool
  const agent = new Agent({
    name: 'Gmail Assistant',
    model: 'gpt-4o',
    instructions: 'Help users manage their Gmail.',
    tools: [
      hostedMcpTool({
        serverLabel: 'composio',
        serverUrl: mcp.url,
        headers: mcp.headers
      })
    ]
  });

  // ✅ Framework independent
  // ⚠️ Slower execution

  return agent;
}

const agent = await createAssistantMCP('user_123');
const result = await run(agent, 'Fetch my last email');
```

```python
# DO: Use MCP with OpenAI Agents for flexibility
from composio import Composio
from agents import Agent, Runner, HostedMCPTool

composio = Composio()

def create_assistant_mcp(user_id: str):
    # Create session
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Create agent with MCP tool
    composio_mcp = HostedMCPTool(
        tool_config={
            "type": "mcp",
            "server_label": "composio",
            "server_url": session.mcp.url,
            "require_approval": "never",
            "headers": session.mcp.headers
        }
    )

    agent = Agent(
        name="Gmail Assistant",
        instructions="Help users manage their Gmail.",
        tools=[composio_mcp]
    )

    # ✅ Framework independent
    # ⚠️ Slower execution

    return agent

agent = create_assistant_mcp("user_123")
result = Runner.run_sync(starting_agent=agent, input="Fetch my last email")
print(result.final_output)
```

## ✅ Correct - LangChain (MCP)

```typescript
// DO: Use LangChain with MCP
import { MultiServerMCPClient } from '@langchain/mcp-adapters';
import { ChatOpenAI } from '@langchain/openai';
import { createAgent } from 'langchain';
import { Composio } from '@composio/core';

const composio = new Composio();

async function createLangChainAgent(userId: string) {
  // Create session
  const session = await composio.create(userId, {
    toolkits: ['gmail']
  });

  // Create MCP client
  const client = new MultiServerMCPClient({
    composio: {
      transport: 'http',
      url: session.mcp.url,
      headers: session.mcp.headers
    }
  });

  // Get tools
  const tools = await client.getTools();

  // Create agent
  const llm = new ChatOpenAI({ model: 'gpt-4o' });

  const agent = createAgent({
    name: 'Gmail Assistant',
    systemPrompt: 'You help users manage their Gmail.',
    model: llm,
    tools
  });

  return agent;
}

const agent = await createLangChainAgent('user_123');
const result = await agent.invoke({
  messages: [{ role: 'user', content: 'Fetch my last email' }]
});
console.log(result);
```

```python
# DO: Use LangChain with MCP
from composio import Composio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai.chat_models import ChatOpenAI

composio = Composio()

async def create_langchain_agent(user_id: str):
    # Create session
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Create MCP client
    mcp_client = MultiServerMCPClient({
        "composio": {
            "transport": "streamable_http",
            "url": session.mcp.url,
            "headers": session.mcp.headers
        }
    })

    # Get tools
    tools = await mcp_client.get_tools()

    # Create agent
    agent = create_agent(
        tools=tools,
        model=ChatOpenAI(model="gpt-4o")
    )

    return agent

agent = await create_langchain_agent("user_123")
result = await agent.ainvoke({
    "messages": [
        {"role": "user", "content": "Fetch my last email"}
    ]
})
print(result)
```

## ✅ Correct - Claude Agent SDK (Native Tools)

```typescript
// DO: Use Claude Agent SDK with native tools
import { query } from '@anthropic-ai/claude-agent-sdk';
import { Composio } from '@composio/core';
import { ClaudeAgentSDKProvider } from '@composio/claude-agent-sdk';

const composio = new Composio({
  provider: new ClaudeAgentSDKProvider()
});

async function runClaudeAgent(userId: string, prompt: string) {
  // Create session with native tools
  const session = await composio.create(userId, {
    toolkits: ['gmail']
  });

  // Get native Claude tools format
  const tools = await session.tools();

  // Query with tools
  const stream = await query({
    prompt,
    options: {
      model: 'claude-sonnet-4-5-20250929',
      permissionMode: 'bypassPermissions',
      tools
    }
  });

  for await (const event of stream) {
    if (event.type === 'result' && event.subtype === 'success') {
      process.stdout.write(event.result);
    }
  }
}

await runClaudeAgent('user_123', 'Fetch my last email');
```

```python
# DO: Use Claude Agent SDK with native tools
from composio import Composio
from composio_claude_agent_sdk import ClaudeAgentSDKProvider
from claude_agent_sdk import query, ClaudeAgentOptions

composio = Composio(provider=ClaudeAgentSDKProvider())

async def run_claude_agent(user_id: str, prompt: str):
    # Create session with native tools
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Get native Claude tools format
    tools = session.tools()

    # Query with tools
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5-20250929",
        permission_mode="bypassPermissions",
        tools=tools
    )

    async for message in query(prompt=prompt, options=options):
        print(message, end="")

await run_claude_agent("user_123", "Fetch my last email")
```

## ✅ Correct - Claude Agent SDK (MCP)

```typescript
// DO: Use Claude Agent SDK with MCP
import { query } from '@anthropic-ai/claude-agent-sdk';
import { Composio } from '@composio/core';

const composio = new Composio();

async function runClaudeAgentMCP(userId: string, prompt: string) {
  // Create session
  const session = await composio.create(userId, {
    toolkits: ['gmail']
  });

  // Query with MCP server
  const stream = await query({
    prompt,
    options: {
      model: 'claude-sonnet-4-5-20250929',
      permissionMode: 'bypassPermissions',
      mcpServers: {
        composio: {
          type: 'http',
          url: session.mcp.url,
          headers: session.mcp.headers
        }
      }
    }
  });

  for await (const event of stream) {
    if (event.type === 'result' && event.subtype === 'success') {
      process.stdout.write(event.result);
    }
  }
}

await runClaudeAgentMCP('user_123', 'Fetch my last email');
```

```python
# DO: Use Claude Agent SDK with MCP
from composio import Composio
from claude_agent_sdk import query, ClaudeAgentOptions

composio = Composio()

async def run_claude_agent_mcp(user_id: str, prompt: str):
    # Create session
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Query with MCP server
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5-20250929",
        permission_mode="bypassPermissions",
        mcp_servers={
            "composio": {
                "type": session.mcp.type,
                "url": session.mcp.url,
                "headers": session.mcp.headers
            }
        }
    )

    async for message in query(prompt=prompt, options=options):
        print(message, end="")

await run_claude_agent_mcp("user_123", "Fetch my last email")
```

## ✅ Correct - CrewAI (MCP)

```python
# DO: Use CrewAI with MCP
from crewai import Agent, Task, Crew
from crewai.mcp import MCPServerHTTP
from composio import Composio

composio = Composio()

def create_crewai_agent(user_id: str):
    # Create session
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Create agent with MCP server
    agent = Agent(
        role="Gmail Assistant",
        goal="Help with Gmail related queries",
        backstory="You are a helpful assistant.",
        mcps=[
            MCPServerHTTP(
                url=session.mcp.url,
                headers=session.mcp.headers
            )
        ]
    )

    return agent

# Create agent
agent = create_crewai_agent("user_123")

# Define task
task = Task(
    description="Find the last email and summarize it.",
    expected_output="A summary including sender, subject, and key points.",
    agent=agent
)

# Execute
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
print(result)
```

## Using Modifiers with Native Tools

```typescript
// Add logging and telemetry with modifiers
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';
import { SessionExecuteMetaModifiers } from '@composio/core';

const composio = new Composio({
  provider: new VercelProvider()
});

async function getToolsWithLogging(userId: string) {
  const session = await composio.create(userId, {
    toolkits: ['gmail']
  });

  // Add modifiers for logging
  const modifiers: SessionExecuteMetaModifiers = {
    beforeExecute: ({ toolSlug, sessionId, params }) => {
      console.log(`[${sessionId}] Executing ${toolSlug}`);
      console.log('Parameters:', JSON.stringify(params, null, 2));
      return params;
    },
    afterExecute: ({ toolSlug, sessionId, result }) => {
      console.log(`[${sessionId}] Completed ${toolSlug}`);
      console.log('Success:', result.successful);
      return result;
    }
  };

  // Get tools with modifiers
  const tools = await session.tools(modifiers);

  return tools;
}
```

```python
# Add logging and telemetry with modifiers
from composio import Composio, before_execute, after_execute
from composio_openai_agents import OpenAIAgentsProvider
from composio.types import ToolExecuteParams, ToolExecutionResponse

composio = Composio(provider=OpenAIAgentsProvider())

async def get_tools_with_logging(user_id: str):
    session = composio.create(user_id=user_id, toolkits=["gmail"])

    # Define logging modifiers
    @before_execute(tools=[])
    def log_before(
        tool: str,
        toolkit: str,
        params: ToolExecuteParams
    ) -> ToolExecuteParams:
        print(f"🔧 Executing {toolkit}.{tool}")
        print(f"   Arguments: {params.get('arguments', {})}")
        return params

    @after_execute(tools=[])
    def log_after(
        tool: str,
        toolkit: str,
        response: ToolExecutionResponse
    ) -> ToolExecutionResponse:
        print(f"✅ Completed {toolkit}.{tool}")
        if "data" in response:
            print(f"   Response: {response['data']}")
        return response

    # Get tools with modifiers
    tools = session.tools(modifiers=[log_before, log_after])

    return tools
```

## Framework Comparison

| Framework | Native Tools | MCP | Provider Package | Best For |
|-----------|--------------|-----|------------------|----------|
| **Vercel AI SDK** | ✅ | ✅ | `@composio/vercel` | Modern web apps, streaming |
| **OpenAI Agents SDK** | ✅ | ✅ | `@composio/openai-agents` | Production agents |
| **LangChain** | ❌ | ✅ | N/A (MCP only) | Complex chains, memory |
| **Claude Agent SDK** | ✅ | ✅ | `@composio/claude-agent-sdk` | Claude-specific features |
| **CrewAI** | ❌ | ✅ | N/A (MCP only) | Multi-agent teams |

## Pattern: Framework Switching

```typescript
// Same session, different frameworks
const composio = new Composio();
const session = await composio.create('user_123', { toolkits: ['gmail'] });

// Use with Vercel AI SDK
const client1 = await createMCPClient({
  transport: { type: 'http', url: session.mcp.url, headers: session.mcp.headers }
});

// Use with LangChain
const client2 = new MultiServerMCPClient({
  composio: { transport: 'http', url: session.mcp.url, headers: session.mcp.headers }
});

// Use with OpenAI Agents
const client3 = hostedMcpTool({
  serverUrl: session.mcp.url,
  headers: session.mcp.headers
});

// ✅ Same tools, different frameworks
// ✅ Framework flexibility with MCP
```

## Best Practices

### 1. **Choose Native Tools When Available**
- Faster execution (no MCP overhead)
- Better performance for production
- Full control with modifiers

### 2. **Use MCP for Flexibility**
- When using multiple frameworks
- During prototyping phase
- When native tools unavailable

### 3. **Always Create User Sessions**
- Never share sessions across users
- Use proper user IDs (not 'default')
- Isolate tools per user

### 4. **Enable Connection Management**
- Set `manageConnections: true`
- Let agent handle authentication
- Better user experience

### 5. **Add Logging with Modifiers**
- Use beforeExecute/afterExecute
- Track tool execution
- Debug agent behavior

### 6. **Handle Streaming Properly**
- Use framework's streaming APIs
- Process events as they arrive
- Better UX for long operations

## Key Principles

1. **Native tools recommended** - Faster and more control
2. **MCP for flexibility** - Framework independent
3. **User isolation** - Create sessions per user
4. **Connection management** - Enable auto-authentication
5. **Logging and monitoring** - Use modifiers for observability
6. **Framework agnostic** - Same session works with any framework

## Reference

- [Tool Router Documentation](https://docs.composio.dev/sdk/typescript/api/tool-router)
- [Vercel AI SDK](https://sdk.vercel.ai)
- [OpenAI Agents SDK](https://github.com/openai/agents)
- [LangChain](https://langchain.com)
- [Claude Agent SDK](https://github.com/anthropics/anthropic-sdk-typescript)
- [CrewAI](https://www.crewai.com)

---

### 1.7. Auto Authentication in Chat

<a name="auto-authentication-in-chat"></a>

**Impact:** 🟠 HIGH

> Allow users to authenticate toolkits directly within chat conversations

# Enable Auto Authentication in Chat

Enable `manageConnections` to allow users to authenticate toolkits on-demand during agent conversations.

## ❌ Incorrect

```typescript
// DON'T: Disable connection management for interactive apps
const session = await composio.create('user_123', {
  toolkits: ['gmail'],
  manageConnections: false // User can't authenticate!
});

// Agent tries to use Gmail but user isn't connected
// Tool execution will fail with no way to fix it
```

```python
# DON'T: Disable connection management for interactive apps
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail"],
    manage_connections=False  # User can't authenticate!
)

# Agent tries to use Gmail but user isn't connected
# Tool execution will fail with no way to fix it
```

## ✅ Correct

```typescript
// DO: Enable connection management for interactive apps
import { Composio } from '@composio/core';

const composio = new Composio();
const session = await composio.create('user_123', {
  toolkits: ['gmail', 'slack'],
  manageConnections: true // Users can authenticate in chat
});

// When agent needs Gmail and user isn't connected:
// 1. Agent calls COMPOSIO_MANAGE_CONNECTIONS tool
// 2. User receives auth link in chat
// 3. User authenticates via OAuth
// 4. Agent continues with Gmail access
```

```python
# DO: Enable connection management for interactive apps
from composio import Composio

composio = Composio()
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack"],
    manage_connections=True  # Users can authenticate in chat
)

# When agent needs Gmail and user isn't connected:
# 1. Agent calls COMPOSIO_MANAGE_CONNECTIONS tool
# 2. User receives auth link in chat
# 3. User authenticates via OAuth
# 4. Agent continues with Gmail access
```

## Advanced: Custom Callback URL

```typescript
// Configure custom callback for OAuth flow
const session = await composio.create('user_123', {
  toolkits: ['gmail'],
  manageConnections: {
    enable: true,
    callbackUrl: 'https://your-app.com/auth/callback'
  }
});
```

```python
# Configure custom callback for OAuth flow
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail"],
    manage_connections={
        "enable": True,
        "callback_url": "https://your-app.com/auth/callback"
    }
)
```

## How It Works

1. Agent detects missing connection for a toolkit
2. Agent automatically calls meta tool `COMPOSIO_MANAGE_CONNECTIONS`
3. Tool returns OAuth redirect URL
4. User authenticates via the URL
5. Agent resumes with access granted

## Reference

- [Connection Management](https://docs.composio.dev/sdk/typescript/api/tool-router#manageconnections)
- [Authorization Flow](https://docs.composio.dev/sdk/typescript/api/tool-router#authorization-flow)

---

### 1.8. Manual Authorization

<a name="manual-authorization"></a>

**Impact:** 🟡 MEDIUM

> Control authentication flows explicitly using session.authorize() for onboarding and settings pages

# Use Manual Authorization for Explicit Control

Use `session.authorize()` to explicitly control when users authenticate toolkits - perfect for onboarding flows, settings pages, or when you want authentication before starting agent workflows.

## ❌ Incorrect

```typescript
// DON'T: Mix auto and manual auth without clear purpose
const session = await composio.create('user_123', {
  toolkits: ['gmail'],
  manageConnections: true // Agent handles auth
});

// Then immediately force manual auth (redundant)
await session.authorize('gmail');
// Agent could have handled this automatically
```

```python
# DON'T: Mix auto and manual auth without clear purpose
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail"],
    manage_connections=True  # Agent handles auth
)

# Then immediately force manual auth (redundant)
session.authorize("gmail")
# Agent could have handled this automatically
```

## ✅ Correct - Onboarding Flow

```typescript
// DO: Use manual auth for onboarding before agent starts
import { Composio } from '@composio/core';

const composio = new Composio();

// Step 1: Create session for onboarding
const session = await composio.create('user_123', {
  toolkits: ['gmail', 'slack']
});

// Step 2: Explicitly connect required toolkits during onboarding
async function onboardUser() {
  const requiredToolkits = ['gmail', 'slack'];

  for (const toolkit of requiredToolkits) {
    const connectionRequest = await session.authorize(toolkit, {
      callbackUrl: 'https://your-app.com/onboarding/callback'
    });

    console.log(`Connect ${toolkit}:`, connectionRequest.redirectUrl);

    // Wait for user to complete each connection
    await connectionRequest.waitForConnection();
    console.log(`✓ ${toolkit} connected`);
  }

  console.log('Onboarding complete! All toolkits connected.');
}
```

```python
# DO: Use manual auth for onboarding before agent starts
from composio import Composio

composio = Composio()

# Step 1: Create session for onboarding
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack"]
)

# Step 2: Explicitly connect required toolkits during onboarding
async def onboard_user():
    required_toolkits = ["gmail", "slack"]

    for toolkit in required_toolkits:
        connection_request = session.authorize(
            toolkit,
            callback_url="https://your-app.com/onboarding/callback"
        )

        print(f"Connect {toolkit}: {connection_request.redirect_url}")

        # Wait for user to complete each connection
        connection_request.wait_for_connection()
        print(f"✓ {toolkit} connected")

    print("Onboarding complete! All toolkits connected.")
```

## ✅ Correct - Settings Page

```typescript
// DO: Manual auth for connection management in settings
async function settingsPageHandler(userId: string, toolkit: string) {
  const session = await composio.create(userId, {
    toolkits: [toolkit]
  });

  // User clicked "Connect" button in settings
  const connectionRequest = await session.authorize(toolkit, {
    callbackUrl: 'https://your-app.com/settings/callback'
  });

  // Redirect user to OAuth flow
  return { redirectUrl: connectionRequest.redirectUrl };
}
```

```python
# DO: Manual auth for connection management in settings
async def settings_page_handler(user_id: str, toolkit: str):
    session = composio.tool_router.create(
        user_id=user_id,
        toolkits=[toolkit]
    )

    # User clicked "Connect" button in settings
    connection_request = session.authorize(
        toolkit,
        callback_url="https://your-app.com/settings/callback"
    )

    # Redirect user to OAuth flow
    return {"redirect_url": connection_request.redirect_url}
```

## When to Use Manual Authorization

**Use `session.authorize()` for:**
- **Onboarding flows**: Connect required toolkits before user can proceed
- **Settings pages**: User explicitly manages connections via UI
- **Pre-authentication**: Ensure critical connections exist before starting workflows
- **Re-authorization**: Handle expired or revoked connections

**Use `manageConnections: true` (auto) for:**
- **Interactive agents**: Let agent prompt for auth when needed
- **Flexible workflows**: User may or may not have connections
- **Just-in-time auth**: Only authenticate when toolkit is actually used

## Key Difference

- **Manual auth** = You control WHEN authentication happens
- **Auto auth** = Agent handles authentication ON-DEMAND when tools need it

## Reference

- [session.authorize()](https://docs.composio.dev/sdk/typescript/api/tool-router#authorize)
- [Authorization Flow](https://docs.composio.dev/sdk/typescript/api/tool-router#authorization-flow)

---

### 1.9. Connection Management

<a name="connection-management"></a>

**Impact:** 🔴 CRITICAL

> Understand manageConnections settings to control authentication behavior in Tool Router

# Configure Connection Management Properly

The `manageConnections` setting determines how Tool Router handles missing toolkit connections. Configure it correctly based on your application type.

## ❌ Incorrect

```typescript
// DON'T: Disable connections in interactive applications
const session = await composio.create('user_123', {
  toolkits: ['gmail'],
  manageConnections: false // Tools will FAIL if user not connected!
});

// When agent tries to use Gmail:
// ❌ Error: No connected account found for gmail
// User has no way to authenticate
```

```python
# DON'T: Disable connections in interactive applications
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail"],
    manage_connections=False  # Tools will FAIL if user not connected!
)

# When agent tries to use Gmail:
# ❌ Error: No connected account found for gmail
# User has no way to authenticate
```

## ✅ Correct - Enable Auto Authentication (Default)

```typescript
// DO: Enable connection management for interactive apps
import { Composio } from '@composio/core';

const composio = new Composio();

// Option 1: Use default (manageConnections: true)
const session1 = await composio.create('user_123', {
  toolkits: ['gmail', 'slack']
  // manageConnections defaults to true
});

// Option 2: Explicitly enable with boolean
const session2 = await composio.create('user_123', {
  toolkits: ['gmail'],
  manageConnections: true // Agent can prompt for auth
});

// How it works:
// 1. Agent tries to use Gmail tool
// 2. No connection exists
// 3. Agent calls COMPOSIO_MANAGE_CONNECTIONS meta tool
// 4. User receives auth link in chat
// 5. User authenticates
// 6. Agent continues with Gmail access
```

```python
# DO: Enable connection management for interactive apps
from composio import Composio

composio = Composio()

# Option 1: Use default (manage_connections: True)
session1 = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack"]
    # manage_connections defaults to True
)

# Option 2: Explicitly enable with boolean
session2 = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail"],
    manage_connections=True  # Agent can prompt for auth
)

# How it works:
# 1. Agent tries to use Gmail tool
# 2. No connection exists
# 3. Agent calls COMPOSIO_MANAGE_CONNECTIONS meta tool
# 4. User receives auth link in chat
# 5. User authenticates
# 6. Agent continues with Gmail access
```

## ✅ Correct - Advanced Configuration

```typescript
// DO: Configure with object for fine-grained control
const session = await composio.create('user_123', {
  toolkits: ['gmail', 'slack'],
  manageConnections: {
    enable: true, // Allow in-chat authentication
    callbackUrl: 'https://your-app.com/auth/callback', // Custom OAuth callback
    waitForConnections: true // Wait for user to complete auth before proceeding
  }
});

// With waitForConnections: true
// Session creation waits until user completes authentication
// Perfect for workflows where connections are required upfront
```

```python
# DO: Configure with object for fine-grained control
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack"],
    manage_connections={
        "enable": True,  # Allow in-chat authentication
        "callback_url": "https://your-app.com/auth/callback",  # Custom OAuth callback
        "wait_for_connections": True  # Wait for user to complete auth before proceeding
    }
)

# With wait_for_connections: True
# Session creation waits until user completes authentication
# Perfect for workflows where connections are required upfront
```

## Configuration Options

```typescript
manageConnections: boolean | {
  enable?: boolean;           // Enable/disable connection management (default: true)
  callbackUrl?: string;       // Custom OAuth callback URL
  waitForConnections?: boolean; // Block until connections complete (default: false)
}
```

## When to Use Each Setting

**`manageConnections: true` (Default)**
- Interactive chat applications
- User can authenticate on-demand
- Flexible, user-friendly experience

**`manageConnections: { waitForConnections: true }`**
- Workflows requiring connections upfront
- Onboarding flows
- Critical operations needing guaranteed access

**`manageConnections: false`**
- Backend automation (no user interaction)
- Pre-connected accounts only
- System-to-system integrations
- ⚠️ Tools WILL FAIL if connections are missing

## Key Insight

With `manageConnections: true`, **you never need to check connections before agent execution**. The agent intelligently prompts users for authentication only when needed. This creates the smoothest user experience.

## Reference

- [Connection Management](https://docs.composio.dev/sdk/typescript/api/tool-router#manageconnections)
- [Wait for Connections](https://docs.composio.dev/sdk/typescript/api/tool-router#wait-for-connections)

---

### 1.10. Building Chat UIs

<a name="building-chat-uis"></a>

**Impact:** 🟠 HIGH

> Best practices for building chat applications with toolkit selection, connection management, and session handling

# Building Chat UIs with Tool Router

Build chat applications with Tool Router using **Vercel AI SDK**, create **sessions per message** with dynamic configuration, and provide **toolkit selection** and **connection management** UI.

## Recommended: Vercel AI SDK

- Native streaming support
- React hooks for chat interfaces
- Built-in UI components
- Excellent DX with Tool Router

## ❌ Incorrect - Sharing Sessions Without Config

```typescript
// DON'T: Reuse sessions without proper configuration
const globalSession = await composio.create('default', {
  toolkits: ['gmail'] // Hard-coded toolkits
});

app.post('/api/chat', async (req, res) => {
  // ❌ No user isolation
  // ❌ No per-message configuration
  // ❌ Can't change toolkits dynamically
  const tools = await globalSession.tools();
});
```

## ✅ Correct - Session Per Message

```typescript
// DO: Create sessions per message with proper config
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

const composio = new Composio({ provider: new VercelProvider() });

app.post('/api/chat', async (req, res) => {
  const { userId, message, selectedToolkits } = req.body;

  // Create new session for this message
  const session = await composio.create(userId, {
    toolkits: selectedToolkits, // User-selected toolkits
    manageConnections: true
  });

  const tools = await session.tools();

  const stream = await streamText({
    model: openai('gpt-4o'),
    messages: [{ role: 'user', content: message }],
    tools,
    maxSteps: 10
  });

  return stream.toDataStreamResponse();
});
```

## Toolkit Selection UI

### List All Available Toolkits

Create a session **without toolkit filters** to show all available toolkits:

```typescript
// API endpoint to list all toolkits
app.post('/api/toolkits', async (req, res) => {
  const { userId } = req.body;

  // No toolkits parameter = all toolkits available
  const session = await composio.create(userId);
  const toolkits = await session.toolkits();

  res.json(toolkits.map(tk => ({
    slug: tk.slug,
    name: tk.name,
    description: tk.description,
    logo: tk.logo,
    isConnected: tk.connectedAccounts.length > 0
  })));
});
```

### React Component

```typescript
export function ToolkitSelector({ userId, onSelect }: Props) {
  const [toolkits, setToolkits] = useState<Toolkit[]>([]);
  const [selected, setSelected] = useState<string[]>([]);

  useEffect(() => {
    fetch('/api/toolkits', {
      method: 'POST',
      body: JSON.stringify({ userId })
    }).then(res => res.json()).then(setToolkits);
  }, [userId]);

  return (
    <div className="toolkit-grid">
      {toolkits.map(tk => (
        <div
          key={tk.slug}
          className={selected.includes(tk.slug) ? 'selected' : ''}
          onClick={() => setSelected(prev =>
            prev.includes(tk.slug) ? prev.filter(s => s !== tk.slug) : [...prev, tk.slug]
          )}
        >
          <img src={tk.logo} alt={tk.name} />
          <h3>{tk.name}</h3>
          {tk.isConnected && <span>✓ Connected</span>}
        </div>
      ))}
      <button onClick={() => onSelect(selected)}>Use Selected</button>
    </div>
  );
}
```

## Connection Management UI

### Authorize Toolkits

```typescript
// API endpoint to start connection flow
app.post('/api/connect', async (req, res) => {
  const { userId, toolkitSlug } = req.body;

  const session = await composio.create(userId, {
    toolkits: [toolkitSlug]
  });

  const auth = await session.authorize({
    toolkit: toolkitSlug,
    redirectUrl: `${process.env.APP_URL}/auth/callback`
  });

  res.json({ redirectUrl: auth.redirectUrl });
});
```

### React Component

```typescript
export function ConnectedAccounts({ userId }: Props) {
  const [toolkits, setToolkits] = useState<Toolkit[]>([]);

  const handleConnect = async (slug: string) => {
    const res = await fetch('/api/connect', {
      method: 'POST',
      body: JSON.stringify({ userId, toolkitSlug: slug })
    });
    const { redirectUrl } = await res.json();
    window.location.href = redirectUrl;
  };

  return (
    <div>
      {toolkits.map(tk => (
        <div key={tk.slug}>
          <h3>{tk.name}</h3>
          {tk.isConnected ? (
            <button onClick={() => handleDisconnect(tk.slug)}>Disconnect</button>
          ) : (
            <button onClick={() => handleConnect(tk.slug)}>Connect</button>
          )}
        </div>
      ))}
    </div>
  );
}
```

## Connected Account Sharing

**Connected accounts are shared between sessions** (tied to user ID and auth configs, not individual sessions).

```typescript
// Both sessions use the same Gmail connected account
const session1 = await composio.create('user_123', { toolkits: ['gmail'] });
const session2 = await composio.create('user_123', { toolkits: ['gmail', 'slack'] });

// ✅ Connected accounts shared across sessions
// ✅ No need to reconnect for each session
```

### Override Connected Accounts

```typescript
// Override which connected account to use
const session = await composio.create('user_123', {
  toolkits: ['gmail'],
  connectedAccounts: {
    gmail: 'conn_specific_account_id' // Use specific account
  }
});
```

### Override Auth Config

```typescript
// Override which auth config to use
const session = await composio.create('user_123', {
  toolkits: ['gmail'],
  authConfig: {
    gmail: 'auth_config_custom_id' // Use custom auth config
  }
});
```

## Complete Chat Application

```typescript
// app/api/chat/route.ts
import { Composio } from '@composio/core';
import { VercelProvider } from '@composio/vercel';
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

const composio = new Composio({ provider: new VercelProvider() });

export async function POST(req: Request) {
  const { userId, messages, selectedToolkits } = await req.json();

  const session = await composio.create(userId, {
    toolkits: selectedToolkits,
    manageConnections: true
  });

  const tools = await session.tools();

  const result = await streamText({
    model: openai('gpt-4o'),
    messages,
    tools,
    maxSteps: 10
  });

  return result.toDataStreamResponse();
}
```

```typescript
// app/page.tsx - Chat UI
'use client';
import { useChat } from 'ai/react';
import { useState } from 'react';

export default function ChatPage() {
  const [selectedToolkits, setSelectedToolkits] = useState(['gmail']);

  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: '/api/chat',
    body: { userId: 'user_123', selectedToolkits }
  });

  return (
    <div>
      <ToolkitSelector
        userId="user_123"
        selected={selectedToolkits}
        onSelect={setSelectedToolkits}
      />
      <div className="messages">
        {messages.map(m => (
          <div key={m.id} className={m.role}>{m.content}</div>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

## Manual Tool Operations (Advanced)

For custom workflows, you can manually fetch and execute tools instead of using sessions.

### Manual Tool Fetching

```typescript
// Fetch raw tool metadata
const tools = await composio.tools.getRawComposioTools({
  toolkits: ['gmail', 'slack'],
  important: true
});
```

### Manual Tool Execution

```typescript
// Execute tools directly
const result = await composio.tools.execute('GMAIL_SEND_EMAIL', {
  userId: 'user_123',
  arguments: { to: 'test@example.com', subject: 'Hello' },
  version: '15082025_00' // Version REQUIRED for manual execution
});

if (!result.successful) {
  console.error('Failed:', result.error);
}
```

### When to Use Manual Approach

| Use Case | Recommended Approach |
|----------|---------------------|
| Chat UIs, agents, streaming | ✅ `session.tools()` |
| Custom workflows, catalogs | ✅ Manual fetch/execute |

**Reference:** See [Fetching Tools](./app-fetch-tools.md) and [Tool Execution](./app-execute-tools.md) for detailed manual operation guides.

## Best Practices

1. **Create Sessions Per Message** - Fresh session with config for each interaction
2. **Let Users Select Toolkits** - Dynamic toolkit configuration via UI
3. **Show Connection Status** - Display which toolkits are connected
4. **Handle Authorization** - Use `session.authorize()` for auth flows
5. **Enable Connection Management** - Set `manageConnections: true`

## Key Principles

1. **Vercel AI SDK** - Best framework for chat UIs
2. **Session per message** - Fresh sessions with config
3. **No toolkit filter** - List all by creating session without toolkits
4. **Shared connections** - Connected accounts shared across sessions
5. **Override when needed** - Use `connectedAccounts` or `authConfig` for special cases

## Reference

- [Vercel AI SDK](https://sdk.vercel.ai)
- [Tool Router Sessions](https://docs.composio.dev/sdk/typescript/api/tool-router#creating-sessions)
- [Session Authorization](https://docs.composio.dev/sdk/typescript/api/tool-router#authorization)
- [Fetching Tools](./app-fetch-tools.md)
- [Tool Execution](./app-execute-tools.md)
- [Tool Versions](./app-tool-versions.md)

---

### 1.11. Query Toolkit States

<a name="query-toolkit-states"></a>

**Impact:** 🟡 MEDIUM

> Use session.toolkits() to build connection management UIs showing which toolkits are connected

# Query Toolkit Connection States for UI

Use `session.toolkits()` to check connection status and build UIs showing which toolkits are connected. With `manageConnections: true`, agents handle missing connections automatically.

## ❌ Incorrect

```typescript
// DON'T: Build UI without showing connection status
async function showToolkits(session) {
  // Just show toolkit names with no status
  const toolkits = ['Gmail', 'Slack', 'GitHub'];

  return toolkits.map(name => ({
    name,
    // Missing: connection status, auth button, etc.
  }));
}
```

```python
# DON'T: Build UI without showing connection status
def show_toolkits(session):
    # Just show toolkit names with no status
    toolkits = ["Gmail", "Slack", "GitHub"]

    return [{"name": name} for name in toolkits]
    # Missing: connection status, auth button, etc.
```

## ✅ Correct

```typescript
// DO: Query connection states to build connection UI
import { Composio } from '@composio/core';

const composio = new Composio();
const session = await composio.create('user_123', {
  toolkits: ['gmail', 'slack', 'github'],
  manageConnections: true // Agent handles auth automatically
});

// Get connection states for building UI
const { items } = await session.toolkits();

// Build connection management UI
const connectionUI = items.map(toolkit => ({
  slug: toolkit.slug,
  name: toolkit.name,
  logo: toolkit.logo,
  isConnected: toolkit.connection?.isActive || false,
  status: toolkit.connection?.connectedAccount?.status,
  // Show "Connect" button if not connected
  needsAuth: !toolkit.connection?.isActive && !toolkit.isNoAuth
}));

console.log('Connection Status:', connectionUI);
// Use this to render connection cards in your UI
```

```python
# DO: Query connection states to build connection UI
from composio import Composio

composio = Composio()
session = composio.tool_router.create(
    user_id="user_123",
    toolkits=["gmail", "slack", "github"],
    manage_connections=True  # Agent handles auth automatically
)

# Get connection states for building UI
result = session.toolkits()

# Build connection management UI
connection_ui = []
for toolkit in result.items:
    connection_ui.append({
        "slug": toolkit.slug,
        "name": toolkit.name,
        "logo": toolkit.logo,
        "is_connected": toolkit.connection.is_active if toolkit.connection else False,
        "status": toolkit.connection.connected_account.status if toolkit.connection.connected_account else None,
        # Show "Connect" button if not connected
        "needs_auth": not (toolkit.connection.is_active if toolkit.connection else False) and not toolkit.is_no_auth
    })

print(f"Connection Status: {connection_ui}")
# Use this to render connection cards in your UI
```

## Response Structure

```typescript
interface ToolkitConnectionState {
  slug: string;              // 'gmail'
  name: string;              // 'Gmail'
  logo?: string;             // 'https://...'
  isNoAuth: boolean;         // true if no auth needed
  connection: {
    isActive: boolean;       // Is connection active?
    authConfig?: {
      id: string;            // Auth config ID
      mode: string;          // 'OAUTH2', 'API_KEY', etc.
      isComposioManaged: boolean;
    };
    connectedAccount?: {
      id: string;            // Connected account ID
      status: string;        // 'ACTIVE', 'INVALID', etc.
    };
  };
}
```

## Use Cases

- **Build connection UI**: Display connected/disconnected state with auth buttons
- **Settings pages**: Let users view and manage their connections
- **Onboarding flows**: Show which toolkits to connect during setup
- **Status dashboards**: Monitor connection health across toolkits

## Important Note

With `manageConnections: true` (default), you don't need to check connections before agent execution - the agent will prompt users to authenticate when needed. Use `session.toolkits()` primarily for building user-facing connection management UIs.

## Reference

- [session.toolkits()](https://docs.composio.dev/sdk/typescript/api/tool-router#toolkits)
- [Toolkit Connection State](https://docs.composio.dev/sdk/typescript/api/tool-router#toolkitconnectionstate)

---

### 1.12. Creating Triggers

<a name="creating-triggers"></a>

**Impact:** 🟠 HIGH

> Set up trigger instances to receive real-time events from connected accounts

# Create Triggers for Real-Time Events

Triggers receive real-time events from connected accounts (Gmail, GitHub, Slack, etc.). Create trigger instances to subscribe to specific events.

## Basic Usage

```typescript
import { Composio } from '@composio/core';

const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });

// Create trigger for specific connected account
const trigger = await composio.triggers.create(
  'user_123',
  'GMAIL_NEW_GMAIL_MESSAGE',
  {
    connectedAccountId: 'conn_abc123',
    triggerConfig: {
      labelIds: 'INBOX',
      userId: 'me',
      interval: 60
    }
  }
);

console.log('Trigger ID:', trigger.triggerId);
```

## SDK Auto-Discovery

Omit `connectedAccountId` to let SDK find the account automatically:

```typescript
// SDK finds user's Gmail connection
const trigger = await composio.triggers.create(
  'user_123',
  'GMAIL_NEW_GMAIL_MESSAGE',
  {
    triggerConfig: { labelIds: 'INBOX', interval: 60 }
  }
);
```

## Automatic Reuse

Triggers with identical configuration are automatically reused:

```typescript
// First call creates trigger
const trigger1 = await composio.triggers.create(
  'user_123',
  'GMAIL_NEW_GMAIL_MESSAGE',
  { triggerConfig: { labelIds: 'INBOX' } }
);

// Second call returns same trigger (no duplicate)
const trigger2 = await composio.triggers.create(
  'user_123',
  'GMAIL_NEW_GMAIL_MESSAGE',
  { triggerConfig: { labelIds: 'INBOX' } }
);

console.log(trigger1.triggerId === trigger2.triggerId); // true
```

## Version Pinning

Pin trigger versions in production to prevent breaking changes:

```typescript
const composio = new Composio({
  apiKey: process.env.COMPOSIO_API_KEY,
  triggerVersions: {
    'GMAIL_NEW_GMAIL_MESSAGE': '12082025_00',
    'GITHUB_COMMIT_EVENT': '12082025_00'
  }
});

// Uses pinned version
const trigger = await composio.triggers.create(
  'user_123',
  'GMAIL_NEW_GMAIL_MESSAGE',
  { triggerConfig: { labelIds: 'INBOX' } }
);
```

**Why pin versions:**
- Prevents config schema changes
- Ensures production stability
- Updates on your schedule

## Trigger Configuration Examples

```typescript
// Gmail - New messages in specific label
await composio.triggers.create('user_123', 'GMAIL_NEW_GMAIL_MESSAGE', {
  triggerConfig: {
    labelIds: 'INBOX',
    userId: 'me',
    interval: 60
  }
});

// GitHub - New commits
await composio.triggers.create('user_123', 'GITHUB_COMMIT_EVENT', {
  triggerConfig: {
    owner: 'composio',
    repo: 'sdk',
    branch: 'main'
  }
});

// Slack - New messages in channel
await composio.triggers.create('user_123', 'SLACK_NEW_MESSAGE', {
  triggerConfig: {
    channelId: 'C123456',
    botUserId: 'U123456'
  }
});
```

## Error Handling

```typescript
try {
  const trigger = await composio.triggers.create(
    'user_123',
    'GMAIL_NEW_GMAIL_MESSAGE',
    { triggerConfig: { labelIds: 'INBOX' } }
  );
} catch (error) {
  if (error.name === 'ComposioConnectedAccountNotFoundError') {
    // User hasn't connected Gmail yet
    console.log('Please connect your Gmail account');
  } else if (error.name === 'ValidationError') {
    // Invalid trigger config
    console.error('Invalid configuration:', error.message);
  } else {
    throw error;
  }
}
```

## Discover Available Triggers

```typescript
// Get all triggers
const triggers = await composio.triggers.list();

// Search by keyword
const emailTriggers = await composio.triggers.list({ search: 'email' });

// Filter by toolkit
const slackTriggers = await composio.triggers.list({ toolkit: 'slack' });

// Get trigger details
const trigger = await composio.triggers.getTrigger('GMAIL_NEW_GMAIL_MESSAGE');
console.log(trigger.config); // Shows required config fields
```

## List Active Triggers

```typescript
// All active triggers
const active = await composio.triggers.getActiveTriggers();

// By trigger slug
const gmailTriggers = await composio.triggers.getActiveTriggers({
  triggerSlugs: ['GMAIL_NEW_GMAIL_MESSAGE']
});

// By connected account
const accountTriggers = await composio.triggers.getActiveTriggers({
  connectedAccountIds: ['conn_abc123']
});

// Combine filters
const userSlackTriggers = await composio.triggers.getActiveTriggers({
  triggerSlugs: ['SLACK_NEW_MESSAGE'],
  connectedAccountIds: ['conn_def456']
});
```

## Common Patterns

### Check Before Creating

```typescript
async function ensureTrigger(userId: string, triggerSlug: string, config: any) {
  // Check if trigger exists
  const existing = await composio.triggers.getActiveTriggers({
    triggerSlugs: [triggerSlug]
  });

  if (existing.items.length > 0) {
    return existing.items[0];
  }

  // Create if doesn't exist
  return await composio.triggers.create(userId, triggerSlug, {
    triggerConfig: config
  });
}
```

### Onboarding Flow

```typescript
async function setupUserTriggers(userId: string) {
  // Check connected accounts
  const accounts = await composio.connectedAccounts.list({
    userIds: [userId]
  });

  // Create triggers for each service
  for (const account of accounts.items) {
    if (account.toolkit.slug === 'gmail') {
      await composio.triggers.create(userId, 'GMAIL_NEW_GMAIL_MESSAGE', {
        connectedAccountId: account.id,
        triggerConfig: { labelIds: 'INBOX' }
      });
    }
  }
}
```

## Key Points

- **Use proper user IDs** - Never use 'default' in production
- **Requires connected account** - User must authenticate first
- **Automatic reuse** - Identical configs share same trigger instance
- **Pin versions** - Prevents breaking changes in production
- **Error handling** - Handle missing connections gracefully

---

### 1.13. Subscribing to Events

<a name="subscribing-to-events"></a>

**Impact:** 🟡 MEDIUM

> Listen to real-time trigger events during development using subscribe()

# Subscribe to Trigger Events

Use `subscribe()` to listen to trigger events in **development only**. For production, use webhooks via `listenToTriggers()`.

## Development vs Production

**Development (subscribe):**
- Real-time event listening in CLI/local development
- Simple callback function
- No webhook URLs needed
- **Do NOT use in production**

**Production (webhooks):**
- Scalable webhook delivery
- Reliable event processing
- Use `listenToTriggers()` with Express/HTTP server
- See triggers-webhook.md

## Basic Subscribe

```typescript
import { Composio } from '@composio/core';

const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });

// Subscribe to trigger events
const unsubscribe = await composio.triggers.subscribe((event) => {
  console.log('Trigger received:', event.triggerSlug);
  console.log('Payload:', event.payload);
  console.log('User:', event.userId);
  console.log('Account:', event.connectedAccountId);
});

// Keep process alive
console.log('Listening for events... Press Ctrl+C to stop');
```

## Subscribe with Filters

```typescript
// Filter by trigger slug
await composio.triggers.subscribe(
  (event) => {
    console.log('Gmail message:', event.payload);
  },
  { triggerSlugs: ['GMAIL_NEW_GMAIL_MESSAGE'] }
);

// Filter by user ID
await composio.triggers.subscribe(
  (event) => {
    console.log('Event for user_123:', event.payload);
  },
  { userIds: ['user_123'] }
);

// Filter by connected account
await composio.triggers.subscribe(
  (event) => {
    console.log('Event from specific account:', event.payload);
  },
  { connectedAccountIds: ['conn_abc123'] }
);

// Combine filters
await composio.triggers.subscribe(
  (event) => {
    console.log('Filtered event:', event.payload);
  },
  {
    triggerSlugs: ['SLACK_NEW_MESSAGE'],
    userIds: ['user_123'],
    connectedAccountIds: ['conn_def456']
  }
);
```

## Event Payload Structure

```typescript
interface TriggerEvent {
  triggerSlug: string;           // 'GMAIL_NEW_GMAIL_MESSAGE'
  userId: string;                // 'user_123'
  connectedAccountId: string;    // 'conn_abc123'
  payload: {
    // Trigger-specific data
    // Example for Gmail:
    // { id: 'msg_123', subject: 'Hello', from: 'user@example.com' }
  };
  metadata: {
    triggerId: string;
    timestamp: string;
  };
}
```

## Unsubscribe

```typescript
const unsubscribe = await composio.triggers.subscribe((event) => {
  console.log('Event:', event);
});

// Stop listening
await unsubscribe();
console.log('Unsubscribed from all triggers');
```

## Development Pattern

```typescript
async function devMode() {
  console.log('Starting development mode...');

  // Subscribe to events
  const unsubscribe = await composio.triggers.subscribe((event) => {
    console.log(`\n[${event.triggerSlug}]`);
    console.log('User:', event.userId);
    console.log('Payload:', JSON.stringify(event.payload, null, 2));
  });

  // Handle shutdown
  process.on('SIGINT', async () => {
    console.log('\nShutting down...');
    await unsubscribe();
    process.exit(0);
  });

  console.log('Listening for events. Press Ctrl+C to stop.');
}

devMode();
```

## Migration to Production

Development (subscribe):
```typescript
// Development only
await composio.triggers.subscribe((event) => {
  console.log(event);
});
```

Production (webhooks):
```typescript
// Production ready
import express from 'express';

const app = express();
const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });

await composio.triggers.listenToTriggers(app, (event) => {
  console.log('Webhook received:', event);
});

app.listen(3000);
```

## Key Points

- **Development only** - Never use subscribe() in production
- **Use webhooks for production** - More reliable and scalable
- **Filter events** - Reduce noise with triggerSlugs, userIds, connectedAccountIds
- **Cleanup** - Always call unsubscribe() when done
- **Long-running process** - Keep Node.js process alive to receive events

---

### 1.14. Webhook Verification

<a name="webhook-verification"></a>

**Impact:** 🔴 CRITICAL

> Use webhook verification for reliable, scalable event delivery in production

# Webhook Verification for Production

Webhooks are the **production-ready** way to receive trigger events. Provides reliable delivery, automatic retries, and works with serverless.

## Setup with listenToTriggers()

```typescript
import express from 'express';
import { Composio } from '@composio/core';

const app = express();
const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });

// Automatic webhook verification and handling
await composio.triggers.listenToTriggers(app, async (event) => {
  console.log('Webhook:', event.triggerSlug);
  console.log('User:', event.userId);
  console.log('Payload:', event.payload);

  await handleEvent(event);
});

app.listen(3000);
```

**What it does:**
- Creates `/composio/triggers` endpoint
- Verifies webhook signatures automatically
- Parses and validates payloads
- Calls callback with verified events

## Manual Verification

For custom endpoints:

```typescript
import { verifyWebhookSignature } from '@composio/core';

app.post('/custom/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  const signature = req.headers['x-composio-signature'];
  const payload = req.body;

  const isValid = verifyWebhookSignature(
    payload,
    signature,
    process.env.COMPOSIO_WEBHOOK_SECRET
  );

  if (!isValid) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  const event = JSON.parse(payload);
  handleEvent(event);
  res.json({ success: true });
});
```

## Event Structure

```typescript
interface WebhookEvent {
  triggerSlug: string;
  userId: string;
  connectedAccountId: string;
  payload: object;
  metadata: {
    triggerId: string;
    timestamp: string;
    webhookId: string;
  };
}
```

## Processing Patterns

### Route by Trigger Type

```typescript
async function handleEvent(event: WebhookEvent) {
  switch (event.triggerSlug) {
    case 'GMAIL_NEW_GMAIL_MESSAGE':
      await handleGmail(event.userId, event.payload);
      break;
    case 'GITHUB_COMMIT_EVENT':
      await handleGithub(event.userId, event.payload);
      break;
    case 'SLACK_NEW_MESSAGE':
      await handleSlack(event.userId, event.payload);
      break;
  }
}
```

### With Error Handling

```typescript
await composio.triggers.listenToTriggers(app, async (event) => {
  try {
    await processEvent(event);
  } catch (error) {
    console.error('Error:', error);
    // Don't throw - acknowledge webhook received
  }
});
```

### With Idempotency

```typescript
await composio.triggers.listenToTriggers(app, async (event) => {
  const webhookId = event.metadata.webhookId;

  // Check if already processed
  if (await isProcessed(webhookId)) {
    console.log('Duplicate webhook, skipping');
    return;
  }

  // Mark as processed
  await markProcessed(webhookId);

  // Process event
  await handleEvent(event);
});
```

## Configuration

Set webhook URL in Composio dashboard:

1. Go to [platform.composio.dev](https://platform.composio.dev)
2. **Settings** > **Webhooks**
3. Set URL: `https://your-app.com/composio/triggers`

**Requirements:**
- HTTPS URL (publicly accessible)
- Respond with 200 OK within 30 seconds
- Handle concurrent requests

## Testing Locally

Use ngrok:

```bash
ngrok http 3000
# Use https://abc123.ngrok.io/composio/triggers in dashboard
```

## Security

- **Always verify signatures** - Use `listenToTriggers()` or manual verification
- **HTTPS only** - Never HTTP in production
- **Keep secrets secure** - Environment variables only
- **Validate payloads** - Check required fields
- **Handle errors gracefully** - Log, don't throw
- **Implement idempotency** - Use webhookId to deduplicate

## Common Issues

**401 Unauthorized:**
- Invalid signature - check webhook secret
- Wrong secret - verify environment variable

**Timeout:**
- Processing > 30 seconds - move to background queue
- Return 200 OK immediately

**Duplicates:**
- Webhooks may deliver multiple times
- Use webhookId for idempotency

## Complete Example

```typescript
import express from 'express';
import { Composio } from '@composio/core';

const app = express();
const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });

await composio.triggers.listenToTriggers(app, async (event) => {
  try {
    // Idempotency check
    if (await isProcessed(event.metadata.webhookId)) {
      return;
    }

    // Process
    switch (event.triggerSlug) {
      case 'GMAIL_NEW_GMAIL_MESSAGE':
        await sendNotification(event.userId, {
          title: 'New Email',
          body: event.payload.subject
        });
        break;
    }

    // Mark processed
    await markProcessed(event.metadata.webhookId);
  } catch (error) {
    console.error('Error:', error);
  }
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

## Key Points

- **Production standard** - Use webhooks, not subscribe()
- **listenToTriggers()** - Handles verification automatically
- **HTTPS required** - Security requirement
- **Quick response** - Return 200 OK within 30s
- **Idempotency** - Handle duplicates with webhookId
- **Error handling** - Log but don't throw

---

### 1.15. Managing Triggers

<a name="managing-triggers"></a>

**Impact:** 🟠 HIGH

> Control trigger states, update configurations, and manage trigger instances

# Manage Trigger Lifecycle

Control trigger states and configurations without recreating triggers.

## Enable/Disable Triggers

```typescript
// Disable trigger (stop receiving events)
await composio.triggers.disable('trigger_id_123');

// Enable trigger (resume receiving events)
await composio.triggers.enable('trigger_id_123');
```

**Use cases:**
- **Disable:** Pause events temporarily, user disconnects account, billing issues
- **Enable:** Resume after resolving issues, user reconnects account

## Update Trigger Configuration

```typescript
// Update trigger config
await composio.triggers.update('trigger_id_123', {
  triggerConfig: {
    labelIds: 'SENT', // Changed from 'INBOX'
    interval: 120     // Changed from 60
  }
});
```

**Updateable fields:**
- `triggerConfig` - Trigger-specific configuration
- Cannot change trigger slug or connected account

## Delete Triggers

```typescript
await composio.triggers.delete('trigger_id_123');
```

**Warning:** Permanent deletion. Creates new trigger if needed later.

## List Active Triggers

```typescript
// All active triggers
const triggers = await composio.triggers.getActiveTriggers();

// By trigger slug
const gmailTriggers = await composio.triggers.getActiveTriggers({
  triggerSlugs: ['GMAIL_NEW_GMAIL_MESSAGE']
});

// By user
const userTriggers = await composio.triggers.getActiveTriggers({
  userIds: ['user_123']
});

// By connected account
const accountTriggers = await composio.triggers.getActiveTriggers({
  connectedAccountIds: ['conn_abc123']
});

// By status
const enabled = await composio.triggers.getActiveTriggers({
  status: 'enabled'
});
const disabled = await composio.triggers.getActiveTriggers({
  status: 'disabled'
});

// Combine filters
const filtered = await composio.triggers.getActiveTriggers({
  triggerSlugs: ['SLACK_NEW_MESSAGE'],
  userIds: ['user_123'],
  status: 'enabled'
});
```

**Response includes:**
- `triggerId` - Unique ID
- `triggerSlug` - Trigger type
- `userId` - User ID
- `connectedAccountId` - Account ID
- `status` - 'enabled' or 'disabled'
- `config` - Current configuration
- `createdAt`, `updatedAt` - Timestamps

## Get Trigger Details

```typescript
// Get specific trigger
const trigger = await composio.triggers.getTriggerById('trigger_id_123');

console.log(trigger.status);                // 'enabled'
console.log(trigger.triggerSlug);           // 'GMAIL_NEW_GMAIL_MESSAGE'
console.log(trigger.config.triggerConfig);  // { labelIds: 'INBOX', ... }
```

## Common Patterns

### Pause User's Triggers

```typescript
async function pauseUserTriggers(userId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId],
    status: 'enabled'
  });

  for (const trigger of triggers.items) {
    await composio.triggers.disable(trigger.triggerId);
  }
}
```

### Resume User's Triggers

```typescript
async function resumeUserTriggers(userId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId],
    status: 'disabled'
  });

  for (const trigger of triggers.items) {
    await composio.triggers.enable(trigger.triggerId);
  }
}
```

### Clean Up Disconnected Account Triggers

```typescript
async function cleanupTriggers(connectedAccountId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    connectedAccountIds: [connectedAccountId]
  });

  for (const trigger of triggers.items) {
    await composio.triggers.delete(trigger.triggerId);
  }
}
```

### Update All User Gmail Triggers

```typescript
async function updateGmailInterval(userId: string, newInterval: number) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId],
    triggerSlugs: ['GMAIL_NEW_GMAIL_MESSAGE']
  });

  for (const trigger of triggers.items) {
    await composio.triggers.update(trigger.triggerId, {
      triggerConfig: {
        ...trigger.config.triggerConfig,
        interval: newInterval
      }
    });
  }
}
```

### Check Trigger Status

```typescript
async function isTriggerActive(triggerId: string): Promise<boolean> {
  try {
    const trigger = await composio.triggers.getTriggerById(triggerId);
    return trigger.status === 'enabled';
  } catch (error) {
    return false; // Trigger doesn't exist
  }
}
```

### Get Trigger Count by User

```typescript
async function getUserTriggerCount(userId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId]
  });

  return {
    total: triggers.items.length,
    enabled: triggers.items.filter(t => t.status === 'enabled').length,
    disabled: triggers.items.filter(t => t.status === 'disabled').length
  };
}
```

## Lifecycle Management

### Account Disconnection

```typescript
// When user disconnects an account
async function handleAccountDisconnect(accountId: string) {
  // Option 1: Disable triggers (can resume later)
  const triggers = await composio.triggers.getActiveTriggers({
    connectedAccountIds: [accountId]
  });
  for (const trigger of triggers.items) {
    await composio.triggers.disable(trigger.triggerId);
  }

  // Option 2: Delete triggers (permanent)
  for (const trigger of triggers.items) {
    await composio.triggers.delete(trigger.triggerId);
  }
}
```

### Account Reconnection

```typescript
// When user reconnects
async function handleAccountReconnect(accountId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    connectedAccountIds: [accountId],
    status: 'disabled'
  });

  for (const trigger of triggers.items) {
    await composio.triggers.enable(trigger.triggerId);
  }
}
```

### Subscription Management

```typescript
// Downgrade: disable non-essential triggers
async function handleDowngrade(userId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId],
    triggerSlugs: ['NON_ESSENTIAL_TRIGGER']
  });

  for (const trigger of triggers.items) {
    await composio.triggers.disable(trigger.triggerId);
  }
}

// Upgrade: enable all triggers
async function handleUpgrade(userId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId],
    status: 'disabled'
  });

  for (const trigger of triggers.items) {
    await composio.triggers.enable(trigger.triggerId);
  }
}
```

## Key Points

- **Disable vs Delete** - Disable pauses events, delete is permanent
- **Update config** - Change trigger settings without recreating
- **Filter getActiveTriggers** - Use multiple filters to narrow results
- **Batch operations** - Loop through triggers for bulk enable/disable
- **Handle disconnects** - Disable or delete triggers when accounts disconnect
- **Status check** - Always verify trigger status before operations

---

## 2. Building Apps with Composio Tools

<a name="building-apps-with-composio-tools"></a>

### 2.1. Fetching Tools

<a name="fetching-tools"></a>

**Impact:** 🟠 HIGH

> Essential patterns for discovering and retrieving tools from Composio for direct execution in traditional applications

# Fetching Tools for Applications

When building traditional applications (non-agent workflows), use direct tool fetching methods to discover and retrieve tools from Composio.

## Methods Overview

- **`tools.get()`** - Use when working with a provider (OpenAI, Vercel, etc.). Returns tools wrapped in provider-specific format.
- **`tools.getRawComposioTools()`** - Use for standalone applications and building UIs. Returns raw tool metadata without provider wrapping.

### 1. tools.get() - For Provider-Based Applications

Use `tools.get()` when you're using Composio with a provider like OpenAI, Vercel AI SDK, or LangChain. This method wraps tools in the format expected by your provider.

**Get tools from a toolkit:**
```typescript
// Get important tools only (auto-applies important filter)
const importantGithubTools = await composio.tools.get('default', {
  toolkits: ['github']
});

// Get a limited number of tools (does NOT auto-apply important filter)
const githubTools = await composio.tools.get('default', {
  toolkits: ['github'],
  limit: 10
});
```

**Get a specific tool by slug:**
```typescript
const tool = await composio.tools.get('default', 'GITHUB_GET_REPO');
```

### 2. tools.getRawComposioTools() - For Standalone Applications & UIs

Use `getRawComposioTools()` for standalone applications and building UIs. This method returns raw tool metadata without provider-specific wrapping, making it ideal for:
- Building tool selection UIs
- Creating tool catalogs or documentation
- Direct tool execution workflows (without providers)
- Custom tool management interfaces

```typescript
// Get important tools (auto-applies important filter)
const importantTools = await composio.tools.getRawComposioTools({
  toolkits: ['github']
});

// Get specific tools by slug
const specificTools = await composio.tools.getRawComposioTools({
  tools: ['GITHUB_GET_REPOS', 'SLACK_SEND_MESSAGE']
});

// Get limited tools (does NOT auto-apply important)
const limitedTools = await composio.tools.getRawComposioTools({
  toolkits: ['slack'],
  limit: 5
});
```

## Important Filter Behavior

The `important` filter auto-applies to show only the most commonly used tools.

**Auto-applies when:**
- Only `toolkits` filter is provided (no other filters)

**Does NOT auto-apply when:**
- `limit` is specified
- `search` is used
- `tools` (specific slugs) are provided
- `tags` are specified
- `important` is explicitly set to `false`

```typescript
// Auto-applies important=true
await composio.tools.get('default', { toolkits: ['github'] });

// Does NOT auto-apply important (limit specified)
await composio.tools.get('default', { toolkits: ['github'], limit: 10 });

// Does NOT auto-apply important (search used)
await composio.tools.get('default', { search: 'repo' });

// Explicitly disable important filter
await composio.tools.get('default', { toolkits: ['github'], important: false });
```

## Filter Parameters

Available filters for both `tools.get()` and `tools.getRawComposioTools()`:

- `toolkits`: Array of toolkit names (e.g., `['github', 'slack']`)
- `tools`: Array of specific tool slugs (e.g., `['GITHUB_GET_REPO']`)
- `search`: Search string for tool names/descriptions
- `limit`: Maximum number of tools to return
- `tags`: Array of tags to filter by
- `scopes`: Array of scopes to filter by
- `authConfigIds`: Array of auth config IDs to filter tools by specific auth configs
- `important`: Boolean to explicitly control important filter (auto-applies in some cases)

**Note:** You cannot use `tools` and `toolkits` filters together.

## Schema Modification

Customize tool schemas at fetch time:

```typescript
const customizedTools = await composio.tools.get('default', {
  toolkits: ['github']
}, {
  modifySchema: ({ toolSlug, toolkitSlug, schema }) => {
    return { ...schema, description: 'Custom description' };
  }
});
```

## Best Practices

1. **Choose the right method:**
   - Use `tools.get()` when working with providers (OpenAI, Vercel, LangChain)
   - Use `tools.getRawComposioTools()` for standalone apps, UIs, and catalogs

2. **Use important filter for UIs**: Show important tools first, then allow users to discover all tools

3. **Cache tool metadata**: Tools don't change frequently, cache the results

4. **Filter by toolkit**: Group tools by toolkit for better organization

5. **Don't mix tools and toolkits filters**: Cannot use both filters together

---

### 2.2. Direct Tool Execution

<a name="direct-tool-execution"></a>

**Impact:** 🟠 HIGH

> Core patterns for manually executing Composio tools in traditional applications without agent frameworks

# Direct Tool Execution for Applications

When building traditional applications without agent frameworks, use `composio.tools.execute()` to manually execute tools.

## Basic Execution

```typescript
// Execute with a specific version (REQUIRED)
const result = await composio.tools.execute('GITHUB_GET_ISSUES', {
  userId: 'default',
  arguments: { owner: 'composio', repo: 'sdk' },
  version: '12082025_00', // Specific version required
});
```

## Version Management

**CRITICAL**: When manually executing tools (especially in workflows), a **specific version is required**. Using `'latest'` will throw an error.

**Why version pinning is required:**
- Tool argument schemas can change between versions
- Using `'latest'` in workflows can cause runtime errors when tools are updated
- Pinned versions ensure workflow stability and predictability
- Version validation prevents production issues from schema mismatches

See [Tool Version Management](app-tool-versions.md) for detailed version strategies.

## Parameters

### ExecuteParams Object

```typescript
{
  userId: string,           // User ID for connected account lookup
  arguments: object,        // Tool-specific input parameters
  version?: string,         // Toolkit version (required for manual execution)
  dangerouslySkipVersionCheck?: boolean  // Bypass version validation (NOT recommended)
}
```

### Execution Modifiers

Transform requests and responses with modifiers:

```typescript
const result = await composio.tools.execute(
  'GITHUB_GET_ISSUES',
  {
    userId: 'default',
    arguments: { owner: 'composio', repo: 'sdk' },
    version: '12082025_00',
  },
  {
    beforeExecute: ({ toolSlug, toolkitSlug, params }) => {
      // Modify params before execution
      console.log('Executing:', toolSlug);
      return {
        ...params,
        arguments: {
          ...params.arguments,
          per_page: 100 // Add default parameter
        }
      };
    },
    afterExecute: ({ toolSlug, toolkitSlug, result }) => {
      // Transform result after execution
      console.log('Completed:', toolSlug);
      return {
        ...result,
        timestamp: new Date().toISOString()
      };
    },
  }
);
```

## Response Format

```typescript
interface ToolExecuteResponse {
  data: any;           // Tool-specific response data
  error: string | null;  // Error message if execution failed
  successful: boolean;   // Whether execution succeeded
}
```

## Error Handling

```typescript
try {
  const result = await composio.tools.execute('GITHUB_GET_ISSUES', {
    userId: 'user_123',
    arguments: { owner: 'composio', repo: 'sdk' },
    version: '12082025_00',
  });

  if (!result.successful) {
    console.error('Tool execution failed:', result.error);
    // Handle error case
    return;
  }

  // Process successful result
  console.log('Issues:', result.data);
} catch (error) {
  if (error.name === 'ComposioToolNotFoundError') {
    console.error('Tool not found');
  } else if (error.name === 'ComposioToolExecutionError') {
    console.error('Execution error:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## Common Error Types

- `ComposioCustomToolsNotInitializedError`: Custom tools instance not initialized
- `ComposioToolNotFoundError`: Tool with the given slug not found
- `ComposioToolExecutionError`: Error during tool execution
- Version validation errors: Thrown when version is missing or `'latest'` is used

## Best Practices

1. **Always specify versions**: Use explicit versions or configure at initialization
2. **Handle errors gracefully**: Check `successful` flag and handle `error` field
3. **Validate arguments**: Ensure all required parameters are provided
4. **Use modifiers sparingly**: Only add modifiers when necessary for transformation
5. **Log execution details**: Track which tools are executed for debugging
6. **Test with real data**: Validate execution with actual connected accounts
7. **Handle authentication errors**: User may not have connected account for toolkit

## Common Patterns

### Execute with retry logic

```typescript
async function executeWithRetry(slug, params, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const result = await composio.tools.execute(slug, params);
      if (result.successful) return result;

      console.log(`Retry ${i + 1}/${maxRetries}`);
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }
  }
}
```

### Execute multiple tools in sequence

```typescript
async function executeWorkflow(userId) {
  // Step 1: Get repository
  const repo = await composio.tools.execute('GITHUB_GET_REPO', {
    userId,
    arguments: { owner: 'composio', repo: 'sdk' },
    version: '12082025_00',
  });

  if (!repo.successful) {
    throw new Error(`Failed to get repo: ${repo.error}`);
  }

  // Step 2: Create issue using data from step 1
  const issue = await composio.tools.execute('GITHUB_CREATE_ISSUE', {
    userId,
    arguments: {
      owner: 'composio',
      repo: 'sdk',
      title: `Update for ${repo.data.name}`,
      body: 'Automated issue creation'
    },
    version: '12082025_00',
  });

  return { repo: repo.data, issue: issue.data };
}
```

### Execute with parameter validation

```typescript
async function sendSlackMessage(userId, channel, text) {
  // Validate inputs
  if (!channel.startsWith('#')) {
    throw new Error('Channel must start with #');
  }
  if (text.length > 4000) {
    throw new Error('Message too long');
  }

  const result = await composio.tools.execute('SLACK_SEND_MESSAGE', {
    userId,
    arguments: { channel, text },
    version: '10082025_01',
  });

  return result;
}
```

---

### 2.3. Tool Version Management

<a name="tool-version-management"></a>

**Impact:** 🟠 HIGH

> Critical strategies for version pinning to ensure workflow stability and prevent runtime errors in production

# Tool Version Management

> **⚠️ CRITICAL:** Never assume or make up version numbers. Always use `composio.toolkits.get('toolkit_name')` to fetch available versions, or check the [dashboard](https://platform.composio.dev) to view versions and changes. Using non-existent versions will cause runtime errors.

Tool versions are critical for workflow stability. When manually executing tools, a specific version is **required** to prevent argument mismatches when tool schemas change.

## Why Version Pinning Matters

- **Tool schemas evolve**: Tool argument schemas can change between versions
- **Prevent runtime errors**: Using `'latest'` in workflows causes errors when tools update
- **Workflow stability**: Pinned versions ensure predictable behavior
- **Production safety**: Version validation prevents schema mismatch issues

## Three Version Management Strategies

### Strategy 1: Explicit Version in Execute Call (Recommended for One-off Executions)

Specify the version directly in the execute call:

```typescript
const result = await composio.tools.execute('GITHUB_GET_ISSUES', {
  userId: 'default',
  arguments: { owner: 'composio', repo: 'sdk' },
  version: '12082025_00', // Explicit version for this tool
});
```

**Pros:**
- Clear version visibility at execution point
- Different versions for different tools
- Easy to update individual tool versions

**Cons:**
- Repetitive if executing same tool multiple times
- Version scattered across codebase

**Use when:**
- One-off tool executions
- Testing different tool versions
- Tool versions need to differ within the same app

### Strategy 2: Configure Toolkit Versions at Initialization (Recommended for Production)

Configure versions once at SDK initialization:

```typescript
const composio = new Composio({
  toolkitVersions: {
    github: '12082025_00',
    slack: '10082025_01',
    gmail: '15082025_02'
  }
});

// Execute without version parameter - uses pinned version from config
const result = await composio.tools.execute('GITHUB_GET_ISSUES', {
  userId: 'default',
  arguments: { owner: 'composio', repo: 'sdk' },
  // Uses github: '12082025_00' from initialization
});
```

**Pros:**
- Centralized version management
- Clean execution calls
- Easy to update all tools from a toolkit
- Best for production environments

**Cons:**
- All tools from a toolkit use the same version
- Requires initialization configuration

**Use when:**
- Building production applications
- Managing multiple tools from the same toolkit
- Want centralized version control

### Strategy 3: dangerouslySkipVersionCheck (NOT Recommended for Production)

Bypass version validation entirely:

```typescript
const result = await composio.tools.execute('GITHUB_GET_ISSUES', {
  userId: 'default',
  arguments: { owner: 'composio', repo: 'sdk' },
  dangerouslySkipVersionCheck: true, // Uses 'latest' version
});
```

**⚠️ Warning:** This bypasses version validation and uses `'latest'` version. Can lead to:
- Unexpected behavior when tool schemas change
- Argument mismatches in production
- Runtime errors when tools are updated
- Workflow breakage without notice

**Only use for:**
- Development and testing
- Prototyping
- When you explicitly want to test latest versions

**NEVER use in:**
- Production environments
- Critical workflows
- User-facing applications

## Version Format

Versions follow the format: `DDMMYYYY_XX`

Examples:
- `12082025_00` - August 12, 2025, revision 00
- `10082025_01` - August 10, 2025, revision 01
- `15082025_02` - August 15, 2025, revision 02

## Finding Available Versions

**⚠️ CRITICAL: Never assume or guess version numbers. Always verify that a version exists before using it.**

### Method 1: Use SDK to List Available Versions

Fetch toolkit metadata to see all available versions:

```typescript
// Get available versions for a specific toolkit
const toolkit = await composio.toolkits.get('github');
console.log('Available versions:', toolkit.versions);
console.log('Latest version:', toolkit.latestVersion);

// For Gmail
const gmailToolkit = await composio.toolkits.get('gmail');
console.log('Gmail versions:', gmailToolkit.versions);

// For Slack
const slackToolkit = await composio.toolkits.get('slack');
console.log('Slack versions:', slackToolkit.versions);
```

### Method 2: Check Dashboard

View versions and changelog on the [Composio dashboard](https://platform.composio.dev):
- Navigate to Toolkits section
- Select the specific toolkit (e.g., GitHub, Gmail, Slack)
- View available versions and their changes

### How to Use Versions Correctly

Once you've found available versions, choose a specific version to test, then pin it in your configuration:

**Step 1: List available versions**
```typescript
const githubToolkit = await composio.toolkits.get('github');
console.log('Available versions:', githubToolkit.versions);
// Example output: ['12082025_00', '10082025_01', '08082025_00']
```

**Step 2: Choose and test a specific version**
```typescript
// Test with a specific version from the list
const composio = new Composio({
  toolkitVersions: {
    github: '12082025_00', // Choose a specific version to test
  }
});
```

**Step 3: Pin the tested version in production**
```typescript
// After testing, pin the version in your production config
const composio = new Composio({
  toolkitVersions: {
    github: '12082025_00',  // Pinned version that you've tested
    slack: '10082025_01',   // Pinned version that you've tested
  }
});
```

### Using Environment Variables

You can also set toolkit versions using environment variables:

```bash
# Set specific versions for individual toolkits
export COMPOSIO_TOOLKIT_VERSION_GITHUB=12082025_00
export COMPOSIO_TOOLKIT_VERSION_SLACK=10082025_01
export COMPOSIO_TOOLKIT_VERSION_GMAIL=15082025_00
```

Then initialize Composio without specifying `toolkitVersions`:

```typescript
const composio = new Composio({
  apiKey: 'your-api-key'
  // Will automatically use environment variables
});
```

### IMPORTANT: Don't Auto-Use Latest Version

❌ **DON'T DO THIS:**
```typescript
// This defeats the purpose of version pinning!
const githubToolkit = await composio.toolkits.get('github');
const composio = new Composio({
  toolkitVersions: {
    github: githubToolkit.latestVersion, // Always uses latest - no pinning!
  }
});

// Never use made-up version numbers either!
const composio = new Composio({
  toolkitVersions: {
    github: '01012025_00', // Random version - might not exist!
    slack: '25122024_99',  // Made up version - will fail!
  }
});
```

✅ **DO THIS:**
```typescript
// 1. List available versions to find valid options
const githubToolkit = await composio.toolkits.get('github');
console.log('Available versions:', githubToolkit.versions);

// 2. Choose and test a specific version from the list
// 3. Pin that tested version in your code or environment variables
const composio = new Composio({
  toolkitVersions: {
    github: '12082025_00',  // Specific tested version
    slack: '10082025_01',   // Specific tested version
  }
});
```

**Why this matters:**
- Automatically using `latestVersion` means your app always uses the newest version, defeating the purpose of pinning
- Version pinning is about locking to a specific, tested version for stability
- When you're ready to upgrade, you explicitly choose and test a new version before deploying

## Version Migration Strategy

When updating tool versions:

1. **Test in development first**
   ```typescript
   // Dev environment
   const devComposio = new Composio({
     toolkitVersions: { github: '20082025_00' } // New version
   });
   ```

2. **Validate schema changes**
   ```typescript
   const oldTool = await composio.tools.get('default', 'GITHUB_GET_ISSUES');
   const newTool = await composio.tools.get('default', 'GITHUB_GET_ISSUES');
   // Compare schemas before migrating
   ```

3. **Update gradually**
   - Update one toolkit at a time
   - Monitor for errors
   - Roll back if issues occur

4. **Update production**
   ```typescript
   // Production environment
   const prodComposio = new Composio({
     toolkitVersions: { github: '20082025_00' } // Deploy new version
   });
   ```

## Best Practices

1. **Always pin versions in production**: Never use `'latest'` or skip version checks
2. **Use initialization-level config**: Centralize version management for maintainability
3. **Document version choices**: Comment why specific versions are used
4. **Test version updates**: Validate in dev before deploying to production
5. **Monitor after updates**: Watch for errors after version changes
6. **Keep versions consistent**: Use same version across environments when possible
7. **Version control your config**: Track toolkit versions in your repository

## Common Patterns

### Environment-based version config

```typescript
const toolkitVersions = {
  development: {
    github: '12082025_00',
    slack: '10082025_01',
  },
  production: {
    github: '10082025_00', // Older stable version
    slack: '08082025_00',
  }
};

const composio = new Composio({
  toolkitVersions: toolkitVersions[process.env.NODE_ENV]
});
```

### Override version for specific execution

```typescript
// Use global config version by default
const composio = new Composio({
  toolkitVersions: { github: '12082025_00' }
});

// Override for specific execution
const result = await composio.tools.execute('GITHUB_GET_ISSUES', {
  userId: 'default',
  arguments: { owner: 'composio', repo: 'sdk' },
  version: '15082025_00', // Override global version
});
```

### Version validation helper

```typescript
function validateToolVersion(version: string): boolean {
  // Check format: DDMMYYYY_XX
  const versionRegex = /^\d{8}_\d{2}$/;
  return versionRegex.test(version);
}

const version = '12082025_00';
if (!validateToolVersion(version)) {
  throw new Error('Invalid version format');
}
```

---

### 2.4. Connected Accounts CRUD

<a name="connected-accounts-crud"></a>

**Impact:** 🟠 HIGH

> Comprehensive guide to CRUD operations on connected accounts with emphasis on secure authentication flows

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

---

### 2.5. Auth Config Management

<a name="auth-config-management"></a>

**Impact:** 🟡 MEDIUM

> Advanced programmatic management of authentication configurations for multi-tenant applications

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

---

### 2.6. Toolkit Management

<a name="toolkit-management"></a>

**Impact:** 🟡 MEDIUM

> Discover and query toolkits, categories, and authentication requirements for application integration

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

---

### 2.7. Creating Custom Tools

<a name="creating-custom-tools"></a>

**Impact:** 🟡 MEDIUM

> Build standalone and toolkit-based custom tools with proper authentication and validation

# Creating Custom Tools

Create your own tools that integrate with Composio:
- **Standalone tools** - No external authentication required
- **Toolkit-based tools** - Use toolkit credentials for API requests

## Standalone Tools

For tools that don't need external authentication:

```typescript
import { z } from 'zod';

const tool = await composio.tools.createCustomTool({
  slug: 'CALCULATE_SQUARE',
  name: 'Calculate Square',
  description: 'Calculates the square of a number',
  inputParams: z.object({
    number: z.number().describe('The number to calculate the square of'),
  }),
  execute: async (input) => {
    return {
      data: { result: input.number * input.number },
      error: null,
      successful: true,
    };
  },
});
```

**Use for:** Math, string operations, data transformations, internal logic.

## Toolkit-Based Tools

For tools that call authenticated APIs.

### Using executeToolRequest (Recommended)

Automatically handles authentication and baseURL:

```typescript
const tool = await composio.tools.createCustomTool({
  slug: 'GITHUB_STAR_REPOSITORY',
  name: 'Star GitHub Repository',
  toolkitSlug: 'github',
  description: 'Star a repository under composiohq',
  inputParams: z.object({
    repository: z.string().describe('Repository name'),
    page: z.number().optional().describe('Page number'),
  }),
  execute: async (input, connectionConfig, executeToolRequest) => {
    return await executeToolRequest({
      endpoint: `/user/starred/composiohq/${input.repository}`,
      method: 'PUT',
      parameters: [
        {
          name: 'page',
          value: input.page?.toString() || '1',
          in: 'query', // Adds ?page=1
        },
      ],
    });
  },
});
```

### Using connectionConfig (Direct API Calls)

For custom HTTP requests:

```typescript
const tool = await composio.tools.createCustomTool({
  slug: 'GITHUB_DIRECT_API',
  name: 'Direct GitHub API',
  toolkitSlug: 'github',
  inputParams: z.object({
    repo: z.string().describe('Repository name'),
  }),
  execute: async (input, connectionConfig) => {
    const response = await fetch(`https://api.github.com/repos/${input.repo}`, {
      headers: {
        Authorization: `Bearer ${connectionConfig.val?.access_token}`,
      },
    });

    const data = await response.json();

    return {
      data: data,
      error: response.ok ? null : 'API request failed',
      successful: response.ok,
    };
  },
});
```

## Input Validation with Zod

Define and validate parameters using Zod:

```typescript
inputParams: z.object({
  // Required string
  name: z.string().describe('User name'),

  // Optional with default
  count: z.number().optional().default(10).describe('Number of items'),

  // With validation
  email: z.string().email().describe('Email address'),

  // Enum
  status: z.enum(['active', 'inactive']).describe('Status'),

  // Array
  tags: z.array(z.string()).describe('Tags'),

  // Nested object
  metadata: z.object({
    key: z.string(),
    value: z.string(),
  }).optional().describe('Metadata'),
})
```

**Always use `.describe()`** - helps AI understand parameter purpose.

## Headers and Query Parameters

Add headers and query params via `parameters` array:

```typescript
execute: async (input, connectionConfig, executeToolRequest) => {
  return await executeToolRequest({
    endpoint: '/search/repositories',
    method: 'GET',
    parameters: [
      // Query parameters
      {
        name: 'q',
        value: input.query,
        in: 'query', // ?q=value
      },
      // Headers
      {
        name: 'Accept',
        value: 'application/vnd.github.v3+json',
        in: 'header',
      },
    ],
  });
}
```

## Executing Custom Tools

```typescript
// Standalone tool
await composio.tools.execute('CALCULATE_SQUARE', {
  userId: 'default',
  arguments: { number: 5 },
});

// Toolkit-based tool (uses userId to find account)
await composio.tools.execute('GITHUB_STAR_REPOSITORY', {
  userId: 'user_123',
  arguments: { repository: 'composio' },
});

// With explicit connected account
await composio.tools.execute('GITHUB_STAR_REPOSITORY', {
  userId: 'user_123',
  connectedAccountId: 'conn_abc123',
  arguments: { repository: 'composio' },
});
```

## Error Handling

Always return structured responses:

```typescript
execute: async (input) => {
  try {
    const result = performOperation(input);
    return {
      data: result,
      error: null,
      successful: true,
    };
  } catch (error) {
    return {
      data: null,
      error: error.message,
      successful: false,
    };
  }
}
```

## Key Points

- **Naming:** Use `TOOLKIT_ACTION_DESCRIPTION` format for slugs
- **Prefer executeToolRequest:** Handles auth and baseURL automatically
- **Describe parameters:** AI agents need clear descriptions
- **Not persisted:** Custom tools exist in memory only, recreate on restart
- **Single toolkit scope:** executeToolRequest only works within same toolkit

---

### 2.8. Tool Modifiers

<a name="tool-modifiers"></a>

**Impact:** 🟡 MEDIUM

> Advanced patterns for customizing tool behavior with schema modifications and execution hooks

# Tool Modifiers

Modifiers customize tool behavior through schema transformations, pre-execution hooks, and post-execution hooks.

## Schema Modification

Customize tool descriptions or parameters at fetch time:

```typescript
const tools = await composio.tools.get(
  'default',
  { toolkits: ['github'] },
  {
    modifySchema: ({ toolSlug, toolkitSlug, schema }) => {
      // Enhance descriptions for AI
      schema.description = `[Enhanced] ${schema.description}`;

      // Customize specific parameters
      if (toolSlug === 'GITHUB_GET_REPO') {
        schema.inputParameters.properties.owner.description =
          'GitHub organization or user name (e.g., "composio")';
      }

      return schema;
    },
  }
);
```

## Pre-Execution Hooks (beforeExecute)

Modify parameters before execution:

```typescript
const result = await composio.tools.execute(
  'GITHUB_GET_REPO',
  {
    userId: 'default',
    arguments: { owner: 'Composio', repo: 'sdk' },
  },
  {
    beforeExecute: ({ toolSlug, params }) => {
      // Normalize inputs
      params.arguments.owner = params.arguments.owner.toLowerCase();

      // Add defaults
      params.arguments.branch = params.arguments.branch || 'main';

      return params;
    },
  }
);
```

**Common uses:**
- Parameter validation and normalization
- Adding default values
- Logging and tracing

## Post-Execution Hooks (afterExecute)

Transform outputs after execution:

```typescript
const result = await composio.tools.execute(
  'GITHUB_GET_REPO',
  {
    userId: 'default',
    arguments: { owner: 'composio', repo: 'sdk' },
  },
  {
    afterExecute: ({ result }) => {
      if (result.successful) {
        // Remove sensitive data
        delete result.data.token;

        // Add metadata
        result.data.fetchedAt = new Date().toISOString();
      }

      return result;
    },
  }
);
```

**Common uses:**
- Filtering sensitive data
- Data transformation and formatting
- Adding metadata

## Common Patterns

### Sensitive Data Filtering

```typescript
const filterSensitive = ({ result }) => {
  if (result.successful) {
    ['token', 'secret', 'password', 'api_key'].forEach(field => {
      delete result.data[field];
    });
  }
  return result;
};
```

### Logging & Monitoring

```typescript
const monitor = {
  beforeExecute: ({ toolSlug, params }) => {
    console.log(`[START] ${toolSlug}`, params.arguments);
    return params;
  },
  afterExecute: ({ toolSlug, result }) => {
    console.log(`[END] ${toolSlug} - Success: ${result.successful}`);
    return result;
  },
};
```

### Reusable Modifiers

```typescript
const addTimestamps = ({ result }) => {
  if (result.successful) result.data.executedAt = new Date().toISOString();
  return result;
};

// Use in multiple executions
await composio.tools.execute('GITHUB_GET_REPO', { ... }, {
  afterExecute: addTimestamps
});
```

## Key Points

- Schema modifiers apply at fetch time, execution modifiers at runtime
- Always return modified object (don't just mutate)
- Modifiers are synchronous - keep operations lightweight
- Must pass modifiers to each execute() call (not persisted)

---

### 2.9. Creating Triggers

<a name="creating-triggers"></a>

**Impact:** 🟠 HIGH

> Set up trigger instances to receive real-time events from connected accounts

# Create Triggers for Real-Time Events

Triggers receive real-time events from connected accounts (Gmail, GitHub, Slack, etc.). Create trigger instances to subscribe to specific events.

## Basic Usage

```typescript
import { Composio } from '@composio/core';

const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });

// Create trigger for specific connected account
const trigger = await composio.triggers.create(
  'user_123',
  'GMAIL_NEW_GMAIL_MESSAGE',
  {
    connectedAccountId: 'conn_abc123',
    triggerConfig: {
      labelIds: 'INBOX',
      userId: 'me',
      interval: 60
    }
  }
);

console.log('Trigger ID:', trigger.triggerId);
```

## SDK Auto-Discovery

Omit `connectedAccountId` to let SDK find the account automatically:

```typescript
// SDK finds user's Gmail connection
const trigger = await composio.triggers.create(
  'user_123',
  'GMAIL_NEW_GMAIL_MESSAGE',
  {
    triggerConfig: { labelIds: 'INBOX', interval: 60 }
  }
);
```

## Automatic Reuse

Triggers with identical configuration are automatically reused:

```typescript
// First call creates trigger
const trigger1 = await composio.triggers.create(
  'user_123',
  'GMAIL_NEW_GMAIL_MESSAGE',
  { triggerConfig: { labelIds: 'INBOX' } }
);

// Second call returns same trigger (no duplicate)
const trigger2 = await composio.triggers.create(
  'user_123',
  'GMAIL_NEW_GMAIL_MESSAGE',
  { triggerConfig: { labelIds: 'INBOX' } }
);

console.log(trigger1.triggerId === trigger2.triggerId); // true
```

## Version Pinning

Pin trigger versions in production to prevent breaking changes:

```typescript
const composio = new Composio({
  apiKey: process.env.COMPOSIO_API_KEY,
  triggerVersions: {
    'GMAIL_NEW_GMAIL_MESSAGE': '12082025_00',
    'GITHUB_COMMIT_EVENT': '12082025_00'
  }
});

// Uses pinned version
const trigger = await composio.triggers.create(
  'user_123',
  'GMAIL_NEW_GMAIL_MESSAGE',
  { triggerConfig: { labelIds: 'INBOX' } }
);
```

**Why pin versions:**
- Prevents config schema changes
- Ensures production stability
- Updates on your schedule

## Trigger Configuration Examples

```typescript
// Gmail - New messages in specific label
await composio.triggers.create('user_123', 'GMAIL_NEW_GMAIL_MESSAGE', {
  triggerConfig: {
    labelIds: 'INBOX',
    userId: 'me',
    interval: 60
  }
});

// GitHub - New commits
await composio.triggers.create('user_123', 'GITHUB_COMMIT_EVENT', {
  triggerConfig: {
    owner: 'composio',
    repo: 'sdk',
    branch: 'main'
  }
});

// Slack - New messages in channel
await composio.triggers.create('user_123', 'SLACK_NEW_MESSAGE', {
  triggerConfig: {
    channelId: 'C123456',
    botUserId: 'U123456'
  }
});
```

## Error Handling

```typescript
try {
  const trigger = await composio.triggers.create(
    'user_123',
    'GMAIL_NEW_GMAIL_MESSAGE',
    { triggerConfig: { labelIds: 'INBOX' } }
  );
} catch (error) {
  if (error.name === 'ComposioConnectedAccountNotFoundError') {
    // User hasn't connected Gmail yet
    console.log('Please connect your Gmail account');
  } else if (error.name === 'ValidationError') {
    // Invalid trigger config
    console.error('Invalid configuration:', error.message);
  } else {
    throw error;
  }
}
```

## Discover Available Triggers

```typescript
// Get all triggers
const triggers = await composio.triggers.list();

// Search by keyword
const emailTriggers = await composio.triggers.list({ search: 'email' });

// Filter by toolkit
const slackTriggers = await composio.triggers.list({ toolkit: 'slack' });

// Get trigger details
const trigger = await composio.triggers.getTrigger('GMAIL_NEW_GMAIL_MESSAGE');
console.log(trigger.config); // Shows required config fields
```

## List Active Triggers

```typescript
// All active triggers
const active = await composio.triggers.getActiveTriggers();

// By trigger slug
const gmailTriggers = await composio.triggers.getActiveTriggers({
  triggerSlugs: ['GMAIL_NEW_GMAIL_MESSAGE']
});

// By connected account
const accountTriggers = await composio.triggers.getActiveTriggers({
  connectedAccountIds: ['conn_abc123']
});

// Combine filters
const userSlackTriggers = await composio.triggers.getActiveTriggers({
  triggerSlugs: ['SLACK_NEW_MESSAGE'],
  connectedAccountIds: ['conn_def456']
});
```

## Common Patterns

### Check Before Creating

```typescript
async function ensureTrigger(userId: string, triggerSlug: string, config: any) {
  // Check if trigger exists
  const existing = await composio.triggers.getActiveTriggers({
    triggerSlugs: [triggerSlug]
  });

  if (existing.items.length > 0) {
    return existing.items[0];
  }

  // Create if doesn't exist
  return await composio.triggers.create(userId, triggerSlug, {
    triggerConfig: config
  });
}
```

### Onboarding Flow

```typescript
async function setupUserTriggers(userId: string) {
  // Check connected accounts
  const accounts = await composio.connectedAccounts.list({
    userIds: [userId]
  });

  // Create triggers for each service
  for (const account of accounts.items) {
    if (account.toolkit.slug === 'gmail') {
      await composio.triggers.create(userId, 'GMAIL_NEW_GMAIL_MESSAGE', {
        connectedAccountId: account.id,
        triggerConfig: { labelIds: 'INBOX' }
      });
    }
  }
}
```

## Key Points

- **Use proper user IDs** - Never use 'default' in production
- **Requires connected account** - User must authenticate first
- **Automatic reuse** - Identical configs share same trigger instance
- **Pin versions** - Prevents breaking changes in production
- **Error handling** - Handle missing connections gracefully

---

### 2.10. Subscribing to Events

<a name="subscribing-to-events"></a>

**Impact:** 🟡 MEDIUM

> Listen to real-time trigger events during development using subscribe()

# Subscribe to Trigger Events

Use `subscribe()` to listen to trigger events in **development only**. For production, use webhooks via `listenToTriggers()`.

## Development vs Production

**Development (subscribe):**
- Real-time event listening in CLI/local development
- Simple callback function
- No webhook URLs needed
- **Do NOT use in production**

**Production (webhooks):**
- Scalable webhook delivery
- Reliable event processing
- Use `listenToTriggers()` with Express/HTTP server
- See triggers-webhook.md

## Basic Subscribe

```typescript
import { Composio } from '@composio/core';

const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });

// Subscribe to trigger events
const unsubscribe = await composio.triggers.subscribe((event) => {
  console.log('Trigger received:', event.triggerSlug);
  console.log('Payload:', event.payload);
  console.log('User:', event.userId);
  console.log('Account:', event.connectedAccountId);
});

// Keep process alive
console.log('Listening for events... Press Ctrl+C to stop');
```

## Subscribe with Filters

```typescript
// Filter by trigger slug
await composio.triggers.subscribe(
  (event) => {
    console.log('Gmail message:', event.payload);
  },
  { triggerSlugs: ['GMAIL_NEW_GMAIL_MESSAGE'] }
);

// Filter by user ID
await composio.triggers.subscribe(
  (event) => {
    console.log('Event for user_123:', event.payload);
  },
  { userIds: ['user_123'] }
);

// Filter by connected account
await composio.triggers.subscribe(
  (event) => {
    console.log('Event from specific account:', event.payload);
  },
  { connectedAccountIds: ['conn_abc123'] }
);

// Combine filters
await composio.triggers.subscribe(
  (event) => {
    console.log('Filtered event:', event.payload);
  },
  {
    triggerSlugs: ['SLACK_NEW_MESSAGE'],
    userIds: ['user_123'],
    connectedAccountIds: ['conn_def456']
  }
);
```

## Event Payload Structure

```typescript
interface TriggerEvent {
  triggerSlug: string;           // 'GMAIL_NEW_GMAIL_MESSAGE'
  userId: string;                // 'user_123'
  connectedAccountId: string;    // 'conn_abc123'
  payload: {
    // Trigger-specific data
    // Example for Gmail:
    // { id: 'msg_123', subject: 'Hello', from: 'user@example.com' }
  };
  metadata: {
    triggerId: string;
    timestamp: string;
  };
}
```

## Unsubscribe

```typescript
const unsubscribe = await composio.triggers.subscribe((event) => {
  console.log('Event:', event);
});

// Stop listening
await unsubscribe();
console.log('Unsubscribed from all triggers');
```

## Development Pattern

```typescript
async function devMode() {
  console.log('Starting development mode...');

  // Subscribe to events
  const unsubscribe = await composio.triggers.subscribe((event) => {
    console.log(`\n[${event.triggerSlug}]`);
    console.log('User:', event.userId);
    console.log('Payload:', JSON.stringify(event.payload, null, 2));
  });

  // Handle shutdown
  process.on('SIGINT', async () => {
    console.log('\nShutting down...');
    await unsubscribe();
    process.exit(0);
  });

  console.log('Listening for events. Press Ctrl+C to stop.');
}

devMode();
```

## Migration to Production

Development (subscribe):
```typescript
// Development only
await composio.triggers.subscribe((event) => {
  console.log(event);
});
```

Production (webhooks):
```typescript
// Production ready
import express from 'express';

const app = express();
const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });

await composio.triggers.listenToTriggers(app, (event) => {
  console.log('Webhook received:', event);
});

app.listen(3000);
```

## Key Points

- **Development only** - Never use subscribe() in production
- **Use webhooks for production** - More reliable and scalable
- **Filter events** - Reduce noise with triggerSlugs, userIds, connectedAccountIds
- **Cleanup** - Always call unsubscribe() when done
- **Long-running process** - Keep Node.js process alive to receive events

---

### 2.11. Webhook Verification

<a name="webhook-verification"></a>

**Impact:** 🔴 CRITICAL

> Use webhook verification for reliable, scalable event delivery in production

# Webhook Verification for Production

Webhooks are the **production-ready** way to receive trigger events. Provides reliable delivery, automatic retries, and works with serverless.

## Setup with listenToTriggers()

```typescript
import express from 'express';
import { Composio } from '@composio/core';

const app = express();
const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });

// Automatic webhook verification and handling
await composio.triggers.listenToTriggers(app, async (event) => {
  console.log('Webhook:', event.triggerSlug);
  console.log('User:', event.userId);
  console.log('Payload:', event.payload);

  await handleEvent(event);
});

app.listen(3000);
```

**What it does:**
- Creates `/composio/triggers` endpoint
- Verifies webhook signatures automatically
- Parses and validates payloads
- Calls callback with verified events

## Manual Verification

For custom endpoints:

```typescript
import { verifyWebhookSignature } from '@composio/core';

app.post('/custom/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  const signature = req.headers['x-composio-signature'];
  const payload = req.body;

  const isValid = verifyWebhookSignature(
    payload,
    signature,
    process.env.COMPOSIO_WEBHOOK_SECRET
  );

  if (!isValid) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  const event = JSON.parse(payload);
  handleEvent(event);
  res.json({ success: true });
});
```

## Event Structure

```typescript
interface WebhookEvent {
  triggerSlug: string;
  userId: string;
  connectedAccountId: string;
  payload: object;
  metadata: {
    triggerId: string;
    timestamp: string;
    webhookId: string;
  };
}
```

## Processing Patterns

### Route by Trigger Type

```typescript
async function handleEvent(event: WebhookEvent) {
  switch (event.triggerSlug) {
    case 'GMAIL_NEW_GMAIL_MESSAGE':
      await handleGmail(event.userId, event.payload);
      break;
    case 'GITHUB_COMMIT_EVENT':
      await handleGithub(event.userId, event.payload);
      break;
    case 'SLACK_NEW_MESSAGE':
      await handleSlack(event.userId, event.payload);
      break;
  }
}
```

### With Error Handling

```typescript
await composio.triggers.listenToTriggers(app, async (event) => {
  try {
    await processEvent(event);
  } catch (error) {
    console.error('Error:', error);
    // Don't throw - acknowledge webhook received
  }
});
```

### With Idempotency

```typescript
await composio.triggers.listenToTriggers(app, async (event) => {
  const webhookId = event.metadata.webhookId;

  // Check if already processed
  if (await isProcessed(webhookId)) {
    console.log('Duplicate webhook, skipping');
    return;
  }

  // Mark as processed
  await markProcessed(webhookId);

  // Process event
  await handleEvent(event);
});
```

## Configuration

Set webhook URL in Composio dashboard:

1. Go to [platform.composio.dev](https://platform.composio.dev)
2. **Settings** > **Webhooks**
3. Set URL: `https://your-app.com/composio/triggers`

**Requirements:**
- HTTPS URL (publicly accessible)
- Respond with 200 OK within 30 seconds
- Handle concurrent requests

## Testing Locally

Use ngrok:

```bash
ngrok http 3000
# Use https://abc123.ngrok.io/composio/triggers in dashboard
```

## Security

- **Always verify signatures** - Use `listenToTriggers()` or manual verification
- **HTTPS only** - Never HTTP in production
- **Keep secrets secure** - Environment variables only
- **Validate payloads** - Check required fields
- **Handle errors gracefully** - Log, don't throw
- **Implement idempotency** - Use webhookId to deduplicate

## Common Issues

**401 Unauthorized:**
- Invalid signature - check webhook secret
- Wrong secret - verify environment variable

**Timeout:**
- Processing > 30 seconds - move to background queue
- Return 200 OK immediately

**Duplicates:**
- Webhooks may deliver multiple times
- Use webhookId for idempotency

## Complete Example

```typescript
import express from 'express';
import { Composio } from '@composio/core';

const app = express();
const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });

await composio.triggers.listenToTriggers(app, async (event) => {
  try {
    // Idempotency check
    if (await isProcessed(event.metadata.webhookId)) {
      return;
    }

    // Process
    switch (event.triggerSlug) {
      case 'GMAIL_NEW_GMAIL_MESSAGE':
        await sendNotification(event.userId, {
          title: 'New Email',
          body: event.payload.subject
        });
        break;
    }

    // Mark processed
    await markProcessed(event.metadata.webhookId);
  } catch (error) {
    console.error('Error:', error);
  }
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

## Key Points

- **Production standard** - Use webhooks, not subscribe()
- **listenToTriggers()** - Handles verification automatically
- **HTTPS required** - Security requirement
- **Quick response** - Return 200 OK within 30s
- **Idempotency** - Handle duplicates with webhookId
- **Error handling** - Log but don't throw

---

### 2.12. Managing Triggers

<a name="managing-triggers"></a>

**Impact:** 🟠 HIGH

> Control trigger states, update configurations, and manage trigger instances

# Manage Trigger Lifecycle

Control trigger states and configurations without recreating triggers.

## Enable/Disable Triggers

```typescript
// Disable trigger (stop receiving events)
await composio.triggers.disable('trigger_id_123');

// Enable trigger (resume receiving events)
await composio.triggers.enable('trigger_id_123');
```

**Use cases:**
- **Disable:** Pause events temporarily, user disconnects account, billing issues
- **Enable:** Resume after resolving issues, user reconnects account

## Update Trigger Configuration

```typescript
// Update trigger config
await composio.triggers.update('trigger_id_123', {
  triggerConfig: {
    labelIds: 'SENT', // Changed from 'INBOX'
    interval: 120     // Changed from 60
  }
});
```

**Updateable fields:**
- `triggerConfig` - Trigger-specific configuration
- Cannot change trigger slug or connected account

## Delete Triggers

```typescript
await composio.triggers.delete('trigger_id_123');
```

**Warning:** Permanent deletion. Creates new trigger if needed later.

## List Active Triggers

```typescript
// All active triggers
const triggers = await composio.triggers.getActiveTriggers();

// By trigger slug
const gmailTriggers = await composio.triggers.getActiveTriggers({
  triggerSlugs: ['GMAIL_NEW_GMAIL_MESSAGE']
});

// By user
const userTriggers = await composio.triggers.getActiveTriggers({
  userIds: ['user_123']
});

// By connected account
const accountTriggers = await composio.triggers.getActiveTriggers({
  connectedAccountIds: ['conn_abc123']
});

// By status
const enabled = await composio.triggers.getActiveTriggers({
  status: 'enabled'
});
const disabled = await composio.triggers.getActiveTriggers({
  status: 'disabled'
});

// Combine filters
const filtered = await composio.triggers.getActiveTriggers({
  triggerSlugs: ['SLACK_NEW_MESSAGE'],
  userIds: ['user_123'],
  status: 'enabled'
});
```

**Response includes:**
- `triggerId` - Unique ID
- `triggerSlug` - Trigger type
- `userId` - User ID
- `connectedAccountId` - Account ID
- `status` - 'enabled' or 'disabled'
- `config` - Current configuration
- `createdAt`, `updatedAt` - Timestamps

## Get Trigger Details

```typescript
// Get specific trigger
const trigger = await composio.triggers.getTriggerById('trigger_id_123');

console.log(trigger.status);                // 'enabled'
console.log(trigger.triggerSlug);           // 'GMAIL_NEW_GMAIL_MESSAGE'
console.log(trigger.config.triggerConfig);  // { labelIds: 'INBOX', ... }
```

## Common Patterns

### Pause User's Triggers

```typescript
async function pauseUserTriggers(userId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId],
    status: 'enabled'
  });

  for (const trigger of triggers.items) {
    await composio.triggers.disable(trigger.triggerId);
  }
}
```

### Resume User's Triggers

```typescript
async function resumeUserTriggers(userId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId],
    status: 'disabled'
  });

  for (const trigger of triggers.items) {
    await composio.triggers.enable(trigger.triggerId);
  }
}
```

### Clean Up Disconnected Account Triggers

```typescript
async function cleanupTriggers(connectedAccountId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    connectedAccountIds: [connectedAccountId]
  });

  for (const trigger of triggers.items) {
    await composio.triggers.delete(trigger.triggerId);
  }
}
```

### Update All User Gmail Triggers

```typescript
async function updateGmailInterval(userId: string, newInterval: number) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId],
    triggerSlugs: ['GMAIL_NEW_GMAIL_MESSAGE']
  });

  for (const trigger of triggers.items) {
    await composio.triggers.update(trigger.triggerId, {
      triggerConfig: {
        ...trigger.config.triggerConfig,
        interval: newInterval
      }
    });
  }
}
```

### Check Trigger Status

```typescript
async function isTriggerActive(triggerId: string): Promise<boolean> {
  try {
    const trigger = await composio.triggers.getTriggerById(triggerId);
    return trigger.status === 'enabled';
  } catch (error) {
    return false; // Trigger doesn't exist
  }
}
```

### Get Trigger Count by User

```typescript
async function getUserTriggerCount(userId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId]
  });

  return {
    total: triggers.items.length,
    enabled: triggers.items.filter(t => t.status === 'enabled').length,
    disabled: triggers.items.filter(t => t.status === 'disabled').length
  };
}
```

## Lifecycle Management

### Account Disconnection

```typescript
// When user disconnects an account
async function handleAccountDisconnect(accountId: string) {
  // Option 1: Disable triggers (can resume later)
  const triggers = await composio.triggers.getActiveTriggers({
    connectedAccountIds: [accountId]
  });
  for (const trigger of triggers.items) {
    await composio.triggers.disable(trigger.triggerId);
  }

  // Option 2: Delete triggers (permanent)
  for (const trigger of triggers.items) {
    await composio.triggers.delete(trigger.triggerId);
  }
}
```

### Account Reconnection

```typescript
// When user reconnects
async function handleAccountReconnect(accountId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    connectedAccountIds: [accountId],
    status: 'disabled'
  });

  for (const trigger of triggers.items) {
    await composio.triggers.enable(trigger.triggerId);
  }
}
```

### Subscription Management

```typescript
// Downgrade: disable non-essential triggers
async function handleDowngrade(userId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId],
    triggerSlugs: ['NON_ESSENTIAL_TRIGGER']
  });

  for (const trigger of triggers.items) {
    await composio.triggers.disable(trigger.triggerId);
  }
}

// Upgrade: enable all triggers
async function handleUpgrade(userId: string) {
  const triggers = await composio.triggers.getActiveTriggers({
    userIds: [userId],
    status: 'disabled'
  });

  for (const trigger of triggers.items) {
    await composio.triggers.enable(trigger.triggerId);
  }
}
```

## Key Points

- **Disable vs Delete** - Disable pauses events, delete is permanent
- **Update config** - Change trigger settings without recreating
- **Filter getActiveTriggers** - Use multiple filters to narrow results
- **Batch operations** - Loop through triggers for bulk enable/disable
- **Handle disconnects** - Disable or delete triggers when accounts disconnect
- **Status check** - Always verify trigger status before operations

---

### 2.13. User ID Patterns

<a name="user-id-patterns"></a>

**Impact:** 🟠 HIGH

> Critical patterns for user identification, multi-tenancy, and data isolation in production applications

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

---

## Quick Start

Examples

## References

**Tool Router (Agents):**
- [Tool Router Docs](https://docs.composio.dev/sdk/typescript/api/tool-router)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Framework Integration Examples](https://github.com/composiohq/composio/tree/main/ts/examples/tool-router)

**Direct Execution (Apps):**
- [Tools API](https://docs.composio.dev/sdk/typescript/api/tools)
- [Connected Accounts API](https://docs.composio.dev/sdk/typescript/api/connected-accounts)
- [Auth Configs API](https://docs.composio.dev/sdk/typescript/api/auth-configs)
- [Toolkits API](https://docs.composio.dev/sdk/typescript/api/toolkits)
- [Custom Tools Guide](https://docs.composio.dev/sdk/typescript/api/custom-tools)
- [Modifiers](https://docs.composio.dev/sdk/typescript/advanced/modifiers)
- [Core Concepts](https://docs.composio.dev/sdk/typescript/core-concepts)

**Shared:**
- [Triggers API](https://docs.composio.dev/sdk/typescript/api/triggers)
- [Webhook Verification](https://docs.composio.dev/sdk/typescript/advanced/webhook-verification)


---

_This file was automatically generated from individual rule files on 2026-02-06T05:10:09.820Z_
_To update, run: `npm run build:agents`_
