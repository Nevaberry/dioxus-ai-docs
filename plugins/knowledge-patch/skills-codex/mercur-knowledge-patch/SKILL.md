---
name: mercur-knowledge-patch
description: Mercur
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Mercur Development Guide

Use this skill for Mercur marketplace architecture, upgrades, block installation,
dashboard extensions, typed API clients, and marketplace operations. First identify
whether the project follows the 1.x monolith or the 2.0 block-owned architecture,
because their extension models differ.

## Reference index

| Reference | Topics |
| --- | --- |
| [Architecture and setup](references/architecture-and-setup.md) | 2.0 core plugin, block ownership, requirements, local services, and project conventions |
| [Blocks and CLI](references/blocks-and-cli.md) | Official blocks, CLI lifecycle, project templates, and command reference |
| [Dashboards and client](references/dashboards-and-client.md) | Admin and Vendor extensions, file-derived routes, shared primitives, and generated clients |
| [Sellers and marketplace operations](references/sellers-and-operations.md) | Onboarding, teams, seller administration, notifications, fulfillment, shipping, orders, commissions, and payouts |
| [Catalog, inventory, and engagement](references/catalog-inventory-and-engagement.md) | Product governance, inventory, merchandising, search, reviews, wishlists, email, and chat |

## Breaking changes and architecture

### Use the block-owned extension model in 2.0

Mercur 2.0 replaces the 1.x monolith and fork-based customization model with
`@mercurjs/core-plugin` plus application-owned blocks. Installing a block copies its
source into the project, where the application owns and can edit it.

A block can span:

- modules and module links;
- workflows and API routes;
- Admin extensions;
- Vendor extensions.

Cart, order, pricing, and vendor workflows can be extended, replaced, or hooked
instead of rebuilt.

`@mercurjs/core-plugin` supplies the marketplace baseline:

- seller, commission, payout, and custom-field modules;
- Admin UI, Vendor UI, and code-generation modules;
- core Medusa integrations.

Optional features come from registries and remain owned and editable by the
application after installation.

### Revalidate 1.0 order and country integrations

The order format changed in Mercur 1.0. Integrations that consume order data cannot
assume the 0.9 representation remains compatible.

The supported-country set also changed in 1.0. Revalidate country-dependent
marketplace configuration when upgrading.

### Preserve automatic order completion behavior

Creating shipping marks an order as completed. Code that reacts to order status
must account for that automatic transition.

## Bootstrap a 2.0 project

Mercur 2.0 requires:

- Node.js 20 or newer;
- PostgreSQL;
- Redis;
- Git.

The Mercur monorepo uses Bun. Create a marketplace with:

```bash
bunx @mercurjs/cli create my-marketplace
```

After project creation, start the runtime with:

```bash
npm run dev
```

The backend runs at `http://localhost:9000`, Admin is available at `/dashboard`,
and Vendor is available at `/seller`.

## Work with registry blocks

The official registry names are:

- `reviews`
- `product-import-export`
- `team-management`
- `wishlist`
- `vendor-notifications`
- `algolia`
- `requests`
- `vendor-chat`

A block may install backend, API, and panel-extension pieces together. Use
`@mercurjs/cli` throughout the project and block lifecycle:

```bash
mercurjs init
mercurjs search -q "payment"
mercurjs view reviews
mercurjs add reviews wishlist vendor-chat
mercurjs diff reviews
mercurjs codegen
mercurjs build
```

The available templates are:

- `basic` for a marketplace with both panels;
- `registry` for distributing blocks;
- `plugin` for reusable Medusa plugins.

## Extend Admin and Vendor dashboards

Admin and Vendor live in the monorepo and use the same
`@mercurjs/dashboard-sdk` Vite plugin:

```typescript
import { dashboardPlugin } from "@mercurjs/dashboard-sdk";

export default {
  plugins: [react(), dashboardPlugin()],
};
```

The plugin derives routes from files. For example,
`src/pages/users/[id]/page.tsx` becomes `/users/:id`. It also:

- generates virtual modules for routes, configuration, components, menus, and i18n;
- supports hot reloading;
- automatically loads Medusa plugin UI extensions.

Use `@mercurjs/dashboard-shared` for shared panel primitives, including data-table,
query-parameter, date, and command-history hooks and TanStack Query key factories.

## Use the route-derived client

`@mercurjs/client` shares route specifications between server and client and exposes
a generated route tree. Run this after changing API routes:

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

## Keep marketplace boundaries intact

Mercur applies several seller and customer boundaries that integrations should
preserve:

- a seller-created promotion can select only that seller's products;
- seller return flows provide seller-specific return shipping options;
- Admin notifications do not appear in the seller feed;
- deleted linked entities are filtered out;
- each order can receive one review;
- duplicate return requests for an order are prevented.

When a seller has no email address, Mercur falls back to the member email. A selected
shipping method can be removed from a cart before checkout.

## Handle commissions and payouts

Marketplace commissions are built in. A zero-percent commission is valid, and the
commission is included in order payouts. Mercur also provides a commission API and
Admin dashboard, plus payout-reversal creation for an already-created payout.

In 2.0, `@mercurjs/payout-stripe-connect` is the bundled Stripe Connect provider,
not a fixed payment implementation. It covers seller account creation and onboarding,
automatic order-to-payout processing, payout webhooks, KYC/KYB data, and idempotent
processing. Another payout provider can replace it.

## Apply project-local conventions

Generated templates contain `.ai/skills/` definitions for:

- Mercur CLI and block conventions;
- Medusa UI conformance;
- Admin pages and forms;
- tabbed wizards;
- 1.x-to-2.0 migration.

Treat those files as the project-local source of extension and migration conventions.
Use the topic references for the complete operational details and earlier marketplace
capabilities.
