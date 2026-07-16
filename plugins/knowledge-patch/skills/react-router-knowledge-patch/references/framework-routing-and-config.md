# Framework Routing and Configuration

## Contents

- [Route configuration](#route-configuration)
- [Route discovery and patching](#route-discovery-and-patching)
- [Route-module splitting and lazy route code](#route-module-splitting-and-lazy-route-code)
- [Prerendering and static output](#prerendering-and-static-output)
- [Framework request behavior](#framework-request-behavior)
- [URL presentation and path generation](#url-presentation-and-path-generation)
- [Multiple server bundles](#multiple-server-bundles)

## Route configuration

### Explicit route trees

Framework routes are exported from `app/routes.ts` as `RouteConfig`. Use helpers from
`@react-router/dev/routes`:

```ts
import { index, route, type RouteConfig } from "@react-router/dev/routes";

export default [
  index("./home.tsx"),
  route("products/:id", "./product.tsx"),
] satisfies RouteConfig;
```

`layout(module, children)` adds a route module and outlet nesting without adding a URL
segment. `prefix(path, children)` adds a URL prefix without adding a route to the tree and
returns an array that must be spread.

```ts
import { layout, prefix, route, type RouteConfig } from "@react-router/dev/routes";

export default [
  layout("./auth/layout.tsx", [route("login", "./auth/login.tsx")]),
  ...prefix("projects", [route(":id", "./projects/project.tsx")]),
] satisfies RouteConfig;
```

The route ID `root` is reserved for the actual root route and is rejected on any other route.
The `relative(directory)` helper creates route helpers whose module paths resolve relative to
that directory, which lets route config be split across files without manually rebasing paths.

### File-route compatibility

Use `flatRoutes()` from `@react-router/fs-routes` for Remix-style discovery. It defaults to
`app/routes`; `rootDirectory` selects another directory relative to `app`, and
`ignoredRouteFiles` excludes matching modules.

```ts
import { flatRoutes } from "@react-router/fs-routes";
import type { RouteConfig } from "@react-router/dev/routes";

export default flatRoutes({
  rootDirectory: "file-routes",
  ignoredRouteFiles: ["home.tsx"],
}) satisfies RouteConfig;
```

Bridge a custom Remix route callback with `@react-router/remix-config-routes-adapter`. The
adapter exports both `DefineRoutesFunction` and the per-route `DefineRouteFunction` type.

## Route discovery and patching

Framework Mode defaults to a lazy route manifest served at `/__manifest`. Configure another
path for servers hosting multiple apps, or use `mode: "initial"` to put every route in the
initial manifest and avoid discovery requests.

```ts
export default {
  routeDiscovery: {
    mode: "lazy",
    manifestPath: "/my-app/__manifest",
  },
};
```

In lazy mode, the first manifest contains only initially matched routes. Rendered links are
batched into one manifest request so their routes can be patched before navigation. A click
that wins the race still succeeds after discovery, and a route is discovered only once per
session.

Framework Mode detects route-manifest skew after a deployment. Navigating to a stale,
undiscovered route reloads the destination path; a fetcher request reloads the current path.

Custom `patchRoutesOnNavigation` callbacks receive `fetcherKey` to identify a fetcher-driven
patch. For those calls, `path` excludes the search string.

```ts
createBrowserRouter(routes, {
  patchRoutesOnNavigation({ fetcherKey, path, patch }) {
    // Discover and patch `path`; associate work with `fetcherKey` if present.
  },
});
```

## Route-module splitting and lazy route code

Framework Mode automatically splits route modules. In v7, the behavior progressed through
`future.unstable_splitRouteModules` and `future.v8_splitRouteModules`; in v8 it is configured
with top-level `splitRouteModules`, defaulting to `true`.

```ts
export default {
  splitRouteModules: "enforce",
};
```

Use `false` for one chunk per module. With `"enforce"`, the root route may still combine
splittable and unsplittable exports because it is always emitted as one chunk.

A declaration shared by two exports inside one route module prevents those exports from being
isolated. The app can build as one chunk, but enforced splitting fails. Move shared declarations
to another module so each generated chunk imports them.

```tsx
// shared.ts
export const shared = () => "hello";

// route.tsx
import { shared } from "./shared";
export async function clientLoader() { return { message: shared() }; }
export default function Component() { return <p>{shared()}</p>; }
```

Since 7.5.0, Data Mode `route.lazy` can use the faster, granular object form whose properties
import independently:

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

The short-lived `route.unstable_lazyMiddleware` migration is obsolete. It replaced middleware
returned from function-form `route.lazy` in 7.4.1, then was removed in favor of
`route.lazy.unstable_middleware` in the per-property object API. Stable middleware uses the
current route middleware surface described in the middleware reference.

## Prerendering and static output

The framework plugin's `prerender` callback can combine statically known paths with application
paths and emits `.html` and `.data`; resource routes can be prerendered too.

```ts
reactRouter({
  async prerender({ getStaticPaths }) {
    return [...getStaticPaths(), "/products/hat"];
  },
});
```

Set `prerender: true` to discover and build all static paths from `routes.ts`. Parameterized
routes are omitted because their values must be supplied explicitly. `prerender.concurrency`
controls parallel work; it was originally called `prerender.unstable_concurrency`.

`@react-router/serve` serves generated `.data` as `text/x-turbo`. Prerendered files outside the
asset directory receive no explicit cache policy.

When `ssr: false`, omitting `/` from a path list leaves `index.html` as a generic SPA fallback.
Including `/` makes `index.html` root-specific and emits `__spa-fallback.html` for other
non-prerendered application paths.

```ts
export default {
  ssr: false,
  prerender: ["/", "/blog/post"],
};
```

In SPA Mode, a root `loader` can run at build time. Without explicit prerender paths, only the
root may have a loader. Configured paths may use all matched loaders. `headers` and `action`
remain invalid, and dynamic fallback paths need `clientLoader` rather than later server-loader
revalidation. `Route.HydrateFallbackProps.loaderData` is optional while child routes load.

## Framework request behavior

With SSR, Framework Mode revalidates route loaders after every navigation and form submission;
Data Mode does not. Define route-level `shouldRevalidate` to opt out. SPA Mode has no navigation
server loaders and therefore behaves like Data Mode.

Pass-through request behavior exposes the raw incoming `request` to loaders, actions, and
middleware while a sibling `url` provides the normalized routing URL. It began as
`future.unstable_passThroughRequests` with `unstable_url`, then became
`future.v8_passThroughRequests` with `url`, and is unconditional in v8.
Before opting into pass-through requests, both `request.url` and the sibling URL represented the
same normalized routing location. Opting in stops the router from replacing the request URL to
hide `.data`, `index`, and `_routes` implementation details; the sibling `url: URL` remains the
right value for routing logic.

```ts
export function loader({ request, url }: Route.LoaderArgs) {
  return {
    rawPath: new URL(request.url).pathname,
    routePath: url.pathname,
  };
}
```

Trailing-slash-aware data requests preserve `/a/b/c/` for middleware and handlers and map it to
`/a/b/c/_.data` instead of `/a/b/c.data`; the root endpoint is `/_.data` rather than
`/_root.data`. The flag spelling
moved from `future.unstable_trailingSlashAwareDataRequests` to
`future.v8_trailingSlashAwareDataRequests` and the behavior is unconditional in v8. Update
caches and URL-sensitive infrastructure when adopting it. The old unstable spelling is a config
resolution error once the `v8_` spelling is available.

## URL presentation and path generation

Framework and Data Mode links can navigate to one location while displaying another using the
`mask` prop. Read the optional mask from `useLocation().mask`. Masking is SPA-only and is removed
from history state during SSR. These were originally `<Link unstable_mask>` and
`useLocation().unstable_mask` when introduced in 7.13.1.

```tsx
<Link to="/gallery?image=42" mask="/images/42">
  Open image
</Link>
```

`generatePath()` correctly handles a dynamic parameter followed by a suffix, such as
`/books/:id.json`. Typed framework `href()` supports optional static and dynamic segments,
splats, suffixed parameters, and single optional-parameter routes. See the type/API reference
for its typing and encoding rules.

## Multiple server bundles

`serverBundles` receives each matched branch and returns a bundle ID, which becomes the
directory name under the server build directory.

```ts
import type { Config } from "@react-router/dev/config";

export default {
  serverBundles: ({ branch }) =>
    branch.some((route) => route.id === "admin") ? "admin" : "main",
} satisfies Config;
```

Prerendering multiple server bundles is supported when the v7 Vite Environment API behavior is
enabled and follows the mandatory environment API in v8.
