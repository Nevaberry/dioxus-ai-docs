# Server Rendering and Cache Lifetimes

The APIs and behavior in this reference are available in React `19.2.0`.

## Cancel work with `cacheSignal`

`cacheSignal()` is available only in React Server Components. It returns an `AbortSignal` tied to the surrounding `cache()` lifetime. The signal aborts when rendering:

- completes;
- aborts; or
- fails.

Pass it to cancellable work so work stops when its result can no longer enter the cache:

```jsx
import { cache, cacheSignal } from "react";

const dedupedFetch = cache(fetch);

async function Component() {
  await dedupedFetch(url, { signal: cacheSignal() });
  return null;
}
```

## Partial pre-rendering workflow

Static rendering can stop at dynamic work and return two artifacts:

- `prelude`: HTML that can be served immediately or cached; and
- `postponed`: reusable state needed to continue the same tree later.

Create and retain the postponed state:

```jsx
import { prerender } from "react-dom/static";

const controller = new AbortController();
const { prelude, postponed } = await prerender(<App />, {
  signal: controller.signal,
});

await savePostponedState(postponed);
```

Resume the same tree when request-specific dynamic content is available:

```jsx
import { resume } from "react-dom/server";

const postponed = await getPostponedState(request);
const stream = await resume(<App />, postponed);
```

The resumed render must correspond to the pre-rendered tree and its saved postponed state.

## Resume API selection

| Goal | Web Stream API | Node stream API |
|---|---|---|
| Resume and stream dynamic content | `resume` | `resumeToPipeableStream` |
| Complete postponed work as static HTML for SSG | `resumeAndPrerender` | `resumeAndPrerenderToNodeStream` |

`resumeAndPrerender` and `resumeAndPrerenderToNodeStream` finish the postponed tree as static output rather than serving it as a dynamic streaming continuation.

## Web Streams on Node

Node.js supports these Web Streams server-rendering APIs:

- `renderToReadableStream`;
- `prerender`;
- `resume`; and
- `resumeAndPrerender`.

Prefer the corresponding Node-stream APIs when rendering on Node because they are faster there:

- `renderToPipeableStream`;
- `prerenderToNodeStream`;
- `resumeToPipeableStream`; and
- `resumeAndPrerenderToNodeStream`.

Web Streams do not provide compression by default.

## Batched Suspense reveals

During streaming SSR, React may wait briefly after a Suspense boundary completes so nearby boundaries can replace their fallbacks together. This aligns server reveals with client reveal behavior and can produce larger View Transition batches.

The delay is opportunistic. React abandons it when waiting could hurt user-visible metrics, including the 2.5-second Largest Contentful Paint threshold. Application correctness and coordination must not depend on all nearby boundaries revealing in one batch.
