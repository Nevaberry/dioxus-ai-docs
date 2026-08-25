# Vite development and testing

This reference covers Vite and production-build test guidance from batches
`2025` and `2026`, plus local observability from batch
`2026-07-30-2026-08-14`.

## Run Workers in Vite

`@cloudflare/vite-plugin` v1 runs application code in `workerd` during Vite
development while retaining HMR. It supports SPA, SSR, static, and API
workloads.

```ts
import { cloudflare } from "@cloudflare/vite-plugin";
import { defineConfig } from "vite";

export default defineConfig({ plugins: [cloudflare()] });
```

## Resolve plugin configuration

The entry Worker configuration is resolved in this order:

1. The plugin's `configPath`.
2. `CLOUDFLARE_VITE_WRANGLER_CONFIG_PATH`.
3. A root `wrangler.jsonc`, `wrangler.json`, or `wrangler.toml`.

A `config` object or callback is applied after file resolution. By default,
state persists to `.wrangler/state`, the inspector listens on port 9229, and
remote bindings are enabled. Plugin options can override those defaults or
expose development through a tunnel.

## Configure auxiliary Workers

Every `auxiliaryWorkers` entry requires `configPath`, `config`, or both.
Requests still enter through the main Worker. Builds put each Worker in its own
`dist` subdirectory.

`wrangler deploy` deploys only the entry Worker. Deploy every auxiliary Worker
separately:

```sh
wrangler deploy -c dist/<auxiliary-worker>/wrangler.json
```

## Test production builds

Wrangler's `createTestHarness()` starts Workers built by Wrangler or the Vite
plugin from any Node.js test runner. It replaces `unstable_startWorker()` and
`unstable_dev()` for integration testing.

A harness can load multiple Worker configurations, dispatch requests through
`server.fetch()`, clear storage with `server.reset()`, expose runtime logs,
mock outbound requests, and support Playwright.

```ts
const server = createTestHarness({
  workers: [{ configPath: "./workers/api/wrangler.jsonc" }],
});
await server.listen();
const response = await server.fetch("http://api.example.com/");
await server.reset();
await server.close();
```

Always close the harness. Reset storage between cases that require isolation,
and exercise the same built output intended for deployment.

## Inspect local traces and logs

`wrangler dev` and `vite dev` automatically capture structured OpenTelemetry
traces and correlated console logs. Local Explorer displays automatic spans for
handlers, outbound `fetch()` calls, and binding calls alongside custom spans.

Its `/cdn-cgi/explorer/api` endpoint exposes an OpenAPI schema and read-only
queries for traces, logs, and binding state. The endpoint is advertised in the
terminal when an agent session is detected.
