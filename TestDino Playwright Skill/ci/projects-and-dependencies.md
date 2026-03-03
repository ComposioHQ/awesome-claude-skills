# Projects and Dependencies

> **When to use**: Running tests across multiple browsers, devices, or environments from a single config. Projects let you define different test configurations that can depend on each other, share setup work, and run selectively.

## Quick Reference

```bash
# Run all projects
npx playwright test

# Run a specific project
npx playwright test --project=chromium
npx playwright test --project="Mobile Safari"

# Run multiple projects
npx playwright test --project=chromium --project=firefox

# List all projects and their tests
npx playwright test --list

# Skip dependencies (e.g., skip setup during debugging)
npx playwright test --project=chromium --no-deps
```

## Patterns

### Pattern 1: Multi-Browser Testing

**Use when**: Ensuring your application works across Chromium, Firefox, and WebKit.
**Avoid when**: Early development -- start with Chromium only and add browsers later.

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,

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
  ],
});
```

**Selective browser testing in CI (fast on PRs, thorough on main):**

```yaml
# .github/workflows/ci.yml
jobs:
  test-pr:
    if: github.event_name == 'pull_request'
    steps:
      # Chromium only on PRs for fast feedback
      - run: npx playwright test --project=chromium

  test-main:
    if: github.ref == 'refs/heads/main'
    steps:
      # All browsers on main branch
      - run: npx playwright test
```

### Pattern 2: Desktop and Mobile Projects

**Use when**: Testing responsive layouts, touch interactions, or mobile-specific behavior.
**Avoid when**: Your application is desktop-only.

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,

  projects: [
    // Desktop browsers
    {
      name: 'Desktop Chrome',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'Desktop Firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'Desktop Safari',
      use: { ...devices['Desktop Safari'] },
    },

    // Mobile devices
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 7'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 14'] },
    },

    // Tablet
    {
      name: 'iPad',
      use: { ...devices['iPad Pro 11'] },
    },
  ],
});
```

**Run only mobile or only desktop:**

```bash
npx playwright test --project="Mobile Chrome" --project="Mobile Safari"
npx playwright test --project="Desktop Chrome" --project="Desktop Firefox"
```

### Pattern 3: Setup Project with Dependencies

**Use when**: Tests need shared state (authentication, seeded data) that should be created once before all test projects run.
**Avoid when**: Tests are fully independent with no shared setup phase.

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',

  projects: [
    // Setup runs first -- no dependencies, so it runs immediately
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

**How dependencies work:**
1. Playwright identifies projects with no dependencies and runs them first.
2. Once a dependency project completes successfully, dependent projects start.
3. If a dependency project fails, all dependent projects are skipped.

### Pattern 4: Multiple Auth Roles

**Use when**: Tests need different user roles (admin, editor, viewer) with separate auth states.
**Avoid when**: All tests use the same user -- use a single setup project.

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',

  projects: [
    // Auth setup for each role
    {
      name: 'auth-admin',
      testMatch: /auth\.setup\.ts/,
      use: {
        userRole: 'admin',
        storageStatePath: 'playwright/.auth/admin.json',
      },
    },
    {
      name: 'auth-editor',
      testMatch: /auth\.setup\.ts/,
      use: {
        userRole: 'editor',
        storageStatePath: 'playwright/.auth/editor.json',
      },
    },

    // Admin tests
    {
      name: 'admin-tests',
      testDir: './tests/admin',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.auth/admin.json',
      },
      dependencies: ['auth-admin'],
    },

    // Editor tests
    {
      name: 'editor-tests',
      testDir: './tests/editor',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.auth/editor.json',
      },
      dependencies: ['auth-editor'],
    },

    // Unauthenticated tests (no dependencies, no storageState)
    {
      name: 'public-tests',
      testDir: './tests/public',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
```

```ts
// tests/auth.setup.ts
import { test as setup, expect } from '@playwright/test';

const credentials: Record<string, { email: string; password: string }> = {
  admin: { email: 'admin@example.com', password: process.env.ADMIN_PASSWORD! },
  editor: { email: 'editor@example.com', password: process.env.EDITOR_PASSWORD! },
};

setup('authenticate', async ({ page }, testInfo) => {
  const role = testInfo.project.use.userRole as string;
  const authFile = testInfo.project.use.storageStatePath as string;
  const { email, password } = credentials[role];

  await page.goto('/login');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await page.context().storageState({ path: authFile });
});
```

### Pattern 5: Environment-Specific Projects

**Use when**: Running the same tests against different environments (dev, staging, production) from one config.
**Avoid when**: You only test one environment.

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

const ENV = process.env.TEST_ENV || 'local';

const envConfig: Record<string, { baseURL: string; retries: number }> = {
  local:      { baseURL: 'http://localhost:3000',       retries: 0 },
  staging:    { baseURL: 'https://staging.example.com', retries: 2 },
  production: { baseURL: 'https://www.example.com',     retries: 2 },
};

const env = envConfig[ENV];

export default defineConfig({
  testDir: './tests',
  retries: env.retries,
  use: {
    baseURL: env.baseURL,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Only run smoke tests in production
    ...(ENV === 'production'
      ? [{
          name: 'smoke',
          testMatch: '**/*smoke*.spec.ts',
          use: { ...devices['Desktop Chrome'] },
          grep: /@smoke/,
        }]
      : []),
  ],
});
```

```bash
# Run against different environments
TEST_ENV=local npx playwright test
TEST_ENV=staging npx playwright test
TEST_ENV=production npx playwright test --project=smoke
```

### Pattern 6: Project with Custom `testDir` and `testMatch`

**Use when**: Different projects need different test directories or file patterns.
**Avoid when**: All projects run the same tests.

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    // E2E tests -- run in all browsers
    {
      name: 'e2e-chromium',
      testDir: './tests/e2e',
      testMatch: '**/*.spec.ts',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'e2e-firefox',
      testDir: './tests/e2e',
      testMatch: '**/*.spec.ts',
      use: { ...devices['Desktop Firefox'] },
    },

    // API tests -- no browser needed, run once
    {
      name: 'api',
      testDir: './tests/api',
      testMatch: '**/*.spec.ts',
      use: {
        baseURL: 'https://api.example.com',
      },
    },

    // Visual regression -- Chromium only
    {
      name: 'visual',
      testDir: './tests/visual',
      testMatch: '**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        // Lock viewport for consistent screenshots
        viewport: { width: 1280, height: 720 },
      },
    },
  ],
});
```

```bash
# Run only API tests
npx playwright test --project=api

# Run only visual tests
npx playwright test --project=visual

# Run all E2E tests
npx playwright test --project=e2e-chromium --project=e2e-firefox
```

### Pattern 7: Teardown Projects

**Use when**: You need browser-based cleanup after tests complete (e.g., deleting test data via the UI).
**Avoid when**: Cleanup can be done via API in `globalTeardown` or fixtures (the usual case).

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'setup',
      testMatch: /global\.setup\.ts/,
      teardown: 'teardown',  // link to teardown project
    },
    {
      name: 'teardown',
      testMatch: /global\.teardown\.ts/,
    },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

```ts
// tests/global.teardown.ts
import { test as teardown } from '@playwright/test';

teardown('clean up test data', async ({ request }) => {
  await request.post('/api/test/cleanup', {
    headers: { Authorization: `Bearer ${process.env.ADMIN_API_KEY}` },
  });
});
```

**Execution order:**
1. `setup` project runs
2. `chromium` project runs (depends on setup)
3. `teardown` project runs (linked via setup's `teardown` field)

### Pattern 8: Grep and GrepInvert for Project Filtering

**Use when**: Different projects should run different subsets of tests based on tags.
**Avoid when**: All projects run all tests.

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',

  projects: [
    // Smoke tests -- only @smoke tagged tests, Chromium only
    {
      name: 'smoke',
      use: { ...devices['Desktop Chrome'] },
      grep: /@smoke/,
    },

    // Full regression -- everything except @slow, all browsers
    {
      name: 'regression-chromium',
      use: { ...devices['Desktop Chrome'] },
      grepInvert: /@slow/,
    },
    {
      name: 'regression-firefox',
      use: { ...devices['Desktop Firefox'] },
      grepInvert: /@slow/,
    },

    // Slow tests -- only @slow, Chromium only, higher timeout
    {
      name: 'slow',
      use: { ...devices['Desktop Chrome'] },
      grep: /@slow/,
      timeout: 120_000,
    },
  ],
});
```

```bash
# CI: run smoke on PRs
npx playwright test --project=smoke

# CI: run full regression on main
npx playwright test --project=regression-chromium --project=regression-firefox

# CI: run slow tests nightly
npx playwright test --project=slow
```

## Decision Guide

| Scenario | Number of Projects | Configuration |
|---|---|---|
| Getting started | 1 (chromium) | Single project, no dependencies |
| Cross-browser testing | 3 (chromium, firefox, webkit) | One per browser engine |
| Responsive design | 5-6 (desktop + mobile + tablet) | Use `devices` presets |
| Authenticated tests | 1 setup + N browser projects | Setup with `dependencies` |
| Multiple auth roles | N setup + N test projects | One setup project per role |
| Different test types (E2E, API, visual) | One per type | Custom `testDir` per project |
| Environment targeting | Same projects, different `baseURL` | Use `TEST_ENV` env var |
| Smoke vs regression suites | Projects with `grep` / `grepInvert` | Tag-based filtering |

| Feature | `dependencies` | `teardown` | `globalSetup` |
|---|---|---|---|
| Has browser context | Yes | Yes | No |
| Runs when | Before dependent projects | After linked setup project's dependents | Before all projects |
| Use for | Auth state, data seeding with browser | Browser-based cleanup | Non-browser setup (DB, health check) |
| Skips dependents on failure | Yes | N/A | Yes (entire suite fails) |

## Anti-Patterns

| Anti-Pattern | Problem | Do This Instead |
|---|---|---|
| All browsers on every PR | 3x CI time for marginal benefit | Chromium on PRs; all browsers on main |
| `dependencies` on projects that don't need shared state | Forced serial execution; slower | Only use dependencies when projects truly need shared state |
| Duplicating config across projects | Hard to maintain; settings drift | Use shared `use` at the top level; override per project |
| No `--project` filtering in CI | All projects always run; no control | Use `--project` to run subsets based on context |
| Setup project modifies database without teardown | Dirty state for next run | Always pair setup with teardown or make setup idempotent |
| Many projects with overlapping test directories | Same test runs multiple times unintentionally | Set explicit `testDir` and `testMatch` per project |
| Not using `--no-deps` for debugging | Setup runs every time, even for one test | Use `--no-deps` to skip dependencies during focused debugging |

## Troubleshooting

### "No tests found" when running specific project

**Cause**: The project's `testDir` or `testMatch` doesn't match any files.

**Fix**: List tests for the project to see what matches:

```bash
npx playwright test --project=chromium --list
```

Check that `testDir` and `testMatch` are correct:

```ts
{
  name: 'chromium',
  testDir: './tests',         // must contain test files
  testMatch: '**/*.spec.ts',  // must match your file naming
}
```

### Setup project runs every time, even for a single test

**Cause**: The test's project has `dependencies: ['setup']`, so setup always runs first.

**Fix**: Use `--no-deps` to skip dependencies during development:

```bash
npx playwright test --project=chromium --no-deps tests/specific-test.spec.ts
```

### `storageState` file not found

**Cause**: Setup project failed or didn't create the file. Or the path in `use.storageState` doesn't match the path in the setup project.

**Fix**: Verify paths match exactly:

```ts
// In setup test:
await page.context().storageState({ path: 'playwright/.auth/user.json' });

// In project config:
use: { storageState: 'playwright/.auth/user.json' }  // must match exactly
```

Add `.auth` to `.gitignore`:

```bash
echo "playwright/.auth/" >> .gitignore
```

### Dependent projects run even when setup fails

**Cause**: This should not happen -- Playwright skips dependent projects when a dependency fails. If it seems like they run, check that `dependencies` is spelled correctly.

**Fix**: Verify the dependency name matches exactly:

```ts
// Setup project name
{ name: 'setup', ... }

// Dependency reference (must match exactly, case-sensitive)
{ dependencies: ['setup'] }  // correct
{ dependencies: ['Setup'] }  // WRONG -- case mismatch
```

### Tests from multiple projects interfere with each other

**Cause**: Projects share a database or external state. Since projects run in parallel by default, they can collide.

**Fix**: Either:
1. Use per-project isolated data (different test users, different database schemas)
2. Run projects sequentially by adding artificial dependencies:

```ts
projects: [
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  {
    name: 'firefox',
    use: { ...devices['Desktop Firefox'] },
    dependencies: ['chromium'],  // forces serial execution
  },
],
```

### Custom `use` properties cause TypeScript errors

**Cause**: Playwright's `use` type doesn't include your custom properties.

**Fix**: Extend the type or use `as any`:

```ts
// Option 1: Declare custom properties
declare module '@playwright/test' {
  interface PlaywrightTestOptions {
    userRole: string;
    storageStatePath: string;
  }
}

// Option 2: Quick fix (less type-safe)
{
  name: 'auth-admin',
  use: {
    userRole: 'admin',
    storageStatePath: 'playwright/.auth/admin.json',
  } as any,
}
```

## Related

- [core/configuration.md](../core/configuration.md) -- base config, `projects`, `use` settings
- [ci/global-setup-teardown.md](global-setup-teardown.md) -- `globalSetup` vs setup projects
- [core/fixtures-and-hooks.md](../core/fixtures-and-hooks.md) -- option fixtures configured per project
- [core/authentication.md](../core/authentication.md) -- auth state via setup projects
- [ci/parallel-and-sharding.md](parallel-and-sharding.md) -- sharding across projects
- [ci/ci-github-actions.md](ci-github-actions.md) -- running specific projects in CI
