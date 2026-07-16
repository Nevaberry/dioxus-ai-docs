# Middleware and Context

## Contents

- [Current context model](#current-context-model)
- [Route-module middleware](#route-module-middleware)
- [Calling `next()`](#calling-next)
- [Error flow](#error-flow)
- [When server middleware runs](#when-server-middleware-runs)
- [Context lifetime](#context-lifetime)
- [Custom static-handler response generation](#custom-static-handler-response-generation)
- [Testing middleware](#testing-middleware)
- [Lazy middleware migration history](#lazy-middleware-migration-history)

## Current context model

Middleware is a stable feature. Define typed keys with `createContext()` and store request or
navigation values in a `RouterContextProvider`.

```ts
import { createContext, RouterContextProvider } from "react-router";

export const userContext = createContext<User>();

export function getContext() {
  const context = new RouterContextProvider();
  context.set(userContext, getCurrentUser());
  return context;
}
```

Use `context.get(key)` and `context.set(key, value)`. The `getContext` spelling applies to the
`createBrowserRouter` option and the `HydratedRouter` prop. Adapter `getLoadContext` functions
also return a provider when middleware is enabled; in v8 that is unconditional.

Client-side `clientLoader` and `clientAction` in Framework Mode, and `loader` and `action` in
Library/Data Mode, receive the typed context. A fresh provider is created for each navigation or
fetcher call; seed it through the router or hydrated-router `getContext` callback.

### Migration of provisional context APIs

The context API evolved in three stages:

1. Early v7 used `unstable_createContext`, an `unstable_InitialContext` `Map`, and
   `unstable_getContext`.
2. Provider-based context then required `unstable_RouterContextProvider`; the Map-returning
   `unstable_InitialContext` was removed, and handler context parameters became read-only
   provider views rather than extensible objects.
3. Stable APIs are `createContext`, `RouterContextProvider`, and `getContext`.

Do not combine examples from different stages. A current provider callback looks like:

```tsx
const router = createBrowserRouter(routes, {
  getContext() {
    const context = new RouterContextProvider();
    context.set(userContext, getCurrentUser());
    return context;
  },
});

<HydratedRouter getContext={getContext} />;
```

In v8, middleware is always enabled and all loaders, actions, and middleware receive a provider.
Remove the old `future.v8_middleware` gate, the Data Mode `Future` augmentation, and the
`MiddlewareEnabled` gating type formerly exposed as `UNSAFE_MiddlewareEnabled`.

## Route-module middleware

Export `middleware` for server document/data requests and `clientMiddleware` for browser-side
navigations. Functions run in route order around the work at the leaf.

```ts
export const middleware = [loggingMiddleware, authMiddleware];
export const clientMiddleware = [clientLoggingMiddleware];
```

At the server leaf, `next()` executes the action or matched loaders and yields the response.
Client middleware's `next()` does not return a `Response`.

In Data Mode, adding middleware to a route is itself the client-middleware opt-in; do not pass
`future.unstable_middleware` to `createBrowserRouter`. Framework Mode required the flag while
the feature was provisional so route-module and context types could change together. The gate
became `future.v8_middleware` before becoming unconditional in v8.

Client middleware runs even when a navigation has no loaders. It receives the inner
`dataStrategy` results on unwind and may post-process them. It can return redirects directly.

## Calling `next()`

A middleware may call `next()` at most once. Calling it twice throws. Returning without calling
it automatically continues the chain, so setup-only middleware can omit explicit forwarding.

```ts
export const middleware: Route.MiddlewareFunction[] = [
  async ({ request, context }) => {
    context.set(userContext, await requireUser(request));
  },
];
```

Server middleware that intentionally does not continue may return a `Response` or `data()`;
`data()` is converted with `Response.json()`.

The provisional `Route.unstable_MiddlewareFunction` return type changed from `Response | void`
to `Response | undefined`. Patch 7.4.1 corrected false type errors for functions that return no
value.

## Error flow

Do not wrap `await next()` in `try`/`catch` to intercept downstream route errors. Earlier
provisional middleware exposed an internal `MiddlewareError`, then rethrew the original error;
the settled flow does not throw downstream errors from `next()`. React Router selects a route
error boundary, renders its response, and passes that response back through ancestor middleware.
Thrown non-redirect `Response` objects also reach route error boundaries.

Error-boundary selection depends on whether handler work has begun:

- An error thrown after `await next()` originates at the throwing route and has loader data.
- An error thrown before `next()` runs before any loaders. React Router bubbles to the highest
  matched route with loader data and then searches upward for a boundary, because the route and
  its descendants cannot render without their loader data.

## When server middleware runs

A document request runs matched server middleware even if the route has no loader. A hydrated
client navigation sends a `.data` request only when a loader or action already requires one, so
server middleware alone does not force a request. Add a loader when the middleware must run on
every matching client navigation:

```ts
export async function loader() {
  return null;
}
```

## Context lifetime

Server context is request-scoped. A document POST can share one provider between its action and
the subsequent loaders, but an SPA submission performs separate POST and GET requests and gets a
new provider for each. Never rely on a value set during the action still existing during SPA
revalidation. Client middleware, client actions, and client loaders can share context because
their work is not split across HTTP requests.

Server middleware can use Node `AsyncLocalStorage.run()` around `next()` to make state visible to
loaders, React Server Components, and Server Actions in the same execution context. Prefer the
explicit React Router provider when the middleware must remain portable across runtimes.

```ts
import { AsyncLocalStorage } from "node:async_hooks";

const currentUser = new AsyncLocalStorage<User>();

export const middleware: Route.MiddlewareFunction[] = [
  async ({ request }, next) =>
    currentUser.run(await getUser(request), next),
];
```

## Custom static-handler response generation

For manual SSR with `createStaticHandler`, use `unstable_generateMiddlewareResponse` on `query`
or `queryRoute`, not the older `unstable_respond`. The callback receives the query function and
must invoke it. This permits setup, cleanup, and handler-error processing around the query.

```ts
await staticHandler.query(request, {
  requestContext: new RouterContextProvider(),
  async unstable_generateMiddlewareResponse(query) {
    const result = await query(request);
    return result instanceof Response ? result : generateHtmlResponse(result);
  },
});
```

The normalized-path option on static-handler `query` and `queryRoute` is named `normalizePath`;
it was initially exposed as `unstable_normalizePath`.

## Testing middleware

`createRoutesStub` supports middleware. Pass a constructed context provider as the second
argument. During the v7 gated stage, render the stub with `future={{ v8_middleware: true }}` to
activate the matching types.

```tsx
const context = new RouterContextProvider();
context.set(userContext, testUser);

const RoutesStub = createRoutesStub(routes, context);
render(<RoutesStub future={{ v8_middleware: true }} />);
```

Without the provisional middleware behavior, v7 `createRoutesStub` retained support for the old
`AppLoadContext` object. Do not pass a `getContext` factory as the stub's second argument.

## Lazy middleware migration history

Early lazy middleware returned `unstable_middleware` from function-form `route.lazy`. In 7.4.1,
that stopped working and temporarily moved to `route.unstable_lazyMiddleware`. The next
per-property lazy API removed that property and used `route.lazy.unstable_middleware`. Treat
these as migration-only spellings and use the stable middleware API supported by the installed
version.
