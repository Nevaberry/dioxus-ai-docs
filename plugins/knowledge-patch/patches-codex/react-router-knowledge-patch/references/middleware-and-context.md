# Middleware and Context

## Select APIs by installed version

Middleware is a stable React Router capability in the migration guidance
(`7.0-guide`), but the v7 implementation passed through provisional names before the
context API stabilized. Do not mix these stages:

| Version stage | Context creation and initialization |
| --- | --- |
| `7.3.0` | `unstable_createContext`; callbacks return `unstable_InitialContext` maps |
| `7.8.0` | callbacks return `unstable_RouterContextProvider`; map type removed |
| `7.9.0` | `createContext`, `RouterContextProvider`, and `getContext` are stable names |
| `8.0.0` | middleware/provider context is unconditional; gating types/flags are removed |

## Context evolution

### Initial typed context (`7.3.0`)

Framework `clientLoader`/`clientAction` and Library Mode `loader`/`action` gained typed
client context. A fresh context is created for each navigation or fetcher call and is
seeded by `unstable_getContext` on `createBrowserRouter` or `HydratedRouter`.

Under provisional server middleware, loaders/actions receive typed context rather than
`AppLoadContext`. Create keys with `unstable_createContext`; custom-server
`getLoadContext` must return an `unstable_InitialContext` map instead of an object.

### Provider instances (`7.8.0`)

`unstable_getContext` on `RouterProvider`, `HydratedRouter`, and
`unstable_RSCHydratedRouter`, and adapter `getLoadContext` under
`future.unstable_middleware`, must return an `unstable_RouterContextProvider` instance.
`unstable_InitialContext` is removed, and middleware-enabled context parameters are
read-only providers rather than extensible objects.

```tsx
function getContext() {
  const context = new unstable_RouterContextProvider();
  context.set(userContext, getCurrentUser());
  return context;
}

<RouterProvider router={router} unstable_getContext={getContext} />;
```

### Stable provider names (`7.9.0`)

Remove `unstable_` from `createContext`, `RouterContextProvider`, and `getContext`. The
stable `getContext` spelling applies to both `createBrowserRouter` and `HydratedRouter`.

```ts
import { createBrowserRouter, createContext, RouterContextProvider } from "react-router";

const userContext = createContext<User>();
const router = createBrowserRouter(routes, {
  getContext() {
    const context = new RouterContextProvider();
    context.set(userContext, getCurrentUser());
    return context;
  },
});
```

### Unconditional v8 context (`8.0.0`)

Middleware is always enabled. Loaders, actions, and middleware always receive a
`RouterContextProvider`; custom `getLoadContext` must return a provider rather than a plain
object. Remove `UNSAFE_MiddlewareEnabled` and Data Mode's `Future` augmentation.

```ts
import { RouterContextProvider } from "react-router";

function getLoadContext() {
  return new RouterContextProvider();
}
```

## Server and client route middleware

### Route exports (`framework-mode`)

`middleware` functions run sequentially around server document and data requests. At the
leaf, `next()` executes loaders or the action and returns the response. `clientMiddleware`
wraps browser navigations similarly, but its `next()` has no `Response` return.

```ts
export const middleware = [loggingMiddleware, authMiddleware];
export const clientMiddleware = [clientLoggingMiddleware];
```

### When middleware runs (`middleware`)

Document requests run matched server middleware even without loaders. Hydrated client
navigation sends no `.data` request when no loader/action requires one, so corresponding
server middleware does not run. Add a loader when it must run on every matching client
navigation.

```ts
export async function loader() {
  return null;
}
```

Data Mode client middleware is enabled by adding middleware to a route; passing
`future.unstable_middleware` to `createBrowserRouter` is rejected as of `7.8.0`.
Framework Mode still required that flag at this stage for route-module/context typing.
Client middleware runs even without loaders and receives inner `dataStrategy` results for
post-processing.

### `next()` usage (`middleware`)

A middleware may call `next()` at most once; a second call throws. Returning without
calling it automatically continues the chain, so setup-only middleware can omit it.

```ts
export const middleware: Route.MiddlewareFunction[] = [
  async ({ request, context }) => {
    context.set(userContext, await requireUser(request));
  },
];
```

### Short-circuit responses and redirects

From `7.8.0`, server middleware that skips `next()` may return a `Response` or `data()`;
`data()` becomes `Response.json()`. Client middleware may return redirect responses from
`7.11.0`.

## Errors and response generation

### Evolution of `next()` error behavior

In `7.4.0`, downstream provisional middleware exceptions were rethrown as the original
error instead of an internal `MiddlewareError`; catch original errors. The provisional
`Route.unstable_MiddlewareFunction` return type became `Response | undefined`, and 7.4.1
fixed no-return functions.

By `7.8.0`, downstream server middleware errors no longer make `next()` throw. The chosen
route error boundary handles them and its response unwinds through ancestor middleware;
do not depend on `try`/`catch` around `next()`. Thrown non-redirect responses also reach
route error boundaries.

### Boundary selection (`middleware`)

An error after `await next()` originates at the throwing route with loader data available.
An error before `next()` occurs before loaders; React Router bubbles to the highest matched
route with a loader and searches upward for an error boundary because it cannot render
that route or descendants without loader data.

### Manual SSR response hook (`7.8.0`)

For `createStaticHandler`, replace `unstable_respond` on `query`/`queryRoute` with
`unstable_generateMiddlewareResponse`. The callback receives the query function and must
invoke it, permitting work around handler execution and error capture.

```ts
await staticHandler.query(request, {
  requestContext: new unstable_RouterContextProvider(),
  async unstable_generateMiddlewareResponse(query) {
    const result = await query(request);
    return result instanceof Response ? result : generateHtmlResponse(result);
  },
});
```

## Lazy middleware migration

In 7.4.1, lazy middleware moved to `route.unstable_lazyMiddleware`; returning
`unstable_middleware` from `route.lazy` stopped working (`7.4.0`). The next stage removed
that property and required `route.lazy.unstable_middleware` in the per-property lazy
object (`7.5.0`). These were provisional spellings; use the API appropriate to the
installed version.

## Context lifetime and async-local state

### HTTP request boundaries (`middleware`)

Server context is request-scoped. A document POST can share a provider between its action
and subsequent loaders, but an SPA submission uses separate POST and GET requests with
separate providers. Client middleware, actions, and loaders can share client context
because their execution is not split across HTTP requests.

### AsyncLocalStorage (`middleware`)

Server middleware can wrap `next()` in `AsyncLocalStorage.run()` so request state reaches
loaders, React Server Components, and Server Actions in the same execution context. Use
React Router context when middleware must be portable beyond Node.

```ts
import { AsyncLocalStorage } from "node:async_hooks";

const currentUser = new AsyncLocalStorage<User>();
export const middleware: Route.MiddlewareFunction[] = [
  async ({ request }, next) => currentUser.run(await getUser(request), next),
];
```

## Testing middleware

`createRoutesStub` used the prior `AppLoadContext` object without middleware in `7.7.0`;
with middleware, its second argument had to be an instantiated
`unstable_RouterContextProvider`, not a context factory.

From `7.9.0`, route stubs support middleware with stable provider names. Render the stub
with `future={{ v8_middleware: true }}` to activate corresponding v8 context typing.

```tsx
const context = new RouterContextProvider();
context.set(SomeContext, someValue);
const RoutesStub = createRoutesStub(routes, context);
render(<RoutesStub future={{ v8_middleware: true }} />);
```
