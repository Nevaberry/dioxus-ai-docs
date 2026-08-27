---
name: medusa-knowledge-patch
description: Medusa
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Medusa Knowledge Patch

Use this skill for Medusa backend, Admin, plugin, storefront API, SDK,
module, workflow, migration, payment, pricing, promotion, fulfillment,
inventory, shipping, tax, event, or upgrade work.

Start with the quick references below, then read the topic reference that
matches the task. Preserve the stated scope of each behavior, especially
experimental status, required migrations, removed fields, and changed method
signatures.

## Reference index

| Reference | Topics |
| --- | --- |
| [Upgrades, runtime, configuration, and CLI](references/upgrades-runtime-and-cli.md) | Dependencies, Zod, MikroORM, runtime compatibility, migrations, caching, CLI, and scaffolding |
| [Modules, data modeling, catalog, and Query](references/modules-modeling-and-query.md) | Module services, generated types, links, data models, Query, Index, search, and catalog resources |
| [API, authentication, HTTP types, and SDK](references/api-auth-and-sdk.md) | OAuth, password reset, JWTs, routes, request contracts, HTTP types, and JavaScript SDK changes |
| [Carts, orders, and workflows](references/carts-orders-and-workflows.md) | Cart rules, line items, orders, draft orders, returns, and workflow composition |
| [Payments, pricing, and promotions](references/payments-pricing-and-promotions.md) | Payment providers, refunds, payment sessions, pricing context, currency, and promotions |
| [Fulfillment, inventory, shipping, and tax](references/fulfillment-inventory-shipping-and-tax.md) | Fulfillment, inventory kits, reservations, stock locations, shipping options, and tax |
| [Admin, plugins, and UI](references/admin-plugins-and-ui.md) | Dashboard behavior, UI compatibility, languages, plugins, and Admin extensions |
| [Events, notifications, and files](references/events-notifications-and-files.md) | Event processing, notification payloads, file uploads, and provider-specific notification data |

## How to apply this patch

1. Identify the Medusa packages, API surface, or workflow involved in the
   task.
2. Read the matching reference before changing code or configuration.
3. For an upgrade, check every affected contract: dependencies, migrations,
   request and response shapes, module links, workflow behavior, and provider
   interfaces.
4. Keep experimental capabilities marked experimental and do not present
   their APIs as stable.
5. Do not infer replacement APIs or migration outcomes beyond what a reference
   states.

## Breaking changes and upgrade hazards

### Do not remain on 2.8.0

Medusa 2.8.0 can return Product Module service results in an inconsistent
order. Positional follow-up work, including price updates in
`updateProductsWorkflow`, can target the wrong product. Upgrade to 2.8.1 as
soon as possible.

See [Modules, data modeling, catalog, and Query](references/modules-modeling-and-query.md).

### Move core dependencies behind the framework

Remove direct dependencies on MikroORM, Awilix, `pg`, and the MikroORM CLI.
Rewrite explicit imports through these framework paths:

- `@medusajs/framework/mikro-orm/<subpath>`
- `@medusajs/framework/awilix`
- `@medusajs/framework/pg`
- `@medusajs/framework/opentelemetry/<subpath>` for supported OpenTelemetry imports

See [Upgrades, runtime, configuration, and CLI](references/upgrades-runtime-and-cli.md).

### Migrate custom code to Zod 4.2

Backends that directly install Zod must use `4.2.0`. Migrate Zod 3 usage in
custom validators, routes, modules, workflows, plugins, and Admin extensions.
The detailed rewrite list is in
[Upgrades, runtime, configuration, and CLI](references/upgrades-runtime-and-cli.md).

### Update payment providers to the V2 contract

Payment-provider methods take dedicated single input objects. Providers must
throw errors instead of returning errors to the Payment Module. Remove a
caller-supplied `context` from Store payment-session creation requests.

See [Payments, pricing, and promotions](references/payments-pricing-and-promotions.md).

### Respect module-link cardinality

`link.create` enforces declared one-to-one, one-to-many, and many-to-many
cardinality. Use `isList: true` on one endpoint for one-to-many and on both
endpoints for many-to-many.

See [Modules, data modeling, catalog, and Query](references/modules-modeling-and-query.md).

### Update Shipping Option Type relations

The Shipping Option-to-Shipping Option Type relation changed from one-to-one
to many-to-one, and its property was renamed. Release migrations apply the
schema change.

See [Fulfillment, inventory, shipping, and tax](references/fulfillment-inventory-shipping-and-tax.md).

### Update renamed and removed APIs

- Replace deprecated `remoteLink` and `remoteQueryConfig` with `link` and
  `queryConfig`. The generated declaration file is now
  `query-entry-points.d.ts`.
- Send singular `create` and `delete`, plus `update`, to the inventory
  location-level batch endpoint.
- Stop sending fulfillment- and payment-status filters removed from validators
  and request types.
- Remove calls to the removed JavaScript SDK user-creation method.
- Omit the redundant request body when marking a fulfillment delivered through
  the Admin JS SDK.

See [API, authentication, HTTP types, and SDK](references/api-auth-and-sdk.md),
[Modules, data modeling, catalog, and Query](references/modules-modeling-and-query.md),
and [Fulfillment, inventory, shipping, and tax](references/fulfillment-inventory-shipping-and-tax.md).

### Update authentication callbacks and password reset

Forward every OAuth callback query parameter, including `state` and `error`.
If the Auth Module definition is overridden, include the Cache Module
dependency because OAuth state is stored there temporarily. Send the password
reset token as a Bearer token, and replace reset-event `actorType` with
`actor_type`.

See [API, authentication, HTTP types, and SDK](references/api-auth-and-sdk.md).

### Account for removed payment fields

Payment Collections no longer store `region_id`; payments no longer store
`cart_id`, `order_id`, or `customer_id`. Update integrations that read or write
those fields.

See [Payments, pricing, and promotions](references/payments-pricing-and-promotions.md).

### Check changed line-item and order behavior

Generated line-item titles come from products and subtitles from variants.
Completed orders cannot be canceled. An `item_update` action updates item
metadata, and line-action matching also considers price and metadata when
multiple order items reference one variant.

See [Carts, orders, and workflows](references/carts-orders-and-workflows.md).

### Reconcile explicit HTTP type consumers

Exports from `@medusajs/framework/types` now exactly reflect core Zod route
schemas. Several names, required fields, removed filters, metadata nullability,
and address or fulfillment-item field types changed. Runtime API interfaces
did not change.

See [API, authentication, HTTP types, and SDK](references/api-auth-and-sdk.md).

### Keep direct UI dependencies aligned

Direct `@medusajs/icons` consumers must use React 19 or pin an earlier Icons
release. Projects that directly declare `react-router-dom` must use `6.30.3`.
Medusa Next.js storefronts are incompatible with Node.js 25 in the documented
release.

See [Admin, plugins, and UI](references/admin-plugins-and-ui.md) and
[Upgrades, runtime, configuration, and CLI](references/upgrades-runtime-and-cli.md).

## High-value capabilities

### Cross-module Index queries

The experimental `@medusajs/index` module can filter Products, Product
Variants, Prices, and Sales Channels across module boundaries. It requires
installation, registration, its feature flag, and migrations. Query it through
`query.index`; `$and`, `$or`, `$nin`, and `$not` are supported. Its metadata
count is a PostgreSQL planner estimate, not an exact count.

See [Modules, data modeling, catalog, and Query](references/modules-modeling-and-query.md).

### Cached Query graphs

The early-preview Caching Module supports provider-backed caching, generated
keys and tags, and tag invalidation from module-service mutations. Enable its
feature flag, register the Redis provider, and opt individual Query graphs into
caching. Earlier cache packages are deprecated.

See [Upgrades, runtime, configuration, and CLI](references/upgrades-runtime-and-cli.md).

### Workflow extension points

Cart workflows expose pre-operation `validate` hooks. Pricing-sensitive cart,
order, shipping-option, claim, exchange, order-edit, and return workflows
expose `hooks.setPricingContext`. Workflow implementations can also access step
results through workflow context.

See [Carts, orders, and workflows](references/carts-orders-and-workflows.md) and
[Payments, pricing, and promotions](references/payments-pricing-and-promotions.md).

### Draft orders

Draft-order workflows and HTTP endpoints support creation and operation. The
Draft Order plugin is installed by default from 2.10.0 and adds Admin flows for
creating, editing, and finalizing draft orders with custom prices, line items,
and shipping methods.

See [Carts, orders, and workflows](references/carts-orders-and-workflows.md).

### Generated custom-module types

Development mode writes valid custom-module container mappings to
`.medusa/types/module-bindings.d.ts`. Generated create and update service
methods infer approximate data-model inputs, but every inferred property is
optional, so database constraints still matter.

See [Modules, data modeling, catalog, and Query](references/modules-modeling-and-query.md).

### Promotion controls

Campaign budgets can limit use separately by `customer_id`, `email`, or another
attribute through `USE_BY_ATTRIBUTE`. The `once` allocation method applies a
promotion across at most `max_quantity` cart items, starting with the
lowest-priced eligible items. Promotions can also have their own usage limits.

See [Payments, pricing, and promotions](references/payments-pricing-and-promotions.md).

### Loyalty and account credits

`@medusajs/loyalty-plugin` provides gift cards, account credits, and a base for
custom loyalty features. Install and register it under `plugins`, then run
migrations.

See [Modules, data modeling, catalog, and Query](references/modules-modeling-and-query.md).

### Shipping and tax controls

Shipping Option Types are manageable through Admin, the API, and the JS SDK.
Promotions can restrict free shipping to selected types, and Tax Regions can
define rates for individual Shipping Options.

See [Fulfillment, inventory, shipping, and tax](references/fulfillment-inventory-shipping-and-tax.md)
and [Payments, pricing, and promotions](references/payments-pricing-and-promotions.md).
