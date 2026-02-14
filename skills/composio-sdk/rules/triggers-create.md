---
title: Create Triggers for Real-Time Events
impact: HIGH
description: Set up trigger instances to receive real-time events from connected accounts
tags: [triggers, events, webhooks, real-time, notifications]
---

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
