# Framework Mode

React Router v7 Framework mode uses a Vite plugin and `routes.ts` for full-stack routing with SSR/SPA support.

## routes.ts

Routes are configured in `app/routes.ts` using helpers from `@react-router/dev/routes`:

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

### File-Based Routing (Remix-Style)

```ts
import { flatRoutes } from "@react-router/fs-routes";
import type { RouteConfig } from "@react-router/dev/routes";

export default flatRoutes() satisfies RouteConfig;
```

## react-router.config.ts

```ts
import type { Config } from "@react-router/dev/config";

export default {
  ssr: true,              // false for SPA mode
  prerender: ["/", "/about"],  // or true for all static paths
  appDirectory: "app",
  buildDirectory: "build",
} satisfies Config;
```

### Pre-rendering

Static paths can be specified as an array, `true` for all static paths, or as an async function:

```ts
export default {
  prerender: async ({ getStaticPaths }) => [
    ...getStaticPaths(),
    ...dynamicPaths,
  ],
} satisfies Config;
```
