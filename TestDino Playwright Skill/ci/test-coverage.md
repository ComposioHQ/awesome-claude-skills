# Test Coverage

> **When to use**: Measuring how much of your application code is exercised by Playwright E2E tests. Useful for identifying untested code paths and enforcing coverage thresholds in CI.

## Quick Reference

```bash
# Install coverage dependencies
npm install -D nyc istanbul-lib-coverage istanbul-reports v8-to-istanbul

# Run with coverage collection
npx playwright test                    # uses fixtures to collect coverage

# Generate reports from collected data
npx nyc report --reporter=html --reporter=text-summary
npx nyc report --reporter=lcov        # for CI integration (Codecov, SonarQube)

# Check coverage thresholds
npx nyc check-coverage --lines 80 --branches 70 --functions 75
```

## Patterns

### Pattern 1: V8 Coverage with Playwright (Recommended)

**Use when**: Measuring code coverage of a web application during E2E tests. V8 coverage uses Chrome DevTools Protocol for accurate JavaScript coverage.
**Avoid when**: Testing third-party sites you don't control.

**Step 1: Create a coverage fixture:**

```ts
// fixtures/coverage.ts
import { test as base, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

const coverageDir = path.resolve(process.cwd(), '.nyc_output');

export const test = base.extend({
  page: async ({ page, browserName }, use, testInfo) => {
    // V8 coverage only works in Chromium
    if (browserName === 'chromium') {
      await page.coverage.startJSCoverage({ resetOnNavigation: false });
    }

    await use(page);

    if (browserName === 'chromium') {
      const coverage = await page.coverage.stopJSCoverage();

      // Filter to only your application code
      const appCoverage = coverage.filter((entry) =>
        entry.url.includes('localhost') && !entry.url.includes('node_modules')
      );

      if (appCoverage.length > 0) {
        // Ensure output directory exists
        fs.mkdirSync(coverageDir, { recursive: true });

        // Write V8 coverage data
        const coverageFile = path.join(
          coverageDir,
          `coverage-${crypto.randomUUID()}.json`
        );
        fs.writeFileSync(coverageFile, JSON.stringify({
          result: appCoverage.map((entry) => ({
            scriptId: '0',
            url: entry.url,
            functions: entry.functions || [],
          })),
        }));
      }
    }
  },
});

export { expect };
```

**Step 2: Use the coverage fixture in tests:**

```ts
// tests/dashboard.spec.ts
import { test, expect } from '../fixtures/coverage';

test('dashboard loads with widgets', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  // Coverage is automatically collected and saved
});
```

**Step 3: Generate coverage report after tests:**

```json
// package.json
{
  "scripts": {
    "test:e2e": "npx playwright test",
    "test:coverage": "npx playwright test --project=chromium && npx nyc report --reporter=html --reporter=text-summary",
    "coverage:check": "npx nyc check-coverage --lines 80 --branches 70 --functions 75"
  }
}
```

### Pattern 2: Istanbul (Source-Map Based) Coverage

**Use when**: Your application uses webpack, Vite, or another bundler and you want source-mapped coverage tied to original source files.
**Avoid when**: V8 coverage works well enough -- it's simpler to set up.

**Step 1: Instrument your application code:**

For **Vite**:

```bash
npm install -D vite-plugin-istanbul
```

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import istanbul from 'vite-plugin-istanbul';

export default defineConfig({
  plugins: [
    ...(process.env.COVERAGE === 'true'
      ? [istanbul({
          include: 'src/*',
          exclude: ['node_modules', 'test/'],
          extension: ['.js', '.ts', '.tsx', '.jsx'],
          requireEnv: true,
        })]
      : []),
  ],
});
```

For **webpack** (Create React App):

```bash
npm install -D @istanbuljs/nyc-config-typescript babel-plugin-istanbul
```

```json
// babel.config.json (or .babelrc)
{
  "env": {
    "test": {
      "plugins": ["istanbul"]
    }
  }
}
```

**Step 2: Collect coverage from `window.__coverage__`:**

```ts
// fixtures/istanbul-coverage.ts
import { test as base, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

const coverageDir = path.resolve(process.cwd(), '.nyc_output');

export const test = base.extend({
  page: async ({ page }, use) => {
    await use(page);

    // Istanbul instruments code and exposes coverage on window.__coverage__
    const coverage = await page.evaluate(() => (window as any).__coverage__);
    if (coverage) {
      fs.mkdirSync(coverageDir, { recursive: true });
      const coverageFile = path.join(
        coverageDir,
        `coverage-${crypto.randomUUID()}.json`
      );
      fs.writeFileSync(coverageFile, JSON.stringify(coverage));
    }
  },
});

export { expect };
```

**Step 3: Configure nyc:**

```json
// .nycrc.json
{
  "extends": "@istanbuljs/nyc-config-typescript",
  "all": true,
  "include": ["src/**/*.{ts,tsx,js,jsx}"],
  "exclude": [
    "src/**/*.test.*",
    "src/**/*.spec.*",
    "src/test/**",
    "src/**/*.d.ts"
  ],
  "reporter": ["html", "text-summary", "lcov"],
  "report-dir": "coverage"
}
```

```bash
# Start app with instrumentation
COVERAGE=true npm run dev

# Run tests (in another terminal or after dev server starts)
npx playwright test --project=chromium

# Generate report
npx nyc report
```

### Pattern 3: Coverage Thresholds in CI

**Use when**: Enforcing minimum coverage levels as a quality gate.
**Avoid when**: You are just starting with coverage -- set thresholds after establishing a baseline.

```json
// .nycrc.json
{
  "check-coverage": true,
  "lines": 80,
  "branches": 70,
  "functions": 75,
  "statements": 80,
  "reporter": ["html", "text-summary", "lcov"]
}
```

**GitHub Actions with coverage check:**

```yaml
# .github/workflows/playwright.yml (add to test job steps)
- name: Run Playwright tests with coverage
  run: COVERAGE=true npx playwright test --project=chromium

- name: Generate coverage report
  run: npx nyc report --reporter=html --reporter=text-summary --reporter=lcov
  if: ${{ !cancelled() }}

- name: Check coverage thresholds
  run: npx nyc check-coverage --lines 80 --branches 70 --functions 75

- name: Upload coverage report
  uses: actions/upload-artifact@v4
  if: ${{ !cancelled() }}
  with:
    name: coverage-report
    path: coverage/
    retention-days: 14
```

### Pattern 4: Merging Coverage from Sharded Runs

**Use when**: Tests are sharded across multiple CI machines and you need aggregate coverage.
**Avoid when**: Tests run on a single machine.

```yaml
# .github/workflows/playwright.yml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    steps:
      # ... checkout, install, etc.

      - name: Run sharded tests with coverage
        run: COVERAGE=true npx playwright test --shard=${{ matrix.shard }} --project=chromium

      - name: Upload coverage data
        uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: coverage-${{ strategy.job-index }}
          path: .nyc_output/
          retention-days: 1

  merge-coverage:
    needs: test
    if: ${{ !cancelled() }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci

      - name: Download all coverage data
        uses: actions/download-artifact@v4
        with:
          path: all-coverage
          pattern: coverage-*
          merge-multiple: true

      - name: Merge coverage
        run: |
          mkdir -p .nyc_output
          cp all-coverage/*.json .nyc_output/
          npx nyc report --reporter=html --reporter=text-summary --reporter=lcov
          npx nyc check-coverage --lines 80 --branches 70 --functions 75

      - name: Upload merged coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage/
          retention-days: 14
```

### Pattern 5: CSS Coverage

**Use when**: Identifying unused CSS to reduce bundle size.
**Avoid when**: CSS is not a performance concern for your application.

```ts
// fixtures/css-coverage.ts
import { test as base, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

export const test = base.extend({
  page: async ({ page, browserName }, use, testInfo) => {
    if (browserName === 'chromium') {
      await page.coverage.startCSSCoverage();
    }

    await use(page);

    if (browserName === 'chromium') {
      const coverage = await page.coverage.stopCSSCoverage();

      // Calculate unused CSS percentage per file
      const report = coverage.map((entry) => {
        const totalBytes = entry.text.length;
        const usedBytes = entry.ranges.reduce(
          (acc, range) => acc + (range.end - range.start),
          0
        );
        return {
          url: entry.url,
          totalBytes,
          usedBytes,
          unusedPercent: ((1 - usedBytes / totalBytes) * 100).toFixed(1),
        };
      });

      // Save for analysis
      const outputDir = path.resolve(process.cwd(), 'css-coverage');
      fs.mkdirSync(outputDir, { recursive: true });
      fs.writeFileSync(
        path.join(outputDir, `${testInfo.testId}.json`),
        JSON.stringify(report, null, 2)
      );
    }
  },
});

export { expect };
```

## Decision Guide

| Coverage Type | Tool | Measures | Setup Effort | Accuracy |
|---|---|---|---|---|
| V8 (Chrome DevTools) | `page.coverage` API | JS execution in browser | Low | High (runtime) |
| Istanbul (instrumentation) | `babel-plugin-istanbul` / `vite-plugin-istanbul` | JS with source maps | Medium | High (source-level) |
| CSS | `page.coverage.startCSSCoverage()` | CSS rule usage | Low | High |

| Metric | What It Measures | Good Threshold | Why |
|---|---|---|---|
| Lines | Lines of code executed | 80%+ | Most intuitive; catches dead code |
| Branches | If/else paths taken | 70%+ | Catches untested conditionals |
| Functions | Functions called | 75%+ | Catches unused functions |
| Statements | Individual statements executed | 80%+ | Similar to lines but counts multi-statement lines |

| Scenario | Approach | Why |
|---|---|---|
| Just starting with coverage | V8 coverage, no thresholds | Establish baseline first |
| Mature codebase | Istanbul + thresholds in CI | Source-mapped, enforced |
| Sharded CI | Merge `.nyc_output` after all shards | Aggregate coverage view |
| Only Chromium matters | V8 coverage fixture | Simplest setup, no build changes |
| Need source-level accuracy | Istanbul with bundler plugin | Maps to original source |
| Uploading to Codecov/SonarQube | Generate `lcov` format | Standard format for coverage services |

## Anti-Patterns

| Anti-Pattern | Problem | Do This Instead |
|---|---|---|
| Targeting 100% E2E coverage | E2E tests are expensive; diminishing returns past 80% | Set realistic thresholds; use unit tests for edge cases |
| Coverage collection in all browsers | V8 coverage only works in Chromium; wasted effort | Run coverage only with `--project=chromium` |
| No source filtering | Coverage includes `node_modules` and third-party code | Filter: `entry.url.includes('localhost') && !entry.url.includes('node_modules')` |
| Coverage slowing down CI without value | Collecting coverage on every PR with no thresholds | Either enforce thresholds or skip coverage |
| Istanbul instrumentation in production builds | Performance overhead; exposes internals | Only instrument when `COVERAGE=true` |
| Measuring E2E coverage alone | E2E tests cover happy paths; unit tests cover branches | Combine E2E coverage with unit test coverage |

## Troubleshooting

### Coverage report shows 0% or empty

**Cause (V8)**: Tests aren't using the coverage fixture, or `startJSCoverage()` wasn't called.

**Fix**: Ensure tests import from the coverage fixture file, not directly from `@playwright/test`:

```ts
// Use this:
import { test, expect } from '../fixtures/coverage';

// Not this:
import { test, expect } from '@playwright/test';
```

**Cause (Istanbul)**: Application wasn't instrumented, or `window.__coverage__` is undefined.

**Fix**: Verify the app is running with instrumentation:

```bash
# Check if coverage is exposed
COVERAGE=true npm run dev
# In browser console: window.__coverage__  -> should be an object, not undefined
```

### Coverage files not merging correctly

**Cause**: Coverage JSON files from different shards have incompatible formats or overlapping keys.

**Fix**: Ensure all shards write to `.nyc_output/` with unique filenames:

```ts
const coverageFile = path.join(coverageDir, `coverage-${crypto.randomUUID()}.json`);
```

Then merge with `npx nyc report` (it reads all files in `.nyc_output/`).

### V8 coverage doesn't map to source files

**Cause**: V8 coverage reports against bundled/compiled URLs, not original source files.

**Fix**: Use Istanbul instrumentation instead for source-level accuracy, or use `v8-to-istanbul` to convert:

```bash
npm install -D v8-to-istanbul
```

### Coverage drops when running in parallel

**Cause**: Parallel workers override each other's coverage files if filenames collide.

**Fix**: Include `workerInfo.workerIndex` or a UUID in the filename:

```ts
const coverageFile = path.join(
  coverageDir,
  `coverage-worker${workerInfo.workerIndex}-${crypto.randomUUID()}.json`
);
```

## Related

- [ci/parallel-and-sharding.md](parallel-and-sharding.md) -- merging coverage from sharded runs
- [ci/ci-github-actions.md](ci-github-actions.md) -- coverage thresholds in CI
- [ci/reporting-and-artifacts.md](reporting-and-artifacts.md) -- uploading coverage reports
- [core/configuration.md](../core/configuration.md) -- project setup for coverage
- [core/test-architecture.md](../core/test-architecture.md) -- E2E vs unit test coverage strategies
