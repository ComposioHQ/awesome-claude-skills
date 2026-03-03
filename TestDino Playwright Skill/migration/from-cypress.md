# Migrating from Cypress to Playwright

> **When to use**: When converting a Cypress test suite to Playwright. Follow this guide command-by-command, pattern-by-pattern.

## Key Mindset Shifts

Before converting any code, internalize these five differences. They affect every line you write.

### 1. Chains vs async/await

Cypress commands are enqueued and run in a serial chain that _looks_ synchronous but is not. Playwright uses standard `async`/`await` -- real asynchronous JavaScript with no magic scheduling.

```javascript
// Cypress — chain-based, implicitly queued
cy.get('.todo-list li').should('have.length', 3);
cy.get('.todo-list li').first().should('have.text', 'Buy milk');

// Playwright — async/await, explicit control flow
const items = page.getByTestId('todo-item');
await expect(items).toHaveCount(3);
await expect(items.first()).toHaveText('Buy milk');
```

**Why it matters**: You can use `if`/`else`, `for` loops, `try`/`catch`, and any JavaScript construct naturally. No `cy.then()` workarounds.

### 2. Automatic retry vs auto-wait

Cypress retries the _entire command chain_ until assertions pass (or time out). Playwright locators are lazy -- they do nothing until you perform an _action_ or _assertion_, at which point Playwright auto-waits for the element to be actionable (visible, enabled, stable).

```javascript
// Cypress — retries cy.get + .should together
cy.get('[data-testid="submit"]').should('be.visible').click();

// Playwright — locator is created instantly; .click() auto-waits for visibility + stability
await page.getByTestId('submit').click();
```

### 3. In-browser vs Node.js

Cypress test code runs _inside_ the browser (same origin). Playwright runs in Node.js and controls browsers over the Chrome DevTools Protocol or equivalent. This means:

- Playwright can open multiple tabs, windows, and even multiple browsers in a single test.
- Playwright has native access to the file system, databases, and APIs from test code -- no `cy.task()` needed.
- You cannot access `window` or `document` directly; use `page.evaluate()` when you need browser-side code.

### 4. One tab vs multi-tab, multi-browser

Cypress is limited to a single browser tab and a single browser. Playwright can control multiple pages, multiple browser contexts (each with isolated cookies/storage), and even multiple browser types (Chromium, Firefox, WebKit) in the same test run.

### 5. Custom commands vs fixtures

Cypress extends via `Cypress.Commands.add()` -- a global mutable registry. Playwright uses `test.extend()` fixtures with dependency injection, guaranteed teardown, and type safety. Fixtures are dramatically more powerful.

## Command Mapping Table

| Cypress | Playwright | Notes |
|---|---|---|
| `cy.visit('/path')` | `await page.goto('/path')` | Use `baseURL` in config to avoid full URLs |
| `cy.get('selector')` | `page.locator('selector')` | Prefer `page.getByRole()` over CSS selectors |
| `cy.get('[data-testid="x"]')` | `page.getByTestId('x')` | Configure `testIdAttribute` in playwright.config |
| `cy.contains('text')` | `page.getByText('text')` | For buttons/links, prefer `page.getByRole('button', { name: 'text' })` |
| `cy.find('child')` | `locator.locator('child')` | Chain locators to scope within a parent |
| `cy.get('sel').click()` | `await locator.click()` | Auto-waits for element to be actionable |
| `cy.get('sel').type('text')` | `await locator.fill('text')` | `fill()` sets value instantly. Use `locator.pressSequentially('text')` for character-by-character typing |
| `cy.get('sel').clear()` | `await locator.clear()` | Or `await locator.fill('')` |
| `cy.get('select').select('val')` | `await locator.selectOption('val')` | Accepts value, label, or `{ index }` |
| `cy.get('input').check()` | `await locator.check()` | No-op if already checked |
| `cy.get('input').uncheck()` | `await locator.uncheck()` | No-op if already unchecked |
| `cy.get('sel').should('be.visible')` | `await expect(locator).toBeVisible()` | Web-first assertion; auto-retries |
| `cy.get('sel').should('have.text', 'x')` | `await expect(locator).toHaveText('x')` | Also accepts regex: `.toHaveText(/pattern/)` |
| `cy.get('sel').should('contain', 'x')` | `await expect(locator).toContainText('x')` | Substring match |
| `cy.get('sel').should('have.length', 3)` | `await expect(locator).toHaveCount(3)` | Counts matching elements |
| `cy.get('sel').should('have.value', 'x')` | `await expect(locator).toHaveValue('x')` | Input/textarea value |
| `cy.get('sel').should('have.attr', 'href', '/x')` | `await expect(locator).toHaveAttribute('href', '/x')` | Any HTML attribute |
| `cy.get('sel').should('have.class', 'active')` | `await expect(locator).toHaveClass(/active/)` | Regex for partial class match |
| `cy.get('sel').should('be.disabled')` | `await expect(locator).toBeDisabled()` | |
| `cy.get('sel').should('not.exist')` | `await expect(locator).toBeHidden()` | Or `.toHaveCount(0)` for truly absent elements |
| `cy.intercept('GET', '/api/**', { body })` | `await page.route('/api/**', route => route.fulfill({ body }))` | Set up _before_ the action that triggers the request |
| `cy.intercept('POST', '/api/save').as('save')` | `const resp = page.waitForResponse('**/api/save')` | Start _before_ the action, `await` after |
| `cy.wait('@save')` | `await resp` | Returns `Response` object with `.json()`, `.status()` |
| `cy.fixture('users.json')` | Fixtures via `test.extend()` or direct `import`/`require` | See Example 5 below |
| `cy.request('GET', '/api/users')` | `const resp = await request.get('/api/users')` | Use the `request` fixture or `APIRequestContext` |
| `cy.request('POST', '/api/users', body)` | `const resp = await request.post('/api/users', { data: body })` | |
| `cy.wrap(value)` | No equivalent needed | Just use the value directly with `await` |
| `cy.then((result) => { ... })` | `const result = await ...` | Standard async/await replaces `.then()` chains |
| `Cypress.env('API_KEY')` | `process.env.API_KEY` | Or use `use: {}` in playwright.config for test-specific values |
| `Cypress.Commands.add('login', fn)` | Custom fixture via `test.extend()` | See Example 5 below |
| `cy.clock()` / `cy.tick(1000)` | `await page.clock.install()` / `await page.clock.fastForward(1000)` | `page.clock` API for full time control |
| `cy.screenshot('name')` | `await page.screenshot({ path: 'name.png' })` | Auto-captured on failure when `screenshot: 'on'` in config |
| `cy.viewport(1280, 720)` | `await page.setViewportSize({ width: 1280, height: 720 })` | Prefer setting in config or per-project |
| `beforeEach(() => { cy.visit('/') })` | `test.beforeEach(async ({ page }) => { await page.goto('/') })` | Destructure `page` from fixtures |
| `cy.scrollTo('bottom')` | `await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))` | Actions auto-scroll to elements; manual scroll is rarely needed |
| `cy.focused()` | `page.locator(':focus')` | Or assert: `await expect(locator).toBeFocused()` |
| `cy.go('back')` | `await page.goBack()` | Also `page.goForward()` |
| `cy.reload()` | `await page.reload()` | |
| `cy.title()` | `await expect(page).toHaveTitle('text')` | Web-first assertion on page title |
| `cy.url()` | `await expect(page).toHaveURL('/path')` | Accepts string or regex |
| `cy.getCookie('name')` | `const cookies = await context.cookies()` | Filter by name from the array |
| `cy.setCookie('name', 'val')` | `await context.addCookies([{ name, value, url }])` | |
| `cy.clearCookies()` | `await context.clearCookies()` | |

## Before/After Examples

### Example 1: Basic Navigation and Assertion

**Cypress**
```javascript
describe('Homepage', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('displays the welcome heading', () => {
    cy.get('h1').should('have.text', 'Welcome to Acme');
    cy.get('[data-testid="hero-subtitle"]').should('be.visible');
    cy.url().should('include', '/');
  });

  it('navigates to the about page', () => {
    cy.contains('About').click();
    cy.url().should('include', '/about');
    cy.get('h1').should('have.text', 'About Us');
  });
});
```

**Playwright (TypeScript)**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('displays the welcome heading', async ({ page }) => {
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Welcome to Acme');
    await expect(page.getByTestId('hero-subtitle')).toBeVisible();
    await expect(page).toHaveURL('/');
  });

  test('navigates to the about page', async ({ page }) => {
    await page.getByRole('link', { name: 'About' }).click();
    await expect(page).toHaveURL(/\/about/);
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('About Us');
  });
});
```

**Playwright (JavaScript)**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Homepage', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('displays the welcome heading', async ({ page }) => {
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Welcome to Acme');
    await expect(page.getByTestId('hero-subtitle')).toBeVisible();
    await expect(page).toHaveURL('/');
  });

  test('navigates to the about page', async ({ page }) => {
    await page.getByRole('link', { name: 'About' }).click();
    await expect(page).toHaveURL(/\/about/);
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('About Us');
  });
});
```

**Key changes**: `cy.get('h1')` becomes `page.getByRole('heading', { level: 1 })` for resilience. `cy.contains('About').click()` becomes `page.getByRole('link', { name: 'About' }).click()` to assert the element is actually a link. `cy.url().should('include', ...)` becomes `await expect(page).toHaveURL(...)` which auto-retries.

---

### Example 2: Form Interaction

**Cypress**
```javascript
describe('Registration Form', () => {
  it('submits a valid form', () => {
    cy.visit('/register');

    cy.get('#first-name').type('Jane');
    cy.get('#last-name').type('Doe');
    cy.get('#email').type('jane@example.com');
    cy.get('#password').type('s3cure!Pass');
    cy.get('#country').select('United States');
    cy.get('#terms').check();

    cy.get('form').submit();

    cy.get('.success-message').should('be.visible');
    cy.get('.success-message').should('contain', 'Welcome, Jane');
  });

  it('shows validation errors for empty fields', () => {
    cy.visit('/register');
    cy.get('[type="submit"]').click();

    cy.get('.error').should('have.length', 4);
    cy.get('#first-name').should('have.attr', 'aria-invalid', 'true');
  });
});
```

**Playwright (TypeScript)**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Registration Form', () => {
  test('submits a valid form', async ({ page }) => {
    await page.goto('/register');

    await page.getByLabel('First name').fill('Jane');
    await page.getByLabel('Last name').fill('Doe');
    await page.getByLabel('Email').fill('jane@example.com');
    await page.getByLabel('Password').fill('s3cure!Pass');
    await page.getByLabel('Country').selectOption('United States');
    await page.getByLabel('I agree to the terms').check();

    await page.getByRole('button', { name: 'Register' }).click();

    const successMessage = page.getByText('Welcome, Jane');
    await expect(successMessage).toBeVisible();
  });

  test('shows validation errors for empty fields', async ({ page }) => {
    await page.goto('/register');
    await page.getByRole('button', { name: 'Register' }).click();

    await expect(page.getByRole('alert')).toHaveCount(4);
    await expect(page.getByLabel('First name')).toHaveAttribute('aria-invalid', 'true');
  });
});
```

**Playwright (JavaScript)**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Registration Form', () => {
  test('submits a valid form', async ({ page }) => {
    await page.goto('/register');

    await page.getByLabel('First name').fill('Jane');
    await page.getByLabel('Last name').fill('Doe');
    await page.getByLabel('Email').fill('jane@example.com');
    await page.getByLabel('Password').fill('s3cure!Pass');
    await page.getByLabel('Country').selectOption('United States');
    await page.getByLabel('I agree to the terms').check();

    await page.getByRole('button', { name: 'Register' }).click();

    const successMessage = page.getByText('Welcome, Jane');
    await expect(successMessage).toBeVisible();
  });

  test('shows validation errors for empty fields', async ({ page }) => {
    await page.goto('/register');
    await page.getByRole('button', { name: 'Register' }).click();

    await expect(page.getByRole('alert')).toHaveCount(4);
    await expect(page.getByLabel('First name')).toHaveAttribute('aria-invalid', 'true');
  });
});
```

**Key changes**: `cy.get('#id').type()` becomes `page.getByLabel('Label').fill()`. No IDs needed -- labels are resilient and accessible. `fill()` replaces `type()` and sets the value instantly. `cy.get('form').submit()` becomes an explicit button click, matching real user behavior.

---

### Example 3: Network Mocking

**Cypress**
```javascript
describe('Product List', () => {
  it('displays products from the API', () => {
    cy.intercept('GET', '/api/products', {
      statusCode: 200,
      body: [
        { id: 1, name: 'Widget', price: 9.99 },
        { id: 2, name: 'Gadget', price: 24.99 },
      ],
    }).as('getProducts');

    cy.visit('/products');
    cy.wait('@getProducts');

    cy.get('[data-testid="product-card"]').should('have.length', 2);
    cy.get('[data-testid="product-card"]').first().should('contain', 'Widget');
  });

  it('shows error state when API fails', () => {
    cy.intercept('GET', '/api/products', {
      statusCode: 500,
      body: { error: 'Internal server error' },
    }).as('getProducts');

    cy.visit('/products');
    cy.wait('@getProducts');

    cy.get('[data-testid="error-message"]').should('contain', 'Something went wrong');
  });

  it('submits a new product', () => {
    cy.intercept('POST', '/api/products', {
      statusCode: 201,
      body: { id: 3, name: 'Doohickey', price: 14.99 },
    }).as('createProduct');

    cy.visit('/products/new');
    cy.get('#product-name').type('Doohickey');
    cy.get('#product-price').type('14.99');
    cy.get('button[type="submit"]').click();

    cy.wait('@createProduct').its('request.body').should('deep.equal', {
      name: 'Doohickey',
      price: 14.99,
    });
  });
});
```

**Playwright (TypeScript)**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Product List', () => {
  test('displays products from the API', async ({ page }) => {
    await page.route('**/api/products', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, name: 'Widget', price: 9.99 },
          { id: 2, name: 'Gadget', price: 24.99 },
        ]),
      })
    );

    await page.goto('/products');

    await expect(page.getByTestId('product-card')).toHaveCount(2);
    await expect(page.getByTestId('product-card').first()).toContainText('Widget');
  });

  test('shows error state when API fails', async ({ page }) => {
    await page.route('**/api/products', (route) =>
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' }),
      })
    );

    await page.goto('/products');

    await expect(page.getByTestId('error-message')).toContainText('Something went wrong');
  });

  test('submits a new product', async ({ page }) => {
    // Set up route mock AND capture the request
    let requestBody: unknown;
    await page.route('**/api/products', (route) => {
      requestBody = route.request().postDataJSON();
      return route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ id: 3, name: 'Doohickey', price: 14.99 }),
      });
    });

    await page.goto('/products/new');
    await page.getByLabel('Product name').fill('Doohickey');
    await page.getByLabel('Price').fill('14.99');
    await page.getByRole('button', { name: 'Create product' }).click();

    // Assert on the captured request body
    expect(requestBody).toEqual({ name: 'Doohickey', price: 14.99 });
  });
});
```

**Playwright (JavaScript)**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Product List', () => {
  test('displays products from the API', async ({ page }) => {
    await page.route('**/api/products', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, name: 'Widget', price: 9.99 },
          { id: 2, name: 'Gadget', price: 24.99 },
        ]),
      })
    );

    await page.goto('/products');

    await expect(page.getByTestId('product-card')).toHaveCount(2);
    await expect(page.getByTestId('product-card').first()).toContainText('Widget');
  });

  test('shows error state when API fails', async ({ page }) => {
    await page.route('**/api/products', (route) =>
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' }),
      })
    );

    await page.goto('/products');

    await expect(page.getByTestId('error-message')).toContainText('Something went wrong');
  });

  test('submits a new product', async ({ page }) => {
    let requestBody;
    await page.route('**/api/products', (route) => {
      requestBody = route.request().postDataJSON();
      return route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ id: 3, name: 'Doohickey', price: 14.99 }),
      });
    });

    await page.goto('/products/new');
    await page.getByLabel('Product name').fill('Doohickey');
    await page.getByLabel('Price').fill('14.99');
    await page.getByRole('button', { name: 'Create product' }).click();

    expect(requestBody).toEqual({ name: 'Doohickey', price: 14.99 });
  });
});
```

**Key changes**: `cy.intercept()` becomes `page.route()`. Set up routes _before_ the action that triggers the request. No `cy.wait('@alias')` needed -- Playwright auto-waits for the UI to update. To assert on request bodies, capture them in the route handler. For waiting on a specific response, use `page.waitForResponse()`.

---

### Example 4: Authentication

**Cypress**
```javascript
// cypress/support/commands.js
Cypress.Commands.add('login', (email, password) => {
  cy.session([email, password], () => {
    cy.visit('/login');
    cy.get('#email').type(email);
    cy.get('#password').type(password);
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
  });
});

// cypress/e2e/dashboard.cy.js
describe('Dashboard', () => {
  beforeEach(() => {
    cy.login('admin@example.com', 'password123');
    cy.visit('/dashboard');
  });

  it('shows admin content', () => {
    cy.get('[data-testid="admin-panel"]').should('be.visible');
  });
});
```

**Playwright (TypeScript)** -- using `storageState` for session reuse (recommended)
```typescript
// auth.setup.ts — runs once, saves auth state to a file
import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../.auth/user.json');

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('admin@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  // Save signed-in state to file
  await page.context().storageState({ path: authFile });
});
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    // Setup project — runs auth first
    { name: 'setup', testMatch: /.*\.setup\.ts/ },

    // All tests reuse the saved auth state
    {
      name: 'chromium',
      dependencies: ['setup'],
      use: {
        storageState: '.auth/user.json',
      },
    },
  ],
});
```

```typescript
// dashboard.spec.ts — already authenticated, no login code needed
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('shows admin content', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByTestId('admin-panel')).toBeVisible();
  });
});
```

**Playwright (JavaScript)** -- using `storageState` for session reuse (recommended)
```javascript
// auth.setup.js
const { test: setup, expect } = require('@playwright/test');
const path = require('path');

const authFile = path.join(__dirname, '../.auth/user.json');

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('admin@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  await page.context().storageState({ path: authFile });
});
```

```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.js/ },
    {
      name: 'chromium',
      dependencies: ['setup'],
      use: {
        storageState: '.auth/user.json',
      },
    },
  ],
});
```

```javascript
// dashboard.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Dashboard', () => {
  test('shows admin content', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByTestId('admin-panel')).toBeVisible();
  });
});
```

**Key changes**: Cypress `cy.session()` becomes Playwright's `storageState`. Auth runs once as a setup project, saves cookies/localStorage to a JSON file, and all test projects reuse it. Tests never touch login flows -- they start authenticated. Add `.auth/` to `.gitignore`.

---

### Example 5: Custom Commands to Fixtures

**Cypress** -- custom commands are globally registered
```javascript
// cypress/support/commands.js
Cypress.Commands.add('createTodo', (text) => {
  cy.get('[data-testid="new-todo"]').type(`${text}{enter}`);
});

Cypress.Commands.add('getTodos', () => {
  return cy.get('[data-testid="todo-item"]');
});

Cypress.Commands.add('apiCreateUser', (userData) => {
  return cy.request('POST', '/api/users', userData);
});

// cypress/e2e/todos.cy.js
describe('Todos', () => {
  beforeEach(() => {
    cy.visit('/todos');
  });

  it('adds and verifies todos', () => {
    cy.createTodo('Buy milk');
    cy.createTodo('Walk dog');
    cy.getTodos().should('have.length', 2);
  });
});
```

**Playwright (TypeScript)** -- fixtures replace custom commands
```typescript
// fixtures.ts
import { test as base, expect } from '@playwright/test';

// Define the types for your custom fixtures
type TodoFixtures = {
  todosPage: TodosPage;
  apiHelper: ApiHelper;
};

class TodosPage {
  constructor(private page: import('@playwright/test').Page) {}

  async createTodo(text: string) {
    await this.page.getByTestId('new-todo').fill(text);
    await this.page.getByTestId('new-todo').press('Enter');
  }

  get todos() {
    return this.page.getByTestId('todo-item');
  }
}

class ApiHelper {
  constructor(private request: import('@playwright/test').APIRequestContext) {}

  async createUser(userData: { name: string; email: string }) {
    const response = await this.request.post('/api/users', { data: userData });
    return response.json();
  }
}

export const test = base.extend<TodoFixtures>({
  todosPage: async ({ page }, use) => {
    await page.goto('/todos');
    await use(new TodosPage(page));
  },

  apiHelper: async ({ request }, use) => {
    await use(new ApiHelper(request));
  },
});

export { expect };
```

```typescript
// todos.spec.ts
import { test, expect } from './fixtures';

test('adds and verifies todos', async ({ todosPage }) => {
  await todosPage.createTodo('Buy milk');
  await todosPage.createTodo('Walk dog');
  await expect(todosPage.todos).toHaveCount(2);
});

test('creates a user via API then verifies in UI', async ({ todosPage, apiHelper, page }) => {
  const user = await apiHelper.createUser({ name: 'Jane', email: 'jane@test.com' });
  await page.goto(`/users/${user.id}`);
  await expect(page.getByRole('heading')).toHaveText('Jane');
});
```

**Playwright (JavaScript)** -- fixtures replace custom commands
```javascript
// fixtures.js
const { test: base, expect } = require('@playwright/test');

class TodosPage {
  constructor(page) {
    this.page = page;
  }

  async createTodo(text) {
    await this.page.getByTestId('new-todo').fill(text);
    await this.page.getByTestId('new-todo').press('Enter');
  }

  get todos() {
    return this.page.getByTestId('todo-item');
  }
}

class ApiHelper {
  constructor(request) {
    this.request = request;
  }

  async createUser(userData) {
    const response = await this.request.post('/api/users', { data: userData });
    return response.json();
  }
}

const test = base.extend({
  todosPage: async ({ page }, use) => {
    await page.goto('/todos');
    await use(new TodosPage(page));
  },

  apiHelper: async ({ request }, use) => {
    await use(new ApiHelper(request));
  },
});

module.exports = { test, expect };
```

```javascript
// todos.spec.js
const { test, expect } = require('./fixtures');

test('adds and verifies todos', async ({ todosPage }) => {
  await todosPage.createTodo('Buy milk');
  await todosPage.createTodo('Walk dog');
  await expect(todosPage.todos).toHaveCount(2);
});
```

**Key changes**: Every Cypress custom command maps to either a method on a page object (for UI interactions) or a helper class (for API calls), exposed via `test.extend()` fixtures. Fixtures provide dependency injection, type safety, and guaranteed teardown. Tests declare what they need by name in the function signature.

## Migration Steps

A battle-tested process for migrating an existing Cypress test suite to Playwright.

### Step 1: Install Playwright alongside Cypress

Do not remove Cypress yet. Run both frameworks in parallel during migration.

```bash
npm init playwright@latest
# Accept defaults: TypeScript (or JavaScript), tests folder, GitHub Actions CI, install browsers
```

This creates `playwright.config.ts`, a `tests/` folder, and installs browsers.

### Step 2: Configure playwright.config to match your Cypress setup

Map your `cypress.config.js` settings to `playwright.config.ts`:

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',       // Your new Playwright test directory
  timeout: 30_000,          // Cypress default is 4s per command; Playwright uses 30s per test
  expect: { timeout: 5_000 }, // Assertion auto-retry timeout (like Cypress defaultCommandTimeout)
  fullyParallel: true,      // Cypress runs serially by default; Playwright parallelizes
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? 'html' : 'list',

  use: {
    baseURL: 'http://localhost:3000', // Matches Cypress baseUrl
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    // Add more browsers — something Cypress cannot do:
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],

  // Equivalent to Cypress's devServer config
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? 'html' : 'list',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### Step 3: Convert custom commands to fixtures

Before migrating individual tests, convert your `cypress/support/commands.js` into Playwright fixtures. This gives every migrated test immediate access to the same helpers.

1. Identify each custom command in `cypress/support/commands.js` and `cypress/support/e2e.js`.
2. Group UI commands into page object classes.
3. Group API commands into API helper classes.
4. Expose them via `test.extend()` in a shared `fixtures.ts` (or `fixtures.js`).
5. See Example 5 above for the complete pattern.

### Step 4: Set up authentication

Convert `cy.session()` or login-in-`beforeEach` patterns to Playwright's `storageState`:

1. Create an `auth.setup.ts` file (see Example 4 above).
2. Add a `setup` project to `playwright.config.ts`.
3. Add `.auth/` to `.gitignore`.
4. Remove all login code from individual test files.

### Step 5: Migrate tests file by file

Start with the simplest spec files. For each file:

1. Create the corresponding Playwright test file in `tests/`.
2. Convert using the Command Mapping Table above.
3. Replace CSS selectors with semantic locators (`getByRole`, `getByLabel`, `getByText`).
4. Run the Playwright test in headed mode: `npx playwright test tests/my-test.spec.ts --headed`.
5. Once passing, mark the Cypress spec as migrated (move to an `archived/` folder or delete).

Prioritize by value: migrate your critical path tests first (auth, checkout, core CRUD).

### Step 6: Convert cy.intercept patterns to page.route

For each intercepted route:

1. Move `page.route()` calls _before_ the action that triggers the request (Playwright routes must be set up in advance).
2. Replace `cy.wait('@alias')` with either `page.waitForResponse()` (when you need the response) or just let auto-waiting assertions handle it (when you only care about UI updates).
3. For request body assertions, capture the body inside the `page.route()` handler.

### Step 7: Convert Cypress plugins to Node.js code

Cypress plugins (in `cypress/plugins/` or `setupNodeEvents` in config) run in a separate Node.js process and communicate with test code via `cy.task()`. In Playwright, your test code already runs in Node.js, so:

- Database seeding: call directly from fixtures or `globalSetup`.
- File operations: use `fs` directly in test code or fixtures.
- Environment setup: use `globalSetup` / `globalTeardown` in config.
- Custom task logic: move into fixture setup/teardown.

### Step 8: Update CI pipeline

Replace the Cypress CI step with Playwright:

```yaml
# GitHub Actions example
- name: Install Playwright Browsers
  run: npx playwright install --with-deps

- name: Run Playwright tests
  run: npx playwright test

- name: Upload Playwright Report
  uses: actions/upload-artifact@v4
  if: ${{ !cancelled() }}
  with:
    name: playwright-report
    path: playwright-report/
    retention-days: 30
```

### Step 9: Remove Cypress

Once all tests are migrated and passing in CI:

```bash
npm uninstall cypress
rm -rf cypress/
rm cypress.config.js   # or .ts
# Remove any Cypress-related CI config
# Remove Cypress-related entries from .eslintrc if present
```

## Common Gotchas

Things that look similar between Cypress and Playwright but behave differently.

### 1. Locators are lazy, not retrying

Cypress `cy.get()` immediately starts querying the DOM and retries until the chain passes. Playwright `page.locator()` creates a locator object instantly -- it does _nothing_ until you call an action (`.click()`, `.fill()`) or assertion (`expect(locator).toBeVisible()`).

```typescript
// This does NOT query the DOM — it just creates a locator reference
const button = page.getByRole('button', { name: 'Submit' });

// This is where the actual DOM query + waiting happens
await button.click();
```

This means storing locators in variables is free and encouraged. Reuse them across multiple actions and assertions.

### 2. Assertions are separate from locators

Cypress chains assertions onto commands: `cy.get('x').should('be.visible').and('have.text', 'y')`. Playwright uses separate `expect()` calls for each assertion:

```typescript
// Cypress — chained assertions
cy.get('.card').should('be.visible').and('have.text', 'Hello').and('have.class', 'active');

// Playwright — separate expect() calls, each auto-retries independently
const card = page.locator('.card');
await expect(card).toBeVisible();
await expect(card).toHaveText('Hello');
await expect(card).toHaveClass(/active/);
```

### 3. fill() vs type() — the speed difference

`cy.type('text')` sends keystrokes one at a time, triggering `keydown`, `keypress`, `input`, and `keyup` events for each character. Playwright's `locator.fill('text')` clears the field and sets the value in one shot, only triggering `input` and `change` events.

Use `fill()` by default. Use `pressSequentially()` only when character-by-character input matters (autocomplete, search-as-you-type, input masks):

```typescript
// Default — fast, sets value directly
await page.getByLabel('Name').fill('Jane Doe');

// Character-by-character — only when keystroke events matter
await page.getByLabel('Search').pressSequentially('play', { delay: 100 });
```

### 4. Auto-scroll behavior

Cypress auto-scrolls to bring elements into view before _any_ interaction. Playwright auto-scrolls into view only when performing _actions_ (click, fill, check). Assertions like `toBeVisible()` do **not** scroll -- they check if the element is visible in its current position.

If you need to scroll before asserting visibility:

```typescript
// Scroll into view first, then assert
await page.getByText('Footer content').scrollIntoViewIfNeeded();
await expect(page.getByText('Footer content')).toBeVisible();
```

### 5. No implicit cy.wrap() equivalent

Cypress `cy.wrap()` brings a non-Cypress value into the command chain. Playwright does not need this because you are already in async/await land:

```typescript
// Cypress
const value = 42;
cy.wrap(value).should('equal', 42);

// Playwright — just use the value
const value = 42;
expect(value).toBe(42);
```

### 6. Route setup timing

Cypress `cy.intercept()` can be called at any point and will match the _next_ matching request. Playwright `page.route()` must be set up _before_ the action that triggers the request. A common mistake is setting up the route _after_ `page.goto()` -- by then the request may have already fired.

```typescript
// WRONG — route set up too late
await page.goto('/products');
await page.route('**/api/products', (route) => route.fulfill({ body: '[]' }));

// CORRECT — route set up before navigation
await page.route('**/api/products', (route) => route.fulfill({ body: '[]' }));
await page.goto('/products');
```

### 7. Cypress subject vs Playwright return values

Cypress commands yield a "subject" to the next command in the chain. Playwright actions return `void` (or a `Promise<void>`). If you need a value _from_ the browser, use `evaluate`, `textContent`, `inputValue`, etc.:

```typescript
// Cypress — subject chaining
cy.get('#counter').invoke('text').then((text) => {
  const count = parseInt(text, 10);
  expect(count).to.be.greaterThan(0);
});

// Playwright — direct return values
const text = await page.locator('#counter').textContent();
const count = parseInt(text!, 10);
expect(count).toBeGreaterThan(0);

// Better: use a web-first assertion when possible
await expect(page.locator('#counter')).not.toHaveText('0');
```

### 8. Cypress plugins vs Playwright global setup

Cypress uses `setupNodeEvents` (or the legacy `plugins/index.js`) for Node.js-side operations, accessed via `cy.task()`. Since Playwright tests already run in Node.js, you do not need a separate plugin layer:

```typescript
// Cypress — plugin pattern
// cypress.config.js
setupNodeEvents(on) {
  on('task', {
    seedDatabase(data) { return db.seed(data); },
  });
}
// Test: cy.task('seedDatabase', testData);

// Playwright — direct call in fixture
export const test = base.extend({
  seededDatabase: async ({}, use) => {
    await db.seed(testData);
    await use();
    await db.cleanup();
  },
});
```

### 9. cy.within() vs locator scoping

Cypress `cy.within()` scopes all subsequent commands to a container element. Playwright scopes by chaining locators:

```typescript
// Cypress
cy.get('[data-testid="signup-form"]').within(() => {
  cy.get('input[name="email"]').type('user@test.com');
  cy.get('button').click();
});

// Playwright — chain locators for scoping
const form = page.getByTestId('signup-form');
await form.getByLabel('Email').fill('user@test.com');
await form.getByRole('button', { name: 'Sign up' }).click();
```

### 10. Test isolation differences

Cypress clears cookies, localStorage, and sessionStorage between tests by default but shares the same browser instance. Playwright creates a _fresh browser context_ for each test -- complete isolation of cookies, storage, cache, and service workers. This means:

- You never need to manually clear state between tests.
- You cannot "leak" state from one test to another (which can mask or cause flakiness in Cypress).
- Worker-scoped fixtures are the way to share expensive resources across tests.

## What's Better in Playwright

Features that have no Cypress equivalent and make Playwright the stronger choice for production test suites.

### Multi-browser testing out of the box

Test on Chromium, Firefox, and WebKit (Safari) in a single config. No plugins, no paid dashboard.

```typescript
// playwright.config.ts — three browsers, zero extra setup
projects: [
  { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
  { name: 'mobile-safari', use: { ...devices['iPhone 13'] } },
],
```

### Multi-tab and multi-window testing

Test popups, OAuth flows, new tabs, and multi-window interactions:

```typescript
// Handle a popup window (e.g., OAuth)
const popupPromise = page.waitForEvent('popup');
await page.getByRole('button', { name: 'Sign in with Google' }).click();
const popup = await popupPromise;
await popup.getByLabel('Email').fill('user@gmail.com');
```

### Multi-user testing in a single test

Test collaboration features with multiple independent browser contexts:

```typescript
test('two users can collaborate', async ({ browser }) => {
  const aliceContext = await browser.newContext({ storageState: 'auth/alice.json' });
  const bobContext = await browser.newContext({ storageState: 'auth/bob.json' });
  const alicePage = await aliceContext.newPage();
  const bobPage = await bobContext.newPage();

  await alicePage.goto('/doc/shared');
  await bobPage.goto('/doc/shared');

  await alicePage.getByRole('textbox').fill('Hello from Alice');
  await expect(bobPage.getByText('Hello from Alice')).toBeVisible();

  await aliceContext.close();
  await bobContext.close();
});
```

### Native API testing

Test APIs without a browser, using the same runner and assertion library:

```typescript
test('API returns user list', async ({ request }) => {
  const response = await request.get('/api/users');
  expect(response.ok()).toBeTruthy();

  const users = await response.json();
  expect(users).toHaveLength(3);
  expect(users[0]).toHaveProperty('email');
});
```

### Parallel execution with sharding

Run tests across multiple machines with zero configuration:

```bash
# Split across 4 CI machines
npx playwright test --shard=1/4  # Machine 1
npx playwright test --shard=2/4  # Machine 2
npx playwright test --shard=3/4  # Machine 3
npx playwright test --shard=4/4  # Machine 4
```

### Trace viewer

Playwright traces capture a complete record of test execution: DOM snapshots, network requests, console logs, and action screenshots. Open with:

```bash
npx playwright show-trace trace.zip
```

This replaces Cypress's time-travel debugger with a more detailed, offline-capable tool.

### Component testing with framework support

Test React, Vue, Svelte, and Solid components in real browsers (not jsdom):

```typescript
import { test, expect } from '@playwright/experimental-ct-react';
import { Button } from './Button';

test('button renders with label', async ({ mount }) => {
  const component = await mount(<Button label="Click me" />);
  await expect(component).toContainText('Click me');
  await component.click();
});
```

### Built-in code generation

Generate test code by interacting with your app:

```bash
npx playwright codegen http://localhost:3000
```

Records your clicks, fills, and assertions, and outputs Playwright test code. Use it as a starting point, then refine locators to use `getByRole`.

### Clock control

Full control over `Date`, `setTimeout`, `setInterval`, and `requestAnimationFrame`:

```typescript
test('shows expired badge after timeout', async ({ page }) => {
  await page.clock.install({ time: new Date('2024-01-01T00:00:00Z') });
  await page.goto('/offers');

  await page.clock.fastForward('24:00:00');

  await expect(page.getByText('Offer expired')).toBeVisible();
});
```

### Network request interception with HAR files

Record and replay network traffic from HAR files for deterministic tests:

```typescript
// Record all network traffic
await page.routeFromHAR('tests/fixtures/products.har', {
  url: '**/api/**',
  update: true, // Set to true once to record, then false to replay
});
```

## Related

- [core/locators.md](../core/locators.md) -- locator strategy for Playwright (replaces Cypress `cy.get()` patterns)
- [core/fixtures-and-hooks.md](../core/fixtures-and-hooks.md) -- deep dive on fixtures (replaces Cypress custom commands)
- [core/assertions-and-waiting.md](../core/assertions-and-waiting.md) -- web-first assertions (replaces Cypress `should` chains)
- [core/configuration.md](../core/configuration.md) -- playwright.config setup
- [core/authentication.md](../core/authentication.md) -- auth patterns (replaces Cypress `cy.session()`)
- [core/network-mocking.md](../core/network-mocking.md) -- route mocking (replaces Cypress `cy.intercept()`)
- [ci/ci-github-actions.md](../ci/ci-github-actions.md) -- CI setup for Playwright
