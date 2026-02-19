---
name: OpenAI Automation
description: "Automate OpenAI API operations -- generate responses with multimodal and structured output support, create embeddings, generate images, and list models via the Composio MCP integration."
requires:
  mcp:
    - rube
---

# OpenAI Automation

Automate your OpenAI API workflows -- generate text with the Responses API (including multimodal image+text inputs and structured JSON outputs), create embeddings for search and clustering, generate images with DALL-E and GPT Image models, and list available models.

**Toolkit docs:** [composio.dev/toolkits/openai](https://composio.dev/toolkits/openai)

---

## Setup

1. Add the Composio MCP server to your client: `https://rube.app/mcp`
2. Connect your OpenAI account when prompted (API key authentication)
3. Start using the workflows below

---

## Core Workflows

### 1. Generate a Response (Text, Multimodal, Structured)

Use `OPENAI_CREATE_RESPONSE` for one-shot model responses including text, image analysis, OCR, and structured JSON outputs.

```
Tool: OPENAI_CREATE_RESPONSE
Inputs:
  - model: string (required) -- e.g., "gpt-5", "gpt-4o", "o3-mini"
  - input: string | array (required)
    Simple: "Explain quantum computing"
    Multimodal: [
      { role: "user", content: [
        { type: "input_text", text: "What is in this image?" },
        { type: "input_image", image_url: { url: "https://..." } }
      ]}
    ]
  - temperature: number (0-2, optional -- not supported with reasoning models)
  - max_output_tokens: integer (optional)
  - reasoning: { effort: "none" | "minimal" | "low" | "medium" | "high" }
  - text: object (structured output config)
    - format: { type: "json_schema", name: "...", schema: {...}, strict: true }
  - tools: array (function, code_interpreter, file_search, web_search)
  - tool_choice: "auto" | "none" | "required" | { type: "function", function: { name: "..." } }
  - store: boolean (false to opt out of model distillation)
  - stream: boolean
```

**Structured output example:** Set `text.format` to `{ type: "json_schema", name: "person", schema: { type: "object", properties: { name: { type: "string" }, age: { type: "integer" } }, required: ["name", "age"], additionalProperties: false }, strict: true }`.

### 2. Create Embeddings

Use `OPENAI_CREATE_EMBEDDINGS` for vector search, clustering, recommendations, and RAG pipelines.

```
Tool: OPENAI_CREATE_EMBEDDINGS
Inputs:
  - input: string | string[] | int[] | int[][] (required) -- max 8192 tokens, max 2048 items
  - model: string (required) -- "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"
  - dimensions: integer (optional, only for text-embedding-3 and later)
  - encoding_format: "float" | "base64" (default "float")
  - user: string (optional, end-user ID for abuse monitoring)
```

### 3. Generate Images

Use `OPENAI_CREATE_IMAGE` to create images from text prompts using GPT Image or DALL-E models.

```
Tool: OPENAI_CREATE_IMAGE
Inputs:
  - model: string (required) -- "gpt-image-1", "gpt-image-1.5", "dall-e-3", "dall-e-2"
  - prompt: string (required) -- max 32000 chars (GPT Image), 4000 (DALL-E 3), 1000 (DALL-E 2)
  - size: "1024x1024" | "1536x1024" | "1024x1536" | "auto" | "256x256" | "512x512" | "1792x1024" | "1024x1792"
  - quality: "standard" | "hd" | "auto" | "high" | "medium" | "low"
  - n: integer (1-10; DALL-E 3 supports n=1 only)
  - background: "transparent" | "opaque" | "auto" (GPT Image models only)
  - style: "vivid" | "natural" (DALL-E 3 only)
  - user: string (optional)
```

### 4. List Available Models

Use `OPENAI_LIST_MODELS` to discover which models are accessible with your API key.

```
Tool: OPENAI_LIST_MODELS
Inputs: (none)
```

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| DALL-E deprecation | DALL-E 2 and DALL-E 3 are deprecated and will stop being supported on 05/12/2026. Prefer GPT Image models. |
| DALL-E 3 single image only | `OPENAI_CREATE_IMAGE` with DALL-E 3 only supports `n=1`. Use GPT Image models or DALL-E 2 for multiple images. |
| Token limits for embeddings | Input must not exceed 8192 tokens per item and 2048 items per batch for embedding models. |
| Reasoning model restrictions | `temperature` and `top_p` are not supported with reasoning models (o3-mini, etc.). Use `reasoning.effort` instead. |
| Structured output strict mode | When `strict: true` in json_schema format, ALL schema properties must be listed in the `required` array. |
| Prompt length varies by model | Image prompt max lengths differ: 32000 (GPT Image), 4000 (DALL-E 3), 1000 (DALL-E 2). |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `OPENAI_CREATE_RESPONSE` | Generate text/multimodal responses with structured output support |
| `OPENAI_CREATE_EMBEDDINGS` | Create text embeddings for search, clustering, and RAG |
| `OPENAI_CREATE_IMAGE` | Generate images from text prompts |
| `OPENAI_LIST_MODELS` | List all models available to your API key |

---

*Powered by [Composio](https://composio.dev)*
