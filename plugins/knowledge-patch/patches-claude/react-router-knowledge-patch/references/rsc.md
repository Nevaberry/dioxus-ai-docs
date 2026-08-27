# React Server Components

React Server Components support includes distinct Data Mode and Framework Mode
surfaces. The 7.0-guide introduced the previews and noted a later Framework Mode
preview. Confirm exact package entry points and names for the installed version;
several APIs remain provisional and are not recommended for production use.

## Data Mode APIs

### Initial preview

Version 7.7.0 introduced experimental Data Mode support through:

- `unstable_RSCHydratedRouter`
- `unstable_RSCStaticRouter`
- `unstable_createCallServer`
- `unstable_getRSCStream`
- `unstable_matchRSCServerRequest`
- `unstable_routeRSCServerRequest`

In 7.9.0, `unstable_RSCHydratedRouter` and its browser utilities moved to
`react-router/dom`. React-server environments gained implementations of `Await` and
`href`.

### Route exports and server-action behavior

As of 7.8.0, RSC Data Mode handles route `meta` and `links`, exposes
`isRouteErrorResponse` in react-server environments, and proxies Server Action
side-effect redirects for both document and `callServer` requests.

A hidden form field named `$SKIP_REVALIDATION` lets an RSC Server Action suppress
revalidation.

## Rendering responses

RSC rendering gained support for thrown `data()` values and `Response` objects,
including redirect responses, in 7.11.0. A raw response body is not serialized while
encoding an error; throw `data()` when an error boundary needs a payload.

The same release renamed the `fetchServer` option on `routeRSCServerRequest` to
`serverResponse`. Update integrations using the older spelling.

Cross-origin action rejection returns an appropriate RSC error UI as of 7.13.1; see
the security reference for origin configuration.

## Framework Mode

### Tooling and entrypoints

Custom Framework Mode RSC entry points became possible through `@react-router/dev`
and `@react-router/serve` in 7.11.0.

The 7.14.0 Framework Mode preview added prerendering, SPA Mode, and
`<Link prefetch>`. `react-router reveal` can expose `entry.client`, `entry.rsc`, and
`entry.ssr` for customization.

### Explicit client and server route exports

Framework RSC route exports are paired but independent:

| Client export | Server export |
| --- | --- |
| `default` | `ServerComponent` |
| `ErrorBoundary` | `ServerErrorBoundary` |
| `Layout` | `ServerLayout` |
| `HydrateFallback` | `ServerHydrateFallback` |

This became explicit in 7.14.0 and was breaking for early adopters. Declaring
`ServerComponent` no longer implies that the error boundary, layout, and hydrate
fallback are server components. Prefix every export that must stay server-side.

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

## Middleware and request state

Framework server middleware wraps RSC document/data work. Node runtimes may use
`AsyncLocalStorage.run()` around `next()` to make request-scoped state visible to
React Server Components and Server Actions. Use `RouterContextProvider` instead when
the integration must remain runtime-portable.

Client and server contexts have different lifetimes. Do not assume server context
persists between the POST and GET of an SPA submission.

## Adoption checklist

- Distinguish Data Mode routers from Framework Mode route-module exports.
- Import DOM hydrated-router utilities from `react-router/dom` where required.
- Preserve `data()` payloads when RSC error boundaries need structured error data.
- Update `fetchServer` integrations to `serverResponse`.
- Define every intended `Server*` boundary, layout, and fallback explicitly.
- Test document rendering, `callServer`, redirects, action revalidation, prerender,
  SPA hydration, and prefetched links separately.
