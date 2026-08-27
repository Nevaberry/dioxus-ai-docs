# Payments, Discounts, and Subscriptions

## Customer payment-method creation migration

`customerPaymentMethodRemoteCreditCardCreate` is hidden in `2025-01`, requires
`stripePaymentMethodId`, and was scheduled for removal after January 2026.
Use `customerPaymentMethodRemoteCreate`. Invalid customer IDs produce a user
error.

## Delivery promises and discount purchase types

`deliveryPromiseSettings`, `deliveryPromiseParticipantsUpdate`, and
`delivery_promise_settings/update` provide the read, write, and webhook
contract for delivery-promise configuration.

App-discount inputs and objects distinguish one-time and subscription
applicability and support `recurringCycleLimit`. Setting both purchase modes
to false is invalid.

## Subscription relationships

Customer API `Order.subscriptionContracts` exposes contracts associated with
an order. `SubscriptionLine.concatenatedOriginContract` identifies the source
contract when a line was formed by concatenation. Pickup subscription methods
expose `pickupAddress`.

## Vaulting verification and 3DS

Vaulting payment extensions must use `VerificationSessionRedirect` for a
required 3DS challenge and pass `authentication` when later resolving or
rejecting it. `REQUIRED_3DS_CHALLENGE` is deprecated.

`verificationSessionResolve` accepts `paymentDetails.card`. Revocations can
report `PAYMENT_METHOD_VERIFICATION_FAILED` or
`THREE_D_SECURE_FLOW_IN_VERIFICATION_NOT_IMPLEMENTED`.

## Subscription calculation and actors

`SubscriptionContractCalculation` is available in early access.
Subscription-contract and billing-attempt mutations expose an `actor` field.

## App-discount execution semantics

App-discount inputs now default `appliesOnSubscription` to `true`. Multiple
product discounts can apply to one cart line. Discounts can target specific
markets.

## Gift-card API additions

The GraphQL Admin API supports gift cards in local currencies, resolves
`GiftCardCashOutTransaction` through `GiftCardTransaction`, and exposes
`GiftCard.lineItem`.

## Financial and customer-tax behavior

Customer tax settings are available in the Admin API.
`LineItem.priceAfterAllDiscountsBeforeTaxesSet` exposes a post-discount,
pre-tax amount.

The `totalUnsettledSet` calculation for pending captures has changed. POS 11.5
custom-line-item discount rounding has also changed. Dependent calculations
need retesting.
