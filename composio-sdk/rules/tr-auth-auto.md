---
title: Enable Auto Authentication in Chat
impact: HIGH
description: Allow users to authenticate toolkits directly within chat conversations
tags: [authentication, tool-router, user-experience, oauth]
---

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
