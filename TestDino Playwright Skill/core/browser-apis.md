# Browser APIs

> **When to use**: When testing features that depend on browser-native APIs -- geolocation, permissions, clipboard, notifications, camera/microphone, localStorage, sessionStorage, IndexedDB.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/fixtures-and-hooks.md](fixtures-and-hooks.md)

## Quick Reference

```typescript
// Geolocation — set via context options
const context = await browser.newContext({
  geolocation: { latitude: 40.7128, longitude: -74.0060 },
  permissions: ['geolocation'],
});

// Permissions — grant at context level
const context = await browser.newContext({
  permissions: ['clipboard-read', 'clipboard-write', 'notifications'],
});

// localStorage / sessionStorage — access via page.evaluate
await page.evaluate(() => localStorage.setItem('theme', 'dark'));
const value = await page.evaluate(() => localStorage.getItem('theme'));

// Clipboard — read/write in page context
await page.evaluate(() => navigator.clipboard.writeText('copied text'));
```

## Patterns

### Geolocation

**Use when**: Your app uses `navigator.geolocation` for maps, store locators, delivery tracking, or location-based features.
**Avoid when**: Your app never reads the user's location.

Geolocation is set at the context level. You can also update it mid-test with `context.setGeolocation()`.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('shows nearest store based on geolocation', async ({ browser }) => {
  const context = await browser.newContext({
    geolocation: { latitude: 40.7128, longitude: -74.0060 }, // New York
    permissions: ['geolocation'],
  });
  const page = await context.newPage();

  await page.goto('/store-locator');
  await page.getByRole('button', { name: 'Find nearby stores' }).click();

  await expect(page.getByText('Manhattan Store')).toBeVisible();
  await context.close();
});

test('update location mid-test for moving user', async ({ browser }) => {
  const context = await browser.newContext({
    geolocation: { latitude: 37.7749, longitude: -122.4194 }, // San Francisco
    permissions: ['geolocation'],
  });
  const page = await context.newPage();

  await page.goto('/delivery-tracker');
  await expect(page.getByTestId('current-city')).toHaveText('San Francisco');

  // Simulate user moving to a new location
  await context.setGeolocation({ latitude: 34.0522, longitude: -118.2437 }); // Los Angeles

  // Trigger location refresh
  await page.getByRole('button', { name: 'Update location' }).click();
  await expect(page.getByTestId('current-city')).toHaveText('Los Angeles');

  await context.close();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('shows nearest store based on geolocation', async ({ browser }) => {
  const context = await browser.newContext({
    geolocation: { latitude: 40.7128, longitude: -74.0060 },
    permissions: ['geolocation'],
  });
  const page = await context.newPage();

  await page.goto('/store-locator');
  await page.getByRole('button', { name: 'Find nearby stores' }).click();

  await expect(page.getByText('Manhattan Store')).toBeVisible();
  await context.close();
});

test('update location mid-test', async ({ browser }) => {
  const context = await browser.newContext({
    geolocation: { latitude: 37.7749, longitude: -122.4194 },
    permissions: ['geolocation'],
  });
  const page = await context.newPage();

  await page.goto('/delivery-tracker');
  await expect(page.getByTestId('current-city')).toHaveText('San Francisco');

  await context.setGeolocation({ latitude: 34.0522, longitude: -118.2437 });
  await page.getByRole('button', { name: 'Update location' }).click();
  await expect(page.getByTestId('current-city')).toHaveText('Los Angeles');

  await context.close();
});
```

You can also set geolocation globally in `playwright.config`:

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    geolocation: { latitude: 51.5074, longitude: -0.1278 }, // London
    permissions: ['geolocation'],
  },
});
```

### Permissions

**Use when**: Your app requests browser permissions -- notifications, camera, microphone, geolocation, clipboard.
**Avoid when**: Your app does not use the Permissions API.

Grant permissions at context creation. Playwright does not show permission dialogs; you pre-grant or deny them.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('notification permission granted shows notification UI', async ({ browser }) => {
  const context = await browser.newContext({
    permissions: ['notifications'],
  });
  const page = await context.newPage();

  await page.goto('/settings/notifications');

  // App checks Notification.permission and shows the toggle
  await expect(page.getByRole('switch', { name: 'Enable notifications' })).toBeEnabled();

  await context.close();
});

test('notification permission denied shows upgrade prompt', async ({ browser }) => {
  // No 'notifications' in permissions = denied
  const context = await browser.newContext({
    permissions: [],
  });
  const page = await context.newPage();

  await page.goto('/settings/notifications');

  await expect(page.getByText('Notifications are blocked')).toBeVisible();
  await context.close();
});

test('grant permissions mid-test', async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('/camera-app');

  // Initially no camera permission
  await expect(page.getByText('Camera access needed')).toBeVisible();

  // Grant permission dynamically
  await context.grantPermissions(['camera'], { origin: 'https://localhost:3000' });

  await page.getByRole('button', { name: 'Enable camera' }).click();
  await expect(page.getByTestId('camera-preview')).toBeVisible();

  // Revoke all permissions
  await context.clearPermissions();
  await context.close();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('notification permission granted shows notification UI', async ({ browser }) => {
  const context = await browser.newContext({
    permissions: ['notifications'],
  });
  const page = await context.newPage();

  await page.goto('/settings/notifications');
  await expect(page.getByRole('switch', { name: 'Enable notifications' })).toBeEnabled();
  await context.close();
});

test('grant permissions mid-test', async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('/camera-app');

  await context.grantPermissions(['camera'], { origin: 'https://localhost:3000' });
  await page.getByRole('button', { name: 'Enable camera' }).click();
  await expect(page.getByTestId('camera-preview')).toBeVisible();

  await context.clearPermissions();
  await context.close();
});
```

### Clipboard API

**Use when**: Testing copy/paste functionality, "Copy to clipboard" buttons, or paste-from-clipboard features.
**Avoid when**: Your app does not interact with the clipboard.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('copy button puts text on clipboard', async ({ browser }) => {
  const context = await browser.newContext({
    permissions: ['clipboard-read', 'clipboard-write'],
  });
  const page = await context.newPage();

  await page.goto('/share');
  await page.getByRole('button', { name: 'Copy link' }).click();

  // Read clipboard content
  const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
  expect(clipboardText).toContain('https://example.com/share/');

  await context.close();
});

test('paste from clipboard into editor', async ({ browser }) => {
  const context = await browser.newContext({
    permissions: ['clipboard-read', 'clipboard-write'],
  });
  const page = await context.newPage();

  await page.goto('/editor');

  // Write to clipboard programmatically
  await page.evaluate(() => navigator.clipboard.writeText('Pasted content from clipboard'));

  // Focus the editor and trigger paste
  const editor = page.getByRole('textbox', { name: 'Editor' });
  await editor.focus();
  await page.keyboard.press('ControlOrMeta+v');

  await expect(editor).toContainText('Pasted content from clipboard');

  await context.close();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('copy button puts text on clipboard', async ({ browser }) => {
  const context = await browser.newContext({
    permissions: ['clipboard-read', 'clipboard-write'],
  });
  const page = await context.newPage();

  await page.goto('/share');
  await page.getByRole('button', { name: 'Copy link' }).click();

  const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
  expect(clipboardText).toContain('https://example.com/share/');
  await context.close();
});
```

### Camera and Microphone Mocking

**Use when**: Testing video calls, QR code scanners, voice recording, or any feature using `getUserMedia`.
**Avoid when**: Your app does not use camera or microphone.

Chromium can use fake media devices. This is not available in Firefox or WebKit.

**TypeScript**
```typescript
import { test, expect, chromium } from '@playwright/test';

test('video call shows local preview with fake camera', async () => {
  // Launch Chromium with fake media streams
  const browser = await chromium.launch({
    args: [
      '--use-fake-device-for-media-stream',
      '--use-fake-ui-for-media-stream',
    ],
  });

  const context = await browser.newContext({
    permissions: ['camera', 'microphone'],
  });
  const page = await context.newPage();

  await page.goto('/video-call');
  await page.getByRole('button', { name: 'Start camera' }).click();

  // Verify the video element is playing
  const isPlaying = await page.evaluate(() => {
    const video = document.querySelector('video#local-preview') as HTMLVideoElement;
    return video && !video.paused && video.readyState >= 2;
  });
  expect(isPlaying).toBe(true);

  await context.close();
  await browser.close();
});
```

**JavaScript**
```javascript
const { test, expect, chromium } = require('@playwright/test');

test('video call shows local preview with fake camera', async () => {
  const browser = await chromium.launch({
    args: [
      '--use-fake-device-for-media-stream',
      '--use-fake-ui-for-media-stream',
    ],
  });

  const context = await browser.newContext({
    permissions: ['camera', 'microphone'],
  });
  const page = await context.newPage();

  await page.goto('/video-call');
  await page.getByRole('button', { name: 'Start camera' }).click();

  const isPlaying = await page.evaluate(() => {
    const video = document.querySelector('video#local-preview');
    return video && !video.paused && video.readyState >= 2;
  });
  expect(isPlaying).toBe(true);

  await context.close();
  await browser.close();
});
```

### localStorage and sessionStorage

**Use when**: Your app persists state, tokens, preferences, or feature flags in web storage.
**Avoid when**: You can set the state through the UI or API instead. Prefer those approaches for realism.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('app loads dark theme from localStorage preference', async ({ page }) => {
  // Set localStorage before navigating
  await page.goto('/');
  await page.evaluate(() => localStorage.setItem('theme', 'dark'));

  // Reload to pick up the stored preference
  await page.reload();

  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
});

test('clear localStorage between scenarios', async ({ page }) => {
  await page.goto('/');

  // Seed some data
  await page.evaluate(() => {
    localStorage.setItem('cart', JSON.stringify([{ id: 1, qty: 2 }]));
    localStorage.setItem('user_prefs', JSON.stringify({ currency: 'EUR' }));
  });

  // Read and verify
  const cart = await page.evaluate(() => JSON.parse(localStorage.getItem('cart') || '[]'));
  expect(cart).toHaveLength(1);

  // Clear specific keys
  await page.evaluate(() => localStorage.removeItem('cart'));

  // Or clear everything
  await page.evaluate(() => localStorage.clear());
});

test('sessionStorage survives navigations within the session', async ({ page }) => {
  await page.goto('/step-1');
  await page.evaluate(() => sessionStorage.setItem('wizard_step', '1'));

  await page.goto('/step-2');
  const step = await page.evaluate(() => sessionStorage.getItem('wizard_step'));
  expect(step).toBe('1');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('app loads dark theme from localStorage preference', async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => localStorage.setItem('theme', 'dark'));
  await page.reload();

  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
});

test('sessionStorage survives navigations within the session', async ({ page }) => {
  await page.goto('/step-1');
  await page.evaluate(() => sessionStorage.setItem('wizard_step', '1'));

  await page.goto('/step-2');
  const step = await page.evaluate(() => sessionStorage.getItem('wizard_step'));
  expect(step).toBe('1');
});
```

### IndexedDB Testing

**Use when**: Your app uses IndexedDB for offline storage, caching, or large datasets (progressive web apps, offline-first apps).
**Avoid when**: Your app only uses localStorage or server-side storage.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('offline-first app stores data in IndexedDB', async ({ page }) => {
  await page.goto('/notes');

  // Create a note through the UI
  await page.getByRole('button', { name: 'New note' }).click();
  await page.getByRole('textbox', { name: 'Title' }).fill('Test Note');
  await page.getByRole('textbox', { name: 'Content' }).fill('This is stored in IndexedDB');
  await page.getByRole('button', { name: 'Save' }).click();

  // Verify it is stored in IndexedDB
  const storedNotes = await page.evaluate(() => {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('NotesDB', 1);
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction('notes', 'readonly');
        const store = tx.objectStore('notes');
        const getAll = store.getAll();
        getAll.onsuccess = () => resolve(getAll.result);
        getAll.onerror = () => reject(getAll.error);
      };
      request.onerror = () => reject(request.error);
    });
  });

  expect(storedNotes).toHaveLength(1);
  expect(storedNotes[0]).toMatchObject({
    title: 'Test Note',
    content: 'This is stored in IndexedDB',
  });
});

test('clear IndexedDB for a clean test state', async ({ page }) => {
  await page.goto('/');

  // Delete the entire database
  await page.evaluate(() => {
    return new Promise((resolve, reject) => {
      const request = indexedDB.deleteDatabase('NotesDB');
      request.onsuccess = () => resolve(undefined);
      request.onerror = () => reject(request.error);
    });
  });

  await page.reload();
  await expect(page.getByText('No notes yet')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('offline-first app stores data in IndexedDB', async ({ page }) => {
  await page.goto('/notes');

  await page.getByRole('button', { name: 'New note' }).click();
  await page.getByRole('textbox', { name: 'Title' }).fill('Test Note');
  await page.getByRole('textbox', { name: 'Content' }).fill('This is stored in IndexedDB');
  await page.getByRole('button', { name: 'Save' }).click();

  const storedNotes = await page.evaluate(() => {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('NotesDB', 1);
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction('notes', 'readonly');
        const store = tx.objectStore('notes');
        const getAll = store.getAll();
        getAll.onsuccess = () => resolve(getAll.result);
        getAll.onerror = () => reject(getAll.error);
      };
      request.onerror = () => reject(request.error);
    });
  });

  expect(storedNotes).toHaveLength(1);
  expect(storedNotes[0]).toMatchObject({
    title: 'Test Note',
    content: 'This is stored in IndexedDB',
  });
});
```

### Notifications

**Use when**: Your app uses the browser Notification API to show desktop notifications.
**Avoid when**: Notifications are purely server-side (push without Notification API).

Playwright cannot capture the actual system notification. Instead, mock the Notification constructor and verify the app calls it correctly.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('app triggers a browser notification on new message', async ({ browser }) => {
  const context = await browser.newContext({
    permissions: ['notifications'],
  });
  const page = await context.newPage();

  // Intercept Notification constructor to capture calls
  await page.evaluate(() => {
    (window as any).__notifications = [];
    const OriginalNotification = window.Notification;
    (window as any).Notification = class MockNotification {
      constructor(title: string, options?: NotificationOptions) {
        (window as any).__notifications.push({ title, ...options });
      }
      static get permission() { return 'granted'; }
      static requestPermission() { return Promise.resolve('granted' as NotificationPermission); }
    };
  });

  await page.goto('/chat');

  // Simulate receiving a message that triggers a notification
  await page.evaluate(() => {
    window.dispatchEvent(new CustomEvent('new-message', {
      detail: { from: 'Alice', text: 'Hey there!' },
    }));
  });

  // Check the notification was created with correct content
  const notifications = await page.evaluate(() => (window as any).__notifications);
  expect(notifications).toHaveLength(1);
  expect(notifications[0].title).toBe('New message from Alice');
  expect(notifications[0].body).toBe('Hey there!');

  await context.close();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('app triggers a browser notification on new message', async ({ browser }) => {
  const context = await browser.newContext({
    permissions: ['notifications'],
  });
  const page = await context.newPage();

  await page.evaluate(() => {
    window.__notifications = [];
    window.Notification = class MockNotification {
      constructor(title, options) {
        window.__notifications.push({ title, ...options });
      }
      static get permission() { return 'granted'; }
      static requestPermission() { return Promise.resolve('granted'); }
    };
  });

  await page.goto('/chat');

  await page.evaluate(() => {
    window.dispatchEvent(new CustomEvent('new-message', {
      detail: { from: 'Alice', text: 'Hey there!' },
    }));
  });

  const notifications = await page.evaluate(() => window.__notifications);
  expect(notifications).toHaveLength(1);
  expect(notifications[0].title).toBe('New message from Alice');
  await context.close();
});
```

## Decision Guide

| Browser API | How to Test | Key Configuration |
|---|---|---|
| Geolocation | `geolocation` context option + `permissions: ['geolocation']` | `context.setGeolocation()` for mid-test changes |
| Permissions (any) | `permissions` array in context options | `context.grantPermissions()` / `context.clearPermissions()` |
| Clipboard | Grant `clipboard-read`/`clipboard-write` + `page.evaluate(navigator.clipboard...)` | Requires secure context (HTTPS or localhost) |
| Notifications | Mock `Notification` constructor via `page.evaluate` | Grant `notifications` permission; capture constructor calls |
| Camera / Microphone | Chromium `--use-fake-device-for-media-stream` launch arg | Only works in Chromium; grant `camera`/`microphone` permissions |
| localStorage | `page.evaluate(() => localStorage.getItem/setItem(...))` | Set before navigation or reload to take effect |
| sessionStorage | `page.evaluate(() => sessionStorage.getItem/setItem(...))` | Scoped to the browsing session; cleared on context close |
| IndexedDB | `page.evaluate` with `indexedDB.open()` | Wrap in Promises for async operations |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Set `geolocation` without granting the permission | `getCurrentPosition` returns permission error | Always pair `geolocation` with `permissions: ['geolocation']` |
| Test clipboard without secure context | `navigator.clipboard` throws in non-HTTPS contexts | Use `localhost` or configure HTTPS in your test server |
| Access localStorage before navigating to the origin | `page.evaluate` runs in `about:blank` context initially | `page.goto('/')` first, then set localStorage, then reload |
| Store test tokens in localStorage directly | Bypasses auth flow; may mask real login bugs | Use `storageState` or proper auth fixtures |
| Rely on IndexedDB state from a previous test | Tests must be independent | Clear or delete the database in test setup |
| Skip cleanup of injected mocks (Notification, etc.) | Mock leaks into subsequent tests if using the same context | Each test gets a fresh context by default; only a concern with shared contexts |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `geolocation` returns `undefined` in the app | Permission not granted | Add `permissions: ['geolocation']` to context options |
| Clipboard `readText()` throws `DOMException` | Missing clipboard permissions or non-secure context | Grant `clipboard-read`; ensure HTTPS or localhost |
| `localStorage.getItem()` returns `null` after `setItem` | Set was done on a different origin or before navigation | Verify you navigated to the correct origin before calling `setItem` |
| Camera not working in Firefox/WebKit | Fake media devices are Chromium-only | Skip camera tests on non-Chromium browsers or mock `getUserMedia` via `page.evaluate` |
| IndexedDB `evaluate` returns `undefined` | Forgot to return the Promise | Ensure the `page.evaluate` callback returns `new Promise(...)` |
| Permissions change not reflected | App caches permission state on load | Reload the page after `grantPermissions()` or `clearPermissions()` |

## Related

- [core/configuration.md](configuration.md) -- global geolocation/permissions in config
- [core/service-workers-and-pwa.md](service-workers-and-pwa.md) -- offline and cache testing using IndexedDB and service workers
- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) -- wrap browser API setup in reusable fixtures
- [core/debugging.md](debugging.md) -- inspecting storage and permissions in Playwright traces
