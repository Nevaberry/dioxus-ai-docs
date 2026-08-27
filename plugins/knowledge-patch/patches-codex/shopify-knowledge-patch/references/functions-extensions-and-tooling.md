# Functions, Extensions, and Tooling

## Localized checkout data and validation

`localizationExtensions` became `localizedFields` on `DraftOrderInput` and
`OrderUpdate` input. `HasLocalizedFields` supports locally required tax-field
validation.

Function `Cart.localizedFields` returns values only for server-side
`purchase.validation.run`.

Across Function APIs, malformed metafield input-query variables raise
`InvalidVariableValueError` instead of being treated as empty.

## Function external-call responses

Use `HttpResponse.header(name: ...)` for a case-insensitive lookup of one header. The
all-header `headers` field remains but is deprecated.

For JSON responses, use `JSON_body` without `body`. If both are present, `body` wins.
When `Content-Type` is missing, it is filled as `application/json`.

## Function data sources

Shopify Functions can read `Customer.createdAt` and Shop User metafields.

## Analytics surfaces

Shop Campaigns performance data is queryable through ShopifyQL. Analytics metric
targets are exposed by the GraphQL Admin API. App Events adds app-usage and
performance data to the Dev Dashboard.

## POS data and extension behavior

POS APIs expose cash-management activities and drawers. UI extensions can print
directly to hardware receipt printers and run at a background target.

In `2026-07`, bundle components expose discount allocations and fixed-amount
line-item discounts are per unit.

## Liquid blocks and partials

Liquid's developer preview adds block and partial tags so templates can compose pages
from reusable pieces.

## App Home and extension testing

Custom-distribution apps can build Shopify-hosted App Home UI extensions with Preact,
Polaris web components, and the `admin.app.home.render` target.

`@shopify/ui-extensions-tester` supports automated UI-extension testing.

## Mobile App Bridge actions

On mobile, `ActionBar` is removed. The `TitleBar` primary action renders as an icon
button. A CSS variable exposes mobile safe-area insets.

## Partner subscription cancellation

The Partner API adds `appSubscriptionCancel`.
