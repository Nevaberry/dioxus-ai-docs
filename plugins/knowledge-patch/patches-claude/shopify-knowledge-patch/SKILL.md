---
name: shopify-knowledge-patch
description: Shopify
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Shopify Knowledge Patch

Load this skill when work touches Shopify APIs, webhooks, Functions, Liquid,
Hydrogen, app or UI extensions, checkout, Customer Accounts, POS, payments,
subscriptions, markets, inventory, fulfillment, or commerce data models.

Use the quick references for high-impact migrations and common contract
changes. Open the topic reference that matches the work before changing a
query, mutation, webhook consumer, extension, or integration.

## Reference index

| Reference | Topics |
| --- | --- |
| [API lifecycle and removals](references/api-lifecycle-and-removals.md) | Version cadence, fall-forward behavior, access deadlines, versioned surfaces, enforcement, removed schema members |
| [Custom data and metafields](references/custom-data-and-metafields.md) | Metafield permissions, access, constraints, uniqueness, deletion, custom IDs, localized fields, GraphQL errors |
| [Customers, orders, and drafts](references/customers-orders-and-drafts.md) | Customer webhooks, order creation and updates, draft orders, business entities, bundles, attribution, consent |
| [Products, inventory, and fulfillment](references/products-inventory-and-fulfillment.md) | Product queries, variants, media IDs, inventory, holds, fulfillment, exchanges, publishing, shipping labels |
| [Storefront, checkout, and markets](references/storefront-checkout-and-markets.md) | Carts, Customer Accounts, Liquid, Hydrogen, market context, shipping, branding, UCP |
| [Payments, discounts, and subscriptions](references/payments-discounts-and-subscriptions.md) | Payment methods, vaulting, delivery promises, app discounts, subscriptions, gift cards, tax and settlement behavior |
| [Functions, events, and analytics](references/functions-events-and-analytics.md) | Function response handling and data, analytics, events, webhook previews |
| [Apps, extensions, and POS](references/apps-extensions-and-pos.md) | Script tags, access tokens, mTLS, POS, App Home, extension testing, App Bridge |

## Breaking changes and deadlines

### Verify the API version actually served

Stable versions release quarterly at 17:00 UTC, remain supported for at least
12 months, and overlap consecutive versions by at least nine months. A request
for an inaccessible version falls forward to the oldest accessible stable
version. Read `X-Shopify-API-Version` on responses and versioned webhooks to
identify the version actually used.

### Plan around published access deadlines

| API version | Access ends at 15:00 UTC |
| --- | --- |
| `2025-07` | `2026-07-16` |
| `2025-10` | `2026-10-16` |
| `2026-01` | `2027-01-16` |
| `2026-04` | `2027-04-16` |
| `2026-07` | `2027-07-16` |
| `2026-10` | `2027-10-16` |
| `2027-01` | `2028-01-16` |

Pinning an older version does not postpone a deprecation that Shopify applies
across every supported stable version. Continued use of an unsupported
resource after its deadline can delist an app and block installs for at least
seven days.

### Migrate customer webhook payloads

In `2025-01`, embedded customer payloads omit `tags`,
`email_marketing_consent`, `sms_marketing_consent`, `last_order_id`,
`last_order_name`, `total_spent`, and `orders_count`. Consume the dedicated
customer tags, marketing-consent, and purchasing-summary webhook topics
instead. See the exact topic names in
[customers, orders, and drafts](references/customers-orders-and-drafts.md).

### Replace remote credit-card creation

`customerPaymentMethodRemoteCreditCardCreate` is hidden in `2025-01`, requires
`stripePaymentMethodId`, and was scheduled for removal after January 2026.
Use `customerPaymentMethodRemoteCreate`; an invalid customer ID produces a
user error.

### Remove Customer Account checkout dependencies

Customer Account API removes `Customer.lastIncompleteCheckout` and the
Checkout types in `2026-10`. Headless checkout SSO supports the documented
`sso=silent` flow.

### Retire script-tag integrations

`ScriptTagInput.displayScope` accepts only `ONLINE_STORE` and defaults to it
when omitted. Thank you and Order status page script tags were deprecated for
August 28, 2025. Online Store script tags stop running on March 1, 2027.

Move checkout UI changes to Checkout Extensions and analytics or conversion
tracking to Web Pixels.

### Adopt expiring public-app tokens and card-deposit mTLS

All public apps must use expiring offline access tokens starting January 1,
2027. The card-deposit endpoint requires an mTLS certificate.

### Update metafield deletion and storefront access

`metafieldDelete(gid)` was removed. Use `metafieldsDelete` with entries that
identify `ownerId`, `namespace`, and `key`; it does not accept a metafield GID.

The `MetafieldStorefrontVisibility` object, its queries and mutations, and
`visibleToStorefrontApi` fields were removed. Read
`MetafieldDefinition.access` and change it with `metafieldDefinitionUpdate`.

### Update REST product-image GIDs

REST Admin `2025-01` returns product-image `admin_graphql_api_id` values as
`gid://shopify/MediaImage/...`, not `gid://shopify/ProductImage/...`. Migrate
with `medias.id`, not `medias.legacy_id` or `product_images.id`. Older API
versions retain the old GID.

### Account for removed schema members

`ShopifyPaymentsBankAccount.accountNumber` and `routingNumber` were removed.
Several `PriceListUserErrorCode` values were also removed; consult
[API lifecycle and removals](references/api-lifecycle-and-removals.md) for the
complete list. `ITEM_NOT_STOCKED_AT_LOCATION` is no longer an inventory error.

## High-use API changes

### Authorize fulfillment-hold reads by ownership

`node` and `nodes` return `null` for a fulfillment hold outside the app's
fulfillment-order scope. Merchant-managed, app-assigned, third-party, and
marketplace holds each require their corresponding read scope. Replace
`FulfillmentHold.heldBy` with `heldByApp`, using `heldByApp.title` when the
former string value is needed.

### Handle multiple holds and SKU sharing

A fulfillment order can have multiple independently releasable holds in
`2025-01`. `fulfillmentServiceCreate` defaults `permitsSkuSharing` to `true`,
unless the input overrides it.

### Use the expanded product and variant contracts

`productTags`, `productTypes`, and `productVendors` are root connections with
cursor pagination instead of a 250-item cap. `ProductInput.handle` is checked
for uniqueness when supplied. One Storefront `product` or `productByHandle`
query can request up to 2,000 variants, subject to the path-specific limits in
the product reference.

### Create orders and control draft pricing

`orderCreate` accepts `order.customer.toUpsert` and can attach multiple
tracking numbers to each fulfillment. `DraftOrderLineItemInput.priceOverride`
replaces catalog price, requires caller-managed currency conversion, and is
stripped from bundles and their components.

Beginning with API version `2026-10`, changing an order's shipping address
recalculates its taxes.

### Use custom IDs within their supported scope

Custom IDs are metafield-backed identifiers for any metafield-capable
resource, but lookup by custom ID is limited to products and customers.
`productSet` and unstable `customerSet` support matching-key upserts, but a
custom ID cannot yet be the matching key.

### Handle cart addresses, costs, and line identity

`CartDelivery.addresses` exposes selectable delivery addresses. Cart duty and
tax totals on `Cart.cost` are deprecated because tax and duties are finalized
at checkout with full customer context. `CartLine.viewKey` is readable, and
cart-line update and removal mutations can identify lines with `view_key`.

### Apply app discounts with current defaults

App-discount inputs distinguish one-time and subscription applicability and
support `recurringCycleLimit`; setting both purchase modes to false is
invalid. `appliesOnSubscription` now defaults to `true`. Multiple product
discounts can apply to one cart line, and discounts can target markets.

### Use current Function response handling

Use `HttpResponse.header(name: ...)` for a case-insensitive single-header
lookup; the all-header `headers` field is deprecated. For JSON responses, use
`JSON_body` without `body`: `body` wins when both are present, and a missing
`Content-Type` is filled as `application/json`.

Malformed metafield input-query variables raise `InvalidVariableValueError`
instead of being treated as empty.

## Feature previews and newer capabilities

Treat items explicitly described as developer preview, feature preview, early
access, or unstable according to that stated status.

### Commerce and inventory previews

Physical inventory and mixed shipping plus pickup are available as feature
previews. Market-driven shipping and its Admin API are also in feature
preview. `SubscriptionContractCalculation` is available in early access.

### Events and Liquid previews

Next Generation Events adds field-level trigger control, custom GraphQL
payloads, and query-based delivery filters in developer preview. Liquid's
developer preview adds block and partial tags for reusable composition.

### Platform additions

Shop Campaigns performance data is queryable through ShopifyQL, the GraphQL
Admin API exposes analytics metric targets, and App Events adds app usage and
performance data to the Dev Dashboard.

Oxygen is available on development stores, Hydrogen can deploy to Vercel, and
Storefront Catalog MCP implements UCP while Storefront MCP cart tools are
deprecated in favor of UCP Cart MCP.
