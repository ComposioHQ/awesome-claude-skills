# Test Architecture: E2E vs Component vs API

> **When to use**: When deciding what kind of test to write for a feature. Before you write any test, ask: "What is the cheapest test that gives me confidence this works?"

## Quick Answer

Most teams write too many E2E tests. Default to the **testing trophy** approach:

1. **API tests** for business logic, data validation, and permissions (fastest, most stable)
2. **Component tests** for isolated UI behavior, form validation, and interactive widgets (fast, focused)
3. **E2E tests only for critical user paths** -- login, checkout, onboarding (slow, highest confidence)

If you only have time for one layer, start with API tests. They cover the most ground with the least maintenance cost.

## The Testing Trophy

The testing trophy (coined by Kent C. Dodds) replaces the traditional testing pyramid for modern web apps:

```
        ╱ ╲
       ╱ E2E ╲           Thin layer -- critical paths only
      ╱─────────╲
     ╱           ╲
    ╱ Integration  ╲      Thickest layer -- component + API tests
   ╱                 ╲
  ╱───────────────────╲
 ╱        Unit         ╲   Utility functions, pure logic
╱───────────────────────╲
     Static Analysis       TypeScript, ESLint, Prettier
```

**Where Playwright fits**:
- **E2E layer**: `@playwright/test` with a browser -- full user flow testing
- **Integration / Component layer**: `@playwright/experimental-ct-*` -- render components in a real browser without a full app
- **Integration / API layer**: `@playwright/test` with `request` context -- HTTP testing without a browser
- **Static layer**: Not Playwright's job. Use TypeScript and ESLint.

The trophy shape means integration tests (component + API) should be your **largest** investment. They give the best ratio of confidence to cost.

## Decision Matrix

| What You're Testing | Test Type | Why | Playwright Example |
|---|---|---|---|
| Login / auth flow | E2E | Cross-page, cookies, redirects, session state | Full browser flow with `storageState` |
| Form submission | Component | Isolated validation logic, error states, UX | Mount form component, test states |
| CRUD operations | API | Data integrity matters more than UI for create/update/delete | `request.post()`, `request.put()`, `request.delete()` |
| Search with results UI | Component + API | API test for query logic; component test for rendering results | Split: API for data, component for display |
| Cross-page navigation | E2E | Routing, history, deep linking are browser concerns | `page.goto()`, `page.waitForURL()` |
| Error handling (API errors) | API | Validate status codes, error shapes, edge cases without UI | `expect(response.status()).toBe(422)` |
| Error handling (UI feedback) | Component | Toast, banner, inline error rendering | Mount component, mock error response |
| Accessibility | Component | Test ARIA roles, keyboard nav per-component; faster than full E2E | `expect(locator).toHaveAttribute('aria-expanded')` |
| Responsive layout | Component | Viewport-specific rendering without full app overhead | `mount()` with viewport config |
| API integration (contract) | API | Validate response shapes, headers, auth independently | `request.get()` with schema validation |
| Real-time features (WebSocket) | E2E | Requires full browser environment for WebSocket connections | `page.evaluate()` with WebSocket listeners |
| Payment / checkout flow | E2E | Multi-step, third-party iframes, real-world reliability | Full browser flow, `frameLocator()` |
| Onboarding / wizard | E2E | Multi-step, state persists across pages | `test.step()` for each wizard stage |
| Individual widget behavior | Component | Toggle, accordion, date picker, modal -- isolated interactions | Mount component, test open/close/select |
| Permissions / authorization | API | Role-based access is backend logic; test without UI overhead | Request with different auth tokens |

## When to Use E2E Tests

**Best for**:
- Critical user flows that generate revenue (checkout, signup, subscription)
- Authentication and authorization flows (login, SSO, MFA, password reset)
- Multi-page workflows where state carries across navigation (wizards, onboarding)
- Flows involving third-party iframes (payment widgets, embedded forms)
- Smoke tests validating the entire stack is wired together
- Real-time collaboration features requiring multiple browser contexts

**Avoid for**:
- Testing every permutation of form validation (use component tests)
- CRUD operations where the UI is a thin wrapper (use API tests)
- Verifying individual component states (use component tests)
- Testing API response shapes or error codes (use API tests)
- Responsive layout at every breakpoint (use component tests)
- Edge cases that only affect the backend (use API tests)

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// E2E: critical checkout flow -- this justifies the cost of a full browser
test.describe('checkout flow', () => {
  test.beforeEach(async ({ page }) => {
    // Seed data via API to keep E2E tests focused on the flow, not setup
    await page.request.post('/api/test/seed-cart', {
      data: { items: [{ sku: 'SHOE-001', qty: 1 }] },
    });
    await page.goto('/cart');
  });

  test('completes purchase with valid payment', async ({ page }) => {
    await test.step('review cart', async () => {
      await expect(page.getByRole('heading', { name: 'Your Cart' })).toBeVisible();
      await expect(page.getByText('Running Shoes')).toBeVisible();
      await page.getByRole('button', { name: 'Proceed to checkout' }).click();
    });

    await test.step('fill shipping details', async () => {
      await page.getByLabel('Full name').fill('Jane Doe');
      await page.getByLabel('Address').fill('123 Main St');
      await page.getByLabel('City').fill('Portland');
      await page.getByRole('combobox', { name: 'State' }).selectOption('OR');
      await page.getByLabel('ZIP code').fill('97201');
      await page.getByRole('button', { name: 'Continue to payment' }).click();
    });

    await test.step('enter payment', async () => {
      const paymentFrame = page.frameLocator('iframe[title="Payment"]');
      await paymentFrame.getByLabel('Card number').fill('4242424242424242');
      await paymentFrame.getByLabel('Expiration').fill('12/28');
      await paymentFrame.getByLabel('CVC').fill('123');
      await page.getByRole('button', { name: 'Place order' }).click();
    });

    await test.step('verify confirmation', async () => {
      await page.waitForURL('**/order/confirmation/**');
      await expect(page.getByRole('heading', { name: 'Order Confirmed' })).toBeVisible();
      await expect(page.getByText(/Order #\d+/)).toBeVisible();
    });
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('checkout flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.request.post('/api/test/seed-cart', {
      data: { items: [{ sku: 'SHOE-001', qty: 1 }] },
    });
    await page.goto('/cart');
  });

  test('completes purchase with valid payment', async ({ page }) => {
    await test.step('review cart', async () => {
      await expect(page.getByRole('heading', { name: 'Your Cart' })).toBeVisible();
      await expect(page.getByText('Running Shoes')).toBeVisible();
      await page.getByRole('button', { name: 'Proceed to checkout' }).click();
    });

    await test.step('fill shipping details', async () => {
      await page.getByLabel('Full name').fill('Jane Doe');
      await page.getByLabel('Address').fill('123 Main St');
      await page.getByLabel('City').fill('Portland');
      await page.getByRole('combobox', { name: 'State' }).selectOption('OR');
      await page.getByLabel('ZIP code').fill('97201');
      await page.getByRole('button', { name: 'Continue to payment' }).click();
    });

    await test.step('enter payment', async () => {
      const paymentFrame = page.frameLocator('iframe[title="Payment"]');
      await paymentFrame.getByLabel('Card number').fill('4242424242424242');
      await paymentFrame.getByLabel('Expiration').fill('12/28');
      await paymentFrame.getByLabel('CVC').fill('123');
      await page.getByRole('button', { name: 'Place order' }).click();
    });

    await test.step('verify confirmation', async () => {
      await page.waitForURL('**/order/confirmation/**');
      await expect(page.getByRole('heading', { name: 'Order Confirmed' })).toBeVisible();
      await expect(page.getByText(/Order #\d+/)).toBeVisible();
    });
  });
});
```

## When to Use Component Tests

**Best for**:
- Form validation (required fields, format rules, error messages, field interactions)
- Interactive widgets (modals, dropdowns, accordions, date pickers, tabs)
- Conditional rendering (show/hide logic, loading states, empty states, error states)
- Accessibility per-component (ARIA attributes, keyboard navigation, focus management)
- Responsive layout at different viewports without full app overhead
- Visual states (hover, focus, disabled, selected) for design system components

**Avoid for**:
- Testing routing or navigation between pages (use E2E)
- Flows requiring real cookies, sessions, or server-side state (use E2E)
- Data persistence or API contract validation (use API tests)
- Third-party iframe interactions (use E2E)
- Anything requiring multiple pages or browser contexts (use E2E)

**TypeScript** (React example using `@playwright/experimental-ct-react`)
```typescript
import { test, expect } from '@playwright/experimental-ct-react';
import { LoginForm } from '../src/components/LoginForm';

test.describe('LoginForm component', () => {
  test('shows validation errors for empty submission', async ({ mount }) => {
    const component = await mount(<LoginForm onSubmit={() => {}} />);

    await component.getByRole('button', { name: 'Sign in' }).click();

    await expect(component.getByText('Email is required')).toBeVisible();
    await expect(component.getByText('Password is required')).toBeVisible();
  });

  test('shows error for invalid email format', async ({ mount }) => {
    const component = await mount(<LoginForm onSubmit={() => {}} />);

    await component.getByLabel('Email').fill('not-an-email');
    await component.getByLabel('Password').fill('password123');
    await component.getByRole('button', { name: 'Sign in' }).click();

    await expect(component.getByText('Enter a valid email address')).toBeVisible();
  });

  test('calls onSubmit with credentials for valid input', async ({ mount }) => {
    const submitted: Array<{ email: string; password: string }> = [];
    const component = await mount(
      <LoginForm onSubmit={(data) => submitted.push(data)} />
    );

    await component.getByLabel('Email').fill('jane@example.com');
    await component.getByLabel('Password').fill('s3cure!Pass');
    await component.getByRole('button', { name: 'Sign in' }).click();

    expect(submitted).toHaveLength(1);
    expect(submitted[0]).toEqual({
      email: 'jane@example.com',
      password: 's3cure!Pass',
    });
  });

  test('disables submit button while loading', async ({ mount }) => {
    const component = await mount(<LoginForm onSubmit={() => {}} loading={true} />);

    await expect(component.getByRole('button', { name: 'Signing in...' })).toBeDisabled();
  });

  test('meets accessibility requirements', async ({ mount }) => {
    const component = await mount(<LoginForm onSubmit={() => {}} />);

    // Labels are associated with inputs
    await expect(component.getByRole('textbox', { name: 'Email' })).toBeVisible();

    // Error messages are announced via aria-live
    await component.getByRole('button', { name: 'Sign in' }).click();
    await expect(component.getByRole('alert')).toContainText('Email is required');
  });
});
```

**JavaScript** (React example using `@playwright/experimental-ct-react`)
```javascript
const { test, expect } = require('@playwright/experimental-ct-react');
const { LoginForm } = require('../src/components/LoginForm');

test.describe('LoginForm component', () => {
  test('shows validation errors for empty submission', async ({ mount }) => {
    const component = await mount(<LoginForm onSubmit={() => {}} />);

    await component.getByRole('button', { name: 'Sign in' }).click();

    await expect(component.getByText('Email is required')).toBeVisible();
    await expect(component.getByText('Password is required')).toBeVisible();
  });

  test('calls onSubmit with credentials for valid input', async ({ mount }) => {
    const submitted = [];
    const component = await mount(
      <LoginForm onSubmit={(data) => submitted.push(data)} />
    );

    await component.getByLabel('Email').fill('jane@example.com');
    await component.getByLabel('Password').fill('s3cure!Pass');
    await component.getByRole('button', { name: 'Sign in' }).click();

    expect(submitted).toHaveLength(1);
    expect(submitted[0]).toEqual({
      email: 'jane@example.com',
      password: 's3cure!Pass',
    });
  });

  test('disables submit button while loading', async ({ mount }) => {
    const component = await mount(<LoginForm onSubmit={() => {}} loading={true} />);

    await expect(component.getByRole('button', { name: 'Signing in...' })).toBeDisabled();
  });
});
```

## When to Use API Tests

**Best for**:
- CRUD operations (create, read, update, delete resources)
- Input validation and error responses (400, 422 with structured error bodies)
- Permission and authorization checks (role-based access, token scoping)
- Data integrity and business rules (uniqueness, referential integrity, calculations)
- API contract verification (response shapes, headers, pagination)
- Edge cases that are expensive to reproduce through the UI (rate limiting, concurrent updates)
- Test data setup and teardown for E2E tests (seed via API, verify via API)

**Avoid for**:
- Testing how errors are displayed to the user (use component tests)
- Testing browser-specific behavior (cookies, redirects, navigation)
- Verifying visual layout or responsive design (use component tests)
- Flows requiring JavaScript execution or DOM interaction (use E2E or component)
- Third-party iframe interactions (use E2E)

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Users API', () => {
  let authToken: string;

  test.beforeAll(async ({ request }) => {
    const response = await request.post('/api/auth/login', {
      data: { email: 'admin@example.com', password: 'admin-pass' },
    });
    const body = await response.json();
    authToken = body.token;
  });

  test('creates a user with valid data', async ({ request }) => {
    const response = await request.post('/api/users', {
      headers: { Authorization: `Bearer ${authToken}` },
      data: {
        email: 'newuser@example.com',
        name: 'Jane Doe',
        role: 'editor',
      },
    });

    expect(response.status()).toBe(201);

    const user = await response.json();
    expect(user).toMatchObject({
      email: 'newuser@example.com',
      name: 'Jane Doe',
      role: 'editor',
    });
    expect(user).toHaveProperty('id');
    expect(user).toHaveProperty('createdAt');
  });

  test('rejects duplicate email with 409', async ({ request }) => {
    const response = await request.post('/api/users', {
      headers: { Authorization: `Bearer ${authToken}` },
      data: {
        email: 'admin@example.com', // already exists
        name: 'Duplicate',
        role: 'viewer',
      },
    });

    expect(response.status()).toBe(409);

    const error = await response.json();
    expect(error.message).toContain('already exists');
  });

  test('returns 422 for invalid email format', async ({ request }) => {
    const response = await request.post('/api/users', {
      headers: { Authorization: `Bearer ${authToken}` },
      data: {
        email: 'not-valid',
        name: 'Bad Email',
        role: 'viewer',
      },
    });

    expect(response.status()).toBe(422);

    const error = await response.json();
    expect(error.errors).toContainEqual(
      expect.objectContaining({ field: 'email' })
    );
  });

  test('non-admin cannot create users', async ({ request }) => {
    // Login as a non-admin user
    const loginResponse = await request.post('/api/auth/login', {
      data: { email: 'viewer@example.com', password: 'viewer-pass' },
    });
    const { token: viewerToken } = await loginResponse.json();

    const response = await request.post('/api/users', {
      headers: { Authorization: `Bearer ${viewerToken}` },
      data: {
        email: 'another@example.com',
        name: 'Unauthorized',
        role: 'editor',
      },
    });

    expect(response.status()).toBe(403);
  });

  test('lists users with pagination', async ({ request }) => {
    const response = await request.get('/api/users', {
      headers: { Authorization: `Bearer ${authToken}` },
      params: { page: '1', limit: '10' },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.data).toBeInstanceOf(Array);
    expect(body.data.length).toBeLessThanOrEqual(10);
    expect(body).toHaveProperty('total');
    expect(body).toHaveProperty('page', 1);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Users API', () => {
  let authToken;

  test.beforeAll(async ({ request }) => {
    const response = await request.post('/api/auth/login', {
      data: { email: 'admin@example.com', password: 'admin-pass' },
    });
    const body = await response.json();
    authToken = body.token;
  });

  test('creates a user with valid data', async ({ request }) => {
    const response = await request.post('/api/users', {
      headers: { Authorization: `Bearer ${authToken}` },
      data: {
        email: 'newuser@example.com',
        name: 'Jane Doe',
        role: 'editor',
      },
    });

    expect(response.status()).toBe(201);

    const user = await response.json();
    expect(user).toMatchObject({
      email: 'newuser@example.com',
      name: 'Jane Doe',
      role: 'editor',
    });
    expect(user).toHaveProperty('id');
    expect(user).toHaveProperty('createdAt');
  });

  test('rejects duplicate email with 409', async ({ request }) => {
    const response = await request.post('/api/users', {
      headers: { Authorization: `Bearer ${authToken}` },
      data: {
        email: 'admin@example.com',
        name: 'Duplicate',
        role: 'viewer',
      },
    });

    expect(response.status()).toBe(409);

    const error = await response.json();
    expect(error.message).toContain('already exists');
  });

  test('non-admin cannot create users', async ({ request }) => {
    const loginResponse = await request.post('/api/auth/login', {
      data: { email: 'viewer@example.com', password: 'viewer-pass' },
    });
    const { token: viewerToken } = await loginResponse.json();

    const response = await request.post('/api/users', {
      headers: { Authorization: `Bearer ${viewerToken}` },
      data: {
        email: 'another@example.com',
        name: 'Unauthorized',
        role: 'editor',
      },
    });

    expect(response.status()).toBe(403);
  });
});
```

## Combining Test Types

The most effective test suites layer all three types. Here is how they work together for a "user management" feature:

### Layer 1: API Tests (60% of test count)

Cover every permutation of the backend logic. These are cheap to run and maintain.

```
tests/api/users.spec.ts
  - creates user with valid data (201)
  - rejects duplicate email (409)
  - rejects invalid email format (422)
  - rejects missing required fields (422)
  - non-admin cannot create users (403)
  - unauthenticated request returns 401
  - lists users with pagination
  - filters users by role
  - updates user profile
  - soft-deletes a user
  - prevents deleting last admin
```

### Layer 2: Component Tests (30% of test count)

Cover every visual state and interaction of the UI components.

```
tests/components/UserForm.spec.tsx
  - shows validation errors on empty submit
  - shows inline error for invalid email
  - disables submit while loading
  - calls onSubmit with form data
  - resets form after successful submit

tests/components/UserTable.spec.tsx
  - renders user rows from props
  - shows empty state when no users
  - handles delete confirmation modal
  - sorts by column header click
  - shows role badges with correct colors
```

### Layer 3: E2E Tests (10% of test count)

Cover only the critical path that proves the full stack works together.

```
tests/e2e/user-management.spec.ts
  - admin creates a user and sees them in the list
  - admin edits a user's role
  - viewer cannot access user management page
```

### The math

For this single feature, you might have:
- **11 API tests** -- run in ~2 seconds total, no browser needed
- **10 component tests** -- run in ~5 seconds total, real browser but no server
- **3 E2E tests** -- run in ~15 seconds total, full stack

Total: 24 tests, ~22 seconds. The 11 API tests catch most regressions. The 10 component tests catch UI bugs. The 3 E2E tests prove the wiring works. If the E2E tests fail but API and component tests pass, you know the problem is in the integration layer (routing, state management, API client) -- not in the business logic or UI components.

## Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|---|---|---|
| E2E test for every form validation rule | 30-second browser test for something an API test covers in 200ms | API test for validation logic, one component test for error display |
| No API tests -- all E2E | Slow suite, flaky from UI timing, hard to diagnose failures | API tests for data/logic, E2E for critical paths only |
| Component tests that mock everything | Tests pass but app is broken because mocks drift from reality | Mock only external boundaries; use API tests to verify real contracts |
| Duplicating assertions across layers | Same check in API, component, AND E2E test -- triple maintenance cost | Each layer tests what it is uniquely positioned to verify |
| E2E test that creates its own test data via the UI | 2-minute test where 90 seconds is setup; breaks when unrelated UI changes | Seed data via API calls in `beforeEach`, then test the actual flow |
| Testing third-party behavior | Testing that Stripe validates card numbers (that is Stripe's job) | Mock Stripe in component/E2E tests; trust their API contract |
| Skipping the API layer entirely | UI tests catch the bug but you can't tell if it is frontend or backend | API tests isolate backend bugs; component tests isolate frontend bugs |
| One giant E2E test for the whole feature | 5-minute test that fails somewhere in the middle with no clear cause | Break into focused E2E tests per critical path; use `test.step()` for clarity |

## Related

- [core/test-organization.md](test-organization.md) -- file structure and naming conventions for each test type
- [core/api-testing.md](api-testing.md) -- deep-dive on Playwright's `request` API for HTTP testing
- [core/component-testing.md](component-testing.md) -- setting up and writing component tests with Playwright CT
- [core/authentication.md](authentication.md) -- auth flow testing patterns (E2E + `storageState` reuse)
- [core/when-to-mock.md](when-to-mock.md) -- when to mock network requests vs hit real services
- [pom/pom-vs-fixtures-vs-helpers.md](../pom/pom-vs-fixtures-vs-helpers.md) -- organizing shared test logic across layers
