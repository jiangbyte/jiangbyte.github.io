#!/usr/bin/env python3
"""Sync jiangbyte/Projects into content/projects.

Project articles live in the jiangbyte meta-repo under Projects/.
This site only keeps content/projects/_index.md in git; the rest is
copied at build / local sync time (same pattern as Notes → posts).

Source may use ``tags:`` for authoring; on copy they become ``project_tags``
so Hugo never merges them with article ``tags`` / ``categories``.
"""

from __future__ import annotations

import re
import shutil
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_SRC = (
    Path(sys.argv[1]).resolve()
    if len(sys.argv) > 1
    else ROOT.parent / "jiangbyte" / "Projects"
)
PROJECTS_DST = ROOT / "content" / "projects"

SKIP_NAMES = {"README.md", "_index.md", "index.md"}
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)
TITLE_LINE = re.compile(r"^title:\s*.*\n?", re.M)
DRAFT_FALSE = re.compile(r"^draft:\s*(?:false|False|no|0)\s*\n?", re.M)
CATEGORIES_LINE = re.compile(r"^categories:\s*.*\n?", re.M)
TAGS_KEY = re.compile(r"^tags:\s*", re.M)


def strip_title_and_false_draft(text: str) -> str:
    m = FM_RE.match(text)
    if not m:
        return text
    fm = TITLE_LINE.sub("", m.group(1))
    fm = DRAFT_FALSE.sub("", fm)
    fm = re.sub(r"\n{3,}", "\n\n", fm).strip()
    return f"---\n{fm}\n---\n" + text[m.end() :]


def set_title_from_filename(text: str, stem: str) -> str:
    title_line = f"title: {json.dumps(stem, ensure_ascii=False)}"
    m = FM_RE.match(text)
    if not m:
        return f"---\n{title_line}\n---\n\n" + text
    fm = TITLE_LINE.sub("", m.group(1)).strip()
    fm = f"{title_line}\n{fm}" if fm else title_line
    return f"---\n{fm}\n---\n" + text[m.end() :]


def remap_project_taxonomies(text: str) -> str:
    """Keep project labels out of article tags/categories taxonomies."""
    m = FM_RE.match(text)
    if not m:
        return text
    fm = CATEGORIES_LINE.sub("", m.group(1))
    fm = TAGS_KEY.sub("project_tags: ", fm)
    fm = re.sub(r"\n{3,}", "\n\n", fm).strip()
    return f"---\n{fm}\n---\n" + text[m.end() :]


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
            text = strip_title_and_false_draft(src.read_text(encoding="utf-8"))
            text = set_title_from_filename(text, src.stem)
            text = remap_project_taxonomies(text)
            dest.write_text(text, encoding="utf-8")
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
