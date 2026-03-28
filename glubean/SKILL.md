---
name: glubean
description: Write, run, and debug API tests using @glubean/sdk — a TypeScript-first API test automation framework. Handles project setup, test generation, auth configuration, and CI wiring.
---

# Glubean — API Test Automation

## When to Use This Skill

- You want to write API verification tests in TypeScript
- You need to set up a new API testing project from scratch
- You want AI to generate tests from an OpenAPI spec or endpoint docs
- You need to debug failing API tests with structured traces
- You want to wire API tests into CI (GitHub Actions, etc.)

## What This Skill Does

1. **Bootstraps projects** — guides you through `npx glubean@latest init` with the right template, environment setup, and auth configuration
2. **Writes tests** — generates typed API tests using `@glubean/sdk` patterns (smoke, CRUD, data-driven, builder workflows)
3. **Runs and debugs** — executes tests via MCP, reads structured failures (assertions, traces, response schemas), and fixes iteratively
4. **Configures auth** — supports bearer, API key, basic, OAuth2 (client credentials, refresh token, authorization code), with explicit user confirmation before writing auth code
5. **Wires CI** — creates GitHub Actions workflows targeting `tests/` with result artifacts

## How to Use

### Install the full skill (recommended)

```bash
npx skills add glubean/skill
```

This installs the complete skill with SDK reference, 12 pattern guides, CLI reference, and project workflow — everything the AI needs to write production-quality tests.

### Basic Usage

```
Write smoke tests for my /users and /products endpoints
```

```
Set up a new Glubean project for the Stripe API
```

```
Help me write CRUD tests for the GitHub Issues API in explore/
```

### Advanced Usage

```
Read context/openapi.json and generate comprehensive tests for all endpoints — happy path, auth boundaries, and validation errors
```

```
My tests are failing with 401 — diagnose the auth configuration and fix it
```

```
Move my stable explore/ tests to tests/ and set up GitHub Actions CI
```

## Example

**User:** Write a smoke test for the DummyJSON products API

**Output:** A complete test file with typed responses, assertions, and tags — ready to run with `npx glubean@latest run` or the VS Code extension Play button.

## Tips

- Install the [VS Code extension](https://marketplace.visualstudio.com/items?itemName=Glubean.glubean) for Play buttons, inline results, and trace inspection
- Configure MCP (`npx glubean@latest config mcp`) for AI closed-loop: write, run, read failures, fix, rerun
- Use `explore/` for interactive API exploration (individual tests), `tests/` for CI regression (builder workflows)
- Clone the [cookbook](https://github.com/glubean/cookbook) to learn patterns from 23 real test files

## Common Use Cases

- Replacing Postman collections with version-controlled TypeScript tests
- Generating API tests from OpenAPI specs or endpoint documentation
- Setting up API verification in CI pipelines
- Debugging API integration failures with structured traces
- Migrating from manual HTTP testing to automated test suites
