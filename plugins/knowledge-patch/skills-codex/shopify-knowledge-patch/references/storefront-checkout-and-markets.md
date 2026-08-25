# Storefront, Checkout, and Markets

## Storefront cart delivery and cost

`CartDelivery.addresses` exposes selectable delivery addresses.

`Cart.cost` deprecates `totalDutyAmount`, `totalDutyAmountEstimated`,
`totalTaxAmount`, and `totalTaxAmountEstimated` because tax and duties are finalized
at checkout with full customer context.

## Script-tag scope and shutdown

`ScriptTagInput.displayScope` accepts only `ONLINE_STORE` and defaults to it when
omitted. Thank you and Order status page script tags were deprecated for August 28,
2025.

Move checkout UI changes to Checkout Extensions and analytics or conversion tracking
to Web Pixels. Online Store script tags stop running on March 1, 2027.

## Storefront channel context and cart-line identity

Storefront API `@inContext` accepts `channelId`. `CartLine.viewKey` is readable.
`cartLinesUpdate` and `cartLinesRemove` can identify lines with `view_key`.

## Customer Account checkout removal and SSO

Customer Account API removes `Customer.lastIncompleteCheckout` and Checkout types in
`2026-10`. Headless checkout SSO supports the documented `sso=silent` flow.

## Markets

Markets APIs support `MarketRegionSubdivision`. The GraphQL Admin API can create
channel markets.

## Market-driven shipping

Market-driven shipping and its Admin API are in feature preview. Merchant-owned
delivery-profile APIs are deprecated for that model. App-owned delivery profiles can
cover all shippable items.

## Hydrogen deployment

Oxygen is available on development stores, and Hydrogen can deploy to Vercel.

## Storefront MCP migration

Storefront Catalog MCP implements UCP. Storefront MCP cart tools are deprecated in
favor of UCP Cart MCP.

## Unified branding and checkout metafields

The Checkout and Accounts Configuration API unifies branding across checkout,
customer accounts, and sign-in. Checkout metafields are deprecated in Checkout and
Customer Account UI extensions.
