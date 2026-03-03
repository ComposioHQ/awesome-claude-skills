# Fixtures and Hooks

> **When to use**: Whenever tests need shared setup, teardown, reusable resources, or configurable context. Fixtures are Playwright's killer feature — prefer them over hooks in every situation where both could work.

## Quick Reference

| Mechanism | Scope | Cleanup guaranteed? | Parallelism-safe? | Use for |
|---|---|---|---|---|
| `test.extend()` fixture | per-test | Yes (via `use()` callback) | Yes | Most setup/teardown needs |
| Worker-scoped fixture | per-worker | Yes | Yes (isolated per worker) | Expensive resources: DB connections, auth state |
| Auto fixture | per-test or per-worker | Yes | Yes | Side effects that must always run: blocking analytics, logging |
| `beforeEach` / `afterEach` | per-test | No (`afterEach` skipped on crash) | Yes | Simple, one-off setup that doesn't need cleanup |
| `beforeAll` / `afterAll` | per-worker | No (`afterAll` skipped on crash) | Dangerous if mutating shared state | One-time worker setup with no cleanup needs |

**The rule**: If it needs cleanup, use a fixture. If it doesn't need cleanup and is simple, a hook is acceptable. When in doubt, use a fixture.

## Patterns

### 1. Custom Test Fixture

**Use when**: Tests need a resource with guaranteed setup and teardown.
**Avoid when**: The setup is a single line with no teardown — a `beforeEach` is fine.

Fixtures use a `use()` callback. Everything before `use()` is setup; everything after is teardown. Teardown runs even if the test crashes.

**TypeScript**
```typescript
// fixtures.ts
import { test as base, expect } from '@playwright/test';

type TodoFixtures = {
  todoPage: TodoPage;
};

class TodoPage {
  constructor(private page: import('@playwright/test').Page) {}

  async addTodo(text: string) {
    await this.page.getByPlaceholder('What needs to be done?').fill(text);
    await this.page.getByPlaceholder('What needs to be done?').press('Enter');
  }

  async todos() {
    return this.page.getByTestId('todo-item');
  }
}

export const test = base.extend<TodoFixtures>({
  todoPage: async ({ page }, use) => {
    // Setup
    await page.goto('/todos');
    const todoPage = new TodoPage(page);

    // Hand the fixture to the test
    await use(todoPage);

    // Teardown — runs even if test fails or crashes
    await page.evaluate(() => localStorage.clear());
  },
});

export { expect };
```

```typescript
// todos.spec.ts
import { test, expect } from './fixtures';

test('add a todo item', async ({ todoPage, page }) => {
  await todoPage.addTodo('Buy milk');
  await expect(await todoPage.todos()).toHaveCount(1);
});
```

**JavaScript**
```javascript
// fixtures.js
const { test: base, expect } = require('@playwright/test');

class TodoPage {
  constructor(page) {
    this.page = page;
  }

  async addTodo(text) {
    await this.page.getByPlaceholder('What needs to be done?').fill(text);
    await this.page.getByPlaceholder('What needs to be done?').press('Enter');
  }

  async todos() {
    return this.page.getByTestId('todo-item');
  }
}

const test = base.extend({
  todoPage: async ({ page }, use) => {
    await page.goto('/todos');
    const todoPage = new TodoPage(page);
    await use(todoPage);
    await page.evaluate(() => localStorage.clear());
  },
});

module.exports = { test, expect };
```

### 2. Worker-Scoped Fixtures

**Use when**: A resource is expensive to create and safe to share across tests in the same worker (database connections, auth tokens, compiled assets).
**Avoid when**: Tests mutate the resource — each test must get its own copy.

Worker-scoped fixtures are created once per worker process, not once per test. They cannot depend on test-scoped fixtures (`page`, `context`, `request`).

**TypeScript**
```typescript
// fixtures.ts
import { test as base } from '@playwright/test';

type WorkerFixtures = {
  dbConnection: DatabaseClient;
  authToken: string;
};

export const test = base.extend<{}, WorkerFixtures>({
  dbConnection: [async ({}, use) => {
    const db = await DatabaseClient.connect(process.env.DB_URL!);
    await use(db);
    await db.disconnect();
  }, { scope: 'worker' }],

  authToken: [async ({}, use) => {
    const response = await fetch(`${process.env.API_URL}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'test-user',
        password: process.env.TEST_PASSWORD,
      }),
    });
    const { token } = await response.json();
    await use(token);
    // No teardown needed — token expires on its own
  }, { scope: 'worker' }],
});

export { expect } from '@playwright/test';
```

**JavaScript**
```javascript
// fixtures.js
const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  dbConnection: [async ({}, use) => {
    const db = await DatabaseClient.connect(process.env.DB_URL);
    await use(db);
    await db.disconnect();
  }, { scope: 'worker' }],

  authToken: [async ({}, use) => {
    const response = await fetch(`${process.env.API_URL}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'test-user',
        password: process.env.TEST_PASSWORD,
      }),
    });
    const { token } = await response.json();
    await use(token);
  }, { scope: 'worker' }],
});

module.exports = { test, expect };
```

**Important**: The second type parameter in `base.extend<TestFixtures, WorkerFixtures>` is for worker-scoped fixtures. Always put worker fixtures in the second generic argument.

### 3. Auto Fixtures

**Use when**: Something must run for every test without being explicitly requested — blocking analytics, capturing console errors, injecting feature flags.
**Avoid when**: Tests need to opt out. Auto fixtures always run; there is no per-test escape hatch.

**TypeScript**
```typescript
// fixtures.ts
import { test as base, expect } from '@playwright/test';

type AutoFixtures = {
  blockAnalytics: void;
  consoleErrors: string[];
};

export const test = base.extend<AutoFixtures>({
  // Blocks all analytics/tracking requests in every test
  blockAnalytics: [async ({ page }, use) => {
    await page.route(/google-analytics|segment|hotjar|mixpanel/, (route) =>
      route.abort()
    );
    await use();
  }, { auto: true }],

  // Captures console errors — fail test if unexpected errors appear
  consoleErrors: [async ({ page }, use) => {
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    await use(errors);
    // Teardown: assert no unexpected console errors
    const unexpected = errors.filter(
      (e) => !e.includes('Expected warning')
    );
    if (unexpected.length > 0) {
      throw new Error(
        `Unexpected console errors:\n${unexpected.join('\n')}`
      );
    }
  }, { auto: true }],
});

export { expect };
```

**JavaScript**
```javascript
// fixtures.js
const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  blockAnalytics: [async ({ page }, use) => {
    await page.route(/google-analytics|segment|hotjar|mixpanel/, (route) =>
      route.abort()
    );
    await use();
  }, { auto: true }],

  consoleErrors: [async ({ page }, use) => {
    const errors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    await use(errors);
    const unexpected = errors.filter(
      (e) => !e.includes('Expected warning')
    );
    if (unexpected.length > 0) {
      throw new Error(
        `Unexpected console errors:\n${unexpected.join('\n')}`
      );
    }
  }, { auto: true }],
});

module.exports = { test, expect };
```

Auto fixtures can also be worker-scoped with `{ auto: true, scope: 'worker' }` for things like starting a dev server once per worker.

### 4. Fixture Composition with `mergeTests()`

**Use when**: You have multiple fixture files (auth fixtures, API fixtures, UI fixtures) and tests need several of them.
**Avoid when**: You only have one fixture file. Don't over-engineer.

`mergeTests()` combines multiple extended `test` objects into one. Each fixture file defines its own concerns.

**TypeScript**
```typescript
// fixtures/auth.ts
import { test as base } from '@playwright/test';

type AuthFixtures = {
  authenticatedPage: import('@playwright/test').Page;
};

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');
    await use(page);
  },
});
```

```typescript
// fixtures/api.ts
import { test as base, APIRequestContext } from '@playwright/test';

type ApiFixtures = {
  apiClient: APIRequestContext;
};

export const test = base.extend<ApiFixtures>({
  apiClient: async ({ playwright }, use) => {
    const api = await playwright.request.newContext({
      baseURL: 'https://api.example.com',
      extraHTTPHeaders: { Authorization: `Bearer ${process.env.API_TOKEN}` },
    });
    await use(api);
    await api.dispose();
  },
});
```

```typescript
// fixtures/index.ts
import { mergeTests } from '@playwright/test';
import { test as authTest } from './auth';
import { test as apiTest } from './api';

export const test = mergeTests(authTest, apiTest);
export { expect } from '@playwright/test';
```

```typescript
// dashboard.spec.ts
import { test, expect } from './fixtures';

test('dashboard loads user data', async ({ authenticatedPage, apiClient }) => {
  // Both fixtures are available
  const data = await apiClient.get('/users/me');
  await expect(authenticatedPage.getByRole('heading')).toContainText('Dashboard');
});
```

**JavaScript**
```javascript
// fixtures/auth.js
const { test: base } = require('@playwright/test');

const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');
    await use(page);
  },
});

module.exports = { test };
```

```javascript
// fixtures/api.js
const { test: base } = require('@playwright/test');

const test = base.extend({
  apiClient: async ({ playwright }, use) => {
    const api = await playwright.request.newContext({
      baseURL: 'https://api.example.com',
      extraHTTPHeaders: { Authorization: `Bearer ${process.env.API_TOKEN}` },
    });
    await use(api);
    await api.dispose();
  },
});

module.exports = { test };
```

```javascript
// fixtures/index.js
const { mergeTests } = require('@playwright/test');
const { test: authTest } = require('./auth');
const { test: apiTest } = require('./api');

const test = mergeTests(authTest, apiTest);
module.exports = { test, expect: require('@playwright/test').expect };
```

### 5. Parameterized Fixtures (Option Fixtures)

**Use when**: A fixture's behavior should be configurable per-project or per-describe block (locale, viewport, user role, feature flags).
**Avoid when**: The value never changes — just hardcode it in the fixture.

Option fixtures are declared with `{ option: true }` and can be overridden in `playwright.config` under `use` or with `test.use()` in test files.

**TypeScript**
```typescript
// fixtures.ts
import { test as base, expect } from '@playwright/test';

type OptionFixtures = {
  userRole: 'admin' | 'editor' | 'viewer';
  locale: string;
};

type DerivedFixtures = {
  authenticatedPage: import('@playwright/test').Page;
};

export const test = base.extend<OptionFixtures & DerivedFixtures>({
  // Option fixtures — configurable per project or describe block
  userRole: ['viewer', { option: true }],
  locale: ['en-US', { option: true }],

  // Derived fixture — uses the option values
  authenticatedPage: async ({ page, userRole, locale }, use) => {
    await page.goto(`/login?locale=${locale}`);
    const credentials = {
      admin: { email: 'admin@test.com', password: 'admin-pass' },
      editor: { email: 'editor@test.com', password: 'editor-pass' },
      viewer: { email: 'viewer@test.com', password: 'viewer-pass' },
    };
    const { email, password } = credentials[userRole];
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await use(page);
  },
});

export { expect };
```

```typescript
// playwright.config.ts (override per project)
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'admin-tests',
      testDir: './tests/admin',
      use: { userRole: 'admin', locale: 'en-US' },
    },
    {
      name: 'viewer-tests',
      testDir: './tests/viewer',
      use: { userRole: 'viewer', locale: 'fr-FR' },
    },
  ],
});
```

```typescript
// admin-settings.spec.ts (override per describe block)
import { test, expect } from './fixtures';

test.describe('admin settings', () => {
  test.use({ userRole: 'admin' });

  test('can access settings page', async ({ authenticatedPage }) => {
    await authenticatedPage.goto('/settings');
    await expect(authenticatedPage.getByRole('heading')).toHaveText('Admin Settings');
  });
});
```

**JavaScript**
```javascript
// fixtures.js
const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  userRole: ['viewer', { option: true }],
  locale: ['en-US', { option: true }],

  authenticatedPage: async ({ page, userRole, locale }, use) => {
    await page.goto(`/login?locale=${locale}`);
    const credentials = {
      admin: { email: 'admin@test.com', password: 'admin-pass' },
      editor: { email: 'editor@test.com', password: 'editor-pass' },
      viewer: { email: 'viewer@test.com', password: 'viewer-pass' },
    };
    const { email, password } = credentials[userRole];
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await use(page);
  },
});

module.exports = { test, expect };
```

### 6. Fixture Dependencies

**Use when**: One fixture needs the output of another fixture. Playwright automatically resolves the dependency graph.
**Avoid when**: You are tempted to nest fixtures more than 3 levels deep — flatten the design instead.

Request fixtures by name in the destructured first argument. Playwright handles ordering and lifecycle.

**TypeScript**
```typescript
// fixtures.ts
import { test as base, expect } from '@playwright/test';

type Fixtures = {
  apiContext: import('@playwright/test').APIRequestContext;
  testUser: { id: string; email: string };
  userPage: import('@playwright/test').Page;
};

export const test = base.extend<Fixtures>({
  apiContext: async ({ playwright }, use) => {
    const ctx = await playwright.request.newContext({
      baseURL: process.env.API_URL,
    });
    await use(ctx);
    await ctx.dispose();
  },

  // Depends on apiContext — Playwright creates apiContext first
  testUser: async ({ apiContext }, use) => {
    const response = await apiContext.post('/test/users', {
      data: { email: `user-${Date.now()}@test.com`, role: 'editor' },
    });
    const user = await response.json();
    await use(user);
    // Teardown: delete the test user
    await apiContext.delete(`/test/users/${user.id}`);
  },

  // Depends on page AND testUser — both are ready before this runs
  userPage: async ({ page, testUser }, use) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill(testUser.email);
    await page.getByLabel('Password').fill('default-test-password');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');
    await use(page);
  },
});

export { expect };
```

**JavaScript**
```javascript
// fixtures.js
const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  apiContext: async ({ playwright }, use) => {
    const ctx = await playwright.request.newContext({
      baseURL: process.env.API_URL,
    });
    await use(ctx);
    await ctx.dispose();
  },

  testUser: async ({ apiContext }, use) => {
    const response = await apiContext.post('/test/users', {
      data: { email: `user-${Date.now()}@test.com`, role: 'editor' },
    });
    const user = await response.json();
    await use(user);
    await apiContext.delete(`/test/users/${user.id}`);
  },

  userPage: async ({ page, testUser }, use) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill(testUser.email);
    await page.getByLabel('Password').fill('default-test-password');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');
    await use(page);
  },
});

module.exports = { test, expect };
```

Teardown runs in reverse dependency order: `userPage` tears down first, then `testUser` (which deletes the user), then `apiContext`.

### 7. Overriding Built-in Fixtures

**Use when**: Every test needs the same modification to `page`, `context`, or `browser` — custom headers, viewport, locale, route blocking.
**Avoid when**: Only some tests need the override. Use a new named fixture instead to keep the default `page` available.

**TypeScript**
```typescript
// fixtures.ts
import { test as base, expect } from '@playwright/test';

export const test = base.extend({
  // Override the built-in context fixture to add custom headers
  context: async ({ browser }, use) => {
    const context = await browser.newContext({
      extraHTTPHeaders: {
        'X-Test-ID': `test-${Date.now()}`,
        'Accept-Language': 'en-US',
      },
      permissions: ['geolocation'],
      geolocation: { latitude: 37.7749, longitude: -122.4194 },
    });
    await use(context);
    await context.close();
  },

  // Override the built-in page fixture to block third-party scripts
  page: async ({ context }, use) => {
    const page = await context.newPage();
    await page.route('**/*.{png,jpg,jpeg,gif,svg}', (route) => route.abort());
    await use(page);
    // No need to close page — context.close() handles it
  },
});

export { expect };
```

**JavaScript**
```javascript
// fixtures.js
const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  context: async ({ browser }, use) => {
    const context = await browser.newContext({
      extraHTTPHeaders: {
        'X-Test-ID': `test-${Date.now()}`,
        'Accept-Language': 'en-US',
      },
      permissions: ['geolocation'],
      geolocation: { latitude: 37.7749, longitude: -122.4194 },
    });
    await use(context);
    await context.close();
  },

  page: async ({ context }, use) => {
    const page = await context.newPage();
    await page.route('**/*.{png,jpg,jpeg,gif,svg}', (route) => route.abort());
    await use(page);
  },
});

module.exports = { test, expect };
```

### 8. beforeEach / afterEach — When Hooks Are Acceptable

**Use when**: Simple, stateless setup with no teardown needed. Navigation to a starting URL is the canonical example.
**Avoid when**: The setup creates something that must be cleaned up. Use a fixture instead.

**TypeScript**
```typescript
// acceptable-hooks.spec.ts
import { test, expect } from '@playwright/test';

// Acceptable: simple navigation, no teardown needed
test.beforeEach(async ({ page }) => {
  await page.goto('/dashboard');
});

test('shows welcome message', async ({ page }) => {
  await expect(page.getByRole('heading')).toHaveText('Welcome');
});

test('shows navigation sidebar', async ({ page }) => {
  await expect(page.getByRole('navigation')).toBeVisible();
});
```

**JavaScript**
```javascript
// acceptable-hooks.spec.js
const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.goto('/dashboard');
});

test('shows welcome message', async ({ page }) => {
  await expect(page.getByRole('heading')).toHaveText('Welcome');
});

test('shows navigation sidebar', async ({ page }) => {
  await expect(page.getByRole('navigation')).toBeVisible();
});
```

Hooks can use fixtures in their argument list — `beforeEach(async ({ page, context })` works. But hooks cannot *define* fixtures.

### 9. beforeAll / afterAll — Worker-Level Hooks

**Use when**: One-time setup that all tests in a file share and that has no cleanup needs, such as logging a diagnostic or checking a precondition.
**Avoid when**: You are creating resources that need cleanup (use worker-scoped fixtures) or storing mutable state (this breaks parallelism).

**TypeScript**
```typescript
// health-check.spec.ts
import { test, expect } from '@playwright/test';

// Good: read-only check, no mutable state
test.beforeAll(async ({ request }) => {
  const response = await request.get('/api/health');
  expect(response.ok()).toBeTruthy();
});

test('homepage loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/My App/);
});
```

**JavaScript**
```javascript
// health-check.spec.js
const { test, expect } = require('@playwright/test');

test.beforeAll(async ({ request }) => {
  const response = await request.get('/api/health');
  expect(response.ok()).toBeTruthy();
});

test('homepage loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/My App/);
});
```

`beforeAll` / `afterAll` receive only worker-scoped fixtures: `request`, `browser`, and any custom worker fixtures. They do **not** receive `page` or `context` (those are per-test).

### 10. Typed Fixtures in TypeScript

Always define an interface for your fixtures. This gives you autocomplete, catches typos at compile time, and documents the fixture contract.

**TypeScript**
```typescript
// fixtures.ts
import { test as base, expect, Page, APIRequestContext } from '@playwright/test';

// Define fixture types explicitly
interface TestFixtures {
  adminPage: Page;
  editorPage: Page;
  apiClient: APIRequestContext;
}

interface WorkerFixtures {
  sharedToken: string;
}

export const test = base.extend<TestFixtures, WorkerFixtures>({
  sharedToken: [async ({}, use) => {
    const res = await fetch(`${process.env.API_URL}/auth/service-token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ secret: process.env.SERVICE_SECRET }),
    });
    const { token } = await res.json();
    await use(token);
  }, { scope: 'worker' }],

  apiClient: async ({ playwright, sharedToken }, use) => {
    const ctx = await playwright.request.newContext({
      baseURL: process.env.API_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${sharedToken}` },
    });
    await use(ctx);
    await ctx.dispose();
  },

  adminPage: async ({ browser }, use) => {
    const ctx = await browser.newContext({ storageState: 'auth/admin.json' });
    const page = await ctx.newPage();
    await use(page);
    await ctx.close();
  },

  editorPage: async ({ browser }, use) => {
    const ctx = await browser.newContext({ storageState: 'auth/editor.json' });
    const page = await ctx.newPage();
    await use(page);
    await ctx.close();
  },
});

export { expect };
```

## Decision Guide

```
I need to set up something before tests run.
│
├── Does it create a resource that MUST be cleaned up?
│   │
│   ├── YES → Use a fixture (setup before `use()`, teardown after)
│   │   │
│   │   ├── Is the resource expensive and safe to share across tests?
│   │   │   ├── YES → Worker-scoped fixture: { scope: 'worker' }
│   │   │   └── NO  → Test-scoped fixture (default)
│   │   │
│   │   ├── Should every test get this automatically?
│   │   │   ├── YES → Auto fixture: { auto: true }
│   │   │   └── NO  → Regular fixture (test declares it in args)
│   │   │
│   │   └── Should the value be configurable per project?
│   │       ├── YES → Option fixture: { option: true }
│   │       └── NO  → Regular fixture with hardcoded setup
│   │
│   └── NO → Hook is acceptable
│       │
│       ├── Per-test setup?
│       │   └── beforeEach
│       │
│       └── One-time per worker?
│           └── beforeAll (but only for read-only / diagnostic checks)
│
└── Am I combining fixtures from multiple domains?
    └── YES → mergeTests() from separate fixture files
```

## Anti-Patterns

### 1. Global Mutable State in `beforeAll`

```typescript
// BAD: Mutable state shared across parallel tests
let testUser: { id: string; email: string };

test.beforeAll(async ({ request }) => {
  const res = await request.post('/api/users', { data: { email: 'shared@test.com' } });
  testUser = await res.json(); // Shared mutable state!
});

test.afterAll(async ({ request }) => {
  await request.delete(`/api/users/${testUser.id}`); // Cleanup may not run
});

test('test 1', async ({ page }) => {
  // Uses testUser — but what if another worker also has a testUser?
});
```

```typescript
// GOOD: Worker-scoped fixture — isolated per worker, guaranteed cleanup
import { test as base } from '@playwright/test';

export const test = base.extend<{ testUser: { id: string; email: string } }>({
  testUser: async ({ request }, use) => {
    const res = await request.post('/api/users', {
      data: { email: `user-${Date.now()}@test.com` },
    });
    const user = await res.json();
    await use(user);
    await request.delete(`/api/users/${user.id}`);
  },
});
```

### 2. Cleanup in `afterEach` Instead of Fixture Teardown

```typescript
// BAD: afterEach is not guaranteed to run on crash
test.beforeEach(async ({ page }) => {
  await page.evaluate(() => localStorage.setItem('debug', 'true'));
});

test.afterEach(async ({ page }) => {
  // This might NOT run if the test crashes or times out
  await page.evaluate(() => localStorage.clear());
});
```

```typescript
// GOOD: Fixture teardown always runs
export const test = base.extend<{ debugMode: void }>({
  debugMode: async ({ page }, use) => {
    await page.evaluate(() => localStorage.setItem('debug', 'true'));
    await use();
    await page.evaluate(() => localStorage.clear()); // Guaranteed
  },
});
```

### 3. Fixtures That Do Too Many Things

```typescript
// BAD: One fixture doing setup for unrelated concerns
export const test = base.extend({
  everything: async ({ page }, use) => {
    // Logs in
    await page.goto('/login');
    await page.getByLabel('Email').fill('user@test.com');
    await page.getByLabel('Password').fill('password');
    await page.getByRole('button', { name: 'Sign in' }).click();
    // Creates test data
    await page.request.post('/api/products', { data: { name: 'Widget' } });
    // Blocks analytics
    await page.route(/analytics/, (r) => r.abort());
    // Sets locale
    await page.evaluate(() => localStorage.setItem('locale', 'en'));
    await use(page);
  },
});
```

```typescript
// GOOD: Separate fixtures, each with one responsibility
export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('user@test.com');
    await page.getByLabel('Password').fill('password');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await use(page);
  },

  testProduct: async ({ request }, use) => {
    const res = await request.post('/api/products', { data: { name: 'Widget' } });
    const product = await res.json();
    await use(product);
    await request.delete(`/api/products/${product.id}`);
  },

  blockAnalytics: [async ({ page }, use) => {
    await page.route(/analytics/, (r) => r.abort());
    await use();
  }, { auto: true }],
});
```

### 4. Over-Abstracting Fixtures

```typescript
// BAD: Fixture factory with layers of indirection nobody can follow
const createFixture = (role, permissions, options) =>
  base.extend({
    [`${role}Page`]: async ({ page }, use) => {
      await setupRole(page, role, permissions, options);
      await use(page);
    },
  });

const adminTest = createFixture('admin', ['read', 'write', 'delete'], { mfa: true });
const editorTest = createFixture('editor', ['read', 'write'], { mfa: false });
// Good luck debugging which fixture ran
```

```typescript
// GOOD: Explicit fixtures — boring but readable
export const test = base.extend({
  adminPage: async ({ browser }, use) => {
    const ctx = await browser.newContext({ storageState: 'auth/admin.json' });
    const page = await ctx.newPage();
    await use(page);
    await ctx.close();
  },

  editorPage: async ({ browser }, use) => {
    const ctx = await browser.newContext({ storageState: 'auth/editor.json' });
    const page = await ctx.newPage();
    await use(page);
    await ctx.close();
  },
});
```

### 5. Not Typing Fixtures in TypeScript

```typescript
// BAD: No type parameter — no autocomplete, no compile-time errors
export const test = base.extend({
  myFixture: async ({ page }, use) => {
    await use({ count: 42 });
  },
});
// test('example', async ({ myFixture }) => {
//   myFixture.cont // No autocomplete, no type safety
// });
```

```typescript
// GOOD: Explicit type interface
interface MyFixtures {
  myFixture: { count: number };
}

export const test = base.extend<MyFixtures>({
  myFixture: async ({ page }, use) => {
    await use({ count: 42 });
  },
});
// test('example', async ({ myFixture }) => {
//   myFixture.count // Autocomplete works, typos caught at compile time
// });
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Cannot use a test-scoped fixture in a worker-scoped fixture` | Worker fixture depends on `page`, `context`, or test-scoped custom fixture | Worker fixtures can only depend on other worker fixtures or built-in worker fixtures (`browser`, `playwright`) |
| `Fixture "X" has already been registered` | Two fixture files define the same fixture name and are both extended | Use `mergeTests()` instead of chaining `.extend()` calls, or rename one fixture |
| Fixture teardown not running | You used `afterEach` instead of the `use()` callback pattern | Move cleanup code after the `await use()` call inside the fixture |
| `beforeAll` can't access `page` | `page` is test-scoped; `beforeAll` only gets worker-scoped fixtures | Use a worker-scoped fixture, or move logic to `beforeEach` |
| Test hangs inside fixture | `await use()` was never called — Playwright waits indefinitely for the fixture to yield | Ensure every fixture code path calls `await use(value)` exactly once |
| Fixture runs but test doesn't see the value | Fixture not declared in the test's destructured arguments | Add the fixture name to the test function signature: `test('name', async ({ myFixture }) => { ... })` |
| Option fixture value ignored | `test.use()` called inside `test()` instead of `test.describe()` | `test.use()` must be at the top level of a `describe` block or file, not inside a test |
| Auto fixture not running | Fixture file not imported — the custom `test` is not used | Import and use the `test` from your fixture file, not from `@playwright/test` |

## Related

- [pom/page-object-model.md](../pom/page-object-model.md) — Page objects are typically consumed via fixtures
- [core/test-organization.md](test-organization.md) — Where to put fixture files in the project tree
- [core/configuration.md](configuration.md) — Option fixtures are configured in `playwright.config`
- [core/authentication.md](authentication.md) — Auth state is the most common worker-scoped fixture
- [ci/global-setup-teardown.md](../ci/global-setup-teardown.md) — For truly global (all-workers) setup, not per-worker
- [pom/pom-vs-fixtures-vs-helpers.md](../pom/pom-vs-fixtures-vs-helpers.md) — When to use each abstraction
