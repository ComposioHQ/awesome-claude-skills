---
name: GroqCloud Automation
description: "Automate AI inference, chat completions, audio translation, and TTS voice management through GroqCloud's high-performance API via Composio"
requires:
  mcp:
    - rube
---

# GroqCloud Automation

Automate AI inference workflows using GroqCloud's ultra-fast API -- chat completions, model discovery, audio translation, and TTS voice selection -- all orchestrated through the Composio MCP integration.

**Toolkit docs:** [composio.dev/toolkits/groqcloud](https://composio.dev/toolkits/groqcloud)

---

## Setup

1. Connect your GroqCloud account through the Composio MCP server at `https://rube.app/mcp`
2. The agent will prompt you with an authentication link if no active connection exists
3. Once connected, all `GROQCLOUD_*` tools become available for execution

---

## Core Workflows

### 1. Discover Available Models
List all models available on GroqCloud to find valid model IDs before running inference.

**Tool:** `GROQCLOUD_LIST_MODELS`

```
No parameters required -- returns all available models with metadata.
```

Use this as a prerequisite before any chat completion call to ensure you reference a valid, non-deprecated model ID.

---

### 2. Run Chat Completions
Generate AI responses for conversational prompts using a specified GroqCloud model.

**Tool:** `GROQCLOUD_GROQ_CREATE_CHAT_COMPLETION`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model ID from `GROQCLOUD_LIST_MODELS` |
| `messages` | array | Yes | Ordered list of `{role, content}` objects (`system`, `user`, `assistant`) |
| `temperature` | number | No | Sampling temperature 0-2 (default: 1) |
| `max_completion_tokens` | integer | No | Max tokens to generate |
| `top_p` | number | No | Nucleus sampling 0-1 (default: 1) |
| `stop` | string/array | No | Up to 4 stop sequences |
| `stream` | boolean | No | Enable SSE streaming (default: false) |

---

### 3. Inspect Model Details
Retrieve detailed metadata for a specific model including context window and capabilities.

**Tool:** `GROQCLOUD_GROQ_RETRIEVE_MODEL`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model identifier (e.g., `groq-1-large`) |

---

### 4. Translate Audio to English
Translate non-English audio files into English text using Whisper models.

**Tool:** `GROQCLOUD_GROQ_CREATE_AUDIO_TRANSLATION`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Local path, HTTP(S) URL, or base64 data URL for audio |
| `model` | string | No | Model ID (default: `whisper-large-v3`). Note: `whisper-large-v3-turbo` may not support translations |
| `response_format` | string | No | `json`, `verbose_json`, or `text` (default: `json`) |
| `temperature` | number | No | Sampling temperature 0-1 (default: 0) |

---

### 5. List TTS Voices
Enumerate available text-to-speech voices for Groq PlayAI models to drive voice selection UX.

**Tool:** `GROQCLOUD_LIST_VOICES`

```
Returns the set of supported TTS voices. Note: this is a static list maintained manually.
```

---

## Known Pitfalls

| Pitfall | Details |
|---------|---------|
| **Nested model list** | `GROQCLOUD_LIST_MODELS` response may be nested at `response['data']['data']` -- do not assume a flat top-level array |
| **Hard-coded model IDs break** | Always fetch model IDs dynamically via `GROQCLOUD_LIST_MODELS`; hard-coded names can break when models are deprecated or renamed |
| **Audio format validation** | `GROQCLOUD_GROQ_CREATE_AUDIO_TRANSLATION` rejects invalid or unsupported audio formats silently -- validate inputs before calling |
| **Model metadata drifts** | Data from `GROQCLOUD_GROQ_RETRIEVE_MODEL` (context window, features) can change as models update -- do not treat it as static |
| **TTS voice changes** | Voice sets from `GROQCLOUD_LIST_VOICES` may shrink or rename over time -- handle missing voices gracefully |

---

## Quick Reference

| Tool Slug | Purpose |
|-----------|---------|
| `GROQCLOUD_LIST_MODELS` | List all available models and metadata |
| `GROQCLOUD_GROQ_CREATE_CHAT_COMPLETION` | Generate chat-based AI completions |
| `GROQCLOUD_GROQ_RETRIEVE_MODEL` | Get detailed info for a specific model |
| `GROQCLOUD_GROQ_CREATE_AUDIO_TRANSLATION` | Translate non-English audio to English text |
| `GROQCLOUD_LIST_VOICES` | Retrieve available TTS voices for PlayAI |

---

*Powered by [Composio](https://composio.dev)*
