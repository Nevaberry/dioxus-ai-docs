# Nitro, server runtime, and deployment

Use this reference for Nuxt's Nitro integration, Nitro 3 prerelease migration, server routing and entries, dependency bundling, assets, caching, tasks, security, observability, and deployment presets.

## Contents

- [Nuxt-integrated server behavior](#nuxt-integrated-server-behavior)
- [Nitro 3 channel and builder integration](#nitro-3-channel-and-builder-integration)
- [Dependency bundling and TypeScript](#dependency-bundling-and-typescript)
- [Vite assets, public output, and source maps](#vite-assets-public-output-and-source-maps)
- [CLI, preview, deploy, and tasks](#cli-preview-deploy-and-tasks)
- [Networking, authentication, and request security](#networking-authentication-and-request-security)
- [Tracing, OpenAPI, and caching](#tracing-openapi-and-caching)
- [Deployment preset behavior](#deployment-preset-behavior)

## Nuxt-integrated server behavior

### Resolve layered public assets through Nuxt (3.11.0)

Nuxt resolves public assets from the application and its layers. Directories registered in `nitro.publicAssets` work with custom URL prefixes instead of depending on Nitro's former project-root assumptions.

### Apply Nitro source maps automatically for errors (3.16.0)

Nuxt's integrated Nitro runtime applies source maps without extra Node flags and sets appropriate security headers on rendered error pages.

### Expose page routes to server observability (3.18.0)

Nuxt publishes page routes to supported Nitro observability integrations so monitoring systems can attribute metrics to page-level routes.

## Nitro 3 channel and builder integration

### Pin the prerelease deliberately (nitro-3-release-feeds)

The supplied Nitro 3 feed remains on explicitly versioned beta releases; its newest tag is `v3.0.260610-beta`. Pin a beta instead of assuming the stable `nitro` package resolves to v3.

### Integrate Nitro with Vite or Rolldown (nitro-3-release-feeds)

Nitro 3 supports Rolldown and `rolldown-vite`, can auto-detect its builder, and makes Rollup optional. Extend Nitro with Vite plugins or select a builder through `nitro build --builder`.

```ts
import { defineConfig } from 'vite'
import { nitro } from 'nitro/vite'

export default defineConfig({
  plugins: [nitro({ serverDir: './server' })],
  resolve: { tsconfigPaths: true },
})
```

### Configure routes and opt into filesystem routing (nitro-3-release-feeds)

Nitro 3 adds a `routes` configuration surface. File-based routing is opt-in through `serverDir`. Both routes and production assets consistently honor `baseURL`.

### Select server entry and renderer behavior (nitro-3-release-feeds)

The build can emit the `node` handler format, use a custom `serverEntry`, disable rendering with `renderer: false`, or configure static rendering through `renderer.static`.

## Dependency bundling and TypeScript

### Bundle production dependencies by default (nitro-3-release-feeds)

Nitro 3 bundles production dependencies into portable output instead of copying them to `.output/server/node_modules`. It traces known native or incompatible packages. Add other exceptions through `traceDeps`, including full-trace mode and custom trace options.

### Remove v2 dependency escape hatches (nitro-3-release-feeds)

Migrate away from removed `nodeModulesDirs`, `nitro/deps/*` imports, and custom `moduleSideEffects` build configuration. Use Nitro 3's bundling and tracing approach instead.

### Use project TypeScript paths directly (nitro-3-release-feeds)

Nitro loads the project `tsconfig.json` for aliases and JSX options and exposes a `nitro/tsconfig` preset. Remove the temporary `experimental.tsconfigPaths`; Rolldown-backed Vite can use `resolve.tsconfigPaths` as in the Vite example above.

### Consolidate Nitro imports (nitro-3-release-feeds)

Import `defineConfig`, runtime utilities, HTTP utilities, and server-fetch helpers from the root `nitro` package. Import the server request type from `nitro/types` as `ServerRequest`.

### Keep native packages out of inappropriate bundles (nitro-3-release-feeds)

Native WebAssembly works by default. Nitro also traces known packages with native bindings automatically instead of trying to bundle them.

## Vite assets, public output, and source maps

### Use Vite assets and experimental RSC support (nitro-3-release-feeds)

The Vite integration supports `?assets` imports, treats server-consumer environments as Nitro services automatically, and can detect the client entry. Experimental React Server Components integrate through `@vitejs/plugin-rsc`.

### Configure public-asset processing (nitro-3-release-feeds)

`compressPublicAssets` can emit Zstandard-compressed variants, and public-asset configuration accepts custom ignore patterns. Under Vite integration, `copyPublicDir` defaults to `false`, so Vite does not copy the public directory independently.

### Enable standalone source maps explicitly (nitro-3-release-feeds)

Standalone Nitro 3 improves source-map handling but keeps source maps disabled by default. The Vercel preset installs its source-map support only when maps are enabled. Build/runtime metadata includes `manifest.deploymentId` and Nitro version information.

## CLI, preview, deploy, and tasks

### Use first-party preview, deploy, docs, and task commands (nitro-3-release-feeds)

The CLI provides `nitro preview`, `nitro deploy`, bundled documentation through `nitro docs`, and task execution. Framework integrations can supply custom preview and deploy commands.

### Match preview and development environment loading (nitro-3-release-feeds)

Vite preview loads dotenv files and respects Vite `mode`. `$production` and `$development` config layers apply even when `NODE_ENV` is unset. Scheduled tasks run during Vite development, and service-fetch failures propagate in development as they do in production.

### Use request context in task handlers (nitro-3-release-feeds)

Task handlers receive `req` and `waitUntil`. Scheduled-task integration works in the Vercel and Cloudflare presets and in local Vite development.

### Set an explicit fallback deployment preset (nitro-3-release-feeds)

Use `defaultPreset` to choose the fallback target. A beta no longer infers Bun or Deno solely from the runtime running the build, preventing accidental deployment-target changes that occurred in an early alpha.

## Networking, authentication, and request security

### Use WebSockets and proxy adapters with platform constraints (nitro-3-release-feeds)

Nitro 3 supports WebSockets. Its ecosystem includes `createWebSocketProxy` and `fromNodeUpgradeHandler`, including Socket.IO support. Vercel WebSocket upgrades remain marked for internal testing in the supplied beta feed.

### Authenticate route rules before other behavior (nitro-3-release-feeds)

Route rules can apply basic authentication. Nitro evaluates the basic-auth rule first, preventing later route-rule behavior from running before authentication.

### Include the proxy and redirect security fixes (nitro-3-release-feeds)

April beta releases patch medium-severity vulnerabilities in `proxy` and `redirect` route rules. Updated proxy rules reject out-of-scope requests, and redirect rules reject protocol-relative bypasses. Do not deploy either rule on an earlier vulnerable beta.

### Apply hardened H3 v2 HTTP behavior (nitro-3-release-feeds)

The bundled H3 v2 line:

- Preserves CORS headers on error responses.
- Adds `Allow` to `405 Method Not Allowed` responses.
- Enforces streaming body limits independently of `Content-Length`.
- Moves cookie handling toward RFC 6265bis.
- Adds a hardened `redirectBack` utility.
- Normalizes encoded mounted paths.

## Tracing, OpenAPI, and caching

### Enable request tracing channels experimentally (nitro-3-release-feeds)

Built-in tracing channels record request spans. Nitro wraps route handlers for tracing at build time, and channels extend into unstorage operations.

### Configure an OpenAPI interface (nitro-3-release-feeds)

OpenAPI support includes Swagger UI options, allowing a generated API description to be exposed through a configured interactive interface.

### Invalidate and tier ocache entries (nitro-3-release-feeds)

Nitro's ocache-based cache supports `handler.invalidate()`, `resolveCacheKey`/`.resolveKey()`, and multi-tier caching. Nullish writes delete entries, stale-age and zero-TTL values are honored, and expired in-memory entries are proactively flushed.

## Deployment preset behavior

### Read platform request metadata (nitro-3-release-feeds)

`req.ip` is populated by the Vercel, Netlify, Cloudflare, and Deno Deploy presets. Cloudflare requests consistently include the platform `cf` context.

### Review Cloudflare v3 defaults (nitro-3-release-feeds)

Cloudflare enables `nodeCompat` and `deployConfig` by default. It enables `no_bundle` by default for Workers, but not Pages. The preset supports `exports.cloudflare.ts`; treat the v3 environment-binding access pattern as a breaking migration point.

### Configure Vercel queues and functions per route (nitro-3-release-feeds)

The Vercel preset supports queues in deployment and local development plus per-route function settings for memory or duration. It also supports Bun and Node 24 runtimes, skew protection, and an opt-in Node handler format.

### Target additional platforms (nitro-3-release-feeds)

Nitro 3 adds `edgeone-pages` and `zephyr` presets, a `netlify.config` options namespace, and Node 24 support for AWS Amplify.
