---
title: Treat Sessions as Short-Lived and Disposable
impact: CRITICAL
description: Create new sessions frequently for better logging, debugging, and configuration management
tags: [tool-router, session, lifecycle, best-practices, logging]
---

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
