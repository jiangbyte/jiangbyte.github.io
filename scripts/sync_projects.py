#!/usr/bin/env python3
"""Sync jiangbyte/Projects into content/projects.

Project articles live in the jiangbyte meta-repo under Projects/.
This site only keeps content/projects/_index.md in git; the rest is
copied at build / local sync time (same pattern as Notes → posts).
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_SRC = (
    Path(sys.argv[1]).resolve()
    if len(sys.argv) > 1
    else ROOT.parent / "jiangbyte" / "Projects"
)
PROJECTS_DST = ROOT / "content" / "projects"

SKIP_NAMES = {"README.md", "_index.md", "index.md"}


def sync() -> None:
    if not PROJECTS_SRC.is_dir():
        raise SystemExit(f"Projects not found: {PROJECTS_SRC}")

    index = PROJECTS_DST / "_index.md"
    index_text = (
        index.read_text(encoding="utf-8")
        if index.exists()
        else "---\ntitle: 项目\ntype: projects\naside: false\ncomment: false\n---\n"
    )

    if PROJECTS_DST.exists():
        shutil.rmtree(PROJECTS_DST)
    PROJECTS_DST.mkdir(parents=True)
    index.write_text(index_text, encoding="utf-8")

    count = 0
    assets = 0
    for src in PROJECTS_SRC.rglob("*"):
        if src.name.startswith("."):
            continue
        if src.is_dir():
            continue
        rel = src.relative_to(PROJECTS_SRC)
        if src.suffix.lower() == ".md":
            if src.name in SKIP_NAMES:
                continue
            dest = PROJECTS_DST / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            count += 1
        elif "assets" in rel.parts:
            dest = PROJECTS_DST / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            assets += 1

    print(f"synced {count} projects -> {PROJECTS_DST}")
    print(f"copied {assets} assets beside projects")


if __name__ == "__main__":
    sync()
