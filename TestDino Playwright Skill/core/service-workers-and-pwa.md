# Service Workers and PWA Testing

> **When to use**: When your application is a Progressive Web App (PWA) or uses service workers for offline support, caching, push notifications, or background sync.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/assertions-and-waiting.md](assertions-and-waiting.md)

## Quick Reference

```typescript
// Service workers require a persistent context — use launchPersistentContext
const context = await chromium.launchPersistentContext(userDataDir, {
  baseURL: 'https://localhost:3000',
});

// Enable/disable offline mode
await context.setOffline(true);   // Go offline
await context.setOffline(false);  // Come back online

// Wait for service worker to register
const sw = await context.waitForEvent('serviceworker');
console.log('SW URL:', sw.url());
```

## Patterns

### Service Worker Registration

**Use when**: You need to verify that your service worker registers successfully, activates, and controls the page.
**Avoid when**: Your app does not use service workers.

Service workers require a persistent browser context because they are tied to a profile. The default `page` fixture uses a temporary context that does not persist service worker registrations across navigations reliably.

**TypeScript**
```typescript
import { test as base, expect, chromium, BrowserContext } from '@playwright/test';
import path from 'path';
import fs from 'fs';

// Create a fixture with a persistent context for SW testing
const test = base.extend<{ swContext: BrowserContext }>({
  swContext: async ({}, use) => {
    const userDataDir = path.join(__dirname, '.tmp-profile');
    const context = await chromium.launchPersistentContext(userDataDir, {
      baseURL: 'https://localhost:3000',
    });
    await use(context);
    await context.close();
    fs.rmSync(userDataDir, { recursive: true, force: true });
  },
});

test('service worker registers and activates', async ({ swContext }) => {
  const page = await swContext.newPage();

  // Listen for the service worker event
  const swPromise = swContext.waitForEvent('serviceworker');

  await page.goto('/');

  const sw = await swPromise;
  expect(sw.url()).toContain('service-worker.js');

  // Verify the SW is controlling the page
  const isControlled = await page.evaluate(() => {
    return navigator.serviceWorker.controller !== null;
  });
  expect(isControlled).toBe(true);
});
```

**JavaScript**
```javascript
const { test: base, expect, chromium } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

const test = base.extend({
  swContext: async ({}, use) => {
    const userDataDir = path.join(__dirname, '.tmp-profile');
    const context = await chromium.launchPersistentContext(userDataDir, {
      baseURL: 'https://localhost:3000',
    });
    await use(context);
    await context.close();
    fs.rmSync(userDataDir, { recursive: true, force: true });
  },
});

test('service worker registers and activates', async ({ swContext }) => {
  const page = await swContext.newPage();
  const swPromise = swContext.waitForEvent('serviceworker');

  await page.goto('/');

  const sw = await swPromise;
  expect(sw.url()).toContain('service-worker.js');

  const isControlled = await page.evaluate(() => {
    return navigator.serviceWorker.controller !== null;
  });
  expect(isControlled).toBe(true);
});
```

### Offline Mode Testing

**Use when**: Your PWA should work offline -- serving cached pages, showing offline indicators, queuing data for sync.
**Avoid when**: Your app has no offline support.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('app serves cached page when offline', async ({ swContext }) => {
  const page = await swContext.newPage();

  // First visit — caches the page and assets
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  // Wait for the service worker to finish caching
  await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.ready;
    // Wait for the SW to be in the 'activated' state
    return registration.active?.state === 'activated';
  });

  // Go offline
  await swContext.setOffline(true);

  // Reload — should serve from cache
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  // Verify offline indicator appears
  await expect(page.getByText('You are offline')).toBeVisible();

  // Come back online
  await swContext.setOffline(false);
  await expect(page.getByText('You are offline')).toBeHidden();
});

test('form submission queues when offline', async ({ swContext }) => {
  const page = await swContext.newPage();
  await page.goto('/feedback');

  // Ensure SW is active
  await page.evaluate(() => navigator.serviceWorker.ready);

  // Go offline
  await swContext.setOffline(true);

  // Submit a form while offline
  await page.getByLabel('Feedback').fill('Great product!');
  await page.getByRole('button', { name: 'Submit' }).click();

  // App should show a "queued" message, not an error
  await expect(page.getByText('Saved offline. Will sync when connected.')).toBeVisible();

  // Come back online — the queued data should sync
  await swContext.setOffline(false);
  await expect(page.getByText('Feedback submitted successfully')).toBeVisible({ timeout: 10000 });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('app serves cached page when offline', async ({ swContext }) => {
  const page = await swContext.newPage();

  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.ready;
    return registration.active?.state === 'activated';
  });

  await swContext.setOffline(true);
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByText('You are offline')).toBeVisible();

  await swContext.setOffline(false);
  await expect(page.getByText('You are offline')).toBeHidden();
});
```

### Cache Verification

**Use when**: You need to confirm that specific resources are cached by the service worker.
**Avoid when**: You trust the framework's caching strategy and only need to verify the offline UX (test offline mode instead).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('critical assets are cached by the service worker', async ({ swContext }) => {
  const page = await swContext.newPage();
  await page.goto('/');

  // Wait for SW to be ready
  await page.evaluate(() => navigator.serviceWorker.ready);

  // Check the cache contents
  const cachedUrls = await page.evaluate(async () => {
    const cacheNames = await caches.keys();
    const allUrls: string[] = [];
    for (const name of cacheNames) {
      const cache = await caches.open(name);
      const keys = await cache.keys();
      allUrls.push(...keys.map((req) => new URL(req.url).pathname));
    }
    return allUrls;
  });

  // Verify critical resources are cached
  expect(cachedUrls).toContain('/');
  expect(cachedUrls).toContain('/offline.html');
  expect(cachedUrls.some((url) => url.endsWith('.js'))).toBe(true);
  expect(cachedUrls.some((url) => url.endsWith('.css'))).toBe(true);
});

test('cache is invalidated after service worker update', async ({ swContext }) => {
  const page = await swContext.newPage();
  await page.goto('/');

  // Get initial cache version
  const initialCaches = await page.evaluate(() => caches.keys());

  // Simulate a new SW version by clearing and reloading
  await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.getRegistration();
    await registration?.update();
  });

  // After update, old caches should be cleaned up
  await page.reload();
  await page.evaluate(() => navigator.serviceWorker.ready);

  const updatedCaches = await page.evaluate(() => caches.keys());

  // The app should manage cache names with versioning
  expect(updatedCaches.length).toBeGreaterThanOrEqual(1);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('critical assets are cached by the service worker', async ({ swContext }) => {
  const page = await swContext.newPage();
  await page.goto('/');
  await page.evaluate(() => navigator.serviceWorker.ready);

  const cachedUrls = await page.evaluate(async () => {
    const cacheNames = await caches.keys();
    const allUrls = [];
    for (const name of cacheNames) {
      const cache = await caches.open(name);
      const keys = await cache.keys();
      allUrls.push(...keys.map((req) => new URL(req.url).pathname));
    }
    return allUrls;
  });

  expect(cachedUrls).toContain('/');
  expect(cachedUrls).toContain('/offline.html');
});
```

### PWA Install Prompt

**Use when**: You need to test the "Add to Home Screen" / PWA install flow.
**Avoid when**: Your app is not a PWA or does not handle the `beforeinstallprompt` event.

The `beforeinstallprompt` event cannot be synthetically triggered by Playwright. Instead, verify that your app captures and handles the event correctly.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('app captures install prompt and shows install button', async ({ swContext }) => {
  const page = await swContext.newPage();

  // Mock the beforeinstallprompt event
  await page.addInitScript(() => {
    let deferredPrompt: Event | null = null;

    // Simulate the browser firing beforeinstallprompt
    window.addEventListener('load', () => {
      const event = new Event('beforeinstallprompt');
      (event as any).preventDefault = () => {};
      (event as any).prompt = () => Promise.resolve();
      (event as any).userChoice = Promise.resolve({ outcome: 'accepted' });

      window.dispatchEvent(event);
    });
  });

  await page.goto('/');

  // Your app should show an install button when it captures the prompt
  await expect(page.getByRole('button', { name: 'Install app' })).toBeVisible();
});

test('web app manifest is valid', async ({ swContext }) => {
  const page = await swContext.newPage();
  await page.goto('/');

  // Verify manifest link exists
  const manifestUrl = await page.evaluate(() => {
    const link = document.querySelector('link[rel="manifest"]') as HTMLLinkElement;
    return link?.href;
  });
  expect(manifestUrl).toBeTruthy();

  // Fetch and validate the manifest
  const response = await page.request.get(manifestUrl!);
  expect(response.ok()).toBe(true);

  const manifest = await response.json();
  expect(manifest.name).toBeTruthy();
  expect(manifest.icons).toHaveLength(expect.any(Number));
  expect(manifest.start_url).toBeTruthy();
  expect(manifest.display).toBe('standalone');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('app captures install prompt and shows install button', async ({ swContext }) => {
  const page = await swContext.newPage();

  await page.addInitScript(() => {
    window.addEventListener('load', () => {
      const event = new Event('beforeinstallprompt');
      event.preventDefault = () => {};
      event.prompt = () => Promise.resolve();
      event.userChoice = Promise.resolve({ outcome: 'accepted' });
      window.dispatchEvent(event);
    });
  });

  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Install app' })).toBeVisible();
});
```

### Push Notification Testing

**Use when**: Your PWA uses the Push API to receive push notifications from a server.
**Avoid when**: Notifications are handled entirely client-side without the Push API.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('push notification triggers UI update', async ({ swContext }) => {
  const page = await swContext.newPage();
  await page.goto('/');

  // Wait for SW to be ready
  const swURL = await page.evaluate(async () => {
    const reg = await navigator.serviceWorker.ready;
    return reg.active?.scriptURL;
  });
  expect(swURL).toBeTruthy();

  // Get the service worker and evaluate inside it
  const sw = swContext.serviceWorkers()[0];

  // Simulate a push event inside the service worker
  await sw.evaluate(async () => {
    const event = new PushEvent('push', {
      data: new TextEncoder().encode(JSON.stringify({
        title: 'New Message',
        body: 'You have a new message from Alice',
        url: '/messages',
      })),
    });
    // @ts-ignore — dispatchEvent works in SW context
    self.dispatchEvent(event);
  });

  // Verify the app reacts (e.g., shows a badge or notification banner)
  await expect(page.getByTestId('notification-badge')).toHaveText('1');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('push notification triggers UI update', async ({ swContext }) => {
  const page = await swContext.newPage();
  await page.goto('/');

  const swURL = await page.evaluate(async () => {
    const reg = await navigator.serviceWorker.ready;
    return reg.active?.scriptURL;
  });
  expect(swURL).toBeTruthy();

  const sw = swContext.serviceWorkers()[0];

  await sw.evaluate(async () => {
    const event = new PushEvent('push', {
      data: new TextEncoder().encode(JSON.stringify({
        title: 'New Message',
        body: 'You have a new message from Alice',
        url: '/messages',
      })),
    });
    self.dispatchEvent(event);
  });

  await expect(page.getByTestId('notification-badge')).toHaveText('1');
});
```

### Background Sync Testing

**Use when**: Your app uses the Background Sync API to defer network requests until the user has connectivity.
**Avoid when**: Your app does not use background sync.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('background sync retries failed requests when online', async ({ swContext }) => {
  const page = await swContext.newPage();
  await page.goto('/tasks');

  // Ensure SW is active
  await page.evaluate(() => navigator.serviceWorker.ready);

  // Go offline
  await swContext.setOffline(true);

  // Create a task (will fail to sync)
  await page.getByLabel('New task').fill('Buy groceries');
  await page.getByRole('button', { name: 'Add' }).click();

  // Task shows as "pending sync"
  await expect(page.getByText('Buy groceries')).toBeVisible();
  await expect(page.getByTestId('sync-status')).toHaveText('Pending');

  // Come back online — background sync should fire
  await swContext.setOffline(false);

  // Wait for sync to complete
  await expect(page.getByTestId('sync-status')).toHaveText('Synced', { timeout: 15000 });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('background sync retries failed requests when online', async ({ swContext }) => {
  const page = await swContext.newPage();
  await page.goto('/tasks');
  await page.evaluate(() => navigator.serviceWorker.ready);

  await swContext.setOffline(true);

  await page.getByLabel('New task').fill('Buy groceries');
  await page.getByRole('button', { name: 'Add' }).click();

  await expect(page.getByText('Buy groceries')).toBeVisible();
  await expect(page.getByTestId('sync-status')).toHaveText('Pending');

  await swContext.setOffline(false);
  await expect(page.getByTestId('sync-status')).toHaveText('Synced', { timeout: 15000 });
});
```

## Decision Guide

| Scenario | Approach | Why |
|---|---|---|
| Verify SW registers | `context.waitForEvent('serviceworker')` | Confirms the SW file was fetched and registered |
| Test offline page serving | `context.setOffline(true)` + reload | Simulates network loss at the browser level |
| Verify specific assets are cached | `page.evaluate(() => caches.keys())` | Directly queries the Cache API |
| Test install prompt | `addInitScript` to mock `beforeinstallprompt` | Browser does not fire this event in automation |
| Validate web manifest | `page.request.get(manifestUrl)` | Fetch and parse the JSON manifest |
| Test push notifications | `sw.evaluate()` to dispatch PushEvent | Simulates a push message inside the SW |
| Test background sync | Go offline, perform action, come back online | Verifies the sync queue processes correctly |
| Test SW update flow | `registration.update()` via `page.evaluate` | Triggers a manual SW update check |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Test service workers with the default `page` fixture | Default context is temporary; SWs may not persist | Use `launchPersistentContext` for reliable SW testing |
| Skip `navigator.serviceWorker.ready` before going offline | SW may not have finished caching | Always `await page.evaluate(() => navigator.serviceWorker.ready)` first |
| Use `page.route()` to simulate offline | Only intercepts Playwright-visible requests; SW fetch events are not intercepted | Use `context.setOffline(true)` for true network-level offline |
| Test the SW JavaScript file directly with unit tests only | Misses integration with the page and caching behavior | Combine unit tests with Playwright end-to-end SW tests |
| Assume caches are clean at test start | Previous test runs may leave stale caches | Clear caches in fixture setup or use a fresh `userDataDir` |
| `waitForTimeout` after `setOffline(false)` | Background sync timing is unpredictable | Use `expect(...).toHaveText('Synced', { timeout: 15000 })` |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `context.waitForEvent('serviceworker')` never resolves | SW already registered before listener attached | Register listener before `page.goto()`, or check `context.serviceWorkers()` |
| SW does not activate | Old SW is still controlling the page | Use `skipWaiting()` in the SW or clear the `userDataDir` |
| Offline test still loads fresh content | SW cache was not populated before going offline | Wait for `navigator.serviceWorker.ready` and verify cache contents first |
| `context.setOffline(true)` has no effect | Using a non-persistent context or the wrong context | Ensure offline is set on the same context that owns the page |
| Push event does nothing | SW is not the active controller | Ensure `sw.evaluate()` targets the correct service worker from `context.serviceWorkers()` |
| Tests interfere with each other | Shared `userDataDir` between tests | Use a unique temp directory per test, cleaned in fixture teardown |
| Service worker tests only work in Chromium | Firefox and WebKit have limited SW support in Playwright | Run SW tests in Chromium only via `test.skip` or project config |

## Related

- [core/browser-apis.md](browser-apis.md) -- IndexedDB and localStorage used alongside service workers
- [core/configuration.md](configuration.md) -- project-level config for PWA testing
- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) -- wrapping persistent context in fixtures
- [core/websockets-and-realtime.md](websockets-and-realtime.md) -- real-time features that interact with offline/online state
