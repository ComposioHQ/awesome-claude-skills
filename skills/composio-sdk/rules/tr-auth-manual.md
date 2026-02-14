---
title: Use Manual Authorization for Explicit Control
impact: MEDIUM
description: Control authentication flows explicitly using session.authorize() for onboarding and settings pages
tags: [authentication, tool-router, authorization, oauth]
---

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
