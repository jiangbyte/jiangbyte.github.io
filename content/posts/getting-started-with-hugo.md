---
title: Getting Started with Hugo
date: 2025-01-15
draft: false
description: A quick guide to building static sites with Hugo
categories:
  - Tech
tags:
  - hugo
  - tutorial
---

Hugo is one of the fastest static site generators out there.

<!--more-->

## Why Hugo?

Hugo is written in Go and can build thousands of pages in seconds. No dependencies, no runtime required.

## Quick Start

```bash
hugo new site my-site
cd my-site
git init
git submodule add https://github.com/g1eny0ung/hugo-theme-dream.git themes/dream
```

## Project Structure

```
content/
├── posts/
│   └── my-post.md
└── about/
    └── index.md
config/
└── _default/
    ├── hugo.yaml
    └── params.yaml
```
