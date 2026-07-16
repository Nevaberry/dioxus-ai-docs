# Migration, Packages, and Tooling

## Contents

- [Package and import migration](#package-and-import-migration)
- [Runtime and dependency requirements](#runtime-and-dependency-requirements)
- [Framework compiler and Vite tooling](#framework-compiler-and-vite-tooling)
- [Configuration and source-file tooling](#configuration-and-source-file-tooling)
- [Scaffolding and local developer support](#scaffolding-and-local-developer-support)
- [Project direction](#project-direction)
- [Versioned batch attribution](#versioned-batch-attribution)

## Package and import migration

### Consolidated packages

In v7, `react-router-dom`, `@remix-run/react`, `@remix-run/server-runtime`,
`@remix-run/router`, and `@remix-run/testing` were consolidated into `react-router`.
`react-router-dom` remained only as a re-export shim. `react-router-native` and
`react-router-dom-v5-compat` were removed. The Cloudflare Pages and Workers packages
converged on `@react-router/cloudflare`.

Import runtime-neutral APIs from `react-router`, not from an adapter. Cookie and session
helpers such as `createCookieSessionStorage` also moved there; their low-level `*Factory`
APIs were removed. Adapter-specific APIs remain in packages such as `@react-router/node`.

```ts
import { redirect, useLoaderData } from "react-router";
import { createFileSessionStorage } from "@react-router/node";
```

In v8, the compatibility `react-router-dom` package is removed completely. Import
`RouterProvider` and `HydratedRouter` from `react-router/dom`; import other former DOM-package
APIs from `react-router`.

```ts
import { Link } from "react-router";
import { HydratedRouter, RouterProvider } from "react-router/dom";
```

Framework client entries use `HydratedRouter` from `react-router/dom`. Manual browser and
hash routers should use that entry point's `RouterProvider` to enable `ReactDOM.flushSync()`.
Memory and other non-DOM routers use `RouterProvider` from `react-router`.

### Public API replacement names

Apply these v7 replacements:

| Removed or old | Replacement |
| --- | --- |
| `createRemixStub` | `createRoutesStub` |
| `RemixContext` | `FrameworkContext` |
| `PrefetchPageDescriptor` | `PageLinkDescriptor` |
| `Action` | `NavigationType` |
| internal router type | `RemixRouter` |
| `detectErrorBoundary` | `mapRouteProperties` |
| `unstable_dataStrategy` | `dataStrategy` |
| `unstable_patchRoutesOnNavigation` | `patchRoutesOnNavigation` |

The public low-level `createBrowserHistory`, `createHashHistory`, and `createMemoryHistory`
constructors were removed in favor of `create*Router`. For migration of
`unstable_HistoryRouter` only, `UNSAFE_createBrowserHistory`, `UNSAFE_createHashHistory`, and
`UNSAFE_createMemoryHistory` are available; do not use them in new applications.

In v8, remove `hasErrorBoundary` from route objects, `<Route>` props, and lazy route
definitions. `MapRoutePropertiesFunction` need not return it because the router infers error
boundary presence.

## Runtime and dependency requirements

### Remove obsolete future flags

The former v6 `v7_*` and Remix `v3_*` flags are not optional in v7. Their behaviors for
relative splats, React transitions, fetcher persistence, form methods, partial hydration, action
revalidation, Single Fetch, lazy route discovery, abort reasons, and dependency optimization are
unconditional. Remove the corresponding flag settings rather than carrying them forward.

`<RouterProvider fallbackElement>` was removed in the same migration. Put
`hydrateFallbackElement` or `HydrateFallback` on the root route; its initial navigation remains
`idle` during partial hydration.

### v7 application floors

Framework packages initially required Node 20 and React/React DOM 18. `installGlobals()` was
removed because native Fetch and Web Crypto globals are expected. Apps pinning `isbot@3` while
using the default server entry needed `isbot@5`.

The Express adapter accepts Express 5. In v8 its Express 4 peer range starts at 4.22.2 and
continues to accept Express 5; `@react-router/serve` uses Express 5.2.1.

### v8 application floors

React Router v8 requires Node 22.22.0+, React 19.2.7+, and Vite 7+. Packages are ESM-only and
target ES2022. On Maintenance LTS Node lines only the latest minor branch is supported, so a
React Router minor may raise the minimum supported Node minor.

## Framework compiler and Vite tooling

### Vite-only framework builds

The old esbuild compiler is removed. Use the renamed Vite entry points:

```ts
import { reactRouter } from "@react-router/dev/vite";
import { cloudflareDevProxy } from "@react-router/dev/vite/cloudflare"; // v7 only
```

The plugin's former `manifest` option is replaced by `buildEnd({ buildManifest })`.
`reactRouterConfig.publicPath` is removed. When Vite manifests are enabled, find them beneath
the individual build directories, for example `build/client/.vite/manifest.json`.

Tooling support was added for Vite 6 (7.1.0), Vite 7 (7.6.3), and Vite 8 (7.14.0).
The experimental Vite Environment API started behind
`future.unstable_viteEnvironmentApi`, was renamed to `future.v8_viteEnvironmentApi`, and is
unconditional in v8. The experimental spelling was not recommended for production. While that
flag existed, a plugin replacing the SSR
environment, such as `@cloudflare/vite-plugin`, could appear before or after React Router's
plugin. With the v8 behavior enabled, the dev tool can prerender multiple server bundles.

In v8, `@react-router/dev/vite/cloudflare` is removed; use `@cloudflare/vite-plugin`.
Wrangler 3 is unsupported. Earlier v7 tooling accepted Wrangler 4 as an optional peer.

### Preview and server entry behavior

Framework production builds can be served with `vite preview`. In v8, preview-server
prerendering is the only implementation; remove `future.unstable_previewServerPrerendering`.

As of 8.2.0, apps without a custom `entry.server.tsx` default to
`renderToReadableStream` unless they depend on `@react-router/node`, `@react-router/express`, or
`@react-router/serve`; those Node adapters retain `renderToPipeableStream`. A Node app without
a custom entry can opt into Web Streams with:

```ts
import type { Config } from "@react-router/dev/config";

export default {
  future: { unstable_enableNodeReadableStream: true },
} satisfies Config;
```

The obsolete `abortDelay` prop on `ServerRouter` was removed with deferred data. Export the
Single Fetch timeout from `entry.server` instead:

```ts
export const streamTimeout = 10_000;
```

## Configuration and source-file tooling

`@react-router/dev` accepts route config files ending in `.ts`, `.js`, `.mts`, or `.mjs`.
It loads environment variables before evaluating `routes.ts`, so route selection can use
`VITE_`-prefixed `import.meta.env` values.

```ts
import { route, type RouteConfig } from "@react-router/dev/routes";

const routes: RouteConfig = [];
if (import.meta.env.VITE_ENV_ROUTE === "my-route") {
  routes.push(route("my-route", "routes/my-route.tsx"));
}
export default routes;
```

Framework type generation provides declarations for `virtual:react-router/server-build`.
Patch 7.4.1 made those declarations work with TypeScript `moduleDetection: "force"`.

Generated type registration under `.react-router/types` means a future/config flag can enable
its corresponding types automatically; do not add a duplicate manual `declare module
"react-router"` augmentation. In v8, the Data Mode `Future` augmentation and the middleware
gating type formerly exported as `UNSAFE_MiddlewareEnabled` are removed.

Patch 7.16 rejects the obsolete `future.unstable_trailingSlashAwareDataRequests` spelling during
config resolution. Its dev tooling warns about the approaching `v8_middleware`,
`v8_splitRouteModules`, `v8_viteEnvironmentApi`, `v8_passThroughRequests`, and
`v8_trailingSlashAwareDataRequests` defaults; resolve those warnings before a major upgrade.

## Scaffolding and local developer support

`create-react-router` detects Deno at version 2.0.5 or newer. With older Deno, select it with
`--package-manager deno`. As of 8.2.0, `@react-router/dev` and the scaffolder also recognize
the `nub` package manager.

The v8 scaffolder uses native `fetch`, so it no longer inherits implicit `HTTPS_PROXY`
support from the previous fetch implementation.

Generated projects can include the official React Router skill at
`.agents/skills/react-router`. Interactive runs default to yes, and `--yes` or non-interactive
runs include it; pass `--no-agent-skills` to omit it.

```sh
create-react-router my-app --no-agent-skills
```

The `react-router` package includes a subset of version-matched official Markdown at
`node_modules/react-router/docs`. It excludes generated API docs, community material, and
tutorials.

## Project direction

Remix 3 is a separate, ground-up modular toolkit with its own component model and no React
dependency. It is not a compatible next release or drop-in upgrade for a React-based Remix v2
application; no preview was available when this direction was announced.

## Versioned batch attribution

The version-specific details in this skill derive from batches `7.0-guide`, `7.0.0`, `7.1.0`,
`7.2.0`, `7.3.0`, `7.4.0`, `7.5.0`, `7.6.0`, `7.7.0`, `7.8.0`, `7.9.0`, `7.10.0`,
`7.11.0`, `7.12.0`, `7.13.0`, `7.14.0`, `7.15.0`, `7.16.0`, `7.17.0`, `7.18.0`,
`8.0.0`, `8.1.0`, and `8.2.0`.
