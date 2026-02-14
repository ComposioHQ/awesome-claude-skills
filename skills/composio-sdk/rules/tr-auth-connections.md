---
title: Configure Connection Management Properly
impact: CRITICAL
description: Understand manageConnections settings to control authentication behavior in Tool Router
tags: [authentication, tool-router, connections, configuration]
---

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
