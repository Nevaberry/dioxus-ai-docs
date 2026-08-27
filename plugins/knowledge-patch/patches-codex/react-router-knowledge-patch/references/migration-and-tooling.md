# Migration, Packages, and Tooling

## Package consolidation and entry points

### V7 package moves (`7.0.0`)

V7 consolidates `react-router-dom`, `@remix-run/react`,
`@remix-run/server-runtime`, `@remix-run/router`, and `@remix-run/testing` into
`react-router`. `react-router-dom` is only a v7 re-export shim. The native and v5
compatibility packages are removed. Cloudflare Pages and Workers packages converge on
`@react-router/cloudflare`; import runtime-neutral APIs from `react-router`, not adapters.

```ts
import { redirect, useLoaderData } from "react-router";
import { createFileSessionStorage } from "@react-router/node";
```

Browser/hash framework renderers use `HydratedRouter` or `RouterProvider` from
`react-router/dom`, which enables `ReactDOM.flushSync()`. Memory/non-DOM routers import
`RouterProvider` from `react-router`.

### V8 removes the compatibility package (`8.0.0`)

`react-router-dom` no longer exists. Import DOM renderers from `react-router/dom` and all
other former DOM-package APIs from `react-router`.

```ts
import { Link } from "react-router";
import { HydratedRouter, RouterProvider } from "react-router/dom";
```

## Runtime, modules, and sessions

### V7 floors and native globals (`7.0.0`)

Framework packages require Node 20 and React/React DOM 18. `installGlobals()` is removed
because native Fetch and Web Crypto globals are expected. Cookie/session APIs including
`createCookieSessionStorage` come from `react-router`; low-level `*Factory` variants are
removed. A project pinned to `isbot@3` and using the default server entry must move to
`isbot@5`.

### V8 floors and output (`8.0.0`)

V8 requires Node 22.22.0+, React 19.2.7+, and Vite 7+, publishes ESM-only packages, and
targets ES2022. Only the newest minor on a Maintenance LTS Node line is supported, so a
React Router minor may raise the minimum Node minor.

### Server entry rendering (`8.2.0`)

Without a custom `entry.server.tsx`, Framework Mode uses `renderToReadableStream` unless
the app depends on `@react-router/node`, `@react-router/express`, or
`@react-router/serve`; those Node adapters retain `renderToPipeableStream`. A Node app
without a custom entry can opt into Web Streams:

```ts
import type { Config } from "@react-router/dev/config";

export default {
  future: { unstable_enableNodeReadableStream: true },
} satisfies Config;
```

## Removed helpers and renamed public APIs

### Data and upload removals (`7.0.0`)

`json`, `defer`, deferred-data types/symbols, `unstable_composeUploadHandlers`,
`unstable_createMemoryUploadHandler`, and `unstable_parseMultipartFormData` are removed.
Return promises and serializable data directly under Single Fetch, or call
`Response.json()` when a real response is required. Loaders/actions may return
`undefined`.

### Public-name migration (`7.0.0`)

Apply these renames:

| Old | New |
| --- | --- |
| `createRemixStub` | `createRoutesStub` |
| `RemixContext` | `FrameworkContext` |
| `PrefetchPageDescriptor` | `PageLinkDescriptor` |
| `Action` | `NavigationType` |
| internal router type | `RemixRouter` |
| `detectErrorBoundary` | `mapRouteProperties` |
| `unstable_dataStrategy` | `dataStrategy` |
| `unstable_patchRoutesOnNavigation` | `patchRoutesOnNavigation` |

Low-level `createBrowserHistory`, `createHashHistory`, and `createMemoryHistory` are
removed in favor of `create*Router` APIs. Later, `7.12.0` exposes
`UNSAFE_createBrowserHistory`, `UNSAFE_createHashHistory`, and
`UNSAFE_createMemoryHistory` only to migrate `unstable_HistoryRouter`; do not use them
for new code.

### Stream timeout (`7.1.0`)

`ServerRouter` no longer accepts the old deferred-data `abortDelay`. Export the Single
Fetch timeout from `entry.server` instead:

```ts
export const streamTimeout = 10_000;
```

### Error-boundary metadata (`8.0.0`)

Remove `hasErrorBoundary` from route objects, `<Route>`, and lazy definitions. The router
infers it, and `MapRoutePropertiesFunction` no longer needs to return it.

## Framework compiler and Vite

### Vite-only compiler (`7.0.0`)

The esbuild compiler is gone. Import `reactRouter` from `@react-router/dev/vite` and the
v7 Cloudflare proxy from `@react-router/dev/vite/cloudflare`. Replace the plugin
`manifest` option with `buildEnd({ buildManifest })`; remove
`reactRouterConfig.publicPath`. Enabled Vite manifests are written per build, for example
`build/client/.vite/manifest.json`.

```ts
import { reactRouter } from "@react-router/dev/vite";
import { cloudflareDevProxy } from "@react-router/dev/vite/cloudflare";
```

Vite support progressed through Vite 6 in `7.1.0`, Vite 7 in `7.6.0` (added by 7.6.3),
and Vite 8 in `7.14.0`. Use the version supported by the installed React Router release.

### Environment API evolution

`7.2.0` introduced `future.unstable_viteEnvironmentApi` as experimental and unsuitable
for production. Under that flag, `7.4.0` permits a plugin replacing the SSR environment,
such as `@cloudflare/vite-plugin`, before or after React Router's plugin. The flag became
`future.v8_viteEnvironmentApi` in `7.10.0`, enabled multiple-bundle prerendering in
`7.14.0`, and was removed in `8.0.0` when the behavior became mandatory.

V8 also makes preview-server prerendering the sole implementation and removes
`future.unstable_previewServerPrerendering`. Framework production builds can be exercised
with `vite preview` starting in `7.11.0`.

### Cloudflare v8 development (`8.0.0`)

The `@react-router/dev/vite/cloudflare` proxy export is removed. Use
`@cloudflare/vite-plugin`. `@react-router/dev` no longer supports Wrangler 3.

## Adapters and ecosystem compatibility

- `7.3.0`: `@react-router/express` accepts Express 5.
- `7.5.0`: the optional `@react-router/dev` peer accepts Wrangler 4.
- `7.7.0`: `create-react-router` detects Deno 2.0.5+; on older Deno, pass
  `--package-manager deno`. Route config accepts `.mts` and `.mjs`, and the Remix config
  adapter exports `DefineRouteFunction` as well as `DefineRoutesFunction`.
- `7.18.0`: `@react-router/architect` accepts `useRequestContextDomainName` so API Gateway
  request context can supply the request URL host; this is the intended v8 default when
  it matches the deployment.
- `8.0.0`: Express v4 must be at least 4.22.2; Express 5 remains accepted and
  `@react-router/serve` uses Express 5.2.1.
- `8.2.0`: development tooling and scaffolding recognize the `nub` package manager.

## Generated and local tooling

### Route configuration file and virtual-module types

Framework routes move to an explicit `app/routes.ts` `RouteConfig` in `7.0.0`.
`flatRoutes()` from `@react-router/fs-routes` retains file-route discovery, and
`@react-router/remix-config-routes-adapter` bridges Remix callbacks.

`7.4.0` adds generated declarations for `virtual:react-router/server-build`; 7.4.1 also
supports `moduleDetection: "force"`. In `7.6.0`, generated `+types/*` stops exporting
`Info`, and the provisional `react-router/route-module` entry moves to
`react-router/internal`.

### Scaffolding behavior

In `8.0.0`, `create-react-router` switches to native `fetch`, so it no longer inherits
implicit `HTTPS_PROXY` support from the old implementation.

In `8.1.0`, generated projects can include the official skill under
`.agents/skills/react-router`. Interactive creation defaults to yes; `--yes` and
non-interactive creation include it. Pass `--no-agent-skills` to opt out.

```sh
create-react-router my-app --no-agent-skills
```

### Version-matched local docs (`7.17.0`)

The `react-router` package includes selected official Markdown in
`node_modules/react-router/docs`. It excludes generated API docs, tutorials, and community
content.

## Project-line caution

The migration guide announced React Server Component previews, stable middleware,
granular Data Mode lazy loading from v7.5, and automatic Framework route-module splitting
from v7.2 (`7.0-guide`). Treat those as distinct capabilities, not one mode.

Remix 3 is a separate, ground-up modular toolkit with its own component model and no React
dependency (`project-direction-and-route-modules`). It is not a drop-in Remix v2 upgrade,
and no preview was available in the source guidance.
