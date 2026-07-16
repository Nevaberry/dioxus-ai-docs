# React Server Components

## Contents

- [Data Mode RSC](#data-mode-rsc)
- [RSC request routing and responses](#rsc-request-routing-and-responses)
- [Framework Mode RSC](#framework-mode-rsc)
- [Middleware and request-local state](#middleware-and-request-local-state)
- [Rendering streams](#rendering-streams)
- [CSP](#csp)

React Router provides separate provisional RSC surfaces for Data Mode and Framework Mode. Check
the installed version and package entry point before using an example; several names and export
semantics changed while the previews evolved. Do not treat these APIs as production-stable.

## Data Mode RSC

Experimental Data Mode support includes these APIs:

- `unstable_RSCHydratedRouter`
- `unstable_RSCStaticRouter`
- `unstable_createCallServer`
- `unstable_getRSCStream`
- `unstable_matchRSCServerRequest`
- `unstable_routeRSCServerRequest`

`unstable_RSCHydratedRouter` and its utilities moved to the `react-router/dom` entry point.
`react-server` environments also provide implementations of `Await` and `href`, and expose
`isRouteErrorResponse`.

RSC Data Mode supports route `meta` and `links` exports. It proxies side-effect redirects from
server actions for document requests and `callServer` requests. To suppress revalidation after
an RSC server action, include a hidden `$SKIP_REVALIDATION` form field.

```tsx
<input type="hidden" name="$SKIP_REVALIDATION" value="true" />
```

## RSC request routing and responses

RSC rendering accepts thrown `data()` values and `Response` objects, including redirects. A raw
response body is not serialized while encoding an error, so throw `data()` when an error
boundary needs access to a payload.

The provisional `routeRSCServerRequest` integration renamed its `fetchServer` option to
`serverResponse`. Update custom integrations rather than supporting both names silently.

Server action redirects can be forwarded for both document and `callServer` request paths. Keep
redirect validation and action-origin protection enabled; origin failures render the proper RSC
error UI.

## Framework Mode RSC

Framework Mode RSC tooling in `@react-router/dev` and `@react-router/serve` supports custom
entrypoints. The `react-router reveal` command can reveal `entry.client`, `entry.rsc`, and
`entry.ssr` for customization.

The preview supports prerendering, SPA Mode, and `<Link prefetch>`. These capabilities remain
unstable and should be isolated from stable application architecture.

### Explicit client and server route exports

The client-oriented exports `default`, `ErrorBoundary`, `Layout`, and `HydrateFallback` have
separate, mutually exclusive server counterparts:

| Client export | Server export |
| --- | --- |
| `default` | `ServerComponent` |
| `ErrorBoundary` | `ServerErrorBoundary` |
| `Layout` | `ServerLayout` |
| `HydrateFallback` | `ServerHydrateFallback` |

Declaring `ServerComponent` does not implicitly make the other three exports server components.
Prefix every export that must execute on the server.

```tsx
export function ServerComponent() {
  return <main>Page</main>;
}

export function ErrorBoundary() {
  return <p>Try again</p>; // client component
}

export function ServerLayout() {
  return <html><body /></html>;
}

export function ServerHydrateFallback() {
  return <p>Loading…</p>;
}
```

## Middleware and request-local state

Route middleware works with RSC request handling. A server middleware can wrap `next()` in
Node's `AsyncLocalStorage.run()` to expose request-local values to loaders, Server Components,
and Server Actions within the same execution context. Use `RouterContextProvider` instead when
the code must be runtime-portable.

```ts
const currentUser = new AsyncLocalStorage<User>();

export const middleware: Route.MiddlewareFunction[] = [
  async ({ request }, next) =>
    currentUser.run(await getUser(request), next),
];
```

Server context still follows HTTP request boundaries. Do not assume an SPA submission's POST and
subsequent GET share the same provider.

## Rendering streams

For apps without a custom `entry.server.tsx`, the 8.2.0 default uses
`renderToReadableStream` when no Node-specific React Router adapter is installed. Apps depending
on `@react-router/node`, `@react-router/express`, or `@react-router/serve` retain
`renderToPipeableStream`. A Node app without a custom entry may opt into the Web Streams path
with `future.unstable_enableNodeReadableStream`.

The removed `ServerRouter.abortDelay` does not control Single Fetch streams. Export
`streamTimeout` from `entry.server` for that timeout.

## CSP

Nonce-aware server-rendered components inherit the `nonce` supplied to `ServerRouter` when they
do not receive a component-specific nonce. This includes framework-generated output involved in
RSC SSR. Still inspect rendered markup when combining RSC, prefetching, SRI, and a strict CSP.
