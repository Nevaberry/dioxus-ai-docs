# Telemetry Data, Sessions, and Logs

## Structured logging

Enable logs with the top-level `enableLogs` option and process them with the
top-level `beforeSendLog` hook. The former `_experiments.enableLogs` and
`_experiments.beforeSendLog` locations are obsolete (10.0.0-guide).

`Sentry.logger` requires a message and supports `trace`, `debug`, `info`,
`warn`, `error`, and `fatal`. Pass searchable attributes in the second
argument. `Sentry.logger.fmt` is a tagged template that extracts interpolated
values as searchable attributes.

```js
Sentry.logger.info("Order created", { orderId: "order_456" });
Sentry.logger.info(
  Sentry.logger.fmt`User ${userId} purchased ${productName}`,
);
```

## Shared log and metric attributes

Since 10.61.0, `Sentry.setAttribute()` and `Sentry.setAttributes()` attach
shared attributes to logs and metrics. Values may be strings, numbers,
booleans, or arrays of those primitive types.

The same methods on the global scope establish application-wide attributes;
on the current scope they establish operation-local attributes.

```js
Sentry.setAttributes({ org_id: user.orgId, user_tier: user.tier });
Sentry.withScope((scope) => {
  scope.setAttribute("request_id", req.id);
  Sentry.logger.info("Processing order");
});
```

## Console and Consola ingestion

`consoleLoggingIntegration({ levels })` converts selected console calls into
logs. Since 10.13.0, extra console arguments are searchable as
`message.parameter.N` attributes.

```js
Sentry.init({
  integrations: [
    Sentry.consoleLoggingIntegration({ levels: ["log", "warn", "error"] }),
  ],
});
```

Consola applications can attach `Sentry.createConsolaReporter()` since
10.12.0.

## Trace and Replay correlation

A log emitted during an active span carries `sentry.trace.parent_span_id`.
In supported browser environments, a log emitted during an active Session
Replay also carries `sentry.replay_id`.

Replay's `_experiments.autoFlushOnFeedback` option is removed. Capturing user
feedback flushes Replay by default.

## Feedback payloads

Use `captureFeedback()` rather than the removed `captureUserFeedback()`, and
rename the payload field from `comments` to `message`:

```js
Sentry.captureFeedback({ message: "What happened" });
```

## Browser PII and console events

Browser SDKs do not request backend IP inference by default. Set
`sendDefaultPii: true` when that collection is intended.

With `attachStackTrace: true`, `captureConsoleIntegration` marks console events
handled unless configured with `{ handled: false }` (9.0.0-guide).

## Request and framework data collection

`requestDataIntegration` does not infer the Sentry user from Express
`request.user`. Explicitly call `Sentry.setUser()` in middleware.

Elysia, Hono, Nitro, and TanStack Start SDKs expose `dataCollection` controls.
To avoid sending default user information or any request bodies:

```js
Sentry.init({
  dataCollection: { userInfo: false, httpBodies: [] },
});
```

## Stack-frame variables

`stackFrameVariables` supports filtering captured variables by variable name
(since 10.68.0). Use it to retain only the variables permitted by the
application's data policy.

## Session source and lifecycle

Session state is read from the isolation scope (since 9.0.0). Configure
tracking through `browserSessionIntegration`, `httpIntegration`, and the
default `processSessionIntegration`; the former `autoSessionTracking` option
is removed.

When error sampling occurs after `beforeSend` in 10.69.0-10.70.0, session
updates remain preserved even if the error event is later sampled out.
