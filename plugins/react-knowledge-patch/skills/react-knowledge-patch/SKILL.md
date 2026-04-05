---
name: react-knowledge-patch
description: "React changes since training cutoff (latest: 19.2) — Activity component, cacheSignal, Partial Pre-rendering (PPR), eslint-plugin-react-hooks v6. Load before working with React 19.x features."
version: "19.2.0"
license: MIT
metadata:
  author: Nevaberry
---

# React Knowledge Patch

Covers React 19.0–19.2 (through 2025-10-01). Claude Opus 4.6 knows React through 18.x including hooks, Suspense, concurrent features, Server Components basics, and the React 19 `use()` hook / Actions API.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Activity component | [references/activity-component.md](references/activity-component.md) | `<Activity>`, visible/hidden modes, state preservation, pre-rendering |
| Server rendering | [references/server-rendering.md](references/server-rendering.md) | `cacheSignal()`, Partial Pre-rendering (PPR), `prerender`, `resume`, `resumeAndPrerender` |
| Tooling | [references/tooling.md](references/tooling.md) | eslint-plugin-react-hooks v6, flat config, React Compiler rules |

---

## Quick Reference — React 19.2

| Feature | Import | Usage |
|---|---|---|
| Activity | `import { Activity } from 'react'` | `<Activity mode="visible"\|"hidden">` |
| cacheSignal | `import { cacheSignal } from 'react'` | `fetch(url, { signal: cacheSignal() })` |
| PPR prerender | `import { prerender } from 'react-dom/static'` | `const { prelude, postponed } = await prerender(<App />)` |
| PPR resume (SSR) | `import { resume } from 'react-dom/server'` | `const stream = await resume(<App />, postponed)` |
| PPR resume (SSG) | `import { resumeAndPrerender } from 'react-dom/static'` | `const { prelude } = await resumeAndPrerender(<App />, postponed)` |
| ESLint hooks v6 | `eslint-plugin-react-hooks` | Default export is flat config |

---

## `<Activity>` Component

New built-in component for pre-rendering and preserving hidden UI. Replaces conditional rendering patterns when state must survive visibility toggles.

```jsx
import { Activity } from 'react';

<Activity mode={isVisible ? 'visible' : 'hidden'}>
  <Page />
</Activity>;
```

Two modes:
- **`visible`** — normal rendering
- **`hidden`** — hides children via CSS, unmounts effects, defers updates; state is preserved (input values, scroll position, etc.)

Common patterns:
- Tab containers where inactive tabs keep their state
- Route pre-rendering (render next route before navigation)
- Keeping form state alive while showing a confirmation dialog

---

## `cacheSignal()` (Server Components)

Returns an `AbortSignal` tied to the `cache()` lifetime. Abort fetch requests when the cached result is no longer needed (render completed, aborted, or failed).

```jsx
import { cache, cacheSignal } from 'react';

const dedupedFetch = cache(fetch);

async function Component() {
  await dedupedFetch(url, { signal: cacheSignal() });
}
```

Only available in Server Components. Pairs with `cache()` for request deduplication with automatic cleanup.

---

## Partial Pre-rendering (PPR)

Pre-render a static shell, save postponed state, resume later with dynamic content. Enables hybrid static/dynamic SSR.

```jsx
import { prerender } from 'react-dom/static';
import { resume } from 'react-dom/server';

// Step 1: Pre-render static shell
const { prelude, postponed } = await prerender(<App />, {
  signal: controller.signal,
});
await savePostponedState(postponed);

// Step 2a: Resume to SSR stream (dynamic content)
const stream = await resume(<App />, postponed);

// Step 2b: Or resume to static HTML (SSG)
import { resumeAndPrerender } from 'react-dom/static';
const { prelude } = await resumeAndPrerender(<App />, postponedState);
```

Node stream variants: `resumeToPipeableStream`, `resumeAndPrerenderToNodeStream`.

---

## eslint-plugin-react-hooks v6

Default export is now ESLint flat config. For legacy `.eslintrc` config:

```diff
- extends: ['plugin:react-hooks/recommended']
+ extends: ['plugin:react-hooks/recommended-legacy']
```

New opt-in React Compiler powered rules available in the `recommended` preset.
