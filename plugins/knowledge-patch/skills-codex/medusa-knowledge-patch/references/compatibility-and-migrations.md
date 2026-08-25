# Compatibility and migrations

## Dependency and runtime upgrades

### Product-update ordering regression (2.8.0)

Version 2.8.0 can return Product Module service results in an inconsistent
order. This breaks workflows such as `updateProductsWorkflow` when later work,
including price updates, applies data positionally. Upgrade to 2.8.1 as soon as
possible rather than remaining on 2.8.0.

### MikroORM 6 dependency upgrade (2.4.0)

Medusa 2.4 upgrades MikroORM 5 to 6. User projects need no other changes for
MikroORM's breaking APIs, but must upgrade all runtime packages and the CLI to
`6.4.3` with Medusa and refresh the lock file:

```json
{
  "dependencies": {
    "@mikro-orm/core": "6.4.3",
    "@mikro-orm/knex": "6.4.3",
    "@mikro-orm/migrations": "6.4.3",
    "@mikro-orm/postgresql": "6.4.3"
  },
  "devDependencies": {
    "@mikro-orm/cli": "6.4.3"
  }
}
```

### Core dependencies are bundled behind the framework (2.11.0)

Non-Medusa core dependencies are installed internally through
`@medusajs/deps`. Remove direct dependencies on MikroORM, Awilix, `pg`, and the
MikroORM CLI, then reinstall. Rewrite explicit imports to
`@medusajs/framework/mikro-orm/<subpath>`,
`@medusajs/framework/awilix`, and `@medusajs/framework/pg`. Supported
OpenTelemetry imports move to
`@medusajs/framework/opentelemetry/<subpath>`.

### Framework-owned Zod imports (2.13.0)

Zod is a dependency and export of `@medusajs/framework`, making it available
under strict package-manager isolation. Move direct imports to the framework
export; the codemod performs the rewrite:

```ts
import { z } from "@medusajs/framework/zod"
```

```sh
npx medusa codemod replace-zod-imports
```

### Zod 4.2 migration for custom code (2.14.0)

Medusa uses Zod 4. Backends that directly install Zod must upgrade to `4.2.0`.
Before upgrading, migrate Zod 3 usage in custom validators, routes, modules,
workflows, plugins, and Admin extensions:

```sh
yarn add zod@4.2.0
```

Notable rewrites are:

- `invalid_type_error`, `required_error`, and `errorMap` to `error`.
- `.format()` and `.flatten()` to `z.treeifyError`.
- String-format methods such as `z.string().email()` to top-level functions
  such as `z.email()`.
- `.strict()` and `.passthrough()` to `z.strictObject()` and `z.looseObject()`.
- `z.nativeEnum()` to `z.enum()`.
- One-argument `z.record(value)` to `z.record(z.string(), value)`.

### React 19 alignment for direct Icons consumers (2.14.0)

`@medusajs/icons` targets React 19. Projects that install Icons directly must
upgrade React to 19 or pin an earlier Icons release. Indirect consumers need no
change.

### Required React Router upgrade for direct dependencies (2.13.0)

Medusa upgrades `react-router-dom` from `6.20.1` to `6.30.3` for a security fix.
Projects that declare it directly must also upgrade to `6.30.3`.

### Vite 6 peer compatibility (2.6.0)

Medusa accepts Vite 5 or Vite 6 as a peer dependency, so projects can upgrade
to Vite 6 without a peer-dependency conflict.

### Next.js storefronts are incompatible with Node.js 25 (2.13.0)

Medusa's Next.js storefronts are not compatible with Node.js 25. Use another
supported Node.js version for their runtime.

### Monorepo scaffolding for new applications (2.14.0)

`create-medusa-app` and `medusa new` scaffold a `dtc-starter`-based monorepo
with separate backend and storefront packages. The former
`medusa-starter-default` and Next.js Starter Storefront repositories are
deprecated in favor of this layout:

```sh
yarn dlx create-medusa-app@latest my-medusa-store
```

## API, SDK, and type compatibility

### Link and query API renames (2.2.0)

`remoteLink` and `remoteQueryConfig` are deprecated in favor of `link` and
`queryConfig`. `remote-query-entry-points.d.ts` was renamed to
`query-entry-points.d.ts`. The old APIs still work in this release but are
scheduled for removal.

### Inventory location-level batch request rename (2.3.0)

`POST /admin/inventory-items/:id/location-levels/batch` accepts singular
`create` and `delete` properties rather than `creates` and `deletes`, and adds
`update`:

```http
POST /admin/inventory-items/:id/location-levels/batch
Content-Type: application/json

{"create":[],"update":[],"delete":[]}
```

### Payment model fields removed (2.3.0)

The Payment Module no longer stores `region_id` on Payment Collections or
`cart_id`, `order_id`, and `customer_id` on payments. Update code and
integrations that read or write those fields.

### Delivery marking no longer takes a request body (2.4.0)

The Admin JS SDK and request types no longer require the redundant body when
marking a fulfillment as delivered. Omit that payload from callers written for
the previous signature.

### Payment-provider contract redesigned for V2 (2.5.0)

Payment-provider methods take dedicated single input objects such as
`InitiatePaymentInput`, `AuthorizePaymentInput`, `CapturePaymentInput`, and
`RefundPaymentInput`. This also applies to update, delete, retrieve, cancel,
status, list-method, and save-method operations. Providers must throw errors
instead of returning them, and custom providers must update their signatures.

Providers may implement `createAccountHolder` and `deleteAccountHolder`.
`POST /store/payment-collections/:id/payment-sessions` no longer accepts a
caller-supplied `context`; remove it from storefront requests.

### JS SDK user-creation method removed (2.5.0)

The JS SDK no longer exposes its user-creation method. Remove or replace calls
to that client method before upgrading.

### Password-reset token and event contracts (2.6.0)

The provider-identity update endpoint requires the reset token as a Bearer token
instead of a query parameter:

```http
POST /auth/user/emailpass/update
Authorization: Bearer ey...
```

Reset-password event consumers must replace removed `actorType` with
`actor_type`.

### Fulfillment- and payment-status filters removed (2.6.0)

HTTP validators and request types no longer expose fulfillment- and
payment-status filters. Clients must stop sending those fields in filtered
requests.

### Multiple payment account holders per customer (2.7.0)

A customer may have account holders for multiple payment providers. Custom
payment code must replace `customer.account_holder` with
`customer.account_holders` and select the entry for the desired `provider_id`.
Projects without account-holder customizations are unaffected.

### Line-item title and subtitle sources (2.8.0)

Generated line items take their title from the product and subtitle from the
variant, reversing the previous sources. Storefronts and integrations that
display or interpret these fields must account for the breaking change.

### Membership behavior for `in` (2.9.0)

The `in` operator applies inclusion semantics rather than treating its input as
an equality comparison.

### Missing variant inventory is nullable (2.11.0)

In `GET /store/products`, a variant whose sales-channel locations have no
inventory levels returns `inventory_quantity: null`, not `0`. Storefronts must
distinguish missing inventory data from a known zero quantity.

### Refetch utilities take parameter objects (2.11.0)

`refetchEntity` and `refetchEntities` no longer accept positional arguments.
Pass `{ entity, idOrFilter, scope, fields, options }`; the plural utility also
accepts `pagination` and `withDeleted` in the object.

### Upload payloads use base64 encoding (2.11.0)

Files received through `/admin/uploads` are base64-encoded rather than binary.
The built-in Local and S3 providers handle this; custom file providers should
accept both encodings for compatibility.

### Shipping Option Type cardinality change (2.12.0)

The Shipping Option-to-Shipping Option Type relationship changed from
one-to-one to many-to-one and its related property was renamed. This breaking
schema change affects custom code using the relation and is applied by release
migrations.

### HTTP types now match route validators (2.14.0)

HTTP types from `@medusajs/framework/types` exactly reflect the core Zod route
schemas. Runtime API interfaces are unchanged, but explicit type consumers may
need these breaking updates:

- `InventoryLevel` became `AdminInventoryLevel`; `AdminPricePreferenceParams`
  became `AdminGetPricePreferenceParams`.
- `AdminCreatePricePreference.attribute`, `AdminCreatePricePreference.value`,
  and `AdminCreateProductVariantInventoryKit.required_quantity` are required.
- `AdminProductCategoryListParams.name`, `BaseClaimListParams.q`,
  `StoreCustomerAddressFilters.company`, and
  `StoreCustomerAddressFilters.province` were removed.
- `AdminCreateProductVariantPrice.rules` is now `Record` and rejects `null`;
  `AdminUpdateProductVariant.prices` uses
  `AdminUpdateProductVariantPrice[]`; `AdminInventoryItemsParams.location_levels`
  is `{ location_id?: string | string[] }`.
- Collection, fulfillment, shipment, and product-category create/update
  `metadata` inputs accept `null`; fulfillment item IDs and address strings use
  `string | null` rather than `string | undefined`.

### ESM-compliant JavaScript SDK output (2.14.0)

The JavaScript SDK emits explicit `.js` extensions on relative imports, making
its package output fully ESM-compliant for Node.js and modern bundlers.

## CLI and migration behavior

### Production CLI defaults and environment loading (2.5.0)

When `NODE_ENV` is unset, `medusa start` defaults it to `production`. The CLI
always loads `.env` alongside the environment-specific file. A failed
`medusa build` exits with a failure status so CI can detect it.

### Store product variant query changes (2.5.0)

Variant query parameters support filtering by `sku`. `variants.options` is
optional in the TypeScript `StoreGetProductsParams` contract.

### Project-name validation in `create-medusa-app` (2.9.0)

`create-medusa-app` rejects project names containing a dot. Supply a dot-free
project name.

### Order adjustment version migration (2.12.0)

Release migrations add a `version` column to order line-item adjustments. The
accompanying data migration sets every adjustment to the latest version of its
associated order:

```sh
npx medusa db:migrate
```
