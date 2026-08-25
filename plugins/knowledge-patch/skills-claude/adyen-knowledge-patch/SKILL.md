---
name: adyen-knowledge-patch
description: Adyen
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Adyen Knowledge Patch

Use this skill when implementing or upgrading Adyen Web, Drop-in, Components,
sessions flows, or Checkout API v72 integrations. Consult the topic reference
that matches the integration surface, then apply the quick-reference rules
below where relevant.

## Reference index

| Reference | Topics |
| --- | --- |
| [Web components and sessions](references/web-components-and-sessions.md) | Select rendering, sessions behavior, payment-method components, localization, payloads, and amount updates |
| [Cards and authentication](references/cards-and-authentication.md) | 3DS2, BIN lookup, Secured Fields, ACH, card callbacks, TypeScript surfaces, and card-brand behavior |
| [Wallets and mobile payments](references/wallets-and-mobile-payments.md) | Apple Pay, Google Pay, UPI, browser support, issuer filtering, and environment handling |
| [Checkout API v72](references/checkout-api-v72.md) | Request validation, precedence, expiry, status codes, redirects, line-item tax fields, and partial payments |

## Breaking changes and upgrade checks

### Checkout API v72 request validation

Checkout API v72 rejects values that fail the new validation requirements in
requests such as `/payments` and `/sessions`. Audit these fields before an
upgrade:

- `billingAddress.postalCode`
- `billingAddress.stateOrProvinceCode`
- `captureDelayHours`
- `dateOfBirth`
- `deliveryAddress.postalCode`
- `deliveryAddress.stateOrProvinceCode`
- `entityType`
- `metadata`
- `reference`
- `returnUrl`
- `shopperEmail`
- `shopperIP`
- `shopperName.firstName`
- `shopperName.lastName`
- `socialSecurityNumber`
- `telephoneNumber`

For card payments, a card number in `holderName` is rejected with **Invalid
card holder name**. Check mappings that could put PAN input in that parameter.

### Checkout API v72 response handling

Some validation and rate-limit failures return HTTP `422` or `429` instead of
`500`. Treat them as validation and throttling responses rather than server
failures.

In Drop-in `/sessions` redirects, use `redirectResult` to complete payment.
The redirect no longer supplies the erroneous `payload` parameter in its
place.

For `/payments` `lineItems`, include `taxAmount` and `amountExcludingTax`.
Omitting them now produces an error; v72 no longer creates an incorrect
`amountExludingTax` equal to `amountIncludingTax`.

### Checkout API v72 request cleanup

V72 deprecates unused parameters and removes parameters that were already
deprecated. Check the v71-to-v72 API diff and regenerate schema-derived
clients before carrying old request fields into the upgrade.

The default Pix session validity is 24 hours rather than one hour. If an
integration depends on the former expiry window, set or enforce its intended
timeout explicitly.

### Removed and corrected Web features

From v6.30.0, UPI Collect is no longer supported. The default UPI flow is QR
code on desktop and Intent on mobile.

From v6.26.0, OpenInvoice components used by Oney, Riverty, and RatePay no
longer have the deprecated `gender` field.

From v6.26.0, use `showOtherInsteadOfNumber` for PayByBankUS. The misspelled
`showOtherInsteafOfNumber` property was corrected.

### Sessions integration constraints

Do not rely on component-level installment configuration in a sessions
integration: the backend ignores it. From v6.41.0, those installments are not
displayed and the SDK emits a console warning.

From v6.35.0, `sdkData` changes increase the payload passed to `onSubmit`.
Allow for that increase when copying, validating, logging, or imposing size
limits on the payload.

### Google Pay configuration hazards

An unrecognized Google Pay environment string falls back to `PRODUCTION`, not
`TEST`, from v6.32.0. Validate the environment value explicitly to avoid
unintentionally initializing production.

From v6.10.0, Google Pay throws an error if the merchant ID is missing. Supply
the merchant ID explicitly.

### Card callback and Secured Fields boundaries

In v6.24.0, `onAdditionalDetails` does not fire when defined only on the Card
component. Define it at Checkout level or update to v6.25.1, which fixes the
regression.

Secured Fields changes cross several boundaries:

- v6.8.0 bundles Secured Fields 5.5.0 with `rem` font-size support.
- v6.11.0 stops using `/binLookup` `panLength` as the card-number input's
  `maxlength`.
- v6.23.0 moves to Secured Fields 6.0.0, bumps the JWE version, drops the ACH
  bundle, and disallows the `compat` version on Live.

## Frequently used capabilities

### Sessions and mounted checkout UI

From v6.36.0, Giving works in `/sessions` flows. When `/payments` requires
Giving, the SDK automatically mounts and handles a Donation component.

From v6.32.0, card components with split funding sources work in sessions
integrations.

From v6.31.0, Drop-in and Components accept amount updates without
reinitialization, preserving the mounted checkout UI across amount changes.

### Component display and filtering

From v6.43.0, Select options may contain `tags`, rendered as colored labels in
the open list and collapsed button. `secondaryText` appears below the option
name only in the open list.

From v6.14.0, Drop-in accepts `filterStoredPaymentMethods` to choose which
saved payment methods are displayed.

From v6.40.0, Affirm accepts `allowedCountries` with supported codes `CA`,
`US`, and `GB`:

```js
{ allowedCountries: ["CA", "US", "GB"] }
```

### Errors, translations, and schemes

From v6.39.0, errors outside Secured Fields also include a translated error
message.

From v6.34.0, English translations are bundled as fallback. Translations are
requested from the CDN only when the selected locale is supported.

From v6.38.0, Secured Fields recognizes `ionic://` domains for Ionic
applications that use that URL scheme.

### Cards and authentication

From v6.42.0, the 3DS2 iframe has the attributes required to allow WebAuthn
and Secure Payment Confirmation challenges in compatible browsers.

From v6.41.0, `onBinLookup` callback values include `healthcare`.

From v6.31.0, card payments support Japanese bonus installments.

From v6.21.0, the SDK does not preselect a brand for dual-branded cards
outside Europe, preserving low-cost-routing choice.

### Wallet configuration

Apple Pay supports third-party browsers from v6.10.0,
`shippingContactEditingMode` from v6.13.0, iframe merchant-validation
`domainName` from v6.23.0, and coupon codes from v6.33.0.

From v6.32.0, Google Pay accepts `allowedIssuerCountryCodes` and
`blockedIssuerCountryCodes` for issuer-country filtering.

From v6.34.1, UPI Autopay mandates require `endsAt`; TypeScript integrations
must not treat it as optional.

## API precedence and returned state

For Drop-in or Components using Advanced flow, `/payments` uses values from
`sdkData` when the same SDK-related information is supplied elsewhere. For
example, `sdkData.checkoutAttemptId` wins over another supplied
`checkoutAttemptId`.

Responses for partial payments that undergo 3D Secure 2 include order data,
so the integration can continue with the returned order state.

## Additional payment-method details

Use the topic references for the complete component guidance, including
Canadian EFT PAD, bank-transfer country variants, Riverty redirects, ACH
fields, Econtext voucher references, Brazilian meal-voucher restrictions,
and TypeScript callback and payment-data changes.
