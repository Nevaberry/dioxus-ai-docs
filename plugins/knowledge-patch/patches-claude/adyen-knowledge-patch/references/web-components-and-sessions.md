# Web Components and Sessions

Source batches: `adyen-web-releases-current`,
`adyen-web-releases-history`.

## Select option rendering

From v6.43.0, Select options can carry `tags`. They render as colored labels
in both the open list and collapsed button. `secondaryText` appears below an
option name in the open list and is omitted from the collapsed button.

## Installment configuration with sessions

Component-level installment configuration is not supported in a sessions
integration because the backend ignores it. From v6.41.0, such installments
are not displayed and a console warning is emitted.

## Affirm country restrictions

From v6.40.0, Affirm components accept `allowedCountries`. The supported
country codes are `CA`, `US`, and `GB`.

```js
{ allowedCountries: ["CA", "US", "GB"] }
```

## Localized non-Secured Fields errors

From v6.39.0, error objects for errors outside Secured Fields also include a
translated error message, enabling consistent localized error handling.

## Giving in sessions flows

From v6.36.0, Giving is supported in `/sessions` flows. When the `/payments`
response requires Giving, the SDK automatically mounts and handles a Donation
component.

## Larger `onSubmit` payloads

From v6.35.0, changes to `sdkData` increase the size of the payload passed to
`onSubmit`. Integrations that copy, validate, log, or impose size limits on
that payload must allow for the increase.

## Translation fallback

From v6.34.0, English translations are bundled as the fallback. Translations
are requested from the CDN only when the selected locale is supported.

## Amount updates

From v6.31.0, Drop-in and Components can receive amount updates without being
reinitialized, preserving the mounted checkout UI across amount changes.

## Canadian EFT PAD

From v6.17.0, Web integrations can use the `PreAuthorizedDebitCanada`
component for EFT PAD.

## Bank-transfer country variants

From v6.18.0, supported variants include `bankTransfer_BE`,
`bankTransfer_NL`, `bankTransfer_PL`, `bankTransfer_FR`, `bankTransfer_CH`,
`bankTransfer_IE`, `bankTransfer_GB`, and `bankTransfer_DE`.

## Stored-payment filtering

From v6.14.0, Drop-in accepts a `filterStoredPaymentMethods` callback for
choosing which saved payment methods to display.

## Riverty redirects

From v6.14.0, Riverty is implemented as a Redirect component.

## OpenInvoice field removal

From v6.26.0, the deprecated `gender` field is removed from OpenInvoice
components used by Oney, Riverty, and RatePay.

## PayByBankUS property correction

From v6.26.0, use `showOtherInsteadOfNumber`. The misspelled
`showOtherInsteafOfNumber` property name was corrected.

## Econtext voucher references

From v6.29.0, Econtext voucher results can include `alternativeReference`.

## Brazilian meal-voucher restrictions

From v6.29.0, Brazilian meal vouchers no longer offer installments or Click
to Pay.
