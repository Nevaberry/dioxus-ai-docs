# Migrations and runtime compatibility

## Runtime, language, browser, and framework floors

For the `9.0.0-guide` migration, SDK packages may contain ES2020. Node.js
packages require Node.js 18.0.0, except the ESM-only Astro, Nuxt, and SvelteKit
SDKs, which require 18.19.1. Deno 2.0 and TypeScript 5.0.4 are the other runtime
and language floors.

Native browser support starts at Chrome and Edge 80, Safari 14, iOS Safari
14.4, Firefox 74, Opera 67, and Samsung Internet 13. Transpile the SDK when
older targets are required.

Support is dropped for Remix 1.x, TanStack Router 1.63.0 and lower, SvelteKit
1.x, Ember 3.x and lower, and Prisma 5.x.

## Serverless layer names

The v9 AWS Lambda layer is `SentryNodeServerlessSDKv9`; updates remaining on v8
use `SentryNodeServerlessSDKv8` (`9.0.0-guide`). The v10 layer is
`SentryNodeServerlessSDKv10` and is unified for ESM and CommonJS deployments
(`10.0.0`).

## Package and primary API removals

As of `9.0.0-guide`, `@sentry/utils` is not published and `@sentry/types` is
deprecated. Their remaining exports move to `@sentry/core`. The metrics API,
`getCurrentHub()`, `Hub`, and `getCurrentHubShim()` are removed. Replace
`debugIntegration` with send hooks and `sessionTimingIntegration` with explicit
event context.

The `9.0.0` core also removes `TransactionNamingScheme`, `arrayify()`,
`flatten()`, `getDomElement()`, `makeFifoCache()`, `memoBuilder`, `urlEncode()`,
the deprecated `Request` type, and `validSeverityLevels`. React removes
`getNumberOfUrlSegments()`, Next.js removes `experimental_captureRequestError`,
and the `nitro-utils` package is dropped.

`recordDroppedEvent()` no longer accepts an event argument, and
`hasTracingEnabled()` is renamed to `hasSpansEnabled()`. The `shutdownTimeout`
option type moves from core to Node. The `Scope` type interface becomes the
`Scope` class, and React `ErrorBoundary` changes the type of `componentStack`.

## Client and logger internals

During the v9 migration, custom clients must extend `BaseClient`
(`9.0.0-guide`). In v10, `BaseClient` is removed, so custom clients use `Client`
directly (`10.0.0-guide`). This is a version succession rather than an
interchangeable choice.

The internal `logger` value and `Logger` type are removed in favor of `debug`
and `SentryDebugLogger` (`10.0.0-guide`). These changes do not remove the public
structured logging API documented separately.

## Low-level extension API migrations

For `9.0.0-guide` custom extensions:

- Include `sampleRand` in custom propagation contexts.
- Replace `spanId` with optional `propagationSpanId`.
- Enrich requests with `httpRequestToRequestData()` and assign its result to
  `event.request`.
- Replace `generatePropagationContext()` with `generateTraceId()`.
- Use the literal `"baggage"` instead of `BAGGAGE_HEADER_NAME`.
- Replace `IntegrationClass` with `Integration` or `IntegrationFn`.
- Extend `BaseClient` only while targeting the v9 client API; use `Client`
  directly after moving to v10.

## OpenTelemetry setup and compatibility

`addOpenTelemetryInstrumentation()` is removed in `9.0.0-guide`. Supply custom
instrumentation at initialization:

```js
Sentry.init({
  openTelemetryInstrumentations: [new GenericPoolInstrumentation()],
});
```

`skipOpenTelemetrySetup: true` also configures `httpIntegration({ spans: false
})` by default. `registerEsmLoaderHooks` accepts only a boolean or `undefined`
and defaults to wrapping modules used by OpenTelemetry instrumentation.

Node-based v10 SDKs move to OpenTelemetry 2.x/0.20x dependencies and current
instrumentation releases (`10.0.0-guide`). Projects unable to use OpenTelemetry
2 must stay on Sentry v9 or use `@sentry/node-core`, whose peer ranges are
wider. V10 remains compatible with Sentry self-hosted 24.4.2 and newer.

## Prisma instrumentation

The bundled `prismaIntegration` targets Prisma 6 and drops Prisma 5 support in
`9.0.0-guide`. Prisma 6 does not require the `tracing` preview feature. To
instrument a different version, install its matching `@prisma/instrumentation`,
pass a `PrismaInstrumentation` through `prismaInstrumentation`, and retain
`previewFeatures = ["tracing"]` for pre-v6 Prisma when required.

```js
Sentry.init({
  integrations: [
    Sentry.prismaIntegration({
      prismaInstrumentation: new PrismaInstrumentation(),
    }),
  ],
});
```

## Renamed Node.js integrations

In `9.0.0-guide`, `processThreadBreadcrumbIntegration` becomes
`childProcessIntegration`, and its integration name changes from
`ProcessAndThreadBreadcrumbs` to `ChildProcess`. `vercelAIIntegration` changes
its name from `vercelAI` to `VercelAI`. Update integration-name filters as well
as factory calls.

## Deno distribution

`@sentry/deno` is no longer published on `deno.land` (`9.0.0-guide`). Import it
from npm:

```js
import * as Sentry from "npm:@sentry/deno";
```

## Protocol and peer support additions

Core supports stable MCP SDK v2 in `10.69.0-10.70.0`. Solid and SolidStart
support `@solidjs/router` v1, Gatsby permits React 19 in its peer dependency
range, and the SvelteKit worker entry point exports `metrics`.
