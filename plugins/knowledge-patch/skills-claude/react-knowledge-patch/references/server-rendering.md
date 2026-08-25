# Server Rendering and Cache Lifetimes

## Cancel work when an RSC cache lifetime ends

Since `19.2.0`, `cacheSignal()` is an RSC-only API. It returns a signal that
aborts when the surrounding `cache()` lifetime ends because rendering
completed, aborted, or failed:

```jsx
import { cache, cacheSignal } from "react";

const dedupedFetch = cache(fetch);

async function Component() {
  await dedupedFetch(url, { signal: cacheSignal() });
  return null;
}
```

Pass the signal to cancellable work so a result that can no longer enter the
cache does not continue consuming resources.

## Resume partial pre-rendering

Since `19.2.0`, static rendering can stop with reusable `postponed` state.
Serve or cache the returned `prelude`, persist the postponed state, and later
resume the same tree to fill in dynamic content:

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

Select the continuation for the desired output:

| Goal | Web Stream | Node stream |
|---|---|---|
| Resume dynamic output | `resume` | `resumeToPipeableStream` |
| Finish as static HTML for SSG | `resumeAndPrerender` | `resumeAndPrerenderToNodeStream` |

## Choose streams deliberately on Node

Node supports the Web Streams SSR APIs `renderToReadableStream`, `prerender`,
`resume`, and `resumeAndPrerender` since `19.2.0`. Their Node-stream
counterparts are faster for server rendering on Node:

| Web Streams API | Preferred Node-stream counterpart |
|---|---|
| `renderToReadableStream` | `renderToPipeableStream` |
| `prerender` | `prerenderToNodeStream` |
| `resume` | `resumeToPipeableStream` |
| `resumeAndPrerender` | `resumeAndPrerenderToNodeStream` |

Web Streams also do not provide compression by default.

## Do not depend on Suspense reveal batching

During streaming SSR, completed Suspense boundaries can wait briefly so
nearby completions replace their fallbacks together (`19.2.0`). This matches
client reveal behavior and can produce larger View Transition batches. React
abandons the delay when it could hurt metrics such as the 2.5-second LCP
threshold. Do not assume every nearby boundary will be held or revealed in
one batch.
