# Nitro, server runtime, and deployment

Configure Nitro routing, bundling, runtime behavior, security, caching, tasks, and deployment presets.

## Build, routing, and runtime

### Automatic Nitro source maps for errors (since 3.16.0)

Nitro now applies source maps automatically without extra Node options, and sets appropriate security headers when rendering error pages.

### Configured and filesystem routes (nitro-3-release-feeds)

Nitro 3 adds a `routes` configuration surface, while file-based routing is opt-in through `serverDir`. Routing and production assets now honor `baseURL` consistently.

### Consolidated imports and request types (nitro-3-release-feeds)

`defineConfig`, runtime utilities, and HTTP utilities are exposed from the root `nitro` package, and Nitro 3 also adds server-fetch helpers. The server request type is available from `nitro/types` as `ServerRequest`.

### Dependencies bundle by default (nitro-3-release-feeds)

Production dependencies are bundled into the portable output by default instead of being copied into `.output/server/node_modules`. Nitro traces only known native or incompatible packages; add other exceptions through `traceDeps`, which also supports full-trace mode and custom trace options.

### Native WebAssembly (nitro-3-release-feeds)

Native WebAssembly support is enabled by default. Known packages with native bindings are also traced automatically instead of being incorrectly bundled.

### Nitro 3 prerelease channel (nitro-3-release-feeds)

The v3 feed is still on explicitly versioned beta releases; the newest supplied tag is `v3.0.260610-beta`. Pin a beta deliberately rather than assuming the stable Nitro package resolves to v3.

### Nuxt-managed public assets (since 3.11.0)

Nuxt now resolves public assets from the app and its layers itself, so directories registered in `nitro.publicAssets` work with custom URL prefixes.

### Page routes available to Nitro observability (since 3.18.0)

Nuxt now exposes page routes to Nitro's observability integrations, allowing supported monitoring platforms to attribute metrics to page-level routes.

### Public-asset processing (nitro-3-release-feeds)

`compressPublicAssets` can emit Zstandard-compressed assets, and public assets accept custom ignore patterns. Under the Vite integration, `copyPublicDir` now defaults to `false`, so Vite does not independently copy the public directory.

### Removed dependency controls (nitro-3-release-feeds)

The `nodeModulesDirs` option, `nitro/deps/*` imports, and custom `moduleSideEffects` build configuration are removed. Projects using those v2 escape hatches must migrate to the v3 bundling and tracing model.

### Server entry and renderer controls (nitro-3-release-feeds)

The build can emit the `node` handler format, accept a custom `serverEntry`, disable the renderer with `renderer: false`, or configure static rendering through `renderer.static`.

### Source maps and build metadata (nitro-3-release-feeds)

Standalone Nitro 3 improves source-map handling but leaves source maps disabled by default; the Vercel preset installs its source-map support only when they are enabled. Build/runtime metadata now includes `manifest.deploymentId` and Nitro version information.

### TypeScript paths and configuration (nitro-3-release-feeds)

Nitro loads the project `tsconfig.json` for aliases and JSX options and provides a `nitro/tsconfig` preset. The temporary `experimental.tsconfigPaths` option was removed; Rolldown-backed Vite can instead use `resolve.tsconfigPaths` as shown above.

### Vite and Rolldown integration (nitro-3-release-feeds)

Nitro 3 has first-class Rolldown and `rolldown-vite` support, can auto-detect its builder, and makes Rollup optional. Vite plugins can extend Nitro, while `nitro build --builder` selects a builder explicitly.

```ts
import { defineConfig } from 'vite'
import { nitro } from 'nitro/vite'

export default defineConfig({
  plugins: [nitro({ serverDir: './server' })],
  resolve: { tsconfigPaths: true },
})
```

### Vite assets and React Server Components (nitro-3-release-feeds)

The Vite integration supports `?assets` imports, automatically treats server-consumer environments as Nitro services, and can auto-detect the client entry. Experimental React Server Components work through `@vitejs/plugin-rsc`.

## CLI, development, and tasks

### Environment-aware preview and development (nitro-3-release-feeds)

Vite preview loads dotenv files and respects Vite's `mode` during environment loading. `$production` and `$development` config layers still apply when `NODE_ENV` is unset, scheduled tasks run during Vite development, and service-fetch failures propagate in development as they do in production.

### Preview, deploy, docs, and task commands (nitro-3-release-feeds)

The CLI adds `nitro preview`, `nitro deploy`, and bundled documentation through `nitro docs`; tasks can also be run from the CLI. Framework integrations can supply custom preview and deploy commands.

### Task request context and scheduling (nitro-3-release-feeds)

Task handlers receive `req` and `waitUntil` in their context. Scheduled-task integration is available in the Vercel and Cloudflare presets as well as local Vite development.

## Deployment presets and platforms

### Additional deployment targets (nitro-3-release-feeds)

Nitro 3 adds the `edgeone-pages` and `zephyr` targets, a `netlify.config` options namespace, and Node 24 support for AWS Amplify.

### Cloudflare v3 defaults (nitro-3-release-feeds)

Cloudflare enables `nodeCompat` and `deployConfig` by default, and enables `no_bundle` by default for Workers but not Pages. It also supports `exports.cloudflare.ts`; the feed flags the v3 environment-binding access pattern as a breaking migration point.

### Platform request information (nitro-3-release-feeds)

`req.ip` is populated by the Vercel, Netlify, Cloudflare, and Deno Deploy presets. Cloudflare requests also consistently carry the platform `cf` context.

### Preset fallback and runtime detection (nitro-3-release-feeds)

`defaultPreset` customizes the fallback deployment preset. Although an early alpha inferred Bun and Deno from the running runtime, the beta stopped using the host runtime alone for that inference, avoiding accidental deployment-target changes.

### Vercel queues and function controls (nitro-3-release-feeds)

The Vercel preset supports queues in deployments and local development, plus per-route function configuration for routes needing different memory or duration limits. It also adds Bun and Node 24 runtimes, skew protection, and an opt-in Node handler format.

## Security, caching, and observability

### Basic-auth route rules (nitro-3-release-feeds)

Route rules can apply basic authentication. The basic-auth rule is always evaluated first so later route-rule behavior cannot run before authentication.

### Cache invalidation and multi-tier storage (nitro-3-release-feeds)

Nitro's ocache-based cache supports `handler.invalidate()`, `resolveCacheKey`/`.resolveKey()`, and multi-tier caches. Nullish storage writes delete the entry, stale-age and zero-TTL values are respected, and expired in-memory entries are proactively flushed.

### H3 v2 HTTP behavior (nitro-3-release-feeds)

The bundled H3 v2 line preserves CORS headers on error responses, adds `Allow` to 405 responses, enforces streaming body limits independently of `Content-Length`, and updates cookie handling toward RFC 6265bis. It also adds a hardened `redirectBack` utility and normalizes encoded mounted paths.

### OpenAPI UI configuration (nitro-3-release-feeds)

OpenAPI support now includes Swagger UI configuration, allowing the generated API description to be exposed through a configured interactive UI.

### Proxy and redirect security behavior (nitro-3-release-feeds)

The April beta patches medium-severity vulnerabilities in `proxy` and `redirect` route rules. Updated rules reject out-of-scope proxy requests and protocol-relative redirect bypasses, so deployments using either rule should not remain on an earlier beta.

### Request tracing channels (nitro-3-release-feeds)

Experimental built-in tracing channels record request spans; route handlers are wrapped for tracing at build time, and tracing channels extend into unstorage operations.

### WebSockets and proxy adapters (nitro-3-release-feeds)

Nitro 3 supports WebSockets, and the bundled ecosystem adds `createWebSocketProxy` plus `fromNodeUpgradeHandler` with Socket.IO support. Vercel WebSocket upgrades remain marked for internal testing in the supplied beta feed.
