# Clock and Time Mocking

> **When to use**: Testing time-dependent features -- countdown timers, scheduled events, expiration dates, age gates, session timeouts, or any UI that behaves differently based on the current time. Playwright's `page.clock` API lets you control time without waiting in real-time.
> **Prerequisites**: [core/assertions-and-waiting.md](assertions-and-waiting.md), [core/configuration.md](configuration.md)

## Quick Reference

```typescript
// Freeze time at a specific moment
await page.clock.install({ time: new Date('2025-03-15T10:00:00Z') });
await page.goto('/dashboard');

// Advance time by 5 minutes
await page.clock.fastForward('05:00');

// Set time to a specific point (jumps, does not tick through)
await page.clock.setFixedTime(new Date('2025-12-31T23:59:59Z'));

// Let time resume ticking from current mocked point
await page.clock.resume();
```

**Key concept**: `page.clock.install()` replaces `Date`, `setTimeout`, `setInterval`, and `requestAnimationFrame` in the page. Call it before `page.goto()` so the page loads with mocked time from the start.

## Patterns

### Frozen Time with `install()` and `setFixedTime()`

**Use when**: Your test needs time to stand still at a specific moment -- verifying what the UI shows at a particular date/time.
**Avoid when**: The feature under test depends on timers ticking (use `fastForward` instead).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('dashboard shows correct greeting based on time of day', async ({ page }) => {
  // Install clock BEFORE navigating
  await page.clock.install({ time: new Date('2025-06-15T08:30:00') });
  await page.goto('/dashboard');
  await expect(page.getByText('Good morning')).toBeVisible();

  // Jump to afternoon
  await page.clock.setFixedTime(new Date('2025-06-15T14:00:00'));
  await page.reload();
  await expect(page.getByText('Good afternoon')).toBeVisible();

  // Jump to evening
  await page.clock.setFixedTime(new Date('2025-06-15T20:00:00'));
  await page.reload();
  await expect(page.getByText('Good evening')).toBeVisible();
});

test('subscription shows correct expiration status', async ({ page }) => {
  // Freeze time to a date when subscription is active
  await page.clock.install({ time: new Date('2025-06-01T12:00:00Z') });
  await page.goto('/account');

  await expect(page.getByTestId('subscription-status')).toHaveText('Active');
  await expect(page.getByTestId('days-remaining')).toContainText('29');

  // Jump to the expiration date
  await page.clock.setFixedTime(new Date('2025-06-30T12:00:00Z'));
  await page.reload();

  await expect(page.getByTestId('subscription-status')).toHaveText('Expiring today');
});

test('content displays correctly on a specific holiday', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-12-25T10:00:00') });
  await page.goto('/');

  await expect(page.getByText('Happy Holidays')).toBeVisible();
  await expect(page.getByTestId('holiday-banner')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('dashboard shows correct greeting based on time of day', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-06-15T08:30:00') });
  await page.goto('/dashboard');
  await expect(page.getByText('Good morning')).toBeVisible();

  await page.clock.setFixedTime(new Date('2025-06-15T14:00:00'));
  await page.reload();
  await expect(page.getByText('Good afternoon')).toBeVisible();
});

test('subscription shows correct expiration status', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-06-01T12:00:00Z') });
  await page.goto('/account');

  await expect(page.getByTestId('subscription-status')).toHaveText('Active');
});
```

### Fast-Forwarding Time with `fastForward()`

**Use when**: Testing timers, countdowns, debounced actions, or any feature that reacts to elapsed time. `fastForward` fires all pending timers up to the specified duration.
**Avoid when**: You just need to check a static time-dependent display -- use `setFixedTime` instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('countdown timer reaches zero', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-03-15T10:00:00Z') });
  await page.goto('/sale');

  // Sale countdown starts at 2 hours
  await expect(page.getByTestId('countdown')).toContainText('2:00:00');

  // Fast-forward 1 hour
  await page.clock.fastForward('01:00:00');
  await expect(page.getByTestId('countdown')).toContainText('1:00:00');

  // Fast-forward remaining time
  await page.clock.fastForward('01:00:00');
  await expect(page.getByTestId('countdown')).toContainText('0:00:00');
  await expect(page.getByText('Sale ended')).toBeVisible();
});

test('auto-save triggers after 30 seconds of inactivity', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-03-15T10:00:00Z') });
  await page.goto('/editor');

  // Type something
  await page.getByRole('textbox', { name: 'Content' }).fill('Draft content');

  // Fast-forward past the auto-save interval
  await page.clock.fastForward('00:30');

  await expect(page.getByText('Saved')).toBeVisible();
});

test('session timeout warning appears after 25 minutes', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-03-15T10:00:00Z') });
  await page.goto('/dashboard');

  // Fast-forward to just before the warning (25 min)
  await page.clock.fastForward('24:59');
  await expect(page.getByRole('dialog', { name: 'Session timeout' })).not.toBeVisible();

  // One more minute triggers the warning
  await page.clock.fastForward('00:01');
  await expect(page.getByRole('dialog', { name: 'Session timeout' })).toBeVisible();
  await expect(page.getByText('Your session will expire in 5 minutes')).toBeVisible();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('countdown timer reaches zero', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-03-15T10:00:00Z') });
  await page.goto('/sale');

  await expect(page.getByTestId('countdown')).toContainText('2:00:00');

  await page.clock.fastForward('01:00:00');
  await expect(page.getByTestId('countdown')).toContainText('1:00:00');

  await page.clock.fastForward('01:00:00');
  await expect(page.getByText('Sale ended')).toBeVisible();
});

test('auto-save triggers after inactivity', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-03-15T10:00:00Z') });
  await page.goto('/editor');

  await page.getByRole('textbox', { name: 'Content' }).fill('Draft content');
  await page.clock.fastForward('00:30');

  await expect(page.getByText('Saved')).toBeVisible();
});
```

### Resuming Time with `resume()`

**Use when**: You need to start with a mocked time, then let time flow normally for interaction-dependent behavior.
**Avoid when**: The entire test should use mocked time.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('notification appears in real-time after scheduled trigger', async ({ page }) => {
  // Start at a known time
  await page.clock.install({ time: new Date('2025-03-15T09:59:55Z') });
  await page.goto('/dashboard');

  // Notification is scheduled for 10:00:00 — advance to 5 seconds before
  await expect(page.getByTestId('notification-bell')).not.toHaveAttribute('data-count');

  // Let real time tick from this point
  await page.clock.resume();

  // The notification should appear within a few seconds
  await expect(page.getByTestId('notification-bell')).toHaveAttribute('data-count', '1', {
    timeout: 10000,
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('notification appears after scheduled trigger', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-03-15T09:59:55Z') });
  await page.goto('/dashboard');

  await page.clock.resume();

  await expect(page.getByTestId('notification-bell')).toHaveAttribute('data-count', '1', {
    timeout: 10000,
  });
});
```

### Testing Date-Dependent UI

**Use when**: Features that change based on the current date -- age verification, expiration warnings, seasonal content, date pickers.
**Avoid when**: The date is passed from the server and does not depend on client-side `Date`.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('age gate blocks users under 18', async ({ page }) => {
  // User born on 2010-01-15 — under 18 as of 2025-06-01
  await page.clock.install({ time: new Date('2025-06-01T12:00:00') });
  await page.goto('/age-restricted');

  await page.getByLabel('Date of birth').fill('2010-01-15');
  await page.getByRole('button', { name: 'Verify age' }).click();

  await expect(page.getByText('You must be 18 or older')).toBeVisible();
});

test('age gate allows users 18 and older', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-06-01T12:00:00') });
  await page.goto('/age-restricted');

  await page.getByLabel('Date of birth').fill('2005-01-15');
  await page.getByRole('button', { name: 'Verify age' }).click();

  await expect(page.getByText('Welcome')).toBeVisible();
});

test('trial expiration banner shows at correct times', async ({ page }) => {
  // Day 1 of 14-day trial
  await page.clock.install({ time: new Date('2025-03-01T12:00:00Z') });
  await page.goto('/dashboard');
  await expect(page.getByTestId('trial-banner')).toContainText('13 days remaining');

  // Day 12 — warning state
  await page.clock.setFixedTime(new Date('2025-03-12T12:00:00Z'));
  await page.reload();
  await expect(page.getByTestId('trial-banner')).toContainText('2 days remaining');
  await expect(page.getByTestId('trial-banner')).toHaveCSS('background-color', /rgb\(255/); // Red/warning

  // Day 15 — expired
  await page.clock.setFixedTime(new Date('2025-03-15T12:00:00Z'));
  await page.reload();
  await expect(page.getByText('Your trial has expired')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Upgrade now' })).toBeVisible();
});

test('date picker defaults to current mocked date', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-07-04T12:00:00') });
  await page.goto('/booking');

  await page.getByLabel('Check-in date').click();

  // Calendar should open to July 2025
  await expect(page.getByText('July 2025')).toBeVisible();

  // Today (July 4) should be highlighted
  const today = page.locator('[aria-current="date"]');
  await expect(today).toHaveText('4');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('age gate blocks users under 18', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-06-01T12:00:00') });
  await page.goto('/age-restricted');

  await page.getByLabel('Date of birth').fill('2010-01-15');
  await page.getByRole('button', { name: 'Verify age' }).click();

  await expect(page.getByText('You must be 18 or older')).toBeVisible();
});

test('trial expiration shows correct days remaining', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-03-01T12:00:00Z') });
  await page.goto('/dashboard');
  await expect(page.getByTestId('trial-banner')).toContainText('13 days remaining');

  await page.clock.setFixedTime(new Date('2025-03-15T12:00:00Z'));
  await page.reload();
  await expect(page.getByText('Your trial has expired')).toBeVisible();
});
```

### Timezone-Dependent Features

**Use when**: Testing features that combine mocked time with specific timezones.
**Avoid when**: The feature uses only UTC and does not render local times.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('business hours banner shows open/closed status', async ({ browser }) => {
  // Business hours: 9 AM - 5 PM Eastern
  const context = await browser.newContext({ timezoneId: 'America/New_York' });
  const page = await context.newPage();

  // 10 AM Eastern — should show "Open"
  await page.clock.install({ time: new Date('2025-03-15T14:00:00Z') }); // 10 AM ET
  await page.goto('/contact');
  await expect(page.getByTestId('business-hours')).toContainText('Open');

  // 6 PM Eastern — should show "Closed"
  await page.clock.setFixedTime(new Date('2025-03-15T22:00:00Z')); // 6 PM ET
  await page.reload();
  await expect(page.getByTestId('business-hours')).toContainText('Closed');

  await context.close();
});

test('scheduled event shows correct local time', async ({ browser }) => {
  // Event at 2025-03-20T18:00:00Z

  // User in Tokyo (UTC+9)
  const tokyoCtx = await browser.newContext({ timezoneId: 'Asia/Tokyo' });
  const tokyoPage = await tokyoCtx.newPage();
  await tokyoPage.clock.install({ time: new Date('2025-03-20T10:00:00Z') });
  await tokyoPage.goto('/events/upcoming');
  // 18:00 UTC = 03:00 AM next day in Tokyo (UTC+9)
  await expect(tokyoPage.getByTestId('event-time')).toContainText('3:00 AM');
  await tokyoCtx.close();

  // User in London (UTC+0 in March, before DST)
  const londonCtx = await browser.newContext({ timezoneId: 'Europe/London' });
  const londonPage = await londonCtx.newPage();
  await londonPage.clock.install({ time: new Date('2025-03-20T10:00:00Z') });
  await londonPage.goto('/events/upcoming');
  await expect(londonPage.getByTestId('event-time')).toContainText('6:00 PM');
  await londonCtx.close();
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('business hours banner shows open/closed status', async ({ browser }) => {
  const context = await browser.newContext({ timezoneId: 'America/New_York' });
  const page = await context.newPage();

  await page.clock.install({ time: new Date('2025-03-15T14:00:00Z') });
  await page.goto('/contact');
  await expect(page.getByTestId('business-hours')).toContainText('Open');

  await page.clock.setFixedTime(new Date('2025-03-15T22:00:00Z'));
  await page.reload();
  await expect(page.getByTestId('business-hours')).toContainText('Closed');

  await context.close();
});
```

## Decision Guide

| Scenario | API | Why |
|---|---|---|
| Check UI at a specific date/time | `clock.install()` + `clock.setFixedTime()` | Time is frozen; no timer ticking |
| Test countdown or timer behavior | `clock.install()` + `clock.fastForward()` | Fires timers as time advances without real waiting |
| Test after a long idle period | `clock.install()` + `clock.fastForward('30:00')` | Simulates 30 minutes without waiting 30 minutes |
| Start mocked, then tick normally | `clock.install()` + `clock.resume()` | Useful when you need real `requestAnimationFrame` after setup |
| Different timezone display | `browser.newContext({ timezoneId })` | Affects `Date` timezone rendering |
| Timezone + mocked time | `newContext({ timezoneId })` + `clock.install()` | Both timezone and absolute time are controlled |
| Test date picker defaults | `clock.install()` with target date | Calendar opens to the mocked "today" |
| Test DST transitions | Set `timezoneId` + `install` at DST boundary | Tests the most common timezone bugs |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Calling `clock.install()` after `page.goto()` | Page already loaded with real `Date`; timers already fired | Call `clock.install()` BEFORE `page.goto()` |
| Using `page.waitForTimeout(30000)` to test a 30-second timer | Wastes 30 real seconds per test run | `page.clock.fastForward('00:30')` completes instantly |
| Testing time without mocking the clock | Results depend on when the test runs (morning vs evening, Monday vs Sunday) | Always mock time for time-dependent assertions |
| Using `setFixedTime` when you need timers to fire | `setFixedTime` freezes time; `setInterval`/`setTimeout` will not trigger | Use `fastForward` to advance time and fire pending timers |
| Mocking only `Date.now()` via `page.evaluate` | Does not affect `setTimeout`, `setInterval`, or `requestAnimationFrame` | Use `page.clock.install()` which mocks all time APIs |
| Forgetting timezone when testing dates | Test passes locally but fails in CI (different timezone) | Always set `timezoneId` in context or use UTC dates |
| Advancing time in very small increments | Slow test; many unnecessary timer firings | Advance to the exact time of interest in one call |
| Not calling `resume()` before real-time-dependent assertions | Mocked timers will not fire naturally; assertions time out | Call `clock.resume()` when you need real time to flow |

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `clock.install()` has no effect | Called after `page.goto()`; page already has real `Date` | Move `clock.install()` before navigation |
| Timer callbacks never fire | Time is frozen with `setFixedTime`; timers need advancing | Use `fastForward()` to advance past the timer delay |
| `fastForward` does not trigger timer | Timer was registered with a delay longer than the fast-forward amount | Fast-forward by at least the timer's delay |
| Date is correct but timezone display is wrong | `clock.install` sets time in UTC; `timezoneId` not set on context | Create context with `{ timezoneId: 'Your/Timezone' }` |
| Animations break with mocked clock | `requestAnimationFrame` is mocked and does not fire naturally | Call `clock.resume()` before animation-dependent assertions |
| Test passes locally but fails in CI | Local timezone differs from CI timezone | Always set `timezoneId` explicitly in the context |
| `setFixedTime` throws "clock not installed" | `install()` was not called first | Call `page.clock.install()` before any other clock methods |
| Page makes fetch requests with wrong timestamps | Server sees mocked `Date.now()` in request payloads | This is expected; mock server responses if needed |

## Related

- [core/i18n-and-localization.md](i18n-and-localization.md) -- timezone and locale testing patterns
- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- auto-waiting vs time-based assertions
- [core/error-and-edge-cases.md](error-and-edge-cases.md) -- testing timeout and expiration edge cases
- [core/performance-testing.md](performance-testing.md) -- timing-related performance measurement
- [core/websockets-and-realtime.md](websockets-and-realtime.md) -- real-time features that depend on timing
