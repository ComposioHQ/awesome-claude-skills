# Iframes and Shadow DOM

> **When to use**: When your application embeds content in `<iframe>` elements (payment widgets, third-party embeds, legacy modules) or uses Web Components with Shadow DOM (design systems, custom elements, Salesforce Lightning).
> **Prerequisites**: [core/locators.md](locators.md), [core/assertions-and-waiting.md](assertions-and-waiting.md)

## Quick Reference

```typescript
// Iframes — use frameLocator to reach inside
const frame = page.frameLocator('iframe[title="Payment"]');
await frame.getByLabel('Card number').fill('4242424242424242');

// Nested iframes — chain frameLocator calls
const inner = page.frameLocator('#outer').frameLocator('#inner');
await inner.getByRole('button', { name: 'Submit' }).click();

// Shadow DOM — Playwright pierces open shadow roots automatically
await page.getByRole('button', { name: 'Toggle' }).click();       // auto-pierces
await page.locator('my-component').getByText('Hello').click();     // auto-pierces
```

## Patterns

### Basic iframe Interaction with `frameLocator()`

**Use when**: You need to interact with content inside an `<iframe>` -- payment forms, embedded editors, captchas, third-party widgets.
**Avoid when**: The content is in the main frame. Never use `frameLocator` for Shadow DOM.

`frameLocator()` returns a locator-like object scoped to the iframe's document. All standard locator methods work inside it.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('complete payment inside Stripe iframe', async ({ page }) => {
  await page.goto('/checkout');

  // Locate the iframe by its title, name, or a CSS selector
  const paymentFrame = page.frameLocator('iframe[title="Secure payment"]');

  // Use normal locators inside the frame
  await paymentFrame.getByLabel('Card number').fill('4242424242424242');
  await paymentFrame.getByLabel('Expiry').fill('12/28');
  await paymentFrame.getByLabel('CVC').fill('123');
  await paymentFrame.getByRole('button', { name: 'Pay' }).click();

  // Assertion on content inside the iframe
  await expect(paymentFrame.getByText('Payment successful')).toBeVisible();

  // Assertion on the parent page (outside the iframe)
  await expect(page.getByRole('heading', { name: 'Order confirmed' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('complete payment inside Stripe iframe', async ({ page }) => {
  await page.goto('/checkout');

  const paymentFrame = page.frameLocator('iframe[title="Secure payment"]');
  await paymentFrame.getByLabel('Card number').fill('4242424242424242');
  await paymentFrame.getByLabel('Expiry').fill('12/28');
  await paymentFrame.getByLabel('CVC').fill('123');
  await paymentFrame.getByRole('button', { name: 'Pay' }).click();

  await expect(paymentFrame.getByText('Payment successful')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Order confirmed' })).toBeVisible();
});
```

### Selecting the Right iframe

**Use when**: Multiple iframes exist on the page or the iframe has no obvious identifier.
**Avoid when**: There is only one iframe and a simple `page.frameLocator('iframe')` works.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('interact with the correct iframe among many', async ({ page }) => {
  await page.goto('/dashboard');

  // By title attribute (best — accessible and stable)
  const chatFrame = page.frameLocator('iframe[title="Live chat"]');

  // By name attribute
  const reportFrame = page.frameLocator('iframe[name="analytics-report"]');

  // By src URL pattern
  const adFrame = page.frameLocator('iframe[src*="ads.example.com"]');

  // By index — when nothing else works (0-indexed)
  const thirdFrame = page.frameLocator('iframe').nth(2);

  // By parent container — scope to a section first
  const sidebar = page.getByRole('complementary');
  const sidebarFrame = sidebar.frameLocator('iframe');

  await chatFrame.getByRole('textbox', { name: 'Message' }).fill('Help');
  await expect(reportFrame.getByRole('heading')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('interact with the correct iframe among many', async ({ page }) => {
  await page.goto('/dashboard');

  const chatFrame = page.frameLocator('iframe[title="Live chat"]');
  const reportFrame = page.frameLocator('iframe[name="analytics-report"]');
  const adFrame = page.frameLocator('iframe[src*="ads.example.com"]');
  const thirdFrame = page.frameLocator('iframe').nth(2);

  await chatFrame.getByRole('textbox', { name: 'Message' }).fill('Help');
  await expect(reportFrame.getByRole('heading')).toBeVisible();
});
```

### Nested Iframes

**Use when**: An iframe contains another iframe (common in complex widget hierarchies, ad containers, or embedded third-party tools).
**Avoid when**: There is only one level of iframe nesting.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('interact with deeply nested iframe content', async ({ page }) => {
  await page.goto('/embed-page');

  // Chain frameLocator calls for each level of nesting
  const outerFrame = page.frameLocator('#widget-container');
  const innerFrame = outerFrame.frameLocator('#payment-form');

  await innerFrame.getByLabel('Amount').fill('99.99');
  await innerFrame.getByRole('button', { name: 'Confirm' }).click();

  // Three levels deep
  const deepFrame = page
    .frameLocator('#level-1')
    .frameLocator('#level-2')
    .frameLocator('#level-3');
  await expect(deepFrame.getByText('Success')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('interact with deeply nested iframe content', async ({ page }) => {
  await page.goto('/embed-page');

  const outerFrame = page.frameLocator('#widget-container');
  const innerFrame = outerFrame.frameLocator('#payment-form');

  await innerFrame.getByLabel('Amount').fill('99.99');
  await innerFrame.getByRole('button', { name: 'Confirm' }).click();

  const deepFrame = page
    .frameLocator('#level-1')
    .frameLocator('#level-2')
    .frameLocator('#level-3');
  await expect(deepFrame.getByText('Success')).toBeVisible();
});
```

### Cross-Origin Iframes

**Use when**: The iframe loads content from a different domain (payment providers, OAuth flows, third-party embeds).
**Avoid when**: The iframe is same-origin.

Playwright handles cross-origin iframes transparently. `frameLocator()` works regardless of origin. No special configuration is needed.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('complete OAuth login in cross-origin iframe', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Sign in with Google' }).click();

  // The OAuth provider renders in a cross-origin iframe or popup
  // For iframes:
  const oauthFrame = page.frameLocator('iframe[src*="accounts.google.com"]');
  await oauthFrame.getByLabel('Email').fill('user@gmail.com');
  await oauthFrame.getByRole('button', { name: 'Next' }).click();
});

test('cross-origin payment widget', async ({ page }) => {
  await page.goto('/checkout');

  // Stripe, PayPal, etc. load in cross-origin iframes
  const stripeFrame = page.frameLocator('iframe[src*="js.stripe.com"]');

  // All locator methods work across origins
  await stripeFrame.getByLabel('Card number').fill('4242424242424242');
  await stripeFrame.getByLabel('MM / YY').fill('12 / 28');
  await stripeFrame.getByLabel('CVC').fill('123');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('cross-origin payment widget', async ({ page }) => {
  await page.goto('/checkout');

  const stripeFrame = page.frameLocator('iframe[src*="js.stripe.com"]');
  await stripeFrame.getByLabel('Card number').fill('4242424242424242');
  await stripeFrame.getByLabel('MM / YY').fill('12 / 28');
  await stripeFrame.getByLabel('CVC').fill('123');
});
```

### Using the Frame API for Advanced Scenarios

**Use when**: You need to access the frame's URL, wait for frame navigation, or run `evaluate` inside the frame.
**Avoid when**: `frameLocator()` covers your needs. It is simpler and auto-waits.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('use Frame API for URL checks and evaluate', async ({ page }) => {
  await page.goto('/dashboard');

  // Get the Frame object (not FrameLocator)
  const frame = page.frame({ url: /analytics\.example\.com/ });
  expect(frame).not.toBeNull();

  // Check the frame's URL
  expect(frame!.url()).toContain('analytics.example.com');

  // Run JavaScript inside the frame
  const title = await frame!.evaluate(() => document.title);
  expect(title).toBe('Analytics Dashboard');

  // Wait for a frame to navigate
  const frameNavPromise = page.waitForEvent('framenavigated', {
    predicate: (f) => f.url().includes('/reports'),
  });
  await page.frameLocator('iframe[name="analytics"]')
    .getByRole('link', { name: 'Reports' }).click();
  await frameNavPromise;
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('use Frame API for URL checks and evaluate', async ({ page }) => {
  await page.goto('/dashboard');

  const frame = page.frame({ url: /analytics\.example\.com/ });
  expect(frame).not.toBeNull();

  expect(frame.url()).toContain('analytics.example.com');

  const title = await frame.evaluate(() => document.title);
  expect(title).toBe('Analytics Dashboard');
});
```

### Shadow DOM -- Automatic Piercing

**Use when**: Your app uses Web Components with open Shadow DOM. This is the default behavior -- no special configuration needed.
**Avoid when**: The shadow root is closed (see workaround below).

Playwright's `locator()`, `getByRole()`, `getByText()`, and all semantic locators pierce open Shadow DOM by default.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('interact with web components using Shadow DOM', async ({ page }) => {
  await page.goto('/design-system-demo');

  // getByRole pierces shadow roots automatically
  await page.getByRole('button', { name: 'Open menu' }).click();

  // locator() with CSS also pierces
  await page.locator('my-dropdown').getByRole('option', { name: 'Settings' }).click();

  // Nested web components — each shadow root is pierced
  await page
    .locator('my-app')
    .locator('my-sidebar')
    .getByRole('link', { name: 'Dashboard' })
    .click();

  // Assertions pierce too
  await expect(page.locator('my-card').getByText('Welcome back')).toBeVisible();

  // getByTestId pierces shadow DOM
  await expect(page.getByTestId('user-avatar')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('interact with web components using Shadow DOM', async ({ page }) => {
  await page.goto('/design-system-demo');

  await page.getByRole('button', { name: 'Open menu' }).click();
  await page.locator('my-dropdown').getByRole('option', { name: 'Settings' }).click();

  await page
    .locator('my-app')
    .locator('my-sidebar')
    .getByRole('link', { name: 'Dashboard' })
    .click();

  await expect(page.locator('my-card').getByText('Welcome back')).toBeVisible();
});
```

### Closed Shadow DOM Workaround

**Use when**: A third-party component uses `attachShadow({ mode: 'closed' })`, which blocks Playwright's auto-piercing.
**Avoid when**: The shadow root is open (the default). Auto-piercing handles open roots.

Override `attachShadow` before the page loads to force open mode.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('access closed shadow DOM by forcing open mode', async ({ page }) => {
  // Intercept attachShadow before the page scripts run
  await page.addInitScript(() => {
    const originalAttachShadow = Element.prototype.attachShadow;
    Element.prototype.attachShadow = function (init: ShadowRootInit) {
      return originalAttachShadow.call(this, { ...init, mode: 'open' });
    };
  });

  await page.goto('/third-party-widget');

  // Now the previously closed shadow root is accessible
  await page.locator('closed-component').getByRole('button', { name: 'Action' }).click();
  await expect(page.locator('closed-component').getByText('Done')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('access closed shadow DOM by forcing open mode', async ({ page }) => {
  await page.addInitScript(() => {
    const originalAttachShadow = Element.prototype.attachShadow;
    Element.prototype.attachShadow = function (init) {
      return originalAttachShadow.call(this, { ...init, mode: 'open' });
    };
  });

  await page.goto('/third-party-widget');

  await page.locator('closed-component').getByRole('button', { name: 'Action' }).click();
  await expect(page.locator('closed-component').getByText('Done')).toBeVisible();
});
```

### Web Components with Slots and Custom Events

**Use when**: Testing web components that use `<slot>` for content projection or dispatch custom events.
**Avoid when**: The component does not use slots or custom events.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('slotted content is visible through web component', async ({ page }) => {
  await page.goto('/components-demo');

  // Content projected into a <slot> is in the light DOM (not shadow)
  // Playwright sees it at its original location
  const card = page.locator('my-card');
  await expect(card.getByRole('heading', { name: 'Product Title' })).toBeVisible();
  await expect(card.getByText('Product description here')).toBeVisible();
});

test('listen for custom events from web components', async ({ page }) => {
  await page.goto('/components-demo');

  // Set up a listener for a custom event
  const eventPromise = page.evaluate(() => {
    return new Promise<{ detail: unknown }>((resolve) => {
      document.querySelector('my-color-picker')!.addEventListener(
        'color-change',
        (e: Event) => resolve({ detail: (e as CustomEvent).detail }),
        { once: true }
      );
    });
  });

  // Trigger the event by interacting with the component
  await page.locator('my-color-picker').getByRole('button', { name: 'Red' }).click();

  const event = await eventPromise;
  expect(event.detail).toEqual({ color: '#ff0000' });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('slotted content is visible through web component', async ({ page }) => {
  await page.goto('/components-demo');

  const card = page.locator('my-card');
  await expect(card.getByRole('heading', { name: 'Product Title' })).toBeVisible();
  await expect(card.getByText('Product description here')).toBeVisible();
});

test('listen for custom events from web components', async ({ page }) => {
  await page.goto('/components-demo');

  const eventPromise = page.evaluate(() => {
    return new Promise((resolve) => {
      document.querySelector('my-color-picker').addEventListener(
        'color-change',
        (e) => resolve({ detail: e.detail }),
        { once: true }
      );
    });
  });

  await page.locator('my-color-picker').getByRole('button', { name: 'Red' }).click();

  const event = await eventPromise;
  expect(event.detail).toEqual({ color: '#ff0000' });
});
```

## Decision Guide

| Scenario | Approach | Why |
|---|---|---|
| Content inside `<iframe>` | `page.frameLocator('selector')` | Returns a scoped locator for the iframe document |
| Multiple iframes on page | Use `title`, `name`, or `src` attribute selectors | More stable than index-based `nth()` |
| Nested iframes | Chain `frameLocator().frameLocator()` | Each call scopes one level deeper |
| Cross-origin iframe | Same as any iframe -- `frameLocator()` | Playwright handles cross-origin transparently |
| URL check or `evaluate` inside frame | `page.frame({ url })` (Frame API) | FrameLocator does not expose URL or evaluate |
| Open Shadow DOM | Standard locators -- no changes needed | Playwright pierces open shadow roots by default |
| Closed Shadow DOM | `addInitScript` to override `attachShadow` | Forces closed roots to open before page loads |
| Slotted content in Web Components | Locate within the custom element tag | Slotted content is light DOM, accessible normally |
| Non-piercing CSS (rare) | `css:light=selector` | Explicitly restricts to light DOM only |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `page.locator('#element-inside-iframe')` | Locators do not cross iframe boundaries | `page.frameLocator('iframe').locator('#element')` |
| `page.frameLocator('iframe').frameLocator('iframe')` without specific selectors | Matches wrong iframes when multiple exist | Use specific attributes: `frameLocator('iframe[title="..."]')` |
| `page.$('>>> .shadow-element')` | `>>>` piercing selector is not standard in Playwright | Use `page.locator('host-element').getByRole(...)` -- auto-piercing works |
| Using `contentFrame()` on a locator for routine interactions | More complex API than `frameLocator` for simple cases | Use `frameLocator()` -- simpler, auto-waits |
| `page.evaluate` to query inside shadow DOM | Bypasses Playwright's auto-waiting and retry logic | Use `page.locator()` which auto-pierces |
| Hardcoding iframe index (`nth(0)`) when attributes are available | Index changes when iframes are added/removed | Use `title`, `name`, or `src` pattern |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Locator times out inside iframe | Using `page.locator()` instead of `frameLocator().locator()` | Switch to `page.frameLocator('selector').locator(...)` |
| `frameLocator` returns no elements | Iframe not yet loaded when locator resolves | `frameLocator` auto-waits; check that the iframe selector matches |
| Cross-origin iframe content inaccessible | Rare: specific browser security policy | Playwright handles cross-origin; ensure you are not using `page.frame()` with wrong URL |
| Shadow DOM element not found with `locator()` | Shadow root is closed (`mode: 'closed'`) | Use `addInitScript` to override `attachShadow` to force open mode |
| `getByRole` finds elements from wrong shadow root | Multiple web components have elements with the same role and name | Scope the locator: `page.locator('my-specific-component').getByRole(...)` |
| Slotted content not found | Searching inside shadow root instead of light DOM | Slotted content stays in light DOM; locate it through the parent custom element |
| `frame.evaluate()` returns null | Frame navigated away or was removed from DOM | Re-acquire the frame reference after navigation |

## Related

- [core/locators.md](locators.md) -- locator fundamentals including frame and shadow DOM basics
- [core/browser-apis.md](browser-apis.md) -- testing browser APIs that may live inside iframes
- [core/canvas-and-webgl.md](canvas-and-webgl.md) -- canvas elements inside iframes or web components
- [core/debugging.md](debugging.md) -- using Playwright Inspector to identify iframe boundaries and shadow roots
