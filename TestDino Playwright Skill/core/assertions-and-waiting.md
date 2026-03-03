# Assertions and Waiting

> **When to use**: Every time you write an `expect()` call, wait for a condition, or wonder why a test is flaky due to timing.
> **Prerequisites**: [core/locators.md](locators.md) for locator strategies used in examples.

## Quick Reference

```typescript
// Web-first (auto-retry) — ALWAYS prefer these
await expect(page.getByRole('button', { name: 'Submit' })).toBeVisible();
await expect(page.getByRole('heading')).toHaveText('Dashboard');
await expect(page.getByRole('listitem')).toHaveCount(5);

// Negative — auto-retries until condition is met
await expect(page.getByRole('dialog')).not.toBeVisible();

// Soft — collect failures, don't stop test
await expect.soft(page.getByRole('heading')).toHaveText('Title');

// Polling — non-DOM async conditions
await expect.poll(() => getUserCount()).toBe(10);

// Retry a block — multiple assertions that must pass together
await expect(async () => { /* assertions */ }).toPass();
```

## Patterns

### Web-First Assertions (Auto-Retry)

**Use when**: Asserting anything about a locator — visibility, text, attributes, CSS, count, values.
**Avoid when**: Asserting on an already-resolved JavaScript value (use non-retrying assertions instead).

Web-first assertions automatically retry until the condition is met or the timeout expires. They are the backbone of reliable Playwright tests.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('web-first assertions demo', async ({ page }) => {
  await page.goto('/products');

  // Visibility
  await expect(page.getByRole('heading', { name: 'Products' })).toBeVisible();

  // Text — exact match
  await expect(page.getByTestId('total')).toHaveText('Total: $99.00');

  // Text — partial match (substring or regex)
  await expect(page.getByTestId('total')).toContainText('$99');
  await expect(page.getByTestId('total')).toHaveText(/Total: \$\d+\.\d{2}/);

  // Element count
  await expect(page.getByRole('listitem')).toHaveCount(5);

  // Attribute
  await expect(page.getByRole('link', { name: 'Docs' })).toHaveAttribute('href', '/docs');

  // CSS property
  await expect(page.getByTestId('alert')).toHaveCSS('background-color', 'rgb(255, 0, 0)');

  // Input value
  await expect(page.getByLabel('Email')).toHaveValue('user@example.com');

  // Class (use toHaveClass for full match, regex for partial)
  await expect(page.getByTestId('card')).toHaveClass(/active/);

  // Enabled / disabled / checked
  await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();
  await expect(page.getByRole('checkbox')).toBeChecked();

  // Editable / focused / attached
  await expect(page.getByLabel('Name')).toBeEditable();
  await expect(page.getByLabel('Name')).toBeFocused();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('web-first assertions demo', async ({ page }) => {
  await page.goto('/products');

  await expect(page.getByRole('heading', { name: 'Products' })).toBeVisible();
  await expect(page.getByTestId('total')).toHaveText('Total: $99.00');
  await expect(page.getByTestId('total')).toContainText('$99');
  await expect(page.getByTestId('total')).toHaveText(/Total: \$\d+\.\d{2}/);
  await expect(page.getByRole('listitem')).toHaveCount(5);
  await expect(page.getByRole('link', { name: 'Docs' })).toHaveAttribute('href', '/docs');
  await expect(page.getByTestId('alert')).toHaveCSS('background-color', 'rgb(255, 0, 0)');
  await expect(page.getByLabel('Email')).toHaveValue('user@example.com');
  await expect(page.getByTestId('card')).toHaveClass(/active/);
  await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();
  await expect(page.getByRole('checkbox')).toBeChecked();
  await expect(page.getByLabel('Name')).toBeEditable();
  await expect(page.getByLabel('Name')).toBeFocused();
});
```

### Non-Retrying Assertions

**Use when**: The value is already resolved — a JavaScript variable, an API response body, a page title from `page.title()`, or a URL from `page.url()`.
**Avoid when**: Asserting on anything that might change asynchronously in the DOM. Use web-first assertions instead.

Non-retrying assertions run once. If they fail, they fail immediately.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('non-retrying assertions for resolved values', async ({ page }) => {
  await page.goto('/api/health');

  // Already-resolved values — no retry needed
  const title = await page.title();
  expect(title).toBe('Health Check');

  const url = page.url();
  expect(url).toContain('/api/health');

  // API response body
  const response = await page.request.get('/api/users');
  const body = await response.json();
  expect(body.users).toHaveLength(3);
  expect(response.status()).toBe(200);

  // Snapshot (value comparison, not retrying)
  expect(body).toMatchObject({ status: 'healthy', users: expect.any(Array) });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('non-retrying assertions for resolved values', async ({ page }) => {
  await page.goto('/api/health');

  const title = await page.title();
  expect(title).toBe('Health Check');

  const url = page.url();
  expect(url).toContain('/api/health');

  const response = await page.request.get('/api/users');
  const body = await response.json();
  expect(body.users).toHaveLength(3);
  expect(response.status()).toBe(200);

  expect(body).toMatchObject({ status: 'healthy', users: expect.any(Array) });
});
```

### Negative Assertions

**Use when**: Verifying something has disappeared, been removed, or is not present.
**Avoid when**: Never.

Negative web-first assertions auto-retry until the condition is met. This is critical: `expect(locator).not.toBeVisible()` correctly waits for the element to disappear. It does not just check once.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('verify element disappears after action', async ({ page }) => {
  await page.goto('/notifications');

  // Dismiss a notification
  await page.getByRole('button', { name: 'Dismiss' }).click();

  // Auto-retries until the notification is gone — correct
  await expect(page.getByRole('alert')).not.toBeVisible();

  // Verify text is not present
  await expect(page.getByText('Error occurred')).not.toBeVisible();

  // Verify element is detached from DOM entirely
  await expect(page.getByTestId('modal')).not.toBeAttached();

  // Verify count dropped to zero
  await expect(page.getByRole('alert')).toHaveCount(0);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('verify element disappears after action', async ({ page }) => {
  await page.goto('/notifications');

  await page.getByRole('button', { name: 'Dismiss' }).click();

  await expect(page.getByRole('alert')).not.toBeVisible();
  await expect(page.getByText('Error occurred')).not.toBeVisible();
  await expect(page.getByTestId('modal')).not.toBeAttached();
  await expect(page.getByRole('alert')).toHaveCount(0);
});
```

**Gotcha**: `not.toBeVisible()` passes for elements that exist but are hidden AND for elements not in the DOM. If you specifically need to assert the element is removed from the DOM entirely (not just hidden), use `not.toBeAttached()`.

### Soft Assertions

**Use when**: You want to collect multiple failures in a single test without stopping at the first one. Common for form validation checks, dashboard content audits, or visual checklists.
**Avoid when**: Subsequent assertions depend on the result of earlier ones (if the first fails, later assertions may be meaningless).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('dashboard shows all expected widgets', async ({ page }) => {
  await page.goto('/dashboard');

  // All checks run even if earlier ones fail
  await expect.soft(page.getByTestId('revenue-widget')).toBeVisible();
  await expect.soft(page.getByTestId('users-widget')).toBeVisible();
  await expect.soft(page.getByTestId('orders-widget')).toBeVisible();
  await expect.soft(page.getByTestId('revenue-widget')).toContainText('$');
  await expect.soft(page.getByTestId('users-widget')).toContainText('active');

  // Test still fails if any soft assertion failed, but you see ALL failures in the report
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('dashboard shows all expected widgets', async ({ page }) => {
  await page.goto('/dashboard');

  await expect.soft(page.getByTestId('revenue-widget')).toBeVisible();
  await expect.soft(page.getByTestId('users-widget')).toBeVisible();
  await expect.soft(page.getByTestId('orders-widget')).toBeVisible();
  await expect.soft(page.getByTestId('revenue-widget')).toContainText('$');
  await expect.soft(page.getByTestId('users-widget')).toContainText('active');
});
```

**Tip**: Guard subsequent actions against soft-assertion failures when those actions would throw confusing errors.

```typescript
await expect.soft(page.getByRole('button', { name: 'Next' })).toBeVisible();
if (test.info().errors.length > 0) return; // bail out — no point continuing
await page.getByRole('button', { name: 'Next' }).click();
```

### Polling Assertions

**Use when**: Waiting for a non-DOM, non-locator async condition: API readiness, database state, file existence, polling a service.
**Avoid when**: The condition is about a DOM element. Use web-first assertions on locators.

`expect.poll()` repeatedly calls a function until the assertion passes.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('wait for background job to complete', async ({ page }) => {
  await page.goto('/jobs');
  await page.getByRole('button', { name: 'Start Export' }).click();

  // Poll an API endpoint until the job finishes
  await expect.poll(async () => {
    const response = await page.request.get('/api/jobs/latest');
    const job = await response.json();
    return job.status;
  }, {
    message: 'Expected export job to complete',
    timeout: 30_000,
    intervals: [1_000, 2_000, 5_000], // backoff: 1s, 2s, then every 5s
  }).toBe('completed');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('wait for background job to complete', async ({ page }) => {
  await page.goto('/jobs');
  await page.getByRole('button', { name: 'Start Export' }).click();

  await expect.poll(async () => {
    const response = await page.request.get('/api/jobs/latest');
    const job = await response.json();
    return job.status;
  }, {
    message: 'Expected export job to complete',
    timeout: 30_000,
    intervals: [1_000, 2_000, 5_000],
  }).toBe('completed');
});
```

### Retrying Assertion Blocks with `toPass()`

**Use when**: Multiple assertions or actions must pass together as a group, and the whole block should be retried if any part fails. Common for race conditions where data appears incrementally.
**Avoid when**: A single web-first assertion suffices.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('search results update correctly', async ({ page }) => {
  await page.goto('/search');

  await expect(async () => {
    await page.getByLabel('Search').fill('playwright');
    await page.getByRole('button', { name: 'Search' }).click();

    // Both must pass together — retries the whole block
    await expect(page.getByRole('listitem')).toHaveCount(10);
    await expect(page.getByRole('listitem').first()).toContainText('Playwright');
  }).toPass({
    timeout: 15_000,
    intervals: [1_000, 2_000, 5_000],
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('search results update correctly', async ({ page }) => {
  await page.goto('/search');

  await expect(async () => {
    await page.getByLabel('Search').fill('playwright');
    await page.getByRole('button', { name: 'Search' }).click();

    await expect(page.getByRole('listitem')).toHaveCount(10);
    await expect(page.getByRole('listitem').first()).toContainText('Playwright');
  }).toPass({
    timeout: 15_000,
    intervals: [1_000, 2_000, 5_000],
  });
});
```

### Custom Matchers

**Use when**: Domain-specific assertions you repeat across many tests — valid price format, date range, accessible form, etc.
**Avoid when**: The assertion is only used in one test. Inline it.

**TypeScript**
```typescript
// fixtures/custom-matchers.ts
import { expect, type Locator } from '@playwright/test';

expect.extend({
  async toHaveValidPrice(locator: Locator) {
    const assertionName = 'toHaveValidPrice';
    let pass: boolean;
    let matcherResult: any;

    try {
      await expect(locator).toHaveText(/^\$\d{1,3}(,\d{3})*\.\d{2}$/);
      pass = true;
    } catch (e: any) {
      matcherResult = e.matcherResult;
      pass = false;
    }

    const message = pass
      ? () => `${this.utils.matcherHint(assertionName, undefined, undefined, { isNot: this.isNot })}\n\nLocator: ${locator}\nExpected: not a valid price format\nReceived: ${matcherResult?.actual || 'valid price'}`
      : () => `${this.utils.matcherHint(assertionName, undefined, undefined, { isNot: this.isNot })}\n\nLocator: ${locator}\nExpected: valid price format ($X,XXX.XX)\nReceived: ${matcherResult?.actual || 'no text'}`;

    return { message, pass, name: assertionName, expected: 'valid price format', actual: matcherResult?.actual };
  },
});

// Declare types for TypeScript
export {};
declare global {
  namespace PlaywrightTest {
    interface Matchers<R, T> {
      toHaveValidPrice(): R;
    }
  }
}
```

```typescript
// tests/products.spec.ts
import { test, expect } from '@playwright/test';
import '../fixtures/custom-matchers';

test('product prices are valid', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByTestId('price-tag').first()).toHaveValidPrice();
});
```

**JavaScript**
```javascript
// fixtures/custom-matchers.js
const { expect } = require('@playwright/test');

expect.extend({
  async toHaveValidPrice(locator) {
    const assertionName = 'toHaveValidPrice';
    let pass;
    let matcherResult;

    try {
      await expect(locator).toHaveText(/^\$\d{1,3}(,\d{3})*\.\d{2}$/);
      pass = true;
    } catch (e) {
      matcherResult = e.matcherResult;
      pass = false;
    }

    const message = pass
      ? () => `Expected locator not to have valid price format`
      : () => `Expected locator to have valid price format ($X,XXX.XX), received: ${matcherResult?.actual || 'no text'}`;

    return { message, pass, name: assertionName };
  },
});
```

```javascript
// tests/products.spec.js
const { test, expect } = require('@playwright/test');
require('../fixtures/custom-matchers');

test('product prices are valid', async ({ page }) => {
  await page.goto('/products');
  await expect(page.getByTestId('price-tag').first()).toHaveValidPrice();
});
```

### Auto-Waiting (Actionability)

**Use when**: You don't need to "use" this — understand it. Every Playwright action (`click`, `fill`, `check`, `selectOption`, etc.) auto-waits for the target element to be actionable before proceeding.

Playwright checks before acting:
| Action | Waits for |
|---|---|
| `click()` | Attached, visible, stable (no animation), enabled, not obscured by another element |
| `fill()` | Attached, visible, enabled, editable |
| `check()` | Attached, visible, stable, enabled |
| `selectOption()` | Attached, visible, enabled |
| `hover()` | Attached, visible, stable |
| `type()` | Attached, visible, enabled, editable |

This means you almost never need explicit waits before actions. Do NOT write `await expect(button).toBeVisible()` before `await button.click()` — the click already waits for visibility.

### Explicit Waits

**Use when**: Waiting for navigation, network responses, or page load states that are not tied to a specific locator.
**Avoid when**: A web-first assertion on a locator would suffice.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('explicit waits for non-locator conditions', async ({ page }) => {
  await page.goto('/login');

  // Wait for navigation after form submit
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.waitForURL('/dashboard');
  // can also use glob: await page.waitForURL('**/dashboard');
  // or regex: await page.waitForURL(/.*dashboard/);

  // Wait for a specific API response
  const responsePromise = page.waitForResponse(
    (resp) => resp.url().includes('/api/user') && resp.status() === 200
  );
  await page.getByRole('button', { name: 'Refresh' }).click();
  const response = await responsePromise;
  const data = await response.json();
  expect(data.name).toBe('Test User');

  // Wait for a network request to be sent
  const requestPromise = page.waitForRequest('**/api/analytics');
  await page.getByRole('button', { name: 'Track' }).click();
  const request = await requestPromise;
  expect(request.method()).toBe('POST');

  // Wait for load state
  await page.waitForLoadState('networkidle'); // use sparingly — only for legacy apps
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('explicit waits for non-locator conditions', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.waitForURL('/dashboard');

  const responsePromise = page.waitForResponse(
    (resp) => resp.url().includes('/api/user') && resp.status() === 200
  );
  await page.getByRole('button', { name: 'Refresh' }).click();
  const response = await responsePromise;
  const data = await response.json();
  expect(data.name).toBe('Test User');

  const requestPromise = page.waitForRequest('**/api/analytics');
  await page.getByRole('button', { name: 'Track' }).click();
  const request = await requestPromise;
  expect(request.method()).toBe('POST');

  await page.waitForLoadState('networkidle');
});
```

**Critical pattern**: Always set up `waitForResponse` / `waitForRequest` BEFORE the action that triggers it. Otherwise you have a race condition.

```typescript
// CORRECT — promise registered before the click
const responsePromise = page.waitForResponse('**/api/data');
await page.getByRole('button', { name: 'Load' }).click();
const response = await responsePromise;

// WRONG — response may already have arrived before waitForResponse is registered
await page.getByRole('button', { name: 'Load' }).click();
const response = await page.waitForResponse('**/api/data'); // race condition!
```

### Assertion Timeouts

**Use when**: A specific assertion needs more or less time than the global default.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// Per-assertion timeout
test('slow element appears eventually', async ({ page }) => {
  await page.goto('/slow-dashboard');

  await expect(page.getByTestId('heavy-chart')).toBeVisible({
    timeout: 30_000, // override for this one assertion
  });
});

// Per-test timeout
test('long-running flow', async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto('/import');
  await page.getByRole('button', { name: 'Import CSV' }).click();
  await expect(page.getByText('Import complete')).toBeVisible({ timeout: 60_000 });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('slow element appears eventually', async ({ page }) => {
  await page.goto('/slow-dashboard');

  await expect(page.getByTestId('heavy-chart')).toBeVisible({
    timeout: 30_000,
  });
});

test('long-running flow', async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto('/import');
  await page.getByRole('button', { name: 'Import CSV' }).click();
  await expect(page.getByText('Import complete')).toBeVisible({ timeout: 60_000 });
});
```

**Global timeout** in `playwright.config.ts`:
```typescript
export default defineConfig({
  expect: {
    timeout: 10_000, // default is 5_000 — increase for slow apps
  },
  timeout: 30_000,   // per-test timeout (default 30_000)
});
```

## Decision Guide

| Scenario | Recommended Approach | Why |
|---|---|---|
| Element visible / hidden | `expect(locator).toBeVisible()` / `.not.toBeVisible()` | Auto-retries, handles timing |
| Text content check | `expect(locator).toHaveText()` or `.toContainText()` | Auto-retries; use `toContainText` for substring |
| Element count | `expect(locator).toHaveCount(n)` | Retries until count matches |
| Input value | `expect(locator).toHaveValue('x')` | Auto-retries on the locator |
| Element attribute | `expect(locator).toHaveAttribute('href', '/x')` | Auto-retries |
| CSS property | `expect(locator).toHaveCSS('color', 'rgb(0,0,0)')` | Auto-retries; use computed RGB values |
| Element gone from DOM | `expect(locator).not.toBeAttached()` | Distinguishes hidden vs. removed |
| URL changed | `page.waitForURL('/path')` or `expect(page).toHaveURL('/path')` | `toHaveURL` auto-retries; `waitForURL` blocks |
| Page title | `expect(page).toHaveTitle('Title')` | Auto-retries |
| API response status | `expect(response.status()).toBe(200)` | Already resolved — non-retrying |
| Background job / polling | `expect.poll(() => fetchStatus())` | Retries a function, not a locator |
| Multiple assertions as one | `expect(async () => { ... }).toPass()` | Retries the entire block |
| Multiple independent checks | `expect.soft(locator)` | Collects all failures |
| Resolved JS value | `expect(value).toBe(x)` | No retry needed |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `await page.waitForTimeout(2000)` | Arbitrary delay. Too slow when fast, too short when slow. Flaky. | Use a web-first assertion: `await expect(locator).toBeVisible()` |
| `const visible = await el.isVisible(); expect(visible).toBe(true)` | `isVisible()` resolves once — no retry. Race condition. | `await expect(el).toBeVisible()` |
| `try { await expect(el).toBeVisible() } catch { /* ignore */ }` | Swallows real failures. Masks bugs. | Use `expect.soft()` or restructure the test |
| `expect(locator).toBeVisible().then(...)` | Missing `await`. Assertion runs detached, test passes before it resolves. | Always `await expect(locator).toBeVisible()` |
| `await expect(btn).toBeVisible(); await btn.click()` | Redundant. `click()` auto-waits for visibility. | Just `await btn.click()` |
| `await page.waitForLoadState('networkidle')` before every action | `networkidle` is fragile (long-poll, analytics, websockets break it). Slows tests. | Wait for a specific element or URL instead |
| `expect(await el.textContent()).toBe('X')` | Resolves text once — no retry. | `await expect(el).toHaveText('X')` |
| `expect(await page.locator('.item').count()).toBe(5)` | Resolves count once — no retry. | `await expect(page.locator('.item')).toHaveCount(5)` |
| Using `toPass()` for a single assertion | Unnecessary complexity. | Use the web-first assertion directly |
| Huge timeout per assertion (>60s) | Hides real performance problems. Tests become unbearably slow on failure. | Fix the app or split the test. Use 10-30s max. |

## Troubleshooting

### "Timed out 5000ms waiting for expect(...).toBeVisible()"

**Cause**: The element never appeared within the assertion timeout. Common reasons:
1. Wrong locator — element exists but locator doesn't match.
2. Element is behind a loading spinner or inside a collapsed section.
3. Network request that populates the element is slow.

**Fix**:
- Run with `--ui` or `--debug` to visually inspect the page state at failure time.
- Check the locator matches in the browser console: `playwright.$(selector)`.
- Increase timeout for genuinely slow operations: `{ timeout: 15_000 }`.
- Verify the locator targets the right element: `await expect(locator).toHaveCount(1)` first.

### "expect.soft: Test finished with X failed assertions"

**Cause**: Soft assertions collected failures but you have no immediate visibility into which ones.

**Fix**: Check the HTML report (`npx playwright show-report`). Each soft failure is listed with its locator, expected value, and actual value. Group related soft assertions under `test.step()` for better readability.

### "Expected '  Dashboard  ' to have text 'Dashboard'"

**Cause**: `toHaveText()` performs full text match including normalization, but whitespace mismatch still trips people up when elements have unusual rendering.

**Fix**:
- Use `toContainText('Dashboard')` for a substring match that is more resilient to whitespace.
- Use regex: `toHaveText(/Dashboard/)`.
- Check for zero-width spaces or special Unicode characters with `--debug`.

## Related

- [core/locators.md](locators.md) — locator strategies used in assertion targets
- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) — custom fixtures for reusable assertion setup
- [core/debugging.md](debugging.md) — debugging assertion failures with UI mode and traces
- [core/flaky-tests.md](flaky-tests.md) — fixing timing-related flakiness
- [core/error-index.md](error-index.md) — specific error messages and fixes
