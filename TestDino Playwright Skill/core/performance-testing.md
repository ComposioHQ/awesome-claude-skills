# Performance Testing

> **When to use**: Measuring and enforcing Web Vitals, resource loading timing, bundle sizes, and runtime performance. Use Playwright to catch performance regressions in CI before users notice them.
> **Prerequisites**: [core/configuration.md](configuration.md), [core/assertions-and-waiting.md](assertions-and-waiting.md)

## Quick Reference

```typescript
// Measure Largest Contentful Paint (LCP)
const lcp = await page.evaluate(() => {
  return new Promise<number>((resolve) => {
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      resolve(entries[entries.length - 1].startTime);
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  });
});
expect(lcp).toBeLessThan(2500); // Good LCP threshold

// Throttle network to 3G
const client = await page.context().newCDPSession(page);
await client.send('Network.emulateNetworkConditions', {
  offline: false, downloadThroughput: 1.6 * 1024 * 1024 / 8,
  uploadThroughput: 750 * 1024 / 8, latency: 150,
});
```

## Patterns

### Web Vitals Measurement (LCP, CLS, FID/INP)

**Use when**: Enforcing Core Web Vitals thresholds as part of your test suite.
**Avoid when**: You only need aggregate field data -- use Chrome UX Report or RUM tools instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('Core Web Vitals meet thresholds on homepage', async ({ page }) => {
  // Inject Web Vitals observer before navigation
  await page.addInitScript(() => {
    (window as any).__webVitals = { lcp: 0, cls: 0, fid: 0 };

    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      (window as any).__webVitals.lcp = entries[entries.length - 1].startTime;
    }).observe({ type: 'largest-contentful-paint', buffered: true });

    new PerformanceObserver((list) => {
      let clsValue = 0;
      for (const entry of list.getEntries()) {
        if (!(entry as any).hadRecentInput) {
          clsValue += (entry as any).value;
        }
      }
      (window as any).__webVitals.cls = clsValue;
    }).observe({ type: 'layout-shift', buffered: true });

    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      (window as any).__webVitals.fid = entries[0]?.processingStart - entries[0]?.startTime;
    }).observe({ type: 'first-input', buffered: true });
  });

  await page.goto('/');

  // Trigger a user interaction to measure FID
  await page.getByRole('button', { name: 'Get started' }).click();

  // Wait for LCP to settle
  await page.waitForTimeout(1000); // Acceptable here: waiting for metric to finalize

  const vitals = await page.evaluate(() => (window as any).__webVitals);

  expect(vitals.lcp).toBeLessThan(2500);   // Good: <2.5s
  expect(vitals.cls).toBeLessThan(0.1);    // Good: <0.1
  // FID may be 0 in automated tests due to no real user delay
  if (vitals.fid > 0) {
    expect(vitals.fid).toBeLessThan(100);  // Good: <100ms
  }
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('LCP meets threshold on homepage', async ({ page }) => {
  await page.addInitScript(() => {
    window.__lcp = 0;
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      window.__lcp = entries[entries.length - 1].startTime;
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  });

  await page.goto('/');
  await page.waitForTimeout(1000);

  const lcp = await page.evaluate(() => window.__lcp);
  expect(lcp).toBeLessThan(2500);
});
```

### Performance API Access

**Use when**: Measuring navigation timing, resource loading, or custom performance marks.
**Avoid when**: Web Vitals alone cover your needs.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('page load timing is within budget', async ({ page }) => {
  await page.goto('/dashboard');

  const timing = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    return {
      dns: nav.domainLookupEnd - nav.domainLookupStart,
      tcp: nav.connectEnd - nav.connectStart,
      ttfb: nav.responseStart - nav.requestStart,
      domContentLoaded: nav.domContentLoadedEventEnd - nav.startTime,
      loadComplete: nav.loadEventEnd - nav.startTime,
      domInteractive: nav.domInteractive - nav.startTime,
    };
  });

  expect(timing.ttfb).toBeLessThan(600);           // TTFB under 600ms
  expect(timing.domContentLoaded).toBeLessThan(2000); // DOM ready under 2s
  expect(timing.loadComplete).toBeLessThan(5000);     // Full load under 5s
});

test('critical API calls complete within budget', async ({ page }) => {
  await page.goto('/dashboard');

  const apiTimings = await page.evaluate(() => {
    return performance
      .getEntriesByType('resource')
      .filter((r) => r.name.includes('/api/'))
      .map((r) => ({
        name: r.name.split('/api/')[1],
        duration: r.duration,
        size: (r as PerformanceResourceTiming).transferSize,
      }));
  });

  for (const api of apiTimings) {
    expect(api.duration, `API ${api.name} too slow`).toBeLessThan(1000);
  }
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('page load timing is within budget', async ({ page }) => {
  await page.goto('/dashboard');

  const timing = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    return {
      ttfb: nav.responseStart - nav.requestStart,
      domContentLoaded: nav.domContentLoadedEventEnd - nav.startTime,
      loadComplete: nav.loadEventEnd - nav.startTime,
    };
  });

  expect(timing.ttfb).toBeLessThan(600);
  expect(timing.domContentLoaded).toBeLessThan(2000);
  expect(timing.loadComplete).toBeLessThan(5000);
});
```

### Resource Loading and Bundle Size Monitoring

**Use when**: Enforcing bundle size budgets and catching unexpected large resources.
**Avoid when**: Bundle analysis is handled by webpack-bundle-analyzer or similar build tools.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('JavaScript bundle sizes are within budget', async ({ page }) => {
  const resourceSizes: { name: string; size: number }[] = [];

  page.on('response', async (response) => {
    const url = response.url();
    if (url.endsWith('.js') || url.includes('.js?')) {
      const headers = response.headers();
      const size = parseInt(headers['content-length'] || '0');
      resourceSizes.push({
        name: url.split('/').pop()!.split('?')[0],
        size,
      });
    }
  });

  await page.goto('/');
  await page.waitForLoadState('networkidle');

  // No single JS bundle should exceed 250KB compressed
  for (const resource of resourceSizes) {
    expect(
      resource.size,
      `Bundle ${resource.name} is ${(resource.size / 1024).toFixed(1)}KB`
    ).toBeLessThan(250 * 1024);
  }

  // Total JS payload should not exceed 500KB
  const totalSize = resourceSizes.reduce((sum, r) => sum + r.size, 0);
  expect(totalSize, `Total JS: ${(totalSize / 1024).toFixed(1)}KB`).toBeLessThan(500 * 1024);
});

test('no unexpected large images', async ({ page }) => {
  const largeImages: { url: string; size: number }[] = [];

  page.on('response', async (response) => {
    const contentType = response.headers()['content-type'] || '';
    if (contentType.startsWith('image/')) {
      const size = parseInt(response.headers()['content-length'] || '0');
      if (size > 200 * 1024) {
        largeImages.push({ url: response.url(), size });
      }
    }
  });

  await page.goto('/');
  await page.waitForLoadState('networkidle');

  expect(
    largeImages,
    `Found ${largeImages.length} images over 200KB: ${largeImages.map(i => i.url).join(', ')}`
  ).toHaveLength(0);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('JavaScript bundle sizes are within budget', async ({ page }) => {
  const resourceSizes = [];

  page.on('response', async (response) => {
    const url = response.url();
    if (url.endsWith('.js') || url.includes('.js?')) {
      const size = parseInt(response.headers()['content-length'] || '0');
      resourceSizes.push({ name: url.split('/').pop().split('?')[0], size });
    }
  });

  await page.goto('/');
  await page.waitForLoadState('networkidle');

  const totalSize = resourceSizes.reduce((sum, r) => sum + r.size, 0);
  expect(totalSize).toBeLessThan(500 * 1024);
});
```

### Slow Network Simulation via CDP

**Use when**: Testing your app's behavior and performance under constrained network conditions.
**Avoid when**: Playwright's built-in `offline` option is sufficient for your test.

**TypeScript**
```typescript
import { test, expect, type Page } from '@playwright/test';

// Network presets
const NETWORK_PRESETS = {
  slow3G: {
    offline: false,
    downloadThroughput: (500 * 1024) / 8,  // 500 Kbps
    uploadThroughput: (500 * 1024) / 8,
    latency: 400,
  },
  fast3G: {
    offline: false,
    downloadThroughput: (1.6 * 1024 * 1024) / 8,  // 1.6 Mbps
    uploadThroughput: (750 * 1024) / 8,
    latency: 150,
  },
  regularLTE: {
    offline: false,
    downloadThroughput: (4 * 1024 * 1024) / 8,  // 4 Mbps
    uploadThroughput: (3 * 1024 * 1024) / 8,
    latency: 20,
  },
} as const;

async function throttleNetwork(page: Page, preset: keyof typeof NETWORK_PRESETS) {
  const client = await page.context().newCDPSession(page);
  await client.send('Network.enable');
  await client.send('Network.emulateNetworkConditions', NETWORK_PRESETS[preset]);
  return client;
}

test('app shows loading states on slow network', async ({ page }) => {
  await throttleNetwork(page, 'slow3G');

  await page.goto('/dashboard');

  // Loading skeleton should appear while content loads slowly
  await expect(page.getByTestId('loading-skeleton')).toBeVisible();

  // Content should eventually load
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 30000 });
});

test('images lazy-load on slow connection', async ({ page }) => {
  await throttleNetwork(page, 'fast3G');
  await page.goto('/gallery');

  // Only above-the-fold images should be loaded initially
  const loadedImages = await page.evaluate(() =>
    Array.from(document.querySelectorAll('img'))
      .filter((img) => img.complete && img.naturalWidth > 0).length
  );

  // Scroll to trigger lazy loading
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(2000);

  const allLoadedImages = await page.evaluate(() =>
    Array.from(document.querySelectorAll('img'))
      .filter((img) => img.complete && img.naturalWidth > 0).length
  );

  expect(allLoadedImages).toBeGreaterThan(loadedImages);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

async function throttleNetwork(page, preset) {
  const presets = {
    slow3G: { offline: false, downloadThroughput: (500 * 1024) / 8, uploadThroughput: (500 * 1024) / 8, latency: 400 },
    fast3G: { offline: false, downloadThroughput: (1.6 * 1024 * 1024) / 8, uploadThroughput: (750 * 1024) / 8, latency: 150 },
  };
  const client = await page.context().newCDPSession(page);
  await client.send('Network.enable');
  await client.send('Network.emulateNetworkConditions', presets[preset]);
  return client;
}

test('app shows loading states on slow network', async ({ page }) => {
  await throttleNetwork(page, 'slow3G');
  await page.goto('/dashboard');

  await expect(page.getByTestId('loading-skeleton')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 30000 });
});
```

### CPU Throttling via CDP

**Use when**: Simulating low-powered devices to test animation smoothness, interaction responsiveness, or heavy computation.
**Avoid when**: Network performance is the bottleneck, not CPU.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('animations remain smooth under CPU throttling', async ({ page }) => {
  const client = await page.context().newCDPSession(page);

  // 4x slowdown simulates a mid-tier mobile device
  await client.send('Emulation.setCPUThrottlingRate', { rate: 4 });

  await page.goto('/animations-demo');
  await page.getByRole('button', { name: 'Start animation' }).click();

  // Measure frame rate during animation
  const fps = await page.evaluate(() => {
    return new Promise<number>((resolve) => {
      let frames = 0;
      const start = performance.now();
      function count() {
        frames++;
        if (performance.now() - start < 1000) {
          requestAnimationFrame(count);
        } else {
          resolve(frames);
        }
      }
      requestAnimationFrame(count);
    });
  });

  // Should maintain at least 30fps even on throttled CPU
  expect(fps).toBeGreaterThan(30);

  // Reset throttling
  await client.send('Emulation.setCPUThrottlingRate', { rate: 1 });
});

test('search input responds quickly under CPU constraint', async ({ page }) => {
  const client = await page.context().newCDPSession(page);
  await client.send('Emulation.setCPUThrottlingRate', { rate: 4 });

  await page.goto('/search');

  const start = Date.now();
  await page.getByRole('textbox', { name: 'Search' }).fill('test query');
  await expect(page.getByRole('listbox')).toBeVisible();
  const elapsed = Date.now() - start;

  // Autocomplete should appear within 500ms even under 4x CPU throttle
  expect(elapsed).toBeLessThan(500);

  await client.send('Emulation.setCPUThrottlingRate', { rate: 1 });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('animations remain smooth under CPU throttling', async ({ page }) => {
  const client = await page.context().newCDPSession(page);
  await client.send('Emulation.setCPUThrottlingRate', { rate: 4 });

  await page.goto('/animations-demo');
  await page.getByRole('button', { name: 'Start animation' }).click();

  const fps = await page.evaluate(() => {
    return new Promise((resolve) => {
      let frames = 0;
      const start = performance.now();
      function count() {
        frames++;
        if (performance.now() - start < 1000) {
          requestAnimationFrame(count);
        } else {
          resolve(frames);
        }
      }
      requestAnimationFrame(count);
    });
  });

  expect(fps).toBeGreaterThan(30);
  await client.send('Emulation.setCPUThrottlingRate', { rate: 1 });
});
```

### Performance Budgets in CI

**Use when**: Enforcing hard performance limits that block merges when thresholds are exceeded.
**Avoid when**: Performance varies too much in CI environment -- use trend-based monitoring instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

// Define budgets in a shared config
const PERFORMANCE_BUDGETS = {
  homepage: {
    lcp: 2500,
    cls: 0.1,
    ttfb: 600,
    totalJsSize: 500 * 1024,
    totalImageSize: 1000 * 1024,
    domContentLoaded: 2000,
  },
  dashboard: {
    lcp: 3000,
    cls: 0.1,
    ttfb: 800,
    totalJsSize: 750 * 1024,
    totalImageSize: 500 * 1024,
    domContentLoaded: 3000,
  },
} as const;

test.describe('performance budgets', () => {
  test('homepage meets performance budget', async ({ page }) => {
    const budget = PERFORMANCE_BUDGETS.homepage;
    let totalJsSize = 0;

    page.on('response', (response) => {
      if (response.url().endsWith('.js') || response.url().includes('.js?')) {
        totalJsSize += parseInt(response.headers()['content-length'] || '0');
      }
    });

    // Inject LCP observer
    await page.addInitScript(() => {
      (window as any).__lcp = 0;
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        (window as any).__lcp = entries[entries.length - 1].startTime;
      }).observe({ type: 'largest-contentful-paint', buffered: true });
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const metrics = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        lcp: (window as any).__lcp,
        ttfb: nav.responseStart - nav.requestStart,
        domContentLoaded: nav.domContentLoadedEventEnd - nav.startTime,
      };
    });

    expect(metrics.lcp, 'LCP budget exceeded').toBeLessThan(budget.lcp);
    expect(metrics.ttfb, 'TTFB budget exceeded').toBeLessThan(budget.ttfb);
    expect(metrics.domContentLoaded, 'DOMContentLoaded budget exceeded').toBeLessThan(budget.domContentLoaded);
    expect(totalJsSize, 'JS bundle budget exceeded').toBeLessThan(budget.totalJsSize);
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

const PERFORMANCE_BUDGETS = {
  homepage: { lcp: 2500, ttfb: 600, totalJsSize: 500 * 1024, domContentLoaded: 2000 },
};

test('homepage meets performance budget', async ({ page }) => {
  const budget = PERFORMANCE_BUDGETS.homepage;
  let totalJsSize = 0;

  page.on('response', (response) => {
    if (response.url().endsWith('.js')) {
      totalJsSize += parseInt(response.headers()['content-length'] || '0');
    }
  });

  await page.addInitScript(() => {
    window.__lcp = 0;
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      window.__lcp = entries[entries.length - 1].startTime;
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  });

  await page.goto('/');
  await page.waitForLoadState('networkidle');

  const metrics = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    return {
      lcp: window.__lcp,
      ttfb: nav.responseStart - nav.requestStart,
      domContentLoaded: nav.domContentLoadedEventEnd - nav.startTime,
    };
  });

  expect(metrics.lcp).toBeLessThan(budget.lcp);
  expect(metrics.ttfb).toBeLessThan(budget.ttfb);
  expect(totalJsSize).toBeLessThan(budget.totalJsSize);
});
```

## Decision Guide

| What to Measure | Technique | When to Use |
|---|---|---|
| LCP, CLS, FID/INP | `PerformanceObserver` via `addInitScript` | Core Web Vitals regression testing |
| TTFB, DOM load times | `performance.getEntriesByType('navigation')` | Server response and page load budgets |
| API call durations | `performance.getEntriesByType('resource')` | Backend performance regression |
| JS/CSS bundle sizes | `page.on('response')` + `content-length` header | Bundle size budgets in CI |
| Slow network behavior | CDP `Network.emulateNetworkConditions` | Testing loading states, lazy loading, offline |
| Low-end device behavior | CDP `Emulation.setCPUThrottlingRate` | Animation smoothness, interaction latency |
| Full Lighthouse audit | `@playwright/test` + Lighthouse CLI via CDP port | Comprehensive performance scoring |
| Runtime performance | `page.evaluate` + `requestAnimationFrame` FPS count | Animation and rendering performance |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| Setting absolute thresholds based on local dev machine | CI machines are slower; thresholds flap | Calibrate budgets on CI hardware or use relative comparisons |
| Using `networkidle` as a performance measurement point | `networkidle` includes analytics, ads, non-critical resources | Measure specific metrics (LCP, TTFB) directly via Performance API |
| Running performance tests with `--headed` in CI | Headed mode adds GPU overhead and inconsistency | Use headless mode for consistent measurement |
| Measuring FID in automated tests | No real user input delay exists in automation | Measure INP or use Lighthouse for FID estimates |
| Running perf tests in parallel with other CI jobs | CPU contention skews results | Run performance tests in isolation or on dedicated CI runners |
| Ignoring `content-length` being `0` | Compressed responses may not report size | Use `response.body().length` for actual transfer size |
| Only testing happy-path performance | Slow error paths degrade user experience | Test performance of error states, empty states, and large datasets |
| Hard-failing CI on minor regressions | Causes merge friction for non-performance changes | Use warning thresholds with mandatory review, fail only on large regressions |

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| LCP is 0 or unrealistically low | Observer did not fire; page has no qualifying LCP element | Verify the page has images or large text blocks; add `buffered: true` to observer |
| CLS is always 0 | Layout shifts occur before observer is registered | Use `addInitScript` to inject observer before page load |
| CDP session errors with Firefox/WebKit | CDP is Chromium-only | Guard CDP code: `test.skip(browserName !== 'chromium')` |
| Performance numbers vary wildly between runs | CI machine load fluctuates | Run performance tests multiple times and take the median; use dedicated runners |
| `content-length` header is missing | Server uses chunked transfer encoding | Use `response.body()` then check `Buffer.byteLength()` |
| Network throttling has no effect | CDP session created on wrong page | Create the CDP session from the page's context, not a separate browser |
| Bundle size test passes but app feels slow | Measuring compressed size, not parsed size | Also check `performance.getEntriesByType('resource')` for `decodedBodySize` |

## Related

- [core/configuration.md](configuration.md) -- timeout and retry settings for performance-sensitive tests
- [core/network-mocking.md](network-mocking.md) -- mocking slow APIs for performance boundary testing
- [core/browser-apis.md](browser-apis.md) -- using browser APIs for measurement
- [ci/ci-github-actions.md](../ci/ci-github-actions.md) -- CI configuration for performance budgets
- [core/clock-and-time-mocking.md](clock-and-time-mocking.md) -- time-related performance testing
