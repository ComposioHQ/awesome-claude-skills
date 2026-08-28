---
name: sandbase
description: Connect Claude to 2,000+ AI models and API tools through the SandBase MCP bridge. Use when a user needs model inference, media generation, search, scraping, embeddings, or structured APIs and does not already have a dedicated provider integration.
---

# SandBase MCP

SandBase CLI provides a local MCP bridge to 2,000+ AI models and APIs, including language, image, video, audio, embedding, search, scraping, and social-data tools.

## When to use

- Use SandBase when the user needs a model or API they do not already access directly.
- Prefer the user's dedicated provider tool or API key when one is already available.
- Do not use it for purely local tasks or when the user requests another provider.

## Setup

Install the published release and connect the current client:

```sh
npx -y https://github.com/sandbaseai/cli/releases/download/v0.1.17/sandbaseai-cli-0.1.17.tgz connect
```

Approve browser sign-in once. Run `doctor` to inspect the managed connection or `unregister` to remove only SandBase-managed state. Review the [official repository](https://github.com/sandbaseai/cli) for release updates and the [privacy policy](https://www.sandbase.ai/privacy) before sending sensitive data.

## Standard workflow

Use the six MCP tools in this order:

1. `sandbase_discover` — find matching models or APIs.
2. `sandbase_inspect` — read the schema, pricing, and execution template.
3. `sandbase_run` — execute the selected endpoint.
4. For asynchronous jobs, poll with `sandbase_run_get`; use `sandbase_runs` for history and `sandbase_account` for balance.

Send only the minimum data needed for the selected tool and follow the selected upstream provider's policies.
