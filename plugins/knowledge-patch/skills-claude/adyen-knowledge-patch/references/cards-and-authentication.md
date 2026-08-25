# Cards and Authentication

Source batches: `adyen-web-releases-current`,
`adyen-web-releases-history`.

## WebAuthn and SPC in 3DS2 challenges

From v6.42.0, the 3DS2 iframe has the attributes needed to allow WebAuthn and
Secure Payment Confirmation challenges in compatible browsers.

## Healthcare data in BIN lookup callbacks

From v6.41.0, the value passed to `onBinLookup` includes the `healthcare`
field, so card integrations can consume it directly from the callback result.

## Ionic scheme support for Secured Fields

From v6.38.0, Secured Fields recognizes `ionic://` domains, enabling card
fields in Ionic applications that use that URL scheme.

## Split funding sources with sessions

From v6.32.0, card components using split funding sources are supported in
sessions integrations.

## Japanese bonus installments

From v6.31.0, card payments support Japanese bonus installments.

## ACH field behavior

Version 6.12.0 adds an account-type dropdown and an account-number
verification input. Version 6.21.0 adds configuration for prefilling the
account-holder name.

## Card-level additional-details regression

In v6.24.0, `onAdditionalDetails` does not fire when defined only on the Card
component. Define it at Checkout level or update to v6.25.1, where the
regression is fixed.

## Secured Fields upgrade boundaries

Version 6.8.0 bundles Secured Fields 5.5.0 with `rem` font-size support.

Version 6.11.0 stops using `/binLookup`'s `panLength` as the card-number
input's `maxlength`.

Version 6.23.0 moves to Secured Fields 6.0.0, bumps the JWE version, drops the
ACH bundle, and disallows the `compat` version on Live.

## TypeScript surface changes

Version 6.9.0 adds `onAutoComplete` to `CustomCardConfiguration`.

Version 6.20.0 adds billing-address and shopper-detail fields to `PaymentData`
and `onAddressSelected` to `CardConfiguration`. The callback's typing is
corrected in v6.22.0.

## Dual-branded card selection

From v6.21.0, the SDK does not preselect a brand for dual-branded cards
outside Europe, preserving low-cost-routing choice.
