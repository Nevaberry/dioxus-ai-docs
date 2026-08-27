# Checkout API v72

Source batch: `checkout-api-v72`.

## Stricter request-field validation

Checkout API v72 rejects values that do not meet new validation requirements
in requests such as `/payments` and `/sessions`. Audit these fields before
upgrading:

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

## Cardholder names reject card numbers

For card payments, a card number sent in `holderName` is rejected with
**Invalid card holder name**. This catches integrations that map PAN input
into a cardholder-name parameter.

## `sdkData` precedence in Advanced flow

For Drop-in or Components using Advanced flow, `/payments` uses values from
`sdkData` when the same SDK-related information is supplied elsewhere. For
example, `sdkData.checkoutAttemptId` wins over another supplied
`checkoutAttemptId`.

## Pix session validity

The default Pix session validity is 24 hours in v72, increased from one hour.
Integrations that depend on the former expiry window must set or enforce their
intended timeout explicitly.

## Parameter deprecations and removals

V72 deprecates unused parameters and removes parameters that were already
deprecated. Check the v71-to-v72 API diff and regenerate schema-derived
clients before carrying old request fields into the upgrade.

## Validation and rate-limit status codes

Some validation and rate-limit failures now return HTTP `422` or `429`
instead of `500`. Error handling and retry logic must recognize them as
validation and throttling responses rather than server failures.

## Sessions redirect result parameter

In Drop-in `/sessions` flows, the redirect back no longer supplies the
erroneous `payload` parameter in place of `redirectResult`. Use
`redirectResult`, which is required to complete the payment.

## Required line-item tax fields

In `/payments` `lineItems`, omitting `taxAmount` and `amountExcludingTax` now
produces an error. V72 no longer creates an incorrect `amountExludingTax`
value equal to `amountIncludingTax`.

## Order data for 3DS2 partial payments

API responses for partial payments that undergo 3D Secure 2 now include the
order data, allowing the integration to continue with the returned order
state.
