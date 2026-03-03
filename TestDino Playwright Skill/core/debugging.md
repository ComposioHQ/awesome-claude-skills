# Debugging Playwright Tests

> **When to use**: A test is failing and you need to understand why — wrong selectors, timing issues, network failures, or unexpected application state.

## Quick Reference

| Tool | Command | Best For |
|---|---|---|
| UI Mode | `npx playwright test --ui` | Interactive exploration, visual timeline, re-running tests |
| Playwright Inspector | `PWDEBUG=1 npx playwright test` | Step-through debugging, selector playground |
| Trace Viewer | `npx playwright show-trace trace.zip` | Post-mortem CI failure analysis |
| Headed mode | `npx playwright test --headed` | Watching the browser during test execution |
| Slow motion | `npx playwright test --headed --slow-mo=500` | Visually following fast interactions |
| `page.pause()` | Insert in test code | Pausing at an exact point to inspect state |
| Verbose API logs | `DEBUG=pw:api npx playwright test` | Seeing every Playwright API call with timing |
| VS Code extension | Playwright Test for VS Code | Breakpoints, step-through, pick locator |

## Systematic Debugging Workflow

Follow this order. Do not skip to step 5 — most issues resolve by step 2.

```
1. Read the full error message
   └─ Check troubleshooting/error-index.md for known patterns
2. Run with --ui to see what happened visually
   └─ Timeline shows every action, screenshot at failure point
3. Enable tracing if not already on
   └─ use: { trace: 'on' } temporarily in config
4. Check the network tab in trace for API failures
   └─ Missing responses, 4xx/5xx, CORS errors
5. Insert page.pause() at the failure point
   └─ Inspect live DOM, try selectors in console
6. Check browser console for JavaScript errors
   └─ page.on('console') or console tab in trace
```

## Patterns

### Pattern 1: UI Mode for Interactive Debugging

**Use when**: Developing new tests, investigating failures locally, exploring application behavior.
**Avoid when**: CI environments (use traces instead).

UI Mode provides a visual timeline, DOM snapshots at each step, network waterfall, and the ability to re-run individual tests.

**TypeScript**
```typescript
// Launch UI Mode from terminal:
// npx playwright test --ui

// Run a specific test file in UI Mode:
// npx playwright test tests/checkout.spec.ts --ui

// playwright.config.ts — configure for UI Mode convenience
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    // Traces are always available in UI Mode regardless of this setting,
    // but this ensures traces are captured for CI failures too
    trace: 'on-first-retry',
  },
});
```

**JavaScript**
```javascript
// Launch UI Mode from terminal:
// npx playwright test --ui

// Run a specific test file in UI Mode:
// npx playwright test tests/checkout.spec.js --ui

// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  use: {
    trace: 'on-first-retry',
  },
});
```

### Pattern 2: Playwright Inspector with PWDEBUG

**Use when**: You need to step through actions one at a time, test selectors interactively, or see the exact state before and after each action.
**Avoid when**: The failure is visible from the error message or trace alone.

**TypeScript**
```typescript
// Launch Inspector from terminal:
// PWDEBUG=1 npx playwright test tests/login.spec.ts

// On Windows PowerShell:
// $env:PWDEBUG=1; npx playwright test tests/login.spec.ts

// On Windows CMD:
// set PWDEBUG=1 && npx playwright test tests/login.spec.ts

// Inspector opens automatically. Use these controls:
// - "Step over" button: execute one action at a time
// - "Pick locator" button: hover elements to see the best locator
// - "Resume" button: run to the next page.pause() or end

import { test, expect } from '@playwright/test';

test('debug login flow', async ({ page }) => {
  await page.goto('/login');

  // Inspector pauses before each action when PWDEBUG=1
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**JavaScript**
```javascript
// Launch Inspector from terminal:
// PWDEBUG=1 npx playwright test tests/login.spec.js

const { test, expect } = require('@playwright/test');

test('debug login flow', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

### Pattern 3: Trace Viewer for CI Failure Analysis

**Use when**: A test fails in CI and you need to understand what happened without re-running locally.
**Avoid when**: You can reproduce the failure locally (use UI Mode or Inspector instead).

**TypeScript**
```typescript
// playwright.config.ts — trace configuration
import { defineConfig } from '@playwright/test';

export default defineConfig({
  retries: process.env.CI ? 2 : 0,
  use: {
    // 'on-first-retry' — captures trace on first retry only (recommended for CI)
    // 'on' — captures every run (use temporarily for stubborn failures)
    // 'retain-on-failure' — captures every run, keeps only failures
    trace: 'on-first-retry',
  },
});

// After CI failure, download the trace artifact and open it:
// npx playwright show-trace test-results/tests-login-Login-test-chromium/trace.zip

// Or open from URL:
// npx playwright show-trace https://ci.example.com/artifacts/trace.zip

// Or use trace.playwright.dev to view traces in the browser — drag and drop the zip file
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

// After CI failure, download the trace artifact and open it:
// npx playwright show-trace test-results/tests-login-Login-test-chromium/trace.zip
```

**Reading a trace — what to check in order:**

1. **Actions tab** — see every Playwright action with before/after screenshots
2. **Console tab** — browser console output (errors, warnings, logs)
3. **Network tab** — every HTTP request with status, timing, request/response bodies
4. **Source tab** — test source code highlighting the failing line
5. **Call tab** — exact arguments and return values of each Playwright call

### Pattern 4: Headed Mode with Slow Motion

**Use when**: You want to watch the browser during execution without the full Inspector overhead.
**Avoid when**: The test runs too fast to follow even with slow-mo (use Inspector instead).

**TypeScript**
```typescript
// From terminal — quick visual debugging:
// npx playwright test tests/checkout.spec.ts --headed --slow-mo=500

// playwright.config.ts — configure headed mode for local development
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    // Do NOT commit these — use CLI flags or environment checks instead
    headless: !process.env.HEADED,
    launchOptions: {
      slowMo: process.env.SLOW_MO ? parseInt(process.env.SLOW_MO) : 0,
    },
  },
});

// Then run:
// HEADED=1 SLOW_MO=500 npx playwright test tests/checkout.spec.ts
```

**JavaScript**
```javascript
// From terminal:
// npx playwright test tests/checkout.spec.js --headed --slow-mo=500

// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  use: {
    headless: !process.env.HEADED,
    launchOptions: {
      slowMo: process.env.SLOW_MO ? parseInt(process.env.SLOW_MO) : 0,
    },
  },
});
```

### Pattern 5: VS Code Integration

**Use when**: You prefer IDE-based debugging with breakpoints, variable inspection, and integrated test running.
**Avoid when**: You are debugging CI-only failures that do not reproduce locally.

Install the **Playwright Test for VS Code** extension (`ms-playwright.playwright`).

**Key capabilities:**
- **Run/debug individual tests** — click the green play button in the gutter next to any `test()`
- **Set breakpoints** — click the gutter to set breakpoints; tests pause at them automatically
- **Pick locator** — use the "Pick locator" command to hover over elements and get the best selector
- **Show browser** — check "Show Browser" in the testing sidebar to see the browser during execution
- **Watch mode** — enable to re-run tests on file save

**TypeScript**
```typescript
// When debugging in VS Code, use test.only() to focus on one test
// instead of running the entire suite through the debugger
import { test, expect } from '@playwright/test';

test.only('debug this specific test', async ({ page }) => {
  await page.goto('/products');

  // Set a VS Code breakpoint on this line, then inspect `page` in the debug panel
  const productCard = page.getByRole('listitem').filter({ hasText: 'Widget' });
  await expect(productCard).toBeVisible();

  await productCard.getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.only('debug this specific test', async ({ page }) => {
  await page.goto('/products');

  const productCard = page.getByRole('listitem').filter({ hasText: 'Widget' });
  await expect(productCard).toBeVisible();

  await productCard.getByRole('button', { name: 'Add to cart' }).click();
  await expect(page.getByTestId('cart-count')).toHaveText('1');
});
```

### Pattern 6: Capturing Browser Console Logs

**Use when**: Suspecting JavaScript errors, failed client-side API calls, or application-level logging that explains the failure.
**Avoid when**: The issue is clearly a selector or timing problem visible in the trace.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('capture console output', async ({ page }) => {
  // Collect all console messages
  const consoleLogs: string[] = [];
  page.on('console', (msg) => {
    consoleLogs.push(`[${msg.type()}] ${msg.text()}`);
  });

  // Capture uncaught exceptions
  page.on('pageerror', (error) => {
    console.error('Page error:', error.message);
  });

  await page.goto('/dashboard');
  await page.getByRole('button', { name: 'Load data' }).click();
  await expect(page.getByRole('table')).toBeVisible();

  // Print collected logs on failure for debugging context
  console.log('Browser console output:', consoleLogs);
});

// Reusable fixture for console logging across all tests
import { test as base } from '@playwright/test';

type ConsoleFixtures = {
  consoleMessages: string[];
};

export const test = base.extend<ConsoleFixtures>({
  consoleMessages: async ({ page }, use) => {
    const messages: string[] = [];
    page.on('console', (msg) => messages.push(`[${msg.type()}] ${msg.text()}`));
    page.on('pageerror', (err) => messages.push(`[pageerror] ${err.message}`));
    await use(messages);
  },
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('capture console output', async ({ page }) => {
  const consoleLogs = [];
  page.on('console', (msg) => {
    consoleLogs.push(`[${msg.type()}] ${msg.text()}`);
  });

  page.on('pageerror', (error) => {
    console.error('Page error:', error.message);
  });

  await page.goto('/dashboard');
  await page.getByRole('button', { name: 'Load data' }).click();
  await expect(page.getByRole('table')).toBeVisible();

  console.log('Browser console output:', consoleLogs);
});

// Reusable fixture for console logging
const { test: base } = require('@playwright/test');

const test = base.extend({
  consoleMessages: async ({ page }, use) => {
    const messages = [];
    page.on('console', (msg) => messages.push(`[${msg.type()}] ${msg.text()}`));
    page.on('pageerror', (err) => messages.push(`[pageerror] ${err.message}`));
    await use(messages);
  },
});

module.exports = { test };
```

### Pattern 7: Screenshots on Failure

**Use when**: You need a visual snapshot at the exact moment of failure.
**Avoid when**: Traces are enabled (they already include screenshots at every step).

**TypeScript**
```typescript
// playwright.config.ts — automatic screenshots on failure
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    // 'off' — no screenshots (default)
    // 'on' — screenshot after every test
    // 'only-on-failure' — screenshot only when test fails (recommended)
    screenshot: 'only-on-failure',
  },
});
```

```typescript
// Manual screenshot at a specific point
import { test, expect } from '@playwright/test';

test('debug visual state', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByLabel('Promo code').fill('SAVE20');
  await page.getByRole('button', { name: 'Apply' }).click();

  // Capture screenshot before assertion for debugging
  await page.screenshot({ path: 'test-results/before-discount.png', fullPage: true });

  await expect(page.getByTestId('discount-amount')).toHaveText('-$20.00');
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  use: {
    screenshot: 'only-on-failure',
  },
});
```

```javascript
// Manual screenshot
const { test, expect } = require('@playwright/test');

test('debug visual state', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByLabel('Promo code').fill('SAVE20');
  await page.getByRole('button', { name: 'Apply' }).click();

  await page.screenshot({ path: 'test-results/before-discount.png', fullPage: true });

  await expect(page.getByTestId('discount-amount')).toHaveText('-$20.00');
});
```

### Pattern 8: Network Debugging

**Use when**: Suspecting API failures, wrong request payloads, missing auth headers, or slow responses causing timeouts.
**Avoid when**: The trace network tab already shows the problem.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('debug network requests', async ({ page }) => {
  // Log all requests
  page.on('request', (request) => {
    console.log(`>> ${request.method()} ${request.url()}`);
  });

  // Log all responses with status
  page.on('response', (response) => {
    console.log(`<< ${response.status()} ${response.url()}`);
  });

  // Log failed requests (network errors, not HTTP errors)
  page.on('requestfailed', (request) => {
    console.log(`FAILED: ${request.url()} ${request.failure()?.errorText}`);
  });

  await page.goto('/dashboard');
  await page.getByRole('button', { name: 'Refresh' }).click();
  await expect(page.getByRole('table')).toBeVisible();
});

// Wait for a specific API response and inspect it
test('inspect API response', async ({ page }) => {
  await page.goto('/products');

  const responsePromise = page.waitForResponse(
    (resp) => resp.url().includes('/api/products') && resp.status() === 200
  );

  await page.getByRole('button', { name: 'Load products' }).click();

  const response = await responsePromise;
  const body = await response.json();
  console.log('API response:', JSON.stringify(body, null, 2));

  await expect(page.getByRole('listitem')).toHaveCount(body.products.length);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('debug network requests', async ({ page }) => {
  page.on('request', (request) => {
    console.log(`>> ${request.method()} ${request.url()}`);
  });

  page.on('response', (response) => {
    console.log(`<< ${response.status()} ${response.url()}`);
  });

  page.on('requestfailed', (request) => {
    console.log(`FAILED: ${request.url()} ${request.failure()?.errorText}`);
  });

  await page.goto('/dashboard');
  await page.getByRole('button', { name: 'Refresh' }).click();
  await expect(page.getByRole('table')).toBeVisible();
});

test('inspect API response', async ({ page }) => {
  await page.goto('/products');

  const responsePromise = page.waitForResponse(
    (resp) => resp.url().includes('/api/products') && resp.status() === 200
  );

  await page.getByRole('button', { name: 'Load products' }).click();

  const response = await responsePromise;
  const body = await response.json();
  console.log('API response:', JSON.stringify(body, null, 2));

  await expect(page.getByRole('listitem')).toHaveCount(body.products.length);
});
```

### Pattern 9: Verbose API Logs

**Use when**: You need to see every single Playwright API call with timing to identify where the test is spending time or getting stuck.
**Avoid when**: You already know which action is failing (use Inspector or `page.pause()` instead).

```bash
# See all Playwright API calls with timestamps
DEBUG=pw:api npx playwright test tests/slow-test.spec.ts

# See browser protocol messages (very verbose — use sparingly)
DEBUG=pw:protocol npx playwright test tests/slow-test.spec.ts

# Combine multiple debug channels
DEBUG=pw:api,pw:browser npx playwright test tests/slow-test.spec.ts

# Windows PowerShell
$env:DEBUG="pw:api"; npx playwright test tests/slow-test.spec.ts

# Windows CMD
set DEBUG=pw:api && npx playwright test tests/slow-test.spec.ts
```

### Pattern 10: `page.pause()` — Inline Breakpoints

**Use when**: You need to pause execution at a precise point to inspect the live DOM, try locators, or check application state.
**Avoid when**: You can use `PWDEBUG=1` which pauses at every step automatically.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('debug with pause', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByLabel('Email').fill('user@example.com');

  // Execution pauses here — Inspector opens with:
  // - Live DOM inspection
  // - Selector playground (try locators in the console)
  // - Step through remaining actions
  await page.pause();

  // These actions wait until you click "Resume" in the Inspector
  await page.getByRole('button', { name: 'Continue' }).click();
  await expect(page.getByText('Order confirmed')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('debug with pause', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByLabel('Email').fill('user@example.com');

  // Execution pauses here — Inspector opens
  await page.pause();

  await page.getByRole('button', { name: 'Continue' }).click();
  await expect(page.getByText('Order confirmed')).toBeVisible();
});
```

**Important**: Remove `page.pause()` before committing. It will hang indefinitely in CI. Use this lint rule or CI check:

```bash
# Add to your pre-commit hook or CI pipeline
grep -r "page.pause()" tests/ && echo "ERROR: Remove page.pause() before committing" && exit 1
```

## Decision Guide

Use this table to pick the right tool based on the failure type.

| Failure Type | First Tool | Why |
|---|---|---|
| **Element not found** (selector wrong) | UI Mode (`--ui`) | See the DOM at the moment of failure, try selectors in Pick Locator |
| **Element not found** (timing issue) | Trace Viewer — Actions tab | Compare before/after screenshots to see if element appeared after timeout |
| **Wrong text / value** | Trace Viewer — Actions tab | Inspect the actual DOM content at each action step |
| **Test hangs / times out** | `DEBUG=pw:api` | See which API call is waiting and never resolving |
| **Network / API failure** | Trace Viewer — Network tab | See request/response status codes, payloads, timing |
| **Auth / session issues** | Network debugging (`page.on('response')`) | Check for 401/403 responses, missing cookies/tokens |
| **Visual rendering wrong** | `--headed --slow-mo=500` | Watch the actual rendering in the browser |
| **JavaScript error in app** | Console logging (`page.on('console')`) | Catch uncaught exceptions and error logs |
| **CI-only failure** | Trace Viewer (from CI artifact) | Reproduce the exact CI state without running locally |
| **Flaky / intermittent** | Trace on every run (`trace: 'on'`) + retries | Compare passing and failing traces side by side |
| **State pollution** | Run single test with `test.only()` | Isolate from other tests; if it passes alone, state leaks from another test |

## Anti-Patterns

### Adding `waitForTimeout` to fix timing issues

```typescript
// WRONG — arbitrary delays mask the real problem and make tests slow and flaky
await page.getByRole('button', { name: 'Submit' }).click();
await page.waitForTimeout(3000); // "It works with this delay"
await expect(page.getByText('Success')).toBeVisible();

// RIGHT — wait for the actual condition
await page.getByRole('button', { name: 'Submit' }).click();
await expect(page.getByText('Success')).toBeVisible(); // Auto-retries for up to 5s
```

If the default timeout is insufficient, investigate *why* the operation is slow, then either:
- Fix the application performance
- Increase the specific assertion timeout: `await expect(locator).toBeVisible({ timeout: 15000 })`
- Wait for a prerequisite: `await page.waitForResponse('**/api/submit')`

### Commenting out tests to isolate a failure

```typescript
// WRONG — commenting out tests to find which one causes the failure
// test('test A', ...);
// test('test B', ...);
test('test C — this one fails', async ({ page }) => { /* ... */ });

// RIGHT — use .only to run a single test
test.only('test C — this one fails', async ({ page }) => { /* ... */ });

// RIGHT — use grep to run tests matching a pattern
// npx playwright test --grep "test C"
```

### Not reading the full error message

Playwright error messages include:
- The **expected** vs **actual** value
- The **locator** that was used
- A **call log** showing what Playwright tried before timing out
- The **line number** in your test

Read all of it. The call log alone often shows exactly what went wrong (e.g., "waiting for selector to be visible" when the element exists but is hidden).

### Debugging in CI without traces

```typescript
// WRONG — no traces in CI, no way to debug failures
export default defineConfig({
  use: {
    trace: 'off',
  },
});

// RIGHT — always capture traces on failure in CI
export default defineConfig({
  retries: process.env.CI ? 2 : 0,
  use: {
    trace: 'on-first-retry',
  },
});
```

### Using `console.log` instead of proper debugging tools

```typescript
// WRONG — sprinkling console.log everywhere
test('debug with logs', async ({ page }) => {
  await page.goto('/dashboard');
  console.log('page loaded');
  const el = page.getByRole('button', { name: 'Save' });
  console.log('button found:', await el.isVisible());
  console.log('button text:', await el.textContent());
  // ...20 more console.log calls

  // RIGHT — use page.pause() at the point of interest
  await page.goto('/dashboard');
  await page.pause(); // Inspect everything interactively
});
```

### Leaving `page.pause()` or `test.only()` in committed code

```typescript
// WRONG — these should never reach CI
test.only('focused test', async ({ page }) => {  // Skips all other tests
  await page.goto('/');
  await page.pause();  // Hangs forever in CI
});

// Add a CI guard if needed during development
if (!process.env.CI) {
  await page.pause();
}
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Inspector does not open with `PWDEBUG=1` | Running in headless mode or workers > 1 | Run with `--headed` and `--workers=1` |
| Trace is empty or missing | `trace: 'off'` in config, or test did not retry | Set `trace: 'on'` temporarily, or `trace: 'retain-on-failure'` |
| UI Mode shows stale test results | File watcher did not pick up changes | Stop UI Mode, clear `test-results/`, restart |
| `page.pause()` does nothing | `PWDEBUG` is not set and running headless | Run with `--headed` or set `PWDEBUG=1` |
| Screenshots are blank or wrong size | Viewport not set or test runs on wrong project | Set `viewport` in config; check which browser project ran |
| Verbose logs are overwhelming | Using `DEBUG=pw:protocol` | Use `DEBUG=pw:api` for a manageable level of detail |
| Trace file is too large | `trace: 'on'` for all tests, including passing | Switch to `trace: 'on-first-retry'` or `trace: 'retain-on-failure'` |
| VS Code does not detect tests | Wrong `testDir` or `testMatch` config | Ensure config paths match and extension settings point to your `playwright.config` |
| Network events not firing | Request was made before listener was attached | Attach `page.on('request')` and `page.on('response')` before `page.goto()` |

## Related

- [core/error-index.md](error-index.md) — look up specific error messages
- [core/flaky-tests.md](flaky-tests.md) — intermittent failure patterns and fixes
- [core/common-pitfalls.md](common-pitfalls.md) — common beginner mistakes
- [core/assertions-and-waiting.md](assertions-and-waiting.md) — web-first assertions and auto-waiting
- [core/configuration.md](configuration.md) — trace, screenshot, and retry configuration
- [ci/reporting-and-artifacts.md](../ci/reporting-and-artifacts.md) — CI artifact collection for traces and screenshots
