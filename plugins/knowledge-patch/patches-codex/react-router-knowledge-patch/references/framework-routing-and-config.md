# Framework Routing and Configuration

## Route configuration

### Explicit framework routes (`7.0.0`)

Export a `RouteConfig` from `app/routes.ts` and use helpers from
`@react-router/dev/routes`. Remix-style file routes remain available through
`flatRoutes()` from `@react-router/fs-routes`; the Remix configuration adapter can bridge
custom route callbacks.

```ts
import { index, route, type RouteConfig } from "@react-router/dev/routes";

export default [
  index("./home.tsx"),
  route("products/:id", "./product.tsx"),
] satisfies RouteConfig;
```

The ID `root` is reserved for the actual root route and is rejected on another configured
route (`7.6.0`). Route config may use `.mts` or `.mjs` files (`7.7.0`).

### Layouts, prefixes, file routes, and relative helpers

`layout` creates outlet nesting with a module but no URL segment. `prefix` prepends a URL
path without creating a route and returns entries that must be spread
(`framework-mode`).

```ts
import { layout, prefix, route, type RouteConfig } from "@react-router/dev/routes";

export default [
  layout("./auth/layout.tsx", [route("login", "./auth/login.tsx")]),
  ...prefix("projects", [route(":id", "./projects/project.tsx")]),
] satisfies RouteConfig;
```

`flatRoutes()` defaults to `app/routes`; use `rootDirectory` relative to `app` and
`ignoredRouteFiles` to customize discovery. The `relative` helper creates route helpers
whose module paths resolve against a chosen directory (`type-safety-and-config`).

```ts
export default flatRoutes({
  rootDirectory: "file-routes",
  ignoredRouteFiles: ["home.tsx"],
}) satisfies RouteConfig;
```

### Environment-aware routes (`7.10.0`)

The dev package loads environment variables before evaluating `routes.ts`, so route
selection can read `VITE_`-prefixed `import.meta.env` values.

```ts
import { route, type RouteConfig } from "@react-router/dev/routes";

const routes: RouteConfig = [];
if (import.meta.env.VITE_ENV_ROUTE === "my-route") {
  routes.push(route("my-route", "routes/my-route.tsx"));
}
export default routes;
```

## Route-module splitting and lazy code

Framework route modules are automatically split from v7.2 (`7.0-guide`). With
`future.unstable_splitRouteModules: "enforce"`, the root route is an exception and may
retain splittable and unsplittable exports because it always remains one chunk (`7.4.0`).

From `7.5.0`, Data Mode `route.lazy` can be an object whose properties import separately.
Each promise resolves to that route export's value. The old
`route.unstable_lazyMiddleware` is removed; at that point lazy middleware belongs at
`route.lazy.unstable_middleware`.

```ts
createBrowserRouter([{
  path: "/show/:showId",
  lazy: {
    loader: async () => (await import("./show.loader.js")).loader,
    action: async () => (await import("./show.action.js")).action,
    Component: async () => (await import("./show.component.js")).Component,
  },
}]);
```

An earlier 7.4.1 transition required `route.unstable_lazyMiddleware` instead of returning
`unstable_middleware` from a `route.lazy` function (`7.4.0`); do not copy either old form
into later versions.

In v8, `splitRouteModules` is top-level and defaults to `true`; use `false` for one chunk
per route or `"enforce"` to require splitting (`8.0.0`).

Shared declarations referenced by multiple route exports prevent isolation. The app can
still build as one chunk, but enforcement fails. Move shared code to another module so
each generated chunk imports it (`project-direction-and-route-modules`).

## Route discovery and patching

### Framework manifest discovery (`7.6.0`)

`routeDiscovery` supports lazy manifest requests, a custom manifest endpoint for
multi-app servers, or `mode: "initial"` to include every route up front. Lazy mode
defaults to `/__manifest`.

```ts
export default {
  routeDiscovery: { mode: "lazy", manifestPath: "/my-app/__manifest" },
};
```

Lazy discovery initially includes only matched routes, then batches rendered links into a
single manifest request and patches their routes before navigation. A click that wins the
race still works after paying for discovery; each route is discovered once per session
(`data-loading-and-rendering`).

Framework Mode detects manifest-version skew across deployments: navigating to a newly
undiscovered route reloads the destination, while a fetcher discovery reloads the current
location (`7.3.0`).

### Data Mode route patching

`patchRoutesOnNavigation` receives `fetcherKey` so discovery can identify its initiating
fetcher (`7.3.0`). For fetcher requests, its `path` excludes search parameters as of
`7.7.0`.

```ts
createBrowserRouter(routes, {
  patchRoutesOnNavigation({ fetcherKey, path, patch }) {
    // Discover routes for path and, when present, the originating fetcher.
  },
});
```

## Requests, paths, and URL presentation

### Trailing-slash data endpoints

`7.12.0` introduced `future.unstable_trailingSlashAwareDataRequests`. It preserves a
browser trailing slash for middleware/loaders/actions and maps `/a/b/c/` to
`/a/b/c/_.data` and `/` to `/_.data`; update cache and proxy rules. The spelling became
`future.v8_trailingSlashAwareDataRequests` in `7.16.0`; the old spelling then caused a
config error. V8 removes the flag because the behavior is unconditional (`8.0.0`).

### Raw requests and normalized URLs

`future.unstable_passThroughRequests` arrived in 7.13.2 (`7.13.0`). It passes the raw
incoming `Request`, including `.data`, `index`, and `_routes` details, and adds
`unstable_url` for normalized routing. In `7.15.0`, the flag and argument become
`future.v8_passThroughRequests` and `url`. V8 adopts the behavior unconditionally: use
`request.url` for transport details and `url` for route logic (`8.0.0`).

### URL masks and path normalization

`<Link unstable_mask>` began as an SPA-only contextual-route API in `7.13.0`; the visible
mask appears on `useLocation().unstable_mask` and is stripped from history state during
SSR. `7.15.0` stabilizes the names to `mask`, optional `Location.mask`, and
`normalizePath` (including `staticHandler.query`/`queryRoute`).

```tsx
<Link to="/gallery?image=42" mask="/images/42">Open image</Link>
```

## SSR, SPA, and prerender configuration

### Build-time prerendering (`7.0.0`)

The Vite plugin's `prerender` callback chooses paths and writes `.html` plus `.data` files;
resource routes can also be prerendered. `@react-router/serve` returns `.data` as
`text/x-turbo`. Files outside the asset directory have no explicit cache policy.

Setting `prerender: true` discovers and builds every static path from `routes.ts`; dynamic
parameters still require explicit values (`data-loading-and-rendering`).

### SPA fallback files (`7.2.0`)

With `ssr: false`, omitting `/` from `prerender` keeps `index.html` as the generic SPA
fallback. Including `/` makes it root-specific and emits `__spa-fallback.html` for other
application paths.

SPA Mode permits a root build-time loader. Without prerender, only root may have a loader;
with prerender, matched routes on configured paths may load. `headers` and `action` remain
forbidden, and dynamic fallback routes need `clientLoader` rather than server revalidation.
`Route.HydrateFallbackProps` has optional `loaderData` while children load.

### Server bundles

`serverBundles` maps a route branch to a bundle ID used as its directory beneath the
server build (`type-safety-and-config`). From `7.14.0`, prerendering supports multiple
server bundles when `v8_viteEnvironmentApi` is enabled.

```ts
export default {
  serverBundles: ({ branch }) =>
    branch.some((route) => route.id === "admin") ? "admin" : "main",
};
```

### Preview behavior (`8.0.0`)

V8 uses Vite preview-server prerendering exclusively and removes
`future.unstable_previewServerPrerendering` because the Environment API is mandatory.

## Flag migration map

`7.10.0` renamed splitting and Environment API flags to `future.v8_splitRouteModules` and
`future.v8_viteEnvironmentApi`. `7.15.0` then stabilized several more names:

| Earlier spelling | Later spelling |
| --- | --- |
| `future.unstable_passThroughRequests` | `future.v8_passThroughRequests` |
| `future.unstable_subResourceIntegrity` | top-level `subResourceIntegrity` |
| `prerender.unstable_concurrency` | `prerender.concurrency` |
| `unstable_url` | `url` |
| `unstable_defaultShouldRevalidate` | `defaultShouldRevalidate` |
| `unstable_useTransitions` | `useTransitions` |
| `unstable_mask` | `mask` |
| `unstable_normalizePath` | `normalizePath` |

Dev tooling warns about upcoming `v8_middleware`, `v8_splitRouteModules`,
`v8_viteEnvironmentApi`, `v8_passThroughRequests`, and
`v8_trailingSlashAwareDataRequests` behaviors from `7.16.0`. In `8.0.0`, middleware,
pass-through requests, trailing-slash-aware data requests, and the Vite Environment API
are unconditional; only current top-level route-splitting configuration remains.
