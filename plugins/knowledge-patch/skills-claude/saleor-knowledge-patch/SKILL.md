---
name: saleor-knowledge-patch
description: Saleor
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Saleor Knowledge Patch

Use this skill when changing Saleor GraphQL clients, storefront checkout and
order flows, payment apps, webhooks, Dashboard extensions, catalog and
attribute integrations, authentication, deployment configuration, or upgrade
automation.

> [!CAUTION]
> Guidance labeled `upcoming-3.24` is prerelease guidance and may change before
> stable release.

## Reference index

| Reference | Topics |
| --- | --- |
| [Checkout and orders](references/checkout-and-orders.md) | Checkout creation, addresses, delivery, order updates, metadata, discounts, and GraphQL contracts |
| [Payments and refunds](references/payments-and-refunds.md) | Transactions, payment methods, refund behavior, invoices, gift cards, and zero-total orders |
| [Apps, webhooks, and telemetry](references/apps-webhooks-and-telemetry.md) | Synchronous and asynchronous webhooks, app extensions, app lifecycle, event delivery, and observability |
| [Catalog, attributes, and search](references/catalog-attributes-and-search.md) | Products, variants, models, attributes, stock, media, translations, filters, and search |
| [Accounts and permissions](references/accounts-and-permissions.md) | Registration privacy, password login, staff deletion, app permissions, and attribute permissions |
| [Deployment and removals](references/deployment-and-removals.md) | Environment settings, removed plugins and APIs, EditorJS, exports, digital content, and upgrade cleanup |

## Quick reference: breaking changes and deprecations

### Move checkout delivery flows to explicit calculation

Call `deliveryOptionsCalculate` when a storefront needs to run
`SHIPPING_LIST_METHODS_FOR_CHECKOUT` and
`CHECKOUT_FILTER_SHIPPING_METHODS`. Use `Checkout.delivery` instead of the
deprecated `shippingMethod` and `deliveryMethod` fields, and pass a
`CheckoutDelivery` ID to
`checkoutDeliveryMethodUpdate.deliveryMethodId`.

Treat `CheckoutProblemDeliveryMethodStale` as non-blocking: calculation or
completion revalidates it. `CheckoutProblemDeliveryMethodInvalid` blocks
completion until a valid delivery is assigned.

### Do not depend on integration side effects from reads or async events

Checkout read queries no longer run checkout tax or shipping webhooks, and
order read queries no longer run order tax or shipping webhooks. Preparing
asynchronous order, draft-order, or fulfillment events also does not invoke
synchronous tax or shipping hooks. Those hooks run only when their data is
actually requested.

`draftOrderUpdate` and `orderUpdate` emit no update webhook when nothing
changed. Shipping-filter hooks are also skipped when a related mutation
produces no available-method change.

### Migrate deprecated product, discount, and export interfaces

Use `Product.productVariants` instead of deprecated `Product.variants`. Use
`OrderDiscount.total` instead of deprecated `OrderDiscount.amount`, and move
away from `draftOrderInput.discount`.

Products may have multiple variants regardless of `ProductType.hasVariants`;
that field is deprecated and no longer prevents assigning variant attributes.
Replace the deprecated draft-order `voucher` input with `voucherCode`.

The product, gift-card, and voucher export mutations are deprecated in favor
of fetching GraphQL data for external export tooling. See the deployment
reference for removed export surfaces in prerelease guidance.

### Migrate legacy payment and plugin integrations

Do not combine legacy `Payment` records and Transactions on one checkout;
creating a legacy payment after a Transaction exists is rejected. Adyen and NP
Atobarai gateway plugins are removed in favor of their apps, and
`Payment.partial` is gone.

The invoicing plugin and deprecated `mirumee.payments.stripe` plugin are
removed. Use an invoice app and migrate Stripe references to
`saleor.payments.stripe`. The plugin-manager methods `perform_mutation` and
`change_user_address` are also removed.

### Update app extension manifests

`AppExtension` and `AppManifestExtension` use `settings`, `mountName`, and
`targetName` instead of `options`, `mount`, and `target`. Manifests may still
provide string `mount` and `target` values plus JSON `options`; Dashboard,
rather than Saleor, validates that contract. `tokenTargetUrl` may be omitted,
but `appInstall` still requires `appName` and `manifestUrl`.

### Respect stricter GraphQL contracts

`Attribute.name`, `Attribute.slug`, and `Attribute.type` are non-null, while
`RefundSettingsUpdate.refundSettings` becomes nullable on errors. Federation
`_entities` requires `representations: [_Any!]!`; `AppInstallInput.appName` and
`manifestUrl` are schema-required. Negative `Minute`, `Hour`, and `Day` values
fail GraphQL validation through `NonNegativeInt`.

## Quick reference: commonly used capabilities

### Create and update checkout context

`CheckoutCreateInput` accepts `metadata` and `privateMetadata`, and
`CheckoutLinesUpdate` accepts per-line `metadata`. `Checkout.customerNote` and
`CheckoutCustomerNoteUpdate` expose customer notes. Filterable subscriptions
cover checkout creation, updates, full payment, and metadata updates.

The checkout and draft-order create/address-update flows accept
`saveBillingAddress` and `saveShippingAddress`. These flags must accompany a
valid address input, apply for signed-in customers at completion, and never
save a Click & Collect shipping address. Without an override, checkouts save
addresses and draft orders do not.

### Use structured transaction amounts and payment details

Payment apps can provide `PaymentMethodDetails` through transaction mutations
or webhooks. The object supports card brand, first and last four digits,
expiration, or a non-card method name. Older transactions are not backfilled,
and apps must explicitly support these fields.

Use `Money.fractionalAmount` with `Money.fractionDigits` when an integration
needs an integer amount and currency precision. Transaction action amounts are
non-null for refund, charge, and cancelation request subscriptions; when an
app omits an amount from a supported response, Saleor uses the payload's
`action.amount`.

### Validate synchronous webhooks against Saleor schemas

Saleor validates response types, string lengths, and numeric ranges for the
listed shipping, tax, and payment/transaction synchronous webhooks. Invalid
shipping responses are logged and ignored. Invalid tax or payment responses
are recorded on the checkout, order, or transaction event and stop checkout
or order processing.

The same JSON Schemas are published from `saleor/json_schemas.py`. A disabled-
by-default circuit breaker can monitor failures in dry-run mode before
blocking is selectively enabled.

### Choose stock availability mode deliberately

`Shop.useLegacyShippingZoneStockAvailability` selects legacy
address/shipping-zone filtering or direct warehouse-channel availability.
Existing installations default to legacy behavior. Setting it to `false`
changes stock validation, reservation, allocation, fulfillment, product
availability, and applicable webhook warehouse selection.

In direct-link mode, the `address` argument on `ProductVariant.stocks`,
`ProductVariant.quantityAvailable`, and `Product.isAvailable` is deprecated
and ignored.

### Use the shared search and filtering system

Orders, draft orders, customers, and Pages use `where` and `search` in place
of deprecated `filter` arguments. Search supports prefix matching, Boolean
`AND`, `OR`, and `-`, quoted phrases, accent-insensitive matching, and relevance
ordering; `RANK` requests relevance sorting explicitly.

Reference and single-reference product filters can match a target by ID, slug,
or SKU without naming the attribute slug. Page attribute filters support
numeric, boolean, date, and reference values, including `containsAll` and
`containsAny`.

### Configure authentication modes

`PasswordLoginMode.DISABLED` makes password token, password-setting,
password-change, password-reset, and token-refresh operations return errors.
`CUSTOMERS_ONLY` strips staff permissions when staff authenticate by password.

Google OIDC refresh tokens require `access_type=offline`. The first OIDC claim
for an existing user invalidates that user's old password.

### Instrument field migration

The `saleor.graphql.field.usage` OpenTelemetry metric counts resolver calls for
deprecated fields and custom fields declared with `monitor_usage=True`. Saleor
can emit metrics and OTLP traces with W3C Trace Context; its public telemetry
stream omits codebase-oriented details such as individual SQL queries.

### Check the detailed reference before shipping

The reference files contain the full contracts, defaults, permission changes,
event names, removals, and prerelease markers. Consult the relevant topic file
before changing a client, app, deployment, or migration.
