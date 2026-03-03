# Testing Vue Apps with Playwright

> **When to use**: Testing Vue 3 applications, including composition API components, Pinia stores, Vue Router navigation, Nuxt.js apps, Teleport portals, and transitions. Covers E2E testing and experimental component testing with `@playwright/experimental-ct-vue`.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/locators.md](locators.md)

## Quick Reference

```bash
# Install Playwright in a Vue project
npm init playwright@latest

# Install component testing (experimental)
npm install -D @playwright/experimental-ct-vue

# Run E2E tests
npx playwright test

# Run component tests
npx playwright test -c playwright-ct.config.ts

# Debug a test with headed browser and inspector
npx playwright test tests/home.spec.ts --headed --debug
```

## Setup

### Playwright Config for Vue (Vite)

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: '**/*.spec.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? '50%' : undefined,

  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
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
      name: 'mobile',
      use: { ...devices['iPhone 14'] },
    },
  ],

  webServer: {
    command: process.env.CI
      ? 'npm run build && npx vite preview --port 5173'
      : 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  testMatch: '**/*.spec.js',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? '50%' : undefined,

  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
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
      name: 'mobile',
      use: { ...devices['iPhone 14'] },
    },
  ],

  webServer: {
    command: process.env.CI
      ? 'npm run build && npx vite preview --port 5173'
      : 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

### Component Testing Config

**TypeScript**
```typescript
// playwright-ct.config.ts
import { defineConfig, devices } from '@playwright/experimental-ct-vue';

export default defineConfig({
  testDir: './tests/components',
  testMatch: '**/*.ct.ts',

  use: {
    trace: 'on-first-retry',
    ctPort: 3100,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
```

**JavaScript**
```javascript
// playwright-ct.config.js
const { defineConfig, devices } = require('@playwright/experimental-ct-vue');

module.exports = defineConfig({
  testDir: './tests/components',
  testMatch: '**/*.ct.js',

  use: {
    trace: 'on-first-retry',
    ctPort: 3100,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
```

### Nuxt.js Setup

Nuxt requires a build step before testing and uses port 3000 by default.

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: '**/*.spec.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,

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
  ],

  webServer: {
    command: process.env.CI
      ? 'npx nuxi build && npx nuxi preview'
      : 'npx nuxi dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      NUXT_PUBLIC_API_BASE: 'http://localhost:3000/api',
    },
  },
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  testMatch: '**/*.spec.js',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,

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
  ],

  webServer: {
    command: process.env.CI
      ? 'npx nuxi build && npx nuxi preview'
      : 'npx nuxi dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      NUXT_PUBLIC_API_BASE: 'http://localhost:3000/api',
    },
  },
});
```

## Patterns

### Component Testing with `@playwright/experimental-ct-vue`

**Use when**: Testing complex interactive Vue components in isolation -- data tables, form components, custom select dropdowns, rich editors. The component needs a real browser but not a full application.
**Avoid when**: The component depends heavily on Pinia stores, Vue Router, or backend data. Use E2E tests instead, or provide the dependencies in your component test setup.

**TypeScript**
```typescript
// tests/components/Counter.ct.ts
import { test, expect } from '@playwright/experimental-ct-vue';
import Counter from '../../src/components/Counter.vue';

test('renders with initial count and increments', async ({ mount }) => {
  const component = await mount(Counter, {
    props: {
      initialCount: 0,
    },
  });

  await expect(component.getByText('Count: 0')).toBeVisible();
  await component.getByRole('button', { name: 'Increment' }).click();
  await expect(component.getByText('Count: 1')).toBeVisible();
});

test('emits update event when count changes', async ({ mount }) => {
  const emittedValues: number[] = [];
  const component = await mount(Counter, {
    props: {
      initialCount: 5,
    },
    on: {
      update: (value: number) => emittedValues.push(value),
    },
  });

  await component.getByRole('button', { name: 'Increment' }).click();
  await component.getByRole('button', { name: 'Increment' }).click();

  expect(emittedValues).toEqual([6, 7]);
});

test('respects max prop', async ({ mount }) => {
  const component = await mount(Counter, {
    props: {
      initialCount: 9,
      max: 10,
    },
  });

  await component.getByRole('button', { name: 'Increment' }).click();
  await expect(component.getByText('Count: 10')).toBeVisible();

  // At max -- button should be disabled
  await expect(component.getByRole('button', { name: 'Increment' })).toBeDisabled();
});

test('renders with slot content', async ({ mount }) => {
  const component = await mount(Counter, {
    props: { initialCount: 0 },
    slots: {
      default: '<span class="custom-label">Items in cart</span>',
    },
  });

  await expect(component.getByText('Items in cart')).toBeVisible();
});
```

**JavaScript**
```javascript
// tests/components/Counter.ct.js
const { test, expect } = require('@playwright/experimental-ct-vue');
const Counter = require('../../src/components/Counter.vue');

test('renders with initial count and increments', async ({ mount }) => {
  const component = await mount(Counter, {
    props: {
      initialCount: 0,
    },
  });

  await expect(component.getByText('Count: 0')).toBeVisible();
  await component.getByRole('button', { name: 'Increment' }).click();
  await expect(component.getByText('Count: 1')).toBeVisible();
});

test('emits update event when count changes', async ({ mount }) => {
  const emittedValues = [];
  const component = await mount(Counter, {
    props: {
      initialCount: 5,
    },
    on: {
      update: (value) => emittedValues.push(value),
    },
  });

  await component.getByRole('button', { name: 'Increment' }).click();
  await component.getByRole('button', { name: 'Increment' }).click();

  expect(emittedValues).toEqual([6, 7]);
});

test('renders with slot content', async ({ mount }) => {
  const component = await mount(Counter, {
    props: { initialCount: 0 },
    slots: {
      default: '<span class="custom-label">Items in cart</span>',
    },
  });

  await expect(component.getByText('Items in cart')).toBeVisible();
});
```

### Testing Pinia Stores Through the UI

**Use when**: Verifying that Pinia stores produce the correct UI behavior. Playwright tests the rendered output, not the store directly. If the UI is correct, the store is correct.
**Avoid when**: Testing pure store logic (getters, actions with no UI side effect) -- use unit tests with Vitest for that.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Pinia cart store (tested through UI)', () => {
  test('adding items updates the cart across the app', async ({ page }) => {
    await page.goto('/products');

    const cartBadge = page.getByTestId('cart-count');

    // Initially empty
    await expect(cartBadge).toHaveText('0');

    // Add first item -- Pinia store action is triggered
    await page.getByRole('listitem')
      .filter({ hasText: 'Vue T-Shirt' })
      .getByRole('button', { name: 'Add to cart' })
      .click();
    await expect(cartBadge).toHaveText('1');

    // Add second item
    await page.getByRole('listitem')
      .filter({ hasText: 'Pinia Sticker Pack' })
      .getByRole('button', { name: 'Add to cart' })
      .click();
    await expect(cartBadge).toHaveText('2');

    // Navigate to cart page -- store state persists
    await page.getByRole('link', { name: 'Cart' }).click();
    await page.waitForURL('/cart');

    await expect(page.getByText('Vue T-Shirt')).toBeVisible();
    await expect(page.getByText('Pinia Sticker Pack')).toBeVisible();
    await expect(page.getByText('Total: $29.98')).toBeVisible();
  });

  test('removing items from cart updates total', async ({ page }) => {
    // Navigate to a pre-populated cart (seed via API or navigate through adding items)
    await page.goto('/products');
    await page.getByRole('listitem')
      .filter({ hasText: 'Vue T-Shirt' })
      .getByRole('button', { name: 'Add to cart' })
      .click();

    await page.getByRole('link', { name: 'Cart' }).click();
    await page.waitForURL('/cart');

    await page.getByRole('button', { name: 'Remove Vue T-Shirt' }).click();

    await expect(page.getByText('Your cart is empty')).toBeVisible();
    await expect(page.getByTestId('cart-count')).toHaveText('0');
  });

  test('store persists after page reload when using pinia-plugin-persistedstate', async ({ page }) => {
    await page.goto('/products');

    await page.getByRole('listitem')
      .filter({ hasText: 'Vue T-Shirt' })
      .getByRole('button', { name: 'Add to cart' })
      .click();

    // Reload the page -- persisted store should restore state
    await page.reload();

    await expect(page.getByTestId('cart-count')).toHaveText('1');
  });
});

test.describe('Pinia auth store (tested through UI)', () => {
  test('login updates auth state across all components', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('link', { name: 'Sign in' })).toBeVisible();

    await page.getByRole('link', { name: 'Sign in' }).click();
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign in' }).click();

    await page.waitForURL('/dashboard');

    // Header updates (uses auth store)
    await expect(page.getByText('user@example.com')).toBeVisible();
    // Navigation updates (uses auth store for conditional routes)
    await expect(page.getByRole('link', { name: 'Admin' })).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Pinia cart store (tested through UI)', () => {
  test('adding items updates the cart across the app', async ({ page }) => {
    await page.goto('/products');

    const cartBadge = page.getByTestId('cart-count');
    await expect(cartBadge).toHaveText('0');

    await page.getByRole('listitem')
      .filter({ hasText: 'Vue T-Shirt' })
      .getByRole('button', { name: 'Add to cart' })
      .click();
    await expect(cartBadge).toHaveText('1');

    await page.getByRole('listitem')
      .filter({ hasText: 'Pinia Sticker Pack' })
      .getByRole('button', { name: 'Add to cart' })
      .click();
    await expect(cartBadge).toHaveText('2');

    await page.getByRole('link', { name: 'Cart' }).click();
    await page.waitForURL('/cart');

    await expect(page.getByText('Vue T-Shirt')).toBeVisible();
    await expect(page.getByText('Pinia Sticker Pack')).toBeVisible();
  });

  test('store persists after page reload when using pinia-plugin-persistedstate', async ({ page }) => {
    await page.goto('/products');

    await page.getByRole('listitem')
      .filter({ hasText: 'Vue T-Shirt' })
      .getByRole('button', { name: 'Add to cart' })
      .click();

    await page.reload();
    await expect(page.getByTestId('cart-count')).toHaveText('1');
  });
});
```

### Testing Vue Router Navigation

**Use when**: Testing client-side routing with Vue Router. Verify route transitions, navigation guards, URL parameters, and browser history behavior.
**Avoid when**: Testing Nuxt.js file-based routing -- the patterns are similar but Nuxt has additional server-side concerns.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Vue Router navigation', () => {
  test('client-side navigation does not cause full page reload', async ({ page }) => {
    await page.goto('/');

    await page.evaluate(() => {
      (window as any).__testMarker = 'no-reload';
    });

    await page.getByRole('link', { name: 'Products' }).click();
    await page.waitForURL('/products');

    const marker = await page.evaluate(() => (window as any).__testMarker);
    expect(marker).toBe('no-reload');
  });

  test('dynamic route params render correct content', async ({ page }) => {
    await page.goto('/products/42');

    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await expect(page.getByText('Product #42')).toBeVisible();
  });

  test('navigation guard redirects unauthenticated users', async ({ page }) => {
    // Visit a route guarded by router.beforeEach
    await page.goto('/admin/users');

    // Guard should redirect to login
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  });

  test('named routes and nested views render correctly', async ({ page }) => {
    await page.goto('/settings');

    // Parent layout
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
    await expect(page.getByRole('navigation', { name: 'Settings' })).toBeVisible();

    // Default child route
    await expect(page.getByRole('heading', { name: 'General', level: 2 })).toBeVisible();

    // Navigate to sibling child route
    await page.getByRole('link', { name: 'Notifications' }).click();
    await page.waitForURL('/settings/notifications');

    // Parent layout persists, child content changes
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Notifications', level: 2 })).toBeVisible();
  });

  test('browser back/forward works with Vue Router', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: 'Products' }).click();
    await page.waitForURL('/products');
    await page.getByRole('link', { name: 'About' }).click();
    await page.waitForURL('/about');

    await page.goBack();
    await expect(page).toHaveURL(/\/products/);

    await page.goBack();
    await expect(page).toHaveURL(/\/$/);

    await page.goForward();
    await expect(page).toHaveURL(/\/products/);
  });

  test('query parameters update reactive computed properties', async ({ page }) => {
    await page.goto('/products?sort=price-asc&category=electronics');

    await expect(page.getByRole('heading', { name: 'Electronics' })).toBeVisible();

    // Change sort via UI (updates route query params)
    await page.getByRole('combobox', { name: 'Sort by' }).selectOption('name-asc');
    await expect(page).toHaveURL(/sort=name-asc/);
  });

  test('404 catch-all route displays not found page', async ({ page }) => {
    await page.goto('/this-page-does-not-exist');

    await expect(page.getByRole('heading', { name: 'Page Not Found' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Go home' })).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Vue Router navigation', () => {
  test('client-side navigation does not cause full page reload', async ({ page }) => {
    await page.goto('/');

    await page.evaluate(() => {
      window.__testMarker = 'no-reload';
    });

    await page.getByRole('link', { name: 'Products' }).click();
    await page.waitForURL('/products');

    const marker = await page.evaluate(() => window.__testMarker);
    expect(marker).toBe('no-reload');
  });

  test('dynamic route params render correct content', async ({ page }) => {
    await page.goto('/products/42');

    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await expect(page.getByText('Product #42')).toBeVisible();
  });

  test('navigation guard redirects unauthenticated users', async ({ page }) => {
    await page.goto('/admin/users');

    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  });

  test('browser back/forward works with Vue Router', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: 'Products' }).click();
    await page.waitForURL('/products');
    await page.getByRole('link', { name: 'About' }).click();
    await page.waitForURL('/about');

    await page.goBack();
    await expect(page).toHaveURL(/\/products/);

    await page.goBack();
    await expect(page).toHaveURL(/\/$/);
  });
});
```

### Testing Teleport (Portals)

**Use when**: Testing components rendered via Vue's `<Teleport>` -- modals, notifications, overlay menus. Teleport moves DOM elements to a different location (often `body`), but Playwright sees the entire document.
**Avoid when**: The component is not teleported -- it renders inline in its parent.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Teleport components', () => {
  test('modal teleported to body is visible and interactive', async ({ page }) => {
    await page.goto('/products');

    await page.getByRole('button', { name: 'Delete' }).first().click();

    // Modal is teleported to <body> with <Teleport to="body">
    // Playwright sees it like any other element
    const modal = page.getByRole('dialog', { name: 'Confirm deletion' });
    await expect(modal).toBeVisible();

    await modal.getByRole('button', { name: 'Cancel' }).click();
    await expect(modal).toBeHidden();
  });

  test('teleported notification appears above all content', async ({ page }) => {
    await page.goto('/settings');

    await page.getByRole('button', { name: 'Save' }).click();

    // Notification teleported to #notifications container
    const notification = page.getByRole('alert');
    await expect(notification).toBeVisible();
    await expect(notification).toContainText('Settings saved');

    // Auto-dismiss
    await expect(notification).toBeHidden({ timeout: 10_000 });
  });

  test('teleported dropdown closes on outside click', async ({ page }) => {
    await page.goto('/dashboard');

    await page.getByRole('button', { name: 'User menu' }).click();

    const menu = page.getByRole('menu');
    await expect(menu).toBeVisible();

    // Click outside the menu
    await page.locator('body').click({ position: { x: 10, y: 10 } });
    await expect(menu).toBeHidden();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Teleport components', () => {
  test('modal teleported to body is visible and interactive', async ({ page }) => {
    await page.goto('/products');

    await page.getByRole('button', { name: 'Delete' }).first().click();

    const modal = page.getByRole('dialog', { name: 'Confirm deletion' });
    await expect(modal).toBeVisible();

    await modal.getByRole('button', { name: 'Cancel' }).click();
    await expect(modal).toBeHidden();
  });

  test('teleported notification appears above all content', async ({ page }) => {
    await page.goto('/settings');

    await page.getByRole('button', { name: 'Save' }).click();

    const notification = page.getByRole('alert');
    await expect(notification).toBeVisible();
    await expect(notification).toContainText('Settings saved');

    await expect(notification).toBeHidden({ timeout: 10_000 });
  });

  test('teleported dropdown closes on outside click', async ({ page }) => {
    await page.goto('/dashboard');

    await page.getByRole('button', { name: 'User menu' }).click();

    const menu = page.getByRole('menu');
    await expect(menu).toBeVisible();

    await page.locator('body').click({ position: { x: 10, y: 10 } });
    await expect(menu).toBeHidden();
  });
});
```

### Testing Transitions and Animations

**Use when**: Verifying that Vue `<Transition>` and `<TransitionGroup>` components work correctly -- elements appear, disappear, and reorder with expected behavior. Focus on the end state, not the animation itself.
**Avoid when**: Testing the exact CSS animation keyframes -- visual regression testing is better for pixel-level validation.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('transitions', () => {
  test('list items animate in when added', async ({ page }) => {
    await page.goto('/todo');

    await page.getByRole('textbox', { name: 'New task' }).fill('Buy groceries');
    await page.getByRole('button', { name: 'Add' }).click();

    // The item should be visible after the enter transition completes
    // Playwright auto-waits for visibility, handling the transition automatically
    await expect(page.getByText('Buy groceries')).toBeVisible();
  });

  test('deleted items animate out and are removed from DOM', async ({ page }) => {
    await page.goto('/todo');

    // Add an item first
    await page.getByRole('textbox', { name: 'New task' }).fill('Temporary task');
    await page.getByRole('button', { name: 'Add' }).click();
    await expect(page.getByText('Temporary task')).toBeVisible();

    // Delete it
    await page.getByRole('listitem')
      .filter({ hasText: 'Temporary task' })
      .getByRole('button', { name: 'Delete' })
      .click();

    // After the leave transition, the element should be gone
    await expect(page.getByText('Temporary task')).toBeHidden();
  });

  test('page transition completes between routes', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('link', { name: 'About' }).click();
    await page.waitForURL('/about');

    // After the route transition animation, content should be visible
    await expect(page.getByRole('heading', { name: 'About' })).toBeVisible();
  });

  test('disable animations for faster, more reliable tests', async ({ page }) => {
    // Disable all CSS animations and transitions for deterministic testing
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `,
    });

    await page.goto('/todo');

    await page.getByRole('textbox', { name: 'New task' }).fill('Instant task');
    await page.getByRole('button', { name: 'Add' }).click();

    // With animations disabled, elements appear/disappear instantly
    await expect(page.getByText('Instant task')).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('transitions', () => {
  test('list items animate in when added', async ({ page }) => {
    await page.goto('/todo');

    await page.getByRole('textbox', { name: 'New task' }).fill('Buy groceries');
    await page.getByRole('button', { name: 'Add' }).click();

    await expect(page.getByText('Buy groceries')).toBeVisible();
  });

  test('deleted items animate out and are removed from DOM', async ({ page }) => {
    await page.goto('/todo');

    await page.getByRole('textbox', { name: 'New task' }).fill('Temporary task');
    await page.getByRole('button', { name: 'Add' }).click();
    await expect(page.getByText('Temporary task')).toBeVisible();

    await page.getByRole('listitem')
      .filter({ hasText: 'Temporary task' })
      .getByRole('button', { name: 'Delete' })
      .click();

    await expect(page.getByText('Temporary task')).toBeHidden();
  });

  test('disable animations for faster, more reliable tests', async ({ page }) => {
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `,
    });

    await page.goto('/todo');

    await page.getByRole('textbox', { name: 'New task' }).fill('Instant task');
    await page.getByRole('button', { name: 'Add' }).click();

    await expect(page.getByText('Instant task')).toBeVisible();
  });
});
```

### Testing Composition API Components

**Use when**: Testing components built with the Vue 3 Composition API (`<script setup>`, `setup()` function). From Playwright's perspective, Composition API and Options API components are identical -- you test the rendered output.
**Avoid when**: You want to test composable functions in isolation -- use Vitest for that.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('composition API patterns', () => {
  test('computed properties update the UI reactively', async ({ page }) => {
    await page.goto('/calculator');

    await page.getByLabel('Price').fill('100');
    await page.getByLabel('Quantity').fill('3');

    // Computed total should update reactively
    await expect(page.getByTestId('total')).toHaveText('$300.00');

    // Apply discount
    await page.getByLabel('Discount (%)').fill('10');
    await expect(page.getByTestId('total')).toHaveText('$270.00');
  });

  test('watcher triggers side effect on value change', async ({ page }) => {
    await page.goto('/settings');

    // Changing the language triggers a watcher that reloads translations
    await page.getByRole('combobox', { name: 'Language' }).selectOption('fr');

    // Watcher fetches French translations -- UI updates
    await expect(page.getByRole('heading', { name: 'Parametres' })).toBeVisible();
  });

  test('composable hook (useSearch) provides debounced search', async ({ page }) => {
    await page.goto('/products');

    const searchInput = page.getByRole('textbox', { name: 'Search products' });
    await searchInput.pressSequentially('vue stickers', { delay: 50 });

    // useSearch composable debounces and fetches results
    await expect(page.getByRole('listitem')).toHaveCount(3);
    await expect(page.getByText('Vue Sticker Pack')).toBeVisible();
  });

  test('provide/inject context works across component tree', async ({ page }) => {
    await page.goto('/dashboard');

    // Theme is provided at the app root and injected in child components
    await page.getByRole('switch', { name: 'Dark mode' }).click();

    // All components using inject('theme') should update
    await expect(page.locator('body')).toHaveClass(/dark/);
    await expect(page.getByRole('navigation')).toHaveCSS('background-color', /rgb\(30/);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('composition API patterns', () => {
  test('computed properties update the UI reactively', async ({ page }) => {
    await page.goto('/calculator');

    await page.getByLabel('Price').fill('100');
    await page.getByLabel('Quantity').fill('3');

    await expect(page.getByTestId('total')).toHaveText('$300.00');

    await page.getByLabel('Discount (%)').fill('10');
    await expect(page.getByTestId('total')).toHaveText('$270.00');
  });

  test('watcher triggers side effect on value change', async ({ page }) => {
    await page.goto('/settings');

    await page.getByRole('combobox', { name: 'Language' }).selectOption('fr');
    await expect(page.getByRole('heading', { name: 'Parametres' })).toBeVisible();
  });

  test('composable hook (useSearch) provides debounced search', async ({ page }) => {
    await page.goto('/products');

    const searchInput = page.getByRole('textbox', { name: 'Search products' });
    await searchInput.pressSequentially('vue stickers', { delay: 50 });

    await expect(page.getByRole('listitem')).toHaveCount(3);
    await expect(page.getByText('Vue Sticker Pack')).toBeVisible();
  });
});
```

### Testing Nuxt.js Specific Patterns

**Use when**: Testing Nuxt 3 applications with server-side rendering, auto-imports, server routes (`/server/api/`), and middleware.
**Avoid when**: Testing a plain Vue SPA without Nuxt.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Nuxt-specific patterns', () => {
  test('SSR page renders server-fetched data', async ({ page }) => {
    await page.goto('/blog');

    // useFetch/useAsyncData runs on the server -- content is in the initial HTML
    await expect(page.getByRole('article')).toHaveCount(10);
    await expect(page.getByRole('article').first()).toContainText(/\w+/);
  });

  test('Nuxt server route returns correct data', async ({ request }) => {
    const response = await request.get('/api/products');

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toBeInstanceOf(Array);
    expect(body[0]).toHaveProperty('id');
  });

  test('Nuxt middleware redirects unauthenticated users', async ({ page }) => {
    await page.goto('/admin');

    // definePageMeta({ middleware: 'auth' }) in the page triggers redirect
    await expect(page).toHaveURL(/\/login/);
  });

  test('NuxtLink enables client-side navigation', async ({ page }) => {
    await page.goto('/');

    await page.evaluate(() => {
      (window as any).__testMarker = 'no-reload';
    });

    await page.getByRole('link', { name: 'Blog' }).click();
    await page.waitForURL('/blog');

    const marker = await page.evaluate(() => (window as any).__testMarker);
    expect(marker).toBe('no-reload');
  });

  test('useHead sets meta tags for SEO', async ({ page }) => {
    await page.goto('/blog/my-post');

    const title = await page.title();
    expect(title).toContain('My Post');

    const description = await page.locator('meta[name="description"]').getAttribute('content');
    expect(description).toBeTruthy();
    expect(description!.length).toBeGreaterThan(50);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Nuxt-specific patterns', () => {
  test('SSR page renders server-fetched data', async ({ page }) => {
    await page.goto('/blog');

    await expect(page.getByRole('article')).toHaveCount(10);
    await expect(page.getByRole('article').first()).toContainText(/\w+/);
  });

  test('Nuxt server route returns correct data', async ({ request }) => {
    const response = await request.get('/api/products');

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body).toBeInstanceOf(Array);
    expect(body[0]).toHaveProperty('id');
  });

  test('Nuxt middleware redirects unauthenticated users', async ({ page }) => {
    await page.goto('/admin');

    await expect(page).toHaveURL(/\/login/);
  });

  test('NuxtLink enables client-side navigation', async ({ page }) => {
    await page.goto('/');

    await page.evaluate(() => {
      window.__testMarker = 'no-reload';
    });

    await page.getByRole('link', { name: 'Blog' }).click();
    await page.waitForURL('/blog');

    const marker = await page.evaluate(() => window.__testMarker);
    expect(marker).toBe('no-reload');
  });
});
```

## Framework-Specific Tips

### Vue DevTools and Playwright

Vue DevTools is a browser extension. It does not interfere with Playwright tests since Playwright launches its own browser profile without extensions. Do not rely on Vue DevTools for debugging in CI -- use Playwright traces instead.

### Testing `v-model` Two-Way Binding

`v-model` on form inputs works through standard HTML events. Playwright's `fill()`, `check()`, `selectOption()` methods trigger the correct events automatically. No special handling is needed.

```typescript
// This works for any v-model input -- no special Vue handling needed
await page.getByLabel('Username').fill('janedoe');
await page.getByRole('checkbox', { name: 'Remember me' }).check();
await page.getByRole('combobox', { name: 'Role' }).selectOption('admin');
```

### Vue vs Nuxt: Configuration Differences

| Aspect | Vue 3 (Vite) | Nuxt 3 |
|---|---|---|
| Default port | `5173` | `3000` |
| Dev command | `npm run dev` (vite) | `npx nuxi dev` |
| Build + preview | `npm run build && npx vite preview` | `npx nuxi build && npx nuxi preview` |
| SSR | Optional (vue-server-renderer) | Built-in |
| API routes | External backend | `/server/api/` built-in |
| Environment variables | `VITE_*` prefix | `NUXT_PUBLIC_*` prefix for client, `NUXT_*` for server |
| File-based routing | No (uses vue-router config) | Yes (automatic from `/pages/`) |

### Component Testing: Providing Pinia and Router

When using `@playwright/experimental-ct-vue`, components that depend on Pinia or Vue Router need these dependencies provided. Configure the test wrapper:

```typescript
// playwright/index.ts (component testing setup)
import { beforeMount } from '@playwright/experimental-ct-vue/hooks';
import { createPinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';

beforeMount(async ({ app, hooksConfig }) => {
  // Install Pinia for all component tests
  const pinia = createPinia();
  app.use(pinia);

  // Install a minimal router if the component uses <RouterLink> or useRoute()
  if (hooksConfig?.routes) {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: hooksConfig.routes,
    });
    app.use(router);
  }
});
```

### Handling Vue Warnings in Tests

Vue emits runtime warnings (prop validation, missing components, etc.) that can indicate real issues:

```typescript
test('no Vue warnings during render', async ({ page }) => {
  const warnings: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'warning' && msg.text().includes('[Vue warn]')) {
      warnings.push(msg.text());
    }
  });

  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  expect(warnings).toEqual([]);
});
```

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `page.evaluate(() => app.__vue_app__.config.globalProperties.$store)` | Accesses Vue internals; breaks on upgrades; tests implementation | Assert on the UI that state produces |
| `page.locator('[data-v-abc123]')` (scoped style hash) | Vue generates random scoped attribute hashes; changes on every build | Use `getByRole`, `getByText`, `getByTestId` |
| Import `.vue` files in E2E tests | E2E tests run in Node.js; `.vue` files need Vite/Webpack compilation | Use `@playwright/experimental-ct-vue` for component tests |
| `page.waitForTimeout(300)` to wait for transition to finish | Transition durations vary; arbitrary waits are fragile | `await expect(locator).toBeVisible()` auto-waits through transitions |
| Mock Pinia stores by patching `window.__pinia` | Fragile; depends on Pinia internals; may not trigger reactivity | Control state through UI interactions or mock the API responses the store consumes |
| Test composables by calling them via `page.evaluate` | Composables rely on Vue's setup context; calling them outside a component fails | Test composables through the components that use them, or unit test with Vitest |
| Use `page.locator('.v-btn')` for Vuetify components | Vuetify class names are internal and change between versions | `page.getByRole('button', { name: 'Submit' })` works regardless of the component library |
| Skip testing keyboard navigation for custom components | Vue component libraries often have incomplete keyboard support | Test `Tab`, `Enter`, `Escape`, `ArrowDown/Up` on dropdowns, modals, tabs |
| Run Nuxt dev server in CI | Dev mode includes hot reload overhead, slower builds, development warnings | Use `npx nuxi build && npx nuxi preview` in CI |

## Related

- [core/locators.md](locators.md) -- locator strategies for any Vue component library (Vuetify, PrimeVue, Quasar)
- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- auto-waiting assertions for Vue reactivity
- [core/component-testing.md](component-testing.md) -- in-depth component testing patterns
- [core/forms-and-validation.md](forms-and-validation.md) -- form testing patterns for VeeValidate and FormKit
- [core/accessibility.md](accessibility.md) -- accessibility testing for Vue component libraries
- [core/test-architecture.md](test-architecture.md) -- when to use E2E vs component vs unit tests
- [core/nextjs.md](nextjs.md) -- comparison: Nuxt vs Next.js testing patterns
