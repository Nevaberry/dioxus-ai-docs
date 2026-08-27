# Server and Route Data

## Server-function error flow

Errors from `server$` functions and route loaders use standardized handling.
Middleware marked with `@plugin` can catch `server$` failures. On the client,
calls throw for 4xx statuses and statuses above 500, while 499 is accepted as
a valid status.

## Redirect response middleware

The send-request event receives a `Response` object even when the request
redirects. Middleware should inspect that response rather than expecting a
different redirect-only value.

## Route-data cache headers

Qwik City does not force a fresh `q-data.json` download for every navigation.
Navigation follows the resource's cache headers, and the default cache
duration is one hour. Set route-data cache headers intentionally when the
default is unsuitable.

## Route-loader and action mocks

`QwikCityMockProvider` can mock route loaders and actions in tests. Use the
provider to supply route-data and action behavior without invoking the live
handlers.

## Bun and Deno request origins

`QwikCityBunOptions` and `QwikCityDenoOptions` accept `getOrigin`. Supply it
when the runtime or proxy setup requires custom URL-origin handling.

## Request-event immutability

Request events use readonly types instead of being frozen at runtime. Treat
the TypeScript surface as immutable, but do not depend on `Object.freeze()`
runtime behavior.

Source batches: `v1.8-1.13`, `v1.14-1.19`.
