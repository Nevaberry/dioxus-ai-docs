# Tracing, sampling, and spans

## Span send hooks

Beginning with `9.0.0-guide`, `beforeSendSpan` receives root spans as well as
child spans. Returning `null` can no longer drop a span; control which spans are
recorded through integration configuration, or use the filtering mechanism for
the active trace lifecycle.

## Custom scopes passed to startSpan

Outside Node.js, `startSpan({ scope })` clones the supplied scope in
`9.0.0-guide`. Mutating the current scope inside the callback remains local to
that callback. Make persistent changes on the original scope too:

```js
Sentry.startSpan({ name: "work", scope: customScope }, () => {
  Sentry.getCurrentScope().setTag("local", "yes");
  customScope.setTag("persistent", "yes");
});
```

## Sampling context migration

For `9.0.0-guide`, replace `samplingContext.request` with
`samplingContext.normalizedRequest`. `transactionContext` is removed; fields
such as `name` are top-level sampling-context properties. Replace
`enableTracing` with `tracesSampleRate`.

Node.js does not invoke `tracesSampler` for every span. An explicitly
`undefined` `tracesSampleRate` is treated as absent so downstream services can
make the sampling decision.

```js
Sentry.init({
  tracesSampler: ({ name, normalizedRequest }) =>
    name === "/health-check" ? 0 : 0.5,
});
```

In `9.0.0`, the sampler gains `inheritOrSampleWith` and receives
`parentSampleRate`, enabling explicit parent-aware decisions.

## Strict trace continuation

Core adds `strictTraceContinuation` in `10.0.0` for opting into stricter inbound
trace-continuation behavior:

```js
Sentry.init({ strictTraceContinuation: true });
```

## OpenAI instrumentation attributes

In `10.0.0`, OpenAI instrumentation records tool-call attributes and instruments
streamed Node.js responses. The response-object attribute is renamed from
`ai.response.object` to `gen_ai.response.object`; update telemetry queries and
processors using the old key.

## HTTP, cache, and state-graph attributes

At `10.68.0`, DataLoader spans set `cache.key`, and Redis delete operations are
captured as `cache.remove`. Parameterized `http.server` spans carry
`http.route`, `url.full`, and `url.path`; core fetch instrumentation also adds
`url.full`.

Core also exposes `instrumentStateGraph`, making state-graph instrumentation a
supported SDK capability.

## Stream mode configuration

The `streamed-spans` guidance applies to SDK 10.66.0 and newer. Stream mode
sends completed spans in periodic batches rather than retaining the whole
transaction until the root ends. It becomes the default in SDK 11. Service
spans replace transactions as service entry points, and the transaction mode's
1,000-span ceiling does not apply. Cordova and Electron do not support stream
mode.

```js
// Server and serverless SDKs
Sentry.init({ tracesSampleRate: 1, traceLifecycle: "stream" });

// Direct browser SDKs
Sentry.init({
  tracesSampleRate: 1,
  integrations: [Sentry.spanStreamingIntegration()],
});
```

Trace lifecycle is scoped per SDK, so services using transaction and stream
mode can participate in the same distributed trace. Completed spans flush
every five seconds by default, at 1,000 buffered spans, at the batch size limit,
and on `Sentry.flush()` or `Sentry.close()`.

## Stream-aware span hooks

In stream mode, wrap `beforeSendSpan` with `Sentry.withStreamedSpan()`. An
unwrapped hook makes the SDK fall back to transaction mode.

The wrapped callback receives `StreamedSpanJSON`, where:

- `description` becomes `name`.
- Processed `data` becomes raw `attributes`.
- `timestamp` becomes `end_timestamp`.
- `op` moves to `attributes["sentry.op"]`.
- Status is `"ok"` or `"error"`.

```js
Sentry.init({
  traceLifecycle: "stream",
  beforeSendSpan: Sentry.withStreamedSpan(span => {
    if (span.attributes?.["sentry.op"] === "db.query") {
      span.name = "[filtered]";
    }
    return span;
  }),
});
```

`beforeSendTransaction` is unavailable in stream mode. Migrate rules that drop
transactions to `ignoreSpans`.

## Start-time span dropping

Stream mode evaluates `ignoreSpans` when a span starts, using only its initial
name and attributes. Later renaming or enrichment cannot affect the choice.
Rules may be name strings, regular expressions, or objects matching a name and
attributes.

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

Dropping a service span also drops its descendants. Dropping a child reparents
its children to the nearest retained ancestor.

## Attributes replace span tags in stream mode

`Sentry.setTag()` and `Sentry.setTags()` continue to apply to errors but do not
apply their values to streamed spans. Record span-relevant metadata with the
attribute APIs as well.
