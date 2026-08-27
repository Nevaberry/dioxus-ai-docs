---
name: tanstack-router-knowledge-patch
description: TanStack Router
version: "1.170.18"
license: MIT
metadata:
  author: Nevaberry
---


# TanStack Router Knowledge Patch

Use this skill when implementing or reviewing TanStack Router applications,
especially around typed search, rewrites, masks, loaders, SSR, route splitting,
navigation blocking, matching, or route-generation tooling. Prefer the project's
installed types and generated route tree when they disagree with an example.

## Reference index

| Reference | Topics |
| --- | --- |
| [Search and matching](references/search-and-matching.md) | Search validation and middleware, trie matching, parameter parsing, route errors |
| [Rewrites, masks, and blocking](references/rewrites-masks-and-blocking.md) | Public/internal URLs, basepaths, route masks, reload behavior, navigation blockers |
| [Loaders and SSR](references/loaders-and-ssr.md) | Stale reloads, cache lifetimes, request handlers, streaming, serialization, hydration, runtime assets |
| [Code splitting and tooling](references/code-splitting-and-tooling.md) | Lazy routes, automatic splitting, route generation, transforms, Rsbuild, HMR, intent tooling |

## Breaking-change and pitfall checklist

- Treat `location.href` as the internal rewritten URL and
  `location.publicHref` as the external shareable URL.
- Keep custom rewrite pairs reversible. Input rewrites run in declaration order;
  output rewrites unwind in reverse order.
- Do not expect `@tanstack/router-cli` to perform automatic route splitting.
  `autoCodeSplitting` belongs to the bundler plugin.
- Split only `component`, `errorComponent`, `pendingComponent`, and
  `notFoundComponent` automatically. Matching and data configuration remains in
  the critical route chunk.
- Do not create a lazy `__root` route. Root render options remain unsplit.
- Distinguish a stale loader's reload mode from freshness. Blocking reloads wait;
  `staleTime: Infinity` prevents staleness instead.
- Remember that search navigation uses a validator's input type while route reads
  use its output type. Defaults are optional only when both are preserved.
- Treat route masks as history-state metadata. Shared masked URLs load the
  displayed route because the runtime location is absent.
- Keep browser unload prompting separate from client navigation resolution by
  configuring `enableBeforeUnload` explicitly.
- Serialize `Map`, `Set`, `BigInt`, and other complex SSR values yourself; they
  are outside the built-in serializer's supported set.
- Preserve literal punctuation rules when moving between physical and virtual
  route configurations; virtual dots and edge underscores are literal.

## Search validation quick reference

`validateSearch` receives parsed JSON data that has not yet been validated. A
thrown error reaches `onError` with `error.routerCode === 'VALIDATE_SEARCH'` and
renders the route's `errorComponent`. Prefer tolerant fallbacks for URLs that
should recover from malformed values.

```tsx
const searchSchema = z.object({
  page: z.number().catch(1),
  sort: z.enum(['newest', 'oldest']).catch('newest'),
})

export const Route = createFileRoute('/products')({
  validateSearch: searchSchema,
})
```

For Zod v3, use `@tanstack/zod-adapter` and its `fallback` helper so input and
output inference survives defaults. Zod v4 and Standard Schema validators can
be supplied directly.

Search middlewares affect links to a route and its descendants, then run again
after validation during navigation. Compose through `next`; use
`retainSearchParams` to carry selected current values and `stripSearchParams`
to omit values equal to defaults.

## Rewrites and masks quick reference

Configure `rewrite.input` for public-to-internal URL conversion before matching
and `rewrite.output` for internal-to-public conversion before link or history
writes. A handler receives `{ url: URL }` and may return the same URL, a new
`URL`, a full href string, or `undefined`.

```tsx
const router = createRouter({
  routeTree,
  basepath: '/app',
  rewrite: composeRewrites([localeRewrite, legacyRewrite]),
})
```

The router strips `basepath` before custom input rewrites and restores it after
custom output rewrites. Links and programmatic navigation apply output rewrites
automatically; an output rewrite that changes origin causes a hard navigation.

Use a per-navigation `mask` or register a typed `createRouteMask` in
`routeMasks`. A local reload retains mask state by default. Set
`unmaskOnReload: true` to discard it; per-link or navigation settings override
route-mask settings, which override the router default.

## Loader and cache quick reference

A loader can use `{ handler, staleReloadMode }`. Successful stale matches reload
in the background by default and retain existing `loaderData`; choose
`'blocking'` when navigation must await replacement data. Set
`defaultStaleReloadMode` for a router-wide default.

```tsx
export const Route = createFileRoute('/posts')({
  loader: {
    handler: () => fetchPosts(),
    staleReloadMode: 'blocking',
  },
})
```

Navigation data is immediately stale by default, preloads stay fresh for 30
seconds, and unused loader entries are collected after 30 minutes.
`router.invalidate()` reloads active routes and marks every cached route stale.

To discard unloaded data while still allowing dependency and entry loads, pair
`gcTime: 0` with `shouldReload: false`. The preload can still survive according
to `preloadGcTime`. Set `defaultPreloadStaleTime: 0` when an external cache
should receive every loader event and perform its own deduplication.

## SSR quick reference

The standalone React SSR API is experimental. Export a shared router factory,
pass it and a web-standard `Request` to `createRequestHandler`, and hydrate with
`RouterClient`. The default renderer supplies memory history and transfers
resolved loader data automatically.

```tsx
export function render({ request }: { request: Request }) {
  return createRequestHandler({ request, createRouter })(defaultRenderHandler)
}
```

Use `defaultStreamHandler` for automatic markup and dehydration streaming. Use
`renderRouterToString` or `renderRouterToStream` with an explicit `RouterServer`
when custom wrappers or providers must be rendered. Translate framework request
and response objects at adapter boundaries because the handler consumes a
web-standard `Request` and returns a web-standard `Response`.

The built-in serializer handles ordinary JSON plus `undefined`, `Date`, `Error`,
and `FormData`. See the SSR reference for hydration ordering, document-shell
behavior, deferred hydration, runtime CSS assets, script formats, and
server-component-safe exports.

## Code-splitting quick reference

For automatic file-route splitting, put the router plugin before the framework
plugin and enable its bundler option.

```ts
plugins: [
  tanstackRouter({ autoCodeSplitting: true }),
  react(),
]
```

Without automatic splitting, keep critical options in the normal route file and
place supported render options in a matching `.lazy.tsx` file with
`createLazyFileRoute`. If no critical configuration remains, delete the empty
normal file; the generated tree provides a virtual anchor.

Code-defined routes use `createLazyRoute` and attach it with `Route.lazy()`.
Split a loader by named import with `lazyFn`; its context commonly needs an
explicit `LoaderContext` type. File-based loaders require automatic splitting
with customized bundling options.

## Matching and navigation quick reference

Matching traverses a segment trie. Static candidates have priority, dynamic and
optional branches follow, and wildcards are considered last. Use
`params.priority` only to break otherwise competing candidates.

An experimental `params.parse` may return `false` to reject a candidate. Thrown
parse errors still surface on the selected match. Outgoing typed route-template
links use exact route lookup and then `params.stringify`.

With `useBlocker({ withResolver: true })`, a blocked result waits for `proceed`
or `reset`. Without resolver mode, `shouldBlockFn` may return a promise: resolve
`true` to cancel navigation and `false` to allow it.

## Tooling quick reference

- A route file can move from `posts.tsx` to `posts/route.tsx` so related split
  files can live together.
- Virtual route paths preserve dots, and leading or trailing underscores are
  literal URL characters. Physical file routes retain bracket escaping rules.
- Virtual configs resolve TypeScript path aliases.
- Transform parsing recognizes plain TypeScript when a filename is available,
  so angle-bracket assertions are not treated as JSX.
- Custom `routeToken` and `indexToken` values may begin with regex
  metacharacters.
- Multiple router plugin instances keep isolated route metadata.
- The router plugin supports Rsbuild, Vite 8 peers, and `vite-plugin-solid`
  beginning with `3.0.0-0`.
- Route HMR covers auto-split and unsplit render groups while preserving state
  across additional component shapes and aliased imports.

Use the references for exact API behavior and implementation constraints before
changing routing, loading, SSR, or build configuration.
