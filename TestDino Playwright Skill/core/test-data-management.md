# Test Data Management

> **When to use**: Every test that interacts with data — user accounts, form inputs, entities, or any state that must exist before assertions run.

## Quick Reference

| Strategy | Speed | Isolation | Complexity | Best For |
|---|---|---|---|---|
| Inline data | Instant | Perfect | None | Simple value checks, form inputs |
| Factory functions | Instant | Perfect | Low | Unique identifiers, consistent shapes |
| Faker/random data | Instant | Perfect | Low | Realistic fields, edge-case discovery |
| Builder pattern | Instant | Perfect | Medium | Complex objects with many optional fields |
| API seeding | Fast | Perfect | Medium | Creating entities the app depends on |
| Database seeding | Fast | Good | High | Complex relational data, bulk setup |
| Storage state | Fast | Good | Low | Reusing authenticated sessions |
| Fixture-based setup | Fast | Perfect | Medium | Encapsulating setup + guaranteed teardown |

**Core principle**: Every test creates its own data and cleans up after itself. No test should depend on data left behind by another test or pre-existing in the environment.

## Patterns

### Inline Test Data

**Use when**: The data is simple, unique to one test, and essential for understanding the assertion.

**Avoid when**: The same data shape repeats across many tests — extract a factory instead.

Inline data makes tests self-documenting. The reader sees exactly what matters without chasing imports.

**TypeScript**
```typescript
// tests/contact-form.spec.ts
import { test, expect } from '@playwright/test';

test('submits contact form with valid data', async ({ page }) => {
  const name = 'Ada Lovelace';
  const email = `ada-${Date.now()}@example.com`;
  const message = 'Inquiry about analytics engine';

  await page.goto('/contact');
  await page.getByLabel('Name').fill(name);
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Message').fill(message);
  await page.getByRole('button', { name: 'Send' }).click();

  await expect(page.getByText('Thank you, Ada Lovelace')).toBeVisible();
});
```

**JavaScript**
```javascript
// tests/contact-form.spec.js
const { test, expect } = require('@playwright/test');

test('submits contact form with valid data', async ({ page }) => {
  const name = 'Ada Lovelace';
  const email = `ada-${Date.now()}@example.com`;
  const message = 'Inquiry about analytics engine';

  await page.goto('/contact');
  await page.getByLabel('Name').fill(name);
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Message').fill(message);
  await page.getByRole('button', { name: 'Send' }).click();

  await expect(page.getByText('Thank you, Ada Lovelace')).toBeVisible();
});
```

Use `Date.now()` or `crypto.randomUUID()` for fields that must be unique (emails, usernames). This prevents collisions during parallel execution.

---

### Factory Functions

**Use when**: Multiple tests need the same data shape with different values, or you need guaranteed uniqueness.

**Avoid when**: The data is trivial and only used once — inline it instead.

Factories centralize data creation logic. When the data shape changes, you update one function, not dozens of tests.

**TypeScript**
```typescript
// tests/factories/user.factory.ts
export interface UserData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
}

let counter = 0;

export function createUserData(overrides: Partial<UserData> = {}): UserData {
  counter++;
  const id = `${Date.now()}-${counter}`;
  return {
    firstName: `Test`,
    lastName: `User${id}`,
    email: `testuser-${id}@example.com`,
    password: 'SecureP@ss123!',
    ...overrides,
  };
}
```

```typescript
// tests/registration.spec.ts
import { test, expect } from '@playwright/test';
import { createUserData } from './factories/user.factory';

test('registers a new user', async ({ page }) => {
  const user = createUserData();

  await page.goto('/register');
  await page.getByLabel('First name').fill(user.firstName);
  await page.getByLabel('Last name').fill(user.lastName);
  await page.getByLabel('Email').fill(user.email);
  await page.getByLabel('Password').fill(user.password);
  await page.getByRole('button', { name: 'Create account' }).click();

  await expect(page.getByText(`Welcome, ${user.firstName}`)).toBeVisible();
});

test('rejects duplicate email', async ({ page }) => {
  const user = createUserData({ email: 'duplicate@example.com' });

  await page.goto('/register');
  await page.getByLabel('Email').fill(user.email);
  await page.getByLabel('Password').fill(user.password);
  await page.getByRole('button', { name: 'Create account' }).click();

  await expect(page.getByText('Email already registered')).toBeVisible();
});
```

**JavaScript**
```javascript
// tests/factories/user.factory.js
let counter = 0;

function createUserData(overrides = {}) {
  counter++;
  const id = `${Date.now()}-${counter}`;
  return {
    firstName: 'Test',
    lastName: `User${id}`,
    email: `testuser-${id}@example.com`,
    password: 'SecureP@ss123!',
    ...overrides,
  };
}

module.exports = { createUserData };
```

```javascript
// tests/registration.spec.js
const { test, expect } = require('@playwright/test');
const { createUserData } = require('./factories/user.factory');

test('registers a new user', async ({ page }) => {
  const user = createUserData();

  await page.goto('/register');
  await page.getByLabel('First name').fill(user.firstName);
  await page.getByLabel('Last name').fill(user.lastName);
  await page.getByLabel('Email').fill(user.email);
  await page.getByLabel('Password').fill(user.password);
  await page.getByRole('button', { name: 'Create account' }).click();

  await expect(page.getByText(`Welcome, ${user.firstName}`)).toBeVisible();
});
```

---

### Faker / Random Data

**Use when**: You need realistic-looking data (names, addresses, phone numbers) or want to discover edge cases through randomness.

**Avoid when**: Debugging a failure — use a fixed seed to make it reproducible.

Always seed faker so failures are reproducible. Use `testInfo.testId` or a fixed seed per test file.

**TypeScript**
```typescript
// tests/factories/faker-user.factory.ts
import { faker } from '@faker-js/faker';

export function createFakerUser(seed?: number) {
  if (seed !== undefined) {
    faker.seed(seed);
  }
  return {
    firstName: faker.person.firstName(),
    lastName: faker.person.lastName(),
    email: faker.internet.email({ provider: 'testmail.example.com' }),
    phone: faker.phone.number(),
    address: {
      street: faker.location.streetAddress(),
      city: faker.location.city(),
      state: faker.location.state({ abbreviated: true }),
      zip: faker.location.zipCode(),
    },
  };
}
```

```typescript
// tests/checkout.spec.ts
import { test, expect } from '@playwright/test';
import { createFakerUser } from './factories/faker-user.factory';

test('completes checkout with shipping address', async ({ page }, testInfo) => {
  // Seed with a stable value so re-runs produce the same data
  const user = createFakerUser(testInfo.workerIndex);

  await page.goto('/checkout');
  await page.getByLabel('Street address').fill(user.address.street);
  await page.getByLabel('City').fill(user.address.city);
  await page.getByLabel('State').fill(user.address.state);
  await page.getByLabel('ZIP code').fill(user.address.zip);
  await page.getByRole('button', { name: 'Place order' }).click();

  await expect(page.getByText('Order confirmed')).toBeVisible();
});
```

**JavaScript**
```javascript
// tests/factories/faker-user.factory.js
const { faker } = require('@faker-js/faker');

function createFakerUser(seed) {
  if (seed !== undefined) {
    faker.seed(seed);
  }
  return {
    firstName: faker.person.firstName(),
    lastName: faker.person.lastName(),
    email: faker.internet.email({ provider: 'testmail.example.com' }),
    phone: faker.phone.number(),
    address: {
      street: faker.location.streetAddress(),
      city: faker.location.city(),
      state: faker.location.state({ abbreviated: true }),
      zip: faker.location.zipCode(),
    },
  };
}

module.exports = { createFakerUser };
```

```javascript
// tests/checkout.spec.js
const { test, expect } = require('@playwright/test');
const { createFakerUser } = require('./factories/faker-user.factory');

test('completes checkout with shipping address', async ({ page }, testInfo) => {
  const user = createFakerUser(testInfo.workerIndex);

  await page.goto('/checkout');
  await page.getByLabel('Street address').fill(user.address.street);
  await page.getByLabel('City').fill(user.address.city);
  await page.getByLabel('State').fill(user.address.state);
  await page.getByLabel('ZIP code').fill(user.address.zip);
  await page.getByRole('button', { name: 'Place order' }).click();

  await expect(page.getByText('Order confirmed')).toBeVisible();
});
```

Always use a test-specific email domain (e.g., `testmail.example.com`) so faker-generated emails never hit real inboxes. The `example.com` domain is reserved by RFC 2606 and is safe for testing.

---

### Builder Pattern

**Use when**: Objects have many optional fields, conditional logic, or multiple valid configurations. Common for product listings, user profiles, or form payloads with nested data.

**Avoid when**: The object has fewer than 5 fields — a factory with overrides is simpler.

**TypeScript**
```typescript
// tests/builders/product.builder.ts
export interface Product {
  name: string;
  price: number;
  currency: string;
  category: string;
  description: string;
  inStock: boolean;
  tags: string[];
  variants: { size: string; color: string }[];
}

export class ProductBuilder {
  private product: Product = {
    name: `Product-${Date.now()}`,
    price: 29.99,
    currency: 'USD',
    category: 'Electronics',
    description: 'A test product',
    inStock: true,
    tags: [],
    variants: [],
  };

  withName(name: string): this {
    this.product.name = name;
    return this;
  }

  withPrice(price: number, currency = 'USD'): this {
    this.product.price = price;
    this.product.currency = currency;
    return this;
  }

  withCategory(category: string): this {
    this.product.category = category;
    return this;
  }

  outOfStock(): this {
    this.product.inStock = false;
    return this;
  }

  withTags(...tags: string[]): this {
    this.product.tags = tags;
    return this;
  }

  withVariant(size: string, color: string): this {
    this.product.variants.push({ size, color });
    return this;
  }

  build(): Product {
    return { ...this.product };
  }
}
```

```typescript
// tests/product-catalog.spec.ts
import { test, expect } from '@playwright/test';
import { ProductBuilder } from './builders/product.builder';

test('displays out-of-stock badge for unavailable products', async ({ page, request }) => {
  const product = new ProductBuilder()
    .withName('Wireless Keyboard')
    .withCategory('Accessories')
    .outOfStock()
    .build();

  // Seed via API (see API Seeding pattern below)
  await request.post('/api/products', { data: product });

  await page.goto('/products');
  const card = page.getByRole('listitem').filter({ hasText: product.name });
  await expect(card.getByText('Out of Stock')).toBeVisible();
});
```

**JavaScript**
```javascript
// tests/builders/product.builder.js
class ProductBuilder {
  constructor() {
    this.product = {
      name: `Product-${Date.now()}`,
      price: 29.99,
      currency: 'USD',
      category: 'Electronics',
      description: 'A test product',
      inStock: true,
      tags: [],
      variants: [],
    };
  }

  withName(name) {
    this.product.name = name;
    return this;
  }

  withPrice(price, currency = 'USD') {
    this.product.price = price;
    this.product.currency = currency;
    return this;
  }

  withCategory(category) {
    this.product.category = category;
    return this;
  }

  outOfStock() {
    this.product.inStock = false;
    return this;
  }

  withTags(...tags) {
    this.product.tags = tags;
    return this;
  }

  withVariant(size, color) {
    this.product.variants.push({ size, color });
    return this;
  }

  build() {
    return { ...this.product };
  }
}

module.exports = { ProductBuilder };
```

```javascript
// tests/product-catalog.spec.js
const { test, expect } = require('@playwright/test');
const { ProductBuilder } = require('./builders/product.builder');

test('displays out-of-stock badge for unavailable products', async ({ page, request }) => {
  const product = new ProductBuilder()
    .withName('Wireless Keyboard')
    .withCategory('Accessories')
    .outOfStock()
    .build();

  await request.post('/api/products', { data: product });

  await page.goto('/products');
  const card = page.getByRole('listitem').filter({ hasText: product.name });
  await expect(card.getByText('Out of Stock')).toBeVisible();
});
```

---

### API Seeding

**Use when**: Tests need entities to already exist (users, products, orders) and the app exposes APIs to create them. This is the default strategy for test data setup.

**Avoid when**: No API exists for the entity, or the API itself is what you are testing (use the UI or database instead).

API seeding is faster than UI-based setup, more maintainable than database seeding, and exercises real application logic. Prefer it over all other approaches when an API is available.

**TypeScript**
```typescript
// tests/fixtures/api-data.fixture.ts
import { test as base, APIRequestContext } from '@playwright/test';
import { createUserData, UserData } from '../factories/user.factory';

type ApiDataFixtures = {
  apiUser: UserData & { id: string };
};

export const test = base.extend<ApiDataFixtures>({
  apiUser: async ({ request }, use) => {
    const userData = createUserData();

    // Create
    const response = await request.post('/api/users', { data: userData });
    const created = await response.json();
    const user = { ...userData, id: created.id };

    // Provide to test
    await use(user);

    // Cleanup — runs even if test fails
    await request.delete(`/api/users/${user.id}`);
  },
});

export { expect } from '@playwright/test';
```

```typescript
// tests/user-profile.spec.ts
import { test, expect } from './fixtures/api-data.fixture';

test('edits user profile name', async ({ page, apiUser }) => {
  await page.goto(`/users/${apiUser.id}/profile`);
  await page.getByLabel('First name').fill('Updated');
  await page.getByRole('button', { name: 'Save' }).click();

  await expect(page.getByText('Profile updated')).toBeVisible();
});
```

**JavaScript**
```javascript
// tests/fixtures/api-data.fixture.js
const { test: base } = require('@playwright/test');
const { createUserData } = require('../factories/user.factory');

const test = base.extend({
  apiUser: async ({ request }, use) => {
    const userData = createUserData();

    const response = await request.post('/api/users', { data: userData });
    const created = await response.json();
    const user = { ...userData, id: created.id };

    await use(user);

    await request.delete(`/api/users/${user.id}`);
  },
});

module.exports = { test, expect: require('@playwright/test').expect };
```

```javascript
// tests/user-profile.spec.js
const { test, expect } = require('./fixtures/api-data.fixture');

test('edits user profile name', async ({ page, apiUser }) => {
  await page.goto(`/users/${apiUser.id}/profile`);
  await page.getByLabel('First name').fill('Updated');
  await page.getByRole('button', { name: 'Save' }).click();

  await expect(page.getByText('Profile updated')).toBeVisible();
});
```

For multi-entity seeding, compose fixtures:

**TypeScript**
```typescript
// tests/fixtures/order-data.fixture.ts
import { test as base } from './api-data.fixture';

export const test = base.extend({
  apiOrder: async ({ request, apiUser }, use) => {
    const orderResponse = await request.post('/api/orders', {
      data: { userId: apiUser.id, items: [{ sku: 'WIDGET-001', qty: 2 }] },
    });
    const order = await orderResponse.json();

    await use(order);

    await request.delete(`/api/orders/${order.id}`);
  },
});
```

---

### Database Seeding

**Use when**: No API exists for the data you need, you need bulk data, or you need to set up complex relational state that is cumbersome via API calls.

**Avoid when**: An API exists — API seeding is more maintainable and exercises real application logic. Database seeding couples tests to schema details.

**TypeScript**
```typescript
// tests/fixtures/db.fixture.ts
import { test as base } from '@playwright/test';
import { Pool } from 'pg';

type DbFixtures = {
  db: Pool;
  seededOrg: { id: string; name: string };
};

export const test = base.extend<DbFixtures>({
  db: async ({}, use) => {
    const pool = new Pool({
      connectionString: process.env.TEST_DATABASE_URL,
    });
    await use(pool);
    await pool.end();
  },

  seededOrg: async ({ db }, use) => {
    const orgName = `TestOrg-${Date.now()}`;
    const result = await db.query(
      'INSERT INTO organizations (name, plan) VALUES ($1, $2) RETURNING id',
      [orgName, 'enterprise']
    );
    const orgId = result.rows[0].id;

    await use({ id: orgId, name: orgName });

    // Cascade delete cleans up related data
    await db.query('DELETE FROM organizations WHERE id = $1', [orgId]);
  },
});

export { expect } from '@playwright/test';
```

**JavaScript**
```javascript
// tests/fixtures/db.fixture.js
const { test: base } = require('@playwright/test');
const { Pool } = require('pg');

const test = base.extend({
  db: async ({}, use) => {
    const pool = new Pool({
      connectionString: process.env.TEST_DATABASE_URL,
    });
    await use(pool);
    await pool.end();
  },

  seededOrg: async ({ db }, use) => {
    const orgName = `TestOrg-${Date.now()}`;
    const result = await db.query(
      'INSERT INTO organizations (name, plan) VALUES ($1, $2) RETURNING id',
      [orgName, 'enterprise']
    );
    const orgId = result.rows[0].id;

    await use({ id: orgId, name: orgName });

    await db.query('DELETE FROM organizations WHERE id = $1', [orgId]);
  },
});

module.exports = { test, expect: require('@playwright/test').expect };
```

Always use parameterized queries (`$1`, `$2`) to prevent SQL injection — even in tests. It is a good habit and prevents breakage from special characters in generated data.

---

### Storage State

**Use when**: Multiple tests need an authenticated session and you want to avoid logging in via the UI in every test.

**Avoid when**: The test is specifically testing the login flow itself.

Generate storage state once in a setup project, then reuse it across all tests that need authentication.

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'auth-setup',
      testMatch: /auth\.setup\.ts/,
    },
    {
      name: 'authenticated-tests',
      dependencies: ['auth-setup'],
      use: {
        storageState: '.auth/user.json',
      },
    },
  ],
});
```

```typescript
// tests/auth.setup.ts
import { test as setup, expect } from '@playwright/test';
import path from 'node:path';

const authFile = path.join(__dirname, '..', '.auth', 'user.json');

setup('authenticate as standard user', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  await page.context().storageState({ path: authFile });
});
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  projects: [
    {
      name: 'auth-setup',
      testMatch: /auth\.setup\.js/,
    },
    {
      name: 'authenticated-tests',
      dependencies: ['auth-setup'],
      use: {
        storageState: '.auth/user.json',
      },
    },
  ],
});
```

```javascript
// tests/auth.setup.js
const { test: setup, expect } = require('@playwright/test');
const path = require('node:path');

const authFile = path.join(__dirname, '..', '.auth', 'user.json');

setup('authenticate as standard user', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  await page.context().storageState({ path: authFile });
});
```

For multiple roles, create separate setup files and storage state files:

```typescript
// tests/admin-auth.setup.ts
import { test as setup } from '@playwright/test';
import path from 'node:path';

const adminAuthFile = path.join(__dirname, '..', '.auth', 'admin.json');

setup('authenticate as admin', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.ADMIN_EMAIL!);
  await page.getByLabel('Password').fill(process.env.ADMIN_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.context().storageState({ path: adminAuthFile });
});
```

Add `.auth/` to `.gitignore` — storage state files contain session tokens.

---

### Test Data Cleanup

**Use when**: Always. Every test that creates data must clean it up.

**Avoid when**: Never. Skipping cleanup causes cascading failures in subsequent runs.

**Strategy 1: Fixture teardown (preferred)**

Put cleanup in the fixture's teardown block. Runs even if the test throws.

```typescript
// Already shown in API Seeding — the cleanup runs after `use()`
apiUser: async ({ request }, use) => {
  const user = await createViaApi(request);
  await use(user);
  // This ALWAYS runs — even on test failure
  await request.delete(`/api/users/${user.id}`);
},
```

**Strategy 2: Batch cleanup by timestamp prefix**

Tag all test-created data with a recognizable prefix, then sweep it in global teardown.

**TypeScript**
```typescript
// global-teardown.ts
import { request } from '@playwright/test';

export default async function globalTeardown() {
  const context = await request.newContext({
    baseURL: process.env.BASE_URL,
  });

  // Delete all test entities created in this run
  // Assumes entities created with the "test-" prefix
  const response = await context.delete('/api/test-data/cleanup', {
    data: { prefix: 'test-', olderThanMinutes: 60 },
  });

  if (!response.ok()) {
    console.warn(`Cleanup returned ${response.status()}`);
  }

  await context.dispose();
}
```

**JavaScript**
```javascript
// global-teardown.js
const { request } = require('@playwright/test');

module.exports = async function globalTeardown() {
  const context = await request.newContext({
    baseURL: process.env.BASE_URL,
  });

  const response = await context.delete('/api/test-data/cleanup', {
    data: { prefix: 'test-', olderThanMinutes: 60 },
  });

  if (!response.ok()) {
    console.warn(`Cleanup returned ${response.status()}`);
  }

  await context.dispose();
};
```

**Strategy 3: Isolated tenant per worker**

Each Playwright worker gets its own tenant/organization. All data is scoped to that tenant. Teardown deletes the entire tenant.

```typescript
// tests/fixtures/tenant.fixture.ts
import { test as base } from '@playwright/test';

export const test = base.extend<{}, { workerTenant: { id: string; apiKey: string } }>({
  workerTenant: [async ({ request }, use) => {
    const res = await request.post('/api/tenants', {
      data: { name: `test-worker-${Date.now()}` },
    });
    const tenant = await res.json();

    await use(tenant);

    await request.delete(`/api/tenants/${tenant.id}`);
  }, { scope: 'worker' }],
});
```

---

### Environment-Specific Data

**Use when**: Tests run against multiple environments (dev, staging, production-mirror) with different base URLs, credentials, or data constraints.

**Avoid when**: You only have one test environment.

Never hardcode environment-specific values in test files. Use `.env` files and `playwright.config` to inject them.

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';
import dotenv from 'dotenv';
import path from 'node:path';

// Load environment-specific .env file
const envFile = process.env.TEST_ENV || 'local';
dotenv.config({ path: path.resolve(__dirname, `.env.${envFile}`) });

export default defineConfig({
  use: {
    baseURL: process.env.BASE_URL,
  },
});
```

```
# .env.local
BASE_URL=http://localhost:3000
TEST_USER_EMAIL=testuser@localhost.test
TEST_USER_PASSWORD=localpassword123

# .env.staging
BASE_URL=https://staging.example.com
TEST_USER_EMAIL=e2e-bot@staging.example.com
TEST_USER_PASSWORD=staging-secret-from-vault
```

```typescript
// tests/fixtures/env-data.fixture.ts
import { test as base } from '@playwright/test';

type EnvConfig = {
  testCredentials: { email: string; password: string };
};

export const test = base.extend<EnvConfig>({
  testCredentials: async ({}, use) => {
    const email = process.env.TEST_USER_EMAIL;
    const password = process.env.TEST_USER_PASSWORD;
    if (!email || !password) {
      throw new Error('TEST_USER_EMAIL and TEST_USER_PASSWORD must be set');
    }
    await use({ email, password });
  },
});

export { expect } from '@playwright/test';
```

**JavaScript**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');
const dotenv = require('dotenv');
const path = require('node:path');

const envFile = process.env.TEST_ENV || 'local';
dotenv.config({ path: path.resolve(__dirname, `.env.${envFile}`) });

module.exports = defineConfig({
  use: {
    baseURL: process.env.BASE_URL,
  },
});
```

Run against a specific environment:

```bash
TEST_ENV=staging npx playwright test
```

---

### Fixtures for Test Data

**Use when**: Test data setup and teardown should be encapsulated, reusable, and guaranteed to clean up. This is the recommended pattern for all non-trivial test data.

**Avoid when**: The data is a simple inline value that does not require cleanup.

Fixtures are the backbone of reliable test data management in Playwright. They compose, they guarantee teardown, and they make tests declarative.

**TypeScript**
```typescript
// tests/fixtures/index.ts
import { test as base, expect } from '@playwright/test';
import { createUserData, UserData } from '../factories/user.factory';

type TestFixtures = {
  seedUser: UserData & { id: string };
  seedProduct: { id: string; name: string; price: number };
};

export const test = base.extend<TestFixtures>({
  seedUser: async ({ request }, use) => {
    const data = createUserData();
    const res = await request.post('/api/users', { data });
    expect(res.ok()).toBeTruthy();
    const user = { ...data, id: (await res.json()).id };

    await use(user);

    await request.delete(`/api/users/${user.id}`);
  },

  seedProduct: async ({ request }, use) => {
    const data = {
      name: `Product-${Date.now()}`,
      price: 49.99,
      category: 'Testing',
    };
    const res = await request.post('/api/products', { data });
    expect(res.ok()).toBeTruthy();
    const product = { ...data, id: (await res.json()).id };

    await use(product);

    await request.delete(`/api/products/${product.id}`);
  },
});

export { expect };
```

```typescript
// tests/shopping-cart.spec.ts
import { test, expect } from './fixtures';

test('adds product to cart', async ({ page, seedUser, seedProduct }) => {
  // seedUser and seedProduct are already created and will be cleaned up automatically
  await page.goto(`/products/${seedProduct.id}`);
  await page.getByRole('button', { name: 'Add to cart' }).click();

  await page.goto('/cart');
  await expect(page.getByText(seedProduct.name)).toBeVisible();
  await expect(page.getByText('$49.99')).toBeVisible();
});
```

**JavaScript**
```javascript
// tests/fixtures/index.js
const { test: base, expect } = require('@playwright/test');
const { createUserData } = require('../factories/user.factory');

const test = base.extend({
  seedUser: async ({ request }, use) => {
    const data = createUserData();
    const res = await request.post('/api/users', { data });
    expect(res.ok()).toBeTruthy();
    const user = { ...data, id: (await res.json()).id };

    await use(user);

    await request.delete(`/api/users/${user.id}`);
  },

  seedProduct: async ({ request }, use) => {
    const data = {
      name: `Product-${Date.now()}`,
      price: 49.99,
      category: 'Testing',
    };
    const res = await request.post('/api/products', { data });
    expect(res.ok()).toBeTruthy();
    const product = { ...data, id: (await res.json()).id };

    await use(product);

    await request.delete(`/api/products/${product.id}`);
  },
});

module.exports = { test, expect };
```

```javascript
// tests/shopping-cart.spec.js
const { test, expect } = require('./fixtures');

test('adds product to cart', async ({ page, seedUser, seedProduct }) => {
  await page.goto(`/products/${seedProduct.id}`);
  await page.getByRole('button', { name: 'Add to cart' }).click();

  await page.goto('/cart');
  await expect(page.getByText(seedProduct.name)).toBeVisible();
  await expect(page.getByText('$49.99')).toBeVisible();
});
```

Fixtures only run when a test requests them by name. If a test does not use `seedProduct`, the product is never created — no wasted setup, no unnecessary cleanup.

## Decision Guide

```
What data does your test need?
│
├── Simple values (strings, numbers for form fields)?
│   └── Use INLINE DATA — keep it in the test
│
├── Same shape used across many tests?
│   ├── < 5 fields? → Use a FACTORY FUNCTION
│   └── >= 5 fields with optional/conditional fields? → Use a BUILDER
│
├── Need realistic-looking data (names, addresses)?
│   └── Use FAKER with a fixed seed
│
├── Entities that must exist before the test starts?
│   ├── App has an API for this entity?
│   │   └── Use API SEEDING in a fixture (preferred)
│   ├── No API, but have database access?
│   │   └── Use DATABASE SEEDING in a fixture
│   └── No API, no DB access?
│       └── Use UI setup in a beforeEach (slowest — avoid if possible)
│
├── Need an authenticated session?
│   └── Use STORAGE STATE via setup project
│
└── Need data isolated per worker?
    └── Use WORKER-SCOPED FIXTURES with tenant isolation
```

### Speed ranking (fastest to slowest)

1. Inline data / factories / faker — no I/O, instant
2. API seeding — one HTTP call per entity
3. Database seeding — direct DB call, skips app logic
4. Storage state — one-time login, reused across tests
5. UI-based setup — full browser interaction per test (avoid)

### Isolation ranking (most to least isolated)

1. Test-scoped fixtures with API teardown — each test gets fresh data, cleaned up after
2. Worker-scoped tenant isolation — tests in a worker share a tenant, cleaned up when worker exits
3. Timestamp-prefixed batch cleanup — catches orphaned data, runs in global teardown
4. Shared database state — fragile, prone to ordering bugs (avoid)

## Anti-Patterns

### Shared mutable data across tests

```typescript
// BAD — tests share the same user object and depend on execution order
let sharedUser: UserData;

test.beforeAll(async ({ request }) => {
  sharedUser = await createUser(request);
});

test('updates user name', async ({ page }) => {
  // Mutates sharedUser — other tests see the changed state
});

test('checks original name', async ({ page }) => {
  // Fails because the previous test changed the name
});
```

Fix: Use test-scoped fixtures. Each test gets its own instance.

### Hardcoded IDs

```typescript
// BAD — this ID only exists in your local database
test('edits product', async ({ page }) => {
  await page.goto('/products/507f1f77bcf86cd799439011/edit');
});
```

Fix: Create the product in a fixture and use the returned ID.

### No cleanup

```typescript
// BAD — creates data but never deletes it
test.beforeEach(async ({ request }) => {
  await request.post('/api/products', { data: { name: 'Leaked Product' } });
});
// Over time, the database fills with test debris causing slowdowns and false positives
```

Fix: Always pair creation with deletion in a fixture teardown.

### Relying on pre-existing database state

```typescript
// BAD — assumes "Premium Plan" already exists in the database
test('subscribes to premium', async ({ page }) => {
  await page.goto('/pricing');
  await page.getByRole('button', { name: 'Premium Plan' }).click();
  // Breaks on a fresh database or different environment
});
```

Fix: Seed the plan via API or database fixture before the test.

### Using production data in tests

```typescript
// BAD — tests against real customer data
test('views customer orders', async ({ page }) => {
  await page.goto('/admin/customers/real-customer-id/orders');
});
```

Fix: Create synthetic test data. Never point test suites at production databases or use real customer identifiers.

### Over-engineering data setup

```typescript
// BAD — abstraction for its own sake
const data = new TestDataOrchestrator()
  .withStrategy('api')
  .withRetry(3)
  .withCleanupPolicy('deferred')
  .withEnvironment('staging')
  .build();
```

Fix: A factory function and a fixture cover 95% of cases. Add complexity only when you have a proven need.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Tests fail with "duplicate key" errors | Data from previous runs was not cleaned up | Add fixture teardown; run batch cleanup in `globalTeardown` |
| Tests pass alone but fail in parallel | Tests share mutable state or collide on unique fields | Use `Date.now()` or `crypto.randomUUID()` in factory output; use test-scoped fixtures |
| Faker produces different data on retry | Faker was not seeded, or seed changes between runs | Seed with `testInfo.workerIndex` or a fixed value |
| Storage state expired / session invalid | Auth tokens have a short TTL | Re-run auth setup before each suite; set `fullyParallel: false` on auth-dependent project if needed |
| Cleanup fails and blocks other tests | Teardown makes network calls that can timeout | Wrap cleanup in `try/catch`; log failures but do not throw; rely on batch cleanup as a safety net |
| Database seeding is slow | Too many individual INSERT statements | Batch inserts; use transactions; consider API seeding instead |
| Tests break when run against staging | Hardcoded values that only exist locally | Use environment variables for all environment-specific data; validate in fixture with clear error messages |

### Making cleanup resilient

```typescript
// Wrap fixture teardown in try/catch so a cleanup failure does not mask the real test failure
seedUser: async ({ request }, use) => {
  const user = await createViaApi(request);
  await use(user);

  try {
    await request.delete(`/api/users/${user.id}`);
  } catch (error) {
    console.warn(`Failed to clean up user ${user.id}:`, error);
  }
},
```

## Related

- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) — fixture mechanics, scoping, composition
- [core/authentication.md](authentication.md) — storage state setup, multi-role auth patterns
- [core/api-testing.md](api-testing.md) — API request context, response validation
- [ci/global-setup-teardown.md](../ci/global-setup-teardown.md) — global setup/teardown for batch operations
- [pom/pom-vs-fixtures-vs-helpers.md](../pom/pom-vs-fixtures-vs-helpers.md) — when to use fixtures vs page objects vs helpers
