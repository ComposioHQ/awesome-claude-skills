#!/usr/bin/env python3
"""Download Apple Human Interface Guidelines sources and build a consolidated raw file."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

INDEX_URL = "https://developer.apple.com/tutorials/data/index/design--human-interface-guidelines"
DATA_BASE = "https://developer.apple.com/tutorials/data"
PAGE_PREFIX = "/design/human-interface-guidelines"
NON_IOS_SLUGS = {
    "designing-for-ipados",
    "designing-for-macos",
    "designing-for-tvos",
    "designing-for-visionos",
    "designing-for-watchos",
    "designing-for-games",
}
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


@dataclass
class Node:
    path: str
    title: str
    kind: str
    parent_path: str | None


def http_get_json(url: str, timeout_s: int = 45) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def normalize_space(value: str) -> str:
    return " ".join(value.split())


def extract_abstract(page_json: dict[str, Any]) -> str:
    abstract = page_json.get("abstract")
    if isinstance(abstract, str):
        return normalize_space(abstract)
    if isinstance(abstract, list):
        parts: list[str] = []
        for item in abstract:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        if parts:
            return normalize_space(" ".join(parts))
    return ""


def collect_text_fragments(value: Any, out: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "text" and isinstance(child, str):
                text = normalize_space(child)
                if text:
                    out.append(text)
            else:
                collect_text_fragments(child, out)
        return

    if isinstance(value, list):
        for child in value:
            collect_text_fragments(child, out)


def extract_full_text(page_json: dict[str, Any]) -> str:
    fragments: list[str] = []
    collect_text_fragments(page_json, fragments)

    compact: list[str] = []
    last = None
    for fragment in fragments:
        if fragment != last:
            compact.append(fragment)
            last = fragment

    return "\n\n".join(compact)


def walk_nodes(node: dict[str, Any], parent_path: str | None, out: list[Node]) -> None:
    path = node.get("path")
    title = node.get("title")
    kind = node.get("type")

    current_parent = parent_path
    if isinstance(path, str) and path.startswith(PAGE_PREFIX):
        out.append(
            Node(
                path=path,
                title=title if isinstance(title, str) else path.rsplit("/", 1)[-1],
                kind=kind if isinstance(kind, str) else "unknown",
                parent_path=parent_path,
            )
        )
        current_parent = path

    children = node.get("children")
    if isinstance(children, list):
        for child in children:
            if isinstance(child, dict):
                walk_nodes(child, current_parent, out)


def collect_hig_nodes(index_json: dict[str, Any]) -> list[Node]:
    swift_tree = index_json.get("interfaceLanguages", {}).get("swift", [])
    nodes: list[Node] = []
    for root in swift_tree:
        if isinstance(root, dict):
            walk_nodes(root, parent_path=None, out=nodes)

    dedup: dict[str, Node] = {}
    for node in nodes:
        dedup[node.path] = node

    return sorted(dedup.values(), key=lambda n: n.path)


def path_to_local_json(raw_pages_dir: Path, path: str) -> Path:
    normalized = path.lstrip("/") + ".json"
    return raw_pages_dir / normalized


def build_raw_markdown(
    output_file: Path,
    catalog_rows: list[dict[str, Any]],
    generated_at: str,
) -> None:
    lines: list[str] = []
    lines.append("# Apple HIG Raw Index (iOS-focused usage)")
    lines.append("")
    lines.append("This file is auto-generated from Apple source endpoints.")
    lines.append(f"Generated at: {generated_at}")
    lines.append("")
    lines.append("## Source endpoints")
    lines.append("")
    lines.append(f"- Index JSON: `{INDEX_URL}`")
    lines.append("- Page JSON pattern: `https://developer.apple.com/tutorials/data{path}.json`")
    lines.append("")
    lines.append("## Pages")
    lines.append("")

    for row in catalog_rows:
        lines.append(f"### {row['title']}")
        lines.append("")
        lines.append(f"- Path: `{row['path']}`")
        lines.append(f"- Kind: `{row['kind']}`")
        if row.get("parent_path"):
            lines.append(f"- Parent: `{row['parent_path']}`")
        lines.append(f"- Source URL: {row['source_url']}")
        lines.append(f"- Data URL: {row['data_url']}")
        lines.append(f"- Local JSON: `{row['local_json']}`")
        abstract = row.get("abstract", "")
        if abstract:
            lines.append(f"- Abstract: {abstract}")
        else:
            lines.append("- Abstract: (empty)")
        status = row.get("download_status", "unknown")
        lines.append(f"- Download: `{status}`")
        lines.append("")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_fulltext_markdown(
    output_file: Path,
    catalog_rows: list[dict[str, Any]],
    references_dir: Path,
    generated_at: str,
) -> None:
    lines: list[str] = []
    lines.append("# Apple HIG Full Text Dump (iOS-focused usage)")
    lines.append("")
    lines.append("This file is auto-generated from Apple source endpoints.")
    lines.append("The content below is extracted from all `text` fields in each page JSON.")
    lines.append(f"Generated at: {generated_at}")
    lines.append("")

    for row in catalog_rows:
        if row.get("download_status") != "ok":
            continue

        local_rel = row.get("local_json")
        if not isinstance(local_rel, str):
            continue

        local_path = references_dir / local_rel
        try:
            page_json = json.loads(local_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        full_text = extract_full_text(page_json)

        lines.append(f"## {row['title']}")
        lines.append("")
        lines.append(f"- Path: `{row['path']}`")
        lines.append(f"- Source URL: {row['source_url']}")
        lines.append(f"- Data URL: {row['data_url']}")
        lines.append("")

        if full_text:
            lines.append(full_text)
        else:
            lines.append("(no extracted text)")
        lines.append("")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def is_curated_ios_row(row: dict[str, Any]) -> bool:
    if row.get("download_status") != "ok":
        return False
    if row.get("kind") != "article":
        return False

    path = row.get("path")
    if not isinstance(path, str):
        return False

    slug = path.rsplit("/", 1)[-1]
    if slug in NON_IOS_SLUGS:
        return False

    return True


def build_curated_markdown(
    output_file: Path,
    catalog_rows: list[dict[str, Any]],
    references_dir: Path,
    generated_at: str,
) -> None:
    curated_rows = [row for row in catalog_rows if is_curated_ios_row(row)]

    lines: list[str] = []
    lines.append("# Apple HIG iOS Curated Text")
    lines.append("")
    lines.append("This file is auto-generated for practical iOS design-spec writing.")
    lines.append("It excludes index/module/symbol nodes and non-iOS platform overview pages.")
    lines.append(f"Generated at: {generated_at}")
    lines.append(f"Included pages: {len(curated_rows)}")
    lines.append("")

    for row in curated_rows:
        local_rel = row.get("local_json")
        if not isinstance(local_rel, str):
            continue

        local_path = references_dir / local_rel
        try:
            page_json = json.loads(local_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        full_text = extract_full_text(page_json)

        lines.append(f"## {row['title']}")
        lines.append("")
        lines.append(f"- Path: `{row['path']}`")
        lines.append(f"- Source URL: {row['source_url']}")
        lines.append("")
        if full_text:
            lines.append(full_text)
        else:
            lines.append("(no extracted text)")
        lines.append("")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def sync_sources(skill_dir: Path, sleep_ms: int = 120) -> dict[str, Any]:
    references_dir = skill_dir / "references"
    raw_dir = references_dir / "raw"
    raw_index_dir = raw_dir / "index"
    raw_pages_dir = raw_dir / "pages"

    generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    index_json = http_get_json(INDEX_URL)
    write_json(raw_index_dir / "design--human-interface-guidelines.json", index_json)

    nodes = collect_hig_nodes(index_json)
    rows: list[dict[str, Any]] = []
    ok_count = 0

    for i, node in enumerate(nodes, start=1):
        data_url = f"{DATA_BASE}{node.path}.json"
        source_url = f"https://developer.apple.com{node.path}"
        local_path = path_to_local_json(raw_pages_dir, node.path)

        row = {
            "path": node.path,
            "title": node.title,
            "kind": node.kind,
            "parent_path": node.parent_path,
            "source_url": source_url,
            "data_url": data_url,
            "local_json": os.path.relpath(local_path, references_dir),
            "download_status": "pending",
            "abstract": "",
            "error": "",
        }

        try:
            page_json = http_get_json(data_url)
            write_json(local_path, page_json)
            row["abstract"] = extract_abstract(page_json)
            row["download_status"] = "ok"
            ok_count += 1
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            row["download_status"] = "error"
            row["error"] = normalize_space(str(exc))

        rows.append(row)

        if sleep_ms > 0 and i < len(nodes):
            time.sleep(sleep_ms / 1000)

    catalog = {
        "generated_at": generated_at,
        "index_url": INDEX_URL,
        "page_base": DATA_BASE,
        "page_prefix": PAGE_PREFIX,
        "total_nodes": len(nodes),
        "download_ok": ok_count,
        "download_error": len(nodes) - ok_count,
        "rows": rows,
    }
    write_json(raw_dir / "catalog.json", catalog)

    build_raw_markdown(
        output_file=references_dir / "apple-hig-ios-raw.md",
        catalog_rows=rows,
        generated_at=generated_at,
    )
    build_fulltext_markdown(
        output_file=references_dir / "apple-hig-ios-fulltext.md",
        catalog_rows=rows,
        references_dir=references_dir,
        generated_at=generated_at,
    )
    build_curated_markdown(
        output_file=references_dir / "apple-hig-ios-curated.md",
        catalog_rows=rows,
        references_dir=references_dir,
        generated_at=generated_at,
    )

    return catalog


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync Apple Human Interface Guidelines JSON sources into references/raw."
    )
    parser.add_argument(
        "--skill-dir",
        default=str(Path(__file__).resolve().parents[1]),
        help="Path to skill root (default: parent of scripts directory)",
    )
    parser.add_argument(
        "--sleep-ms",
        type=int,
        default=120,
        help="Delay between requests to reduce rate risk (default: 120)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_dir = Path(args.skill_dir).resolve()

    if not (skill_dir / "SKILL.md").exists():
        print(f"[ERR] Skill dir looks invalid: {skill_dir}", file=sys.stderr)
        return 1

    catalog = sync_sources(skill_dir=skill_dir, sleep_ms=args.sleep_ms)
    print(
        "[OK] synced HIG sources "
        f"total={catalog['total_nodes']} ok={catalog['download_ok']} err={catalog['download_error']}"
    )
    print(
        "[OK] wrote references/apple-hig-ios-raw.md, "
        "references/apple-hig-ios-fulltext.md, references/apple-hig-ios-curated.md, "
        "and references/raw/catalog.json"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
