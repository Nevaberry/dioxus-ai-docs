# Sessions and Checkout API v72

Use this reference for sessions-specific Web behavior and Checkout API v72
upgrade work. Items come from `adyen-web-releases-current` and
`checkout-api-v72`.

## Sessions-specific Adyen Web behavior

### Component-level installments (since Web v6.41.0)

Component-level installment configuration is not supported by a sessions
integration because the backend ignores it. Such installments are not
displayed, and a console warning is emitted instead.

### Giving (since Web v6.36.0)

Giving is supported in `/sessions` flows. When the `/payments` response
requires Giving, the SDK automatically mounts and handles a Donation component.

### Split-funding-source cards (since Web v6.32.0)

Card components using split funding sources are supported in sessions
integrations.

## Request validation

### Stricter field validation

Checkout API v72 rejects values that do not meet new validation requirements in
requests such as `/payments` and `/sessions`. Audit these fields before
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

### Cardholder names reject card numbers

For card payments, a card number sent in `holderName` is rejected with
**Invalid card holder name**. This catches integrations that map PAN input into
a cardholder-name parameter.

### Missing line-item tax fields

In `/payments` `lineItems`, omitting `taxAmount` and `amountExcludingTax`
produces an error. V72 no longer creates an incorrect `amountExludingTax` value
equal to `amountIncludingTax`.

## Request precedence

### `sdkData` in Advanced flow

For Drop-in or Components using Advanced flow, `/payments` uses values from
`sdkData` when the same SDK-related information is supplied elsewhere. For
example, `sdkData.checkoutAttemptId` wins over another supplied
`checkoutAttemptId`.

## Expiry and redirects

### Pix session validity

The default Pix session validity is 24 hours in v72, increased from one hour.
Integrations that depend on the former expiry window must set or enforce their
intended timeout explicitly.

### Sessions redirect result

In Drop-in `/sessions` flows, the redirect back no longer supplies the
erroneous `payload` parameter in place of `redirectResult`. Use
`redirectResult`, which is required to complete the payment.

## Upgrade cleanup

### Parameter deprecations and removals

V72 deprecates unused parameters and removes parameters that were already
deprecated. Check the v71-to-v72 API diff and regenerate schema-derived clients
before carrying old request fields into the upgrade.

### Validation and rate-limit status codes

Some validation and rate-limit failures now return HTTP `422` or `429` instead
of `500`. Error handling and retry logic must recognize these as validation and
throttling responses rather than server failures.

## Partial payments

### Order data after 3DS2

API responses for partial payments that undergo 3D Secure 2 now include the
order data, allowing the integration to continue with the returned order state.
