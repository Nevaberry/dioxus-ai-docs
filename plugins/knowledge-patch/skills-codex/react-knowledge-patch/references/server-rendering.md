# Server Rendering and Cache Lifetimes

The APIs and behavior in this reference are attributed to `19.2.0`.

## Cancel work when an RSC cache lifetime ends

`cacheSignal()` is an RSC-only API. It returns a signal that aborts when the surrounding `cache()` lifetime ends because rendering completed, aborted, or failed.

```jsx
import { cache, cacheSignal } from "react";

const dedupedFetch = cache(fetch);

async function Component() {
  await dedupedFetch(url, { signal: cacheSignal() });
  return null;
}
```

Pass the signal to cancellable work so work stops once its result can no longer enter the cache.

## Persist and resume partial pre-rendering

Static rendering can stop with reusable `postponed` state. Serve or cache the returned `prelude`, persist the `postponed` value, and resume the same tree later to fill in dynamic content.

```jsx
import { resume } from "react-dom/server";
import { prerender } from "react-dom/static";

const controller = new AbortController();
const { prelude, postponed } = await prerender(<App />, {
  signal: controller.signal,
});
await savePostponedState(postponed);

const stream = await resume(
  <App />,
  await getPostponedState(request),
);
```

Select the continuation by stream and output target:

| Goal | Web Stream | Node stream |
|---|---|---|
| Resume dynamic output | `resume` | `resumeToPipeableStream` |
| Finish the postponed tree as static HTML for SSG | `resumeAndPrerender` | `resumeAndPrerenderToNodeStream` |

## Prefer Node streams for Node SSR

Node supports the Web Streams SSR APIs `renderToReadableStream`, `prerender`, `resume`, and `resumeAndPrerender`. Prefer `renderToPipeableStream`, `prerenderToNodeStream`, `resumeToPipeableStream`, and `resumeAndPrerenderToNodeStream` on Node because the Node-stream variants are faster there and Web Streams do not provide compression by default.

## Do not depend on every Suspense reveal being batched

During streaming SSR, completed Suspense boundaries may wait briefly so nearby completions replace their fallbacks together. This matches client reveal behavior and can create larger View Transition batches.

React abandons the delay when holding a boundary could harm metrics such as the 2.5-second LCP threshold. Treat reveal batching as an optimization, not an ordering or timing guarantee.
