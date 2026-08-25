---
name: medusa-knowledge-patch
description: Medusa
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Medusa Knowledge Patch

Use this skill for Medusa development, upgrades, integrations, custom modules,
workflows, Admin extensions, storefronts, and operational configuration.

## Find the relevant guidance

| Reference | Topics |
| --- | --- |
| [Compatibility and migrations](references/compatibility-and-migrations.md) | Breaking API and type changes, dependency upgrades, migration hazards, CLI and runtime compatibility |
| [Modules, models, and extensions](references/modules-models-and-extensions.md) | Module services, links, data models, migrations, exports, translation, Loyalty |
| [Authentication, runtime, and query](references/auth-runtime-and-query.md) | OAuth, middleware loading, health, Index queries, caching, logging, JWTs |
| [Payments, pricing, and promotions](references/payments-pricing-and-promotions.md) | Payment methods and completion, pricing rules, promotion behavior, currencies |
| [Carts, orders, workflows, and events](references/carts-orders-workflows-and-events.md) | Cart hooks, order and draft-order flows, retries, idempotency, events and notifications |
| [Fulfillment, inventory, shipping, and tax](references/fulfillment-inventory-shipping-and-tax.md) | Shipping profiles and types, fulfillment, reservations, inventory kits, tax providers |
| [Admin, storefront, and tooling](references/admin-storefront-and-tooling.md) | Admin UI, plugins, SDK capabilities, storefront contracts, scaffolding and locales |

## Critical upgrade checks

### Do not remain on the affected product update release

Version 2.8.0 can return Product Module results in inconsistent order. This can
break positional follow-up work in `updateProductsWorkflow`, including price
updates. Upgrade to 2.8.1 as soon as possible.

### Migrate custom Zod code

Medusa uses Zod 4. Backends that install Zod directly must use `4.2.0`, and
custom validators, routes, modules, workflows, plugins, and Admin extensions
must migrate Zod 3 usage.

```sh
yarn add zod@4.2.0
```

Relevant rewrites include:

- `invalid_type_error`, `required_error`, and `errorMap` to `error`.
- `.format()` and `.flatten()` to `z.treeifyError`.
- String-format methods such as `z.string().email()` to top-level functions
  such as `z.email()`.
- `.strict()` and `.passthrough()` to `z.strictObject()` and `z.looseObject()`.
- `z.nativeEnum()` to `z.enum()`.
- `z.record(value)` to `z.record(z.string(), value)`.

Custom code can import the framework-owned export:

```ts
import { z } from "@medusajs/framework/zod"
```

```sh
npx medusa codemod replace-zod-imports
```

### Remove direct core dependencies

Core non-Medusa dependencies are bundled through `@medusajs/deps`. Remove
direct dependencies on MikroORM, Awilix, `pg`, and the MikroORM CLI, reinstall,
and rewrite explicit imports to:

- `@medusajs/framework/mikro-orm/<subpath>`
- `@medusajs/framework/awilix`
- `@medusajs/framework/pg`
- `@medusajs/framework/opentelemetry/<subpath>` for supported OpenTelemetry imports

### Update payment providers

Payment-provider methods take dedicated single input objects, including
`InitiatePaymentInput`, `AuthorizePaymentInput`, `CapturePaymentInput`, and
`RefundPaymentInput`. The same contract applies to update, delete, retrieve,
cancel, status, list-method, and save-method operations. Providers must throw
errors instead of returning them.

Remove caller-supplied `context` from requests to:

```http
POST /store/payment-collections/:id/payment-sessions
```

### Run required data migrations

Run the release migrations where the guidance calls for schema or data changes:

```sh
npx medusa db:migrate
```

Migration-related changes include stock-location address cardinality, shipping
profiles, workflow-execution retention, the Index module, refund reasons,
order-adjustment versions, Shipping Option Type cardinality, and the Loyalty
plugin. Consult the topic references for each migration's exact conditions and
effects.

### Review HTTP and SDK call sites

- Inventory location-level batch bodies use `create`, `update`, and `delete`,
  not `creates` and `deletes`.
- Marking a fulfillment delivered no longer takes the redundant request body.
- Fulfillment- and payment-status filters were removed from HTTP validators and
  request types.
- The JS SDK user-creation method was removed.
- `refetchEntity` and `refetchEntities` take parameter objects rather than
  positional arguments.
- Exported HTTP types now exactly match core route validators; explicit type
  consumers may require changes.

## High-value extension patterns

### Validate cart operations before they run

Cart workflows expose a `validate` hook. Throw from the hook to abort the
operation:

```ts
import { completeCartWorkflow } from "@medusajs/medusa/core-flows"

completeCartWorkflow.hooks.validate(({ cart }) => {
  if (!cart.metadata.approved_at) {
    throw new Error("Cannot complete unapproved cart")
  }
})
```

### Add dynamic pricing context

Pricing-sensitive workflows expose `hooks.setPricingContext`. Return a
`StepResponse`; its fields participate in pricing-rule selection:

```ts
import { addToCartWorkflow } from "@medusajs/medusa/core-flows"
import { StepResponse } from "@medusajs/workflows-sdk"

addToCartWorkflow.hooks.setPricingContext(() =>
  new StepResponse({ location_id: "loca_1234" })
)
```

The hook result does not override the customer and region established by the
core flow.

### Declare module-link cardinality

`link.create` enforces declared link cardinality. With neither endpoint marked
as a list, both IDs are unique. Mark one endpoint with `isList: true` for
one-to-many or both endpoints for many-to-many:

```ts
export default defineLink(
  ProductModule.linkable.product,
  { linkable: CustomModule.linkable.customModel, isList: true }
)
```

### Package Admin extensions correctly

Plugin builds emit Admin extensions as `index.mjs` and `index.js`. Expose both
through `./admin` or the dashboard will not recognize the package:

```json
{
  "exports": {
    "./admin": {
      "import": "./.medusa/server/src/admin/index.mjs",
      "require": "./.medusa/server/src/admin/index.js",
      "default": "./.medusa/server/src/admin/index.js"
    }
  }
}
```

## Query and caching recipes

### Use the experimental cross-module Index

Install and register `@medusajs/index`, enable `MEDUSA_FF_INDEX_ENGINE=true`,
and run its migrations. Query it through `query.index`:

```ts
const { data, metadata } = await query.index({
  entity: "product",
  fields: ["id", "title", "brand.*"],
  filters: { brand: { name: "Hermes" } },
})
```

Add a custom linked model's property names to `filterable` on that side of the
link. The count in `metadata` is a PostgreSQL planner estimate, not an exact
`COUNT(*)`, and can be inaccurate for small data sets. The module is
experimental and its API is subject to change.

Index filters support nested `$and` and `$or` arrays and the `$nin` and `$not`
operators.

### Opt Query graphs into preview caching

Enable the caching feature, register the Redis provider, and opt a graph in
with `options.cache.enable`:

```ts
const { data } = await query.graph({
  entity: "product",
  filters: { id: "prod_1234" },
  options: { cache: { enable: true } },
})
```

The preview Caching Module uses provider-backed caching, strategy-generated
keys and tags, and module-service mutation events to invalidate tagged entries.
The earlier `@medusajs/cache`, `@medusajs/cache-redis`, and
`@medusajs/cache-inmemory` modules are deprecated.

## Authentication essentials

OAuth authentication requests may provide a per-request `callback_url` and
carry OAuth `state`. Callback handling must forward every provider query
parameter, including `state` and `error`, rather than only `code`.

If the Auth Module definition is overridden, add the Cache Module dependency
because OAuth state is stored there temporarily:

```ts
{
  resolve: "@medusajs/medusa/auth",
  dependencies: [Modules.CACHE, ContainerRegistrationKeys.LOGGER],
  options: { providers: [/* ... */] },
}
```

Provider-identity password reset updates require the reset token as a Bearer
token. Reset-password event consumers use `actor_type`, not the removed
`actorType` property.
