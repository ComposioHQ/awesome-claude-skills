---
name: typecast-tts
description: Automate Typecast text-to-speech workflows — generate speech from text, browse and filter voices, inspect voice details, and tune output with emotion, pitch, tempo, and volume controls via the Typecast REST API.
---

# Typecast TTS

Automate your Typecast text-to-speech workflows — convert text to natural speech, browse the voice library, inspect voice details, and fine-tune output with emotion presets, pitch, tempo, and volume controls.

**API docs:** [typecast.ai](https://typecast.ai)

---

## Setup

1. Get your API key from the Typecast dashboard
2. Set your API key as an environment variable:
   ```bash
   export TYPECAST_API_KEY=your_api_key_here
   ```
3. Use `X-API-Key: $TYPECAST_API_KEY` in all requests below

**Base URL:** `https://api.typecast.ai`

---

## Core Workflows

### 1. List Available Voices

Use `GET /v2/voices` to browse all voices and find the right one for your use case.

```bash
curl -s -H "X-API-Key: $TYPECAST_API_KEY" \
  https://api.typecast.ai/v2/voices
```

**Response structure** (array of voice objects):
```json
[
  {
    "voice_id": "tc_...",
    "voice_name": "Wonwoo",
    "models": [
      {
        "version": "ssfm-v30",
        "emotions": ["normal", "happy", "sad", "angry", "whisper", "toneup", "tonedown"]
      }
    ],
    "gender": "male",
    "age": "young_adult",
    "use_cases": ["Conversational", "Radio/Podcast"]
  }
]
```

**Filter by use case or gender:** The API returns all voices; filter the response locally.

```bash
# Find all female voices for e-learning
curl -s -H "X-API-Key: $TYPECAST_API_KEY" \
  https://api.typecast.ai/v2/voices | \
  python3 -c "
import json, sys
voices = json.load(sys.stdin)
matches = [v for v in voices if v['gender'] == 'female' and 'E-learning/Explainer' in v.get('use_cases', [])]
for v in matches:
    print(v['voice_id'], v['voice_name'])
"
```

### 2. Inspect a Specific Voice

Use `GET /v2/voices/{voice_id}` to confirm supported models and emotions before generating.

```bash
curl -s -H "X-API-Key: $TYPECAST_API_KEY" \
  https://api.typecast.ai/v2/voices/tc_YOUR_VOICE_ID
```

Returns the same structure as a single list item. Check `models[].emotions` to see which emotion presets are available for that voice.

### 3. Generate Speech from Text

Use `POST /v1/text-to-speech` to convert text to an audio file.

```bash
curl -s -X POST \
  -H "X-API-Key: $TYPECAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test.",
    "voice_id": "tc_YOUR_VOICE_ID",
    "model": "ssfm-v30",
    "format": "mp3"
  }' \
  https://api.typecast.ai/v1/text-to-speech \
  -o output.mp3
```

The response is raw audio binary — save it directly with `-o`. No presigned URL, no JSON wrapper.

**With emotion and prosody controls:**
```bash
curl -s -X POST \
  -H "X-API-Key: $TYPECAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Great news! Your order has shipped.",
    "voice_id": "tc_YOUR_VOICE_ID",
    "model": "ssfm-v30",
    "format": "mp3",
    "emotion_preset": "happy",
    "pitch": 2,
    "tempo": 1.1,
    "volume": 120,
    "seed": 42
  }' \
  https://api.typecast.ai/v1/text-to-speech \
  -o output_happy.mp3
```

**With sentence context** (improves prosody at boundaries):
```bash
curl -s -X POST \
  -H "X-API-Key: $TYPECAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The results were surprising.",
    "voice_id": "tc_YOUR_VOICE_ID",
    "model": "ssfm-v30",
    "format": "mp3",
    "prev_text": "We ran the experiment three times.",
    "next_text": "None of us expected this outcome."
  }' \
  https://api.typecast.ai/v1/text-to-speech \
  -o output.mp3
```

---

## Parameters Reference

| Parameter | Type | Range / Values | Default | Notes |
|-----------|------|----------------|---------|-------|
| `text` | string | — | required | Text to synthesize |
| `voice_id` | string | `tc_...` | required | From `GET /v2/voices` |
| `model` | string | `ssfm-v30`, `ssfm-v21` | `ssfm-v30` | v30 supports more emotions |
| `format` | string | `mp3`, `wav` | — | Determines output audio format |
| `emotion_preset` | string | `normal`, `happy`, `sad`, `angry`, `whisper`, `toneup`, `tonedown` | — | Must be supported by the voice's model |
| `pitch` | int | -12 to +12 semitones | 0 | Positive = higher pitch |
| `tempo` | float | 0.5 – 2.0 | 1.0 | 1.0 = normal speed |
| `volume` | int | 0 – 200 | 100 | 100 = original volume |
| `seed` | int | any integer | -1 (random) | Set for reproducible output |
| `language` | string | ISO 639-3 (e.g. `kor`, `eng`) | auto-detected | Force a specific language |
| `prev_text` | string | — | — | Sentence before — improves prosody |
| `next_text` | string | — | — | Sentence after — improves prosody |

---

## Known Pitfalls

| Pitfall | Detail |
|---------|--------|
| Response is raw audio | `POST /v1/text-to-speech` returns binary audio directly, not JSON with a URL. Always pipe to a file with `-o output.mp3`. |
| emotion_preset varies by voice | Not all voices support all emotion presets. `ssfm-v21` voices only support `normal`, `happy`, `sad`, `angry`. Check `GET /v2/voices/{id}` first. |
| ssfm-v21 vs ssfm-v30 | v30 adds `whisper`, `toneup`, `tonedown`. Not all voices have both model versions — check the voice's `models` array. |
| Long text | No documented character limit per request. For safety, split text at ~1000 characters per request and concatenate the resulting audio files. |
| format field | Specifying `"format": "wav"` returns WAV audio. The `Content-Disposition` header includes the filename, but you must set the output filename explicitly with `-o`. |

---

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v2/voices` | GET | List all available voices |
| `/v2/voices/{voice_id}` | GET | Get details for a specific voice |
| `/v1/text-to-speech` | POST | Generate speech, returns audio binary |
