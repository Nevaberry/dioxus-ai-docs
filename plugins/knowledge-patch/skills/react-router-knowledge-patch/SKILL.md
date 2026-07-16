---
name: react-router-knowledge-patch
description: React Router 8.2.0 compatibility. Use for React Router work.
license: MIT
version: 8.2.0
metadata:
  author: Nevaberry
---

# React Router Knowledge Patch

Use this skill before changing React Router applications, route modules, adapters,
framework configuration, data APIs, middleware, generated types, or migrations.
Determine the installed major and mode first: Framework, Data, Declarative, or RSC.
Several names and defaults differ by major, and provisional names were stabilized in
multiple steps.

## Reference index

| Reference | Topics |
| --- | --- |
| [Data loading and rendering](references/data-loading-and-rendering.md) | Single Fetch, loaders/actions, hydration, revalidation, fetchers, navigation, prerendering |
| [Framework routing and configuration](references/framework-routing-and-config.md) | Route config, discovery, splitting, SPA/SSR, server bundles, paths, masks |
| [Middleware and context](references/middleware-and-context.md) | Context providers, server/client middleware, `next()`, errors, request scope |
| [Migration, packages, and tooling](references/migration-and-tooling.md) | Package imports, runtime floors, Vite, adapters, removed APIs, scaffolding, major upgrades |
| [React Server Components](references/rsc.md) | Data Mode and Framework Mode RSC APIs, exports, rendering, entrypoints |
| [Security, observability, and CSP](references/security-observability-and-csp.md) | Action origins, patched vulnerabilities, nonces, SRI, error reporting, instrumentation |
| [Type safety and APIs](references/type-safety-and-apis.md) | Typegen, `href`, route props, serialization, meta/matches, public API details |

## Working method

1. Inspect `package.json`, the lockfile, and imports to identify the installed major.
2. Identify the routing mode and whether the app uses the framework Vite plugin.
3. Read the migration reference before changing imports, flags, runtime versions, or adapters.
4. Read only the topical references needed for the task.
5. Prefer stable spellings supported by the installed version; do not copy provisional names blindly.
6. Run route type generation before standalone TypeScript checks.
7. Test document requests, client navigations, submissions, and hydration separately when relevant.

## Breaking changes first

### Choose imports by major

For current major projects, import shared APIs such as `Link`, `redirect`, cookie helpers,
and hooks from `react-router`. Import DOM renderers from `react-router/dom`.

```ts
import { Link, redirect } from "react-router";
import { HydratedRouter, RouterProvider } from "react-router/dom";
```

The compatibility `react-router-dom` package is absent in v8. During v7 migration it is
only a re-export shim. Runtime-neutral APIs do not belong in adapter packages.

### Respect runtime and module floors

Before upgrading a major, verify Node, React, Vite, ESM, and output-target requirements.
The current major requires Node 22.22.0 or newer, React 19.2.7 or newer, Vite 7 or
newer, ESM packages, and an ES2022 target. Adapter peer floors may be narrower.

### Remove obsolete response and deferred helpers

Do not use removed `json()`, `defer()`, deferred-data symbols, or the removed multipart
upload helpers. Return serializable values and promises directly; use `Response.json()`
only when an actual response is needed. Loaders and actions may return `undefined`.

```ts
export function loader() {
  return { report: loadReport() };
}
```

### Replace flags with current config

Do not retain old `v7_*`, `v3_*`, `unstable_*`, or adopted `v8_*` flags without checking
the installed major. In v8, middleware, pass-through requests, trailing-slash-aware data
requests, and the Vite Environment API are unconditional. Route splitting is top-level.

```ts
export default {
  splitRouteModules: true,
  subResourceIntegrity: true,
};
```

Use `false` for one chunk per route module or `"enforce"` to require splittability.

### Use provider-based context

Middleware context is a typed `RouterContextProvider`, not an arbitrary object or `Map`.
Custom `getLoadContext` functions must return a provider where middleware is enabled;
that is unconditional in v8.

```ts
import { createContext, RouterContextProvider } from "react-router";

const userContext = createContext<User>();
const context = new RouterContextProvider();
context.set(userContext, user);
```

### Use `loaderData`, not match `data`

The old match-level `data` fields were deprecated and then removed. Read `loaderData`
from meta arguments, route component matches, and `UIMatch`, guarding it where an error
boundary can render without completed loader data.

### Treat route modules as split units

Framework route modules are automatically split. Shared local declarations referenced by
multiple exports can prevent isolation; move them to another module. Root routes are the
exception when enforced splitting is used because the root stays one chunk.

## Framework quick reference

### Configure routes explicitly

Export a `RouteConfig` from `app/routes.ts`. Use `index`, `route`, `layout`, and `prefix`
from `@react-router/dev/routes`; spread the routes returned by `prefix`.

```ts
import { index, layout, prefix, route, type RouteConfig } from "@react-router/dev/routes";

export default [
  index("./home.tsx"),
  layout("./auth/layout.tsx", [route("login", "./auth/login.tsx")]),
  ...prefix("products", [route(":id", "./product.tsx")]),
] satisfies RouteConfig;
```

Use `flatRoutes()` only when file-route discovery is desired. Route ID `root` is reserved.

### Wire generated types

Generated sibling modules live under `.react-router/types`; include that tree and configure
TypeScript `rootDirs`. Import `Route` from each route's `./+types/<route>` module.

```tsx
import type { Route } from "./+types/product";

export async function loader({ params }: Route.LoaderArgs) {
  return { id: params.id };
}

export default function Product({ loaderData }: Route.ComponentProps) {
  return <h1>{loaderData.id}</h1>;
}
```

Run `react-router typegen && tsc` in CI and standalone checks.

### Combine server and client data deliberately

Under SSR, `loader` supplies server or prerender data and `clientLoader` handles later
navigations. Call `serverLoader()` to combine them. Set `clientLoader.hydrate = true as const`
when it must run before hydration and provide `HydrateFallback` when the UI should wait.

Client-only loaders hydrate implicitly. If a hydrating client loader has no fallback, its
first value must match server-rendered data to avoid a hydration mismatch.

### Understand prerender and SPA output

Use `prerender: true` for all static routes or provide paths/callbacks for dynamic ones.
Parameterized routes need explicit values. With `ssr: false`, including `/` changes which
file is the generic fallback; inspect generated `index.html` and `__spa-fallback.html`.

### Await router work

Navigation, submission, fetcher load/submit, and revalidation APIs expose completion
promises. POP navigations can also be awaited.

```ts
await navigate(-1);
await fetcher.submit(formData, { method: "post" });
```

## Middleware quick reference

Route `middleware` wraps server document/data work; `clientMiddleware` wraps browser work.
A middleware may call `next()` at most once. Omitting it automatically continues, which is
useful for pre-handler setup. A middleware that short-circuits may return `Response` or `data()`.

Do not assume server middleware runs on every hydrated navigation: without a loader or action,
no `.data` request is made. Add a loader returning `null` when the server middleware must run.

Do not expect server context to survive an SPA submission's POST-to-GET boundary. Each HTTP
request receives a separate provider. Client middleware work can share one client context.

## Security quick reference

Cross-origin UI-route actions are rejected by default. Configure only trusted
`allowedActionOrigins`; `**` allows every domain. With reverse proxies, validate the host
on the adapter-constructed request because that host drives origin checks.

Pass a CSP nonce through `ServerRouter`, `Links`, `PrefetchPageLinks`, and `Scripts` as needed.
Generated critical CSS, import maps, scripts, and module-preload links can inherit or receive it.

Use stable `onError` on `RouterProvider` or `HydratedRouter` for client reporting. Group telemetry
by normalized `url` and route `pattern`, not by concrete URLs alone, and consult the observability
reference before implementing instrumentations.

## RSC caution

RSC support spans distinct Data Mode and Framework Mode APIs and remains provisional in several
surfaces. Confirm entry-point placement and route export semantics before adopting it. In Framework
Mode, client exports and `Server*` exports are explicitly independent; a `ServerComponent` does not
implicitly make the error boundary, layout, or hydrate fallback server components.

## Verification checklist

- Confirm imports resolve from the intended package entry points.
- Confirm config keys match the installed major and no removed flag remains.
- Regenerate route types and run TypeScript with the generated tree included.
- Exercise direct document loads, client navigation, actions, fetchers, and back/forward navigation.
- Exercise hydration and SPA fallback paths when SSR or prerender settings change.
- Exercise middleware both before and after `next()`, including error boundaries.
- Exercise mutation requests behind the production proxy or adapter.
- Verify CSP output in rendered HTML when nonces or SRI are enabled.
- Treat provisional RSC and router-state APIs as version-sensitive.
