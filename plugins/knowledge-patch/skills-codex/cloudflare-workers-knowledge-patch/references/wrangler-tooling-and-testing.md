# Wrangler, Vite, Types, and Testing

Use this reference when upgrading Wrangler, running local or remote resource
commands, configuring the Workers Vite plugin, authenticating, generating
types, testing production builds, or inspecting startup and local traces.

Relevant source batches: `2025`, `2026`, and
`2026-07-30-2026-08-14`.

## Wrangler v4 runtime and bundling changes

Wrangler v4 follows the Node.js release lifecycle and no longer supports
Node.js 16. Its bundled esbuild moves from 0.17.19 to 0.24.

Wrangler minor releases may update pre-1.0 esbuild and thereby change bundling.
Pin and test Wrangler when bundle behavior is release-sensitive. Wildcard
dynamic imports now bundle every matching file; narrow their patterns when
unwanted matches would increase the bundle or expose code.

## Local is the resource-command default

Every Wrangler command supporting local and remote operation now defaults to
local mode. Add `--remote` when the command must touch account data:

```sh
wrangler kv key get --binding MY_KV "my-key" --remote
```

Audit KV and R2 scripts that previously relied on an implicit remote target.
This default reduces accidental account mutations but can make an old script
appear to return missing local data.

## Removed and deprecated Wrangler interfaces

Use these replacements:

| Removed or deprecated | Replacement |
| --- | --- |
| `legacy_assets` | Static Assets |
| `node_compat` | `nodejs_compat` |
| `getBindingsProxy()` | `getPlatformProxy()` |
| `publish` | `deploy` |
| `pages publish` | `pages deploy` |
| `generate` | `npm create cloudflare@latest` |
| `wrangler version` | `wrangler --version` |

Remove `usage_model`, which has no effect. Workers Sites and service
environments using `legacy_env` are deprecated; migrate them to Static Assets
and Wrangler environments.

## Workers Vite plugin

`@cloudflare/vite-plugin` v1 runs application code in `workerd` during Vite
development while preserving HMR. It supports SPA, SSR, static, and API
workloads.

```ts
import { cloudflare } from "@cloudflare/vite-plugin";
import { defineConfig } from "vite";

export default defineConfig({ plugins: [cloudflare()] });
```

## Vite configuration resolution and defaults

The entry Worker configuration resolves in this order:

1. `configPath`
2. `CLOUDFLARE_VITE_WRANGLER_CONFIG_PATH`
3. Root `wrangler.jsonc`, `wrangler.json`, or `wrangler.toml`
4. A `config` object or callback applied afterward

Defaults are:

- persisted state in `.wrangler/state`;
- inspector port 9229; and
- remote bindings enabled.

Plugin options can override these settings or expose development through a
tunnel.

## Auxiliary Workers

Every `auxiliaryWorkers` entry requires `configPath`, `config`, or both.
Requests still enter through the main Worker. Production builds place the
Workers in separate `dist` subdirectories.

`wrangler deploy` deploys only the entry Worker. Deploy each auxiliary Worker
separately with its generated configuration:

```sh
wrangler deploy -c dist/<auxiliary-worker>/wrangler.json
```

## Named authentication profiles

Wrangler supports named OAuth logins activated for a directory and its
descendants:

```sh
wrangler auth create client-a
wrangler auth activate client-a ~/clients/client-a
wrangler deploy --profile client-a
```

Keep `account_id` in a project when it should be constrained to one account.
`CLOUDFLARE_API_TOKEN` takes precedence over profiles in CI and other automated
environments.

## Device-code login

Wrangler 4.119.0 adds OAuth device login, avoiding a callback server on
`localhost:8976`. Use it from containers, SSH sessions, Codespaces, or a second
device. Suppress the automatic browser launch when needed:

```sh
npx wrangler login --device --browser=false
```

## Generate configuration-derived types

`wrangler types` derives `worker-configuration.d.ts` from the compatibility
date, compatibility flags, bindings, and module rules.

- Include the generated file through `compilerOptions.types`.
- Add `@types/node` when using the Node.js compatibility surface.
- Commit the generated type file if the project relies on checked-in output.
- Run `wrangler types --check` in CI to detect stale output.

`@cloudflare/workers-types` v5 exposes latest stable types at the package root
and experimental APIs at `/experimental`. Dated package entrypoints are gone.

## Test production builds

Wrangler's `createTestHarness()` runs Workers built by Wrangler or the Workers
Vite plugin from any Node.js test runner. It replaces `unstable_startWorker()`
and `unstable_dev()` for integration tests.

The harness can:

- load multiple Worker configurations;
- dispatch requests with `server.fetch()`;
- reset storage with `server.reset()`;
- expose runtime logs;
- mock outbound requests; and
- integrate with Playwright.

```ts
const server = createTestHarness({
  workers: [{ configPath: "./workers/api/wrangler.jsonc" }],
});
await server.listen();
const response = await server.fetch("http://api.example.com/");
await server.reset();
await server.close();
```

Always close the harness, and reset state between tests that require isolation.

## Inspect local traces and state

`wrangler dev` and `vite dev` automatically capture structured OpenTelemetry
traces and correlated console logs. Local Explorer displays automatic spans for
event handlers, outbound `fetch()` calls, and binding calls alongside custom
spans.

The `/cdn-cgi/explorer/api` endpoint exposes an OpenAPI schema and read-only
queries for traces, logs, and binding state. Its URL is advertised in the
terminal when an automated coding session is detected.

## Inspect Worker startup

Wrangler 4.116.0 extends `wrangler check startup` with raw and gzip bundle sizes
and a local CPU summary split into sampled, active, garbage-collection, and idle
time. It continues to write `worker-startup.cpuprofile` for Chrome DevTools or
VS Code.

Use the local durations to locate expensive startup work. They are not
authoritative production startup measurements.

## Select the Workers Builds Node.js version

Workers Builds defaults to Node.js 24.18.0. Node.js 22.23.2 and 24.18.0 are
preinstalled in the build image. Override selection with `NODE_VERSION`,
`.nvmrc`, or `.node-version` when the build requires another release.
