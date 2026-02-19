---
name: ElevenLabs Automation
description: "Automate ElevenLabs text-to-speech workflows -- generate speech from text, browse and inspect voices, check subscription limits, list models, stream audio, and retrieve history via the Composio MCP integration."
requires:
  mcp:
    - rube
---

# ElevenLabs Automation

Automate your ElevenLabs text-to-speech workflows -- convert text to natural speech, browse the voice library, inspect voice details, check subscription credits, select TTS models, stream audio for low-latency delivery, and retrieve previously generated audio from history.

**Toolkit docs:** [composio.dev/toolkits/elevenlabs](https://composio.dev/toolkits/elevenlabs)

---

## Setup

1. Add the Composio MCP server to your client: `https://rube.app/mcp`
2. Connect your ElevenLabs account when prompted (API key authentication)
3. Start using the workflows below

---

## Core Workflows

### 1. Generate Speech from Text

Use `ELEVENLABS_TEXT_TO_SPEECH` to convert text into a downloadable audio file.

```
Tool: ELEVENLABS_TEXT_TO_SPEECH
Inputs:
  - voice_id: string (required) -- obtain from ELEVENLABS_GET_VOICES
  - text: string (required) -- max ~10,000 chars (most models), 30,000 (Flash/Turbo v2), 40,000 (v2.5)
  - model_id: string (default "eleven_monolingual_v1") -- e.g., "eleven_multilingual_v2"
  - output_format: string (default "mp3_44100_128") -- see formats below
  - optimize_streaming_latency: integer (0-4; NOT supported with eleven_v3)
  - seed: integer (optional, for reproducibility -- not guaranteed)
  - pronunciation_dictionary_locators: array (optional, up to 3 dictionaries)
```

**Output formats:**
- MP3: `mp3_22050_32`, `mp3_44100_32`, `mp3_44100_64`, `mp3_44100_96`, `mp3_44100_128`, `mp3_44100_192` (Creator+)
- PCM: `pcm_16000`, `pcm_22050`, `pcm_24000`, `pcm_44100` (Pro+)
- uLaw: `ulaw_8000` (for Twilio)

**Important:** Output is a file object with a presigned download link at `data.file.s3url` (expires in ~1 hour). Download promptly.

### 2. Browse Available Voices

Use `ELEVENLABS_GET_VOICES` to list all voices with their attributes and settings.

```
Tool: ELEVENLABS_GET_VOICES
Inputs: (none)
```

Returns an array at `data.voices[]` with `voice_id`, `name`, `labels` (gender, accent, use_case), and settings.

### 3. Inspect a Specific Voice

Use `ELEVENLABS_GET_VOICE` to get detailed metadata for a candidate voice before synthesis.

```
Tool: ELEVENLABS_GET_VOICE
Inputs:
  - voice_id: string (required) -- e.g., "21m00Tcm4TlvDq8ikWAM"
  - with_settings: boolean (default false) -- include detailed voice settings
```

### 4. Check Subscription and Credits

Use `ELEVENLABS_GET_USER_SUBSCRIPTION_INFO` to verify plan limits and remaining credits before bulk generation.

```
Tool: ELEVENLABS_GET_USER_SUBSCRIPTION_INFO
Inputs: (none)
```

### 5. List Available TTS Models

Use `ELEVENLABS_GET_MODELS` to discover compatible models and filter by `can_do_text_to_speech: true`.

```
Tool: ELEVENLABS_GET_MODELS
Inputs: (none)
```

### 6. Stream Audio and Retrieve History

Use `ELEVENLABS_TEXT_TO_SPEECH_STREAM` for low-latency streamed delivery, and `ELEVENLABS_GET_AUDIO_FROM_HISTORY_ITEM` to re-download previously generated audio.

```
Tool: ELEVENLABS_TEXT_TO_SPEECH_STREAM
  - Same core inputs as TEXT_TO_SPEECH but returns a stream for low-latency playback

Tool: ELEVENLABS_GET_AUDIO_FROM_HISTORY_ITEM
  - history_item_id: string (required) -- ID from a previous generation
```

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| Text length limits | Most models cap at ~10,000-20,000 chars per request. Oversized input returns HTTP 400. Split long text into chunks (~5000 chars) and generate per chunk. |
| Output is a presigned URL | `ELEVENLABS_TEXT_TO_SPEECH` returns `data.file.s3url` with a ~1 hour expiry (X-Amz-Expires=3600). Download the audio file promptly. |
| Quota and credit errors | HTTP 401 with `quota_exceeded` or HTTP 402 `payment_required` means insufficient credits or tier restrictions. Check with `ELEVENLABS_GET_USER_SUBSCRIPTION_INFO` before bulk jobs. |
| Voice permissions | HTTP 401 with `missing_permissions` means the API key lacks `voices_read` scope. Verify key permissions. |
| Model compatibility | Not all models support TTS. Use `ELEVENLABS_GET_MODELS` and filter by `can_do_text_to_speech: true`. The `optimize_streaming_latency` parameter is NOT supported with `eleven_v3`. |
| Large voice list truncation | `ELEVENLABS_GET_VOICES` may return a large list. Select from the full `data.voices[]` payload -- previews may appear truncated. |

---

## Quick Reference

| Tool Slug | Description |
|-----------|-------------|
| `ELEVENLABS_TEXT_TO_SPEECH` | Convert text to speech, returns downloadable audio file |
| `ELEVENLABS_GET_VOICES` | List all available voices with attributes |
| `ELEVENLABS_GET_VOICE` | Get detailed info for a specific voice |
| `ELEVENLABS_GET_USER_SUBSCRIPTION_INFO` | Check subscription plan and remaining credits |
| `ELEVENLABS_GET_MODELS` | List available TTS models and capabilities |
| `ELEVENLABS_TEXT_TO_SPEECH_STREAM` | Stream audio for low-latency delivery |
| `ELEVENLABS_GET_AUDIO_FROM_HISTORY_ITEM` | Re-download audio from generation history |

---

*Powered by [Composio](https://composio.dev)*
