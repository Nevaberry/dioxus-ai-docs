# Routing and SolidStart

## Router-neutral generated routes

`FileRoutes` exposes SolidStart's filesystem-route configuration as both a
component and a regular function (solidstart-1.0.0). The component form lets an
application choose and configure its own router:

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

Use the regular function form when a router needs the generated configuration
directly rather than as JSX.

## Route-tree and filename rules

Parenthesized filename parts do not participate in URL matching, but they still
shape the route tree. Use them for route groups, named index routes, or an
intentional break from normal filesystem nesting.

Optional and catch-all parameters use distinct forms:

```text
routes/users/[[id]].tsx    # /users or /users/123
routes/blog/[...post].tsx  # /blog/a/b; params.post === "a/b"
```

`[[name]]` makes a parameter optional. `[...name]` captures any number of
segments as one slash-delimited string rather than an array.

## Route-module configuration

A route module can export `route` with router-specific configuration such as a
loader or parameter filter:

```tsx
import type { RouteDefinition } from "@solidjs/router";

export const route = {
  matchFilters: { id: /^\d+$/ },
} satisfies RouteDefinition;

export default function Story() {
  return <main>Story</main>;
}
```

SolidStart lazy-wraps the default export and supplies it as the route
configuration's `component`. Do not duplicate `component` in the named
`route` export.

## Route preloading and descriptions

The route option previously named `load` is now `preload`. The router exports
`usePreloadRoute`, and `preloadRoute` accepts a string path. Update the option
name, imports, and call sites together so route discovery and imperative
preloading agree.

The public `Route` type is now `RouteDescription`. All types used by the public
API are exported, so import the public declarations instead of copying internal
shapes.

`rootLoad` was added, and `root` plus `rootLoad` moved outside route matching.
Do not rely on either root setting to participate in the matching algorithm.

## Parameters, hrefs, and URL rewriting

`SearchParams` is a public exported type. Its values may be optional and may be
arrays; `Params` values may also be optional. Preserve those possibilities in
application types instead of narrowing every value to a required string.

Objects returned by `useParams()` support the `in` operator. Use it when route
logic needs to distinguish a missing key from a key whose value is optional.

The router supports URL rewriting. `useHref` returns a string when it receives
a string parameter, so string-based helpers can preserve a string-to-string
contract without an extra coercion.

## Router package integration

The router package re-exports its context and supports Vite 6. Prefer the public
context export rather than reaching into an internal module path.

## SolidStart runtime lineage

The 2.0 alpha line began the move from Vinxi to a pure Vite-based system and
targeted feature parity with 1.x. During that staging plan, beta was the
milestone for Solid 2 support, stable was reserved for hardening, continued v1
work lived on the `1.x` branch, and Nitro 3 integration was planned before the
stable release.

Stable SolidStart 2 is the Solid 1 line built directly on Vite's Environment API
with a Vite 8 and Rolldown foundation and direct deployment-plugin integration
(since 2.0.0). Treat earlier alpha notes as migration history, not evidence that
the installed stable runtime still uses Vinxi.

## Preview and server runtime

SolidStart 2 supports `vite preview`:

```sh
vite preview
```

As of 2.0.1, that command delegates to Nitro when Nitro's preview plugin is
active. Delegation also applies to static builds that intentionally have no
server entry.

Server-side types are exported from `@solidjs/start/server`. API routes honor
the configured base URL. Redirect responses preserve multiple `Set-Cookie`
headers rather than dropping all but one.

## API route `OPTIONS` handlers

Since SolidStart 1.1, a filesystem API route can export `OPTIONS` and answer a
CORS preflight directly:

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

Return the status and access-control headers required by the endpoint; do not
assume another server layer will synthesize the preflight response.

## Request-local application types

Since SolidStart 1.1, request locals are typed through
`App.RequestEventLocals`:

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

Augment the global interface in application code so middleware and handlers
share the same local-state contract.

## Server-function metadata

Import `getServerFunctionMeta` from the package root:

```ts
import { getServerFunctionMeta } from "@solidjs/start";
```

The former export from `@solidjs/start/server` is temporarily retained but
deprecated. Change the import without moving unrelated server-only type
imports that still belong in the server entry point.

## Public assets

Since SolidStart 1.2, the public-assets directory is configurable rather than
fixed to `public`. Set it explicitly when the project's static assets live
elsewhere and keep deployment-plugin configuration aligned with that path.
