# Authentication Flow Recipes

> **When to use**: You need to test login, signup, logout, session management, or any authentication-related user flow.

---

## Recipe 1: Basic Login

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('logs in with valid credentials', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('SecurePass123!');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Wait for navigation to complete after login
  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByText('Welcome, user@example.com')).toBeVisible();
});

test('shows error for invalid credentials', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('WrongPassword');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByRole('alert')).toContainText('Invalid email or password');
  // Should remain on login page
  await expect(page).toHaveURL('/login');
});

test('shows validation errors for empty fields', async ({ page }) => {
  await page.goto('/login');

  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByText('Email is required')).toBeVisible();
  await expect(page.getByText('Password is required')).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('logs in with valid credentials', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('SecurePass123!');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByText('Welcome, user@example.com')).toBeVisible();
});

test('shows error for invalid credentials', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('WrongPassword');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByRole('alert')).toContainText('Invalid email or password');
  await expect(page).toHaveURL('/login');
});

test('shows validation errors for empty fields', async ({ page }) => {
  await page.goto('/login');

  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByText('Email is required')).toBeVisible();
  await expect(page.getByText('Password is required')).toBeVisible();
});
```

---

## Recipe 2: Login with "Remember Me"

### Complete Example

**TypeScript**

```typescript
import { test, expect, type BrowserContext } from '@playwright/test';

test('remember me persists session across browser restarts', async ({ browser }) => {
  // First session: log in with "remember me" checked
  const context1 = await browser.newContext();
  const page1 = await context1.newPage();

  await page1.goto('/login');
  await page1.getByLabel('Email').fill('user@example.com');
  await page1.getByLabel('Password').fill('SecurePass123!');
  await page1.getByLabel('Remember me').check();
  await page1.getByRole('button', { name: 'Sign in' }).click();

  await expect(page1).toHaveURL('/dashboard');

  // Save storage state (cookies + localStorage)
  const storageState = await context1.storageState();
  await context1.close();

  // Second session: restore state to simulate browser restart
  const context2 = await browser.newContext({ storageState });
  const page2 = await context2.newPage();

  await page2.goto('/dashboard');

  // Should still be logged in without re-authenticating
  await expect(page2).toHaveURL('/dashboard');
  await expect(page2.getByText('Welcome, user@example.com')).toBeVisible();

  await context2.close();
});

test('no remember me does not persist session', async ({ browser }) => {
  const context1 = await browser.newContext();
  const page1 = await context1.newPage();

  await page1.goto('/login');
  await page1.getByLabel('Email').fill('user@example.com');
  await page1.getByLabel('Password').fill('SecurePass123!');
  // Explicitly leave "Remember me" unchecked
  await expect(page1.getByLabel('Remember me')).not.toBeChecked();
  await page1.getByRole('button', { name: 'Sign in' }).click();

  await expect(page1).toHaveURL('/dashboard');

  // Capture only cookies (not sessionStorage) to simulate new tab/window
  const cookies = await context1.cookies();
  await context1.close();

  // New context with only persistent cookies (session cookies are excluded)
  const persistentCookies = cookies.filter(c => c.expires > 0);
  const context2 = await browser.newContext();
  await context2.addCookies(persistentCookies);
  const page2 = await context2.newPage();

  await page2.goto('/dashboard');

  // Should redirect to login since session was not persisted
  await expect(page2).toHaveURL(/\/login/);

  await context2.close();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('remember me persists session across browser restarts', async ({ browser }) => {
  const context1 = await browser.newContext();
  const page1 = await context1.newPage();

  await page1.goto('/login');
  await page1.getByLabel('Email').fill('user@example.com');
  await page1.getByLabel('Password').fill('SecurePass123!');
  await page1.getByLabel('Remember me').check();
  await page1.getByRole('button', { name: 'Sign in' }).click();

  await expect(page1).toHaveURL('/dashboard');

  const storageState = await context1.storageState();
  await context1.close();

  const context2 = await browser.newContext({ storageState });
  const page2 = await context2.newPage();

  await page2.goto('/dashboard');

  await expect(page2).toHaveURL('/dashboard');
  await expect(page2.getByText('Welcome, user@example.com')).toBeVisible();

  await context2.close();
});
```

---

## Recipe 3: Signup with Email Verification (Mocked)

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('completes signup flow with mocked email verification', async ({ page }) => {
  // Intercept the verification email API so we can capture the token
  let verificationToken = '';
  await page.route('**/api/auth/send-verification', async (route) => {
    // Let the request go through to the server
    const response = await route.fetch();
    const body = await response.json();

    // Capture the token from the API response (test environments expose this)
    verificationToken = body.verificationToken;

    await route.fulfill({ response });
  });

  // Step 1: Fill out signup form
  await page.goto('/signup');

  await page.getByLabel('Full name').fill('Jane Tester');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Password', { exact: true }).fill('SecurePass123!');
  await page.getByLabel('Confirm password').fill('SecurePass123!');
  await page.getByLabel('I agree to the Terms of Service').check();
  await page.getByRole('button', { name: 'Create account' }).click();

  // Step 2: Verify "check your email" screen appears
  await expect(page.getByText('Check your email')).toBeVisible();
  await expect(page.getByText('jane@example.com')).toBeVisible();

  // Step 3: Navigate directly to verification URL using captured token
  expect(verificationToken).toBeTruthy();
  await page.goto(`/verify-email?token=${verificationToken}`);

  // Step 4: Verify account is now active
  await expect(page.getByText('Email verified successfully')).toBeVisible();
  await expect(page).toHaveURL('/login');

  // Step 5: Log in with the new account
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Password').fill('SecurePass123!');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByText('Welcome, Jane Tester')).toBeVisible();
});

test('signup with fully mocked email API (no server dependency)', async ({ page }) => {
  const fakeToken = 'test-verification-token-12345';

  // Mock the signup API endpoint
  await page.route('**/api/auth/signup', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        message: 'Verification email sent',
        verificationToken: fakeToken,
      }),
    });
  });

  // Mock the verification endpoint
  await page.route(`**/api/auth/verify-email?token=${fakeToken}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ message: 'Email verified', redirectTo: '/login' }),
    });
  });

  await page.goto('/signup');

  await page.getByLabel('Full name').fill('Jane Tester');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Password', { exact: true }).fill('SecurePass123!');
  await page.getByLabel('Confirm password').fill('SecurePass123!');
  await page.getByLabel('I agree to the Terms of Service').check();
  await page.getByRole('button', { name: 'Create account' }).click();

  await expect(page.getByText('Check your email')).toBeVisible();

  // Simulate clicking the verification link from the email
  await page.goto(`/verify-email?token=${fakeToken}`);

  await expect(page.getByText('Email verified successfully')).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('completes signup flow with mocked email verification', async ({ page }) => {
  let verificationToken = '';
  await page.route('**/api/auth/send-verification', async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    verificationToken = body.verificationToken;
    await route.fulfill({ response });
  });

  await page.goto('/signup');

  await page.getByLabel('Full name').fill('Jane Tester');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Password', { exact: true }).fill('SecurePass123!');
  await page.getByLabel('Confirm password').fill('SecurePass123!');
  await page.getByLabel('I agree to the Terms of Service').check();
  await page.getByRole('button', { name: 'Create account' }).click();

  await expect(page.getByText('Check your email')).toBeVisible();

  expect(verificationToken).toBeTruthy();
  await page.goto(`/verify-email?token=${verificationToken}`);

  await expect(page.getByText('Email verified successfully')).toBeVisible();
  await expect(page).toHaveURL('/login');
});
```

---

## Recipe 4: Password Reset Flow

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('completes password reset flow', async ({ page }) => {
  let resetToken = '';

  // Intercept the password reset API to capture the reset token
  await page.route('**/api/auth/forgot-password', async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    resetToken = body.resetToken;
    await route.fulfill({ response });
  });

  // Step 1: Request password reset
  await page.goto('/forgot-password');

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByRole('button', { name: 'Send reset link' }).click();

  await expect(page.getByText('Reset link sent')).toBeVisible();
  await expect(page.getByText('user@example.com')).toBeVisible();

  // Step 2: Navigate to the reset page with token
  expect(resetToken).toBeTruthy();
  await page.goto(`/reset-password?token=${resetToken}`);

  // Step 3: Set new password
  await page.getByLabel('New password', { exact: true }).fill('NewSecurePass456!');
  await page.getByLabel('Confirm new password').fill('NewSecurePass456!');
  await page.getByRole('button', { name: 'Reset password' }).click();

  await expect(page.getByText('Password reset successfully')).toBeVisible();

  // Step 4: Log in with new password
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('NewSecurePass456!');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page).toHaveURL('/dashboard');
});

test('password reset with expired token shows error', async ({ page }) => {
  await page.goto('/reset-password?token=expired-token-123');

  await page.getByLabel('New password', { exact: true }).fill('NewSecurePass456!');
  await page.getByLabel('Confirm new password').fill('NewSecurePass456!');
  await page.getByRole('button', { name: 'Reset password' }).click();

  await expect(page.getByRole('alert')).toContainText(
    /token has expired|link is no longer valid/i
  );
  await expect(page.getByRole('link', { name: 'Request a new reset link' })).toBeVisible();
});

test('password reset enforces password strength requirements', async ({ page }) => {
  await page.goto('/reset-password?token=valid-token');

  // Try a weak password
  await page.getByLabel('New password', { exact: true }).fill('123');
  await page.getByLabel('Confirm new password').fill('123');
  await page.getByRole('button', { name: 'Reset password' }).click();

  await expect(page.getByText(/at least 8 characters/i)).toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('completes password reset flow', async ({ page }) => {
  let resetToken = '';

  await page.route('**/api/auth/forgot-password', async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    resetToken = body.resetToken;
    await route.fulfill({ response });
  });

  await page.goto('/forgot-password');

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByRole('button', { name: 'Send reset link' }).click();

  await expect(page.getByText('Reset link sent')).toBeVisible();

  expect(resetToken).toBeTruthy();
  await page.goto(`/reset-password?token=${resetToken}`);

  await page.getByLabel('New password', { exact: true }).fill('NewSecurePass456!');
  await page.getByLabel('Confirm new password').fill('NewSecurePass456!');
  await page.getByRole('button', { name: 'Reset password' }).click();

  await expect(page.getByText('Password reset successfully')).toBeVisible();

  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('NewSecurePass456!');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page).toHaveURL('/dashboard');
});
```

---

## Recipe 5: OAuth Login (Mocked Callback)

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('logs in via mocked Google OAuth callback', async ({ page }) => {
  // Intercept the OAuth redirect to Google and simulate the callback
  await page.route('**/accounts.google.com/**', async (route) => {
    // Instead of actually going to Google, redirect back to our callback URL
    // with a mock authorization code
    const callbackUrl = new URL('/auth/callback/google', 'http://localhost:3000');
    callbackUrl.searchParams.set('code', 'mock-auth-code-12345');
    callbackUrl.searchParams.set('state', route.request().url().match(/state=([^&]+)/)?.[1] || '');

    await route.fulfill({
      status: 302,
      headers: { location: callbackUrl.toString() },
    });
  });

  // Mock the token exchange on our backend
  await page.route('**/api/auth/callback/google**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        user: {
          id: '1',
          email: 'googleuser@gmail.com',
          name: 'Google User',
          avatar: 'https://example.com/avatar.jpg',
        },
        token: 'mock-jwt-token',
      }),
    });
  });

  await page.goto('/login');

  // Click the OAuth button
  await page.getByRole('button', { name: /Sign in with Google/i }).click();

  // After the mocked OAuth flow, we should land on the dashboard
  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByText('Google User')).toBeVisible();
});

test('handles OAuth login failure gracefully', async ({ page }) => {
  // Simulate OAuth provider returning an error
  await page.route('**/accounts.google.com/**', async (route) => {
    const callbackUrl = new URL('/auth/callback/google', 'http://localhost:3000');
    callbackUrl.searchParams.set('error', 'access_denied');
    callbackUrl.searchParams.set('error_description', 'User denied access');

    await route.fulfill({
      status: 302,
      headers: { location: callbackUrl.toString() },
    });
  });

  await page.goto('/login');
  await page.getByRole('button', { name: /Sign in with Google/i }).click();

  await expect(page.getByRole('alert')).toContainText(/authentication failed|access denied/i);
  await expect(page).toHaveURL(/\/login/);
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('logs in via mocked Google OAuth callback', async ({ page }) => {
  await page.route('**/accounts.google.com/**', async (route) => {
    const callbackUrl = new URL('/auth/callback/google', 'http://localhost:3000');
    callbackUrl.searchParams.set('code', 'mock-auth-code-12345');
    callbackUrl.searchParams.set('state', route.request().url().match(/state=([^&]+)/)?.[1] || '');

    await route.fulfill({
      status: 302,
      headers: { location: callbackUrl.toString() },
    });
  });

  await page.route('**/api/auth/callback/google**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        user: { id: '1', email: 'googleuser@gmail.com', name: 'Google User' },
        token: 'mock-jwt-token',
      }),
    });
  });

  await page.goto('/login');
  await page.getByRole('button', { name: /Sign in with Google/i }).click();

  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByText('Google User')).toBeVisible();
});
```

---

## Recipe 6: Role-Based Access Testing

### Complete Example

**TypeScript**

```typescript
import { test, expect, type Page } from '@playwright/test';
import path from 'path';

// Store auth state for each role in separate files
const authDir = path.resolve(__dirname, '../.auth');

// Setup: create auth state files for each role (run in globalSetup or auth.setup)
// This pattern uses Playwright's storage state for efficient role switching
const roles = ['admin', 'editor', 'viewer'] as const;
type Role = typeof roles[number];

function authFile(role: Role): string {
  return path.join(authDir, `${role}.json`);
}

// Auth setup project — runs before all tests
test.describe('auth setup', () => {
  const credentials: Record<Role, { email: string; password: string }> = {
    admin: { email: 'admin@example.com', password: 'AdminPass123!' },
    editor: { email: 'editor@example.com', password: 'EditorPass123!' },
    viewer: { email: 'viewer@example.com', password: 'ViewerPass123!' },
  };

  for (const role of roles) {
    test(`authenticate as ${role}`, async ({ page }) => {
      await page.goto('/login');
      await page.getByLabel('Email').fill(credentials[role].email);
      await page.getByLabel('Password').fill(credentials[role].password);
      await page.getByRole('button', { name: 'Sign in' }).click();
      await expect(page).toHaveURL('/dashboard');

      await page.context().storageState({ path: authFile(role) });
    });
  }
});

// Admin tests
test.describe('admin access', () => {
  test.use({ storageState: authFile('admin') });

  test('admin can access user management', async ({ page }) => {
    await page.goto('/admin/users');
    await expect(page).toHaveURL('/admin/users');
    await expect(page.getByRole('heading', { name: 'User Management' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Add user' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Delete' }).first()).toBeVisible();
  });

  test('admin can access system settings', async ({ page }) => {
    await page.goto('/admin/settings');
    await expect(page).toHaveURL('/admin/settings');
    await expect(page.getByRole('heading', { name: 'System Settings' })).toBeVisible();
  });
});

// Editor tests
test.describe('editor access', () => {
  test.use({ storageState: authFile('editor') });

  test('editor can create and edit content', async ({ page }) => {
    await page.goto('/content');
    await expect(page.getByRole('button', { name: 'New post' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Edit' }).first()).toBeVisible();
  });

  test('editor cannot access admin area', async ({ page }) => {
    await page.goto('/admin/users');
    // Should be redirected or shown forbidden
    await expect(page).toHaveURL(/\/(403|dashboard|login)/);
  });
});

// Viewer tests
test.describe('viewer access', () => {
  test.use({ storageState: authFile('viewer') });

  test('viewer can read content', async ({ page }) => {
    await page.goto('/content');
    await expect(page.getByRole('article').first()).toBeVisible();
  });

  test('viewer cannot create content', async ({ page }) => {
    await page.goto('/content');
    await expect(page.getByRole('button', { name: 'New post' })).not.toBeVisible();
  });

  test('viewer cannot access admin area', async ({ page }) => {
    await page.goto('/admin/users');
    await expect(page).toHaveURL(/\/(403|dashboard|login)/);
  });
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');
const path = require('path');

const authDir = path.resolve(__dirname, '../.auth');

function authFile(role) {
  return path.join(authDir, `${role}.json`);
}

// Admin tests
test.describe('admin access', () => {
  test.use({ storageState: authFile('admin') });

  test('admin can access user management', async ({ page }) => {
    await page.goto('/admin/users');
    await expect(page).toHaveURL('/admin/users');
    await expect(page.getByRole('heading', { name: 'User Management' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Add user' })).toBeVisible();
  });

  test('admin can access system settings', async ({ page }) => {
    await page.goto('/admin/settings');
    await expect(page).toHaveURL('/admin/settings');
  });
});

// Viewer tests
test.describe('viewer access', () => {
  test.use({ storageState: authFile('viewer') });

  test('viewer cannot create content', async ({ page }) => {
    await page.goto('/content');
    await expect(page.getByRole('button', { name: 'New post' })).not.toBeVisible();
  });

  test('viewer cannot access admin area', async ({ page }) => {
    await page.goto('/admin/users');
    await expect(page).toHaveURL(/\/(403|dashboard|login)/);
  });
});
```

---

## Recipe 7: Session Timeout Handling

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

test('redirects to login after session timeout', async ({ page, context }) => {
  // Log in first
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('SecurePass123!');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL('/dashboard');

  // Simulate session expiration by clearing the session cookie
  const cookies = await context.cookies();
  const sessionCookie = cookies.find(
    (c) => c.name === 'session' || c.name === 'sid' || c.name === 'connect.sid'
  );

  if (sessionCookie) {
    await context.clearCookies({ name: sessionCookie.name });
  }

  // Try to navigate to a protected page
  await page.goto('/settings');

  // Should redirect to login with a return URL
  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByText(/session.*expired|please.*log in again/i)).toBeVisible();
});

test('shows session expiry warning before timeout', async ({ page }) => {
  // Mock the session check endpoint to return "expiring soon"
  await page.route('**/api/auth/session', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        valid: true,
        expiresIn: 120, // 2 minutes remaining
      }),
    });
  });

  await page.goto('/dashboard');

  // The app should show a warning when session is about to expire
  await expect(page.getByText(/session.*expir/i)).toBeVisible({ timeout: 10000 });
  await expect(page.getByRole('button', { name: /extend|stay logged in/i })).toBeVisible();
});

test('extends session when user clicks extend', async ({ page }) => {
  let sessionExtended = false;

  await page.route('**/api/auth/session', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ valid: true, expiresIn: 120 }),
    });
  });

  await page.route('**/api/auth/refresh', async (route) => {
    sessionExtended = true;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ valid: true, expiresIn: 3600 }),
    });
  });

  await page.goto('/dashboard');

  await expect(page.getByRole('button', { name: /extend|stay logged in/i })).toBeVisible({
    timeout: 10000,
  });
  await page.getByRole('button', { name: /extend|stay logged in/i }).click();

  expect(sessionExtended).toBe(true);
  await expect(page.getByText(/session.*expir/i)).not.toBeVisible();
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test('redirects to login after session timeout', async ({ page, context }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('SecurePass123!');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL('/dashboard');

  const cookies = await context.cookies();
  const sessionCookie = cookies.find(
    (c) => c.name === 'session' || c.name === 'sid' || c.name === 'connect.sid'
  );

  if (sessionCookie) {
    await context.clearCookies({ name: sessionCookie.name });
  }

  await page.goto('/settings');

  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByText(/session.*expired|please.*log in again/i)).toBeVisible();
});
```

---

## Recipe 8: Logout

### Complete Example

**TypeScript**

```typescript
import { test, expect } from '@playwright/test';

// Use a logged-in state
test.use({ storageState: '.auth/user.json' });

test('logs out and redirects to login page', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByText('Welcome')).toBeVisible();

  // Open user menu and click logout
  await page.getByRole('button', { name: /user menu|account|profile/i }).click();
  await page.getByRole('menuitem', { name: 'Log out' }).click();

  // Should redirect to login
  await expect(page).toHaveURL('/login');

  // Verify we can no longer access protected pages
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/\/login/);
});

test('logout clears all session data', async ({ page, context }) => {
  await page.goto('/dashboard');

  await page.getByRole('button', { name: /user menu|account|profile/i }).click();
  await page.getByRole('menuitem', { name: 'Log out' }).click();

  await expect(page).toHaveURL('/login');

  // Verify cookies are cleared
  const cookies = await context.cookies();
  const sessionCookies = cookies.filter(
    (c) => c.name === 'session' || c.name === 'sid' || c.name === 'token'
  );
  expect(sessionCookies).toHaveLength(0);

  // Verify localStorage is cleared
  const token = await page.evaluate(() => localStorage.getItem('authToken'));
  expect(token).toBeNull();
});

test('logout from all devices', async ({ page }) => {
  let logoutAllCalled = false;

  await page.route('**/api/auth/logout-all', async (route) => {
    logoutAllCalled = true;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ message: 'Logged out from all devices' }),
    });
  });

  await page.goto('/settings/security');

  await page.getByRole('button', { name: 'Log out of all devices' }).click();

  // Confirm the action in the dialog
  await page.getByRole('dialog').getByRole('button', { name: 'Confirm' }).click();

  expect(logoutAllCalled).toBe(true);
  await expect(page).toHaveURL(/\/login/);
});
```

**JavaScript**

```javascript
const { test, expect } = require('@playwright/test');

test.use({ storageState: '.auth/user.json' });

test('logs out and redirects to login page', async ({ page }) => {
  await page.goto('/dashboard');

  await page.getByRole('button', { name: /user menu|account|profile/i }).click();
  await page.getByRole('menuitem', { name: 'Log out' }).click();

  await expect(page).toHaveURL('/login');

  await page.goto('/dashboard');
  await expect(page).toHaveURL(/\/login/);
});

test('logout clears all session data', async ({ page, context }) => {
  await page.goto('/dashboard');

  await page.getByRole('button', { name: /user menu|account|profile/i }).click();
  await page.getByRole('menuitem', { name: 'Log out' }).click();

  await expect(page).toHaveURL('/login');

  const cookies = await context.cookies();
  const sessionCookies = cookies.filter(
    (c) => c.name === 'session' || c.name === 'sid' || c.name === 'token'
  );
  expect(sessionCookies).toHaveLength(0);
});
```

---

## Variations

### Login via API for Speed

Skip the UI for login when testing non-auth features. Use `request` context to get tokens faster.

**TypeScript**

```typescript
import { test as setup } from '@playwright/test';

setup('authenticate via API', async ({ request }) => {
  const response = await request.post('/api/auth/login', {
    data: {
      email: 'user@example.com',
      password: 'SecurePass123!',
    },
  });

  expect(response.ok()).toBeTruthy();

  // Save the auth state
  await request.storageState({ path: '.auth/user.json' });
});
```

### Multi-Factor Authentication

```typescript
test('logs in with MFA (TOTP)', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('mfa-user@example.com');
  await page.getByLabel('Password').fill('SecurePass123!');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // MFA challenge screen appears
  await expect(page.getByText('Enter verification code')).toBeVisible();

  // In test environments, use a predictable TOTP code or mock the verification
  await page.route('**/api/auth/verify-mfa', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, token: 'jwt-token' }),
    });
  });

  await page.getByLabel('Verification code').fill('123456');
  await page.getByRole('button', { name: 'Verify' }).click();

  await expect(page).toHaveURL('/dashboard');
});
```

### Testing Auth with Different Browser Contexts

```typescript
test('two users interact simultaneously', async ({ browser }) => {
  const adminContext = await browser.newContext({
    storageState: '.auth/admin.json',
  });
  const userContext = await browser.newContext({
    storageState: '.auth/viewer.json',
  });

  const adminPage = await adminContext.newPage();
  const userPage = await userContext.newPage();

  // Admin bans a user
  await adminPage.goto('/admin/users');
  await adminPage.getByRole('row', { name: 'viewer@example.com' })
    .getByRole('button', { name: 'Ban' }).click();
  await adminPage.getByRole('dialog').getByRole('button', { name: 'Confirm' }).click();

  // User tries to navigate and should be blocked
  await userPage.goto('/dashboard');
  await expect(userPage.getByText(/account.*banned|access.*revoked/i)).toBeVisible();

  await adminContext.close();
  await userContext.close();
});
```

---

## Tips

1. **Use `storageState` for reusable auth**. Run login once in a setup project, save the state to a JSON file, and reuse it across all tests. This dramatically speeds up your test suite since you only log in once per role.

2. **Never hard-code credentials in test files**. Use environment variables or a `.env` file loaded via `dotenv`. In `playwright.config.ts`, set `process.env` values or use the `env` option in `use`.

3. **Prefer API-based login for non-auth tests**. Only test the login UI in your auth-specific tests. For everything else, authenticate via the API or by restoring `storageState`. This makes tests faster and less brittle.

4. **Test the negative paths too**. Invalid credentials, expired tokens, locked accounts, rate limiting. These are the scenarios users actually encounter in production and are frequently undertested.

5. **Set a shorter session timeout in your test environment**. If your app has a 30-minute session timeout, configure it to 30 seconds in the test environment so you can test timeout behavior without slow tests.

---

## Related

- [Playwright Authentication Docs](https://playwright.dev/docs/auth)
- `patterns/page-objects.md` -- Encapsulate login flows in page objects
- `foundations/assertions.md` -- Assertion patterns for auth states
- `recipes/crud-testing.md` -- Test CRUD operations once authenticated
