# Loaders, Server Rendering, Hydration, and Runtime Assets

## Choose background or blocking stale reloads

A loader can use an object form with `handler` and `staleReloadMode`. Successful
stale matches default to `'background'`, keeping existing `loaderData` visible
during revalidation. Select `'blocking'` on the loader when navigation must
wait for replacement data, or set `defaultStaleReloadMode` on the router.

```tsx
export const Route = createFileRoute('/posts')({
  loader: {
    handler: () => fetchPosts(),
    staleReloadMode: 'blocking',
  },
})
```

`staleTime: Infinity` solves a different problem: it prevents the data from
becoming stale instead of changing how an already stale reload runs.

## Apply loader-cache defaults and opt-outs

Navigation results default to `staleTime: 0`. Preloads remain fresh for 30
seconds, and unused entries are garbage-collected after 30 minutes.
`router.invalidate()` immediately reloads active routes and marks every cached
route stale.

To discard data after a route unloads while allowing entry and dependency
loads, combine `gcTime: 0` with `shouldReload: false`. The default
`preloadGcTime` still allows a preload to survive until navigation.

```tsx
export const Route = createFileRoute('/posts')({
  loaderDeps: ({ search }) => ({ page: search.page }),
  loader: ({ deps }) => fetchPosts(deps),
  gcTime: 0,
  shouldReload: false,
})

const router = createRouter({
  routeTree,
  defaultPreloadStaleTime: 0,
})
```

Set `defaultPreloadStaleTime: 0` when an external cache should receive and
deduplicate every loader event.

## Render with router-native SSR

The standalone React SSR API is experimental. Export a shared router factory,
then pass it with a web-standard `Request` to `createRequestHandler`. Hydrate
the client with `RouterClient`. The default renderer supplies server memory
history and automatically dehydrates and rehydrates resolved loader data.

```tsx
// entry-server.tsx
import {
  createRequestHandler,
  defaultRenderHandler,
} from '@tanstack/react-router/ssr/server'
import { createRouter } from './router'

export function render({ request }: { request: Request }) {
  return createRequestHandler({ request, createRouter })(defaultRenderHandler)
}

// entry-client.tsx
import { RouterClient } from '@tanstack/react-router/ssr/client'
import { hydrateRoot } from 'react-dom/client'

const router = createRouter()
hydrateRoot(document, <RouterClient router={router} />)
```

The handler returns a web-standard `Response`. Adapters such as Express must
translate request and response objects at the boundary. When wrappers or
providers must be rendered explicitly, use `renderRouterToString` with an
explicit `RouterServer` child instead of `defaultRenderHandler`.

## Stream markup and dehydration data

Use the same request-handler setup with `defaultStreamHandler` to stream markup
and dehydration data automatically. The lower-level alternative is
`renderRouterToStream` with an explicit `RouterServer` child.

```tsx
import {
  createRequestHandler,
  defaultStreamHandler,
} from '@tanstack/react-router/ssr/server'

export function render({ request }: { request: Request }) {
  return createRequestHandler({ request, createRouter })(defaultStreamHandler)
}
```

## Respect built-in serialization limits

The built-in serializer round-trips ordinary JSON data plus `undefined`,
`Date`, `Error`, and `FormData`. It does not include `Map`, `Set`, `BigInt`, or
other complex values. Handle those values explicitly; a general serializer
customization mechanism remains work in progress.

## Defer hydration at compiler boundaries

TanStack Start's compiler can split `Hydrate` boundaries, preload their
generated client chunks, preserve server-rendered fallback HTML, and replay
interaction-triggered events after hydration. This integration supports Vite
and Rsbuild.

## Hydrate router configuration before matching

Custom router hydration runs before the first client route match. Install
hydrated configuration, including request-specific URL rewrites, before SSR
hydration compares route matches.

## Transform runtime SSR assets

TanStack Start SSR supports inline CSS manifests that hydrate without duplicate
stylesheet links. `transformAssets` also supports runtime-configurable inline
CSS and opt-in CSS URL templates.

## Select Rsbuild client script formats

Rsbuild client output uses module scripts by default and can emit IIFE output
for classic-script environments. A `transformAssets` script callback receives
only `{ kind: 'script', url }`. Configure script asset cross-origin behavior
under the `script` key.

## Import server-safe router exports

The `@tanstack/react-router` root export defines a `react-server` condition that
preserves the normal API surface while resolving `notFound` and `redirect` from
a server-safe entry. React Server Components and server functions can continue
to import them from the package root.

```tsx
import { notFound, redirect } from '@tanstack/react-router'
```

## Keep root document components outside Suspense

Since 1.170.28, root components that may render the HTML document are not
wrapped in a Suspense boundary during SSR or hydration. The document shell
therefore cannot be suspended at the root.
