# Tracing and Performance

## Span hooks and scoped spans (9.0.0-guide)

`beforeSendSpan` receives root spans as well as child spans. Returning `null`
cannot drop a span; control which spans are recorded with integration
configuration.

Outside Node.js, `startSpan({ scope })` clones the supplied scope. Mutating the
current scope inside the callback remains local. Also mutate the original
scope when a value must persist afterward.

```js
startSpan({ name: "work", scope: customScope }, () => {
  getCurrentScope().setTag("local", "yes");
  customScope.setTag("persistent", "yes");
});
```

## Sampling configuration and context

Replace `samplingContext.request` with `normalizedRequest`.
`transactionContext` is removed; values such as `name` are now top-level
sampling-context fields. Replace `enableTracing` with `tracesSampleRate`.

Node.js does not invoke `tracesSampler` for every span. An explicitly
`undefined` `tracesSampleRate` counts as absent, so a downstream service may
make the sampling decision.

Since 9.0.0, the callback also receives `parentSampleRate` and the
`inheritOrSampleWith` helper for parent-aware sampling:

```js
Sentry.init({
  tracesSampler: ({ name, normalizedRequest, inheritOrSampleWith }) =>
    name === "/health-check" ? 0 : inheritOrSampleWith(0.5),
});
```

`strictTraceContinuation: true` opts into stricter trace continuation (since
10.0.0).

## OpenTelemetry initialization

`addOpenTelemetryInstrumentation()` is removed. Pass custom instrumentation
through `openTelemetryInstrumentations` during initialization:

```js
Sentry.init({
  openTelemetryInstrumentations: [new GenericPoolInstrumentation()],
});
```

`skipOpenTelemetrySetup: true` also configures
`httpIntegration({ spans: false })` by default. `registerEsmLoaderHooks`
accepts only a boolean or `undefined` and defaults to wrapping modules used by
OpenTelemetry instrumentation.

## Streamed spans

### Enable stream mode

SDK 10.66.0 and newer can send completed spans in periodic batches instead of
holding an entire transaction until the root ends. Stream mode becomes the
default in SDK 11. Service spans replace transactions as service entry points,
and the transaction mode's 1,000-span ceiling does not apply. Cordova and
Electron do not support it.

```js
// Server and serverless SDKs
Sentry.init({ tracesSampleRate: 1, traceLifecycle: "stream" });

// Direct browser SDKs
Sentry.init({
  tracesSampleRate: 1,
  integrations: [Sentry.spanStreamingIntegration()],
});
```

Mode is scoped to each SDK, so transaction-mode and stream-mode services can
share a distributed trace. Completed spans flush every five seconds by
default, at 1,000 buffered spans, at the batch-size limit, or on
`Sentry.flush()` and `Sentry.close()`.

### Filter and transform streamed spans

Wrap `beforeSendSpan` in `Sentry.withStreamedSpan()`; leaving it unwrapped
causes fallback to transaction mode. The hook receives `StreamedSpanJSON` with
these field changes:

| Transaction representation | Stream representation |
| --- | --- |
| `description` | `name` |
| Processed `data` | Raw `attributes` |
| `timestamp` | `end_timestamp` |
| `op` | `attributes["sentry.op"]` |
| Status values | `"ok"` or `"error"` |

```js
Sentry.init({
  traceLifecycle: "stream",
  beforeSendSpan: Sentry.withStreamedSpan((span) => {
    if (span.attributes?.["sentry.op"] === "db.query") {
      span.name = "[filtered]";
    }
    return span;
  }),
});
```

`beforeSendTransaction` is unavailable in stream mode. Move dropping rules to
`ignoreSpans`.

### Drop spans at start time

`ignoreSpans` evaluates when the span starts, using only its initial name and
attributes. Later renaming and enrichment cannot affect the decision. Rules
may be name strings, regular expressions, or name-and-attribute objects.

```js
Sentry.init({
  traceLifecycle: "stream",
  ignoreSpans: [
    "healthcheck",
    /^GET \/api\/v1\/internal/,
    { name: /^GET \//, attributes: { "http.route": "/api/status" } },
  ],
});
```

Dropping a service span also drops all descendants. Dropping a child reparents
its children to the nearest retained ancestor.

### Use attributes rather than span tags

Stream mode does not apply `Sentry.setTag()` or `Sentry.setTags()` values to
spans, although they still apply to errors. Also record span-relevant values
with attribute APIs.

## Instrumentation semantics

### AI and cache spans

OpenAI instrumentation records tool-call attributes and streamed responses in
Node.js. The response-object attribute is renamed from `ai.response.object` to
`gen_ai.response.object`; update queries using the old key.

DataLoader spans set `cache.key`, and Redis delete operations use
`cache.remove` (10.68.0).

### HTTP and state graphs

Parameterized `http.server` spans carry `http.route`, `url.full`, and
`url.path`; core fetch instrumentation adds `url.full` (10.68.0). Core also
exports `instrumentStateGraph` for supported state-graph instrumentation.

### Router and middleware traces

React Router uses its instrumentation API by default; custom setup must not
assume that the older path is selected automatically (10.68.0).

Next.js middleware wrappers no longer create tracing in
10.69.0-10.70.0. Do not rely on those wrappers for middleware spans.

## Error sampling order

Error sampling runs after `beforeSend` in 10.69.0-10.70.0, while session
updates remain preserved. A `beforeSend` hook may therefore execute for an
event that is subsequently sampled out.
