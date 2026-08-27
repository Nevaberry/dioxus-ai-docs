# Framework Routing and Configuration

## Define the route tree

### Explicit route configuration

Since 7.0.0, Framework Mode exports a `RouteConfig` from `app/routes.ts` and uses
helpers from `@react-router/dev/routes`.

```ts
import { index, layout, prefix, route, type RouteConfig } from "@react-router/dev/routes";

export default [
  index("./home.tsx"),
  layout("./auth/layout.tsx", [route("login", "./auth/login.tsx")]),
  ...prefix("products", [route(":id", "./products/product.tsx")]),
] satisfies RouteConfig;
```

`layout` inserts a route module and outlet nesting without adding a URL segment.
`prefix` adds a URL prefix without adding a route and returns an array that must be
spread. The `relative` helper creates route helpers whose module paths resolve from
a supplied directory, which is useful for route definitions split across files.

The route ID `root` is reserved for the actual root route as of 7.6.0; assigning it
to another route is rejected.

### File-route discovery

Remix-style file routes remain available through `flatRoutes()` from
`@react-router/fs-routes`. It defaults to `app/routes`; `rootDirectory` selects a
different directory relative to `app`, while `ignoredRouteFiles` filters matched
modules.

```ts
import { flatRoutes } from "@react-router/fs-routes";
import type { RouteConfig } from "@react-router/dev/routes";

export default flatRoutes({
  rootDirectory: "file-routes",
  ignoredRouteFiles: ["home.tsx"],
}) satisfies RouteConfig;
```

Custom Remix route callbacks can be bridged through
`@react-router/remix-config-routes-adapter`.

## Route discovery and lazy code

### Configurable manifest discovery

Framework Mode's 7.6.0 `routeDiscovery` option supports the default lazy manifest,
a custom endpoint for hosts serving multiple applications, and initial mode, which
puts every route in the initial manifest.

```ts
export default {
  routeDiscovery: {
    mode: "lazy",
    manifestPath: "/my-app/__manifest",
  },
};
```

Lazy mode defaults to `/__manifest`. The first document includes matched routes;
rendered links are then batched into one manifest request and patched before likely
navigations. A click that beats discovery still succeeds after the discovery
request, and each route is discovered only once per session. If deployment makes a
client manifest stale, Framework Mode reloads the destination for navigation or the
current page for a fetcher call (7.3.0).

`patchRoutesOnNavigation` receives `fetcherKey` as of 7.3.0. For fetcher-triggered
calls, its `path` excludes search parameters as of 7.7.0.

```ts
createBrowserRouter(routes, {
  patchRoutesOnNavigation({ fetcherKey, path, patch }) {
    // Discover and patch routes for this path and initiating fetcher.
  },
});
```

### Per-property Data Mode lazy imports

Since 7.5.0, `route.lazy` can be an object whose members import route properties
independently rather than importing a whole route module.

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

The former `route.unstable_lazyMiddleware` transition is obsolete. In 7.5, lazy
middleware used `route.lazy.unstable_middleware`; current code should use the stable
middleware surface supported by its installed version.

## Route-module splitting

Automatic Framework Mode route-module splitting was introduced in the 7.0-guide
and active by 7.2. It later used `future.unstable_splitRouteModules`, then
`future.v8_splitRouteModules` in 7.10.0. In 8.0.0 it became top-level
`splitRouteModules` and defaults to `true`.

```ts
export default {
  splitRouteModules: "enforce",
};
```

Use `false` for one chunk per route module. Under enforced splitting, the root route
may still contain splittable and unsplittable exports because it is always emitted
as one chunk (7.4.0).

If multiple route exports reference one declaration defined inside the route module,
they cannot be isolated. The app can still build as one chunk, but enforcement fails;
move the shared declaration into another module so each chunk can import it.

## Prerendering and SPA output

### Select paths at build time

The 7.0.0 Vite plugin can prerender route and resource paths into `.html` and `.data`
files. A callback can combine generated static paths with explicit dynamic values.

```ts
reactRouter({
  async prerender({ getStaticPaths }) {
    return [...getStaticPaths(), "/products/hat"];
  },
});
```

`prerender: true` discovers and builds every static route from `routes.ts`;
parameterized routes remain excluded until explicit values are supplied. Prerender
concurrency began as `prerender.unstable_concurrency` in 7.9.0 and stabilized as
`prerender.concurrency` in 7.15.0.

When multiple server bundles are enabled, 7.14.0 can prerender them under the v8
Vite Environment API behavior. In v8, the preview-server prerenderer is the only
implementation.

`@react-router/serve` serves `.data` files as `text/x-turbo`. Generated prerender
files outside the asset directory have no explicit cache policy, so configure the
deployment cache deliberately.

### SPA fallback files

With `ssr: false`, omitting `/` from `prerender` leaves `index.html` as the generic
SPA fallback. Including `/` makes `index.html` the root-route output and emits
`__spa-fallback.html` for non-prerendered application paths (7.2.0).

```ts
export default {
  ssr: false,
  prerender: ["/", "/blog/post"],
};
```

Without prerendering, SPA Mode permits only a build-time root loader. With explicit
prerender paths, their matched loaders may also run. `headers` and `action` remain
forbidden, and dynamic fallback paths need `clientLoader` rather than server-loader
revalidation.

## Server bundles and environment-aware routes

The `serverBundles` callback receives a route branch and returns the output directory
name, allowing server code to be split by route family.

```ts
import type { Config } from "@react-router/dev/config";

export default {
  serverBundles: ({ branch }) =>
    branch.some((route) => route.id === "admin") ? "admin" : "main",
} satisfies Config;
```

Since 7.10.0, `@react-router/dev` loads environment variables before evaluating
`routes.ts`; route selection may use `VITE_`-prefixed `import.meta.env` values.

## URL forms and masking

URL masks route to `to` while displaying another URL, such as a gallery modal with a
shareable standalone address. The feature arrived as `unstable_mask` in 7.13.1 and
stabilized as `mask` in 7.15.0. Read the active mask from `useLocation().mask`.
Masking is SPA-only and is removed from history state during SSR.
`Location.mask` is optional in the stable 7.15.0 API.

```tsx
<Link to="/gallery?image=42" mask="/images/42">Open image</Link>
```

Trailing-slash-aware data endpoints first used
`future.unstable_trailingSlashAwareDataRequests` in 7.12.0 and
`future.v8_trailingSlashAwareDataRequests` in 7.16.0; the older spelling then became
a config error. The behavior is unconditional in 8.0.0. A browser path `/a/b/c/`
changes its data endpoint from `/a/b/c.data` to `/a/b/c/_.data`; root changes from
`/_root.data` to `/_.data`. Update caches and URL-sensitive infrastructure.

Raw request pass-through similarly moved from `future.unstable_passThroughRequests`
in 7.13.2 to `future.v8_passThroughRequests` in 7.15.0, then became unconditional
in v8. Loaders, actions, and middleware receive the raw implementation URL in
`request`; use their normalized `url` argument for routing logic.

## Config-name migration map

The 7.15.0 stable spellings replaced these provisional names:

| Old | Stable |
| --- | --- |
| `future.unstable_passThroughRequests` | `future.v8_passThroughRequests` |
| `future.unstable_subResourceIntegrity` | top-level `subResourceIntegrity` |
| `prerender.unstable_concurrency` | `prerender.concurrency` |
| `unstable_url` | `url` |
| `unstable_instrumentations` | `instrumentations` |
| `unstable_pattern` | `pattern` |
| `unstable_defaultShouldRevalidate` | `defaultShouldRevalidate` |
| `unstable_useTransitions` | `useTransitions` |
| `unstable_mask` | `mask` |
| `unstable_normalizePath` | `normalizePath` |

Earlier, 7.10.0 renamed `future.unstable_viteEnvironmentApi` and
`future.unstable_splitRouteModules` to `future.v8_viteEnvironmentApi` and
`future.v8_splitRouteModules`. In 8.0.0, Vite Environment API, pass-through
requests, middleware, and trailing-slash behavior became unconditional; splitting
moved top-level. Remove adopted flags rather than carrying them forward.

The 7.16.0 development tooling warns about all approaching v8 behaviors:
`v8_middleware`, `v8_splitRouteModules`, `v8_viteEnvironmentApi`,
`v8_passThroughRequests`, and `v8_trailingSlashAwareDataRequests`.
