# Parallel Execution and Sharding

> **When to use**: Speeding up test suites by running tests concurrently within a single machine (parallelism) or across multiple machines (sharding). Essential once your suite exceeds 5 minutes.

## Quick Reference

```bash
# Workers (parallelism within one machine)
npx playwright test --workers=4          # fixed worker count
npx playwright test --workers=50%        # percentage of CPU cores

# Sharding (splitting across machines)
npx playwright test --shard=1/4          # run first quarter
npx playwright test --shard=2/4          # run second quarter

# Merging shard results
npx playwright merge-reports ./blob-report          # merge to default HTML
npx playwright merge-reports --reporter=html,json ./blob-report  # multiple formats

# Fully parallel mode
npx playwright test --fully-parallel     # override config for this run
```

## Patterns

### Pattern 1: Configuring Workers

**Use when**: Controlling how many tests run simultaneously on one machine.
**Avoid when**: You only have 1-2 tests (parallelism has no effect).

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  // fullyParallel: true means tests WITHIN a file also run in parallel.
  // Without it, only files run in parallel (tests within a file are serial).
  fullyParallel: true,

  // Workers: how many parallel processes
  // - undefined: auto-detect (half CPU cores, capped at a reasonable number)
  // - number: fixed count
  // - string percentage: '50%' of CPU cores
  workers: process.env.CI ? '50%' : undefined,
});
```

**What `fullyParallel` actually controls:**

| Setting | Files run in parallel | Tests within a file run in parallel |
|---|---|---|
| `fullyParallel: false` (default) | Yes | No -- serial within each file |
| `fullyParallel: true` | Yes | Yes -- every test is independent |

**Per-file override when one file needs serial execution:**

```ts
// tests/onboarding.spec.ts
import { test, expect } from '@playwright/test';

// This file's tests run serially even with fullyParallel: true in config
test.describe.configure({ mode: 'serial' });

test('step 1: enter company name', async ({ page }) => {
  // ...
});

test('step 2: choose plan', async ({ page }) => {
  // ...
});
```

### Pattern 2: Sharding Across CI Machines

**Use when**: Suite is too slow for a single machine even with maximum workers. Split work across N separate CI jobs.
**Avoid when**: Suite runs under 5 minutes on one machine.

Sharding splits the test file list into N equal groups. Each shard runs one group.

```bash
# Machine 1          Machine 2          Machine 3          Machine 4
--shard=1/4          --shard=2/4          --shard=3/4          --shard=4/4
```

**Config for sharded runs -- use blob reporter:**

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  fullyParallel: true,
  workers: process.env.CI ? '50%' : undefined,

  // Blob reporter outputs a binary file that can be merged later.
  // In non-CI, use HTML for local viewing.
  reporter: process.env.CI
    ? [['blob'], ['github']]
    : [['html', { open: 'on-failure' }]],
});
```

### Pattern 3: Merging Blob Reports from Shards

**Use when**: You sharded your tests and need a single unified report.
**Avoid when**: No sharding -- the regular HTML reporter works directly.

Each shard produces a `.zip` file in `blob-report/`. After all shards complete, merge them:

```bash
# Download all blob-report/ directories into one folder, then:
npx playwright merge-reports --reporter=html ./all-blob-reports

# Multiple output formats
npx playwright merge-reports --reporter=html,json,junit ./all-blob-reports

# Custom output directory
PLAYWRIGHT_HTML_REPORT=merged-report npx playwright merge-reports --reporter=html ./all-blob-reports
```

**GitHub Actions example (merge job):**

```yaml
merge-reports:
  if: ${{ !cancelled() }}
  needs: test
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: 20
        cache: 'npm'
    - run: npm ci

    - uses: actions/download-artifact@v4
      with:
        path: all-blob-reports
        pattern: blob-report-*
        merge-multiple: true

    - run: npx playwright merge-reports --reporter=html ./all-blob-reports

    - uses: actions/upload-artifact@v4
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 14
```

### Pattern 4: Worker-Scoped Fixtures for Shared Resources

**Use when**: Parallel workers each need an expensive resource (database connection, auth token) that should be created once per worker, not once per test.
**Avoid when**: The resource is cheap to create -- use a regular test-scoped fixture.

```ts
// fixtures.ts
import { test as base } from '@playwright/test';

type WorkerFixtures = {
  dbConnection: DatabaseClient;
  workerAuthToken: string;
};

export const test = base.extend<{}, WorkerFixtures>({
  // Created once per worker process, shared across all tests in that worker
  dbConnection: [async ({}, use) => {
    const db = await DatabaseClient.connect(process.env.DB_URL!);
    await use(db);
    await db.disconnect();
  }, { scope: 'worker' }],

  workerAuthToken: [async ({}, use, workerInfo) => {
    // Each worker gets a unique user to avoid test interference
    const response = await fetch(`${process.env.API_URL}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: `worker-user-${workerInfo.workerIndex}`,
        password: process.env.TEST_PASSWORD,
      }),
    });
    const { token } = await response.json();
    await use(token);
  }, { scope: 'worker' }],
});

export { expect } from '@playwright/test';
```

### Pattern 5: Test Isolation for Safe Parallelism

**Use when**: Preparing tests to run in parallel without interference.
**Avoid when**: Never -- isolation is always required for reliable parallel execution.

**The golden rule**: Each test must create its own state and clean up after itself. No test should depend on or modify state that another test uses.

```ts
// BAD: Tests share a hardcoded user -- parallel runs collide
test('update profile', async ({ page }) => {
  await page.goto('/users/shared-user/profile');
  await page.getByLabel('Name').fill('New Name');
  await page.getByRole('button', { name: 'Save' }).click();
  // Another parallel test also editing "shared-user" -- race condition!
});

// GOOD: Each test creates its own user
test('update profile', async ({ page, request }) => {
  // Create a unique user for this test
  const res = await request.post('/api/test/users', {
    data: { name: `user-${Date.now()}`, email: `${Date.now()}@test.com` },
  });
  const user = await res.json();

  await page.goto(`/users/${user.id}/profile`);
  await page.getByLabel('Name').fill('Updated Name');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByLabel('Name')).toHaveValue('Updated Name');

  // Cleanup
  await request.delete(`/api/test/users/${user.id}`);
});
```

**Using `workerInfo` and `testInfo` for unique identifiers:**

```ts
import { test, expect } from '@playwright/test';

test('create order', async ({ page }, testInfo) => {
  const uniqueId = `order-${testInfo.workerIndex}-${Date.now()}`;
  // Use uniqueId for any data this test creates
  await page.goto(`/orders/new?ref=${uniqueId}`);
  // ...
});
```

### Pattern 6: Dynamic Shard Count Based on Test Count

**Use when**: You want to automatically adjust shard count based on how many tests exist, rather than hardcoding.
**Avoid when**: Your test count is stable and a fixed shard count works well.

```yaml
# .github/workflows/playwright.yml -- dynamic shard calculation
jobs:
  determine-shards:
    runs-on: ubuntu-latest
    outputs:
      shard-count: ${{ steps.calc.outputs.count }}
      shard-matrix: ${{ steps.calc.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - id: calc
        run: |
          TEST_COUNT=$(npx playwright test --list --reporter=json 2>/dev/null | node -e "
            const data = require('fs').readFileSync('/dev/stdin', 'utf8');
            const parsed = JSON.parse(data);
            console.log(parsed.suites?.reduce((acc, s) => acc + (s.specs?.length || 0), 0) || 0);
          ")
          # 1 shard per 20 tests, minimum 1, maximum 8
          SHARDS=$(( (TEST_COUNT + 19) / 20 ))
          SHARDS=$(( SHARDS > 8 ? 8 : SHARDS ))
          SHARDS=$(( SHARDS < 1 ? 1 : SHARDS ))
          # Build matrix array: ["1/N", "2/N", ...]
          MATRIX="["
          for i in $(seq 1 $SHARDS); do
            [ $i -gt 1 ] && MATRIX+=","
            MATRIX+="\"$i/$SHARDS\""
          done
          MATRIX+="]"
          echo "count=$SHARDS" >> $GITHUB_OUTPUT
          echo "matrix=$MATRIX" >> $GITHUB_OUTPUT

  test:
    needs: determine-shards
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shard: ${{ fromJson(needs.determine-shards.outputs.shard-matrix) }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test --shard=${{ matrix.shard }}
```

## Decision Guide

| Scenario | Workers | Shards | Why |
|---|---|---|---|
| < 50 tests, < 5 min | Auto (default) | None | No optimization needed |
| 50-200 tests, 5-15 min | `'50%'` in CI | 2-4 shards | Balance speed and CI cost |
| 200+ tests, > 15 min | `'50%'` in CI | 4-8 shards | Keep feedback under 10 min |
| Flaky tests due to resource contention | Reduce: `workers: 2` | Keep current | Fewer workers = less CPU/memory pressure |
| Tests modify shared database | `workers: 1` or isolate per worker | Still useful | Sharding splits files; workers run them |
| CI has limited CPU/RAM | `workers: 1` or `'25%'` | More shards | Compensate fewer workers with more machines |

| Question | `workers` (in-process) | `--shard` (across machines) |
|---|---|---|
| What does it split? | Tests across CPU cores on one machine | Test files across separate CI jobs |
| Controlled by? | `playwright.config.ts` or `--workers` CLI | `--shard=X/Y` CLI flag |
| Shares memory? | Yes (same machine) | No (separate machines) |
| Report merging needed? | No (single process) | Yes (`merge-reports`) |
| Cost | Free (same machine) | More CI minutes (more machines) |

## Anti-Patterns

| Anti-Pattern | Problem | Do This Instead |
|---|---|---|
| `fullyParallel: false` with no reason | Tests within files run serially; slow suite | Set `fullyParallel: true` unless specific tests need serial |
| `workers: 1` in CI "to be safe" | Negates parallelism entirely | Fix isolation issues; use `workers: '50%'` |
| Tests sharing a hardcoded user account | Race conditions when parallel -- both tests modify same data | Each test creates unique data via API or fixture |
| `--shard=1/4` without blob reporter | Each shard produces its own HTML report; no merged view | Configure `reporter: [['blob']]` for sharded CI runs |
| Sharding with 3 tests | Overhead of shard setup exceeds time saved | Only shard when suite exceeds 5 minutes |
| `test.describe.serial()` everywhere | Kills parallelism, creates hidden dependencies | Use only when tests genuinely depend on prior state |
| Worker count higher than CPU cores | Context switching overhead; slower, not faster | Use `'50%'` or let Playwright auto-detect |
| Not using `fail-fast: false` in CI matrix | One shard failure cancels others; incomplete results | Always set `fail-fast: false` for sharded strategies |

## Troubleshooting

### Tests pass alone but fail when run together

**Cause**: Shared state between tests -- database rows, cookies, global variables, file system.

**Fix**: Isolate each test. Use unique data per test:

```ts
test('create order', async ({ page, request }, testInfo) => {
  // Unique product per test -- no collision with parallel tests
  const product = await request.post('/api/test/products', {
    data: { name: `Widget-${testInfo.workerIndex}-${Date.now()}` },
  });
  // ...
});
```

### Shard produces no tests: "No tests found"

**Cause**: Shard count exceeds the number of test files. A shard gets zero files.

**Fix**: Reduce shard count to at most the number of test files:

```bash
# If you have 10 test files, max 10 shards
npx playwright test --shard=1/10  # OK
npx playwright test --shard=1/20  # Some shards will be empty
```

### Merged report missing some test results

**Cause**: Blob report files from a shard were not downloaded or were overwritten due to name collision.

**Fix**: Give each shard's artifact a unique name:

```yaml
# Each shard
- uses: actions/upload-artifact@v4
  with:
    name: blob-report-${{ strategy.job-index }}  # unique per shard
    path: blob-report/

# Merge step
- uses: actions/download-artifact@v4
  with:
    pattern: blob-report-*
    merge-multiple: true
    path: all-blob-reports
```

### Worker-scoped fixture not shared -- recreated per test

**Cause**: Missing `{ scope: 'worker' }` option, or the fixture depends on a test-scoped fixture.

**Fix**: Ensure the fixture uses worker scope and only depends on worker-scoped fixtures:

```ts
export const test = base.extend<{}, { sharedResource: Resource }>({
  sharedResource: [async ({}, use) => {
    const resource = await Resource.create();
    await use(resource);
    await resource.destroy();
  }, { scope: 'worker' }],  // Don't forget this
});
```

### Tests are slower with more workers

**Cause**: Machine is CPU- or memory-bound. More workers cause thrashing.

**Fix**: Reduce workers until you find the sweet spot:

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  workers: process.env.CI ? 2 : undefined,  // Start low, increase if stable
});
```

## Related

- [ci/ci-github-actions.md](ci-github-actions.md) -- sharded GitHub Actions workflow
- [ci/ci-gitlab.md](ci-gitlab.md) -- GitLab `parallel:` keyword with sharding
- [ci/ci-other.md](ci-other.md) -- sharding on CircleCI, Azure DevOps, Jenkins
- [ci/reporting-and-artifacts.md](reporting-and-artifacts.md) -- blob reporter and merge-reports
- [core/fixtures-and-hooks.md](../core/fixtures-and-hooks.md) -- worker-scoped fixtures
- [core/test-organization.md](../core/test-organization.md) -- parallel vs serial execution
