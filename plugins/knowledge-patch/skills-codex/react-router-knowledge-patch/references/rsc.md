# React Server Components

React Server Components support entered as previews, including a later Framework Mode
preview (`7.0-guide`). Data Mode and Framework Mode use different APIs and entry points;
many RSC surfaces remain unstable, so bind implementation choices to the installed
version.

## Data Mode RSC

### Initial APIs (`7.7.0`)

Experimental Data Mode support exposes:

- `unstable_RSCHydratedRouter`
- `unstable_RSCStaticRouter`
- `unstable_createCallServer`
- `unstable_getRSCStream`
- `unstable_matchRSCServerRequest`
- `unstable_routeRSCServerRequest`

These are experimental in this release and are not recommended for production.

### Route support and server actions (`7.8.0`)

Data Mode RSC handles route `meta` and `links`, and makes `isRouteErrorResponse`
available in `react-server` environments. Server-action side-effect redirects are proxied
for both document and `callServer` requests.

To opt a server action out of revalidation, include a hidden form field named
`$SKIP_REVALIDATION`.

### DOM entry-point placement (`7.9.0`)

`unstable_RSCHydratedRouter` and related utilities move to `react-router/dom`.
React-server entry points also implement `Await` and `href`. Audit imports when upgrading
from the earlier placement.

## Framework Mode RSC

### Rendering responses (`7.11.0`)

RSC render paths accept thrown `data()` values and `Response` objects, including
redirects. Raw response bodies are not serialized into error encoding; throw `data()`
when an error boundary needs a payload.

The `routeRSCServerRequest` integration renames `fetchServer` to `serverResponse`.
Framework tooling in `@react-router/dev` and `@react-router/serve` also begins supporting
custom RSC entrypoints.

### Expanded framework features (`7.14.0`)

Framework Mode RSC adds prerendering, SPA Mode, and `<Link prefetch>`. The
`react-router reveal` command can expose `entry.client`, `entry.rsc`, and `entry.ssr`.
These features remain unstable and unsuitable for production in this release.

### Explicit client/server route exports (`7.14.0`)

Client exports `default`, `ErrorBoundary`, `Layout`, and `HydrateFallback` have mutually
exclusive server counterparts `ServerComponent`, `ServerErrorBoundary`, `ServerLayout`,
and `ServerHydrateFallback`.

This breaks an earlier implicit behavior: exporting `ServerComponent` does not make the
other exports server components. Prefix each independently when it belongs on the server.

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

## Middleware and RSC request state

Server middleware may wrap `next()` in Node `AsyncLocalStorage.run()` so request-local
state is visible to React Server Components and Server Actions in the same execution
context (`middleware`). Prefer React Router's context API when runtime portability is
required.

## Adoption checklist

- Identify Data Mode versus Framework Mode before selecting APIs.
- Confirm whether RSC DOM APIs live in `react-router/dom` for the installed version.
- Test document, `callServer`, redirect, thrown-data, and error-boundary paths separately.
- Treat every `unstable_` surface as version-bound.
- In Framework Mode, choose every client or `Server*` route export explicitly.
- Reveal and inspect generated RSC entrypoints before replacing them with custom files.
