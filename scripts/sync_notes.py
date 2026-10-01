#!/usr/bin/env python3
"""Sync jiangbyte/Notes into content/posts.

Keeps Obsidian relative image paths (assets/...) and places assets next to
posts under content/, so Hugo publishes them. Leaf-page path resolution is
handled by layouts/_markup/render-image.html (see Notes 工具/hugo article).
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
NOTES = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT.parent / "jiangbyte" / "Notes"
POSTS = ROOT / "content" / "posts"
STATIC_NOTES = ROOT / "static" / "notes"  # legacy; removed on sync
COVERS_FILE = ROOT / "data" / "covers.yaml"

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)

DEFAULT_COVERS = [
    "https://t.alcy.cc/pic/pc/347.webp",
    "https://t.alcy.cc/pic/pc/360.webp",
    "https://t.alcy.cc/pic/pc/361.webp",
    "https://t.alcy.cc/pic/pc/365.webp",
    "https://t.alcy.cc/pic/pc/375.webp",
    "https://t.alcy.cc/pic/pc/413.webp",
    "https://t.alcy.cc/pic/pc/416.webp",
    "https://t.alcy.cc/pic/pc/442.webp",
    "https://t.alcy.cc/pic/pc/470.webp",
    "https://t.alcy.cc/pic/pc/476.webp",
    "https://t.alcy.cc/pic/pc/499.webp",
    "https://t.alcy.cc/pic/pc/518.webp",
]


def load_covers() -> list[str]:
    if COVERS_FILE.exists():
        text = COVERS_FILE.read_text(encoding="utf-8")
        if yaml is not None:
            data = yaml.safe_load(text) or {}
            covers = data.get("covers") or []
            if covers:
                return [str(c) for c in covers]
        covers = []
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("- "):
                covers.append(s[2:].strip().strip("\"'"))
        if covers:
            return covers
    return DEFAULT_COVERS


def pick_cover(rel: Path, covers: list[str]) -> str:
    digest = hashlib.sha1(rel.as_posix().encode("utf-8")).hexdigest()
    return covers[int(digest[:8], 16) % len(covers)]


def ensure_cover(text: str, rel: Path, covers: list[str]) -> str:
    m = FM_RE.match(text)
    if not m:
        cover = pick_cover(rel, covers)
        return f'---\ncover: "{cover}"\n---\n\n' + text
    fm = m.group(1)
    if re.search(r"^cover:\s*\S", fm, re.M):
        return text
    cover = pick_cover(rel, covers)
    new_fm = fm.rstrip() + f'\ncover: "{cover}"'
    return f"---\n{new_fm}\n---\n" + text[m.end() :]


def sync() -> None:
    if not NOTES.is_dir():
        raise SystemExit(f"Notes not found: {NOTES}")

    covers = load_covers()

    index = POSTS / "_index.md"
    index_text = index.read_text(encoding="utf-8") if index.exists() else "---\ntitle: 文章\n---\n"

    if POSTS.exists():
        shutil.rmtree(POSTS)
    POSTS.mkdir(parents=True)
    index.write_text(index_text, encoding="utf-8")

    # Drop legacy static/notes rewrite layout
    if STATIC_NOTES.exists():
        shutil.rmtree(STATIC_NOTES)

    count = 0
    assets = 0
    for src in NOTES.rglob("*"):
        if src.name.startswith("."):
            continue
        rel = src.relative_to(NOTES)
        if src.is_dir():
            continue

        if src.suffix.lower() == ".md":
            if src.name in {"README.md", "_index.md", "index.md"}:
                continue
            dest = POSTS / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Keep relative assets/... paths; render-image.html resolves them.
            text = ensure_cover(src.read_text(encoding="utf-8"), rel, covers)
            dest.write_text(text, encoding="utf-8")
            count += 1
        elif "assets" in rel.parts:
            # Publish beside posts: content/posts/<dir>/assets/... → /posts/<dir>/assets/...
            dest = POSTS / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            assets += 1

    print(f"synced {count} posts -> {POSTS}")
    print(f"copied {assets} assets beside posts (relative path + render hook)")
    if STATIC_NOTES.exists():
        print(f"warning: {STATIC_NOTES} still present")


if __name__ == "__main__":
    sync()
