# Testing Angular Apps with Playwright

> **When to use**: Testing Angular applications -- reactive forms, Angular Material components, Angular Router navigation, lazy-loaded modules, signals, observables, and Zone.js-driven change detection. This guide covers E2E testing patterns specific to Angular behavior.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/locators.md](locators.md)

## Quick Reference

```bash
# Install Playwright in an Angular project
npm init playwright@latest

# Run tests with Angular dev server managed by Playwright
npx playwright test

# Run against a production build (recommended for CI)
npx playwright test --project=chromium

# Debug a single test
npx playwright test tests/home.spec.ts --headed --debug

# Generate tests with codegen
npx playwright codegen http://localhost:4200
```

## Setup

### Playwright Config for Angular

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  testMatch: '**/*.spec.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? '50%' : undefined,

  use: {
    baseURL: 'http://localhost:4200',
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
      ? 'npx ng build && npx http-server dist/your-app/browser -p 4200 -s'
      : 'npx ng serve',
    url: 'http://localhost:4200',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000, // Angular builds can be slow
  },
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './e2e',
  testMatch: '**/*.spec.js',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? '50%' : undefined,

  use: {
    baseURL: 'http://localhost:4200',
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
      ? 'npx ng build && npx http-server dist/your-app/browser -p 4200 -s'
      : 'npx ng serve',
    url: 'http://localhost:4200',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

### Angular CLI Integration

Angular projects that previously used Protractor can adopt Playwright as a direct replacement. The test directory conventionally lives at `e2e/` in Angular projects.

```
your-angular-app/
  src/
  e2e/
    tests/
      home.spec.ts
      auth.spec.ts
      products.spec.ts
    fixtures/
      auth.fixture.ts
  playwright.config.ts
  angular.json
  package.json
```

Add scripts to `package.json`:

```json
{
  "scripts": {
    "e2e": "playwright test",
    "e2e:headed": "playwright test --headed",
    "e2e:debug": "playwright test --debug",
    "e2e:report": "playwright show-report"
  }
}
```

### Environment Configuration

Angular uses `environment.ts` and `environment.prod.ts` for build-time configuration. For test-specific settings, use environment variables passed through the Playwright config.

**TypeScript**
```typescript
// playwright.config.ts (excerpt)
webServer: {
  command: process.env.CI
    ? 'npx ng build --configuration=production && npx http-server dist/your-app/browser -p 4200 -s'
    : 'npx ng serve --configuration=development',
  url: 'http://localhost:4200',
  reuseExistingServer: !process.env.CI,
  timeout: 120_000,
  env: {
    NG_APP_API_URL: 'http://localhost:4200/api',
  },
},
```

## Patterns

### Angular-Specific Locator Strategies

**Use when**: Targeting elements in Angular templates. Angular generates specific attribute patterns (`_ngcontent-*`, `_nghost-*`, `ng-reflect-*`) that you must avoid in locators. Always use semantic locators.
**Avoid when**: You are tempted to use `[_ngcontent-abc123]` or `[ng-reflect-model]` attributes -- they are internal and change on every build.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Angular locator strategies', () => {
  test('prefer role-based locators over Angular internals', async ({ page }) => {
    await page.goto('/dashboard');

    // GOOD: Role-based locators work with Angular Material and native HTML
    await page.getByRole('button', { name: 'Create project' }).click();
    await expect(page.getByRole('heading', { name: 'New Project' })).toBeVisible();

    // GOOD: Label-based for form fields
    await page.getByLabel('Project name').fill('My Project');

    // GOOD: Text-based for non-interactive content
    await expect(page.getByText('3 projects total')).toBeVisible();

    // BAD (never do this):
    // page.locator('[_ngcontent-abc]')  -- changes every build
    // page.locator('[ng-reflect-model]') -- debug attribute, stripped in prod
    // page.locator('app-dashboard .mat-card') -- component selector + internal class
  });

  test('use test IDs for complex Angular components', async ({ page }) => {
    await page.goto('/analytics');

    // Angular components with no semantic role need test IDs
    const chart = page.getByTestId('revenue-chart');
    await expect(chart).toBeVisible();

    // Configure the testIdAttribute if your team uses a different attribute
    // In playwright.config.ts: use: { testIdAttribute: 'data-cy' }
  });

  test('scope locators within Angular component boundaries', async ({ page }) => {
    await page.goto('/users');

    // Scope within a table to find specific rows
    const userTable = page.getByRole('table', { name: 'Users' });
    const adminRow = userTable.getByRole('row').filter({
      has: page.getByRole('cell', { name: 'Admin' }),
    });
    await adminRow.getByRole('button', { name: 'Edit' }).click();

    await expect(page.getByRole('dialog', { name: 'Edit User' })).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Angular locator strategies', () => {
  test('prefer role-based locators over Angular internals', async ({ page }) => {
    await page.goto('/dashboard');

    await page.getByRole('button', { name: 'Create project' }).click();
    await expect(page.getByRole('heading', { name: 'New Project' })).toBeVisible();

    await page.getByLabel('Project name').fill('My Project');
    await expect(page.getByText('3 projects total')).toBeVisible();
  });

  test('use test IDs for complex Angular components', async ({ page }) => {
    await page.goto('/analytics');

    const chart = page.getByTestId('revenue-chart');
    await expect(chart).toBeVisible();
  });

  test('scope locators within Angular component boundaries', async ({ page }) => {
    await page.goto('/users');

    const userTable = page.getByRole('table', { name: 'Users' });
    const adminRow = userTable.getByRole('row').filter({
      has: page.getByRole('cell', { name: 'Admin' }),
    });
    await adminRow.getByRole('button', { name: 'Edit' }).click();

    await expect(page.getByRole('dialog', { name: 'Edit User' })).toBeVisible();
  });
});
```

### Testing Reactive Forms

**Use when**: Testing Angular reactive forms (`FormGroup`, `FormControl`, `FormArray`). Playwright interacts with the rendered DOM, so reactive forms are transparent -- test the user experience.
**Avoid when**: Testing form validation logic in isolation -- use Angular TestBed unit tests for that.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('reactive forms', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register');
  });

  test('shows validation errors for invalid inputs', async ({ page }) => {
    // Touch and blur each field to trigger Angular's touched + dirty validators
    const emailInput = page.getByLabel('Email');
    await emailInput.click();
    await emailInput.blur();

    await expect(page.getByText('Email is required')).toBeVisible();

    await emailInput.fill('not-an-email');
    await emailInput.blur();

    await expect(page.getByText('Invalid email format')).toBeVisible();
  });

  test('cross-field validation (password match)', async ({ page }) => {
    await page.getByLabel('Password', { exact: true }).fill('Str0ng!Pass');
    await page.getByLabel('Confirm password').fill('different-password');
    await page.getByLabel('Confirm password').blur();

    await expect(page.getByText('Passwords do not match')).toBeVisible();

    // Fix the mismatch
    await page.getByLabel('Confirm password').fill('Str0ng!Pass');
    await page.getByLabel('Confirm password').blur();

    await expect(page.getByText('Passwords do not match')).toBeHidden();
  });

  test('dynamic FormArray -- add and remove items', async ({ page }) => {
    await page.goto('/profile/edit');

    // Add a phone number (FormArray push)
    await page.getByRole('button', { name: 'Add phone number' }).click();

    const phoneInputs = page.getByLabel(/Phone number/);
    await expect(phoneInputs).toHaveCount(2); // default + new one

    await phoneInputs.nth(1).fill('+1-555-0199');

    // Remove the first phone number
    await page.getByRole('button', { name: 'Remove phone 1' }).click();
    await expect(phoneInputs).toHaveCount(1);
    await expect(phoneInputs.first()).toHaveValue('+1-555-0199');
  });

  test('submit button disabled when form is invalid', async ({ page }) => {
    const submitButton = page.getByRole('button', { name: 'Create account' });

    // Form starts invalid -- button should be disabled
    await expect(submitButton).toBeDisabled();

    // Fill all required fields
    await page.getByLabel('Full name').fill('Jane Doe');
    await page.getByLabel('Email').fill('jane@example.com');
    await page.getByLabel('Password', { exact: true }).fill('Str0ng!Pass');
    await page.getByLabel('Confirm password').fill('Str0ng!Pass');
    await page.getByLabel('I agree to the terms').check();

    // Now the form is valid -- button should be enabled
    await expect(submitButton).toBeEnabled();
  });

  test('async validator shows loading state', async ({ page }) => {
    // Slow down the username availability check
    await page.route('**/api/check-username*', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ available: true }),
      });
    });

    await page.getByLabel('Username').fill('janedoe');
    await page.getByLabel('Username').blur();

    // Async validator fires -- shows a loading indicator
    await expect(page.getByTestId('username-checking')).toBeVisible();

    // After the check completes
    await expect(page.getByTestId('username-checking')).toBeHidden();
    await expect(page.getByText('Username is available')).toBeVisible();
  });

  test('form submission posts correct data', async ({ page }) => {
    let submittedData: Record<string, unknown> = {};
    await page.route('**/api/register', async (route) => {
      submittedData = route.request().postDataJSON();
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ id: 1 }),
      });
    });

    await page.getByLabel('Full name').fill('Jane Doe');
    await page.getByLabel('Email').fill('jane@example.com');
    await page.getByLabel('Password', { exact: true }).fill('Str0ng!Pass');
    await page.getByLabel('Confirm password').fill('Str0ng!Pass');
    await page.getByLabel('I agree to the terms').check();
    await page.getByRole('button', { name: 'Create account' }).click();

    expect(submittedData).toMatchObject({
      name: 'Jane Doe',
      email: 'jane@example.com',
    });
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('reactive forms', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register');
  });

  test('shows validation errors for invalid inputs', async ({ page }) => {
    const emailInput = page.getByLabel('Email');
    await emailInput.click();
    await emailInput.blur();

    await expect(page.getByText('Email is required')).toBeVisible();

    await emailInput.fill('not-an-email');
    await emailInput.blur();

    await expect(page.getByText('Invalid email format')).toBeVisible();
  });

  test('cross-field validation (password match)', async ({ page }) => {
    await page.getByLabel('Password', { exact: true }).fill('Str0ng!Pass');
    await page.getByLabel('Confirm password').fill('different-password');
    await page.getByLabel('Confirm password').blur();

    await expect(page.getByText('Passwords do not match')).toBeVisible();

    await page.getByLabel('Confirm password').fill('Str0ng!Pass');
    await page.getByLabel('Confirm password').blur();

    await expect(page.getByText('Passwords do not match')).toBeHidden();
  });

  test('submit button disabled when form is invalid', async ({ page }) => {
    const submitButton = page.getByRole('button', { name: 'Create account' });

    await expect(submitButton).toBeDisabled();

    await page.getByLabel('Full name').fill('Jane Doe');
    await page.getByLabel('Email').fill('jane@example.com');
    await page.getByLabel('Password', { exact: true }).fill('Str0ng!Pass');
    await page.getByLabel('Confirm password').fill('Str0ng!Pass');
    await page.getByLabel('I agree to the terms').check();

    await expect(submitButton).toBeEnabled();
  });
});
```

### Testing Angular Material Components

**Use when**: Testing apps using Angular Material (mat-button, mat-input, mat-select, mat-dialog, mat-table, etc.). Angular Material components use proper ARIA attributes, making them accessible to role-based locators.
**Avoid when**: Using CSS class selectors like `.mat-mdc-button` or `.mat-option` -- these change between Material versions.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Angular Material components', () => {
  test('mat-select dropdown', async ({ page }) => {
    await page.goto('/settings');

    // Angular Material select has role="combobox"
    await page.getByRole('combobox', { name: 'Theme' }).click();

    // Options appear in a CDK overlay (similar to a portal)
    await page.getByRole('option', { name: 'Dark' }).click();

    // Verify the selection
    await expect(page.getByRole('combobox', { name: 'Theme' })).toContainText('Dark');
  });

  test('mat-autocomplete with type-ahead', async ({ page }) => {
    await page.goto('/users/new');

    const roleInput = page.getByRole('combobox', { name: 'Role' });
    await roleInput.fill('adm');

    // Autocomplete suggestions appear in a CDK overlay
    await expect(page.getByRole('option', { name: 'Admin' })).toBeVisible();
    await expect(page.getByRole('option', { name: 'Administrator' })).toBeVisible();

    await page.getByRole('option', { name: 'Admin' }).click();
    await expect(roleInput).toHaveValue('Admin');
  });

  test('mat-dialog opens and closes', async ({ page }) => {
    await page.goto('/projects');

    await page.getByRole('button', { name: 'Delete project' }).first().click();

    // MatDialog renders as a CDK overlay with role="dialog"
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();
    await expect(dialog.getByText('Are you sure?')).toBeVisible();

    // Cancel
    await dialog.getByRole('button', { name: 'Cancel' }).click();
    await expect(dialog).toBeHidden();
  });

  test('mat-table sorting', async ({ page }) => {
    await page.goto('/users');

    // Click the column header to sort
    await page.getByRole('columnheader', { name: 'Name' }).click();

    // Verify sort indicator
    const header = page.getByRole('columnheader', { name: 'Name' });
    await expect(header).toHaveAttribute('aria-sort', 'ascending');

    // Verify rows are sorted
    const names = await page.getByRole('cell').filter({
      has: page.locator('[data-column="name"]'),
    }).allTextContents();
    const sortedNames = [...names].sort();
    expect(names).toEqual(sortedNames);

    // Click again for descending
    await page.getByRole('columnheader', { name: 'Name' }).click();
    await expect(header).toHaveAttribute('aria-sort', 'descending');
  });

  test('mat-paginator controls table pagination', async ({ page }) => {
    await page.goto('/users');

    await expect(page.getByText('1 - 10 of 50')).toBeVisible();

    // Navigate to next page
    await page.getByRole('button', { name: 'Next page' }).click();
    await expect(page.getByText('11 - 20 of 50')).toBeVisible();

    // Change page size
    await page.getByRole('combobox', { name: 'Items per page' }).click();
    await page.getByRole('option', { name: '25' }).click();
    await expect(page.getByText('1 - 25 of 50')).toBeVisible();
  });

  test('mat-snack-bar notification appears and dismisses', async ({ page }) => {
    await page.goto('/settings');

    await page.getByRole('button', { name: 'Save' }).click();

    // Snackbar appears at the bottom of the screen
    await expect(page.getByText('Settings saved successfully')).toBeVisible();

    // Dismiss via action button
    await page.getByRole('button', { name: 'Dismiss' }).click();
    await expect(page.getByText('Settings saved successfully')).toBeHidden();
  });

  test('mat-stepper wizard flow', async ({ page }) => {
    await page.goto('/onboarding');

    // Step 1: Personal info
    await expect(page.getByText('Step 1 of 3')).toBeVisible();
    await page.getByLabel('Full name').fill('Jane Doe');
    await page.getByRole('button', { name: 'Next' }).click();

    // Step 2: Company info
    await expect(page.getByText('Step 2 of 3')).toBeVisible();
    await page.getByLabel('Company').fill('Acme Corp');
    await page.getByRole('button', { name: 'Next' }).click();

    // Step 3: Review
    await expect(page.getByText('Step 3 of 3')).toBeVisible();
    await expect(page.getByText('Jane Doe')).toBeVisible();
    await expect(page.getByText('Acme Corp')).toBeVisible();

    // Go back to step 1
    await page.getByRole('button', { name: 'Back' }).click();
    await page.getByRole('button', { name: 'Back' }).click();
    await expect(page.getByText('Step 1 of 3')).toBeVisible();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Angular Material components', () => {
  test('mat-select dropdown', async ({ page }) => {
    await page.goto('/settings');

    await page.getByRole('combobox', { name: 'Theme' }).click();
    await page.getByRole('option', { name: 'Dark' }).click();

    await expect(page.getByRole('combobox', { name: 'Theme' })).toContainText('Dark');
  });

  test('mat-dialog opens and closes', async ({ page }) => {
    await page.goto('/projects');

    await page.getByRole('button', { name: 'Delete project' }).first().click();

    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();
    await expect(dialog.getByText('Are you sure?')).toBeVisible();

    await dialog.getByRole('button', { name: 'Cancel' }).click();
    await expect(dialog).toBeHidden();
  });

  test('mat-table sorting', async ({ page }) => {
    await page.goto('/users');

    await page.getByRole('columnheader', { name: 'Name' }).click();

    const header = page.getByRole('columnheader', { name: 'Name' });
    await expect(header).toHaveAttribute('aria-sort', 'ascending');
  });

  test('mat-snack-bar notification appears and dismisses', async ({ page }) => {
    await page.goto('/settings');

    await page.getByRole('button', { name: 'Save' }).click();
    await expect(page.getByText('Settings saved successfully')).toBeVisible();

    await page.getByRole('button', { name: 'Dismiss' }).click();
    await expect(page.getByText('Settings saved successfully')).toBeHidden();
  });
});
```

### Testing Angular Router Navigation

**Use when**: Testing Angular Router navigation, lazy-loaded routes, route guards, and URL parameter handling.
**Avoid when**: Testing router configuration in isolation -- use Angular TestBed for that.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Angular Router navigation', () => {
  test('lazy-loaded module loads on navigation', async ({ page }) => {
    await page.goto('/');

    // Navigate to a lazy-loaded route
    await page.getByRole('link', { name: 'Admin' }).click();
    await page.waitForURL('/admin');

    // The lazy module loads and renders its component
    await expect(page.getByRole('heading', { name: 'Admin Dashboard' })).toBeVisible();
  });

  test('route guard redirects unauthorized users', async ({ page }) => {
    // Visit a route protected by AuthGuard (canActivate)
    await page.goto('/admin/users');

    // Guard should redirect to login
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  });

  test('route resolver prefetches data before navigation', async ({ page }) => {
    // Intercept the API call that the resolver makes
    const resolverPromise = page.waitForResponse('**/api/products/*');

    await page.goto('/products/42');

    // The resolver fetches data before the component renders
    await resolverPromise;

    // Component renders with pre-fetched data (no loading spinner)
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Product');
  });

  test('nested router-outlet renders child components', async ({ page }) => {
    await page.goto('/settings/profile');

    // Parent layout (SettingsComponent with its own router-outlet)
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
    await expect(page.getByRole('navigation', { name: 'Settings' })).toBeVisible();

    // Child route (ProfileComponent rendered inside nested router-outlet)
    await expect(page.getByRole('heading', { name: 'Profile', level: 2 })).toBeVisible();

    // Navigate to sibling child route
    await page.getByRole('link', { name: 'Security' }).click();
    await page.waitForURL('/settings/security');

    // Parent persists, child changes
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Security', level: 2 })).toBeVisible();
  });

  test('route parameters update component state', async ({ page }) => {
    await page.goto('/users/1');
    await expect(page.getByRole('heading')).toContainText('User #1');

    // Navigate to a different user via the URL
    await page.goto('/users/2');
    await expect(page.getByRole('heading')).toContainText('User #2');
  });

  test('query parameters drive filter behavior', async ({ page }) => {
    await page.goto('/products?category=electronics&page=2');

    await expect(page.getByRole('heading', { name: 'Electronics' })).toBeVisible();
    await expect(page.getByText('Page 2')).toBeVisible();
  });

  test('browser back navigates through Angular history', async ({ page }) => {
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

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Angular Router navigation', () => {
  test('lazy-loaded module loads on navigation', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('link', { name: 'Admin' }).click();
    await page.waitForURL('/admin');

    await expect(page.getByRole('heading', { name: 'Admin Dashboard' })).toBeVisible();
  });

  test('route guard redirects unauthorized users', async ({ page }) => {
    await page.goto('/admin/users');

    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  });

  test('nested router-outlet renders child components', async ({ page }) => {
    await page.goto('/settings/profile');

    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Profile', level: 2 })).toBeVisible();

    await page.getByRole('link', { name: 'Security' }).click();
    await page.waitForURL('/settings/security');

    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Security', level: 2 })).toBeVisible();
  });

  test('browser back navigates through Angular history', async ({ page }) => {
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

### Testing Lazy-Loaded Modules

**Use when**: Verifying that Angular lazy-loaded feature modules load correctly when the user navigates to their routes. Lazy-loaded modules introduce network requests for JavaScript chunks.
**Avoid when**: The module is eagerly loaded -- no separate chunk to load.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('lazy-loaded modules', () => {
  test('lazy module loads without errors', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/');

    // Navigate to a lazy-loaded route
    const chunkRequest = page.waitForResponse((response) =>
      response.url().includes('.js') && response.status() === 200
    );
    await page.getByRole('link', { name: 'Reports' }).click();
    await chunkRequest;

    await page.waitForURL('/reports');
    await expect(page.getByRole('heading', { name: 'Reports' })).toBeVisible();

    // No chunk loading errors
    const chunkErrors = consoleErrors.filter(
      (e) => e.includes('ChunkLoadError') || e.includes('Loading chunk')
    );
    expect(chunkErrors).toEqual([]);
  });

  test('preloaded lazy module navigates instantly', async ({ page }) => {
    await page.goto('/dashboard');

    // If preloadingStrategy is configured, the module may already be cached
    // Navigate and verify it renders without visible delay
    const startTime = Date.now();
    await page.getByRole('link', { name: 'Reports' }).click();
    await page.waitForURL('/reports');
    await expect(page.getByRole('heading', { name: 'Reports' })).toBeVisible();
    const loadTime = Date.now() - startTime;

    // Preloaded modules should render quickly (not an exact assertion, but a sanity check)
    expect(loadTime).toBeLessThan(3000);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('lazy-loaded modules', () => {
  test('lazy module loads without errors', async ({ page }) => {
    const consoleErrors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/');

    await page.getByRole('link', { name: 'Reports' }).click();
    await page.waitForURL('/reports');
    await expect(page.getByRole('heading', { name: 'Reports' })).toBeVisible();

    const chunkErrors = consoleErrors.filter(
      (e) => e.includes('ChunkLoadError') || e.includes('Loading chunk')
    );
    expect(chunkErrors).toEqual([]);
  });
});
```

### Testing Signals and Observables Indirectly

**Use when**: Verifying that Angular signals (`signal()`, `computed()`, `effect()`) and RxJS observables produce correct UI updates. Playwright cannot subscribe to observables or read signals directly -- test through the rendered output.
**Avoid when**: Testing observable transformation logic in isolation -- use Jasmine/Jest with Angular TestBed for that.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('signals (tested through UI)', () => {
  test('signal-based counter updates the DOM', async ({ page }) => {
    await page.goto('/counter');

    // The counter uses signal() internally
    await expect(page.getByTestId('count')).toHaveText('0');

    await page.getByRole('button', { name: 'Increment' }).click();
    await expect(page.getByTestId('count')).toHaveText('1');

    await page.getByRole('button', { name: 'Increment' }).click();
    await page.getByRole('button', { name: 'Increment' }).click();
    await expect(page.getByTestId('count')).toHaveText('3');

    await page.getByRole('button', { name: 'Reset' }).click();
    await expect(page.getByTestId('count')).toHaveText('0');
  });

  test('computed signal updates derived values', async ({ page }) => {
    await page.goto('/cart');

    // Cart total is a computed() signal derived from items
    await expect(page.getByTestId('cart-total')).toHaveText('$0.00');

    // Add item (updates the items signal, which updates the computed total)
    await page.goto('/products');
    await page.getByRole('listitem')
      .filter({ hasText: '$29.99' })
      .getByRole('button', { name: 'Add to cart' })
      .click();

    await page.getByRole('link', { name: 'Cart' }).click();
    await expect(page.getByTestId('cart-total')).toHaveText('$29.99');
  });
});

test.describe('observables (tested through UI)', () => {
  test('real-time data stream updates the UI', async ({ page }) => {
    await page.goto('/dashboard');

    // The component subscribes to an observable that emits stock prices
    const priceElement = page.getByTestId('stock-price');
    await expect(priceElement).toBeVisible();

    // Get the initial value
    const initialPrice = await priceElement.textContent();

    // Wait for the observable to emit a new value
    // Use polling assertion instead of waitForTimeout
    await expect(priceElement).not.toHaveText(initialPrice!, { timeout: 10_000 });
  });

  test('search with debounceTime observable', async ({ page }) => {
    await page.goto('/search');

    const apiCalls: string[] = [];
    await page.route('**/api/search*', async (route) => {
      apiCalls.push(route.request().url());
      await route.continue();
    });

    // Type quickly -- the observable's debounceTime should batch
    await page.getByRole('textbox', { name: 'Search' }).pressSequentially('angular', {
      delay: 50,
    });

    await expect(page.getByRole('listitem')).toHaveCount(5);

    // debounceTime should prevent a request per keystroke
    expect(apiCalls.length).toBeLessThanOrEqual(2);
  });

  test('switchMap cancels previous requests on new input', async ({ page }) => {
    await page.goto('/search');

    // Type one query
    await page.getByRole('textbox', { name: 'Search' }).fill('first query');

    // Immediately type a different query before results come back
    await page.getByRole('textbox', { name: 'Search' }).fill('second query');

    // Results should match the second query, not the first
    await expect(page.getByRole('listitem').first()).toContainText(/second query/i);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('signals (tested through UI)', () => {
  test('signal-based counter updates the DOM', async ({ page }) => {
    await page.goto('/counter');

    await expect(page.getByTestId('count')).toHaveText('0');

    await page.getByRole('button', { name: 'Increment' }).click();
    await expect(page.getByTestId('count')).toHaveText('1');

    await page.getByRole('button', { name: 'Increment' }).click();
    await page.getByRole('button', { name: 'Increment' }).click();
    await expect(page.getByTestId('count')).toHaveText('3');

    await page.getByRole('button', { name: 'Reset' }).click();
    await expect(page.getByTestId('count')).toHaveText('0');
  });
});

test.describe('observables (tested through UI)', () => {
  test('search with debounceTime observable', async ({ page }) => {
    await page.goto('/search');

    const apiCalls = [];
    await page.route('**/api/search*', async (route) => {
      apiCalls.push(route.request().url());
      await route.continue();
    });

    await page.getByRole('textbox', { name: 'Search' }).pressSequentially('angular', {
      delay: 50,
    });

    await expect(page.getByRole('listitem')).toHaveCount(5);
    expect(apiCalls.length).toBeLessThanOrEqual(2);
  });
});
```

## Framework-Specific Tips

### Zone.js Considerations

Angular uses Zone.js to detect async operations and trigger change detection. Playwright does not depend on Zone.js -- it interacts with the DOM directly. However, Zone.js can affect test behavior:

1. **Change detection timing**: After user interactions (click, fill), Angular schedules change detection via Zone.js. Playwright's auto-waiting handles this -- `expect(locator).toHaveText('new value')` retries until the DOM updates.

2. **Zoneless Angular (experimental)**: Angular 17+ supports zoneless change detection. Tests work identically with Playwright because Playwright waits for DOM changes, not Zone.js ticks.

3. **Long-running async operations**: If your app has `setInterval` or long-running observables, Zone.js keeps Angular in a "not stable" state. This does not affect Playwright (unlike Protractor, which waited for Angular stability). Playwright simply interacts with whatever is on the screen.

### Protractor to Playwright Migration Checklist

| Protractor | Playwright Equivalent |
|---|---|
| `element(by.css('.btn'))` | `page.locator('.btn')` -- but prefer `page.getByRole('button', { name: '...' })` |
| `element(by.id('login'))` | `page.getByTestId('login')` or `page.getByRole(...)` |
| `element(by.buttonText('Submit'))` | `page.getByRole('button', { name: 'Submit' })` |
| `element(by.model('user.name'))` | `page.getByLabel('Name')` -- Playwright cannot read ng-model |
| `element(by.binding('user.name'))` | `page.getByText(expectedValue)` -- test the rendered output |
| `element(by.repeater('item in items'))` | `page.getByRole('listitem')` or `page.getByTestId(...)` |
| `browser.waitForAngular()` | Not needed -- Playwright auto-waits; remove all instances |
| `browser.sleep(3000)` | `await expect(locator).toBeVisible()` -- never use arbitrary waits |
| `browser.get('/path')` | `await page.goto('/path')` |
| `protractor.ExpectedConditions` | `await expect(locator).toBeVisible/toBeHidden/toHaveText(...)` |

### Angular Build Configurations

| Scenario | Build Command | Notes |
|---|---|---|
| Local development | `npx ng serve` | Fast rebuild, source maps, no optimization |
| CI (production build) | `npx ng build && npx http-server dist/your-app/browser -p 4200 -s` | Tests the real production bundle |
| CI (SSR/Universal) | `npx ng build --ssr && node dist/your-app/server/server.mjs` | Tests server-side rendered Angular |
| Staging environment | No `webServer` needed | Point `baseURL` to the staging URL |

The `-s` flag on `http-server` enables SPA fallback (sends `index.html` for all routes), which is essential for Angular Router to work correctly.

### CDK Overlay Container

Angular Material and Angular CDK render overlays (dialogs, menus, selects, autocompletes) in a special container outside the component tree. Playwright sees these overlays in the document -- no special handling is needed. Use standard role-based locators:

```typescript
// CDK overlays render into <div class="cdk-overlay-container"> at the body level
// Playwright sees them as regular DOM elements
const dialog = page.getByRole('dialog');
const menu = page.getByRole('menu');
const listbox = page.getByRole('listbox');
```

### Testing with Angular SSR (Universal)

If your Angular app uses server-side rendering:

```typescript
// playwright.config.ts (SSR-specific)
webServer: {
  command: process.env.CI
    ? 'npx ng build --ssr && node dist/your-app/server/server.mjs'
    : 'npx ng serve --ssr',
  url: 'http://localhost:4200',
  reuseExistingServer: !process.env.CI,
  timeout: 180_000, // SSR builds are slower
},
```

Test for hydration issues the same way as with other SSR frameworks:

```typescript
test('no hydration errors after SSR', async ({ page }) => {
  const errors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error' && msg.text().includes('hydration')) {
      errors.push(msg.text());
    }
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Get started' }).click();

  expect(errors).toEqual([]);
});
```

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `page.locator('[_ngcontent-abc123]')` | Angular scoped style attributes are random and change every build | Use `getByRole`, `getByLabel`, `getByText`, `getByTestId` |
| `page.locator('[ng-reflect-model="value"]')` | `ng-reflect-*` attributes only exist in dev mode; stripped in production | Test the rendered value: `expect(input).toHaveValue('value')` |
| `page.locator('app-my-component')` | Angular component selectors are implementation details | Target the content the component renders using semantic locators |
| `page.locator('.mat-mdc-button')` | Angular Material class names change between versions (MDC migration) | `page.getByRole('button', { name: 'Submit' })` |
| `page.evaluate(() => (window as any).ng)` to access Angular internals | Depends on debug mode; not available in production builds | Test through the DOM; never access the Angular runtime |
| `await page.waitForTimeout(500)` after clicking a button | Zone.js change detection timing varies; arbitrary waits are fragile | `await expect(locator).toHaveText('expected value')` auto-retries |
| `browser.waitForAngular()` (Protractor pattern) | Does not exist in Playwright; not needed -- Playwright auto-waits | Remove entirely; use web-first assertions |
| Test Angular services by injecting them via `page.evaluate` | Services are not accessible from the browser console in production | Test services indirectly through the UI they power; unit test with TestBed |
| Use `ng serve` in CI | Development server is slower, includes debug code, may hide production-only bugs | Use `ng build && http-server` in CI |
| Skip testing CDK overlay components (dialogs, selects, menus) | These are the most interactive parts of the app; bugs here are highly visible | Test overlays with role-based locators; they render in the regular DOM |

## Related

- [core/locators.md](locators.md) -- locator strategies for Angular Material and CDK components
- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- auto-waiting assertions that replace Protractor's waitForAngular
- [core/forms-and-validation.md](forms-and-validation.md) -- form testing patterns for reactive and template-driven forms
- [core/accessibility.md](accessibility.md) -- accessibility testing for Angular Material components
- [core/authentication.md](authentication.md) -- authentication with Angular route guards
- [migration/from-selenium.md](../migration/from-selenium.md) -- migration patterns applicable to Protractor (Protractor is built on Selenium)
- [core/test-architecture.md](test-architecture.md) -- when to use E2E vs unit tests with Angular TestBed
- [ci/ci-github-actions.md](../ci/ci-github-actions.md) -- CI setup with Angular build caching
