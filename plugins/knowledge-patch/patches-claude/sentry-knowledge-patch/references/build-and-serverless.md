# Build, Source Maps, and Serverless Deployments

## Meta-framework source maps (9.0.0-guide)

Meta-framework SDKs preserve explicitly enabled or disabled source-map build
settings rather than rewriting them.

- When generation is unspecified, the SDK enables source maps and deletes
  them after upload.
- When generation is explicitly enabled, the SDK preserves the emission mode
  and does not delete maps automatically.
- Use `filesToDeleteAfterUpload` for custom cleanup.

## Next.js build configuration

Next.js enables client `hidden-source-map` and server `source-map` output
unless `sourcemaps.disable` is set. Client maps are deleted after upload by
default; set `sourcemaps.deleteSourcemapsAfterUpload: false` to keep them.

The removed `hideSourceMaps` option has no replacement. The SDK no longer
falls back to the nondeterministic Next.js Build ID for its release. Set a
release name explicitly or provide another deterministic release source.

The Next config's discontinued nested `sentry` property must become options
passed directly to `withSentryConfig`:

```js
export default withSentryConfig(nextConfig, {
  release: { name: "my-release" },
  sourcemaps: { deleteSourcemapsAfterUpload: false },
});
```

## Bundler plugin and instrumentation checks

SDK v10 upgrades Sentry bundler plugins to the v4 major line (10.0.0). Upgrade
direct pins and SDK packages together.

Server instrumentation warns when a bundler marks an instrumented module as
external (since 10.68.0). Treat the warning as an instrumentation failure
risk: bundled wrappers cannot instrument a module they do not load.

## AWS Lambda layers

The v9 Lambda layer is `SentryNodeServerlessSDKv9`; continuing v8 updates use
`SentryNodeServerlessSDKv8` (9.0.0-guide).

The v10 layer is `SentryNodeServerlessSDKv10` and is shared by ESM and
CommonJS deployments (10.0.0).

## Serverless flushing and environment detection

React Router automatically flushes for serverless loaders and actions and for
Vercel request handlers. Next.js route handlers also flush automatically
(10.0.0).

Unified serverless-environment detection recognizes Cloud Run, so
serverless-specific behavior applies there without custom detection.

## Cloudflare Vite auto-instrumentation

The `@sentry/cloudflare/vite` Orchestrion plugin reads Wrangler configuration,
resolves the Sentry options module, wraps the worker entry with `withSentry`,
and instruments Durable Object, `WorkerEntrypoint`, and Workflow classes
(10.68.0).

The plugin also instruments Cloudflare `Agent` classes automatically in
10.69.0-10.70.0. Set its `wranglerConfigPath` option when a non-default
Wrangler configuration must be selected explicitly.

## Cloudflare Agents and development tools

`instrumentAgentWithSentry` wraps `Agent` classes from the Cloudflare `agents`
SDK in the same style as `instrumentDurableObjectWithSentry`. It creates spans
for `@callable` RPC methods and derives `conversationId` from the agent name.
Clearing a chat rotates the conversation ID.

The Cloudflare SDK can forward local-development events through the Spotlight
integration.

## Cloudflare runtime semantics

Workflow instrumentation accepts non-UUID instance IDs. Durable Object
instrumentation preserves synchronous methods instead of converting them to
asynchronous functions (10.0.0).

## Framework build behavior

### SolidStart

Replace the removed `sentrySolidStartVite` export by wrapping the SolidStart
config with `withSentry`; pass build-time Sentry options as the second
argument.

### Nitro

`withSentryConfig` registers the Sentry module, enables tracing channels, and
uploads hidden source maps before deleting them by default. An explicit Nitro
`sourcemap` setting is respected. Preload the root `instrument.mjs` with
`--import` in development, preview, and production.

### TanStack Start

Place `sentryTanstackStart()` last in the Vite plugin list. It manages
production source-map uploads and tracing middleware. Copy and preload
`instrument.server.mjs` in the deployed output for full server
instrumentation.

### Remix

Sentry CLI source-map upload failures during Remix builds are silent rather
than build-failing (10.0.0). Monitor upload results separately when missing
source maps must block a release.

## Next.js middleware tracing

Next.js middleware wrappers no longer add tracing in 10.69.0-10.70.0. Build
and telemetry validation must not treat wrapper installation as proof that
middleware spans are produced.
