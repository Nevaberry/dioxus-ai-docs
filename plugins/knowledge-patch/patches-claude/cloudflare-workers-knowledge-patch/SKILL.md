---
name: cloudflare-workers-knowledge-patch
description: Cloudflare Workers
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Cloudflare Workers Knowledge Patch

Use this skill when implementing, migrating, testing, or deploying Cloudflare
Workers. Start with the compatibility date and Wrangler configuration, then
open only the reference files relevant to the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [runtime-compatibility.md](references/runtime-compatibility.md) | Compatibility gates, Fetch and Cache behavior, JavaScript and stream APIs, Access, tracing, Dynamic Workers |
| [nodejs-compatibility.md](references/nodejs-compatibility.md) | `nodejs_compat`, process and environment behavior, native APIs, stubs, timers, runtime types |
| [rpc-and-websockets.md](references/rpc-and-websockets.md) | Workers RPC capabilities and ownership, pipelining, cross-language calls, WebSocket behavior |
| [static-assets-and-pages-migration.md](references/static-assets-and-pages-migration.md) | Static Assets routing and deployment, Pages migration, preview and domain caveats |
| [vite-development-and-testing.md](references/vite-development-and-testing.md) | Vite plugin configuration, auxiliary Workers, production-build integration tests, local traces |
| [wrangler-and-deployment.md](references/wrangler-and-deployment.md) | Wrangler v4 migration, local versus remote resources, authentication, types, startup inspection, Builds |

## Triage compatibility-date changes first

Before changing code, read `compatibility_date` and `compatibility_flags` from
the active Wrangler configuration. Many runtime differences below are date
gated and have explicit rollback flags.

For dates from `2026-08-04`, Node.js compatibility is on by default. Opting out
requires both flags:

```jsonc
{
  "compatibility_date": "2026-08-04",
  "compatibility_flags": ["no_nodejs_compat", "no_nodejs_compat_v2"]
}
```

Earlier dates do not change. Positive Node.js compatibility flags on a new
date are redundant and local tooling may ignore them.

When upgrading an existing Worker, specifically regression-test:

- `process.env` population at `2025-04-01` with `nodejs_compat`.
- Static Asset navigation fallback ordering at `2025-04-01`.
- cross-origin `Authorization` stripping at `2025-09-01`.
- optional runtime properties becoming present with `undefined` at
  `2025-12-03`.
- `require()` default-export interop at `2026-01-22`.
- iterable request and response bodies at `2026-02-19`.
- WebSocket close, binary, and half-open behavior in March 2026.
- Node-compatible timer handles at `2026-02-10`.

See [runtime compatibility](references/runtime-compatibility.md) and
[Node.js compatibility](references/nodejs-compatibility.md) for flags and
edge cases.

## Migrate to Wrangler v4

Wrangler v4 requires a supported Node.js release and no longer supports
Node.js 16. Its bundled esbuild moved from 0.17.19 to 0.24; minor Wrangler
updates may also move pre-1.0 esbuild versions and alter bundling. Wildcard
dynamic imports include every matching file, so inspect bundle contents.

Replace removed commands and settings:

| Removed or deprecated | Use |
| --- | --- |
| `legacy_assets` | Static Assets |
| `node_compat` | `nodejs_compat` |
| `getBindingsProxy()` | `getPlatformProxy()` |
| `wrangler publish` | `wrangler deploy` |
| `wrangler pages publish` | `wrangler pages deploy` |
| `wrangler generate` | `npm create cloudflare@latest` |
| `wrangler version` | `wrangler --version` |
| `usage_model` | Remove it; it has no effect |

Workers Sites and service environments using `legacy_env` are deprecated;
prefer Static Assets and Wrangler environments.

Resource commands default to local operation. Add `--remote` when a command
must operate on account data:

```sh
wrangler kv key get --binding MY_KV "my-key" --remote
```

Read [Wrangler and deployment](references/wrangler-and-deployment.md) before
changing authentication, generated types, Builds, or deployment commands.

## Configure Static Assets deliberately

`assets.directory` deploys static files and Worker code together. Exact asset
matches bypass the Worker by default; misses invoke `main`. Add an asset
binding only when Worker code must delegate to the asset service:

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

An assets-only Worker must omit `binding`. Unlike Pages, Workers does not infer
SPA or 404 behavior, so set `not_found_handling`. From `2025-04-01`, navigation
fallback can run before the Worker unless `run_worker_first` applies.

For a Pages migration, preserve the compatibility date, replace
`pages_build_output_dir` with `assets.directory`, and explicitly recreate
function-first routes. See
[Static Assets and Pages migration](references/static-assets-and-pages-migration.md).

## Choose the right development and test path

The Cloudflare Vite plugin executes application code in `workerd` while
retaining Vite HMR:

```ts
import { cloudflare } from "@cloudflare/vite-plugin";
import { defineConfig } from "vite";

export default defineConfig({ plugins: [cloudflare()] });
```

Requests enter through the main Worker even when `auxiliaryWorkers` are
configured. Builds emit separate subdirectories, and each auxiliary Worker
must be deployed separately.

Use Wrangler's `createTestHarness()` for integration tests against production
builds. It supersedes `unstable_startWorker()` and `unstable_dev()` and can
dispatch requests, reset storage, expose logs, mock outbound requests, and
integrate with Playwright.

See [Vite development and testing](references/vite-development-and-testing.md)
for configuration precedence, persisted state, inspector defaults, tunnels,
and harness lifecycle.

## Use RPC as capability-based async calls

RPC requires compatibility date `2024-04-03` or later, or the `rpc` flag.
Public `WorkerEntrypoint` methods are callable through Service Bindings and
Durable Object methods through object bindings. Every remote call is async,
even when the implementation is synchronous.

Functions become callable stubs in their originating Worker. Classes crossing
RPC must extend `RpcTarget`; accessing a remote property also requires
`await`. Prefer one `RpcTarget` over plain objects containing many functions,
because each plain function creates a separate stub.

Use promise pipelining to avoid an unnecessary round trip:

```ts
using pendingCounter = env.COUNTERS.create();
await pendingCounter.increment();
```

Streams, `Request`, and `Response` transfer ownership. Clone or `tee()` values
that the sender still needs. Forwarded stubs cannot be persisted beyond the
participating execution contexts. RPC ignores Smart Placement.

Read [RPC and WebSockets](references/rpc-and-websockets.md) for stub lifetime,
parameter duplication, message limits, Python interoperability, and WebSocket
compatibility gates.

## Handle WebSocket gates explicitly

The maximum WebSocket message size is 32 MiB. Client failures surface as
catchable JavaScript exceptions.

From `2026-03-03`, close reasons over 123 UTF-8 bytes throw `SyntaxError`. From
`2026-03-10`, receipt of a Close frame sends the reciprocal frame and marks the
socket closed before the event. A proxy requiring the old half-open phase must
accept an upgrade-created socket with `{ allowHalfOpen: true }`.

From `2026-03-17`, `binaryType` defaults to `"blob"`. Set it to
`"arraybuffer"` before `accept()` when needed. Hibernatable Durable Object
handlers continue receiving `ArrayBuffer`.

## Generate runtime types from configuration

Prefer `wrangler types` so declarations match the Worker's compatibility date,
flags, bindings, and module rules:

```sh
wrangler types
wrangler types --check
```

Include `worker-configuration.d.ts` through `compilerOptions.types`; add
`@types/node` with Node.js compatibility. The root of
`@cloudflare/workers-types` v5 contains current stable types, experimental APIs
live under `/experimental`, and dated package entrypoints no longer exist.

## Validate before deployment

1. Confirm the active Wrangler configuration and compatibility date.
2. Run `wrangler types --check` when generated declarations are committed.
3. Exercise the production bundle through `createTestHarness()`.
4. Inspect startup cost with `wrangler check startup` when initialization is
   material.
5. Use local trace and log correlation to find binding and subrequest latency.
6. Deploy auxiliary Workers individually, then deploy the entry Worker.
7. Pass `--remote` only for resource commands intentionally targeting account
   data.
