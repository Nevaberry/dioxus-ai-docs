# Nitro, server runtime, and deployment

## Establish the Nitro line first

Nuxt 4 did not initially adopt Nitro 3; Nuxt and Nitro majors are independent (4.0-platform-guide). The supplied Nitro 3 feed remains on explicitly versioned beta releases, with `v3.0.260610-beta` as its newest tag. Pin a beta deliberately rather than assuming an unqualified stable package resolves to v3 (nitro-3-release-feeds).

## Builders and Vite integration

Nitro 3 supports Rolldown and `rolldown-vite`, auto-detects a builder, and makes Rollup optional. Select explicitly with `nitro build --builder`. Vite plugins can embed Nitro (nitro-3-release-feeds):

```ts
import { defineConfig } from 'vite'
import { nitro } from 'nitro/vite'

export default defineConfig({
  plugins: [nitro({ serverDir: './server' })],
  resolve: { tsconfigPaths: true },
})
```

The Vite integration supports `?assets`, can detect the client entry, and treats server-consumer environments as Nitro services. Experimental React Server Components integrate through `@vitejs/plugin-rsc` (nitro-3-release-feeds).

## Routing, entries, and renderers

Nitro 3 adds configured `routes`; filesystem routing is opt-in through `serverDir`. Routing and production assets honor `baseURL` consistently. The build can emit the `node` handler format, use a custom `serverEntry`, disable rendering with `renderer: false`, or configure static rendering through `renderer.static` (nitro-3-release-feeds).

Nuxt decodes request paths before route-rule matching, so percent-encoded requests match their decoded form (4.5.2).

## Dependency bundling and tracing

Production dependencies are bundled into portable output by default instead of copied into `.output/server/node_modules`. Nitro automatically traces known native or incompatible packages; add exceptions with `traceDeps`, which supports full tracing and custom options (nitro-3-release-feeds).

Remove the v2 `nodeModulesDirs` option, `nitro/deps/*` imports, and custom `moduleSideEffects` configuration. Native WebAssembly is enabled by default, and known native-binding packages are traced rather than bundled incorrectly (nitro-3-release-feeds).

## TypeScript and imports

Nitro loads project `tsconfig.json` aliases and JSX settings and provides `nitro/tsconfig`. The temporary `experimental.tsconfigPaths` option is removed; Rolldown-backed Vite can use `resolve.tsconfigPaths` (nitro-3-release-feeds).

Import configuration, runtime utilities, HTTP utilities, and server-fetch helpers from the root `nitro` package. Import `ServerRequest` from `nitro/types` (nitro-3-release-feeds). Modules can add server runtime files with `addServerTemplate` (3.14.0) and type declarations with `addTypeTemplate(..., { nitro: true })` (3.16.0).

Server application code may use the protected `#server` alias; client and shared code cannot import it (3.21.0).

## Public assets and build metadata

Nuxt resolves public assets from the application and layers, so directories registered in `nitro.publicAssets` work with custom URL prefixes (3.11.0).

Nitro 3 can emit Zstandard-compressed public assets and accepts custom ignore patterns. With Vite integration, `copyPublicDir` defaults to `false`, preventing a second independent public-directory copy (nitro-3-release-feeds).

Standalone source maps are improved but disabled by default. The Vercel preset installs source-map support only when maps are enabled. Runtime/build metadata exposes `manifest.deploymentId` and Nitro version information (nitro-3-release-feeds). In Nuxt integration, error source maps are applied automatically and error pages receive suitable security headers (3.16.0).

## CLI, preview, and environment behavior

The CLI provides `nitro preview`, `nitro deploy`, `nitro docs`, and task execution; frameworks may provide custom preview and deployment commands (nitro-3-release-feeds).

Vite preview loads dotenv files and respects Vite `mode`. `$production` and `$development` configuration layers apply even when `NODE_ENV` is unset. Scheduled tasks run during Vite development, and service-fetch failures propagate there as in production (nitro-3-release-feeds).

Set `defaultPreset` to customize the fallback deployment preset. Beta behavior no longer infers Bun or Deno deployment solely from the host runtime, avoiding accidental target changes (nitro-3-release-feeds).

## Tasks and scheduling

Task handlers receive `req` and `waitUntil` in context. Scheduled-task integration works in Vercel and Cloudflare presets and local Vite development (nitro-3-release-feeds).

## WebSockets and proxy adapters

Nitro 3 supports WebSockets. Ecosystem adapters include `createWebSocketProxy` and `fromNodeUpgradeHandler`, with Socket.IO support. Vercel WebSocket upgrades were still internally tested in the supplied beta feed (nitro-3-release-feeds).

## Route-rule security

Basic-auth route rules execute authentication before later rule behavior. Beta patches fixed medium-severity proxy and redirect issues by rejecting out-of-scope proxy requests and protocol-relative redirect bypasses; deployments using either rule should not remain on an earlier beta (nitro-3-release-feeds).

Nuxt navigation helpers separately reject script-capable protocols, unsafe normalized redirects, and cross-origin reload paths (3.21.0).

## Tracing, OpenAPI, and route observability

Experimental tracing channels record request spans, wrap route handlers at build time, and extend into unstorage operations. OpenAPI can configure Swagger UI for an interactive API description (nitro-3-release-feeds).

Nuxt exposes page routes to Nitro observability integrations, allowing monitoring platforms to attribute metrics to page-level routes (3.18.0).

## Cache behavior

The ocache-based cache supports `handler.invalidate()`, `resolveCacheKey`/`.resolveKey()`, and multi-tier storage. Nullish storage writes delete entries, stale-age and zero-TTL values are honored, and expired memory entries are proactively flushed (nitro-3-release-feeds).

## H3 v2 HTTP behavior

The bundled H3 v2 line preserves CORS headers on errors, includes `Allow` on 405 responses, enforces streaming body limits independently of `Content-Length`, updates cookies toward RFC 6265bis, hardens `redirectBack`, and normalizes encoded mounted paths (nitro-3-release-feeds).

## Platform request context

`req.ip` is populated by Vercel, Netlify, Cloudflare, and Deno Deploy presets. Cloudflare requests consistently expose platform `cf` context (nitro-3-release-feeds).

## Cloudflare defaults

Cloudflare enables `nodeCompat` and `deployConfig` by default. `no_bundle` defaults on for Workers but not Pages. The preset supports `exports.cloudflare.ts`; audit the v3 environment-binding access change during migration (nitro-3-release-feeds).

## Vercel capabilities

The Vercel preset supports queues in deployments and local development, per-route memory/duration settings, Bun and Node 24 runtimes, skew protection, and an opt-in Node handler format (nitro-3-release-feeds).

## Additional deployment targets

Nitro 3 adds `edgeone-pages` and `zephyr`, a `netlify.config` options namespace, and Node 24 support for AWS Amplify (nitro-3-release-feeds). Exercise the actual preset after changing assets, dependencies, cache rules, queues, schedules, or runtime format.
