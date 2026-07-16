# Data Loading and Rendering

## Contents

- [Loader and action return values](#loader-and-action-return-values)
- [Server and client loaders](#server-and-client-loaders)
- [Revalidation](#revalidation)
- [Awaitable router operations](#awaitable-router-operations)
- [Fetchers](#fetchers)
- [Custom data strategies](#custom-data-strategies)
- [Navigation and transition state](#navigation-and-transition-state)
- [Error and match rendering behavior](#error-and-match-rendering-behavior)
- [Prerender execution](#prerender-execution)

## Loader and action return values

### Return values directly

The `json()` and `defer()` helpers, deferred-data types and symbols, and the old multipart
helpers `unstable_composeUploadHandlers`, `unstable_createMemoryUploadHandler`, and
`unstable_parseMultipartFormData` are removed. With Single Fetch, return values and promises
directly. Use `Response.json()` only when response semantics are required. Loaders and actions
may return `undefined`.

```ts
export function loader() {
  return {
    profile: getProfile(),
    report: loadReport(),
  };
}
```

Single Fetch throws unwrapped redirect responses, matching the behavior before Single Fetch.
Redirects are excluded from loader-data inference, so they do not pollute the successful data
shape.

Framework loader serialization supports values beyond JSON primitives, including `Date`, `Map`,
and `Set`. Server response typing preserves `ReadonlyMap` and `ReadonlySet` rather than widening
them to mutable collections. Libraries can register additional turbo-stream-supported values
with the provisional `unstable_SerializesTo` brand type.

## Server and client loaders

### Combine both sources under SSR

When a route exports both functions, `loader` provides the initial server/prerender value and
`clientLoader` handles later browser navigations. The client loader can call `serverLoader()`
and add client-only state.

```tsx
import type { Route } from "./+types/profile";

export async function loader() {
  return getServerProfile();
}

export async function clientLoader({ serverLoader }: Route.ClientLoaderArgs) {
  return { ...(await serverLoader()), theme: getLocalTheme() };
}

clientLoader.hydrate = true as const;

export function HydrateFallback() {
  return <p>Loading…</p>;
}
```

`clientLoader.hydrate = true as const` runs the client loader before initial hydration. A route
with only a `clientLoader` receives this behavior implicitly; export `HydrateFallback` for the
interim UI.

If both loaders exist and hydration is enabled without a fallback, the server renders the route
component while the client loader runs. Its first result must match the server loader data or
hydration will mismatch. A client loader that only primes a cache should return
`serverLoader()` on that initial run.

For a purely static SPA build, server loader constraints depend on prerender configuration:
without configured paths only the root loader runs at build time; a configured path may run its
matched loaders. Dynamic fallback navigation needs a `clientLoader` because no server loader can
revalidate there.

### Wrap server mutations from the client

In the browser, `clientAction` takes precedence over a route's `action`, but it receives
`serverAction()` so client work can wrap the server mutation.

```ts
export async function action() {
  return updateOnServer();
}

export async function clientAction({ serverAction }: Route.ClientActionArgs) {
  invalidateClientCache();
  return serverAction();
}
```

## Revalidation

### Mode defaults

Framework Mode with SSR revalidates loaders after every navigation and form submission. Data
Mode does not, and SPA Mode follows Data Mode because it has no server loaders during navigation.
Use a route's `shouldRevalidate` to make the final route-level decision.

After an action returns a 4xx or 5xx response, Framework Mode supplies
`defaultShouldRevalidate: false`. Code that returns the default no longer causes the older
unintended revalidation.

Call sites including `Form`, `submit`, `fetcher.Form`, `fetcher.submit`, `Link`, `navigate`, and
`setSearchParams` accept `defaultShouldRevalidate`. Set it to `false` to make that call opt out
of the standard default; each route's `shouldRevalidate` still receives the value and has the
final say. The property was initially named `unstable_defaultShouldRevalidate`.

```tsx
<Form method="post" defaultShouldRevalidate={false} />
```

```ts
navigate("?analytics-param=1", { defaultShouldRevalidate: false });
```

When this default is false, parent routes without their own `shouldRevalidate` are excluded from
the Single Fetch request for new child-route data.

An RSC server action can opt out of revalidation by including a hidden form input named
`$SKIP_REVALIDATION`.

## Awaitable router operations

The operations returned by `useNavigate()`, `useSubmit()`, `useFetcher().load`,
`useFetcher().submit`, and `useRevalidator().revalidate()` expose their underlying promises.
Await them when subsequent work depends on completion.

```ts
await navigate("/account");
await submit(formData, { method: "post" });
await fetcher.load("/resource");
await revalidator.revalidate();
```

The navigation promise also tracks the full duration of `popstate`/POP history traversal in
Framework and Data Mode:

```ts
await navigate(-1);
```

## Fetchers

Use `fetcher.reset()` to return a fetcher to its initial idle state. The provisional spelling
was `fetcher.unstable_reset()`.

```tsx
const fetcher = useFetcher();
<button onClick={() => fetcher.reset()}>Reset</button>;
```

`useFetchers()` keeps the returned array identity stable until its fetchers change, so effects
and memoization do not rerun because of a newly allocated but equivalent snapshot.

For fetcher-triggered route discovery, `patchRoutesOnNavigation` receives the originating
`fetcherKey`; its `path` contains only the pathname, not search parameters.

## Custom data strategies

Use `match.shouldCallHandler()` and `match.shouldRevalidateArgs` in a custom `dataStrategy`.
Their provisional names were `unstable_shouldCallHandler()` and
`unstable_shouldRevalidateArgs`. The less capable `match.shouldLoad` is deprecated.

A custom strategy that returns too few results now produces explicit errors for routes without
a result rather than leaving those routes in an indeterminate missing-result state.

Client middleware receives the inner data-strategy results on the way back up the chain, which
allows post-processing. It also runs on client navigations that have no loaders.

## Navigation and transition state

`useNavigation()` has a discriminated union for `idle`, `loading`, and `submitting`; checking
`navigation.state` narrows the fields available in that state.

`unstable_useRouterState()` consolidates an always-present `active` snapshot and an optional
`pending` snapshot. Each contains location, search parameters, params, matches, navigation
type/state, and submission data. It works only with Framework, Data, and RSC routers and throws
without a data router.

```tsx
const { active, pending } = unstable_useRouterState();
const location = pending?.location ?? active.location;
```

Transition controls are mode-specific. In Framework and Data Mode, leaving
`unstable_transition` unset on `HydratedRouter` or `RouterProvider` preserves the normal
`React.startTransition` wrapping. Setting it to `true` additionally wraps `Link` and `Form`
navigations and exposes optimistic navigation/fetcher state through `React.useOptimistic`, which
requires React 19. `false` disables transition and optimistic handling. Declarative Mode exposes
the transition-only `useTransitions` prop on `BrowserRouter`; this was originally
`unstable_useTransitions`.

```tsx
<RouterProvider router={router} unstable_transition={true} />
<BrowserRouter useTransitions={false}>{children}</BrowserRouter>
```

The updater callback passed to `setSearchParams` receives a copy of the current
`URLSearchParams`. Mutating it cannot modify the router's internal instance before a navigation
succeeds, so a blocked navigation no longer desynchronizes it from `useLocation().search`.

## Error and match rendering behavior

SPA Mode reports synchronous initial-loader failures through `RouterProvider.onError`, allowing
central reporting to cover initial rendering.

Match-level loader data may be `undefined` while an error boundary renders, including when an
earlier route loader failed. Guard `loaderData` access. `Route.MetaArgs.loaderData` is optional
only when that route exports an `ErrorBoundary`; `Route.MetaArgs.data` also became possibly
undefined before its later removal.

`<RouterProvider fallbackElement>` is removed. For partial hydration, put
`hydrateFallbackElement` or `HydrateFallback` on the root route. Initial navigation remains
`idle` while the fallback renders.

## Prerender execution

`prerender: true` builds every static route but cannot invent parameter values. A callback or
explicit list can add dynamic paths and resource routes. Set `prerender.concurrency` to perform
build-time renders concurrently; the original key was `prerender.unstable_concurrency`.

Generated `.html` and `.data` files have distinct server behavior: `@react-router/serve` assigns
`.data` the `text/x-turbo` content type, and prerendered files outside the asset directory have
no automatic cache policy.
