# Third-Party Integrations

> **When to use**: Testing your application's interaction with external services -- OAuth providers, payment gateways, analytics, chat widgets, maps, social login, and CAPTCHAs. The core principle: mock the third-party boundary, not your own application code.
> **Prerequisites**: [core/network-mocking.md](network-mocking.md), [core/when-to-mock.md](when-to-mock.md), [core/authentication.md](authentication.md)

## Quick Reference

```typescript
// Mock an OAuth callback to bypass the real provider
await page.route('**/auth/callback*', (route) => {
  route.fulfill({
    status: 302,
    headers: { Location: '/dashboard?token=mock-jwt-token' },
  });
});

// Block analytics scripts from loading
await page.route('**/*.google-analytics.com/**', (route) => route.abort());
await page.route('**/segment.io/**', (route) => route.abort());

// Mock a third-party widget endpoint
await page.route('**/api.stripe.com/**', (route) => {
  route.fulfill({ status: 200, contentType: 'application/json', body: '{"id":"pi_mock"}' });
});
```

**Core principle**: In E2E tests, mock the external service, not your own application. Your code should run as-is; only the third-party responses are faked.

## Patterns

### Mocking OAuth Providers (Google, GitHub, etc.)

**Use when**: Testing the full login flow without depending on real OAuth provider availability, rate limits, or test accounts.
**Avoid when**: You need to verify the actual OAuth integration works end-to-end (use a dedicated integration test for that).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('Google OAuth login via route mocking', async ({ page }) => {
  // Intercept the redirect to Google and simulate the callback
  await page.route('**/accounts.google.com/**', async (route) => {
    // Extract the redirect_uri from the request URL
    const url = new URL(route.request().url());
    const redirectUri = url.searchParams.get('redirect_uri') || '/auth/callback';

    // Simulate Google redirecting back with an auth code
    await route.fulfill({
      status: 302,
      headers: {
        Location: `${redirectUri}?code=mock-auth-code&state=${url.searchParams.get('state') || ''}`,
      },
    });
  });

  // Mock your own backend's token exchange endpoint
  await page.route('**/api/auth/google/callback*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        token: 'mock-jwt-token',
        user: {
          id: '1',
          name: 'Test User',
          email: 'testuser@gmail.com',
          avatar: 'https://placehold.co/100x100',
        },
      }),
    });
  });

  await page.goto('/login');
  await page.getByRole('button', { name: 'Sign in with Google' }).click();

  // Should land on dashboard with user info
  await page.waitForURL('/dashboard');
  await expect(page.getByText('Test User')).toBeVisible();
});

test('GitHub OAuth login with mocked provider', async ({ page }) => {
  await page.route('**/github.com/login/oauth/**', async (route) => {
    const url = new URL(route.request().url());
    const redirectUri = url.searchParams.get('redirect_uri') || '/auth/callback';
    await route.fulfill({
      status: 302,
      headers: {
        Location: `${redirectUri}?code=mock-github-code`,
      },
    });
  });

  await page.route('**/api/auth/github/callback*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        token: 'mock-jwt-token',
        user: { id: '2', name: 'GitHub User', email: 'user@github.com' },
      }),
    });
  });

  await page.goto('/login');
  await page.getByRole('button', { name: 'Sign in with GitHub' }).click();
  await page.waitForURL('/dashboard');
  await expect(page.getByText('GitHub User')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('Google OAuth login via route mocking', async ({ page }) => {
  await page.route('**/accounts.google.com/**', async (route) => {
    const url = new URL(route.request().url());
    const redirectUri = url.searchParams.get('redirect_uri') || '/auth/callback';
    await route.fulfill({
      status: 302,
      headers: {
        Location: `${redirectUri}?code=mock-auth-code&state=${url.searchParams.get('state') || ''}`,
      },
    });
  });

  await page.route('**/api/auth/google/callback*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        token: 'mock-jwt-token',
        user: { id: '1', name: 'Test User', email: 'testuser@gmail.com' },
      }),
    });
  });

  await page.goto('/login');
  await page.getByRole('button', { name: 'Sign in with Google' }).click();
  await page.waitForURL('/dashboard');
  await expect(page.getByText('Test User')).toBeVisible();
});
```

### Payment Gateway Testing (Stripe Elements)

**Use when**: Testing checkout flows that use Stripe Elements, PayPal buttons, or similar embedded payment UIs.
**Avoid when**: Stripe provides test mode with test card numbers and you want full integration coverage.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('complete Stripe checkout with test card', async ({ page }) => {
  await page.goto('/checkout');

  // Stripe Elements load in an iframe
  const stripeFrame = page.frameLocator('iframe[name*="__privateStripeFrame"]').first();

  // Fill card details inside the Stripe iframe
  await stripeFrame.getByPlaceholder('Card number').fill('4242424242424242');
  await stripeFrame.getByPlaceholder('MM / YY').fill('12/28');
  await stripeFrame.getByPlaceholder('CVC').fill('123');
  await stripeFrame.getByPlaceholder('ZIP').fill('10001');

  await page.getByRole('button', { name: 'Pay' }).click();
  await expect(page.getByText('Payment successful')).toBeVisible({ timeout: 15000 });
});

test('Stripe checkout with mocked API for speed', async ({ page }) => {
  // Mock Stripe API calls for faster, more reliable tests
  await page.route('**/api.stripe.com/v1/payment_intents*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'pi_mock_123',
        status: 'succeeded',
        client_secret: 'pi_mock_123_secret_456',
      }),
    });
  });

  await page.route('**/api.stripe.com/v1/payment_methods*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'pm_mock_789',
        type: 'card',
        card: { brand: 'visa', last4: '4242' },
      }),
    });
  });

  await page.goto('/checkout');
  // With mocked Stripe, your app-level payment form may work without the iframe
  await page.getByRole('button', { name: 'Pay' }).click();
  await expect(page.getByText('Payment successful')).toBeVisible();
});

test('handles declined card gracefully', async ({ page }) => {
  await page.goto('/checkout');

  const stripeFrame = page.frameLocator('iframe[name*="__privateStripeFrame"]').first();
  // Stripe test card that always declines
  await stripeFrame.getByPlaceholder('Card number').fill('4000000000000002');
  await stripeFrame.getByPlaceholder('MM / YY').fill('12/28');
  await stripeFrame.getByPlaceholder('CVC').fill('123');
  await stripeFrame.getByPlaceholder('ZIP').fill('10001');

  await page.getByRole('button', { name: 'Pay' }).click();
  await expect(page.getByText(/declined|failed/i)).toBeVisible({ timeout: 15000 });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('complete Stripe checkout with test card', async ({ page }) => {
  await page.goto('/checkout');

  const stripeFrame = page.frameLocator('iframe[name*="__privateStripeFrame"]').first();
  await stripeFrame.getByPlaceholder('Card number').fill('4242424242424242');
  await stripeFrame.getByPlaceholder('MM / YY').fill('12/28');
  await stripeFrame.getByPlaceholder('CVC').fill('123');
  await stripeFrame.getByPlaceholder('ZIP').fill('10001');

  await page.getByRole('button', { name: 'Pay' }).click();
  await expect(page.getByText('Payment successful')).toBeVisible({ timeout: 15000 });
});
```

### Analytics Blocking

**Use when**: Preventing analytics scripts from executing during tests to improve speed, avoid polluting analytics data, and eliminate flakiness from third-party script failures.
**Avoid when**: You specifically need to test that analytics events are fired correctly.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// Block analytics in a fixture for all tests
import { test as base } from '@playwright/test';

export const test = base.extend({
  page: async ({ page }, use) => {
    // Block common analytics and tracking scripts
    await page.route(/(google-analytics|googletagmanager|segment\.io|hotjar|mixpanel|amplitude)/, (route) =>
      route.abort()
    );
    await page.route('**/collect?**', (route) => route.abort()); // GA beacon
    await page.route('**/analytics/**', (route) => route.abort());
    await use(page);
  },
});

export { expect };
```

```typescript
// For tests that verify analytics events ARE sent
import { test, expect } from '@playwright/test';

test('purchase event fires on checkout completion', async ({ page }) => {
  const analyticsRequests: { url: string; body: string }[] = [];

  // Intercept analytics calls instead of blocking them
  await page.route('**/collect**', async (route) => {
    analyticsRequests.push({
      url: route.request().url(),
      body: route.request().postData() || '',
    });
    await route.fulfill({ status: 200 }); // Respond but don't send to real analytics
  });

  await page.goto('/checkout');
  await page.getByRole('button', { name: 'Complete order' }).click();
  await page.waitForURL('/order/confirmation');

  // Verify the purchase event was sent
  const purchaseEvent = analyticsRequests.find(
    (r) => r.body.includes('purchase') || r.url.includes('purchase')
  );
  expect(purchaseEvent).toBeDefined();
});
```

**JavaScript**
```javascript
const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  page: async ({ page }, use) => {
    await page.route(/(google-analytics|googletagmanager|segment\.io|hotjar|mixpanel)/, (route) =>
      route.abort()
    );
    await use(page);
  },
});

module.exports = { test, expect };
```

### Chat Widget Testing (Intercom, Drift, etc.)

**Use when**: Your app embeds a third-party chat widget and you need to test the interaction or verify it does not break your UI.
**Avoid when**: The chat widget is cosmetic and not part of critical user flows.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('Intercom chat widget opens and accepts messages', async ({ page }) => {
  await page.goto('/');

  // Wait for the chat widget to load (often delayed)
  const chatLauncher = page.frameLocator('iframe[name*="intercom"]')
    .getByRole('button', { name: /chat|message/i });
  await expect(chatLauncher).toBeVisible({ timeout: 15000 });

  // Open the chat
  await chatLauncher.click();

  // The chat conversation iframe loads
  const chatFrame = page.frameLocator('iframe[name*="intercom-messenger"]');
  await expect(chatFrame.getByText(/How can we help/i)).toBeVisible();

  // Type a message
  await chatFrame.getByRole('textbox').fill('I need help with my order');
  await chatFrame.getByRole('button', { name: /send/i }).click();

  await expect(chatFrame.getByText('I need help with my order')).toBeVisible();
});

test('chat widget does not overlap critical UI', async ({ page }) => {
  await page.goto('/checkout');

  // Get chat widget position
  const chatWidget = page.locator('iframe[name*="intercom"]').first();
  if (await chatWidget.isVisible()) {
    const chatBox = await chatWidget.boundingBox();
    const payButton = await page.getByRole('button', { name: 'Pay' }).boundingBox();

    // Ensure the pay button is not hidden behind the chat widget
    if (chatBox && payButton) {
      const overlaps =
        payButton.x < chatBox.x + chatBox.width &&
        payButton.x + payButton.width > chatBox.x &&
        payButton.y < chatBox.y + chatBox.height &&
        payButton.y + payButton.height > chatBox.y;
      expect(overlaps).toBe(false);
    }
  }
});

// Block chat widget in most tests for speed
test('block chat widget for non-chat tests', async ({ page }) => {
  await page.route('**/widget.intercom.io/**', (route) => route.abort());
  await page.route('**/js.intercomcdn.com/**', (route) => route.abort());

  await page.goto('/dashboard');
  // Chat widget will not load — test runs faster
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('block chat widget for speed', async ({ page }) => {
  await page.route('**/widget.intercom.io/**', (route) => route.abort());
  await page.route('**/js.intercomcdn.com/**', (route) => route.abort());

  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

### Map Integration Testing (Google Maps)

**Use when**: Your app embeds Google Maps or a similar map provider and you need to verify map-related interactions.
**Avoid when**: The map is decorative and not part of a user workflow.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('store locator shows markers on the map', async ({ page }) => {
  await page.goto('/store-locator');

  // Google Maps loads in an iframe or directly on the page
  await page.getByLabel('Search location').fill('New York');
  await page.getByRole('button', { name: 'Search' }).click();

  // Wait for map markers to appear
  await expect(page.locator('[data-testid="map-marker"]')).toHaveCount(5, {
    timeout: 10000,
  });

  // Click a marker to see store details
  await page.locator('[data-testid="map-marker"]').first().click();
  await expect(page.getByTestId('store-info')).toBeVisible();
  await expect(page.getByTestId('store-info')).toContainText('New York');
});

test('mock Google Maps API for offline testing', async ({ page }) => {
  // Block real Google Maps and provide mock responses
  await page.route('**/maps.googleapis.com/**', async (route) => {
    const url = route.request().url();

    if (url.includes('/geocode/')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [{
            geometry: { location: { lat: 40.7128, lng: -74.0060 } },
            formatted_address: 'New York, NY, USA',
          }],
          status: 'OK',
        }),
      });
    } else if (url.includes('/places/')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            { name: 'Store A', geometry: { location: { lat: 40.71, lng: -74.00 } } },
            { name: 'Store B', geometry: { location: { lat: 40.72, lng: -74.01 } } },
          ],
          status: 'OK',
        }),
      });
    } else {
      await route.continue();
    }
  });

  await page.goto('/store-locator');
  await page.getByLabel('Search location').fill('New York');
  await page.getByRole('button', { name: 'Search' }).click();

  await expect(page.getByText('Store A')).toBeVisible();
  await expect(page.getByText('Store B')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('mock Google Maps geocode API', async ({ page }) => {
  await page.route('**/maps.googleapis.com/maps/api/geocode/**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: [{
          geometry: { location: { lat: 40.7128, lng: -74.0060 } },
          formatted_address: 'New York, NY, USA',
        }],
        status: 'OK',
      }),
    });
  });

  await page.goto('/store-locator');
  await page.getByLabel('Search location').fill('New York');
  await page.getByRole('button', { name: 'Search' }).click();
  await expect(page.getByText('New York')).toBeVisible();
});
```

### reCAPTCHA Bypass for Testing

**Use when**: Your app uses reCAPTCHA or hCaptcha and you need tests to proceed without solving challenges.
**Avoid when**: You can disable CAPTCHA in your test environment through a server-side flag (preferred approach).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('reCAPTCHA handling', () => {
  // Best approach: Use test keys provided by Google
  // Site key: 6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI (always passes)
  // Secret key: 6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe

  test('form submission with reCAPTCHA bypassed via test keys', async ({ page }) => {
    // Your test environment should be configured with Google's test keys
    await page.goto('/contact');

    await page.getByLabel('Name').fill('Test User');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Message').fill('Test message');

    // With test keys, reCAPTCHA auto-passes — just click submit
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('Message sent')).toBeVisible();
  });

  test('mock reCAPTCHA verification endpoint', async ({ page }) => {
    // Mock Google's reCAPTCHA verification API
    await page.route('**/recaptcha/api/siteverify**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, score: 0.9 }),
      });
    });

    // Mock the reCAPTCHA script to provide a fake token
    await page.addInitScript(() => {
      (window as any).grecaptcha = {
        ready: (cb: () => void) => cb(),
        execute: () => Promise.resolve('mock-recaptcha-token'),
        render: () => 'mock-widget-id',
        getResponse: () => 'mock-recaptcha-token',
        reset: () => {},
      };
    });

    await page.goto('/contact');
    await page.getByLabel('Name').fill('Test User');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Message').fill('Test message');
    await page.getByRole('button', { name: 'Send' }).click();

    await expect(page.getByText('Message sent')).toBeVisible();
  });

  test('invisible reCAPTCHA v3 bypass', async ({ page }) => {
    // For reCAPTCHA v3, mock the enterprise API
    await page.route('**/recaptcha/**', async (route) => {
      if (route.request().url().includes('api.js')) {
        // Serve a mock script that provides the grecaptcha object
        await route.fulfill({
          status: 200,
          contentType: 'application/javascript',
          body: `
            window.grecaptcha = {
              ready: function(cb) { cb(); },
              execute: function() { return Promise.resolve('mock-token'); },
              enterprise: {
                ready: function(cb) { cb(); },
                execute: function() { return Promise.resolve('mock-token'); },
              }
            };
          `,
        });
      } else {
        await route.abort();
      }
    });

    await page.goto('/login');
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('mock reCAPTCHA for form submission', async ({ page }) => {
  await page.route('**/recaptcha/api/siteverify**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, score: 0.9 }),
    });
  });

  await page.addInitScript(() => {
    window.grecaptcha = {
      ready: (cb) => cb(),
      execute: () => Promise.resolve('mock-recaptcha-token'),
      render: () => 'mock-widget-id',
      getResponse: () => 'mock-recaptcha-token',
      reset: () => {},
    };
  });

  await page.goto('/contact');
  await page.getByLabel('Name').fill('Test User');
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Message').fill('Test message');
  await page.getByRole('button', { name: 'Send' }).click();
  await expect(page.getByText('Message sent')).toBeVisible();
});
```

### Social Login Mocking

**Use when**: Your app offers multiple social login options and you need to test the login flow without real provider accounts.
**Avoid when**: You have a backend bypass that sets auth state directly.

**TypeScript**
```typescript
import { test as base, expect } from '@playwright/test';

// Reusable fixture that mocks any OAuth provider
type OAuthFixtures = {
  mockOAuth: (provider: string, userData: Record<string, string>) => Promise<void>;
};

export const test = base.extend<OAuthFixtures>({
  mockOAuth: async ({ page }, use) => {
    const mock = async (provider: string, userData: Record<string, string>) => {
      const providerPatterns: Record<string, string> = {
        google: '**/accounts.google.com/**',
        github: '**/github.com/login/oauth/**',
        facebook: '**/facebook.com/v*/dialog/oauth**',
        apple: '**/appleid.apple.com/**',
        microsoft: '**/login.microsoftonline.com/**',
      };

      const pattern = providerPatterns[provider];
      if (!pattern) throw new Error(`Unknown provider: ${provider}`);

      // Intercept the OAuth redirect
      await page.route(pattern, async (route) => {
        const url = new URL(route.request().url());
        const redirectUri = url.searchParams.get('redirect_uri') || '/auth/callback';
        await route.fulfill({
          status: 302,
          headers: { Location: `${redirectUri}?code=mock-${provider}-code` },
        });
      });

      // Mock the token exchange
      await page.route(`**/api/auth/${provider}/callback*`, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ token: `mock-${provider}-jwt`, user: userData }),
        });
      });
    };

    await use(mock);
  },
});

// Usage in tests
test('login with multiple social providers', async ({ page, mockOAuth }) => {
  // Test Google login
  await mockOAuth('google', { name: 'Google User', email: 'user@gmail.com' });
  await page.goto('/login');
  await page.getByRole('button', { name: 'Sign in with Google' }).click();
  await page.waitForURL('/dashboard');
  await expect(page.getByText('Google User')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  mockOAuth: async ({ page }, use) => {
    const mock = async (provider, userData) => {
      const patterns = {
        google: '**/accounts.google.com/**',
        github: '**/github.com/login/oauth/**',
        facebook: '**/facebook.com/v*/dialog/oauth**',
      };

      await page.route(patterns[provider], async (route) => {
        const url = new URL(route.request().url());
        const redirectUri = url.searchParams.get('redirect_uri') || '/auth/callback';
        await route.fulfill({
          status: 302,
          headers: { Location: `${redirectUri}?code=mock-${provider}-code` },
        });
      });

      await page.route(`**/api/auth/${provider}/callback*`, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ token: `mock-${provider}-jwt`, user: userData }),
        });
      });
    };
    await use(mock);
  },
});

test('login with Google', async ({ page, mockOAuth }) => {
  await mockOAuth('google', { name: 'Google User', email: 'user@gmail.com' });
  await page.goto('/login');
  await page.getByRole('button', { name: 'Sign in with Google' }).click();
  await page.waitForURL('/dashboard');
  await expect(page.getByText('Google User')).toBeVisible();
});

module.exports = { test, expect };
```

## Decision Guide

| Integration | Mock Strategy | When to Use Real | When to Mock |
|---|---|---|---|
| OAuth (Google, GitHub, etc.) | Route intercept on provider URL + mock callback | Dedicated integration test with test accounts | All E2E feature tests that require login |
| Stripe/payment gateway | Use Stripe test mode with test cards OR mock API | Checkout flow integration tests | All non-payment E2E tests |
| Google Analytics / Segment | `route.abort()` to block entirely | Dedicated analytics verification tests | Every other test (block for speed) |
| Chat widgets (Intercom, Drift) | `route.abort()` to block, or interact via iframe | Tests specifically about chat functionality | Every other test (block for speed/stability) |
| Google Maps | Mock geocoding/places API responses | Tests verifying real map rendering | Tests that only need location data |
| reCAPTCHA | Google test keys (preferred) or mock `grecaptcha` | Never in automated tests | Always -- CAPTCHA cannot be solved by automation |
| Social login | Reusable OAuth mock fixture per provider | Periodic integration check | All E2E tests requiring auth |
| Email services (SendGrid, SES) | Mock API endpoints, verify calls were made | End-to-end email delivery tests (separate suite) | All tests that trigger emails |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Using real OAuth provider accounts in tests | Rate limits, 2FA requirements, account lockouts, test flakiness | Mock the OAuth flow or use provider test modes |
| Letting analytics scripts run in all tests | Slower tests, pollutes real analytics data, adds network flakiness | Block analytics with `route.abort()` in a shared fixture |
| Solving reCAPTCHA with image recognition | Fragile, slow, violates CAPTCHA terms of service | Use Google's test keys or mock the `grecaptcha` object |
| Mocking your own application code instead of the third-party | Does not test your integration logic | Mock only the external boundary (API endpoints, scripts) |
| Hardcoding mock responses for every test | Duplicated mock setup, hard to maintain | Build reusable mock fixtures (see Social Login pattern) |
| Not testing error paths from third parties | Misses how your app handles OAuth failures, payment declines | Mock error responses: `{ error: 'access_denied' }`, declined cards |
| Loading real Stripe.js in every test | Slow initial load, occasional CDN failures | Mock Stripe for non-payment tests; use real Stripe only for checkout tests |
| Trusting `networkidle` for third-party scripts | Third-party scripts may poll indefinitely | Wait for specific app-level indicators, not `networkidle` |

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| OAuth mock route never fires | The app uses a redirect chain that bypasses your route pattern | Use a broader pattern like `**accounts.google.com**` or log all requests to see the actual URL |
| Stripe iframe not found | Stripe.js loads async; iframe name varies by version | Use a flexible selector: `iframe[name*="__privateStripeFrame"]` with a long timeout |
| reCAPTCHA mock does not work | Script loads before `addInitScript` runs | Use `route` to intercept the reCAPTCHA script and serve a mock version |
| Analytics blocking breaks the app | App code depends on analytics library being present (e.g., `window.gtag`) | Instead of blocking, fulfill with a stub: `route.fulfill({ body: 'window.gtag=function(){}' })` |
| Chat widget iframe is not accessible | Cross-origin iframe restrictions | Use `frameLocator` with the correct iframe name/selector |
| Mock OAuth returns wrong redirect URI | The `redirect_uri` parameter is URL-encoded or different in test | Log the actual request URL with `page.on('request')` and match accordingly |
| Payment test passes locally but fails in CI | Stripe test mode has rate limits; CI IP may be blocked | Mock Stripe API in CI, use real Stripe only in a separate integration pipeline |
| Social login mock does not redirect | Your app opens OAuth in a popup, not a redirect | Handle the popup: `page.waitForEvent('popup')` and mock routes on the popup page |

## Related

- [core/network-mocking.md](network-mocking.md) -- foundational route interception patterns
- [core/authentication.md](authentication.md) -- auth state management and login bypasses
- [core/when-to-mock.md](when-to-mock.md) -- decision framework for mocking vs real services
- [core/multi-context-and-popups.md](multi-context-and-popups.md) -- handling OAuth popup windows
- [core/security-testing.md](security-testing.md) -- testing auth security aspects
- [core/iframes-and-shadow-dom.md](iframes-and-shadow-dom.md) -- interacting with payment widget iframes
