---
name: Replicate Automation
description: "Automate Replicate AI model operations -- run predictions, upload files, inspect model schemas, list versions, and manage prediction history via the Composio MCP integration."
requires:
  mcp:
    - rube
---

# Replicate Automation

Automate your Replicate AI model workflows -- run predictions on any public model (image generation, LLMs, audio, video), upload input files, inspect model schemas and documentation, list model versions, and track prediction history.

**Toolkit docs:** [composio.dev/toolkits/replicate](https://composio.dev/toolkits/replicate)

---

## Setup

1. Add the Composio MCP server to your client: `https://rube.app/mcp`
2. Connect your Replicate account when prompted (API token authentication)
3. Start using the workflows below

---

## Core Workflows

### 1. Get Model Details and Schema

Use `REPLICATE_MODELS_GET` to inspect a model's input/output schema before running predictions.

```
Tool: REPLICATE_MODELS_GET
Inputs:
  - model_owner: string (required) -- e.g., "meta", "black-forest-labs", "stability-ai"
  - model_name: string (required) -- e.g., "meta-llama-3-8b-instruct", "flux-1.1-pro"
```

**Important:** Each model has unique input keys and types. Always check the `openapi_schema` from this response before constructing prediction inputs.

### 2. Run a Prediction

Use `REPLICATE_MODELS_PREDICTIONS_CREATE` to run inference on any model with optional synchronous waiting and webhooks.

```
Tool: REPLICATE_MODELS_PREDICTIONS_CREATE
Inputs:
  - model_owner: string (required) -- e.g., "meta", "black-forest-labs"
  - model_name: string (required) -- e.g., "flux-1.1-pro", "sdxl"
  - input: object (required) -- model-specific inputs, e.g., { "prompt": "A sunset over mountains" }
  - wait_for: integer (1-60 seconds, optional) -- synchronous wait for completion
  - cancel_after: string (optional) -- max execution time, e.g., "300s", "5m"
  - webhook: string (optional) -- HTTPS URL for async completion notifications
  - webhook_events_filter: array (optional) -- ["start", "output", "logs", "completed"]
```

**Sync vs Async:** Use `wait_for` (1-60s) for fast models. For long-running jobs, omit it and use webhooks or poll via `REPLICATE_PREDICTIONS_LIST`.

### 3. Upload Files for Model Input

Use `REPLICATE_CREATE_FILE` to upload images, documents, or other binary inputs that models need.

```
Tool: REPLICATE_CREATE_FILE
Inputs:
  - content: string (required) -- base64-encoded file content
  - filename: string (required) -- e.g., "input.png", "audio.wav" (max 255 bytes UTF-8)
  - content_type: string (default "application/octet-stream") -- MIME type
  - metadata: object (optional) -- custom JSON metadata
```

### 4. Read Model Documentation

Use `REPLICATE_MODELS_README_GET` to access a model's README in Markdown format for detailed usage instructions.

```
Tool: REPLICATE_MODELS_README_GET
Inputs:
  - model_owner: string (required)
  - model_name: string (required)
```

### 5. List Model Versions

Use `REPLICATE_MODELS_VERSIONS_LIST` to see all available versions of a model, sorted newest first.

```
Tool: REPLICATE_MODELS_VERSIONS_LIST
Inputs:
  - model_owner: string (required)
  - model_name: string (required)
```

### 6. Track Prediction History and Files

Use `REPLICATE_PREDICTIONS_LIST` to retrieve prediction history, and `REPLICATE_FILES_GET`/`REPLICATE_FILES_LIST` to manage uploaded files.

```
Tool: REPLICATE_PREDICTIONS_LIST
  - Lists all predictions for the authenticated user with pagination

Tool: REPLICATE_FILES_LIST
  - Lists uploaded files, most recent first

Tool: REPLICATE_FILES_GET
  - Get details of a specific file by ID
```

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| Model-specific input keys | Each model has unique input keys and types. Using the wrong key causes validation errors. Always call `REPLICATE_MODELS_GET` first to check the `openapi_schema`. |
| File upload encoding | `REPLICATE_CREATE_FILE` requires base64-encoded content. Binary files treated as text (UTF-8) will fail with decode errors. |
| Public vs deployment paths | Public models must be run via `REPLICATE_MODELS_PREDICTIONS_CREATE`. Using deployment-oriented paths causes HTTP 404 failures. |
| Sync wait limits | `wait_for` supports 1-60 seconds only. Long-running jobs need async handling via webhooks or polling `REPLICATE_PREDICTIONS_LIST`. |
| Image model constraints | Image models like flux-1.1-pro have specific constraints (e.g., max width/height 1440px, valid aspect ratios). Check the model schema first. |
| Stale file references | Heavy usage creates many uploads. Routinely check `REPLICATE_FILES_LIST` to avoid using stale `file_id` references. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `REPLICATE_MODELS_GET` | Get model details, schema, and metadata |
| `REPLICATE_MODELS_PREDICTIONS_CREATE` | Run a prediction on a model |
| `REPLICATE_CREATE_FILE` | Upload a file for model input |
| `REPLICATE_MODELS_README_GET` | Get model README documentation |
| `REPLICATE_MODELS_VERSIONS_LIST` | List all versions of a model |
| `REPLICATE_PREDICTIONS_LIST` | List prediction history with pagination |
| `REPLICATE_FILES_LIST` | List uploaded files |
| `REPLICATE_FILES_GET` | Get file details by ID |

---

*Powered by [Composio](https://composio.dev)*
