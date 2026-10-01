#!/usr/bin/env python3
"""Sync jiangbyte/Notes into content/posts and rewrite asset image paths."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT.parent / "jiangbyte" / "Notes"
POSTS = ROOT / "content" / "posts"
STATIC_NOTES = ROOT / "static" / "notes"

IMG_RE = re.compile(r"(!\[[^\]]*\]\()((?:\./)?assets/[^)\s]+)(\))")


def sync() -> None:
    if not NOTES.is_dir():
        raise SystemExit(f"Notes not found: {NOTES}")

    # Keep posts/_index.md
    index = POSTS / "_index.md"
    index_text = index.read_text(encoding="utf-8") if index.exists() else "---\ntitle: 文章\n---\n"

    if POSTS.exists():
        shutil.rmtree(POSTS)
    POSTS.mkdir(parents=True)
    index.write_text(index_text, encoding="utf-8")

    if STATIC_NOTES.exists():
        shutil.rmtree(STATIC_NOTES)
    STATIC_NOTES.mkdir(parents=True)

    count = 0
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
            text = src.read_text(encoding="utf-8")
            parent = rel.parent.as_posix()
            prefix = f"/notes/{parent}/" if parent != "." else "/notes/"

            def repl(m: re.Match[str]) -> str:
                path = m.group(2)
                if path.startswith("./"):
                    path = path[2:]
                return f"{m.group(1)}{prefix}{path}{m.group(3)}"

            text = IMG_RE.sub(repl, text)
            dest.write_text(text, encoding="utf-8")
            count += 1
        elif "assets" in rel.parts:
            dest = STATIC_NOTES / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    print(f"synced {count} posts -> {POSTS}")
    print(f"assets -> {STATIC_NOTES}")


if __name__ == "__main__":
    sync()
