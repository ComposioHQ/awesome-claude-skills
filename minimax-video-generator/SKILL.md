---
name: minimax-video-generator
description: Generate videos with the MiniMax video generation API. Use this skill when the user asks to create, generate, or render a video from text, images, video, or audio references. Supports MiniMax-H3 and the MiniMax-Hailuo-2.3 model family, global and China regions, asynchronous status polling, file retrieval, and local download.
---

# MiniMax Video Generator

Create short videos with the MiniMax video generation API. The skill submits
an asynchronous generation task, polls it until it finishes, retrieves the
resulting file, and downloads the video locally. It covers text-to-video,
image-to-video, and multimodal reference generation, works against the global
and China regions, and defaults to the MiniMax-H3 model.

## When to Use This Skill

- The user wants to generate a video clip from a written description.
- The user has a starting image and wants to animate it into a video.
- The user needs to check the status of a running generation task or download
  a finished result by its file id.

## What This Skill Does

1. **Text-to-video**: Turns a text prompt into a video with a chosen model.
2. **Image-to-video**: Animates a first-frame image (local file, URL, or data
   URI), optionally guided by a text prompt.
3. **Asynchronous handling**: Submits the task, polls the status endpoint until
   it reports `Success` or `Fail`, then retrieves and downloads the file.

## Setup

Set your API key before running the script. The key is sent as a Bearer token.

```bash
export MINIMAX_API_KEY="your-api-key"
```

Only the Python standard library is required.

## How to Use

### Text-to-Video

```bash
python scripts/generate_video.py text-to-video \
  "A red fox running through a snowy forest at dawn" \
  --duration 6 --ratio 16:9
```

### Image-to-Video

```bash
python scripts/generate_video.py image-to-video ./first_frame.jpg \
  --prompt "The camera slowly zooms in" --duration 6
```

MiniMax-H3 requires a prompt and a duration from 4 through 15 seconds. The
first frame can be a local image path, an `http(s)` URL, or a `data:` URI.

## Options

### Model

Use `--model` to choose a video model (default: `MiniMax-H3`):

- `MiniMax-H3`
- `MiniMax-Hailuo-2.3`
- `MiniMax-Hailuo-2.3-Fast`
- `MiniMax-Hailuo-02`
- `T2V-01-Director`
- `T2V-01`
- `I2V-01-Director`
- `I2V-01-live`
- `I2V-01`

```bash
python scripts/generate_video.py text-to-video "A city skyline at night" \
  --model MiniMax-Hailuo-2.3-Fast
```

### Region

Use `--region` to target the global (default) or China endpoint:

- `global`: `https://api.minimax.io/v1` and `https://api.minimax.io/v2`
- `cn`: `https://api.minimaxi.com/v1` and `https://api.minimaxi.com/v2`

```bash
python scripts/generate_video.py text-to-video "Waves on a beach" \
  --duration 6 --ratio 16:9 --region cn
```

### Generation Parameters

- `--duration`: Clip duration in seconds.
- `--resolution`: Output resolution. MiniMax-H3 uses `2K`.
- `--ratio`: MiniMax-H3 aspect ratio. Text-to-video requires a specific ratio.
- `--prompt-optimizer`: Let the API refine the prompt before generating.
- `--fast-pretreatment`: Enable faster input pre-processing.
- `--callback-url`: URL to receive asynchronous status callbacks.
- `--first-frame-image`, `--last-frame-image`: MiniMax-H3 frame inputs.
- `--reference-image`, `--reference-video`, `--reference-audio`: Repeatable
  MiniMax-H3 reference inputs.
- `--aigc-watermark`: Add the China-region AIGC watermark for MiniMax-H3.
- `-o`, `--output`: Output file or directory (default: `/mnt/user-data/outputs`).
- `--poll-interval`: Seconds between status checks (default: 10).
- `--timeout`: Maximum seconds to wait for completion (default: 600).
- `--no-wait`: Submit the task and exit without polling or downloading.

### MiniMax-H3 Pricing

MiniMax-H3 pricing depends on the selected region:

| Usage | Global | China |
| --- | --- | --- |
| 2K output video | $0.13 per second | ¥0.80 per second |
| 2K reference video input | $0.02 per second | ¥0.80 per second |
| Reference audio input | Free | Free |
| Reference image input | First 5 images free, then $0.03 per image | First 5 images free, then ¥0.20 per image |

### Checking Status and Downloading Later

Submit without waiting, then query and retrieve when ready:

```bash
python scripts/generate_video.py text-to-video "A hot air balloon over mountains" \
  --duration 6 --ratio 16:9 --no-wait
python scripts/generate_video.py query TASK_ID
python scripts/generate_video.py retrieve FILE_ID -o /mnt/user-data/outputs
```

The `retrieve` command is for v1 tasks. Successful MiniMax-H3 queries return a
download URL directly.

## Example

**User**: "Generate a 6-second video of a paper boat floating down a rainy street."

**Output**:
```
Submitting text-to-video task with model MiniMax-H3 (global)...
Task created: 1234567890
Status: Preparing
Status: Processing
Status: Success
Saved video to /mnt/user-data/outputs/1234567890.mp4
```

## How It Works

MiniMax-H3 uses the v2 endpoints under the selected region host:

- `POST /v2/video_generation` creates a task.
- `GET /v2/query/video_generation/{task_id}` reports status and the result URL.
- `GET /v2/query/video_generation` lists recent tasks.
- `DELETE /v2/video_generation/{task_id}` cancels or deletes a task.

The earlier models use three v1 endpoints:

- `POST /v1/video_generation` creates a text-to-video or image-to-video task
  and returns a `task_id`.
- `GET /v1/query/video_generation?task_id=...` reports the task `status` and,
  once finished, the `file_id`.
- `GET /v1/files/retrieve?file_id=...` returns the file `download_url`.

The script polls the query endpoint until the status is `Success`, then
downloads the file. API errors are surfaced through the `base_resp.status_code`
field in each response.

## Important Notes

- Downloads are saved to `/mnt/user-data/outputs/` by default; when the output
  is a directory the file is named after the task or file id.
- The API key is read from the `MINIMAX_API_KEY` environment variable and never
  written to disk.
- Generation is asynchronous; longer clips and higher resolutions take longer
  to finish.

## Common Use Cases

- Producing short marketing or social clips from a text brief.
- Animating a product still or concept image into motion.
- Batching generation tasks with `--no-wait` and retrieving results later.
