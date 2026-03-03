# Docker and Containers

> **When to use**: Running Playwright tests in containers for reproducible environments, CI pipelines, or local development with consistent browser versions. Essential when your team needs identical test environments across machines.

## Quick Reference

```bash
# Official Playwright Docker images
docker pull mcr.microsoft.com/playwright:v1.52.0-noble     # Ubuntu 24.04, all browsers
docker pull mcr.microsoft.com/playwright:v1.52.0-jammy      # Ubuntu 22.04, all browsers

# Run tests in container
docker run --rm -v $(pwd):/app -w /app mcr.microsoft.com/playwright:v1.52.0-noble \
  npx playwright test

# Check your Playwright version (must match image tag)
npx playwright --version
```

## Patterns

### Pattern 1: Running Tests in the Official Image

**Use when**: Quick, reproducible test runs without building a custom image.
**Avoid when**: You need application services (database, API) running alongside -- use docker-compose instead.

```bash
# Run all tests
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  mcr.microsoft.com/playwright:v1.52.0-noble \
  bash -c "npm ci && npx playwright test"

# Run with environment variables
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  -e CI=true \
  -e BASE_URL=http://host.docker.internal:3000 \
  mcr.microsoft.com/playwright:v1.52.0-noble \
  bash -c "npm ci && npx playwright test"

# Run and extract report
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  -v $(pwd)/playwright-report:/app/playwright-report \
  mcr.microsoft.com/playwright:v1.52.0-noble \
  bash -c "npm ci && npx playwright test"
```

### Pattern 2: Custom Dockerfile

**Use when**: You need additional system dependencies, pre-installed npm packages, or a smaller image with only certain browsers.
**Avoid when**: The official image works as-is.

```dockerfile
# Dockerfile.playwright
FROM mcr.microsoft.com/playwright:v1.52.0-noble

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the project
COPY . .

# Default command
CMD ["npx", "playwright", "test"]
```

```bash
# Build and run
docker build -f Dockerfile.playwright -t my-e2e-tests .
docker run --rm my-e2e-tests

# Run with specific options
docker run --rm my-e2e-tests npx playwright test --project=chromium

# Extract report
docker run --rm -v $(pwd)/reports:/app/playwright-report my-e2e-tests
```

**Slim image with only Chromium:**

```dockerfile
# Dockerfile.playwright-chromium
FROM node:20-slim

# Install only Chromium dependencies
RUN npx playwright install --with-deps chromium

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

CMD ["npx", "playwright", "test", "--project=chromium"]
```

### Pattern 3: Docker Compose with Application Stack

**Use when**: Tests need the full application stack: web server, database, cache, and Playwright running together.
**Avoid when**: Tests run against a remote environment (staging/prod) -- no local services needed.

```yaml
# docker-compose.yml
services:
  # Application under test
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=test
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/test
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started

  # Database
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: test
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    tmpfs:
      - /var/lib/postgresql/data  # RAM disk for speed

  # Cache
  cache:
    image: redis:7-alpine

  # Playwright test runner
  e2e:
    image: mcr.microsoft.com/playwright:v1.52.0-noble
    working_dir: /app
    volumes:
      - .:/app
      - /app/node_modules  # prevent host node_modules from overriding
    environment:
      - CI=true
      - BASE_URL=http://app:3000
    depends_on:
      - app
    command: bash -c "npm ci && npx playwright test"
    profiles:
      - test  # only start with: docker compose --profile test up
```

```bash
# Run the full stack with tests
docker compose --profile test up --abort-on-container-exit --exit-code-from e2e

# Run just the app (for local dev)
docker compose up app

# Run tests against already-running stack
docker compose --profile test run --rm e2e npx playwright test

# Tear down everything
docker compose --profile test down -v
```

### Pattern 4: Extracting Reports and Traces from Containers

**Use when**: You need test artifacts (HTML reports, traces, screenshots) accessible on the host after container tests complete.
**Avoid when**: CI handles artifact collection natively (GitHub Actions, GitLab artifacts).

```bash
# Method 1: Bind mount the output directories
docker run --rm \
  -v $(pwd):/app \
  -v $(pwd)/playwright-report:/app/playwright-report \
  -v $(pwd)/test-results:/app/test-results \
  -w /app \
  mcr.microsoft.com/playwright:v1.52.0-noble \
  bash -c "npm ci && npx playwright test"

# Method 2: Copy artifacts from a stopped container
docker run --name e2e-run \
  -v $(pwd):/app \
  -w /app \
  mcr.microsoft.com/playwright:v1.52.0-noble \
  bash -c "npm ci && npx playwright test" || true

docker cp e2e-run:/app/playwright-report ./playwright-report
docker cp e2e-run:/app/test-results ./test-results
docker rm e2e-run

# View the report
npx playwright show-report ./playwright-report
```

**Docker Compose for report extraction:**

```yaml
# docker-compose.yml (add to e2e service)
services:
  e2e:
    image: mcr.microsoft.com/playwright:v1.52.0-noble
    working_dir: /app
    volumes:
      - .:/app
      - ./playwright-report:/app/playwright-report
      - ./test-results:/app/test-results
    # ... rest of config
```

### Pattern 5: CI Container Strategies

**Use when**: Your CI environment benefits from containerized test execution.

**GitHub Actions -- container job:**

```yaml
# .github/workflows/playwright.yml
jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: mcr.microsoft.com/playwright:v1.52.0-noble
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx playwright test
        env:
          HOME: /root
```

**GitLab CI -- image directive:**

```yaml
# .gitlab-ci.yml
test:
  image: mcr.microsoft.com/playwright:v1.52.0-noble
  script:
    - npm ci
    - npx playwright test
```

**Jenkins -- Docker agent:**

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright:v1.52.0-noble'
            args '-u root'
        }
    }
    stages {
        stage('Test') {
            steps {
                sh 'npm ci'
                sh 'npx playwright test'
            }
        }
    }
}
```

### Pattern 6: Development Container (devcontainer)

**Use when**: Your team uses VS Code Dev Containers or GitHub Codespaces and needs Playwright available in the development environment.
**Avoid when**: Everyone installs Playwright locally and version differences don't cause issues.

```json
// .devcontainer/devcontainer.json
{
  "name": "Playwright Dev",
  "image": "mcr.microsoft.com/playwright:v1.52.0-noble",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20"
    }
  },
  "postCreateCommand": "npm ci",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-playwright.playwright"
      ]
    }
  },
  "forwardPorts": [3000, 9323],
  "remoteUser": "root"
}
```

## Decision Guide

| Scenario | Approach | Why |
|---|---|---|
| Simple CI pipeline | Official Playwright image as CI image | Browsers pre-installed; zero browser install time |
| Tests need database + cache | Docker Compose with app, db, cache, e2e services | Full stack in isolated containers |
| Team needs identical environments | Dev Container or custom Dockerfile | Eliminate "works on my machine" |
| Only testing Chromium | Slim image: `node:20-slim` + `install --with-deps chromium` | Smaller image, faster pulls |
| Cross-browser testing | Official Playwright image (has all browsers) | All three engines pre-installed |
| Local development | Run directly on host, not in container | Faster iteration, easier debugging |
| CI with artifact extraction | Bind mount report/results dirs or use CI artifact upload | Reports accessible after container exits |

| Image | Size | Browsers | Base OS |
|---|---|---|---|
| `mcr.microsoft.com/playwright:v1.52.0-noble` | ~2 GB | Chromium, Firefox, WebKit | Ubuntu 24.04 |
| `mcr.microsoft.com/playwright:v1.52.0-jammy` | ~2 GB | Chromium, Firefox, WebKit | Ubuntu 22.04 |
| Custom slim (Chromium only) | ~800 MB | Chromium | Depends on base |

## Anti-Patterns

| Anti-Pattern | Problem | Do This Instead |
|---|---|---|
| Image tag doesn't match `@playwright/test` version | Browser binaries incompatible with Playwright library | Always match: `v1.52.0` image for `@playwright/test@1.52.0` |
| Using `latest` tag | Unpredictable; image updates can break tests | Pin to exact version: `v1.52.0-noble` |
| Installing browsers inside container at runtime | Wastes 60-90 seconds on every run | Use official image (browsers pre-installed) or build custom image with browsers baked in |
| Running as non-root without configuring sandbox | Chromium sandbox fails with permission errors | Run as root (`-u root`) or disable sandbox (`--no-sandbox` in launch args) |
| Bind-mounting `node_modules` from host | Platform-specific binaries (macOS vs Linux) cause crashes | Use anonymous volume: `-v /app/node_modules` |
| No health checks on dependent services | Tests start before database is ready | Add `healthcheck` to db service; use `depends_on: condition: service_healthy` |
| Building application inside the Playwright container | Large image, slow builds, wrong base for your app | Separate app and e2e containers in docker-compose |

## Troubleshooting

### "browserType.launch: Executable doesn't exist" in container

**Cause**: Playwright version in `package.json` doesn't match the Docker image version.

**Fix**: Ensure exact version match:

```bash
# Check your version
npm ls @playwright/test
# @playwright/test@1.52.0

# Use matching image
docker pull mcr.microsoft.com/playwright:v1.52.0-noble
```

### Tests fail with "net::ERR_CONNECTION_REFUSED" in docker-compose

**Cause**: Tests are trying to reach `localhost:3000` but the app is in a different container.

**Fix**: Use the service name as hostname and configure `baseURL`:

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
  },
  // Disable webServer in Docker -- app is managed by docker-compose
  ...(process.env.CI ? {} : {
    webServer: {
      command: 'npm run dev',
      url: 'http://localhost:3000',
      reuseExistingServer: true,
    },
  }),
});
```

```yaml
# docker-compose.yml
e2e:
  environment:
    - BASE_URL=http://app:3000  # "app" is the service name
```

### Permission denied on mounted volumes

**Cause**: Container runs as root but host files are owned by your user, or vice versa.

**Fix**: Match user IDs or run as root:

```bash
# Run as your host user
docker run --rm -u $(id -u):$(id -g) \
  -v $(pwd):/app -w /app \
  mcr.microsoft.com/playwright:v1.52.0-noble \
  npx playwright test

# Or run as root (simpler, fine for CI)
docker run --rm \
  -v $(pwd):/app -w /app \
  mcr.microsoft.com/playwright:v1.52.0-noble \
  npx playwright test
```

### Container tests are much slower than local

**Cause**: Docker Desktop on macOS/Windows has I/O overhead for bind-mounted volumes.

**Fix**: Copy files into the container instead of mounting:

```dockerfile
# Dockerfile.playwright
FROM mcr.microsoft.com/playwright:v1.52.0-noble
WORKDIR /app
COPY . .
RUN npm ci
CMD ["npx", "playwright", "test"]
```

Or use delegated mount on macOS:

```bash
docker run --rm \
  -v $(pwd):/app:delegated \
  -w /app \
  mcr.microsoft.com/playwright:v1.52.0-noble \
  bash -c "npm ci && npx playwright test"
```

## Related

- [ci/ci-github-actions.md](ci-github-actions.md) -- container jobs in GitHub Actions
- [ci/ci-gitlab.md](ci-gitlab.md) -- Docker images in GitLab CI
- [ci/ci-other.md](ci-other.md) -- Docker agents in Jenkins, CircleCI
- [ci/parallel-and-sharding.md](parallel-and-sharding.md) -- sharding within containers
- [ci/reporting-and-artifacts.md](reporting-and-artifacts.md) -- extracting reports from containers
