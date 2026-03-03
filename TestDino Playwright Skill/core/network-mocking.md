# Network Mocking

> **When to use**: Isolating your frontend from external services, simulating error states, testing loading/empty/error UI, speeding up tests by avoiding real network calls, and testing against APIs that don't exist yet.
> **Prerequisites**: [core/locators.md](locators.md), [core/assertions-and-waiting.md](assertions-and-waiting.md)

## Quick Reference

```typescript
// Intercept and return fake data
await page.route('**/api/users', (route) =>
  route.fulfill({ json: [{ id: 1, name: 'Jane' }] })
);

// Modify a real response before it reaches the browser
await page.route('**/api/users', async (route) => {
  const response = await route.fetch();
  const json = await response.json();
  json.push({ id: 999, name: 'Injected' });
  await route.fulfill({ response, json });
});

// Block third-party scripts
await page.route('**/*.{png,jpg,svg}', (route) => route.abort());

// Wait for a specific request/response
const responsePromise = page.waitForResponse('**/api/users');
await page.getByRole('button', { name: 'Load' }).click();
await responsePromise;

// HAR replay — serve recorded responses
await page.routeFromHAR('tests/data/api.har', { url: '**/api/**' });
```

## Patterns

### Route Interception Basics

**Use when**: You need to intercept any HTTP request made by the page to fulfill, modify, or block it.
**Avoid when**: You want to test the real integration between frontend and backend (use real API calls instead).

`page.route()` registers a handler that runs for every request matching a URL pattern. Each handler must call exactly one of `route.fulfill()`, `route.continue()`, or `route.abort()`.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('route interception basics', async ({ page }) => {
  // Intercept before navigating — routes must be set up first
  await page.route('**/api/users', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 1, name: 'Alice' }]),
    });
  });

  await page.goto('/dashboard');
  await expect(page.getByText('Alice')).toBeVisible();

  // Remove the route when done (important for cleanup)
  await page.unroute('**/api/users');
});

test('context-level routes apply to all pages', async ({ context, page }) => {
  // Routes on the context apply to every page in that context
  await context.route('**/api/config', (route) =>
    route.fulfill({ json: { theme: 'dark', locale: 'en' } })
  );

  await page.goto('/settings');
  await expect(page.getByText('Dark')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('route interception basics', async ({ page }) => {
  await page.route('**/api/users', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 1, name: 'Alice' }]),
    });
  });

  await page.goto('/dashboard');
  await expect(page.getByText('Alice')).toBeVisible();

  await page.unroute('**/api/users');
});

test('context-level routes apply to all pages', async ({ context, page }) => {
  await context.route('**/api/config', (route) =>
    route.fulfill({ json: { theme: 'dark', locale: 'en' } })
  );

  await page.goto('/settings');
  await expect(page.getByText('Dark')).toBeVisible();
});
```

### Mocking REST Responses

**Use when**: Your frontend depends on a REST API and you want deterministic, instant responses with controlled data.
**Avoid when**: You need to verify that your frontend sends the correct request body or headers to the real API (use `route.continue()` with `waitForRequest` instead).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

const mockUsers = [
  { id: 1, name: 'Alice', email: 'alice@example.com', role: 'admin' },
  { id: 2, name: 'Bob', email: 'bob@example.com', role: 'user' },
];

test('mock a GET endpoint with JSON', async ({ page }) => {
  await page.route('**/api/users', (route) =>
    route.fulfill({ json: mockUsers })
  );

  await page.goto('/users');
  await expect(page.getByRole('row')).toHaveCount(3); // header + 2 data rows
});

test('mock a POST endpoint and verify the request', async ({ page }) => {
  await page.route('**/api/users', (route) => {
    if (route.request().method() === 'POST') {
      return route.fulfill({
        status: 201,
        json: { id: 3, name: 'Charlie', email: 'charlie@example.com' },
      });
    }
    // Let other methods through
    return route.continue();
  });

  await page.goto('/users/new');
  await page.getByLabel('Name').fill('Charlie');
  await page.getByLabel('Email').fill('charlie@example.com');
  await page.getByRole('button', { name: 'Create' }).click();

  await expect(page.getByText('Charlie')).toBeVisible();
});

test('mock with custom headers and status', async ({ page }) => {
  await page.route('**/api/users', (route) =>
    route.fulfill({
      status: 200,
      headers: {
        'content-type': 'application/json',
        'x-total-count': '42',
        'x-request-id': 'test-abc-123',
      },
      body: JSON.stringify(mockUsers),
    })
  );

  await page.goto('/users');
  await expect(page.getByText('42 total')).toBeVisible();
});

test('mock empty state', async ({ page }) => {
  await page.route('**/api/users', (route) =>
    route.fulfill({ json: [] })
  );

  await page.goto('/users');
  await expect(page.getByText('No users found')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

const mockUsers = [
  { id: 1, name: 'Alice', email: 'alice@example.com', role: 'admin' },
  { id: 2, name: 'Bob', email: 'bob@example.com', role: 'user' },
];

test('mock a GET endpoint with JSON', async ({ page }) => {
  await page.route('**/api/users', (route) =>
    route.fulfill({ json: mockUsers })
  );

  await page.goto('/users');
  await expect(page.getByRole('row')).toHaveCount(3);
});

test('mock a POST endpoint and verify the request', async ({ page }) => {
  await page.route('**/api/users', (route) => {
    if (route.request().method() === 'POST') {
      return route.fulfill({
        status: 201,
        json: { id: 3, name: 'Charlie', email: 'charlie@example.com' },
      });
    }
    return route.continue();
  });

  await page.goto('/users/new');
  await page.getByLabel('Name').fill('Charlie');
  await page.getByLabel('Email').fill('charlie@example.com');
  await page.getByRole('button', { name: 'Create' }).click();

  await expect(page.getByText('Charlie')).toBeVisible();
});

test('mock empty state', async ({ page }) => {
  await page.route('**/api/users', (route) =>
    route.fulfill({ json: [] })
  );

  await page.goto('/users');
  await expect(page.getByText('No users found')).toBeVisible();
});
```

### Mocking GraphQL

**Use when**: Your frontend uses GraphQL and you want to mock specific queries or mutations by operation name.
**Avoid when**: The GraphQL endpoint is part of your own backend and you want full integration coverage.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('mock a GraphQL query by operation name', async ({ page }) => {
  await page.route('**/graphql', async (route) => {
    const request = route.request();
    const postData = request.postDataJSON();

    if (postData.operationName === 'GetUsers') {
      return route.fulfill({
        json: {
          data: {
            users: [
              { id: '1', name: 'Alice', email: 'alice@example.com' },
              { id: '2', name: 'Bob', email: 'bob@example.com' },
            ],
          },
        },
      });
    }

    if (postData.operationName === 'GetUser') {
      return route.fulfill({
        json: {
          data: {
            user: { id: '1', name: 'Alice', email: 'alice@example.com' },
          },
        },
      });
    }

    // Let unmocked operations through to the real server
    return route.continue();
  });

  await page.goto('/users');
  await expect(page.getByText('Alice')).toBeVisible();
  await expect(page.getByText('Bob')).toBeVisible();
});

test('mock a GraphQL mutation', async ({ page }) => {
  await page.route('**/graphql', async (route) => {
    const { operationName, variables } = route.request().postDataJSON();

    if (operationName === 'CreateUser') {
      return route.fulfill({
        json: {
          data: {
            createUser: {
              id: '99',
              name: variables.input.name,
              email: variables.input.email,
            },
          },
        },
      });
    }

    return route.continue();
  });

  await page.goto('/users/new');
  await page.getByLabel('Name').fill('Charlie');
  await page.getByLabel('Email').fill('charlie@example.com');
  await page.getByRole('button', { name: 'Create' }).click();

  await expect(page.getByText('Charlie')).toBeVisible();
});

test('mock GraphQL errors', async ({ page }) => {
  await page.route('**/graphql', async (route) => {
    const { operationName } = route.request().postDataJSON();

    if (operationName === 'GetUsers') {
      return route.fulfill({
        json: {
          data: null,
          errors: [
            {
              message: 'Not authorized',
              extensions: { code: 'UNAUTHORIZED' },
            },
          ],
        },
      });
    }

    return route.continue();
  });

  await page.goto('/users');
  await expect(page.getByText('Not authorized')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('mock a GraphQL query by operation name', async ({ page }) => {
  await page.route('**/graphql', async (route) => {
    const postData = route.request().postDataJSON();

    if (postData.operationName === 'GetUsers') {
      return route.fulfill({
        json: {
          data: {
            users: [
              { id: '1', name: 'Alice', email: 'alice@example.com' },
              { id: '2', name: 'Bob', email: 'bob@example.com' },
            ],
          },
        },
      });
    }

    return route.continue();
  });

  await page.goto('/users');
  await expect(page.getByText('Alice')).toBeVisible();
  await expect(page.getByText('Bob')).toBeVisible();
});

test('mock a GraphQL mutation', async ({ page }) => {
  await page.route('**/graphql', async (route) => {
    const { operationName, variables } = route.request().postDataJSON();

    if (operationName === 'CreateUser') {
      return route.fulfill({
        json: {
          data: {
            createUser: {
              id: '99',
              name: variables.input.name,
              email: variables.input.email,
            },
          },
        },
      });
    }

    return route.continue();
  });

  await page.goto('/users/new');
  await page.getByLabel('Name').fill('Charlie');
  await page.getByLabel('Email').fill('charlie@example.com');
  await page.getByRole('button', { name: 'Create' }).click();

  await expect(page.getByText('Charlie')).toBeVisible();
});
```

### Modifying Responses

**Use when**: You need the real API response but want to tweak specific fields -- inject test data, override feature flags, simulate edge cases in real data.
**Avoid when**: You can fully mock the response. `route.fetch()` adds a real network round-trip, so it is slower.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('modify a real API response', async ({ page }) => {
  await page.route('**/api/users', async (route) => {
    // Fetch the real response from the server
    const response = await route.fetch();
    const users = await response.json();

    // Inject a test user into the real data
    users.push({ id: 999, name: 'Test User', email: 'test@example.com' });

    await route.fulfill({ response, json: users });
  });

  await page.goto('/users');
  await expect(page.getByText('Test User')).toBeVisible();
});

test('override feature flags from real config', async ({ page }) => {
  await page.route('**/api/config', async (route) => {
    const response = await route.fetch();
    const config = await response.json();

    // Enable a feature flag for testing
    config.featureFlags = {
      ...config.featureFlags,
      newCheckout: true,
      darkMode: true,
    };

    await route.fulfill({ response, json: config });
  });

  await page.goto('/settings');
  await expect(page.getByRole('switch', { name: 'Dark mode' })).toBeVisible();
});

test('modify response headers', async ({ page }) => {
  await page.route('**/api/data', async (route) => {
    const response = await route.fetch();

    await route.fulfill({
      response,
      headers: {
        ...response.headers(),
        'cache-control': 'no-cache',
        'x-test-header': 'injected',
      },
    });
  });

  await page.goto('/data');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('modify a real API response', async ({ page }) => {
  await page.route('**/api/users', async (route) => {
    const response = await route.fetch();
    const users = await response.json();

    users.push({ id: 999, name: 'Test User', email: 'test@example.com' });

    await route.fulfill({ response, json: users });
  });

  await page.goto('/users');
  await expect(page.getByText('Test User')).toBeVisible();
});

test('override feature flags from real config', async ({ page }) => {
  await page.route('**/api/config', async (route) => {
    const response = await route.fetch();
    const config = await response.json();

    config.featureFlags = {
      ...config.featureFlags,
      newCheckout: true,
      darkMode: true,
    };

    await route.fulfill({ response, json: config });
  });

  await page.goto('/settings');
  await expect(page.getByRole('switch', { name: 'Dark mode' })).toBeVisible();
});
```

### Request Blocking

**Use when**: Blocking analytics, ads, third-party scripts, images, or fonts to speed up tests and eliminate flakiness from external dependencies.
**Avoid when**: The blocked resource is required for the feature under test.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('block analytics and tracking scripts', async ({ page }) => {
  await page.route(/(google-analytics|segment|hotjar|mixpanel)/, (route) =>
    route.abort()
  );

  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});

test('block images to speed up tests', async ({ page }) => {
  await page.route('**/*.{png,jpg,jpeg,gif,svg,webp}', (route) =>
    route.abort()
  );

  await page.goto('/gallery');
  // Test interactions without waiting for image downloads
  await page.getByRole('button', { name: 'Next' }).click();
});

test('block specific third-party domains', async ({ page }) => {
  const blockedDomains = [
    'ads.example.com',
    'tracker.example.com',
    'cdn.slow-service.com',
  ];

  await page.route('**/*', (route) => {
    const url = new URL(route.request().url());
    if (blockedDomains.includes(url.hostname)) {
      return route.abort();
    }
    return route.continue();
  });

  await page.goto('/home');
});

test('block by resource type', async ({ context }) => {
  // Context-level blocking affects all pages
  await context.route('**/*', (route) => {
    const resourceType = route.request().resourceType();
    if (['image', 'font', 'media'].includes(resourceType)) {
      return route.abort();
    }
    return route.continue();
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('block analytics and tracking scripts', async ({ page }) => {
  await page.route(/(google-analytics|segment|hotjar|mixpanel)/, (route) =>
    route.abort()
  );

  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});

test('block images to speed up tests', async ({ page }) => {
  await page.route('**/*.{png,jpg,jpeg,gif,svg,webp}', (route) =>
    route.abort()
  );

  await page.goto('/gallery');
  await page.getByRole('button', { name: 'Next' }).click();
});

test('block by resource type', async ({ context }) => {
  await context.route('**/*', (route) => {
    const resourceType = route.request().resourceType();
    if (['image', 'font', 'media'].includes(resourceType)) {
      return route.abort();
    }
    return route.continue();
  });
});
```

### HAR Recording and Replay

**Use when**: You want to capture real network traffic once and replay it in tests for speed and determinism. Great for complex APIs with many endpoints or when API access is limited.
**Avoid when**: API responses change frequently and stale recordings would cause false passes. Keep HAR files in version control and update them regularly.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// Record a HAR file — run once to capture traffic, then replay
test('record HAR for later replay', async ({ page }) => {
  // This records all matching network traffic to the HAR file.
  // If the file already exists and responses match, it serves from HAR.
  // If a request has no match in the HAR, it falls through to the network
  // and the new response is appended to the HAR file.
  await page.routeFromHAR('tests/data/users-api.har', {
    url: '**/api/**',
    update: true, // set to true to record, false (or omit) to replay
  });

  await page.goto('/users');
  await expect(page.getByRole('row')).toHaveCount(6);
});

// Replay from a previously recorded HAR file
test('replay from HAR', async ({ page }) => {
  await page.routeFromHAR('tests/data/users-api.har', {
    url: '**/api/**',
    // update: false is the default — serves from the HAR file
  });

  await page.goto('/users');
  await expect(page.getByRole('row')).toHaveCount(6);
});

// HAR with notFound option — control what happens for unmatched requests
test('HAR replay with fallback behavior', async ({ page }) => {
  await page.routeFromHAR('tests/data/users-api.har', {
    url: '**/api/**',
    notFound: 'abort', // 'abort' fails unmatched requests; 'fallback' lets them through
  });

  await page.goto('/users');
  await expect(page.getByText('Alice')).toBeVisible();
});

// Context-level HAR replay
test('HAR replay at context level', async ({ context, page }) => {
  await context.routeFromHAR('tests/data/full-app.har', {
    url: '**/api/**',
  });

  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('record HAR for later replay', async ({ page }) => {
  await page.routeFromHAR('tests/data/users-api.har', {
    url: '**/api/**',
    update: true,
  });

  await page.goto('/users');
  await expect(page.getByRole('row')).toHaveCount(6);
});

test('replay from HAR', async ({ page }) => {
  await page.routeFromHAR('tests/data/users-api.har', {
    url: '**/api/**',
  });

  await page.goto('/users');
  await expect(page.getByRole('row')).toHaveCount(6);
});

test('HAR replay with fallback behavior', async ({ page }) => {
  await page.routeFromHAR('tests/data/users-api.har', {
    url: '**/api/**',
    notFound: 'abort',
  });

  await page.goto('/users');
  await expect(page.getByText('Alice')).toBeVisible();
});
```

### Conditional Mocking

**Use when**: You need different responses based on the request method, body, headers, or query parameters. Common for paginated APIs, search endpoints, and role-based access.
**Avoid when**: Simple static mocking suffices. Don't over-engineer route handlers.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('respond based on request method', async ({ page }) => {
  await page.route('**/api/users', (route) => {
    const method = route.request().method();

    switch (method) {
      case 'GET':
        return route.fulfill({
          json: [{ id: 1, name: 'Alice' }],
        });
      case 'POST':
        return route.fulfill({
          status: 201,
          json: { id: 2, name: 'Bob' },
        });
      case 'DELETE':
        return route.fulfill({ status: 204, body: '' });
      default:
        return route.continue();
    }
  });

  await page.goto('/users');
  await expect(page.getByText('Alice')).toBeVisible();
});

test('respond based on query parameters', async ({ page }) => {
  await page.route('**/api/users*', (route) => {
    const url = new URL(route.request().url());
    const page_num = parseInt(url.searchParams.get('page') || '1');
    const role = url.searchParams.get('role');

    const allUsers = [
      { id: 1, name: 'Alice', role: 'admin' },
      { id: 2, name: 'Bob', role: 'user' },
      { id: 3, name: 'Charlie', role: 'user' },
      { id: 4, name: 'Diana', role: 'admin' },
    ];

    let filtered = allUsers;
    if (role) {
      filtered = allUsers.filter((u) => u.role === role);
    }

    const perPage = 2;
    const start = (page_num - 1) * perPage;
    const paginated = filtered.slice(start, start + perPage);

    return route.fulfill({
      json: paginated,
      headers: {
        'content-type': 'application/json',
        'x-total-count': String(filtered.length),
      },
    });
  });

  await page.goto('/users');
  await expect(page.getByRole('row')).toHaveCount(3); // header + 2 rows
});

test('respond based on request body', async ({ page }) => {
  await page.route('**/api/search', (route) => {
    const body = route.request().postDataJSON();
    const query = body?.query?.toLowerCase() || '';

    const results = {
      playwright: [{ title: 'Playwright Docs' }, { title: 'Playwright GitHub' }],
      cypress: [{ title: 'Cypress Docs' }],
    };

    return route.fulfill({
      json: results[query] || [],
    });
  });

  await page.goto('/search');
  await page.getByLabel('Search').fill('playwright');
  await page.getByRole('button', { name: 'Search' }).click();
  await expect(page.getByRole('listitem')).toHaveCount(2);
});

test('respond based on request headers', async ({ page }) => {
  await page.route('**/api/users', (route) => {
    const authHeader = route.request().headers()['authorization'];

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return route.fulfill({
        status: 401,
        json: { error: 'Unauthorized' },
      });
    }

    return route.fulfill({
      json: [{ id: 1, name: 'Alice' }],
    });
  });

  await page.goto('/login');
  await expect(page.getByText('Unauthorized')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('respond based on request method', async ({ page }) => {
  await page.route('**/api/users', (route) => {
    const method = route.request().method();

    switch (method) {
      case 'GET':
        return route.fulfill({ json: [{ id: 1, name: 'Alice' }] });
      case 'POST':
        return route.fulfill({ status: 201, json: { id: 2, name: 'Bob' } });
      case 'DELETE':
        return route.fulfill({ status: 204, body: '' });
      default:
        return route.continue();
    }
  });

  await page.goto('/users');
  await expect(page.getByText('Alice')).toBeVisible();
});

test('respond based on query parameters', async ({ page }) => {
  await page.route('**/api/users*', (route) => {
    const url = new URL(route.request().url());
    const role = url.searchParams.get('role');

    const allUsers = [
      { id: 1, name: 'Alice', role: 'admin' },
      { id: 2, name: 'Bob', role: 'user' },
      { id: 3, name: 'Charlie', role: 'user' },
    ];

    const filtered = role ? allUsers.filter((u) => u.role === role) : allUsers;

    return route.fulfill({ json: filtered });
  });

  await page.goto('/users?role=admin');
  await expect(page.getByText('Alice')).toBeVisible();
});

test('respond based on request body', async ({ page }) => {
  await page.route('**/api/search', (route) => {
    const body = route.request().postDataJSON();
    const query = body?.query?.toLowerCase() || '';

    const results = {
      playwright: [{ title: 'Playwright Docs' }, { title: 'Playwright GitHub' }],
      cypress: [{ title: 'Cypress Docs' }],
    };

    return route.fulfill({ json: results[query] || [] });
  });

  await page.goto('/search');
  await page.getByLabel('Search').fill('playwright');
  await page.getByRole('button', { name: 'Search' }).click();
  await expect(page.getByRole('listitem')).toHaveCount(2);
});
```

### Network Error Simulation

**Use when**: Testing how your UI handles server errors, timeouts, and connection failures. Essential for verifying error boundaries, retry logic, and degraded-mode UX.
**Avoid when**: The test is about the happy path. Only introduce errors when testing error handling.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('simulate a 500 server error', async ({ page }) => {
  await page.route('**/api/users', (route) =>
    route.fulfill({
      status: 500,
      json: { error: 'Internal Server Error' },
    })
  );

  await page.goto('/users');
  await expect(page.getByText('Something went wrong')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
});

test('simulate a 403 forbidden', async ({ page }) => {
  await page.route('**/api/admin/**', (route) =>
    route.fulfill({
      status: 403,
      json: { error: 'Forbidden', message: 'Admin access required' },
    })
  );

  await page.goto('/admin/settings');
  await expect(page.getByText('Admin access required')).toBeVisible();
});

test('simulate a 404 not found', async ({ page }) => {
  await page.route('**/api/users/999', (route) =>
    route.fulfill({
      status: 404,
      json: { error: 'User not found' },
    })
  );

  await page.goto('/users/999');
  await expect(page.getByText('User not found')).toBeVisible();
});

test('simulate a network error (connection refused)', async ({ page }) => {
  await page.route('**/api/users', (route) =>
    route.abort('connectionrefused')
  );

  await page.goto('/users');
  await expect(page.getByText('Network error')).toBeVisible();
});

test('simulate a timeout', async ({ page }) => {
  await page.route('**/api/users', async (route) => {
    // Delay longer than the app's fetch timeout to trigger a timeout error
    await new Promise((resolve) => setTimeout(resolve, 30_000));
    await route.fulfill({ json: [] });
  });

  await page.goto('/users');
  // The app should show a timeout message before the route resolves
  await expect(page.getByText('Request timed out')).toBeVisible({
    timeout: 15_000,
  });
});

test('simulate intermittent failures then recovery', async ({ page }) => {
  let requestCount = 0;

  await page.route('**/api/users', (route) => {
    requestCount++;
    if (requestCount <= 2) {
      return route.fulfill({
        status: 503,
        json: { error: 'Service Unavailable' },
      });
    }
    return route.fulfill({
      json: [{ id: 1, name: 'Alice' }],
    });
  });

  await page.goto('/users');
  await expect(page.getByText('Something went wrong')).toBeVisible();

  // Simulate user clicking retry (which makes the 3rd request)
  await page.getByRole('button', { name: 'Retry' }).click();
  await expect(page.getByText('Something went wrong')).toBeVisible();

  // Third attempt succeeds
  await page.getByRole('button', { name: 'Retry' }).click();
  await expect(page.getByText('Alice')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('simulate a 500 server error', async ({ page }) => {
  await page.route('**/api/users', (route) =>
    route.fulfill({
      status: 500,
      json: { error: 'Internal Server Error' },
    })
  );

  await page.goto('/users');
  await expect(page.getByText('Something went wrong')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
});

test('simulate a network error (connection refused)', async ({ page }) => {
  await page.route('**/api/users', (route) =>
    route.abort('connectionrefused')
  );

  await page.goto('/users');
  await expect(page.getByText('Network error')).toBeVisible();
});

test('simulate intermittent failures then recovery', async ({ page }) => {
  let requestCount = 0;

  await page.route('**/api/users', (route) => {
    requestCount++;
    if (requestCount <= 2) {
      return route.fulfill({
        status: 503,
        json: { error: 'Service Unavailable' },
      });
    }
    return route.fulfill({
      json: [{ id: 1, name: 'Alice' }],
    });
  });

  await page.goto('/users');
  await expect(page.getByText('Something went wrong')).toBeVisible();

  await page.getByRole('button', { name: 'Retry' }).click();
  await expect(page.getByText('Something went wrong')).toBeVisible();

  await page.getByRole('button', { name: 'Retry' }).click();
  await expect(page.getByText('Alice')).toBeVisible();
});
```

**Abort reasons**: `'aborted'`, `'accessdenied'`, `'addressunreachable'`, `'blockedbyclient'`, `'blockedbyresponse'`, `'connectionaborted'`, `'connectionclosed'`, `'connectionfailed'`, `'connectionrefused'`, `'connectionreset'`, `'internetdisconnected'`, `'namenotresolved'`, `'timedout'`, `'failed'`.

### Request Waiting

**Use when**: Synchronizing your test with network activity -- waiting for a request to be sent or a response to arrive before asserting on the UI.
**Avoid when**: A web-first assertion on a locator is sufficient. Only use request waiting when you need to inspect the request/response itself.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('wait for response and verify UI updates', async ({ page }) => {
  await page.goto('/users');

  // CRITICAL: set up the wait BEFORE triggering the action
  const responsePromise = page.waitForResponse('**/api/users');
  await page.getByRole('button', { name: 'Refresh' }).click();
  const response = await responsePromise;

  expect(response.status()).toBe(200);
  const users = await response.json();
  expect(users).toHaveLength(5);
});

test('wait for request and verify payload', async ({ page }) => {
  await page.goto('/users/new');

  const requestPromise = page.waitForRequest('**/api/users');
  await page.getByLabel('Name').fill('Alice');
  await page.getByLabel('Email').fill('alice@example.com');
  await page.getByRole('button', { name: 'Create' }).click();
  const request = await requestPromise;

  expect(request.method()).toBe('POST');
  expect(request.postDataJSON()).toMatchObject({
    name: 'Alice',
    email: 'alice@example.com',
  });
});

test('wait for response with predicate function', async ({ page }) => {
  await page.goto('/dashboard');

  // Wait for a specific response matching custom criteria
  const responsePromise = page.waitForResponse(
    (response) =>
      response.url().includes('/api/users') &&
      response.status() === 200 &&
      response.request().method() === 'GET'
  );
  await page.getByRole('button', { name: 'Load users' }).click();
  const response = await responsePromise;

  const data = await response.json();
  expect(data.length).toBeGreaterThan(0);
});

test('wait for multiple requests in sequence', async ({ page }) => {
  await page.goto('/checkout');

  // Wait for multiple API calls that happen during a flow
  const [validateResponse, submitResponse] = await Promise.all([
    page.waitForResponse('**/api/cart/validate'),
    page.waitForResponse('**/api/orders'),
    page.getByRole('button', { name: 'Place order' }).click(),
  ]);

  expect(validateResponse.status()).toBe(200);
  expect(submitResponse.status()).toBe(201);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('wait for response and verify UI updates', async ({ page }) => {
  await page.goto('/users');

  const responsePromise = page.waitForResponse('**/api/users');
  await page.getByRole('button', { name: 'Refresh' }).click();
  const response = await responsePromise;

  expect(response.status()).toBe(200);
  const users = await response.json();
  expect(users).toHaveLength(5);
});

test('wait for request and verify payload', async ({ page }) => {
  await page.goto('/users/new');

  const requestPromise = page.waitForRequest('**/api/users');
  await page.getByLabel('Name').fill('Alice');
  await page.getByLabel('Email').fill('alice@example.com');
  await page.getByRole('button', { name: 'Create' }).click();
  const request = await requestPromise;

  expect(request.method()).toBe('POST');
  expect(request.postDataJSON()).toMatchObject({
    name: 'Alice',
    email: 'alice@example.com',
  });
});

test('wait for multiple requests in sequence', async ({ page }) => {
  await page.goto('/checkout');

  const [validateResponse, submitResponse] = await Promise.all([
    page.waitForResponse('**/api/cart/validate'),
    page.waitForResponse('**/api/orders'),
    page.getByRole('button', { name: 'Place order' }).click(),
  ]);

  expect(validateResponse.status()).toBe(200);
  expect(submitResponse.status()).toBe(201);
});
```

### Glob Patterns and URL Matching

**Use when**: You need to match URLs with wildcards, partial paths, or regex. Every `page.route()`, `waitForRequest()`, and `waitForResponse()` accepts glob patterns, strings, or regex.
**Avoid when**: The URL is known and static. Use the exact string.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('glob pattern examples', async ({ page }) => {
  // ** matches any path segments (including nested)
  await page.route('**/api/users', (route) =>
    route.fulfill({ json: [] })
  );
  // Matches: https://example.com/api/users
  // Matches: https://example.com/v2/api/users

  // * matches any single path segment
  await page.route('**/api/users/*/orders', (route) =>
    route.fulfill({ json: [] })
  );
  // Matches: /api/users/123/orders
  // Matches: /api/users/abc/orders
  // Does NOT match: /api/users/123/456/orders

  // Match file extensions
  await page.route('**/*.{png,jpg,svg}', (route) => route.abort());
  // Matches: /images/logo.png, /assets/photo.jpg

  // Match query strings with *
  await page.route('**/api/search?q=*', (route) =>
    route.fulfill({ json: [] })
  );
  // Matches: /api/search?q=anything

  // Use regex for complex patterns
  await page.route(/\/api\/users\/\d+$/, (route) =>
    route.fulfill({ json: { id: 1, name: 'Alice' } })
  );
  // Matches: /api/users/123, /api/users/456
  // Does NOT match: /api/users/abc, /api/users/123/orders

  // Regex with captured groups for dynamic responses
  await page.route(/\/api\/users\/(\d+)/, (route) => {
    const match = route.request().url().match(/\/api\/users\/(\d+)/);
    const userId = match ? match[1] : '0';
    return route.fulfill({
      json: { id: parseInt(userId), name: `User ${userId}` },
    });
  });

  await page.goto('/users');
});

test('match all requests on a domain', async ({ page }) => {
  // Block everything from a specific domain
  await page.route('https://analytics.example.com/**', (route) =>
    route.abort()
  );

  await page.goto('/dashboard');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('glob pattern examples', async ({ page }) => {
  // ** matches any path segments
  await page.route('**/api/users', (route) =>
    route.fulfill({ json: [] })
  );

  // * matches a single path segment
  await page.route('**/api/users/*/orders', (route) =>
    route.fulfill({ json: [] })
  );

  // Match file extensions
  await page.route('**/*.{png,jpg,svg}', (route) => route.abort());

  // Regex for complex patterns
  await page.route(/\/api\/users\/\d+$/, (route) =>
    route.fulfill({ json: { id: 1, name: 'Alice' } })
  );

  // Regex with dynamic responses
  await page.route(/\/api\/users\/(\d+)/, (route) => {
    const match = route.request().url().match(/\/api\/users\/(\d+)/);
    const userId = match ? match[1] : '0';
    return route.fulfill({
      json: { id: parseInt(userId), name: `User ${userId}` },
    });
  });

  await page.goto('/users');
});

test('match all requests on a domain', async ({ page }) => {
  await page.route('https://analytics.example.com/**', (route) =>
    route.abort()
  );

  await page.goto('/dashboard');
});
```

**Pattern reference**:

| Pattern | Matches | Does Not Match |
|---|---|---|
| `**/api/users` | `/api/users`, `/v2/api/users` | `/api/users/1` |
| `**/api/users*` | `/api/users`, `/api/users?page=1` | `/api/users/1` |
| `**/api/users/**` | `/api/users/1`, `/api/users/1/orders` | `/api/users` |
| `**/api/users/*/orders` | `/api/users/1/orders` | `/api/users/1/2/orders` |
| `**/*.{png,jpg}` | `/logo.png`, `/deep/path/img.jpg` | `/file.svg` |
| `/\/api\/users\/\d+$/` (regex) | `/api/users/123` | `/api/users/abc` |

## Decision Guide

| Scenario | Use | Why |
|---|---|---|
| Frontend depends on an external API | `route.fulfill()` | Deterministic data, no external dependency, fast |
| Need to test real API but tweak one field | `route.fetch()` + modify + `route.fulfill()` | Uses real data as baseline, only overrides what you need |
| Testing happy path with real backend | `route.continue()` (or no route) | Full integration coverage |
| Block analytics/ads/third-party noise | `route.abort()` | Faster tests, no flakiness from external services |
| Complex API with many endpoints | `page.routeFromHAR()` with `update: true` | Record once, replay forever; minimal test code |
| Testing error handling (500, timeout) | `route.fulfill({ status: 500 })` or `route.abort('timedout')` | Simulate errors deterministically |
| Verify request payload sent by frontend | `page.waitForRequest()` + assertions | Confirms frontend sends correct data |
| Verify response data before UI check | `page.waitForResponse()` + assertions | Confirms data arrives before asserting on DOM |
| Multiple tests need the same mock | `context.route()` or fixture | Share routes across tests without repetition |
| Testing loading spinners / skeleton UI | `route.fulfill()` with a delay (via `setTimeout`) | Control exact timing of response |
| Paginated or search-based API | Conditional mock (check query params / body) | Dynamic responses based on request content |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Mocking your own app's pages and static assets | You end up testing a fake app, not your real one | Only mock API/data endpoints, never HTML/JS/CSS served by your app |
| Hardcoding mock data inline in every test | Duplicated data, hard to update when API changes | Extract mock data into shared fixtures (`tests/data/users.json`) |
| Never updating mocks when the API changes | Tests pass against stale data; real app breaks | Use HAR recording with periodic `update: true` runs, or validate mock shapes against OpenAPI schemas |
| Mocking in production-like E2E tests | You lose integration confidence | Keep a separate test suite with real backends for smoke/integration tests; mock only in component and isolated UI tests |
| Forgetting to call `route.fulfill()`, `route.continue()`, or `route.abort()` | Request hangs, test times out with a confusing error | Every route handler must call exactly one of the three |
| Setting up routes after `page.goto()` | Requests fire during navigation before the route is registered | Always call `page.route()` before `page.goto()` |
| Using `waitForResponse` after the triggering action | Race condition: response may arrive before the wait is registered | Always set up the promise before the action: `const p = page.waitForResponse(...); await click(); await p;` |
| Mocking with `route.continue()` and thinking it mocks | `route.continue()` passes the request to the real server | Use `route.fulfill()` to return fake data |
| Over-broad glob patterns (`**/*`) without filtering | Catches all requests including HTML, JS, CSS; breaks the app | Be specific: `**/api/**` or filter by `resourceType()` |
| Forgetting `await` on route setup or fulfillment | Route may not be active when navigation starts | Always `await page.route(...)` and `await route.fulfill(...)` |
| Not calling `page.unroute()` when swapping mocks mid-test | Old route handler still fires, new one is ignored or both fire | Call `page.unroute()` before registering a new handler for the same pattern |
| Using `page.on('request')` for mocking | Event listeners are read-only; they cannot modify or fulfill requests | Use `page.route()` for interception; `page.on('request')` only for logging |

## Troubleshooting

### Route handler never fires

**Cause**: The URL pattern does not match the actual request URL. Common when the base URL includes a port number, path prefix, or the request uses a different protocol.

**Fix**:
- Log all requests to find the exact URL:
```typescript
page.on('request', (req) => console.log(req.method(), req.url()));
```
- Ensure glob pattern matches. `**/api/users` does not match `http://localhost:3000/api/users?page=1` -- use `**/api/users*` to include query strings.
- Check that `page.route()` is called before `page.goto()`.

### Route handler fires but test still times out

**Cause**: The handler throws an error or never calls `fulfill`/`continue`/`abort`.

**Fix**:
- Add error handling inside the route handler.
- Ensure every code path in the handler ends with one of the three resolution methods.
```typescript
await page.route('**/api/users', async (route) => {
  try {
    const data = getTestData(); // this might throw
    await route.fulfill({ json: data });
  } catch (error) {
    console.error('Route handler error:', error);
    await route.abort();
  }
});
```

### Mocked response is ignored -- app shows real data

**Cause**: The route is registered at the page level but the request is made by a service worker or a different browser context.

**Fix**:
- Use `context.route()` instead of `page.route()` to cover all pages and service workers.
- Disable service workers in the config if they interfere:
```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    serviceWorkers: 'block',
  },
});
```

### `route.fetch()` causes infinite loop

**Cause**: `route.fetch()` re-issues the request, which can re-trigger the same route handler if the URL pattern matches.

**Fix**: Playwright handles this correctly for the same route handler -- `route.fetch()` will not re-enter the handler that called it. But if you have multiple overlapping route handlers, they can interfere. Simplify to a single handler per URL pattern, or use `route.fetch({ url: 'different-url' })` to redirect.

### HAR replay returns wrong responses

**Cause**: HAR files match requests by URL and sometimes by POST body. If the request body changes (e.g., timestamps, CSRF tokens), the match fails.

**Fix**:
- Re-record the HAR file with `update: true`.
- Use `notFound: 'fallback'` to let unmatched requests hit the real server.
- For POST requests with dynamic bodies, consider using `page.route()` with manual matching instead of HAR.

## Related

- [core/when-to-mock.md](when-to-mock.md) -- decision framework for when to mock vs use real services
- [core/api-testing.md](api-testing.md) -- testing REST and GraphQL APIs directly (without a browser)
- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- web-first assertions and `waitForResponse` patterns
- [core/authentication.md](authentication.md) -- mocking auth tokens and session state
- [core/error-and-edge-cases.md](error-and-edge-cases.md) -- error state testing patterns beyond network errors
- [core/service-workers-and-pwa.md](service-workers-and-pwa.md) -- handling service worker caching that interferes with mocks
