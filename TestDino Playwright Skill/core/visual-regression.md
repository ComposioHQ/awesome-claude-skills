# Visual Regression Testing

> **When to use**: Catching unintended visual changes -- layout shifts, style regressions, broken responsive designs, theme corruption -- that functional assertions miss. Visual tests answer "does it still look right?" after code changes.
> **Prerequisites**: [core/configuration.md](configuration.md) for project setup, [core/assertions-and-waiting.md](assertions-and-waiting.md) for assertion basics.

## Quick Reference

```typescript
// Page screenshot -- compare entire viewport
await expect(page).toHaveScreenshot();

// Element screenshot -- compare a specific component
await expect(page.getByTestId('pricing-card')).toHaveScreenshot();

// Named snapshot -- explicit file name
await expect(page).toHaveScreenshot('homepage-hero.png');

// With threshold -- allow minor pixel differences
await expect(page).toHaveScreenshot({ maxDiffPixelRatio: 0.01 });

// Mask dynamic content -- hide timestamps, avatars, ads
await expect(page).toHaveScreenshot({
  mask: [page.getByTestId('timestamp'), page.getByRole('img', { name: 'Avatar' })],
});

// Disable animations -- prevent flaky diffs from CSS transitions
await expect(page).toHaveScreenshot({ animations: 'disabled' });

// Update baselines (CLI)
npx playwright test --update-snapshots
```

## Patterns

### 1. Screenshot Comparison Basics

**Use when**: Verifying that a page or component renders correctly after code changes. Best for pages with stable layouts -- landing pages, dashboards, settings panels.
**Avoid when**: The page is highly dynamic with real-time data, live feeds, or content that changes on every load. Use functional assertions instead.

Playwright compares a screenshot taken during the test against a stored baseline (golden) image. On first run, the baseline is created. On subsequent runs, differences cause the test to fail with a visual diff report.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('homepage renders correctly', async ({ page }) => {
  await page.goto('/');

  // Full page screenshot comparison
  await expect(page).toHaveScreenshot('homepage.png');
});

test('pricing card matches design', async ({ page }) => {
  await page.goto('/pricing');

  // Element-level screenshot -- scoped to a single component
  const card = page.getByTestId('pro-plan-card');
  await expect(card).toHaveScreenshot('pro-plan-card.png');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('homepage renders correctly', async ({ page }) => {
  await page.goto('/');

  await expect(page).toHaveScreenshot('homepage.png');
});

test('pricing card matches design', async ({ page }) => {
  await page.goto('/pricing');

  const card = page.getByTestId('pro-plan-card');
  await expect(card).toHaveScreenshot('pro-plan-card.png');
});
```

Snapshots are stored alongside tests by default in a folder named `<test-file-name>-snapshots/`. The folder structure includes the project name and platform:

```
tests/
  homepage.spec.ts
  homepage.spec.ts-snapshots/
    homepage-chromium-linux.png
    homepage-chromium-darwin.png
```

### 2. Configuring Thresholds

**Use when**: Your UI has minor rendering differences between runs -- anti-aliasing, font hinting, sub-pixel rendering. Thresholds prevent false failures from pixel-level noise.
**Avoid when**: You want pixel-perfect comparisons (design-system component libraries, icon rendering). Keep thresholds at zero.

Three knobs control comparison sensitivity:

| Option | What it controls | Good default |
|---|---|---|
| `maxDiffPixels` | Absolute number of pixels that can differ | `100` for full pages, `10` for components |
| `maxDiffPixelRatio` | Fraction of total pixels that can differ (0-1) | `0.01` (1%) for full pages |
| `threshold` | Per-pixel color difference tolerance (0-1) | `0.2` for most UIs, `0.1` for design systems |

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('dashboard allows minor rendering variance', async ({ page }) => {
  await page.goto('/dashboard');

  // Allow up to 1% of pixels to differ
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixelRatio: 0.01,
  });
});

test('icon renders pixel-perfect', async ({ page }) => {
  await page.goto('/icons');

  // Strict: zero tolerance
  await expect(page.getByTestId('logo')).toHaveScreenshot('logo.png', {
    maxDiffPixels: 0,
    threshold: 0,
  });
});

test('chart allows anti-aliasing differences', async ({ page }) => {
  await page.goto('/analytics');

  // Per-pixel color threshold + absolute pixel count cap
  await expect(page.getByTestId('revenue-chart')).toHaveScreenshot('revenue-chart.png', {
    threshold: 0.3,
    maxDiffPixels: 200,
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('dashboard allows minor rendering variance', async ({ page }) => {
  await page.goto('/dashboard');

  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixelRatio: 0.01,
  });
});

test('icon renders pixel-perfect', async ({ page }) => {
  await page.goto('/icons');

  await expect(page.getByTestId('logo')).toHaveScreenshot('logo.png', {
    maxDiffPixels: 0,
    threshold: 0,
  });
});

test('chart allows anti-aliasing differences', async ({ page }) => {
  await page.goto('/analytics');

  await expect(page.getByTestId('revenue-chart')).toHaveScreenshot('revenue-chart.png', {
    threshold: 0.3,
    maxDiffPixels: 200,
  });
});
```

**Global thresholds** in `playwright.config.ts`:

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  expect: {
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.01,
      threshold: 0.2,
      animations: 'disabled',
    },
  },
});
```

### 3. Full Page vs Element Screenshots

**Use when**: Deciding scope. Full page catches layout shifts and spacing regressions. Element screenshots isolate components and are more stable.
**Avoid when**: Neither -- use both strategically.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('full page screenshot catches layout shifts', async ({ page }) => {
  await page.goto('/');

  // Captures the visible viewport
  await expect(page).toHaveScreenshot('homepage-viewport.png');

  // Captures the entire scrollable page
  await expect(page).toHaveScreenshot('homepage-full.png', {
    fullPage: true,
  });
});

test('element screenshot isolates component changes', async ({ page }) => {
  await page.goto('/pricing');

  // Only the pricing table -- immune to header/footer changes
  await expect(page.getByRole('table')).toHaveScreenshot('pricing-table.png');

  // A specific card within the page
  await expect(page.getByTestId('enterprise-card')).toHaveScreenshot('enterprise-card.png');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('full page screenshot catches layout shifts', async ({ page }) => {
  await page.goto('/');

  await expect(page).toHaveScreenshot('homepage-viewport.png');

  await expect(page).toHaveScreenshot('homepage-full.png', {
    fullPage: true,
  });
});

test('element screenshot isolates component changes', async ({ page }) => {
  await page.goto('/pricing');

  await expect(page.getByRole('table')).toHaveScreenshot('pricing-table.png');
  await expect(page.getByTestId('enterprise-card')).toHaveScreenshot('enterprise-card.png');
});
```

**Rule of thumb**: Use element screenshots for components that change independently. Use full page screenshots for key landing pages and layouts where spacing between sections matters.

### 4. Masking Dynamic Content

**Use when**: The page contains content that changes between test runs -- timestamps, user avatars, ad slots, relative dates ("3 minutes ago"), random hero images, A/B test variants.
**Avoid when**: All content is deterministic. Masking adds maintenance overhead.

The `mask` option overlays a solid-colored box over specified locators before taking the screenshot. The masked region is excluded from comparison.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('dashboard with masked dynamic content', async ({ page }) => {
  await page.goto('/dashboard');

  await expect(page).toHaveScreenshot('dashboard.png', {
    mask: [
      page.getByTestId('current-time'),
      page.getByTestId('user-avatar'),
      page.getByTestId('live-visitor-count'),
      page.locator('.ad-banner'),
    ],
    maskColor: '#FF00FF', // visible magenta -- makes it obvious what's masked in reviews
  });
});

test('feed page with relative timestamps', async ({ page }) => {
  await page.goto('/feed');

  // Mask all relative time elements at once
  await expect(page).toHaveScreenshot('feed.png', {
    mask: [page.locator('time[datetime]')],
  });
});

test('profile page with user-generated content', async ({ page }) => {
  await page.goto('/profile/test-user');

  await expect(page).toHaveScreenshot('profile.png', {
    mask: [
      page.getByRole('img', { name: 'Profile photo' }),
      page.getByTestId('last-login'),
      page.getByTestId('member-since'),
    ],
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('dashboard with masked dynamic content', async ({ page }) => {
  await page.goto('/dashboard');

  await expect(page).toHaveScreenshot('dashboard.png', {
    mask: [
      page.getByTestId('current-time'),
      page.getByTestId('user-avatar'),
      page.getByTestId('live-visitor-count'),
      page.locator('.ad-banner'),
    ],
    maskColor: '#FF00FF',
  });
});

test('feed page with relative timestamps', async ({ page }) => {
  await page.goto('/feed');

  await expect(page).toHaveScreenshot('feed.png', {
    mask: [page.locator('time[datetime]')],
  });
});

test('profile page with user-generated content', async ({ page }) => {
  await page.goto('/profile/test-user');

  await expect(page).toHaveScreenshot('profile.png', {
    mask: [
      page.getByRole('img', { name: 'Profile photo' }),
      page.getByTestId('last-login'),
      page.getByTestId('member-since'),
    ],
  });
});
```

**Alternative: freeze dynamic content with JavaScript**

When masking is not sufficient (e.g., content affects layout), inject JavaScript to freeze the content:

```typescript
test('freeze clock before screenshot', async ({ page }) => {
  await page.goto('/dashboard');

  // Replace all dynamic timestamps with a fixed value
  await page.evaluate(() => {
    document.querySelectorAll('[data-testid="timestamp"]').forEach((el) => {
      el.textContent = 'Jan 1, 2025 12:00 PM';
    });
  });

  await expect(page).toHaveScreenshot('dashboard-frozen.png');
});
```

### 5. Animations Handling

**Use when**: Always. CSS animations and transitions are the number one cause of flaky visual diffs. A screenshot captured mid-animation will never match the baseline.
**Avoid when**: You are explicitly testing the animation itself (rare).

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('page renders without animation interference', async ({ page }) => {
  await page.goto('/');

  // Disables CSS animations and transitions before screenshotting
  await expect(page).toHaveScreenshot('homepage.png', {
    animations: 'disabled',
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('page renders without animation interference', async ({ page }) => {
  await page.goto('/');

  await expect(page).toHaveScreenshot('homepage.png', {
    animations: 'disabled',
  });
});
```

**Set globally** -- this should be the default for every project:

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  expect: {
    toHaveScreenshot: {
      animations: 'disabled',
    },
  },
});
```

When `animations: 'disabled'` is set, Playwright:
1. Injects a stylesheet that sets `* { animation-duration: 0s !important; transition-duration: 0s !important; }`.
2. Waits for any currently running animations to finish (forces them to their end state).
3. Takes the screenshot.

For JavaScript-driven animations (requestAnimationFrame, GSAP, Framer Motion), you may also need to wait for stability:

```typescript
test('page with JS animations', async ({ page }) => {
  await page.goto('/animated-landing');

  // Wait for the hero animation to settle
  await page.getByTestId('hero-section').waitFor({ state: 'visible' });
  await page.waitForTimeout(500); // last resort for JS animations -- use sparingly

  await expect(page).toHaveScreenshot('landing.png', {
    animations: 'disabled',
  });
});
```

### 6. Updating Snapshots

**Use when**: You have intentionally changed the UI and need to update the baselines. A design refresh, rebrand, new feature, or layout change.
**Avoid when**: The diff is unexpected -- investigate the cause before blindly updating.

```bash
# Update all snapshots
npx playwright test --update-snapshots

# Update snapshots for a specific test file
npx playwright test tests/homepage.spec.ts --update-snapshots

# Update snapshots for a specific project (browser)
npx playwright test --project=chromium --update-snapshots
```

**Workflow for reviewing snapshot changes:**

1. Run tests and observe failures in the HTML report:
   ```bash
   npx playwright test
   npx playwright show-report
   ```
   The report shows the expected image, actual image, and a diff image side-by-side.

2. If the changes are intentional, update the snapshots:
   ```bash
   npx playwright test --update-snapshots
   ```

3. Review the updated snapshots in your diff tool before committing:
   ```bash
   git diff --name-only  # see which snapshot files changed
   ```

4. Commit the updated snapshots with a clear message explaining why they changed.

**Tip**: Never run `--update-snapshots` in CI. Always update locally, review the diffs, and commit the new baselines.

**TypeScript -- helper for controlled updates**
```typescript
import { test, expect } from '@playwright/test';

// Tag visual tests so you can update them selectively
test('homepage visual @visual', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png', {
    animations: 'disabled',
  });
});

test('pricing visual @visual', async ({ page }) => {
  await page.goto('/pricing');
  await expect(page).toHaveScreenshot('pricing.png', {
    animations: 'disabled',
  });
});
```

```bash
# Update only visual tests
npx playwright test --grep @visual --update-snapshots
```

### 7. Cross-Browser Visual Testing

**Use when**: Your users span Chrome, Firefox, and Safari and you need to verify rendering consistency per browser.
**Avoid when**: Early stage projects targeting a single browser -- visual tests across three browsers triple the maintenance burden.

Playwright automatically separates snapshots by project name. Each browser gets its own baseline file. This is correct behavior -- browsers render fonts, shadows, and anti-aliasing differently.

**TypeScript**
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  expect: {
    toHaveScreenshot: {
      animations: 'disabled',
      maxDiffPixelRatio: 0.01,
    },
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
```

```typescript
// tests/homepage.spec.ts
import { test, expect } from '@playwright/test';

test('homepage renders correctly per browser', async ({ page }) => {
  await page.goto('/');

  // Playwright creates separate baselines per project:
  //   homepage.spec.ts-snapshots/homepage-chromium-linux.png
  //   homepage.spec.ts-snapshots/homepage-firefox-linux.png
  //   homepage.spec.ts-snapshots/homepage-webkit-linux.png
  await expect(page).toHaveScreenshot('homepage.png', {
    animations: 'disabled',
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('homepage renders correctly per browser', async ({ page }) => {
  await page.goto('/');

  await expect(page).toHaveScreenshot('homepage.png', {
    animations: 'disabled',
  });
});
```

**Strategy for managing cross-browser snapshots**: Run visual tests in a single browser (Chromium on Linux in CI) to minimize snapshot count and only add other browsers when you have actual cross-browser rendering bugs. You can scope visual tests to one project:

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'visual',
      testMatch: '**/*.visual.spec.ts',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'chromium',
      testIgnore: '**/*.visual.spec.ts',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      testIgnore: '**/*.visual.spec.ts',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
});
```

### 8. Responsive Visual Testing

**Use when**: Your application has responsive breakpoints and you need to verify layouts at different viewport sizes.
**Avoid when**: The page has a single fixed-width layout.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

const viewports = [
  { name: 'mobile', width: 375, height: 812 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1440, height: 900 },
];

for (const viewport of viewports) {
  test(`homepage at ${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto('/');

    await expect(page).toHaveScreenshot(`homepage-${viewport.name}.png`, {
      animations: 'disabled',
      fullPage: true,
    });
  });
}
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

const viewports = [
  { name: 'mobile', width: 375, height: 812 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1440, height: 900 },
];

for (const viewport of viewports) {
  test(`homepage at ${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto('/');

    await expect(page).toHaveScreenshot(`homepage-${viewport.name}.png`, {
      animations: 'disabled',
      fullPage: true,
    });
  });
}
```

**Alternative: use Playwright projects for responsive testing.**

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'desktop',
      testMatch: '**/*.visual.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1440, height: 900 },
      },
    },
    {
      name: 'tablet',
      testMatch: '**/*.visual.spec.ts',
      use: {
        ...devices['iPad (gen 7)'],
      },
    },
    {
      name: 'mobile',
      testMatch: '**/*.visual.spec.ts',
      use: {
        ...devices['iPhone 14'],
      },
    },
  ],
});
```

This approach gives you separate snapshot folders per device and runs them in parallel.

### 9. CI Setup for Visual Tests

**Use when**: Running visual regression tests in CI. The critical requirement is consistent rendering -- the same test must produce the same screenshot every time.
**Avoid when**: Never skip this. Visual tests without CI consistency are worthless.

**The problem**: Font rendering, anti-aliasing, and sub-pixel rendering differ across operating systems. A snapshot taken on macOS will not match one taken on Linux. This is the most common source of visual test pain.

**The solution**: Run visual tests inside Docker using the official Playwright container. Generate and update snapshots from the same container.

**GitHub Actions with Docker**

```yaml
# .github/workflows/visual-tests.yml
name: Visual Regression Tests
on: [push, pull_request]

jobs:
  visual-tests:
    runs-on: ubuntu-latest
    container:
      image: mcr.microsoft.com/playwright:v1.50.0-noble
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci

      - name: Run visual tests
        run: npx playwright test --project=visual
        env:
          HOME: /root  # required for Playwright in Docker

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: visual-test-report
          path: playwright-report/
          retention-days: 14
```

**Updating snapshots locally using Docker** -- so your local baselines match CI:

```bash
# Generate/update snapshots using the same container as CI
docker run --rm -v $(pwd):/work -w /work \
  mcr.microsoft.com/playwright:v1.50.0-noble \
  npx playwright test --update-snapshots --project=visual
```

**Add a script to `package.json`** for convenience:

```json
{
  "scripts": {
    "test:visual": "npx playwright test --project=visual",
    "test:visual:update": "docker run --rm -v $(pwd):/work -w /work mcr.microsoft.com/playwright:v1.50.0-noble npx playwright test --update-snapshots --project=visual"
  }
}
```

**Configure snapshots for Linux only** in your config:

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  snapshotPathTemplate: '{testDir}/{testFileDir}/{testFileName}-snapshots/{arg}{-projectName}{ext}',
  // Omits {-snapshotSuffix} which includes the platform name (linux, darwin, win32).
  // This means snapshots are platform-agnostic -- you MUST generate them in Docker.
  projects: [
    {
      name: 'visual',
      testMatch: '**/*.visual.spec.ts',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
```

### 10. Component Visual Testing

**Use when**: Testing individual UI components in isolation -- buttons, cards, forms, modals. Faster than full-page screenshots, more stable, and easier to maintain.
**Avoid when**: You need to verify interactions between multiple components or page-level layout.

**TypeScript -- using Playwright component testing**
```typescript
// tests/components/button.visual.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Button component visual states', () => {
  test('primary button', async ({ page }) => {
    await page.goto('/storybook/iframe.html?id=button--primary');
    const button = page.getByRole('button');
    await expect(button).toHaveScreenshot('button-primary.png', {
      animations: 'disabled',
    });
  });

  test('primary button hover', async ({ page }) => {
    await page.goto('/storybook/iframe.html?id=button--primary');
    const button = page.getByRole('button');
    await button.hover();
    await expect(button).toHaveScreenshot('button-primary-hover.png', {
      animations: 'disabled',
    });
  });

  test('primary button disabled', async ({ page }) => {
    await page.goto('/storybook/iframe.html?id=button--primary-disabled');
    const button = page.getByRole('button');
    await expect(button).toHaveScreenshot('button-primary-disabled.png', {
      animations: 'disabled',
    });
  });

  test('button sizes', async ({ page }) => {
    for (const size of ['small', 'medium', 'large']) {
      await page.goto(`/storybook/iframe.html?id=button--${size}`);
      const button = page.getByRole('button');
      await expect(button).toHaveScreenshot(`button-${size}.png`, {
        animations: 'disabled',
      });
    }
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Button component visual states', () => {
  test('primary button', async ({ page }) => {
    await page.goto('/storybook/iframe.html?id=button--primary');
    const button = page.getByRole('button');
    await expect(button).toHaveScreenshot('button-primary.png', {
      animations: 'disabled',
    });
  });

  test('primary button hover', async ({ page }) => {
    await page.goto('/storybook/iframe.html?id=button--primary');
    const button = page.getByRole('button');
    await button.hover();
    await expect(button).toHaveScreenshot('button-primary-hover.png', {
      animations: 'disabled',
    });
  });

  test('primary button disabled', async ({ page }) => {
    await page.goto('/storybook/iframe.html?id=button--primary-disabled');
    const button = page.getByRole('button');
    await expect(button).toHaveScreenshot('button-primary-disabled.png', {
      animations: 'disabled',
    });
  });

  test('button sizes', async ({ page }) => {
    for (const size of ['small', 'medium', 'large']) {
      await page.goto(`/storybook/iframe.html?id=button--${size}`);
      const button = page.getByRole('button');
      await expect(button).toHaveScreenshot(`button-${size}.png`, {
        animations: 'disabled',
      });
    }
  });
});
```

**Using a dedicated visual test page** instead of Storybook:

```typescript
// tests/components/card.visual.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Card component', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to a page that renders the component in isolation
    await page.goto('/test-harness/card');
  });

  test('default state', async ({ page }) => {
    await expect(page.getByTestId('card')).toHaveScreenshot('card-default.png', {
      animations: 'disabled',
    });
  });

  test('with long content truncates correctly', async ({ page }) => {
    await page.goto('/test-harness/card?content=long');
    await expect(page.getByTestId('card')).toHaveScreenshot('card-long-content.png', {
      animations: 'disabled',
    });
  });

  test('error state', async ({ page }) => {
    await page.goto('/test-harness/card?state=error');
    await expect(page.getByTestId('card')).toHaveScreenshot('card-error.png', {
      animations: 'disabled',
    });
  });
});
```

## Decision Guide

| Scenario | Recommended Approach | Why |
|---|---|---|
| Key landing pages, marketing site | Full page screenshot, `fullPage: true` | Catches layout shifts, spacing, and overall visual harmony |
| Individual UI components (buttons, cards, modals) | Element screenshot on the component | Isolated, fast, stable -- immune to unrelated page changes |
| Page with dynamic content (timestamps, live data) | Full page + `mask` on dynamic elements | Covers layout while ignoring volatile content |
| Design system component library | Element screenshot per variant, zero threshold | Pixel-perfect enforcement for shared components |
| Responsive layout verification | Screenshot per viewport (loop or projects) | Catches breakpoint bugs at mobile/tablet/desktop |
| Cross-browser rendering consistency | Separate snapshots per browser project | Browsers render fonts and shadows differently |
| CI pipeline | Docker container (Playwright image), Linux-only snapshots | Consistent rendering, no OS-dependent diffs |
| Pixel threshold: design system | `threshold: 0`, `maxDiffPixels: 0` | Zero tolerance for component library |
| Pixel threshold: content pages | `maxDiffPixelRatio: 0.01`, `threshold: 0.2` | Allows minor anti-aliasing variance |
| Pixel threshold: charts and graphs | `maxDiffPixels: 200`, `threshold: 0.3` | Anti-aliasing on curves varies across runs |
| Visual tests add value | Stable pages, design systems, post-refactor verification | Clear baseline, predictable content |
| Visual tests are noise | Highly dynamic pages, real-time dashboards, A/B test pages | Content changes on every load, diffs are meaningless |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Visual testing every page in the app | Massive snapshot maintenance, constant false failures, team ignores results | Pick 5-10 key pages and critical components. Quality over quantity. |
| Not masking dynamic content (timestamps, avatars, counters) | Screenshots differ on every run. Tests are permanently flaky. | Use `mask` option for all dynamic elements. Audit pages for volatility before adding visual tests. |
| Running visual tests across macOS, Linux, and Windows | Font rendering differs per OS. Snapshots never match cross-platform. | Standardize on Linux via Docker. Generate and run snapshots in the same Playwright Docker container. |
| Not using Docker in CI for visual tests | CI runner OS updates, font changes, or library upgrades silently shift rendering. | Pin a specific Playwright Docker image version. Update intentionally. |
| Updating snapshots blindly with `--update-snapshots` | Accepts unintentional regressions. The baseline becomes wrong. | Always review the diff in the HTML report first. Understand why the snapshot changed. |
| Skipping `animations: 'disabled'` | CSS transitions and keyframe animations create random diffs. One of the top causes of flaky visual tests. | Set `animations: 'disabled'` globally in config. |
| Using visual tests instead of functional assertions | Screenshot diffs do not tell you *what* broke -- just that *something* looks different. Slow to debug. | Use functional assertions (`toHaveText`, `toBeVisible`) for behavior. Visual tests complement, never replace. |
| Committing snapshots generated on different platforms | The repo has macOS snapshots from dev A, Linux snapshots from dev B. Tests fail for everyone. | All team members generate snapshots using the same Docker container. Add a `test:visual:update` script. |
| Setting threshold too high (e.g., `maxDiffPixelRatio: 0.1`) | 10% of pixels can change and the test still passes. Defeats the purpose. | Start with `0.01` (1%) and adjust per-test if needed. |
| Full page screenshots on pages with infinite scroll or lazy loading | Page height is nondeterministic. Screenshots vary by load timing. | Use element screenshots on the above-the-fold content, or scroll to a deterministic state first. |

## Troubleshooting

### "Screenshot comparison failed" on first CI run after local development

**Cause**: Snapshots were generated on macOS (or Windows) locally. CI runs on Linux. Font rendering differs between operating systems, so every pixel comparison fails.

**Fix**: Generate snapshots using Docker locally so they match CI:

```bash
docker run --rm -v $(pwd):/work -w /work \
  mcr.microsoft.com/playwright:v1.50.0-noble \
  npx playwright test --update-snapshots --project=visual
```

Commit the Linux-generated snapshots. Never commit macOS-generated snapshots if CI runs on Linux.

### "Expected screenshot to match but X pixels differ"

**Cause**: Minor rendering differences from anti-aliasing, font hinting, or sub-pixel rendering. Common with text-heavy pages and curved shapes (charts, rounded corners).

**Fix**: Add a small tolerance:

```typescript
await expect(page).toHaveScreenshot('page.png', {
  maxDiffPixelRatio: 0.01,  // allow 1% variance
  threshold: 0.2,           // per-pixel color tolerance
});
```

If the diff is larger, check the HTML report. Look at the diff image to determine if the change is a real regression or rendering noise.

### Visual tests pass locally but fail in CI (even with Docker)

**Cause**: Different Playwright versions locally vs CI. The Docker image pins a specific Playwright version. If your local `@playwright/test` is newer, the rendering engine may differ.

**Fix**: Ensure the Playwright version in `package.json` matches the Docker image tag:

```json
{
  "devDependencies": {
    "@playwright/test": "1.50.0"
  }
}
```

```yaml
# CI config
container:
  image: mcr.microsoft.com/playwright:v1.50.0-noble  # must match
```

### Animations cause random diff failures

**Cause**: CSS animations or transitions captured mid-frame. The screenshot is taken at a non-deterministic point in the animation timeline.

**Fix**: Set `animations: 'disabled'` globally:

```typescript
// playwright.config.ts
export default defineConfig({
  expect: {
    toHaveScreenshot: {
      animations: 'disabled',
    },
  },
});
```

For JavaScript-driven animations, wait for a stable state before screenshotting. As a last resort, use `page.waitForTimeout(300)` after the animation trigger.

### Snapshot file names conflict between tests

**Cause**: Two tests in different files use the same screenshot name (`'homepage.png'`) without unique file paths.

**Fix**: Playwright includes the test file name in the snapshot path by default. If you still have conflicts, use explicit unique names:

```typescript
await expect(page).toHaveScreenshot('auth-homepage.png');   // in auth.spec.ts
await expect(page).toHaveScreenshot('public-homepage.png'); // in public.spec.ts
```

Or customize the snapshot path template in config:

```typescript
export default defineConfig({
  snapshotPathTemplate: '{testDir}/{testFileDir}/{testFileName}-snapshots/{arg}{-projectName}{ext}',
});
```

### Too many snapshot files to maintain

**Cause**: Visual tests for every page, every browser, every viewport. The snapshot count explodes.

**Fix**: Be selective. Visual test only pages where visual regressions are high-risk:
- Landing pages and marketing pages
- Design system components
- Complex layouts (dashboards, data tables)
- Pages after a major refactor

Skip pages where functional assertions already cover the key elements. A `toHaveText` and `toBeVisible` check is often enough.

## Related

- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- `toHaveScreenshot()` is a web-first assertion and follows the same retry semantics
- [core/configuration.md](configuration.md) -- global screenshot config, project setup, `snapshotPathTemplate`
- [core/mobile-and-responsive.md](mobile-and-responsive.md) -- responsive viewport testing patterns
- [ci/docker-and-containers.md](../ci/docker-and-containers.md) -- Docker setup for consistent rendering
- [ci/ci-github-actions.md](../ci/ci-github-actions.md) -- CI pipeline configuration for visual tests
