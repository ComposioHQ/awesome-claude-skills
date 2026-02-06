---
title: Query Toolkit Connection States for UI
impact: MEDIUM
description: Use session.toolkits() to build connection management UIs showing which toolkits are connected
tags: [tool-router, toolkits, connections, ui]
---

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
