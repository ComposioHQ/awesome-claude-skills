# Testing React Apps with Playwright

> **When to use**: Testing React applications built with Create React App (CRA), Vite, or custom bundlers. Covers E2E testing, experimental component testing, React Router navigation, form libraries, portals, error boundaries, and context/state verification through the UI.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/locators.md](locators.md)

## Quick Reference

```bash
# Install Playwright in a React project
npm init playwright@latest

# Install component testing (experimental)
npm install -D @playwright/experimental-ct-react

# Run E2E tests
npx playwright test

# Run component tests
npx playwright test -c playwright-ct.config.ts

# Debug a specific test
npx playwright test tests/login.spec.ts --headed --debug
```

## Setup

### Playwright Config for React (Vite)

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? '50%' : undefined,

  use: {
    baseURL: 'http://localhost:5173', // Vite default port
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
      ? 'npm run build && npx serve -s build -l 5173' // CRA
      // ? 'npm run build && npx vite preview --port 5173' // Vite
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
  testDir: './tests',
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
      ? 'npm run build && npx serve -s build -l 5173'
      : 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

### Component Testing Config

Component testing mounts individual React components in a real browser without a full dev server. This is experimental but useful for testing complex components in isolation.

**TypeScript**
```typescript
// playwright-ct.config.ts
import { defineConfig, devices } from '@playwright/experimental-ct-react';

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
const { defineConfig, devices } = require('@playwright/experimental-ct-react');

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

## Patterns

### Component Testing with `@playwright/experimental-ct-react`

**Use when**: Testing complex interactive components in isolation -- data tables, form wizards, rich text editors, dropdowns with keyboard navigation. The component needs a real browser (not jsdom) but not a full application.
**Avoid when**: The component behavior depends heavily on backend data or routing context. Use E2E tests instead.

**TypeScript**
```typescript
// tests/components/Counter.ct.ts
import { test, expect } from '@playwright/experimental-ct-react';
import Counter from '../../src/components/Counter';

test('increments count on button click', async ({ mount }) => {
  const component = await mount(<Counter initialCount={0} />);

  await expect(component.getByText('Count: 0')).toBeVisible();
  await component.getByRole('button', { name: 'Increment' }).click();
  await expect(component.getByText('Count: 1')).toBeVisible();
});

test('decrements count on button click', async ({ mount }) => {
  const component = await mount(<Counter initialCount={5} />);

  await component.getByRole('button', { name: 'Decrement' }).click();
  await expect(component.getByText('Count: 4')).toBeVisible();
});

test('calls onChange callback when count changes', async ({ mount }) => {
  const values: number[] = [];
  const component = await mount(
    <Counter initialCount={0} onChange={(val) => values.push(val)} />
  );

  await component.getByRole('button', { name: 'Increment' }).click();
  await component.getByRole('button', { name: 'Increment' }).click();

  expect(values).toEqual([1, 2]);
});

test('disables decrement at zero when min is set', async ({ mount }) => {
  const component = await mount(<Counter initialCount={0} min={0} />);

  await expect(component.getByRole('button', { name: 'Decrement' })).toBeDisabled();
});
```

**JavaScript**
```javascript
// tests/components/Counter.ct.js
const { test, expect } = require('@playwright/experimental-ct-react');
const Counter = require('../../src/components/Counter');

test('increments count on button click', async ({ mount }) => {
  const component = await mount(<Counter initialCount={0} />);

  await expect(component.getByText('Count: 0')).toBeVisible();
  await component.getByRole('button', { name: 'Increment' }).click();
  await expect(component.getByText('Count: 1')).toBeVisible();
});

test('decrements count on button click', async ({ mount }) => {
  const component = await mount(<Counter initialCount={5} />);

  await component.getByRole('button', { name: 'Decrement' }).click();
  await expect(component.getByText('Count: 4')).toBeVisible();
});

test('calls onChange callback when count changes', async ({ mount }) => {
  const values = [];
  const component = await mount(
    <Counter initialCount={0} onChange={(val) => values.push(val)} />
  );

  await component.getByRole('button', { name: 'Increment' }).click();
  await component.getByRole('button', { name: 'Increment' }).click();

  expect(values).toEqual([1, 2]);
});
```

### Testing Hooks Indirectly Through the UI

**Use when**: Verifying that custom hooks produce the correct UI behavior. Playwright cannot call hooks directly -- test them through the components that consume them.
**Avoid when**: The hook logic is pure computation with no UI side effects -- use a unit testing framework for that.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('useDebounce hook (tested through SearchInput)', () => {
  test('debounced search triggers after user stops typing', async ({ page }) => {
    await page.goto('/search');

    // Set up a response interceptor to track API calls
    const apiCalls: string[] = [];
    await page.route('**/api/search*', async (route) => {
      apiCalls.push(route.request().url());
      await route.continue();
    });

    // Type quickly -- the debounce hook should batch these
    await page.getByRole('textbox', { name: 'Search' }).pressSequentially('playwright', {
      delay: 50,
    });

    // Wait for results to appear (debounce has fired)
    await expect(page.getByRole('listitem')).toHaveCount(5);

    // The debounced hook should have made 1-2 API calls, not 10 (one per keystroke)
    expect(apiCalls.length).toBeLessThanOrEqual(2);
  });
});

test.describe('usePagination hook (tested through ProductList)', () => {
  test('pagination controls navigate between pages', async ({ page }) => {
    await page.goto('/products');

    await expect(page.getByText('Page 1 of 5')).toBeVisible();

    await page.getByRole('button', { name: 'Next page' }).click();
    await expect(page.getByText('Page 2 of 5')).toBeVisible();

    await page.getByRole('button', { name: 'Previous page' }).click();
    await expect(page.getByText('Page 1 of 5')).toBeVisible();

    // First page: previous should be disabled
    await expect(page.getByRole('button', { name: 'Previous page' })).toBeDisabled();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('useDebounce hook (tested through SearchInput)', () => {
  test('debounced search triggers after user stops typing', async ({ page }) => {
    await page.goto('/search');

    const apiCalls = [];
    await page.route('**/api/search*', async (route) => {
      apiCalls.push(route.request().url());
      await route.continue();
    });

    await page.getByRole('textbox', { name: 'Search' }).pressSequentially('playwright', {
      delay: 50,
    });

    await expect(page.getByRole('listitem')).toHaveCount(5);
    expect(apiCalls.length).toBeLessThanOrEqual(2);
  });
});

test.describe('usePagination hook (tested through ProductList)', () => {
  test('pagination controls navigate between pages', async ({ page }) => {
    await page.goto('/products');

    await expect(page.getByText('Page 1 of 5')).toBeVisible();

    await page.getByRole('button', { name: 'Next page' }).click();
    await expect(page.getByText('Page 2 of 5')).toBeVisible();

    await page.getByRole('button', { name: 'Previous page' }).click();
    await expect(page.getByText('Page 1 of 5')).toBeVisible();

    await expect(page.getByRole('button', { name: 'Previous page' })).toBeDisabled();
  });
});
```

### Testing Context and State Changes Through User Interactions

**Use when**: Verifying that React context (theme, auth, locale) and state management (Redux, Zustand, Jotai) produce correct UI changes.
**Avoid when**: You want to assert on the raw state object -- Playwright tests the UI, not internal state. If the UI is correct, the state is correct.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('theme context', () => {
  test('dark mode toggle changes the visual theme', async ({ page }) => {
    await page.goto('/settings');

    // Verify initial light mode
    const body = page.locator('body');
    await expect(body).not.toHaveClass(/dark/);

    // Toggle dark mode
    await page.getByRole('switch', { name: 'Dark mode' }).click();

    // Verify dark mode is applied
    await expect(body).toHaveClass(/dark/);

    // Verify the toggle state persists after navigation
    await page.getByRole('link', { name: 'Home' }).click();
    await expect(page.locator('body')).toHaveClass(/dark/);
  });
});

test.describe('shopping cart state', () => {
  test('adding items updates cart badge across pages', async ({ page }) => {
    await page.goto('/products');

    // Cart badge should show 0 or be hidden
    const cartBadge = page.getByTestId('cart-count');

    // Add first item
    await page.getByRole('listitem')
      .filter({ hasText: 'Running Shoes' })
      .getByRole('button', { name: 'Add to cart' })
      .click();
    await expect(cartBadge).toHaveText('1');

    // Add second item
    await page.getByRole('listitem')
      .filter({ hasText: 'Trail Jacket' })
      .getByRole('button', { name: 'Add to cart' })
      .click();
    await expect(cartBadge).toHaveText('2');

    // Navigate to a different page -- cart count persists (global state)
    await page.getByRole('link', { name: 'About' }).click();
    await expect(cartBadge).toHaveText('2');
  });
});

test.describe('auth context', () => {
  test('login updates the UI across all components consuming auth context', async ({ page }) => {
    await page.goto('/');

    // Unauthenticated state
    await expect(page.getByRole('link', { name: 'Sign in' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign out' })).toBeHidden();

    // Log in
    await page.getByRole('link', { name: 'Sign in' }).click();
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign in' }).click();

    // Authenticated state -- multiple components update
    await expect(page.getByRole('link', { name: 'Sign in' })).toBeHidden();
    await expect(page.getByText('user@example.com')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('theme context', () => {
  test('dark mode toggle changes the visual theme', async ({ page }) => {
    await page.goto('/settings');

    const body = page.locator('body');
    await expect(body).not.toHaveClass(/dark/);

    await page.getByRole('switch', { name: 'Dark mode' }).click();

    await expect(body).toHaveClass(/dark/);

    await page.getByRole('link', { name: 'Home' }).click();
    await expect(page.locator('body')).toHaveClass(/dark/);
  });
});

test.describe('shopping cart state', () => {
  test('adding items updates cart badge across pages', async ({ page }) => {
    await page.goto('/products');

    const cartBadge = page.getByTestId('cart-count');

    await page.getByRole('listitem')
      .filter({ hasText: 'Running Shoes' })
      .getByRole('button', { name: 'Add to cart' })
      .click();
    await expect(cartBadge).toHaveText('1');

    await page.getByRole('listitem')
      .filter({ hasText: 'Trail Jacket' })
      .getByRole('button', { name: 'Add to cart' })
      .click();
    await expect(cartBadge).toHaveText('2');

    await page.getByRole('link', { name: 'About' }).click();
    await expect(cartBadge).toHaveText('2');
  });
});
```

### Testing React Router Navigation

**Use when**: Testing client-side routing with React Router v6+. Verify route transitions, URL parameters, protected routes, and browser history behavior.
**Avoid when**: Your app uses server-side routing only (Next.js App Router handles this differently -- see [core/nextjs.md](nextjs.md)).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('React Router navigation', () => {
  test('client-side navigation does not cause full page reload', async ({ page }) => {
    await page.goto('/');

    // Store a marker in window to detect full reload
    await page.evaluate(() => {
      (window as any).__testMarker = 'no-reload';
    });

    // Navigate via a React Router Link
    await page.getByRole('link', { name: 'Products' }).click();
    await page.waitForURL('/products');

    // If the page fully reloaded, the marker would be gone
    const marker = await page.evaluate(() => (window as any).__testMarker);
    expect(marker).toBe('no-reload');
  });

  test('URL params update the page content', async ({ page }) => {
    await page.goto('/products?category=electronics');

    await expect(page.getByRole('heading', { name: 'Electronics' })).toBeVisible();

    // Change category via UI interaction (which updates the URL param)
    await page.getByRole('link', { name: 'Clothing' }).click();
    await page.waitForURL('/products?category=clothing');

    await expect(page.getByRole('heading', { name: 'Clothing' })).toBeVisible();
  });

  test('nested routes render parent and child layouts', async ({ page }) => {
    await page.goto('/settings/profile');

    // Parent layout (Settings)
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
    await expect(page.getByRole('navigation', { name: 'Settings' })).toBeVisible();

    // Child route (Profile)
    await expect(page.getByRole('heading', { name: 'Profile', level: 2 })).toBeVisible();

    // Navigate to sibling route
    await page.getByRole('link', { name: 'Notifications' }).click();
    await page.waitForURL('/settings/notifications');

    // Parent layout persists
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Notifications', level: 2 })).toBeVisible();
  });

  test('browser back button works with client-side routing', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: 'Products' }).click();
    await page.waitForURL('/products');
    await page.getByRole('link', { name: 'About' }).click();
    await page.waitForURL('/about');

    // Go back
    await page.goBack();
    await expect(page).toHaveURL(/\/products/);

    await page.goBack();
    await expect(page).toHaveURL(/\/$/);
  });

  test('protected route redirects unauthenticated users', async ({ page }) => {
    await page.goto('/admin');

    // React Router's protected route should redirect to login
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  });

  test('404 route shows not found page', async ({ page }) => {
    await page.goto('/this-route-does-not-exist');

    await expect(page.getByRole('heading', { name: 'Page Not Found' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Go home' })).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('React Router navigation', () => {
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

  test('URL params update the page content', async ({ page }) => {
    await page.goto('/products?category=electronics');

    await expect(page.getByRole('heading', { name: 'Electronics' })).toBeVisible();

    await page.getByRole('link', { name: 'Clothing' }).click();
    await page.waitForURL('/products?category=clothing');

    await expect(page.getByRole('heading', { name: 'Clothing' })).toBeVisible();
  });

  test('browser back button works with client-side routing', async ({ page }) => {
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

  test('protected route redirects unauthenticated users', async ({ page }) => {
    await page.goto('/admin');

    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  });
});
```

### Testing Form Libraries (React Hook Form, Formik)

**Use when**: Testing forms built with react-hook-form, Formik, or similar libraries. Playwright interacts with the DOM, so the form library is transparent -- test the user experience, not the library internals.
**Avoid when**: Testing the form library itself. You are testing YOUR form behavior.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('registration form (react-hook-form)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register');
  });

  test('shows validation errors on submit with empty fields', async ({ page }) => {
    await page.getByRole('button', { name: 'Create account' }).click();

    // react-hook-form shows errors after submit attempt
    await expect(page.getByText('Email is required')).toBeVisible();
    await expect(page.getByText('Password is required')).toBeVisible();
  });

  test('shows inline validation on blur', async ({ page }) => {
    const emailInput = page.getByLabel('Email');
    await emailInput.fill('not-an-email');
    await emailInput.blur();

    // react-hook-form with mode: 'onBlur' validates immediately
    await expect(page.getByText('Invalid email address')).toBeVisible();
  });

  test('password requirements update in real time', async ({ page }) => {
    const passwordInput = page.getByLabel('Password', { exact: true });

    await passwordInput.fill('short');
    await expect(page.getByText('At least 8 characters')).toHaveClass(/text-red/);

    await passwordInput.fill('longenough');
    await expect(page.getByText('At least 8 characters')).toHaveClass(/text-green/);

    await passwordInput.fill('LongEnough1!');
    await expect(page.getByText('Contains uppercase')).toHaveClass(/text-green/);
    await expect(page.getByText('Contains number')).toHaveClass(/text-green/);
    await expect(page.getByText('Contains special character')).toHaveClass(/text-green/);
  });

  test('successful registration submits form and redirects', async ({ page }) => {
    await page.getByLabel('Full name').fill('Jane Doe');
    await page.getByLabel('Email').fill('jane@example.com');
    await page.getByLabel('Password', { exact: true }).fill('Str0ng!Pass');
    await page.getByLabel('Confirm password').fill('Str0ng!Pass');
    await page.getByLabel('I agree to the terms').check();

    await page.getByRole('button', { name: 'Create account' }).click();

    await page.waitForURL('/dashboard');
    await expect(page.getByText('Welcome, Jane')).toBeVisible();
  });

  test('disables submit button while form is submitting', async ({ page }) => {
    // Slow down the API to observe the submitting state
    await page.route('**/api/register', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ id: 1, email: 'jane@example.com' }),
      });
    });

    await page.getByLabel('Full name').fill('Jane Doe');
    await page.getByLabel('Email').fill('jane@example.com');
    await page.getByLabel('Password', { exact: true }).fill('Str0ng!Pass');
    await page.getByLabel('Confirm password').fill('Str0ng!Pass');
    await page.getByLabel('I agree to the terms').check();

    await page.getByRole('button', { name: 'Create account' }).click();

    // Button should show loading state
    await expect(page.getByRole('button', { name: /Creating|Loading|Submitting/ })).toBeDisabled();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('registration form (react-hook-form)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register');
  });

  test('shows validation errors on submit with empty fields', async ({ page }) => {
    await page.getByRole('button', { name: 'Create account' }).click();

    await expect(page.getByText('Email is required')).toBeVisible();
    await expect(page.getByText('Password is required')).toBeVisible();
  });

  test('shows inline validation on blur', async ({ page }) => {
    const emailInput = page.getByLabel('Email');
    await emailInput.fill('not-an-email');
    await emailInput.blur();

    await expect(page.getByText('Invalid email address')).toBeVisible();
  });

  test('successful registration submits form and redirects', async ({ page }) => {
    await page.getByLabel('Full name').fill('Jane Doe');
    await page.getByLabel('Email').fill('jane@example.com');
    await page.getByLabel('Password', { exact: true }).fill('Str0ng!Pass');
    await page.getByLabel('Confirm password').fill('Str0ng!Pass');
    await page.getByLabel('I agree to the terms').check();

    await page.getByRole('button', { name: 'Create account' }).click();

    await page.waitForURL('/dashboard');
    await expect(page.getByText('Welcome, Jane')).toBeVisible();
  });
});
```

### Testing React Portals (Modals, Tooltips, Dropdowns)

**Use when**: Testing components rendered via `ReactDOM.createPortal()` -- modals, dialogs, tooltips, dropdown menus, toast notifications. These render outside the parent DOM hierarchy, but Playwright sees the full document.
**Avoid when**: The component is not a portal -- it renders inline.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('portals', () => {
  test('modal opens and is accessible', async ({ page }) => {
    await page.goto('/products');

    await page.getByRole('button', { name: 'Delete product' }).first().click();

    // Modal is rendered via a portal to document.body, but Playwright
    // sees it like any other element
    const modal = page.getByRole('dialog', { name: 'Confirm deletion' });
    await expect(modal).toBeVisible();

    // Verify focus is trapped inside the modal
    await expect(modal.getByRole('button', { name: 'Cancel' })).toBeFocused();

    // Verify backdrop/overlay blocks interaction with elements behind
    // (Playwright will auto-wait for the element to be actionable)
    await modal.getByRole('button', { name: 'Delete' }).click();
    await expect(modal).toBeHidden();
  });

  test('modal closes on Escape key', async ({ page }) => {
    await page.goto('/products');
    await page.getByRole('button', { name: 'Delete product' }).first().click();

    const modal = page.getByRole('dialog', { name: 'Confirm deletion' });
    await expect(modal).toBeVisible();

    await page.keyboard.press('Escape');
    await expect(modal).toBeHidden();
  });

  test('tooltip shows on hover and hides on leave', async ({ page }) => {
    await page.goto('/dashboard');

    const triggerButton = page.getByRole('button', { name: 'Info' });
    await triggerButton.hover();

    // Tooltip rendered via portal
    await expect(page.getByRole('tooltip')).toBeVisible();
    await expect(page.getByRole('tooltip')).toContainText('Click for more details');

    // Move mouse away
    await page.mouse.move(0, 0);
    await expect(page.getByRole('tooltip')).toBeHidden();
  });

  test('toast notifications stack and auto-dismiss', async ({ page }) => {
    await page.goto('/settings');

    // Trigger multiple toasts
    await page.getByRole('button', { name: 'Save' }).click();
    await expect(page.getByText('Settings saved')).toBeVisible();

    // Toast should auto-dismiss after a delay
    await expect(page.getByText('Settings saved')).toBeHidden({ timeout: 10_000 });
  });

  test('dropdown menu rendered via portal positions correctly', async ({ page }) => {
    await page.goto('/dashboard');

    await page.getByRole('button', { name: 'More actions' }).click();

    const menu = page.getByRole('menu');
    await expect(menu).toBeVisible();
    await expect(menu.getByRole('menuitem', { name: 'Edit' })).toBeVisible();
    await expect(menu.getByRole('menuitem', { name: 'Delete' })).toBeVisible();

    // Click a menu item
    await menu.getByRole('menuitem', { name: 'Edit' }).click();
    await expect(menu).toBeHidden();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('portals', () => {
  test('modal opens and is accessible', async ({ page }) => {
    await page.goto('/products');

    await page.getByRole('button', { name: 'Delete product' }).first().click();

    const modal = page.getByRole('dialog', { name: 'Confirm deletion' });
    await expect(modal).toBeVisible();
    await expect(modal.getByRole('button', { name: 'Cancel' })).toBeFocused();

    await modal.getByRole('button', { name: 'Delete' }).click();
    await expect(modal).toBeHidden();
  });

  test('modal closes on Escape key', async ({ page }) => {
    await page.goto('/products');
    await page.getByRole('button', { name: 'Delete product' }).first().click();

    const modal = page.getByRole('dialog', { name: 'Confirm deletion' });
    await expect(modal).toBeVisible();

    await page.keyboard.press('Escape');
    await expect(modal).toBeHidden();
  });

  test('tooltip shows on hover and hides on leave', async ({ page }) => {
    await page.goto('/dashboard');

    await page.getByRole('button', { name: 'Info' }).hover();
    await expect(page.getByRole('tooltip')).toBeVisible();

    await page.mouse.move(0, 0);
    await expect(page.getByRole('tooltip')).toBeHidden();
  });
});
```

### Testing Error Boundaries

**Use when**: Verifying that React error boundaries catch rendering errors gracefully and show fallback UI instead of a white screen.
**Avoid when**: You are testing error handling in event handlers or async code -- error boundaries only catch rendering errors.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('error boundaries', () => {
  test('error boundary shows fallback UI when child crashes', async ({ page }) => {
    // Capture console errors to verify the error was thrown
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/dashboard');

    // Trigger an action that causes a component to throw during render
    // (e.g., a component that crashes on specific data)
    await page.route('**/api/dashboard/widgets', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ widgets: null }), // null causes .map() to throw
      });
    });

    await page.reload();

    // Error boundary should catch the error and show fallback
    await expect(page.getByText('Something went wrong')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Try again' })).toBeVisible();

    // The rest of the page should still be functional
    await expect(page.getByRole('navigation', { name: 'Main' })).toBeVisible();
  });

  test('retry button in error boundary recovers the component', async ({ page }) => {
    let requestCount = 0;
    await page.route('**/api/dashboard/widgets', (route) => {
      requestCount++;
      if (requestCount === 1) {
        // First request: return bad data that crashes the component
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ widgets: null }),
        });
      } else {
        // Subsequent requests: return good data
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ widgets: [{ id: 1, name: 'Sales' }] }),
        });
      }
    });

    await page.goto('/dashboard');

    // Error boundary shows fallback
    await expect(page.getByText('Something went wrong')).toBeVisible();

    // Click retry -- component re-mounts with good data
    await page.getByRole('button', { name: 'Try again' }).click();

    // Component recovers
    await expect(page.getByText('Something went wrong')).toBeHidden();
    await expect(page.getByText('Sales')).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('error boundaries', () => {
  test('error boundary shows fallback UI when child crashes', async ({ page }) => {
    const consoleErrors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.route('**/api/dashboard/widgets', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ widgets: null }),
      });
    });

    await page.goto('/dashboard');

    await expect(page.getByText('Something went wrong')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Try again' })).toBeVisible();
    await expect(page.getByRole('navigation', { name: 'Main' })).toBeVisible();
  });

  test('retry button in error boundary recovers the component', async ({ page }) => {
    let requestCount = 0;
    await page.route('**/api/dashboard/widgets', (route) => {
      requestCount++;
      if (requestCount === 1) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ widgets: null }),
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ widgets: [{ id: 1, name: 'Sales' }] }),
        });
      }
    });

    await page.goto('/dashboard');

    await expect(page.getByText('Something went wrong')).toBeVisible();
    await page.getByRole('button', { name: 'Try again' }).click();

    await expect(page.getByText('Something went wrong')).toBeHidden();
    await expect(page.getByText('Sales')).toBeVisible();
  });
});
```

## Framework-Specific Tips

### CRA vs Vite: Key Differences

| Aspect | Create React App (CRA) | Vite |
|---|---|---|
| Default port | `3000` | `5173` |
| Build output | `build/` | `dist/` |
| Serve production build | `npx serve -s build -l 3000` | `npx vite preview --port 5173` |
| Environment variables | `REACT_APP_*` prefix | `VITE_*` prefix |
| Dev server start time | Slow (Webpack) | Fast (esbuild) |

Adjust your `webServer.command` and `baseURL` accordingly.

### React Strict Mode and Double Effects

React Strict Mode in development runs effects twice. This can cause unexpected behavior in tests (e.g., double API calls). Your tests should be resilient to this:

- Do not assert on exact API call counts in development mode
- If you test API call counts, run against a production build or account for double invocations

### Testing Suspense and Lazy Components

```typescript
// React.lazy() components show a fallback while loading
test('lazy-loaded route shows spinner then content', async ({ page }) => {
  await page.goto('/');

  // Navigate to a lazy route
  await page.getByRole('link', { name: 'Reports' }).click();

  // The reports module loads lazily -- you may briefly see a spinner
  // Playwright auto-waits for the final content
  await expect(page.getByRole('heading', { name: 'Reports' })).toBeVisible();
});
```

### Component Testing: When to Use It vs E2E

| Scenario | Use Component Testing | Use E2E |
|---|---|---|
| Complex dropdown with keyboard navigation | Yes -- test in isolation with mount() | Also yes -- verify it works within the page |
| Data table with sorting, filtering, pagination | Yes -- control props directly | Also yes -- verify API integration |
| Button that submits a form | No -- trivial in isolation | Yes -- test the full form flow |
| Theme toggle component | Yes -- verify visual changes | Also yes -- verify persistence |
| Login form connected to auth context | No -- too many dependencies | Yes -- test the real flow |

### Detecting Memory Leaks in Long-Running Tests

If your React app has unmounted component state updates (the "Can't perform a React state update on an unmounted component" warning), catch them:

```typescript
test('no state-update-on-unmounted warnings during navigation', async ({ page }) => {
  const warnings: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'warning' && msg.text().includes('unmounted')) {
      warnings.push(msg.text());
    }
  });

  // Rapid navigation to trigger unmount edge cases
  await page.goto('/dashboard');
  await page.getByRole('link', { name: 'Settings' }).click();
  await page.goBack();
  await page.getByRole('link', { name: 'Profile' }).click();
  await page.goBack();

  expect(warnings).toEqual([]);
});
```

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `page.evaluate(() => store.getState())` to assert Redux state | Couples tests to implementation; state shape changes break tests | Assert on the UI that the state produces: `expect(cartBadge).toHaveText('3')` |
| Import React components in E2E test files | E2E tests run in Node.js, not the browser; component imports fail | Use `@playwright/experimental-ct-react` for component testing, E2E for full-app tests |
| `page.waitForTimeout(500)` after React state changes | React batches updates; timing varies across machines | Use `expect(locator).toHaveText('new value')` which auto-retries |
| Test internal component state with `page.evaluate` | Fragile; breaks on refactors; tests implementation, not behavior | Interact through the UI and assert on visible output |
| Mock `useState` or `useEffect` in Playwright tests | Playwright runs in the browser context, not the React component tree | Let hooks run naturally; control inputs (API responses, props via component testing) |
| Use `page.locator('.MuiButton-root')` for Material UI | Class names change between MUI versions and are generated dynamically | `page.getByRole('button', { name: 'Submit' })` works regardless of the component library |
| Test every component with `@playwright/experimental-ct-react` | Overhead of browser mounting for simple components; duplicates unit tests | Use component testing for complex interactive widgets; unit tests for pure logic; E2E for flows |
| Skip testing keyboard navigation on custom components | Accessibility regressions are common in custom dropdowns, modals, tabs | Test `Tab`, `Enter`, `Escape`, `ArrowDown` interactions in component tests |
| Assert on React DevTools or `__REACT_FIBER__` internals | Internal React properties are not stable across versions | Only interact with and assert on the rendered DOM |

## Related

- [core/locators.md](locators.md) -- locator strategies that work with any React component library
- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- auto-waiting assertions for React state changes
- [core/forms-and-validation.md](forms-and-validation.md) -- form testing patterns applicable to react-hook-form and Formik
- [core/component-testing.md](component-testing.md) -- in-depth component testing guide
- [core/accessibility.md](accessibility.md) -- testing ARIA patterns in React component libraries
- [core/test-architecture.md](test-architecture.md) -- when to use E2E vs component vs unit tests
- [core/nextjs.md](nextjs.md) -- Next.js-specific patterns for React apps with SSR
