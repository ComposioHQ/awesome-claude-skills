# Test Organization

> **When to use**: Structuring test files, naming tests, grouping with `describe`, tagging, filtering, and deciding parallel vs serial execution.
> **Prerequisites**: [core/configuration.md](foundations/configuration.md)

## Quick Reference

| Concept | Rule |
|---|---|
| File suffix | `.spec.ts` / `.spec.js` — always |
| Grouping | By feature/domain, not by page or URL |
| Test names | `test('should ...')` or `test('user can ...')` — describe behavior |
| Nesting | Max 2 levels of `test.describe()` |
| Default execution | `fullyParallel: true` — tests run in parallel by default |
| Serial tests | Almost never use `test.describe.serial()` |
| Test dependencies | Avoid — each test sets up its own state |
| Tags | `@smoke`, `@regression`, `@slow` — filter with `--grep` |

## Patterns

### Pattern 1: Feature-Based File Structure

**Use when**: Any project — this is the default layout.
**Avoid when**: Never. This is always correct.

Group tests by feature or domain, not by page class or test type.

**Small project (< 20 tests):**

```
tests/
├── auth.spec.ts
├── dashboard.spec.ts
├── settings.spec.ts
└── checkout.spec.ts
playwright.config.ts
```

**Medium project (20–200 tests):**

```
tests/
├── auth/
│   ├── login.spec.ts
│   ├── signup.spec.ts
│   ├── password-reset.spec.ts
│   └── mfa.spec.ts
├── dashboard/
│   ├── widgets.spec.ts
│   ├── filters.spec.ts
│   └── export.spec.ts
├── checkout/
│   ├── cart.spec.ts
│   ├── payment.spec.ts
│   └── confirmation.spec.ts
├── settings/
│   ├── profile.spec.ts
│   └── notifications.spec.ts
└── fixtures/
    ├── auth.fixture.ts
    └── test-data.ts
playwright.config.ts
```

**Large project (200+ tests):**

```
tests/
├── e2e/
│   ├── auth/
│   │   ├── login.spec.ts
│   │   ├── signup.spec.ts
│   │   ├── password-reset.spec.ts
│   │   └── mfa.spec.ts
│   ├── checkout/
│   │   ├── cart.spec.ts
│   │   ├── payment.spec.ts
│   │   ├── promo-codes.spec.ts
│   │   └── confirmation.spec.ts
│   ├── admin/
│   │   ├── user-management.spec.ts
│   │   ├── reports.spec.ts
│   │   └── audit-log.spec.ts
│   └── inventory/
│       ├── product-list.spec.ts
│       ├── product-detail.spec.ts
│       └── stock-management.spec.ts
├── api/
│   ├── users.spec.ts
│   ├── orders.spec.ts
│   └── products.spec.ts
├── visual/
│   ├── homepage.spec.ts
│   └── product-page.spec.ts
├── fixtures/
│   ├── auth.fixture.ts
│   ├── db.fixture.ts
│   └── base.fixture.ts
├── page-objects/
│   ├── login.page.ts
│   ├── dashboard.page.ts
│   └── checkout.page.ts
└── helpers/
    ├── test-data.ts
    └── api-client.ts
playwright.config.ts
```

---

### Pattern 2: Naming Conventions

**Use when**: Writing any test or file.
**Avoid when**: Never.

**TypeScript:**

```typescript
// tests/checkout/cart.spec.ts
import { test, expect } from '@playwright/test';

// Good: group by feature, describe behavior
test.describe('Shopping Cart', () => {
  test('should add item to empty cart', async ({ page }) => {
    await page.goto('/products/widget-a');
    await page.getByRole('button', { name: 'Add to cart' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('1');
  });

  test('should update quantity when same item added twice', async ({ page }) => {
    await page.goto('/products/widget-a');
    await page.getByRole('button', { name: 'Add to cart' }).click();
    await page.getByRole('button', { name: 'Add to cart' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('2');
  });

  test('user can remove item from cart', async ({ page }) => {
    await page.goto('/cart');
    // ... setup item in cart via API or fixture
    await page.getByRole('button', { name: 'Remove' }).first().click();
    await expect(page.getByText('Your cart is empty')).toBeVisible();
  });
});
```

**JavaScript:**

```javascript
// tests/checkout/cart.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Shopping Cart', () => {
  test('should add item to empty cart', async ({ page }) => {
    await page.goto('/products/widget-a');
    await page.getByRole('button', { name: 'Add to cart' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('1');
  });

  test('should update quantity when same item added twice', async ({ page }) => {
    await page.goto('/products/widget-a');
    await page.getByRole('button', { name: 'Add to cart' }).click();
    await page.getByRole('button', { name: 'Add to cart' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('2');
  });

  test('user can remove item from cart', async ({ page }) => {
    await page.goto('/cart');
    await page.getByRole('button', { name: 'Remove' }).first().click();
    await expect(page.getByText('Your cart is empty')).toBeVisible();
  });
});
```

**Naming rules:**

| Element | Convention | Example |
|---|---|---|
| File name | `kebab-case.spec.ts` | `password-reset.spec.ts` |
| `test.describe()` | Title Case, feature name | `'Password Reset'` |
| `test()` | Sentence starting with `should` or `user can` | `'should send reset email'` |
| Page objects | `PascalCase.page.ts` | `login.page.ts` / `LoginPage` |
| Fixtures | `kebab-case.fixture.ts` | `auth.fixture.ts` |

---

### Pattern 3: `test.describe()` Grouping

**Use when**: A file has multiple related tests that share context or setup.
**Avoid when**: A file has only 1–3 tests with no shared setup — skip the `describe` wrapper.

**TypeScript:**

```typescript
// tests/auth/login.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Login', () => {
  // Shared setup for all tests in this describe block
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('securepass123');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page).toHaveURL('/dashboard');
  });

  test('should show error for invalid password', async ({ page }) => {
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('wrongpassword');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page.getByRole('alert')).toHaveText('Invalid credentials');
  });

  // One level of nesting — acceptable
  test.describe('Rate Limiting', () => {
    test('should lock account after 5 failed attempts', async ({ page }) => {
      for (let i = 0; i < 5; i++) {
        await page.getByLabel('Email').fill('user@example.com');
        await page.getByLabel('Password').fill('wrong');
        await page.getByRole('button', { name: 'Sign in' }).click();
      }
      await expect(page.getByRole('alert')).toContainText('Account locked');
    });
  });
});
```

**JavaScript:**

```javascript
// tests/auth/login.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Login', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('securepass123');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page).toHaveURL('/dashboard');
  });

  test('should show error for invalid password', async ({ page }) => {
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('wrongpassword');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page.getByRole('alert')).toHaveText('Invalid credentials');
  });

  test.describe('Rate Limiting', () => {
    test('should lock account after 5 failed attempts', async ({ page }) => {
      for (let i = 0; i < 5; i++) {
        await page.getByLabel('Email').fill('user@example.com');
        await page.getByLabel('Password').fill('wrong');
        await page.getByRole('button', { name: 'Sign in' }).click();
      }
      await expect(page.getByRole('alert')).toContainText('Account locked');
    });
  });
});
```

**Nesting limit: 2 levels max.** If you need a third level, split into a separate file.

---

### Pattern 4: Tags and Annotations

**Use when**: You need to categorize tests for selective runs (smoke suites, CI pipelines, skip known issues).
**Avoid when**: All tests always run together and you have < 20 tests.

**TypeScript:**

```typescript
// tests/checkout/payment.spec.ts
import { test, expect } from '@playwright/test';

// Tag in the test title — simplest approach
test('should process credit card payment @smoke', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByLabel('Card number').fill('4242424242424242');
  await page.getByLabel('Expiry').fill('12/28');
  await page.getByLabel('CVC').fill('123');
  await page.getByRole('button', { name: 'Pay now' }).click();
  await expect(page.getByText('Payment successful')).toBeVisible();
});

test('should handle declined card @regression', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByLabel('Card number').fill('4000000000000002');
  await page.getByLabel('Expiry').fill('12/28');
  await page.getByLabel('CVC').fill('123');
  await page.getByRole('button', { name: 'Pay now' }).click();
  await expect(page.getByRole('alert')).toContainText('Card declined');
});

// Tag via test.describe for group-level tagging
test.describe('Payment Edge Cases @regression', () => {
  test('should handle network timeout during payment', async ({ page }) => {
    await page.goto('/checkout');
    // ... test implementation
    await expect(page.getByText('Please try again')).toBeVisible();
  });
});

// Annotations for test lifecycle control
test('should render 3D Secure iframe @slow', async ({ page }) => {
  test.slow(); // Triples the default timeout
  await page.goto('/checkout/3ds');
  // ... long-running 3D Secure flow
  await expect(page.getByText('Verified')).toBeVisible();
});

test('should apply loyalty points discount', async ({ page }) => {
  test.skip(process.env.CI !== 'true', 'Only run in CI — needs loyalty service');
  await page.goto('/checkout');
  // ...
});

test('should handle Apple Pay on Safari', async ({ page, browserName }) => {
  test.skip(browserName !== 'webkit', 'Apple Pay only works in Safari');
  await page.goto('/checkout');
  // ...
});

test('should display PayPal button', async ({ page }) => {
  test.fixme(); // Known broken — tracked in JIRA-1234
  await page.goto('/checkout');
  await expect(page.getByRole('button', { name: 'PayPal' })).toBeVisible();
});

test('should fail when submitting empty card form', async ({ page }) => {
  test.fail(); // This test is expected to fail — documents known bug
  await page.goto('/checkout');
  await page.getByRole('button', { name: 'Pay now' }).click();
  // Bug: currently no validation shown — this assertion will fail
  await expect(page.getByRole('alert')).toBeVisible();
});
```

**JavaScript:**

```javascript
// tests/checkout/payment.spec.js
const { test, expect } = require('@playwright/test');

test('should process credit card payment @smoke', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByLabel('Card number').fill('4242424242424242');
  await page.getByLabel('Expiry').fill('12/28');
  await page.getByLabel('CVC').fill('123');
  await page.getByRole('button', { name: 'Pay now' }).click();
  await expect(page.getByText('Payment successful')).toBeVisible();
});

test('should handle declined card @regression', async ({ page }) => {
  await page.goto('/checkout');
  await page.getByLabel('Card number').fill('4000000000000002');
  await page.getByLabel('Expiry').fill('12/28');
  await page.getByLabel('CVC').fill('123');
  await page.getByRole('button', { name: 'Pay now' }).click();
  await expect(page.getByRole('alert')).toContainText('Card declined');
});

test.describe('Payment Edge Cases @regression', () => {
  test('should handle network timeout during payment', async ({ page }) => {
    await page.goto('/checkout');
    await expect(page.getByText('Please try again')).toBeVisible();
  });
});

test('should render 3D Secure iframe @slow', async ({ page }) => {
  test.slow();
  await page.goto('/checkout/3ds');
  await expect(page.getByText('Verified')).toBeVisible();
});

test('should apply loyalty points discount', async ({ page }) => {
  test.skip(process.env.CI !== 'true', 'Only run in CI — needs loyalty service');
  await page.goto('/checkout');
});

test('should handle Apple Pay on Safari', async ({ page, browserName }) => {
  test.skip(browserName !== 'webkit', 'Apple Pay only works in Safari');
  await page.goto('/checkout');
});

test('should display PayPal button', async ({ page }) => {
  test.fixme(); // Known broken — tracked in JIRA-1234
  await page.goto('/checkout');
  await expect(page.getByRole('button', { name: 'PayPal' })).toBeVisible();
});

test('should fail when submitting empty card form', async ({ page }) => {
  test.fail();
  await page.goto('/checkout');
  await page.getByRole('button', { name: 'Pay now' }).click();
  await expect(page.getByRole('alert')).toBeVisible();
});
```

**Annotation cheat sheet:**

| Annotation | Effect | When to use |
|---|---|---|
| `test.skip()` | Skips the test entirely | Feature not available in this env/browser |
| `test.skip(condition, reason)` | Conditional skip | Browser-specific or env-specific tests |
| `test.fixme()` | Skips and marks as "needs fix" | Known bug, not yet fixed |
| `test.slow()` | Triples the timeout | Tests with inherently slow workflows |
| `test.fail()` | Expects the test to fail; fails if it passes | Documenting a known bug with a regression guard |
| `test.info().annotations` | Add custom annotations | Custom metadata for reports |

---

### Pattern 5: Test Filtering

**Use when**: Running a subset of tests from the CLI or CI.
**Avoid when**: Never — know these commands.

```bash
# By tag (in test title)
npx playwright test --grep @smoke
npx playwright test --grep @regression
npx playwright test --grep-invert @slow     # everything except @slow

# By file
npx playwright test tests/auth/
npx playwright test tests/checkout/payment.spec.ts

# By test name
npx playwright test --grep "should login"

# By project (from playwright.config)
npx playwright test --project=chromium
npx playwright test --project=mobile-safari

# Combine filters
npx playwright test --grep @smoke --project=chromium
npx playwright test tests/checkout/ --grep @smoke

# By line number — run a single test
npx playwright test tests/auth/login.spec.ts:15
```

**Using tags with `test.describe.configure()`:**

**TypeScript:**

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'smoke',
      testMatch: '**/*.spec.ts',
      grep: /@smoke/,
    },
    {
      name: 'regression',
      testMatch: '**/*.spec.ts',
      grep: /@regression/,
    },
    {
      name: 'all',
      testMatch: '**/*.spec.ts',
      grepInvert: /@slow/,
    },
  ],
});
```

**JavaScript:**

```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  projects: [
    {
      name: 'smoke',
      testMatch: '**/*.spec.js',
      grep: /@smoke/,
    },
    {
      name: 'regression',
      testMatch: '**/*.spec.js',
      grep: /@regression/,
    },
    {
      name: 'all',
      testMatch: '**/*.spec.js',
      grepInvert: /@slow/,
    },
  ],
});
```

---

### Pattern 6: Parallel vs Serial Execution

**Use when**: Deciding how tests run relative to each other.
**Avoid when**: You have < 5 tests (parallelism doesn't matter).

**Default: always parallel.** Set `fullyParallel: true` in config.

**TypeScript:**

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  fullyParallel: true, // All tests run in parallel by default
  workers: process.env.CI ? 1 : undefined, // Use all cores locally, 1 in CI (or adjust)
});
```

**JavaScript:**

```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  fullyParallel: true,
  workers: process.env.CI ? 1 : undefined,
});
```

**Serial execution — use only when tests share external state you cannot isolate:**

**TypeScript:**

```typescript
// tests/onboarding/wizard.spec.ts
import { test, expect } from '@playwright/test';

// ONLY use serial when steps truly depend on prior state that cannot be set up independently
test.describe.serial('Onboarding Wizard', () => {
  test('step 1: user enters company name', async ({ page }) => {
    await page.goto('/onboarding');
    await page.getByLabel('Company name').fill('Acme Corp');
    await page.getByRole('button', { name: 'Next' }).click();
    await expect(page).toHaveURL('/onboarding/step-2');
  });

  test('step 2: user selects plan', async ({ page }) => {
    await page.goto('/onboarding/step-2');
    await page.getByRole('radio', { name: 'Pro plan' }).check();
    await page.getByRole('button', { name: 'Next' }).click();
    await expect(page).toHaveURL('/onboarding/step-3');
  });

  test('step 3: user confirms and completes', async ({ page }) => {
    await page.goto('/onboarding/step-3');
    await page.getByRole('button', { name: 'Complete setup' }).click();
    await expect(page.getByText('Welcome to Acme Corp')).toBeVisible();
  });
});
```

**JavaScript:**

```javascript
// tests/onboarding/wizard.spec.js
const { test, expect } = require('@playwright/test');

test.describe.serial('Onboarding Wizard', () => {
  test('step 1: user enters company name', async ({ page }) => {
    await page.goto('/onboarding');
    await page.getByLabel('Company name').fill('Acme Corp');
    await page.getByRole('button', { name: 'Next' }).click();
    await expect(page).toHaveURL('/onboarding/step-2');
  });

  test('step 2: user selects plan', async ({ page }) => {
    await page.goto('/onboarding/step-2');
    await page.getByRole('radio', { name: 'Pro plan' }).check();
    await page.getByRole('button', { name: 'Next' }).click();
    await expect(page).toHaveURL('/onboarding/step-3');
  });

  test('step 3: user confirms and completes', async ({ page }) => {
    await page.goto('/onboarding/step-3');
    await page.getByRole('button', { name: 'Complete setup' }).click();
    await expect(page.getByText('Welcome to Acme Corp')).toBeVisible();
  });
});
```

**Better alternative: test the full flow in one test with `test.step()`:**

**TypeScript:**

```typescript
// tests/onboarding/wizard.spec.ts
import { test, expect } from '@playwright/test';

test('user completes full onboarding wizard', async ({ page }) => {
  await test.step('enter company name', async () => {
    await page.goto('/onboarding');
    await page.getByLabel('Company name').fill('Acme Corp');
    await page.getByRole('button', { name: 'Next' }).click();
    await expect(page).toHaveURL('/onboarding/step-2');
  });

  await test.step('select plan', async () => {
    await page.getByRole('radio', { name: 'Pro plan' }).check();
    await page.getByRole('button', { name: 'Next' }).click();
    await expect(page).toHaveURL('/onboarding/step-3');
  });

  await test.step('confirm and complete', async () => {
    await page.getByRole('button', { name: 'Complete setup' }).click();
    await expect(page.getByText('Welcome to Acme Corp')).toBeVisible();
  });
});
```

**JavaScript:**

```javascript
// tests/onboarding/wizard.spec.js
const { test, expect } = require('@playwright/test');

test('user completes full onboarding wizard', async ({ page }) => {
  await test.step('enter company name', async () => {
    await page.goto('/onboarding');
    await page.getByLabel('Company name').fill('Acme Corp');
    await page.getByRole('button', { name: 'Next' }).click();
    await expect(page).toHaveURL('/onboarding/step-2');
  });

  await test.step('select plan', async () => {
    await page.getByRole('radio', { name: 'Pro plan' }).check();
    await page.getByRole('button', { name: 'Next' }).click();
    await expect(page).toHaveURL('/onboarding/step-3');
  });

  await test.step('confirm and complete', async () => {
    await page.getByRole('button', { name: 'Complete setup' }).click();
    await expect(page.getByText('Welcome to Acme Corp')).toBeVisible();
  });
});
```

---

### Pattern 7: Monorepo Testing

**Use when**: A single repository contains multiple apps or packages that each need E2E tests.
**Avoid when**: Single app repo.

**TypeScript:**

```typescript
// playwright.config.ts (root of monorepo)
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'web-app',
      testDir: './apps/web/tests',
      use: {
        baseURL: 'http://localhost:3000',
      },
    },
    {
      name: 'admin-panel',
      testDir: './apps/admin/tests',
      use: {
        baseURL: 'http://localhost:3001',
      },
    },
    {
      name: 'marketing-site',
      testDir: './apps/marketing/tests',
      use: {
        baseURL: 'http://localhost:4000',
      },
    },
  ],
});
```

**JavaScript:**

```javascript
// playwright.config.js (root of monorepo)
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  projects: [
    {
      name: 'web-app',
      testDir: './apps/web/tests',
      use: {
        baseURL: 'http://localhost:3000',
      },
    },
    {
      name: 'admin-panel',
      testDir: './apps/admin/tests',
      use: {
        baseURL: 'http://localhost:3001',
      },
    },
    {
      name: 'marketing-site',
      testDir: './apps/marketing/tests',
      use: {
        baseURL: 'http://localhost:4000',
      },
    },
  ],
});
```

**Monorepo directory layout:**

```
monorepo/
├── apps/
│   ├── web/
│   │   ├── src/
│   │   └── tests/
│   │       ├── auth/
│   │       │   └── login.spec.ts
│   │       └── dashboard/
│   │           └── widgets.spec.ts
│   ├── admin/
│   │   ├── src/
│   │   └── tests/
│   │       └── user-management.spec.ts
│   └── marketing/
│       ├── src/
│       └── tests/
│           └── landing-page.spec.ts
├── packages/
│   └── shared-fixtures/
│       ├── auth.fixture.ts
│       └── index.ts
└── playwright.config.ts
```

Run only one app's tests:

```bash
npx playwright test --project=web-app
npx playwright test --project=admin-panel
```

## Decision Guide

```
How many tests do you have?
│
├── < 20 tests (small)
│   ├── Flat structure: all .spec.ts files in tests/
│   ├── No subdirectories needed
│   ├── Tags optional — just run everything
│   └── fullyParallel: true, single config project
│
├── 20–200 tests (medium)
│   ├── Feature subdirectories: tests/auth/, tests/checkout/
│   ├── Use @smoke tag for critical-path subset (< 15 min)
│   ├── Shared fixtures in tests/fixtures/
│   ├── Page objects in tests/page-objects/ (if you use them)
│   └── Consider separate projects for different browsers
│
└── 200+ tests (large)
    ├── Top-level split: tests/e2e/, tests/api/, tests/visual/
    ├── Feature subdirectories under each
    ├── @smoke, @regression, @slow tags — multiple CI pipelines
    ├── Sharding in CI for faster runs
    ├── Project-based filtering: smoke project, full project
    └── Shared fixtures as a package in monorepo
```

```
Should I use test.describe.serial()?
│
├── Can each test set up its own state via API/fixture?
│   └── YES → Do NOT use serial. Use independent parallel tests.
│
├── Is this a multi-step wizard where each step changes server state
│   that cannot be reset between tests?
│   └── Write it as ONE test with test.step() instead.
│
└── Is this genuinely stateful (e.g., database migration sequence)?
    └── Use serial as last resort. Add a comment explaining why.
```

## Anti-Patterns

### One giant test file

```typescript
// BAD: tests/all-tests.spec.ts with 80 tests and 2000+ lines
test.describe('Everything', () => {
  test('login works', async ({ page }) => { /* ... */ });
  test('signup works', async ({ page }) => { /* ... */ });
  test('cart works', async ({ page }) => { /* ... */ });
  // ... 77 more tests
});
```

**Fix:** Split by feature — one file per feature area, 5–15 tests per file.

---

### Meaningless test names

```typescript
// BAD
test('test1', async ({ page }) => { /* ... */ });
test('test2', async ({ page }) => { /* ... */ });
test('payment test', async ({ page }) => { /* ... */ });
test('it works', async ({ page }) => { /* ... */ });
```

**Fix:** Describe behavior. When a test fails, the name should tell you what broke.

```typescript
// GOOD
test('should reject expired credit card', async ({ page }) => { /* ... */ });
test('user can update shipping address during checkout', async ({ page }) => { /* ... */ });
```

---

### Deep describe nesting

```typescript
// BAD: 3+ levels deep — hard to read, hard to find tests in reports
test.describe('Auth', () => {
  test.describe('Login', () => {
    test.describe('With MFA', () => {
      test.describe('SMS', () => {
        test('should send code', async ({ page }) => { /* ... */ });
      });
    });
  });
});
```

**Fix:** Max 2 levels. Split deeper nesting into separate files.

```typescript
// GOOD: tests/auth/login-mfa-sms.spec.ts
test.describe('Login with SMS MFA', () => {
  test('should send verification code', async ({ page }) => { /* ... */ });
  test('should reject invalid code', async ({ page }) => { /* ... */ });
});
```

---

### Using `test.describe.serial()` as the default

```typescript
// BAD: serial for no reason — kills parallelism, creates hidden dependencies
test.describe.serial('User Profile', () => {
  test('should display profile page', async ({ page }) => { /* ... */ });
  test('should update display name', async ({ page }) => { /* ... */ });
  test('should upload avatar', async ({ page }) => { /* ... */ });
});
```

**Fix:** Each test should be independent. Use `beforeEach` or fixtures to set up state.

```typescript
// GOOD
test.describe('User Profile', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/profile');
  });

  test('should display profile page', async ({ page }) => { /* ... */ });
  test('should update display name', async ({ page }) => { /* ... */ });
  test('should upload avatar', async ({ page }) => { /* ... */ });
});
```

---

### Relying on test execution order

```typescript
// BAD: test 2 depends on test 1 creating data
test('should create a product', async ({ page }) => {
  // creates "Widget X" in the database
});

test('should edit the product', async ({ page }) => {
  // assumes "Widget X" exists — breaks if run alone or in parallel
});
```

**Fix:** Each test creates its own data via API calls or fixtures.

```typescript
// GOOD
test('should edit a product', async ({ page, request }) => {
  // Set up test data independently
  const response = await request.post('/api/products', {
    data: { name: 'Widget X', price: 9.99 },
  });
  const product = await response.json();

  await page.goto(`/products/${product.id}/edit`);
  await page.getByLabel('Name').fill('Widget X Updated');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText('Widget X Updated')).toBeVisible();
});
```

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Tests pass alone but fail together | Shared state between tests (cookies, DB rows, global variables) | Isolate each test — use fixtures for setup/teardown |
| `--grep @smoke` matches nothing | Tag not in test title string | Verify the tag appears literally in `test('... @smoke', ...)` |
| Serial tests cascade-fail | One test fails, all subsequent tests skip | Rewrite as independent tests or use `test.step()` in a single test |
| Tests run slower than expected | `fullyParallel` not set | Add `fullyParallel: true` in `playwright.config` |
| Wrong tests run in CI | `testMatch` or `testDir` misconfigured | Check `playwright.config` — print resolved config with `npx playwright test --list` |
| Monorepo tests pick up wrong files | Default `testDir` is `.` | Set explicit `testDir` per project |

## Related

- [core/configuration.md](foundations/configuration.md) — `testMatch`, `testDir`, `fullyParallel`, `workers`
- [core/fixtures-and-hooks.md](foundations/fixtures-and-hooks.md) — shared setup via fixtures instead of `beforeAll`
- [core/test-architecture.md](decisions/test-architecture.md) — when to write E2E vs API vs component tests
- [ci/parallel-and-sharding.md](infrastructure/parallel-and-sharding.md) — CI sharding for large suites
- [ci/projects-and-dependencies.md](infrastructure/projects-and-dependencies.md) — multi-project config
