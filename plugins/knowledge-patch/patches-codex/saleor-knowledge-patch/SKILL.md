---
name: saleor-knowledge-patch
description: Saleor
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Saleor Knowledge Patch

Load this skill when designing, upgrading, or debugging Saleor GraphQL clients,
storefronts, apps, Dashboard extensions, payment integrations, or deployments.
Use the index to open the reference file for the area being changed, then apply
the quick-reference rules below before relying on older contracts.

> [!CAUTION]
> Guidance marked `upcoming-3.24` is prerelease guidance and may change before
> stable release.

## Reference index

| Reference | Topics |
| --- | --- |
| [api-auth-and-search.md](references/api-auth-and-search.md) | GraphQL input and nullability changes, authentication, accounts, permissions, filters, and search |
| [checkout-orders-and-delivery.md](references/checkout-orders-and-delivery.md) | Checkout and order mutations, delivery calculation, address persistence, events, metadata, and base prices |
| [payments-transactions-and-discounts.md](references/payments-transactions-and-discounts.md) | Transaction and payment contracts, refunds, invoices, discounts, money, gift cards, and exports |
| [apps-webhooks-and-extensions.md](references/apps-webhooks-and-extensions.md) | Synchronous and asynchronous webhooks, circuit breaking, app lifecycle, extensions, and subscriptions |
| [catalog-attributes-and-content.md](references/catalog-attributes-and-content.md) | Products, variants, attributes, models, translations, stock, media, and digital content |
| [operations-and-observability.md](references/operations-and-observability.md) | Deployment configuration, telemetry, JWKS, rich text, staff deletion, and bulk limits |

## Breaking changes and removals

### Move checkout delivery clients to the explicit delivery contract

Call `deliveryOptionsCalculate` when shipping integrations must run. Consume
`Checkout.delivery` instead of deprecated `shippingMethod` and
`deliveryMethod`, and pass a `CheckoutDelivery` ID to
`checkoutDeliveryMethodUpdate.deliveryMethodId`. Treat a stale delivery problem
as non-blocking and revalidatable, but require a valid delivery before
completion when the problem is invalid.

### Update app-extension field names

Use `settings`, `mountName`, and `targetName` on `AppExtension` and
`AppManifestExtension`; `options`, `mount`, and `target` were removed. A
manifest may still provide string `mount`/`target` and JSON `options`, whose
contract is validated by Dashboard rather than Saleor.

### Remove remaining built-in payment-plugin dependencies

Adyen and NP Atobarai gateway plugins have been removed in favor of their apps,
and `Payment.partial` is gone. The old invoicing plugin and deprecated
`mirumee.payments.stripe` plugin are also gone; use an invoice app and
`saleor.payments.stripe` references.

#### Prerelease gateway removals

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Authorize.Net, Razorpay, Braintree, Dummy, and Dummy Credit Card built-in
plugins are removed. Migrate deployments that still use them before upgrading.

### Rewrite prerelease checkout mutation calls

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Use `id` instead of `checkoutId` in checkout address updates. Replace
`checkoutLineDelete` with `checkoutLinesDelete`, passing `linesIds` and only the
checkout `id`. `checkoutCreate.lines` is optional and may be omitted to create
an empty checkout.

### Move prerelease shop and order settings

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Replace `shopDomainUpdate` with `PUBLIC_URL`. Replace `orderSettingsUpdate` and
the `orderSettings` query with `channelUpdate(orderSettings: ...)` and
`channel.orderSettings`. Remove use of `shopFetchTaxRates` and
`ShopFetchTaxRates`; use a tax configuration mutation such as
`taxConfigurationUpdate`.

### Replace removed and deprecated order, product, and checkout fields

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Replace `orderAddNote` with `orderNoteAdd`, `Order.availableShippingMethods`
with `shippingMethods`, `Product.variant` with the top-level `variant` query,
and `Checkout.note` with `customerNote`.

### Move attribute presentation policy out of removed flags

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Do not use `filterableInStorefront`, `filterableInDashboard`,
`availableInGrid`, or `storefrontSearchPosition` in attribute fields, inputs,
filters, or related sort enums. Put presentation logic in the client or in
attribute metadata; the unused database columns remain temporarily.

## Webhook and app behavior

### Validate synchronous responses before returning them

Saleor strongly validates types, string lengths, and numeric ranges in shipping,
tax, and payment/transaction synchronous-webhook responses. Invalid shipping
responses are logged and ignored. Invalid tax or payment responses are recorded
on the checkout, order, or transaction event and stop checkout or order
processing. Apps can import the same JSON Schemas from
`saleor/json_schemas.py`.

### Do not depend on read or async-event side effects

Checkout and order read queries do not invoke tax or shipping integrations.
Preparing async order, draft-order, or fulfillment events also does not pre-fire
their synchronous hooks. Run integrations through the paths that actually
request their data.

### Account for no-op and deactivated delivery suppression

No-op draft-order and order updates suppress update webhooks, and unchanged
shipping-method availability suppresses filter webhooks. Deactivated apps
receive neither asynchronous nor synchronous webhooks.

### Roll out the circuit breaker deliberately

The synchronous-webhook circuit breaker is disabled by default. It can first
monitor errors in dry-run mode, then selectively block an app after its error
threshold is crossed.

## Checkout, order, and stock behavior

### Choose address persistence explicitly

Checkout and checkout-address mutations, plus draft-order create/update, accept
`saveBillingAddress` and `saveShippingAddress`. Supply a valid address input.
Without an override, checkouts save addresses and draft orders do not; Click &
Collect never saves a shipping address.

### Choose the stock-availability model

`Shop.useLegacyShippingZoneStockAvailability` selects legacy address and
shipping-zone filtering or direct warehouse-channel availability. Existing
installations default to legacy behavior. Setting it to `false` changes stock
validation, reservation, allocation, fulfillment, availability, and relevant
webhook warehouse selection; address arguments are deprecated and ignored in
direct-link mode.

### Preserve explicit mutation semantics

`transactionUpdate` merges metadata maps rather than replacing them. Updating
`Order` or `OrderLine` metadata requires `MANAGE_ORDERS`. `UNCONFIRMED` orders
never refresh denormalized base prices, while `DRAFT` orders refresh them after
a default of 24 hours.

## Payment and transaction behavior

### Use transaction action amounts as the fallback

Refund, charge, and cancelation request subscription actions expose a non-null
amount. When an app omits `amount` from the listed charge, refund, cancelation,
initialize, or process response, Saleor uses the payload's `action.amount`.

### Store payment-method details structurally

Payment apps may provide `PaymentMethodDetails`, including supported card
details or a non-card method name, through transaction mutations or webhooks.
Older transactions are not backfilled and apps must explicitly support the
fields. Move these values out of `TransactionItem` metadata.

### Keep legacy payments separate from transactions

Do not create a legacy `Payment` for a checkout that already has a
`Transaction`. A manual charge on a zero-total order creates neither object nor
an `ORDER_MARKED_AS_PAID` event.

### Avoid floating-point money calculations

Use `Money.fractionalAmount` with `Money.fractionDigits` when an integration
needs an integer amount and currency precision.

## Search, accounts, and permissions

### Migrate filters to `where` and `search`

Orders, draft orders, customers, and Pages use the newer filter/search system;
the older `filter` arguments are deprecated. Search supports prefix matching,
Boolean operators, quoted phrases, accent-insensitive matching, and relevance
ordering, including explicit `RANK` sorting.

### Treat registration state as concealed

Account registration and recovery mutations do not reveal whether an email is
registered, and `accountRegister` no longer returns a user ID. Non-staff
password-reset requests no longer fail solely because `channel` is omitted.

### Enforce prerelease permission distinctions

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Reject `MANAGE_APPS` in app installation requests. For attribute mutations,
require the permission matching the attribute type; a bulk request spanning
types requires all matching permissions, and `MANAGE_PRODUCTS` no longer
authorizes `attributeValueCreate`.

### Distinguish omitted, null, and empty app permissions

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

On `appCreate`, omitted or null `permissions` creates an app without
permissions. On `appUpdate`, omitted or null preserves permissions, while an
empty list clears them.
