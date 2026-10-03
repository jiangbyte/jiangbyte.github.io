#!/usr/bin/env python3
"""Sync jiangbyte/Notes into content/posts.

Keeps Obsidian relative image paths (assets/...) and places assets next to
posts under content/, so Hugo publishes them. Leaf-page path resolution is
handled by layouts/_markup/render-image.html (see Notes 工具/hugo article).

Goldmark will not parse ``![alt](assets/Pasted image x.png)`` because an
unquoted space ends the destination; those lines render as literal text.
On copy, destinations that contain spaces are wrapped as ``<…>``.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
import json
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
TITLE_LINE = re.compile(r"^title:\s*.*\n?", re.M)
DRAFT_FALSE = re.compile(r"^draft:\s*(?:false|False|no|0)\s*\n?", re.M)
# ![alt](dest) / [text](dest), dest either <angled> or raw up to ')'
MD_LINK = re.compile(r"(!?\[[^\]]*\]\()(?:<([^>\n]+)>|([^)\n]+))(\))")

# Random scenery API. Unique ?u= avoids same-page cache / identical draws.
COVER_API = "https://t.alcy.cc/fj"


def wrap_spaced_md_destinations(text: str) -> str:
    """Make spaced relative URLs CommonMark-legal without changing Notes."""

    def rewrite_chunk(chunk: str) -> str:
        def repl(m: re.Match[str]) -> str:
            prefix, angled, raw, close = m.group(1), m.group(2), m.group(3), m.group(4)
            dest = (angled or raw).strip()
            if dest.startswith(("http://", "https://", "mailto:", "#")):
                return m.group(0)
            dest = dest.replace("%20", " ")
            if " " in dest:
                return f"{prefix}<{dest}>{close}"
            return m.group(0)

        return MD_LINK.sub(repl, chunk)

    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        if text.startswith("```", i):
            end = text.find("```", i + 3)
            if end == -1:
                out.append(text[i:])
                break
            out.append(text[i : end + 3])
            i = end + 3
            continue
        nxt = text.find("```", i)
        chunk = text[i:] if nxt == -1 else text[i:nxt]
        out.append(rewrite_chunk(chunk))
        if nxt == -1:
            break
        i = nxt
    return "".join(out)


def strip_title_and_false_draft(text: str) -> str:
    """Title comes from filename; omit draft unless true."""
    m = FM_RE.match(text)
    if not m:
        return text
    fm = TITLE_LINE.sub("", m.group(1))
    fm = DRAFT_FALSE.sub("", fm)
    fm = re.sub(r"\n{3,}", "\n\n", fm).strip()
    return f"---\n{fm}\n---\n" + text[m.end() :]


def set_title_from_filename(text: str, stem: str) -> str:
    """Hugo .Title is front matter only; derive it from the Notes filename."""
    title_line = f"title: {json.dumps(stem, ensure_ascii=False)}"
    m = FM_RE.match(text)
    if not m:
        return f"---\n{title_line}\n---\n\n" + text
    fm = TITLE_LINE.sub("", m.group(1)).strip()
    fm = f"{title_line}\n{fm}" if fm else title_line
    return f"---\n{fm}\n---\n" + text[m.end() :]


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
            text = strip_title_and_false_draft(src.read_text(encoding="utf-8"))
            text = wrap_spaced_md_destinations(text)
            text = set_title_from_filename(text, src.stem)
            text = ensure_cover(text, rel)
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
            dest.write_text(
                ensure_cover(
                    set_title_from_filename(
                        wrap_spaced_md_destinations(strip_title_and_false_draft(text)),
                        dest.stem,
                    ),
                    rel,
                ),
                encoding="utf-8",
            )
            local_n += 1

    print(f"synced {count} posts -> {POSTS}")
    print(f"preserved {local_n} local posts")
    print(f"copied {assets} assets beside posts (relative path + render hook)")
    print(f"covers: {COVER_API}?u=<path-hash> (unique per post)")


if __name__ == "__main__":
    sync()
