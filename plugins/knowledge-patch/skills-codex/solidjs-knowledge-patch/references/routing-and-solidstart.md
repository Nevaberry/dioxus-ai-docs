# Routing and SolidStart

## Filesystem routes

### Supply the application router

In `solidstart-1.0.0`, `FileRoutes` exposes the generated filesystem-route
configuration as both a component and a regular function. The application can
therefore supply and configure its own router:

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

Use the regular function form when the selected router needs direct access to
the generated route configuration.

### Shape the tree without changing the URL

Parenthesized filename parts do not participate in URL matching, but they
still shape the route tree. Use them for route groups, named index routes, and
intentional breaks from normal nesting.

Double brackets make a filesystem parameter optional. A bracketed ellipsis
captures any number of segments as one slash-delimited string:

```text
routes/users/[[id]].tsx    # /users or /users/123
routes/blog/[...post].tsx  # /blog/a/b; params.post === "a/b"
```

### Configure route modules

A route module may export `route` for router-specific configuration such as
loaders and parameter filters:

```tsx
import type { RouteDefinition } from "@solidjs/router";

export const route = {
  matchFilters: { id: /^\d+$/ },
} satisfies RouteDefinition;

export default function Story() {
  return <main>Story</main>;
}
```

SolidStart lazy-wraps the default export and supplies it as `component`; do
not duplicate `component` in the `route` object.

## Router descriptions and loading

### Apply current preload names

The route option formerly called `load` is now `preload`. The router also
exports `usePreloadRoute`, and `preloadRoute` accepts a string path.

The public `Route` type was renamed to `RouteDescription`, and the types used
by the public API are exported. `rootLoad` was added; both `root` and
`rootLoad` now sit outside route matching.

### Use navigation helpers with their narrowed result

Solid Router supports URL rewriting. When `useHref` receives a string
parameter, its result is a string.

The router package also re-exports its context and supports Vite 6.

## Request APIs

### Answer CORS preflight requests

Since SolidStart 1.1, a filesystem API route can export `OPTIONS` directly:

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

### Type request-local state

Since SolidStart 1.1, `RequestEventLocals` belongs to the global `App`
namespace. Augment it in application code:

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

### Import server-function metadata from the public entry point

Import `getServerFunctionMeta` from `@solidjs/start`:

```ts
import { getServerFunctionMeta } from "@solidjs/start";
```

The previous `@solidjs/start/server` export remains temporarily but is
deprecated.

## Runtime and configuration

### Track the de-Vinxi transition

The SolidStart 2 alpha line replaced Vinxi with a pure Vite-based system and
targeted feature parity with 1.x. Its published roadmap placed Solid 2 support
at beta, reserved stable for hardening, kept continued v1 work on the `1.x`
branch, and planned Nitro 3 integration before stable.

The stable 2.0.0 line is built directly on Vite's Environment API. It remains
on Solid 1 and uses a Vite 8 and Rolldown foundation with direct deployment
plugin integration.

### Preview with the active runtime

The alpha runtime supports `vite preview`, server-side type exports from
`@solidjs/start/server`, and API routes under the configured base URL. It also
preserves multiple `Set-Cookie` headers on redirect responses.

As of 2.0.1, `vite preview` delegates to Nitro whenever Nitro's preview plugin
is active. This also applies to static builds that intentionally have no
server entry.

### Configure public assets

Since SolidStart 1.2, the public-assets directory is configurable instead of
being fixed to `public`.
