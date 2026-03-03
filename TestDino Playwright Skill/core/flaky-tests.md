# Flaky Tests

> **When to use**: A test passes sometimes and fails other times. You need to diagnose the root cause, fix it, and prevent it from happening again.
> **Prerequisites**: [core/assertions-and-waiting.md](assertions-and-waiting.md), [core/fixtures-and-hooks.md](fixtures-and-hooks.md)

## Quick Reference

```bash
# Burn-in test — run 10 times to expose flakiness
npx playwright test tests/checkout.spec.ts --repeat-each=10

# Run with retries to catch intermittent failures
npx playwright test --retries=3

# Run single test in isolation to rule out state leaks
npx playwright test tests/checkout.spec.ts --grep "adds item" --workers=1

# Run with tracing on every attempt for comparison
npx playwright test --retries=3 --trace=on

# Run in fully parallel mode to expose isolation issues
npx playwright test --fully-parallel --workers=4

# List flaky tests (tests that failed then passed on retry)
npx playwright test --retries=2 --reporter=json | jq '.suites[].specs[] | select(.ok == true and (.tests[].results | length > 1))'
```

## Patterns

### Flakiness Taxonomy

Every flaky test falls into one of four categories. Identify the category first, then apply the matching fix.

| Category | Symptom | Typical Root Cause | Diagnosis Method |
|---|---|---|---|
| **Timing / Async** | Fails intermittently everywhere | Race conditions, missing `await`, arbitrary waits | Fails locally with `--repeat-each=20` |
| **Test Isolation** | Fails only when run with other tests, passes alone | Shared mutable state, data collisions, test ordering dependency | Passes with `--workers=1 --grep "this test"`, fails in full suite |
| **Environment** | Fails only in CI, passes locally | Different OS, viewport, fonts, network latency, missing dependencies | Compare CI screenshots/traces with local; run in Docker locally |
| **Infrastructure** | Random failures unrelated to test logic | Browser crash, OOM, DNS resolution, file system race | Failures have no pattern; error messages reference browser internals |

### Diagnosis Flowchart

Follow this decision tree to identify which category your flaky test belongs to.

```
Test is flaky
|
+-- Does it fail locally with --repeat-each=20?
|   |
|   +-- YES --> TIMING / ASYNC issue
|   |           - Missing await
|   |           - Using waitForTimeout instead of assertions
|   |           - Race condition between action and assertion
|   |           - Not waiting for network response before asserting
|   |
|   +-- NO --> Does it fail only in CI?
|       |
|       +-- YES --> ENVIRONMENT issue
|       |           - Different viewport/screen size
|       |           - Missing fonts causing layout shift
|       |           - Slower CI machines hitting timeouts
|       |           - External services unavailable
|       |
|       +-- NO --> Does it fail only when run with other tests?
|           |
|           +-- YES --> ISOLATION issue
|           |           - Shared mutable state (module-level variables)
|           |           - Database/API state from previous test
|           |           - localStorage/cookies leaking between tests
|           |           - Parallel tests colliding on unique constraints
|           |
|           +-- NO --> INFRASTRUCTURE issue
|                       - Browser process crash
|                       - Out of memory
|                       - File system or network instability
|                       - Flaky third-party service
```

### Fix: Timing and Async Issues

**Use when**: The test fails locally with `--repeat-each=20`, or you see `waitForTimeout`, missing `await`, or race conditions.

The most common source of flakiness. The fix is always the same: replace arbitrary waits and manual checks with Playwright's auto-retrying mechanisms.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// ---- FIX 1: Replace waitForTimeout with assertions ----

// BAD — arbitrary delay, fails on slow machines, wastes time on fast ones
test('bad: uses arbitrary wait', async ({ page }) => {
  await page.goto('/dashboard');
  await page.getByRole('button', { name: 'Refresh' }).click();
  await page.waitForTimeout(3000); // hoping data loads in 3s
  await expect(page.getByTestId('data-table')).toBeVisible();
});

// GOOD — auto-retrying assertion waits exactly as long as needed
test('good: uses auto-retrying assertion', async ({ page }) => {
  await page.goto('/dashboard');
  await page.getByRole('button', { name: 'Refresh' }).click();
  await expect(page.getByTestId('data-table')).toBeVisible();
});

// ---- FIX 2: Wait for network responses before asserting ----

// BAD — clicks button and immediately asserts, but data comes from API
test('bad: does not wait for API response', async ({ page }) => {
  await page.goto('/users');
  await page.getByRole('button', { name: 'Load More' }).click();
  // Flaky: API response may not have arrived yet
  await expect(page.getByRole('listitem')).toHaveCount(20);
});

// GOOD — waits for the specific API response that populates the data
test('good: waits for API response', async ({ page }) => {
  await page.goto('/users');

  const responsePromise = page.waitForResponse(
    (resp) => resp.url().includes('/api/users') && resp.status() === 200
  );
  await page.getByRole('button', { name: 'Load More' }).click();
  await responsePromise;

  await expect(page.getByRole('listitem')).toHaveCount(20);
});

// ---- FIX 3: Handle animations and transitions ----

// BAD — element exists but is mid-animation, click lands on wrong target
test('bad: clicks during animation', async ({ page }) => {
  await page.goto('/modal-demo');
  await page.getByRole('button', { name: 'Open' }).click();
  // Modal is animating in — click may miss the button inside it
  await page.getByRole('button', { name: 'Confirm' }).click();
});

// GOOD — wait for the modal to be fully stable before interacting
test('good: waits for stable state', async ({ page }) => {
  await page.goto('/modal-demo');
  await page.getByRole('button', { name: 'Open' }).click();
  // toBeVisible auto-waits for stability (no animation in progress)
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.getByRole('button', { name: 'Confirm' }).click();
});

// ---- FIX 4: Use toPass() for multi-step assertions that must succeed together ----

test('good: retry entire assertion block', async ({ page }) => {
  await page.goto('/search');

  await expect(async () => {
    await page.getByLabel('Search').fill('playwright');
    await page.getByRole('button', { name: 'Search' }).click();
    await expect(page.getByTestId('result-count')).toHaveText('10 results');
  }).toPass({
    timeout: 15_000,
    intervals: [1_000, 2_000, 5_000],
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// FIX 1: Replace waitForTimeout with assertions
test('good: uses auto-retrying assertion', async ({ page }) => {
  await page.goto('/dashboard');
  await page.getByRole('button', { name: 'Refresh' }).click();
  await expect(page.getByTestId('data-table')).toBeVisible();
});

// FIX 2: Wait for network responses before asserting
test('good: waits for API response', async ({ page }) => {
  await page.goto('/users');

  const responsePromise = page.waitForResponse(
    (resp) => resp.url().includes('/api/users') && resp.status() === 200
  );
  await page.getByRole('button', { name: 'Load More' }).click();
  await responsePromise;

  await expect(page.getByRole('listitem')).toHaveCount(20);
});

// FIX 3: Handle animations and transitions
test('good: waits for stable state', async ({ page }) => {
  await page.goto('/modal-demo');
  await page.getByRole('button', { name: 'Open' }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.getByRole('button', { name: 'Confirm' }).click();
});

// FIX 4: Use toPass() for multi-step assertions
test('good: retry entire assertion block', async ({ page }) => {
  await page.goto('/search');

  await expect(async () => {
    await page.getByLabel('Search').fill('playwright');
    await page.getByRole('button', { name: 'Search' }).click();
    await expect(page.getByTestId('result-count')).toHaveText('10 results');
  }).toPass({
    timeout: 15_000,
    intervals: [1_000, 2_000, 5_000],
  });
});
```

### Fix: Test Isolation Issues

**Use when**: The test passes when run alone (`--grep "test name"`) but fails when run with other tests, or fails only in parallel mode.

Isolation issues come from shared state: module-level variables, database rows, localStorage, cookies, or file system artifacts.

**TypeScript**
```typescript
import { test as base, expect } from '@playwright/test';

// ---- FIX 1: Unique test data per test ----

// BAD — all parallel tests use the same email, causing unique constraint violations
test('bad: hardcoded data', async ({ page }) => {
  await page.goto('/register');
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByRole('button', { name: 'Register' }).click();
  await expect(page.getByText('Welcome')).toBeVisible();
});

// GOOD — unique email per test run
test('good: unique data per test', async ({ page }) => {
  const email = `test-${Date.now()}-${Math.random().toString(36).slice(2)}@example.com`;

  await page.goto('/register');
  await page.getByLabel('Email').fill(email);
  await page.getByRole('button', { name: 'Register' }).click();
  await expect(page.getByText('Welcome')).toBeVisible();
});

// ---- FIX 2: Worker-scoped fixtures for shared expensive resources ----

type WorkerFixtures = {
  workerAccount: { email: string; id: string };
};

export const test = base.extend<{}, WorkerFixtures>({
  workerAccount: [async ({ request }, use) => {
    const email = `worker-${Date.now()}-${Math.random().toString(36).slice(2)}@example.com`;
    const response = await request.post('/api/users', {
      data: { email, password: 'TestP@ss123!' },
    });
    const account = await response.json();

    await use({ email, id: account.id });

    // Cleanup after all tests in this worker are done
    await request.delete(`/api/users/${account.id}`);
  }, { scope: 'worker' }],
});

// ---- FIX 3: Clean up state in fixture teardown ----

export const testWithCleanup = base.extend({
  cleanPage: async ({ page }, use) => {
    await use(page);

    // Teardown: clear all client-side state
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.context().clearCookies();
  },
});

// ---- FIX 4: Isolate tests that cannot run in parallel ----

import { test } from '@playwright/test';

// Use serial mode ONLY for tests that genuinely depend on shared state
// (e.g., a multi-step wizard where each test is one step)
test.describe.serial('checkout wizard', () => {
  test('step 1: add items', async ({ page }) => {
    await page.goto('/shop');
    await page.getByRole('button', { name: 'Add Widget' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('1');
  });

  test('step 2: enter shipping', async ({ page }) => {
    await page.goto('/checkout/shipping');
    await page.getByLabel('Address').fill('123 Test St');
    await page.getByRole('button', { name: 'Continue' }).click();
  });
});
```

**JavaScript**
```javascript
const { test: base, expect } = require('@playwright/test');

// FIX 1: Unique test data per test
test('good: unique data per test', async ({ page }) => {
  const email = `test-${Date.now()}-${Math.random().toString(36).slice(2)}@example.com`;

  await page.goto('/register');
  await page.getByLabel('Email').fill(email);
  await page.getByRole('button', { name: 'Register' }).click();
  await expect(page.getByText('Welcome')).toBeVisible();
});

// FIX 2: Worker-scoped fixtures for shared expensive resources
const test = base.extend({
  workerAccount: [async ({ request }, use) => {
    const email = `worker-${Date.now()}-${Math.random().toString(36).slice(2)}@example.com`;
    const response = await request.post('/api/users', {
      data: { email, password: 'TestP@ss123!' },
    });
    const account = await response.json();

    await use({ email, id: account.id });

    await request.delete(`/api/users/${account.id}`);
  }, { scope: 'worker' }],
});

module.exports = { test, expect };
```

### Fix: Environment Issues

**Use when**: The test passes locally but fails in CI, or fails on certain operating systems, viewports, or machines.

Environment flakiness stems from differences in rendering, timing, available resources, or external service availability between your local machine and CI.

**TypeScript**
```typescript
// playwright.config.ts — environment-consistent configuration
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // ---- FIX 1: Disable animations for deterministic behavior ----
  use: {
    // Disable CSS animations and transitions
    contextOptions: {
      reducedMotion: 'reduce',
    },
  },

  // ---- FIX 2: Consistent viewport across environments ----
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Explicit viewport prevents layout differences between local and CI
        viewport: { width: 1280, height: 720 },
      },
    },
  ],

  // ---- FIX 3: Use webServer to start app in CI ----
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },

  // ---- FIX 4: Higher timeouts for slower CI machines ----
  timeout: process.env.CI ? 60_000 : 30_000,
  expect: {
    timeout: process.env.CI ? 10_000 : 5_000,
  },
});
```

```typescript
// tests/fixtures/stub-externals.ts — stub external services
import { test as base, expect } from '@playwright/test';

export const test = base.extend({
  // Auto fixture: block all external services in every test
  stubExternals: [async ({ page }, use) => {
    // Block third-party scripts that vary between environments
    await page.route(/google-analytics|segment|hotjar|intercom/, (route) =>
      route.abort()
    );

    // Stub flaky external API with consistent response
    await page.route('**/api.external-service.com/**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'ok', data: [] }),
      })
    );

    await use();
  }, { auto: true }],
});

export { expect };
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  use: {
    contextOptions: {
      reducedMotion: 'reduce',
    },
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
    },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  timeout: process.env.CI ? 60_000 : 30_000,
  expect: {
    timeout: process.env.CI ? 10_000 : 5_000,
  },
});
```

```javascript
// tests/fixtures/stub-externals.js
const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  stubExternals: [async ({ page }, use) => {
    await page.route(/google-analytics|segment|hotjar|intercom/, (route) =>
      route.abort()
    );

    await page.route('**/api.external-service.com/**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'ok', data: [] }),
      })
    );

    await use();
  }, { auto: true }],
});

module.exports = { test, expect };
```

### Detection Strategies

**Use when**: You suspect flakiness but the test does not fail consistently, or you want to validate a fix actually eliminated the flakiness.

**TypeScript**
```typescript
// ---- Strategy 1: Burn-in testing with --repeat-each ----
// Run a test 20 times. If it fails even once, it has a flakiness bug.
// npx playwright test tests/checkout.spec.ts --repeat-each=20

// ---- Strategy 2: Retry configuration to catch intermittent failures ----
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  // Retries in CI surface flaky tests in the report
  retries: process.env.CI ? 2 : 0,

  // Reporter shows which tests needed retries
  reporter: process.env.CI
    ? [['html', { open: 'never' }], ['json', { outputFile: 'results.json' }]]
    : [['html', { open: 'on-failure' }]],
});

// ---- Strategy 3: Custom reporter to track flaky test metrics ----
// flaky-reporter.ts
import type { Reporter, TestCase, TestResult } from '@playwright/test/reporter';

class FlakyReporter implements Reporter {
  private flakyTests: { name: string; file: string; retries: number }[] = [];

  onTestEnd(test: TestCase, result: TestResult) {
    if (result.retry > 0 && result.status === 'passed') {
      this.flakyTests.push({
        name: test.title,
        file: test.location.file,
        retries: result.retry,
      });
    }
  }

  onEnd() {
    if (this.flakyTests.length > 0) {
      console.log('\n--- FLAKY TESTS ---');
      for (const t of this.flakyTests) {
        console.log(`  ${t.file} > "${t.name}" (needed ${t.retries} retries)`);
      }
      console.log(`Total flaky: ${this.flakyTests.length}`);
    }
  }
}

export default FlakyReporter;
```

```typescript
// playwright.config.ts — register custom flaky reporter
import { defineConfig } from '@playwright/test';

export default defineConfig({
  retries: process.env.CI ? 2 : 0,
  reporter: [
    ['html'],
    ['./flaky-reporter.ts'],
  ],
});
```

**JavaScript**
```javascript
// flaky-reporter.js
class FlakyReporter {
  constructor() {
    this.flakyTests = [];
  }

  onTestEnd(test, result) {
    if (result.retry > 0 && result.status === 'passed') {
      this.flakyTests.push({
        name: test.title,
        file: test.location.file,
        retries: result.retry,
      });
    }
  }

  onEnd() {
    if (this.flakyTests.length > 0) {
      console.log('\n--- FLAKY TESTS ---');
      for (const t of this.flakyTests) {
        console.log(`  ${t.file} > "${t.name}" (needed ${t.retries} retries)`);
      }
      console.log(`Total flaky: ${this.flakyTests.length}`);
    }
  }
}

module.exports = FlakyReporter;
```

### Quarantine Strategy

**Use when**: A test is known-flaky and you cannot fix it immediately. Quarantine it so it does not block CI, but track it so it does not rot.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// ---- Option 1: test.fixme() — skips the test with a reason ----
test.fixme('checkout with promo code applies discount', async ({ page }) => {
  // TODO(JIRA-1234): Flaky due to race condition in promo service
  // Fails ~10% of runs. Root cause: /api/promo responds after rendering
  await page.goto('/checkout');
  await page.getByLabel('Promo code').fill('SAVE20');
  await page.getByRole('button', { name: 'Apply' }).click();
  await expect(page.getByTestId('discount')).toHaveText('-$20.00');
});

// ---- Option 2: test.fail() — inverts: test passes only if it fails ----
// Use this when you KNOW the test fails and want CI to alert you when it starts passing
test.fail('known broken: export to PDF', async ({ page }) => {
  // When this test starts passing, the .fail() annotation will make it fail,
  // reminding you to remove the annotation
  await page.goto('/reports');
  await page.getByRole('button', { name: 'Export PDF' }).click();
  await expect(page.getByText('PDF ready')).toBeVisible({ timeout: 10_000 });
});

// ---- Option 3: Skip by tag — quarantine with a grep filter ----
test('@flaky checkout race condition', async ({ page }) => {
  // In CI, exclude flaky-tagged tests: npx playwright test --grep-invert @flaky
  // Run ONLY flaky tests nightly: npx playwright test --grep @flaky --retries=5
  await page.goto('/checkout');
  await page.getByRole('button', { name: 'Place Order' }).click();
  await expect(page.getByText('Order confirmed')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

// Option 1: test.fixme() — skips the test with a reason
test.fixme('checkout with promo code applies discount', async ({ page }) => {
  // TODO(JIRA-1234): Flaky due to race condition in promo service
  await page.goto('/checkout');
  await page.getByLabel('Promo code').fill('SAVE20');
  await page.getByRole('button', { name: 'Apply' }).click();
  await expect(page.getByTestId('discount')).toHaveText('-$20.00');
});

// Option 2: test.fail() — inverts: test passes only if it fails
test.fail('known broken: export to PDF', async ({ page }) => {
  await page.goto('/reports');
  await page.getByRole('button', { name: 'Export PDF' }).click();
  await expect(page.getByText('PDF ready')).toBeVisible({ timeout: 10_000 });
});

// Option 3: Skip by tag
test('@flaky checkout race condition', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByRole('button', { name: 'Place Order' }).click();
  await expect(page.getByText('Order confirmed')).toBeVisible();
});
```

**CI configuration for quarantine:**

```yaml
# .github/workflows/tests.yml
jobs:
  e2e-tests:
    steps:
      - name: Run stable tests
        run: npx playwright test --grep-invert @flaky

  flaky-monitoring:
    # Runs nightly, not on every PR
    schedule:
      - cron: '0 3 * * *'
    steps:
      - name: Run flaky tests with retries
        run: npx playwright test --grep @flaky --retries=5 --reporter=json
      - name: Report flaky test results
        run: node scripts/report-flaky-metrics.js
```

### Prevention Checklist

Apply these rules from the start to prevent flakiness from entering your test suite.

**TypeScript**
```typescript
// playwright.config.ts — flake-resistant configuration
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // RULE 1: Run tests fully parallel to expose isolation issues early
  fullyParallel: true,

  // RULE 2: Fail CI if test.only() is left in code
  forbidOnly: !!process.env.CI,

  // RULE 3: Use retries in CI to surface (not hide) flaky tests
  retries: process.env.CI ? 2 : 0,

  // RULE 4: Reasonable timeouts — not too high, not too low
  timeout: 30_000,
  expect: { timeout: 5_000 },

  use: {
    // RULE 5: Always capture traces on retry for debugging
    trace: 'on-first-retry',

    // RULE 6: Use baseURL — never hardcode full URLs in tests
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    // RULE 7: Disable animations for deterministic behavior
    contextOptions: {
      reducedMotion: 'reduce',
    },

    // RULE 8: Explicit viewport — same locally and in CI
    viewport: { width: 1280, height: 720 },
  },

  // RULE 9: Start the app automatically in CI
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

```typescript
// tests/example-stable-test.spec.ts — applying all rules in a test
import { test, expect } from '@playwright/test';

test.describe('user profile', () => {
  test('updates display name', async ({ page }) => {
    // RULE 10: Unique data per test
    const newName = `User-${Date.now()}`;

    // RULE 11: Use baseURL — relative paths only
    await page.goto('/profile');

    // RULE 12: Role-based locators — resilient to implementation changes
    await page.getByRole('textbox', { name: 'Display name' }).fill(newName);
    await page.getByRole('button', { name: 'Save' }).click();

    // RULE 13: Auto-retrying assertions — never manual waits
    await expect(page.getByRole('alert')).toHaveText('Profile updated');

    // RULE 14: Assert on the result, not intermediate states
    await expect(page.getByRole('textbox', { name: 'Display name' })).toHaveValue(newName);
  });
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  timeout: 30_000,
  expect: { timeout: 5_000 },
  use: {
    trace: 'on-first-retry',
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    contextOptions: {
      reducedMotion: 'reduce',
    },
    viewport: { width: 1280, height: 720 },
  },
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

```javascript
// tests/example-stable-test.spec.js
const { test, expect } = require('@playwright/test');

test.describe('user profile', () => {
  test('updates display name', async ({ page }) => {
    const newName = `User-${Date.now()}`;

    await page.goto('/profile');
    await page.getByRole('textbox', { name: 'Display name' }).fill(newName);
    await page.getByRole('button', { name: 'Save' }).click();

    await expect(page.getByRole('alert')).toHaveText('Profile updated');
    await expect(page.getByRole('textbox', { name: 'Display name' })).toHaveValue(newName);
  });
});
```

## Decision Guide

```
My test is flaky. What do I do?
|
+-- Step 1: Reproduce locally
|   |
|   +-- npx playwright test <file> --repeat-each=20
|   +-- Fails? --> TIMING issue. Fix with auto-retrying assertions.
|   +-- Does not fail? --> Continue to Step 2.
|
+-- Step 2: Isolate from other tests
|   |
|   +-- npx playwright test --grep "exact test name" --workers=1
|   +-- Passes alone? --> ISOLATION issue. Fix with unique data + fixtures.
|   +-- Fails alone? --> Continue to Step 3.
|
+-- Step 3: Compare environments
|   |
|   +-- Download CI trace, compare with local trace
|   +-- Different? --> ENVIRONMENT issue. Fix with explicit viewport,
|   |                  reducedMotion, webServer config, stub externals.
|   +-- Same? --> Continue to Step 4.
|
+-- Step 4: Check infrastructure
|   |
|   +-- Error mentions browser crash, OOM, DNS, ECONNREFUSED?
|   +-- YES --> INFRASTRUCTURE issue. Fix with Docker, retry config,
|   |           health checks before test run.
|   +-- NO --> Re-examine. Enable trace: 'on' and retries to collect
|              more data. Compare passing and failing traces side by side.
```

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Increase timeout to 120s to "fix" flakiness | Masks the real issue. Tests become unbearably slow when they fail. Slows the entire CI pipeline. | Diagnose the root cause. Fix the race condition, not the timeout. |
| Use `page.waitForTimeout(N)` | Arbitrary delays are too slow on fast machines and too fast on slow ones. The #1 cause of flakiness. | Use `expect(locator).toBeVisible()`, `page.waitForResponse()`, or `expect.poll()`. |
| Ignore flaky tests ("it works if you run it again") | Flaky tests erode trust in the entire suite. People stop reading failures. Real bugs slip through. | Diagnose immediately. If you cannot fix now, quarantine with `test.fixme()` and a tracking ticket. |
| Add `--retries=3` and call it fixed | Retries do not fix flakiness, they hide it. A test that needs retries is a test with a bug. | Use retries to **detect** flakiness (check the retry count in reports), not to paper over it. |
| Use `test.describe.serial()` to fix ordering-dependent tests | Serial mode forces all tests in the block to run sequentially. It hides isolation bugs and slows the suite. | Fix the isolation issue. Each test should pass regardless of execution order. |
| Mock everything to prevent environment differences | Over-mocking removes confidence that the real system works. Tests pass but the app is broken. | Mock only external/third-party services. Test your own API for real. |
| Run `--repeat-each=100` in CI on every commit | Multiplies CI time by 100x. Wastes resources. | Run burn-in locally or in a nightly job, not on every PR. |

## Troubleshooting

| Symptom | Category | Fix |
|---|---|---|
| Test fails with "Timeout 5000ms" intermittently | Timing | Increase `expect.timeout` to 10s, or add `page.waitForResponse()` before the assertion |
| Test passes alone, fails in full suite run | Isolation | Check for module-level `let` variables, shared database rows, or localStorage leaks |
| Test passes locally, fails in CI | Environment | Compare traces. Check viewport, fonts, `reducedMotion`, and external service availability |
| Test fails with "Target closed" or "Browser closed" | Infrastructure | Check CI memory limits. Add `--workers=50%` to reduce parallel load. Add health check in `beforeAll` |
| Test fails differently every time | Timing + Isolation | Enable `trace: 'on'` and compare multiple failing traces. The inconsistency itself is a clue |
| Flaky test passes 99/100 times | Timing (rare race) | Use `--repeat-each=200` locally. Add `page.waitForResponse()` or `expect.poll()` for the specific race |
| Visual comparison test is flaky | Environment | Use `maxDiffPixelRatio` threshold. Set explicit fonts with `@font-face`. Use Docker for consistent rendering |
| Tests flake only on WebKit | Environment | WebKit has different timing behavior. Add WebKit-specific assertions or increase timeouts per project |

## Related

- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- auto-retrying assertions and explicit waits
- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) -- fixture teardown for test isolation
- [core/test-data-management.md](test-data-management.md) -- unique data per test, factory functions
- [core/configuration.md](configuration.md) -- retry, timeout, and trace configuration
- [core/debugging.md](debugging.md) -- trace viewer, UI mode, and Inspector for diagnosing failures
- [core/common-pitfalls.md](common-pitfalls.md) -- common mistakes that cause flakiness
