# Data Loading and Rendering

## Loader and action return values

### Return values directly under Single Fetch

The `json()` and `defer()` helpers, deferred-data types and symbols, and
`unstable_composeUploadHandlers`, `unstable_createMemoryUploadHandler`, and
`unstable_parseMultipartFormData` were removed in 7.0.0. Return values and promises
directly; use `Response.json()` only when response semantics are required. Loaders
and actions may return `undefined`.

```ts
export function loader() {
  return { report: loadReport() };
}
```

Single Fetch throws unwrapped redirects and excludes redirects from loader-data type
inference as of 7.1.0. This restores pre-Single Fetch redirect handling without
polluting the successful data shape.

Framework loader transport supports maps, sets, dates, and other values beyond JSON
primitives, so route components receive reconstructed generated `loaderData` without
manual JSON flattening. Server response typing preserves `ReadonlyMap` and
`ReadonlySet` rather than widening them to mutable collections (7.8.0).

### Stream timeouts

The removed `ServerRouter.abortDelay` prop was tied to `defer`. Export
`streamTimeout` from `entry.server` to configure Single Fetch stream termination.

```ts
export const streamTimeout = 10_000;
```

## Server and client data functions

### Combine loaders under SSR

When a route exports both functions, `loader` supplies the initial server-rendered
or prerendered value and `clientLoader` handles later browser navigations. The client
loader can call `serverLoader()` to combine server and browser state.

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

Set `clientLoader.hydrate = true as const` to run it before initial hydration. A
route with `clientLoader` but no `loader` hydrates implicitly; export
`HydrateFallback` while it loads. With both loaders and no fallback, the server route
component renders before the hydrating client loader runs, so the first client value
must match server data. Cache-priming code should return `serverLoader()` on that
initial run.

Client-loader type inference needs an explicitly annotated
`Route.ClientLoaderArgs` parameter to keep client-only values such as functions from
being server-serialized in `useRouteLoaderData<typeof clientLoader>` (7.6.0).

### Wrap server actions from the client

In the browser, `clientAction` takes priority over `action` but receives
`serverAction()` so it can perform local work and invoke the server mutation.

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

With SSR, Framework Mode revalidates route loaders after every navigation and form
submission, unlike Data Mode. A route-level `shouldRevalidate` can opt out. SPA Mode
has no navigation-time server loaders and therefore behaves like Data Mode.

After an action returns a 4xx or 5xx response, Framework Mode supplies
`defaultShouldRevalidate: false` to `shouldRevalidate` as of 7.10.0. Overrides that
follow the default no longer repeat loaders after unsuccessful actions.

### Per-call opt-outs

`Form`, `submit`, `fetcher.Form`, `fetcher.submit`, `Link`, `navigate`, and
`setSearchParams` gained provisional `unstable_defaultShouldRevalidate` in 7.11.0;
the stable 7.15.0 spelling is `defaultShouldRevalidate`. Set it to `false` to change
the default for that call; each route's `shouldRevalidate` still has the final say.

```tsx
<Form method="post" defaultShouldRevalidate={false} />
navigate("?analytics=1", { defaultShouldRevalidate: false });
```

When the default is false, parent routes without their own `shouldRevalidate` are
excluded from the Single Fetch request for new child data (7.15.0).

## Awaitable router operations

Since 7.0.0, `useNavigate()`, `useSubmit()`, `fetcher.load`, `fetcher.submit`, and
`revalidator.revalidate()` expose the underlying completion promise. Since 7.10.0,
the navigation promise also covers the full duration of POP history traversal.

```ts
await navigate(-1);
await fetcher.submit(formData, { method: "post" });
await revalidator.revalidate();
```

## Fetchers and search parameters

`fetcher.unstable_reset()` was introduced in 7.9.0 and stabilized as
`fetcher.reset()` in 7.10.0. It returns a fetcher to its initial idle state.

`useFetchers()` preserves its returned array identity until fetcher state actually
changes as of 7.15.0, so memo and effect dependencies do not rerun merely because a
new snapshot was allocated.

Since 7.7.0, the updater callback passed to `setSearchParams` receives a copy of the
current `URLSearchParams`. Mutating it cannot corrupt the router's internal instance
if navigation is blocked.

## Custom data strategies

The stable `dataStrategy` and `patchRoutesOnNavigation` names replaced their
`unstable_` forms in 7.0.0. In 7.10.0, custom strategies must use
`match.shouldCallHandler()` and `match.shouldRevalidateArgs` instead of their
`unstable_` spellings. Prefer them over the deprecated, less capable
`match.shouldLoad`.

If a custom data strategy returns too few results, the router adds route errors for
missing results instead of leaving those routes without results (7.11.0).

## Transition and router-state controls

### React transitions

The 7.10.0 provisional `unstable_transition` option on `RouterProvider` and
`HydratedRouter` keeps existing `React.startTransition` behavior when omitted.
Setting it to `true` also transitions `Link` and `Form` navigation and exposes
optimistic navigation/fetcher state through `React.useOptimistic`, which requires
React 19. Setting it to `false` disables transition and optimistic handling.

Declarative `BrowserRouter` provides transition-only control. Its provisional
`unstable_useTransitions` name stabilized as `useTransitions` in 7.15.0.

```tsx
<RouterProvider router={router} unstable_transition={true} />
<BrowserRouter useTransitions={false}>{children}</BrowserRouter>
```

### Consolidated active and pending state

`unstable_useRouterState()` in 7.15.0 returns an always-present `active` snapshot and
a `pending` snapshot during navigation. Each consolidates location, search params,
params, matches, navigation type/state, and submission data. It works only in
Framework, Data, and RSC modes and throws without a data router.

```tsx
const { active, pending } = unstable_useRouterState();
const location = pending?.location ?? active.location;
```

`useNavigation()` preserves a discriminated union across `idle`, `loading`, and
`submitting` as of 7.16.0, so checking `navigation.state` narrows the accompanying
fields correctly.

## Initial rendering and error reporting

`<RouterProvider fallbackElement>` was removed in 7.0.0. Put
`hydrateFallbackElement` or `HydrateFallback` on the root route. During partial
hydration its initial navigation state remains `idle`.

SPA Mode's `RouterProvider` calls `onError` for synchronous errors from initial
loaders as of 7.15.0, bringing these failures under centralized client reporting.

`Route.HydrateFallbackProps` receives optional loader data in SPA Mode. Meta and
match-level loader data can also be unavailable during error rendering; see the
type-safety reference for the exact `loaderData` migration.
