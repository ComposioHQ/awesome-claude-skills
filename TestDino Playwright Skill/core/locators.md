# Locators

> **When to use**: Every time you need to find an element on the page. Start here before reaching for CSS or XPath.
> **Prerequisites**: [core/configuration.md](configuration.md)

## Quick Reference

```typescript
// Priority order — use the first one that works:
page.getByRole('button', { name: 'Submit' })        // 1. Role (default)
page.getByLabel('Email address')                     // 2. Label (form fields)
page.getByText('Welcome back')                       // 3. Text (non-interactive)
page.getByPlaceholder('Search...')                    // 4. Placeholder
page.getByAltText('Company logo')                    // 5. Alt text (images)
page.getByTitle('Close dialog')                      // 6. Title attribute
page.getByTestId('checkout-summary')                 // 7. Test ID (last semantic option)
page.locator('css=.legacy-widget >> internal:role=button') // 8. CSS/XPath (last resort)
```

## Patterns

### Role-Based Locators (Default Choice)

**Use when**: Always. This is your starting point for every element.
**Avoid when**: The element has no ARIA role and adding one is outside your control.

Role-based locators mirror how assistive technology sees your page. They survive refactors, class renames, and component library swaps.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('role-based locators cover most UI elements', async ({ page }) => {
  await page.goto('/dashboard');

  // Buttons — matches <button>, <input type="submit">, role="button"
  await page.getByRole('button', { name: 'Save changes' }).click();

  // Links — matches <a href>
  await page.getByRole('link', { name: 'View profile' }).click();

  // Headings — use level to target specific h1-h6
  await expect(page.getByRole('heading', { name: 'Dashboard', level: 1 })).toBeVisible();

  // Text inputs — match by accessible name (label association)
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

  // Checkboxes and radios
  await page.getByRole('checkbox', { name: 'Remember me' }).check();
  await page.getByRole('radio', { name: 'Monthly billing' }).click();

  // Dropdowns — <select> elements
  await page.getByRole('combobox', { name: 'Country' }).selectOption('US');

  // Navigation landmarks
  const nav = page.getByRole('navigation', { name: 'Main' });
  await expect(nav.getByRole('link', { name: 'Settings' })).toBeVisible();

  // Tables
  const table = page.getByRole('table', { name: 'Recent orders' });
  await expect(table.getByRole('row')).toHaveCount(5);

  // Dialogs
  const dialog = page.getByRole('dialog', { name: 'Confirm deletion' });
  await dialog.getByRole('button', { name: 'Delete' }).click();

  // Exact matching — prevents "Log" from matching "Log out"
  await page.getByRole('button', { name: 'Log', exact: true }).click();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('role-based locators cover most UI elements', async ({ page }) => {
  await page.goto('/dashboard');

  await page.getByRole('button', { name: 'Save changes' }).click();
  await page.getByRole('link', { name: 'View profile' }).click();
  await expect(page.getByRole('heading', { name: 'Dashboard', level: 1 })).toBeVisible();
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('checkbox', { name: 'Remember me' }).check();
  await page.getByRole('radio', { name: 'Monthly billing' }).click();
  await page.getByRole('combobox', { name: 'Country' }).selectOption('US');

  const nav = page.getByRole('navigation', { name: 'Main' });
  await expect(nav.getByRole('link', { name: 'Settings' })).toBeVisible();

  const dialog = page.getByRole('dialog', { name: 'Confirm deletion' });
  await dialog.getByRole('button', { name: 'Delete' }).click();

  await page.getByRole('button', { name: 'Log', exact: true }).click();
});
```

### Label-Based Locators

**Use when**: Targeting form fields that have associated `<label>` elements or `aria-label`.
**Avoid when**: The element is not a form control. Use `getByRole` with the accessible name instead — it covers labels too.

`getByLabel` is a shortcut for form fields. It matches `<label for="">`, wrapping `<label>`, and `aria-label` / `aria-labelledby`.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('fill a registration form using labels', async ({ page }) => {
  await page.goto('/register');

  await page.getByLabel('First name').fill('Jane');
  await page.getByLabel('Last name').fill('Doe');
  await page.getByLabel('Email address').fill('jane@example.com');
  await page.getByLabel('Password', { exact: true }).fill('s3cure!Pass');
  await page.getByLabel('Confirm password').fill('s3cure!Pass');
  await page.getByLabel('I agree to the terms').check();

  await page.getByRole('button', { name: 'Create account' }).click();
  await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('fill a registration form using labels', async ({ page }) => {
  await page.goto('/register');

  await page.getByLabel('First name').fill('Jane');
  await page.getByLabel('Last name').fill('Doe');
  await page.getByLabel('Email address').fill('jane@example.com');
  await page.getByLabel('Password', { exact: true }).fill('s3cure!Pass');
  await page.getByLabel('Confirm password').fill('s3cure!Pass');
  await page.getByLabel('I agree to the terms').check();

  await page.getByRole('button', { name: 'Create account' }).click();
  await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
});
```

### Text-Based Locators

**Use when**: Targeting non-interactive content — status messages, paragraphs, banners, labels outside forms.
**Avoid when**: The element is a button, link, heading, or form field. Use `getByRole` instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('verify text content on the page', async ({ page }) => {
  await page.goto('/order/confirmation');

  // Substring match (default)
  await expect(page.getByText('Order confirmed')).toBeVisible();

  // Exact match — use when substring hits multiple elements
  await expect(page.getByText('Order #12345', { exact: true })).toBeVisible();

  // Regex match — for dynamic content patterns
  await expect(page.getByText(/Order #\d+/)).toBeVisible();

  // DO NOT use getByText for buttons or links:
  // Bad:  page.getByText('Submit')
  // Good: page.getByRole('button', { name: 'Submit' })
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('verify text content on the page', async ({ page }) => {
  await page.goto('/order/confirmation');

  await expect(page.getByText('Order confirmed')).toBeVisible();
  await expect(page.getByText('Order #12345', { exact: true })).toBeVisible();
  await expect(page.getByText(/Order #\d+/)).toBeVisible();
});
```

### Test ID Locators

**Use when**: No semantic locator works — the element has no accessible role, label, or stable text. Common with custom canvas-rendered components, complex data grids, or third-party widgets.
**Avoid when**: Any semantic locator (`getByRole`, `getByLabel`, `getByText`) can identify the element. Test IDs are invisible to users and assistive technology.

Configure the attribute name once in `playwright.config`:

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    testIdAttribute: 'data-testid', // default; change to match your codebase
  },
});
```

```typescript
import { test, expect } from '@playwright/test';

test('interact with a custom widget using test IDs', async ({ page }) => {
  await page.goto('/analytics');

  // Only when the chart component exposes no accessible roles
  const chart = page.getByTestId('revenue-chart');
  await expect(chart).toBeVisible();
  await chart.click({ position: { x: 150, y: 75 } });

  await expect(page.getByTestId('chart-tooltip')).toContainText('$12,400');
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  use: {
    testIdAttribute: 'data-testid',
  },
});
```

```javascript
const { test, expect } = require('@playwright/test');

test('interact with a custom widget using test IDs', async ({ page }) => {
  await page.goto('/analytics');

  const chart = page.getByTestId('revenue-chart');
  await expect(chart).toBeVisible();
  await chart.click({ position: { x: 150, y: 75 } });

  await expect(page.getByTestId('chart-tooltip')).toContainText('$12,400');
});
```

### CSS/XPath — Last Resort

**Use when**: You have zero control over the markup, no test IDs, no accessible names, and no way to add them. Legacy apps with generated class names and no semantic HTML.
**Avoid when**: Any other locator type works. Always.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('legacy app with no semantic markup', async ({ page }) => {
  await page.goto('/legacy-admin');

  // CSS — prefer short, structural selectors over fragile class chains
  await page.locator('table.report-grid td:has-text("Overdue")').first().click();

  // XPath — only when CSS cannot express the query (e.g., text + ancestor traversal)
  await page.locator('xpath=//td[contains(text(),"Overdue")]/ancestor::tr//button').click();

  // Combine CSS with Playwright pseudo-selectors for resilience
  await page.locator('.sidebar >> role=button[name="Expand"]').click();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('legacy app with no semantic markup', async ({ page }) => {
  await page.goto('/legacy-admin');

  await page.locator('table.report-grid td:has-text("Overdue")').first().click();
  await page.locator('xpath=//td[contains(text(),"Overdue")]/ancestor::tr//button').click();
  await page.locator('.sidebar >> role=button[name="Expand"]').click();
});
```

### Locator Chaining and Filtering

**Use when**: A single locator matches multiple elements and you need to narrow down by context, content, or position.
**Avoid when**: A direct `getByRole` with `name` already uniquely identifies the element.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('chaining and filtering locators', async ({ page }) => {
  await page.goto('/products');

  // Chain: scope a locator within another
  const productCard = page.getByRole('listitem').filter({ hasText: 'Running Shoes' });
  await productCard.getByRole('button', { name: 'Add to cart' }).click();

  // Filter by child locator — more precise than hasText
  const row = page.getByRole('row').filter({
    has: page.getByRole('cell', { name: 'Premium Plan' }),
  });
  await row.getByRole('button', { name: 'Upgrade' }).click();

  // Filter with hasNot — exclude elements containing a child
  const availableItems = page.getByRole('listitem').filter({
    hasNot: page.getByText('Sold out'),
  });
  await expect(availableItems).toHaveCount(3);

  // Filter with hasNotText — exclude by text content
  const nonFeatured = page.getByRole('listitem').filter({
    hasNotText: 'Featured',
  });

  // Positional: nth, first, last — use sparingly, only when order is stable
  const thirdItem = page.getByRole('listitem').nth(2); // 0-indexed
  const firstItem = page.getByRole('listitem').first();
  const lastItem = page.getByRole('listitem').last();

  // Combining multiple filters
  const activeAdminRow = page
    .getByRole('row')
    .filter({ has: page.getByRole('cell', { name: 'Admin' }) })
    .filter({ has: page.getByText('Active') });
  await expect(activeAdminRow).toHaveCount(1);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('chaining and filtering locators', async ({ page }) => {
  await page.goto('/products');

  const productCard = page.getByRole('listitem').filter({ hasText: 'Running Shoes' });
  await productCard.getByRole('button', { name: 'Add to cart' }).click();

  const row = page.getByRole('row').filter({
    has: page.getByRole('cell', { name: 'Premium Plan' }),
  });
  await row.getByRole('button', { name: 'Upgrade' }).click();

  const availableItems = page.getByRole('listitem').filter({
    hasNot: page.getByText('Sold out'),
  });
  await expect(availableItems).toHaveCount(3);

  const thirdItem = page.getByRole('listitem').nth(2);
  const firstItem = page.getByRole('listitem').first();
  const lastItem = page.getByRole('listitem').last();

  const activeAdminRow = page
    .getByRole('row')
    .filter({ has: page.getByRole('cell', { name: 'Admin' }) })
    .filter({ has: page.getByText('Active') });
  await expect(activeAdminRow).toHaveCount(1);
});
```

### Frame Locators

**Use when**: Interacting with content inside `<iframe>` or `<frame>` elements — payment widgets, embedded editors, third-party widgets.
**Avoid when**: The content is in the main frame or a Shadow DOM (use piercing instead).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('interact with content inside an iframe', async ({ page }) => {
  await page.goto('/checkout');

  // Locate the iframe, then use normal locators inside it
  const paymentFrame = page.frameLocator('iframe[title="Payment"]');
  await paymentFrame.getByLabel('Card number').fill('4242424242424242');
  await paymentFrame.getByLabel('Expiration').fill('12/28');
  await paymentFrame.getByLabel('CVC').fill('123');
  await paymentFrame.getByRole('button', { name: 'Pay' }).click();

  // Nested iframes — chain frameLocator calls
  const nestedFrame = page
    .frameLocator('#outer-frame')
    .frameLocator('#inner-frame');
  await expect(nestedFrame.getByText('Payment confirmed')).toBeVisible();

  // Frame by nth index — when no better selector exists
  const secondFrame = page.frameLocator('iframe').nth(1);
  await expect(secondFrame.getByRole('heading')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('interact with content inside an iframe', async ({ page }) => {
  await page.goto('/checkout');

  const paymentFrame = page.frameLocator('iframe[title="Payment"]');
  await paymentFrame.getByLabel('Card number').fill('4242424242424242');
  await paymentFrame.getByLabel('Expiration').fill('12/28');
  await paymentFrame.getByLabel('CVC').fill('123');
  await paymentFrame.getByRole('button', { name: 'Pay' }).click();

  const nestedFrame = page
    .frameLocator('#outer-frame')
    .frameLocator('#inner-frame');
  await expect(nestedFrame.getByText('Payment confirmed')).toBeVisible();

  const secondFrame = page.frameLocator('iframe').nth(1);
  await expect(secondFrame.getByRole('heading')).toBeVisible();
});
```

### Shadow DOM Piercing

**Use when**: Targeting elements inside web components that use Shadow DOM (custom elements, design system components, Salesforce Lightning).
**Avoid when**: The element is in a regular DOM or iframe.

Playwright pierces open Shadow DOM automatically with `locator()`. The `getByRole` / `getByText` family also pierces shadow roots by default.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('interact with Shadow DOM elements', async ({ page }) => {
  await page.goto('/design-system-demo');

  // getByRole automatically pierces open Shadow DOM — just use it normally
  await page.getByRole('button', { name: 'Toggle menu' }).click();

  // locator() with CSS also pierces shadow roots by default
  await page.locator('my-dropdown').getByRole('option', { name: 'Settings' }).click();

  // Chain into nested shadow DOMs
  await page
    .locator('my-app')
    .locator('my-sidebar')
    .getByRole('link', { name: 'Profile' })
    .click();

  // If you explicitly need non-piercing behavior (rare), use css=light/
  // await page.locator('css:light=.outer-only').click();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('interact with Shadow DOM elements', async ({ page }) => {
  await page.goto('/design-system-demo');

  await page.getByRole('button', { name: 'Toggle menu' }).click();
  await page.locator('my-dropdown').getByRole('option', { name: 'Settings' }).click();

  await page
    .locator('my-app')
    .locator('my-sidebar')
    .getByRole('link', { name: 'Profile' })
    .click();
});
```

### Dynamic Content — Waiting for Elements

**Use when**: Elements appear after API calls, animations, lazy loading, or route transitions.
**Avoid when**: The element is already on the page. Playwright auto-waits on actions, so explicit waits are rarely needed.

Never use `page.waitForTimeout()`. Use auto-waiting assertions or explicit event waits.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('handle dynamic content without manual waits', async ({ page }) => {
  await page.goto('/search');

  // Auto-waiting: actions like click(), fill() wait for the element automatically
  await page.getByRole('textbox', { name: 'Search' }).fill('playwright');
  await page.getByRole('button', { name: 'Search' }).click();

  // Web-first assertion: auto-retries until timeout (default 5s)
  await expect(page.getByRole('listitem')).toHaveCount(10);

  // Wait for a specific element to appear after an async operation
  await expect(page.getByRole('heading', { name: 'Results' })).toBeVisible();

  // Wait for loading indicators to disappear
  await expect(page.getByRole('progressbar')).toBeHidden();

  // Wait for network-dependent content: wait for response then assert
  const responsePromise = page.waitForResponse('**/api/search*');
  await page.getByRole('button', { name: 'Load more' }).click();
  await responsePromise;
  await expect(page.getByRole('listitem')).toHaveCount(20);

  // Wait for URL change after navigation
  await page.getByRole('link', { name: 'First result' }).click();
  await page.waitForURL('**/results/**');
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('handle dynamic content without manual waits', async ({ page }) => {
  await page.goto('/search');

  await page.getByRole('textbox', { name: 'Search' }).fill('playwright');
  await page.getByRole('button', { name: 'Search' }).click();

  await expect(page.getByRole('listitem')).toHaveCount(10);
  await expect(page.getByRole('heading', { name: 'Results' })).toBeVisible();
  await expect(page.getByRole('progressbar')).toBeHidden();

  const responsePromise = page.waitForResponse('**/api/search*');
  await page.getByRole('button', { name: 'Load more' }).click();
  await responsePromise;
  await expect(page.getByRole('listitem')).toHaveCount(20);

  await page.getByRole('link', { name: 'First result' }).click();
  await page.waitForURL('**/results/**');
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
});
```

## Decision Guide

| Element Type | Recommended Locator | Example | Why |
|---|---|---|---|
| Button | `getByRole('button', { name })` | `getByRole('button', { name: 'Submit' })` | Matches `<button>`, `<input type="submit">`, `role="button"` |
| Link | `getByRole('link', { name })` | `getByRole('link', { name: 'Home' })` | Matches any `<a href>` regardless of styling |
| Text input | `getByRole('textbox', { name })` | `getByRole('textbox', { name: 'Email' })` | Matches by accessible name (label) |
| Password input | `getByLabel()` | `getByLabel('Password')` | Password fields have no distinct role; label is the best match |
| Checkbox | `getByRole('checkbox', { name })` | `getByRole('checkbox', { name: 'Agree' })` | Also use `.check()` / `.uncheck()` instead of `.click()` |
| Radio button | `getByRole('radio', { name })` | `getByRole('radio', { name: 'Express' })` | Group radios with `getByRole('radiogroup')` |
| Select/dropdown | `getByRole('combobox', { name })` | `getByRole('combobox', { name: 'Country' })` | Native `<select>` maps to combobox role |
| Custom dropdown | `getByRole('listbox')` + `getByRole('option')` | Click trigger, then `getByRole('option', { name })` | ARIA listbox pattern for custom dropdowns |
| Heading | `getByRole('heading', { name, level })` | `getByRole('heading', { name: 'Dashboard', level: 2 })` | Use `level` to distinguish h1-h6 |
| Table | `getByRole('table', { name })` | `getByRole('table', { name: 'Users' })` | Chain with `getByRole('row')`, `getByRole('cell')` |
| Table row | `getByRole('row').filter({ has })` | `.filter({ has: getByRole('cell', { name: 'Jane' }) })` | Filter rows by cell content |
| Navigation | `getByRole('navigation', { name })` | `getByRole('navigation', { name: 'Main' })` | Matches `<nav>` with `aria-label` |
| Dialog/modal | `getByRole('dialog', { name })` | `getByRole('dialog', { name: 'Confirm' })` | Scope all dialog interactions under this |
| Tab | `getByRole('tab', { name })` | `getByRole('tab', { name: 'Settings' })` | Use with `getByRole('tabpanel')` |
| Image | `getByAltText()` | `getByAltText('User avatar')` | Matches the `alt` attribute |
| Form field (any) | `getByLabel()` | `getByLabel('Date of birth')` | Fallback when role is ambiguous (date pickers, custom inputs) |
| Static text | `getByText()` | `getByText('No results found')` | Non-interactive content only |
| No semantic markup | `getByTestId()` | `getByTestId('sparkline-chart')` | Last semantic option before CSS |
| Iframe content | `frameLocator()` then any locator | `frameLocator('#payment').getByLabel('Card')` | Required for cross-frame access |
| Shadow DOM | `getByRole()` / `locator()` | Works automatically | Playwright pierces open shadow roots by default |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `page.locator('.btn-primary')` | Breaks when CSS classes change (renames, CSS modules, Tailwind) | `page.getByRole('button', { name: 'Save' })` |
| `page.locator('#submit-btn')` | IDs are implementation details; often auto-generated | `page.getByRole('button', { name: 'Submit' })` |
| `page.locator('div > span:nth-child(3)')` | Breaks on any DOM restructure | `page.getByText('Expected content')` or `getByTestId()` |
| `page.locator('xpath=//div[@class="form"]//input[2]')` | Fragile, unreadable, position-dependent | `page.getByLabel('Last name')` |
| `page.getByText('Submit')` for a button | Text locators don't assert the element is interactive | `page.getByRole('button', { name: 'Submit' })` |
| `page.locator('.item').nth(0)` on dynamic lists | Index changes when items are added/removed/reordered | `.filter({ hasText: 'Specific item' })` |
| `page.getByText('Aceptar')` hardcoded i18n text | Fails when locale changes | `page.getByRole('button', { name: /accept/i })` or `getByTestId('confirm-btn')` |
| `await page.waitForTimeout(3000)` | Arbitrary delay; too slow in fast environments, too short in slow ones | `await expect(locator).toBeVisible()` |
| `page.locator('.card').locator('.card-title').locator('a')` | Deep CSS chaining breaks on any structural change | `page.getByRole('link', { name: 'Card title text' })` |
| `page.$('selector')` (ElementHandle API) | Returns a snapshot, not auto-waiting; deprecated pattern | `page.locator('selector')` — locators are lazy and auto-wait |
| `page.locator('text=Click here')` | Legacy text selector syntax | `page.getByText('Click here')` or `getByRole` with name |
| Multiple locators for one element in sequence | Each `locator()` call in a chain restarts the search | Store as variable: `const btn = page.getByRole('button', { name: 'Save' })` |

## Troubleshooting

### "strict mode violation" — locator matches multiple elements

**Cause**: Your locator is not specific enough and Playwright refuses to pick one for you.

```typescript
// Error: locator.click: strict mode violation, getByRole('button') resolved to 5 elements
await page.getByRole('button').click(); // Too broad

// Fix 1: Add a name filter
await page.getByRole('button', { name: 'Save' }).click();

// Fix 2: Scope within a parent
await page.getByRole('dialog').getByRole('button', { name: 'Save' }).click();

// Fix 3: Use exact matching when names are substrings of each other
await page.getByRole('button', { name: 'Save', exact: true }).click();

// Fix 4: Use filter to narrow down
await page.getByRole('button').filter({ hasText: 'Save draft' }).click();

// Debug: see what matched
console.log(await page.getByRole('button').all()); // list all matches
```

### Element exists but locator times out

**Cause**: The element is inside an iframe, Shadow DOM, or is obscured/hidden.

```typescript
// Check if element is inside an iframe
const frame = page.frameLocator('iframe');
await frame.getByRole('button', { name: 'Submit' }).click();

// Check if element is in a Shadow DOM — getByRole pierces automatically,
// but page.$() and CSS selectors may not. Switch to getByRole.

// Check if element is hidden (display: none, visibility: hidden, opacity: 0)
// Use toBeVisible() to confirm, or toBeAttached() if hidden is expected
await expect(page.getByRole('button', { name: 'Submit' })).toBeAttached();
```

### `getByRole` doesn't find the element

**Cause**: The element's implicit ARIA role doesn't match what you expect, or it has no role.

```typescript
// Debug: inspect the accessibility tree
const snapshot = await page.accessibility.snapshot();
console.log(JSON.stringify(snapshot, null, 2));

// Common mismatches:
// - <div onclick="..."> has no button role → add role="button" or use <button>
// - <input type="text"> with no label has no accessible name → add <label> or aria-label
// - <a> without href has no link role → add href or role="link"

// Fallback chain: try getByLabel → getByText → getByTestId → locator()
```

## Related

- [core/locator-strategy.md](locator-strategy.md) — deep-dive decision framework for choosing locator strategies at the project level
- [core/assertions-and-waiting.md](assertions-and-waiting.md) — pair locators with web-first assertions
- [pom/page-object-model.md](../pom/page-object-model.md) — encapsulate locators in page objects
- [core/iframes-and-shadow-dom.md](iframes-and-shadow-dom.md) — advanced iframe and Shadow DOM patterns
- [core/i18n-and-localization.md](i18n-and-localization.md) — locator strategies for internationalized apps
