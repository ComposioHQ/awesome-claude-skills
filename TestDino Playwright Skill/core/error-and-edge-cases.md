# Error States and Edge Cases

> **When to use**: Testing how your application handles errors, failures, boundary conditions, and unusual user behavior. These tests catch bugs that happy-path tests miss.
> **Prerequisites**: [core/assertions-and-waiting.md](assertions-and-waiting.md), [core/network-mocking.md](network-mocking.md) for route interception

## Quick Reference

```typescript
// Mock a 500 server error
await page.route('**/api/data', (route) => route.fulfill({ status: 500 }));

// Simulate offline mode
await page.context().setOffline(true);

// Test empty state
await page.route('**/api/items', (route) =>
  route.fulfill({ status: 200, json: [] })
);

// Browser back/forward
await page.goBack();
await page.goForward();

// Abort a network request (simulate network failure)
await page.route('**/api/save', (route) => route.abort('connectionfailed'));
```

## Patterns

### HTTP Error Status Codes

**Use when**: Testing that your application displays appropriate error pages or messages for 4xx and 5xx responses.
**Avoid when**: The error is handled silently (no user-facing feedback). Test via API or logs instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('displays 404 page for missing resources', async ({ page }) => {
  // Navigate directly to a non-existent URL
  await page.goto('/this-page-does-not-exist');

  await expect(page.getByRole('heading', { name: /not found/i })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Go home' })).toBeVisible();
});

test('handles 500 server error gracefully', async ({ page }) => {
  // Intercept the API call and return a 500
  await page.route('**/api/dashboard', (route) =>
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal server error' }),
    })
  );

  await page.goto('/dashboard');

  await expect(page.getByText('Something went wrong')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Try again' })).toBeVisible();
});

test('handles 403 forbidden with redirect to login', async ({ page }) => {
  await page.route('**/api/admin/**', (route) =>
    route.fulfill({ status: 403 })
  );

  await page.goto('/admin/settings');

  // Should redirect to login or show access denied
  await expect(page.getByText(/access denied|not authorized/i)).toBeVisible();
});

test('handles 429 rate limiting', async ({ page }) => {
  await page.route('**/api/search*', (route) =>
    route.fulfill({
      status: 429,
      headers: { 'Retry-After': '30' },
      body: JSON.stringify({ error: 'Too many requests' }),
    })
  );

  await page.goto('/search');
  await page.getByLabel('Search').fill('test');
  await page.getByRole('button', { name: 'Search' }).click();

  await expect(page.getByText(/too many requests|try again later/i)).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('displays 404 page for missing resources', async ({ page }) => {
  await page.goto('/this-page-does-not-exist');

  await expect(page.getByRole('heading', { name: /not found/i })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Go home' })).toBeVisible();
});

test('handles 500 server error gracefully', async ({ page }) => {
  await page.route('**/api/dashboard', (route) =>
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal server error' }),
    })
  );

  await page.goto('/dashboard');

  await expect(page.getByText('Something went wrong')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Try again' })).toBeVisible();
});

test('handles 403 forbidden with redirect to login', async ({ page }) => {
  await page.route('**/api/admin/**', (route) =>
    route.fulfill({ status: 403 })
  );

  await page.goto('/admin/settings');
  await expect(page.getByText(/access denied|not authorized/i)).toBeVisible();
});

test('handles 429 rate limiting', async ({ page }) => {
  await page.route('**/api/search*', (route) =>
    route.fulfill({
      status: 429,
      headers: { 'Retry-After': '30' },
      body: JSON.stringify({ error: 'Too many requests' }),
    })
  );

  await page.goto('/search');
  await page.getByLabel('Search').fill('test');
  await page.getByRole('button', { name: 'Search' }).click();

  await expect(page.getByText(/too many requests|try again later/i)).toBeVisible();
});
```

### Network Failure and Offline Mode

**Use when**: Testing how the app behaves when the network is down, requests fail, or the connection is intermittent.
**Avoid when**: The app has no offline or error handling behavior to test.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('offline mode shows offline banner', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  // Go offline
  await page.context().setOffline(true);

  // Trigger a network-dependent action
  await page.getByRole('button', { name: 'Refresh' }).click();

  await expect(page.getByText(/offline|no connection/i)).toBeVisible();

  // Go back online
  await page.context().setOffline(false);

  await page.getByRole('button', { name: 'Refresh' }).click();
  await expect(page.getByText(/offline|no connection/i)).not.toBeVisible();
});

test('network request failure shows error state', async ({ page }) => {
  // Abort specific requests to simulate network failure
  await page.route('**/api/user/profile', (route) =>
    route.abort('connectionfailed')
  );

  await page.goto('/profile');

  await expect(page.getByText('Failed to load profile')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
});

test('request timeout shows timeout message', async ({ page }) => {
  // Delay the response beyond the app's timeout threshold
  await page.route('**/api/reports', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 30_000));
    await route.fulfill({ status: 200, json: { data: [] } });
  });

  await page.goto('/reports');

  // App should show timeout message before Playwright's own timeout
  await expect(page.getByText(/timed out|taking too long/i)).toBeVisible({
    timeout: 20_000,
  });
});

test('intermittent connectivity — request fails then succeeds', async ({ page }) => {
  let requestCount = 0;

  await page.route('**/api/data', (route) => {
    requestCount++;
    if (requestCount <= 2) {
      return route.abort('connectionfailed');
    }
    return route.fulfill({ status: 200, json: { items: ['a', 'b', 'c'] } });
  });

  await page.goto('/data');

  // First load fails
  await expect(page.getByText(/failed|error/i)).toBeVisible();

  // User retries — still fails
  await page.getByRole('button', { name: 'Retry' }).click();
  await expect(page.getByText(/failed|error/i)).toBeVisible();

  // Third attempt succeeds
  await page.getByRole('button', { name: 'Retry' }).click();
  await expect(page.getByRole('listitem')).toHaveCount(3);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('offline mode shows offline banner', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  await page.context().setOffline(true);

  await page.getByRole('button', { name: 'Refresh' }).click();
  await expect(page.getByText(/offline|no connection/i)).toBeVisible();

  await page.context().setOffline(false);

  await page.getByRole('button', { name: 'Refresh' }).click();
  await expect(page.getByText(/offline|no connection/i)).not.toBeVisible();
});

test('network request failure shows error state', async ({ page }) => {
  await page.route('**/api/user/profile', (route) =>
    route.abort('connectionfailed')
  );

  await page.goto('/profile');

  await expect(page.getByText('Failed to load profile')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
});

test('intermittent connectivity — request fails then succeeds', async ({ page }) => {
  let requestCount = 0;

  await page.route('**/api/data', (route) => {
    requestCount++;
    if (requestCount <= 2) {
      return route.abort('connectionfailed');
    }
    return route.fulfill({ status: 200, json: { items: ['a', 'b', 'c'] } });
  });

  await page.goto('/data');

  await expect(page.getByText(/failed|error/i)).toBeVisible();

  await page.getByRole('button', { name: 'Retry' }).click();
  await expect(page.getByText(/failed|error/i)).toBeVisible();

  await page.getByRole('button', { name: 'Retry' }).click();
  await expect(page.getByRole('listitem')).toHaveCount(3);
});
```

### Empty States and Boundary Testing

**Use when**: Testing what the UI shows when there is no data, when inputs are at their minimum or maximum values, or when inputs contain special characters.
**Avoid when**: Never. Every feature should have empty state and boundary tests.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('empty state is shown when no items exist', async ({ page }) => {
  // Mock an empty response
  await page.route('**/api/tasks', (route) =>
    route.fulfill({ status: 200, json: [] })
  );

  await page.goto('/tasks');

  await expect(page.getByText('No tasks yet')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Create your first task' })).toBeVisible();

  // List elements should not be present
  await expect(page.getByRole('listitem')).toHaveCount(0);
});

test('handles maximum length input', async ({ page }) => {
  await page.goto('/profile');

  // Fill with max-length string
  const maxLengthName = 'A'.repeat(255);
  await page.getByLabel('Display name').fill(maxLengthName);
  await page.getByRole('button', { name: 'Save' }).click();

  // Verify the name was saved (or truncated, depending on app behavior)
  await expect(page.getByText('Profile updated')).toBeVisible();
});

test('handles special characters in input', async ({ page }) => {
  await page.goto('/search');

  const specialInputs = [
    '<script>alert("xss")</script>',
    '"; DROP TABLE users; --',
    'unicode: \u00e9\u00e0\u00fc\u00f1 \u4f60\u597d \ud83d\ude80',
    'null bytes: \x00\x01\x02',
    'path traversal: ../../etc/passwd',
  ];

  for (const input of specialInputs) {
    await page.getByLabel('Search').fill(input);
    await page.getByRole('button', { name: 'Search' }).click();

    // App should not crash — either show results or "no results"
    await expect(
      page.getByText(/results|no results|no matches/i)
    ).toBeVisible();
  }
});

test('handles zero, one, and many items (0-1-N pattern)', async ({ page }) => {
  // Zero items
  await page.route('**/api/notifications', (route) =>
    route.fulfill({ status: 200, json: [] })
  );
  await page.goto('/notifications');
  await expect(page.getByText('No notifications')).toBeVisible();

  // One item
  await page.route('**/api/notifications', (route) =>
    route.fulfill({
      status: 200,
      json: [{ id: 1, message: 'Welcome!' }],
    })
  );
  await page.reload();
  await expect(page.getByRole('listitem')).toHaveCount(1);
  await expect(page.getByText('No notifications')).not.toBeVisible();

  // Many items — verify pagination or "load more"
  await page.route('**/api/notifications', (route) =>
    route.fulfill({
      status: 200,
      json: Array.from({ length: 50 }, (_, i) => ({
        id: i + 1,
        message: `Notification ${i + 1}`,
      })),
    })
  );
  await page.reload();
  await expect(page.getByRole('listitem').first()).toBeVisible();
  await expect(page.getByRole('button', { name: /load more|show all/i })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('empty state is shown when no items exist', async ({ page }) => {
  await page.route('**/api/tasks', (route) =>
    route.fulfill({ status: 200, json: [] })
  );

  await page.goto('/tasks');

  await expect(page.getByText('No tasks yet')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Create your first task' })).toBeVisible();
  await expect(page.getByRole('listitem')).toHaveCount(0);
});

test('handles maximum length input', async ({ page }) => {
  await page.goto('/profile');

  const maxLengthName = 'A'.repeat(255);
  await page.getByLabel('Display name').fill(maxLengthName);
  await page.getByRole('button', { name: 'Save' }).click();

  await expect(page.getByText('Profile updated')).toBeVisible();
});

test('handles special characters in input', async ({ page }) => {
  await page.goto('/search');

  const specialInputs = [
    '<script>alert("xss")</script>',
    '"; DROP TABLE users; --',
    'unicode: \u00e9\u00e0\u00fc\u00f1 \u4f60\u597d \ud83d\ude80',
    'path traversal: ../../etc/passwd',
  ];

  for (const input of specialInputs) {
    await page.getByLabel('Search').fill(input);
    await page.getByRole('button', { name: 'Search' }).click();

    await expect(
      page.getByText(/results|no results|no matches/i)
    ).toBeVisible();
  }
});

test('handles zero, one, and many items (0-1-N pattern)', async ({ page }) => {
  await page.route('**/api/notifications', (route) =>
    route.fulfill({ status: 200, json: [] })
  );
  await page.goto('/notifications');
  await expect(page.getByText('No notifications')).toBeVisible();

  await page.route('**/api/notifications', (route) =>
    route.fulfill({
      status: 200,
      json: [{ id: 1, message: 'Welcome!' }],
    })
  );
  await page.reload();
  await expect(page.getByRole('listitem')).toHaveCount(1);

  await page.route('**/api/notifications', (route) =>
    route.fulfill({
      status: 200,
      json: Array.from({ length: 50 }, (_, i) => ({
        id: i + 1,
        message: `Notification ${i + 1}`,
      })),
    })
  );
  await page.reload();
  await expect(page.getByRole('listitem').first()).toBeVisible();
  await expect(page.getByRole('button', { name: /load more|show all/i })).toBeVisible();
});
```

### Loading States and Skeletons

**Use when**: Verifying that loading indicators, skeleton screens, or spinners appear during data fetching and disappear when data arrives.
**Avoid when**: The application renders synchronously with no loading indicators (SSR without client-side fetching).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('loading skeleton appears and resolves', async ({ page }) => {
  // Delay the API response to observe the loading state
  let resolveResponse: () => void;
  const responseReady = new Promise<void>((resolve) => {
    resolveResponse = resolve;
  });

  await page.route('**/api/dashboard', async (route) => {
    await responseReady;
    await route.fulfill({
      status: 200,
      json: { revenue: 12400, users: 350 },
    });
  });

  await page.goto('/dashboard');

  // Skeleton should be visible while loading
  await expect(page.getByTestId('skeleton-revenue')).toBeVisible();
  await expect(page.getByTestId('skeleton-users')).toBeVisible();

  // Real content should not be visible yet
  await expect(page.getByText('$12,400')).not.toBeVisible();

  // Release the response
  resolveResponse!();

  // Skeleton disappears, real content appears
  await expect(page.getByTestId('skeleton-revenue')).not.toBeVisible();
  await expect(page.getByText('$12,400')).toBeVisible();
  await expect(page.getByText('350')).toBeVisible();
});

test('spinner shown during form submission', async ({ page }) => {
  let resolveSubmit: () => void;
  const submitReady = new Promise<void>((resolve) => {
    resolveSubmit = resolve;
  });

  await page.route('**/api/contact', async (route) => {
    await submitReady;
    await route.fulfill({ status: 200, json: { success: true } });
  });

  await page.goto('/contact');
  await page.getByLabel('Name').fill('Jane');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Message').fill('Test');

  await page.getByRole('button', { name: 'Send' }).click();

  // Loading spinner/state during submission
  await expect(page.getByRole('button', { name: /sending/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /sending/i })).toBeDisabled();

  // Complete the submission
  resolveSubmit!();

  await expect(page.getByText('Message sent')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('loading skeleton appears and resolves', async ({ page }) => {
  let resolveResponse;
  const responseReady = new Promise((resolve) => {
    resolveResponse = resolve;
  });

  await page.route('**/api/dashboard', async (route) => {
    await responseReady;
    await route.fulfill({
      status: 200,
      json: { revenue: 12400, users: 350 },
    });
  });

  await page.goto('/dashboard');

  await expect(page.getByTestId('skeleton-revenue')).toBeVisible();
  await expect(page.getByTestId('skeleton-users')).toBeVisible();
  await expect(page.getByText('$12,400')).not.toBeVisible();

  resolveResponse();

  await expect(page.getByTestId('skeleton-revenue')).not.toBeVisible();
  await expect(page.getByText('$12,400')).toBeVisible();
  await expect(page.getByText('350')).toBeVisible();
});

test('spinner shown during form submission', async ({ page }) => {
  let resolveSubmit;
  const submitReady = new Promise((resolve) => {
    resolveSubmit = resolve;
  });

  await page.route('**/api/contact', async (route) => {
    await submitReady;
    await route.fulfill({ status: 200, json: { success: true } });
  });

  await page.goto('/contact');
  await page.getByLabel('Name').fill('Jane');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Message').fill('Test');

  await page.getByRole('button', { name: 'Send' }).click();

  await expect(page.getByRole('button', { name: /sending/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /sending/i })).toBeDisabled();

  resolveSubmit();

  await expect(page.getByText('Message sent')).toBeVisible();
});
```

### Retry Behavior Testing

**Use when**: Testing that the application retries failed requests automatically or via a user-triggered "retry" button.
**Avoid when**: The application has no retry mechanism.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('retry button recovers from a failed API call', async ({ page }) => {
  let callCount = 0;

  await page.route('**/api/feed', (route) => {
    callCount++;
    if (callCount === 1) {
      return route.fulfill({ status: 500 });
    }
    return route.fulfill({
      status: 200,
      json: { posts: [{ id: 1, title: 'Hello World' }] },
    });
  });

  await page.goto('/feed');

  // First load fails
  await expect(page.getByText(/something went wrong/i)).toBeVisible();

  // Click retry — second call succeeds
  await page.getByRole('button', { name: 'Try again' }).click();

  await expect(page.getByText('Hello World')).toBeVisible();
  expect(callCount).toBe(2);
});

test('automatic retry with exponential backoff', async ({ page }) => {
  const callTimestamps: number[] = [];

  await page.route('**/api/status', (route) => {
    callTimestamps.push(Date.now());
    if (callTimestamps.length <= 3) {
      return route.fulfill({ status: 503 });
    }
    return route.fulfill({ status: 200, json: { status: 'ok' } });
  });

  await page.goto('/status');

  // Wait for the auto-retry to eventually succeed
  await expect(page.getByText('System operational')).toBeVisible({
    timeout: 30_000,
  });

  // Verify multiple retry attempts were made
  expect(callTimestamps.length).toBeGreaterThanOrEqual(4);

  // Verify backoff: gaps between retries should increase
  if (callTimestamps.length >= 3) {
    const gap1 = callTimestamps[1] - callTimestamps[0];
    const gap2 = callTimestamps[2] - callTimestamps[1];
    expect(gap2).toBeGreaterThanOrEqual(gap1);
  }
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('retry button recovers from a failed API call', async ({ page }) => {
  let callCount = 0;

  await page.route('**/api/feed', (route) => {
    callCount++;
    if (callCount === 1) {
      return route.fulfill({ status: 500 });
    }
    return route.fulfill({
      status: 200,
      json: { posts: [{ id: 1, title: 'Hello World' }] },
    });
  });

  await page.goto('/feed');

  await expect(page.getByText(/something went wrong/i)).toBeVisible();

  await page.getByRole('button', { name: 'Try again' }).click();

  await expect(page.getByText('Hello World')).toBeVisible();
  expect(callCount).toBe(2);
});

test('automatic retry with exponential backoff', async ({ page }) => {
  const callTimestamps = [];

  await page.route('**/api/status', (route) => {
    callTimestamps.push(Date.now());
    if (callTimestamps.length <= 3) {
      return route.fulfill({ status: 503 });
    }
    return route.fulfill({ status: 200, json: { status: 'ok' } });
  });

  await page.goto('/status');

  await expect(page.getByText('System operational')).toBeVisible({
    timeout: 30_000,
  });

  expect(callTimestamps.length).toBeGreaterThanOrEqual(4);
});
```

### Browser Back/Forward Navigation

**Use when**: Testing that the application handles browser history navigation correctly — preserving state, URL updates, and content after going back or forward.
**Avoid when**: The app is a single-page application that does not use the browser history API. Focus on client-side routing tests instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('browser back preserves navigation context', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('link', { name: 'Running Shoes' }).click();
  await page.waitForURL('**/products/running-shoes');

  // Go back
  await page.goBack();

  await expect(page).toHaveURL(/\/products$/);
  await expect(page.getByRole('heading', { name: 'Products' })).toBeVisible();
});

test('browser forward returns to previous page', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('link', { name: 'Running Shoes' }).click();
  await page.waitForURL('**/products/running-shoes');

  await page.goBack();
  await page.goForward();

  await expect(page).toHaveURL(/\/products\/running-shoes/);
  await expect(page.getByRole('heading', { name: 'Running Shoes' })).toBeVisible();
});

test('form state after browser back', async ({ page }) => {
  await page.goto('/checkout');

  // Fill form on step 1
  await page.getByLabel('Address').fill('123 Main St');
  await page.getByRole('button', { name: 'Continue' }).click();

  // Arrived at step 2
  await expect(page.getByRole('heading', { name: 'Payment' })).toBeVisible();

  // Go back to step 1
  await page.goBack();

  // Data should be preserved (depends on app implementation)
  await expect(page.getByLabel('Address')).toHaveValue('123 Main St');
});

test('back button after form submission does not re-submit', async ({ page }) => {
  await page.goto('/contact');

  await page.getByLabel('Name').fill('Jane');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Message').fill('Test');
  await page.getByRole('button', { name: 'Send' }).click();

  await expect(page.getByText('Message sent')).toBeVisible();

  // Going back should show the form, not re-submit
  await page.goBack();
  await expect(page.getByLabel('Name')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('browser back preserves navigation context', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('link', { name: 'Running Shoes' }).click();
  await page.waitForURL('**/products/running-shoes');

  await page.goBack();

  await expect(page).toHaveURL(/\/products$/);
  await expect(page.getByRole('heading', { name: 'Products' })).toBeVisible();
});

test('browser forward returns to previous page', async ({ page }) => {
  await page.goto('/products');
  await page.getByRole('link', { name: 'Running Shoes' }).click();
  await page.waitForURL('**/products/running-shoes');

  await page.goBack();
  await page.goForward();

  await expect(page).toHaveURL(/\/products\/running-shoes/);
  await expect(page.getByRole('heading', { name: 'Running Shoes' })).toBeVisible();
});

test('form state after browser back', async ({ page }) => {
  await page.goto('/checkout');

  await page.getByLabel('Address').fill('123 Main St');
  await page.getByRole('button', { name: 'Continue' }).click();

  await expect(page.getByRole('heading', { name: 'Payment' })).toBeVisible();

  await page.goBack();
  await expect(page.getByLabel('Address')).toHaveValue('123 Main St');
});

test('back button after form submission does not re-submit', async ({ page }) => {
  await page.goto('/contact');

  await page.getByLabel('Name').fill('Jane');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByLabel('Message').fill('Test');
  await page.getByRole('button', { name: 'Send' }).click();

  await expect(page.getByText('Message sent')).toBeVisible();

  await page.goBack();
  await expect(page.getByLabel('Name')).toBeVisible();
});
```

### Concurrent User Actions

**Use when**: Testing that rapid user interactions do not cause race conditions — double-clicking submit, typing while data is loading, navigating during an async operation.
**Avoid when**: The UI has no async operations that could conflict with user actions.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('double-click submit does not create duplicate entries', async ({ page }) => {
  const requests: string[] = [];

  await page.route('**/api/orders', (route) => {
    requests.push(route.request().method());
    return route.fulfill({
      status: 201,
      json: { id: 1, status: 'created' },
    });
  });

  await page.goto('/checkout');
  await page.getByLabel('Item').fill('Widget');

  const submitButton = page.getByRole('button', { name: 'Place order' });

  // Rapid double-click
  await submitButton.dblclick();

  // Wait for the result
  await expect(page.getByText('Order confirmed')).toBeVisible();

  // The app should prevent duplicate submissions
  // (button disabled after first click, or server deduplication)
  expect(requests.filter((m) => m === 'POST').length).toBeLessThanOrEqual(1);
});

test('typing during navigation does not crash', async ({ page }) => {
  await page.goto('/search');

  // Start typing and immediately navigate
  await page.getByLabel('Search').pressSequentially('test query', { delay: 30 });
  await page.getByRole('link', { name: 'Home' }).click();

  // Should arrive at home page without errors
  await page.waitForURL('**/');
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
});

test('rapid filter changes use latest value', async ({ page }) => {
  const requestUrls: string[] = [];

  await page.route('**/api/products*', (route) => {
    requestUrls.push(route.request().url());
    return route.fulfill({
      status: 200,
      json: { products: [{ name: 'Latest result' }] },
    });
  });

  await page.goto('/products');

  // Rapidly change the filter
  await page.getByLabel('Category').selectOption('electronics');
  await page.getByLabel('Category').selectOption('clothing');
  await page.getByLabel('Category').selectOption('books');

  // Wait for the final result
  await expect(page.getByText('Latest result')).toBeVisible();

  // The UI should show results for "books", not an earlier selection
  // Some apps debounce; some cancel in-flight requests
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('double-click submit does not create duplicate entries', async ({ page }) => {
  const requests = [];

  await page.route('**/api/orders', (route) => {
    requests.push(route.request().method());
    return route.fulfill({
      status: 201,
      json: { id: 1, status: 'created' },
    });
  });

  await page.goto('/checkout');
  await page.getByLabel('Item').fill('Widget');

  const submitButton = page.getByRole('button', { name: 'Place order' });
  await submitButton.dblclick();

  await expect(page.getByText('Order confirmed')).toBeVisible();

  expect(requests.filter((m) => m === 'POST').length).toBeLessThanOrEqual(1);
});

test('typing during navigation does not crash', async ({ page }) => {
  await page.goto('/search');

  await page.getByLabel('Search').pressSequentially('test query', { delay: 30 });
  await page.getByRole('link', { name: 'Home' }).click();

  await page.waitForURL('**/');
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
});

test('rapid filter changes use latest value', async ({ page }) => {
  const requestUrls = [];

  await page.route('**/api/products*', (route) => {
    requestUrls.push(route.request().url());
    return route.fulfill({
      status: 200,
      json: { products: [{ name: 'Latest result' }] },
    });
  });

  await page.goto('/products');

  await page.getByLabel('Category').selectOption('electronics');
  await page.getByLabel('Category').selectOption('clothing');
  await page.getByLabel('Category').selectOption('books');

  await expect(page.getByText('Latest result')).toBeVisible();
});
```

### Graceful Degradation

**Use when**: Testing that the app continues to function when non-critical services fail (analytics, chat widget, recommendations).
**Avoid when**: The failing service is critical to the core workflow.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('page works when analytics service fails', async ({ page }) => {
  // Block analytics and tracking scripts
  await page.route('**/analytics/**', (route) => route.abort());
  await page.route('**/tracking/**', (route) => route.abort());

  await page.goto('/products');

  // Core functionality still works
  await expect(page.getByRole('heading', { name: 'Products' })).toBeVisible();
  await page.getByRole('link', { name: 'Running Shoes' }).click();
  await expect(page.getByRole('button', { name: 'Add to cart' })).toBeEnabled();
});

test('page works when recommendation engine fails', async ({ page }) => {
  await page.route('**/api/recommendations', (route) =>
    route.fulfill({ status: 500 })
  );

  await page.goto('/products/running-shoes');

  // Main product content loads
  await expect(page.getByRole('heading', { name: 'Running Shoes' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Add to cart' })).toBeEnabled();

  // Recommendations section shows fallback
  await expect(
    page.getByText(/recommendations unavailable|you may also like/i)
  ).toBeVisible();
});

test('page works when third-party chat widget fails to load', async ({ page }) => {
  // Block the chat widget script
  await page.route('**/chat-widget.js', (route) => route.abort());

  await page.goto('/support');

  // Core support page loads
  await expect(page.getByRole('heading', { name: 'Help Center' })).toBeVisible();

  // No console errors from the blocked widget should crash the page
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));

  // Navigate around to ensure no cascade failures
  await page.getByRole('link', { name: 'FAQ' }).click();
  await expect(page.getByRole('heading', { name: 'FAQ' })).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('page works when analytics service fails', async ({ page }) => {
  await page.route('**/analytics/**', (route) => route.abort());
  await page.route('**/tracking/**', (route) => route.abort());

  await page.goto('/products');

  await expect(page.getByRole('heading', { name: 'Products' })).toBeVisible();
  await page.getByRole('link', { name: 'Running Shoes' }).click();
  await expect(page.getByRole('button', { name: 'Add to cart' })).toBeEnabled();
});

test('page works when recommendation engine fails', async ({ page }) => {
  await page.route('**/api/recommendations', (route) =>
    route.fulfill({ status: 500 })
  );

  await page.goto('/products/running-shoes');

  await expect(page.getByRole('heading', { name: 'Running Shoes' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Add to cart' })).toBeEnabled();
});

test('page works when third-party chat widget fails to load', async ({ page }) => {
  await page.route('**/chat-widget.js', (route) => route.abort());

  await page.goto('/support');

  await expect(page.getByRole('heading', { name: 'Help Center' })).toBeVisible();

  await page.getByRole('link', { name: 'FAQ' }).click();
  await expect(page.getByRole('heading', { name: 'FAQ' })).toBeVisible();
});
```

## Decision Guide

| Scenario | Approach | Key API |
|---|---|---|
| 404 page | Navigate to non-existent URL, assert error page | `page.goto('/nonexistent')` |
| 500 server error | Mock route with `status: 500` | `page.route(url, route => route.fulfill({ status: 500 }))` |
| Network failure | Abort the route | `route.abort('connectionfailed')` |
| Offline mode | Toggle offline on the browser context | `page.context().setOffline(true)` |
| Slow response | Delay route fulfillment with a Promise | `await new Promise(r => setTimeout(r, delay))` in route handler |
| Empty state | Mock API to return empty array | `route.fulfill({ json: [] })` |
| Boundary values | Fill inputs with min/max/special values | `locator.fill('A'.repeat(255))` |
| Loading skeleton | Delay route, assert skeleton visible, release, assert content | Promise-based route handler |
| Retry behavior | Track route call count, fail first N, succeed after | Counter in route handler |
| Browser history | Use `page.goBack()` and `page.goForward()` | Assert URL and content after navigation |
| Double submit | `dblclick()` on submit, verify single POST | Track requests in route handler |
| Third-party failure | Abort non-critical routes, verify core works | `route.abort()` on optional services |
| Console error monitoring | Listen for `pageerror` event | `page.on('pageerror', handler)` |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Only testing the happy path | Real users hit errors. Errors in production are more expensive than test time. | Add error/edge case tests for every feature |
| `page.route('**/*', route => route.abort())` | Blocks ALL requests including the page itself | Target specific URLs: `page.route('**/api/specific', ...)` |
| Using `page.waitForTimeout()` to simulate slow loading | Arbitrary, flaky, slows tests | Use promise-based route handlers to control timing precisely |
| Hardcoding error messages in assertions | Messages change. Tests break on copy edits. | Use regex or partial matches: `getByText(/error/i)` |
| Testing every error code in one mega-test | Hard to debug, slow, first failure hides the rest | One test per error scenario, or use `test.describe` groups |
| Skipping empty state tests | Empty states are the first thing new users see; often broken | Always test 0-item state alongside 1-item and N-item |
| Testing offline by disconnecting real network | Flaky, affects parallel tests, CI may not support it | Use `context.setOffline(true)` — deterministic and scoped |
| Not cleaning up route mocks between tests | Routes persist on the page. Test B inherits test A's mocks. | Each test sets its own routes; Playwright resets between tests by default |
| Asserting on exact error strings from the server | Couples tests to backend implementation details | Assert the UI message, not the raw API response body |
| Using `try/catch` to "handle" expected errors | Swallows real bugs; test passes when it shouldn't | Let errors propagate; use route mocking to control the response |

## Troubleshooting

### Route handler is not intercepting requests

**Cause**: The URL pattern does not match, or the route was registered after the navigation that triggers the request.

```typescript
// Always register routes BEFORE navigating
await page.route('**/api/data', (route) => route.fulfill({ status: 500 }));
await page.goto('/dashboard'); // route is active before the page loads

// Debug: log all requests to find the actual URL pattern
page.on('request', (req) => console.log(req.url()));
```

### `context.setOffline(true)` does not affect Service Worker

**Cause**: Service Workers have their own network handling. `setOffline` simulates offline at the browser level, but a Service Worker may serve cached responses.

```typescript
// Unregister service workers first
await page.evaluate(async () => {
  const registrations = await navigator.serviceWorker.getRegistrations();
  for (const registration of registrations) {
    await registration.unregister();
  }
});
await page.context().setOffline(true);
```

### Delayed route handler causes test timeout

**Cause**: The promise in the route handler never resolves, or the delay exceeds the test timeout.

```typescript
// Always ensure the delay is less than the assertion timeout
await page.route('**/api/slow', async (route) => {
  await new Promise((resolve) => setTimeout(resolve, 5_000)); // 5s delay
  await route.fulfill({ status: 200, json: {} });
});

// Increase assertion timeout to account for the artificial delay
await expect(page.getByText('Data loaded')).toBeVisible({ timeout: 10_000 });
```

### `goBack()` does not navigate

**Cause**: There is no history entry to go back to. `goBack()` requires at least one previous navigation.

```typescript
// Ensure there is history before calling goBack
await page.goto('/page-a');
await page.goto('/page-b');
await page.goBack(); // goes to /page-a

// If using SPA client-side routing, goBack may not work if the router
// does not push to browser history. Use the app's own back button instead.
await page.getByRole('button', { name: 'Back' }).click();
```

## Related

- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- assertion strategies for error states
- [core/network-mocking.md](network-mocking.md) -- detailed network interception and mocking patterns
- [core/forms-and-validation.md](forms-and-validation.md) -- form validation error testing
- [core/flaky-tests.md](flaky-tests.md) -- fixing timing issues in error/edge case tests
- [core/service-workers-and-pwa.md](service-workers-and-pwa.md) -- offline-first and PWA testing patterns
- [core/multi-context-and-popups.md](multi-context-and-popups.md) -- testing concurrent browser contexts
