# Security Testing

> **When to use**: Validating your application's defenses against common web vulnerabilities — XSS, CSRF, insecure cookies, missing headers, authentication bypass, and sensitive data exposure. Playwright is not a replacement for dedicated security scanners, but it catches the most common issues as part of your E2E suite.
> **Prerequisites**: [core/assertions-and-waiting.md](assertions-and-waiting.md), [core/authentication.md](authentication.md)

## Quick Reference

```typescript
// Check security headers on every navigation
const response = await page.goto('/dashboard');
expect(response.headers()['content-security-policy']).toBeDefined();
expect(response.headers()['x-frame-options']).toBe('DENY');

// Verify cookie security flags
const cookies = await context.cookies();
const sessionCookie = cookies.find(c => c.name === 'session');
expect(sessionCookie.httpOnly).toBe(true);
expect(sessionCookie.secure).toBe(true);
expect(sessionCookie.sameSite).toBe('Strict');
```

## Patterns

### XSS Injection Testing

**Use when**: Verifying that user inputs are properly sanitized and rendered as text, not HTML.
**Avoid when**: You need comprehensive XSS scanning — use a dedicated tool like OWASP ZAP alongside Playwright.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

const XSS_PAYLOADS = [
  '<script>alert("xss")</script>',
  '<img src=x onerror=alert("xss")>',
  '"><script>alert("xss")</script>',
  "javascript:alert('xss')",
  '<svg onload=alert("xss")>',
  '{{constructor.constructor("alert(1)")()}}', // Template injection
];

test.describe('XSS protection', () => {
  for (const payload of XSS_PAYLOADS) {
    test(`input sanitizes: ${payload.slice(0, 40)}...`, async ({ page }) => {
      await page.goto('/profile/edit');

      // Inject the payload into a text field
      await page.getByLabel('Display name').fill(payload);
      await page.getByRole('button', { name: 'Save' }).click();

      // Verify the payload is rendered as text, not executed
      await page.goto('/profile');
      const displayName = page.getByTestId('display-name');
      await expect(displayName).toBeVisible();

      // The payload text should appear literally, not as HTML
      const innerHTML = await displayName.innerHTML();
      expect(innerHTML).not.toContain('<script');
      expect(innerHTML).not.toContain('onerror');
      expect(innerHTML).not.toContain('onload');

      // No dialog should have appeared (script execution)
      // If a dialog fires, the test will fail because it's unhandled
    });
  }
});

test('XSS via URL parameters is prevented', async ({ page }) => {
  const xssUrl = '/search?q=<script>alert("xss")</script>';
  await page.goto(xssUrl);

  // The search term should be displayed as text
  const searchInput = page.getByRole('textbox', { name: 'Search' });
  const value = await searchInput.inputValue();
  expect(value).not.toContain('<script');

  // Page should not have injected script tags
  const scriptCount = await page.locator('script:not([src])').count();
  const pageContent = await page.content();
  expect(pageContent).not.toContain('alert("xss")');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

const XSS_PAYLOADS = [
  '<script>alert("xss")</script>',
  '<img src=x onerror=alert("xss")>',
  '"><script>alert("xss")</script>',
  '<svg onload=alert("xss")>',
];

test.describe('XSS protection', () => {
  for (const payload of XSS_PAYLOADS) {
    test(`input sanitizes: ${payload.slice(0, 40)}...`, async ({ page }) => {
      await page.goto('/profile/edit');
      await page.getByLabel('Display name').fill(payload);
      await page.getByRole('button', { name: 'Save' }).click();

      await page.goto('/profile');
      const innerHTML = await page.getByTestId('display-name').innerHTML();
      expect(innerHTML).not.toContain('<script');
      expect(innerHTML).not.toContain('onerror');
    });
  }
});
```

### CSRF Token Verification

**Use when**: Ensuring state-changing requests include valid CSRF tokens and the server rejects requests without them.
**Avoid when**: Your API uses token-based auth (JWT) with no cookie-based sessions — CSRF is not applicable.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('form submissions include CSRF token', async ({ page }) => {
  await page.goto('/settings');

  // Verify the CSRF token is present in the form
  const csrfInput = page.locator('input[name="_csrf"], input[name="csrf_token"]');
  await expect(csrfInput).toBeAttached();
  const tokenValue = await csrfInput.inputValue();
  expect(tokenValue).toBeTruthy();
  expect(tokenValue.length).toBeGreaterThan(16);
});

test('server rejects requests without CSRF token', async ({ page, request }) => {
  // First, get a valid session by logging in through the UI
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  // Attempt a state-changing request without the CSRF token
  const cookies = await page.context().cookies();
  const response = await request.post('/api/settings', {
    headers: {
      Cookie: cookies.map(c => `${c.name}=${c.value}`).join('; '),
    },
    data: { theme: 'dark' }, // No CSRF token
  });

  // Server should reject it
  expect(response.status()).toBe(403);
});

test('CSRF token rotates per session', async ({ browser }) => {
  const context1 = await browser.newContext();
  const context2 = await browser.newContext();

  const page1 = await context1.newPage();
  const page2 = await context2.newPage();

  await page1.goto('/login');
  await page2.goto('/login');

  const token1 = await page1.locator('input[name="_csrf"]').inputValue();
  const token2 = await page2.locator('input[name="_csrf"]').inputValue();

  // Tokens should differ between sessions
  expect(token1).not.toBe(token2);

  await context1.close();
  await context2.close();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('form submissions include CSRF token', async ({ page }) => {
  await page.goto('/settings');

  const csrfInput = page.locator('input[name="_csrf"], input[name="csrf_token"]');
  await expect(csrfInput).toBeAttached();
  const tokenValue = await csrfInput.inputValue();
  expect(tokenValue).toBeTruthy();
  expect(tokenValue.length).toBeGreaterThan(16);
});

test('server rejects requests without CSRF token', async ({ page, request }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  const cookies = await page.context().cookies();
  const response = await request.post('/api/settings', {
    headers: {
      Cookie: cookies.map(c => `${c.name}=${c.value}`).join('; '),
    },
    data: { theme: 'dark' },
  });

  expect(response.status()).toBe(403);
});
```

### CSP Header Validation

**Use when**: Verifying Content Security Policy headers are present and correctly configured.
**Avoid when**: CSP is managed by infrastructure (CDN/WAF) tested separately.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('CSP headers are properly configured', async ({ page }) => {
  const response = await page.goto('/');
  const csp = response!.headers()['content-security-policy'];

  expect(csp).toBeDefined();
  expect(csp).toContain("default-src 'self'");
  expect(csp).not.toContain("'unsafe-inline'"); // Disallow inline scripts
  expect(csp).not.toContain("'unsafe-eval'");   // Disallow eval()
  expect(csp).toContain('script-src');
});

test('security headers are present on all pages', async ({ page }) => {
  const pagesToCheck = ['/', '/login', '/dashboard', '/api/health'];

  for (const url of pagesToCheck) {
    const response = await page.goto(url);
    const headers = response!.headers();

    expect(headers['x-content-type-options']).toBe('nosniff');
    expect(headers['x-frame-options']).toMatch(/DENY|SAMEORIGIN/);
    expect(headers['strict-transport-security']).toBeDefined();
    expect(headers['referrer-policy']).toBeDefined();
    expect(headers['x-xss-protection']).toBeUndefined(); // Deprecated, should not be set
  }
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('CSP headers are properly configured', async ({ page }) => {
  const response = await page.goto('/');
  const csp = response.headers()['content-security-policy'];

  expect(csp).toBeDefined();
  expect(csp).toContain("default-src 'self'");
  expect(csp).not.toContain("'unsafe-inline'");
  expect(csp).not.toContain("'unsafe-eval'");
});

test('security headers are present on all pages', async ({ page }) => {
  const pagesToCheck = ['/', '/login', '/dashboard'];

  for (const url of pagesToCheck) {
    const response = await page.goto(url);
    const headers = response.headers();

    expect(headers['x-content-type-options']).toBe('nosniff');
    expect(headers['x-frame-options']).toMatch(/DENY|SAMEORIGIN/);
    expect(headers['strict-transport-security']).toBeDefined();
  }
});
```

### Cookie Security Flags

**Use when**: Verifying session cookies and auth cookies have proper security attributes.
**Avoid when**: Your app is fully stateless with no cookies.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('session cookie has correct security flags', async ({ page, context }) => {
  // Log in to create a session cookie
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  const cookies = await context.cookies();

  // Check session cookie
  const session = cookies.find(c => c.name === 'session' || c.name === 'sid');
  expect(session).toBeDefined();
  expect(session!.httpOnly).toBe(true);   // Not accessible via JavaScript
  expect(session!.secure).toBe(true);     // Only sent over HTTPS
  expect(session!.sameSite).toBe('Strict'); // Or 'Lax' at minimum

  // Session cookie should not have an excessive expiry
  if (session!.expires !== -1) {
    const maxAge = session!.expires - Date.now() / 1000;
    expect(maxAge).toBeLessThan(86400 * 30); // No more than 30 days
  }
});

test('sensitive cookies are not exposed to JavaScript', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  // document.cookie should NOT contain HttpOnly cookies
  const jsCookies = await page.evaluate(() => document.cookie);
  expect(jsCookies).not.toContain('session');
  expect(jsCookies).not.toContain('sid');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('session cookie has correct security flags', async ({ page, context }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  const cookies = await context.cookies();
  const session = cookies.find(c => c.name === 'session' || c.name === 'sid');

  expect(session).toBeDefined();
  expect(session.httpOnly).toBe(true);
  expect(session.secure).toBe(true);
  expect(session.sameSite).toBe('Strict');
});
```

### Authentication Bypass Testing

**Use when**: Ensuring protected routes redirect unauthenticated users and that session invalidation works.
**Avoid when**: Auth is tested through dedicated API tests that cover these cases already.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('unauthenticated user cannot access protected routes', async ({ page }) => {
  const protectedRoutes = ['/dashboard', '/settings', '/admin', '/api/users'];

  for (const route of protectedRoutes) {
    const response = await page.goto(route);

    // Should redirect to login or return 401/403
    const isRedirected = page.url().includes('/login');
    const isBlocked = response!.status() === 401 || response!.status() === 403;
    expect(isRedirected || isBlocked).toBe(true);
  }
});

test('session is invalidated after logout', async ({ page, context }) => {
  // Log in
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  // Capture session cookie
  const cookiesBefore = await context.cookies();
  const sessionBefore = cookiesBefore.find(c => c.name === 'session');

  // Log out
  await page.getByRole('button', { name: 'Log out' }).click();
  await page.waitForURL('/login');

  // Verify session cookie is cleared
  const cookiesAfter = await context.cookies();
  const sessionAfter = cookiesAfter.find(c => c.name === 'session');
  expect(sessionAfter).toBeUndefined();

  // Attempting to access protected route should fail
  await page.goto('/dashboard');
  expect(page.url()).toContain('/login');
});

test('expired session redirects to login', async ({ page, context }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  // Manually expire the session cookie
  await context.clearCookies();

  // Next navigation should redirect to login
  await page.goto('/dashboard');
  expect(page.url()).toContain('/login');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('unauthenticated user cannot access protected routes', async ({ page }) => {
  const protectedRoutes = ['/dashboard', '/settings', '/admin'];

  for (const route of protectedRoutes) {
    await page.goto(route);
    expect(page.url()).toContain('/login');
  }
});

test('session is invalidated after logout', async ({ page, context }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  await page.getByRole('button', { name: 'Log out' }).click();
  await page.waitForURL('/login');

  const cookies = await context.cookies();
  const session = cookies.find(c => c.name === 'session');
  expect(session).toBeUndefined();
});
```

### HTTPS Redirect and Sensitive Data Exposure

**Use when**: Verifying that HTTP requests are redirected to HTTPS and that sensitive data is not leaked in URLs, headers, or client-side storage.
**Avoid when**: Running against `localhost` where HTTPS is not configured.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('HTTP redirects to HTTPS', async ({ request }) => {
  // Use the API request context to follow redirects
  const response = await request.get('http://your-app.com/', {
    maxRedirects: 0, // Don't follow — inspect the redirect
  });
  expect(response.status()).toBe(301);
  expect(response.headers()['location']).toMatch(/^https:\/\//);
});

test('HSTS header is set', async ({ page }) => {
  const response = await page.goto('/');
  const hsts = response!.headers()['strict-transport-security'];
  expect(hsts).toBeDefined();
  expect(hsts).toContain('max-age=');

  // Extract max-age value and verify it's at least 1 year
  const maxAge = parseInt(hsts!.match(/max-age=(\d+)/)?.[1] || '0');
  expect(maxAge).toBeGreaterThanOrEqual(31536000);
});

test('sensitive data is not in URL parameters', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  // Password should never appear in URL
  expect(page.url()).not.toContain('password');
  expect(page.url()).not.toContain('token');
  expect(page.url()).not.toContain('secret');
});

test('sensitive data is not in localStorage', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  const storageData = await page.evaluate(() => {
    const data: Record<string, string> = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)!;
      data[key] = localStorage.getItem(key)!;
    }
    return JSON.stringify(data);
  });

  expect(storageData).not.toContain('password');
  expect(storageData.toLowerCase()).not.toContain('secret');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('sensitive data is not in localStorage', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  const storageData = await page.evaluate(() => {
    const data = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      data[key] = localStorage.getItem(key);
    }
    return JSON.stringify(data);
  });

  expect(storageData).not.toContain('password');
  expect(storageData.toLowerCase()).not.toContain('secret');
});
```

### Session Fixation Prevention

**Use when**: Ensuring the session ID changes after authentication to prevent session fixation attacks.
**Avoid when**: Using stateless token auth (JWT) with no server-side sessions.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('session ID changes after login', async ({ page, context }) => {
  await page.goto('/login');

  // Capture pre-login session identifier
  const cookiesBefore = await context.cookies();
  const preLoginSession = cookiesBefore.find(c => c.name === 'session');
  const preLoginValue = preLoginSession?.value;

  // Log in
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  // Session ID must change after authentication
  const cookiesAfter = await context.cookies();
  const postLoginSession = cookiesAfter.find(c => c.name === 'session');
  expect(postLoginSession).toBeDefined();

  if (preLoginValue) {
    expect(postLoginSession!.value).not.toBe(preLoginValue);
  }
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('session ID changes after login', async ({ page, context }) => {
  await page.goto('/login');

  const cookiesBefore = await context.cookies();
  const preLoginSession = cookiesBefore.find(c => c.name === 'session');
  const preLoginValue = preLoginSession?.value;

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  const cookiesAfter = await context.cookies();
  const postLoginSession = cookiesAfter.find(c => c.name === 'session');
  expect(postLoginSession).toBeDefined();

  if (preLoginValue) {
    expect(postLoginSession.value).not.toBe(preLoginValue);
  }
});
```

## Decision Guide

| Vulnerability | Playwright Test Approach | Confidence Level |
|---|---|---|
| Reflected XSS | Inject payloads in inputs and URL params, assert no script execution | Medium -- covers common cases, not exhaustive |
| Stored XSS | Inject payload, reload page, assert sanitized output | Medium -- catches rendering-level issues |
| CSRF | Verify token presence, test rejection without token | High -- directly tests the mechanism |
| Insecure cookies | Assert `httpOnly`, `secure`, `sameSite` flags | High -- deterministic check |
| Missing security headers | Assert header presence and values | High -- deterministic check |
| Auth bypass | Navigate to protected routes without auth | High -- tests the redirect/block mechanism |
| Session fixation | Compare session IDs before and after login | High -- directly verifiable |
| Sensitive data exposure | Check URLs, localStorage, response bodies for secrets | Medium -- catches obvious leaks |
| HTTPS enforcement | Verify redirect and HSTS header | High -- deterministic check |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Only testing the "happy path" login | Misses bypass vectors | Test unauthenticated access, expired sessions, tampered tokens |
| Checking `SameSite` only on one cookie | Other cookies may leak session info | Check all cookies that contain session data |
| Ignoring CSP on API endpoints | APIs can serve HTML on error pages | Check headers on API routes too |
| Testing security only in development | Dev servers often have relaxed security | Run security tests against staging with production-like config |
| Using `page.waitForTimeout` after login | Hides timing-based auth issues | Use `page.waitForURL` or assertion-based waiting |
| Hardcoding test credentials in test files | Credentials leak into version control | Use environment variables or a secrets manager |
| Skipping HTTPS tests because "it works locally" | HTTP-only local dev hides HTTPS issues | Test HTTPS redirect against staging or use `--ignore-https-errors` carefully |
| Treating Playwright as a full security scanner | Playwright tests are not penetration tests | Use Playwright for regression checks; pair with OWASP ZAP, Burp Suite, or Snyk for deep scanning |

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| CSP header missing in test but present in production | Dev server does not set CSP | Run security tests against staging with production config |
| Cookie `secure` flag is `false` | Testing over HTTP (localhost) | Test against HTTPS staging, or verify the flag is set conditionally for production |
| CSRF test passes without token | CSRF protection disabled in test environment | Enable CSRF in test environment or run against staging |
| XSS payload does not execute but test passes | Framework auto-escapes by default | Still test -- the test confirms the protection works; add edge cases for raw HTML rendering |
| `context.cookies()` returns empty | Cookies set on a different domain or path | Pass the specific URL to `context.cookies('https://your-app.com')` |
| HSTS header check fails on localhost | HSTS requires HTTPS with valid certs | Skip HSTS tests for localhost, run against staging |
| Session cookie not found by name | Cookie name differs across environments | Search by pattern: `cookies.find(c => c.name.includes('sess'))` |

## Related

- [core/authentication.md](authentication.md) -- login flows and auth state management
- [core/network-mocking.md](network-mocking.md) -- intercepting requests for security testing
- [core/configuration.md](configuration.md) -- `ignoreHTTPSErrors` and base URL configuration
- [core/third-party-integrations.md](third-party-integrations.md) -- testing OAuth and third-party auth providers
- [ci/ci-github-actions.md](../ci/ci-github-actions.md) -- running security tests in CI pipelines
