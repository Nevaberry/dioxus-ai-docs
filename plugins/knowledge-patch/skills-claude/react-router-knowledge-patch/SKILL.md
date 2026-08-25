---
name: react-router-knowledge-patch
description: React Router
version: 8.2.0
license: MIT
metadata:
  author: Nevaberry
---


# React Router Knowledge Patch

Use this skill before changing React Router applications, route modules, adapters,
framework configuration, data APIs, middleware, generated types, or migrations.
Determine the installed major and routing mode first: Framework, Data, Declarative,
or RSC. Names, defaults, runtime floors, and entry points differ by major.

## Reference index

| Reference | Topics |
| --- | --- |
| [Data loading and rendering](references/data-loading-and-rendering.md) | Loaders, actions, hydration, Single Fetch, fetchers, revalidation, navigation |
| [Framework routing and configuration](references/framework-routing-and-config.md) | Route config, discovery, splitting, SPA/SSR, prerendering, server bundles, masks |
| [Middleware and context](references/middleware-and-context.md) | Context providers, server/client middleware, `next()`, errors, request scope |
| [Migration, packages, and tooling](references/migration-and-tooling.md) | Imports, runtime floors, Vite, adapters, removed APIs, scaffolding, upgrades |
| [React Server Components](references/rsc.md) | Data and Framework Mode RSC APIs, exports, responses, entrypoints |
| [Security, observability, and CSP](references/security-observability-and-csp.md) | Action origins, patched vulnerabilities, nonces, SRI, reporting, instrumentation |
| [Type safety and APIs](references/type-safety-and-apis.md) | Typegen, `href`, route props, serialization, meta/matches, public types |

## Working method

1. Inspect `package.json`, the lockfile, and imports to identify the installed major.
2. Identify the routing mode and whether the framework Vite plugin is active.
3. Read the migration reference before changing imports, flags, runtime versions,
   adapters, or custom server entry points.
4. Read the topical references for the subsystem being changed.
5. Prefer the stable spelling supported by the installed version; several APIs
   passed through provisional names before stabilizing.
6. Run route type generation before standalone TypeScript checks.
7. Test document requests, browser navigations, submissions, and hydration as
   distinct paths when the change can affect them.

## Breaking changes first

### Choose imports by major

For current-major projects, import shared APIs such as `Link`, `redirect`, cookie
helpers, and hooks from `react-router`. Import DOM renderers from
`react-router/dom`.

```ts
import { Link, redirect } from "react-router";
import { HydratedRouter, RouterProvider } from "react-router/dom";
```

The v7 `react-router-dom` compatibility shim is absent in v8. Runtime-neutral APIs
do not belong in adapter packages.

### Respect runtime and module floors

Before a major upgrade, verify Node, React, Vite, ESM, and output-target
requirements. The current major requires Node 22.22.0 or newer, React 19.2.7 or
newer, Vite 7 or newer, ESM packages, and an ES2022 target.

### Remove obsolete response and deferred helpers

Do not use removed `json()`, `defer()`, deferred-data symbols, or removed multipart
upload helpers. Return serializable values and promises directly; use
`Response.json()` only when an actual response is needed. Loaders and actions may
return `undefined`.

```ts
export function loader() {
  return { report: loadReport() };
}
```

### Replace flags with current config

Do not retain v6 `v7_*`, Remix `v3_*`, old `unstable_*`, or adopted `v8_*` flags
without checking the installed major. In v8, middleware, raw pass-through requests,
trailing-slash-aware data requests, and the Vite Environment API are unconditional.
Route splitting is top-level and defaults on.

```ts
export default {
  splitRouteModules: true,
  subResourceIntegrity: true,
};
```

Use `splitRouteModules: false` for one chunk per route module or `"enforce"` to
require splittability. Stable names include `instrumentations`, `pattern`, `url`,
`mask`, `normalizePath`, `defaultShouldRevalidate`, and `useTransitions`.

### Use provider-based context

Middleware context is a typed `RouterContextProvider`, not an arbitrary object or
`Map`. In v8, custom `getLoadContext` functions must always return a provider.

```ts
import { createContext, RouterContextProvider } from "react-router";

const userContext = createContext<User>();
const context = new RouterContextProvider();
context.set(userContext, user);
```

The provider is request-scoped on the server. Do not expect it to persist across an
SPA submission's POST and subsequent GET.

### Use `loaderData`, not match `data`

The old match-level `data` fields are removed. Read `loaderData` from meta arguments,
route component matches, and `UIMatch`. Guard it where an error boundary can render
without a completed loader.

### Treat route modules as split units

Framework route modules split automatically. A declaration shared by multiple
exports inside one route can prevent isolation; move it to another module. The root
route may remain a single chunk even when enforced splitting is enabled.

## Framework quick reference

### Configure routes explicitly

Export a `RouteConfig` from `app/routes.ts`. Use `index`, `route`, `layout`, and
`prefix` from `@react-router/dev/routes`; spread the routes returned by `prefix`.

```ts
import { index, layout, prefix, route, type RouteConfig } from "@react-router/dev/routes";

export default [
  index("./home.tsx"),
  layout("./auth/layout.tsx", [route("login", "./auth/login.tsx")]),
  ...prefix("products", [route(":id", "./product.tsx")]),
] satisfies RouteConfig;
```

Use `flatRoutes()` only when file-route discovery is desired. Route ID `root` is
reserved.

### Wire generated types

Generated sibling modules live under `.react-router/types`; include that tree and
configure TypeScript `rootDirs`. Import `Route` from each route's
`./+types/<route>` module.

```tsx
import type { Route } from "./+types/product";

export async function loader({ params }: Route.LoaderArgs) {
  return { id: params.id };
}

export default function Product({ loaderData }: Route.ComponentProps) {
  return <h1>{loaderData.id}</h1>;
}
```

Run `react-router typegen && tsc` in CI and standalone checks. A fetcher generic is
the producing function type, for example `useFetcher<typeof loader>()`.

### Combine server and client data deliberately

Under SSR, `loader` supplies server or prerender data and `clientLoader` handles
later browser navigations. Call `serverLoader()` to combine them. Set
`clientLoader.hydrate = true as const` when it must run before hydration and export
`HydrateFallback` when the UI should wait.

Client-only loaders hydrate implicitly. If a hydrating client loader has no fallback,
its first value must match server-rendered data to avoid a hydration mismatch. A
`clientAction` can wrap the server mutation through `serverAction()`.

### Understand prerender and SPA output

Use `prerender: true` for every static route or provide paths/a callback for selected
routes. Parameterized routes need explicit values. With `ssr: false`, including `/`
changes which file is the generic fallback; inspect generated `index.html` and
`__spa-fallback.html`. SPA fallback paths require `clientLoader` rather than later
server-loader revalidation.

### Await router work

Navigation, submission, fetcher load/submit, and revalidation APIs expose completion
promises. POP navigations can also be awaited.

```ts
await navigate(-1);
await fetcher.submit(formData, { method: "post" });
```

Use `fetcher.reset()` to return a fetcher to its initial idle state. Prefer
`shouldCallHandler()` and `shouldRevalidateArgs` in custom `dataStrategy`
implementations; `shouldLoad` is deprecated.

## Middleware quick reference

Route `middleware` wraps server document/data work; `clientMiddleware` wraps browser
work. A middleware may call `next()` at most once. Omitting it automatically
continues, which is useful for pre-handler setup. A server middleware that
short-circuits may return `Response` or `data()`.

Do not assume server middleware runs on every hydrated navigation: without a loader
or action, no `.data` request is made. Add a loader returning `null` when the server
middleware must run. Client middleware can run even without loaders.

Errors after `next()` retain loader progress; errors before it may force selection of
a higher error boundary whose loader data is available. Do not rely on catching
downstream route errors around `next()` because boundary responses flow back through
the middleware chain.

## Security and observability quick reference

Cross-origin UI-route actions are rejected by default. Configure only trusted
`allowedActionOrigins`; `**` allows every domain. With reverse proxies, validate the
host on the adapter-constructed request because that host drives origin checks.

Pass a CSP nonce through `ServerRouter`, `Links`, `PrefetchPageLinks`, and `Scripts`
as needed. Generated critical CSS, import maps, scripts, and module-preload links can
inherit or receive it. Enable top-level `subResourceIntegrity` when SRI is required.

Use stable `onError` on `RouterProvider` or `HydratedRouter` for client reporting.
Group telemetry by normalized `url` and route `pattern`, and use outer
instrumentation `result.meta` after matching completes.

## RSC caution

RSC support spans distinct Data Mode and Framework Mode APIs, with provisional
surfaces. Confirm entry-point placement and route export semantics before adoption.
In Framework Mode, client exports and `Server*` exports are independent; a
`ServerComponent` does not implicitly make the error boundary, layout, or hydrate
fallback server components.

## Verification checklist

- Confirm imports resolve from the intended package entry points.
- Confirm config keys match the installed major and no removed flag remains.
- Regenerate route types and run TypeScript with the generated tree included.
- Exercise direct document loads, client navigation, actions, fetchers, and POPs.
- Exercise hydration, prerendering, and SPA fallback paths when applicable.
- Exercise middleware before and after `next()`, including error boundaries.
- Exercise mutation requests behind the production proxy or adapter.
- Verify CSP output in rendered HTML when nonces or SRI are enabled.
- Treat provisional RSC and router-state APIs as version-sensitive.
