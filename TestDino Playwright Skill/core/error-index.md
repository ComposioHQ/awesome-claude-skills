# Playwright Error Index

Quick-reference for specific Playwright error messages. Find your error, understand the cause, apply the fix.

> **How to use**: Search this file for the exact error text you see in your terminal or test report. Each entry gives you the cause and a working fix.

---

## Locator & Element Errors

---

### "locator.click: Target closed"

**Cause**: The page or frame navigated away (or was closed) before Playwright finished executing the action on the element.

**Common triggers**:
- Clicking a link that triggers navigation while another action is still pending
- A form submit causes a page reload before a subsequent `click()` or `fill()` resolves
- Calling `page.close()` or `context.close()` in a `finally` block that races with an in-flight action
- An unhandled exception in the application triggers an error page redirect

**Fix**: Wait for navigation to complete before performing the next action, or use `Promise.all` to coordinate the click and navigation together.

```typescript
// TypeScript — wait for navigation caused by clicking a link
await Promise.all([
  page.waitForURL('**/dashboard'),
  page.getByRole('link', { name: 'Dashboard' }).click(),
]);
```

```javascript
// JavaScript — same pattern
await Promise.all([
  page.waitForURL('**/dashboard'),
  page.getByRole('link', { name: 'Dashboard' }).click(),
]);
```

If the page is closing intentionally (e.g., a popup), capture a reference before the action:

```typescript
// TypeScript — handle popup that closes itself
const popupPromise = page.waitForEvent('popup');
await page.getByRole('button', { name: 'Open popup' }).click();
const popup = await popupPromise;
await popup.waitForLoadState();
// interact with popup before it closes
await popup.getByRole('button', { name: 'Confirm' }).click();
```

```javascript
// JavaScript — handle popup that closes itself
const popupPromise = page.waitForEvent('popup');
await page.getByRole('button', { name: 'Open popup' }).click();
const popup = await popupPromise;
await popup.waitForLoadState();
await popup.getByRole('button', { name: 'Confirm' }).click();
```

**Related**: [core/assertions-and-waiting.md](assertions-and-waiting.md), [core/multi-context-and-popups.md](multi-context-and-popups.md)

---

### "waiting for locator('...') to be visible"

**Cause**: Playwright's auto-waiting timed out because the element never appeared in the DOM or remained hidden (e.g., `display: none`, `visibility: hidden`, zero size, or behind `aria-hidden`).

**Common triggers**:
- The element renders conditionally and the condition was not met (missing data, unauthenticated state)
- Content loads asynchronously and the locator was evaluated before the API response arrived
- The selector is wrong — typo in role, name, or test ID
- The element exists but is off-screen or inside a collapsed container
- CSS animation or transition keeps the element at `opacity: 0` without making it visible to Playwright

**Fix**: First confirm the locator matches what you expect using the Playwright Inspector. Then ensure the precondition for the element to appear is met.

```typescript
// TypeScript — debug: check what the locator resolves to
console.log(await page.getByRole('button', { name: 'Submit' }).count());
// If 0, the element is not in the DOM — check your selector or page state

// Correct approach: wait for the data to load first
await page.waitForResponse(resp =>
  resp.url().includes('/api/data') && resp.status() === 200
);
await expect(page.getByRole('button', { name: 'Submit' })).toBeVisible();
```

```javascript
// JavaScript — same approach
console.log(await page.getByRole('button', { name: 'Submit' }).count());

await page.waitForResponse(resp =>
  resp.url().includes('/api/data') && resp.status() === 200
);
await expect(page.getByRole('button', { name: 'Submit' })).toBeVisible();
```

**Related**: [core/locators.md](locators.md), [core/assertions-and-waiting.md](assertions-and-waiting.md)

---

### "locator.click: Error: strict mode violation"

**Cause**: The locator matched more than one element and Playwright's strict mode (enabled by default) refuses to act on ambiguous matches.

**Common triggers**:
- Using `getByRole('button')` when multiple buttons exist on the page
- Using `getByText('Save')` when both "Save" and "Save as draft" are present
- Partial text matching when `exact: true` is needed
- The same component is rendered multiple times (e.g., in a list)

**Fix**: Make the locator more specific so it resolves to exactly one element.

```typescript
// TypeScript

// BAD — matches multiple buttons
await page.getByRole('button', { name: 'Save' }).click();

// GOOD — use exact matching
await page.getByRole('button', { name: 'Save', exact: true }).click();

// GOOD — scope to a specific container
await page.getByRole('dialog')
  .getByRole('button', { name: 'Save' }).click();

// GOOD — use .first(), .last(), .nth() when order is meaningful
await page.getByRole('listitem').first().click();

// GOOD — chain with filter for list items
await page.getByRole('listitem')
  .filter({ hasText: 'Project Alpha' })
  .getByRole('button', { name: 'Delete' }).click();
```

```javascript
// JavaScript

// BAD — matches multiple buttons
await page.getByRole('button', { name: 'Save' }).click();

// GOOD — use exact matching
await page.getByRole('button', { name: 'Save', exact: true }).click();

// GOOD — scope to a specific container
await page.getByRole('dialog')
  .getByRole('button', { name: 'Save' }).click();

// GOOD — use .first(), .last(), .nth() when order is meaningful
await page.getByRole('listitem').first().click();

// GOOD — chain with filter for list items
await page.getByRole('listitem')
  .filter({ hasText: 'Project Alpha' })
  .getByRole('button', { name: 'Delete' }).click();
```

**Related**: [core/locators.md](locators.md), [core/locator-strategy.md](locator-strategy.md)

---

### "Error: expect(locator).toBeVisible() — locator resolved to X elements"

**Cause**: Same root cause as strict mode violation above — the assertion's locator matched multiple elements, so Playwright cannot determine which one to assert on.

**Common triggers**:
- Same as strict mode violation triggers above
- Writing `expect(page.locator('.item')).toBeVisible()` when there are many `.item` elements

**Fix**: Narrow the locator to a single element (see strict mode violation fix above). Alternatively, if you intentionally want to check all matches:

```typescript
// TypeScript — assert count instead of visibility
await expect(page.getByRole('listitem')).toHaveCount(5);

// Or assert on a specific one
await expect(page.getByRole('listitem').first()).toBeVisible();

// Or assert all are visible with a loop
for (const item of await page.getByRole('listitem').all()) {
  await expect(item).toBeVisible();
}
```

```javascript
// JavaScript — assert count instead of visibility
await expect(page.getByRole('listitem')).toHaveCount(5);

// Or assert on a specific one
await expect(page.getByRole('listitem').first()).toBeVisible();

// Or assert all are visible with a loop
for (const item of await page.getByRole('listitem').all()) {
  await expect(item).toBeVisible();
}
```

**Related**: [core/locators.md](locators.md), [core/assertions-and-waiting.md](assertions-and-waiting.md)

---

### "locator.fill: Error: Element is not an <input>, <textarea> or [contenteditable] element"

**Cause**: `fill()` only works on `<input>`, `<textarea>`, or elements with `contenteditable`. The locator resolved to a different element type (e.g., a `<div>`, `<label>`, or the `<form>` itself).

**Common triggers**:
- Locating by label text but the label and input are not properly associated via `for`/`id`
- Using `getByText()` instead of `getByLabel()` or `getByRole('textbox')`
- Custom components that wrap the actual `<input>` in a styled `<div>`
- Rich text editors that use `contenteditable` on an inner element, not the outer wrapper

**Fix**: Target the actual input element.

```typescript
// TypeScript

// BAD — targets the label, not the input
await page.getByText('Email').fill('user@example.com');

// GOOD — getByLabel finds the associated input
await page.getByLabel('Email').fill('user@example.com');

// GOOD — target by role
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

// For contenteditable rich text editors
await page.locator('[contenteditable="true"]').fill('Hello world');

// If fill() still doesn't work (e.g., custom widget), use keyboard input
await page.getByRole('textbox', { name: 'Email' }).click();
await page.keyboard.type('user@example.com');
```

```javascript
// JavaScript

// BAD — targets the label, not the input
await page.getByText('Email').fill('user@example.com');

// GOOD — getByLabel finds the associated input
await page.getByLabel('Email').fill('user@example.com');

// GOOD — target by role
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

// For contenteditable rich text editors
await page.locator('[contenteditable="true"]').fill('Hello world');

// If fill() still doesn't work (e.g., custom widget), use keyboard input
await page.getByRole('textbox', { name: 'Email' }).click();
await page.keyboard.type('user@example.com');
```

**Related**: [core/locators.md](locators.md), [core/forms-and-validation.md](forms-and-validation.md)

---

### "Error: elementHandle.click: Node is not an Element"

**Cause**: You are using the legacy ElementHandle API and the handle has gone stale — the underlying DOM node was removed or replaced by a re-render.

**Common triggers**:
- Storing an `elementHandle` in a variable and using it after a navigation or React/Vue re-render
- Using `page.$()` or `page.$$()` instead of Locator API
- Framework hydration replaces the server-rendered node with a client-rendered one

**Fix**: Switch from ElementHandle to Locator. Locators re-query the DOM on every action and never go stale.

```typescript
// TypeScript

// BAD — stale handle
const button = await page.$('button.submit');
// ... page re-renders ...
await button!.click(); // Node is not an Element

// GOOD — locator always re-queries
const button = page.getByRole('button', { name: 'Submit' });
// ... page re-renders ...
await button.click(); // works fine
```

```javascript
// JavaScript

// BAD — stale handle
const button = await page.$('button.submit');
// ... page re-renders ...
await button.click(); // Node is not an Element

// GOOD — locator always re-queries
const button = page.getByRole('button', { name: 'Submit' });
// ... page re-renders ...
await button.click(); // works fine
```

**Related**: [core/locators.md](locators.md)

---

### "Error: locator.click: Timeout 30000ms exceeded"

**Cause**: The element was found in the DOM but was not actionable within the timeout. "Actionable" means visible, stable (not animating), enabled, and not obscured by another element.

**Common triggers**:
- An overlay, modal, or toast is covering the element
- The element is disabled (`disabled` attribute or `aria-disabled="true"`)
- CSS animation has not completed (element is still moving)
- A loading spinner overlays the button
- The element is outside the viewport and Playwright's auto-scroll failed

**Fix**: Identify what is blocking the action using traces, then address it.

```typescript
// TypeScript

// Step 1: Enable tracing to diagnose
// In playwright.config.ts:
// use: { trace: 'on-first-retry' }
// Then run: npx playwright show-trace trace.zip

// Common fix: wait for the overlay to disappear
await expect(page.locator('.loading-overlay')).toBeHidden();
await page.getByRole('button', { name: 'Submit' }).click();

// Common fix: force click when you know the overlay is benign
// (use sparingly — this skips actionability checks)
await page.getByRole('button', { name: 'Submit' }).click({ force: true });

// Common fix: wait for the element to be enabled
await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();
await page.getByRole('button', { name: 'Submit' }).click();
```

```javascript
// JavaScript

// Common fix: wait for the overlay to disappear
await expect(page.locator('.loading-overlay')).toBeHidden();
await page.getByRole('button', { name: 'Submit' }).click();

// Common fix: force click (use sparingly)
await page.getByRole('button', { name: 'Submit' }).click({ force: true });

// Common fix: wait for the element to be enabled
await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();
await page.getByRole('button', { name: 'Submit' }).click();
```

**Related**: [core/assertions-and-waiting.md](assertions-and-waiting.md), [core/debugging.md](debugging.md)

---

## Navigation & Page Errors

---

### "page.goto: net::ERR_CONNECTION_REFUSED"

**Cause**: Playwright could not connect to the target URL. The server is not running or is not listening on the expected host/port.

**Common triggers**:
- Forgot to start the dev server before running tests
- Dev server is on a different port than `baseURL` in config
- Server is listening on `127.0.0.1` but test uses `localhost` (or vice versa) and the OS resolves them differently
- In CI, the application build/start step failed silently
- Docker container networking: the app runs inside a container but the test tries to reach `localhost`

**Fix**: Use the `webServer` config option to let Playwright start and manage the dev server automatically.

```typescript
// TypeScript — playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000, // 2 minutes for server start
  },
  use: {
    baseURL: 'http://localhost:3000',
  },
});
```

```javascript
// JavaScript — playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  use: {
    baseURL: 'http://localhost:3000',
  },
});
```

**Related**: [core/configuration.md](configuration.md), [ci/ci-github-actions.md](../ci/ci-github-actions.md)

---

### "page.goto: Timeout 30000ms exceeded"

**Cause**: The page did not reach the `load` state (by default) within the navigation timeout. The server responded but the page took too long to fully load.

**Common triggers**:
- Large assets (images, fonts, scripts) slow the page load
- Third-party scripts (analytics, ads) blocking the load event
- The page makes many API calls before becoming interactive
- The server responded with a redirect chain that takes too long

**Fix**: Use a more appropriate `waitUntil` option or increase the navigation timeout.

```typescript
// TypeScript

// Use 'domcontentloaded' instead of 'load' if you don't need all assets
await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });

// Or increase the navigation timeout for known slow pages
await page.goto('/dashboard', { timeout: 60_000 });

// Or set it globally in config
// playwright.config.ts
export default defineConfig({
  use: {
    navigationTimeout: 60_000,
  },
});
```

```javascript
// JavaScript

await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });

await page.goto('/dashboard', { timeout: 60_000 });

// playwright.config.js
module.exports = defineConfig({
  use: {
    navigationTimeout: 60_000,
  },
});
```

**Related**: [core/configuration.md](configuration.md)

---

### "Error: page.goto: Navigation failed because page was closed!"

**Cause**: The page or browser context was closed while `goto()` was still in progress. This typically happens in teardown/cleanup race conditions.

**Common triggers**:
- `afterEach` or a fixture closes the page/context before navigation completes
- Another test or hook called `browser.close()` prematurely
- A test failed and the cleanup ran while an async navigation was still pending
- Using `test.fixme()` or `test.skip()` after an async operation has started

**Fix**: Ensure cleanup only runs after all page operations complete. Use fixtures for lifecycle management instead of manual `afterEach`.

```typescript
// TypeScript

// BAD — race condition between test body and cleanup
test.afterEach(async ({ page }) => {
  await page.close(); // may race with in-flight navigation
});

// GOOD — let Playwright manage page lifecycle via fixtures
// Playwright automatically creates and destroys the page per test
// No manual cleanup needed

// If you need custom cleanup, make sure to await all navigation first
test('navigates to dashboard', async ({ page }) => {
  const responsePromise = page.waitForResponse('**/api/user');
  await page.goto('/dashboard');
  await responsePromise; // ensure all async ops are done
  // test assertions here
});
```

```javascript
// JavaScript — same pattern

test('navigates to dashboard', async ({ page }) => {
  const responsePromise = page.waitForResponse('**/api/user');
  await page.goto('/dashboard');
  await responsePromise;
  // test assertions here
});
```

**Related**: [core/fixtures-and-hooks.md](fixtures-and-hooks.md)

---

### "page.waitForNavigation: Timeout 30000ms exceeded"

**Cause**: `waitForNavigation()` waited for a full page navigation that never happened. In SPAs, client-side routing does not trigger a navigation event.

**Common triggers**:
- Using `waitForNavigation()` with a SPA that uses React Router, Vue Router, or Next.js client-side navigation
- The navigation already happened before `waitForNavigation()` was called (race condition)
- Using the deprecated pattern when `waitForURL()` is the correct replacement

**Fix**: Replace `waitForNavigation()` with `waitForURL()` which works with both SPAs and traditional page loads.

```typescript
// TypeScript

// BAD — deprecated, race-prone, doesn't work with SPA routing
await page.waitForNavigation();

// GOOD — works with SPAs and full navigations
await page.getByRole('link', { name: 'Dashboard' }).click();
await page.waitForURL('**/dashboard');

// GOOD — combine with glob patterns
await page.waitForURL(/\/dashboard\/\d+/);

// GOOD — for SPA route changes, assert on visible content
await page.getByRole('link', { name: 'Settings' }).click();
await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
```

```javascript
// JavaScript

// BAD — deprecated, race-prone
await page.waitForNavigation();

// GOOD — works with SPAs and full navigations
await page.getByRole('link', { name: 'Dashboard' }).click();
await page.waitForURL('**/dashboard');

// GOOD — combine with glob patterns
await page.waitForURL(/\/dashboard\/\d+/);

// GOOD — for SPA route changes, assert on visible content
await page.getByRole('link', { name: 'Settings' }).click();
await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
```

**Related**: [core/assertions-and-waiting.md](assertions-and-waiting.md)

---

### "Error: frame.goto: Frame was detached"

**Cause**: The iframe was removed from the DOM (detached) while Playwright was navigating or interacting with it.

**Common triggers**:
- The parent page re-rendered and recreated the iframe element
- JavaScript on the parent page removed and re-added the iframe
- A SPA route change unmounted the component containing the iframe
- An ad iframe reloaded itself

**Fix**: Re-acquire the frame reference after the parent page updates.

```typescript
// TypeScript

// BAD — frame reference becomes stale
const frame = page.frameLocator('#my-iframe');
// ... parent page re-renders ...
await frame.getByRole('button').click(); // Frame was detached

// GOOD — use frameLocator (re-evaluates each time)
// frameLocator itself is lazy, but the frame it points to must exist
await expect(page.frameLocator('#my-iframe').getByRole('button')).toBeVisible();
await page.frameLocator('#my-iframe').getByRole('button').click();

// GOOD — wait for the iframe to be present after a re-render
await expect(page.locator('#my-iframe')).toBeAttached();
await page.frameLocator('#my-iframe').getByRole('button').click();
```

```javascript
// JavaScript

// GOOD — frameLocator re-evaluates lazily
await expect(page.frameLocator('#my-iframe').getByRole('button')).toBeVisible();
await page.frameLocator('#my-iframe').getByRole('button').click();

// GOOD — wait for the iframe to be present after a re-render
await expect(page.locator('#my-iframe')).toBeAttached();
await page.frameLocator('#my-iframe').getByRole('button').click();
```

**Related**: [core/iframes-and-shadow-dom.md](iframes-and-shadow-dom.md)

---

## Test Framework Errors

---

### "Error: Test timeout of 30000ms exceeded"

**Cause**: The entire test (including all hooks and assertions) did not complete within the configured test timeout.

**Common triggers**:
- Waiting for an element that never appears (wrong locator, missing data)
- Unresolved `page.waitForEvent()` — the expected event never fires
- Slow test environment (CI with limited resources)
- Too many sequential actions in a single test
- A `beforeEach` hook performs expensive setup (login, data seeding)

**Fix**: Identify the slow step using `test.step()` and traces, then either fix the root cause or adjust the timeout.

```typescript
// TypeScript

// Increase timeout for a specific slow test
test('generates large report', async ({ page }) => {
  test.setTimeout(120_000); // 2 minutes for this test only
  // ...
});

// Increase timeout globally in config
// playwright.config.ts
export default defineConfig({
  timeout: 60_000, // 60 seconds per test
});

// Better: diagnose with test.step() to find what's slow
test('checkout flow', async ({ page }) => {
  await test.step('add item to cart', async () => {
    await page.goto('/products');
    await page.getByRole('button', { name: 'Add to Cart' }).click();
  });

  await test.step('complete checkout', async () => {
    await page.getByRole('link', { name: 'Cart' }).click();
    await page.getByRole('button', { name: 'Checkout' }).click();
  });
});
```

```javascript
// JavaScript

test('generates large report', async ({ page }) => {
  test.setTimeout(120_000);
  // ...
});

// playwright.config.js
module.exports = defineConfig({
  timeout: 60_000,
});

test('checkout flow', async ({ page }) => {
  await test.step('add item to cart', async () => {
    await page.goto('/products');
    await page.getByRole('button', { name: 'Add to Cart' }).click();
  });

  await test.step('complete checkout', async () => {
    await page.getByRole('link', { name: 'Cart' }).click();
    await page.getByRole('button', { name: 'Checkout' }).click();
  });
});
```

**Related**: [core/configuration.md](configuration.md), [core/debugging.md](debugging.md)

---

### "Error: expect(received).toMatchSnapshot()"

**Cause**: The current screenshot or text does not match the stored baseline snapshot.

**Common triggers**:
- Legitimate UI changes that require updating the snapshot
- Different rendering between local and CI (fonts, anti-aliasing, OS-level rendering)
- Dynamic content (timestamps, random IDs, ads) that changes between runs
- Different viewport sizes or device emulation settings between environments

**Fix**: Update the snapshot if the change is intentional, or mask/hide dynamic areas.

```typescript
// TypeScript

// Update snapshots after intentional changes
// Run: npx playwright test --update-snapshots

// Mask dynamic content before taking a screenshot
await expect(page).toHaveScreenshot('dashboard.png', {
  mask: [
    page.locator('.timestamp'),
    page.locator('.random-ad'),
  ],
  maxDiffPixelRatio: 0.01, // allow 1% pixel difference
});

// Use text snapshot with a sanitizer for dynamic values
const content = await page.getByRole('main').textContent();
const sanitized = content!.replace(/\d{4}-\d{2}-\d{2}/g, 'DATE');
expect(sanitized).toMatchSnapshot('dashboard-content.txt');
```

```javascript
// JavaScript

// Update snapshots: npx playwright test --update-snapshots

await expect(page).toHaveScreenshot('dashboard.png', {
  mask: [
    page.locator('.timestamp'),
    page.locator('.random-ad'),
  ],
  maxDiffPixelRatio: 0.01,
});

const content = await page.getByRole('main').textContent();
const sanitized = content.replace(/\d{4}-\d{2}-\d{2}/g, 'DATE');
expect(sanitized).toMatchSnapshot('dashboard-content.txt');
```

**Related**: [core/visual-regression.md](visual-regression.md)

---

### "Error: browserType.launch: Executable doesn't exist"

**Cause**: The Playwright browser binaries are not installed on this machine or they were installed for a different Playwright version.

**Common triggers**:
- Fresh clone of a project without running the install step
- Upgrading `@playwright/test` without reinstalling browsers
- CI environment missing the install step
- Using `npm ci` which cleans `node_modules` but does not trigger the browser install postinstall script
- Multiple Playwright versions installed (global vs local)

**Fix**: Install the browsers.

```bash
# Install all browsers
npx playwright install

# Install only the browser you need (faster in CI)
npx playwright install chromium

# Install browsers with OS dependencies (needed in CI/Docker)
npx playwright install --with-deps

# If you're on a CI Dockerfile, add this to your Dockerfile
# RUN npx playwright install --with-deps chromium
```

For CI pipelines, always include the install step:

```yaml
# GitHub Actions example
- name: Install Playwright Browsers
  run: npx playwright install --with-deps
```

**Related**: [ci/ci-github-actions.md](../ci/ci-github-actions.md), [ci/docker-and-containers.md](../ci/docker-and-containers.md)

---

### "Error: Cannot use import statement outside a module"

**Cause**: Node.js is running the test file as CommonJS but the file uses ES module `import` syntax without the right configuration.

**Common triggers**:
- Missing or misconfigured `tsconfig.json`
- Using `.ts` files without `@playwright/test` properly resolving TypeScript
- `package.json` does not have `"type": "module"` but test files use `import`
- Running test files directly with `node` instead of through `npx playwright test`
- Conflicting Babel or ts-node configuration

**Fix**: Ensure TypeScript is configured correctly and always run tests through the Playwright CLI.

```bash
# Always run tests through the Playwright CLI — never with node directly
npx playwright test

# NOT this:
# node tests/example.spec.ts  <-- will fail
```

```typescript
// TypeScript — tsconfig.json (minimal working config)
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

If using JavaScript without TypeScript:

```javascript
// JavaScript — ensure package.json has "type": "module"
// Or rename files to .mjs

// In playwright.config.js — use require if package.json lacks "type": "module"
const { defineConfig } = require('@playwright/test');
module.exports = defineConfig({ /* ... */ });
```

**Related**: [core/configuration.md](configuration.md)

---

### "Error: fixture \"xxx\" has already been registered"

**Cause**: A custom fixture was defined with the same name in multiple `test.extend()` calls that got merged, or the same fixture name was registered twice in the same extension.

**Common triggers**:
- Two different fixture files both define a fixture with the same name
- Importing the extended `test` object from multiple files that each add overlapping fixtures
- Copy-pasting fixture definitions without renaming

**Fix**: Ensure each fixture name is unique across your merged fixture chain. Use a single fixture file that combines all extensions.

```typescript
// TypeScript

// BAD — two separate extensions with the same fixture name
// fixtures/auth.ts
export const test = base.extend<{ user: User }>({
  user: async ({}, use) => { /* ... */ },
});

// fixtures/data.ts — CONFLICT: "user" already exists
export const test = base.extend<{ user: User }>({
  user: async ({}, use) => { /* ... */ },
});

// GOOD — single combined fixture file
// fixtures/index.ts
import { test as base } from '@playwright/test';

type MyFixtures = {
  authenticatedUser: User;
  testData: TestData;
};

export const test = base.extend<MyFixtures>({
  authenticatedUser: async ({}, use) => {
    const user = await createUser();
    await use(user);
    await deleteUser(user);
  },
  testData: async ({}, use) => {
    const data = await seedData();
    await use(data);
    await cleanupData(data);
  },
});

export { expect } from '@playwright/test';
```

```javascript
// JavaScript

// GOOD — single combined fixture file
// fixtures/index.js
const { test: base } = require('@playwright/test');

const test = base.extend({
  authenticatedUser: async ({}, use) => {
    const user = await createUser();
    await use(user);
    await deleteUser(user);
  },
  testData: async ({}, use) => {
    const data = await seedData();
    await use(data);
    await cleanupData(data);
  },
});

module.exports = { test };
```

**Related**: [core/fixtures-and-hooks.md](fixtures-and-hooks.md)

---

## Network & API Errors

---

### "page.route: Pattern should start with..."

**Cause**: The URL pattern passed to `page.route()` does not match the expected format. Playwright expects a glob pattern (starting with `**/` or `http`), a regex, or a predicate function.

**Common triggers**:
- Passing a bare path like `/api/users` instead of `**/api/users`
- Missing the `**` glob prefix for relative patterns
- Passing an object or invalid type instead of a string/regex

**Fix**: Use the correct pattern format.

```typescript
// TypeScript

// BAD — bare path without glob prefix
await page.route('/api/users', route => route.fulfill({ body: '[]' }));

// GOOD — glob pattern
await page.route('**/api/users', route =>
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ id: 1, name: 'Alice' }]),
  })
);

// GOOD — regex pattern
await page.route(/\/api\/users\/\d+/, route =>
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ id: 1, name: 'Alice' }),
  })
);

// GOOD — predicate function for complex matching
await page.route(
  url => url.pathname.startsWith('/api/') && url.searchParams.has('filter'),
  route => route.fulfill({ body: '[]' })
);
```

```javascript
// JavaScript

// GOOD — glob pattern
await page.route('**/api/users', route =>
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ id: 1, name: 'Alice' }]),
  })
);

// GOOD — regex pattern
await page.route(/\/api\/users\/\d+/, route =>
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ id: 1, name: 'Alice' }),
  })
);

// GOOD — predicate function
await page.route(
  url => url.pathname.startsWith('/api/') && url.searchParams.has('filter'),
  route => route.fulfill({ body: '[]' })
);
```

**Related**: [core/network-mocking.md](network-mocking.md)

---

### "Error: apiRequestContext.get: connect ECONNREFUSED"

**Cause**: The API request made via `request.get()` (or `.post()`, `.put()`, etc.) could not connect to the target server. Same underlying issue as `page.goto: net::ERR_CONNECTION_REFUSED` but for API testing.

**Common triggers**:
- API server not running when using `request` fixture
- Wrong `baseURL` in the config or in the API request context
- Running API tests against a service that hasn't started yet
- In CI, the API service container is not ready

**Fix**: Ensure the API server is running. Use `webServer` config to auto-start it, or add a health check.

```typescript
// TypeScript — playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  webServer: [
    {
      command: 'npm run start:api',
      url: 'http://localhost:4000/health',
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run start:web',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
    },
  ],
  use: {
    baseURL: 'http://localhost:3000',
  },
});

// In tests, use the request fixture with explicit baseURL for API calls
test('fetch users', async ({ request }) => {
  const response = await request.get('http://localhost:4000/api/users');
  expect(response.ok()).toBeTruthy();
});
```

```javascript
// JavaScript — playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  webServer: [
    {
      command: 'npm run start:api',
      url: 'http://localhost:4000/health',
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run start:web',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
    },
  ],
  use: {
    baseURL: 'http://localhost:3000',
  },
});
```

**Related**: [core/api-testing.md](api-testing.md), [core/configuration.md](configuration.md)

---

### "Request was not handled: GET https://..."

**Cause**: A route handler was registered with `page.route()` using `{ times: N }` or `page.unrouteAll()` was called, and a subsequent request matching that pattern was not intercepted — Playwright warns you that a request fell through.

**Common triggers**:
- Using `page.route()` with `{ times: 1 }` but the app makes the same request more than once
- Calling `route.fallback()` or `route.continue()` without a handler to catch it
- Calling `page.unrouteAll({ behavior: 'wait' })` mid-test and the app makes another request

**Fix**: Ensure your route handler covers all expected requests, or let unhandled requests pass through.

```typescript
// TypeScript

// BAD — only handles the first request, second one is unhandled
await page.route('**/api/data', route =>
  route.fulfill({ body: '{}' }),
  { times: 1 }
);

// GOOD — handle all requests to this URL
await page.route('**/api/data', route =>
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ items: [] }),
  })
);

// GOOD — if you only want to intercept once, use waitForResponse for subsequent
await page.route('**/api/data', route =>
  route.fulfill({ body: '{"items": []}' }),
  { times: 1 }
);
// For the second call, let it go to the real server (no route needed)
```

```javascript
// JavaScript

// GOOD — handle all requests to this URL
await page.route('**/api/data', route =>
  route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ items: [] }),
  })
);
```

**Related**: [core/network-mocking.md](network-mocking.md)

---

## Authentication & State Errors

---

### "Error: browserContext.storageState: No such file"

**Cause**: The `storageState` path referenced in the config or test does not point to an existing file. The auth state file has not been generated yet.

**Common triggers**:
- Running tests before running the auth setup project
- The `globalSetup` or auth setup project did not complete successfully
- The file path in the config does not match the path used in the setup
- `.gitignore` excluded the storage state file and it was not regenerated after a fresh clone
- CI cache expired and the state file was not recreated

**Fix**: Ensure the auth setup runs first and the file path is consistent.

```typescript
// TypeScript — playwright.config.ts
import { defineConfig } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

export default defineConfig({
  projects: [
    // Setup project runs first and creates the auth state file
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    {
      name: 'chromium',
      use: {
        storageState: authFile,
      },
      dependencies: ['setup'], // ensures setup runs first
    },
  ],
});

// auth.setup.ts
import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  // Save the authenticated state
  await page.context().storageState({ path: authFile });
});
```

```javascript
// JavaScript — playwright.config.js
const { defineConfig } = require('@playwright/test');

const authFile = 'playwright/.auth/user.json';

module.exports = defineConfig({
  projects: [
    {
      name: 'setup',
      testMatch: /.*\.setup\.js/,
    },
    {
      name: 'chromium',
      use: {
        storageState: authFile,
      },
      dependencies: ['setup'],
    },
  ],
});

// auth.setup.js
const { test: setup, expect } = require('@playwright/test');

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: authFile });
});
```

Ensure the auth directory exists and is in `.gitignore`:

```bash
mkdir -p playwright/.auth
echo "playwright/.auth/" >> .gitignore
```

**Related**: [core/authentication.md](authentication.md), [core/auth-flows.md](auth-flows.md)

---

### "Error: Target page, context or browser has been closed"

**Cause**: Code attempted to use a `page`, `context`, or `browser` object that has already been closed or disposed.

**Common triggers**:
- Using a `page` reference after `page.close()` was called
- Storing a `page` or `context` in a module-level variable and reusing it across tests
- A fixture tore down the browser context while an async callback was still running
- A `beforeAll` created a context that was closed before all tests finished using it
- Using `browser.newContext()` manually and forgetting to manage its lifecycle

**Fix**: Never store page/context references in shared mutable state. Use Playwright fixtures for lifecycle management.

```typescript
// TypeScript

// BAD — shared module-level variable
let sharedPage: Page;
test.beforeAll(async ({ browser }) => {
  sharedPage = await browser.newPage();
});
test.afterAll(async () => {
  await sharedPage.close();
});
test('first', async () => {
  await sharedPage.goto('/'); // might fail if afterAll from another describe ran first
});

// GOOD — use the built-in page fixture (one per test, auto-managed)
test('first', async ({ page }) => {
  await page.goto('/'); // always a fresh, open page
});

// GOOD — for shared state across tests, use a worker-scoped fixture
import { test as base } from '@playwright/test';

export const test = base.extend<{}, { adminContext: BrowserContext }>({
  adminContext: [async ({ browser }, use) => {
    const context = await browser.newContext();
    await use(context);
    await context.close();
  }, { scope: 'worker' }],
});
```

```javascript
// JavaScript

// GOOD — use the built-in page fixture
test('first', async ({ page }) => {
  await page.goto('/');
});

// GOOD — for shared state, use a worker-scoped fixture
const { test: base } = require('@playwright/test');

const test = base.extend({
  adminContext: [async ({ browser }, use) => {
    const context = await browser.newContext();
    await use(context);
    await context.close();
  }, { scope: 'worker' }],
});
```

**Related**: [core/fixtures-and-hooks.md](fixtures-and-hooks.md)

---

## CI-Specific Errors

---

### "Error: browserType.launch: Browser closed unexpectedly"

**Cause**: The browser process crashed immediately after launch, usually because required OS-level dependencies are missing in the CI environment.

**Common triggers**:
- Running on a minimal Docker image (e.g., `node:alpine`) without browser dependencies
- Missing shared libraries (`libgbm`, `libnss3`, `libatk-bridge`, etc.) on Linux CI
- Insufficient shared memory (`/dev/shm` too small) — browsers use shared memory for rendering
- Running as root in Docker without `--no-sandbox` (Chromium refuses to run as root with sandbox)
- Out-of-memory kill on CI (browser process is OOM-killed by the OS)

**Fix**: Install OS-level dependencies and configure the environment.

```bash
# Install browsers with their OS dependencies (recommended)
npx playwright install --with-deps chromium

# If using Docker, use the official Playwright image
# Dockerfile
FROM mcr.microsoft.com/playwright:v1.50.0-noble
WORKDIR /app
COPY . .
RUN npm ci
RUN npx playwright install chromium
CMD ["npx", "playwright", "test"]
```

For shared memory issues:

```yaml
# GitHub Actions — increase /dev/shm
jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: mcr.microsoft.com/playwright:v1.50.0-noble
      options: --shm-size=2gb

# Docker run — increase shared memory
# docker run --shm-size=2gb my-test-image
```

For running as root in Docker:

```typescript
// TypeScript — playwright.config.ts (only for Docker/CI)
export default defineConfig({
  use: {
    launchOptions: {
      args: process.env.CI ? ['--no-sandbox', '--disable-setuid-sandbox'] : [],
    },
  },
});
```

```javascript
// JavaScript — playwright.config.js
module.exports = defineConfig({
  use: {
    launchOptions: {
      args: process.env.CI ? ['--no-sandbox', '--disable-setuid-sandbox'] : [],
    },
  },
});
```

**Related**: [ci/ci-github-actions.md](../ci/ci-github-actions.md), [ci/docker-and-containers.md](../ci/docker-and-containers.md)

---

### "Error: Playwright Test needs to be invoked via 'npx playwright test'"

**Cause**: The test file was executed directly with `node` or `ts-node` instead of through the Playwright test runner.

**Common triggers**:
- Running `node tests/example.spec.ts` or `ts-node tests/example.spec.ts`
- A misconfigured IDE run configuration that invokes `node` directly
- Using Jest or Mocha to run Playwright test files that import from `@playwright/test`
- A CI script that calls the wrong command

**Fix**: Always use the Playwright CLI to run tests.

```bash
# Correct invocations
npx playwright test                           # run all tests
npx playwright test tests/login.spec.ts       # run specific file
npx playwright test --grep "login"            # run tests matching pattern
npx playwright test --project=chromium        # run specific project
npx playwright test --debug                   # run with inspector

# If using a package.json script
# package.json
# "scripts": { "test:e2e": "playwright test" }
npm run test:e2e
```

For IDE configuration (VS Code):

```json
// .vscode/settings.json — install the Playwright VS Code extension instead of custom configs
{
  "playwright.reuseBrowser": true
}
```

**Related**: [core/configuration.md](configuration.md)

---

## Additional Common Errors

---

### "Error: page.evaluate: Execution context was destroyed"

**Cause**: The page navigated or reloaded while `page.evaluate()` was executing JavaScript in the browser context.

**Common triggers**:
- Calling `evaluate()` while the page is in the middle of a navigation
- A timer or event on the page triggers a redirect during evaluation
- Running `evaluate()` in a `beforeEach` that races with `page.goto()`

**Fix**: Ensure the page is stable before evaluating.

```typescript
// TypeScript

// BAD — evaluate races with navigation
await page.goto('/dashboard');
const title = await page.evaluate(() => document.title); // context might be destroyed

// GOOD — wait for load state first
await page.goto('/dashboard');
await page.waitForLoadState('domcontentloaded');
const title = await page.evaluate(() => document.title);

// GOOD — prefer locator-based assertions (no evaluate needed)
await page.goto('/dashboard');
await expect(page).toHaveTitle('Dashboard');
```

```javascript
// JavaScript

// GOOD — wait for load state first
await page.goto('/dashboard');
await page.waitForLoadState('domcontentloaded');
const title = await page.evaluate(() => document.title);

// GOOD — prefer locator-based assertions
await page.goto('/dashboard');
await expect(page).toHaveTitle('Dashboard');
```

**Related**: [core/assertions-and-waiting.md](assertions-and-waiting.md)

---

### "Error: page.screenshot: Cannot take a screenshot larger than..."

**Cause**: The requested screenshot dimensions exceed Playwright's limit (typically 16384x16384 pixels). This happens with full-page screenshots of very long pages.

**Common triggers**:
- `page.screenshot({ fullPage: true })` on an infinitely-scrolling page
- Pages with extremely tall content (long data tables, chat logs)
- CSS bugs that create enormous element heights

**Fix**: Clip the screenshot to a specific region or limit the viewport.

```typescript
// TypeScript

// BAD — might exceed size limits on tall pages
await page.screenshot({ fullPage: true, path: 'full.png' });

// GOOD — clip to a specific region
await page.screenshot({
  path: 'clipped.png',
  clip: { x: 0, y: 0, width: 1280, height: 2000 },
});

// GOOD — screenshot a specific element instead
await page.getByRole('main').screenshot({ path: 'main-content.png' });

// GOOD — set a reasonable viewport before full-page screenshot
await page.setViewportSize({ width: 1280, height: 720 });
await page.screenshot({ fullPage: true, path: 'full.png' });
```

```javascript
// JavaScript

// GOOD — clip to a specific region
await page.screenshot({
  path: 'clipped.png',
  clip: { x: 0, y: 0, width: 1280, height: 2000 },
});

// GOOD — screenshot a specific element
await page.getByRole('main').screenshot({ path: 'main-content.png' });
```

**Related**: [core/visual-regression.md](visual-regression.md)

---

### "Error: waiting for locator('...').toBeAttached()"

**Cause**: The element never entered the DOM within the assertion timeout. Unlike `toBeVisible()`, `toBeAttached()` only checks DOM presence — but the element was never rendered at all.

**Common triggers**:
- The component is conditionally rendered and the condition is not met
- A network request that populates the data has not completed
- Wrong selector that does not match any element
- The element is rendered by a lazy-loaded chunk that has not downloaded yet

**Fix**: Verify the precondition for the element to render.

```typescript
// TypeScript

// Ensure the data loads before asserting
await page.goto('/users');
await page.waitForResponse(resp => resp.url().includes('/api/users'));
await expect(page.getByRole('table')).toBeAttached();

// For lazy-loaded content, wait longer or trigger the load
await page.getByRole('tab', { name: 'Advanced' }).click();
await expect(page.getByTestId('advanced-panel')).toBeAttached({ timeout: 10_000 });
```

```javascript
// JavaScript

await page.goto('/users');
await page.waitForResponse(resp => resp.url().includes('/api/users'));
await expect(page.getByRole('table')).toBeAttached();

await page.getByRole('tab', { name: 'Advanced' }).click();
await expect(page.getByTestId('advanced-panel')).toBeAttached({ timeout: 10_000 });
```

**Related**: [core/assertions-and-waiting.md](assertions-and-waiting.md), [core/locators.md](locators.md)

---

### "Error: protocol error: Target.createTarget: Failed to create target"

**Cause**: The browser could not create a new tab or context, usually due to resource exhaustion.

**Common triggers**:
- Opening too many pages or contexts without closing them
- Memory leak in tests — each test opens a context but never closes it
- Running many parallel workers on a resource-constrained CI machine
- Browser process is unstable after a previous crash

**Fix**: Reduce parallelism, close unused contexts, or use fewer workers.

```typescript
// TypeScript — playwright.config.ts

export default defineConfig({
  // Reduce parallelism if resources are limited
  workers: process.env.CI ? 2 : undefined,

  // Limit to one browser context per worker
  fullyParallel: false, // run test files serially within a worker
});
```

```javascript
// JavaScript — playwright.config.js

module.exports = defineConfig({
  workers: process.env.CI ? 2 : undefined,
  fullyParallel: false,
});
```

If you manually create contexts, always close them:

```typescript
// TypeScript
test('multi-user test', async ({ browser }) => {
  const userContext = await browser.newContext();
  const adminContext = await browser.newContext();
  try {
    const userPage = await userContext.newPage();
    const adminPage = await adminContext.newPage();
    // ... test logic
  } finally {
    await userContext.close();
    await adminContext.close();
  }
});
```

```javascript
// JavaScript
test('multi-user test', async ({ browser }) => {
  const userContext = await browser.newContext();
  const adminContext = await browser.newContext();
  try {
    const userPage = await userContext.newPage();
    const adminPage = await adminContext.newPage();
    // ... test logic
  } finally {
    await userContext.close();
    await adminContext.close();
  }
});
```

**Related**: [ci/parallel-and-sharding.md](../ci/parallel-and-sharding.md), [core/multi-user-and-collaboration.md](multi-user-and-collaboration.md)

---

### "Error: expect(locator).toHaveText() — expected string but received array"

**Cause**: The locator matched multiple elements and `toHaveText()` returned an array of strings instead of a single string.

**Common triggers**:
- Using a broad locator like `page.locator('.item')` that matches a list
- Expecting a single heading but the selector matches multiple
- Not scoping the locator to a specific container

**Fix**: Either narrow the locator to one element or use the array form of `toHaveText()`.

```typescript
// TypeScript

// BAD — locator matches multiple elements
await expect(page.locator('.item')).toHaveText('First Item');

// GOOD — narrow to one element
await expect(page.locator('.item').first()).toHaveText('First Item');

// GOOD — assert against an array when multiple elements are expected
await expect(page.locator('.item')).toHaveText([
  'First Item',
  'Second Item',
  'Third Item',
]);

// GOOD — use a more specific locator
await expect(page.getByRole('heading', { level: 1 })).toHaveText('Welcome');
```

```javascript
// JavaScript

// GOOD — narrow to one element
await expect(page.locator('.item').first()).toHaveText('First Item');

// GOOD — assert against an array
await expect(page.locator('.item')).toHaveText([
  'First Item',
  'Second Item',
  'Third Item',
]);

// GOOD — use a more specific locator
await expect(page.getByRole('heading', { level: 1 })).toHaveText('Welcome');
```

**Related**: [core/assertions-and-waiting.md](assertions-and-waiting.md), [core/locators.md](locators.md)

---

### "Error: page.waitForSelector: Timeout 30000ms exceeded (deprecated)"

**Cause**: `page.waitForSelector()` timed out. This method is deprecated in favor of locator-based assertions.

**Common triggers**:
- Using legacy `page.waitForSelector()` from older tutorials or migration from Puppeteer
- The selector does not match any element in the DOM
- The element exists but does not meet the state requirement (e.g., `{ state: 'visible' }` but element is hidden)

**Fix**: Replace `waitForSelector()` with locator-based assertions.

```typescript
// TypeScript

// BAD — deprecated, no auto-retry, not composable
await page.waitForSelector('.loading', { state: 'hidden' });
await page.waitForSelector('.content', { state: 'visible' });

// GOOD — locator-based assertions with auto-retry
await expect(page.locator('.loading')).toBeHidden();
await expect(page.locator('.content')).toBeVisible();

// GOOD — use role-based locators for even more resilience
await expect(page.getByRole('progressbar')).toBeHidden();
await expect(page.getByRole('main')).toBeVisible();
```

```javascript
// JavaScript

// BAD — deprecated
await page.waitForSelector('.loading', { state: 'hidden' });
await page.waitForSelector('.content', { state: 'visible' });

// GOOD — locator-based assertions
await expect(page.locator('.loading')).toBeHidden();
await expect(page.locator('.content')).toBeVisible();

// GOOD — role-based locators
await expect(page.getByRole('progressbar')).toBeHidden();
await expect(page.getByRole('main')).toBeVisible();
```

**Related**: [core/locators.md](locators.md), [core/assertions-and-waiting.md](assertions-and-waiting.md), [migration/from-selenium.md](../migration/from-selenium.md)

---

### "Error: Test was expected to have a title matching /.../"

**Cause**: The `expect(page).toHaveTitle()` assertion failed because the page title did not match the expected value or pattern within the timeout.

**Common triggers**:
- The page has not finished loading and the title is still the initial empty or default value
- The SPA updates the document title asynchronously after rendering
- The expected title has a typo or does not match case-sensitively
- The page redirected to an error page with a different title

**Fix**: Ensure the page is fully loaded and use the correct expected value.

```typescript
// TypeScript

// toHaveTitle auto-retries, but ensure the page has loaded
await page.goto('/dashboard');
await expect(page).toHaveTitle('Dashboard | MyApp');

// Use regex for flexible matching
await expect(page).toHaveTitle(/Dashboard/);

// Debug: check what the actual title is
console.log(await page.title());
```

```javascript
// JavaScript

await page.goto('/dashboard');
await expect(page).toHaveTitle('Dashboard | MyApp');

// Use regex for flexible matching
await expect(page).toHaveTitle(/Dashboard/);

// Debug: check what the actual title is
console.log(await page.title());
```

**Related**: [core/assertions-and-waiting.md](assertions-and-waiting.md)

---

### "Error: page.type: Element is not focusable"

**Cause**: `page.type()` or `locator.type()` could not focus the target element before typing. The element may be hidden, disabled, or not an input.

**Common triggers**:
- The element is covered by an overlay or modal
- The element has `tabindex="-1"` and is not natively focusable
- Using `type()` instead of `fill()` — `fill()` is preferred in almost all cases
- The element is inside a Shadow DOM and the locator does not pierce it

**Fix**: Use `fill()` instead of `type()`. Only use `type()` when you specifically need to simulate individual keystrokes.

```typescript
// TypeScript

// BAD — type() is slower and more fragile
await page.locator('#search').type('hello');

// GOOD — fill() clears and sets the value directly
await page.getByRole('searchbox').fill('hello');

// When you truly need keystroke-by-keystroke input (e.g., autocomplete trigger)
await page.getByRole('searchbox').pressSequentially('hello', { delay: 100 });
```

```javascript
// JavaScript

// GOOD — fill() is preferred
await page.getByRole('searchbox').fill('hello');

// Keystroke-by-keystroke when needed (e.g., autocomplete)
await page.getByRole('searchbox').pressSequentially('hello', { delay: 100 });
```

**Related**: [core/locators.md](locators.md), [core/forms-and-validation.md](forms-and-validation.md)

---

### "Error: page.setInputFiles: Non-multiple file input can only accept single file"

**Cause**: Attempted to upload multiple files to an `<input type="file">` that does not have the `multiple` attribute.

**Common triggers**:
- Passing an array of files to a single-file upload input
- The app uses a custom upload component that only handles one file at a time

**Fix**: Upload one file at a time, or ensure the input supports multiple files.

```typescript
// TypeScript

// BAD — input does not have multiple attribute
await page.getByLabel('Upload file').setInputFiles([
  'file1.pdf',
  'file2.pdf', // error: non-multiple input
]);

// GOOD — single file
await page.getByLabel('Upload file').setInputFiles('file1.pdf');

// GOOD — for multiple file input (must have multiple attribute in HTML)
await page.getByLabel('Upload files').setInputFiles([
  'file1.pdf',
  'file2.pdf',
]);

// To clear the file input
await page.getByLabel('Upload file').setInputFiles([]);
```

```javascript
// JavaScript

// GOOD — single file
await page.getByLabel('Upload file').setInputFiles('file1.pdf');

// GOOD — multiple files (input must have multiple attribute)
await page.getByLabel('Upload files').setInputFiles([
  'file1.pdf',
  'file2.pdf',
]);

// To clear the file input
await page.getByLabel('Upload file').setInputFiles([]);
```

**Related**: [core/file-operations.md](file-operations.md), [core/file-upload-download.md](file-upload-download.md)

---

### "Error: browser.newContext: Could not parse content-type application/json"

**Cause**: The `storageState` option was given a path to a file with invalid JSON content, or the file is not a valid Playwright storage state format.

**Common triggers**:
- The auth setup wrote an empty file or incomplete JSON
- The storage state file was corrupted or truncated
- Manually editing the storage state file and introducing a syntax error
- The auth setup failed silently (login did not complete) and saved an invalid state

**Fix**: Delete the storage state file and regenerate it.

```bash
# Delete the corrupted file
rm -f playwright/.auth/user.json

# Re-run the setup
npx playwright test --project=setup
```

To prevent this, add error checking in the auth setup:

```typescript
// TypeScript — auth.setup.ts
import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Verify login actually succeeded before saving state
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  await page.context().storageState({ path: authFile });
});
```

```javascript
// JavaScript — auth.setup.js
const { test: setup, expect } = require('@playwright/test');

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Verify login actually succeeded before saving state
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  await page.context().storageState({ path: authFile });
});
```

**Related**: [core/authentication.md](authentication.md), [core/auth-flows.md](auth-flows.md)

---

## Quick Diagnostic Checklist

When you hit an error not listed above, run through this checklist:

1. **Read the full error** — Playwright errors include the locator, action, and a snippet of the page state. The answer is often in the details.
2. **Enable traces** — Add `trace: 'on'` temporarily or `trace: 'on-first-retry'` in config. Run `npx playwright show-trace trace.zip` to see screenshots, DOM, network, and console at the point of failure.
3. **Use the Playwright Inspector** — Run `npx playwright test --debug` to step through the test interactively.
4. **Check the locator** — Run `npx playwright codegen <url>` to verify locators against the live page.
5. **Check the Playwright version** — Run `npx playwright --version`. Ensure `@playwright/test` and browser binaries are the same version.
6. **Search the Playwright issue tracker** — Many errors have known solutions in [github.com/microsoft/playwright/issues](https://github.com/microsoft/playwright/issues).
