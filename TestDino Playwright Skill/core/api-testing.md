# API Testing

> **When to use**: Testing REST or GraphQL APIs directly — validating endpoints, seeding test data, or verifying backend behavior without browser overhead.
> **Prerequisites**: [core/configuration.md](configuration.md) for `baseURL` setup, [core/fixtures-and-hooks.md](fixtures-and-hooks.md) for custom fixture patterns.

## Quick Reference

```typescript
// Standalone API test — no browser launched
import { test, expect } from '@playwright/test';

test('GET /api/users returns user list', async ({ request }) => {
  const response = await request.get('/api/users');
  expect(response.status()).toBe(200);
  expect(response.headers()['content-type']).toContain('application/json');
  const body = await response.json();
  expect(body.users).toHaveLength(3);
  expect(body.users[0]).toMatchObject({ id: expect.any(Number), email: expect.any(String) });
});
```

## Patterns

### APIRequestContext Basics

**Use when**: Making HTTP requests in any test — GET, POST, PUT, PATCH, DELETE with headers, query params, and request bodies.
**Avoid when**: You need to test browser-rendered responses (redirects, cookies set via `Set-Cookie` with `HttpOnly`). Use a browser test instead.

The `request` fixture provides a pre-configured `APIRequestContext` that inherits `baseURL` from your config. No browser is launched.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('CRUD operations via API', async ({ request }) => {
  // GET with query parameters
  const listResponse = await request.get('/api/users', {
    params: { page: 1, limit: 10, role: 'admin' },
  });
  expect(listResponse.ok()).toBeTruthy();

  // POST with JSON body
  const createResponse = await request.post('/api/users', {
    data: {
      name: 'Jane Doe',
      email: 'jane@example.com',
      role: 'editor',
    },
  });
  expect(createResponse.status()).toBe(201);
  const created = await createResponse.json();

  // PUT — full replacement
  const updateResponse = await request.put(`/api/users/${created.id}`, {
    data: {
      name: 'Jane Smith',
      email: 'jane.smith@example.com',
      role: 'editor',
    },
  });
  expect(updateResponse.ok()).toBeTruthy();

  // PATCH — partial update
  const patchResponse = await request.patch(`/api/users/${created.id}`, {
    data: { role: 'admin' },
  });
  expect(patchResponse.ok()).toBeTruthy();
  const patched = await patchResponse.json();
  expect(patched.role).toBe('admin');

  // DELETE
  const deleteResponse = await request.delete(`/api/users/${created.id}`);
  expect(deleteResponse.status()).toBe(204);

  // Verify deletion
  const getDeleted = await request.get(`/api/users/${created.id}`);
  expect(getDeleted.status()).toBe(404);
});

test('custom headers and auth tokens', async ({ request }) => {
  const response = await request.get('/api/protected/resource', {
    headers: {
      'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...',
      'X-Request-ID': 'test-correlation-id-123',
      'Accept': 'application/json',
    },
  });
  expect(response.ok()).toBeTruthy();
});

test('form-urlencoded body', async ({ request }) => {
  const response = await request.post('/api/oauth/token', {
    form: {
      grant_type: 'client_credentials',
      client_id: 'my-app',
      client_secret: 'secret-value',
    },
  });
  expect(response.ok()).toBeTruthy();
  const token = await response.json();
  expect(token).toHaveProperty('access_token');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('CRUD operations via API', async ({ request }) => {
  const listResponse = await request.get('/api/users', {
    params: { page: 1, limit: 10, role: 'admin' },
  });
  expect(listResponse.ok()).toBeTruthy();

  const createResponse = await request.post('/api/users', {
    data: {
      name: 'Jane Doe',
      email: 'jane@example.com',
      role: 'editor',
    },
  });
  expect(createResponse.status()).toBe(201);
  const created = await createResponse.json();

  const updateResponse = await request.put(`/api/users/${created.id}`, {
    data: {
      name: 'Jane Smith',
      email: 'jane.smith@example.com',
      role: 'editor',
    },
  });
  expect(updateResponse.ok()).toBeTruthy();

  const patchResponse = await request.patch(`/api/users/${created.id}`, {
    data: { role: 'admin' },
  });
  expect(patchResponse.ok()).toBeTruthy();

  const deleteResponse = await request.delete(`/api/users/${created.id}`);
  expect(deleteResponse.status()).toBe(204);
});

test('form-urlencoded body', async ({ request }) => {
  const response = await request.post('/api/oauth/token', {
    form: {
      grant_type: 'client_credentials',
      client_id: 'my-app',
      client_secret: 'secret-value',
    },
  });
  expect(response.ok()).toBeTruthy();
  const token = await response.json();
  expect(token).toHaveProperty('access_token');
});
```

### API Test Structure

**Use when**: Writing dedicated API test suites that do not need a browser.
**Avoid when**: You need to assert on UI state after an API call — use a combined test with `page` and `request` fixtures.

Structure API tests in their own directory with descriptive `describe` blocks per resource or domain.

**TypeScript**
```typescript
// tests/api/users.spec.ts
import { test, expect } from '@playwright/test';

// No browser is launched — these tests use only the request fixture
test.describe('Users API', () => {
  test.describe('GET /api/users', () => {
    test('returns paginated user list', async ({ request }) => {
      const response = await request.get('/api/users', {
        params: { page: 1, limit: 5 },
      });
      expect(response.status()).toBe(200);
      const body = await response.json();
      expect(body.users.length).toBeLessThanOrEqual(5);
      expect(body.pagination).toMatchObject({
        page: 1,
        limit: 5,
        total: expect.any(Number),
      });
    });

    test('filters by role', async ({ request }) => {
      const response = await request.get('/api/users', {
        params: { role: 'admin' },
      });
      const body = await response.json();
      for (const user of body.users) {
        expect(user.role).toBe('admin');
      }
    });
  });

  test.describe('POST /api/users', () => {
    test('creates a new user with valid data', async ({ request }) => {
      const response = await request.post('/api/users', {
        data: { name: 'Test User', email: `test-${Date.now()}@example.com` },
      });
      expect(response.status()).toBe(201);
      const user = await response.json();
      expect(user).toMatchObject({
        id: expect.any(Number),
        name: 'Test User',
      });
    });

    test('rejects duplicate email', async ({ request }) => {
      const email = `dupe-${Date.now()}@example.com`;
      await request.post('/api/users', { data: { name: 'First', email } });

      const response = await request.post('/api/users', {
        data: { name: 'Second', email },
      });
      expect(response.status()).toBe(409);
      const body = await response.json();
      expect(body.error).toContain('already exists');
    });
  });
});
```

**JavaScript**
```javascript
// tests/api/users.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Users API', () => {
  test.describe('GET /api/users', () => {
    test('returns paginated user list', async ({ request }) => {
      const response = await request.get('/api/users', {
        params: { page: 1, limit: 5 },
      });
      expect(response.status()).toBe(200);
      const body = await response.json();
      expect(body.users.length).toBeLessThanOrEqual(5);
      expect(body.pagination).toMatchObject({
        page: 1,
        limit: 5,
        total: expect.any(Number),
      });
    });
  });

  test.describe('POST /api/users', () => {
    test('creates a new user with valid data', async ({ request }) => {
      const response = await request.post('/api/users', {
        data: { name: 'Test User', email: `test-${Date.now()}@example.com` },
      });
      expect(response.status()).toBe(201);
      const user = await response.json();
      expect(user).toMatchObject({
        id: expect.any(Number),
        name: 'Test User',
      });
    });
  });
});
```

**Config tip**: Use a dedicated project for API tests to avoid launching browsers.

```typescript
// playwright.config.ts — API project runs without a browser
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'api',
      testDir: './tests/api',
      use: {
        baseURL: 'https://api.example.com',
        extraHTTPHeaders: {
          'Accept': 'application/json',
        },
      },
    },
    {
      name: 'e2e',
      testDir: './tests/e2e',
      use: {
        baseURL: 'https://app.example.com',
        browserName: 'chromium',
      },
    },
  ],
});
```

### Request Fixtures

**Use when**: Multiple tests need an authenticated API client, or you want to share request configuration (headers, base URL, auth tokens) across a test suite.
**Avoid when**: A single test makes one-off API calls. Use the built-in `request` fixture directly.

**TypeScript**
```typescript
// fixtures/api-fixtures.ts
import { test as base, expect, APIRequestContext } from '@playwright/test';

type ApiFixtures = {
  authenticatedRequest: APIRequestContext;
  adminRequest: APIRequestContext;
};

export const test = base.extend<ApiFixtures>({
  authenticatedRequest: async ({ playwright }, use) => {
    // Create a fresh context with auth headers
    const context = await playwright.request.newContext({
      baseURL: 'https://api.example.com',
      extraHTTPHeaders: {
        'Authorization': `Bearer ${process.env.API_TOKEN}`,
        'Accept': 'application/json',
      },
    });
    await use(context);
    await context.dispose();
  },

  adminRequest: async ({ playwright }, use) => {
    // Login via API to get a token, then create authenticated context
    const loginContext = await playwright.request.newContext({
      baseURL: 'https://api.example.com',
    });
    const loginResponse = await loginContext.post('/api/auth/login', {
      data: {
        email: process.env.ADMIN_EMAIL,
        password: process.env.ADMIN_PASSWORD,
      },
    });
    expect(loginResponse.ok()).toBeTruthy();
    const { token } = await loginResponse.json();
    await loginContext.dispose();

    const context = await playwright.request.newContext({
      baseURL: 'https://api.example.com',
      extraHTTPHeaders: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
      },
    });
    await use(context);
    await context.dispose();
  },
});

export { expect };
```

```typescript
// tests/api/admin.spec.ts
import { test, expect } from '../../fixtures/api-fixtures';

test('admin can list all users', async ({ adminRequest }) => {
  const response = await adminRequest.get('/api/admin/users');
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.users.length).toBeGreaterThan(0);
});

test('admin can delete a user', async ({ adminRequest }) => {
  // Create then delete
  const createResp = await adminRequest.post('/api/users', {
    data: { name: 'To Delete', email: `del-${Date.now()}@example.com` },
  });
  const { id } = await createResp.json();

  const deleteResp = await adminRequest.delete(`/api/users/${id}`);
  expect(deleteResp.status()).toBe(204);
});
```

**JavaScript**
```javascript
// fixtures/api-fixtures.js
const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  authenticatedRequest: async ({ playwright }, use) => {
    const context = await playwright.request.newContext({
      baseURL: 'https://api.example.com',
      extraHTTPHeaders: {
        'Authorization': `Bearer ${process.env.API_TOKEN}`,
        'Accept': 'application/json',
      },
    });
    await use(context);
    await context.dispose();
  },

  adminRequest: async ({ playwright }, use) => {
    const loginContext = await playwright.request.newContext({
      baseURL: 'https://api.example.com',
    });
    const loginResponse = await loginContext.post('/api/auth/login', {
      data: {
        email: process.env.ADMIN_EMAIL,
        password: process.env.ADMIN_PASSWORD,
      },
    });
    expect(loginResponse.ok()).toBeTruthy();
    const { token } = await loginResponse.json();
    await loginContext.dispose();

    const context = await playwright.request.newContext({
      baseURL: 'https://api.example.com',
      extraHTTPHeaders: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
      },
    });
    await use(context);
    await context.dispose();
  },
});

module.exports = { test, expect };
```

```javascript
// tests/api/admin.spec.js
const { test, expect } = require('../../fixtures/api-fixtures');

test('admin can list all users', async ({ adminRequest }) => {
  const response = await adminRequest.get('/api/admin/users');
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.users.length).toBeGreaterThan(0);
});
```

### JSON Response Assertions

**Use when**: Validating response status, headers, and body structure after every API call.
**Avoid when**: Never skip these. Every API test should assert on status and body.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('thorough response validation', async ({ request }) => {
  const response = await request.get('/api/users/42');

  // Status code — always check first
  expect(response.status()).toBe(200);

  // Status category — ok() checks 200-299 range
  expect(response.ok()).toBeTruthy();

  // Response headers
  expect(response.headers()['content-type']).toContain('application/json');
  expect(response.headers()['x-request-id']).toBeDefined();
  expect(response.headers()['cache-control']).toMatch(/max-age=\d+/);

  // Full body parse and deep assertion
  const user = await response.json();

  // Exact match on known fields
  expect(user.id).toBe(42);
  expect(user.name).toBe('Jane Doe');
  expect(user.email).toBe('jane@example.com');

  // Partial match — ignore fields you don't care about
  expect(user).toMatchObject({
    id: 42,
    name: 'Jane Doe',
    role: expect.stringMatching(/^(admin|editor|viewer)$/),
  });

  // Type checks with expect.any()
  expect(user).toMatchObject({
    id: expect.any(Number),
    name: expect.any(String),
    createdAt: expect.any(String),
    permissions: expect.any(Array),
  });

  // Array content
  expect(user.permissions).toEqual(
    expect.arrayContaining(['read', 'write'])
  );
  expect(user.permissions).not.toContain('delete');

  // Nested object assertions
  expect(user.profile).toMatchObject({
    avatar: expect.stringMatching(/^https:\/\//),
    bio: expect.any(String),
  });

  // Date format validation
  expect(new Date(user.createdAt).toISOString()).toBe(user.createdAt);
});

test('list response structure', async ({ request }) => {
  const response = await request.get('/api/users');
  const body = await response.json();

  // Array length
  expect(body.users).toHaveLength(10);

  // Every item in array matches shape
  for (const user of body.users) {
    expect(user).toMatchObject({
      id: expect.any(Number),
      name: expect.any(String),
      email: expect.stringContaining('@'),
    });
  }

  // Pagination metadata
  expect(body.pagination).toEqual({
    page: 1,
    limit: 10,
    total: expect.any(Number),
    totalPages: expect.any(Number),
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('thorough response validation', async ({ request }) => {
  const response = await request.get('/api/users/42');

  expect(response.status()).toBe(200);
  expect(response.ok()).toBeTruthy();
  expect(response.headers()['content-type']).toContain('application/json');

  const user = await response.json();

  expect(user).toMatchObject({
    id: 42,
    name: 'Jane Doe',
    role: expect.stringMatching(/^(admin|editor|viewer)$/),
  });

  expect(user).toMatchObject({
    id: expect.any(Number),
    name: expect.any(String),
    createdAt: expect.any(String),
    permissions: expect.any(Array),
  });

  expect(user.permissions).toEqual(
    expect.arrayContaining(['read', 'write'])
  );
});

test('list response structure', async ({ request }) => {
  const response = await request.get('/api/users');
  const body = await response.json();

  expect(body.users).toHaveLength(10);
  for (const user of body.users) {
    expect(user).toMatchObject({
      id: expect.any(Number),
      name: expect.any(String),
      email: expect.stringContaining('@'),
    });
  }
});
```

### GraphQL Testing

**Use when**: Your backend exposes a GraphQL API and you want to test queries, mutations, variables, and error handling.
**Avoid when**: Your API is purely REST. Use the standard HTTP methods instead.

All GraphQL requests go through `POST` to a single endpoint. Send `query`, `variables`, and optionally `operationName` in the JSON body.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

const GRAPHQL_ENDPOINT = '/graphql';

test.describe('GraphQL API', () => {
  test('query with variables', async ({ request }) => {
    const response = await request.post(GRAPHQL_ENDPOINT, {
      data: {
        query: `
          query GetUser($id: ID!) {
            user(id: $id) {
              id
              name
              email
              posts {
                id
                title
              }
            }
          }
        `,
        variables: { id: '42' },
      },
    });

    expect(response.ok()).toBeTruthy();
    const { data, errors } = await response.json();

    // GraphQL returns 200 even on errors — always check both
    expect(errors).toBeUndefined();
    expect(data.user).toMatchObject({
      id: '42',
      name: expect.any(String),
      email: expect.stringContaining('@'),
    });
    expect(data.user.posts).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ id: expect.any(String), title: expect.any(String) }),
      ])
    );
  });

  test('mutation creates a resource', async ({ request }) => {
    const response = await request.post(GRAPHQL_ENDPOINT, {
      data: {
        query: `
          mutation CreatePost($input: CreatePostInput!) {
            createPost(input: $input) {
              id
              title
              status
              author {
                id
              }
            }
          }
        `,
        variables: {
          input: {
            title: 'API Testing with Playwright',
            body: 'A comprehensive guide...',
            status: 'DRAFT',
          },
        },
      },
    });

    const { data, errors } = await response.json();
    expect(errors).toBeUndefined();
    expect(data.createPost).toMatchObject({
      id: expect.any(String),
      title: 'API Testing with Playwright',
      status: 'DRAFT',
    });
  });

  test('handles GraphQL validation errors', async ({ request }) => {
    const response = await request.post(GRAPHQL_ENDPOINT, {
      data: {
        query: `
          mutation CreatePost($input: CreatePostInput!) {
            createPost(input: $input) {
              id
            }
          }
        `,
        variables: {
          input: { title: '' }, // invalid: empty title
        },
      },
    });

    // GraphQL often returns 200 even for validation errors
    const { data, errors } = await response.json();
    expect(errors).toBeDefined();
    expect(errors.length).toBeGreaterThan(0);
    expect(errors[0].message).toContain('title');
    expect(errors[0].extensions?.code).toBe('BAD_USER_INPUT');
  });

  test('handles authorization errors', async ({ request }) => {
    const response = await request.post(GRAPHQL_ENDPOINT, {
      data: {
        query: `
          query AdminDashboard {
            adminStats {
              totalRevenue
              activeUsers
            }
          }
        `,
      },
      // No auth header
    });

    const { data, errors } = await response.json();
    expect(errors).toBeDefined();
    expect(errors[0].extensions?.code).toBe('UNAUTHORIZED');
    expect(data?.adminStats).toBeNull();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

const GRAPHQL_ENDPOINT = '/graphql';

test.describe('GraphQL API', () => {
  test('query with variables', async ({ request }) => {
    const response = await request.post(GRAPHQL_ENDPOINT, {
      data: {
        query: `
          query GetUser($id: ID!) {
            user(id: $id) {
              id
              name
              email
            }
          }
        `,
        variables: { id: '42' },
      },
    });

    const { data, errors } = await response.json();
    expect(errors).toBeUndefined();
    expect(data.user).toMatchObject({
      id: '42',
      name: expect.any(String),
      email: expect.stringContaining('@'),
    });
  });

  test('mutation creates a resource', async ({ request }) => {
    const response = await request.post(GRAPHQL_ENDPOINT, {
      data: {
        query: `
          mutation CreatePost($input: CreatePostInput!) {
            createPost(input: $input) {
              id
              title
              status
            }
          }
        `,
        variables: {
          input: {
            title: 'API Testing with Playwright',
            body: 'A comprehensive guide...',
            status: 'DRAFT',
          },
        },
      },
    });

    const { data, errors } = await response.json();
    expect(errors).toBeUndefined();
    expect(data.createPost).toMatchObject({
      id: expect.any(String),
      title: 'API Testing with Playwright',
      status: 'DRAFT',
    });
  });

  test('handles GraphQL validation errors', async ({ request }) => {
    const response = await request.post(GRAPHQL_ENDPOINT, {
      data: {
        query: `
          mutation CreatePost($input: CreatePostInput!) {
            createPost(input: $input) { id }
          }
        `,
        variables: { input: { title: '' } },
      },
    });

    const { data, errors } = await response.json();
    expect(errors).toBeDefined();
    expect(errors.length).toBeGreaterThan(0);
    expect(errors[0].message).toContain('title');
  });
});
```

### API Data Seeding

**Use when**: E2E tests need specific data to exist before running. API seeding is 10-100x faster than UI-based setup.
**Avoid when**: The test specifically validates the creation flow through the UI. Seed everything *except* what you are testing.

**TypeScript**
```typescript
import { test as base, expect, APIRequestContext } from '@playwright/test';

// Fixture that seeds data via API before each test
type SeedFixtures = {
  seedUser: { id: number; email: string; password: string };
  seedProject: { id: number; name: string };
};

export const test = base.extend<SeedFixtures>({
  seedUser: async ({ request }, use) => {
    const email = `user-${Date.now()}@example.com`;
    const password = 'TestPass123!';

    // Create via API
    const response = await request.post('/api/users', {
      data: { name: 'Test User', email, password },
    });
    expect(response.ok()).toBeTruthy();
    const user = await response.json();

    // Pass to test
    await use({ id: user.id, email, password });

    // Cleanup after test — always delete what you created
    await request.delete(`/api/users/${user.id}`);
  },

  seedProject: async ({ request, seedUser }, use) => {
    const response = await request.post('/api/projects', {
      data: { name: `Test Project ${Date.now()}`, ownerId: seedUser.id },
    });
    expect(response.ok()).toBeTruthy();
    const project = await response.json();

    await use({ id: project.id, name: project.name });

    await request.delete(`/api/projects/${project.id}`);
  },
});

export { expect };
```

```typescript
// tests/e2e/project-dashboard.spec.ts
import { test, expect } from '../../fixtures/seed-fixtures';

test('user sees their project on dashboard', async ({ page, seedUser, seedProject }) => {
  // Login via UI (or use storageState for speed)
  await page.goto('/login');
  await page.getByLabel('Email').fill(seedUser.email);
  await page.getByLabel('Password').fill(seedUser.password);
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Data already exists — go straight to assertion
  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: seedProject.name })).toBeVisible();
});
```

**JavaScript**
```javascript
// fixtures/seed-fixtures.js
const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  seedUser: async ({ request }, use) => {
    const email = `user-${Date.now()}@example.com`;
    const password = 'TestPass123!';

    const response = await request.post('/api/users', {
      data: { name: 'Test User', email, password },
    });
    expect(response.ok()).toBeTruthy();
    const user = await response.json();

    await use({ id: user.id, email, password });

    await request.delete(`/api/users/${user.id}`);
  },

  seedProject: async ({ request, seedUser }, use) => {
    const response = await request.post('/api/projects', {
      data: { name: `Test Project ${Date.now()}`, ownerId: seedUser.id },
    });
    expect(response.ok()).toBeTruthy();
    const project = await response.json();

    await use({ id: project.id, name: project.name });

    await request.delete(`/api/projects/${project.id}`);
  },
});

module.exports = { test, expect };
```

```javascript
// tests/e2e/project-dashboard.spec.js
const { test, expect } = require('../../fixtures/seed-fixtures');

test('user sees their project on dashboard', async ({ page, seedUser, seedProject }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(seedUser.email);
  await page.getByLabel('Password').fill(seedUser.password);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: seedProject.name })).toBeVisible();
});
```

### Schema Validation

**Use when**: Verifying that API responses match a contract — field types, required fields, value constraints. Catches backend regressions early.
**Avoid when**: You only need to check one or two specific fields. Use `toMatchObject` instead.

#### Option A: Zod (recommended for TypeScript projects)

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import { z } from 'zod';

// Define schemas once, reuse across tests
const UserSchema = z.object({
  id: z.number().positive(),
  name: z.string().min(1),
  email: z.string().email(),
  role: z.enum(['admin', 'editor', 'viewer']),
  createdAt: z.string().datetime(),
  profile: z.object({
    avatar: z.string().url().nullable(),
    bio: z.string().max(500),
  }),
});

const PaginatedUsersSchema = z.object({
  users: z.array(UserSchema),
  pagination: z.object({
    page: z.number().int().positive(),
    limit: z.number().int().positive(),
    total: z.number().int().nonnegative(),
  }),
});

test('GET /api/users matches schema', async ({ request }) => {
  const response = await request.get('/api/users');
  expect(response.ok()).toBeTruthy();

  const body = await response.json();
  const result = PaginatedUsersSchema.safeParse(body);

  if (!result.success) {
    // Detailed error output showing exactly which fields failed
    throw new Error(
      `Schema validation failed:\n${result.error.issues
        .map((i) => `  ${i.path.join('.')}: ${i.message}`)
        .join('\n')}`
    );
  }
});

test('POST /api/users returns valid user', async ({ request }) => {
  const response = await request.post('/api/users', {
    data: { name: 'Schema Test', email: `schema-${Date.now()}@example.com` },
  });

  const body = await response.json();
  // Throws with detailed path info if validation fails
  UserSchema.parse(body);
});
```

#### Option B: Manual type checks (no dependencies)

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

function assertUserShape(user: unknown): void {
  expect(user).toBeDefined();
  expect(user).toMatchObject({
    id: expect.any(Number),
    name: expect.any(String),
    email: expect.any(String),
    role: expect.any(String),
    createdAt: expect.any(String),
  });

  const u = user as Record<string, unknown>;
  // Value constraints
  expect(['admin', 'editor', 'viewer']).toContain(u.role);
  expect(typeof u.email === 'string' && u.email.includes('@')).toBe(true);
  expect(new Date(u.createdAt as string).toString()).not.toBe('Invalid Date');
}

test('response matches expected shape', async ({ request }) => {
  const response = await request.get('/api/users/1');
  expect(response.ok()).toBeTruthy();

  const body = await response.json();
  assertUserShape(body);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

function assertUserShape(user) {
  expect(user).toBeDefined();
  expect(user).toMatchObject({
    id: expect.any(Number),
    name: expect.any(String),
    email: expect.any(String),
    role: expect.any(String),
    createdAt: expect.any(String),
  });
  expect(['admin', 'editor', 'viewer']).toContain(user.role);
  expect(user.email).toContain('@');
  expect(new Date(user.createdAt).toString()).not.toBe('Invalid Date');
}

test('response matches expected shape', async ({ request }) => {
  const response = await request.get('/api/users/1');
  expect(response.ok()).toBeTruthy();

  const body = await response.json();
  assertUserShape(body);
});
```

### Error Response Testing

**Use when**: Every API has error paths. Test them. A missing 401 test today is a security hole tomorrow.
**Avoid when**: Never skip error testing.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test.describe('Error responses', () => {
  test('400 — validation error with details', async ({ request }) => {
    const response = await request.post('/api/users', {
      data: { name: '', email: 'not-an-email' }, // invalid
    });
    expect(response.status()).toBe(400);

    const body = await response.json();
    expect(body).toMatchObject({
      error: 'Validation Error',
      details: expect.any(Array),
    });
    // Check individual field errors
    expect(body.details).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ field: 'name', message: expect.any(String) }),
        expect.objectContaining({ field: 'email', message: expect.any(String) }),
      ])
    );
  });

  test('401 — missing authentication', async ({ request }) => {
    // Create a fresh context with NO auth headers
    const response = await request.get('/api/protected/resource', {
      headers: { 'Authorization': '' }, // explicitly clear
    });
    expect(response.status()).toBe(401);

    const body = await response.json();
    expect(body.error).toMatch(/unauthorized|unauthenticated/i);
  });

  test('403 — insufficient permissions', async ({ request }) => {
    // Assuming `request` is authenticated as a viewer
    const response = await request.delete('/api/admin/users/1');
    expect(response.status()).toBe(403);

    const body = await response.json();
    expect(body.error).toMatch(/forbidden|insufficient permissions/i);
  });

  test('404 — resource not found', async ({ request }) => {
    const response = await request.get('/api/users/999999');
    expect(response.status()).toBe(404);

    const body = await response.json();
    expect(body).toMatchObject({
      error: expect.stringMatching(/not found/i),
    });
  });

  test('409 — conflict on duplicate resource', async ({ request }) => {
    const email = `conflict-${Date.now()}@example.com`;
    await request.post('/api/users', {
      data: { name: 'First', email },
    });

    const response = await request.post('/api/users', {
      data: { name: 'Duplicate', email },
    });
    expect(response.status()).toBe(409);
  });

  test('422 — unprocessable entity', async ({ request }) => {
    const response = await request.post('/api/orders', {
      data: { items: [] }, // empty cart
    });
    expect(response.status()).toBe(422);
    const body = await response.json();
    expect(body.error).toContain('at least one item');
  });

  test('429 — rate limiting', async ({ request }) => {
    // Send rapid requests to trigger rate limit
    const responses = await Promise.all(
      Array.from({ length: 50 }, () =>
        request.get('/api/search', { params: { q: 'test' } })
      )
    );
    const rateLimited = responses.filter((r) => r.status() === 429);
    expect(rateLimited.length).toBeGreaterThan(0);

    // Verify rate limit headers
    const limited = rateLimited[0];
    expect(limited.headers()['retry-after']).toBeDefined();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Error responses', () => {
  test('400 — validation error with details', async ({ request }) => {
    const response = await request.post('/api/users', {
      data: { name: '', email: 'not-an-email' },
    });
    expect(response.status()).toBe(400);

    const body = await response.json();
    expect(body).toMatchObject({
      error: 'Validation Error',
      details: expect.any(Array),
    });
    expect(body.details).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ field: 'name', message: expect.any(String) }),
        expect.objectContaining({ field: 'email', message: expect.any(String) }),
      ])
    );
  });

  test('401 — missing authentication', async ({ request }) => {
    const response = await request.get('/api/protected/resource', {
      headers: { 'Authorization': '' },
    });
    expect(response.status()).toBe(401);
  });

  test('404 — resource not found', async ({ request }) => {
    const response = await request.get('/api/users/999999');
    expect(response.status()).toBe(404);
  });

  test('409 — conflict on duplicate resource', async ({ request }) => {
    const email = `conflict-${Date.now()}@example.com`;
    await request.post('/api/users', { data: { name: 'First', email } });

    const response = await request.post('/api/users', {
      data: { name: 'Duplicate', email },
    });
    expect(response.status()).toBe(409);
  });
});
```

### File Upload via API

**Use when**: Testing file upload endpoints with multipart form data — document uploads, image processing, CSV imports.
**Avoid when**: You need to test the browser file picker dialog. Use `page.setInputFiles()` in an E2E test instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

test('upload a file via multipart form data', async ({ request }) => {
  const filePath = path.resolve('tests/fixtures/test-document.pdf');

  const response = await request.post('/api/documents/upload', {
    multipart: {
      file: {
        name: 'test-document.pdf',
        mimeType: 'application/pdf',
        buffer: fs.readFileSync(filePath),
      },
      description: 'Quarterly report',
      category: 'reports',
    },
  });

  expect(response.status()).toBe(201);
  const body = await response.json();
  expect(body).toMatchObject({
    id: expect.any(String),
    filename: 'test-document.pdf',
    mimeType: 'application/pdf',
    size: expect.any(Number),
    url: expect.stringMatching(/^https:\/\//),
  });
});

test('upload an image with metadata', async ({ request }) => {
  const imagePath = path.resolve('tests/fixtures/avatar.png');

  const response = await request.post('/api/users/42/avatar', {
    multipart: {
      image: {
        name: 'avatar.png',
        mimeType: 'image/png',
        buffer: fs.readFileSync(imagePath),
      },
      crop: JSON.stringify({ x: 0, y: 0, width: 200, height: 200 }),
    },
  });

  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body.avatarUrl).toMatch(/\.png$/);
});

test('upload multiple files', async ({ request }) => {
  const files = ['report-q1.csv', 'report-q2.csv'].map((name) => ({
    name,
    mimeType: 'text/csv',
    buffer: fs.readFileSync(path.resolve(`tests/fixtures/${name}`)),
  }));

  // Send sequential uploads when the API does not support batch
  const results = [];
  for (const file of files) {
    const response = await request.post('/api/imports/csv', {
      multipart: { file },
    });
    expect(response.ok()).toBeTruthy();
    results.push(await response.json());
  }
  expect(results).toHaveLength(2);
});

test('rejects oversized files', async ({ request }) => {
  // Create a buffer that exceeds the server limit
  const largeBuffer = Buffer.alloc(11 * 1024 * 1024); // 11MB

  const response = await request.post('/api/documents/upload', {
    multipart: {
      file: {
        name: 'large-file.bin',
        mimeType: 'application/octet-stream',
        buffer: largeBuffer,
      },
    },
  });

  expect(response.status()).toBe(413); // Payload Too Large
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

test('upload a file via multipart form data', async ({ request }) => {
  const filePath = path.resolve('tests/fixtures/test-document.pdf');

  const response = await request.post('/api/documents/upload', {
    multipart: {
      file: {
        name: 'test-document.pdf',
        mimeType: 'application/pdf',
        buffer: fs.readFileSync(filePath),
      },
      description: 'Quarterly report',
      category: 'reports',
    },
  });

  expect(response.status()).toBe(201);
  const body = await response.json();
  expect(body).toMatchObject({
    id: expect.any(String),
    filename: 'test-document.pdf',
    mimeType: 'application/pdf',
    size: expect.any(Number),
  });
});

test('rejects oversized files', async ({ request }) => {
  const largeBuffer = Buffer.alloc(11 * 1024 * 1024);

  const response = await request.post('/api/documents/upload', {
    multipart: {
      file: {
        name: 'large-file.bin',
        mimeType: 'application/octet-stream',
        buffer: largeBuffer,
      },
    },
  });

  expect(response.status()).toBe(413);
});
```

### Chained API Calls

**Use when**: Testing multi-step workflows — create, read, update, delete sequences; order flows; state machine transitions. This verifies the API's behavior as an integrated system, not just isolated endpoints.
**Avoid when**: You can test each endpoint in isolation and the interactions are trivial.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('complete order workflow', async ({ request }) => {
  // Step 1: Create a product
  const productResp = await request.post('/api/products', {
    data: { name: 'Widget', price: 29.99, stock: 100 },
  });
  expect(productResp.status()).toBe(201);
  const product = await productResp.json();

  // Step 2: Create a cart
  const cartResp = await request.post('/api/carts', {
    data: { items: [{ productId: product.id, quantity: 2 }] },
  });
  expect(cartResp.status()).toBe(201);
  const cart = await cartResp.json();
  expect(cart.total).toBe(59.98);

  // Step 3: Checkout — create an order from the cart
  const orderResp = await request.post('/api/orders', {
    data: {
      cartId: cart.id,
      shippingAddress: {
        street: '123 Test St',
        city: 'Testville',
        zip: '12345',
      },
    },
  });
  expect(orderResp.status()).toBe(201);
  const order = await orderResp.json();
  expect(order.status).toBe('pending');
  expect(order.items).toHaveLength(1);
  expect(order.total).toBe(59.98);

  // Step 4: Verify order appears in user's order list
  const ordersResp = await request.get('/api/orders');
  const orders = await ordersResp.json();
  expect(orders.items.map((o: any) => o.id)).toContain(order.id);

  // Step 5: Verify product stock decreased
  const updatedProduct = await (await request.get(`/api/products/${product.id}`)).json();
  expect(updatedProduct.stock).toBe(98); // 100 - 2

  // Cleanup
  await request.delete(`/api/orders/${order.id}`);
  await request.delete(`/api/products/${product.id}`);
});

test('state machine transitions — publish workflow', async ({ request }) => {
  // Create a draft post
  const createResp = await request.post('/api/posts', {
    data: { title: 'Draft Post', body: 'Content here.' },
  });
  const post = await createResp.json();
  expect(post.status).toBe('draft');

  // Submit for review
  const reviewResp = await request.patch(`/api/posts/${post.id}/status`, {
    data: { status: 'in_review' },
  });
  expect(reviewResp.ok()).toBeTruthy();
  expect((await reviewResp.json()).status).toBe('in_review');

  // Approve (requires admin — use appropriate fixture in real tests)
  const approveResp = await request.patch(`/api/posts/${post.id}/status`, {
    data: { status: 'published' },
  });
  expect(approveResp.ok()).toBeTruthy();
  expect((await approveResp.json()).status).toBe('published');

  // Verify: cannot go back to draft from published
  const revertResp = await request.patch(`/api/posts/${post.id}/status`, {
    data: { status: 'draft' },
  });
  expect(revertResp.status()).toBe(422);

  // Cleanup
  await request.delete(`/api/posts/${post.id}`);
});

test('API + E2E hybrid — seed via API, verify in browser', async ({ request, page }) => {
  // Seed test data via API
  const resp = await request.post('/api/products', {
    data: {
      name: `Hybrid Test Product ${Date.now()}`,
      price: 42.00,
      published: true,
    },
  });
  const product = await resp.json();

  // Verify via browser
  await page.goto('/products');
  await expect(
    page.getByRole('heading', { name: product.name })
  ).toBeVisible();
  await expect(page.getByText('$42.00')).toBeVisible();

  // Cleanup via API
  await request.delete(`/api/products/${product.id}`);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('complete order workflow', async ({ request }) => {
  const productResp = await request.post('/api/products', {
    data: { name: 'Widget', price: 29.99, stock: 100 },
  });
  expect(productResp.status()).toBe(201);
  const product = await productResp.json();

  const cartResp = await request.post('/api/carts', {
    data: { items: [{ productId: product.id, quantity: 2 }] },
  });
  expect(cartResp.status()).toBe(201);
  const cart = await cartResp.json();
  expect(cart.total).toBe(59.98);

  const orderResp = await request.post('/api/orders', {
    data: {
      cartId: cart.id,
      shippingAddress: {
        street: '123 Test St',
        city: 'Testville',
        zip: '12345',
      },
    },
  });
  expect(orderResp.status()).toBe(201);
  const order = await orderResp.json();
  expect(order.status).toBe('pending');

  const ordersResp = await request.get('/api/orders');
  const orders = await ordersResp.json();
  expect(orders.items.map((o) => o.id)).toContain(order.id);

  await request.delete(`/api/orders/${order.id}`);
  await request.delete(`/api/products/${product.id}`);
});

test('API + E2E hybrid — seed via API, verify in browser', async ({ request, page }) => {
  const resp = await request.post('/api/products', {
    data: {
      name: `Hybrid Test Product ${Date.now()}`,
      price: 42.00,
      published: true,
    },
  });
  const product = await resp.json();

  await page.goto('/products');
  await expect(
    page.getByRole('heading', { name: product.name })
  ).toBeVisible();

  await request.delete(`/api/products/${product.id}`);
});
```

## Decision Guide

| Scenario | Use API Tests | Use E2E Tests | Why |
|---|---|---|---|
| Validate response status/body/headers | Yes | No | No browser needed; 10-100x faster |
| Test business logic (calculations, rules) | Yes | No | API tests isolate backend logic from UI |
| Verify form submission creates correct data | Seed via API, submit via UI | Yes | UI test validates the form; API check confirms persistence |
| Test error messages shown to user | No | Yes | Error rendering is a UI concern |
| Validate pagination, filtering, sorting | Yes | Maybe both | API test for correctness; E2E test only if the UI logic is complex |
| Seed test data for E2E tests | Yes (fixture) | No | API seeding is fast and reliable |
| Test auth flows (login/logout/RBAC) | Yes for token/session logic | Yes for UI flow | Both matter: API protects resources, UI guides users |
| Verify file upload processing | Yes | Only if testing file picker UI | API test validates backend processing |
| Contract/schema regression testing | Yes | No | Schema tests run in milliseconds |
| Test third-party webhook handling | Yes | No | Webhooks are API-to-API; no UI involved |
| Verify redirect behavior after action | No | Yes | Redirects are browser/navigation concerns |
| Test real-time updates (WebSocket + API trigger) | API triggers | E2E verifies | Seed via API, observe in browser |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Use E2E tests to validate pure API responses | Slow, flaky, launches a browser for no reason | Use `request` fixture — no browser, direct HTTP |
| Ignore `response.status()` | A 500 with a fallback body can pass all body assertions | Always assert status first: `expect(response.status()).toBe(200)` |
| Skip response header checks | Missing `Content-Type`, `Cache-Control`, CORS headers cause production bugs | Assert critical headers: `expect(response.headers()['content-type']).toContain('application/json')` |
| Only test the happy path | Real users trigger 400, 401, 403, 404, 409, 422 — every one needs a test | Dedicate a `describe` block to error responses |
| Hardcode IDs in API tests | Tests break when database is reset or IDs are reassigned | Create resources in the test, use returned IDs |
| Share mutable state between tests | Tests that depend on execution order are flaky and cannot run in parallel | Each test creates and cleans up its own data |
| Parse `response.text()` then `JSON.parse()` manually | Playwright's `response.json()` handles this and throws clear errors on non-JSON | Use `await response.json()` |
| Forget cleanup after creating resources | Test pollution: subsequent tests may see stale data or hit unique constraints | Use fixtures with teardown or explicit `delete` calls |
| Test GraphQL by checking only `response.ok()` | GraphQL returns 200 even on errors — `errors` array is the real signal | Always check both `data` and `errors` in the response body |
| Use `page.request` when you don't need a page | `page.request` shares cookies with the browser context, which may cause auth confusion | Use the standalone `request` fixture for pure API tests |

## Troubleshooting

### "Request failed: connect ECONNREFUSED 127.0.0.1:3000"

**Cause**: The API server is not running, or `baseURL` points to the wrong host/port.

**Fix**:
- Verify the server is running before tests: use `webServer` in `playwright.config.ts` to start it automatically.
- Check `baseURL` in your config matches the actual server address.

```typescript
// playwright.config.ts
export default defineConfig({
  webServer: {
    command: 'npm run start:api',
    url: 'http://localhost:3000/api/health',
    reuseExistingServer: !process.env.CI,
  },
  use: {
    baseURL: 'http://localhost:3000',
  },
});
```

### "response.json() failed — body is not valid JSON"

**Cause**: The endpoint returned HTML (error page), plain text, or an empty body instead of JSON.

**Fix**:
- Check `response.status()` first — a 500 or 302 often returns HTML.
- Log `await response.text()` to see the actual body.
- Verify the `Accept: application/json` header is set.

```typescript
const response = await request.get('/api/endpoint');
if (!response.ok()) {
  console.error(`Status: ${response.status()}, Body: ${await response.text()}`);
}
const body = await response.json(); // now you know what failed
```

### "401 Unauthorized" when using `request` fixture

**Cause**: The built-in `request` fixture does not carry browser cookies or auth tokens automatically. It starts with a clean slate.

**Fix**:
- Set `extraHTTPHeaders` in your config or create a custom authenticated fixture.
- If you need cookies from a browser login, use `page.request` (which shares the browser context's cookies) instead of the standalone `request` fixture.

```typescript
// Option A: config-level headers
export default defineConfig({
  use: {
    extraHTTPHeaders: {
      'Authorization': `Bearer ${process.env.API_TOKEN}`,
    },
  },
});

// Option B: per-request headers
const response = await request.get('/api/resource', {
  headers: { 'Authorization': `Bearer ${token}` },
});

// Option C: use page.request to inherit browser cookies
test('API call with browser auth', async ({ page }) => {
  await page.goto('/login');
  // ... login via UI ...
  const response = await page.request.get('/api/profile');
  expect(response.ok()).toBeTruthy();
});
```

### GraphQL returns 200 but data is null

**Cause**: GraphQL servers return HTTP 200 even when the query has errors. The actual error is in the `errors` array.

**Fix**: Always destructure and check both `data` and `errors`.

```typescript
const { data, errors } = await response.json();
if (errors) {
  console.error('GraphQL errors:', JSON.stringify(errors, null, 2));
}
expect(errors).toBeUndefined();
expect(data.user).toBeDefined();
```

### Tests pass locally but fail in CI

**Cause**: Different environments, database state, or missing environment variables.

**Fix**:
- Use `process.env` for secrets and base URLs — never hardcode them.
- Run database seeds or migrations in `globalSetup`.
- Use unique identifiers (timestamps, UUIDs) for test data to avoid collisions in parallel runs.
- Check that the CI `baseURL` matches the deployed or containerized service.

## Related

- [core/configuration.md](configuration.md) — `baseURL`, `extraHTTPHeaders`, and `webServer` config
- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) — custom fixture patterns for reusable API clients
- [core/authentication.md](authentication.md) — auth patterns including token-based API auth
- [core/network-mocking.md](network-mocking.md) — mocking API responses in E2E tests (opposite of this guide)
- [core/test-architecture.md](test-architecture.md) — when to use API tests vs E2E vs component tests
- [core/when-to-mock.md](when-to-mock.md) — when to hit real APIs vs mock them
