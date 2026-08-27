# API, authentication, HTTP types, and SDK

## Authentication

### Authentication JWT user metadata (since 2.11.0)

JWTs issued by authentication routes now include `user_metadata`, making identity-associated custom data available in the token claims.

### OAuth callback validation requires all query parameters (since 2.2.0)

Third-party callback handling must forward every query parameter returned by the provider, not only `code`; this includes `state` and `error`. If the Auth Module definition is overridden in `medusa-config.ts`, add the Cache Module dependency because OAuth state is stored there temporarily:

```ts
{
  resolve: "@medusajs/medusa/auth",
  dependencies: [Modules.CACHE, ContainerRegistrationKeys.LOGGER],
  options: { providers: [/* ... */] },
}
```

### Password-reset token and event contracts (since 2.6.0)

The provider-identity update endpoint now requires the reset token as a Bearer token instead of a query parameter. Reset-password event consumers must also replace the removed `actorType` property with `actor_type`.

```http
POST /auth/user/emailpass/update
Authorization: Bearer ey...
```

### Per-request OAuth callback URLs (since 2.2.0)

OAuth authentication requests can now include a `callback_url`, allowing different actors or login pages to choose different return destinations. The flow also carries the OAuth `state` parameter.

```http
POST /customer/auth/github
Content-Type: application/json

{"callback_url":"https://example.com/customer/github/callback"}
```

## HTTP types

### HTTP types now match route validators (since 2.14.0)

HTTP types exported from `@medusajs/framework/types` now exactly reflect the core Zod route schemas; runtime API interfaces are unchanged, but explicit type consumers may need these breaking updates:

- `InventoryLevel` is now `AdminInventoryLevel`, and `AdminPricePreferenceParams` is now `AdminGetPricePreferenceParams`.
- `AdminCreatePricePreference.attribute`, `AdminCreatePricePreference.value`, and `AdminCreateProductVariantInventoryKit.required_quantity` are required.
- `AdminProductCategoryListParams.name`, `BaseClaimListParams.q`, `StoreCustomerAddressFilters.company`, and `StoreCustomerAddressFilters.province` were removed.
- `AdminCreateProductVariantPrice.rules` is now `Record` and no longer accepts `null`; `AdminUpdateProductVariant.prices` uses `AdminUpdateProductVariantPrice[]`; `AdminInventoryItemsParams.location_levels` is now `{ location_id?: string | string[] }`.
- Collection, fulfillment, shipment, and product-category create/update `metadata` inputs now accept `null`; fulfillment item IDs and address string fields use `string | null` rather than `string | undefined`.

## JavaScript SDK

### ESM-compliant JavaScript SDK output (since 2.14.0)

The JavaScript SDK now emits explicit `.js` extensions on relative imports, making its package output fully ESM-compliant for Node.js and modern bundlers.

### JS SDK user-creation method removed (since 2.5.0)

The JS SDK no longer exposes its user-creation method. Callers that referenced that client method must remove or replace the call before upgrading.

### SDK token retrieval (since 2.9.0)

The JS SDK client now allows callers to retrieve the token it holds, making that credential available when an integration needs it outside the client's normal request helpers.

## Routes, requests, and responses

### Deterministic API route and middleware loading (since 2.6.0)

The rebuilt loader registers global middleware, route middleware, then API routes. Within the middleware groups, core runs first, registered plugins run in registration order, and the application runs last; matchers are ordered wildcard, regex, static, then dynamic.

A middleware definition without HTTP methods is global, while specifying methods makes it route middleware. Custom middleware extends the existing stack rather than replacing it, and application route overrides still take precedence over plugin and core routes in this release, although that override behavior is planned for removal.

### Draft-order workflows and API endpoints (since 2.7.0)

Core Flows and the HTTP API now provide workflows and endpoints for creating and operating on draft orders.

### Product export behavior (since 2.14.0)

Product export now includes variant images and no longer fails when a `sales_channel_id` filter is supplied.

### Project-name validation in `create-medusa-app` (since 2.9.0)

`create-medusa-app` now rejects project names containing a dot, so project names supplied to the scaffolding command must be dot-free.

### Store product variant query changes (since 2.5.0)

Variant query parameters now support filtering by `sku`, and `variants.options` is optional in the TypeScript `StoreGetProductsParams` contract.

### Store product-type and product-tag endpoints (since 2.4.0)

The Store API now exposes the previously missing product-type and product-tag endpoints, making both resources available to storefront clients.

### Variant identifier filters (since 2.14.0)

Both Store and Admin APIs now support filtering variants by `sku`, `barcode`, `ean`, and `upc`.
