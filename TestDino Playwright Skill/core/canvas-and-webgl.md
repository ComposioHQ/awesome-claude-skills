# Canvas and WebGL Testing

> **When to use**: When your application renders content on `<canvas>` elements -- charts (Chart.js, D3), maps (Mapbox, Leaflet), games, image editors, WebGL visualizations, drawing tools, signature pads.
> **Prerequisites**: [core/assertions-and-waiting.md](assertions-and-waiting.md), [core/locators.md](locators.md)

## Quick Reference

```typescript
// Screenshot comparison — the primary strategy for canvas
await expect(page.locator('canvas#chart')).toHaveScreenshot('revenue-chart.png');

// Click at specific coordinates on canvas
await page.locator('canvas').click({ position: { x: 200, y: 150 } });

// Read canvas state via page.evaluate
const pixelColor = await page.evaluate(() => {
  const canvas = document.querySelector('canvas') as HTMLCanvasElement;
  const ctx = canvas.getContext('2d')!;
  const pixel = ctx.getImageData(100, 100, 1, 1).data;
  return { r: pixel[0], g: pixel[1], b: pixel[2], a: pixel[3] };
});
```

## Patterns

### Screenshot Comparison (Visual Regression)

**Use when**: Verifying the visual output of canvas-rendered content -- charts, graphs, maps, drawings. This is the most reliable approach because canvas pixels are not queryable via DOM.
**Avoid when**: The canvas content is dynamic on every render (animations, timestamps). Use threshold or mask options.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('revenue chart renders correctly', async ({ page }) => {
  await page.goto('/dashboard');

  // Wait for the chart to finish rendering
  await expect(page.locator('canvas#revenue-chart')).toBeVisible();

  // Optionally wait for a loading indicator to disappear
  await expect(page.getByTestId('chart-loading')).toBeHidden();

  // Screenshot comparison against a baseline
  await expect(page.locator('canvas#revenue-chart')).toHaveScreenshot('revenue-chart.png', {
    maxDiffPixelRatio: 0.01,  // Allow 1% pixel difference for anti-aliasing
  });
});

test('chart updates after date range change', async ({ page }) => {
  await page.goto('/dashboard');

  // Change date range
  await page.getByRole('combobox', { name: 'Date range' }).selectOption('Last 30 days');

  // Wait for chart to re-render
  await expect(page.getByTestId('chart-loading')).toBeHidden();

  // Compare against a different baseline
  await expect(page.locator('canvas#revenue-chart')).toHaveScreenshot('revenue-chart-30d.png', {
    maxDiffPixelRatio: 0.01,
  });
});

test('mask dynamic areas in canvas screenshot', async ({ page }) => {
  await page.goto('/dashboard');

  await expect(page.locator('canvas#chart')).toHaveScreenshot('chart-stable.png', {
    // Mask the timestamp area that changes every render
    mask: [page.locator('.chart-timestamp')],
    maxDiffPixelRatio: 0.02,
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('revenue chart renders correctly', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.locator('canvas#revenue-chart')).toBeVisible();
  await expect(page.getByTestId('chart-loading')).toBeHidden();

  await expect(page.locator('canvas#revenue-chart')).toHaveScreenshot('revenue-chart.png', {
    maxDiffPixelRatio: 0.01,
  });
});

test('chart updates after date range change', async ({ page }) => {
  await page.goto('/dashboard');
  await page.getByRole('combobox', { name: 'Date range' }).selectOption('Last 30 days');
  await expect(page.getByTestId('chart-loading')).toBeHidden();

  await expect(page.locator('canvas#revenue-chart')).toHaveScreenshot('revenue-chart-30d.png', {
    maxDiffPixelRatio: 0.01,
  });
});
```

### Interacting with Canvas via Coordinates

**Use when**: Testing user interactions on canvas -- clicking chart data points, dragging on a drawing tool, selecting map regions.
**Avoid when**: The element has an accessible DOM overlay (many chart libraries render tooltips as HTML). Interact with the overlay instead.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('click on chart data point shows tooltip', async ({ page }) => {
  await page.goto('/analytics');

  const canvas = page.locator('canvas#line-chart');
  await expect(canvas).toBeVisible();

  // Click at a specific coordinate on the canvas
  await canvas.click({ position: { x: 200, y: 100 } });

  // Tooltip appears as an HTML overlay (most chart libraries)
  await expect(page.getByTestId('chart-tooltip')).toContainText('Revenue: $12,400');
});

test('draw a line on the canvas', async ({ page }) => {
  await page.goto('/drawing-tool');

  const canvas = page.locator('canvas#drawing-area');

  // Simulate a drag to draw a line
  await canvas.hover({ position: { x: 50, y: 50 } });
  await page.mouse.down();
  await page.mouse.move(200, 200, { steps: 10 }); // Smooth drag
  await page.mouse.up();

  // Verify via screenshot
  await expect(canvas).toHaveScreenshot('drawn-line.png');
});

test('pinch-to-zoom on a map canvas', async ({ page }) => {
  await page.goto('/map');

  const canvas = page.locator('canvas#map');

  // Scroll to zoom (common in map libraries)
  await canvas.hover({ position: { x: 300, y: 300 } });
  await page.mouse.wheel(0, -500); // Scroll up = zoom in

  // Verify zoom level changed
  await expect(page.getByTestId('zoom-level')).toHaveText('Zoom: 12');
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('click on chart data point shows tooltip', async ({ page }) => {
  await page.goto('/analytics');

  const canvas = page.locator('canvas#line-chart');
  await expect(canvas).toBeVisible();

  await canvas.click({ position: { x: 200, y: 100 } });
  await expect(page.getByTestId('chart-tooltip')).toContainText('Revenue: $12,400');
});

test('draw a line on the canvas', async ({ page }) => {
  await page.goto('/drawing-tool');

  const canvas = page.locator('canvas#drawing-area');
  await canvas.hover({ position: { x: 50, y: 50 } });
  await page.mouse.down();
  await page.mouse.move(200, 200, { steps: 10 });
  await page.mouse.up();

  await expect(canvas).toHaveScreenshot('drawn-line.png');
});
```

### Canvas API Testing via `page.evaluate()`

**Use when**: You need to inspect canvas pixel data, read the rendering context state, or verify programmatic canvas operations.
**Avoid when**: A screenshot comparison is sufficient. Pixel-level assertions are brittle.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('verify specific pixel color on canvas', async ({ page }) => {
  await page.goto('/color-picker');

  // Click the red swatch
  await page.getByRole('button', { name: 'Red' }).click();

  // Read the pixel color at the canvas center
  const color = await page.evaluate(() => {
    const canvas = document.querySelector('canvas#preview') as HTMLCanvasElement;
    const ctx = canvas.getContext('2d')!;
    const centerX = Math.floor(canvas.width / 2);
    const centerY = Math.floor(canvas.height / 2);
    const pixel = ctx.getImageData(centerX, centerY, 1, 1).data;
    return { r: pixel[0], g: pixel[1], b: pixel[2], a: pixel[3] };
  });

  expect(color.r).toBeGreaterThan(200); // Red channel high
  expect(color.g).toBeLessThan(50);     // Green channel low
  expect(color.b).toBeLessThan(50);     // Blue channel low
});

test('verify canvas dimensions match expected size', async ({ page }) => {
  await page.goto('/editor');

  const dimensions = await page.evaluate(() => {
    const canvas = document.querySelector('canvas#main') as HTMLCanvasElement;
    return { width: canvas.width, height: canvas.height };
  });

  expect(dimensions).toEqual({ width: 1920, height: 1080 });
});

test('canvas has content (is not blank)', async ({ page }) => {
  await page.goto('/chart');

  // Wait for rendering
  await expect(page.getByTestId('chart-loading')).toBeHidden();

  const isBlank = await page.evaluate(() => {
    const canvas = document.querySelector('canvas') as HTMLCanvasElement;
    const ctx = canvas.getContext('2d')!;
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    // Check if all pixels are transparent (blank canvas)
    return imageData.data.every((value, index) => {
      return index % 4 === 3 ? value === 0 : true; // Check alpha channel
    });
  });

  expect(isBlank).toBe(false);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('verify specific pixel color on canvas', async ({ page }) => {
  await page.goto('/color-picker');
  await page.getByRole('button', { name: 'Red' }).click();

  const color = await page.evaluate(() => {
    const canvas = document.querySelector('canvas#preview');
    const ctx = canvas.getContext('2d');
    const centerX = Math.floor(canvas.width / 2);
    const centerY = Math.floor(canvas.height / 2);
    const pixel = ctx.getImageData(centerX, centerY, 1, 1).data;
    return { r: pixel[0], g: pixel[1], b: pixel[2], a: pixel[3] };
  });

  expect(color.r).toBeGreaterThan(200);
  expect(color.g).toBeLessThan(50);
  expect(color.b).toBeLessThan(50);
});

test('canvas has content (is not blank)', async ({ page }) => {
  await page.goto('/chart');
  await expect(page.getByTestId('chart-loading')).toBeHidden();

  const isBlank = await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    const ctx = canvas.getContext('2d');
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    return imageData.data.every((value, index) => {
      return index % 4 === 3 ? value === 0 : true;
    });
  });

  expect(isBlank).toBe(false);
});
```

### WebGL Rendering Verification

**Use when**: Your app uses WebGL for 3D visualizations, data plots, or games.
**Avoid when**: The canvas uses 2D context only.

WebGL canvas cannot be read with `getImageData` from a 2D context. Use `toDataURL()` or screenshot comparison.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('WebGL scene renders a 3D model', async ({ page }) => {
  await page.goto('/3d-viewer');

  // Wait for WebGL to finish rendering
  await page.waitForFunction(() => {
    const canvas = document.querySelector('canvas#scene') as HTMLCanvasElement;
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    return gl !== null;
  });

  // Give the renderer time to complete the first frame
  await expect(page.getByTestId('render-status')).toHaveText('Ready');

  // Screenshot comparison is the most reliable approach for WebGL
  await expect(page.locator('canvas#scene')).toHaveScreenshot('3d-model.png', {
    maxDiffPixelRatio: 0.02, // WebGL has more rendering variance
  });
});

test('WebGL canvas is not blank', async ({ page }) => {
  await page.goto('/3d-viewer');
  await expect(page.getByTestId('render-status')).toHaveText('Ready');

  // Check that the WebGL canvas has drawn something
  const hasContent = await page.evaluate(() => {
    const canvas = document.querySelector('canvas#scene') as HTMLCanvasElement;
    // Convert canvas to data URL and check it's not a blank image
    const dataUrl = canvas.toDataURL();
    // A blank canvas produces a very short data URL
    return dataUrl.length > 1000;
  });

  expect(hasContent).toBe(true);
});

test('rotate 3D model and verify new angle', async ({ page }) => {
  await page.goto('/3d-viewer');
  await expect(page.getByTestId('render-status')).toHaveText('Ready');

  // Take baseline screenshot
  const canvas = page.locator('canvas#scene');

  // Drag to rotate
  await canvas.hover({ position: { x: 300, y: 300 } });
  await page.mouse.down();
  await page.mouse.move(450, 300, { steps: 20 });
  await page.mouse.up();

  // Screenshot should differ from default angle
  await expect(canvas).toHaveScreenshot('3d-model-rotated.png', {
    maxDiffPixelRatio: 0.02,
  });
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('WebGL scene renders a 3D model', async ({ page }) => {
  await page.goto('/3d-viewer');

  await page.waitForFunction(() => {
    const canvas = document.querySelector('canvas#scene');
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    return gl !== null;
  });

  await expect(page.getByTestId('render-status')).toHaveText('Ready');
  await expect(page.locator('canvas#scene')).toHaveScreenshot('3d-model.png', {
    maxDiffPixelRatio: 0.02,
  });
});

test('WebGL canvas is not blank', async ({ page }) => {
  await page.goto('/3d-viewer');
  await expect(page.getByTestId('render-status')).toHaveText('Ready');

  const hasContent = await page.evaluate(() => {
    const canvas = document.querySelector('canvas#scene');
    const dataUrl = canvas.toDataURL();
    return dataUrl.length > 1000;
  });

  expect(hasContent).toBe(true);
});
```

### Chart Library Testing Strategies

**Use when**: Testing Chart.js, D3, Recharts, Highcharts, or similar chart libraries.
**Avoid when**: Charts have full HTML/SVG DOM output (D3 with SVG). Use standard locators for SVG elements.

**TypeScript**
```typescript
import { test, expect } from '@playwright/test';

test('bar chart shows correct number of bars (SVG-based chart)', async ({ page }) => {
  await page.goto('/analytics');

  // SVG-based charts (D3, Recharts) render DOM elements — use locators
  const bars = page.locator('svg.chart rect.bar');
  await expect(bars).toHaveCount(12); // 12 months

  // Check a specific bar's aria-label or tooltip
  await bars.nth(0).hover();
  await expect(page.getByTestId('chart-tooltip')).toContainText('January: $8,200');
});

test('canvas-based chart displays data (Chart.js)', async ({ page }) => {
  await page.goto('/analytics');

  // Canvas charts — no DOM elements to query, use screenshot
  await expect(page.getByTestId('chart-loading')).toBeHidden();
  await expect(page.locator('canvas#monthly-chart')).toHaveScreenshot('monthly-chart.png');
});

test('chart legend toggles data series', async ({ page }) => {
  await page.goto('/analytics');

  // Click legend item (usually HTML, not canvas)
  await page.getByRole('button', { name: 'Revenue' }).click();

  // Revenue series hidden — chart should look different
  await expect(page.locator('canvas#chart')).toHaveScreenshot('chart-no-revenue.png');

  // Click again to re-enable
  await page.getByRole('button', { name: 'Revenue' }).click();
  await expect(page.locator('canvas#chart')).toHaveScreenshot('chart-with-revenue.png');
});

test('export chart as image', async ({ page }) => {
  await page.goto('/analytics');

  // Many chart libraries offer "download as PNG"
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export as PNG' }).click();
  const download = await downloadPromise;

  expect(download.suggestedFilename()).toMatch(/chart.*\.png$/);
});
```

**JavaScript**
```javascript
const { test, expect } = require('@playwright/test');

test('bar chart shows correct number of bars (SVG-based)', async ({ page }) => {
  await page.goto('/analytics');

  const bars = page.locator('svg.chart rect.bar');
  await expect(bars).toHaveCount(12);

  await bars.nth(0).hover();
  await expect(page.getByTestId('chart-tooltip')).toContainText('January: $8,200');
});

test('canvas-based chart displays data', async ({ page }) => {
  await page.goto('/analytics');
  await expect(page.getByTestId('chart-loading')).toBeHidden();
  await expect(page.locator('canvas#monthly-chart')).toHaveScreenshot('monthly-chart.png');
});
```

## Decision Guide

| Scenario | Best Approach | Why |
|---|---|---|
| Verify chart looks correct | `toHaveScreenshot()` on canvas element | Canvas pixels are not DOM; screenshot is the source of truth |
| Click a data point on chart | `canvas.click({ position: { x, y } })` | Canvas does not have clickable child elements |
| Verify canvas is not blank | `page.evaluate` + `getImageData` or `toDataURL` | Quick programmatic check without baseline image |
| Test SVG-based chart (D3) | Standard locators (`svg rect`, `svg path`) | SVG elements are in the DOM; use locator queries |
| Read specific pixel color | `page.evaluate` + `getImageData` | Direct access to pixel data |
| Test WebGL rendering | `toHaveScreenshot()` with higher `maxDiffPixelRatio` | WebGL has rendering variance; pixel assertions are unreliable |
| Test canvas drag/draw | `mouse.down()` + `mouse.move()` + `mouse.up()` | Simulates real drawing interactions |
| Chart tooltip after hover | `canvas.hover({ position })` then assert tooltip DOM | Tooltips are usually HTML overlays |

## Anti-Patterns

| Don't Do This | Problem | Do This Instead |
|---|---|---|
| `page.getByRole('button')` inside a canvas | Canvas content has no DOM elements | Use `canvas.click({ position })` for coordinates |
| Assert pixel colors with exact RGB values | Anti-aliasing and GPU differences cause 1-2 value variance | Use ranges (`toBeGreaterThan(200)`) or `toHaveScreenshot` |
| Skip `maxDiffPixelRatio` in canvas screenshots | Different GPUs and OS versions render slightly differently | Set `maxDiffPixelRatio: 0.01` to `0.02` |
| `waitForTimeout` to wait for chart render | Arbitrary; too slow or too fast | Wait for a loading indicator to disappear or use `waitForFunction` |
| Read WebGL pixels via 2D context `getImageData` | WebGL and 2D contexts are mutually exclusive on the same canvas | Use `canvas.toDataURL()` or screenshot comparison |
| Take full-page screenshots for canvas tests | Captures unrelated content; more brittle baselines | Scope screenshot to `page.locator('canvas#specific')` |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Screenshot baseline always differs | GPU rendering differences across CI and local machine | Use Docker with consistent GPU settings, or increase `maxDiffPixelRatio` |
| Canvas click at coordinates hits wrong element | Coordinates are relative to element, but viewport changed | Use `position` relative to the canvas element, not the page |
| `getImageData` returns all transparent pixels | Canvas has not finished rendering when evaluated | Wait for a render-complete signal or use `waitForFunction` |
| `toDataURL` throws `SecurityError` | Canvas is tainted by cross-origin image | Serve images from the same origin or use CORS headers |
| WebGL context is null | Browser does not support WebGL or it is disabled in CI | Use `--enable-webgl` flag or run tests on a GPU-capable CI runner |
| Screenshot test passes locally, fails in CI | Different font rendering, DPI, or OS | Pin the Docker image, use `fonts` config, or increase threshold |

## Related

- [core/assertions-and-waiting.md](assertions-and-waiting.md) -- auto-retrying assertions and visual comparison options
- [core/configuration.md](configuration.md) -- configure screenshot thresholds and update baselines
- [core/iframes-and-shadow-dom.md](iframes-and-shadow-dom.md) -- canvas elements inside iframes
- [core/debugging.md](debugging.md) -- debugging visual regression failures with trace viewer
