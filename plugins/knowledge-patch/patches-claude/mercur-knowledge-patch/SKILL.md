---
name: mercur-knowledge-patch
description: Mercur
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Mercur Knowledge Patch

Use this skill when building, extending, or upgrading a Mercur marketplace.
First identify whether the project follows the 1.x application model or the
2.0 core-plugin-and-block model, because extension ownership, setup, and client
integration differ substantially.

## Reference index

| Reference | Topics |
| --- | --- |
| [Architecture and setup](references/architecture-and-setup.md) | Medusa baseline, release maturity, 2.0 plugin-and-block architecture, project-local conventions, runtime requirements |
| [Blocks and CLI](references/blocks-and-cli.md) | Official blocks, installation scope, CLI lifecycle, commands, project templates |
| [Dashboards and typed client](references/dashboards-and-client.md) | Admin and Vendor extensions, dashboard SDK, shared UI primitives, generated route client |
| [Sellers, catalog, and inventory](references/sellers-catalog-and-inventory.md) | Seller access and administration, catalog governance, merchandising, inventory ownership |
| [Orders, commissions, and returns](references/orders-commissions-and-returns.md) | Multi-vendor orders, shipping behavior, commissions, payouts, fulfillment, reviews, returns |
| [Search and engagement](references/search-and-engagement.md) | Algolia updates, wishlists, reviews, email, chat, notification feeds |

## Breaking and upgrade-sensitive changes

### Choose the correct architecture

Mercur 2.0 replaces the 1.x monolith and fork-based customization model with
`@mercurjs/core-plugin` plus application-owned blocks. A block may span
modules, module links, workflows, API routes, and Admin or Vendor extensions.
Cart, order, pricing, and vendor workflows can be extended, replaced, or
hooked instead of rebuilt.

Treat optional block source as project-owned and editable. The core plugin
provides the marketplace baseline and core Medusa integrations; optional
features come from registries.

Read [Architecture and setup](references/architecture-and-setup.md) and
[Blocks and CLI](references/blocks-and-cli.md) before changing project
structure or installing optional features.

### Revalidate 1.0 order and country integrations

The order format changed in 1.0. Integrations consuming order data must not
assume that the 0.9 representation remains compatible.

The supported-country set also changed in 1.0. Revalidate country-dependent
marketplace configuration during an upgrade.

### Account for automatic order completion

Creating shipping marks an order as completed. Code reacting to order status
must account for that automatic transition.

### Regenerate client routes

`@mercurjs/client` shares route specifications between server and client.
Run `mercurjs codegen` after changing API routes so the generated route tree
tracks those changes.

## 2.0 project quick reference

### Create and run a project

Mercur 2.0 requires Node.js 20 or newer, PostgreSQL, Redis, and Git. Its
monorepo uses Bun.

```bash
bunx @mercurjs/cli create my-marketplace
```

After creation, `npm run dev` starts the backend at
`http://localhost:9000`, Admin at `/dashboard`, and Vendor at `/seller`.

### Work with registry blocks

The official block names are `reviews`, `product-import-export`,
`team-management`, `wishlist`, `vendor-notifications`, `algolia`, `requests`,
and `vendor-chat`.

```bash
mercurjs init
mercurjs search -q "payment"
mercurjs view reviews
mercurjs add reviews wishlist vendor-chat
mercurjs diff reviews
mercurjs codegen
mercurjs build
```

See [Blocks and CLI](references/blocks-and-cli.md) for command roles and the
available project templates.

### Configure dashboard extensions

Admin and Vendor use the same `@mercurjs/dashboard-sdk` Vite plugin.

```typescript
import { dashboardPlugin } from "@mercurjs/dashboard-sdk";

export default {
  plugins: [react(), dashboardPlugin()],
};
```

The plugin derives file-based routes, generates virtual modules, supports hot
reloading, and loads Medusa plugin UI extensions automatically. Read
[Dashboards and typed client](references/dashboards-and-client.md) for the
route mapping and generated-module details.

### Call generated routes

Collection routes expose methods such as `query` and `mutate`. Dynamic
segments become `$` properties and parameter keys.

```typescript
const products = await sdk.admin.products.query({ limit: 10 });
const product = await sdk.admin.products.$id.query({ $id: "prod_123" });
await sdk.admin.products.mutate({ title: "New Product" });
await sdk.admin.products.$id.delete({ $id: "prod_123" });
```

### Select a payout provider

`@mercurjs/payout-stripe-connect` is the bundled Stripe Connect provider, not
a fixed payment implementation. It can be replaced with another payout
provider and covers seller onboarding, order-to-payout processing, payout
webhooks, KYC/KYB data, and idempotent processing.

## Marketplace behavior quick reference

### Preserve seller boundaries

- Seller-created promotions can select only that seller's products.
- Seller return flows expose seller-specific return shipping options.
- Admin notifications are excluded from the seller notification feed.
- If a seller has no email address, the member email is used instead.
- Sellers own stock locations, and inventory items can be linked to sellers.

Read [Sellers, catalog, and inventory](references/sellers-catalog-and-inventory.md)
for onboarding, administration, catalog, approval, and inventory details.

### Enforce single-instance customer actions

Mercur permits one review per order and prevents duplicate return requests for
an order.

### Keep linked and indexed data current

Deleted linked entities are filtered out. Inventory-item modifications trigger
an Algolia update, allowing indexed product availability to follow inventory
changes without a separate product edit.

### Handle commissions and payouts

Marketplace commissions are built in, may be zero percent, and are included
in order payouts. Mercur also provides commission administration and payout
reversal creation. See
[Orders, commissions, and returns](references/orders-commissions-and-returns.md)
for the complete order, shipping, commission, payout, and return behavior.

## Known maturity limits

The first marketplace release was still under heavy testing. Its stated limits
include multi-vendor order edge cases, commission calculations for some
currencies, and incomplete API input validation. Preserve that qualification
when reasoning about behavior originating in that release.
