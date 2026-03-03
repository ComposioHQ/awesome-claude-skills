# Testing Next.js Apps with Playwright

> **When to use**: Testing Next.js applications -- App Router, Pages Router, API routes, middleware, SSR pages, dynamic routes, and server components. This guide covers E2E testing patterns specific to Next.js behavior.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/locators.md](locators.md)

## Quick Reference

```bash
# Install Playwright in a Next.js project
npm init playwright@latest

# Run with Next.js dev server managed by Playwright
npx playwright test

# Run against a production build (recommended for CI)
npx playwright test --project=chromium

# Debug a single test with headed browser
npx playwright test tests/home.spec.ts --headed --debug
```

```
# .env.test — loaded by Next.js automatically when NODE_ENV=test
NEXT_PUBLIC_API_URL=http://localhost:3000/api
DATABASE_URL=postgresql://localhost:5432/test_db
NEXTAUTH_SECRET=test-secret-do-not-use-in-production
NEXTAUTH_URL=http://localhost:3000
```

## Setup

### Playwright Config for Next.js

The single most important configuration detail: use `webServer` to let Playwright start and manage your Next.js server.

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';
import path from 'path';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? '50%' : undefined,

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 14'] },
    },
  ],

  webServer: {
    command: process.env.CI
      ? 'npm run build && npm run start' // production build in CI
      : 'npm run dev',                   // dev server locally
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      NODE_ENV: process.env.CI ? 'production' : 'test',
    },
  },
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? '50%' : undefined,

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 14'] },
    },
  ],

  webServer: {
    command: process.env.CI
      ? 'npm run build && npm run start'
      : 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      NODE_ENV: process.env.CI ? 'production' : 'test',
    },
  },
});
```

### Environment Variables with `.env.test`

Next.js loads `.env.test` automatically when `NODE_ENV=test`. Use this for test-specific overrides.

```bash
# .env.test (commit this -- no real secrets)
NEXT_PUBLIC_API_URL=http://localhost:3000/api
NEXT_PUBLIC_FEATURE_FLAG_NEW_CHECKOUT=true
DATABASE_URL=postgresql://localhost:5432/test_db

# .env.test.local (gitignored -- real test secrets)
NEXTAUTH_SECRET=test-secret-local
STRIPE_TEST_KEY=sk_test_xxx
```

```bash
# .gitignore
.env*.local
playwright-report/
playwright/.auth/
test-results/
```

## Patterns

### Testing App Router Pages

**Use when**: Testing pages built with the Next.js App Router (`app/` directory). App Router pages are server components by default and may include streaming, suspense boundaries, and loading states.
**Avoid when**: You need to test isolated server component logic -- use unit tests for that. E2E tests verify the rendered result.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('App Router pages', () => {
  test('home page renders server component content', async ({ page }) => {
    await page.goto('/');

    // Server components render on the server -- by the time Playwright
    // sees the page, SSR content is already in the HTML
    await expect(page.getByRole('heading', { name: 'Welcome', level: 1 })).toBeVisible();
    await expect(page.getByRole('navigation', { name: 'Main' })).toBeVisible();
  });

  test('loading state shows while data streams in', async ({ page }) => {
    // Slow down the API to expose the loading state
    await page.route('**/api/dashboard/stats', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      await route.continue();
    });

    await page.goto('/dashboard');

    // Verify the loading skeleton appears during streaming
    await expect(page.getByRole('progressbar')).toBeVisible();

    // Then verify the real content replaces it
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
    await expect(page.getByRole('progressbar')).toBeHidden();
  });

  test('suspense boundary shows fallback then resolves', async ({ page }) => {
    await page.goto('/products');

    // The product list may be inside a Suspense boundary
    // Playwright auto-waits, so just assert the final state
    await expect(page.getByRole('listitem')).toHaveCount(12);
  });

  test('nested layouts persist across navigation', async ({ page }) => {
    await page.goto('/dashboard/analytics');

    // Verify the dashboard layout sidebar is visible
    const sidebar = page.getByRole('navigation', { name: 'Dashboard' });
    await expect(sidebar).toBeVisible();

    // Navigate to a sibling route -- layout should persist (no full reload)
    await sidebar.getByRole('link', { name: 'Settings' }).click();
    await page.waitForURL('/dashboard/settings');

    // Sidebar is still there -- layout was not re-mounted
    await expect(sidebar).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('App Router pages', () => {
  test('home page renders server component content', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'Welcome', level: 1 })).toBeVisible();
    await expect(page.getByRole('navigation', { name: 'Main' })).toBeVisible();
  });

  test('loading state shows while data streams in', async ({ page }) => {
    await page.route('**/api/dashboard/stats', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      await route.continue();
    });

    await page.goto('/dashboard');

    await expect(page.getByRole('progressbar')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
    await expect(page.getByRole('progressbar')).toBeHidden();
  });

  test('suspense boundary shows fallback then resolves', async ({ page }) => {
    await page.goto('/products');

    await expect(page.getByRole('listitem')).toHaveCount(12);
  });

  test('nested layouts persist across navigation', async ({ page }) => {
    await page.goto('/dashboard/analytics');

    const sidebar = page.getByRole('navigation', { name: 'Dashboard' });
    await expect(sidebar).toBeVisible();

    await sidebar.getByRole('link', { name: 'Settings' }).click();
    await page.waitForURL('/dashboard/settings');

    await expect(sidebar).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
  });
});
```

### Testing Pages Router (getServerSideProps / getStaticProps)

**Use when**: Testing pages built with the Pages Router (`pages/` directory) that use `getServerSideProps` or `getStaticProps` for data fetching.
**Avoid when**: Testing the data fetching functions directly -- that is a unit test concern. E2E tests verify what the user sees.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Pages Router with SSR', () => {
  test('page with getServerSideProps renders fetched data', async ({ page }) => {
    await page.goto('/blog');

    // getServerSideProps fetches posts on the server -- verify they render
    await expect(page.getByRole('heading', { name: 'Blog', level: 1 })).toBeVisible();
    await expect(page.getByRole('article')).toHaveCount(10);

    // Verify server-fetched data appears (not a loading skeleton)
    await expect(page.getByRole('article').first()).toContainText(/\w+/);
  });

  test('page with getStaticProps shows pre-rendered content', async ({ page }) => {
    await page.goto('/about');

    // Static pages are pre-rendered at build time -- content is immediate
    await expect(page.getByRole('heading', { name: 'About Us' })).toBeVisible();
    await expect(page.getByText('Founded in 2020')).toBeVisible();
  });

  test('client-side navigation with next/link preserves SPA behavior', async ({ page }) => {
    await page.goto('/blog');

    // Click a next/link -- this should be a client-side transition, not a full reload
    const navigationPromise = page.waitForURL('/blog/my-first-post');
    await page.getByRole('link', { name: 'My First Post' }).click();
    await navigationPromise;

    await expect(page.getByRole('heading', { name: 'My First Post', level: 1 })).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Pages Router with SSR', () => {
  test('page with getServerSideProps renders fetched data', async ({ page }) => {
    await page.goto('/blog');

    await expect(page.getByRole('heading', { name: 'Blog', level: 1 })).toBeVisible();
    await expect(page.getByRole('article')).toHaveCount(10);
    await expect(page.getByRole('article').first()).toContainText(/\w+/);
  });

  test('page with getStaticProps shows pre-rendered content', async ({ page }) => {
    await page.goto('/about');

    await expect(page.getByRole('heading', { name: 'About Us' })).toBeVisible();
    await expect(page.getByText('Founded in 2020')).toBeVisible();
  });

  test('client-side navigation with next/link preserves SPA behavior', async ({ page }) => {
    await page.goto('/blog');

    const navigationPromise = page.waitForURL('/blog/my-first-post');
    await page.getByRole('link', { name: 'My First Post' }).click();
    await navigationPromise;

    await expect(page.getByRole('heading', { name: 'My First Post', level: 1 })).toBeVisible();
  });
});
```

### Testing Dynamic Routes (`[slug]`, `[...catchAll]`)

**Use when**: Testing pages with dynamic segments like `/blog/[slug]`, `/products/[id]`, or catch-all routes like `/docs/[...path]`.
**Avoid when**: The route is static -- no dynamic segments involved.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('dynamic routes', () => {
  test('dynamic [slug] page renders correct content', async ({ page }) => {
    await page.goto('/blog/nextjs-testing-guide');

    await expect(page.getByRole('heading', { level: 1 })).toContainText('Next.js Testing Guide');
    // Verify the slug maps to the correct content, not a 404
    await expect(page.getByText('Page not found')).toBeHidden();
  });

  test('non-existent slug shows 404 page', async ({ page }) => {
    const response = await page.goto('/blog/this-post-does-not-exist');

    // Next.js returns 404 for pages that call notFound() or return { notFound: true }
    expect(response?.status()).toBe(404);
    await expect(page.getByRole('heading', { name: '404' })).toBeVisible();
  });

  test('catch-all route handles nested paths', async ({ page }) => {
    await page.goto('/docs/getting-started/installation');

    await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();

    // Navigate to a different docs path
    await page.goto('/docs/api/configuration');
    await expect(page.getByRole('heading', { name: 'Configuration' })).toBeVisible();
  });

  test('dynamic route with query parameters', async ({ page }) => {
    await page.goto('/products?category=electronics&sort=price-asc');

    await expect(page.getByRole('heading', { name: 'Electronics' })).toBeVisible();
    // Verify sort order is applied
    const prices = await page.getByTestId('product-price').allTextContents();
    const numericPrices = prices.map((p) => parseFloat(p.replace('$', '')));
    expect(numericPrices).toEqual([...numericPrices].sort((a, b) => a - b));
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('dynamic routes', () => {
  test('dynamic [slug] page renders correct content', async ({ page }) => {
    await page.goto('/blog/nextjs-testing-guide');

    await expect(page.getByRole('heading', { level: 1 })).toContainText('Next.js Testing Guide');
    await expect(page.getByText('Page not found')).toBeHidden();
  });

  test('non-existent slug shows 404 page', async ({ page }) => {
    const response = await page.goto('/blog/this-post-does-not-exist');

    expect(response?.status()).toBe(404);
    await expect(page.getByRole('heading', { name: '404' })).toBeVisible();
  });

  test('catch-all route handles nested paths', async ({ page }) => {
    await page.goto('/docs/getting-started/installation');

    await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();

    await page.goto('/docs/api/configuration');
    await expect(page.getByRole('heading', { name: 'Configuration' })).toBeVisible();
  });

  test('dynamic route with query parameters', async ({ page }) => {
    await page.goto('/products?category=electronics&sort=price-asc');

    await expect(page.getByRole('heading', { name: 'Electronics' })).toBeVisible();
    const prices = await page.getByTestId('product-price').allTextContents();
    const numericPrices = prices.map((p) => parseFloat(p.replace('$', '')));
    expect(numericPrices).toEqual([...numericPrices].sort((a, b) => a - b));
  });
});
```

### Testing API Routes

**Use when**: Testing Next.js API routes (`app/api/` or `pages/api/`) directly with Playwright's `request` context, or indirectly through UI interactions that call them.
**Avoid when**: Unit testing API handler logic in isolation -- use a unit testing framework for that.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('API routes -- direct testing', () => {
  test('GET /api/products returns product list', async ({ request }) => {
    const response = await request.get('/api/products');

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.products).toBeInstanceOf(Array);
    expect(body.products.length).toBeGreaterThan(0);
    expect(body.products[0]).toHaveProperty('id');
    expect(body.products[0]).toHaveProperty('name');
    expect(body.products[0]).toHaveProperty('price');
  });

  test('POST /api/products creates a new product', async ({ request }) => {
    const response = await request.post('/api/products', {
      data: {
        name: 'Test Product',
        price: 29.99,
        description: 'Created by Playwright',
      },
    });

    expect(response.status()).toBe(201);
    const body = await response.json();
    expect(body.product.name).toBe('Test Product');
  });

  test('POST /api/products validates required fields', async ({ request }) => {
    const response = await request.post('/api/products', {
      data: { name: '' }, // missing required fields
    });

    expect(response.status()).toBe(400);
    const body = await response.json();
    expect(body.error).toContainEqual(
      expect.objectContaining({ field: 'price' })
    );
  });
});

test.describe('API routes -- indirect through UI', () => {
  test('form submission calls API and shows result', async ({ page }) => {
    await page.goto('/products/new');

    await page.getByLabel('Product name').fill('Widget');
    await page.getByLabel('Price').fill('19.99');
    await page.getByRole('button', { name: 'Create product' }).click();

    // The UI calls POST /api/products internally
    await expect(page.getByText('Product created successfully')).toBeVisible();
    await page.waitForURL('/products/**');
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('API routes -- direct testing', () => {
  test('GET /api/products returns product list', async ({ request }) => {
    const response = await request.get('/api/products');

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.products).toBeInstanceOf(Array);
    expect(body.products.length).toBeGreaterThan(0);
    expect(body.products[0]).toHaveProperty('id');
    expect(body.products[0]).toHaveProperty('name');
    expect(body.products[0]).toHaveProperty('price');
  });

  test('POST /api/products creates a new product', async ({ request }) => {
    const response = await request.post('/api/products', {
      data: {
        name: 'Test Product',
        price: 29.99,
        description: 'Created by Playwright',
      },
    });

    expect(response.status()).toBe(201);
    const body = await response.json();
    expect(body.product.name).toBe('Test Product');
  });

  test('POST /api/products validates required fields', async ({ request }) => {
    const response = await request.post('/api/products', {
      data: { name: '' },
    });

    expect(response.status()).toBe(400);
    const body = await response.json();
    expect(body.error).toContainEqual(
      expect.objectContaining({ field: 'price' })
    );
  });
});

test.describe('API routes -- indirect through UI', () => {
  test('form submission calls API and shows result', async ({ page }) => {
    await page.goto('/products/new');

    await page.getByLabel('Product name').fill('Widget');
    await page.getByLabel('Price').fill('19.99');
    await page.getByRole('button', { name: 'Create product' }).click();

    await expect(page.getByText('Product created successfully')).toBeVisible();
    await page.waitForURL('/products/**');
  });
});
```

### Testing Middleware

**Use when**: Testing Next.js middleware that handles redirects, rewrites, authentication guards, geolocation-based routing, or header manipulation.
**Avoid when**: The middleware logic is trivial -- a redirect from `/old` to `/new` can be verified with a simple navigation test.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('middleware', () => {
  test('unauthenticated user is redirected to login', async ({ page }) => {
    // Visit a protected page without auth cookies
    const response = await page.goto('/dashboard');

    // Middleware should redirect to /login
    expect(page.url()).toContain('/login');
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  });

  test('middleware redirect preserves the return URL', async ({ page }) => {
    await page.goto('/dashboard/settings');

    // Should redirect to login with a callbackUrl or returnTo parameter
    const url = new URL(page.url());
    expect(url.pathname).toBe('/login');
    expect(url.searchParams.get('callbackUrl') || url.searchParams.get('returnTo'))
      .toContain('/dashboard/settings');
  });

  test('middleware sets security headers', async ({ page }) => {
    const response = await page.goto('/');

    const headers = response!.headers();
    expect(headers['x-frame-options']).toBe('DENY');
    expect(headers['x-content-type-options']).toBe('nosniff');
    expect(headers['referrer-policy']).toBe('strict-origin-when-cross-origin');
  });

  test('middleware rewrites based on locale', async ({ page, context }) => {
    // Set Accept-Language header to simulate a French user
    await context.setExtraHTTPHeaders({
      'Accept-Language': 'fr-FR,fr;q=0.9',
    });

    await page.goto('/');

    // Middleware should rewrite to the French locale
    await expect(page.getByText('Bienvenue')).toBeVisible();
  });

  test('middleware blocks unauthorized API access', async ({ request }) => {
    // Call a protected API route without authentication
    const response = await request.get('/api/admin/users');

    expect(response.status()).toBe(401);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('middleware', () => {
  test('unauthenticated user is redirected to login', async ({ page }) => {
    const response = await page.goto('/dashboard');

    expect(page.url()).toContain('/login');
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  });

  test('middleware redirect preserves the return URL', async ({ page }) => {
    await page.goto('/dashboard/settings');

    const url = new URL(page.url());
    expect(url.pathname).toBe('/login');
    expect(url.searchParams.get('callbackUrl') || url.searchParams.get('returnTo'))
      .toContain('/dashboard/settings');
  });

  test('middleware sets security headers', async ({ page }) => {
    const response = await page.goto('/');

    const headers = response.headers();
    expect(headers['x-frame-options']).toBe('DENY');
    expect(headers['x-content-type-options']).toBe('nosniff');
    expect(headers['referrer-policy']).toBe('strict-origin-when-cross-origin');
  });

  test('middleware rewrites based on locale', async ({ page, context }) => {
    await context.setExtraHTTPHeaders({
      'Accept-Language': 'fr-FR,fr;q=0.9',
    });

    await page.goto('/');

    await expect(page.getByText('Bienvenue')).toBeVisible();
  });

  test('middleware blocks unauthorized API access', async ({ request }) => {
    const response = await request.get('/api/admin/users');

    expect(response.status()).toBe(401);
  });
});
```

### Testing Hydration and SSR/CSR Consistency

**Use when**: Verifying that server-rendered HTML matches the client-side hydrated output. Hydration mismatches cause visual flicker, broken interactivity, or React errors in the console.
**Avoid when**: The page has no interactive client components -- pure server components do not hydrate.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('hydration', () => {
  test('no hydration errors in console', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/');
    // Wait for hydration to complete -- interactive elements become clickable
    await page.getByRole('button', { name: 'Get started' }).click();

    // Filter for hydration-specific errors
    const hydrationErrors = consoleErrors.filter(
      (e) =>
        e.includes('Hydration') ||
        e.includes('hydration') ||
        e.includes('server-rendered') ||
        e.includes('did not match')
    );
    expect(hydrationErrors).toEqual([]);
  });

  test('interactive elements work after hydration', async ({ page }) => {
    await page.goto('/');

    // This button relies on a client component event handler
    // If hydration fails, the click will do nothing
    const counter = page.getByTestId('counter-value');
    await expect(counter).toHaveText('0');

    await page.getByRole('button', { name: 'Increment' }).click();
    await expect(counter).toHaveText('1');
  });

  test('date/time renders without hydration mismatch', async ({ page }) => {
    // Dates are a common source of hydration mismatch because server
    // and client may be in different timezones
    await page.goto('/dashboard');

    // Verify the date displays without flicker
    const dateElement = page.getByTestId('current-date');
    await expect(dateElement).toBeVisible();
    // Verify it contains a plausible date format, not "undefined" or garbled text
    await expect(dateElement).toHaveText(/\w+ \d{1,2}, \d{4}/);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('hydration', () => {
  test('no hydration errors in console', async ({ page }) => {
    const consoleErrors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.getByRole('button', { name: 'Get started' }).click();

    const hydrationErrors = consoleErrors.filter(
      (e) =>
        e.includes('Hydration') ||
        e.includes('hydration') ||
        e.includes('server-rendered') ||
        e.includes('did not match')
    );
    expect(hydrationErrors).toEqual([]);
  });

  test('interactive elements work after hydration', async ({ page }) => {
    await page.goto('/');

    const counter = page.getByTestId('counter-value');
    await expect(counter).toHaveText('0');

    await page.getByRole('button', { name: 'Increment' }).click();
    await expect(counter).toHaveText('1');
  });

  test('date/time renders without hydration mismatch', async ({ page }) => {
    await page.goto('/dashboard');

    const dateElement = page.getByTestId('current-date');
    await expect(dateElement).toBeVisible();
    await expect(dateElement).toHaveText(/\w+ \d{1,2}, \d{4}/);
  });
});
```

### Testing next/image Optimization

**Use when**: Verifying that `next/image` components render correctly, lazy load offscreen images, and serve optimized formats.
**Avoid when**: You do not use `next/image` or image optimization is not a concern for your test.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('next/image', () => {
  test('hero image loads with correct attributes', async ({ page }) => {
    await page.goto('/');

    const heroImage = page.getByRole('img', { name: 'Hero banner' });
    await expect(heroImage).toBeVisible();

    // Verify next/image sets srcset for responsive loading
    const srcset = await heroImage.getAttribute('srcset');
    expect(srcset).toBeTruthy();
    expect(srcset).toContain('w='); // next/image adds width descriptors

    // Verify priority images are not lazy-loaded
    const loading = await heroImage.getAttribute('loading');
    expect(loading).not.toBe('lazy'); // priority images use eager loading
  });

  test('offscreen images lazy load on scroll', async ({ page }) => {
    await page.goto('/gallery');

    // Get an image that is below the fold
    const offscreenImage = page.getByRole('img', { name: 'Gallery item 20' });

    // Before scroll: image should not have loaded its src yet
    const initialSrc = await offscreenImage.getAttribute('src');
    // next/image uses a blur placeholder or empty src for lazy images

    // Scroll the image into view
    await offscreenImage.scrollIntoViewIfNeeded();
    await expect(offscreenImage).toBeVisible();

    // Verify the image has loaded (naturalWidth > 0 means the image loaded)
    const naturalWidth = await offscreenImage.evaluate(
      (img: HTMLImageElement) => img.naturalWidth
    );
    expect(naturalWidth).toBeGreaterThan(0);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('next/image', () => {
  test('hero image loads with correct attributes', async ({ page }) => {
    await page.goto('/');

    const heroImage = page.getByRole('img', { name: 'Hero banner' });
    await expect(heroImage).toBeVisible();

    const srcset = await heroImage.getAttribute('srcset');
    expect(srcset).toBeTruthy();
    expect(srcset).toContain('w=');

    const loading = await heroImage.getAttribute('loading');
    expect(loading).not.toBe('lazy');
  });

  test('offscreen images lazy load on scroll', async ({ page }) => {
    await page.goto('/gallery');

    const offscreenImage = page.getByRole('img', { name: 'Gallery item 20' });

    await offscreenImage.scrollIntoViewIfNeeded();
    await expect(offscreenImage).toBeVisible();

    const naturalWidth = await offscreenImage.evaluate(
      (img) => img.naturalWidth
    );
    expect(naturalWidth).toBeGreaterThan(0);
  });
});
```

### Authentication with NextAuth.js / Auth.js

**Use when**: Testing login flows in Next.js apps using NextAuth.js or Auth.js. Use a setup project to authenticate once, then reuse `storageState` across tests.
**Avoid when**: Your app does not use session-based authentication.

**TypeScript**
```typescript
// playwright.config.ts (auth-specific excerpt)
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'setup',
      testMatch: /auth\.setup\.ts/,
    },
    {
      name: 'authenticated',
      use: { storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup'],
    },
    {
      name: 'unauthenticated',
      // No storageState -- tests run as logged-out user
      testMatch: '**/*.unauth.spec.ts',
    },
  ],
});
```

```typescript
// tests/auth.setup.ts
import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate via credentials', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Password').fill(process.env.TEST_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Wait for the redirect after successful login
  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  // Save authentication state (cookies + localStorage)
  await page.context().storageState({ path: authFile });
});
```

```typescript
// tests/dashboard.spec.ts
import { test, expect } from '@playwright/test';

// This test runs with the authenticated storageState from the setup project
test('authenticated user sees dashboard', async ({ page }) => {
  await page.goto('/dashboard');

  // No login redirect -- auth cookies are already set
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByText('test@example.com')).toBeVisible();
});
```

**JavaScript**
```javascript
// tests/auth.setup.js
const { test: setup, expect } = require('@playwright/test');

const authFile = 'playwright/.auth/user.json';

setup('authenticate via credentials', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Password').fill(process.env.TEST_PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  await page.context().storageState({ path: authFile });
});
```

```javascript
// tests/dashboard.spec.js
const { test, expect } = require('@playwright/test');

test('authenticated user sees dashboard', async ({ page }) => {
  await page.goto('/dashboard');

  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByText('test@example.com')).toBeVisible();
});
```

## Framework-Specific Tips

### Dev Server vs Production Build

| Scenario | Command | Trade-off |
|---|---|---|
| Local development | `npm run dev` | Hot reload, fast iteration, but does not test production behavior (minification, optimization, middleware edge runtime) |
| CI pipeline | `npm run build && npm run start` | Tests the real production bundle; catches build errors, middleware edge cases |
| Quick smoke test | `npm run dev` in CI with `reuseExistingServer: false` | Faster CI but misses production-only bugs |

**Recommendation**: Use `npm run dev` locally for fast feedback. Use `npm run build && npm run start` in CI to test the real production artifact.

### Server Components Cannot Be Tested in Isolation

Next.js server components run on the server and produce HTML. Playwright tests the rendered output. You cannot import and render a server component in a Playwright test. Instead:

1. Test the final rendered HTML through navigation (`page.goto`)
2. Verify that server-fetched data appears on the page
3. Use API route tests to validate the data layer separately

### Handling Next.js Redirects

Next.js redirects (configured in `next.config.js`, middleware, or `redirect()` in server actions) are transparent to Playwright. After `page.goto()`, check `page.url()` to verify the final destination.

### Turbopack Compatibility

If using Turbopack (`next dev --turbopack`), update your `webServer.command`:

```typescript
webServer: {
  command: process.env.CI
    ? 'npm run build && npm run start'
    : 'npx next dev --turbopack',
  url: 'http://localhost:3000',
  reuseExistingServer: !process.env.CI,
},
```

### Multiple webServer Entries (Next.js + API Backend)

If your Next.js app consumes a separate backend API:

```typescript
webServer: [
  {
    command: 'npm run dev:api',
    url: 'http://localhost:4000/health',
    reuseExistingServer: !process.env.CI,
  },
  {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
],
```

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `await page.waitForTimeout(3000)` after navigation | Next.js client-side transitions are fast; arbitrary waits are wasteful and fragile | `await page.waitForURL('/expected-path')` or `await expect(locator).toBeVisible()` |
| Test `getServerSideProps` by importing and calling it directly | It depends on `context` (req/res) that Playwright cannot provide; it is a unit test concern | Navigate to the page and verify the rendered output |
| Mock your own API routes with `page.route()` | You are testing a fiction; your API handler may have bugs the mock hides | Let the real API route handle requests; mock only external services |
| Use `page.goto('http://localhost:3000/path')` with full URL | Breaks when port or host changes; ignores `baseURL` | Use `page.goto('/path')` and configure `baseURL` in config |
| Run `npm run build && npm run start` locally for every test run | Extremely slow feedback loop during development | Use `npm run dev` locally with `reuseExistingServer: true`; reserve production builds for CI |
| Test `next/image` by checking exact URL paths | `next/image` rewrites image URLs through `/_next/image`; paths change between dev and prod | Assert on `alt` text, visibility, `naturalWidth > 0`, and `srcset` existence |
| Skip `.env.test` and hardcode test values in config | Values scatter across config and test files; hard to maintain | Use `.env.test` for shared test values; `.env.test.local` for secrets |
| Test server actions by calling them as functions | Server actions are bound to the Next.js runtime; calling them outside a request context fails | Trigger server actions through their UI (form submissions, button clicks) |
| Ignore console errors during SSR tests | Hydration mismatches and server errors appear in the console and indicate real bugs | Listen for `page.on('console')` errors and fail the test if hydration warnings appear |

## Related

- [core/configuration.md](configuration.md) -- base Playwright configuration patterns including `webServer`
- [core/authentication.md](authentication.md) -- authentication setup projects and `storageState` reuse
- [core/api-testing.md](api-testing.md) -- testing API routes directly with `request` context
- [core/network-mocking.md](network-mocking.md) -- mocking external APIs that Next.js API routes call
- [core/when-to-mock.md](when-to-mock.md) -- when to mock vs hit real services
- [core/react.md](react.md) -- React-specific patterns that apply to Next.js client components
- [ci/ci-github-actions.md](../ci/ci-github-actions.md) -- CI setup with `npm run build` caching for Next.js
