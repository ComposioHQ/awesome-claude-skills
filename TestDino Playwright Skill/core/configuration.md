# Configuration

> **When to use**: Setting up a new Playwright project, adjusting timeouts, adding browser targets, configuring CI behavior, or connecting environment-specific settings.

## Quick Reference

```
npx playwright init                    # scaffold config + first test
npx playwright test --config=custom.config.ts  # use non-default config
npx playwright test --project=chromium # run single project
npx playwright test --reporter=html    # override reporter
npx playwright show-report             # open last HTML report
DEBUG=pw:api npx playwright test       # verbose Playwright logging
```

## Production-Ready Config (Copy-Paste Starter)

### TypeScript

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from .env file
dotenv.config({ path: path.resolve(__dirname, '.env') });

export default defineConfig({
  // ── Test discovery ──────────────────────────────────────────────
  testDir: './tests',
  testMatch: '**/*.spec.ts',

  // ── Execution ───────────────────────────────────────────────────
  fullyParallel: true,
  forbidOnly: !!process.env.CI,       // fail CI if test.only left in
  retries: process.env.CI ? 2 : 0,    // retry flakes in CI only
  workers: process.env.CI ? '50%' : undefined, // half CPU in CI, auto locally

  // ── Reporting ───────────────────────────────────────────────────
  reporter: process.env.CI
    ? [['html', { open: 'never' }], ['github']]
    : [['html', { open: 'on-failure' }]],

  // ── Timeouts ────────────────────────────────────────────────────
  timeout: 30_000,                     // per-test timeout
  expect: {
    timeout: 5_000,                    // per-assertion retry timeout
  },

  // ── Shared browser context options ──────────────────────────────
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    actionTimeout: 10_000,             // click, fill, etc.
    navigationTimeout: 15_000,         // goto, waitForURL, etc.

    // Artifact collection
    trace: 'on-first-retry',          // full trace on first retry only
    screenshot: 'only-on-failure',     // screenshot on failure
    video: 'retain-on-failure',        // video only kept for failures

    // Sensible defaults
    locale: 'en-US',
    timezoneId: 'America/New_York',
    extraHTTPHeaders: {
      'x-test-automation': 'playwright',
    },
  },

  // ── Projects (browser targets) ─────────────────────────────────
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 7'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 14'] },
    },
  ],

  // ── Dev server ──────────────────────────────────────────────────
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,                  // 2 min for cold builds
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
```

### JavaScript

```js
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(__dirname, '.env') });

module.exports = defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',

  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? '50%' : undefined,

  reporter: process.env.CI
    ? [['html', { open: 'never' }], ['github']]
    : [['html', { open: 'on-failure' }]],

  timeout: 30_000,
  expect: {
    timeout: 5_000,
  },

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    actionTimeout: 10_000,
    navigationTimeout: 15_000,

    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',

    locale: 'en-US',
    timezoneId: 'America/New_York',
    extraHTTPHeaders: {
      'x-test-automation': 'playwright',
    },
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 7'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 14'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
```

## Patterns

### Pattern 1: Environment-Specific Configuration

**Use when**: Tests run against dev, staging, and production environments.
**Avoid when**: Single-environment local-only projects.

#### TypeScript

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';
import dotenv from 'dotenv';
import path from 'path';

// Load environment-specific .env file: .env.staging, .env.production, etc.
const ENV = process.env.TEST_ENV || 'local';
dotenv.config({ path: path.resolve(__dirname, `.env.${ENV}`) });

const envConfig: Record<string, { baseURL: string; retries: number }> = {
  local:      { baseURL: 'http://localhost:3000',       retries: 0 },
  staging:    { baseURL: 'https://staging.example.com', retries: 2 },
  production: { baseURL: 'https://www.example.com',     retries: 2 },
};

const env = envConfig[ENV];

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  retries: env.retries,
  use: {
    baseURL: env.baseURL,
  },
});
```

```bash
# Run against staging
TEST_ENV=staging npx playwright test

# Run against production (subset of smoke tests)
TEST_ENV=production npx playwright test --grep @smoke
```

#### JavaScript

```js
// playwright.config.js
const { defineConfig } = require('@playwright/test');
const dotenv = require('dotenv');
const path = require('path');

const ENV = process.env.TEST_ENV || 'local';
dotenv.config({ path: path.resolve(__dirname, `.env.${ENV}`) });

const envConfig = {
  local:      { baseURL: 'http://localhost:3000',       retries: 0 },
  staging:    { baseURL: 'https://staging.example.com', retries: 2 },
  production: { baseURL: 'https://www.example.com',     retries: 2 },
};

const env = envConfig[ENV];

module.exports = defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',
  retries: env.retries,
  use: {
    baseURL: env.baseURL,
  },
});
```

### Pattern 2: Multi-Project with Setup Dependencies

**Use when**: Tests need shared authentication state or database seeding before running.
**Avoid when**: Tests are fully independent with no shared setup phase.

#### TypeScript

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',

  projects: [
    // Setup project runs first, saves auth state
    {
      name: 'setup',
      testMatch: /global\.setup\.ts/,
    },

    // Browser projects depend on setup
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

```ts
// tests/global.setup.ts
import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill(process.env.TEST_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await page.context().storageState({ path: authFile });
});
```

#### JavaScript

```js
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',

  projects: [
    {
      name: 'setup',
      testMatch: /global\.setup\.js/,
    },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

```js
// tests/global.setup.js
const { test: setup, expect } = require('@playwright/test');

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill(process.env.TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await page.context().storageState({ path: authFile });
});
```

### Pattern 3: `webServer` with Build Step

**Use when**: Tests need a running application server. Let Playwright manage the server lifecycle.
**Avoid when**: Testing against an already-deployed environment (staging/prod).

#### TypeScript

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  use: {
    baseURL: 'http://localhost:3000',
  },
  webServer: {
    command: process.env.CI
      ? 'npm run build && npm run start'  // production build in CI
      : 'npm run dev',                    // dev server locally
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    stdout: 'pipe',
    stderr: 'pipe',
    env: {
      NODE_ENV: 'test',
      DATABASE_URL: process.env.DATABASE_URL || 'postgresql://localhost:5432/test',
    },
  },
});
```

#### JavaScript

```js
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',
  use: {
    baseURL: 'http://localhost:3000',
  },
  webServer: {
    command: process.env.CI
      ? 'npm run build && npm run start'
      : 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    stdout: 'pipe',
    stderr: 'pipe',
    env: {
      NODE_ENV: 'test',
      DATABASE_URL: process.env.DATABASE_URL || 'postgresql://localhost:5432/test',
    },
  },
});
```

### Pattern 4: `globalSetup` / `globalTeardown`

**Use when**: One-time non-browser work: seeding a database, starting a service, setting env vars. Runs once per `npx playwright test` invocation.
**Avoid when**: You need browser context (use a setup project instead) or per-test isolation (use fixtures).

#### TypeScript

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  globalSetup: './tests/global-setup.ts',
  globalTeardown: './tests/global-teardown.ts',
});
```

```ts
// tests/global-setup.ts
import { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  // Seed test database
  const { execSync } = await import('child_process');
  execSync('npx prisma db seed', { stdio: 'inherit' });

  // Store data for tests to use via environment variables
  process.env.TEST_RUN_ID = `run-${Date.now()}`;
}

export default globalSetup;
```

```ts
// tests/global-teardown.ts
import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  const { execSync } = await import('child_process');
  execSync('npx prisma db push --force-reset', { stdio: 'inherit' });
}

export default globalTeardown;
```

#### JavaScript

```js
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',
  globalSetup: './tests/global-setup.js',
  globalTeardown: './tests/global-teardown.js',
});
```

```js
// tests/global-setup.js
const { execSync } = require('child_process');

async function globalSetup(config) {
  execSync('npx prisma db seed', { stdio: 'inherit' });
  process.env.TEST_RUN_ID = `run-${Date.now()}`;
}

module.exports = globalSetup;
```

```js
// tests/global-teardown.js
const { execSync } = require('child_process');

async function globalTeardown(config) {
  execSync('npx prisma db push --force-reset', { stdio: 'inherit' });
}

module.exports = globalTeardown;
```

### Pattern 5: `.env` File Setup

**Use when**: Managing secrets, URLs, or feature flags without hardcoding.
**Avoid when**: Never commit `.env` files with real secrets. Provide `.env.example` instead.

```bash
# .env.example (commit this)
BASE_URL=http://localhost:3000
TEST_PASSWORD=
API_KEY=

# .env.local (gitignored)
BASE_URL=http://localhost:3000
TEST_PASSWORD=s3cret
API_KEY=test-key-abc123

# .env.staging (gitignored)
BASE_URL=https://staging.example.com
TEST_PASSWORD=staging-password
API_KEY=staging-key-xyz789
```

```bash
# .gitignore
.env
.env.local
.env.staging
.env.production
playwright/.auth/
```

Install dotenv:

```bash
npm install -D dotenv
```

### Pattern 6: Trace, Screenshot, and Video Settings

**Use when**: Deciding artifact collection strategy for local development vs CI.

| Setting | Local | CI | Why |
|---|---|---|---|
| `trace` | `'off'` or `'on-first-retry'` | `'on-first-retry'` | Traces are large; only collect on failure |
| `screenshot` | `'off'` | `'only-on-failure'` | Useful for CI debugging only |
| `video` | `'off'` | `'retain-on-failure'` | Video is slow to record; keep only failures |

#### TypeScript

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  use: {
    // CI: capture everything on failure; Local: minimal overhead
    trace: process.env.CI ? 'on-first-retry' : 'off',
    screenshot: process.env.CI ? 'only-on-failure' : 'off',
    video: process.env.CI ? 'retain-on-failure' : 'off',
  },
});
```

#### JavaScript

```js
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',
  use: {
    trace: process.env.CI ? 'on-first-retry' : 'off',
    screenshot: process.env.CI ? 'only-on-failure' : 'off',
    video: process.env.CI ? 'retain-on-failure' : 'off',
  },
});
```

## Decision Guide

### Which Timeout to Adjust

| Symptom | Timeout to Change | Default | Recommended Range |
|---|---|---|---|
| Test takes too long overall | `timeout` | 30s | 30-60s (never above 120s) |
| Assertion `expect()` keeps retrying too long or not long enough | `expect.timeout` | 5s | 5-10s |
| `page.goto()` or `waitForURL()` times out | `navigationTimeout` | 30s | 10-30s |
| `click()`, `fill()`, `check()` time out | `actionTimeout` | 0 (no limit) | 10-15s |
| Dev server slow to start | `webServer.timeout` | 60s | 60-180s |

### Server Management

| Scenario | Approach | Why |
|---|---|---|
| Local dev + CI, app in same repo | `webServer` with `reuseExistingServer: !process.env.CI` | Playwright manages server; reuses yours locally |
| Separate frontend/backend repos | Manual start or Docker Compose | `webServer` can only run one command |
| Testing deployed staging/production | No `webServer`; set `baseURL` via env var | Server already running remotely |
| Multiple services needed (API + frontend) | Array of `webServer` entries | Each gets its own command and URL health check |

### Single vs Multi-Project Config

| Scenario | Approach | Why |
|---|---|---|
| Starting out, early development | Single project (chromium only) | Faster feedback, simpler config |
| Pre-release cross-browser validation | Multi-project: chromium + firefox + webkit | Catch rendering/API differences |
| Mobile-responsive app | Add mobile projects alongside desktop | Viewport + touch differences matter |
| Authenticated + unauthenticated tests | Setup project + dependent projects | Share auth state without re-login per test |
| CI pipeline with tight time budget | Chromium in PR checks; all browsers on merge to main | Balance speed vs coverage |

### globalSetup vs Setup Projects vs Fixtures

| Need | Use | Why |
|---|---|---|
| One-time DB seed or external service prep | `globalSetup` | Runs once, no browser needed |
| Shared browser auth (login once, reuse cookies) | Setup project with `dependencies` | Needs browser context; `globalSetup` has none |
| Per-test isolated state (unique user, fresh data) | Custom fixture via `test.extend()` | Each test gets its own instance with teardown |
| Cleanup after all tests | `globalTeardown` | Runs once at the end regardless of pass/fail |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `timeout: 300_000` globally | Masks flaky tests; CI runs take forever | Fix the root cause; keep timeout at 30s; raise `navigationTimeout` only if warranted |
| Hardcoded URLs in tests: `page.goto('http://localhost:3000/login')` | Breaks in every non-local environment | Use `baseURL` in config, then `page.goto('/login')` |
| Running chromium + firefox + webkit on every PR | 3x CI time for marginal benefit on most PRs | Chromium on PRs; all browsers on main branch merges |
| `trace: 'on'` always in CI | Huge artifacts, slow uploads, disk full | `trace: 'on-first-retry'` -- only captures when a test fails and retries |
| `video: 'on'` always in CI | Massive CI storage; recording slows tests | `video: 'retain-on-failure'` -- records all but only keeps failures |
| Config values inline in test files: `test.use({ viewport: { width: 1280, height: 720 } })` in every file | Scattered, hard to maintain, inconsistent | Define once in project config; override per-file only when genuinely needed |
| `retries: 3` locally | Hides flakiness during development | `retries: 0` locally, `retries: 2` in CI |
| No `forbidOnly` in CI | Accidentally committed `test.only` runs a single test, everything else silently skipped | `forbidOnly: !!process.env.CI` |
| `globalSetup` for browser auth | No browser context available; complex workarounds needed | Use a setup project with `dependencies` |
| Committing `.env` files with real credentials | Security risk | Commit `.env.example` only; gitignore real `.env` files |

## Troubleshooting

### "baseURL" not working -- tests navigate to full URL

**Cause**: Using `page.goto('http://localhost:3000/path')` instead of `page.goto('/path')`. When `goto` receives an absolute URL, it ignores `baseURL`.

**Fix**: Always pass relative paths to `page.goto()`:

```ts
// Wrong -- ignores baseURL
await page.goto('http://localhost:3000/dashboard');

// Correct -- uses baseURL from config
await page.goto('/dashboard');
```

### webServer starts but tests still fail with connection refused

**Cause**: The `url` in `webServer` does not match what the server actually serves, or the health check endpoint returns non-200.

**Fix**: Ensure `webServer.url` matches the actual server address. Add a health check route if needed:

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000/api/health',  // use a real endpoint
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

### Tests pass locally but timeout in CI

**Cause**: CI machines are slower. Default timeouts too tight for CI hardware.

**Fix**: Increase `navigationTimeout` for CI, reduce `workers` to avoid resource contention:

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  workers: process.env.CI ? '50%' : undefined,
  use: {
    navigationTimeout: process.env.CI ? 30_000 : 15_000,
    actionTimeout: process.env.CI ? 15_000 : 10_000,
  },
});
```

### "Error: page.goto: Target page, context or browser has been closed"

**Cause**: Test exceeded its `timeout` and Playwright tore down the browser while an action was still running.

**Fix**: Do not increase the global timeout. Instead, find the slow step using `--trace on` and fix it. Common causes: waiting for a slow API, unresolved network request, or missing `await`.

```bash
# Record a trace for debugging
npx playwright test --trace on
npx playwright show-report
```

## Related

- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) -- custom fixtures that replace `globalSetup` for per-test state
- [core/test-organization.md](test-organization.md) -- file structure, naming conventions, test grouping
- [core/authentication.md](authentication.md) -- setup projects for shared auth state
- [ci/ci-github-actions.md](../ci/ci-github-actions.md) -- CI-specific config and caching
- [ci/projects-and-dependencies.md](../ci/projects-and-dependencies.md) -- advanced multi-project patterns
