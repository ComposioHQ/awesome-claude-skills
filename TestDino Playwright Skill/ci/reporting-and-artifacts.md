# Reporting and Artifacts

> **When to use**: Configuring test output for local debugging, CI dashboards, and team visibility. Every project needs a reporting strategy from day one.

## Quick Reference

```bash
# View the last HTML report
npx playwright show-report

# Run with specific reporter
npx playwright test --reporter=html
npx playwright test --reporter=dot           # minimal CI output
npx playwright test --reporter=line          # one line per test
npx playwright test --reporter=json          # machine-readable
npx playwright test --reporter=junit         # CI integration

# Multiple reporters via CLI
npx playwright test --reporter=dot,html

# Merge shard reports
npx playwright merge-reports --reporter=html ./blob-report
```

## Patterns

### Pattern 1: Multi-Reporter Configuration

**Use when**: Every project. You always want at least two reporters: one for humans, one for CI.
**Avoid when**: Never -- always configure reporters.

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: process.env.CI
    ? [
        // CI: machine-readable + human-readable + CI annotations
        ['dot'],                                    // minimal console output
        ['html', { open: 'never' }],               // browsable report (uploaded as artifact)
        ['junit', { outputFile: 'test-results/junit.xml' }],  // CI test tab integration
        ['github'],                                 // PR annotations (GitHub Actions only)
      ]
    : [
        // Local: detailed console + auto-opening report
        ['list'],                                   // verbose console output
        ['html', { open: 'on-failure' }],          // auto-open on failure
      ],
});
```

### Pattern 2: Built-in Reporters in Detail

**Use when**: Choosing the right reporter for your context.

| Reporter | Output | Best For |
|---|---|---|
| `list` | One line per test with pass/fail | Local development |
| `line` | Updates a single line as tests complete | Local, less verbose |
| `dot` | Single dot per test: `.` pass, `F` fail | CI logs (minimal) |
| `html` | Interactive HTML page with traces | Post-run analysis |
| `json` | Machine-readable JSON to stdout or file | Custom tooling, dashboards |
| `junit` | JUnit XML | CI platforms (Azure DevOps, Jenkins, CircleCI) |
| `github` | GitHub Actions annotations | GitHub PRs |
| `blob` | Binary archive for shard merging | Sharded CI runs |

**JSON reporter -- write to file:**

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [
    ['json', { outputFile: 'test-results/results.json' }],
  ],
});
```

**JUnit reporter -- customize output:**

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [
    ['junit', {
      outputFile: 'test-results/junit.xml',
      stripANSIControlSequences: true,
      includeProjectInTestName: true,
    }],
  ],
});
```

### Pattern 3: Custom Reporter

**Use when**: Built-in reporters don't meet your needs -- you want Slack notifications, database logging, or custom dashboards.
**Avoid when**: A built-in reporter or existing third-party reporter covers your case.

```ts
// reporters/slack-reporter.ts
import type {
  FullConfig,
  FullResult,
  Reporter,
  Suite,
  TestCase,
  TestResult,
} from '@playwright/test/reporter';

class SlackReporter implements Reporter {
  private passed = 0;
  private failed = 0;
  private skipped = 0;
  private failures: string[] = [];

  onTestEnd(test: TestCase, result: TestResult) {
    switch (result.status) {
      case 'passed':
        this.passed++;
        break;
      case 'failed':
      case 'timedOut':
        this.failed++;
        this.failures.push(`${test.title}: ${result.error?.message?.split('\n')[0]}`);
        break;
      case 'skipped':
        this.skipped++;
        break;
    }
  }

  async onEnd(result: FullResult) {
    const total = this.passed + this.failed + this.skipped;
    const emoji = this.failed > 0 ? ':red_circle:' : ':large_green_circle:';
    const text = [
      `${emoji} *Playwright Tests*: ${result.status}`,
      `Passed: ${this.passed} | Failed: ${this.failed} | Skipped: ${this.skipped} | Total: ${total}`,
      `Duration: ${(result.duration / 1000).toFixed(1)}s`,
    ];

    if (this.failures.length > 0) {
      text.push('', '*Failures:*');
      this.failures.slice(0, 5).forEach((f) => text.push(`  - ${f}`));
      if (this.failures.length > 5) {
        text.push(`  ...and ${this.failures.length - 5} more`);
      }
    }

    const webhookUrl = process.env.SLACK_WEBHOOK_URL;
    if (webhookUrl) {
      await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text.join('\n') }),
      });
    }
  }
}

export default SlackReporter;
```

**Register the custom reporter:**

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [
    ['dot'],
    ['html', { open: 'never' }],
    ['./reporters/slack-reporter.ts'],
  ],
});
```

### Pattern 4: Trace File Management

**Use when**: Debugging test failures. Traces capture a complete timeline of actions, network requests, DOM snapshots, and console logs.
**Avoid when**: Never disable traces entirely in CI -- the on-first-retry setting has minimal overhead.

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  retries: process.env.CI ? 2 : 0,
  use: {
    // 'on-first-retry': records trace only when a test fails and retries.
    // Minimal overhead on passing tests, full debugging on failures.
    trace: 'on-first-retry',
  },
});
```

**Trace options:**

| Value | Records trace | When | Overhead |
|---|---|---|---|
| `'off'` | Never | -- | None |
| `'on'` | Every test | Always | High (large files) |
| `'on-first-retry'` | On first retry after failure | Retries only | Minimal |
| `'retain-on-failure'` | Every test, keeps only failures | Failures | Medium |
| `'retain-on-first-failure'` | Every test, keeps only first failure | First failure | Medium |

**Viewing traces:**

```bash
# Open trace viewer locally
npx playwright show-trace test-results/my-test/trace.zip

# Open trace from HTML report (click "Traces" tab in the report)
npx playwright show-report

# Online trace viewer (upload trace.zip)
# https://trace.playwright.dev
```

### Pattern 5: Screenshot and Video Configuration

**Use when**: Visual evidence of test failures is valuable for debugging or bug reports.
**Avoid when**: Never disable screenshots in CI -- the on-failure setting is cheap.

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    // Screenshots
    screenshot: 'only-on-failure',  // capture final state on failure

    // Video
    video: 'retain-on-failure',     // record all, keep only failures

    // Video size (optional -- smaller = less disk)
    video: {
      mode: 'retain-on-failure',
      size: { width: 1280, height: 720 },
    },
  },
});
```

**Screenshot options:**

| Value | Captures | Disk cost |
|---|---|---|
| `'off'` | Never | None |
| `'on'` | Every test (at end) | High |
| `'only-on-failure'` | Failed tests only | Low |

**Video options:**

| Value | Records | Keeps | Disk cost |
|---|---|---|---|
| `'off'` | Never | -- | None |
| `'on'` | Every test | All | Very high |
| `'on-first-retry'` | On retry | Retried tests | Low |
| `'retain-on-failure'` | Every test | Failed only | Medium |

### Pattern 6: Artifact Organization for CI

**Use when**: Keeping test artifacts organized and accessible in CI.

**Recommended directory structure:**

```
test-results/             # Playwright's default output directory
├── my-test-chromium/
│   ├── trace.zip         # Trace file
│   ├── test-failed-1.png # Screenshot
│   └── video.webm        # Video recording
├── another-test-firefox/
│   ├── trace.zip
│   └── test-failed-1.png
└── junit.xml             # JUnit report (if configured)

playwright-report/        # HTML report directory
├── index.html
└── data/
    └── ...

blob-report/              # Blob report for shard merging
└── report-1.zip
```

**GitHub Actions artifact upload:**

```yaml
# Upload HTML report (always -- useful even when tests pass)
- uses: actions/upload-artifact@v4
  if: ${{ !cancelled() }}
  with:
    name: playwright-report
    path: playwright-report/
    retention-days: 14

# Upload traces and screenshots (only on failure -- saves storage)
- uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: test-traces
    path: |
      test-results/**/trace.zip
      test-results/**/*.png
      test-results/**/*.webm
    retention-days: 7
```

### Pattern 7: Allure Integration

**Use when**: Your team uses Allure for test reporting across multiple test frameworks.
**Avoid when**: The built-in HTML reporter meets your needs (it usually does).

```bash
# Install Allure reporter
npm install -D allure-playwright
```

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [
    ['line'],
    ['allure-playwright', {
      detail: true,
      outputFolder: 'allure-results',
      suiteTitle: true,
    }],
  ],
});
```

```bash
# Generate and view Allure report
npx allure generate allure-results -o allure-report --clean
npx allure open allure-report

# Or use Allure CLI
allure serve allure-results
```

**Add Allure metadata to tests:**

```ts
import { test, expect } from '@playwright/test';
import { allure } from 'allure-playwright';

test('checkout flow', async ({ page }) => {
  await allure.epic('E-Commerce');
  await allure.feature('Checkout');
  await allure.story('Credit Card Payment');
  await allure.severity('critical');

  await page.goto('/checkout');
  // ... test implementation
});
```

## Decision Guide

| Scenario | Reporter Configuration | Why |
|---|---|---|
| Local development | `[['list'], ['html', { open: 'on-failure' }]]` | Verbose console + auto-opening report on failure |
| GitHub Actions | `[['dot'], ['html'], ['github']]` | Minimal logs + report artifact + PR annotations |
| GitLab CI | `[['dot'], ['html'], ['junit']]` | Minimal logs + report artifact + test tab |
| Azure DevOps / Jenkins | `[['dot'], ['html'], ['junit']]` | JUnit for native test results integration |
| Sharded CI | `[['blob'], ['github']]` | Blob for merging; github for PR annotations |
| Team uses Allure | `[['line'], ['allure-playwright']]` | Cross-framework reporting consistency |
| Custom dashboard | `[['json', { outputFile: '...' }]]` + custom reporter | JSON for data, custom for notifications |

| Artifact | When to Collect | Retention | Upload Condition |
|---|---|---|---|
| HTML report | Always | 14 days | `if: ${{ !cancelled() }}` |
| Traces (`.zip`) | On failure | 7 days | `if: failure()` |
| Screenshots (`.png`) | On failure | 7 days | `if: failure()` |
| Videos (`.webm`) | On failure | 7 days | `if: failure()` |
| JUnit XML | Always | 14 days | `if: ${{ !cancelled() }}` |
| Blob report | Always (sharded) | 1 day | `if: ${{ !cancelled() }}` |

## Anti-Patterns

| Anti-Pattern | Problem | Do This Instead |
|---|---|---|
| No reporter configured | Default `list` only; no persistent report | Always configure `html` + one CI reporter |
| `trace: 'on'` in CI | Massive artifacts (50-100 MB per test), slow uploads | Use `trace: 'on-first-retry'` |
| `video: 'on'` in CI | Enormous storage cost; slows test execution | Use `video: 'retain-on-failure'` |
| Only uploading artifacts on failure | No report when tests pass; can't verify results | Upload with `if: ${{ !cancelled() }}` (always) |
| No retention limits on artifacts | CI storage fills up within weeks | Set `retention-days: 7-14` |
| Using only `dot` reporter with no HTML | Can't drill into failures after the run | Always pair `dot` with `html` in CI |
| JUnit output to stdout | Interferes with console output; hard to parse | Write to file: `['junit', { outputFile: 'results/junit.xml' }]` |
| Custom reporter that blocks `onEnd` | Slow Slack/HTTP calls delay pipeline completion | Use `Promise.race` with a timeout in custom reporters |

## Troubleshooting

### HTML report is empty or missing tests

**Cause**: Another reporter is conflicting, or `outputFolder` was overridden to a non-default path.

**Fix**: Check your reporter config. The HTML report defaults to `playwright-report/`:

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [['html', { outputFolder: 'playwright-report', open: 'never' }]],
});
```

### Traces are too large for CI artifact upload

**Cause**: `trace: 'on'` records every test, even passing ones.

**Fix**: Switch to `'on-first-retry'` and ensure `retries > 0` in CI:

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  retries: process.env.CI ? 2 : 0,
  use: {
    trace: 'on-first-retry',
  },
});
```

### JUnit XML not recognized by CI platform

**Cause**: Output path doesn't match what the CI task expects, or the file is empty.

**Fix**: Ensure the path matches your CI configuration:

```ts
// playwright.config.ts -- the outputFile path
reporter: [['junit', { outputFile: 'test-results/junit.xml' }]],
```

```yaml
# GitHub Actions
- uses: dorny/test-reporter@v1
  with:
    path: test-results/junit.xml
    reporter: java-junit

# Azure DevOps
- task: PublishTestResults@2
  inputs:
    testResultsFiles: 'test-results/junit.xml'

# Jenkins
junit 'test-results/junit.xml'
```

### `merge-reports` produces empty report

**Cause**: Shards are using `html` reporter instead of `blob`. Only `blob` output can be merged.

**Fix**: Use blob reporter for sharded runs:

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: process.env.CI
    ? [['blob'], ['dot']]  // blob for merge, dot for console
    : [['html', { open: 'on-failure' }]],
});
```

### Screenshots not appearing in HTML report

**Cause**: `screenshot: 'off'` or screenshots are in `test-results/` but not linked to the report.

**Fix**: Enable screenshots and ensure both directories are available:

```ts
use: {
  screenshot: 'only-on-failure',
},
```

The HTML report automatically embeds screenshots from `test-results/`. If you move or delete `test-results/`, screenshots will be missing from the report.

## Related

- [ci/ci-github-actions.md](ci-github-actions.md) -- artifact upload in GitHub Actions
- [ci/ci-gitlab.md](ci-gitlab.md) -- artifact configuration in GitLab
- [ci/parallel-and-sharding.md](parallel-and-sharding.md) -- blob reporter for sharded runs
- [core/configuration.md](../core/configuration.md) -- trace, screenshot, video settings
- [core/debugging.md](../core/debugging.md) -- using traces and screenshots for debugging
