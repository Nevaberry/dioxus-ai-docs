---
name: bigcommerce-knowledge-patch
description: BigCommerce
version: null
license: MIT
metadata:
  author: Nevaberry
---


# BigCommerce Knowledge Patch

Use this skill for BigCommerce development involving Storefront GraphQL,
Customer Segmentation REST responses, B2B quote webhooks, Catalyst checkout
session sync, Stencil category content, or customer-group pricing rules.

## Reference index

| Reference | Topics |
| --- | --- |
| [API responses and webhooks](references/api-responses-and-webhooks.md) | B2B quote event payloads and Customer Segmentation response contracts |
| [GraphQL schema](references/graphql-schema.md) | Alpha, deprecated, removed, and newly stable Storefront GraphQL fields and mutations |
| [Storefront and themes](references/storefront-and-themes.md) | Catalyst session-sync failures and Stencil custom-field visibility |
| [Catalog pricing](references/catalog-pricing.md) | Early-access customer-group markup rules |

## Breaking and deprecated contracts

### Parse quote-specific webhook identifiers

B2B quote events provide these fields in `data`:

- `quote_id`
- `quote_uuid`

They do not provide the previously documented `type` and `id` fields. Webhook
consumers must parse the quote-specific fields.

### Update Customer Segmentation status handling

Segment and Shopper Profile delete or remove operations return `200` with a
batch envelope. Invalid input returns `422`; do not expect the formerly
documented empty `204` response.

Create and update validation failures also return `422`, not `400`.

Create, update, add, and remove responses contain:

- `data`
- `errors`
- `meta`, including `total`, `success`, and `failed`

Paginated list responses include `links`.

### Remove Stencil `is_visible` references

The redundant `is_visible` property on custom-field overrides in Stencil's
`category_content` resource is deprecated and will stop being returned.
Remove theme references to it. There is no replacement field.

### Do not use removed alpha company-user fields

The following alpha Storefront GraphQL fields have been removed:

- the `companyUser` query
- the `updateCompanyUser` mutation
- the `CompanyOrdersFiltersInput.search` filter

## Non-production GraphQL surface

### Payment methods and shipment labels

`Site.paymentMethods` is a new connection containing payment methods enabled
for the store and channel. Its `PaymentMethod` nodes expose:

- `entityId`
- `name`

`OrderShipment.shippingProviderDisplayName` adds a human-readable shipping
provider label.

Both fields are alpha, deprecated, and not for production use.

### Delete a stored payment instrument

Authenticated customers can call the alpha
`CustomerMutations.deleteStoredPaymentInstrument` mutation with
`DeleteStoredPaymentInstrumentInput.token`.

The result exposes typed `errors`; an empty list indicates success. The schema
marks the mutation deprecated because it is not production-ready.

### Update a stored payment instrument

The alpha `CustomerMutations.updateStoredPaymentInstrument` mutation accepts:

- a token
- optional `billingAddress`
- optional `setAsDefault`

`setAsDefault` can promote an instrument to the default, but it cannot unset
the existing default. The result includes the updated instrument, the
resulting default token, and typed errors. The mutation is not intended for
production use.

### Manage company addresses

Authenticated company users gain these alpha `CompanyMutations` fields:

- `addAddress`
- `updateAddress`
- `deleteAddress`

`CompanyQueries` and `ActiveCompany` also gain single-address lookup by
`entityId`. These mutations and lookups are deprecated and not for production
use.

Address connections add these filters:

- `city`
- `state`
- `country`
- `companyIds`

`CompanyAddress` adds nullable `createdAt` and `updatedAt` fields.

## GraphQL additions and production-ready fields

The following fields have graduated from alpha, are no longer deprecated, and
are production-ready:

- `Locale.fullPath`
- `Locale.path`
- `Product.featuredPromotions`

`Country.stateRequired` reports whether addresses for a country require a
state or province. The `currencyCode` enum adds `MRU` and `STN`.

## Catalyst session-sync diagnosis

Checkout session sync can fail with `Invalid JWT token` or `404` under any of
these conditions:

- checkout or login-token routes use the edge runtime
- `BIGCOMMERCE_STOREFRONT_TOKEN` contains an OAuth token
- the channel and custom domain do not match
- the domain is not primary
- the domain is not fully propagated and verified
- the redirect exceeds the JWT's 30-second lifetime

Inspect these JWT claims when diagnosing configuration mismatches:

- `channel_id`
- `redirect_to`
- `eat`

## Customer-group markup

Customer groups can apply an early-access `markup` entry in `discount_rules`.
Its `method` is one of:

- `percent`
- `price`

The rule raises member prices across the entire catalog. It cannot coexist
with other discount-rule types and must be enabled by support.

## Task routing

- For webhook or REST response parsing, use
  [API responses and webhooks](references/api-responses-and-webhooks.md).
- For Storefront GraphQL schema status, inputs, results, removals, filters,
  country behavior, or currencies, use
  [GraphQL schema](references/graphql-schema.md).
- For checkout session sync or Stencil theme migration, use
  [Storefront and themes](references/storefront-and-themes.md).
- For customer-group price increases, use
  [Catalog pricing](references/catalog-pricing.md).
