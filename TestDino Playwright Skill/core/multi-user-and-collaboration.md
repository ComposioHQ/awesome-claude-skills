# Multi-User and Collaboration Testing

> **When to use**: When your application involves real-time collaboration, multi-user workflows, or any scenario where two or more users interact with the same resource simultaneously -- chat apps, shared documents, multiplayer features, admin-and-user flows.
> **Prerequisites**: [core/fixtures-and-hooks.md](fixtures-and-hooks.md), [core/configuration.md](configuration.md)

## Quick Reference

```typescript
// Two independent browser contexts in one test = two users
const alice = await browser.newContext({ storageState: 'auth/alice.json' });
const bob = await browser.newContext({ storageState: 'auth/bob.json' });
const alicePage = await alice.newPage();
const bobPage = await bob.newPage();

// Each operates independently — different cookies, sessions, localStorage
await alicePage.goto('/chat/room-1');
await bobPage.goto('/chat/room-1');
```

## Patterns

### Two Users in One Test via Browser Contexts

**Use when**: You need to verify that actions by one user are visible to another in real time.
**Avoid when**: You only need to test a single user's flow. One context per test is the default.

Each `browser.newContext()` creates a fully isolated session -- separate cookies, localStorage, and network state. This is how you simulate two logged-in users in a single test without launching a second browser.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('alice sends a message and bob sees it', async ({ browser }) => {
  // Create two isolated contexts
  const aliceContext = await browser.newContext({ storageState: 'auth/alice.json' });
  const bobContext = await browser.newContext({ storageState: 'auth/bob.json' });

  const alicePage = await aliceContext.newPage();
  const bobPage = await bobContext.newPage();

  // Both navigate to the same chat room
  await alicePage.goto('/chat/general');
  await bobPage.goto('/chat/general');

  // Alice sends a message
  await alicePage.getByRole('textbox', { name: 'Message' }).fill('Hello Bob!');
  await alicePage.getByRole('button', { name: 'Send' }).click();

  // Bob sees it in real time
  await expect(bobPage.getByText('Hello Bob!')).toBeVisible();

  // Alice also sees her own message
  await expect(alicePage.getByText('Hello Bob!')).toBeVisible();

  // Cleanup
  await aliceContext.close();
  await bobContext.close();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('alice sends a message and bob sees it', async ({ browser }) => {
  const aliceContext = await browser.newContext({ storageState: 'auth/alice.json' });
  const bobContext = await browser.newContext({ storageState: 'auth/bob.json' });

  const alicePage = await aliceContext.newPage();
  const bobPage = await bobContext.newPage();

  await alicePage.goto('/chat/general');
  await bobPage.goto('/chat/general');

  await alicePage.getByRole('textbox', { name: 'Message' }).fill('Hello Bob!');
  await alicePage.getByRole('button', { name: 'Send' }).click();

  await expect(bobPage.getByText('Hello Bob!')).toBeVisible();
  await expect(alicePage.getByText('Hello Bob!')).toBeVisible();

  await aliceContext.close();
  await bobContext.close();
});
```

### Multi-User Fixture for Reusability

**Use when**: Multiple tests need two-user setups. Wrap context creation in a fixture to avoid boilerplate.
**Avoid when**: Only one test needs multi-user logic.

**TypeScript**
```typescript
// fixtures.ts
import { test as base, expect, BrowserContext, Page } from '@playwright/test';

type MultiUserFixtures = {
  aliceContext: BrowserContext;
  alicePage: Page;
  bobContext: BrowserContext;
  bobPage: Page;
};

export const test = base.extend<MultiUserFixtures>({
  aliceContext: async ({ browser }, use) => {
    const context = await browser.newContext({ storageState: 'auth/alice.json' });
    await use(context);
    await context.close();
  },
  alicePage: async ({ aliceContext }, use) => {
    const page = await aliceContext.newPage();
    await use(page);
  },
  bobContext: async ({ browser }, use) => {
    const context = await browser.newContext({ storageState: 'auth/bob.json' });
    await use(context);
    await context.close();
  },
  bobPage: async ({ bobContext }, use) => {
    const page = await bobContext.newPage();
    await use(page);
  },
});

export { expect };
```

```typescript
// collaboration.spec.ts
import { test, expect } from './fixtures';

test('both users see shared document title', async ({ alicePage, bobPage }) => {
  await alicePage.goto('/docs/shared-doc');
  await bobPage.goto('/docs/shared-doc');

  await alicePage.getByRole('textbox', { name: 'Title' }).fill('Project Plan');

  await expect(bobPage.getByRole('textbox', { name: 'Title' })).toHaveValue('Project Plan');
});
```

**JavaScript**
```javascript
// fixtures.js
const { test: base, expect } = require('@playwright/test');

const test = base.extend({
  aliceContext: async ({ browser }, use) => {
    const context = await browser.newContext({ storageState: 'auth/alice.json' });
    await use(context);
    await context.close();
  },
  alicePage: async ({ aliceContext }, use) => {
    const page = await aliceContext.newPage();
    await use(page);
  },
  bobContext: async ({ browser }, use) => {
    const context = await browser.newContext({ storageState: 'auth/bob.json' });
    await use(context);
    await context.close();
  },
  bobPage: async ({ bobContext }, use) => {
    const page = await bobContext.newPage();
    await use(page);
  },
});

module.exports = { test, expect };
```

### Collaborative Editing with Conflict Detection

**Use when**: Testing real-time collaborative editors (Google Docs-style) where both users edit the same content.
**Avoid when**: Your app does not support concurrent editing.

**TypeScript**
```typescript
import { test, expect } from './fixtures';

test('concurrent edits merge without data loss', async ({ alicePage, bobPage }) => {
  await alicePage.goto('/docs/shared-doc');
  await bobPage.goto('/docs/shared-doc');

  // Wait for both to be connected
  await expect(alicePage.getByTestId('connection-status')).toHaveText('Connected');
  await expect(bobPage.getByTestId('connection-status')).toHaveText('Connected');

  // Alice types at the beginning
  const aliceEditor = alicePage.getByRole('textbox', { name: 'Editor' });
  await aliceEditor.pressSequentially('Alice was here. ');

  // Bob types at the end (simultaneously)
  const bobEditor = bobPage.getByRole('textbox', { name: 'Editor' });
  await bobEditor.press('End');
  await bobEditor.pressSequentially('Bob was here.');

  // Both edits should be visible to both users
  await expect(aliceEditor).toContainText('Alice was here.');
  await expect(aliceEditor).toContainText('Bob was here.');
  await expect(bobEditor).toContainText('Alice was here.');
  await expect(bobEditor).toContainText('Bob was here.');
});
```

**JavaScript**
```javascript
const { test, expect } = require('./fixtures');

test('concurrent edits merge without data loss', async ({ alicePage, bobPage }) => {
  await alicePage.goto('/docs/shared-doc');
  await bobPage.goto('/docs/shared-doc');

  await expect(alicePage.getByTestId('connection-status')).toHaveText('Connected');
  await expect(bobPage.getByTestId('connection-status')).toHaveText('Connected');

  const aliceEditor = alicePage.getByRole('textbox', { name: 'Editor' });
  await aliceEditor.pressSequentially('Alice was here. ');

  const bobEditor = bobPage.getByRole('textbox', { name: 'Editor' });
  await bobEditor.press('End');
  await bobEditor.pressSequentially('Bob was here.');

  await expect(aliceEditor).toContainText('Alice was here.');
  await expect(aliceEditor).toContainText('Bob was here.');
  await expect(bobEditor).toContainText('Alice was here.');
  await expect(bobEditor).toContainText('Bob was here.');
});
```

### Shared State Verification (Presence, Cursors, Indicators)

**Use when**: Verifying that one user's presence or activity is reflected in the other user's UI -- online indicators, typing indicators, cursor positions.
**Avoid when**: Presence is not a feature of your app.

**TypeScript**
```typescript
import { test, expect } from './fixtures';

test('bob sees alice typing indicator', async ({ alicePage, bobPage }) => {
  await alicePage.goto('/chat/general');
  await bobPage.goto('/chat/general');

  // Alice starts typing
  await alicePage.getByRole('textbox', { name: 'Message' }).pressSequentially('Hel', { delay: 100 });

  // Bob sees the typing indicator
  await expect(bobPage.getByText('Alice is typing...')).toBeVisible();

  // Alice stops typing — indicator disappears after debounce
  await expect(bobPage.getByText('Alice is typing...')).toBeHidden({ timeout: 5000 });
});

test('online users list updates when user joins', async ({ alicePage, bobPage }) => {
  await alicePage.goto('/chat/general');

  // Alice sees only herself
  await expect(alicePage.getByTestId('online-users').getByText('Alice')).toBeVisible();
  await expect(alicePage.getByTestId('online-users').getByText('Bob')).toBeHidden();

  // Bob joins
  await bobPage.goto('/chat/general');

  // Alice now sees Bob in the online list
  await expect(alicePage.getByTestId('online-users').getByText('Bob')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('./fixtures');

test('bob sees alice typing indicator', async ({ alicePage, bobPage }) => {
  await alicePage.goto('/chat/general');
  await bobPage.goto('/chat/general');

  await alicePage.getByRole('textbox', { name: 'Message' }).pressSequentially('Hel', { delay: 100 });
  await expect(bobPage.getByText('Alice is typing...')).toBeVisible();
  await expect(bobPage.getByText('Alice is typing...')).toBeHidden({ timeout: 5000 });
});

test('online users list updates when user joins', async ({ alicePage, bobPage }) => {
  await alicePage.goto('/chat/general');
  await expect(alicePage.getByTestId('online-users').getByText('Alice')).toBeVisible();

  await bobPage.goto('/chat/general');
  await expect(alicePage.getByTestId('online-users').getByText('Bob')).toBeVisible();
});
```

### Race Condition Testing Between Users

**Use when**: You need to verify that simultaneous actions (two users clicking "buy" on the last item, or two users editing the same field) are handled correctly.
**Avoid when**: Your app has no shared mutable resources.

**TypeScript**
```typescript
import { test, expect } from './fixtures';

test('only one user can claim the last item', async ({ alicePage, bobPage }) => {
  await alicePage.goto('/store/limited-item');
  await bobPage.goto('/store/limited-item');

  // Both see the item is available
  await expect(alicePage.getByText('1 remaining')).toBeVisible();
  await expect(bobPage.getByText('1 remaining')).toBeVisible();

  // Both click buy at approximately the same time
  const aliceBuy = alicePage.getByRole('button', { name: 'Buy now' }).click();
  const bobBuy = bobPage.getByRole('button', { name: 'Buy now' }).click();
  await Promise.all([aliceBuy, bobBuy]);

  // One succeeds, one fails — verify the app handles the race
  const aliceResult = await alicePage.getByTestId('purchase-result').textContent();
  const bobResult = await bobPage.getByTestId('purchase-result').textContent();

  const results = [aliceResult, bobResult];
  expect(results).toContain('Purchase successful');
  expect(results).toContain('Item no longer available');
});

test('simultaneous form submissions do not create duplicates', async ({ alicePage, bobPage }) => {
  await alicePage.goto('/admin/settings');
  await bobPage.goto('/admin/settings');

  // Both change the same setting
  await alicePage.getByLabel('Company name').fill('Alice Corp');
  await bobPage.getByLabel('Company name').fill('Bob Inc');

  // Submit simultaneously
  await Promise.all([
    alicePage.getByRole('button', { name: 'Save' }).click(),
    bobPage.getByRole('button', { name: 'Save' }).click(),
  ]);

  // Reload both pages — one value should win, no corruption
  await alicePage.reload();
  const finalValue = await alicePage.getByLabel('Company name').inputValue();
  expect(['Alice Corp', 'Bob Inc']).toContain(finalValue);

  // The "loser" should see a conflict notification or the updated value
  await bobPage.reload();
  await expect(bobPage.getByLabel('Company name')).toHaveValue(finalValue);
});
```

**JavaScript**
```javascript
const { test, expect } = require('./fixtures');

test('only one user can claim the last item', async ({ alicePage, bobPage }) => {
  await alicePage.goto('/store/limited-item');
  await bobPage.goto('/store/limited-item');

  await expect(alicePage.getByText('1 remaining')).toBeVisible();
  await expect(bobPage.getByText('1 remaining')).toBeVisible();

  const aliceBuy = alicePage.getByRole('button', { name: 'Buy now' }).click();
  const bobBuy = bobPage.getByRole('button', { name: 'Buy now' }).click();
  await Promise.all([aliceBuy, bobBuy]);

  const aliceResult = await alicePage.getByTestId('purchase-result').textContent();
  const bobResult = await bobPage.getByTestId('purchase-result').textContent();

  const results = [aliceResult, bobResult];
  expect(results).toContain('Purchase successful');
  expect(results).toContain('Item no longer available');
});
```

### N Users with Dynamic Context Creation

**Use when**: You need more than two users, or the number of users is variable (load-like collaboration tests).
**Avoid when**: Two users suffice. Keep it simple.

**TypeScript**
```typescript
import { test, expect, Browser, Page } from '@playwright/test';

async function createUser(browser: Browser, name: string, room: string): Promise<Page> {
  const context = await browser.newContext({ storageState: `auth/${name}.json` });
  const page = await context.newPage();
  await page.goto(`/chat/${room}`);
  return page;
}

test('five users in a chat room all see each other', async ({ browser }) => {
  const names = ['alice', 'bob', 'charlie', 'diana', 'eve'];
  const pages = await Promise.all(
    names.map((name) => createUser(browser, name, 'team-room'))
  );

  // First user sends a message
  await pages[0].getByRole('textbox', { name: 'Message' }).fill('Hello everyone!');
  await pages[0].getByRole('button', { name: 'Send' }).click();

  // All users see the message
  for (const page of pages) {
    await expect(page.getByText('Hello everyone!')).toBeVisible();
  }

  // Cleanup
  for (const page of pages) {
    await page.context().close();
  }
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

async function createUser(browser, name, room) {
  const context = await browser.newContext({ storageState: `auth/${name}.json` });
  const page = await context.newPage();
  await page.goto(`/chat/${room}`);
  return page;
}

test('five users in a chat room all see each other', async ({ browser }) => {
  const names = ['alice', 'bob', 'charlie', 'diana', 'eve'];
  const pages = await Promise.all(
    names.map((name) => createUser(browser, name, 'team-room'))
  );

  await pages[0].getByRole('textbox', { name: 'Message' }).fill('Hello everyone!');
  await pages[0].getByRole('button', { name: 'Send' }).click();

  for (const page of pages) {
    await expect(page.getByText('Hello everyone!')).toBeVisible();
  }

  for (const page of pages) {
    await page.context().close();
  }
});
```

## Decision Guide

| Scenario | Approach | Why |
|---|---|---|
| Two users interact in real time | Two `browser.newContext()` in one test | Fully isolated sessions, same test timeline |
| Same multi-user setup across many tests | Custom fixture per user context | Eliminates boilerplate, guarantees cleanup |
| Testing presence/typing indicators | Sequential actions, assert on other page | Order matters -- act on one, assert on the other |
| Race condition (simultaneous clicks) | `Promise.all([action1, action2])` | Fires both as close to simultaneously as possible |
| Admin performs action, user sees result | Two contexts with different `storageState` | Different auth roles, same browser instance |
| 3+ users in one test | Loop with `browser.newContext()` per user | Each context is cheap; browser is shared |
| Cross-browser multi-user (Chrome + Firefox) | Separate browser launches in `beforeAll` | Rarely needed; contexts within one browser suffice |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Use one context with two pages for two users | Pages in the same context share cookies and localStorage | Use `browser.newContext()` per user |
| Open a second browser for the second user | Wastes memory and startup time | Use a second `browser.newContext()` -- contexts are lightweight |
| `await page.waitForTimeout(2000)` for real-time sync | Arbitrary delay; flaky in CI, slow in dev | `await expect(bobPage.getByText('msg')).toBeVisible()` |
| Share mutable state via `let` variables between contexts | Test order and timing become implicit dependencies | Each context is independent; assert via UI |
| Put multi-user setup in `beforeAll` | `beforeAll` cannot access `page` or `context` | Use test-scoped fixtures or inline `browser.newContext()` |
| Forget to close extra contexts | Leaks memory and may cause port exhaustion | Always close contexts in fixture teardown or `finally` |
| Assert on both pages without waiting | The second page may not have received the update yet | Use `expect` with auto-retry on the receiving page |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Second user sees stale data | Context created before server state was ready | Navigate the second page after the first user's action completes |
| `storageState` file not found | Auth setup project has not run, or path is wrong | Run auth setup first via `dependencies` in `playwright.config` |
| Both users have the same session | Reusing the same `storageState` file for both | Create distinct auth state files per user role |
| Real-time updates never arrive on second page | WebSocket/SSE connection not established before assertion | Wait for a connection indicator before asserting: `await expect(page.getByTestId('connected')).toBeVisible()` |
| Test is slow with many contexts | Too many contexts in a single test (10+) | Limit to 3-5 contexts per test; use API setup to reduce page interactions |
| `Promise.all` race test always has same winner | Network/event loop makes one always faster | This is expected in testing -- assert that the app handles both outcomes, not which user wins |

## Related

- [core/fixtures-and-hooks.md](fixtures-and-hooks.md) -- wrap multi-user contexts in fixtures
- [core/websockets-and-realtime.md](websockets-and-realtime.md) -- test the transport layer beneath collaboration features
- [core/test-data-management.md](test-data-management.md) -- set up shared resources (rooms, documents) before multi-user tests
- [core/configuration.md](configuration.md) -- configure `storageState` per project for different user roles
