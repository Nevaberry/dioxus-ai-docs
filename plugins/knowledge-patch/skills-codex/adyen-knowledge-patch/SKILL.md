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
sessions integrations, or Checkout API v72. Start with the breaking changes and
upgrade hazards below, then open the topic reference that matches the payment
method or integration flow being changed.

## Reference index

| Reference | Topics |
| --- | --- |
| [Web upgrades](references/web-upgrades.md) | Select rendering, localization, callbacks, TypeScript surfaces, Secured Fields, amount updates, stored methods, and regressions |
| [Cards and bank payments](references/cards-and-bank-payments.md) | Card data, installments, UPI, ACH, EFT PAD, bank transfers, OpenInvoice, PayByBankUS, Econtext, and meal vouchers |
| [Wallets and components](references/wallets-and-components.md) | Apple Pay, Google Pay, Affirm, Giving, and Riverty |
| [Sessions and Checkout API v72](references/sessions-and-api-v72.md) | Sessions constraints and support, request validation, precedence, redirects, status codes, Pix, line items, and partial payments |

## Breaking changes and upgrade hazards

### Validate Checkout API v72 requests before upgrading

V72 adds stricter validation to requests including `/payments` and `/sessions`.
Audit the following fields before upgrading:

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

For card payments, v72 also rejects a card number in `holderName` with
**Invalid card holder name**. This exposes integrations that map PAN input to
the cardholder-name parameter.

See [Sessions and Checkout API v72](references/sessions-and-api-v72.md).

### Handle v72 validation and throttling statuses

Some validation and rate-limit failures return HTTP `422` or `429` instead of
`500`. Treat them as validation and throttling responses, rather than server
failures, in error handling and retry logic.

### Supply required v72 line-item tax fields

Omitting `taxAmount` and `amountExcludingTax` from `/payments` `lineItems`
produces an error. V72 no longer creates the incorrect `amountExludingTax`
value equal to `amountIncludingTax`.

### Remove obsolete parameters during the v72 upgrade

V72 deprecates unused parameters and removes parameters that were already
deprecated. Check the v71-to-v72 API diff and regenerate schema-derived clients
before carrying old request fields into the upgrade.

### Use `redirectResult` after a sessions redirect

In Drop-in `/sessions` flows, the redirect back no longer supplies the
erroneous `payload` parameter instead of `redirectResult`. Use the required
`redirectResult` to complete the payment.

### Remove UPI Collect assumptions

From Adyen Web v6.30.0, UPI Collect is unsupported. The default UPI flow is QR
code on desktop and Intent on mobile.

### Remove deprecated OpenInvoice gender input

From v6.26.0, OpenInvoice components for Oney, Riverty, and RatePay no longer
contain the deprecated `gender` field.

### Correct the PayByBankUS option name

From v6.26.0, use `showOtherInsteadOfNumber`. The former
`showOtherInsteafOfNumber` spelling was corrected.

### Work around the v6.24.0 Card callback regression

In v6.24.0, `onAdditionalDetails` does not fire when defined only on the Card
component. Define it at Checkout level or update to v6.25.1, where the
regression is fixed.

### Validate Google Pay environment strings

From v6.32.0, an unrecognized Google Pay environment falls back to
`PRODUCTION`, not `TEST`. Validate the configured value explicitly to avoid
unintentionally initializing the production environment.

### Do not configure component-level installments with sessions

The sessions backend ignores component-level installment configuration. From
v6.41.0, the installments are not displayed and the SDK emits a console
warning.

## High-use Web changes

### Update amounts without remounting checkout

From v6.31.0, Drop-in and Components can receive amount updates without
reinitialization, preserving the mounted checkout UI across amount changes.

### Account for larger `onSubmit` payloads

From v6.35.0, `sdkData` changes increase the payload size passed to `onSubmit`.
Allow for the increase in integrations that copy, validate, log, or impose size
limits on the payload.

### Render richer Select options

From v6.43.0, Select options can include `tags`, rendered as colored labels in
the open list and collapsed button. `secondaryText` appears below the option
name in the open list but is omitted from the collapsed button.

### Use localized errors consistently

From v6.39.0, errors outside Secured Fields also include a translated error
message, enabling consistent localized error handling.

### Use the English translation fallback

From v6.34.0, English translations are bundled as the fallback. The SDK
requests translations from the CDN only when the selected locale is supported.

### Consume healthcare BIN data

From v6.41.0, the value passed to `onBinLookup` includes `healthcare`; card
integrations can consume it directly from the callback result.

## High-use payment-method changes

### Configure Google Pay issuer-country filters

From v6.32.0, Google Pay accepts `allowedIssuerCountryCodes` and
`blockedIssuerCountryCodes` component properties to filter cards by issuer
country.

### Configure Affirm countries

From v6.40.0, Affirm components accept `allowedCountries`. Supported codes are
`CA`, `US`, and `GB`:

```js
{ allowedCountries: ["CA", "US", "GB"] }
```

### Use Apple Pay additions

Apple Pay supports third-party browsers from v6.10.0,
`shippingContactEditingMode` from v6.13.0, `domainName` from v6.23.0, and
coupon codes from v6.33.0. The references preserve the scope of each option.

### Use sessions support where available

From v6.32.0, sessions integrations support card components with split funding
sources. From v6.36.0, `/sessions` flows support Giving; when the `/payments`
response requires Giving, the SDK automatically mounts and handles a Donation
component.

### Respect Advanced-flow `sdkData` precedence

In Drop-in or Components Advanced flow, v72 `/payments` uses values from
`sdkData` when the same SDK-related information appears elsewhere. For example,
`sdkData.checkoutAttemptId` wins over another supplied `checkoutAttemptId`.

## Task routing

### When upgrading Adyen Web

1. Check the breaking changes above against the installed Web version.
2. Open [Web upgrades](references/web-upgrades.md) for shared UI, callback,
   localization, TypeScript, and Secured Fields changes.
3. Open the payment-method reference for method-specific changes.
4. If the integration uses `/sessions`, also check
   [Sessions and Checkout API v72](references/sessions-and-api-v72.md).

### When upgrading to Checkout API v72

1. Audit the request fields listed above.
2. Check removed and deprecated parameters against the v71-to-v72 API diff.
3. Regenerate schema-derived clients.
4. Update status-code, redirect, timeout, and line-item handling using the v72
   reference.
5. Preserve returned order data for 3DS2 partial payments.

### When changing a payment method

- Use [Cards and bank payments](references/cards-and-bank-payments.md) for Card,
  UPI, ACH, EFT PAD, bank transfer, OpenInvoice, PayByBankUS, Econtext, and
  Brazilian meal vouchers.
- Use [Wallets and components](references/wallets-and-components.md) for Apple
  Pay, Google Pay, Affirm, Giving, and Riverty.
- Cross-check [Sessions and Checkout API v72](references/sessions-and-api-v72.md)
  whenever the payment method runs through `/sessions`.
