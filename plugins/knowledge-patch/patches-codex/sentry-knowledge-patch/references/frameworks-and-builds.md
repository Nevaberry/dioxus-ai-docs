# Frameworks, builds, and serverless runtimes

## Source-map behavior across meta-frameworks

From `9.0.0-guide`, meta-framework SDKs preserve explicitly enabled or disabled
source-map build settings instead of rewriting them. When generation is
unspecified, the SDK enables source maps and deletes them after upload. When
source maps are explicitly enabled, it preserves the emission mode and does not
delete them automatically; use `filesToDeleteAfterUpload` for custom cleanup.

## Next.js builds and releases

For `9.0.0-guide`, Next.js enables client `hidden-source-map` and server
`source-map` builds unless `sourcemaps.disable` is set. Client maps are deleted
after upload unless `sourcemaps.deleteSourcemapsAfterUpload` is `false`. The
removed `hideSourceMaps` option has no replacement.

The SDK no longer falls back to the nondeterministic Next.js Build ID for the
release. Set a release name explicitly when needed. Replace the discontinued
`sentry` property in Next config with options passed directly to
`withSentryConfig`:

```js
export default withSentryConfig(nextConfig, {
  release: { name: "my-release" },
  sourcemaps: { deleteSourcemapsAfterUpload: false },
});
```

Next.js route handlers flush automatically in `10.0.0`. In
`10.69.0-10.70.0`, middleware wrappers stop adding tracing; application logic
and telemetry assertions must not depend on those wrappers to create middleware
traces.

## SolidStart

`sentrySolidStartVite` is no longer exported in `9.0.0-guide`. Wrap the
SolidStart config with `withSentry`, passing build-time options second:

```ts
export default defineConfig(
  withSentry(solidStartConfig, sentryBuildOptions),
);
```

In `9.0.0`, server setup defaults to `--import` and adds
`autoInjectServerSentry`, including the
`autoInjectServerSentry: "experimental_dynamic-import"` mode.

## NestJS

The Node SDK's `nestIntegration` and `setupNestErrorHandler` are removed in
`9.0.0-guide`; migrate to `@sentry/nestjs`. Replace `@WithSentry` with
`@SentryExceptionCaptured`, use `SentryGlobalFilter` for either a global generic
or GraphQL filter, and remove `SentryService` and `SentryTracingInterceptor`.

As of `10.68.0`, `SentryGlobalFilter` also supports WebSocket errors, so NestJS
WebSocket failures can flow through the global filter.

## React Router and serverless flushing

The generic React helpers `wrapUseRoutes` and `wrapCreateBrowserRouter` are
removed in `9.0.0-guide`. Select the explicit `V6` or `V7` variant of each
wrapper to match the installed React Router major.

React Router flushes automatically for serverless loaders and actions and for
Vercel request handlers in `10.0.0`. Starting with `10.68.0`, React Router uses
its instrumentation API by default; custom setup must not assume that the older
instrumentation path is selected automatically.

## Vue, Nuxt, SvelteKit, and Remix

Vue component tracing belongs under `vueIntegration({ tracingOptions })` from
`9.0.0-guide`, including in Nuxt. Update spans are emitted only when `"update"`
is present in `tracingOptions.hooks`. Pinia `stateTransformer` receives the
combined state keyed by store ID. Remove `logErrors`; the Vue handler always
propagates to a user handler or rethrows.

```js
Sentry.init({
  integrations: [
    Sentry.vueIntegration({
      tracingOptions: {
        trackComponents: true,
        hooks: ["mount", "update", "unmount"],
      },
    }),
  ],
});
```

Nuxt adds an `enabled` switch in `9.0.0`, and its `SourceMapsOptions` adds
`silent`, `errorHandler`, and `release`.

SvelteKit removes `fetchProxyScriptNonce` in `9.0.0-guide`; use a CSP script
hash or disable fetch-proxy injection. In `9.0.0`, the script is injected only
for SvelteKit versions below 2.16.0.

Remix removes `autoInstrumentRemix` and always behaves as though it were `true`
in `9.0.0-guide`. In `10.0.0`, Sentry CLI failures during Remix source-map
upload become silent rather than failing the build.

## Bundler plugin boundary and warnings

SDK v10 upgrades its bundler plugins to their v4 major line (`10.0.0`). Account
for the major boundary when plugins are pinned or consumed directly.

At `10.68.0`, server instrumentation warns when a bundler marks an instrumented
module as external. Treat the warning as a sign that the module may not be
instrumented and adjust externalization where appropriate.

## Astro routes

The `10.0.0` Astro integration parameterizes Astro 5 request routes and
client-side routes, constructing the parameterized request route at runtime.

## Fastify error selection

`fastifyIntegration` gains `shouldHandleError` in `10.0.0`, allowing the
integration error handler to select captured errors:

```js
Sentry.init({
  integrations: [
    Sentry.fastifyIntegration({
      shouldHandleError: error => shouldReport(error),
    }),
  ],
});
```

## Serverless detection and runtime semantics

Serverless-environment detection is unified and recognizes Cloud Run in
`10.0.0`, so serverless-specific behavior applies automatically there.

Cloudflare Workflow instrumentation accepts non-UUID instance IDs, and Durable
Object instrumentation preserves synchronous methods instead of turning them
asynchronous (`10.0.0`).

## Cloudflare Vite instrumentation

The `@sentry/cloudflare/vite` Orchestrion plugin added in `10.68.0` reads
Wrangler configuration, resolves the Sentry options module, wraps the worker
entry with `withSentry`, and automatically instruments Durable Object,
`WorkerEntrypoint`, and Workflow classes.

In `10.69.0-10.70.0`, Vite options accept `wranglerConfigPath` for explicitly
selecting a Wrangler configuration. The Cloudflare SDK can also send local
development events through the Spotlight integration.

## Cloudflare Agents

`10.69.0-10.70.0` adds `instrumentAgentWithSentry` for `Agent` classes from the
`agents` SDK. It behaves like `instrumentDurableObjectWithSentry`, creates spans
for `@callable` RPC methods, and derives `conversationId` from the agent name.
The Sentry Vite plugin instruments Agents automatically. Clearing a chat rotates
the conversation ID.
