# Migration, Packages, and Tooling

## Package consolidation and imports

### Consolidated packages in 7.0.0

`react-router-dom`, `@remix-run/react`, `@remix-run/server-runtime`,
`@remix-run/router`, and `@remix-run/testing` were consolidated into
`react-router`. In v7, `react-router-dom` remained only as a re-export shim;
`react-router-native` and `react-router-dom-v5-compat` were removed. Cloudflare
Pages and Workers adapters converged on `@react-router/cloudflare`.

Import runtime-neutral APIs from `react-router`, not from an adapter. Cookie and
session helpers such as `createCookieSessionStorage` also moved there, while their
low-level `*Factory` APIs were removed.

```ts
import { createCookieSessionStorage, redirect, useLoaderData } from "react-router";
import { createFileSessionStorage } from "@react-router/node";
```

Framework browser entries use `HydratedRouter` from `react-router/dom`. Manual
browser and hash routers use that entry point's `RouterProvider` to enable
`ReactDOM.flushSync()`; memory and other non-DOM routers import `RouterProvider`
from `react-router`.

### Removed DOM compatibility package in 8.0.0

The `react-router-dom` shim is gone. Import `RouterProvider` and `HydratedRouter`
from `react-router/dom`, and all other former DOM-package APIs from `react-router`.

```ts
import { Link } from "react-router";
import { RouterProvider } from "react-router/dom";
```

### Public API renames and removals in 7.0.0

- `createRemixStub` became `createRoutesStub`.
- `RemixContext` became `FrameworkContext`.
- `PrefetchPageDescriptor` became `PageLinkDescriptor`.
- `Action` became `NavigationType`.
- The internal router type became `RemixRouter`.
- `detectErrorBoundary` was replaced by `mapRouteProperties`.
- `unstable_dataStrategy` and `unstable_patchRoutesOnNavigation` stabilized as
  `dataStrategy` and `patchRoutesOnNavigation`.
- Low-level `createBrowserHistory`, `createHashHistory`, and
  `createMemoryHistory` were removed in favor of `create*Router` APIs.

For migration-only `unstable_HistoryRouter` code, 7.12.0 exports
`UNSAFE_createBrowserHistory`, `UNSAFE_createHashHistory`, and
`UNSAFE_createMemoryHistory`. Do not use these constructors in new applications.

### Adopted v7 behavior

The v6 `v7_*` and Remix v2 `v3_*` flags became unconditional in 7.0.0. Remove the
settings for relative splats, transitions, fetcher persistence, normalized form
methods, partial hydration, action revalidation, Single Fetch, lazy route discovery,
abort reasons, and dependency optimization rather than carrying them into v7.

## Runtime baselines

### v7 baseline and globals

Framework packages in 7.0.0 require Node 20 and React/React DOM 18. The removed
`installGlobals()` helper is unnecessary because native Fetch and Web Crypto globals
are expected. Apps that pinned `isbot@3` while using the default server entry needed
to upgrade to `isbot@5`.

### v8 baseline and module format

As of 8.0.0, packages are ESM-only, target ES2022, and require Node 22.22.0 or
newer, React 19.2.7 or newer, and Vite 7 or newer. On Maintenance LTS Node lines,
only the latest minor branch is supported, so a minor React Router release may
raise the minimum Node minor.

The Express adapter accepts Express 5. Its 8.0.0 v4 peer range begins at Express
4.22.2, while `@react-router/serve` uses Express 5.2.1. Express 5 first entered the
adapter's peer range in 7.3.0.

## Compiler and Vite migration

### Vite-only framework compiler in 7.0.0

The old esbuild compiler was removed. Use the renamed Vite entry points:

```ts
import { reactRouter } from "@react-router/dev/vite";
import { cloudflareDevProxy } from "@react-router/dev/vite/cloudflare";
```

The plugin `manifest` option was replaced by `buildEnd({ buildManifest })`;
`reactRouterConfig.publicPath` was removed. Enabled Vite manifests are written
inside each build, such as `build/client/.vite/manifest.json`.

Framework tooling added Vite 6 support in 7.1.0, Vite 7 in 7.6.3 within the
7.6.0 line, and Vite 8 in 7.14.0.

The Vite Environment API initially required
`future.unstable_viteEnvironmentApi` in 7.2.0. It was experimental and unsuitable
for production at that stage.

Under the experimental Vite Environment API in 7.4.0, a plugin replacing the
default SSR environment, such as `@cloudflare/vite-plugin`, could appear before or
after the React Router plugin. The Environment API is mandatory in v8.

In 8.0.0, `@react-router/dev/vite/cloudflare` was removed. Use
`@cloudflare/vite-plugin`; Wrangler 3 is no longer supported. Earlier compatibility
expanded to Wrangler 4 in 7.5.0.

### Preview and server rendering tools

Framework production builds can be served with `vite preview` since 7.11.0. In
8.0.0, preview-server prerendering became the only implementation and
`future.unstable_previewServerPrerendering` was removed.

Framework apps without a custom `entry.server.tsx` use
`renderToReadableStream` by default in 8.2.0 unless they depend on
`@react-router/node`, `@react-router/express`, or `@react-router/serve`; those Node
adapters retain `renderToPipeableStream`. A Node app without a custom entry can opt
into Web Streams with `future.unstable_enableNodeReadableStream`.

```ts
import type { Config } from "@react-router/dev/config";

export default {
  future: { unstable_enableNodeReadableStream: true },
} satisfies Config;
```

## Tooling and scaffolding

### Route-config and generated-module support

The virtual `virtual:react-router/server-build` module gained generated declarations
in 7.4.0; 7.4.1 also supports `moduleDetection: "force"`. Route config accepts
`.mts` and `.mjs` files since 7.7.0.

`@react-router/remix-config-routes-adapter` exports both `DefineRoutesFunction` and,
since 7.7.0, `DefineRouteFunction` for typing one route callback.

### Package-manager and project generation behavior

- `create-react-router` detects Deno 2.0.5 or newer since 7.7.0. With older Deno,
  pass `--package-manager deno` explicitly.
- `@react-router/dev` and `create-react-router` recognize `nub` since 8.2.0.
- Since 8.1.0, generated projects can include the official skill at
  `.agents/skills/react-router`. Interactive runs default to yes, and `--yes` or
  non-interactive runs include it; pass `--no-agent-skills` to opt out.
- Since 8.0.0, scaffolding uses native `fetch`; the former implicit `HTTPS_PROXY`
  support is therefore gone.

The `react-router` package has shipped a subset of version-matched Markdown docs in
`node_modules/react-router/docs` since 7.17.0. Generated API docs, tutorials, and
community content are not part of that local subset.

## Dependency security upgrades

Upgrade `@react-router/dev` to 7.10.1 or later on that line; it raises `valibot` to
`^1.2.0` for GHSA-vqpr-j7v3-hqw9. `@react-router/serve` 7.11.0 updates
`compression` and `morgan` to address the `on-headers` advisory
GHSA-76c9-3jph-rj3q. See the security reference for application-facing fixes.

## Project direction

Remix 3 is a separate, ground-up modular toolkit with its own component model and
no React dependency. It was announced without a preview and is not a drop-in Remix
v2 or React Router upgrade.
