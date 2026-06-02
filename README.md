# Charlie Byte Biu~

Personal blog by **CharlieByte**, built with [Hugo](https://gohugo.io) and [Blowfish](https://blowfish.page/) theme.

## Quick Start

```bash
git clone --recurse-submodules git@github.com:jiangbyte/jiangbyte.github.io.git
cd jiangbyte.github.io
hugo server
```

If already cloned without submodules:

```bash
git submodule update --init
```

## Write a Post

```bash
hugo new content posts/my-new-post/index.md
```

Add `featureimage` in frontmatter for a cover image, or leave it empty to use a random image from `https://api.yppp.net/pc.php`.

## Deploy

Push to `main` branch — GitHub Actions auto-builds and deploys to GitHub Pages.

## License

Content is licensed under CC BY-NC-SA 4.0.
