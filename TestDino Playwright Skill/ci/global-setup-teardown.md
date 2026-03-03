# Global Setup and Teardown

> **When to use**: One-time operations that must run before or after the entire test suite -- database seeding, environment health checks, creating shared auth state, starting external services. Runs once per `npx playwright test` invocation, not once per test or per worker.

## Quick Reference

```
globalSetup         →  runs ONCE before all tests in all projects
  ↓
setup projects      →  runs before dependent projects (has browser context)
  ↓
test projects       →  your actual tests
  ↓
teardown projects   →  runs after dependent projects (has browser context)
  ↓
globalTeardown      →  runs ONCE after all tests in all projects
```

**Key distinction:**
- `globalSetup` / `globalTeardown`: No browser, no Playwright fixtures. Pure Node.js.
- Setup projects with `dependencies`: Has full browser context, can use `page`, `request`, etc.

## Patterns

### Pattern 1: Basic Global Setup and Teardown

**Use when**: One-time non-browser work like database seeding, environment validation, or external service preparation.
**Avoid when**: You need a browser (use a setup project instead) or per-test isolation (use fixtures).

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  globalSetup: './tests/global-setup.ts',
  globalTeardown: './tests/global-teardown.ts',
  testDir: './tests',
});
```

```ts
// tests/global-setup.ts
import type { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('Global setup: seeding database...');

  // Seed the test database
  const { execSync } = await import('child_process');
  execSync('npx prisma db push --force-reset', { stdio: 'inherit' });
  execSync('npx prisma db seed', { stdio: 'inherit' });

  // Store run metadata for tests to use
  process.env.TEST_RUN_ID = `run-${Date.now()}`;
}

export default globalSetup;
```

```ts
// tests/global-teardown.ts
import type { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('Global teardown: cleaning up...');

  const { execSync } = await import('child_process');
  execSync('npx prisma db push --force-reset', { stdio: 'inherit' });
}

export default globalTeardown;
```

### Pattern 2: Environment Health Check in Global Setup

**Use when**: Verifying the test environment is healthy before running any tests. Fails fast if services are down.
**Avoid when**: Tests use `webServer` which already does a health check.

```ts
// tests/global-setup.ts
import type { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const baseURL = config.projects[0]?.use?.baseURL || 'http://localhost:3000';
  const maxRetries = 10;
  const retryDelay = 2000;

  console.log(`Checking if ${baseURL} is reachable...`);

  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(`${baseURL}/api/health`);
      if (response.ok) {
        console.log(`Environment is healthy (attempt ${i + 1})`);
        return;
      }
    } catch {
      // Connection refused or timeout -- retry
    }
    console.log(`Waiting for environment... (attempt ${i + 1}/${maxRetries})`);
    await new Promise((resolve) => setTimeout(resolve, retryDelay));
  }

  throw new Error(`Environment at ${baseURL} is not reachable after ${maxRetries} attempts`);
}

export default globalSetup;
```

### Pattern 3: Authentication State in Global Setup (Without Browser)

**Use when**: Creating auth tokens or session cookies via API, without needing a browser.
**Avoid when**: Login requires browser interaction (use a setup project instead).

```ts
// tests/global-setup.ts
import type { FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function globalSetup(config: FullConfig) {
  const baseURL = config.projects[0]?.use?.baseURL || 'http://localhost:3000';

  // Authenticate via API (no browser needed)
  const response = await fetch(`${baseURL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'admin@example.com',
      password: process.env.TEST_PASSWORD,
    }),
  });

  if (!response.ok) {
    throw new Error(`Authentication failed: ${response.status} ${response.statusText}`);
  }

  const { token } = await response.json();

  // Save the token as storageState for browser tests to pick up
  const authDir = path.resolve(process.cwd(), 'playwright/.auth');
  fs.mkdirSync(authDir, { recursive: true });

  const storageState = {
    cookies: [],
    origins: [
      {
        origin: baseURL,
        localStorage: [
          { name: 'auth_token', value: token },
        ],
      },
    ],
  };

  fs.writeFileSync(
    path.join(authDir, 'user.json'),
    JSON.stringify(storageState, null, 2)
  );
}

export default globalSetup;
```

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  globalSetup: './tests/global-setup.ts',
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.auth/user.json',
      },
    },
  ],
});
```

### Pattern 4: Passing Data from Global Setup to Tests

**Use when**: Global setup generates values (IDs, tokens, URLs) that tests need.
**Avoid when**: Each test should create its own data (the usual case).

**Method 1: Environment variables (simplest):**

```ts
// tests/global-setup.ts
import type { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  process.env.TEST_RUN_ID = `run-${Date.now()}`;
  process.env.SEED_USER_ID = 'user-12345';
}

export default globalSetup;
```

```ts
// tests/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test('dashboard shows seeded data', async ({ page }) => {
  const userId = process.env.SEED_USER_ID;
  await page.goto(`/users/${userId}/dashboard`);
  await expect(page.getByRole('heading')).toBeVisible();
});
```

**Method 2: Shared file (for complex data):**

```ts
// tests/global-setup.ts
import type { FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const SETUP_DATA_PATH = path.resolve(process.cwd(), 'test-data/setup-data.json');

async function globalSetup(config: FullConfig) {
  const baseURL = config.projects[0]?.use?.baseURL || 'http://localhost:3000';

  // Create test data via API
  const res = await fetch(`${baseURL}/api/test/seed`, { method: 'POST' });
  const seedData = await res.json();

  // Write to shared file
  const dir = path.dirname(SETUP_DATA_PATH);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(SETUP_DATA_PATH, JSON.stringify(seedData, null, 2));
}

export default globalSetup;
```

```ts
// tests/helpers/setup-data.ts
import * as fs from 'fs';
import * as path from 'path';

const SETUP_DATA_PATH = path.resolve(process.cwd(), 'test-data/setup-data.json');

export function getSetupData(): { userId: string; orgId: string; apiKey: string } {
  const raw = fs.readFileSync(SETUP_DATA_PATH, 'utf8');
  return JSON.parse(raw);
}
```

```ts
// tests/org-settings.spec.ts
import { test, expect } from '@playwright/test';
import { getSetupData } from './helpers/setup-data';

test('org settings page loads', async ({ page }) => {
  const { orgId } = getSetupData();
  await page.goto(`/orgs/${orgId}/settings`);
  await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
});
```

### Pattern 5: Global Setup with `storageState` (Browser-Based Auth)

**Use when**: Authentication requires browser interaction (form login, OAuth redirect, MFA).
**Avoid when**: Auth can be done via API call (use Pattern 3 instead).

**Important**: `globalSetup` has no browser. For browser-based auth, use a **setup project** instead.

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    // Setup project: runs first, has a browser, saves auth state
    {
      name: 'setup',
      testMatch: /global\.setup\.ts/,
    },

    // Test projects: depend on setup, reuse saved auth state
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

  // Wait for navigation to confirm login succeeded
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  // Save signed-in state (cookies + localStorage)
  await page.context().storageState({ path: authFile });
});
```

### Pattern 6: Global Setup for External Services

**Use when**: Starting or configuring external services (mock servers, test containers, feature flags) before any tests run.
**Avoid when**: Per-test or per-worker isolation is needed (use fixtures).

```ts
// tests/global-setup.ts
import type { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  // Start a mock API server
  const { createServer } = await import('../mocks/server');
  const server = await createServer();
  const port = await server.listen(0);
  process.env.MOCK_API_URL = `http://localhost:${port}`;

  // Configure feature flags for test environment
  const baseURL = config.projects[0]?.use?.baseURL || 'http://localhost:3000';
  await fetch(`${baseURL}/api/admin/feature-flags`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.ADMIN_API_KEY}`,
    },
    body: JSON.stringify({
      newCheckout: true,
      darkMode: false,
      betaFeatures: true,
    }),
  });

  // Return a cleanup function (Playwright calls globalTeardown separately)
  // For cleanup, use globalTeardown
}

export default globalSetup;
```

```ts
// tests/global-teardown.ts
import type { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  // Reset feature flags
  const baseURL = config.projects[0]?.use?.baseURL || 'http://localhost:3000';
  await fetch(`${baseURL}/api/admin/feature-flags/reset`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.ADMIN_API_KEY}` },
  });
}

export default globalTeardown;
```

## Decision Guide

| Need | Use | Why |
|---|---|---|
| One-time DB seed | `globalSetup` | No browser needed; runs once before everything |
| Browser-based login (shared state) | Setup project with `dependencies` | Needs `page` and `context` (not available in globalSetup) |
| API-based auth token | `globalSetup` | Simple HTTP call, no browser needed |
| Per-test unique data | Custom fixture via `test.extend()` | Each test gets isolated data |
| Per-worker shared resource | Worker-scoped fixture (`{ scope: 'worker' }`) | Shared within worker, isolated between workers |
| Health check before tests | `globalSetup` | Fail fast if environment is down |
| Start mock server | `globalSetup` + `globalTeardown` | One-time server lifecycle |
| Clean up after all tests | `globalTeardown` | Runs once at the end regardless of pass/fail |

```
Do I need globalSetup?
│
├── Does the work need a browser (page, context)?
│   ├── YES → Use a setup project, not globalSetup
│   └── NO  → globalSetup is appropriate
│
├── Does every test need unique/isolated data?
│   ├── YES → Use a fixture with test.extend()
│   └── NO  → globalSetup for shared, read-only data
│
├── Is it per-worker (expensive resource, connection pool)?
│   ├── YES → Worker-scoped fixture
│   └── NO  → globalSetup for truly global, one-time work
│
└── Is it cleanup?
    ├── After all tests → globalTeardown
    ├── After each test → Fixture teardown (after use())
    └── After each worker → Worker-scoped fixture teardown
```

## Anti-Patterns

| Anti-Pattern | Problem | Do This Instead |
|---|---|---|
| Browser login in `globalSetup` | No browser context available; complex workarounds | Use a setup project with `dependencies` |
| Creating per-test data in `globalSetup` | All tests share the same data; not isolated | Use per-test fixtures for unique data |
| `globalSetup` without `globalTeardown` | Database or services left in dirty state | Always pair setup with teardown |
| Storing setup results in module-level variables | Workers are separate processes; variables don't share | Use environment variables or files |
| Complex logic in `globalSetup` | Hard to debug; runs outside normal test lifecycle | Keep it minimal: seed, verify, set env vars |
| `globalSetup` that takes > 60 seconds | Slows every test run, even for a single test | Move heavy work to a separate script or CI step |
| Relying on `globalTeardown` for critical cleanup | If the process crashes, `globalTeardown` might not run | Design tests to be idempotent; use `beforeAll` in setup project |

## Troubleshooting

### Global setup runs but environment variables are not available in tests

**Cause**: Each worker is a separate process. `process.env` mutations in `globalSetup` propagate to workers, but only if set before workers spawn.

**Fix**: Set environment variables at the top level of `globalSetup`, before any async work that might delay:

```ts
// tests/global-setup.ts
async function globalSetup() {
  // This works -- set before returning
  process.env.TEST_RUN_ID = `run-${Date.now()}`;
}
export default globalSetup;
```

If environment variables are still missing, write data to a file instead (Pattern 4, Method 2).

### Global setup fails with "Cannot find module"

**Cause**: The path in `globalSetup` is relative to the config file, but the module resolution is wrong.

**Fix**: Use a path relative to the project root:

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  globalSetup: './tests/global-setup.ts',   // relative to config location
  globalTeardown: './tests/global-teardown.ts',
});
```

### Global teardown doesn't run after test failure

**Cause**: If the process is killed (SIGKILL, OOM) rather than exiting normally, teardown is skipped.

**Fix**: Design your setup to be idempotent. Global setup should handle a dirty state from a previous incomplete run:

```ts
// tests/global-setup.ts
async function globalSetup() {
  // Always reset first, then seed -- handles dirty state
  const { execSync } = await import('child_process');
  execSync('npx prisma db push --force-reset', { stdio: 'inherit' });
  execSync('npx prisma db seed', { stdio: 'inherit' });
}
export default globalSetup;
```

### Setup project runs every time, even when only running one test file

**Cause**: The `dependencies` configuration requires the setup project to run before any dependent project.

**Fix**: This is expected behavior. To skip setup during focused debugging:

```bash
# Skip setup by running without dependencies
npx playwright test --project=chromium --no-deps tests/specific-test.spec.ts
```

### `storageState` file doesn't exist when tests start

**Cause**: The setup project or `globalSetup` that creates the file failed silently, or the path is wrong.

**Fix**: Add explicit error handling and verify the file exists:

```ts
// tests/global.setup.ts
import { test as setup, expect } from '@playwright/test';
import * as fs from 'fs';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill(process.env.TEST_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await page.context().storageState({ path: authFile });

  // Verify the file was created
  if (!fs.existsSync(authFile)) {
    throw new Error(`Auth state file was not created at ${authFile}`);
  }
});
```

## Related

- [core/fixtures-and-hooks.md](../core/fixtures-and-hooks.md) -- per-test and per-worker fixtures (preferred over globalSetup for most cases)
- [core/configuration.md](../core/configuration.md) -- `globalSetup`, `globalTeardown`, `webServer` config
- [ci/projects-and-dependencies.md](projects-and-dependencies.md) -- setup projects with `dependencies`
- [core/authentication.md](../core/authentication.md) -- authentication patterns using setup projects
- [core/test-data-management.md](../core/test-data-management.md) -- seeding and managing test data
