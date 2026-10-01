# jiangbyte.github.io

Personal notes site for **Charlie Zhang**, built with [Hugo Solitude](https://solitude.js.org/).

Content source: [`jiangbyte/Notes`](https://github.com/jiangbyte/jiangbyte).

Static output is published to the [`gh-pages`](https://github.com/jiangbyte/jiangbyte.github.io/tree/gh-pages) branch (GitHub Pages serves from there).

## Local

```bash
git submodule update --init --recursive
# optional: sync Notes into content/posts
python3 scripts/sync_notes.py /path/to/jiangbyte/Notes
hugo server
```

## Deploy

Push to `main` (or Notes update via `repository_dispatch`) → GitHub Actions builds Hugo → force-pushes `public/` to `gh-pages`.

Reuse the static site elsewhere:

```bash
git clone --depth 1 --branch gh-pages https://github.com/jiangbyte/jiangbyte.github.io.git
```
