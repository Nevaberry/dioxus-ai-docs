# Routing and SolidStart

## Contents

- [Router-neutral filesystem routes](#router-neutral-filesystem-routes)
- [Route-module configuration](#route-module-configuration)
- [Filesystem parameter syntax](#filesystem-parameter-syntax)
- [Router preloading and navigation](#router-preloading-and-navigation)
- [Public route types and root loading](#public-route-types-and-root-loading)
- [SolidStart runtime migration](#solidstart-runtime-migration)
- [Server-function transport](#server-function-transport)
- [API routes and request locals](#api-routes-and-request-locals)
- [Exports, assets, and alpha runtime contracts](#exports-assets-and-alpha-runtime-contracts)

## Router-neutral filesystem routes

In the `solidstart-1.0.0` filesystem-routing contract, `FileRoutes` exposes the
generated route configuration both as a component and as a regular function.
This lets an application supply and configure its own router:

```tsx
import { FileRoutes } from "@solidjs/start/router";
import { Router } from "@solidjs/router";

export default function App() {
  return (
    <Router>
      <FileRoutes />
    </Router>
  );
}
```

Use the regular function form when direct access to the generated
configuration is needed rather than JSX composition.

Parenthesized filename parts do not participate in URL matching, but they
still shape the route tree. Use them for route groups, named index routes, and
intentional breaks from normal filesystem nesting.

## Route-module configuration

Export `route` from a route module to supply router-specific configuration,
including loaders and parameter filters:

```tsx
import type { RouteDefinition } from "@solidjs/router";

export const route = {
  matchFilters: { id: /^\d+$/ },
} satisfies RouteDefinition;

export default function Story() {
  return <main>Story</main>;
}
```

SolidStart lazy-wraps the default component and supplies it as the route
configuration's `component`. Do not repeat `component` in the `route` object.

## Filesystem parameter syntax

Use double brackets for an optional route parameter and a bracketed ellipsis
for a catch-all:

```text
routes/users/[[id]].tsx    # /users or /users/123
routes/blog/[...post].tsx  # /blog/a/b; params.post === "a/b"
```

The catch-all value is one slash-delimited parameter string and may represent
any number of URL segments.

## Router preloading and navigation

Apply the current preloading names and inputs:

- Rename the route option `load` to `preload`.
- Import `usePreloadRoute` when a component needs the preloading helper.
- Pass a string path to `preloadRoute` when a path string is available.

The router also supports URL rewriting. When `useHref` receives a string
parameter, expect a string result rather than a different route object shape.

## Public route types and root loading

Use `RouteDescription` in place of the former public `Route` type. All types
used by the public API are exported, so prefer those exports over reconstructing
internal shapes.

Use `rootLoad` for root-level data loading. Both `root` and `rootLoad` live
outside route matching, so do not place their behavior inside a matched route
branch.

The router package re-exports its context and supports Vite 6. Prefer the
package export rather than reaching into an internal context module.

Parameter-related public types have also widened:

- Import `SearchParams` as an exported type.
- Allow `SearchParams` values to be optional and to contain arrays.
- Allow `Params` values to be optional.
- Use the `in` operator with the object returned by `useParams()` when checking
  parameter presence.

## SolidStart runtime migration

The SolidStart `2.0.0-alpha` line replaces Vinxi with a pure Vite-based system
and targets feature parity with 1.x. Plan migration work with its stated
milestones in mind:

- Treat beta as the milestone for Solid 2 support.
- Treat stable as the hardening milestone.
- Keep continued v1 work on the `1.x` branch.
- Account for the planned Nitro 3 integration before 2.0 becomes stable.

Do not assume a Vinxi-specific configuration or deployment integration carries
unchanged into the Vite-based alpha runtime.

## Server-function transport

SolidStart 1.1 adopted the TanStack server-functions plugin in a
maintainer-described breaking transition. SolidStart 1.3 then moved
serialization to Seroval JSON mode.

A 1.3.0 regression could loop indefinitely after an unexpected response, such
as an S3 XML error. The regression is fixed in 1.3.2; verify the installed
release before diagnosing the upstream response as an application retry loop.

For the server-function execution and streaming model, see
[Reactivity and async](reactivity-and-async.md).

## API routes and request locals

Since 1.1, a filesystem API route can export an `OPTIONS` handler. Use it to
answer CORS preflight requests directly:

```ts
export function OPTIONS() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    },
  });
}
```

Also since 1.1, type request-event locals by augmenting
`App.RequestEventLocals` globally:

```ts
declare global {
  namespace App {
    interface RequestEventLocals {
      userId?: string;
    }
  }
}

export {};
```

## Exports, assets, and alpha runtime contracts

Import `getServerFunctionMeta` from the package root:

```ts
import { getServerFunctionMeta } from "@solidjs/start";
```

Its former `@solidjs/start/server` export remains temporarily but is
deprecated.

Since 1.2, configure the public-assets directory when assets do not live in the
default `public` directory.

The SolidStart 2 alpha runtime additionally:

- Supports `vite preview`.
- Exports server-side types from `@solidjs/start/server`.
- Makes API routes honor the configured base URL.
- Preserves multiple `Set-Cookie` headers on redirects instead of retaining
  only one.

