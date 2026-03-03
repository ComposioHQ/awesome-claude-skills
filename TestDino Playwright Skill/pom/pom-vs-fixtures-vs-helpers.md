# Page Objects vs Fixtures vs Helpers

> **When to use**: When deciding how to organize reusable test code in a Playwright project.
> **Prerequisites**: [core/page-object-model.md](../core/page-object-model.md), [core/fixtures-and-hooks.md](../core/fixtures-and-hooks.md)

## Quick Answer

**Use all three.** Most projects benefit from a hybrid approach:

- **Page objects** for UI interaction (pages and components with 5+ interactions)
- **Custom fixtures** for test infrastructure (auth state, database, API clients, anything with lifecycle)
- **Helper functions** for stateless utilities (generate data, format values, simple waits)

If you are only going to use one pattern, use **custom fixtures** -- they handle setup/teardown, compose well, and Playwright is built around them. But you should use all three.

## Comparison Table

| Aspect | Page Objects | Custom Fixtures | Helper Functions |
|---|---|---|---|
| **Primary purpose** | Encapsulate UI interactions for a page or component | Provide shared resources with setup/teardown lifecycle | Stateless utility operations |
| **Setup/teardown** | Manual (constructor / methods) | Built-in (`use()` callback with automatic teardown) | None (stateless) |
| **Type safety** | Full class-based typing | Full typing via `test.extend<T>()` generics | Full typing via function signatures |
| **Composability** | Compose via constructor injection or fixture wiring | Compose by depending on other fixtures | Compose by calling other functions |
| **Learning curve** | Low (plain classes) | Medium (Playwright-specific `test.extend` API) | Lowest (plain functions) |
| **Test readability** | High -- `loginPage.signIn(user)` reads like intent | High -- `{ adminPage }` declares dependencies | Medium -- utility calls mixed with test logic |
| **Debugging experience** | Good -- step into class methods | Best -- fixtures appear in traces and reports | Good -- step into functions |
| **IDE support** | Excellent -- autocomplete on class methods | Excellent -- autocomplete on fixture parameters | Excellent -- autocomplete on function params |
| **State management** | Holds page reference and locators as instance state | Manages resource lifecycle (create, provide, cleanup) | No state (pure functions) |
| **Best for** | Pages with many interactions reused across files | Resources that need setup AND teardown | Simple, reusable logic with no side effects |

## Decision Flowchart

```
What kind of reusable code are you writing?
|
+-- Does it interact with a page or component in the browser?
|   |
|   +-- Does the page/component have 5+ interactions (fill, click, navigate, assert)?
|   |   |
|   |   +-- YES: Is it used in 3+ test files?
|   |   |   +-- YES --> PAGE OBJECT
|   |   |   +-- NO --> Inline the interactions or use a small helper function
|   |   |
|   |   +-- NO (< 5 interactions) --> HELPER FUNCTION
|   |
|   +-- Does it need setup before the test AND cleanup after?
|       +-- YES --> CUSTOM FIXTURE (wraps a page object or resource)
|       +-- NO --> PAGE OBJECT method or HELPER FUNCTION
|
+-- Does it manage a resource with lifecycle (create/destroy)?
|   |
|   +-- Examples: auth state, database connection, API client,
|   |   test user, browser context, temporary files
|   |
|   +-- YES --> CUSTOM FIXTURE (always)
|
+-- Is it a stateless utility? (no browser, no side effects)
|   |
|   +-- Examples: generate random email, format date, build URL,
|   |   create test data object, parse response
|   |
|   +-- YES --> HELPER FUNCTION
|
+-- Not sure?
    +-- Start with a HELPER FUNCTION
    +-- Promote to PAGE OBJECT when interactions grow
    +-- Promote to FIXTURE when lifecycle management is needed
```

## When to Use Page Objects

**Best for**: Pages or components with 5+ interactions that appear in 3+ test files. Encapsulate navigation, form filling, action sequences, and element locators into a single class that reads like user intent.

**TypeScript**

```typescript
// page-objects/checkout.page.ts
import { type Page, type Locator, expect } from '@playwright/test';

export class CheckoutPage {
  readonly page: Page;
  readonly cardNumber: Locator;
  readonly expiry: Locator;
  readonly cvc: Locator;
  readonly payButton: Locator;
  readonly promoCodeInput: Locator;
  readonly orderTotal: Locator;

  constructor(page: Page) {
    this.page = page;
    this.cardNumber = page.getByLabel('Card number');
    this.expiry = page.getByLabel('Expiry');
    this.cvc = page.getByLabel('CVC');
    this.payButton = page.getByRole('button', { name: 'Pay now' });
    this.promoCodeInput = page.getByLabel('Promo code');
    this.orderTotal = page.getByTestId('order-total');
  }

  async goto() {
    await this.page.goto('/checkout');
  }

  async fillPaymentDetails(card: { number: string; expiry: string; cvc: string }) {
    await this.cardNumber.fill(card.number);
    await this.expiry.fill(card.expiry);
    await this.cvc.fill(card.cvc);
  }

  async pay() {
    await this.payButton.click();
    await this.page.waitForURL('**/confirmation');
  }

  async applyPromoCode(code: string) {
    await this.promoCodeInput.fill(code);
    await this.page.getByRole('button', { name: 'Apply' }).click();
    await expect(this.page.getByText('Code applied')).toBeVisible();
  }

  async expectTotal(amount: string) {
    await expect(this.orderTotal).toHaveText(amount);
  }
}
```

```typescript
// tests/checkout/payment.spec.ts
import { test, expect } from '@playwright/test';
import { CheckoutPage } from '../page-objects/checkout.page';

test('should complete checkout with valid card', async ({ page }) => {
  const checkout = new CheckoutPage(page);
  await checkout.goto();
  await checkout.fillPaymentDetails({
    number: '4242424242424242',
    expiry: '12/28',
    cvc: '123',
  });
  await checkout.pay();
  await expect(page.getByText('Payment successful')).toBeVisible();
});

test('should apply promo code and update total', async ({ page }) => {
  const checkout = new CheckoutPage(page);
  await checkout.goto();
  await checkout.applyPromoCode('SAVE20');
  await checkout.expectTotal('$79.99');
});
```

**JavaScript**

```javascript
// page-objects/checkout.page.js
const { expect } = require('@playwright/test');

class CheckoutPage {
  constructor(page) {
    this.page = page;
    this.cardNumber = page.getByLabel('Card number');
    this.expiry = page.getByLabel('Expiry');
    this.cvc = page.getByLabel('CVC');
    this.payButton = page.getByRole('button', { name: 'Pay now' });
    this.promoCodeInput = page.getByLabel('Promo code');
    this.orderTotal = page.getByTestId('order-total');
  }

  async goto() {
    await this.page.goto('/checkout');
  }

  async fillPaymentDetails(card) {
    await this.cardNumber.fill(card.number);
    await this.expiry.fill(card.expiry);
    await this.cvc.fill(card.cvc);
  }

  async pay() {
    await this.payButton.click();
    await this.page.waitForURL('**/confirmation');
  }

  async applyPromoCode(code) {
    await this.promoCodeInput.fill(code);
    await this.page.getByRole('button', { name: 'Apply' }).click();
    await expect(this.page.getByText('Code applied')).toBeVisible();
  }

  async expectTotal(amount) {
    await expect(this.orderTotal).toHaveText(amount);
  }
}

module.exports = { CheckoutPage };
```

```javascript
// tests/checkout/payment.spec.js
const { test, expect } = require('@playwright/test');
const { CheckoutPage } = require('../page-objects/checkout.page');

test('should complete checkout with valid card', async ({ page }) => {
  const checkout = new CheckoutPage(page);
  await checkout.goto();
  await checkout.fillPaymentDetails({
    number: '4242424242424242',
    expiry: '12/28',
    cvc: '123',
  });
  await checkout.pay();
  await expect(page.getByText('Payment successful')).toBeVisible();
});

test('should apply promo code and update total', async ({ page }) => {
  const checkout = new CheckoutPage(page);
  await checkout.goto();
  await checkout.applyPromoCode('SAVE20');
  await checkout.expectTotal('$79.99');
});
```

**Key principles for page objects:**
- One class per logical page or component, not per URL
- Constructor takes `Page` (and optionally other page objects for composition)
- Locators are `readonly` properties assigned in the constructor
- Methods represent user-intent actions (`signIn`, `addToCart`), not low-level clicks
- Navigation methods (`goto`) belong on the page object
- Assertions can live on the page object when they verify page-specific state

## When to Use Custom Fixtures

**Best for**: Shared resources that need setup before the test and teardown after -- auth state, database connections, API clients, test users, seeded data, custom browser contexts. Anything with a lifecycle belongs in a fixture.

**TypeScript**

```typescript
// fixtures/base.fixture.ts
import { test as base, expect } from '@playwright/test';
import { CheckoutPage } from '../page-objects/checkout.page';
import { DashboardPage } from '../page-objects/dashboard.page';

// Define types for all custom fixtures
type MyFixtures = {
  checkoutPage: CheckoutPage;
  dashboardPage: DashboardPage;
  authenticatedPage: ReturnType<typeof base['page']> extends Promise<infer P> ? P : never;
  testUser: { email: string; password: string; id: string };
  apiClient: { get: (path: string) => Promise<Response>; post: (path: string, data: unknown) => Promise<Response> };
};

export const test = base.extend<MyFixtures>({
  // Fixture that wraps a page object — created fresh for each test
  checkoutPage: async ({ page }, use) => {
    const checkoutPage = new CheckoutPage(page);
    await use(checkoutPage);
    // No teardown needed — page closes automatically
  },

  dashboardPage: async ({ page }, use) => {
    const dashboardPage = new DashboardPage(page);
    await use(dashboardPage);
  },

  // Fixture with real setup AND teardown — creates a test user, cleans up after
  testUser: async ({ request }, use) => {
    // Setup: create a user via API
    const response = await request.post('/api/test/users', {
      data: {
        email: `test-${Date.now()}@example.com`,
        password: 'TestPass123!',
      },
    });
    const user = await response.json();

    // Provide the user to the test
    await use(user);

    // Teardown: delete the user (runs even if test fails)
    await request.delete(`/api/test/users/${user.id}`);
  },

  // Fixture that depends on another fixture
  authenticatedPage: async ({ page, testUser }, use) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill(testUser.email);
    await page.getByLabel('Password').fill(testUser.password);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page).toHaveURL('/dashboard');

    await use(page);
    // Teardown: logout (optional — browser context is destroyed anyway)
  },

  // API client fixture with lifecycle
  apiClient: async ({ request }, use) => {
    const client = {
      get: (path: string) => request.get(`/api${path}`),
      post: (path: string, data: unknown) => request.post(`/api${path}`, { data }),
    };

    await use(client);
    // Teardown runs automatically when request fixture tears down
  },
});

export { expect } from '@playwright/test';
```

```typescript
// tests/dashboard/widgets.spec.ts
import { test, expect } from '../../fixtures/base.fixture';

// testUser and authenticatedPage are set up automatically by the fixture system
test('authenticated user sees dashboard widgets', async ({ authenticatedPage }) => {
  await expect(authenticatedPage.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(authenticatedPage.getByTestId('revenue-widget')).toBeVisible();
  await expect(authenticatedPage.getByTestId('orders-widget')).toBeVisible();
});

test('user can refresh dashboard data', async ({ authenticatedPage, dashboardPage }) => {
  await authenticatedPage.getByRole('button', { name: 'Refresh' }).click();
  await expect(authenticatedPage.getByText('Updated just now')).toBeVisible();
});

// testUser fixture creates AND cleans up the user automatically
test('new user sees onboarding prompt', async ({ authenticatedPage, testUser }) => {
  await expect(authenticatedPage.getByText(`Welcome, ${testUser.email}`)).toBeVisible();
  await expect(authenticatedPage.getByRole('dialog', { name: 'Get started' })).toBeVisible();
});
```

**JavaScript**

```javascript
// fixtures/base.fixture.js
const { test: base, expect } = require('@playwright/test');
const { CheckoutPage } = require('../page-objects/checkout.page');
const { DashboardPage } = require('../page-objects/dashboard.page');

const test = base.extend({
  checkoutPage: async ({ page }, use) => {
    const checkoutPage = new CheckoutPage(page);
    await use(checkoutPage);
  },

  dashboardPage: async ({ page }, use) => {
    const dashboardPage = new DashboardPage(page);
    await use(dashboardPage);
  },

  testUser: async ({ request }, use) => {
    const response = await request.post('/api/test/users', {
      data: {
        email: `test-${Date.now()}@example.com`,
        password: 'TestPass123!',
      },
    });
    const user = await response.json();

    await use(user);

    await request.delete(`/api/test/users/${user.id}`);
  },

  authenticatedPage: async ({ page, testUser }, use) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill(testUser.email);
    await page.getByLabel('Password').fill(testUser.password);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page).toHaveURL('/dashboard');

    await use(page);
  },

  apiClient: async ({ request }, use) => {
    const client = {
      get: (path) => request.get(`/api${path}`),
      post: (path, data) => request.post(`/api${path}`, { data }),
    };

    await use(client);
  },
});

module.exports = { test, expect };
```

```javascript
// tests/dashboard/widgets.spec.js
const { test, expect } = require('../../fixtures/base.fixture');

test('authenticated user sees dashboard widgets', async ({ authenticatedPage }) => {
  await expect(authenticatedPage.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(authenticatedPage.getByTestId('revenue-widget')).toBeVisible();
  await expect(authenticatedPage.getByTestId('orders-widget')).toBeVisible();
});

test('new user sees onboarding prompt', async ({ authenticatedPage, testUser }) => {
  await expect(authenticatedPage.getByText(`Welcome, ${testUser.email}`)).toBeVisible();
  await expect(authenticatedPage.getByRole('dialog', { name: 'Get started' })).toBeVisible();
});
```

**Key principles for custom fixtures:**
- Use `test.extend()` to define fixtures -- never use module-level variables
- The `use()` callback separates setup (before) from teardown (after)
- Teardown runs even if the test fails or crashes -- this is the main advantage over `afterEach`
- Fixtures compose: one fixture can depend on another (`authenticatedPage` depends on `testUser`)
- Fixtures are lazy: they are only created when a test actually requests them
- Wrap page objects in fixtures to get automatic lifecycle management
- Fixtures appear in Playwright traces, making debugging easier

## When to Use Helper Functions

**Best for**: Stateless utility operations -- generating test data, formatting values, building URLs, parsing responses, creating simple wait conditions. Pure functions with no side effects and no browser interaction.

**TypeScript**

```typescript
// helpers/test-data.ts
import { randomUUID } from 'node:crypto';

export function generateEmail(prefix = 'test'): string {
  return `${prefix}-${Date.now()}-${randomUUID().slice(0, 8)}@example.com`;
}

export function generateUser(overrides: Partial<TestUser> = {}): TestUser {
  return {
    email: generateEmail(),
    password: 'TestPass123!',
    firstName: 'Test',
    lastName: 'User',
    ...overrides,
  };
}

interface TestUser {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

export function formatCurrency(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export function buildApiUrl(path: string, params: Record<string, string> = {}): string {
  const url = new URL(path, 'http://localhost:3000');
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
  return url.toString();
}
```

```typescript
// helpers/assertions.ts
import { type Page, expect } from '@playwright/test';

/**
 * Wait for all network requests to settle.
 * Use sparingly — prefer specific assertions over blanket network waits.
 */
export async function waitForNetworkIdle(page: Page, timeout = 5000): Promise<void> {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Assert that a toast notification appears and then disappears.
 */
export async function expectToast(page: Page, message: string): Promise<void> {
  const toast = page.getByRole('status').filter({ hasText: message });
  await expect(toast).toBeVisible();
  await expect(toast).toBeHidden({ timeout: 10000 });
}
```

```typescript
// tests/settings/profile.spec.ts
import { test, expect } from '@playwright/test';
import { generateEmail, generateUser } from '../../helpers/test-data';
import { expectToast } from '../../helpers/assertions';

test('should update user email', async ({ page }) => {
  const newEmail = generateEmail('updated');

  await page.goto('/settings/profile');
  await page.getByLabel('Email').fill(newEmail);
  await page.getByRole('button', { name: 'Save' }).click();

  await expectToast(page, 'Profile updated');
  await expect(page.getByLabel('Email')).toHaveValue(newEmail);
});

test('should display user info', async ({ page }) => {
  const user = generateUser({ firstName: 'Jane', lastName: 'Doe' });
  // ... use user data in test setup
});
```

**JavaScript**

```javascript
// helpers/test-data.js
const { randomUUID } = require('node:crypto');

function generateEmail(prefix = 'test') {
  return `${prefix}-${Date.now()}-${randomUUID().slice(0, 8)}@example.com`;
}

function generateUser(overrides = {}) {
  return {
    email: generateEmail(),
    password: 'TestPass123!',
    firstName: 'Test',
    lastName: 'User',
    ...overrides,
  };
}

function formatCurrency(cents) {
  return `$${(cents / 100).toFixed(2)}`;
}

function buildApiUrl(path, params = {}) {
  const url = new URL(path, 'http://localhost:3000');
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));
  return url.toString();
}

module.exports = { generateEmail, generateUser, formatCurrency, buildApiUrl };
```

```javascript
// helpers/assertions.js
const { expect } = require('@playwright/test');

async function waitForNetworkIdle(page, timeout = 5000) {
  await page.waitForLoadState('networkidle', { timeout });
}

async function expectToast(page, message) {
  const toast = page.getByRole('status').filter({ hasText: message });
  await expect(toast).toBeVisible();
  await expect(toast).toBeHidden({ timeout: 10000 });
}

module.exports = { waitForNetworkIdle, expectToast };
```

```javascript
// tests/settings/profile.spec.js
const { test, expect } = require('@playwright/test');
const { generateEmail, generateUser } = require('../../helpers/test-data');
const { expectToast } = require('../../helpers/assertions');

test('should update user email', async ({ page }) => {
  const newEmail = generateEmail('updated');

  await page.goto('/settings/profile');
  await page.getByLabel('Email').fill(newEmail);
  await page.getByRole('button', { name: 'Save' }).click();

  await expectToast(page, 'Profile updated');
  await expect(page.getByLabel('Email')).toHaveValue(newEmail);
});
```

**Key principles for helper functions:**
- Pure functions with no side effects -- given the same input, always the same output
- No browser state -- helpers that need `page` should take it as a parameter, not store it
- If a helper grows to need setup/teardown, promote it to a fixture
- If a helper grows to encapsulate many page interactions, promote it to a page object
- Keep helpers small and focused -- one function, one job

## Combining Approaches

The recommended hybrid approach for real projects. This is what a well-organized Playwright project looks like.

**Project structure:**

```
tests/
+-- fixtures/
|   +-- auth.fixture.ts       # Custom fixtures: authenticatedPage, testUser, adminUser
|   +-- db.fixture.ts          # Custom fixtures: database, seedData
|   +-- base.fixture.ts        # Combines all fixtures, re-exports test and expect
+-- page-objects/
|   +-- login.page.ts          # Page object: LoginPage
|   +-- dashboard.page.ts      # Page object: DashboardPage
|   +-- checkout.page.ts       # Page object: CheckoutPage
|   +-- components/
|       +-- data-table.component.ts  # Reusable component object
|       +-- modal.component.ts
+-- helpers/
|   +-- test-data.ts            # Helper: generateEmail, generateUser, generateOrder
|   +-- assertions.ts           # Helper: expectToast, expectTableRowCount
|   +-- api.ts                  # Helper: createProductViaApi, deleteAllTestData
+-- e2e/
|   +-- auth/
|   |   +-- login.spec.ts
|   |   +-- signup.spec.ts
|   +-- checkout/
|   |   +-- cart.spec.ts
|   |   +-- payment.spec.ts
|   +-- dashboard/
|       +-- widgets.spec.ts
playwright.config.ts
```

**How the three approaches work together:**

**TypeScript**

```typescript
// fixtures/base.fixture.ts — the glue layer
import { test as base } from '@playwright/test';
import { LoginPage } from '../page-objects/login.page';
import { DashboardPage } from '../page-objects/dashboard.page';
import { CheckoutPage } from '../page-objects/checkout.page';
import { generateUser } from '../helpers/test-data';

type Fixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  checkoutPage: CheckoutPage;
  testUser: { email: string; password: string; id: string };
  authenticatedPage: import('@playwright/test').Page;
};

export const test = base.extend<Fixtures>({
  // Page objects wrapped in fixtures for convenience
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },

  checkoutPage: async ({ page }, use) => {
    await use(new CheckoutPage(page));
  },

  // Resource fixture with lifecycle — uses helpers for data generation
  testUser: async ({ request }, use) => {
    const userData = generateUser();
    const response = await request.post('/api/test/users', { data: userData });
    const user = await response.json();
    await use(user);
    await request.delete(`/api/test/users/${user.id}`);
  },

  // Composed fixture: depends on page object + resource fixture
  authenticatedPage: async ({ loginPage, testUser }, use) => {
    await loginPage.goto();
    await loginPage.signIn(testUser.email, testUser.password);
    await use(loginPage.page);
  },
});

export { expect } from '@playwright/test';
```

```typescript
// tests/e2e/checkout/payment.spec.ts — clean test using all three
import { test, expect } from '../../../fixtures/base.fixture';
import { generateEmail } from '../../../helpers/test-data';
import { expectToast } from '../../../helpers/assertions';

test.describe('Checkout Payment', () => {
  test('authenticated user completes purchase', async ({ authenticatedPage, checkoutPage }) => {
    // authenticatedPage: fixture handled login + user creation + cleanup
    // checkoutPage: page object encapsulates checkout UI interactions
    await checkoutPage.goto();
    await checkoutPage.fillPaymentDetails({
      number: '4242424242424242',
      expiry: '12/28',
      cvc: '123',
    });
    await checkoutPage.pay();
    await expectToast(authenticatedPage, 'Payment successful');  // helper for common assertion
  });

  test('guest user enters email at checkout', async ({ checkoutPage }) => {
    const email = generateEmail('guest');  // helper for test data
    await checkoutPage.goto();
    await checkoutPage.page.getByLabel('Guest email').fill(email);
    await checkoutPage.fillPaymentDetails({
      number: '4242424242424242',
      expiry: '12/28',
      cvc: '123',
    });
    await checkoutPage.pay();
  });
});
```

**JavaScript**

```javascript
// fixtures/base.fixture.js
const { test: base } = require('@playwright/test');
const { LoginPage } = require('../page-objects/login.page');
const { DashboardPage } = require('../page-objects/dashboard.page');
const { CheckoutPage } = require('../page-objects/checkout.page');
const { generateUser } = require('../helpers/test-data');

const test = base.extend({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },

  checkoutPage: async ({ page }, use) => {
    await use(new CheckoutPage(page));
  },

  testUser: async ({ request }, use) => {
    const userData = generateUser();
    const response = await request.post('/api/test/users', { data: userData });
    const user = await response.json();
    await use(user);
    await request.delete(`/api/test/users/${user.id}`);
  },

  authenticatedPage: async ({ loginPage, testUser }, use) => {
    await loginPage.goto();
    await loginPage.signIn(testUser.email, testUser.password);
    await use(loginPage.page);
  },
});

module.exports = { test, expect: require('@playwright/test').expect };
```

```javascript
// tests/e2e/checkout/payment.spec.js
const { test, expect } = require('../../../fixtures/base.fixture');
const { generateEmail } = require('../../../helpers/test-data');
const { expectToast } = require('../../../helpers/assertions');

test.describe('Checkout Payment', () => {
  test('authenticated user completes purchase', async ({ authenticatedPage, checkoutPage }) => {
    await checkoutPage.goto();
    await checkoutPage.fillPaymentDetails({
      number: '4242424242424242',
      expiry: '12/28',
      cvc: '123',
    });
    await checkoutPage.pay();
    await expectToast(authenticatedPage, 'Payment successful');
  });

  test('guest user enters email at checkout', async ({ checkoutPage }) => {
    const email = generateEmail('guest');
    await checkoutPage.goto();
    await checkoutPage.page.getByLabel('Guest email').fill(email);
    await checkoutPage.fillPaymentDetails({
      number: '4242424242424242',
      expiry: '12/28',
      cvc: '123',
    });
    await checkoutPage.pay();
  });
});
```

**Summary of the hybrid approach:**

| Layer | Pattern | Responsibility |
|---|---|---|
| **Test file** | `test()` | Describes behavior, orchestrates the three layers |
| **Fixtures** | `test.extend()` | Resource lifecycle -- setup, provide, teardown |
| **Page objects** | Classes | UI interaction -- navigation, actions, locators |
| **Helpers** | Functions | Utilities -- data generation, formatting, common assertions |

## Anti-Patterns

### Using only page objects for everything

```typescript
// BAD: page object managing auth state, database, AND UI
class LoginPage {
  async createTestUser() { /* API call to create user */ }
  async deleteTestUser() { /* API call to delete user */ }
  async seedDatabase() { /* database setup */ }
  async signIn(email: string, password: string) { /* UI interaction */ }
}
```

**Problem:** Page objects should only encapsulate UI interaction. Resource lifecycle (create user, seed database) belongs in fixtures where teardown is guaranteed.

**Fix:** Move `createTestUser` and `deleteTestUser` into a `testUser` fixture. Keep only `signIn` in the page object.

---

### Page objects that are just locator containers

```typescript
// BAD: no methods, no encapsulation — just a bag of locators
class LoginPage {
  emailInput = this.page.getByLabel('Email');
  passwordInput = this.page.getByLabel('Password');
  submitButton = this.page.getByRole('button', { name: 'Sign in' });

  constructor(private page: Page) {}
}

// Test still does all the work
test('login', async ({ page }) => {
  const login = new LoginPage(page);
  await login.emailInput.fill('user@example.com');
  await login.passwordInput.fill('pass');
  await login.submitButton.click();
});
```

**Problem:** This adds a layer of indirection with no benefit. The test is not more readable than using locators directly.

**Fix:** Add intent-revealing methods. If the page is simple enough that locators suffice, skip the page object entirely.

```typescript
// GOOD: methods express user intent
class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  async signIn(email: string, password: string) {
    await this.page.getByLabel('Email').fill(email);
    await this.page.getByLabel('Password').fill(password);
    await this.page.getByRole('button', { name: 'Sign in' }).click();
    await this.page.waitForURL('**/dashboard');
  }
}
```

---

### Fixtures that do too much

```typescript
// BAD: one giant fixture that sets up everything
test.extend({
  everything: async ({ page, request }, use) => {
    // Creates user, seeds products, sets up payment method, navigates to dashboard,
    // opens settings modal, enables feature flags, creates admin user...
    const user = await createUser(request);
    const products = await seedProducts(request, 50);
    await setupPayment(request, user.id);
    await page.goto('/dashboard');
    await enableFeatureFlags(request, ['new-ui', 'beta-checkout']);
    const admin = await createAdminUser(request);

    await use({ user, products, admin, page });

    // Massive teardown
    await deleteUser(request, user.id);
    await deleteUser(request, admin.id);
    await deleteProducts(request, products);
    await disableFeatureFlags(request, ['new-ui', 'beta-checkout']);
  },
});
```

**Problem:** Every test pays the cost of full setup even when it only needs a user. Debugging is hard because the fixture does too many things.

**Fix:** Break into small, composable fixtures. Each fixture does one thing.

```typescript
// GOOD: small, composable fixtures
test.extend({
  testUser: async ({ request }, use) => { /* create + cleanup user */ },
  adminUser: async ({ request }, use) => { /* create + cleanup admin */ },
  seededProducts: async ({ request }, use) => { /* seed + cleanup products */ },
  featureFlags: async ({ request }, use) => { /* enable + disable flags */ },
});
```

---

### Helpers with side effects

```typescript
// BAD: "helper" that modifies database and stores state
let createdUserId: string;

export async function createTestUser(request: APIRequestContext) {
  const response = await request.post('/api/users', { data: { email: 'test@example.com' } });
  const user = await response.json();
  createdUserId = user.id;  // Module-level state — shared across tests!
  return user;
}

export async function cleanupTestUser(request: APIRequestContext) {
  await request.delete(`/api/users/${createdUserId}`);
}
```

**Problem:** Module-level state leaks between parallel tests. Cleanup is not guaranteed if the test crashes. This is a fixture pretending to be a helper.

**Fix:** If it has side effects and needs cleanup, make it a fixture.

---

### Over-abstracting simple operations

```typescript
// BAD: helper for a one-liner that adds no clarity
export async function clickButton(page: Page, name: string) {
  await page.getByRole('button', { name }).click();
}

// BAD: page object for a page with 2 interactions
class ConfirmationPage {
  constructor(private page: Page) {}
  async expectSuccess() {
    await expect(this.page.getByText('Success')).toBeVisible();
  }
}
```

**Problem:** Adds indirection without improving readability or reducing duplication. `page.getByRole('button', { name: 'Submit' }).click()` is already clear.

**Fix:** Only abstract when there is real duplication (3+ usages) or real complexity (5+ interactions). Inline simple operations.

## Related

- [core/page-object-model.md](../core/page-object-model.md) -- detailed page object patterns and examples
- [core/fixtures-and-hooks.md](../core/fixtures-and-hooks.md) -- complete guide to Playwright fixtures and lifecycle hooks
- [core/test-organization.md](../core/test-organization.md) -- file structure and naming conventions
- [core/test-architecture.md](../core/test-architecture.md) -- when to write E2E vs API vs component tests
