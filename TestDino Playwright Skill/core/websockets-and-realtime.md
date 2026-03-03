# WebSockets and Real-Time Testing

> **When to use**: When your application uses WebSockets, Server-Sent Events (SSE), or polling for real-time features -- chat, live dashboards, notifications, collaborative editing, stock tickers, live sports scores.
> **Prerequisites**: [core/assertions-and-waiting.md](assertions-and-waiting.md), [core/fixtures-and-hooks.md](fixtures-and-hooks.md)

## Quick Reference

```typescript
// Listen for WebSocket connections
page.on('websocket', (ws) => {
  console.log('WebSocket opened:', ws.url());

  ws.on('framesent', (frame) => console.log('Sent:', frame.payload));
  ws.on('framereceived', (frame) => console.log('Received:', frame.payload));
  ws.on('close', () => console.log('WebSocket closed'));
});

// Mock a WebSocket via route (Playwright 1.48+)
await page.routeWebSocket('**/ws', (ws) => {
  ws.onMessage((message) => {
    ws.send(JSON.stringify({ echo: message }));
  });
});
```

## Patterns

### Observing WebSocket Traffic

**Use when**: You need to verify that your app sends and receives the correct WebSocket messages without modifying them.
**Avoid when**: You need to intercept or mock the messages. Use `routeWebSocket` instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('chat message is sent over WebSocket', async ({ page }) => {
  const messages: { direction: string; payload: string }[] = [];

  page.on('websocket', (ws) => {
    ws.on('framesent', (frame) => {
      messages.push({ direction: 'sent', payload: String(frame.payload) });
    });
    ws.on('framereceived', (frame) => {
      messages.push({ direction: 'received', payload: String(frame.payload) });
    });
  });

  await page.goto('/chat');
  await page.getByRole('textbox', { name: 'Message' }).fill('Hello!');
  await page.getByRole('button', { name: 'Send' }).click();

  // Wait for the message to appear in UI (confirms round-trip)
  await expect(page.getByText('Hello!')).toBeVisible();

  // Verify WebSocket traffic
  const sentMessage = messages.find(
    (m) => m.direction === 'sent' && m.payload.includes('Hello!')
  );
  expect(sentMessage).toBeDefined();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('chat message is sent over WebSocket', async ({ page }) => {
  const messages = [];

  page.on('websocket', (ws) => {
    ws.on('framesent', (frame) => {
      messages.push({ direction: 'sent', payload: String(frame.payload) });
    });
    ws.on('framereceived', (frame) => {
      messages.push({ direction: 'received', payload: String(frame.payload) });
    });
  });

  await page.goto('/chat');
  await page.getByRole('textbox', { name: 'Message' }).fill('Hello!');
  await page.getByRole('button', { name: 'Send' }).click();

  await expect(page.getByText('Hello!')).toBeVisible();

  const sentMessage = messages.find(
    (m) => m.direction === 'sent' && m.payload.includes('Hello!')
  );
  expect(sentMessage).toBeDefined();
});
```

### Waiting for a Specific WebSocket Message

**Use when**: Your test depends on a particular server-pushed message before proceeding.
**Avoid when**: The UI already reflects the message. Assert on the UI instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('wait for server acknowledgment over WebSocket', async ({ page }) => {
  // Create a promise that resolves when we get the specific message
  const ackPromise = new Promise<void>((resolve) => {
    page.on('websocket', (ws) => {
      ws.on('framereceived', (frame) => {
        const data = JSON.parse(String(frame.payload));
        if (data.type === 'message_ack') {
          resolve();
        }
      });
    });
  });

  await page.goto('/chat');
  await page.getByRole('textbox', { name: 'Message' }).fill('Important update');
  await page.getByRole('button', { name: 'Send' }).click();

  // Wait for server to acknowledge
  await ackPromise;

  // Now verify the message shows a "delivered" checkmark
  await expect(page.getByTestId('message-status').last()).toHaveText('Delivered');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('wait for server acknowledgment over WebSocket', async ({ page }) => {
  const ackPromise = new Promise((resolve) => {
    page.on('websocket', (ws) => {
      ws.on('framereceived', (frame) => {
        const data = JSON.parse(String(frame.payload));
        if (data.type === 'message_ack') {
          resolve();
        }
      });
    });
  });

  await page.goto('/chat');
  await page.getByRole('textbox', { name: 'Message' }).fill('Important update');
  await page.getByRole('button', { name: 'Send' }).click();

  await ackPromise;
  await expect(page.getByTestId('message-status').last()).toHaveText('Delivered');
});
```

### Mocking WebSocket Messages with `routeWebSocket`

**Use when**: You want to control what the server sends to test specific UI states -- error messages, edge cases, high-volume data -- without a real backend.
**Avoid when**: You need to test actual server behavior. Use a real backend.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('display notification when server pushes an alert', async ({ page }) => {
  const wsRoute = await page.routeWebSocket('**/ws/notifications', (ws) => {
    // Let the app send its initial handshake
    ws.onMessage((message) => {
      const data = JSON.parse(message);
      if (data.type === 'subscribe') {
        ws.send(JSON.stringify({ type: 'subscribed', channel: data.channel }));
      }
    });

    // Push a notification after a short delay
    setTimeout(() => {
      ws.send(JSON.stringify({
        type: 'notification',
        title: 'Server Alert',
        body: 'Deployment completed successfully',
        severity: 'info',
      }));
    }, 500);
  });

  await page.goto('/dashboard');

  // Verify the notification appears in the UI
  await expect(page.getByRole('alert')).toContainText('Deployment completed successfully');
});

test('handle WebSocket server error gracefully', async ({ page }) => {
  await page.routeWebSocket('**/ws', (ws) => {
    // Immediately close with an error code
    ws.close({ code: 1011, reason: 'Internal server error' });
  });

  await page.goto('/chat');

  // App should show a reconnection message, not crash
  await expect(page.getByText('Connection lost. Reconnecting...')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('display notification when server pushes an alert', async ({ page }) => {
  await page.routeWebSocket('**/ws/notifications', (ws) => {
    ws.onMessage((message) => {
      const data = JSON.parse(message);
      if (data.type === 'subscribe') {
        ws.send(JSON.stringify({ type: 'subscribed', channel: data.channel }));
      }
    });

    setTimeout(() => {
      ws.send(JSON.stringify({
        type: 'notification',
        title: 'Server Alert',
        body: 'Deployment completed successfully',
        severity: 'info',
      }));
    }, 500);
  });

  await page.goto('/dashboard');
  await expect(page.getByRole('alert')).toContainText('Deployment completed successfully');
});

test('handle WebSocket server error gracefully', async ({ page }) => {
  await page.routeWebSocket('**/ws', (ws) => {
    ws.close({ code: 1011, reason: 'Internal server error' });
  });

  await page.goto('/chat');
  await expect(page.getByText('Connection lost. Reconnecting...')).toBeVisible();
});
```

### Forwarding with Modification (Man-in-the-Middle)

**Use when**: You want to connect to the real server but intercept, modify, or inject messages.
**Avoid when**: Full mocking (`routeWebSocket` without `connectToServer`) is sufficient.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('inject a fake high-priority message into real stream', async ({ page }) => {
  await page.routeWebSocket('**/ws/feed', (ws) => {
    const server = ws.connectToServer();

    // Forward all messages from server to client, but inject extras
    server.onMessage((message) => {
      ws.send(message); // Forward the real message
    });

    // Forward all client messages to server
    ws.onMessage((message) => {
      server.send(message);
    });

    // Inject a synthetic message after 1 second
    setTimeout(() => {
      ws.send(JSON.stringify({
        type: 'alert',
        priority: 'high',
        text: 'Injected test alert',
      }));
    }, 1000);
  });

  await page.goto('/live-feed');
  await expect(page.getByText('Injected test alert')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('inject a fake high-priority message into real stream', async ({ page }) => {
  await page.routeWebSocket('**/ws/feed', (ws) => {
    const server = ws.connectToServer();

    server.onMessage((message) => {
      ws.send(message);
    });

    ws.onMessage((message) => {
      server.send(message);
    });

    setTimeout(() => {
      ws.send(JSON.stringify({
        type: 'alert',
        priority: 'high',
        text: 'Injected test alert',
      }));
    }, 1000);
  });

  await page.goto('/live-feed');
  await expect(page.getByText('Injected test alert')).toBeVisible();
});
```

### Server-Sent Events (SSE) Testing

**Use when**: Your app uses `EventSource` for server-to-client streaming (live logs, progress updates, news feeds).
**Avoid when**: The app uses WebSockets. SSE is HTTP-based and intercepted differently.

SSE responses are standard HTTP -- intercept them with `page.route()` and return a streaming response.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('SSE live log stream displays entries', async ({ page }) => {
  // Intercept the SSE endpoint and return controlled events
  await page.route('**/api/logs/stream', async (route) => {
    const events = [
      'data: {"level":"info","message":"Server started"}\n\n',
      'data: {"level":"warn","message":"High memory usage"}\n\n',
      'data: {"level":"error","message":"Connection timeout"}\n\n',
    ];

    await route.fulfill({
      status: 200,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
      body: events.join(''),
    });
  });

  await page.goto('/admin/logs');

  await expect(page.getByText('Server started')).toBeVisible();
  await expect(page.getByText('High memory usage')).toBeVisible();
  await expect(page.getByText('Connection timeout')).toBeVisible();
});

test('SSE reconnection on connection drop', async ({ page }) => {
  let requestCount = 0;

  await page.route('**/api/events', async (route) => {
    requestCount++;
    if (requestCount === 1) {
      // First request: send one event then close abruptly
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: 'data: {"msg":"first"}\n\n',
      });
    } else {
      // Reconnection: send the next event
      await route.fulfill({
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
        body: 'data: {"msg":"reconnected"}\n\n',
      });
    }
  });

  await page.goto('/live');
  await expect(page.getByText('first')).toBeVisible();
  // EventSource auto-reconnects; verify the app handles it
  await expect(page.getByText('reconnected')).toBeVisible({ timeout: 10000 });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('SSE live log stream displays entries', async ({ page }) => {
  await page.route('**/api/logs/stream', async (route) => {
    const events = [
      'data: {"level":"info","message":"Server started"}\n\n',
      'data: {"level":"warn","message":"High memory usage"}\n\n',
      'data: {"level":"error","message":"Connection timeout"}\n\n',
    ];

    await route.fulfill({
      status: 200,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
      body: events.join(''),
    });
  });

  await page.goto('/admin/logs');

  await expect(page.getByText('Server started')).toBeVisible();
  await expect(page.getByText('High memory usage')).toBeVisible();
  await expect(page.getByText('Connection timeout')).toBeVisible();
});
```

### Polling-Based Real-Time Testing

**Use when**: Your app uses HTTP polling (setInterval + fetch) instead of WebSockets or SSE.
**Avoid when**: The app uses WebSockets or SSE -- use the patterns above.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('polling updates dashboard data every interval', async ({ page }) => {
  let callCount = 0;

  await page.route('**/api/dashboard/stats', async (route) => {
    callCount++;
    const data = callCount === 1
      ? { activeUsers: 100, revenue: 5000 }
      : { activeUsers: 142, revenue: 5250 };

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(data),
    });
  });

  await page.goto('/dashboard');

  // First poll result
  await expect(page.getByTestId('active-users')).toHaveText('100');

  // Wait for the second poll to update the UI
  await expect(page.getByTestId('active-users')).toHaveText('142', { timeout: 15000 });

  // Verify at least 2 requests were made
  expect(callCount).toBeGreaterThanOrEqual(2);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('polling updates dashboard data every interval', async ({ page }) => {
  let callCount = 0;

  await page.route('**/api/dashboard/stats', async (route) => {
    callCount++;
    const data = callCount === 1
      ? { activeUsers: 100, revenue: 5000 }
      : { activeUsers: 142, revenue: 5250 };

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(data),
    });
  });

  await page.goto('/dashboard');
  await expect(page.getByTestId('active-users')).toHaveText('100');
  await expect(page.getByTestId('active-users')).toHaveText('142', { timeout: 15000 });
  expect(callCount).toBeGreaterThanOrEqual(2);
});
```

### WebSocket Connection Lifecycle

**Use when**: You need to verify that your app handles connection, disconnection, and reconnection properly.
**Avoid when**: Connection lifecycle is not user-visible.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('app reconnects after WebSocket drops', async ({ page }) => {
  let connectionCount = 0;

  await page.routeWebSocket('**/ws', (ws) => {
    connectionCount++;

    if (connectionCount === 1) {
      // First connection: close after a brief moment
      setTimeout(() => ws.close({ code: 1006, reason: 'Abnormal closure' }), 500);
    } else {
      // Second connection (reconnect): stay open and respond
      ws.onMessage((message) => {
        ws.send(JSON.stringify({ type: 'pong' }));
      });
    }
  });

  await page.goto('/app');

  // App detects disconnect and shows status
  await expect(page.getByText('Reconnecting...')).toBeVisible();

  // App reconnects and status returns to normal
  await expect(page.getByText('Connected')).toBeVisible({ timeout: 10000 });

  expect(connectionCount).toBe(2);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('app reconnects after WebSocket drops', async ({ page }) => {
  let connectionCount = 0;

  await page.routeWebSocket('**/ws', (ws) => {
    connectionCount++;

    if (connectionCount === 1) {
      setTimeout(() => ws.close({ code: 1006, reason: 'Abnormal closure' }), 500);
    } else {
      ws.onMessage((message) => {
        ws.send(JSON.stringify({ type: 'pong' }));
      });
    }
  });

  await page.goto('/app');
  await expect(page.getByText('Reconnecting...')).toBeVisible();
  await expect(page.getByText('Connected')).toBeVisible({ timeout: 10000 });
  expect(connectionCount).toBe(2);
});
```

## Decision Guide

| Scenario | Approach | Why |
|---|---|---|
| Verify app sends correct WS message | `page.on('websocket')` + `ws.on('framesent')` | Observe without intercepting |
| Verify app handles server push | `page.routeWebSocket()` with mock server | Full control over what the "server" sends |
| Test with real server but inject messages | `routeWebSocket` + `connectToServer()` | Man-in-the-middle: forward real traffic plus inject extras |
| Test SSE endpoint | `page.route()` with `text/event-stream` content type | SSE is HTTP -- standard route interception works |
| Test HTTP polling | `page.route()` with changing responses per call | Increment a counter; return different data each call |
| Verify reconnection logic | `routeWebSocket` that closes the first connection | Simulate server failure, verify the app retries |
| Test binary WebSocket data | `ws.on('framereceived')`, check `frame.payload` as Buffer | Binary frames arrive as `Buffer` in Node.js |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `page.waitForTimeout(3000)` to wait for WS message | Arbitrary delay; flaky and slow | `await expect(page.getByText('msg')).toBeVisible()` or wait on a Promise |
| Directly construct `WebSocket` in `page.evaluate` | You lose Playwright's observation and routing capabilities | Let the app create its own WebSocket; intercept via `routeWebSocket` |
| Ignore WebSocket close codes in mocks | App may behave differently for 1000 (normal) vs 1006 (abnormal) | Use the correct close code: `ws.close({ code: 1000 })` |
| Test real-time features against live third-party servers | Flaky, slow, and may incur costs | Mock the WebSocket or SSE endpoint |
| Assert on raw WebSocket frame content in every test | Couples tests to wire protocol; breaks on payload format changes | Assert on the UI -- that is what users see |
| Forget to handle binary vs text frames | `frame.payload` can be `string` or `Buffer` | Check frame type or use `String(frame.payload)` consistently |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `page.on('websocket')` never fires | WebSocket connects before the listener is attached | Register the listener before `page.goto()` |
| `routeWebSocket` does not intercept | URL pattern does not match the actual WebSocket URL | Check the URL in DevTools Network tab; update the glob pattern |
| SSE mock returns all events at once | `route.fulfill` sends the body synchronously | For true streaming, use the real server or chunk the response with pauses via `page.evaluate` |
| WebSocket messages arrive but UI does not update | App processes messages asynchronously; assertion runs too early | Use `await expect(...).toBeVisible()` which auto-retries |
| Binary frames show as garbled text | `String(frame.payload)` on binary data produces garbage | Treat `frame.payload` as `Buffer` and decode appropriately |
| Reconnection test is flaky | App has exponential backoff; timeout too short | Increase assertion timeout: `toBeVisible({ timeout: 15000 })` |

## Related

- [core/multi-user-and-collaboration.md](multi-user-and-collaboration.md) -- multi-user tests that rely on WebSocket for real-time sync
- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- auto-retrying assertions for async UI updates
- [core/when-to-mock.md](when-to-mock.md) -- deciding when to mock WebSocket vs use real server
- [core/debugging.md](debugging.md) -- tracing WebSocket frames in Playwright traces
