# Common Pitfalls

> **When to use**: When learning Playwright, reviewing tests for common mistakes, or onboarding new team members to your test suite.

The 20 most common Playwright mistakes, ordered by how frequently they appear in real codebases. Each pitfall includes the symptom, root cause, and a complete fix.

---

## Pitfall 1: Using `page.waitForTimeout()` Instead of Assertions

**Symptom**: Tests are slow and flaky. They pass on fast machines but fail on slow CI runners.

**Why it happens**: Developers port habits from Selenium or Cypress where explicit waits were necessary. In Playwright, auto-retrying assertions handle timing automatically.

**Fix**: Replace every `waitForTimeout` with a web-first assertion or an explicit wait for a specific condition.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD
test('bad: arbitrary wait', async ({ page }) => {
  await page.goto('/dashboard');
  await page.getByRole('button', { name: 'Load' }).click();
  await page.waitForTimeout(3000);
  await expect(page.getByTestId('chart')).toBeVisible();
});

// GOOD
test('good: auto-retrying assertion', async ({ page }) => {
  await page.goto('/dashboard');
  await page.getByRole('button', { name: 'Load' }).click();
  await expect(page.getByTestId('chart')).toBeVisible();
});

// GOOD — when you need to wait for a specific network event
test('good: wait for response', async ({ page }) => {
  await page.goto('/dashboard');
  const responsePromise = page.waitForResponse('**/api/chart-data');
  await page.getByRole('button', { name: 'Load' }).click();
  await responsePromise;
  await expect(page.getByTestId('chart')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// BAD
test('bad: arbitrary wait', async ({ page }) => {
  await page.goto('/dashboard');
  await page.getByRole('button', { name: 'Load' }).click();
  await page.waitForTimeout(3000);
  await expect(page.getByTestId('chart')).toBeVisible();
});

// GOOD
test('good: auto-retrying assertion', async ({ page }) => {
  await page.goto('/dashboard');
  await page.getByRole('button', { name: 'Load' }).click();
  await expect(page.getByTestId('chart')).toBeVisible();
});
```

**The only acceptable use of `waitForTimeout`**: Debugging with `page.pause()` unavailable, or simulating real user "think time" in performance tests. Never in production test code.

---

## Pitfall 2: Not Awaiting Async Operations

**Symptom**: Tests pass unpredictably. Assertions run before actions complete. Error messages reference detached frames or closed pages.

**Why it happens**: Every Playwright API call is async. Missing a single `await` causes the next line to execute before the previous action finishes.

**Fix**: Always `await` every Playwright call. Enable the `@typescript-eslint/no-floating-promises` ESLint rule.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — missing await on click, assertion runs before navigation
test('bad: missing await', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password');
  page.getByRole('button', { name: 'Sign in' }).click(); // MISSING AWAIT
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});

// GOOD
test('good: all actions awaited', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// BAD
test('bad: missing await', async ({ page }) => {
  await page.goto('/login');
  page.getByRole('button', { name: 'Submit' }).click(); // MISSING AWAIT
  await expect(page.getByText('Success')).toBeVisible();
});

// GOOD
test('good: all actions awaited', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.getByText('Success')).toBeVisible();
});
```

**Prevention**: Add this ESLint config to catch floating promises at compile time:
```json
{
  "rules": {
    "@typescript-eslint/no-floating-promises": "error"
  }
}
```

---

## Pitfall 3: Using CSS Selectors Instead of Role-Based Locators

**Symptom**: Tests break whenever a CSS class name, DOM structure, or component library changes. Tests are hard to read because selectors look like `.btn-primary > span:nth-child(2)`.

**Why it happens**: Developers use what they know from jQuery or DevTools. CSS selectors are implementation details that change frequently.

**Fix**: Use Playwright's built-in locators that target accessible roles, labels, text, and test IDs.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — brittle CSS selectors
test('bad: CSS selectors', async ({ page }) => {
  await page.goto('/settings');
  await page.locator('.form-group:nth-child(3) input.form-control').fill('new value');
  await page.locator('button.btn.btn-primary.submit-btn').click();
  await expect(page.locator('.alert.alert-success')).toBeVisible();
});

// GOOD — role-based locators
test('good: accessible locators', async ({ page }) => {
  await page.goto('/settings');
  await page.getByLabel('Display name').fill('new value');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByRole('alert')).toHaveText('Settings saved');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// BAD
test('bad: CSS selectors', async ({ page }) => {
  await page.locator('.form-group:nth-child(3) input').fill('new value');
  await page.locator('button.btn-primary').click();
});

// GOOD
test('good: accessible locators', async ({ page }) => {
  await page.getByLabel('Display name').fill('new value');
  await page.getByRole('button', { name: 'Save' }).click();
});
```

**Locator priority** (most resilient to least):
1. `getByRole()` -- accessible role + name
2. `getByLabel()` -- form fields by label text
3. `getByPlaceholder()` -- inputs by placeholder
4. `getByText()` -- visible text content
5. `getByTestId()` -- stable `data-testid` attribute
6. CSS/XPath selectors -- last resort only

---

## Pitfall 4: Asserting on `isVisible()` Return Value Instead of `expect().toBeVisible()`

**Symptom**: Test passes when the element is not visible. Assertion is silently wrong. Flaky under timing pressure.

**Why it happens**: `isVisible()` returns a boolean at one point in time -- no retry. If the element has not appeared yet, it returns `false` and `expect(false).toBe(true)` fails immediately without waiting.

**Fix**: Always use `expect(locator).toBeVisible()`, which auto-retries until the element appears or the timeout expires.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — resolves once, no retry
test('bad: isVisible check', async ({ page }) => {
  await page.goto('/dashboard');
  const visible = await page.getByTestId('widget').isVisible();
  expect(visible).toBe(true); // Fails immediately if widget hasn't rendered yet
});

// GOOD — auto-retries for up to 5 seconds
test('good: toBeVisible assertion', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByTestId('widget')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// BAD
test('bad: isVisible check', async ({ page }) => {
  const visible = await page.getByTestId('widget').isVisible();
  expect(visible).toBe(true);
});

// GOOD
test('good: toBeVisible assertion', async ({ page }) => {
  await expect(page.getByTestId('widget')).toBeVisible();
});
```

This applies to all "resolve once" methods: `isVisible()`, `isEnabled()`, `isChecked()`, `textContent()`, `getAttribute()`, `inputValue()`. Always use the `expect(locator)` web-first assertion counterpart.

---

## Pitfall 5: Sharing Mutable State Between Parallel Tests

**Symptom**: Tests pass when run alone but fail in the full suite. Order-dependent failures. "Duplicate key" errors.

**Why it happens**: Module-level variables, shared database rows, or `beforeAll`-created state is mutated by one test and seen by another running in parallel.

**Fix**: Use test-scoped fixtures with unique data. Never store mutable state in module-level variables.

**TypeScript**
```typescript
import { test as base, expect } from '@playwright/test';

// BAD — module-level mutable state shared across parallel tests
let userId: string;

test.beforeAll(async ({ request }) => {
  const res = await request.post('/api/users', {
    data: { email: 'shared@test.com' },
  });
  userId = (await res.json()).id; // Every parallel worker overwrites this
});

test('bad: uses shared state', async ({ page }) => {
  await page.goto(`/users/${userId}`); // userId may be from another worker
});

// GOOD — test-scoped fixture with unique data per test
export const test = base.extend<{ testUser: { id: string; email: string } }>({
  testUser: async ({ request }, use) => {
    const email = `user-${Date.now()}-${Math.random().toString(36).slice(2)}@test.com`;
    const res = await request.post('/api/users', { data: { email } });
    const user = await res.json();

    await use({ id: user.id, email });

    await request.delete(`/api/users/${user.id}`);
  },
});

test('good: isolated data per test', async ({ page, testUser }) => {
  await page.goto(`/users/${testUser.id}`);
  await expect(page.getByText(testUser.email)).toBeVisible();
});
```

**JavaScript**
```javascript
const { test: base, expect } = require('@playwright/test');

// GOOD
const test = base.extend({
  testUser: async ({ request }, use) => {
    const email = `user-${Date.now()}-${Math.random().toString(36).slice(2)}@test.com`;
    const res = await request.post('/api/users', { data: { email } });
    const user = await res.json();

    await use({ id: user.id, email });

    await request.delete(`/api/users/${user.id}`);
  },
});

test('good: isolated data per test', async ({ page, testUser }) => {
  await page.goto(`/users/${testUser.id}`);
  await expect(page.getByText(testUser.email)).toBeVisible();
});

module.exports = { test };
```

---

## Pitfall 6: Not Using `baseURL` (Hardcoding Full URLs)

**Symptom**: Tests break when switching environments (local, staging, production). URL strings are duplicated everywhere.

**Why it happens**: Developers start with `page.goto('http://localhost:3000/login')` and never refactor.

**Fix**: Set `baseURL` in `playwright.config` and use relative paths in all tests.

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
  },
});
```

```typescript
import { test, expect } from '@playwright/test';

// BAD
test('bad: hardcoded URL', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
});

// GOOD
test('good: relative URL', async ({ page }) => {
  await page.goto('/login');
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
  },
});
```

```javascript
const { test, expect } = require('@playwright/test');

// BAD
test('bad: hardcoded URL', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
});

// GOOD
test('good: relative URL', async ({ page }) => {
  await page.goto('/login');
});
```

Run against different environments by setting the variable: `BASE_URL=https://staging.example.com npx playwright test`

---

## Pitfall 7: Using `page.$()` Instead of `page.locator()`

**Symptom**: Element handle is `null`. Stale element errors. No auto-waiting.

**Why it happens**: `page.$()` and `page.$$()` are ElementHandle APIs from Puppeteer. They resolve once and return a handle that can go stale. Locators are Playwright's replacement -- they are lazy and re-evaluate on every action.

**Fix**: Always use `page.locator()`, `page.getByRole()`, or other locator methods.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — ElementHandle API, resolves once, can go stale
test('bad: page.$ usage', async ({ page }) => {
  await page.goto('/products');
  const button = await page.$('.add-to-cart'); // null if not found, stale if DOM changes
  if (button) {
    await button.click();
  }
  const count = await page.$$('.cart-item');
  expect(count.length).toBe(1); // No auto-retry
});

// GOOD — locator API, lazy evaluation, auto-waiting
test('good: locator usage', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('button', { name: 'Add to cart' }).first().click();
  await expect(page.getByTestId('cart-item')).toHaveCount(1); // Auto-retries
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// BAD
test('bad: page.$ usage', async ({ page }) => {
  const button = await page.$('.add-to-cart');
  if (button) await button.click();
});

// GOOD
test('good: locator usage', async ({ page }) => {
  await page.getByRole('button', { name: 'Add to cart' }).first().click();
});
```

---

## Pitfall 8: Not Handling Navigation After Form Submission

**Symptom**: Test fails with "Target page, context or browser has been closed" or assertions fail because the page navigated away before the assertion ran.

**Why it happens**: Clicking a submit button triggers a full page navigation. The assertion runs against the old page that is being unloaded.

**Fix**: Wait for the navigation to complete before asserting on the new page.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — assertion runs before navigation completes
test('bad: no navigation handling', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  // Page is navigating — this may fail with "Execution context was destroyed"
  await expect(page.getByRole('heading')).toHaveText('Dashboard');
});

// GOOD — wait for URL to change, then assert
test('good: waitForURL after navigation', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading')).toHaveText('Dashboard');
});

// GOOD — alternative: use expect().toHaveURL() which auto-retries
test('good: toHaveURL assertion', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/.*dashboard/);
  await expect(page.getByRole('heading')).toHaveText('Dashboard');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// GOOD
test('good: waitForURL after navigation', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading')).toHaveText('Dashboard');
});
```

---

## Pitfall 9: Testing Against `localhost` in CI Without `webServer` Config

**Symptom**: Tests fail in CI with `ECONNREFUSED` on `localhost:3000`. Works locally because the dev server is already running.

**Why it happens**: CI runners start with a clean environment. No dev server is running unless you explicitly start one.

**Fix**: Use the `webServer` config option to start your app automatically.

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    baseURL: 'http://localhost:3000',
  },

  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    // Reuse existing server locally (faster), start fresh in CI
    reuseExistingServer: !process.env.CI,
    // Give the server time to start
    timeout: 120_000,
    // Capture server output for debugging startup failures
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  use: {
    baseURL: 'http://localhost:3000',
  },
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
```

For multiple servers (frontend + backend), pass an array:
```typescript
webServer: [
  { command: 'npm run start:api', url: 'http://localhost:4000/health', reuseExistingServer: !process.env.CI },
  { command: 'npm run start:web', url: 'http://localhost:3000', reuseExistingServer: !process.env.CI },
],
```

---

## Pitfall 10: Using `innerHTML` for Text Assertions Instead of `toHaveText()`

**Symptom**: Tests break when HTML structure changes. Assertions are fragile and hard to read.

**Why it happens**: Developers use `innerHTML()` or `textContent()` to get text and then assert on the resolved string. This resolves once with no retry.

**Fix**: Use `expect(locator).toHaveText()` or `expect(locator).toContainText()` for auto-retrying text assertions.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — resolves once, includes HTML tags, no retry
test('bad: innerHTML assertion', async ({ page }) => {
  await page.goto('/product/123');
  const html = await page.getByTestId('price').innerHTML();
  expect(html).toContain('$49.99'); // Brittle: depends on HTML structure
});

// BAD — textContent resolves once, no retry
test('bad: textContent assertion', async ({ page }) => {
  await page.goto('/product/123');
  const text = await page.getByTestId('price').textContent();
  expect(text).toBe('$49.99'); // No retry if text hasn't loaded yet
});

// GOOD — auto-retrying, no HTML dependency
test('good: toHaveText assertion', async ({ page }) => {
  await page.goto('/product/123');
  await expect(page.getByTestId('price')).toHaveText('$49.99');
});

// GOOD — partial match for flexible assertions
test('good: toContainText assertion', async ({ page }) => {
  await page.goto('/product/123');
  await expect(page.getByTestId('price')).toContainText('$49');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// BAD
test('bad: textContent assertion', async ({ page }) => {
  const text = await page.getByTestId('price').textContent();
  expect(text).toBe('$49.99');
});

// GOOD
test('good: toHaveText assertion', async ({ page }) => {
  await expect(page.getByTestId('price')).toHaveText('$49.99');
});
```

---

## Pitfall 11: Over-Mocking (Mocking Your Own API)

**Symptom**: All tests pass but the app is broken in production. Mocked responses drift from the real API. False confidence.

**Why it happens**: Developers mock every API call for speed and stability, including their own backend. The mocks become stale as the real API evolves.

**Fix**: Only mock external third-party services. Test your own API for real. Use `webServer` to run your backend during tests.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — mocking your own API removes confidence
test('bad: mocks own API', async ({ page }) => {
  await page.route('**/api/users/me', (route) =>
    route.fulfill({
      status: 200,
      body: JSON.stringify({ name: 'Test User', role: 'admin' }),
    })
  );
  await page.goto('/dashboard');
  await expect(page.getByText('Test User')).toBeVisible(); // Passes even if API is broken
});

// GOOD — mock only external services, test your own API for real
test('good: real API, mocked externals', async ({ page }) => {
  // Block third-party analytics and ads
  await page.route(/google-analytics|intercom|segment/, (route) => route.abort());

  // Stub a flaky external payment provider
  await page.route('**/api.stripe.com/**', (route) =>
    route.fulfill({
      status: 200,
      body: JSON.stringify({ status: 'succeeded' }),
    })
  );

  // Test against the real app API
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// GOOD — mock only external services
test('good: real API, mocked externals', async ({ page }) => {
  await page.route(/google-analytics|intercom|segment/, (route) => route.abort());

  await page.route('**/api.stripe.com/**', (route) =>
    route.fulfill({
      status: 200,
      body: JSON.stringify({ status: 'succeeded' }),
    })
  );

  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**When mocking your own API is acceptable**: Testing specific error states (500, 503, network timeout) or edge cases that are hard to reproduce with a real backend.

---

## Pitfall 12: Not Using `test.describe` for Grouping

**Symptom**: Test files are flat lists of unrelated tests. Shared configuration (`test.use()`, `test.beforeEach()`) cannot be scoped. HTML reports are hard to navigate.

**Why it happens**: Developers write tests as a flat list, never grouping related tests together.

**Fix**: Group related tests with `test.describe`. Use it for scoping shared setup, configuration overrides, and logical organization.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — flat list, no grouping, no shared context
test('admin can view users', async ({ page }) => { /* ... */ });
test('admin can delete user', async ({ page }) => { /* ... */ });
test('viewer cannot delete user', async ({ page }) => { /* ... */ });
test('viewer can view users', async ({ page }) => { /* ... */ });

// GOOD — grouped by role, scoped configuration
test.describe('admin users', () => {
  test.use({ storageState: '.auth/admin.json' });

  test.beforeEach(async ({ page }) => {
    await page.goto('/admin/users');
  });

  test('can view user list', async ({ page }) => {
    await expect(page.getByRole('table')).toBeVisible();
  });

  test('can delete a user', async ({ page }) => {
    await page.getByRole('row').first().getByRole('button', { name: 'Delete' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
  });
});

test.describe('viewer users', () => {
  test.use({ storageState: '.auth/viewer.json' });

  test('can view user list', async ({ page }) => {
    await page.goto('/admin/users');
    await expect(page.getByRole('table')).toBeVisible();
  });

  test('cannot see delete button', async ({ page }) => {
    await page.goto('/admin/users');
    await expect(page.getByRole('button', { name: 'Delete' })).not.toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('admin users', () => {
  test.use({ storageState: '.auth/admin.json' });

  test.beforeEach(async ({ page }) => {
    await page.goto('/admin/users');
  });

  test('can view user list', async ({ page }) => {
    await expect(page.getByRole('table')).toBeVisible();
  });

  test('can delete a user', async ({ page }) => {
    await page.getByRole('row').first().getByRole('button', { name: 'Delete' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
  });
});
```

---

## Pitfall 13: Using `beforeAll` for Per-Test Setup

**Symptom**: Tests that should be independent share state from `beforeAll`. One test modifies the state and subsequent tests fail.

**Why it happens**: Developers think `beforeAll` is "more efficient" because it runs once. But `beforeAll` creates worker-scoped state that all tests in the file share.

**Fix**: Use `beforeEach` for per-test setup, or use test-scoped fixtures for setup that needs teardown.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — beforeAll creates one user for all tests; tests mutate shared state
test.beforeAll(async ({ request }) => {
  // This user is shared across all tests in this file
  await request.post('/api/users', { data: { email: 'shared@test.com', name: 'Original' } });
});

test('updates user name', async ({ page }) => {
  await page.goto('/users/shared@test.com');
  await page.getByLabel('Name').fill('Updated');
  await page.getByRole('button', { name: 'Save' }).click();
  // Now the shared user has name "Updated" — other tests see this
});

test('checks user name is Original', async ({ page }) => {
  await page.goto('/users/shared@test.com');
  // FAILS — previous test changed the name
  await expect(page.getByLabel('Name')).toHaveValue('Original');
});

// GOOD — each test creates its own user
test.describe('user profile', () => {
  test('updates user name', async ({ page, request }) => {
    const email = `user-${Date.now()}@test.com`;
    await request.post('/api/users', { data: { email, name: 'Original' } });

    await page.goto(`/users/${email}`);
    await page.getByLabel('Name').fill('Updated');
    await page.getByRole('button', { name: 'Save' }).click();
    await expect(page.getByLabel('Name')).toHaveValue('Updated');
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// GOOD — per-test data creation
test('updates user name', async ({ page, request }) => {
  const email = `user-${Date.now()}@test.com`;
  await request.post('/api/users', { data: { email, name: 'Original' } });

  await page.goto(`/users/${email}`);
  await page.getByLabel('Name').fill('Updated');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByLabel('Name')).toHaveValue('Updated');
});
```

---

## Pitfall 14: Storing Test Data in Variables Shared Between Tests

**Symptom**: Test B depends on data created in Test A. Reordering or running tests in parallel breaks the suite.

**Why it happens**: Developers declare `let` variables at the module level and assign them in one test, expecting another test to read them.

**Fix**: Each test must create its own data. Use fixtures for shared setup logic.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — test B depends on test A creating the product
let productId: string;

test('test A: creates product', async ({ request }) => {
  const res = await request.post('/api/products', { data: { name: 'Widget' } });
  productId = (await res.json()).id;
});

test('test B: edits product', async ({ page }) => {
  await page.goto(`/products/${productId}/edit`); // undefined if test A didn't run first
});

// GOOD — each test is self-contained
test('creates and edits product', async ({ page, request }) => {
  const res = await request.post('/api/products', { data: { name: `Widget-${Date.now()}` } });
  const { id } = await res.json();

  await page.goto(`/products/${id}/edit`);
  await page.getByLabel('Name').fill('Updated Widget');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText('Updated Widget')).toBeVisible();

  // Cleanup
  await request.delete(`/api/products/${id}`);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// GOOD — self-contained test
test('creates and edits product', async ({ page, request }) => {
  const res = await request.post('/api/products', { data: { name: `Widget-${Date.now()}` } });
  const { id } = await res.json();

  await page.goto(`/products/${id}/edit`);
  await page.getByLabel('Name').fill('Updated Widget');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText('Updated Widget')).toBeVisible();

  await request.delete(`/api/products/${id}`);
});
```

---

## Pitfall 15: Deep Nesting of `test.describe` Blocks

**Symptom**: Test structure is 3+ levels deep. Hard to read. `beforeEach` hooks from outer blocks are invisible at the test level. HTML reports are cluttered.

**Why it happens**: Developers organize tests like they organize code -- deeply nested hierarchies. But tests should be flat and scannable.

**Fix**: Limit nesting to 2 levels maximum. Use separate files instead of deep nesting.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — 4 levels deep, impossible to follow
test.describe('admin', () => {
  test.describe('settings', () => {
    test.describe('security', () => {
      test.describe('two-factor auth', () => {
        test('enables TOTP', async ({ page }) => {
          // Which beforeEach hooks ran before this? Good luck figuring out.
        });
      });
    });
  });
});

// GOOD — max 2 levels, clear and flat
test.describe('admin security settings', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/admin/settings/security');
  });

  test('enables two-factor auth via TOTP', async ({ page }) => {
    await page.getByRole('button', { name: 'Enable 2FA' }).click();
    await expect(page.getByText('Scan QR code')).toBeVisible();
  });

  test('disables two-factor auth', async ({ page }) => {
    await page.getByRole('button', { name: 'Disable 2FA' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// GOOD — flat structure, max 2 levels
test.describe('admin security settings', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/admin/settings/security');
  });

  test('enables two-factor auth via TOTP', async ({ page }) => {
    await page.getByRole('button', { name: 'Enable 2FA' }).click();
    await expect(page.getByText('Scan QR code')).toBeVisible();
  });
});
```

If you need to organize many tests, split into separate files: `security-2fa.spec.ts`, `security-passwords.spec.ts`, `security-sessions.spec.ts`.

---

## Pitfall 16: Not Configuring Retries Differently for Local vs CI

**Symptom**: Developers use retries locally (hiding bugs during development) or have no retries in CI (failing on intermittent issues that are not their fault).

**Why it happens**: A single `retries` value is set without considering the environment.

**Fix**: Zero retries locally (fail fast), 1-2 retries in CI (catch infrastructure blips).

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  // GOOD — different retry strategy per environment
  retries: process.env.CI ? 2 : 0,

  use: {
    // Only capture traces on retry — saves CI time and storage
    trace: 'on-first-retry',
  },
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  retries: process.env.CI ? 2 : 0,
  use: {
    trace: 'on-first-retry',
  },
});
```

**Important**: A test that consistently needs retries to pass is not "passing" -- it is flaky. Track retry counts and fix the root cause.

---

## Pitfall 17: Running All Browsers in Every CI Run

**Symptom**: CI takes 3x longer than necessary. Most bugs are caught by a single browser engine.

**Why it happens**: Developers enable Chromium + Firefox + WebKit in the config and never reconsider.

**Fix**: Run Chromium on every PR. Run all browsers in a nightly or pre-release job.

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

const allBrowsers = [
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  { name: 'webkit', use: { ...devices['Desktop Safari'] } },
];

const chromeOnly = [
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
];

export default defineConfig({
  // PR runs: Chromium only. Nightly: all browsers.
  projects: process.env.ALL_BROWSERS ? allBrowsers : chromeOnly,
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

const allBrowsers = [
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  { name: 'webkit', use: { ...devices['Desktop Safari'] } },
];

const chromeOnly = [
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
];

module.exports = defineConfig({
  projects: process.env.ALL_BROWSERS ? allBrowsers : chromeOnly,
});
```

```yaml
# .github/workflows/tests.yml
jobs:
  pr-tests:
    # Fast: Chromium only
    runs-on: ubuntu-latest
    steps:
      - run: npx playwright test

  nightly-full:
    # Comprehensive: all browsers
    schedule:
      - cron: '0 3 * * *'
    steps:
      - run: ALL_BROWSERS=1 npx playwright test
```

---

## Pitfall 18: Using `page.evaluate()` for Things Locators Can Do

**Symptom**: Tests are verbose and fragile. Direct DOM manipulation bypasses Playwright's auto-waiting and actionability checks.

**Why it happens**: Developers with vanilla JS or Puppeteer backgrounds use `evaluate()` for everything because it feels familiar.

**Fix**: Use locator methods for all DOM interactions. Reserve `page.evaluate()` for things locators genuinely cannot do (reading computed styles, calling app-specific JS APIs, setting up test hooks).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — using evaluate for things locators handle better
test('bad: evaluate for DOM interaction', async ({ page }) => {
  await page.goto('/settings');

  // Getting text
  const text = await page.evaluate(() =>
    document.querySelector('[data-testid="username"]')?.textContent
  );
  expect(text).toBe('John');

  // Clicking
  await page.evaluate(() => {
    (document.querySelector('button.save-btn') as HTMLButtonElement)?.click();
  });

  // Checking visibility
  const visible = await page.evaluate(() => {
    const el = document.querySelector('.success-message');
    return el ? window.getComputedStyle(el).display !== 'none' : false;
  });
  expect(visible).toBe(true);
});

// GOOD — locators with auto-waiting and retry
test('good: locator methods', async ({ page }) => {
  await page.goto('/settings');

  await expect(page.getByTestId('username')).toHaveText('John');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText('Settings saved')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// BAD
test('bad: evaluate for DOM interaction', async ({ page }) => {
  const text = await page.evaluate(() =>
    document.querySelector('[data-testid="username"]')?.textContent
  );
  expect(text).toBe('John');
});

// GOOD
test('good: locator methods', async ({ page }) => {
  await expect(page.getByTestId('username')).toHaveText('John');
});
```

**When `evaluate()` is appropriate**: Reading `window.__APP_STATE__`, calling test-specific setup functions exposed by the app, manipulating `localStorage`/`sessionStorage`, or reading computed styles that have no locator equivalent.

---

## Pitfall 19: Not Using `test.step()` for Complex Flows

**Symptom**: Long tests are hard to debug. When they fail, the trace shows 50+ actions with no logical grouping. The HTML report provides no structure.

**Why it happens**: Developers write tests as a linear sequence of actions without labeling phases.

**Fix**: Wrap logical phases in `test.step()`. Steps appear in traces, reports, and error messages.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — 30 lines of actions with no structure
test('bad: flat checkout flow', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('button', { name: 'Add Widget' }).click();
  await page.getByRole('link', { name: 'Cart' }).click();
  await page.getByRole('button', { name: 'Checkout' }).click();
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Address').fill('123 Test St');
  await page.getByRole('button', { name: 'Continue' }).click();
  await page.getByLabel('Card number').fill('4242424242424242');
  await page.getByRole('button', { name: 'Pay' }).click();
  await expect(page.getByText('Order confirmed')).toBeVisible();
});

// GOOD — logical steps, clear in traces and reports
test('good: structured checkout flow', async ({ page }) => {
  await test.step('add item to cart', async () => {
    await page.goto('/products');
    await page.getByRole('button', { name: 'Add Widget' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('1');
  });

  await test.step('proceed to checkout', async () => {
    await page.getByRole('link', { name: 'Cart' }).click();
    await page.getByRole('button', { name: 'Checkout' }).click();
    await expect(page).toHaveURL(/.*checkout/);
  });

  await test.step('fill shipping details', async () => {
    await page.getByLabel('Email').fill('user@test.com');
    await page.getByLabel('Address').fill('123 Test St');
    await page.getByRole('button', { name: 'Continue' }).click();
  });

  await test.step('complete payment', async () => {
    await page.getByLabel('Card number').fill('4242424242424242');
    await page.getByRole('button', { name: 'Pay' }).click();
    await expect(page.getByText('Order confirmed')).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('good: structured checkout flow', async ({ page }) => {
  await test.step('add item to cart', async () => {
    await page.goto('/products');
    await page.getByRole('button', { name: 'Add Widget' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('1');
  });

  await test.step('proceed to checkout', async () => {
    await page.getByRole('link', { name: 'Cart' }).click();
    await page.getByRole('button', { name: 'Checkout' }).click();
  });

  await test.step('fill shipping details', async () => {
    await page.getByLabel('Email').fill('user@test.com');
    await page.getByLabel('Address').fill('123 Test St');
    await page.getByRole('button', { name: 'Continue' }).click();
  });

  await test.step('complete payment', async () => {
    await page.getByLabel('Card number').fill('4242424242424242');
    await page.getByRole('button', { name: 'Pay' }).click();
    await expect(page.getByText('Order confirmed')).toBeVisible();
  });
});
```

When a step fails, the error message includes the step name: `Error in step "complete payment": ...`. This is significantly more helpful than line numbers alone.

---

## Pitfall 20: Catching Errors from Assertions (try/catch Around expect)

**Symptom**: Tests pass when they should fail. Assertion errors are silently swallowed. Real bugs go undetected.

**Why it happens**: Developers wrap assertions in try/catch to handle "optional" elements or to implement conditional logic. This defeats the purpose of assertions.

**Fix**: Use `expect.soft()` for non-critical checks, `.not` assertions for absent elements, or restructure the test to avoid conditional logic.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// BAD — swallows real failures
test('bad: try/catch around assertion', async ({ page }) => {
  await page.goto('/dashboard');

  try {
    await expect(page.getByRole('alert')).toBeVisible({ timeout: 2_000 });
    // Dismiss the alert if it exists
    await page.getByRole('button', { name: 'Dismiss' }).click();
  } catch {
    // Alert didn't appear — that's fine
  }

  await expect(page.getByRole('heading')).toHaveText('Dashboard');
});

// GOOD — check count to determine if element exists, no try/catch needed
test('good: conditional without try/catch', async ({ page }) => {
  await page.goto('/dashboard');

  // If an alert banner is present, dismiss it
  const alertCount = await page.getByRole('alert').count();
  if (alertCount > 0) {
    await page.getByRole('button', { name: 'Dismiss' }).click();
    await expect(page.getByRole('alert')).not.toBeVisible();
  }

  await expect(page.getByRole('heading')).toHaveText('Dashboard');
});

// GOOD — use soft assertions for non-critical checks
test('good: soft assertions for nice-to-have checks', async ({ page }) => {
  await page.goto('/dashboard');

  // These are informational — test continues even if they fail
  await expect.soft(page.getByTestId('revenue')).toContainText('$');
  await expect.soft(page.getByTestId('users')).toContainText('active');

  // This is the actual assertion — test fails if this fails
  await expect(page.getByRole('heading')).toHaveText('Dashboard');
});

// GOOD — assert element is NOT present (no try/catch needed)
test('good: assert absence directly', async ({ page }) => {
  await page.goto('/dashboard');

  // This auto-retries until the error disappears (or times out)
  await expect(page.getByRole('alert')).not.toBeVisible();

  await expect(page.getByRole('heading')).toHaveText('Dashboard');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// GOOD — conditional without try/catch
test('good: conditional without try/catch', async ({ page }) => {
  await page.goto('/dashboard');

  const alertCount = await page.getByRole('alert').count();
  if (alertCount > 0) {
    await page.getByRole('button', { name: 'Dismiss' }).click();
    await expect(page.getByRole('alert')).not.toBeVisible();
  }

  await expect(page.getByRole('heading')).toHaveText('Dashboard');
});

// GOOD — soft assertions for non-critical checks
test('good: soft assertions for nice-to-have checks', async ({ page }) => {
  await page.goto('/dashboard');

  await expect.soft(page.getByTestId('revenue')).toContainText('$');
  await expect.soft(page.getByTestId('users')).toContainText('active');

  await expect(page.getByRole('heading')).toHaveText('Dashboard');
});
```

**Rule**: If you find yourself writing `try/catch` around an `expect()`, the test design is wrong. Rethink the assertion.

---

## Quick Lookup Table

| # | Pitfall | One-Line Fix |
|---|---|---|
| 1 | `waitForTimeout()` | Replace with `expect(locator).toBeVisible()` |
| 2 | Missing `await` | Add `await` + enable `no-floating-promises` ESLint rule |
| 3 | CSS selectors | Use `getByRole()`, `getByLabel()`, `getByTestId()` |
| 4 | `isVisible()` check | Use `expect(locator).toBeVisible()` |
| 5 | Shared mutable state | Use test-scoped fixtures with unique data |
| 6 | Hardcoded URLs | Set `baseURL` in config, use relative paths |
| 7 | `page.$()` / `page.$$()` | Use `page.locator()` or `page.getByRole()` |
| 8 | Navigation not handled | Add `page.waitForURL()` after form submissions |
| 9 | No `webServer` in CI | Add `webServer` config with `reuseExistingServer: !process.env.CI` |
| 10 | `innerHTML` / `textContent` | Use `expect(locator).toHaveText()` |
| 11 | Over-mocking own API | Mock only external services |
| 12 | No `test.describe` | Group related tests, scope `beforeEach` and `test.use()` |
| 13 | `beforeAll` for per-test setup | Use `beforeEach` or test-scoped fixtures |
| 14 | Module-level test data variables | Create data inside each test or via fixtures |
| 15 | Deep `describe` nesting (3+) | Max 2 levels; split into separate files |
| 16 | Same retries everywhere | `retries: process.env.CI ? 2 : 0` |
| 17 | All browsers on every PR | Chromium on PRs, full matrix nightly |
| 18 | `page.evaluate()` overuse | Use locator methods; reserve `evaluate` for JS APIs |
| 19 | No `test.step()` | Wrap logical phases in named steps |
| 20 | `try/catch` around `expect` | Use `expect.soft()`, `.not`, or `locator.count()` |

## Related

- [core/locators.md](locators.md) -- locator strategy hierarchy (Pitfalls 3, 7, 18)
- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- web-first assertions (Pitfalls 1, 4, 10, 20)
- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) -- fixtures vs hooks (Pitfalls 5, 13, 14)
- [core/configuration.md](configuration.md) -- baseURL, webServer, retries (Pitfalls 6, 9, 16, 17)
- [core/test-organization.md](test-organization.md) -- describe blocks, nesting, tags (Pitfalls 12, 15)
- [core/flaky-tests.md](flaky-tests.md) -- diagnosing and fixing flaky tests (Pitfalls 1, 2, 5)
- [core/debugging.md](debugging.md) -- traces, UI mode, page.pause()
