# Payments, Discounts, and Delivery

## Customer payment-method creation

`customerPaymentMethodRemoteCreditCardCreate` is hidden in `2025-01`, requires
`stripePaymentMethodId`, and was scheduled for removal after January 2026. Use
`customerPaymentMethodRemoteCreate`. Invalid customer IDs produce a user error.

## Vaulting verification and 3DS

Vaulting payment extensions must use `VerificationSessionRedirect` for a required 3DS
challenge and pass `authentication` when later resolving or rejecting it.
`REQUIRED_3DS_CHALLENGE` is deprecated.

`verificationSessionResolve` accepts `paymentDetails.card`. Revocations can report
`PAYMENT_METHOD_VERIFICATION_FAILED` or
`THREE_D_SECURE_FLOW_IN_VERIFICATION_NOT_IMPLEMENTED`.

## Delivery promises

`deliveryPromiseSettings`, `deliveryPromiseParticipantsUpdate`, and
`delivery_promise_settings/update` provide the read, write, and webhook contract for
delivery-promise configuration.

## Discount purchase types

App-discount inputs and objects distinguish one-time and subscription applicability
and support `recurringCycleLimit`. Setting both purchase modes to false is invalid.

App-discount inputs default `appliesOnSubscription` to `true`. Multiple product
discounts can apply to one cart line, and discounts can target specific markets.

## Gift cards

The GraphQL Admin API supports gift cards in local currencies, resolves
`GiftCardCashOutTransaction` through `GiftCardTransaction`, and exposes
`GiftCard.lineItem`.

## Market-driven shipping and delivery profiles

Market-driven shipping and its Admin API are in feature preview. Merchant-owned
delivery-profile APIs are deprecated for that model. App-owned delivery profiles can
cover all shippable items.

## Carrier-service profile behavior

New carrier services are no longer added automatically to the default shipping
profile.

## Shipping-label purchase

Shipping labels can be purchased through the GraphQL Admin API.

## Mixed shipping and pickup

A feature preview allows shipping and pickup within the same order.

## Removed payment and price-list members

`ShopifyPaymentsBankAccount.accountNumber` and `routingNumber` were removed.

`PriceListUserErrorCode` no longer contains:

- `CONTEXT_RULE_COUNTRIES_LIMIT`
- `CONTEXT_RULE_COUNTRY_TAKEN`
- `CONTEXT_RULE_LIMIT_REACHED`
- `CONTEXT_RULE_MARKET_NOT_FOUND`
- `CONTEXT_RULE_MARKET_TAKEN`
- `COUNTRY_CURRENCY_MISMATCH`
- `CURRENCY_COUNTRY_MISMATCH`
- `MARKET_CURRENCY_MISMATCH`
