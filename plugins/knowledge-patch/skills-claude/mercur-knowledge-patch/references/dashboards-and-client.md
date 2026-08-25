# Dashboards and Typed Client

## Unified dashboard extensions (2.0.0)

Admin and Vendor live in the monorepo and use the same
`@mercurjs/dashboard-sdk` Vite plugin.

```typescript
import { dashboardPlugin } from "@mercurjs/dashboard-sdk";

export default {
  plugins: [react(), dashboardPlugin()],
};
```

The plugin:

- derives routes, including `src/pages/users/[id]/page.tsx` to `/users/:id`;
- generates virtual modules for routes, configuration, components, menus, and
  i18n;
- supports hot reloading; and
- automatically loads Medusa plugin UI extensions.

Shared panel primitives live in `@mercurjs/dashboard-shared`. They include
data-table, query-parameter, date, and command-history hooks, as well as
TanStack Query key factories.

## Route-derived typed client (2.0.0)

`@mercurjs/client` shares route specifications between server and client and
exposes a generated route tree. Rerun `mercurjs codegen` after changing API
routes.

Collection routes use methods such as `query` and `mutate`. Dynamic segments
become `$` properties and parameter keys.

```typescript
const products = await sdk.admin.products.query({ limit: 10 });
const product = await sdk.admin.products.$id.query({ $id: "prod_123" });
await sdk.admin.products.mutate({ title: "New Product" });
await sdk.admin.products.$id.delete({ $id: "prod_123" });
```
