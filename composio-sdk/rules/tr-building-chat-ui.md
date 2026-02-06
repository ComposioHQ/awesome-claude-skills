---
title: Building Chat UIs with Tool Router
impact: HIGH
description: Best practices for building chat applications with toolkit selection, connection management, and session handling
tags: [tool-router, chat-ui, vercel-ai-sdk, toolkit-selection, authentication, session]
---

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
