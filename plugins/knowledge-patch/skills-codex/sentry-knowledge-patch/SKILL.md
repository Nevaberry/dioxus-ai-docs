---
name: sentry-knowledge-patch
description: Sentry JavaScript SDK
version: 10.68.0
license: MIT
metadata:
  author: Nevaberry
---


# Sentry JavaScript SDK Knowledge Patch

Use this skill when upgrading, configuring, or debugging Sentry JavaScript SDKs,
especially when code crosses major SDK versions, framework wrappers, tracing,
structured logs, or modern server runtimes.

## Reference index

| Reference | Topics |
| --- | --- |
| [migrations-and-runtime.md](references/migrations-and-runtime.md) | Runtime floors, removed packages and APIs, client internals, OpenTelemetry compatibility |
| [frameworks-and-builds.md](references/frameworks-and-builds.md) | Framework wrappers, source maps, serverless runtimes, build integrations |
| [logging-privacy-and-events.md](references/logging-privacy-and-events.md) | Structured logs, privacy, sessions, feedback, console and event behavior |
| [tracing-and-spans.md](references/tracing-and-spans.md) | Sampling, propagation, span hooks, stream mode, telemetry attributes |
| [modern-server-frameworks.md](references/modern-server-frameworks.md) | Elysia, Hono, Nitro, and TanStack Start setup |

## Upgrade triage

Before changing code:

1. Identify the installed Sentry SDK major and every framework-specific Sentry
   package.
2. Check the application runtime, framework, router, Prisma, OpenTelemetry, and
   bundler-plugin versions against the relevant compatibility notes.
3. Search for removed options, imports, integrations, wrappers, and low-level
   extension types before updating dependencies.
4. Review source-map generation, upload, deletion, and release naming as one
   build pipeline.
5. Verify sampling, session tracking, error filtering, and privacy behavior with
   focused tests after migration.

## Major migration quick reference

### Runtime floors

SDK packages may emit ES2020. Node-based packages require Node.js 18.0.0, while
the ESM-only Astro, Nuxt, and SvelteKit packages require Node.js 18.19.1. Deno
2.0 and TypeScript 5.0.4 are the corresponding floors. Transpile for browser
targets older than Chrome or Edge 80, Safari 14, iOS Safari 14.4, Firefox 74,
Opera 67, or Samsung Internet 13.

### Removed tracing switches and sampler fields

Replace `enableTracing` with `tracesSampleRate`. In `tracesSampler`, use
`normalizedRequest` instead of `request`, and read transaction fields such as
`name` directly from the sampling context instead of `transactionContext`.
Node.js invokes the sampler for trace decisions rather than once per span.

```js
Sentry.init({
  tracesSampler: ({ name, normalizedRequest, inheritOrSampleWith }) =>
    name === "/health-check" ? 0 : inheritOrSampleWith(0.5),
});
```

An explicitly `undefined` `tracesSampleRate` is treated as absent, allowing a
downstream service to make its own sampling decision.

### Span hooks cannot drop spans

`beforeSendSpan` receives root and child spans but cannot drop one by returning
`null`. Configure recording or use the appropriate filtering feature instead.
When stream mode is enabled, wrap the hook with `Sentry.withStreamedSpan()` or
the SDK falls back to transaction mode.

### Session tracking is integration-based

Remove `autoSessionTracking`. Browser sessions use
`browserSessionIntegration`, server request sessions use `httpIntegration`, and
Node.js process sessions use the default `processSessionIntegration`.

```js
Sentry.init({
  integrations: [
    Sentry.httpIntegration({ trackIncomingRequestsAsSessions: false }),
  ],
});
```

### Core package and client changes

Do not import from the unpublished `@sentry/utils`; move remaining imports from
it, and deprecated `@sentry/types` imports, to `@sentry/core`. Removed hub and
metrics APIs have no direct compatibility shim. Custom clients use `Client`
directly; `BaseClient` is no longer available in the next major line.

### OpenTelemetry boundary

Node-based v10 packages require the OpenTelemetry 2.x/0.20x generation. Stay on
the prior Sentry major when OpenTelemetry 2 is unavailable, or use
`@sentry/node-core` where its wider peer ranges fit. Pass custom instrumentation
through `openTelemetryInstrumentations`; `addOpenTelemetryInstrumentation()`
is removed.

### Feedback and browser privacy

Replace `captureUserFeedback()` with `captureFeedback()` and rename payload
`comments` to `message`. Browser SDKs no longer request backend IP inference by
default; enable `sendDefaultPii` only when intended. Express user data is not
copied from `request.user`; call `Sentry.setUser()` explicitly.

### Framework wrapper selection

Use the explicit `V6` or `V7` React Router wrapper matching the installed router
major. NestJS applications use `@sentry/nestjs`, `SentryGlobalFilter`, and
`@SentryExceptionCaptured`. SolidStart uses `withSentry`; Vue tracing options
belong under `vueIntegration({ tracingOptions })`.

### Next.js configuration

Pass SDK options directly to `withSentryConfig`; do not use the discontinued
`sentry` property in Next config. Set a deterministic release explicitly when
needed. The removed `hideSourceMaps` option has no replacement.

```js
export default withSentryConfig(nextConfig, {
  release: { name: "my-release" },
  sourcemaps: { deleteSourcemapsAfterUpload: false },
});
```

## High-value current capabilities

### Structured logs

Enable top-level `enableLogs` and `beforeSendLog`. Emit logs with
`Sentry.logger` and attach searchable attributes as the second argument; use
`Sentry.logger.fmt` for parameterized messages.

```js
Sentry.init({ enableLogs: true, beforeSendLog: log => log });
Sentry.logger.info("Order created", { orderId: "order_456" });
Sentry.logger.info(Sentry.logger.fmt`User ${userId} purchased ${productName}`);
```

Use `Sentry.setAttribute()` or `Sentry.setAttributes()` for attributes shared by
logs and metrics. Scope methods provide app-wide or operation-local placement.

### Streamed spans

SDKs that support stream mode can send completed spans in periodic batches
instead of retaining the full transaction. Configure `traceLifecycle: "stream"`
on server SDKs, or install `spanStreamingIntegration()` in direct browser SDKs.

```js
Sentry.init({ tracesSampleRate: 1, traceLifecycle: "stream" });
```

Use `ignoreSpans` for start-time dropping. Rules see only the initial name and
attributes. A dropped service span drops descendants; dropping a child reparents
its retained children. Record span metadata with attributes because scope tags
do not propagate to spans in stream mode.

### Framework data controls

Elysia, Hono, Nitro, and TanStack Start accept `dataCollection` controls for
automatic request enrichment. Disable user data and request bodies explicitly
where collection is not permitted.

```js
Sentry.init({
  dataCollection: { userInfo: false, httpBodies: [] },
});
```

### Error selection and trace continuation

Use `strictTraceContinuation` when stricter inbound trace continuation is
required. Fastify and supported modern framework integrations expose
`shouldHandleError` for application-specific capture policy.

```js
Sentry.init({
  strictTraceContinuation: true,
  integrations: [
    Sentry.fastifyIntegration({
      shouldHandleError: error => shouldReport(error),
    }),
  ],
});
```

## Verification checklist

- Build every client and server bundle and inspect source-map output and cleanup.
- Exercise one sampled and one unsampled distributed trace across service
  boundaries.
- Confirm error hooks, framework filters, and serverless flushes complete before
  responses terminate.
- Verify session counts after replacing legacy automatic tracking.
- Inspect an event for user, IP, request-body, stack-variable, and console
  handling according to the intended privacy policy.
- Query logs and spans using the new attribute names before changing dashboards.
- Test development, preview, and production entry points when instrumentation is
  preloaded with `--import`.
