---
name: bigcommerce-knowledge-patch
description: BigCommerce
version: null
license: MIT
metadata:
  author: Nevaberry
---


# BigCommerce Knowledge Patch

Use this skill for BigCommerce work involving B2B companies and quotes,
customer segmentation, payments, checkout session sync, Stencil category
content, customer-group pricing, or Storefront GraphQL schema fields.

## Reference index

| Reference | Topics |
| --- | --- |
| [b2b-and-pricing.md](references/b2b-and-pricing.md) | B2B quote webhooks, company addresses, customer-group markup |
| [customer-segmentation.md](references/customer-segmentation.md) | REST status codes, batch envelopes, validation responses, pagination links |
| [payments-and-checkout.md](references/payments-and-checkout.md) | Payment and shipment fields, stored instruments, Catalyst session sync |
| [storefront-and-stencil.md](references/storefront-and-stencil.md) | Stencil category custom fields, country and currency fields, graduated Storefront GraphQL fields |

## Breaking changes and deprecations

### Parse B2B quote-specific webhook fields

B2B quote events put `quote_id` and `quote_uuid` in `data`.

Do not parse the previously documented `type` and `id` fields from these
events; they are not sent.

### Remove retired alpha B2B fields

The following alpha Storefront GraphQL fields have been removed:

- the `companyUser` query;
- the `updateCompanyUser` mutation;
- the `CompanyOrdersFiltersInput.search` filter.

### Do not rely on alpha payment and shipment fields

`Site.paymentMethods` is an alpha connection containing payment methods that
are enabled for the store and channel. Its `PaymentMethod` nodes expose
`entityId` and `name`.

`OrderShipment.shippingProviderDisplayName` is an alpha human-readable
shipping-provider label.

Both fields are deprecated and are not for production.

### Remove Stencil `is_visible` references

The redundant `is_visible` property on custom-field overrides in Stencil's
`category_content` resource is deprecated and will stop being returned.

Remove theme references to the property. There is no replacement field.

### Observe revised Customer Segmentation statuses

Segment and Shopper Profile delete and remove operations return `200` with a
batch envelope. They use `422` for invalid input, not the formerly documented
empty `204` response.

Create and update validation failures also return `422`, not `400`.

## B2B company addresses

### Available alpha operations

Authenticated company users have these alpha `CompanyMutations` fields:

- `addAddress`;
- `updateAddress`;
- `deleteAddress`.

`CompanyQueries` and `ActiveCompany` provide single-address lookup by
`entityId`.

These mutations and lookups are deprecated and not for production.

### Address filtering and timestamps

Company address connections support these filters:

- `city`;
- `state`;
- `country`;
- `companyIds`.

`CompanyAddress` exposes nullable `createdAt` and `updatedAt` fields.

## Stored payment instruments

### Delete an instrument

Authenticated customers can use the alpha
`CustomerMutations.deleteStoredPaymentInstrument` mutation with
`DeleteStoredPaymentInstrumentInput.token`.

The result exposes typed `errors`. An empty list indicates success.

The schema marks this mutation deprecated because it is not production-ready.

### Update an instrument

The alpha `CustomerMutations.updateStoredPaymentInstrument` mutation accepts:

- a token;
- optional `billingAddress`;
- optional `setAsDefault`.

`setAsDefault` can promote an instrument to default, but it cannot unset the
existing default.

The result includes:

- the updated instrument;
- the resulting default token;
- typed errors.

This mutation is not intended for production use.

## Customer Segmentation response shapes

Create, update, add, and remove responses contain:

- `data`;
- `errors`;
- `meta` with `total`, `success`, and `failed`.

Paginated list responses include `links`.

## Catalyst checkout session sync

Checkout session sync can fail with `Invalid JWT token` or `404` when:

- checkout or login-token routes use the edge runtime;
- `BIGCOMMERCE_STOREFRONT_TOKEN` contains an OAuth token;
- the channel and custom domain do not match;
- the domain is not primary;
- the domain is not fully propagated and verified;
- the redirect exceeds the JWT's 30-second lifetime.

When diagnosing configuration mismatches, inspect these JWT claims:

- `channel_id`;
- `redirect_to`;
- `eat`.

## Customer-group markup

Customer groups can apply an early-access `markup` entry in `discount_rules`.

Use a `method` of `percent` or `price` to raise member prices across the
entire catalog.

A markup rule cannot coexist with other discount-rule types and must be
enabled by support.

## Storefront GraphQL fields

### Country and currency

`Country.stateRequired` reports whether addresses for a country require a
state or province.

The `currencyCode` enum includes `MRU` and `STN`.

### Production-ready fields

These fields have graduated from alpha, are no longer deprecated, and are
production-ready:

- `Locale.fullPath`;
- `Locale.path`;
- `Product.featuredPromotions`.

## Detailed guidance

Use the topic references for complete field groupings and response details:

- consult [b2b-and-pricing.md](references/b2b-and-pricing.md) for B2B payloads,
  company-address schema changes, and markup constraints;
- consult [customer-segmentation.md](references/customer-segmentation.md) for
  REST status and envelope changes;
- consult [payments-and-checkout.md](references/payments-and-checkout.md) for
  stored-instrument behavior and session-sync failure conditions;
- consult [storefront-and-stencil.md](references/storefront-and-stencil.md) for
  Stencil removal guidance and Storefront GraphQL field status.
