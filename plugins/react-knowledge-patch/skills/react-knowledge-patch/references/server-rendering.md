# Server Rendering Features

*Added in React 19.2 (2025-10-01)*

## cacheSignal (Server Components only)

### Overview

`cacheSignal()` returns an `AbortSignal` tied to the lifetime of a `cache()` call. Use it to abort in-flight fetch requests when the cached result is no longer needed — the render completed, was aborted, or failed.

### Import

```jsx
import { cache, cacheSignal } from 'react';
```

### Usage

```jsx
const dedupedFetch = cache(fetch);

async function Component() {
  // Signal auto-aborts when cache entry is invalidated or render completes
  await dedupedFetch(url, { signal: cacheSignal() });
}
```

### Key details

- Only available inside Server Components
- Pairs with `cache()` for request deduplication
- The signal aborts automatically when:
  - The render completes and the cached value is consumed
  - The render is aborted (e.g., client navigated away)
  - The render fails with an error
- Prevents resource leaks from long-running fetch requests in server rendering

---

## Partial Pre-rendering (PPR)

### Overview

Partial Pre-rendering splits SSR into two phases: a static shell pre-rendered at build time, and dynamic content rendered at request time. The static shell is served instantly while dynamic portions stream in.

### API

#### Phase 1: Pre-render the static shell

```jsx
import { prerender } from 'react-dom/static';

const { prelude, postponed } = await prerender(<App />, {
  signal: controller.signal, // optional AbortSignal
});

// Save postponed state for later resumption
await savePostponedState(postponed);
```

- `prelude` — readable stream of the static HTML shell
- `postponed` — serializable state representing the dynamic holes

#### Phase 2a: Resume to SSR stream (request-time dynamic content)

```jsx
import { resume } from 'react-dom/server';

const stream = await resume(<App />, postponed);
```

Use this at request time to fill in dynamic content as a streaming SSR response.

#### Phase 2b: Resume to static HTML (SSG / incremental static regeneration)

```jsx
import { resumeAndPrerender } from 'react-dom/static';

const { prelude } = await resumeAndPrerender(<App />, postponedState);
```

Use this to produce fully static HTML from postponed state (e.g., during a build step or ISR).

### Node.js stream variants

| API | Module | Use case |
|---|---|---|
| `prerender` | `react-dom/static` | Web streams |
| `prerenderToNodeStream` | `react-dom/static.node` | Node streams |
| `resume` | `react-dom/server` | Web streams |
| `resumeToPipeableStream` | `react-dom/server.node` | Node streams |
| `resumeAndPrerender` | `react-dom/static` | Web streams |
| `resumeAndPrerenderToNodeStream` | `react-dom/static.node` | Node streams |

### Typical PPR flow

1. **Build time**: Call `prerender()` → save `prelude` as static HTML, serialize `postponed`
2. **Request time**: Load serialized `postponed` → call `resume()` → stream dynamic content
3. **Client**: Static shell loads instantly, dynamic content streams in progressively

### Key details

- The `postponed` object is serializable — store it in a database, file, or cache
- Suspense boundaries define the split between static and dynamic content
- Static shell includes all content outside Suspense boundaries
- Dynamic content fills in Suspense fallbacks at request time
