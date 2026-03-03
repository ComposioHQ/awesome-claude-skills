# Authentication Testing

> **When to use**: Any app that has login, session management, or protected routes. Authentication is the most common source of slow test suites -- get this right and your entire suite speeds up.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/fixtures-and-hooks.md](fixtures-and-hooks.md)

## Quick Reference

```typescript
// Storage state reuse — the #1 pattern for fast auth
await page.goto('/login');
await page.getByLabel('Email').fill('user@test.com');
await page.getByLabel('Password').fill('password');
await page.getByRole('button', { name: 'Sign in' }).click();
await page.context().storageState({ path: '.auth/user.json' });

// Reuse in config — every test starts authenticated, zero login overhead
{ use: { storageState: '.auth/user.json' } }

// API login — skip the UI entirely
const context = await browser.newContext();
const response = await context.request.post('/api/auth/login', {
  data: { email: 'user@test.com', password: 'password' },
});
await context.storageState({ path: '.auth/user.json' });
```

## Patterns

### Storage State Reuse

**Use when**: You need authenticated tests and want to avoid logging in before every test. This is the default pattern for nearly every project.
**Avoid when**: Tests require completely fresh sessions with no prior state, or you are testing the login flow itself.

Playwright's `storageState` serializes cookies and localStorage to a JSON file. Load it in any browser context to start authenticated instantly.

**TypeScript**
```typescript
// scripts/save-auth-state.ts — run once to generate the state file
import { chromium } from '@playwright/test';

async function saveAuthState() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto('http://localhost:3000/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('s3cure!Pass');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  // Save cookies + localStorage to a file
  await context.storageState({ path: '.auth/user.json' });
  await browser.close();
}

saveAuthState();
```

```typescript
// playwright.config.ts — load saved state for all tests
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    baseURL: 'http://localhost:3000',
    storageState: '.auth/user.json',
  },
});
```

```typescript
// tests/dashboard.spec.ts — test starts already logged in
import { test, expect } from '@playwright/test';

test('authenticated user sees dashboard', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  // No login step needed — storageState handles it
});
```

**JavaScript**
```javascript
// scripts/save-auth-state.js
const { chromium } = require('@playwright/test');

async function saveAuthState() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto('http://localhost:3000/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('s3cure!Pass');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  await context.storageState({ path: '.auth/user.json' });
  await browser.close();
}

saveAuthState();
```

```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  use: {
    baseURL: 'http://localhost:3000',
    storageState: '.auth/user.json',
  },
});
```

### Global Setup Authentication

**Use when**: You want to authenticate once before the entire test suite runs, then reuse that session everywhere. The standard Playwright-recommended approach.
**Avoid when**: Different tests need different users, or your tokens expire faster than your suite runs.

Global setup runs once per `npx playwright test` invocation. It logs in, saves the state, and every test project that references that state file starts authenticated.

**TypeScript**
```typescript
// global-setup.ts
import { chromium, type FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const { baseURL } = config.projects[0].use;
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto(`${baseURL}/login`);
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('**/dashboard');

  await context.storageState({ path: '.auth/user.json' });
  await browser.close();
}

export default globalSetup;
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  globalSetup: require.resolve('./global-setup'),
  use: {
    baseURL: 'http://localhost:3000',
    storageState: '.auth/user.json',
  },
});
```

**JavaScript**
```javascript
// global-setup.js
const { chromium } = require('@playwright/test');

async function globalSetup(config) {
  const { baseURL } = config.projects[0].use;
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto(`${baseURL}/login`);
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('**/dashboard');

  await context.storageState({ path: '.auth/user.json' });
  await browser.close();
}

module.exports = globalSetup;
```

```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  globalSetup: require.resolve('./global-setup'),
  use: {
    baseURL: 'http://localhost:3000',
    storageState: '.auth/user.json',
  },
});
```

**Important**: Add `.auth/` to your `.gitignore`. Auth state files contain session tokens and should never be committed.

### Per-Worker Authentication

**Use when**: Each parallel worker needs its own authenticated session to avoid race conditions. Essential when tests modify user state (profile updates, settings changes, data mutations).
**Avoid when**: Tests are read-only and a shared session is safe, or you only run tests serially.

Worker-scoped fixtures run once per worker process, not once per test. This gives each parallel worker its own isolated session.

**TypeScript**
```typescript
// fixtures/auth.ts
import { test as base, type BrowserContext } from '@playwright/test';

type AuthFixtures = {
  authenticatedContext: BrowserContext;
};

export const test = base.extend<{}, AuthFixtures>({
  authenticatedContext: [async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto('/login');
    await page.getByLabel('Email').fill(`worker-${test.info().parallelIndex}@test.com`);
    await page.getByLabel('Password').fill('password');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');
    await page.close();

    await use(context);
    await context.close();
  }, { scope: 'worker' }],
});

export { expect } from '@playwright/test';
```

```typescript
// tests/profile.spec.ts
import { test, expect } from '../fixtures/auth';

test('update profile name', async ({ authenticatedContext }) => {
  const page = await authenticatedContext.newPage();
  await page.goto('/settings/profile');
  await page.getByLabel('Display name').fill('Updated Name');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText('Profile updated')).toBeVisible();
});
```

**JavaScript**
```javascript
// fixtures/auth.js
const { test: base } = require('@playwright/test');

const test = base.extend({
  authenticatedContext: [async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto('/login');
    await page.getByLabel('Email').fill(`worker-${test.info().parallelIndex}@test.com`);
    await page.getByLabel('Password').fill('password');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');
    await page.close();

    await use(context);
    await context.close();
  }, { scope: 'worker' }],
});

module.exports = { test, expect: require('@playwright/test').expect };
```

### Multiple Roles

**Use when**: Your app has role-based access control and you need to test that admins, regular users, and viewers see different things.
**Avoid when**: Your app has a single user role.

Use separate Playwright projects with different storage states, one per role. This is cleaner than switching roles within tests.

**TypeScript**
```typescript
// global-setup.ts — authenticate all roles
import { chromium, type FullConfig } from '@playwright/test';

const users = [
  { role: 'admin', email: 'admin@test.com', password: process.env.ADMIN_PASSWORD! },
  { role: 'user', email: 'user@test.com', password: process.env.USER_PASSWORD! },
  { role: 'viewer', email: 'viewer@test.com', password: process.env.VIEWER_PASSWORD! },
];

async function globalSetup(config: FullConfig) {
  const { baseURL } = config.projects[0].use;

  for (const { role, email, password } of users) {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto(`${baseURL}/login`);
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('**/dashboard');

    await context.storageState({ path: `.auth/${role}.json` });
    await browser.close();
  }
}

export default globalSetup;
```

```typescript
// playwright.config.ts — one project per role
import { defineConfig } from '@playwright/test';

export default defineConfig({
  globalSetup: require.resolve('./global-setup'),
  projects: [
    {
      name: 'admin',
      use: { storageState: '.auth/admin.json' },
      testMatch: '**/*.admin.spec.ts',
    },
    {
      name: 'user',
      use: { storageState: '.auth/user.json' },
      testMatch: '**/*.user.spec.ts',
    },
    {
      name: 'viewer',
      use: { storageState: '.auth/viewer.json' },
      testMatch: '**/*.viewer.spec.ts',
    },
    {
      name: 'unauthenticated',
      use: { storageState: { cookies: [], origins: [] } },
      testMatch: '**/*.anon.spec.ts',
    },
  ],
});
```

```typescript
// tests/admin-panel.admin.spec.ts
import { test, expect } from '@playwright/test';

test('admin can access user management', async ({ page }) => {
  await page.goto('/admin/users');
  await expect(page.getByRole('heading', { name: 'User Management' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Delete user' })).toBeEnabled();
});
```

```typescript
// tests/admin-panel.viewer.spec.ts
import { test, expect } from '@playwright/test';

test('viewer cannot access admin panel', async ({ page }) => {
  await page.goto('/admin/users');
  // Should redirect to forbidden or dashboard
  await expect(page.getByText('Access denied')).toBeVisible();
});
```

**JavaScript**
```javascript
// global-setup.js
const { chromium } = require('@playwright/test');

const users = [
  { role: 'admin', email: 'admin@test.com', password: process.env.ADMIN_PASSWORD },
  { role: 'user', email: 'user@test.com', password: process.env.USER_PASSWORD },
  { role: 'viewer', email: 'viewer@test.com', password: process.env.VIEWER_PASSWORD },
];

async function globalSetup(config) {
  const { baseURL } = config.projects[0].use;

  for (const { role, email, password } of users) {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto(`${baseURL}/login`);
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('**/dashboard');

    await context.storageState({ path: `.auth/${role}.json` });
    await browser.close();
  }
}

module.exports = globalSetup;
```

```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  globalSetup: require.resolve('./global-setup'),
  projects: [
    {
      name: 'admin',
      use: { storageState: '.auth/admin.json' },
      testMatch: '**/*.admin.spec.js',
    },
    {
      name: 'user',
      use: { storageState: '.auth/user.json' },
      testMatch: '**/*.user.spec.js',
    },
    {
      name: 'viewer',
      use: { storageState: '.auth/viewer.json' },
      testMatch: '**/*.viewer.spec.js',
    },
    {
      name: 'unauthenticated',
      use: { storageState: { cookies: [], origins: [] } },
      testMatch: '**/*.anon.spec.js',
    },
  ],
});
```

**Alternative**: Use a fixture that accepts a role parameter when you need role switching within a single spec file.

```typescript
// fixtures/auth.ts — role-based fixture
import { test as base, type Page } from '@playwright/test';
import fs from 'fs';

type RoleFixtures = {
  loginAs: (role: 'admin' | 'user' | 'viewer') => Promise<Page>;
};

export const test = base.extend<RoleFixtures>({
  loginAs: async ({ browser }, use) => {
    const pages: Page[] = [];

    await use(async (role) => {
      const statePath = `.auth/${role}.json`;
      if (!fs.existsSync(statePath)) {
        throw new Error(`Auth state for role "${role}" not found at ${statePath}. Run global setup first.`);
      }
      const context = await browser.newContext({ storageState: statePath });
      const page = await context.newPage();
      pages.push(page);
      return page;
    });

    for (const page of pages) {
      await page.context().close();
    }
  },
});

export { expect } from '@playwright/test';
```

```typescript
// tests/role-comparison.spec.ts
import { test, expect } from '../fixtures/auth';

test('admin sees delete button, viewer does not', async ({ loginAs }) => {
  const adminPage = await loginAs('admin');
  await adminPage.goto('/admin/users');
  await expect(adminPage.getByRole('button', { name: 'Delete user' })).toBeVisible();

  const viewerPage = await loginAs('viewer');
  await viewerPage.goto('/admin/users');
  await expect(viewerPage.getByText('Access denied')).toBeVisible();
});
```

### OAuth/SSO Mocking

**Use when**: Your app authenticates via a third-party OAuth provider (Google, GitHub, Okta, Auth0) and you cannot or should not hit the real provider in tests.
**Avoid when**: You have a dedicated test tenant on the OAuth provider and want true end-to-end coverage of the OAuth flow.

The strategy: intercept the OAuth callback route and inject a valid session directly, bypassing the provider entirely.

**TypeScript**
```typescript
// fixtures/oauth-mock.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  // Mock OAuth by intercepting the callback and injecting session cookies
  page: async ({ page }, use) => {
    // Intercept the OAuth redirect to the provider
    await page.route('**/auth/callback**', async (route) => {
      // Instead of going to Google/GitHub, call your own backend
      // with a test token that your backend recognizes in test mode
      const url = new URL(route.request().url());
      url.searchParams.set('code', 'test-oauth-code');
      url.searchParams.set('state', url.searchParams.get('state') || '');

      await route.continue({ url: url.toString() });
    });

    await use(page);
  },
});

export { expect } from '@playwright/test';
```

```typescript
// tests/oauth-login.spec.ts — approach 1: mock the callback route
import { test, expect } from '@playwright/test';

test('login via mocked OAuth flow', async ({ page }) => {
  // Intercept the redirect to the OAuth provider
  await page.route('https://accounts.google.com/**', async (route) => {
    // Redirect back to your app's callback with a fake auth code
    const callbackUrl = new URL('http://localhost:3000/auth/callback');
    callbackUrl.searchParams.set('code', 'mock-auth-code-12345');
    callbackUrl.searchParams.set('state', 'expected-state-value');
    await route.fulfill({
      status: 302,
      headers: { location: callbackUrl.toString() },
    });
  });

  await page.goto('/login');
  await page.getByRole('button', { name: 'Sign in with Google' }).click();

  // Your backend must accept "mock-auth-code-12345" in test mode
  // and exchange it for a real session
  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

```typescript
// tests/oauth-login.spec.ts — approach 2: API-based session injection
import { test, expect } from '@playwright/test';

test('bypass OAuth entirely via API session injection', async ({ page, request }) => {
  // Call a test-only endpoint that creates a session without OAuth
  // Your backend exposes this only when NODE_ENV=test
  const response = await request.post('/api/test/create-session', {
    data: {
      email: 'oauth-user@test.com',
      provider: 'google',
      role: 'user',
    },
  });
  expect(response.ok()).toBeTruthy();

  // The response sets session cookies; storageState captures them
  await page.context().storageState({ path: '.auth/oauth-user.json' });

  // Now navigate — already authenticated
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('login via mocked OAuth flow', async ({ page }) => {
  await page.route('https://accounts.google.com/**', async (route) => {
    const callbackUrl = new URL('http://localhost:3000/auth/callback');
    callbackUrl.searchParams.set('code', 'mock-auth-code-12345');
    callbackUrl.searchParams.set('state', 'expected-state-value');
    await route.fulfill({
      status: 302,
      headers: { location: callbackUrl.toString() },
    });
  });

  await page.goto('/login');
  await page.getByRole('button', { name: 'Sign in with Google' }).click();

  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

```javascript
test('bypass OAuth entirely via API session injection', async ({ page, request }) => {
  const response = await request.post('/api/test/create-session', {
    data: {
      email: 'oauth-user@test.com',
      provider: 'google',
      role: 'user',
    },
  });
  expect(response.ok()).toBeTruthy();

  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**Backend requirement**: Your backend must expose a test-only session creation endpoint (guarded by `NODE_ENV=test`) or accept a known test OAuth code. Never ship test auth endpoints to production.

### MFA Handling

**Use when**: Your app requires two-factor authentication (TOTP, SMS, email codes) and you need to handle it in tests.
**Avoid when**: MFA is optional and you can disable it for test accounts.

**Strategy 1**: Generate real TOTP codes from a shared secret. This is the most reliable approach.

**TypeScript**
```typescript
// helpers/totp.ts
import * as OTPAuth from 'otpauth';

export function generateTOTP(secret: string): string {
  const totp = new OTPAuth.TOTP({
    secret: OTPAuth.Secret.fromBase32(secret),
    digits: 6,
    period: 30,
    algorithm: 'SHA1',
  });
  return totp.generate();
}
```

```typescript
// tests/mfa-login.spec.ts
import { test, expect } from '@playwright/test';
import { generateTOTP } from '../helpers/totp';

test('login with TOTP two-factor auth', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('mfa-user@test.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // MFA challenge screen
  await expect(page.getByText('Enter your authentication code')).toBeVisible();

  // Generate a valid TOTP from the test account's secret
  const code = generateTOTP(process.env.MFA_TOTP_SECRET!);
  await page.getByLabel('Authentication code').fill(code);
  await page.getByRole('button', { name: 'Verify' }).click();

  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**JavaScript**
```javascript
// helpers/totp.js
const OTPAuth = require('otpauth');

function generateTOTP(secret) {
  const totp = new OTPAuth.TOTP({
    secret: OTPAuth.Secret.fromBase32(secret),
    digits: 6,
    period: 30,
    algorithm: 'SHA1',
  });
  return totp.generate();
}

module.exports = { generateTOTP };
```

```javascript
// tests/mfa-login.spec.js
const { test, expect } = require('@playwright/test');
const { generateTOTP } = require('../helpers/totp');

test('login with TOTP two-factor auth', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('mfa-user@test.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByText('Enter your authentication code')).toBeVisible();

  const code = generateTOTP(process.env.MFA_TOTP_SECRET);
  await page.getByLabel('Authentication code').fill(code);
  await page.getByRole('button', { name: 'Verify' }).click();

  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**Strategy 2**: Mock MFA at the backend level. Have your backend accept a known bypass code (e.g., `000000`) when `NODE_ENV=test`.

```typescript
// Simpler but less realistic — backend accepts bypass code in test mode
test('login with MFA bypass code', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('mfa-user@test.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Backend accepts "000000" as a valid MFA code in test environment
  await page.getByLabel('Authentication code').fill('000000');
  await page.getByRole('button', { name: 'Verify' }).click();

  await page.waitForURL('/dashboard');
});
```

**Strategy 3**: Disable MFA for test accounts at the infrastructure level. Set up dedicated test users with MFA disabled. This is the simplest approach when feasible.

### Session Refresh

**Use when**: Your tokens expire during long test runs or your app uses short-lived JWTs that need refreshing.
**Avoid when**: Your test suite runs in under a few minutes and tokens outlast the entire run.

**TypeScript**
```typescript
// fixtures/auth-with-refresh.ts
import { test as base, type BrowserContext } from '@playwright/test';
import fs from 'fs';

type AuthFixtures = {
  authenticatedPage: import('@playwright/test').Page;
};

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ browser }, use) => {
    const statePath = '.auth/user.json';

    // Check if the stored session is still valid
    let context: BrowserContext;
    if (fs.existsSync(statePath)) {
      context = await browser.newContext({ storageState: statePath });
      const page = await context.newPage();

      // Quick health check — does the session still work?
      const response = await page.request.get('/api/auth/me');
      if (response.ok()) {
        await use(page);
        await context.close();
        return;
      }
      // Session expired — close and re-authenticate
      await context.close();
    }

    // Re-authenticate
    context = await browser.newContext();
    const page = await context.newPage();
    await page.goto('/login');
    await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
    await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');

    // Save refreshed state for subsequent tests
    await context.storageState({ path: statePath });

    await use(page);
    await context.close();
  },
});

export { expect } from '@playwright/test';
```

```typescript
// Alternative: intercept token refresh requests to ensure they work
import { test, expect } from '@playwright/test';

test('app refreshes expired token automatically', async ({ page }) => {
  await page.goto('/dashboard');

  // Simulate token expiration by clearing the access token cookie
  await page.context().clearCookies({ name: 'access_token' });

  // Next API call should trigger a token refresh via refresh_token cookie
  const refreshPromise = page.waitForResponse('**/api/auth/refresh');
  await page.getByRole('button', { name: 'Load data' }).click();
  const refreshResponse = await refreshPromise;

  expect(refreshResponse.status()).toBe(200);
  await expect(page.getByTestId('data-table')).toBeVisible();
});
```

**JavaScript**
```javascript
// fixtures/auth-with-refresh.js
const { test: base } = require('@playwright/test');
const fs = require('fs');

const test = base.extend({
  authenticatedPage: async ({ browser }, use) => {
    const statePath = '.auth/user.json';

    if (fs.existsSync(statePath)) {
      const context = await browser.newContext({ storageState: statePath });
      const page = await context.newPage();
      const response = await page.request.get('/api/auth/me');

      if (response.ok()) {
        await use(page);
        await context.close();
        return;
      }
      await context.close();
    }

    const context = await browser.newContext();
    const page = await context.newPage();
    await page.goto('/login');
    await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL);
    await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');
    await context.storageState({ path: statePath });

    await use(page);
    await context.close();
  },
});

module.exports = { test, expect: require('@playwright/test').expect };
```

### Login Page Object

**Use when**: Multiple test files need to log in and you want consistent, maintainable login logic with proper error handling.
**Avoid when**: You use `storageState` everywhere and never navigate through the login UI in tests (still useful for testing the login page itself).

**TypeScript**
```typescript
// page-objects/LoginPage.ts
import { type Page, type Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly signInButton: Locator;
  readonly errorMessage: Locator;
  readonly forgotPasswordLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.signInButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
    this.forgotPasswordLink = page.getByRole('link', { name: 'Forgot password' });
  }

  async goto() {
    await this.page.goto('/login');
    await expect(this.signInButton).toBeVisible();
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.signInButton.click();
  }

  async loginAndWaitForDashboard(email: string, password: string) {
    await this.login(email, password);
    await this.page.waitForURL('/dashboard');
  }

  async expectError(message: string | RegExp) {
    await expect(this.errorMessage).toContainText(message);
  }

  async expectFieldError(field: 'email' | 'password', message: string) {
    const input = field === 'email' ? this.emailInput : this.passwordInput;
    await expect(input).toHaveAttribute('aria-invalid', 'true');
    // Error message associated with the field
    const errorId = await input.getAttribute('aria-describedby');
    if (errorId) {
      await expect(this.page.locator(`#${errorId}`)).toContainText(message);
    }
  }
}
```

```typescript
// tests/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';

// These tests run WITHOUT storageState (unauthenticated)
test.use({ storageState: { cookies: [], origins: [] } });

test.describe('login page', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('successful login redirects to dashboard', async ({ page }) => {
    await loginPage.loginAndWaitForDashboard('user@test.com', 'password');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });

  test('wrong password shows error', async () => {
    await loginPage.login('user@test.com', 'wrong-password');
    await loginPage.expectError('Invalid email or password');
  });

  test('empty fields show validation errors', async () => {
    await loginPage.signInButton.click();
    await loginPage.expectFieldError('email', 'Email is required');
  });

  test('forgot password link navigates correctly', async ({ page }) => {
    await loginPage.forgotPasswordLink.click();
    await page.waitForURL('/forgot-password');
    await expect(page.getByRole('heading', { name: 'Reset password' })).toBeVisible();
  });
});
```

**JavaScript**
```javascript
// page-objects/LoginPage.js
const { expect } = require('@playwright/test');

class LoginPage {
  constructor(page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.signInButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
    this.forgotPasswordLink = page.getByRole('link', { name: 'Forgot password' });
  }

  async goto() {
    await this.page.goto('/login');
    await expect(this.signInButton).toBeVisible();
  }

  async login(email, password) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.signInButton.click();
  }

  async loginAndWaitForDashboard(email, password) {
    await this.login(email, password);
    await this.page.waitForURL('/dashboard');
  }

  async expectError(message) {
    await expect(this.errorMessage).toContainText(message);
  }

  async expectFieldError(field, message) {
    const input = field === 'email' ? this.emailInput : this.passwordInput;
    await expect(input).toHaveAttribute('aria-invalid', 'true');
    const errorId = await input.getAttribute('aria-describedby');
    if (errorId) {
      await expect(this.page.locator(`#${errorId}`)).toContainText(message);
    }
  }
}

module.exports = { LoginPage };
```

```javascript
// tests/login.spec.js
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../page-objects/LoginPage');

test.use({ storageState: { cookies: [], origins: [] } });

test.describe('login page', () => {
  let loginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('successful login redirects to dashboard', async ({ page }) => {
    await loginPage.loginAndWaitForDashboard('user@test.com', 'password');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });

  test('wrong password shows error', async () => {
    await loginPage.login('user@test.com', 'wrong-password');
    await loginPage.expectError('Invalid email or password');
  });

  test('empty fields show validation errors', async () => {
    await loginPage.signInButton.click();
    await loginPage.expectFieldError('email', 'Email is required');
  });
});
```

### API-Based Login

**Use when**: You want the fastest possible authentication without any browser interaction. Ideal for generating `storageState` files in global setup or fixtures.
**Avoid when**: You are specifically testing the login UI. Use the Login Page Object pattern instead.

API login is typically 5-10x faster than UI login. Use `request.post()` to hit your auth endpoint directly, then capture the resulting cookies.

**TypeScript**
```typescript
// global-setup.ts — API-based login (fastest)
import { request, type FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const { baseURL } = config.projects[0].use;

  const requestContext = await request.newContext({ baseURL });

  // Login via API — no browser needed
  const response = await requestContext.post('/api/auth/login', {
    data: {
      email: process.env.TEST_USER_EMAIL!,
      password: process.env.TEST_USER_PASSWORD!,
    },
  });

  if (!response.ok()) {
    throw new Error(`API login failed: ${response.status()} ${await response.text()}`);
  }

  // Save the session cookies from the API response
  await requestContext.storageState({ path: '.auth/user.json' });
  await requestContext.dispose();
}

export default globalSetup;
```

```typescript
// fixtures/api-auth.ts — fixture version for per-test authentication
import { test as base } from '@playwright/test';

export const test = base.extend({
  authenticatedPage: async ({ browser, playwright }, use) => {
    // Create API context and login
    const apiContext = await playwright.request.newContext({
      baseURL: 'http://localhost:3000',
    });

    await apiContext.post('/api/auth/login', {
      data: {
        email: 'user@test.com',
        password: 'password',
      },
    });

    // Transfer API session to browser context
    const state = await apiContext.storageState();
    const context = await browser.newContext({ storageState: state });
    const page = await context.newPage();

    await use(page);

    await context.close();
    await apiContext.dispose();
  },
});

export { expect } from '@playwright/test';
```

**JavaScript**
```javascript
// global-setup.js — API-based login
const { request } = require('@playwright/test');

async function globalSetup(config) {
  const { baseURL } = config.projects[0].use;
  const requestContext = await request.newContext({ baseURL });

  const response = await requestContext.post('/api/auth/login', {
    data: {
      email: process.env.TEST_USER_EMAIL,
      password: process.env.TEST_USER_PASSWORD,
    },
  });

  if (!response.ok()) {
    throw new Error(`API login failed: ${response.status()} ${await response.text()}`);
  }

  await requestContext.storageState({ path: '.auth/user.json' });
  await requestContext.dispose();
}

module.exports = globalSetup;
```

```javascript
// fixtures/api-auth.js
const { test: base } = require('@playwright/test');

const test = base.extend({
  authenticatedPage: async ({ browser, playwright }, use) => {
    const apiContext = await playwright.request.newContext({
      baseURL: 'http://localhost:3000',
    });

    await apiContext.post('/api/auth/login', {
      data: { email: 'user@test.com', password: 'password' },
    });

    const state = await apiContext.storageState();
    const context = await browser.newContext({ storageState: state });
    const page = await context.newPage();

    await use(page);

    await context.close();
    await apiContext.dispose();
  },
});

module.exports = { test, expect: require('@playwright/test').expect };
```

### Unauthenticated Tests

**Use when**: Testing the login page, signup flow, password reset, public pages, authentication error handling, or redirect behavior for unauthenticated users.
**Avoid when**: The test requires a logged-in user.

When your config sets a default `storageState`, you must explicitly clear it for unauthenticated tests.

**TypeScript**
```typescript
// tests/public-pages.spec.ts
import { test, expect } from '@playwright/test';

// Override storageState to empty — no cookies, no session
test.use({ storageState: { cookies: [], origins: [] } });

test.describe('unauthenticated access', () => {
  test('homepage is accessible without login', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Sign in' })).toBeVisible();
  });

  test('protected route redirects to login', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForURL('**/login**');
    // Verify redirect preserves the intended destination
    expect(page.url()).toContain('redirect=%2Fdashboard');
  });

  test('expired session shows re-login prompt', async ({ page, context }) => {
    // Start with a valid session, then invalidate it
    await page.goto('/dashboard');

    // Clear all cookies to simulate session expiration
    await context.clearCookies();

    // Next navigation should detect the invalid session
    await page.goto('/settings');
    await page.waitForURL('**/login**');
    await expect(page.getByText('Your session has expired')).toBeVisible();
  });

  test('login page shows social auth options', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('button', { name: 'Sign in with Google' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign in with GitHub' })).toBeVisible();
  });

  test('signup flow creates account', async ({ page }) => {
    await page.goto('/signup');
    await page.getByLabel('Name').fill('New User');
    await page.getByLabel('Email').fill(`test-${Date.now()}@test.com`);
    await page.getByLabel('Password', { exact: true }).fill('s3cure!Pass');
    await page.getByLabel('Confirm password').fill('s3cure!Pass');
    await page.getByRole('button', { name: 'Create account' }).click();

    await page.waitForURL('/onboarding');
    await expect(page.getByText('Welcome, New User')).toBeVisible();
  });
});
```

**JavaScript**
```javascript
// tests/public-pages.spec.js
const { test, expect } = require('@playwright/test');

test.use({ storageState: { cookies: [], origins: [] } });

test.describe('unauthenticated access', () => {
  test('homepage is accessible without login', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Sign in' })).toBeVisible();
  });

  test('protected route redirects to login', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForURL('**/login**');
    expect(page.url()).toContain('redirect=%2Fdashboard');
  });

  test('signup flow creates account', async ({ page }) => {
    await page.goto('/signup');
    await page.getByLabel('Name').fill('New User');
    await page.getByLabel('Email').fill(`test-${Date.now()}@test.com`);
    await page.getByLabel('Password', { exact: true }).fill('s3cure!Pass');
    await page.getByLabel('Confirm password').fill('s3cure!Pass');
    await page.getByRole('button', { name: 'Create account' }).click();

    await page.waitForURL('/onboarding');
    await expect(page.getByText('Welcome, New User')).toBeVisible();
  });
});
```

## Decision Guide

| Scenario | Approach | Speed | Isolation | When to Choose |
|---|---|---|---|---|
| Most tests need auth | Global setup + `storageState` | Fastest | Shared session | Default for nearly every project. Login happens once, all tests reuse the session file. |
| Tests modify user state | Per-worker fixture | Fast | Per worker | Tests update profile, change settings, or mutate data that could conflict between parallel workers. |
| Multiple user roles | Per-project `storageState` | Fastest | Per role | App has admin/user/viewer roles. Each project gets its own state file from global setup. |
| Testing the login page | No `storageState` | N/A | Full | Use `test.use({ storageState: { cookies: [], origins: [] } })` to override defaults. |
| OAuth/SSO provider | Mock the callback | Fast | Per test | Never hit real OAuth providers in CI. Mock the redirect or use API session injection. |
| MFA is required | TOTP generation or bypass | Moderate | Per test | Generate real TOTP codes from a shared secret, or use a test-mode bypass code. |
| Token expires mid-suite | Session refresh fixture | Fast | Per check | Fixture validates the session before use and re-authenticates if expired. |
| Single test needs different user | `loginAs(role)` fixture | Moderate | Per call | Rare: prefer per-project roles. Use when a single test must compare two roles side by side. |
| API-first app (no login UI) | API login via `request.post()` | Fastest | Per test | No browser needed for auth. Hit the API directly and capture cookies. |
| CI with long-running suites | API login + session check | Fastest | Per worker | Combine API login speed with session refresh for reliability over long runs. |

### UI Login vs API Login vs Storage State

```
Need to test the login page itself?
├── Yes → UI login with LoginPage POM, no storageState
└── No → Do you have a login API endpoint?
    ├── Yes → API login in global setup, save storageState (fastest)
    └── No → UI login in global setup, save storageState
              └── Tokens expire quickly?
                  ├── Yes → Add session refresh fixture
                  └── No → Standard storageState reuse is fine
```

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Log in via UI before every test | Adds 2-5 seconds per test. A suite of 200 tests wastes 7-17 minutes just logging in. | Use `storageState` to skip login entirely. Log in once in global setup. |
| Share a single auth state file across parallel workers that mutate state | Race conditions: worker A changes the password while worker B is mid-test. | Use per-worker fixtures with `{ scope: 'worker' }` or per-worker test accounts. |
| Hardcode credentials in test files | Security risk. Credentials leak into version control and CI logs. | Use environment variables (`process.env.TEST_USER_PASSWORD`) and `.env` files. |
| Ignore token expiration | Tests fail intermittently with 401 errors after running for a while. | Add a session validity check in your auth fixture and re-authenticate when expired. |
| Hit real OAuth providers in CI | Flaky: provider rate limits, CAPTCHA, network issues. Slow. May violate ToS. | Mock the OAuth callback or use API session injection with a test-only endpoint. |
| Use `page.waitForTimeout(2000)` after login | Arbitrary delay. Too slow in fast environments, too short in slow ones. | `await page.waitForURL('/dashboard')` or `await expect(heading).toBeVisible()`. |
| Store `.auth/*.json` files in git | Tokens and cookies in version control. Security incident waiting to happen. | Add `.auth/` to `.gitignore`. Generate auth state in CI as part of the test run. |
| Create one "god" test account with all permissions | Cannot test role-based access control. Bugs in permission checks go undetected. | Create separate accounts per role (admin, user, viewer) with appropriate permissions. |
| Use `browser.newContext()` without `storageState` for authenticated tests | Every context starts unauthenticated. You end up re-logging in constantly. | Pass `storageState` when creating the context: `browser.newContext({ storageState: '.auth/user.json' })`. |
| Test MFA by disabling it everywhere | You never test the MFA flow. Real users hit MFA bugs you never catch. | Use TOTP generation from a shared secret for at least one test. Bypass MFA for the rest. |

## Troubleshooting

### Global setup fails with "Target page, context or browser has been closed"

**Cause**: The login page redirected unexpectedly, or the browser closed before `storageState()` was called. Common when the login URL requires HTTPS but your test server uses HTTP.

**Fix**:
- Add `await page.waitForURL()` after the login action to ensure navigation completed.
- Check that `baseURL` in your config matches the actual server URL and protocol.
- Add error handling to global setup with a meaningful error message:

```typescript
const response = await page.waitForResponse('**/api/auth/**');
if (!response.ok()) {
  throw new Error(`Login failed in global setup: ${response.status()} ${await response.text()}`);
}
```

### Tests fail with 401 Unauthorized after running for a while

**Cause**: The session token saved in `storageState` has expired. Short-lived JWTs (15-minute expiry) will not survive a long test suite.

**Fix**:
- Use the session refresh fixture pattern (see Session Refresh section).
- Increase token expiry in test environment configuration.
- Switch to API-based login in a worker-scoped fixture that re-authenticates per worker.

### `storageState` file is empty or contains no cookies

**Cause**: `storageState()` was called before the login response set cookies. The login may be async (POST returns, then a redirect sets the cookie).

**Fix**:
- Wait for the post-login page to load: `await page.waitForURL('/dashboard')`.
- Wait for a specific cookie: use `await context.cookies()` in a polling check.
- Verify cookies exist before saving:

```typescript
const cookies = await context.cookies();
if (cookies.length === 0) {
  throw new Error('No cookies found after login. Check that the login flow sets cookies.');
}
await context.storageState({ path: '.auth/user.json' });
```

### Different browsers get different cookies (cross-browser auth issues)

**Cause**: Some auth flows set cookies with `SameSite=Strict` or use browser-specific cookie behavior. Chromium and Firefox handle third-party cookies differently.

**Fix**:
- Generate separate auth state files per browser project.
- Check if your auth uses `SameSite=None; Secure` cookies that require HTTPS.
- In `playwright.config`, set separate `storageState` paths per project:

```typescript
projects: [
  {
    name: 'chromium',
    use: { ...devices['Desktop Chrome'], storageState: '.auth/chromium-user.json' },
  },
  {
    name: 'firefox',
    use: { ...devices['Desktop Firefox'], storageState: '.auth/firefox-user.json' },
  },
],
```

### Parallel tests interfere with each other's sessions

**Cause**: Multiple workers share the same test account and one worker's actions (logout, password change, session invalidation) affect others.

**Fix**:
- Use per-worker test accounts: `worker-${test.info().parallelIndex}@test.com`.
- Use the per-worker authentication fixture pattern (see Per-Worker Authentication section).
- Make tests idempotent: each test should work regardless of what other tests did.

### OAuth mock does not work — still redirects to real provider

**Cause**: `page.route()` was registered after the navigation that triggers the OAuth redirect, or the route pattern does not match the actual redirect URL.

**Fix**:
- Register route handlers before any navigation: call `page.route()` before `page.goto()`.
- Log the actual redirect URL to verify the pattern:

```typescript
page.on('request', (req) => {
  if (req.url().includes('oauth') || req.url().includes('accounts.google')) {
    console.log('OAuth request:', req.url());
  }
});
```

- Use a broad pattern first (`**accounts.google.com**`) then narrow it down.

## Related

- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) -- custom fixtures for auth setup and teardown
- [core/configuration.md](configuration.md) -- `storageState`, projects, and global setup configuration
- [ci/global-setup-teardown.md](../ci/global-setup-teardown.md) -- global setup patterns and project dependencies
- [core/network-mocking.md](network-mocking.md) -- route interception patterns used in OAuth mocking
- [core/api-testing.md](api-testing.md) -- API request context used in API-based login
- [core/flaky-tests.md](flaky-tests.md) -- diagnosing auth-related flakiness
- [core/auth-flows.md](auth-flows.md) -- complete recipes for specific auth providers (Auth0, Okta, Firebase)
