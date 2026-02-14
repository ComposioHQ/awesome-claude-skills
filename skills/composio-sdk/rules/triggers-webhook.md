---
title: Verify Webhooks for Production (Recommended)
impact: CRITICAL
description: Use webhook verification for reliable, scalable event delivery in production
tags: [triggers, webhooks, production, security, verification, hmac]
---

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
