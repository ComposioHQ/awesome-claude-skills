# Mobile and Responsive Testing

> **When to use**: Testing how your application behaves on phones, tablets, and across viewport sizes. Covers device emulation, touch interactions, geolocation, orientation changes, and mobile-specific UI patterns.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/locators.md](locators.md)

## Quick Reference

```typescript
import { devices } from '@playwright/test';

// Predefined device profiles (viewport, userAgent, touch, deviceScaleFactor)
devices['iPhone 14']           // 390x844, touch, Safari mobile UA
devices['iPhone 14 Pro Max']   // 430x932, touch, Safari mobile UA
devices['Pixel 7']             // 412x915, touch, Chrome mobile UA
devices['iPad Pro 11']         // 834x1194, touch, Safari tablet UA
devices['Galaxy S9+']          // 320x658, touch, Chrome mobile UA
devices['Desktop Chrome']      // 1280x720, no touch, Chrome desktop UA
devices['Desktop Safari']      // 1280x720, no touch, Safari desktop UA

// Landscape variants
devices['iPhone 14 landscape'] // 844x390, touch, Safari mobile UA
devices['iPad Pro 11 landscape'] // 1194x834, touch, Safari tablet UA
```

```bash
# Run mobile project only
npx playwright test --project=mobile-chrome
npx playwright test --project=mobile-safari

# Run all projects (desktop + mobile in parallel)
npx playwright test

# List available device names
npx playwright test --list-devices 2>/dev/null || node -e "const {devices}=require('@playwright/test');console.log(Object.keys(devices).join('\n'))"
```

## Patterns

### 1. Device Emulation

**Use when**: Testing your app as it appears on a specific real-world device -- iPhone, Pixel, iPad. Applies the correct viewport, user agent, device scale factor, and touch support in one shot.
**Avoid when**: You only need to test a specific viewport width (use custom viewports instead). Device emulation is not a substitute for real device testing when pixel-perfect rendering matters.

#### TypeScript

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  projects: [
    {
      name: 'Desktop Chrome',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 7'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 14'] },
    },
    {
      name: 'Tablet',
      use: { ...devices['iPad Pro 11'] },
    },
  ],
});
```

```typescript
// tests/mobile-navigation.spec.ts
import { test, expect } from '@playwright/test';

test('mobile user can navigate via hamburger menu', async ({ page, isMobile }) => {
  await page.goto('/');

  if (isMobile) {
    // Mobile: hamburger menu is visible, desktop nav is hidden
    await expect(page.getByRole('button', { name: 'Menu' })).toBeVisible();
    await expect(page.getByRole('navigation', { name: 'Main' })).toBeHidden();

    // Open hamburger menu
    await page.getByRole('button', { name: 'Menu' }).click();
    await expect(page.getByRole('navigation', { name: 'Main' })).toBeVisible();
    await page.getByRole('link', { name: 'Products' }).click();
    await page.waitForURL('**/products');
  } else {
    // Desktop: nav links are directly visible
    await expect(page.getByRole('navigation', { name: 'Main' })).toBeVisible();
    await page.getByRole('link', { name: 'Products' }).click();
    await page.waitForURL('**/products');
  }

  await expect(page.getByRole('heading', { name: 'Products', level: 1 })).toBeVisible();
});
```

#### JavaScript

```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  projects: [
    {
      name: 'Desktop Chrome',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 7'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 14'] },
    },
    {
      name: 'Tablet',
      use: { ...devices['iPad Pro 11'] },
    },
  ],
});
```

```javascript
// tests/mobile-navigation.spec.js
const { test, expect } = require('@playwright/test');

test('mobile user can navigate via hamburger menu', async ({ page, isMobile }) => {
  await page.goto('/');

  if (isMobile) {
    await expect(page.getByRole('button', { name: 'Menu' })).toBeVisible();
    await expect(page.getByRole('navigation', { name: 'Main' })).toBeHidden();

    await page.getByRole('button', { name: 'Menu' }).click();
    await expect(page.getByRole('navigation', { name: 'Main' })).toBeVisible();
    await page.getByRole('link', { name: 'Products' }).click();
    await page.waitForURL('**/products');
  } else {
    await expect(page.getByRole('navigation', { name: 'Main' })).toBeVisible();
    await page.getByRole('link', { name: 'Products' }).click();
    await page.waitForURL('**/products');
  }

  await expect(page.getByRole('heading', { name: 'Products', level: 1 })).toBeVisible();
});
```

### 2. Custom Viewports

**Use when**: Testing responsive layouts at specific breakpoints without full device emulation. Ideal for verifying CSS media queries fire at the right widths.
**Avoid when**: You need realistic mobile behavior (touch events, mobile user agent, device scale factor). Use device emulation instead.

#### TypeScript

```typescript
// tests/responsive-layout.spec.ts
import { test, expect } from '@playwright/test';

const breakpoints = [
  { name: 'mobile-small', width: 320, height: 568 },
  { name: 'mobile', width: 375, height: 667 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1024, height: 768 },
  { name: 'desktop-large', width: 1440, height: 900 },
];

for (const bp of breakpoints) {
  test(`layout adapts correctly at ${bp.name} (${bp.width}px)`, async ({ page }) => {
    await page.setViewportSize({ width: bp.width, height: bp.height });
    await page.goto('/');

    if (bp.width < 768) {
      // Mobile layout: stacked, hamburger menu visible
      await expect(page.getByRole('button', { name: 'Menu' })).toBeVisible();
      await expect(page.getByTestId('sidebar')).toBeHidden();
    } else if (bp.width < 1024) {
      // Tablet layout: collapsible sidebar
      await expect(page.getByRole('button', { name: 'Menu' })).toBeHidden();
      await expect(page.getByTestId('sidebar')).toBeVisible();
    } else {
      // Desktop layout: full sidebar, no hamburger
      await expect(page.getByRole('button', { name: 'Menu' })).toBeHidden();
      await expect(page.getByTestId('sidebar')).toBeVisible();
      await expect(page.getByTestId('sidebar')).toHaveCSS('width', '280px');
    }
  });
}
```

```typescript
// Per-file viewport override (applies to all tests in this file)
import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 375, height: 667 } });

test('mobile checkout flow fits on small screen', async ({ page }) => {
  await page.goto('/checkout');

  // Verify no horizontal scrollbar
  const hasHorizontalScroll = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth
  );
  expect(hasHorizontalScroll).toBe(false);

  // Verify all form fields are visible without horizontal scroll
  await expect(page.getByLabel('Card number')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Pay now' })).toBeVisible();
});
```

#### JavaScript

```javascript
// tests/responsive-layout.spec.js
const { test, expect } = require('@playwright/test');

const breakpoints = [
  { name: 'mobile-small', width: 320, height: 568 },
  { name: 'mobile', width: 375, height: 667 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1024, height: 768 },
  { name: 'desktop-large', width: 1440, height: 900 },
];

for (const bp of breakpoints) {
  test(`layout adapts correctly at ${bp.name} (${bp.width}px)`, async ({ page }) => {
    await page.setViewportSize({ width: bp.width, height: bp.height });
    await page.goto('/');

    if (bp.width < 768) {
      await expect(page.getByRole('button', { name: 'Menu' })).toBeVisible();
      await expect(page.getByTestId('sidebar')).toBeHidden();
    } else if (bp.width < 1024) {
      await expect(page.getByRole('button', { name: 'Menu' })).toBeHidden();
      await expect(page.getByTestId('sidebar')).toBeVisible();
    } else {
      await expect(page.getByRole('button', { name: 'Menu' })).toBeHidden();
      await expect(page.getByTestId('sidebar')).toBeVisible();
      await expect(page.getByTestId('sidebar')).toHaveCSS('width', '280px');
    }
  });
}
```

```javascript
// Per-file viewport override
const { test, expect } = require('@playwright/test');

test.use({ viewport: { width: 375, height: 667 } });

test('mobile checkout flow fits on small screen', async ({ page }) => {
  await page.goto('/checkout');

  const hasHorizontalScroll = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth
  );
  expect(hasHorizontalScroll).toBe(false);

  await expect(page.getByLabel('Card number')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Pay now' })).toBeVisible();
});
```

### 3. Touch Events

**Use when**: Testing touch-specific interactions -- tap, swipe, pinch. Required for mobile-only gestures that have no mouse equivalent.
**Avoid when**: The feature works identically with mouse clicks. Playwright's `click()` dispatches touch events automatically on touch-enabled device profiles.

#### TypeScript

```typescript
// tests/touch-interactions.spec.ts
import { test, expect, devices } from '@playwright/test';

test.use({ ...devices['iPhone 14'] });

test('tap to select an item', async ({ page }) => {
  await page.goto('/gallery');

  // tap() dispatches touchstart → touchend → click
  // Only available when hasTouch is true (device profiles set this)
  await page.getByRole('img', { name: 'Sunset photo' }).tap();
  await expect(page.getByText('Selected: Sunset photo')).toBeVisible();
});

test('swipe to dismiss a card', async ({ page }) => {
  await page.goto('/notifications');

  const card = page.getByTestId('notification-card').first();
  const box = await card.boundingBox();

  if (box) {
    // Simulate a left swipe: touchstart on right side, touchmove to left, touchend
    await page.touchscreen.tap(box.x + box.width - 20, box.y + box.height / 2);

    // Swipe gesture using mouse (touch events are synthesized from mouse on emulated devices)
    await card.hover({ position: { x: box.width - 20, y: box.height / 2 } });
    await page.mouse.down();
    await page.mouse.move(box.x - 100, box.y + box.height / 2, { steps: 10 });
    await page.mouse.up();

    await expect(card).toBeHidden();
  }
});

test('long press to open context menu', async ({ page }) => {
  await page.goto('/files');

  const file = page.getByRole('listitem').filter({ hasText: 'Report.pdf' });

  // Long press: dispatch pointerdown, wait, then pointerup
  await file.click({ delay: 800 }); // delay in ms simulates long press
  await expect(page.getByRole('menu')).toBeVisible();
  await page.getByRole('menuitem', { name: 'Delete' }).click();
});

test('pinch to zoom on a map', async ({ page }) => {
  await page.goto('/map');

  // Pinch-to-zoom requires dispatching multi-touch events via JavaScript
  const mapElement = page.getByTestId('map-container');

  await mapElement.evaluate((el) => {
    // Simulate pinch-out (zoom in) with two touch points moving apart
    const center = { x: el.clientWidth / 2, y: el.clientHeight / 2 };

    const touch1 = new Touch({
      identifier: 0,
      target: el,
      clientX: center.x - 50,
      clientY: center.y,
    });
    const touch2 = new Touch({
      identifier: 1,
      target: el,
      clientX: center.x + 50,
      clientY: center.y,
    });

    el.dispatchEvent(new TouchEvent('touchstart', {
      touches: [touch1, touch2],
      changedTouches: [touch1, touch2],
      bubbles: true,
    }));

    const touch1Moved = new Touch({
      identifier: 0,
      target: el,
      clientX: center.x - 120,
      clientY: center.y,
    });
    const touch2Moved = new Touch({
      identifier: 1,
      target: el,
      clientX: center.x + 120,
      clientY: center.y,
    });

    el.dispatchEvent(new TouchEvent('touchmove', {
      touches: [touch1Moved, touch2Moved],
      changedTouches: [touch1Moved, touch2Moved],
      bubbles: true,
    }));

    el.dispatchEvent(new TouchEvent('touchend', {
      touches: [],
      changedTouches: [touch1Moved, touch2Moved],
      bubbles: true,
    }));
  });

  // Verify zoom level changed
  await expect(page.getByTestId('zoom-level')).not.toHaveText('1x');
});
```

#### JavaScript

```javascript
// tests/touch-interactions.spec.js
const { test, expect, devices } = require('@playwright/test');

test.use({ ...devices['iPhone 14'] });

test('tap to select an item', async ({ page }) => {
  await page.goto('/gallery');

  await page.getByRole('img', { name: 'Sunset photo' }).tap();
  await expect(page.getByText('Selected: Sunset photo')).toBeVisible();
});

test('swipe to dismiss a card', async ({ page }) => {
  await page.goto('/notifications');

  const card = page.getByTestId('notification-card').first();
  const box = await card.boundingBox();

  if (box) {
    await card.hover({ position: { x: box.width - 20, y: box.height / 2 } });
    await page.mouse.down();
    await page.mouse.move(box.x - 100, box.y + box.height / 2, { steps: 10 });
    await page.mouse.up();

    await expect(card).toBeHidden();
  }
});

test('long press to open context menu', async ({ page }) => {
  await page.goto('/files');

  const file = page.getByRole('listitem').filter({ hasText: 'Report.pdf' });
  await file.click({ delay: 800 });
  await expect(page.getByRole('menu')).toBeVisible();
  await page.getByRole('menuitem', { name: 'Delete' }).click();
});
```

### 4. Mobile-Specific UI

**Use when**: Testing UI components that only appear on mobile -- hamburger menus, bottom sheets, pull-to-refresh, sticky mobile headers, floating action buttons.
**Avoid when**: The component renders identically on desktop and mobile.

#### TypeScript

```typescript
// tests/mobile-ui.spec.ts
import { test, expect, devices } from '@playwright/test';

test.use({ ...devices['iPhone 14'] });

test('hamburger menu opens and closes', async ({ page }) => {
  await page.goto('/');

  const menuButton = page.getByRole('button', { name: 'Menu' });
  const nav = page.getByRole('navigation', { name: 'Main' });

  // Menu starts closed
  await expect(nav).toBeHidden();

  // Open menu
  await menuButton.click();
  await expect(nav).toBeVisible();

  // Verify all nav items are visible
  await expect(nav.getByRole('link', { name: 'Home' })).toBeVisible();
  await expect(nav.getByRole('link', { name: 'Products' })).toBeVisible();
  await expect(nav.getByRole('link', { name: 'Account' })).toBeVisible();

  // Close menu by tapping outside (overlay)
  await page.getByTestId('menu-overlay').click();
  await expect(nav).toBeHidden();
});

test('bottom sheet slides up on mobile', async ({ page }) => {
  await page.goto('/products/1');

  await page.getByRole('button', { name: 'Add to cart' }).click();

  // Bottom sheet appears with cart summary
  const bottomSheet = page.getByTestId('bottom-sheet');
  await expect(bottomSheet).toBeVisible();
  await expect(bottomSheet).toContainText('Added to cart');

  // Dismiss by swiping down
  const box = await bottomSheet.boundingBox();
  if (box) {
    const startX = box.x + box.width / 2;
    const startY = box.y + 20;
    await page.mouse.move(startX, startY);
    await page.mouse.down();
    await page.mouse.move(startX, startY + 300, { steps: 10 });
    await page.mouse.up();
  }

  await expect(bottomSheet).toBeHidden();
});

test('pull to refresh reloads content', async ({ page }) => {
  await page.goto('/feed');

  // Store initial first item text
  const firstItem = page.getByRole('listitem').first();
  const initialText = await firstItem.textContent();

  // Pull-to-refresh: swipe down from top of scrollable area
  const feed = page.getByTestId('feed-container');
  const box = await feed.boundingBox();

  if (box) {
    await page.mouse.move(box.x + box.width / 2, box.y + 10);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width / 2, box.y + 250, { steps: 15 });
    await page.mouse.up();
  }

  // Wait for refresh indicator and then content reload
  await expect(page.getByTestId('refresh-spinner')).toBeVisible();
  await expect(page.getByTestId('refresh-spinner')).toBeHidden();
});

test('sticky mobile header remains visible on scroll', async ({ page }) => {
  await page.goto('/products');

  const header = page.getByRole('banner');

  // Scroll down significantly
  await page.evaluate(() => window.scrollTo(0, 2000));

  // Header should remain visible (sticky positioning)
  await expect(header).toBeVisible();
  await expect(header).toBeInViewport();
});
```

#### JavaScript

```javascript
// tests/mobile-ui.spec.js
const { test, expect, devices } = require('@playwright/test');

test.use({ ...devices['iPhone 14'] });

test('hamburger menu opens and closes', async ({ page }) => {
  await page.goto('/');

  const menuButton = page.getByRole('button', { name: 'Menu' });
  const nav = page.getByRole('navigation', { name: 'Main' });

  await expect(nav).toBeHidden();
  await menuButton.click();
  await expect(nav).toBeVisible();

  await expect(nav.getByRole('link', { name: 'Home' })).toBeVisible();
  await expect(nav.getByRole('link', { name: 'Products' })).toBeVisible();
  await expect(nav.getByRole('link', { name: 'Account' })).toBeVisible();

  await page.getByTestId('menu-overlay').click();
  await expect(nav).toBeHidden();
});

test('bottom sheet slides up on mobile', async ({ page }) => {
  await page.goto('/products/1');

  await page.getByRole('button', { name: 'Add to cart' }).click();

  const bottomSheet = page.getByTestId('bottom-sheet');
  await expect(bottomSheet).toBeVisible();
  await expect(bottomSheet).toContainText('Added to cart');

  const box = await bottomSheet.boundingBox();
  if (box) {
    const startX = box.x + box.width / 2;
    const startY = box.y + 20;
    await page.mouse.move(startX, startY);
    await page.mouse.down();
    await page.mouse.move(startX, startY + 300, { steps: 10 });
    await page.mouse.up();
  }

  await expect(bottomSheet).toBeHidden();
});

test('sticky mobile header remains visible on scroll', async ({ page }) => {
  await page.goto('/products');

  const header = page.getByRole('banner');
  await page.evaluate(() => window.scrollTo(0, 2000));
  await expect(header).toBeVisible();
  await expect(header).toBeInViewport();
});
```

### 5. Geolocation

**Use when**: Testing location-dependent features -- store finders, delivery zones, weather widgets, location-based pricing.
**Avoid when**: The feature does not use the Geolocation API. If it uses IP-based location, mock the API response instead.

#### TypeScript

```typescript
// playwright.config.ts -- set geolocation per project
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  projects: [
    {
      name: 'mobile-nyc',
      use: {
        ...devices['iPhone 14'],
        geolocation: { latitude: 40.7128, longitude: -74.0060 },
        permissions: ['geolocation'],
      },
    },
    {
      name: 'mobile-london',
      use: {
        ...devices['iPhone 14'],
        geolocation: { latitude: 51.5074, longitude: -0.1278 },
        permissions: ['geolocation'],
        locale: 'en-GB',
        timezoneId: 'Europe/London',
      },
    },
  ],
});
```

```typescript
// tests/store-locator.spec.ts
import { test, expect } from '@playwright/test';

test('shows nearby stores based on geolocation', async ({ page, context }) => {
  // Geolocation is already set via project config above.
  // To override in a specific test:
  await context.setGeolocation({ latitude: 34.0522, longitude: -118.2437 }); // Los Angeles

  await page.goto('/store-locator');
  await page.getByRole('button', { name: 'Use my location' }).click();

  // Verify the app uses the mocked location
  await expect(page.getByText('Stores near Los Angeles')).toBeVisible();
  await expect(page.getByRole('listitem')).toHaveCount(5); // nearest 5 stores
});

test('geolocation updates in real time', async ({ page, context }) => {
  await context.setGeolocation({ latitude: 40.7128, longitude: -74.0060 });
  await page.goto('/delivery-tracker');

  await expect(page.getByText('New York')).toBeVisible();

  // Simulate user moving to a new location
  await context.setGeolocation({ latitude: 40.7580, longitude: -73.9855 }); // Times Square

  // Trigger a location refresh (app-specific)
  await page.getByRole('button', { name: 'Refresh location' }).click();
  await expect(page.getByText('Times Square')).toBeVisible();
});

test('handles geolocation permission denied', async ({ page, context }) => {
  // Clear geolocation permissions to simulate denial
  await context.clearPermissions();
  await page.goto('/store-locator');

  await page.getByRole('button', { name: 'Use my location' }).click();

  // App should show fallback UI
  await expect(page.getByText('Location access denied')).toBeVisible();
  await expect(page.getByLabel('Enter your zip code')).toBeVisible();
});
```

#### JavaScript

```javascript
// tests/store-locator.spec.js
const { test, expect } = require('@playwright/test');

test('shows nearby stores based on geolocation', async ({ page, context }) => {
  await context.setGeolocation({ latitude: 34.0522, longitude: -118.2437 });

  await page.goto('/store-locator');
  await page.getByRole('button', { name: 'Use my location' }).click();

  await expect(page.getByText('Stores near Los Angeles')).toBeVisible();
  await expect(page.getByRole('listitem')).toHaveCount(5);
});

test('geolocation updates in real time', async ({ page, context }) => {
  await context.setGeolocation({ latitude: 40.7128, longitude: -74.0060 });
  await page.goto('/delivery-tracker');

  await expect(page.getByText('New York')).toBeVisible();

  await context.setGeolocation({ latitude: 40.7580, longitude: -73.9855 });
  await page.getByRole('button', { name: 'Refresh location' }).click();
  await expect(page.getByText('Times Square')).toBeVisible();
});

test('handles geolocation permission denied', async ({ page, context }) => {
  await context.clearPermissions();
  await page.goto('/store-locator');

  await page.getByRole('button', { name: 'Use my location' }).click();

  await expect(page.getByText('Location access denied')).toBeVisible();
  await expect(page.getByLabel('Enter your zip code')).toBeVisible();
});
```

### 6. Multi-Project Responsive Testing

**Use when**: Running the same tests across desktop and mobile browsers in parallel. The standard approach for responsive apps.
**Avoid when**: Your app is desktop-only or mobile-only.

#### TypeScript

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,

  projects: [
    // ── Desktop ────────────────────────────────────────────
    {
      name: 'desktop-chrome',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'desktop-firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'desktop-safari',
      use: { ...devices['Desktop Safari'] },
    },

    // ── Mobile ─────────────────────────────────────────────
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 7'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 14'] },
    },

    // ── Tablet ─────────────────────────────────────────────
    {
      name: 'tablet',
      use: { ...devices['iPad Pro 11'] },
    },
  ],
});
```

```typescript
// tests/responsive-checkout.spec.ts
import { test, expect } from '@playwright/test';

test('checkout works across all viewports', async ({ page, isMobile }) => {
  await page.goto('/products');

  // Add item -- same action on all viewports
  await page.getByRole('button', { name: 'Add to cart' }).first().click();

  // Navigate to cart
  if (isMobile) {
    // Mobile: cart link may be in hamburger or bottom nav
    await page.getByRole('link', { name: 'Cart' }).click();
  } else {
    // Desktop: cart icon in header
    await page.getByRole('link', { name: /Cart \(\d+\)/ }).click();
  }

  await page.waitForURL('**/cart');
  await expect(page.getByRole('heading', { name: 'Your cart' })).toBeVisible();

  // Proceed to checkout
  await page.getByRole('link', { name: 'Checkout' }).click();
  await page.waitForURL('**/checkout');

  // Fill form -- same fields on all viewports
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Card number').fill('4242424242424242');
  await page.getByRole('button', { name: 'Pay now' }).click();

  await expect(page.getByText('Order confirmed')).toBeVisible();
});
```

```bash
# Run desktop projects only
npx playwright test --project=desktop-chrome --project=desktop-firefox --project=desktop-safari

# Run mobile projects only
npx playwright test --project=mobile-chrome --project=mobile-safari

# Run specific test file on all projects
npx playwright test tests/responsive-checkout.spec.ts

# CI optimization: mobile + desktop-chrome on PRs, all browsers on main
# In CI config:
# PR:   npx playwright test --project=desktop-chrome --project=mobile-chrome --project=mobile-safari
# Main: npx playwright test
```

#### JavaScript

```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,

  projects: [
    {
      name: 'desktop-chrome',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'desktop-firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'desktop-safari',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 7'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 14'] },
    },
    {
      name: 'tablet',
      use: { ...devices['iPad Pro 11'] },
    },
  ],
});
```

```javascript
// tests/responsive-checkout.spec.js
const { test, expect } = require('@playwright/test');

test('checkout works across all viewports', async ({ page, isMobile }) => {
  await page.goto('/products');

  await page.getByRole('button', { name: 'Add to cart' }).first().click();

  if (isMobile) {
    await page.getByRole('link', { name: 'Cart' }).click();
  } else {
    await page.getByRole('link', { name: /Cart \(\d+\)/ }).click();
  }

  await page.waitForURL('**/cart');
  await expect(page.getByRole('heading', { name: 'Your cart' })).toBeVisible();

  await page.getByRole('link', { name: 'Checkout' }).click();
  await page.waitForURL('**/checkout');

  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Card number').fill('4242424242424242');
  await page.getByRole('button', { name: 'Pay now' }).click();

  await expect(page.getByText('Order confirmed')).toBeVisible();
});
```

### 7. Responsive Breakpoint Testing

**Use when**: Systematically verifying layout behavior at every major CSS breakpoint. Best used alongside visual regression testing.
**Avoid when**: You only need one or two viewport sizes -- just use `test.use()` overrides instead.

#### TypeScript

```typescript
// tests/fixtures/responsive.fixture.ts
import { test as base, expect } from '@playwright/test';

type Breakpoint = {
  name: string;
  width: number;
  height: number;
  isMobileExpected: boolean;
};

const BREAKPOINTS: Breakpoint[] = [
  { name: 'xs',  width: 320,  height: 568, isMobileExpected: true },
  { name: 'sm',  width: 640,  height: 800, isMobileExpected: true },
  { name: 'md',  width: 768,  height: 1024, isMobileExpected: false },
  { name: 'lg',  width: 1024, height: 768, isMobileExpected: false },
  { name: 'xl',  width: 1280, height: 800, isMobileExpected: false },
  { name: '2xl', width: 1440, height: 900, isMobileExpected: false },
];

// Custom fixture that runs a test at every breakpoint
export const test = base.extend<{ forEachBreakpoint: void }>({
  forEachBreakpoint: [async ({ page }, use, testInfo) => {
    // This fixture is used as a tag -- actual breakpoint iteration is done via test.describe
    await use();
  }, { auto: false }],
});

// Helper: create a describe block that tests every breakpoint
export function describeBreakpoints(
  title: string,
  fn: (bp: Breakpoint) => void
) {
  for (const bp of BREAKPOINTS) {
    base.describe(`${title} @ ${bp.name} (${bp.width}px)`, () => {
      base.use({ viewport: { width: bp.width, height: bp.height } });
      fn(bp);
    });
  }
}

export { expect, BREAKPOINTS };
```

```typescript
// tests/responsive-grid.spec.ts
import { test, expect, describeBreakpoints } from './fixtures/responsive.fixture';

describeBreakpoints('product grid', (bp) => {
  test('shows correct number of columns', async ({ page }) => {
    await page.goto('/products');

    const grid = page.getByTestId('product-grid');
    const columns = await grid.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return style.gridTemplateColumns.split(' ').length;
    });

    if (bp.width < 640) {
      expect(columns).toBe(1);     // xs: single column
    } else if (bp.width < 1024) {
      expect(columns).toBe(2);     // sm-md: two columns
    } else {
      expect(columns).toBe(4);     // lg+: four columns
    }
  });

  test('no content overflow', async ({ page }) => {
    await page.goto('/products');

    const hasOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(hasOverflow).toBe(false);
  });
});
```

#### JavaScript

```javascript
// tests/fixtures/responsive.fixture.js
const { test: base, expect } = require('@playwright/test');

const BREAKPOINTS = [
  { name: 'xs',  width: 320,  height: 568, isMobileExpected: true },
  { name: 'sm',  width: 640,  height: 800, isMobileExpected: true },
  { name: 'md',  width: 768,  height: 1024, isMobileExpected: false },
  { name: 'lg',  width: 1024, height: 768, isMobileExpected: false },
  { name: 'xl',  width: 1280, height: 800, isMobileExpected: false },
  { name: '2xl', width: 1440, height: 900, isMobileExpected: false },
];

function describeBreakpoints(title, fn) {
  for (const bp of BREAKPOINTS) {
    base.describe(`${title} @ ${bp.name} (${bp.width}px)`, () => {
      base.use({ viewport: { width: bp.width, height: bp.height } });
      fn(bp);
    });
  }
}

module.exports = { test: base, expect, BREAKPOINTS, describeBreakpoints };
```

```javascript
// tests/responsive-grid.spec.js
const { test, expect, describeBreakpoints } = require('./fixtures/responsive.fixture');

describeBreakpoints('product grid', (bp) => {
  test('shows correct number of columns', async ({ page }) => {
    await page.goto('/products');

    const grid = page.getByTestId('product-grid');
    const columns = await grid.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return style.gridTemplateColumns.split(' ').length;
    });

    if (bp.width < 640) {
      expect(columns).toBe(1);
    } else if (bp.width < 1024) {
      expect(columns).toBe(2);
    } else {
      expect(columns).toBe(4);
    }
  });

  test('no content overflow', async ({ page }) => {
    await page.goto('/products');

    const hasOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(hasOverflow).toBe(false);
  });
});
```

### 8. Orientation Testing

**Use when**: Testing portrait vs landscape layouts. Critical for tablet apps, media players, dashboards, and any app that adapts to orientation.
**Avoid when**: Your app does not change layout based on orientation (purely responsive to width only -- test with custom viewports instead).

#### TypeScript

```typescript
// tests/orientation.spec.ts
import { test, expect, devices } from '@playwright/test';

test.describe('iPad orientation changes', () => {
  test.use({ ...devices['iPad Pro 11'] });

  test('dashboard adjusts layout in landscape', async ({ page }) => {
    // Start in portrait (834x1194 -- default for iPad Pro 11)
    await page.goto('/dashboard');

    // Portrait: sidebar collapses, chart stacks vertically
    await expect(page.getByTestId('sidebar')).toHaveCSS('position', 'fixed');

    // Switch to landscape by changing viewport
    await page.setViewportSize({ width: 1194, height: 834 });

    // Landscape: sidebar visible inline, charts side-by-side
    await expect(page.getByTestId('sidebar')).toHaveCSS('position', 'relative');
  });

  test('video player switches to fullscreen in landscape', async ({ page }) => {
    await page.goto('/videos/1');

    // Portrait: video in inline player
    const player = page.getByTestId('video-player');
    const portraitBox = await player.boundingBox();

    // Switch to landscape
    await page.setViewportSize({ width: 1194, height: 834 });

    // Video should expand to fill width
    const landscapeBox = await player.boundingBox();
    expect(landscapeBox!.width).toBeGreaterThan(portraitBox!.width);
  });
});

test.describe('iPhone orientation changes', () => {
  test('portrait mode', () => {
    test.use({ ...devices['iPhone 14'] }); // 390x844
  });

  test('landscape mode', () => {
    test.use({ ...devices['iPhone 14 landscape'] }); // 844x390
  });
});

// Test both orientations with a loop
const orientations = [
  { name: 'portrait', device: devices['iPad Pro 11'] },
  { name: 'landscape', device: devices['iPad Pro 11 landscape'] },
];

for (const { name, device } of orientations) {
  test.describe(`form usability in ${name}`, () => {
    test.use({ ...device });

    test('all form fields are visible without scrolling', async ({ page }) => {
      await page.goto('/contact');

      const form = page.getByRole('form');
      await expect(form).toBeVisible();

      // Check form fits within viewport
      const formBox = await form.boundingBox();
      const viewport = page.viewportSize()!;
      expect(formBox!.width).toBeLessThanOrEqual(viewport.width);
    });
  });
}
```

#### JavaScript

```javascript
// tests/orientation.spec.js
const { test, expect, devices } = require('@playwright/test');

test.describe('iPad orientation changes', () => {
  test.use({ ...devices['iPad Pro 11'] });

  test('dashboard adjusts layout in landscape', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page.getByTestId('sidebar')).toHaveCSS('position', 'fixed');

    await page.setViewportSize({ width: 1194, height: 834 });

    await expect(page.getByTestId('sidebar')).toHaveCSS('position', 'relative');
  });

  test('video player switches to fullscreen in landscape', async ({ page }) => {
    await page.goto('/videos/1');

    const player = page.getByTestId('video-player');
    const portraitBox = await player.boundingBox();

    await page.setViewportSize({ width: 1194, height: 834 });

    const landscapeBox = await player.boundingBox();
    expect(landscapeBox.width).toBeGreaterThan(portraitBox.width);
  });
});

const orientations = [
  { name: 'portrait', device: devices['iPad Pro 11'] },
  { name: 'landscape', device: devices['iPad Pro 11 landscape'] },
];

for (const { name, device } of orientations) {
  test.describe(`form usability in ${name}`, () => {
    test.use({ ...device });

    test('all form fields are visible without scrolling', async ({ page }) => {
      await page.goto('/contact');

      const form = page.getByRole('form');
      await expect(form).toBeVisible();

      const formBox = await form.boundingBox();
      const viewport = page.viewportSize();
      expect(formBox.width).toBeLessThanOrEqual(viewport.width);
    });
  });
}
```

### 9. Mobile Performance

**Use when**: Simulating real-world mobile conditions -- slow 3G networks, underpowered CPUs. Critical for testing loading states, skeleton screens, and timeout handling.
**Avoid when**: Testing functional correctness only. Performance throttling slows down your test suite significantly.

#### TypeScript

```typescript
// tests/mobile-performance.spec.ts
import { test, expect, devices } from '@playwright/test';

test.describe('mobile on slow network', () => {
  test.use({ ...devices['Pixel 7'] });

  test('shows skeleton loader on slow 3G', async ({ page }) => {
    // Get the CDP session for network throttling (Chromium only)
    const cdpSession = await page.context().newCDPSession(page);

    // Simulate slow 3G: 500kbps download, 500kbps upload, 400ms RTT
    await cdpSession.send('Network.emulateNetworkConditions', {
      offline: false,
      downloadThroughput: (500 * 1024) / 8,  // bytes per second
      uploadThroughput: (500 * 1024) / 8,
      latency: 400,                            // ms
    });

    await page.goto('/products');

    // Skeleton screen should appear while content loads
    await expect(page.getByTestId('product-skeleton')).toBeVisible();

    // Eventually, real content replaces skeleton
    await expect(page.getByRole('listitem')).toHaveCount(12, { timeout: 30_000 });
    await expect(page.getByTestId('product-skeleton')).toBeHidden();
  });

  test('shows offline message when network drops', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

    // Drop network entirely
    await page.context().setOffline(true);

    // Try to navigate -- should show offline message
    await page.getByRole('link', { name: 'Settings' }).click();
    await expect(page.getByText(/you.*offline|no.*connection/i)).toBeVisible();

    // Restore network
    await page.context().setOffline(false);
    await page.reload();
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
  });

  test('images lazy-load on slow connections', async ({ page }) => {
    const cdpSession = await page.context().newCDPSession(page);
    await cdpSession.send('Network.emulateNetworkConditions', {
      offline: false,
      downloadThroughput: (1000 * 1024) / 8,
      uploadThroughput: (500 * 1024) / 8,
      latency: 200,
    });

    await page.goto('/gallery');

    // Images below the fold should have loading="lazy" and not load immediately
    const belowFoldImages = page.locator('img[loading="lazy"]');
    const count = await belowFoldImages.count();
    expect(count).toBeGreaterThan(0);

    // Scroll to trigger lazy loading
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await expect(belowFoldImages.first()).toHaveJSProperty('complete', true);
  });

  test('CPU throttling shows performance impact', async ({ page }) => {
    const cdpSession = await page.context().newCDPSession(page);

    // Simulate 4x CPU slowdown (typical mid-range mobile device)
    await cdpSession.send('Emulation.setCPUThrottlingRate', { rate: 4 });

    await page.goto('/');

    // Measure time to interactive
    const tti = await page.evaluate(() => {
      const entries = performance.getEntriesByType('navigation') as PerformanceNavigationTiming[];
      return entries[0]?.domInteractive ?? 0;
    });

    // Assert TTI is within acceptable range for throttled mobile
    expect(tti).toBeLessThan(5000);

    // Reset throttling
    await cdpSession.send('Emulation.setCPUThrottlingRate', { rate: 1 });
  });
});
```

#### JavaScript

```javascript
// tests/mobile-performance.spec.js
const { test, expect, devices } = require('@playwright/test');

test.describe('mobile on slow network', () => {
  test.use({ ...devices['Pixel 7'] });

  test('shows skeleton loader on slow 3G', async ({ page }) => {
    const cdpSession = await page.context().newCDPSession(page);

    await cdpSession.send('Network.emulateNetworkConditions', {
      offline: false,
      downloadThroughput: (500 * 1024) / 8,
      uploadThroughput: (500 * 1024) / 8,
      latency: 400,
    });

    await page.goto('/products');

    await expect(page.getByTestId('product-skeleton')).toBeVisible();
    await expect(page.getByRole('listitem')).toHaveCount(12, { timeout: 30_000 });
    await expect(page.getByTestId('product-skeleton')).toBeHidden();
  });

  test('shows offline message when network drops', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

    await page.context().setOffline(true);

    await page.getByRole('link', { name: 'Settings' }).click();
    await expect(page.getByText(/you.*offline|no.*connection/i)).toBeVisible();

    await page.context().setOffline(false);
    await page.reload();
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
  });

  test('CPU throttling shows performance impact', async ({ page }) => {
    const cdpSession = await page.context().newCDPSession(page);

    await cdpSession.send('Emulation.setCPUThrottlingRate', { rate: 4 });

    await page.goto('/');

    const tti = await page.evaluate(() => {
      const entries = performance.getEntriesByType('navigation');
      return entries[0]?.domInteractive ?? 0;
    });

    expect(tti).toBeLessThan(5000);
    await cdpSession.send('Emulation.setCPUThrottlingRate', { rate: 1 });
  });
});
```

### 10. PWA Mobile Testing

**Use when**: Testing Progressive Web App features -- service workers, install prompts, offline mode, push notifications on mobile.
**Avoid when**: Your app is not a PWA. For general offline testing, see the network offline pattern in Pattern 9.

#### TypeScript

```typescript
// tests/pwa-mobile.spec.ts
import { test, expect, devices } from '@playwright/test';

test.use({ ...devices['Pixel 7'] });

test('service worker registers and caches resources', async ({ page }) => {
  await page.goto('/');

  // Wait for service worker to register
  const swRegistered = await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.ready;
    return registration.active?.state === 'activated';
  });
  expect(swRegistered).toBe(true);

  // Verify critical resources are cached
  const cacheContents = await page.evaluate(async () => {
    const cache = await caches.open('app-shell-v1');
    const keys = await cache.keys();
    return keys.map((req) => new URL(req.url).pathname);
  });

  expect(cacheContents).toContain('/');
  expect(cacheContents).toContain('/offline.html');
});

test('app works offline after initial load', async ({ page }) => {
  // Load the app online first -- service worker caches resources
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Home' })).toBeVisible();

  // Wait for service worker to finish caching
  await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.ready;
    // Wait for the service worker to activate
    if (registration.active?.state !== 'activated') {
      await new Promise<void>((resolve) => {
        registration.active?.addEventListener('statechange', () => {
          if (registration.active?.state === 'activated') resolve();
        });
      });
    }
  });

  // Go offline
  await page.context().setOffline(true);

  // Navigate to a cached page
  await page.goto('/about');

  // Cached page should render
  await expect(page.getByRole('heading', { name: 'About' })).toBeVisible();
});

test('offline fallback page shows when uncached route is accessed', async ({ page }) => {
  await page.goto('/');

  // Wait for service worker
  await page.evaluate(() => navigator.serviceWorker.ready);

  // Go offline and navigate to an uncached route
  await page.context().setOffline(true);
  await page.goto('/uncached-page');

  // Should show the offline fallback page
  await expect(page.getByText(/offline|no.*connection/i)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
});

test('app prompts to install on mobile', async ({ page, context }) => {
  // Listen for the beforeinstallprompt event
  await page.goto('/');

  const installPromptFired = await page.evaluate(() => {
    return new Promise<boolean>((resolve) => {
      // Check if the event has already fired
      window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault(); // Prevent auto-prompt
        resolve(true);
      });

      // If PWA criteria are met, the event fires automatically
      // Timeout after 5s if it doesn't fire
      setTimeout(() => resolve(false), 5000);
    });
  });

  // Note: beforeinstallprompt only fires in Chromium and when PWA criteria are met
  // This test validates the event handler, not the browser chrome UI
  if (installPromptFired) {
    // App should show a custom install banner
    await expect(page.getByTestId('install-banner')).toBeVisible();
    await page.getByRole('button', { name: 'Install app' }).click();
  }
});

test('push notification permission request on mobile', async ({ page, context }) => {
  // Grant notification permission
  await context.grantPermissions(['notifications']);

  await page.goto('/settings/notifications');

  await page.getByRole('button', { name: 'Enable notifications' }).click();

  // Verify the app registered for push
  const pushSubscription = await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    return subscription !== null;
  });

  expect(pushSubscription).toBe(true);
  await expect(page.getByText('Notifications enabled')).toBeVisible();
});
```

#### JavaScript

```javascript
// tests/pwa-mobile.spec.js
const { test, expect, devices } = require('@playwright/test');

test.use({ ...devices['Pixel 7'] });

test('service worker registers and caches resources', async ({ page }) => {
  await page.goto('/');

  const swRegistered = await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.ready;
    return registration.active?.state === 'activated';
  });
  expect(swRegistered).toBe(true);

  const cacheContents = await page.evaluate(async () => {
    const cache = await caches.open('app-shell-v1');
    const keys = await cache.keys();
    return keys.map((req) => new URL(req.url).pathname);
  });

  expect(cacheContents).toContain('/');
  expect(cacheContents).toContain('/offline.html');
});

test('app works offline after initial load', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Home' })).toBeVisible();

  await page.evaluate(async () => {
    await navigator.serviceWorker.ready;
  });

  await page.context().setOffline(true);
  await page.goto('/about');

  await expect(page.getByRole('heading', { name: 'About' })).toBeVisible();
});

test('offline fallback page shows when uncached route is accessed', async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => navigator.serviceWorker.ready);

  await page.context().setOffline(true);
  await page.goto('/uncached-page');

  await expect(page.getByText(/offline|no.*connection/i)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
});

test('push notification permission request on mobile', async ({ page, context }) => {
  await context.grantPermissions(['notifications']);

  await page.goto('/settings/notifications');

  await page.getByRole('button', { name: 'Enable notifications' }).click();

  const pushSubscription = await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    return subscription !== null;
  });

  expect(pushSubscription).toBe(true);
  await expect(page.getByText('Notifications enabled')).toBeVisible();
});
```

## Decision Guide

| Question | Answer | Approach |
|---|---|---|
| Need to test how app looks on iPhone 14? | Yes | Use `devices['iPhone 14']` -- gets viewport, UA, touch, scale factor in one shot |
| Need to test a CSS breakpoint at 768px? | Yes | Use `test.use({ viewport: { width: 768, height: 1024 } })` -- simpler, no UA change |
| Need to test both portrait and landscape? | Yes | Use named device + landscape variant: `devices['iPad Pro 11']` and `devices['iPad Pro 11 landscape']` |
| Need realistic mobile performance? | Yes | Use CDP `Network.emulateNetworkConditions` + `Emulation.setCPUThrottlingRate` (Chromium only) |
| Need to test touch gestures? | Yes | Use device profile with `hasTouch: true`, then use `tap()`, mouse gestures for swipe |
| Need to test geolocation? | Yes | Set `geolocation` and `permissions: ['geolocation']` in context options |
| Need pixel-perfect mobile testing? | No -- use real devices | Playwright emulation approximates; font rendering and native UI differ from real hardware |
| Which devices to test by default? | Start with 3 | `Desktop Chrome` + `Pixel 7` (Android) + `iPhone 14` (iOS). Add tablet if your app has a tablet layout. |
| When to add more device projects? | When bugs escape | If users report device-specific bugs, add that device profile permanently |
| Run all devices on every PR? | No | Run desktop + one mobile on PRs. Run all devices on main branch merges. |
| Device emulation vs custom viewport? | Depends on goal | Emulation: testing real-world device behavior. Custom viewport: testing CSS breakpoints. |
| Should I test every screen size? | No | Test your actual CSS breakpoints, plus smallest (320px) and largest (1440px+) supported sizes |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Only testing at 1280x720 desktop | Misses all mobile and tablet layout bugs; most web traffic is mobile | Add at least `Pixel 7` and `iPhone 14` projects |
| Using device emulation for pixel-perfect testing | Emulation approximates real devices -- font rendering, sub-pixel antialiasing, and native browser chrome differ | Use emulation for layout and interaction testing; use real device labs (BrowserStack, Sauce Labs) for pixel-perfect validation |
| Ignoring touch interactions | Mobile users tap, swipe, and long-press; `click()` alone may not trigger touch-specific event handlers | Use `tap()` on touch device profiles; test swipe gestures with mouse move sequences |
| Not testing orientation changes | Users rotate tablets and phones; layouts may break in landscape | Test both portrait and landscape with device variants or `page.setViewportSize()` |
| `page.setViewportSize()` without `hasTouch: true` | Viewport is small but browser reports no touch support -- `@media (hover: hover)` still matches desktop | Use device profiles or explicitly set `hasTouch: true` in `test.use()` |
| Hardcoding `isMobile` checks in every test | Duplicates logic, hard to maintain; tests become brittle | Use page objects that abstract mobile vs desktop behavior behind methods |
| Testing mobile layout with `visibility: hidden` checks only | Element may still take up space; CSS may use `display: none` or `transform: translateX(-100%)` | Use `toBeHidden()` (checks not visible) or `toHaveCSS('display', 'none')` for specific CSS behavior |
| Running 10+ device projects on every CI run | Massive CI time and cost with diminishing returns beyond 3-4 devices | Pick representative devices: one Android phone, one iPhone, one tablet, and desktop browsers |
| Network throttling in every test | Slows entire suite dramatically for minimal extra coverage | Create a separate `mobile-perf` project or tag performance tests with `@slow` and run them separately |
| `await page.waitForTimeout(2000)` after orientation change | Arbitrary delay; layout reflow may be faster or slower | `await expect(locator).toHaveCSS('property', 'value')` -- assertion auto-retries until layout settles |
| Testing geolocation without setting permissions | Browser blocks geolocation silently; test sees no location data and passes incorrectly | Always set `permissions: ['geolocation']` alongside `geolocation` coordinates |
| CDP throttling on Firefox or WebKit | CDP sessions are Chromium-only; test will throw on other browsers | Guard CDP calls with a browser check or use Chromium-only projects for performance tests |

## Troubleshooting

### `tap()` throws "Page.tap: Not supported" error

**Cause**: The browser context was created without `hasTouch: true`. Device profiles set this automatically, but custom viewport configurations do not.

```typescript
// Wrong -- custom viewport without touch support
test.use({ viewport: { width: 375, height: 667 } });
test('tap fails', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button').tap(); // Error: Not supported
});

// Fix -- enable touch explicitly
test.use({
  viewport: { width: 375, height: 667 },
  hasTouch: true,
});
test('tap works', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button').tap(); // Works
});

// Or use a device profile that includes hasTouch
test.use({ ...devices['iPhone 14'] });
```

### `isMobile` is always `false`

**Cause**: `isMobile` is set by the device profile's `isMobile` property, not by viewport size. Custom viewports do not set it.

```typescript
// isMobile is false here -- no device profile used
test.use({ viewport: { width: 375, height: 667 } });

test('isMobile is false', async ({ page, isMobile }) => {
  console.log(isMobile); // false
});

// Fix: use a device profile, or set isMobile explicitly
test.use({
  viewport: { width: 375, height: 667 },
  isMobile: true,
  hasTouch: true,
});

test('isMobile is true', async ({ page, isMobile }) => {
  console.log(isMobile); // true
});
```

### Geolocation not working -- location remains default

**Cause**: Missing `permissions: ['geolocation']` in context options. The browser silently denies the Geolocation API without this permission.

```typescript
// Wrong -- geolocation set but no permission granted
test.use({
  geolocation: { latitude: 40.7128, longitude: -74.0060 },
  // Missing: permissions: ['geolocation']
});

// Fix
test.use({
  geolocation: { latitude: 40.7128, longitude: -74.0060 },
  permissions: ['geolocation'],
});
```

### CDP session throws on Firefox/WebKit

**Cause**: `page.context().newCDPSession(page)` is Chromium-only. Firefox and WebKit do not support CDP.

```typescript
// Wrong -- crashes on Firefox and WebKit
test('throttle network', async ({ page }) => {
  const cdp = await page.context().newCDPSession(page); // Throws on non-Chromium
});

// Fix -- guard with browser name check
test('throttle network', async ({ page, browserName }) => {
  test.skip(browserName !== 'chromium', 'CDP throttling is Chromium-only');

  const cdp = await page.context().newCDPSession(page);
  await cdp.send('Network.emulateNetworkConditions', {
    offline: false,
    downloadThroughput: (500 * 1024) / 8,
    uploadThroughput: (500 * 1024) / 8,
    latency: 400,
  });
});

// Alternative -- use context.setOffline() which works on all browsers
test('offline mode', async ({ page }) => {
  await page.context().setOffline(true); // Works everywhere
});
```

### Viewport change does not trigger CSS media queries

**Cause**: `page.setViewportSize()` changes the viewport but does not trigger `resize` or `orientationchange` events in some frameworks that rely on JavaScript-based responsive logic rather than CSS media queries.

```typescript
// If media queries don't fire after setViewportSize, dispatch manually
await page.setViewportSize({ width: 375, height: 667 });
await page.evaluate(() => window.dispatchEvent(new Event('resize')));

// Better: use the viewport in test.use() so it's set before page load
test.use({ viewport: { width: 375, height: 667 } });
```

### Service worker not registering in tests

**Cause**: Service workers require HTTPS or localhost. Playwright's default `baseURL` of `http://localhost:3000` works, but other HTTP origins do not.

```typescript
// Ensure your baseURL is localhost or HTTPS
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'http://localhost:3000',          // Works for service workers
    // baseURL: 'http://192.168.1.100:3000',   // Does NOT work -- not localhost
  },
});

// If testing against a non-localhost server, use HTTPS
// or use serviceWorkers: 'allow' (default) in context options
```

## Related

- [core/configuration.md](configuration.md) -- project setup with device profiles and multi-project config
- [core/visual-regression.md](visual-regression.md) -- combine responsive testing with screenshot comparison across viewports
- [core/network-mocking.md](network-mocking.md) -- mock API responses alongside mobile testing
- [core/service-workers-and-pwa.md](service-workers-and-pwa.md) -- in-depth PWA testing beyond mobile context
- [core/performance-testing.md](performance-testing.md) -- comprehensive performance testing including mobile metrics
- [core/browser-apis.md](browser-apis.md) -- geolocation, permissions, and other browser APIs in detail
- [ci/projects-and-dependencies.md](../ci/projects-and-dependencies.md) -- advanced multi-project patterns for responsive testing matrices
