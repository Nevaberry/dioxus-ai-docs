# Router and Server Behavior

## Error boundaries

Qwik provides an `ErrorBoundary` component. The behavior of
`useErrorBoundary` was corrected in 1.13, so prefer the framework boundary
APIs over ad hoc render-error trapping.

## Server-function error flow

By 1.13, errors are standardized across `server$` functions and route
loaders. `@plugin` middleware can catch `server$` failures. On the client,
calls throw for 4xx statuses and statuses above 500; 499 is accepted as a
valid status.

Keep explicit `try`/`catch` handling around calls whose status is part of the
UI flow.

## Redirect responses in middleware

The send-request event receives a `Response` object even when the request
redirects. Middleware can inspect that response instead of maintaining a
redirect-only branch with no response value.

## Initial previous URL

The router's previous URL is `undefined` on the first render. Treat it as
optional before reading its fields or comparing it with the current URL.

## Rewrite fan-in

Multiple rewrite routes can point to the same destination route. Custom route
validation must not reject that fan-in as inherently ambiguous.

## Route-loader and action mocks

`QwikCityMockProvider` can mock route loaders and actions in tests. Use those
mocks to isolate components that consume loader or action state.

## Bun and Deno request origins

`QwikCityBunOptions` and `QwikCityDenoOptions` accept `getOrigin`. Supply it
when proxying or runtime-specific request details prevent Qwik City from
deriving the correct URL origin.

## Request-event immutability

Request events use readonly types rather than runtime freezing. TypeScript
prevents ordinary mutation, but code must not rely on `Object.isFrozen()` or
a runtime mutation exception as an invariant.

## Internal request rewrites

`RequestEvent.rewrite()` performs an internal redirect while preserving the
browser-visible URL. Throw its return value from a request handler:

```ts
export const onRequest: RequestHandler = async ({ rewrite }) => {
  throw rewrite('/articles/42');
};
```

## Redirect caching

Redirect responses do not inherit `Cache-Control` from a parent layout and
default to `no-store`. Set redirect caching explicitly only when the redirect
semantics make reuse safe.

## Navigation data caching

Qwik City no longer forces fresh `q-data.json` downloads during navigation.
The request follows its cache headers, with a default cache duration of one
hour. Tests that expected an unconditional network refresh should set or
override cache headers deliberately.
