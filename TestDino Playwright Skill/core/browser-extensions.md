# Browser Extensions

> **When to use**: Testing Chrome extensions — popups, content scripts, background service workers, or extension-injected UI. Requires Chromium and a persistent browser context.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/fixtures-and-hooks.md](fixtures-and-hooks.md)

## Quick Reference

```typescript
// Load an unpacked extension with a persistent context (Chromium only)
const context = await chromium.launchPersistentContext(userDataDir, {
  headless: false, // Extensions require headed mode
  args: [
    `--disable-extensions-except=${pathToExtension}`,
    `--load-extension=${pathToExtension}`,
  ],
});
```

**Hard constraints**: Extensions only work in Chromium. They require `launchPersistentContext` (not `browser.newContext`). Headed mode is mandatory — `headless: false` or use the `--headless=new` Chromium flag for "new headless" mode which supports extensions.

## Patterns

### Loading an Extension

**Use when**: You need to test any Chrome extension functionality.
**Avoid when**: You only need to test the web app that an extension interacts with — mock the extension's effects instead.

**TypeScript**
```typescript
import { test as base, expect, chromium, type BrowserContext } from '@playwright/test';
import path from 'path';

// Create a fixture that provides a context with the extension loaded
type ExtensionFixtures = {
  context: BrowserContext;
  extensionId: string;
};

export const test = base.extend<ExtensionFixtures>({
  // Override the default context to load the extension
  context: async ({}, use) => {
    const extensionPath = path.resolve(__dirname, '../my-extension');
    const context = await chromium.launchPersistentContext('', {
      headless: false,
      args: [
        `--disable-extensions-except=${extensionPath}`,
        `--load-extension=${extensionPath}`,
      ],
    });
    await use(context);
    await context.close();
  },

  // Extract the extension ID from the service worker URL
  extensionId: async ({ context }, use) => {
    let [background] = context.serviceWorkers();
    if (!background) {
      background = await context.waitForEvent('serviceworker');
    }
    const extensionId = background.url().split('/')[2];
    await use(extensionId);
  },
});

export { expect };
```

**JavaScript**
```javascript
const { test: base, expect, chromium } = require('@playwright/test');
const path = require('path');

const test = base.extend({
  context: async ({}, use) => {
    const extensionPath = path.resolve(__dirname, '../my-extension');
    const context = await chromium.launchPersistentContext('', {
      headless: false,
      args: [
        `--disable-extensions-except=${extensionPath}`,
        `--load-extension=${extensionPath}`,
      ],
    });
    await use(context);
    await context.close();
  },

  extensionId: async ({ context }, use) => {
    let [background] = context.serviceWorkers();
    if (!background) {
      background = await context.waitForEvent('serviceworker');
    }
    const extensionId = background.url().split('/')[2];
    await use(extensionId);
  },
});

module.exports = { test, expect };
```

### Testing Extension Popups

**Use when**: Your extension has a browser action popup (the UI that appears when clicking the extension icon).
**Avoid when**: The popup is trivial — test the content script or background logic instead.

**TypeScript**
```typescript
import { test, expect } from './extension-fixture';

test('extension popup displays saved bookmarks', async ({ page, extensionId }) => {
  // Navigate directly to the popup HTML
  await page.goto(`chrome-extension://${extensionId}/popup.html`);

  // Interact with popup UI using standard locators
  await expect(page.getByRole('heading', { name: 'My Bookmarks' })).toBeVisible();
  await page.getByRole('button', { name: 'Add current page' }).click();
  await expect(page.getByRole('listitem')).toHaveCount(1);
});

test('extension popup settings toggle works', async ({ page, extensionId }) => {
  await page.goto(`chrome-extension://${extensionId}/popup.html`);

  await page.getByRole('checkbox', { name: 'Enable notifications' }).check();
  await expect(page.getByText('Notifications enabled')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('./extension-fixture');

test('extension popup displays saved bookmarks', async ({ page, extensionId }) => {
  await page.goto(`chrome-extension://${extensionId}/popup.html`);

  await expect(page.getByRole('heading', { name: 'My Bookmarks' })).toBeVisible();
  await page.getByRole('button', { name: 'Add current page' }).click();
  await expect(page.getByRole('listitem')).toHaveCount(1);
});
```

### Testing Content Scripts

**Use when**: Your extension injects scripts or UI into web pages.
**Avoid when**: The content script only modifies data without visible effects — test via the background worker or storage.

**TypeScript**
```typescript
import { test, expect } from './extension-fixture';

test('content script injects price comparison widget', async ({ context }) => {
  const page = await context.newPage();
  await page.goto('https://example-shop.com/product/123');

  // Wait for the content script to inject its UI
  // The extension adds a shadow DOM element — Playwright pierces it automatically
  await expect(page.getByTestId('price-compare-widget')).toBeVisible({ timeout: 10000 });
  await expect(page.getByText('Best price: $29.99')).toBeVisible();
});

test('content script highlights search terms', async ({ context }) => {
  const page = await context.newPage();
  await page.goto('https://example.com/article');

  // Verify the content script added highlight spans
  const highlights = page.locator('.ext-highlight');
  await expect(highlights).toHaveCount(5);
  await expect(highlights.first()).toHaveCSS('background-color', 'rgb(255, 255, 0)');
});
```

**JavaScript**
```javascript
const { test, expect } = require('./extension-fixture');

test('content script injects price comparison widget', async ({ context }) => {
  const page = await context.newPage();
  await page.goto('https://example-shop.com/product/123');

  await expect(page.getByTestId('price-compare-widget')).toBeVisible({ timeout: 10000 });
  await expect(page.getByText('Best price: $29.99')).toBeVisible();
});
```

### Testing Background Service Workers

**Use when**: Your extension uses Manifest V3 service workers for background processing, alarms, or message passing.
**Avoid when**: The background logic is simple and already covered by popup or content script tests.

**TypeScript**
```typescript
import { test, expect } from './extension-fixture';

test('background worker processes messages correctly', async ({ context, extensionId }) => {
  const page = await context.newPage();
  await page.goto(`chrome-extension://${extensionId}/popup.html`);

  // Trigger an action that sends a message to the background worker
  await page.getByRole('button', { name: 'Sync data' }).click();

  // Verify the response from the background worker updates the popup
  await expect(page.getByText('Last synced: just now')).toBeVisible();
});

test('service worker handles extension storage', async ({ context, extensionId }) => {
  const page = await context.newPage();
  await page.goto(`chrome-extension://${extensionId}/popup.html`);

  // Set a value through the popup
  await page.getByLabel('API Key').fill('test-key-123');
  await page.getByRole('button', { name: 'Save' }).click();

  // Reload popup and verify persistence through the service worker
  await page.reload();
  await expect(page.getByLabel('API Key')).toHaveValue('test-key-123');
});
```

**JavaScript**
```javascript
const { test, expect } = require('./extension-fixture');

test('background worker processes messages correctly', async ({ context, extensionId }) => {
  const page = await context.newPage();
  await page.goto(`chrome-extension://${extensionId}/popup.html`);

  await page.getByRole('button', { name: 'Sync data' }).click();
  await expect(page.getByText('Last synced: just now')).toBeVisible();
});
```

### Testing Extension Options Page

**Use when**: Your extension has a dedicated options/settings page.
**Avoid when**: Settings are fully covered by popup tests.

**TypeScript**
```typescript
import { test, expect } from './extension-fixture';

test('options page saves preferences', async ({ page, extensionId }) => {
  await page.goto(`chrome-extension://${extensionId}/options.html`);

  await page.getByRole('combobox', { name: 'Theme' }).selectOption('dark');
  await page.getByRole('checkbox', { name: 'Auto-update' }).check();
  await page.getByRole('button', { name: 'Save' }).click();

  await expect(page.getByText('Settings saved')).toBeVisible();

  // Verify persistence after reload
  await page.reload();
  await expect(page.getByRole('combobox', { name: 'Theme' })).toHaveValue('dark');
  await expect(page.getByRole('checkbox', { name: 'Auto-update' })).toBeChecked();
});
```

**JavaScript**
```javascript
const { test, expect } = require('./extension-fixture');

test('options page saves preferences', async ({ page, extensionId }) => {
  await page.goto(`chrome-extension://${extensionId}/options.html`);

  await page.getByRole('combobox', { name: 'Theme' }).selectOption('dark');
  await page.getByRole('checkbox', { name: 'Auto-update' }).check();
  await page.getByRole('button', { name: 'Save' }).click();

  await expect(page.getByText('Settings saved')).toBeVisible();

  await page.reload();
  await expect(page.getByRole('combobox', { name: 'Theme' })).toHaveValue('dark');
  await expect(page.getByRole('checkbox', { name: 'Auto-update' })).toBeChecked();
});
```

## Decision Guide

| Scenario | Approach | Why |
|---|---|---|
| Test popup UI | Navigate to `chrome-extension://<id>/popup.html` | Direct access without needing to click the extension icon |
| Test content script effects | Load a real or test page, assert injected elements | Content scripts run automatically on matching URLs |
| Test background logic | Trigger via popup/content script, verify side effects | Cannot directly call service worker functions from Playwright |
| Test extension storage | Use popup to set values, reload, verify persistence | `chrome.storage` is only accessible from extension pages |
| Test options page | Navigate to `chrome-extension://<id>/options.html` | Same approach as popup testing |
| Test cross-page behavior | Open multiple pages in the same context | Persistent context shares extension state across tabs |
| Run in CI (headless) | Use `--headless=new` Chromium flag | New headless mode supports extensions unlike old headless |
| Test with multiple extensions | Add multiple paths to `--load-extension` | Comma-separate paths in the flag value |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `browser.newContext()` for extensions | Extensions require persistent context | `chromium.launchPersistentContext()` |
| `headless: true` without `--headless=new` | Old headless mode does not support extensions | Set `headless: false` or use `args: ['--headless=new']` |
| Testing on Firefox or WebKit | Extensions only work in Chromium | Skip extension tests for non-Chromium projects |
| Clicking the extension icon via coordinates | Fragile, toolbar layout varies | Navigate directly to `chrome-extension://<id>/popup.html` |
| Hardcoding the extension ID | IDs change between builds and machines | Extract dynamically from the service worker URL |
| Testing packed `.crx` files directly | Harder to debug, need to unpack first | Test the unpacked extension source directory |
| Sharing persistent context user data dir | State leaks between test runs | Use an empty string `''` for a temp directory |
| No timeout on content script assertions | Content scripts may load after page load | Use `{ timeout: 10000 }` on content script element assertions |

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Extension does not load | Wrong path in `--load-extension` | Use `path.resolve()` to get the absolute path to the extension directory |
| `context.serviceWorkers()` returns empty | Service worker not yet registered | Use `context.waitForEvent('serviceworker')` before extracting the ID |
| Popup page is blank | Popup HTML path is wrong | Check `manifest.json` for the correct `default_popup` path |
| Content script not injecting | Page URL does not match `matches` in manifest | Verify the URL pattern in `content_scripts[].matches` |
| Extension works locally but not in CI | CI uses old headless mode | Add `--headless=new` to launch args for CI |
| `chrome.storage` calls fail | Accessing storage from non-extension context | Only access storage through extension pages (popup, options, background) |
| Multiple extensions conflict | Both extensions modify the same page elements | Test each extension in its own persistent context |
| Tests are slow to start | Persistent context initialization overhead | Reuse context across tests in the same file with `test.describe` |

## Related

- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) -- building custom fixtures for extension contexts
- [core/service-workers-and-pwa.md](service-workers-and-pwa.md) -- service worker testing patterns (non-extension)
- [core/iframes-and-shadow-dom.md](iframes-and-shadow-dom.md) -- content scripts often inject Shadow DOM elements
- [core/configuration.md](configuration.md) -- project configuration for Chromium-only test suites
- [ci/ci-github-actions.md](../ci/ci-github-actions.md) -- CI setup for headed/extension tests
