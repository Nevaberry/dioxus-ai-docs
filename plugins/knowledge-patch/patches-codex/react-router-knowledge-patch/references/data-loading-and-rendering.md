# Data Loading and Rendering

## Single Fetch and returned values

### Direct values and promises (`7.0.0`)

`json()`, `defer()`, and deferred-data symbols are removed. Under Single Fetch, return
serializable values and promises directly; use `Response.json()` only for an actual
response. Loaders and actions may return `undefined`.

```ts
export function loader() {
  return { report: loadReport() };
}
```

Former v6 `v7_*` and Remix v2 `v3_*` behaviors are mandatory in v7: relative splats,
transitions, fetcher persistence, normalized form methods, partial hydration, action
revalidation, Single Fetch, lazy route discovery, abort reasons, and dependency
optimization. Remove the old flags. `<RouterProvider fallbackElement>` is gone; put
`hydrateFallbackElement`/`HydrateFallback` on root. During partial hydration the initial
navigation remains `idle`.

### Redirect and inference behavior (`7.1.0`)

Single Fetch throws redirects unwrapped, as before Single Fetch. Redirect responses are
excluded from loader-data inference and do not widen the data shape. Replace the removed
`ServerRouter abortDelay` with an `entry.server` `streamTimeout` export.

### Rich values and type registration

Framework loaders serialize and reconstruct values beyond JSON primitives, including
`Map`, `Set`, and `Date` (`framework-mode`). Server response types preserve
`ReadonlyMap` and `ReadonlySet` rather than widening them (`7.8.0`).

For libraries, `unstable_SerializesTo` can register types understood by React Router's
`turbo-stream` serialization (`7.2.0`). Treat the brand as unstable in that release.

## Server and client loaders/actions

### Combining both loaders (`framework-mode`)

With SSR, `loader` provides the document/prerender value and `clientLoader` handles later
browser navigation. A client loader can call `serverLoader()` and merge both sources.

```tsx
import type { Route } from "./+types/profile";

export async function loader() {
  return getServerProfile();
}
export async function clientLoader({ serverLoader }: Route.ClientLoaderArgs) {
  return { ...(await serverLoader()), theme: getLocalTheme() };
}
clientLoader.hydrate = true as const;
export function HydrateFallback() { return <p>Loading…</p>; }
```

`clientAction` takes precedence over `action` in the browser but may call
`serverAction()` to wrap the server mutation with client work.

```ts
export async function clientAction({ serverAction }: Route.ClientActionArgs) {
  invalidateClientCache();
  return serverAction();
}
```

### Hydrating client loaders (`data-loading-and-rendering`)

A route with `clientLoader` but no `loader` implicitly hydrates the client loader. Export
`HydrateFallback` while that first browser-only load runs.

When both loaders exist and `clientLoader.hydrate = true`, omitting a fallback renders the
route component on the server while the client loader runs during hydration. Its first
result must equal server loader data or hydration will mismatch; cache-priming code should
return `serverLoader()` on that pass.

### SPA build-time loader rules (`7.2.0`)

With `ssr: false`, root may have a build-time `loader`. Without prerender, other loaders
are forbidden; configured prerender paths may run their matched loaders. `headers` and
`action` remain unavailable, and non-prerendered dynamic paths need `clientLoader`.
`Route.HydrateFallbackProps.loaderData` is optional while child routes resolve.

## Revalidation and data strategies

### Framework defaults (`framework-mode`)

SSR Framework Mode revalidates route loaders after every navigation and form submission,
unlike Data Mode. Override per route with `shouldRevalidate`. SPA Mode has no server
loaders on navigation and therefore behaves like Data Mode.

```ts
export function shouldRevalidate() {
  return false;
}
```

After an action returns a 4xx or 5xx, Framework Mode supplies
`defaultShouldRevalidate: false` from `7.10.0`; overrides that return the default no
longer cause unintended error revalidation.

`Form`, `submit`, `fetcher.Form`, `fetcher.submit`, `Link`, `navigate`, and
`setSearchParams` gained the provisional `unstable_defaultShouldRevalidate` in `7.11.0`.
Set it false to opt out at the call site, while route `shouldRevalidate` retains final say.
The option stabilizes as `defaultShouldRevalidate` in `7.15.0`; when false, parent routes
without their own `shouldRevalidate` are excluded from the Single Fetch request for new
child data.

### Custom `dataStrategy`

`unstable_dataStrategy` stabilized as `dataStrategy` in `7.0.0`. In `7.10.0`, rename
`match.unstable_shouldCallHandler()` and `match.unstable_shouldRevalidateArgs` to
`match.shouldCallHandler()` and `match.shouldRevalidateArgs`; `match.shouldLoad` is
deprecated. From `7.11.0`, an insufficient custom result set produces errors for routes
whose results are missing instead of leaving them unavailable.

## Fetchers, navigation, and search parameters

### Await operations (`7.0.0`)

`useNavigate()`, `useSubmit()`, `fetcher.load`, `fetcher.submit`, and
`revalidator.revalidate()` expose their completion promises. From `7.10.0`, navigate's
promise covers the full `popstate` navigation, so back/forward travel can be awaited.

```ts
await navigate(-1);
await fetcher.submit(formData, { method: "post" });
```

### Fetcher lifecycle

`fetcher.unstable_reset()` resets to the initial `idle` state in `7.9.0`; it becomes
`fetcher.reset()` in `7.10.0`. From `7.15.0`, `useFetchers()` preserves array identity
until the fetcher collection actually changes, making memo/effect dependencies stable.

`patchRoutesOnNavigation` receives `fetcherKey` in `7.3.0`; from `7.7.0`, fetcher-triggered
callbacks receive a `path` without search parameters.

### Search-parameter isolation (`7.7.0`)

The updater passed to `setSearchParams` receives a copy of the active
`URLSearchParams`. Mutating it cannot alter router state before navigation succeeds, so a
blocked navigation no longer desynchronizes it from `useLocation().search`.

## Pending state and React transitions

### Transition controls (`7.10.0`)

In Framework/Data Mode, leaving `unstable_transition` unset on `HydratedRouter` or
`RouterProvider` preserves wrapping state updates in `React.startTransition`. `true` also
wraps `Link`/`Form` navigation and uses React 19 `useOptimistic` for optimistic navigation
and fetchers; `false` disables both. Declarative Mode offers transition-only
`unstable_useTransitions` on `BrowserRouter`; that prop becomes `useTransitions` in
`7.15.0`.

```tsx
<RouterProvider router={router} unstable_transition={true} />
<BrowserRouter useTransitions={false}>{children}</BrowserRouter>
```

### Router snapshots (`7.15.0`)

`unstable_useRouterState()` returns an always-present `active` snapshot and a `pending`
snapshot during navigation. Each collects location, search params, params, matches,
navigation type/state, and submission data. It works only in Framework, Data, and RSC
modes and throws without a data router.

```tsx
const { active, pending } = unstable_useRouterState();
const location = pending?.location ?? active.location;
```

`useNavigation()` has a properly discriminated `idle`/`loading`/`submitting` union from
`7.16.0`, so testing `state` narrows state-specific fields.

## Prerendering and discovery

### Paths and output (`7.0.0`)

The Vite `prerender` callback emits `.html` and `.data` for chosen paths, including
resource routes. `@react-router/serve` serves `.data` as `text/x-turbo`; output outside
the asset directory has no explicit cache policy.

`prerender: true` builds every static route from `routes.ts`, but parameterized routes
still need explicit path values (`data-loading-and-rendering`). With `ssr: false`, whether
`/` is included controls if `index.html` is generic or root-specific and whether
`__spa-fallback.html` is emitted (`7.2.0`).

Prerendering gained `prerender.unstable_concurrency` in `7.9.0`, renamed to
`prerender.concurrency` in `7.15.0`. Multiple server bundles can be prerendered with the
v8 Vite Environment API in `7.14.0`.

### Link-driven route discovery (`data-loading-and-rendering`)

Lazy discovery initially ships matched routes, batches rendered links into one manifest
request, and patches routes before navigation. A faster click still works after awaiting
discovery. Each route is fetched only once per session.

## Route components and test rendering

`createRoutesStub` passes route component props, including `loaderData`, from `7.6.0`, so
tests can use prop-oriented route components directly.

```tsx
const RoutesStub = createRoutesStub([{
  path: "/",
  loader: () => ({ message: "hello" }),
  Component({ loaderData }) {
    return <p>{(loaderData as { message: string }).message}</p>;
  },
}]);
```

In `7.15.0`, synchronous initial-loader failures in SPA Mode reach `RouterProvider`'s
`onError`, bringing those startup failures into centralized reporting.
