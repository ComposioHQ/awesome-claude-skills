---
title: Manage Trigger Lifecycle (Enable, Disable, Update)
impact: HIGH
description: Control trigger states, update configurations, and manage trigger instances
tags: [triggers, lifecycle, enable, disable, update, management]
---

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
