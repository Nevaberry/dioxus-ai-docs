# Migrations and Runtime Compatibility

## Runtime and package floors (9.0.0-guide)

SDK packages may contain ES2020. The general Node.js floor is 18.0.0; the
ESM-only Astro, Nuxt, and SvelteKit SDKs require Node.js 18.19.1. Deno 2.0 and
TypeScript 5.0.4 are the other minimums.

Native browser support begins at Chrome/Edge 80, Safari 14, iOS Safari 14.4,
Firefox 74, Opera 67, and Samsung Internet 13. Transpile SDK code when an
application targets older browsers.

Support is removed for Remix 1.x, TanStack Router 1.63.0 and lower, SvelteKit
1.x, Ember 3.x and lower, and Prisma 5.x.

## Package and client API migration

### Utility and type packages

`@sentry/utils` is no longer published. `@sentry/types` is deprecated; import
its remaining exports and former utility exports from `@sentry/core`.

The metrics API, `getCurrentHub()`, `Hub`, and `getCurrentHubShim()` are
removed. Replace `debugIntegration` with send hooks and replace
`sessionTimingIntegration` by setting event context explicitly.

### Custom clients and logging internals

Custom clients were required to extend `BaseClient` in v9 rather than using a
structural custom implementation. In v10, `BaseClient` itself is removed; use
`Client` directly. The internal `logger` value and `Logger` type are replaced
by `debug` and `SentryDebugLogger` (10.0.0-guide).

### Core removals and type changes (9.0.0)

Core removes `TransactionNamingScheme`, `arrayify()`, `flatten()`,
`getDomElement()`, `makeFifoCache()`, `memoBuilder`, `urlEncode()`, the
deprecated `Request` type, and `validSeverityLevels`. React removes
`getNumberOfUrlSegments()`. Next.js removes
`experimental_captureRequestError`.

`recordDroppedEvent()` no longer accepts an event argument.
`hasTracingEnabled()` is renamed to `hasSpansEnabled()`.

The `shutdownTimeout` option type moves from core to Node. The `Scope` type
interface is replaced by the `Scope` class. React's `ErrorBoundary` changes
the type of `componentStack`, and the `nitro-utils` package is removed.

## Feedback migration

`captureUserFeedback()` is removed. Call `captureFeedback()` and rename the
payload's `comments` field to `message`:

```js
Sentry.captureFeedback({ message: "What happened" });
```

## Low-level extension API migration

Custom propagation contexts require `sampleRand`; replace `spanId` with the
optional `propagationSpanId`. Use `httpRequestToRequestData()` for request
enrichment and assign its return value to `event.request`.

Replace these removed symbols:

| Removed | Replacement |
| --- | --- |
| `generatePropagationContext()` | `generateTraceId()` |
| `BAGGAGE_HEADER_NAME` | Literal `"baggage"` |
| `IntegrationClass` | `Integration` or `IntegrationFn` |

## Deno distribution

`@sentry/deno` is no longer published on `deno.land`. Import the npm package:

```js
import * as Sentry from "npm:@sentry/deno";
```

## Sessions and scope selection

Core always reads session state from the isolation scope (since 9.0.0). If
several scopes contain sessions, this can select a different session than
older code expected.

`autoSessionTracking` is removed. Browser sessions belong to
`browserSessionIntegration`; request sessions belong to `httpIntegration`;
Node.js process sessions use the default `processSessionIntegration`.

```js
Sentry.init({
  integrations: [
    Sentry.httpIntegration({ trackIncomingRequestsAsSessions: false }),
  ],
});
```

Disable browser tracking by removing `browserSessionIntegration`.

## Browser behavior changes

Browser SDKs no longer ask the backend to infer IP addresses by default. Set
`sendDefaultPii: true` only when inference is intended.

When `attachStackTrace: true`, `captureConsoleIntegration` marks console events
handled. Configure `{ handled: false }` to retain the opposite behavior.

```js
Sentry.init({
  sendDefaultPii: true,
  attachStackTrace: true,
  integrations: [Sentry.captureConsoleIntegration({ handled: false })],
});
```

Browser SDKs no longer report First Input Delay (10.0.0-guide). Replace
FID-based event processing, filters, alerts, and dashboards with Interaction
to Next Paint equivalents where appropriate.

## Express user enrichment

`requestDataIntegration` no longer copies `request.user` into events for
Express. Call `Sentry.setUser()` explicitly, normally from middleware.

## OpenTelemetry compatibility boundary

Node-based v10 packages use OpenTelemetry 2.x/0.20x dependencies and current
instrumentations. Applications unable to adopt OpenTelemetry 2 should remain
on Sentry v9 or use `@sentry/node-core`, whose peer dependency ranges are
wider. Sentry v10 remains compatible with self-hosted Sentry 24.4.2 and newer.

## Bundler plugin major

SDK v10 uses the v4 major line of Sentry bundler plugins (10.0.0). Update
directly installed or pinned plugins across that major boundary together with
the SDK.
