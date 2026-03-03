# CI: GitLab CI/CD

> **When to use**: Running Playwright tests in GitLab pipelines on merge requests, merges to main, or scheduled pipelines.

## Quick Reference

```bash
# Key commands used in GitLab pipelines
npx playwright install --with-deps    # install browsers + OS deps
npx playwright test --shard=1/4       # run 1 of 4 parallel shards
npx playwright merge-reports ./blob-report  # merge shard results
npx playwright test --reporter=dot    # minimal output for CI logs
```

## Patterns

### Pattern 1: Production-Ready Pipeline (Copy-Paste Starter)

**Use when**: Any GitLab project with Playwright tests. This is the complete, recommended configuration.

```yaml
# .gitlab-ci.yml
image: mcr.microsoft.com/playwright:v1.52.0-noble

stages:
  - install
  - test
  - report

variables:
  CI: "true"
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

# Cache node_modules and npm cache across pipelines
cache:
  key:
    files:
      - package-lock.json
  paths:
    - .npm/
    - node_modules/

install:
  stage: install
  script:
    - npm ci
  artifacts:
    paths:
      - node_modules/
    expire_in: 1 hour

test:
  stage: test
  needs: [install]
  script:
    - npx playwright test
  artifacts:
    when: always
    paths:
      - playwright-report/
      - test-results/
    expire_in: 14 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Pattern 2: Parallel Sharded Execution

**Use when**: Test suite exceeds 10 minutes. Use GitLab's `parallel` keyword to split across jobs automatically.
**Avoid when**: Suite runs under 5 minutes.

```yaml
# .gitlab-ci.yml
image: mcr.microsoft.com/playwright:v1.52.0-noble

stages:
  - install
  - test
  - report

variables:
  CI: "true"
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

cache:
  key:
    files:
      - package-lock.json
  paths:
    - .npm/
    - node_modules/

install:
  stage: install
  script:
    - npm ci
  artifacts:
    paths:
      - node_modules/
    expire_in: 1 hour

test:
  stage: test
  needs: [install]
  parallel: 4
  script:
    - npx playwright test --shard=$CI_NODE_INDEX/$CI_NODE_TOTAL
  artifacts:
    when: always
    paths:
      - blob-report/
    expire_in: 1 hour
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

merge-report:
  stage: report
  needs: [test]
  when: always
  script:
    - npx playwright merge-reports --reporter=html ./blob-report
  artifacts:
    when: always
    paths:
      - playwright-report/
    expire_in: 14 days
```

**Config for sharded pipelines:**

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: process.env.CI
    ? [['blob'], ['dot']]
    : [['html', { open: 'on-failure' }]],
});
```

### Pattern 3: Merge Request Pipelines with Environment Variables

**Use when**: Tests need secrets (API keys, passwords) and should only run on merge requests or the default branch.
**Avoid when**: Tests are fully self-contained with no external dependencies.

```yaml
# .gitlab-ci.yml
image: mcr.microsoft.com/playwright:v1.52.0-noble

stages:
  - test

variables:
  CI: "true"

test:e2e:
  stage: test
  variables:
    BASE_URL: $STAGING_URL
    TEST_PASSWORD: $TEST_PASSWORD
    API_KEY: $API_KEY
  before_script:
    - npm ci
  script:
    - npx playwright test
  artifacts:
    when: always
    paths:
      - playwright-report/
      - test-results/
    expire_in: 14 days
  rules:
    # Run on merge requests
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    # Run on default branch pushes
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    # Allow manual trigger
    - when: manual
      allow_failure: true
```

**Setting variables in GitLab:**
Navigate to **Settings > CI/CD > Variables** and add:
- `STAGING_URL` -- not masked, not protected
- `TEST_PASSWORD` -- masked, protected
- `API_KEY` -- masked, protected

### Pattern 4: Multi-Browser Testing with Child Pipelines

**Use when**: Running Chromium on MRs and all browsers on the default branch.
**Avoid when**: You only test one browser.

```yaml
# .gitlab-ci.yml
image: mcr.microsoft.com/playwright:v1.52.0-noble

stages:
  - install
  - test

variables:
  CI: "true"

install:
  stage: install
  script:
    - npm ci
  artifacts:
    paths:
      - node_modules/
    expire_in: 1 hour

# Chromium only on merge requests (fast feedback)
test:chromium:
  stage: test
  needs: [install]
  script:
    - npx playwright test --project=chromium
  artifacts:
    when: always
    paths:
      - playwright-report/
      - test-results/
    expire_in: 14 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

# All browsers on default branch
test:all-browsers:
  stage: test
  needs: [install]
  parallel:
    matrix:
      - PROJECT: [chromium, firefox, webkit]
  script:
    - npx playwright test --project=$PROJECT
  artifacts:
    when: always
    paths:
      - playwright-report/
      - test-results/
    expire_in: 14 days
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Pattern 5: Custom Docker Image with Application

**Use when**: Tests need the application running alongside Playwright, or you need custom system dependencies.
**Avoid when**: The official Playwright image plus `webServer` in config handles your use case.

```yaml
# .gitlab-ci.yml
stages:
  - test

test:e2e:
  stage: test
  image: mcr.microsoft.com/playwright:v1.52.0-noble
  services:
    - name: postgres:16-alpine
      alias: db
    - name: redis:7-alpine
      alias: cache
  variables:
    CI: "true"
    DATABASE_URL: "postgresql://postgres:postgres@db:5432/test"
    REDIS_URL: "redis://cache:6379"
    POSTGRES_PASSWORD: "postgres"
    POSTGRES_DB: "test"
  before_script:
    - npm ci
    - npx prisma db push
    - npx prisma db seed
  script:
    - npx playwright test
  artifacts:
    when: always
    paths:
      - playwright-report/
      - test-results/
    expire_in: 14 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Pattern 6: Scheduled Nightly Regression

**Use when**: Full regression is too slow for every MR. Run it on a schedule.

```yaml
# .gitlab-ci.yml (add to existing config)
test:nightly:
  stage: test
  image: mcr.microsoft.com/playwright:v1.52.0-noble
  before_script:
    - npm ci
  script:
    - npx playwright test --grep @regression
  artifacts:
    when: always
    paths:
      - playwright-report/
    expire_in: 30 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
```

Set up the schedule in **CI/CD > Schedules**: `0 3 * * 1-5` (3 AM UTC, weekdays).

## Decision Guide

| Scenario | Approach | Why |
|---|---|---|
| Simple project, < 5 min suite | Single `test` job using Playwright Docker image | No sharding overhead; artifacts capture report |
| Suite > 10 min | `parallel: N` with `--shard` | GitLab auto-assigns `CI_NODE_INDEX`/`CI_NODE_TOTAL` |
| Merge request fast feedback | Chromium only on MRs; all browsers on main | 3x fewer pipeline minutes on MRs |
| External services needed (DB, Redis) | `services:` keyword with Postgres/Redis images | GitLab manages service lifecycle |
| Secrets for staging environment | GitLab CI/CD Variables (masked + protected) | Never hardcode secrets in `.gitlab-ci.yml` |
| Full nightly regression | Pipeline schedule (`CI_PIPELINE_SOURCE == "schedule"`) | Avoids blocking MR pipelines |
| Report browsing | `artifacts:` with `paths: [playwright-report/]` | Browse directly in GitLab job artifacts UI |

## Anti-Patterns

| Anti-Pattern | Problem | Do This Instead |
|---|---|---|
| Not using the Playwright Docker image | Installing browsers every run adds 1-2 minutes | Use `mcr.microsoft.com/playwright:v1.52.0-noble` as base image |
| `artifacts: when: on_failure` only | No report when tests pass; can't verify results | Use `when: always` to capture reports regardless |
| No `expire_in` on artifacts | Artifacts accumulate and consume storage | Set `expire_in: 14 days` for reports, `1 hour` for intermediate artifacts |
| `parallel:` without `fail-fast: false` equivalent | GitLab does not cancel siblings by default (good), but `allow_failure: false` means the pipeline fails fast | Acceptable default behavior; no change needed |
| Hardcoding `CI_NODE_TOTAL` in shard flag | Breaks when you change `parallel:` value | Use `--shard=$CI_NODE_INDEX/$CI_NODE_TOTAL` |
| Skipping `needs:` between stages | Jobs wait for all previous stage jobs, not just their dependencies | Use `needs:` for precise dependency graphs |
| Large `cache:` including `node_modules/` without key | Stale cache causes version conflicts | Key cache on `package-lock.json` hash |

## Troubleshooting

### Browser launch fails: "Failed to launch browser"

**Cause**: Not using the Playwright Docker image, or using a version that doesn't match your `@playwright/test` version.

**Fix**: Match the Docker image tag to your Playwright version:

```yaml
# Check your version
# npm ls @playwright/test  ->  @playwright/test@1.52.0
image: mcr.microsoft.com/playwright:v1.52.0-noble
```

### Tests hang in GitLab runner: "Navigation timeout exceeded"

**Cause**: GitLab shared runners may have limited resources. Default timeouts too tight.

**Fix**: Reduce workers and increase timeouts:

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  workers: process.env.CI ? 2 : undefined,
  use: {
    navigationTimeout: process.env.CI ? 30_000 : 15_000,
  },
});
```

### Pipeline runs on every push, not just merge requests

**Cause**: Missing `rules:` configuration. Default GitLab behavior runs on every push.

**Fix**: Add explicit rules:

```yaml
rules:
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Services (Postgres/Redis) not reachable from tests

**Cause**: Using `localhost` instead of the service alias.

**Fix**: Use the service alias as hostname:

```yaml
services:
  - name: postgres:16-alpine
    alias: db  # <-- use "db" as hostname

variables:
  DATABASE_URL: "postgresql://postgres:postgres@db:5432/test"  # not localhost
```

### Merged report is empty after sharded run

**Cause**: Each shard job needs the `blob` reporter, not `html`. The merge step creates the HTML report.

**Fix**: Configure blob reporter for CI:

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: process.env.CI
    ? [['blob'], ['dot']]
    : [['html', { open: 'on-failure' }]],
});
```

## Related

- [ci/ci-github-actions.md](ci-github-actions.md) -- GitHub Actions equivalent
- [ci/ci-other.md](ci-other.md) -- CircleCI, Azure DevOps, Jenkins
- [ci/parallel-and-sharding.md](parallel-and-sharding.md) -- sharding strategies
- [ci/docker-and-containers.md](docker-and-containers.md) -- Docker image details
- [ci/reporting-and-artifacts.md](reporting-and-artifacts.md) -- reporter configuration
