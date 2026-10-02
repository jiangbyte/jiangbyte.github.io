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

ROOT = Path(__file__).resolve().parent.parent
NOTES = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT.parent / "jiangbyte" / "Notes"
POSTS = ROOT / "content" / "posts"
STATIC_NOTES = ROOT / "static" / "notes"  # legacy; removed on sync

# Local-only posts kept in git (not sourced from Notes). Preserved across sync.
LOCAL_POSTS = (
    Path("其它") / "01-Markdown特性完整测试.md",
)

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)

# Random scenery API. Unique ?u= avoids same-page cache / identical draws.
COVER_API = "https://t.alcy.cc/fj"


def pick_cover(rel: Path) -> str:
    digest = hashlib.sha1(rel.as_posix().encode("utf-8")).hexdigest()[:8]
    return f"{COVER_API}?u={digest}"


def ensure_cover(text: str, rel: Path) -> str:
    """Assign/refresh auto covers from fj API with a per-post unique query key."""
    cover = pick_cover(rel)
    m = FM_RE.match(text)
    if not m:
        return f'---\ncover: "{cover}"\n---\n\n' + text
    fm = m.group(1)
    existing = re.search(r'^cover:\s*["\']?(\S+?)["\']?\s*$', fm, re.M)
    if existing:
        old = existing.group(1)
        # Keep manually set covers; refresh 栗次元 / auto covers
        if "t.alcy.cc" not in old and not old.startswith("/img/"):
            return text
        fm = re.sub(r'^cover:\s*.*$', f'cover: "{cover}"', fm, count=1, flags=re.M)
    else:
        fm = fm.rstrip() + f'\ncover: "{cover}"'
    return f"---\n{fm}\n---\n" + text[m.end() :]


def sync() -> None:
    if not NOTES.is_dir():
        raise SystemExit(f"Notes not found: {NOTES}")

    index = POSTS / "_index.md"
    index_text = index.read_text(encoding="utf-8") if index.exists() else "---\ntitle: 文章\n---\n"

    preserved: dict[Path, str] = {}
    for rel in LOCAL_POSTS:
        fp = POSTS / rel
        if fp.is_file():
            preserved[rel] = fp.read_text(encoding="utf-8")

    if POSTS.exists():
        shutil.rmtree(POSTS)
    POSTS.mkdir(parents=True)
    index.write_text(index_text, encoding="utf-8")

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
            text = ensure_cover(src.read_text(encoding="utf-8"), rel)
            dest.write_text(text, encoding="utf-8")
            count += 1
        elif "assets" in rel.parts:
            dest = POSTS / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            assets += 1

    local_n = 0
    for rel, text in preserved.items():
        dest = POSTS / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Don't overwrite if Notes now ships the same path
        if not dest.exists():
            dest.write_text(ensure_cover(text, rel), encoding="utf-8")
            local_n += 1

    print(f"synced {count} posts -> {POSTS}")
    print(f"preserved {local_n} local posts")
    print(f"copied {assets} assets beside posts (relative path + render hook)")
    print(f"covers: {COVER_API}?u=<path-hash> (unique per post)")


if __name__ == "__main__":
    sync()
