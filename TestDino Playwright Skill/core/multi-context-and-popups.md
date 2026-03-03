# Multi-Context, Popups, and New Windows

> **When to use**: Handling popup windows, new tabs, OAuth authorization flows, payment gateway redirects, multi-tab coordination, and any scenario where your application opens additional browser windows or tabs.
> **Prerequisites**: [core/assertions-and-waiting.md](assertions-and-waiting.md), [core/fixtures-and-hooks.md](fixtures-and-hooks.md)

## Quick Reference

```typescript
// Catch a popup triggered by a click
const popupPromise = page.waitForEvent('popup');
await page.getByRole('button', { name: 'Open preview' }).click();
const popup = await popupPromise;
await popup.waitForLoadState();
await expect(popup.getByRole('heading')).toContainText('Preview');

// List all open pages in a context
const allPages = context.pages();
console.log(`Open tabs: ${allPages.length}`);
```

**Key concept**: In Playwright, a "popup" is any new page opened by `window.open()`, `target="_blank"` links, or JavaScript-triggered new windows. They all fire the `popup` event on the originating page.

## Patterns

### Handling Basic Popups

**Use when**: A user action opens a new tab or window and you need to interact with it.
**Avoid when**: The "popup" is actually a modal dialog within the same page -- use `getByRole('dialog')` instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('handle popup opened by target="_blank" link', async ({ page }) => {
  await page.goto('/help');

  // Set up the popup listener BEFORE the action that triggers it
  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Documentation' }).click();
  const popup = await popupPromise;

  // Wait for the popup to load
  await popup.waitForLoadState();

  // Interact with the popup
  await expect(popup.getByRole('heading', { level: 1 })).toContainText('Documentation');
  expect(popup.url()).toContain('/docs');

  // Close the popup when done
  await popup.close();
});

test('handle popup opened by window.open()', async ({ page }) => {
  await page.goto('/reports');

  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('button', { name: 'Print report' }).click();
  const popup = await popupPromise;

  await popup.waitForLoadState();
  await expect(popup.getByTestId('print-preview')).toBeVisible();

  // The original page is still accessible
  await expect(page.getByRole('heading', { name: 'Reports' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('handle popup opened by target="_blank" link', async ({ page }) => {
  await page.goto('/help');

  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Documentation' }).click();
  const popup = await popupPromise;

  await popup.waitForLoadState();
  await expect(popup.getByRole('heading', { level: 1 })).toContainText('Documentation');

  await popup.close();
});
```

### OAuth Popup Flows

**Use when**: Your app opens a third-party OAuth window (Google, GitHub, Microsoft, etc.) for authentication.
**Avoid when**: You can bypass OAuth entirely by injecting auth tokens directly -- see [core/authentication.md](authentication.md).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('Google OAuth popup flow', async ({ page }) => {
  await page.goto('/login');

  // Listen for the popup before clicking the OAuth button
  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('button', { name: 'Sign in with Google' }).click();
  const oauthPopup = await popupPromise;

  // Wait for the OAuth provider page to load
  await oauthPopup.waitForLoadState();
  expect(oauthPopup.url()).toContain('accounts.google.com');

  // Fill in credentials on the OAuth provider page
  await oauthPopup.getByLabel('Email or phone').fill('testuser@gmail.com');
  await oauthPopup.getByRole('button', { name: 'Next' }).click();
  await oauthPopup.getByLabel('Enter your password').fill('test-password');
  await oauthPopup.getByRole('button', { name: 'Next' }).click();

  // The popup closes automatically after authorization
  // Wait for the original page to receive the auth callback
  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});

test('GitHub OAuth popup flow', async ({ page }) => {
  await page.goto('/login');

  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('button', { name: 'Sign in with GitHub' }).click();
  const popup = await popupPromise;

  await popup.waitForLoadState();
  expect(popup.url()).toContain('github.com');

  await popup.getByLabel('Username or email address').fill('testuser');
  await popup.getByLabel('Password').fill('test-password');
  await popup.getByRole('button', { name: 'Sign in' }).click();

  // Authorize the app if prompted
  const authorizeButton = popup.getByRole('button', { name: 'Authorize' });
  if (await authorizeButton.isVisible({ timeout: 3000 }).catch(() => false)) {
    await authorizeButton.click();
  }

  // Popup closes, original page redirects
  await page.waitForURL('/dashboard');
  await expect(page.getByText(/Welcome/)).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('GitHub OAuth popup flow', async ({ page }) => {
  await page.goto('/login');

  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('button', { name: 'Sign in with GitHub' }).click();
  const popup = await popupPromise;

  await popup.waitForLoadState();
  await popup.getByLabel('Username or email address').fill('testuser');
  await popup.getByLabel('Password').fill('test-password');
  await popup.getByRole('button', { name: 'Sign in' }).click();

  await page.waitForURL('/dashboard');
  await expect(page.getByText(/Welcome/)).toBeVisible();
});
```

### Payment Gateway Popups

**Use when**: Checkout flows open a payment provider in a new window (PayPal, 3D Secure verification).
**Avoid when**: The payment gateway loads in an iframe on the same page -- use `frameLocator` instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('PayPal popup checkout flow', async ({ page }) => {
  await page.goto('/checkout');

  await page.getByLabel('Email').fill('buyer@example.com');
  await page.getByRole('button', { name: 'Proceed to payment' }).click();

  // PayPal opens in a popup
  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('button', { name: 'Pay with PayPal' }).click();
  const paypalPopup = await popupPromise;

  await paypalPopup.waitForLoadState();
  expect(paypalPopup.url()).toContain('paypal.com');

  // Complete PayPal flow
  await paypalPopup.getByLabel('Email').fill('buyer@paypal-test.com');
  await paypalPopup.getByRole('button', { name: 'Next' }).click();
  await paypalPopup.getByLabel('Password').fill('test-password');
  await paypalPopup.getByRole('button', { name: 'Log In' }).click();
  await paypalPopup.getByRole('button', { name: 'Complete Purchase' }).click();

  // Popup closes, return to original page
  await page.waitForURL('/order/confirmation');
  await expect(page.getByText('Payment successful')).toBeVisible();
});

test('3D Secure verification popup', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByLabel('Card number').fill('4000000000003220'); // 3DS test card
  await page.getByLabel('Expiry').fill('12/28');
  await page.getByLabel('CVC').fill('123');
  await page.getByRole('button', { name: 'Pay' }).click();

  // 3DS challenge opens in popup or iframe -- handle both
  const popupPromise = page.waitForEvent('popup', { timeout: 5000 }).catch(() => null);
  const popup = await popupPromise;

  if (popup) {
    await popup.waitForLoadState();
    await popup.getByRole('button', { name: 'Complete authentication' }).click();
  } else {
    // Fallback: 3DS in iframe
    const frame = page.frameLocator('iframe[name*="challenge"]');
    await frame.getByRole('button', { name: 'Complete authentication' }).click();
  }

  await expect(page.getByText('Payment successful')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('PayPal popup checkout flow', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByRole('button', { name: 'Proceed to payment' }).click();

  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('button', { name: 'Pay with PayPal' }).click();
  const paypalPopup = await popupPromise;

  await paypalPopup.waitForLoadState();
  await paypalPopup.getByLabel('Email').fill('buyer@paypal-test.com');
  await paypalPopup.getByRole('button', { name: 'Next' }).click();
  await paypalPopup.getByLabel('Password').fill('test-password');
  await paypalPopup.getByRole('button', { name: 'Log In' }).click();
  await paypalPopup.getByRole('button', { name: 'Complete Purchase' }).click();

  await page.waitForURL('/order/confirmation');
  await expect(page.getByText('Payment successful')).toBeVisible();
});
```

### Multi-Tab Coordination

**Use when**: Testing scenarios where multiple tabs share state -- real-time collaboration, shopping cart sync, or session management across tabs.
**Avoid when**: Each tab is independent and can be tested in separate test cases.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('cart updates reflect across tabs', async ({ context }) => {
  // Open two tabs in the same context (shared cookies/storage)
  const page1 = await context.newPage();
  const page2 = await context.newPage();

  await page1.goto('/products');
  await page2.goto('/cart');

  // Add item in tab 1
  await page1.getByRole('button', { name: 'Add to cart' }).first().click();

  // Tab 2 should reflect the update (via WebSocket, polling, or storage event)
  await expect(page2.getByTestId('cart-count')).toHaveText('1', { timeout: 5000 });
});

test('logout in one tab logs out all tabs', async ({ context }) => {
  const page1 = await context.newPage();
  const page2 = await context.newPage();

  // Both tabs are on authenticated pages
  await page1.goto('/dashboard');
  await page2.goto('/settings');

  // Log out from tab 1
  await page1.getByRole('button', { name: 'Log out' }).click();
  await page1.waitForURL('/login');

  // Tab 2 should redirect to login on next action or automatically
  await page2.reload();
  expect(page2.url()).toContain('/login');
});

test('manage multiple tabs with context.pages()', async ({ context, page }) => {
  await page.goto('/dashboard');

  // Open several new tabs
  const popupPromise1 = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Report A' }).click();
  const tab1 = await popupPromise1;

  const popupPromise2 = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Report B' }).click();
  const tab2 = await popupPromise2;

  // List all pages in this context
  const allPages = context.pages();
  expect(allPages).toHaveLength(3); // original + 2 popups

  // Interact with specific tabs
  await tab1.waitForLoadState();
  await expect(tab1.getByRole('heading')).toContainText('Report A');

  await tab2.waitForLoadState();
  await expect(tab2.getByRole('heading')).toContainText('Report B');

  // Close tabs when done
  await tab2.close();
  await tab1.close();
  expect(context.pages()).toHaveLength(1);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('cart updates reflect across tabs', async ({ context }) => {
  const page1 = await context.newPage();
  const page2 = await context.newPage();

  await page1.goto('/products');
  await page2.goto('/cart');

  await page1.getByRole('button', { name: 'Add to cart' }).first().click();
  await expect(page2.getByTestId('cart-count')).toHaveText('1', { timeout: 5000 });
});

test('manage tabs with context.pages()', async ({ context, page }) => {
  await page.goto('/dashboard');

  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Report A' }).click();
  const newTab = await popupPromise;

  expect(context.pages()).toHaveLength(2);
  await newTab.close();
  expect(context.pages()).toHaveLength(1);
});
```

### Download Triggers in New Tabs

**Use when**: A download is triggered by opening a new tab (e.g., PDF generation that opens in a new window before downloading).
**Avoid when**: The download starts directly without opening a new tab -- use `page.waitForEvent('download')` directly.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('PDF download from new tab', async ({ page }) => {
  await page.goto('/invoices');

  // Some apps open the PDF in a new tab, which then triggers a download
  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Download Invoice #123' }).click();
  const popup = await popupPromise;

  // The popup may directly trigger a download
  const downloadPromise = popup.waitForEvent('download');
  const download = await downloadPromise;

  expect(download.suggestedFilename()).toContain('invoice');
  const path = await download.path();
  expect(path).toBeTruthy();

  await popup.close();
});

test('export opens in new tab then auto-downloads', async ({ page }) => {
  await page.goto('/reports');

  // Handle both: popup that downloads AND popup that shows content
  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('button', { name: 'Export CSV' }).click();
  const popup = await popupPromise;

  // Try to catch a download; if no download, the popup has the content
  try {
    const download = await popup.waitForEvent('download', { timeout: 5000 });
    const filename = download.suggestedFilename();
    expect(filename).toMatch(/\.csv$/);
    await download.saveAs(`./downloads/${filename}`);
  } catch {
    // No download event — content displayed in the popup
    const content = await popup.textContent('body');
    expect(content).toContain('Report Data');
  }

  await popup.close();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('PDF download from new tab', async ({ page }) => {
  await page.goto('/invoices');

  const popupPromise = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Download Invoice #123' }).click();
  const popup = await popupPromise;

  const downloadPromise = popup.waitForEvent('download');
  const download = await downloadPromise;

  expect(download.suggestedFilename()).toContain('invoice');
  await popup.close();
});
```

### Multi-Context for Isolated Sessions

**Use when**: Testing interactions between different users (e.g., admin and regular user, two chat participants).
**Avoid when**: You only need a single user perspective -- a single context is sufficient.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('admin sees user changes in real-time', async ({ browser }) => {
  // Create separate contexts for two users (separate sessions)
  const adminContext = await browser.newContext();
  const userContext = await browser.newContext();

  const adminPage = await adminContext.newPage();
  const userPage = await userContext.newPage();

  // Admin logs in and watches the user list
  await adminPage.goto('/admin/users');

  // User signs up
  await userPage.goto('/register');
  await userPage.getByLabel('Name').fill('New User');
  await userPage.getByLabel('Email').fill('newuser@example.com');
  await userPage.getByLabel('Password').fill('password123');
  await userPage.getByRole('button', { name: 'Register' }).click();

  // Admin should see the new user appear
  await expect(adminPage.getByText('newuser@example.com')).toBeVisible({ timeout: 10000 });

  await adminContext.close();
  await userContext.close();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('admin sees user changes in real-time', async ({ browser }) => {
  const adminContext = await browser.newContext();
  const userContext = await browser.newContext();

  const adminPage = await adminContext.newPage();
  const userPage = await userContext.newPage();

  await adminPage.goto('/admin/users');

  await userPage.goto('/register');
  await userPage.getByLabel('Name').fill('New User');
  await userPage.getByLabel('Email').fill('newuser@example.com');
  await userPage.getByLabel('Password').fill('password123');
  await userPage.getByRole('button', { name: 'Register' }).click();

  await expect(adminPage.getByText('newuser@example.com')).toBeVisible({ timeout: 10000 });

  await adminContext.close();
  await userContext.close();
});
```

## Decision Guide

| Scenario | Approach | Why |
|---|---|---|
| `target="_blank"` link | `page.waitForEvent('popup')` | Playwright fires `popup` for all new windows/tabs |
| `window.open()` call | `page.waitForEvent('popup')` | Same mechanism regardless of how the window opens |
| OAuth login popup | `waitForEvent('popup')` + interact + wait for close | OAuth providers redirect back and close the popup |
| Payment popup (PayPal) | `waitForEvent('popup')` + complete flow | Same as OAuth but with payment-specific UI |
| Download in new tab | `popup.waitForEvent('download')` | Catch the download event on the popup page |
| Multiple tabs, same user | Open pages in the same `context` | Shared cookies, localStorage, session |
| Multiple users (separate sessions) | Create separate `browser.newContext()` per user | Isolated cookies, storage, auth state |
| Tab sync testing | Multiple `context.newPage()` + assert shared state | Tests real-time state synchronization |
| Popup that may or may not appear | `waitForEvent('popup', { timeout })` with try/catch | Graceful handling of conditional popups |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Clicking then calling `waitForEvent('popup')` | Popup may open before listener is registered (race condition) | Set up `waitForEvent` BEFORE the click |
| Using `context.pages()[1]` to get a popup | Index order is not guaranteed; brittle | Use `waitForEvent('popup')` which returns the exact page |
| Forgetting `popup.waitForLoadState()` | Popup page may not be loaded when you interact with it | Always call `waitForLoadState()` after receiving the popup |
| Not closing popups after test | Leaked pages consume memory and may affect subsequent tests | Close popups with `popup.close()` in the test or use fixtures |
| Using separate `browser.newContext()` when tabs should share state | Separate contexts have separate cookies/sessions | Use `context.newPage()` for tabs in the same session |
| Using `context.newPage()` for isolated users | Pages in the same context share state | Use `browser.newContext()` for separate user sessions |
| `page.waitForTimeout()` after popup trigger | Popup timing is unpredictable | Use `page.waitForEvent('popup')` which resolves when the popup opens |
| Catching popup on the wrong page | Popup event fires on the page that triggered it | Listen for `popup` on the page where the click/action happens |

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `waitForEvent('popup')` times out | The action did not open a new window; it navigated in the same tab | Check if the link has `target="_blank"` or if `window.open` is called |
| Popup opens but is blank | Popup is still loading; you interacted too early | Add `await popup.waitForLoadState()` before interacting |
| Popup URL is `about:blank` | Popup is created empty, then navigated by JavaScript | Wait for `popup.waitForURL()` with the expected URL pattern |
| OAuth popup is blocked by browser | Pop-up blocker is active | Playwright disables pop-up blocking by default; check if a browser arg re-enables it |
| Two popups open but only one is caught | `waitForEvent` resolves for the first event only | Use `page.on('popup', callback)` to catch all popups, or chain two `waitForEvent` calls |
| `context.pages()` returns unexpected count | Previous test left pages open | Close all extra pages in `afterEach` or use per-test contexts |
| Popup closes before interaction completes | The app or OAuth provider auto-closes after timeout | Increase test speed or remove `slowMo`; interact with the popup immediately |
| Cross-origin popup interaction fails | Popup navigated to a different origin | Playwright handles cross-origin popups; ensure you are not setting `--disable-web-security` |

## Related

- [core/authentication.md](authentication.md) -- bypassing OAuth popups with stored auth state
- [core/multi-user-and-collaboration.md](multi-user-and-collaboration.md) -- multi-user real-time collaboration testing
- [core/file-operations.md](file-operations.md) -- file download handling without popups
- [core/third-party-integrations.md](third-party-integrations.md) -- mocking OAuth providers to avoid real popups
- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) -- fixtures for multi-context setups
