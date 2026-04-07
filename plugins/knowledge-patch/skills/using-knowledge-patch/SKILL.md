---
name: using-knowledge-patch
description: >
  Runtime guidance for sessions that have knowledge patches installed. Load the matching
  `*-knowledge-patch` skill before working with any patched technology.
---

## Why knowledge patches exist

You have a training data cutoff. After that date, technologies kept evolving: new APIs shipped, defaults changed, functions were deprecated, security vulnerabilities forced version bumps. Users run the latest versions, so the code they need you to write targets APIs you may never have seen.

The problem is that **stale knowledge feels identical to current knowledge from the inside.** You'll feel confident about an API that was redesigned six months ago. You'll reach for a function that was deprecated. You'll miss a new feature that's now the idiomatic solution. And you won't notice, because your confidence comes from real training data. It's just not current.

Knowledge patches fix this. Each one contains only what changed since your cutoff for one technology: curated, verified, and high signal. Loading one takes a moment. Producing plausible but broken code, then debugging it with the user, takes much longer.

## How to use them

Before working with a patched technology, load the matching patch:

1. Identify which technologies the task involves.
2. Check whether an installed `*-knowledge-patch` skill matches.
3. Invoke the matching skill before proceeding.

Priority when sources conflict: knowledge patch, then project docs, then training data.

This applies to code, reviews, debugging, planning, and recommendations. If a patch exists for the technology you're about to work with, load it first.
