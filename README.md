# jiangbyte.github.io

Personal notes site for **Charlie Zhang**, built with [Hugo Solitude](https://solitude.js.org/).

Content source:
- Notes → posts: [`jiangbyte/Notes`](https://github.com/jiangbyte/jiangbyte/tree/main/Notes)
- Projects → projects: [`jiangbyte/Projects`](https://github.com/jiangbyte/jiangbyte/tree/main/Projects)

Static output is published to the [`gh-pages`](https://github.com/jiangbyte/jiangbyte.github.io/tree/gh-pages) branch (GitHub Pages serves from there).

## Local

```bash
git submodule update --init --recursive
# optional: sync Notes / Projects
python3 scripts/sync_notes.py /path/to/jiangbyte/Notes
python3 scripts/sync_projects.py /path/to/jiangbyte/Projects
hugo server
```

## Deploy

Push to site `main`, or push `Notes/**` / `Projects/**` on [`jiangbyte`](https://github.com/jiangbyte/jiangbyte) (triggers `repository_dispatch`) → GitHub Actions syncs content at build time → Hugo → force-pushes `public/` to `gh-pages`.

Reuse the static site elsewhere:

```bash
git clone --depth 1 --branch gh-pages https://github.com/jiangbyte/jiangbyte.github.io.git
```
