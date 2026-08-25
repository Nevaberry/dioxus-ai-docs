# Adyen Web upgrades

Use this reference for cross-cutting Adyen Web UI, callback, localization,
typing, and Secured Fields behavior. Items come from
`adyen-web-releases-current` and `adyen-web-releases-history`.

## Select rendering (since v6.43.0)

Select options can carry `tags`. They render as colored labels in both the open
list and collapsed button. `secondaryText` appears below an option name in the
open list and is omitted from the collapsed button.

## WebAuthn and SPC in 3DS2 challenges (since v6.42.0)

The 3DS2 iframe has the attributes needed to allow WebAuthn and Secure Payment
Confirmation challenges in compatible browsers.

## Localized errors outside Secured Fields (since v6.39.0)

Error objects for errors outside Secured Fields also include a translated error
message, allowing consistent localized error handling.

## Ionic Secured Fields domains (since v6.38.0)

Secured Fields recognizes `ionic://` domains, enabling card fields in Ionic
applications that use that URL scheme.

## Larger `onSubmit` payloads (since v6.35.0)

Changes to `sdkData` increase the size of the payload passed to `onSubmit`.
Integrations that copy, validate, log, or impose size limits on that payload
must allow for the increase.

## Bundled translation fallback (since v6.34.0)

English translations are bundled as the fallback. Translations are requested
from the CDN only when the selected locale is supported.

## Amount updates (since v6.31.0)

Drop-in and Components can receive amount updates without reinitialization,
preserving the mounted checkout UI across amount changes.

## Stored-payment filtering (since v6.14.0)

Drop-in accepts a `filterStoredPaymentMethods` callback for choosing which saved
payment methods to display.

## Card-level `onAdditionalDetails` regression

In v6.24.0, `onAdditionalDetails` does not fire when defined only on the Card
component. Define it at Checkout level or update to v6.25.1, where the
regression is fixed.

## Secured Fields upgrade boundaries

- V6.8.0 bundles Secured Fields 5.5.0 with `rem` font-size support.
- V6.11.0 stops using `/binLookup`'s `panLength` as the card-number input's
  `maxlength`.
- V6.23.0 moves to Secured Fields 6.0.0, bumps the JWE version, drops the ACH
  bundle, and disallows the `compat` version on Live.

## TypeScript surface changes

- V6.9.0 adds `onAutoComplete` to `CustomCardConfiguration`.
- V6.20.0 adds billing-address and shopper-detail fields to `PaymentData`.
- V6.20.0 adds `onAddressSelected` to `CardConfiguration`; its callback typing
  is corrected in v6.22.0.
