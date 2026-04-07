# Server Rendering APIs

New server-side APIs added in React 19.2 for cache management and Partial Pre-rendering.

## `cacheSignal` (RSC only)

Returns an `AbortSignal` tied to the `cache()` lifetime. Use to abort in-flight work (e.g., fetch requests) when cached results are invalidated or no longer needed.

```js
import { cache, cacheSignal } from 'react';

const dedupedFetch = cache(fetch);

async function Component() {
  // Signal aborts when this cache entry is evicted
  await dedupedFetch(url, { signal: cacheSignal() });
}
```

- Only available in React Server Components
- The signal aborts when the cache entry that called `cacheSignal()` is garbage collected
- Pairs with `cache()` for deduplication — the signal is scoped to the same cache boundary

## Partial Pre-rendering

APIs to pre-render a static shell at build time, then resume with dynamic content at request time. Enables hybrid static/dynamic rendering in a single page.

### Two-step flow

**Step 1: Pre-render** — generates static HTML and captures a postponed state object.

```js
const { prelude, postponed } = await prerender(<App />, {
  signal: controller.signal,
});
```

- `prelude` — the static HTML shell (everything outside `<Suspense>` boundaries)
- `postponed` — serializable state needed to resume rendering later

**Step 2: Resume** — picks up where pre-rendering left off, rendering the dynamic parts.

### Resume to SSR stream

Use when serving dynamic content at request time:

```js
const stream = await resume(<App />, postponed);
```

Returns a readable stream of the dynamic HTML that slots into the pre-rendered shell.

### Resume to static HTML (SSG)

Use when generating fully static pages at build time:

```js
const { prelude } = await resumeAndPrerender(<App />, postponedState);
```

Returns static HTML for both the shell and the dynamic content.

### Node.js stream variants

For Node.js environments using `pipe`-based streams:

| API | Use case |
|---|---|
| `resumeToPipeableStream` | SSR with Node.js streams (request-time dynamic content) |
| `resumeAndPrerenderToNodeStream` | SSG with Node.js streams (build-time static generation) |

These are the Node-specific equivalents of `resume` and `resumeAndPrerender`, returning pipeable Node streams instead of web-standard readable streams.
