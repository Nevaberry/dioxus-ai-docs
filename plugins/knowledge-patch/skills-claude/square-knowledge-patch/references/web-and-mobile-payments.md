# Web and mobile payments

## Consolidated card tokenization

In Beta, `Card.tokenize()` supports a consolidated flow for payment processing,
buyer verification, and storing, charging, or both charging and storing a card
on file.

## ACH configuration and results

`ach()` no longer requires `redirectURI`, and `transactionId` is optional.

`AchChargeTokenOptions.total` is deprecated in favor of separate `amount` and
`currency` arguments. The tokenization result exposes `intent` to identify the
authorization flow that ran.

## ACH missing-name errors

The ACH missing-name condition now emits `InvalidOptionError` instead of
`PlaidMissingNameError`. Catch `InvalidOptionError`; the old error type remains
for backward compatibility but is no longer emitted.

## Token and method types

Token status values now return strings instead of the former enumeration.
`PaymentRequestEvent` and `MethodType` are string-union types rather than
enumerations.

## Secure contexts

As of October 1, 2025, every Web Payments SDK integration must run in a secure
HTTPS context. Insecure HTTP contexts are no longer supported.

## Apple Pay and Google Pay in Japan

In-App Payments SDK and Web Payments SDK support Apple Pay and Google Pay for
Japanese sellers. Both wallets are available in every region where Square
operates.

## Apple Pay billing contacts

Apple Pay tokenization results can include `email` and `phone` in
`TokenResult.TokenDetails.BillingContact`.

## Afterpay checkout widget

`AfterpayCheckoutWidgetOptions` adds:

- `border` to show a border.
- `heading` to show an instructional heading.
- `theme` to select the widget's appearance.
