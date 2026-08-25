# Loading and Server Rendering

## Select background or blocking stale reloads

A loader may use an object with `handler` and `staleReloadMode`. Stale
successful matches reload in `'background'` mode by default, keeping the old
`loaderData` visible. Set a loader to `'blocking'`, or configure router
`defaultStaleReloadMode`, when navigation must await the replacement result.

```tsx
export const Route = createFileRoute('/posts')({
  loader: {
    handler: () => fetchPosts(),
    staleReloadMode: 'blocking',
  },
})
```

`staleTime: Infinity` has a different purpose: it keeps data from becoming
stale rather than selecting the behavior of a stale reload.

## Apply loader-cache defaults and opt-outs

- Navigation results use `staleTime: 0` by default.
- Preloads remain fresh for 30 seconds by default.
- Unused cache entries are garbage-collected after 30 minutes by default.
- `router.invalidate()` immediately reloads active routes and marks every
  cached route stale.

To discard data after a route unloads but still permit entry and dependency
loads, combine `gcTime: 0` with `shouldReload: false`. The default
`preloadGcTime` still allows a preload to survive until navigation.

```tsx
export const Route = createFileRoute('/posts')({
  loaderDeps: ({ search }) => ({ page: search.page }),
  loader: ({ deps }) => fetchPosts(deps),
  gcTime: 0,
  shouldReload: false,
})
```

When an external cache should see and deduplicate every loader event, set
router `defaultPreloadStaleTime: 0`.

## Build a router-native SSR entry

The standalone React SSR API is experimental. Export a shared router factory,
then pass it and the web-standard `Request` to `createRequestHandler`. Hydrate
on the client with `RouterClient`.

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
```

```tsx
// entry-client.tsx
import { RouterClient } from '@tanstack/react-router/ssr/client'
import { hydrateRoot } from 'react-dom/client'

const router = createRouter()
hydrateRoot(document, <RouterClient router={router} />)
```

The request handler returns a web-standard `Response`; Express and similar
adapters must translate their native request and response at the boundary. The
default renderer supplies server memory history and transfers resolved loader
data. For explicit wrappers or providers, use `renderRouterToString` and render
an explicit `RouterServer` child.

## Stream markup and dehydration data

Use `defaultStreamHandler` with the same request-handler setup to stream markup
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

SSR serialization round-trips `undefined`, `Date`, `Error`, and `FormData` in
addition to ordinary JSON values. `Map`, `Set`, `BigInt`, and other complex
values are not supported by default and require explicit handling. General
serializer customization remains work in progress.

## Install hydrated configuration before matching

Custom router hydration runs before the first client route match. This allows
hydrated request-specific configuration, including URL rewrites, to be in place
before SSR hydration compares matches.

## Keep the document shell outside Suspense

Since 1.170.28, root components that may render the HTML document are not
wrapped in a Suspense boundary during SSR or hydration. The document shell
therefore cannot itself suspend at the root.

## Transform SSR assets without duplicate styles

TanStack Start SSR accepts inline CSS manifests that hydrate without adding
duplicate stylesheet links. `transformAssets` also supports runtime-selected
inline CSS and opt-in CSS URL templates.

## Defer selected hydration boundaries

TanStack Start's compiler can split `Hydrate` boundaries, preload their
generated client chunks, preserve server-rendered fallback HTML, and replay
events that triggered interaction before hydration finished. This integration
works with Vite and Rsbuild.
