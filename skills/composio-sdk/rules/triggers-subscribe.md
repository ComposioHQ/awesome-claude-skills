---
title: Subscribe to Trigger Events
impact: MEDIUM
description: Listen to real-time trigger events during development using subscribe()
tags: [triggers, events, subscribe, development, real-time]
---

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
