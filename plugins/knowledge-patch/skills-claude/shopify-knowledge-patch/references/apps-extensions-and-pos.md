# Apps, Extensions, and POS

## Script-tag display scope and migration

`ScriptTagInput.displayScope` accepts only `ONLINE_STORE` and defaults to it
when omitted. Thank you and Order status page script tags were deprecated for
August 28, 2025.

Move checkout UI changes to Checkout Extensions. Move analytics or conversion
tracking to Web Pixels.

Online Store script tags stop running on March 1, 2027, so integrations that
still inject them must migrate before that date.

## Public-app tokens and card-deposit mTLS

All public apps must use expiring offline access tokens starting January 1,
2027. The card-deposit endpoint now requires an mTLS certificate.

## POS data and extension behavior

POS APIs expose cash-management activities and drawers. UI extensions can
print directly to hardware receipt printers and run at a background target.

In `2026-07`, bundle components expose discount allocations, and fixed-amount
line-item discounts are per unit.

## Partner subscription cancellation

The Partner API adds `appSubscriptionCancel`.

## App Home and extension testing

Custom-distribution apps can build Shopify-hosted App Home UI extensions with
Preact, Polaris web components, and the `admin.app.home.render` target.

`@shopify/ui-extensions-tester` supports automated UI-extension testing.

## Mobile App Bridge actions

On mobile, `ActionBar` is removed. The `TitleBar` primary action renders as an
icon button. A CSS variable exposes mobile safe-area insets.
