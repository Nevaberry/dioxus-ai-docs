---
name: shopify-knowledge-patch
description: Shopify
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Shopify Knowledge Patch

Use this skill for Shopify API integrations, upgrades, app migrations, storefront work,
Functions, extensions, inventory, fulfillment, payments, subscriptions, and developer
tooling. Read the topic reference that matches the work before changing an integration.

## Reference index

| Reference | Topics |
| --- | --- |
| [api-versioning-and-access.md](references/api-versioning-and-access.md) | API lifecycle, access deadlines, versioned surfaces, enforcement, tokens, and mTLS |
| [custom-data-and-events.md](references/custom-data-and-events.md) | Customer webhooks, metafields, custom IDs, capabilities, Events, and consent |
| [catalog-inventory-and-fulfillment.md](references/catalog-inventory-and-fulfillment.md) | Products, collections, inventory, fulfillment, bundles, and REST image IDs |
| [orders-customers-and-subscriptions.md](references/orders-customers-and-subscriptions.md) | Orders, drafts, exchanges, companies, customers, subscriptions, and tax behavior |
| [payments-discounts-and-delivery.md](references/payments-discounts-and-delivery.md) | Vaulting, gift cards, discounts, delivery promises, profiles, labels, and pickup |
| [storefront-checkout-and-markets.md](references/storefront-checkout-and-markets.md) | Storefront carts, checkout, markets, Hydrogen, UCP, branding, and script tags |
| [functions-extensions-and-tooling.md](references/functions-extensions-and-tooling.md) | Functions, POS, UI extensions, Liquid, analytics, App Home, and Partner API tooling |

## Breaking changes and migrations

### Confirm the effective API version

- Stable versions release quarterly at 17:00 UTC and remain supported for at least
  12 months, with at least nine months of overlap between consecutive versions.
- An inaccessible requested version falls forward to the oldest accessible stable
  version.
- Read `X-Shopify-API-Version` on responses and versioned webhooks to learn the
  version Shopify actually used.
- A deprecation explicitly applied to every supported stable version is not deferred
  by pinning an older version.

### Track published version deadlines

| Version | Access ends |
| --- | --- |
| `2025-07` | `2026-07-16 15:00 UTC` |
| `2025-10` | `2026-10-16 15:00 UTC` |
| `2026-01` | `2027-01-16 15:00 UTC` |
| `2026-04` | `2027-04-16 15:00 UTC` |
| `2026-07` | `2027-07-16 15:00 UTC` |
| `2026-10` | `2027-10-16 15:00 UTC` |
| `2027-01` | `2028-01-16 15:00 UTC` |

Continued use of an unsupported resource after its deadline can delist an app and
block installs for at least seven days. Admin warnings remain until seven days after
the last detected use.

### Migrate customer webhooks

In `2025-01`, embedded customer payloads omit `tags`,
`email_marketing_consent`, `sms_marketing_consent`, `last_order_id`,
`last_order_name`, `total_spent`, and `orders_count`.

Consume the corresponding topics instead:

- `CUSTOMER_TAGS_ADDED` and `CUSTOMER_TAGS_REMOVED`
- `CUSTOMERS_EMAIL_MARKETING_CONSENT_UPDATE`
- `CUSTOMERS_MARKETING_CONSENT_UPDATE`
- `CUSTOMERS_PURCHASING_SUMMARY`

### Replace removed customer payment-method creation

`customerPaymentMethodRemoteCreditCardCreate` is hidden in `2025-01`, requires
`stripePaymentMethodId`, and was scheduled for removal after January 2026. Use
`customerPaymentMethodRemoteCreate`; an invalid customer ID produces a user error.

### Replace removed metafield contracts

- Replace public `PrivateMetafield` usage with app-data metafields for app storage or
  app-reserved namespaces for per-resource data.
- Replace removed `MetafieldStorefrontVisibility` queries, mutations, and
  `visibleToStorefrontApi` fields with reads of `MetafieldDefinition.access` and
  writes through `metafieldDefinitionUpdate`.
- Replace `MetafieldDefinitionInput.useAsCollectionCondition` with
  `capabilities.smartCollectionCondition`.
- Replace removed `metafieldDelete(gid)` with `metafieldsDelete` entries containing
  `ownerId`, `namespace`, and `key`; the mutation does not accept a metafield GID.

### Update fulfillment-hold authorization and fields

`node` and `nodes` return `null` for holds outside the app's fulfillment-order scope.
The required scopes are `read_merchant_managed_fulfillment_orders`,
`read_assigned_fulfillment_orders`, `read_third_party_fulfillment_orders`, and
`read_marketplace_fulfillment_orders` for the corresponding hold owners.

Replace `FulfillmentHold.heldBy` with `heldByApp`, or with `heldByApp.title` when the
former string value is needed.

### Move company-location tax data

Move company-location tax exemptions and registration IDs to
`CompanyLocationTaxSettings`. Replace the four assign/create/revoke mutations with
`companyLocationTaxSettingsUpdate`; see the orders reference for the exact removed
mutation names.

### Prepare for script-tag shutdown

- `ScriptTagInput.displayScope` accepts only `ONLINE_STORE` and defaults to it.
- Thank you and Order status page script tags were deprecated for August 28, 2025.
- Move checkout UI changes to Checkout Extensions and analytics or conversion
  tracking to Web Pixels.
- Online Store script tags stop running on March 1, 2027.

### Meet access and transport deadlines

- All public apps must use expiring offline access tokens starting January 1, 2027.
- The card-deposit endpoint requires an mTLS certificate.

### Handle scheduled schema behavior

- Customer Account API removes `Customer.lastIncompleteCheckout` and Checkout types
  in `2026-10`.
- Beginning in `2026-10`, updating an order shipping address recalculates its taxes.
- GraphQL Admin `2026-10` removes `DraftOrderDiscountNotAppliedWarning.priceRule`.
- `2026-07` removes `DraftOrderLineItem.grams`.
- In POS `2026-07`, bundle components expose discount allocations and fixed-amount
  line-item discounts are per unit.

## High-value current contracts

### Use custom IDs with their present limits

Custom IDs, formerly external keys, are metafield-backed identifiers for any
metafield-capable resource. Lookup by custom ID is limited to products and customers.
`productSet` and unstable `customerSet` support matching-key upserts, but a custom ID
cannot yet serve as the matching key.

### Account for product and inventory behavior

- `ProductInput.handle` is checked for uniqueness when supplied.
- One Storefront `product` or `productByHandle` query can request up to 2,000
  variants; that limit does not apply across multiple product queries in one request
  or when variants are reached through another path.
- `inventoryLevels` and `inventoryLevel` accept `includeInactive`, and
  `InventoryLevel.isActive` reports the result.
- `inventoryActivate` preserves the level's `available` quantity when reactivating it.

### Use the revised order and draft contracts

- `orderCreate` accepts `order.customer.toUpsert` and can attach multiple tracking
  numbers to each fulfillment.
- `DraftOrderLineItemInput.priceOverride` replaces catalog price, requires
  caller-managed currency conversion, and is stripped from bundles and components.
- `CalculateExchangeLineItemInput.variantId` selects the exchange variant.

### Apply discount and delivery semantics precisely

- App-discount inputs and objects distinguish one-time and subscription applicability,
  support `recurringCycleLimit`, and reject both purchase modes set to false.
- App-discount inputs now default `appliesOnSubscription` to `true`.
- Multiple product discounts can apply to one cart line, and discounts can target
  specific markets.
- `deliveryPromiseSettings`, `deliveryPromiseParticipantsUpdate`, and
  `delivery_promise_settings/update` form the read, write, and webhook contract for
  delivery-promise configuration.

### Follow Function response rules

- Use `HttpResponse.header(name: ...)` for case-insensitive lookup of one header;
  the all-header `headers` field remains but is deprecated.
- For JSON responses, use `JSON_body` without `body`. If both are present, `body`
  wins; absent `Content-Type` is filled as `application/json`.
- Malformed metafield input-query variables raise `InvalidVariableValueError` rather
  than behaving as empty input.

## Preview and early-access checks

Treat these items according to their stated availability:

- Physical inventory is a feature preview.
- Next Generation Events is a developer preview.
- Liquid block and partial tags are a developer preview.
- Market-driven shipping and its Admin API are a feature preview.
- Mixed shipping and pickup within one order is a feature preview.
- `SubscriptionContractCalculation` is early access.

Read the topic references before implementing these surfaces; they preserve the
available fields, mutations, and migration details without adding unstated behavior.
