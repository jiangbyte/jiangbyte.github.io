---
title: Understanding CSS Grid Layout
date: 2025-05-20
draft: false
description: A practical guide to CSS Grid for modern web layouts
categories:
  - Tech
tags:
  - css
  - frontend
  - web
---

CSS Grid is a powerful layout system that makes complex designs simple.

<!--more-->

## Basic Grid

```css
.container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
```

## Grid Areas

```css
.layout {
  display: grid;
  grid-template-areas:
    "header header header"
    "sidebar main main"
    "footer footer footer";
}
```

## Auto-fit vs Auto-fill

Use `auto-fit` when you want items to stretch, `auto-fill` when you want to preserve track sizes.

```css
.grid {
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}
```
