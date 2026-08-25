# Logging, privacy, and events

## Structured logger and parameterized messages

The `structured-logs` API exposes `Sentry.logger` at `trace`, `debug`, `info`,
`warn`, `error`, and `fatal` levels. Every call requires a message; pass
searchable attributes as the second argument. The `Sentry.logger.fmt` tagged
template extracts interpolated values as searchable attributes.

```js
Sentry.logger.info("Order created", { orderId: "order_456" });
Sentry.logger.info(
  Sentry.logger.fmt`User ${userId} purchased ${productName}`,
);
```

The v10 initialization options `enableLogs` and `beforeSendLog` are top-level,
not under `_experiments` (`10.0.0-guide`):

```js
Sentry.init({
  enableLogs: true,
  beforeSendLog: log => log,
});
```

Replay's removed `_experiments.autoFlushOnFeedback` option is unnecessary;
feedback flushes Replay by default.

## Shared log and metric attributes

Since 10.61.0, as recorded in `structured-logs`, `Sentry.setAttribute()` and
`Sentry.setAttributes()` add shared attributes to logs and metrics. Values may
be strings, numbers, booleans, or arrays of those types. The same methods on the
global or current scope place attributes app-wide or operation-locally.

```js
Sentry.setAttributes({ org_id: user.orgId, user_tier: user.tier });
Sentry.withScope(scope => {
  scope.setAttribute("request_id", req.id);
  Sentry.logger.info("Processing order");
});
```

## Console and Consola ingestion

`consoleLoggingIntegration({ levels })` converts selected console calls to logs.
Since 10.13.0, additional arguments become searchable
`message.parameter.N` attributes. Since 10.12.0, Consola applications can attach
`Sentry.createConsolaReporter()` instead (`structured-logs`).

```js
Sentry.init({
  integrations: [
    Sentry.consoleLoggingIntegration({ levels: ["log", "warn", "error"] }),
  ],
});
```

Logs emitted during an active span automatically receive
`sentry.trace.parent_span_id`. In supported browsers, a log emitted during an
active Session Replay also receives `sentry.replay_id`.

## Browser PII behavior

Browser SDKs no longer request backend IP inference by default in
`9.0.0-guide`. Set `sendDefaultPii: true` only when IP inference and the other
default PII behavior are intended.

`requestDataIntegration` no longer copies Express `request.user` into events.
Set the user explicitly, usually in middleware:

```js
Sentry.setUser({ id: request.user.id });
```

## Console events and handled state

With `attachStackTrace: true`, `captureConsoleIntegration` marks console events
handled by default in `9.0.0-guide`. Pass `{ handled: false }` to retain
unhandled semantics:

```js
Sentry.init({
  attachStackTrace: true,
  integrations: [
    Sentry.captureConsoleIntegration({ handled: false }),
  ],
});
```

## Session tracking

`autoSessionTracking` is removed in `9.0.0-guide`. Browser sessions use
`browserSessionIntegration`, server request sessions use `httpIntegration`, and
Node.js process sessions use the default `processSessionIntegration`.

Disable browser tracking by removing `browserSessionIntegration`. Disable
incoming server request sessions with:

```js
Sentry.httpIntegration({ trackIncomingRequestsAsSessions: false });
```

Core always uses the session on the isolation scope as of `9.0.0`. If multiple
scopes carry session state, selection follows the isolation scope rather than
another active scope.

## Browser feedback

`captureUserFeedback()` is removed in `9.0.0-guide`. Use `captureFeedback()`
and rename payload `comments` to `message`:

```js
Sentry.captureFeedback({ message: "What happened" });
```

## Web-vital migration

Browser SDKs stop reporting First Input Delay in `10.0.0-guide`. Replace
FID-based processing, filters, alerts, and dashboards with Interaction to Next
Paint equivalents where appropriate.

## Error sampling order

In `10.69.0-10.70.0`, error sampling occurs after `beforeSend`, while session
updates remain preserved. A `beforeSend` hook can therefore execute for an event
that sampling subsequently discards. Avoid relying on the hook as proof that an
event will be sent.

## Stack-frame variable filtering

At `10.68.0`, `stackFrameVariables` can filter by variable name. Use it to
retain only the captured variables allowed by the application's privacy and
diagnostic policy.

## Browser and Node event integrations

The browser SDK gains a Statsig integration in `9.0.0`. The Node SDK also begins
capturing exceptions from `worker_threads` in that release.
