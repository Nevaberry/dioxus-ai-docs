---
name: sentry-knowledge-patch
description: Sentry JavaScript SDK
version: "10.68.0"
license: MIT
metadata:
  author: Nevaberry
---


# Sentry JavaScript SDK

Use this skill when upgrading or configuring Sentry JavaScript SDK packages,
framework integrations, tracing, logs, source maps, or serverless runtimes.
Check the application's installed SDK and framework versions before applying
version-dependent guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migrations and runtime compatibility](references/migrations-and-runtime.md) | Runtime floors, removed APIs, package changes, sessions, browser behavior |
| [Tracing and performance](references/tracing-and-performance.md) | Sampling, span hooks, OpenTelemetry, stream mode, trace attributes |
| [Telemetry data](references/telemetry-data.md) | Logs, shared attributes, console capture, feedback, PII, stack variables |
| [Framework integrations](references/framework-integrations.md) | Prisma, NestJS, routers, Vue, modern server frameworks |
| [Build and serverless](references/build-and-serverless.md) | Source maps, bundler plugins, Lambda, Cloudflare, Cloud Run, flushing |

## Migration priorities

### Meet the runtime and framework floors

Current SDK packages may emit ES2020. Use Node.js 18.0.0 or newer, except
Astro, Nuxt, and SvelteKit packages require Node.js 18.19.1 because they are
ESM-only. Deno 2.0 and TypeScript 5.0.4 are the other minimums. Transpile the
SDK when supporting browsers older than Chrome/Edge 80, Safari 14, iOS Safari
14.4, Firefox 74, Opera 67, or Samsung Internet 13.

Do not upgrade until incompatible framework versions have moved past Remix
1.x, TanStack Router 1.63.0, SvelteKit 1.x, Ember 3.x, and Prisma 5.x.

### Replace removed initialization options

Use `tracesSampleRate` instead of `enableTracing`. Replace
`samplingContext.request` with `normalizedRequest`; sampling-context fields
formerly under `transactionContext`, including `name`, are top-level.

Replace `autoSessionTracking` by configuring the owning integration:

- Browser sessions: include or remove `browserSessionIntegration`.
- Incoming server requests: use
  `httpIntegration({ trackIncomingRequestsAsSessions: false })` to disable.
- Node.js process sessions: use the default `processSessionIntegration`.

Move `_experiments.enableLogs` and `_experiments.beforeSendLog` to top-level
`enableLogs` and `beforeSendLog`. Remove Replay's
`_experiments.autoFlushOnFeedback`; feedback flushes Replay automatically.

### Replace removed core APIs and packages

Import remaining utility and type exports from `@sentry/core`:
`@sentry/utils` is gone and `@sentry/types` is deprecated. The metrics API,
Hub APIs, `debugIntegration`, and `sessionTimingIntegration` are gone. Use send
hooks for debugging and set event context explicitly for session timing.

Custom clients must now use `Client` directly: v9 first required extending
`BaseClient`, and v10 removed `BaseClient`. Use `debug` and
`SentryDebugLogger` instead of `logger` and the `Logger` type.

Use `captureFeedback({ message })` instead of
`captureUserFeedback({ comments })`. See the migration reference for the full
set of removed helpers and type changes.

## Tracing quick reference

### Configure sampling at the trace boundary

Node.js no longer calls `tracesSampler` for every span. The callback receives
`parentSampleRate` and `inheritOrSampleWith` for parent-aware decisions. An
explicitly `undefined` `tracesSampleRate` behaves as absent, allowing a
downstream service to decide.

```js
Sentry.init({
  tracesSampler: ({ name, normalizedRequest, inheritOrSampleWith }) =>
    name === "/health-check" ? 0 : inheritOrSampleWith(0.5),
});
```

Use `strictTraceContinuation: true` when the application should apply stricter
trace-continuation rules.

### Treat `beforeSendSpan` as mutation-only

`beforeSendSpan` receives root and child spans and cannot drop one by returning
`null`. Control recording with integration configuration, or use
`ignoreSpans` where supported.

Outside Node.js, `startSpan({ scope })` clones the supplied scope. Mutations to
the current scope stay within the callback; also mutate the original scope for
persistent changes.

### Opt into streamed spans deliberately

For SDK 10.66.0 and newer, server SDKs enable stream mode with
`traceLifecycle: "stream"`; direct browser SDKs add
`spanStreamingIntegration()`. Cordova and Electron do not support it.

```js
Sentry.init({
  tracesSampleRate: 1,
  traceLifecycle: "stream",
  beforeSendSpan: Sentry.withStreamedSpan((span) => span),
});
```

Wrap `beforeSendSpan` with `withStreamedSpan`; an unwrapped hook causes a
fallback to transaction mode. `beforeSendTransaction` is unavailable, so move
transaction-dropping rules to `ignoreSpans`. Those rules run when a span starts
and can inspect only its initial name and attributes.

Stream mode does not copy `setTag` or `setTags` values to spans. Record
span-relevant data with attributes as well; tags still apply to errors.

## Logs quick reference

Enable logs, then emit structured messages through `Sentry.logger` at
`trace`, `debug`, `info`, `warn`, `error`, or `fatal`. The second argument
holds searchable attributes; `Sentry.logger.fmt` turns interpolated values
into searchable attributes.

```js
Sentry.init({ enableLogs: true });
Sentry.logger.info("Order created", { orderId: "order_456" });
Sentry.logger.info(Sentry.logger.fmt`User ${userId} purchased ${productName}`);
```

Use `Sentry.setAttribute()` and `Sentry.setAttributes()` for attributes shared
by logs and metrics. Global-scope values are application-wide; current-scope
values are operation-local. Accepted values are strings, numbers, booleans,
and arrays of those types.

`consoleLoggingIntegration({ levels })` converts selected console calls to
logs. Additional console arguments become `message.parameter.N` attributes.
Consola applications can attach `Sentry.createConsolaReporter()`.

Logs emitted inside an active span carry `sentry.trace.parent_span_id`; logs
inside a supported active Session Replay also carry `sentry.replay_id`.

## Framework quick reference

### Pick explicit integrations and wrappers

- Prisma's bundled integration targets Prisma 6. For another version, pass a
  matching `PrismaInstrumentation` through `prismaInstrumentation`.
- NestJS applications use `@sentry/nestjs`, `SentryGlobalFilter`, and
  `@SentryExceptionCaptured`; the global filter also handles WebSocket errors.
- React Router uses explicit `V6` or `V7` variants of `wrapUseRoutes` and
  `wrapCreateBrowserRouter`.
- Vue component tracing belongs under
  `vueIntegration({ tracingOptions: ... })`; include `"update"` in `hooks`
  when update spans are required.
- Fastify's `shouldHandleError` selects which errors its handler captures.

### Initialize server frameworks before application code

The Elysia, Hono, Nitro, and TanStack Start SDKs provide native integrations
and `dataCollection` controls. To prevent automatic user and request-body
collection, initialize with:

```js
Sentry.init({ dataCollection: { userInfo: false, httpBodies: [] } });
```

Preload Node instrumentation with `--import` where a framework requires it.
Hono needs a runtime-specific entry point and same-version peer SDK. Nitro
wraps its config with `withSentryConfig`. TanStack Start places
`sentryTanstackStart()` last in the Vite plugin list and wraps an explicit
server fetch handler with `wrapFetchWithSentry`.

## Build and serverless quick reference

### Make source-map behavior explicit

Meta-framework SDKs preserve an explicit source-map setting. When generation
is unspecified, they enable maps, upload them, and delete them; explicitly
enabled maps are not deleted automatically. Use `filesToDeleteAfterUpload` for
custom cleanup.

Next.js uses client `hidden-source-map` and server `source-map` unless
`sourcemaps.disable` is set. It deletes client maps after upload unless
`sourcemaps.deleteSourcemapsAfterUpload` is false. Pass Sentry options directly
to `withSentryConfig`; `hideSourceMaps` and the nested Next config `sentry`
property are removed. Set a deterministic release name rather than relying on
the Next.js Build ID.

### Use the correct serverless behavior

The AWS Lambda v10 layer is `SentryNodeServerlessSDKv10`, unified for ESM and
CommonJS. React Router serverless loaders, actions, and Vercel handlers flush
automatically, as do Next.js route handlers. Unified environment detection
recognizes Cloud Run.

The Cloudflare Vite Orchestrion plugin reads Wrangler configuration, resolves
the options module, wraps the worker entry, and instruments Durable Objects,
`WorkerEntrypoint`, Workflows, and Agents. Supply `wranglerConfigPath` when the
desired Wrangler configuration is not the default.

Review the build reference for source-map cleanup, externalization warnings,
Cloudflare method semantics, local Spotlight forwarding, and upload-failure
behavior.
