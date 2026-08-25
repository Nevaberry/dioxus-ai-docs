# Middleware and Context

## Context API evolution

Middleware is a stable feature in current React Router, as highlighted in the
7.0-guide. Its typed context surface passed through several provisional shapes, so
match code to the installed version.

### Initial typed context in 7.3.0

Framework `clientLoader` and `clientAction`, plus Data/Library Mode `loader` and
`action`, gained a type-safe `context`. A fresh context is created per navigation or
fetcher call. Early adopters created keys with `unstable_createContext`, seeded a
`Map` through `unstable_getContext`, and changed custom `getLoadContext` functions
from an `AppLoadContext` object to `unstable_InitialContext` when unstable middleware
was enabled.

### Provider instances in 7.8.0

`unstable_getContext` on `RouterProvider`, `HydratedRouter`, and
`unstable_RSCHydratedRouter`, plus middleware-enabled adapter `getLoadContext`, then
had to return an `unstable_RouterContextProvider`, not a `Map`. The
`unstable_InitialContext` type was removed. Loader, action, and middleware parameters
were typed as read-only providers rather than arbitrary extensible objects.

### Stable names in 7.9.0

Use `RouterContextProvider`, `createContext`, and `getContext` without
`unstable_` prefixes. The stable `getContext` spelling applies to both the
`createBrowserRouter` option and the `HydratedRouter` prop.

```ts
import {
  createBrowserRouter,
  createContext,
  RouterContextProvider,
} from "react-router";

const userContext = createContext<User>();
const router = createBrowserRouter(routes, {
  getContext() {
    const context = new RouterContextProvider();
    context.set(userContext, getCurrentUser());
    return context;
  },
});
```

### Unconditional provider context in 8.0.0

Middleware is always enabled in v8. Loader, action, and middleware `context` is
always a `RouterContextProvider`, and a custom-server `getLoadContext` must return a
provider rather than a plain object. The `MiddlewareEnabled` gating type, formerly
exported as `UNSAFE_MiddlewareEnabled`, and Data Mode's `Future` module augmentation
were removed.

```ts
function getLoadContext() {
  return new RouterContextProvider();
}
```

## Route middleware

Framework route modules export `middleware` for server document and data requests
and `clientMiddleware` for browser navigations. Functions run sequentially around
the inner handlers. At the server leaf, `next()` runs loaders or the action and
returns a response; client `next()` does not return a `Response`.

```ts
export const middleware = [loggingMiddleware, authMiddleware];
export const clientMiddleware = [clientLoggingMiddleware];
```

### `next()` rules

A middleware may call `next()` at most once; a second call throws. A middleware that
returns without calling it automatically continues the chain, so setup-only
middleware can omit explicit forwarding.

```ts
export const middleware: Route.MiddlewareFunction[] = [
  async ({ request, context }) => {
    context.set(userContext, await requireUser(request));
  },
];
```

A server middleware can short-circuit before `next()` by returning a `Response` or
`data()`, which becomes `Response.json()`. Client middleware may return redirects
directly as of 7.11.0.

### Error and response flow by version

In 7.4.0, `next()` began rethrowing the original downstream error instead of an
internal `MiddlewareError` wrapper. Early catch blocks had to handle the original
value. `Route.unstable_MiddlewareFunction` also changed from `Response | void` to
`Response | undefined`; 7.4.1 fixed no-return type errors.

In 7.8.0, downstream route errors stopped throwing from `next()`: the selected route
error boundary produces the response, which flows back through ancestor middleware.
Do not build current middleware around `try`/`catch` for downstream boundary errors.
Thrown non-redirect responses also reach route error boundaries.

An error thrown after `await next()` is attributed to the throwing route with loader
data available. An error before `next()` runs before all loaders; React Router starts
at the highest matched route with loader data and searches upward for a boundary,
because routes below that point cannot render without their data.

### When server middleware runs

A document request runs matched server middleware even if no route loader exists. A
hydrated browser navigation only makes a server `.data` request when a loader or
action already requires it, so server middleware alone does not force a request. Add
a loader returning `null` when the middleware must run on every matching navigation.

```ts
export async function loader() {
  return null;
}
```

Data Mode client middleware is enabled by putting middleware on a route, not by
passing `future.unstable_middleware` to `createBrowserRouter` (7.8.0). It runs on
navigations even without loaders and passes inner `dataStrategy` results outward for
post-processing. Framework Mode still required the flag until middleware became
unconditional in v8.

## Context lifetime

Server providers are request-scoped. A document POST can share one provider between
its action and subsequent loaders, but an SPA submission uses separate POST and GET
requests and therefore separate providers. Browser middleware, actions, and loaders
can share client context because that work is not split across HTTP requests.

Node-specific server middleware may wrap `next()` in `AsyncLocalStorage.run()` to
expose request state to loaders, React Server Components, and Server Actions in the
same execution context. Prefer the explicit context API when middleware must remain
portable across runtimes.

```ts
import { AsyncLocalStorage } from "node:async_hooks";

const currentUser = new AsyncLocalStorage<User>();
export const middleware: Route.MiddlewareFunction[] = [
  async ({ request }, next) =>
    currentUser.run(await getUser(request), next),
];
```

## Route stubs

Without middleware, `createRoutesStub` accepts the traditional `AppLoadContext`
object. With the provisional middleware surface in 7.7.0, pass an instantiated
`unstable_RouterContextProvider` as the second argument, not a context factory.

Middleware support was formalized in 7.9.0. Pass a provider and render the stub with
`future={{ v8_middleware: true }}` on v7 to enable the corresponding context type.

```tsx
const context = new RouterContextProvider();
context.set(SomeContext, someValue);
const RoutesStub = createRoutesStub(routes, context);
render(<RoutesStub future={{ v8_middleware: true }} />);
```

## Manual SSR response generation

For `createStaticHandler`, 7.8.0 replaced the `unstable_respond` option with
`unstable_generateMiddlewareResponse` on `query` and `queryRoute`. Its callback
receives the query function and must invoke it, allowing work before/after handlers
and explicit error handling.

```ts
await staticHandler.query(request, {
  requestContext: new RouterContextProvider(),
  async unstable_generateMiddlewareResponse(query) {
    const result = await query(request);
    return result instanceof Response ? result : generateHtmlResponse(result);
  },
});
```

The normalization helper on `staticHandler.query` and `queryRoute` was later named
`normalizePath` in 7.15.0.

## Raw and normalized request URLs

The 7.13.2 `future.unstable_passThroughRequests` option preserved the original
incoming `Request`, including `.data`, `index`, and `_routes` implementation details,
while adding `unstable_url` for normalized routing. The names became
`future.v8_passThroughRequests` and `url` in 7.15.0. In v8 the raw-request behavior
is unconditional. Without the provisional flag, `unstable_url` and `request.url`
both represented the same normalized location.

```ts
export function loader({ request, url }: Route.LoaderArgs) {
  return {
    isDataRequest: new URL(request.url).pathname.endsWith(".data"),
    pathname: url.pathname,
  };
}
```

Trailing-slash-aware endpoints likewise became unconditional in v8. Middleware,
loaders, and actions see the preserved browser trailing slash through the normalized
routing URL while caches must account for the corresponding `_.data` endpoint.

## Lazy middleware migration

In 7.4.1, provisional lazy middleware moved from an `unstable_middleware` value
returned by `route.lazy` to `route.unstable_lazyMiddleware`. In 7.5.0 that property
was removed in favor of `route.lazy.unstable_middleware` inside the per-property
lazy object. Treat both as historical migration spellings and use the stable route
middleware API for current projects.
