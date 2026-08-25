---
name: tanstack-router-knowledge-patch
description: TanStack Router
version: 1.170.18
license: MIT
metadata:
  author: Nevaberry
---


# TanStack Router Knowledge Patch

Use this skill when writing, reviewing, upgrading, or debugging TanStack Router
and TanStack Start applications. Identify the installed router, plugin, and
framework versions first, then open the reference matching the task.

Prefer the project's manifests, generated route tree, code, and tests when they
disagree with this guidance. Treat APIs explicitly described as experimental as
unstable.

## Reference index

| Reference | Topics |
| --- | --- |
| [Search parameters](references/search-params.md) | Validation failures, validator input/output typing, schema adapters, defaults, and search middlewares |
| [Matching and parameters](references/matching-and-params.md) | Segment-priority matching, route-param priority, parse rejection, and component-thrown route errors |
| [Rewrites and masking](references/rewrites-and-masking.md) | Bidirectional URL rewriting, composition, basepaths, route masks, and reload behavior |
| [Loading and SSR](references/loading-and-ssr.md) | Stale reloads, cache defaults, invalidation, request handlers, streaming, serialization, hydration, and assets |
| [Code splitting and navigation](references/code-splitting-and-navigation.md) | Route directories, automatic and manual splitting, lazy loaders and routes, blocking, and lazy-component revisits |
| [Start and build tooling](references/start-and-build-tooling.md) | Route-generator syntax, transforms, plugin isolation, Rsbuild, HMR, server exports, and intent tooling |

## Breaking behavior and defaults

### Keep validator input and output types distinct

`validateSearch` receives JSON-parsed, unvalidated search. Reads use the
validator's output type, while links and navigation accept its input type.
Defaults make fields optional at navigation sites only when the validator
preserves both sides correctly.

For Zod v3, use `@tanstack/zod-adapter` and `fallback`; direct `.catch()` can
erase the needed input/output distinction. Zod v4 and Standard Schema
implementations can be supplied directly.

```tsx
import { fallback, zodValidator } from '@tanstack/zod-adapter'

const schema = z.object({
  page: fallback(z.number(), 1).default(1),
})

export const Route = createFileRoute('/products')({
  validateSearch: zodValidator(schema),
})

const link = <Link to="/products" />
```

If validation throws, `onError` receives an error whose `routerCode` is
`'VALIDATE_SEARCH'`, and the route renders `errorComponent`. Use tolerant
fallbacks when a malformed URL should not interrupt navigation.

### Understand deterministic matching

Matching traverses a segment trie. Static, dynamic, optional, and wildcard
branches are explored by priority; fully static branches can win immediately,
and wildcards are considered last. Use `params.priority` only to break ties
between otherwise competing candidates.

`params.parse` may experimentally return `false` to reject an incoming
candidate. Throwing still reports a parse error on the selected match, and
outgoing typed template links use exact route lookup followed by
`params.stringify`.

```tsx
const reportRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/reports/$id',
  params: {
    parse: (raw) => /^\d+$/.test(raw.id)
      ? { id: Number(raw.id) }
      : false,
    stringify: ({ id }) => ({ id: String(id) }),
  },
})
```

### Choose stale reload behavior explicitly

A stale successful match reloads in the background by default and keeps its
current `loaderData` visible. Use loader `staleReloadMode: 'blocking'`, or
router `defaultStaleReloadMode`, when navigation must wait. `staleTime:
Infinity` instead prevents the data from becoming stale.

```tsx
export const Route = createFileRoute('/posts')({
  loader: {
    handler: () => fetchPosts(),
    staleReloadMode: 'blocking',
  },
})
```

Navigation results default to stale immediately, preloads stay fresh for 30
seconds, and unused entries are collected after 30 minutes. `router.invalidate()`
reloads active routes immediately and marks every cached route stale.

### Keep root document components outside Suspense

Since 1.170.28, root components that may render the HTML document are not
wrapped in Suspense during SSR or hydration. Do not rely on suspending the
document shell itself.

### Do not recreate resolved lazy components

Since 1.170.28, a resolved code-split lazy route component is retained for
later visits. A revisit should not show pending UI merely to resolve that same
component again.

## High-value features

### Apply search middlewares to generated destinations

`search.middlewares` transforms search for links to a route or its descendants,
then runs again after validation during navigation. Middlewares compose through
`next`. `retainSearchParams` copies selected current values, and
`stripSearchParams` removes values equal to supplied defaults.

```tsx
search: {
  middlewares: [
    retainSearchParams(['campaign']),
    stripSearchParams({ page: 1, tags: [] }),
  ],
}
```

### Separate internal and public URLs

Router `rewrite.input` maps the browser URL to the internal matching URL;
`rewrite.output` maps internal destinations back before links or history are
written. `location.href` is internal and `location.publicHref` is shareable.
Links and programmatic navigation apply output rewrites automatically, while a
changed origin forces a hard link navigation.

```tsx
const router = createRouter({
  routeTree,
  rewrite: {
    input: ({ url }) => {
      url.pathname = url.pathname.replace(/^\/(en|fr)(?=\/|$)/, '') || '/'
      return url
    },
    output: ({ url }) => {
      url.pathname = `/en${url.pathname === '/' ? '' : url.pathname}`
      return url
    },
  },
})
```

`composeRewrites` applies inputs first-to-last and outputs last-to-first. The
router strips `basepath` before custom input and restores it after custom
output. The same rewrites participate in request parsing and hydration.

### Treat masks as history-local state

A route mask runs one typed route while displaying another location. Pass
`mask` to `Link` or `navigate`, or register a typed `createRouteMask` in
`routeMasks`. Sharing the visible URL loses runtime mask state. Local reloads
retain it unless `unmaskOnReload` is enabled; navigation-level configuration
overrides mask configuration, which overrides the router default.

### Split only supported route options

Bundler-plugin `autoCodeSplitting` extracts only `component`,
`errorComponent`, `pendingComponent`, and `notFoundComponent`. Critical
matching and loading configuration stays eager. The router plugin must precede
the framework plugin, and the standalone router CLI cannot provide automatic
splitting.

```ts
plugins: [
  tanstackRouter({ autoCodeSplitting: true }),
  react(),
]
```

Without automatic splitting, keep critical options in the normal route file
and place those four render options in the corresponding `.lazy.tsx` file with
`createLazyFileRoute`. The `__root` route cannot be split.

### Use resolver mode for explicit navigation decisions

`useBlocker` receives typed `current` and `next` locations. With
`withResolver: true`, a true `shouldBlockFn` leaves the blocker pending until
`proceed` or `reset` is called. `enableBeforeUnload` separately controls the
native reload or tab-close prompt.

```tsx
const { status, proceed, reset } = useBlocker({
  shouldBlockFn: () => formIsDirty,
  withResolver: true,
  enableBeforeUnload: formIsDirty,
})
```

Without resolver mode, `shouldBlockFn` may return a promise: resolve `true` to
cancel navigation and `false` to allow it.

### Start SSR from a shared router factory

The standalone React SSR API is experimental. Pass a web-standard `Request`
and shared `createRouter` factory to `createRequestHandler`; hydrate with
`RouterClient`. Use `defaultStreamHandler` for streaming. Adapters such as
Express must translate request and response objects at their boundaries.

```tsx
export function render({ request }: { request: Request }) {
  return createRequestHandler({ request, createRouter })(defaultRenderHandler)
}
```

The default renderer creates server memory history and transfers resolved
loader data. For custom wrappers, use `renderRouterToString` or
`renderRouterToStream` with an explicit `RouterServer`.
