---
name: react-router-knowledge-patch
description: React Router v7 changes since training cutoff — Framework mode (routes.ts, Vite plugin), type-safe route modules, middleware with context API, pre-rendering, SPA/SSR config. Load before working with React Router v7+.
license: MIT
metadata:
  author: Nevaberry
  version: "7.14.0"
---

# React Router v7+ Knowledge Patch

Claude's baseline knowledge covers React Router v6 (createBrowserRouter, RouterProvider, loaders/actions, nested routing, data routers) and Remix v2 (file-based routing, Vite plugin, loaders/actions).

This skill provides features from v7.0 (November 2024) through v7.14 (April 2025). React Router v7 merges Remix into React Router.

## Three Modes

| Mode | Entry Point | Use Case |
|------|-------------|----------|
| **Declarative** | `<BrowserRouter>` | Classic client-side routing |
| **Data** | `createBrowserRouter` | Client-side with loaders/actions |
| **Framework** | Vite plugin + `routes.ts` | Full-stack SSR/SPA (all new APIs) |

Framework mode is where all the new APIs live.

## Quick Reference

### routes.ts Helpers

| Helper | Purpose | Example |
|--------|---------|---------|
| `route(path, file, children?)` | Named route | `route("products/:pid", "./product.tsx")` |
| `index(file)` | Index route | `index("./home.tsx")` |
| `layout(file, children)` | Layout wrapper | `layout("./marketing-layout.tsx", [...])` |
| `prefix(path, children)` | Path prefix | `prefix("api", [...])` |
| `flatRoutes()` | File-based (Remix-style) | `import { flatRoutes } from "@react-router/fs-routes"` |

All from `@react-router/dev/routes`. See [references/framework-mode.md](references/framework-mode.md).

### routes.ts Example

```ts
import { type RouteConfig, route, index, layout, prefix } from "@react-router/dev/routes";

export default [
  index("./home.tsx"),
  route("products/:pid", "./product.tsx"),
  layout("./marketing-layout.tsx", [
    route("about", "./about.tsx"),
  ]),
  ...prefix("api", [
    route("users", "./api/users.tsx"),
  ]),
] satisfies RouteConfig;
```

### react-router.config.ts Example

```ts
import type { Config } from "@react-router/dev/config";

export default {
  ssr: true,              // false for SPA mode
  prerender: ["/", "/about"],  // or true for all static paths, or async function
  appDirectory: "app",
  buildDirectory: "build",
} satisfies Config;
```

Pre-render can also be async: `prerender: async ({ getStaticPaths }) => [...getStaticPaths(), ...dynamicPaths]`.

### Generated Route Types

| Type | Use For |
|------|---------|
| `Route.LoaderArgs` | Server loader parameters |
| `Route.ActionArgs` | Server action parameters |
| `Route.ClientLoaderArgs` | Client loader parameters |
| `Route.ClientActionArgs` | Client action parameters |
| `Route.ComponentProps` | Route component props (`loaderData`, `actionData`, `params`, `matches`) |
| `Route.ErrorBoundaryProps` | Error boundary props |
| `Route.HydrateFallbackProps` | Hydration fallback props |
| `Route.MiddlewareFunction` | Server middleware type |
| `Route.ClientMiddlewareFunction` | Client middleware type |

Import per-route: `import type { Route } from "./+types/product"`. Requires `"rootDirs": [".", "./.react-router/types"]` in tsconfig.

### Type-Safe Route Module Example

```ts
import type { Route } from "./+types/product";

export async function loader({ params }: Route.LoaderArgs) {
  // params.pid is typed as string
  return { product: await getProduct(params.pid) };
}

export default function Product({ loaderData }: Route.ComponentProps) {
  return <div>{loaderData.product.name}</div>;
}
```

Components receive typed props (`loaderData`, `actionData`, `params`, `matches`) directly — can replace `useLoaderData()`/`useParams()` hooks. See [references/type-safe-routes.md](references/type-safe-routes.md).

### react-router.config.ts

| Option | Type | Purpose |
|--------|------|---------|
| `ssr` | `boolean` | `true` for SSR, `false` for SPA mode |
| `prerender` | `string[] \| boolean \| async fn` | Static pre-rendering paths |
| `appDirectory` | `string` | App source dir (default: `"app"`) |
| `buildDirectory` | `string` | Build output dir (default: `"build"`) |
| `future` | `object` | Future flags (e.g., `{ v8_middleware: true }`) |

See [references/framework-mode.md](references/framework-mode.md).

### Middleware (v8_middleware future flag)

| Concept | Detail |
|---------|--------|
| Enable | `future: { v8_middleware: true }` in config |
| Context | `createContext<T>()` from `"react-router"` |
| Set context | `context.set(myContext, value)` |
| Get context | `context.get(myContext)` in loaders/actions |
| Server export | `export const middleware: Route.MiddlewareFunction[]` |
| Client export | `export const clientMiddleware: Route.ClientMiddlewareFunction[]` |
| Data mode | Attach `middleware` array to route objects |

### Middleware Example

```ts
import { createContext } from "react-router";
const userContext = createContext<User | null>(null);

export const middleware: Route.MiddlewareFunction[] = [
  async function auth({ request, context }, next) {
    const user = await getUser(request);
    if (!user) throw redirect("/login");
    context.set(userContext, user);
    let response = await next();
    return response;
  },
];

export async function loader({ context }: Route.LoaderArgs) {
  const user = context.get(userContext);
  return { profile: await getProfile(user) };
}
```

See [references/middleware.md](references/middleware.md) for client middleware, Data mode, and custom server setup.

## Topic References

- [Framework Mode](references/framework-mode.md) — routes.ts config, file-based routing, react-router.config.ts, pre-rendering
- [Type-Safe Routes](references/type-safe-routes.md) — Auto-generated types, Route.* types, tsconfig setup, component props
- [Middleware](references/middleware.md) — Server/client middleware, typed context API, Data mode integration
