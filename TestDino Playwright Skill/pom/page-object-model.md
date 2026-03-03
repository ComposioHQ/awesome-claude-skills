# Page Object Model

> **When to use**: Any page or component is touched by more than one test file, or a single test file interacts with more than two distinct UI regions.

Page objects encapsulate **actions**, not locators. A test should read like a user story: `await loginPage.login('admin', 'secret')`, never `await loginPage.usernameInput.fill('admin')`. The POM is a boundary between "what the user does" and "how the UI is structured." Assertions stay in tests, never inside page objects.

## Quick Reference

| Concept | Rule |
|---|---|
| Locators | Defined as `readonly` properties in the constructor or as getters. Never exposed raw to tests. |
| Actions | Public methods that perform a user-visible behavior. Return `Promise<void>` or the next page object. |
| Assertions | **Never** inside page objects. Tests own all `expect()` calls. |
| Navigation | Methods that navigate return the destination page object, not `void`. |
| State | Page objects are stateless. No caching locator text, no tracking "current step." |
| Constructor | Takes `Page` (or `Locator` for components). Nothing else. No URLs, no test data. |
| Naming | `LoginPage`, `DashboardPage`, `NavbarComponent`. File: `login.page.ts`, `navbar.component.ts`. |

## Patterns

### 1. Basic POM Class

**Use when**: A page has 3+ interactions across multiple tests.
**Avoid when**: A page is used in a single test file with trivial interactions -- use a helper function instead.

**TypeScript**

```typescript
// tests/pages/login.page.ts
import { type Page, type Locator } from '@playwright/test';

export class LoginPage {
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(private readonly page: Page) {
    this.usernameInput = page.getByLabel('Username');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

**JavaScript**

```javascript
// tests/pages/login.page.js
// @ts-check

export class LoginPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page;
    this.usernameInput = page.getByLabel('Username');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

**Test usage**

```typescript
// tests/auth.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';

test('successful login redirects to dashboard', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('admin', 'password123');

  await expect(page).toHaveURL('/dashboard');
});

test('invalid credentials show error', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('admin', 'wrong');

  await expect(loginPage.errorMessage).toBeVisible();
  await expect(loginPage.errorMessage).toHaveText('Invalid credentials');
});
```

### 2. Component Objects

**Use when**: A UI element (navbar, sidebar, modal, form, table) appears on multiple pages.
**Avoid when**: The component is page-specific and never reused.

Components take a `Locator` (their root container), not a `Page`. This scopes all queries to the component's DOM subtree and allows composing components into page objects.

**TypeScript**

```typescript
// tests/components/navbar.component.ts
import { type Locator } from '@playwright/test';

export class NavbarComponent {
  readonly profileMenu: Locator;
  readonly searchInput: Locator;
  readonly notificationBell: Locator;

  constructor(private readonly root: Locator) {
    this.profileMenu = root.getByRole('button', { name: 'Profile' });
    this.searchInput = root.getByRole('searchbox');
    this.notificationBell = root.getByRole('button', { name: 'Notifications' });
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
  }

  async openProfile() {
    await this.profileMenu.click();
  }

  async openNotifications() {
    await this.notificationBell.click();
  }
}

// tests/components/modal.component.ts
import { type Locator } from '@playwright/test';

export class ModalComponent {
  readonly title: Locator;
  readonly closeButton: Locator;
  readonly confirmButton: Locator;
  readonly cancelButton: Locator;

  constructor(private readonly root: Locator) {
    this.title = root.getByRole('heading');
    this.closeButton = root.getByRole('button', { name: 'Close' });
    this.confirmButton = root.getByRole('button', { name: 'Confirm' });
    this.cancelButton = root.getByRole('button', { name: 'Cancel' });
  }

  async confirm() {
    await this.confirmButton.click();
  }

  async cancel() {
    await this.cancelButton.click();
  }

  async close() {
    await this.closeButton.click();
  }
}

// tests/pages/dashboard.page.ts
import { type Page } from '@playwright/test';
import { NavbarComponent } from '../components/navbar.component';
import { ModalComponent } from '../components/modal.component';

export class DashboardPage {
  readonly navbar: NavbarComponent;
  readonly deleteModal: ModalComponent;

  constructor(private readonly page: Page) {
    this.navbar = new NavbarComponent(page.getByRole('navigation'));
    this.deleteModal = new ModalComponent(page.getByRole('dialog'));
  }

  async goto() {
    await this.page.goto('/dashboard');
  }

  async deleteItem(name: string) {
    await this.page.getByRole('row', { name }).getByRole('button', { name: 'Delete' }).click();
    await this.deleteModal.confirm();
  }
}
```

**JavaScript**

```javascript
// tests/components/navbar.component.js
// @ts-check

export class NavbarComponent {
  /** @param {import('@playwright/test').Locator} root */
  constructor(root) {
    this.root = root;
    this.profileMenu = root.getByRole('button', { name: 'Profile' });
    this.searchInput = root.getByRole('searchbox');
    this.notificationBell = root.getByRole('button', { name: 'Notifications' });
  }

  async search(query) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
  }

  async openProfile() {
    await this.profileMenu.click();
  }

  async openNotifications() {
    await this.notificationBell.click();
  }
}

// tests/pages/dashboard.page.js
// @ts-check
import { NavbarComponent } from '../components/navbar.component.js';
import { ModalComponent } from '../components/modal.component.js';

export class DashboardPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page;
    this.navbar = new NavbarComponent(page.getByRole('navigation'));
    this.deleteModal = new ModalComponent(page.getByRole('dialog'));
  }

  async goto() {
    await this.page.goto('/dashboard');
  }

  async deleteItem(name) {
    await this.page.getByRole('row', { name }).getByRole('button', { name: 'Delete' }).click();
    await this.deleteModal.confirm();
  }
}
```

### 3. Page Object with Navigation

**Use when**: An action on one page navigates to a different page (form submission, link click, redirect).
**Avoid when**: Navigation is uncertain (might fail validation and stay on the same page).

When a method causes navigation, return the destination page object. This creates a typed chain that mirrors the user flow and catches stale page object usage at the call site.

**TypeScript**

```typescript
// tests/pages/login.page.ts
import { type Page } from '@playwright/test';
import { DashboardPage } from './dashboard.page';

export class LoginPage {
  constructor(private readonly page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  /** Returns DashboardPage on success. Call only when credentials are valid. */
  async loginAs(username: string, password: string): Promise<DashboardPage> {
    await this.page.getByLabel('Username').fill(username);
    await this.page.getByLabel('Password').fill(password);
    await this.page.getByRole('button', { name: 'Sign in' }).click();
    await this.page.waitForURL('/dashboard');
    return new DashboardPage(this.page);
  }

  /** Use for invalid credential tests -- stays on login page. */
  async loginExpectingError(username: string, password: string) {
    await this.page.getByLabel('Username').fill(username);
    await this.page.getByLabel('Password').fill(password);
    await this.page.getByRole('button', { name: 'Sign in' }).click();
  }
}

// tests/pages/dashboard.page.ts
import { type Page } from '@playwright/test';
import { SettingsPage } from './settings.page';

export class DashboardPage {
  constructor(private readonly page: Page) {}

  async gotoSettings(): Promise<SettingsPage> {
    await this.page.getByRole('link', { name: 'Settings' }).click();
    await this.page.waitForURL('/settings');
    return new SettingsPage(this.page);
  }
}
```

**JavaScript**

```javascript
// tests/pages/login.page.js
// @ts-check
import { DashboardPage } from './dashboard.page.js';

export class LoginPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/login');
  }

  /** @returns {Promise<DashboardPage>} */
  async loginAs(username, password) {
    await this.page.getByLabel('Username').fill(username);
    await this.page.getByLabel('Password').fill(password);
    await this.page.getByRole('button', { name: 'Sign in' }).click();
    await this.page.waitForURL('/dashboard');
    return new DashboardPage(this.page);
  }

  async loginExpectingError(username, password) {
    await this.page.getByLabel('Username').fill(username);
    await this.page.getByLabel('Password').fill(password);
    await this.page.getByRole('button', { name: 'Sign in' }).click();
  }
}
```

**Test usage showing the navigation chain**

```typescript
// tests/settings.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';

test('user can navigate from login to settings', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();

  const dashboard = await loginPage.loginAs('admin', 'password123');
  const settings = await dashboard.gotoSettings();

  await expect(page).toHaveURL('/settings');
});
```

### 4. Page Object as Fixture

**Use when**: Page objects are used in 3+ test files. This is the recommended approach for mature test suites.
**Avoid when**: Early prototyping with rapidly changing pages.

Fixtures eliminate boilerplate instantiation, provide automatic cleanup, and make POMs available via destructuring -- identical to built-in `page` and `request` fixtures.

**TypeScript**

```typescript
// tests/fixtures.ts
import { test as base } from '@playwright/test';
import { LoginPage } from './pages/login.page';
import { DashboardPage } from './pages/dashboard.page';
import { SettingsPage } from './pages/settings.page';

type PageObjects = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  settingsPage: SettingsPage;
};

export const test = base.extend<PageObjects>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
  settingsPage: async ({ page }, use) => {
    await use(new SettingsPage(page));
  },
});

export { expect } from '@playwright/test';
```

**JavaScript**

```javascript
// tests/fixtures.js
// @ts-check
import { test as base } from '@playwright/test';
import { LoginPage } from './pages/login.page.js';
import { DashboardPage } from './pages/dashboard.page.js';
import { SettingsPage } from './pages/settings.page.js';

export const test = base.extend({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
  settingsPage: async ({ page }, use) => {
    await use(new SettingsPage(page));
  },
});

export { expect } from '@playwright/test';
```

**Test usage**

```typescript
// tests/auth.spec.ts
import { test, expect } from './fixtures';

test('successful login redirects to dashboard', async ({ loginPage, page }) => {
  await loginPage.goto();
  await loginPage.login('admin', 'password123');

  await expect(page).toHaveURL('/dashboard');
});
```

**Advanced: fixture that performs setup**

```typescript
// tests/fixtures.ts
import { test as base } from '@playwright/test';
import { DashboardPage } from './pages/dashboard.page';

export const test = base.extend<{ authenticatedDashboard: DashboardPage }>({
  authenticatedDashboard: async ({ page }, use) => {
    // Setup: navigate and authenticate
    await page.goto('/login');
    await page.getByLabel('Username').fill('admin');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');

    await use(new DashboardPage(page));

    // Teardown (optional): logout, clean up test data
    await page.goto('/logout');
  },
});

export { expect } from '@playwright/test';
```

### 5. Factory Functions

**Use when**: A page has few actions and no shared state. Simpler than a class, still encapsulates actions.
**Avoid when**: The page has 5+ methods or needs component composition.

Factory functions are a lightweight alternative for simple pages. They return an object with action methods, avoiding class ceremony.

**TypeScript**

```typescript
// tests/pages/error.page.ts
import { type Page } from '@playwright/test';

export function createErrorPage(page: Page) {
  return {
    errorHeading: page.getByRole('heading', { name: 'Something went wrong' }),
    retryButton: page.getByRole('button', { name: 'Retry' }),

    async goto() {
      await page.goto('/error');
    },

    async retry() {
      await page.getByRole('button', { name: 'Retry' }).click();
    },

    async goHome() {
      await page.getByRole('link', { name: 'Go home' }).click();
      await page.waitForURL('/');
    },
  };
}
```

**JavaScript**

```javascript
// tests/pages/error.page.js
// @ts-check

/** @param {import('@playwright/test').Page} page */
export function createErrorPage(page) {
  return {
    errorHeading: page.getByRole('heading', { name: 'Something went wrong' }),
    retryButton: page.getByRole('button', { name: 'Retry' }),

    async goto() {
      await page.goto('/error');
    },

    async retry() {
      await page.getByRole('button', { name: 'Retry' }).click();
    },

    async goHome() {
      await page.getByRole('link', { name: 'Go home' }).click();
      await page.waitForURL('/');
    },
  };
}
```

**Test usage**

```typescript
// tests/error.spec.ts
import { test, expect } from '@playwright/test';
import { createErrorPage } from './pages/error.page';

test('retry button reloads the page', async ({ page }) => {
  const errorPage = createErrorPage(page);
  await errorPage.goto();
  await errorPage.retry();

  await expect(page).not.toHaveURL('/error');
});
```

### 6. Getter Pattern for Dynamic Locators

**Use when**: Locators depend on dynamic content (parameterized rows, nth items, content that changes after page load).
**Avoid when**: All locators are static and known at construction time -- use constructor assignment instead.

Getters create the locator fresh on each access. This avoids stale references when the DOM changes after the page object is constructed.

**TypeScript**

```typescript
// tests/pages/users.page.ts
import { type Page, type Locator } from '@playwright/test';

export class UsersPage {
  constructor(private readonly page: Page) {}

  /** Static locators -- fine in constructor or as getters, either works. */
  get addUserButton(): Locator {
    return this.page.getByRole('button', { name: 'Add user' });
  }

  get userRows(): Locator {
    return this.page.getByRole('row').filter({ hasNot: this.page.getByRole('columnheader') });
  }

  /** Dynamic locator -- must be a method since it takes a parameter. */
  userRow(name: string): Locator {
    return this.page.getByRole('row', { name });
  }

  userDeleteButton(name: string): Locator {
    return this.userRow(name).getByRole('button', { name: 'Delete' });
  }

  async goto() {
    await this.page.goto('/admin/users');
  }

  async deleteUser(name: string) {
    await this.userDeleteButton(name).click();
    // Wait for row to disappear, confirming deletion
    await this.userRow(name).waitFor({ state: 'hidden' });
  }

  async addUser() {
    await this.addUserButton.click();
  }
}
```

**JavaScript**

```javascript
// tests/pages/users.page.js
// @ts-check

export class UsersPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page;
  }

  get addUserButton() {
    return this.page.getByRole('button', { name: 'Add user' });
  }

  get userRows() {
    return this.page.getByRole('row').filter({ hasNot: this.page.getByRole('columnheader') });
  }

  userRow(name) {
    return this.page.getByRole('row', { name });
  }

  userDeleteButton(name) {
    return this.userRow(name).getByRole('button', { name: 'Delete' });
  }

  async goto() {
    await this.page.goto('/admin/users');
  }

  async deleteUser(name) {
    await this.userDeleteButton(name).click();
    await this.userRow(name).waitFor({ state: 'hidden' });
  }

  async addUser() {
    await this.addUserButton.click();
  }
}
```

### 7. Directory Structure

Use this layout. Adapt folder names to your convention, but keep the separation between pages, components, and fixtures.

```
tests/
  fixtures.ts              # Custom test with POM fixtures
  auth.spec.ts             # Test files at top level or in feature folders
  dashboard.spec.ts
  pages/                   # One file per page
    login.page.ts
    dashboard.page.ts
    settings.page.ts
    users.page.ts
  components/              # Reusable UI components
    navbar.component.ts
    modal.component.ts
    sidebar.component.ts
    data-table.component.ts
```

Rules:
- **One class per file.** File name matches the class: `LoginPage` lives in `login.page.ts`.
- **Pages vs components**: Pages own a full route (`/login`, `/dashboard`). Components are embedded in pages (`NavbarComponent`, `ModalComponent`).
- **No barrel files** (`index.ts` re-exporting everything). Import directly from the file. Barrel files create circular dependency traps and slow down IDE tooling.
- **`fixtures.ts` at `tests/` root.** Every spec imports `test` and `expect` from `./fixtures` instead of `@playwright/test`.

### 8. Handling Async Initialization

**Use when**: A page object needs async setup before it is usable (waiting for API data to load, waiting for animations to settle, waiting for a specific element to appear).
**Avoid when**: The page is ready immediately after `goto()`.

Never put `await` in a constructor. Use a static factory method instead.

**TypeScript**

```typescript
// tests/pages/analytics.page.ts
import { type Page, type Locator } from '@playwright/test';

export class AnalyticsPage {
  readonly chart: Locator;
  readonly dateRange: Locator;

  private constructor(private readonly page: Page) {
    this.chart = page.locator('[data-testid="analytics-chart"]');
    this.dateRange = page.getByLabel('Date range');
  }

  /** Use this instead of `new AnalyticsPage()`. Waits for chart data to load. */
  static async create(page: Page): Promise<AnalyticsPage> {
    const analyticsPage = new AnalyticsPage(page);
    await page.goto('/analytics');
    // Wait for the async content that makes this page "ready"
    await analyticsPage.chart.waitFor({ state: 'visible' });
    return analyticsPage;
  }

  async selectDateRange(range: string) {
    await this.dateRange.click();
    await this.page.getByRole('option', { name: range }).click();
    // Wait for chart to update after date change
    await this.chart.waitFor({ state: 'visible' });
  }
}
```

**JavaScript**

```javascript
// tests/pages/analytics.page.js
// @ts-check

export class AnalyticsPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page;
    this.chart = page.locator('[data-testid="analytics-chart"]');
    this.dateRange = page.getByLabel('Date range');
  }

  /** @param {import('@playwright/test').Page} page */
  static async create(page) {
    const analyticsPage = new AnalyticsPage(page);
    await page.goto('/analytics');
    await analyticsPage.chart.waitFor({ state: 'visible' });
    return analyticsPage;
  }

  async selectDateRange(range) {
    await this.dateRange.click();
    await this.page.getByRole('option', { name: range }).click();
    await this.chart.waitFor({ state: 'visible' });
  }
}
```

**As a fixture**

```typescript
// tests/fixtures.ts
import { test as base } from '@playwright/test';
import { AnalyticsPage } from './pages/analytics.page';

export const test = base.extend<{ analyticsPage: AnalyticsPage }>({
  analyticsPage: async ({ page }, use) => {
    const analyticsPage = await AnalyticsPage.create(page);
    await use(analyticsPage);
  },
});

export { expect } from '@playwright/test';
```

## Decision Guide

```
How complex is the page?
│
├── 1-2 interactions, single test file
│   └── No POM. Inline locators in the test are fine.
│
├── 3-5 interactions OR 2+ test files use it
│   ├── Few methods, no composition needed
│   │   └── Factory function (Pattern 5)
│   └── Multiple methods, needs component composition
│       └── Full POM class (Pattern 1 + 2)
│
├── Used across 3+ test files
│   └── POM class + fixture injection (Pattern 4)
│
└── Page requires async setup before usable
    └── Static factory method (Pattern 8) + fixture
```

| Factor | Simple helper | Factory function | POM class | POM + fixture |
|---|---|---|---|---|
| Page complexity | 1-2 actions | 3-5 actions | 5+ actions | 5+ actions |
| Reuse across files | 1 file | 1-2 files | 2+ files | 3+ files |
| Component composition | No | No | Yes | Yes |
| Team size | Solo | Small | Any | Any |
| Setup ceremony | None | Low | Medium | Medium (once) |
| Recommended for | Quick prototypes | Simple pages | Standard choice | Mature suites |

## Anti-Patterns

### God Object

One page object for the entire application or a page object with 30+ methods covering unrelated features.

```typescript
// BAD: one class for everything
class AppPage {
  async login() { /* ... */ }
  async addToCart() { /* ... */ }
  async checkout() { /* ... */ }
  async changePassword() { /* ... */ }
  async viewAnalytics() { /* ... */ }
  // 40 more methods...
}
```

Fix: Split by page or feature. One class per logical page. Compose shared UI into component objects.

### Assertions Inside Page Objects

```typescript
// BAD: page object owns the assertion
class LoginPage {
  async loginAndVerify(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
    // This assertion belongs in the test, not here
    await expect(this.page).toHaveURL('/dashboard');
  }
}

// GOOD: page object performs action, test asserts
class LoginPage {
  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

// In test:
await loginPage.login('admin', 'pass');
await expect(page).toHaveURL('/dashboard');
```

Exception: `waitForURL()` or `waitFor()` calls inside POM methods that ensure navigation completed are fine -- those are synchronization, not assertion.

### Deeply Nested Inheritance

```typescript
// BAD: inheritance chain
class BasePage { /* ... */ }
class AuthenticatedPage extends BasePage { /* ... */ }
class AdminPage extends AuthenticatedPage { /* ... */ }
class SuperAdminPage extends AdminPage { /* ... */ }
```

Fix: Use composition. Create component objects for shared UI (navbar, sidebar) and compose them into page objects. Prefer `has-a` over `is-a`.

```typescript
// GOOD: composition
class AdminPage {
  readonly navbar: NavbarComponent;
  readonly sidebar: AdminSidebarComponent;

  constructor(private readonly page: Page) {
    this.navbar = new NavbarComponent(page.getByRole('navigation'));
    this.sidebar = new AdminSidebarComponent(page.getByRole('complementary'));
  }
}
```

### Storing State in Page Objects

```typescript
// BAD: tracking state
class CartPage {
  private itemCount = 0;

  async addItem(name: string) {
    await this.page.getByRole('button', { name: `Add ${name}` }).click();
    this.itemCount++; // State goes stale if the UI changes independently
  }

  getCount() {
    return this.itemCount; // Lies if another tab or API call modified the cart
  }
}
```

Fix: Read state from the DOM when needed. The page is the source of truth, not your JavaScript variable.

```typescript
// GOOD: read from DOM
class CartPage {
  async addItem(name: string) {
    await this.page.getByRole('button', { name: `Add ${name}` }).click();
  }

  get itemCount(): Locator {
    return this.page.getByTestId('cart-count');
  }
}

// In test:
await cartPage.addItem('Widget');
await expect(cartPage.itemCount).toHaveText('1');
```

### Exposing Raw Locators as the Primary API

```typescript
// BAD: test manipulates locators directly
const loginPage = new LoginPage(page);
await loginPage.usernameInput.fill('admin');
await loginPage.passwordInput.fill('secret');
await loginPage.submitButton.click();

// GOOD: test calls an action
const loginPage = new LoginPage(page);
await loginPage.login('admin', 'secret');
```

Exposing locators as `readonly` properties for assertions is acceptable (`expect(loginPage.errorMessage).toBeVisible()`). The anti-pattern is requiring tests to orchestrate multi-step interactions through raw locators.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Locator times out but element exists | POM constructed before navigation; locator attached to wrong page state | Move `goto()` before POM construction, or use getter pattern (Pattern 6) |
| Circular import between page objects | `LoginPage` imports `DashboardPage` which imports `LoginPage` | Break the cycle: use lazy `import()` in the navigation method, or have the test create the destination POM |
| Fixture not available in test | Test imports `test` from `@playwright/test` instead of `./fixtures` | Always import `test` and `expect` from your custom fixtures file |
| TypeScript error: property does not exist on fixture | Fixture type not declared in `test.extend<>()` generic | Add the POM type to the generic parameter: `test.extend<{ loginPage: LoginPage }>()` |
| POM methods feel duplicated across similar pages | Multiple pages share the same form structure | Extract a component object for the shared form, compose into each page |
| `page.goto()` in constructor causes "cannot use await" | Constructors cannot be async | Use static factory method (Pattern 8) |

## Related

- [core/fixtures-and-hooks.md](../core/fixtures-and-hooks.md) -- how `test.extend()` works in depth, fixture scoping, teardown
- [core/locators.md](../core/locators.md) -- choosing the right locator strategy for POM properties
- [core/pom-vs-fixtures-vs-helpers.md](../core/pom-vs-fixtures-vs-helpers.md) -- expanded decision framework for when to use each approach
- [core/test-organization.md](../core/test-organization.md) -- file and folder conventions for the broader test suite
