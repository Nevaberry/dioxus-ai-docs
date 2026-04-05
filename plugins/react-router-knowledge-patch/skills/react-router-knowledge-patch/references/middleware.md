# Middleware

Middleware requires the `v8_middleware` future flag.

## Enable

In `react-router.config.ts`:

```ts
export default {
  future: { v8_middleware: true },
} satisfies Config;
```

## Typed Context API

Create typed context keys with `createContext` from `react-router`:

```ts
import { createContext } from "react-router";

const userContext = createContext<User | null>(null);
```

## Server Middleware

Export a `middleware` array from any route module:

```ts
export const middleware: Route.MiddlewareFunction[] = [
  async function auth({ request, context }, next) {
    const user = await getUser(request);
    if (!user) throw redirect("/login");
    context.set(userContext, user);
    let response = await next(); // runs loaders, returns Response
    return response;
  },
];
```

## Accessing Context in Loaders/Actions

```ts
export async function loader({ context }: Route.LoaderArgs) {
  const user = context.get(userContext);
  return { profile: await getProfile(user) };
}
```

## Client Middleware

Export `clientMiddleware` for client-side middleware:

```ts
export const clientMiddleware: Route.ClientMiddlewareFunction[] = [
  async function analytics({ request }, next) {
    const response = await next();
    trackPageView(request.url);
    return response;
  },
];
```

## Data Mode (createBrowserRouter)

In Data mode, attach `middleware` array directly to route objects in `createBrowserRouter`.

## Custom Servers

For custom server setups, return a `new RouterContextProvider()` from `getLoadContext` to provide initial context values.
