# Web Payments SDK

## ACH configuration and tokenization results

`ach()` no longer requires `redirectURI`, and `transactionId` is optional.

`AchChargeTokenOptions.total` is deprecated in favor of separate `amount` and
`currency` arguments.

The tokenization result exposes `intent` to identify the authorization flow
that ran.

## Afterpay checkout widget styling

`AfterpayCheckoutWidgetOptions` adds `border`, `heading`, and `theme` controls
for showing a border or instructional heading and selecting the widget's
appearance.

## Wallets for Japanese sellers

Web Payments SDK supports Apple Pay and Google Pay for sellers in Japan. Both
wallets are available in every region where Square operates.

## Secure contexts

As of October 1, 2025, every Web Payments SDK integration must run in a secure
HTTPS context. Insecure HTTP contexts are no longer supported.

## ACH missing-name errors

The ACH missing-name condition emits `InvalidOptionError` instead of
`PlaidMissingNameError`. Catch `InvalidOptionError`; the old error type remains
for backward compatibility but is no longer emitted.

## String-based status and method types

Token status values return strings instead of the former enumeration.
`PaymentRequestEvent` and `MethodType` are string-union types rather than
enumerations.

## Apple Pay billing contact fields

Apple Pay tokenization results can include `email` and `phone` in
`TokenResult.TokenDetails.BillingContact`.
