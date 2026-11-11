#!/usr/bin/env python3
"""
MiniMax Video Generator

Generate videos with the MiniMax video generation API. Supports the
MiniMax-H3 v2 multimodal flow plus the older v1 text-to-video and
image-to-video paths, polls asynchronous tasks, lists and deletes v2 tasks,
and downloads completed videos locally.

Only the Python standard library is used, so no extra dependencies are
required.

Set your API key in the MINIMAX_API_KEY environment variable (or pass
--api-key). The key is sent as a Bearer token.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Regional API endpoints. "global" serves international traffic, "cn" serves
# mainland China.
REGIONS = {
    "global": {
        "v1": "https://api.minimax.io/v1",
        "v2": "https://api.minimax.io/v2",
    },
    "cn": {
        "v1": "https://api.minimaxi.com/v1",
        "v2": "https://api.minimaxi.com/v2",
    },
}

V1_MODELS = [
    "MiniMax-Hailuo-2.3",
    "MiniMax-Hailuo-2.3-Fast",
    "MiniMax-Hailuo-02",
    "T2V-01-Director",
    "T2V-01",
    "I2V-01-Director",
    "I2V-01-live",
    "I2V-01",
]
H3_MODEL = "MiniMax-H3"
MODELS = [H3_MODEL, *V1_MODELS]
DEFAULT_MODEL = H3_MODEL
H3_RESOLUTIONS = {"2K"}
H3_RATIOS = {"adaptive", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"}
H3_MAX_PROMPT_CHARACTERS = 7000
H3_MAX_REQUEST_BYTES = 64 * 1024 * 1024

SUCCESS_STATES = {"success", "succeeded"}
FAILURE_STATES = {"fail", "failed", "cancelled", "expired"}


def base_url(region, api_version="v1"):
    """Return the regional API base URL for a version."""
    try:
        return REGIONS[region][api_version]
    except KeyError:
        if region not in REGIONS:
            raise ValueError(
                f"Unknown region '{region}'. Choose from: {', '.join(REGIONS)}"
            )
        raise ValueError(f"Unknown API version '{api_version}'")


def get_api_key(cli_key):
    """Resolve the API key from the CLI flag or the environment."""
    key = cli_key or os.environ.get("MINIMAX_API_KEY")
    if not key:
        print("Error: no API key. Set MINIMAX_API_KEY or pass --api-key.")
        sys.exit(2)
    return key


def _request(url, api_key, method="GET", payload=None):
    """Perform an HTTP request and return the decoded JSON response."""
    data = None
    headers = {"Authorization": f"Bearer {api_key}"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {exc.code} calling {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error calling {url}: {exc.reason}") from exc

    parsed = json.loads(body)
    _check_base_resp(parsed)
    return parsed


def _check_base_resp(parsed):
    """Raise if the API signalled an error via base_resp.status_code."""
    base_resp = parsed.get("base_resp") or {}
    status_code = base_resp.get("status_code")
    if status_code not in (None, 0):
        message = base_resp.get("status_msg", "unknown error")
        raise RuntimeError(f"API error {status_code}: {message}")


def _encode_file(value):
    """Return a data URI for a local file, or pass a URL/data URI through."""
    if value.startswith(("http://", "https://", "data:")):
        return value
    if not os.path.isfile(value):
        raise ValueError(f"media file not found: {value}")
    mime, _ = mimetypes.guess_type(value)
    mime = mime or "application/octet-stream"
    with open(value, "rb") as handle:
        encoded = base64.b64encode(handle.read()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _url_item(item_type, value, role=None):
    item = {"type": item_type, item_type: {"url": _encode_file(value)}}
    if role is not None:
        item["role"] = role
    return item


def _v2_has_reference_media(args):
    return bool(args.reference_image or args.reference_video or args.reference_audio)


def _v2_has_frame_media(args):
    first_frame = getattr(args, "first_frame_image_opt", None) or getattr(
        args, "first_frame_image", None
    )
    return bool(first_frame or args.last_frame_image)


def _build_v2_content(args):
    """Build the MiniMax-H3 content array."""
    if not args.prompt:
        raise ValueError("MiniMax-H3 requires a non-empty prompt")
    if len(args.prompt) > H3_MAX_PROMPT_CHARACTERS:
        raise ValueError(
            f"MiniMax-H3 prompts cannot exceed {H3_MAX_PROMPT_CHARACTERS} characters"
        )

    first_frame = getattr(args, "first_frame_image_opt", None) or getattr(
        args, "first_frame_image", None
    )
    has_reference = _v2_has_reference_media(args)
    has_frame = _v2_has_frame_media(args)
    if has_reference and has_frame:
        raise ValueError("MiniMax-H3 does not allow frame and reference roles together")
    if args.reference_audio and not (args.reference_image or args.reference_video):
        raise ValueError("MiniMax-H3 reference audio requires a reference image or video")

    content = [{"type": "text", "text": args.prompt}]
    if first_frame:
        content.append(_url_item("image_url", first_frame, "first_frame"))
    if args.last_frame_image:
        content.append(_url_item("image_url", args.last_frame_image, "last_frame"))
    for value in args.reference_image:
        content.append(_url_item("image_url", value, "reference_image"))
    for value in args.reference_video:
        content.append(_url_item("video_url", value, "reference_video"))
    for value in args.reference_audio:
        content.append(_url_item("audio_url", value, "reference_audio"))
    return content


def _has_only_text_v2(content):
    return len(content) == 1 and content[0].get("type") == "text"


def _build_v2_payload(args):
    content = _build_v2_content(args)
    resolution = args.resolution or "2K"
    if resolution not in H3_RESOLUTIONS:
        raise ValueError("MiniMax-H3 resolution must be 2K")
    if args.ratio is not None and args.ratio not in H3_RATIOS:
        raise ValueError(
            f"MiniMax-H3 ratio must be one of: {', '.join(sorted(H3_RATIOS))}"
        )

    payload = {
        "model": H3_MODEL,
        "content": content,
        "resolution": resolution,
        "duration": args.duration,
    }
    if _has_only_text_v2(content):
        if args.ratio in (None, "adaptive"):
            raise ValueError(
                "MiniMax-H3 text-to-video requires a non-adaptive --ratio"
            )
        payload["ratio"] = args.ratio
    elif _v2_has_reference_media(args):
        payload["ratio"] = args.ratio or "adaptive"
    else:
        payload["ratio"] = "adaptive"
    if args.callback_url is not None:
        payload["callback_url"] = args.callback_url
    if args.aigc_watermark is not None:
        if args.region != "cn":
            raise ValueError("--aigc-watermark is only available in the China region")
        payload["aigc_watermark"] = args.aigc_watermark
    if len(json.dumps(payload).encode("utf-8")) > H3_MAX_REQUEST_BYTES:
        raise ValueError("MiniMax-H3 request body cannot exceed 64 MB")
    return payload


def _build_v1_payload(args):
    payload = {"model": args.model}
    if args.mode == "image-to-video":
        payload["first_frame_image"] = _encode_file(args.first_frame_image)
        if args.prompt:
            payload["prompt"] = args.prompt
    else:
        payload["prompt"] = args.prompt
    if args.prompt_optimizer is not None:
        payload["prompt_optimizer"] = args.prompt_optimizer
    if args.fast_pretreatment is not None:
        payload["fast_pretreatment"] = args.fast_pretreatment
    if args.duration is not None:
        payload["duration"] = args.duration
    if args.resolution is not None:
        payload["resolution"] = args.resolution
    if args.callback_url is not None:
        payload["callback_url"] = args.callback_url
    return payload


def create_task(args, api_key):
    """Submit a video task and return its task_id plus API version."""
    if args.model == H3_MODEL:
        if args.duration is None:
            raise ValueError("MiniMax-H3 requires --duration")
        if not 4 <= args.duration <= 15:
            raise ValueError("MiniMax-H3 duration must be between 4 and 15 seconds")
        url = f"{base_url(args.region, 'v2')}/video_generation"
        payload = _build_v2_payload(args)
        response = _request(url, api_key, method="POST", payload=payload)
        task_id = response.get("task_id")
        if not task_id:
            raise RuntimeError(f"No task_id in response: {response}")
        return {"api_version": "v2", "task_id": task_id}

    if args.aigc_watermark is not None:
        raise ValueError("--aigc-watermark requires the MiniMax-H3 model")
    url = f"{base_url(args.region)}/video_generation"
    payload = _build_v1_payload(args)
    response = _request(url, api_key, method="POST", payload=payload)
    task_id = response.get("task_id")
    if not task_id:
        raise RuntimeError(f"No task_id in response: {response}")
    return {"api_version": "v1", "task_id": task_id}


def query_task(task_id, region, api_key, api_version="auto"):
    """Query a generation task and return the task metadata."""
    if api_version in ("auto", "v2"):
        try:
            url = f"{base_url(region, 'v2')}/query/video_generation/{task_id}"
            response = _request(url, api_key, method="GET")
            task = response.get("task") or {}
            return {
                "api_version": "v2",
                "status": task.get("status", ""),
                "download_url": (task.get("content") or {}).get("url", ""),
                "raw": task,
            }
        except RuntimeError:
            if api_version == "v2":
                raise

    url = f"{base_url(region)}/query/video_generation?{urllib.parse.urlencode({'task_id': task_id})}"
    response = _request(url, api_key, method="GET")
    return {
        "api_version": "v1",
        "status": response.get("status", ""),
        "file_id": response.get("file_id", ""),
        "raw": response,
    }


def list_tasks(args, api_key):
    """List v2 video generation tasks."""
    params = {}
    if args.page_num is not None:
        params["page_num"] = args.page_num
    if args.page_size is not None:
        params["page_size"] = args.page_size
    if args.filter_status:
        params["filter.status"] = args.filter_status
    if args.filter_task_ids:
        params["filter.task_ids"] = args.filter_task_ids
    if args.filter_model:
        params["filter.model"] = args.filter_model
    if args.filter_task_type:
        params["filter.task_type"] = args.filter_task_type
    query = urllib.parse.urlencode(params, doseq=True)
    url = f"{base_url(args.region, 'v2')}/query/video_generation"
    if query:
        url = f"{url}?{query}"
    return _request(url, api_key, method="GET")


def delete_task(task_id, region, api_key):
    """Cancel or delete a v2 video generation task."""
    url = f"{base_url(region, 'v2')}/video_generation/{task_id}"
    return _request(url, api_key, method="DELETE")


def retrieve_file(file_id, region, api_key):
    """Retrieve a generated file and return its download URL for v1 tasks."""
    query = urllib.parse.urlencode({"file_id": file_id})
    url = f"{base_url(region)}/files/retrieve?{query}"
    response = _request(url, api_key, method="GET")
    file_info = response.get("file") or {}
    download_url = file_info.get("download_url")
    if not download_url:
        raise RuntimeError(f"No download_url in response: {response}")
    return download_url


def download(download_url, output_path):
    """Download the generated video to output_path."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with urllib.request.urlopen(download_url) as resp, open(output_path, "wb") as out:
        out.write(resp.read())
    print(f"Saved video to {output_path}")


def wait_for_completion(task_id, region, api_key, poll_interval, timeout, api_version):
    """Poll a generation task until it succeeds, fails, or times out."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        task = query_task(task_id, region, api_key, api_version=api_version)
        status = (task.get("status") or "").lower()
        print(f"Status: {status or 'unknown'}")
        if status in SUCCESS_STATES:
            if task["api_version"] == "v2":
                if task.get("download_url"):
                    return task
            elif task.get("file_id"):
                return task
        if status in FAILURE_STATES:
            raise RuntimeError(f"Generation failed for task {task_id}")
        time.sleep(poll_interval)
    raise TimeoutError(f"Task {task_id} did not finish within {timeout} seconds")


def run_generation(args):
    """Run the full pipeline: create, poll, retrieve, and download."""
    api_key = get_api_key(args.api_key)
    created = create_task(args, api_key)
    task_id = created["task_id"]

    if args.no_wait:
        print(f"Task {task_id} submitted. Query it later with the 'query' command.")
        return True

    task = wait_for_completion(
        task_id, args.region, api_key, args.poll_interval, args.timeout, created["api_version"]
    )
    if task["api_version"] == "v2":
        download_url = task.get("download_url")
    else:
        download_url = retrieve_file(task.get("file_id", ""), args.region, api_key)

    if not download_url:
        raise RuntimeError(f"No download URL available for task {task_id}")

    output_path = args.output
    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, f"{task_id}.mp4")
    download(download_url, output_path)
    return True


def run_query(args):
    """Query the status of an existing task."""
    api_key = get_api_key(args.api_key)
    task = query_task(args.task_id, args.region, api_key, api_version=args.api_version)
    result = {"task_id": args.task_id, "status": task.get("status", ""), "api_version": task["api_version"]}
    if task["api_version"] == "v2":
        result["download_url"] = task.get("download_url", "")
    else:
        result["file_id"] = task.get("file_id", "")
    print(json.dumps(result))
    return True


def run_list(args):
    """List recent v2 tasks."""
    api_key = get_api_key(args.api_key)
    print(json.dumps(list_tasks(args, api_key)))
    return True


def run_delete(args):
    """Cancel or delete a v2 task."""
    api_key = get_api_key(args.api_key)
    print(json.dumps(delete_task(args.task_id, args.region, api_key)))
    return True


def run_retrieve(args):
    """Retrieve and download a finished file by file_id."""
    api_key = get_api_key(args.api_key)
    download_url = retrieve_file(args.file_id, args.region, api_key)
    output_path = args.output
    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, f"{args.file_id}.mp4")
    download(download_url, output_path)
    return True


def add_common_options(parser):
    parser.add_argument(
        "--region",
        default="global",
        choices=sorted(REGIONS),
        help="API region (default: global)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (defaults to the MINIMAX_API_KEY environment variable)",
    )


def add_generation_options(parser):
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        choices=MODELS,
        help=f"Video model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument("--duration", type=int, help="Clip duration in seconds")
    parser.add_argument("--resolution", help="Output resolution, e.g. 2K or 768P")
    parser.add_argument("--ratio", help="Aspect ratio for MiniMax-H3")
    parser.add_argument(
        "--prompt-optimizer",
        dest="prompt_optimizer",
        action="store_true",
        default=None,
        help="Let the API refine the prompt before generating",
    )
    parser.add_argument(
        "--fast-pretreatment",
        dest="fast_pretreatment",
        action="store_true",
        default=None,
        help="Enable faster input pre-processing",
    )
    parser.add_argument(
        "--callback-url",
        dest="callback_url",
        default=None,
        help="URL to receive asynchronous status callbacks",
    )
    parser.add_argument(
        "--aigc-watermark",
        action="store_true",
        default=None,
        help="Add the China-region AIGC watermark for MiniMax-H3",
    )
    parser.add_argument(
        "--first-frame-image",
        dest="first_frame_image_opt",
        default=None,
        help="First frame image for MiniMax-H3",
    )
    parser.add_argument(
        "--last-frame-image",
        dest="last_frame_image",
        default=None,
        help="Last frame image for MiniMax-H3",
    )
    parser.add_argument(
        "--reference-image",
        action="append",
        default=[],
        help="Reference image for MiniMax-H3 (repeatable)",
    )
    parser.add_argument(
        "--reference-video",
        action="append",
        default=[],
        help="Reference video for MiniMax-H3 (repeatable)",
    )
    parser.add_argument(
        "--reference-audio",
        action="append",
        default=[],
        help="Reference audio for MiniMax-H3 (repeatable)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="/mnt/user-data/outputs",
        help="Output file or directory (default: /mnt/user-data/outputs)",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        help="Seconds between status checks (default: 10)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Maximum seconds to wait for completion (default: 600)",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Submit the task and exit without polling or downloading",
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate videos with the MiniMax video generation API"
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    t2v = sub.add_parser("text-to-video", help="Generate a video from a text prompt")
    t2v.add_argument("prompt", help="Text description of the video")
    add_generation_options(t2v)
    add_common_options(t2v)
    t2v.set_defaults(func=run_generation)

    i2v = sub.add_parser(
        "image-to-video", help="Generate a video from a first-frame image"
    )
    i2v.add_argument(
        "first_frame_image",
        help="First frame: local image path, URL, or data URI",
    )
    i2v.add_argument("--prompt", default="", help="Optional text guidance")
    add_generation_options(i2v)
    add_common_options(i2v)
    i2v.set_defaults(func=run_generation)

    query = sub.add_parser("query", help="Check the status of a task")
    query.add_argument("task_id", help="Task id returned when the task was created")
    query.add_argument(
        "--api-version",
        choices=["auto", "v1", "v2"],
        default="auto",
        help="API version to query (default: auto)",
    )
    add_common_options(query)
    query.set_defaults(func=run_query)

    list_cmd = sub.add_parser("list", help="List v2 video generation tasks")
    list_cmd.add_argument("--page-num", type=int, default=1, dest="page_num")
    list_cmd.add_argument("--page-size", type=int, default=20, dest="page_size")
    list_cmd.add_argument("--filter-status", dest="filter_status")
    list_cmd.add_argument(
        "--filter-task-id",
        action="append",
        dest="filter_task_ids",
        default=[],
        help="Task ID filter (repeatable)",
    )
    list_cmd.add_argument("--filter-model", dest="filter_model")
    list_cmd.add_argument("--filter-task-type", dest="filter_task_type")
    add_common_options(list_cmd)
    list_cmd.set_defaults(func=run_list)

    delete = sub.add_parser("delete", help="Cancel or delete a v2 task")
    delete.add_argument("task_id", help="Task id to cancel or delete")
    add_common_options(delete)
    delete.set_defaults(func=run_delete)

    retrieve = sub.add_parser("retrieve", help="Download a finished file by file id")
    retrieve.add_argument("file_id", help="File id reported by a successful task")
    retrieve.add_argument(
        "-o",
        "--output",
        default="/mnt/user-data/outputs",
        help="Output file or directory (default: /mnt/user-data/outputs)",
    )
    add_common_options(retrieve)
    retrieve.set_defaults(func=run_retrieve)

    return parser


def main():
    args = build_parser().parse_args()
    try:
        ok = args.func(args)
    except (RuntimeError, ValueError, TimeoutError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
