# Dashboards and typed clients

## Unified dashboard extensions (2.0.0)

Admin and Vendor live in the monorepo and use the same
`@mercurjs/dashboard-sdk` Vite plugin:

```typescript
import { dashboardPlugin } from "@mercurjs/dashboard-sdk";

export default {
  plugins: [react(), dashboardPlugin()],
};
```

The plugin derives routes from the page layout. For example:

```text
src/pages/users/[id]/page.tsx -> /users/:id
```

It generates virtual modules for routes, configuration, components, menus, and i18n.
It also supports hot reloading and automatically loads Medusa plugin UI extensions.

## Shared panel primitives (2.0.0)

`@mercurjs/dashboard-shared` provides shared panel primitives, including:

- data-table hooks;
- query-parameter hooks;
- date hooks;
- command-history hooks;
- TanStack Query key factories.

## Route-derived typed client (2.0.0)

`@mercurjs/client` shares route specifications between server and client and exposes
a generated route tree. Rerun the generator after changing API routes:

```bash
mercurjs codegen
```

Collection routes use methods such as `query` and `mutate`. Dynamic segments become
`$` properties and parameter keys:

```typescript
const products = await sdk.admin.products.query({ limit: 10 });
const product = await sdk.admin.products.$id.query({ $id: "prod_123" });
await sdk.admin.products.mutate({ title: "New Product" });
await sdk.admin.products.$id.delete({ $id: "prod_123" });
```

## Vendor-panel notifications (1.0.0)

The Vendor panel includes UI notifications, giving sellers an in-dashboard channel
for marketplace events. Admin notifications are excluded from the seller feed, so
seller-facing notifications remain scoped away from administrator events.
