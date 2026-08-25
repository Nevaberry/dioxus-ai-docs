---
name: cloudflare-workers-knowledge-patch
description: Cloudflare Workers
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Cloudflare Workers Knowledge Patch

Use this skill when implementing, migrating, configuring, testing, or debugging
Cloudflare Workers, Wrangler, the Workers Vite plugin, Static Assets, Workers
RPC, or the Workers Node.js compatibility layer.

Check the project's `compatibility_date`, compatibility flags, Wrangler
configuration, and tool versions before applying date-gated behavior. Prefer the
project's code, tests, and observed runtime behavior if they disagree with this
guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [nodejs-compatibility.md](references/nodejs-compatibility.md) | Default enablement, module coverage and stubs, process and timers, module interop, types, build runtime |
| [rpc-and-websockets.md](references/rpc-and-websockets.md) | RPC capabilities, ownership and pipelining, streams, forwarding, cross-language calls, WebSocket behavior |
| [runtime-and-web-platform.md](references/runtime-and-web-platform.md) | Fetch, cache, request lifecycle, JavaScript and web APIs, serialization, Access, tracing, email, Dynamic Workers |
| [static-assets-and-pages-migration.md](references/static-assets-and-pages-migration.md) | Static Assets routing and bindings, Pages conversion, builds, previews, headers, redirects, domains |
| [wrangler-tooling-and-testing.md](references/wrangler-tooling-and-testing.md) | Wrangler v4, local and remote commands, Vite, authentication, generated types, integration tests, startup inspection |

## Breaking changes and migration priorities

### Wrangler v4

- Node.js 16 is unsupported. Wrangler follows the Node.js release lifecycle.
- Bundled esbuild moved from 0.17.19 to 0.24. Wrangler minor releases may
  update pre-1.0 esbuild and alter bundling behavior.
- Wildcard dynamic imports bundle every matching file.
- Commands that can operate locally or remotely now default to local. Add
  `--remote` when KV, R2, or another command must touch account data.
- Replace removed interfaces: `legacy_assets` with Static Assets,
  `node_compat` with `nodejs_compat`, `getBindingsProxy()` with
  `getPlatformProxy()`, `publish` with `deploy`, `pages publish` with
  `pages deploy`, `generate` with `npm create cloudflare@latest`, and
  `wrangler version` with `wrangler --version`.
- Remove `usage_model`. Migrate Workers Sites and `legacy_env` service
  environments to Static Assets and Wrangler environments.

### Node.js compatibility defaults

Compatibility dates from `2026-08-04` enable `nodejs_compat` and
`nodejs_compat_v2` without positive flags. Earlier dates retain their existing
behavior. Fully opt out on a new date with both flags:

```jsonc
{
  "compatibility_date": "2026-08-04",
  "compatibility_flags": ["no_nodejs_compat", "no_nodejs_compat_v2"]
}
```

Use `nodejs_als` when only `AsyncLocalStorage` is needed. Import-only stubs can
be enabled or disabled per module with `enable_nodejs_<name>_module` and
`disable_nodejs_<name>_module`; omit the leading underscore in the
`node:_stream_wrap` flag name.

### Compatibility-sensitive runtime behavior

- From `2025-09-01`, cross-origin redirect following strips
  `Authorization`; use `retain_authorization_on_cross_origin_redirect` only
  when preserving credentials is intentional.
- From `2025-12-03`, optional runtime properties can exist with value
  `undefined`. Test `obj.key !== undefined`, not own-property presence.
- From `2026-02-19`, iterable `Request` and `Response` bodies stream instead of
  being stringified, except sync iterables with explicit coercion hooks.
- From `2026-03-17`, `WebSocket.binaryType` defaults to `"blob"`. Set
  `"arraybuffer"` before `accept()` when required; hibernatable Durable Object
  handlers continue receiving `ArrayBuffer`.
- From `2026-03-24`, encoding streams start with readable high-water mark 0,
  so a write can wait for a reader to pull.
- From `2026-04-21`, structured cloning and V8 serialization retain more error
  types and own properties, but not the original stack by default.

## Static Assets quick reference

Configure `assets.directory` to deploy assets and Worker code together. Exact
asset matches bypass the Worker by default; misses invoke `main`. Add a binding
when code must delegate to the asset service:

```jsonc
{
  "main": "src/index.js",
  "assets": {
    "directory": "./dist",
    "binding": "ASSETS",
    "not_found_handling": "single-page-application",
    "run_worker_first": ["/api/*", "!/api/docs/*"]
  }
}
```

An assets-only Worker must omit `binding`. The Workers Vite plugin supplies the
asset directory. Unlike Pages, Workers does not infer SPA or 404 fallback from
files; set `not_found_handling` explicitly. Put `.assetsignore` inside the asset
directory because Pages-style default upload exclusions do not carry over.

For Pages migration, replace `pages_build_output_dir` with `assets.directory`,
retain the compatibility date, compile `functions/` to one Worker entrypoint,
and configure `run_worker_first` for middleware or `_routes.json` behavior that
must precede assets. Use `wrangler dev` and `wrangler deploy`.

## RPC quick reference

RPC requires compatibility date `2024-04-03` or later, or the `rpc` flag.
Public `WorkerEntrypoint` methods and Durable Object methods are asynchronous
to callers, even when implemented synchronously.

Functions cross as callable capabilities. Application classes must extend
`RpcTarget`; await remote property reads. Prefer one `RpcTarget` over a plain
object containing many functions to avoid creating a stub per function.

```ts
using pendingCounter = env.COUNTERS.create();
await pendingCounter.increment(); // pipelines through the unresolved result
```

- Promise pipelining removes an intermediate round trip.
- Byte streams, `Request`, and `Response` transfer ownership. Clone or `tee()`
  first when the sender must keep using the value.
- A forwarded stub works only for the current execution contexts and cannot be
  persisted.
- RPC ignores Smart Placement; a service-binding target runs locally on the
  caller's machine.
- JavaScript and Python Workers can call exported methods across ordinary
  Service bindings; a Python binding must name a named JavaScript entrypoint.

## Vite development and production

The Workers Vite plugin runs application code in `workerd` with HMR and supports
SPA, SSR, static, and API workloads:

```ts
import { cloudflare } from "@cloudflare/vite-plugin";
import { defineConfig } from "vite";

export default defineConfig({ plugins: [cloudflare()] });
```

The entry configuration resolves from `configPath`, then
`CLOUDFLARE_VITE_WRANGLER_CONFIG_PATH`, then root Wrangler config files; a
`config` object or callback applies afterward. Defaults include state in
`.wrangler/state`, inspector port 9229, and remote bindings enabled.

Requests enter through the main Worker when using `auxiliaryWorkers`. Builds
place each Worker in its own `dist` subdirectory, and `wrangler deploy` deploys
only the entry Worker. Deploy every auxiliary Worker separately with its
generated config.

## Testing, types, and observability

- Run `wrangler types` after changing compatibility dates, flags, bindings, or
  module rules. Include `worker-configuration.d.ts` through
  `compilerOptions.types`, install `@types/node` when needed, and run
  `wrangler types --check` in CI.
- Use `@cloudflare/workers-types` v5 root types for the latest stable APIs and
  `/experimental` for experimental APIs; dated entrypoints are gone.
- Use `createTestHarness()` for production-build integration tests. It can load
  multiple configs, dispatch with `server.fetch()`, reset storage, expose logs,
  mock outbound requests, and integrate with Playwright.
- `wrangler dev` and `vite dev` capture structured OpenTelemetry traces and
  correlated logs. Inspect automatic and custom spans in Local Explorer; its
  `/cdn-cgi/explorer/api` is a read-only OpenAPI-described interface.
- `wrangler check startup` reports raw and gzip sizes plus sampled, active, GC,
  and idle local CPU time, and writes `worker-startup.cpuprofile`. Treat local
  timings as diagnostic rather than production measurements.

## Authentication and Access

For human deploys, create and directory-activate named Wrangler OAuth profiles.
`CLOUDFLARE_API_TOKEN` overrides profiles in automation. Use device login in
containers or remote shells:

```sh
npx wrangler login --device --browser=false
```

Worker-level Access can protect routes, custom domains, `workers.dev`, and
preview URLs together. At runtime, inspect `ctx.access.aud` and call
`await ctx.access.getIdentity()`. Use `access.dev` to inject a local identity;
remove it to test an unauthenticated request.
