# Storefront, Checkout, and Markets

## Storefront cart delivery and cost changes

`CartDelivery.addresses` exposes selectable delivery addresses.

`Cart.cost` deprecates these fields because tax and duties are finalized at
checkout with full customer context:

- `totalDutyAmount`
- `totalDutyAmountEstimated`
- `totalTaxAmount`
- `totalTaxAmountEstimated`

## Storefront channel context and cart-line identity

Storefront API `@inContext` accepts `channelId`.

`CartLine.viewKey` is readable. `cartLinesUpdate` and `cartLinesRemove` can
identify lines with `view_key`.

## Customer Account checkout removal and SSO

Customer Account API removes `Customer.lastIncompleteCheckout` and the
Checkout types in `2026-10`. Headless checkout SSO supports the documented
`sso=silent` flow.

## Markets API expansion

Markets APIs support `MarketRegionSubdivision`. The GraphQL Admin API can
create channel markets.

## Market-driven shipping and delivery profiles

Market-driven shipping and its Admin API are in feature preview. For that
model, merchant-owned delivery-profile APIs are deprecated. App-owned delivery
profiles can cover all shippable items.

## Liquid blocks and partials

Liquid's developer preview adds block and partial tags so templates can
compose pages from reusable pieces.

## Hydrogen deployment options

Oxygen is available on development stores. Hydrogen can deploy to Vercel.

## Storefront MCP migration to UCP

Storefront Catalog MCP implements UCP. Storefront MCP cart tools are
deprecated in favor of UCP Cart MCP.

## Unified branding and checkout metafields

The Checkout and Accounts Configuration API unifies branding across checkout,
customer accounts, and sign-in.

Checkout metafields are deprecated in Checkout and Customer Account UI
extensions.

## Mixed shipping and pickup

A feature preview allows shipping and pickup within the same order.
