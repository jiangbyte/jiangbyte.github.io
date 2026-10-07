# jiangbyte.github.io

Personal notes site for **Charlie Zhang**, built with [Hugo Solitude](https://solitude.js.org/).

Content source:
- Notes → posts: [`jiangbyte/Notes`](https://github.com/jiangbyte/jiangbyte/tree/main/Notes)
- Projects → projects: [`jiangbyte/Projects`](https://github.com/jiangbyte/jiangbyte/tree/main/Projects)

Static output is published to the [`gh-pages`](https://github.com/jiangbyte/jiangbyte.github.io/tree/gh-pages) branch (GitHub Pages serves from there).

## Local

```bash
git submodule update --init --recursive
# sync Notes / Projects from sibling checkout
python3 scripts/sync_notes.py ../jiangbyte/Notes
python3 scripts/sync_projects.py ../jiangbyte/Projects
hugo server
```

## Deploy

From the content repo, run [`jiangbyte/scripts/push.sh`](https://github.com/jiangbyte/jiangbyte/blob/main/scripts/push.sh):

1. Commits/pushes `jiangbyte`
2. Syncs Notes/Projects into this repo on branch `sync/content` (runs `hugo --minify` locally first)
3. **Merge content sync branch** verifies Hugo, merges `sync/content` → `main`, then deploys `public/` to `gh-pages`

Direct pushes to `main` (site code only) still use **Deploy Hugo site to Pages**.

Reuse the static site elsewhere:

```bash
git clone --depth 1 --branch gh-pages https://github.com/jiangbyte/jiangbyte.github.io.git
```
