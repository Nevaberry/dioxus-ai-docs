# Payments, Transactions, and Discounts

## Legacy invoicing and Stripe plugins are removed

Since 3.21.0, the invoicing plugin and deprecated
`mirumee.payments.stripe` plugin are gone. Custom deployments must use an
invoice app and migrate Stripe references to `saleor.payments.stripe`.

## Transaction metadata updates merge maps

Since 3.21.0, `transactionUpdate` merges supplied `metadata` and
`privateMetadata` into the existing maps instead of replacing them.

## Gift-card inputs accept metadata

Since 3.21.0, `GiftCardCreate` and `GiftCardUpdate` can write metadata and
private metadata through their input types.

## Discounts expose line-level and replacement totals

Since 3.21.0, `OrderLine.discounts` returns `OrderLineDiscount` entries and
`OrderDiscount.total` replaces deprecated `OrderDiscount.amount`.
`draftOrderInput.discount` is deprecated. `useLegacyLineVoucherPropagation`
lets specific voucher types retain the old line-propagation behavior.

## Transaction webhook amounts have a fallback contract

Since 3.21.0, `TransactionAction.amount` is non-null in refund, charge, and
cancelation request subscription payloads, and cancelation requests carry a
decimal amount instead of null. Apps may omit `amount` from responses to
`TRANSACTION_CHARGE_REQUESTED`, `TRANSACTION_REFUND_REQUESTED`,
`TRANSACTION_CANCELATION_REQUESTED`, `TRANSACTION_INITIALIZE_SESSION`, and
`TRANSACTION_PROCESS_SESSION`; Saleor then uses the payload's `action.amount`.

## Transactions expose structured payment-method details

Since 3.22.0, payment apps can supply `PaymentMethodDetails` through
transaction mutations or webhooks. The object can include card brand, first
and last four digits, expiration, or a non-card method name. Transactions
created before 3.22 are not backfilled, and apps must explicitly support the
fields. Integrations that stored these values in `TransactionItem` metadata
should migrate to the structured object.

## Money exposes exact fractional representation

Since 3.22.0, `Money.fractionalAmount` and `Money.fractionDigits` let payment
integrations use an integer amount plus currency precision instead of relying
on floating-point operations.

## Refund reasons can be required and centrally configured

Since 3.22.0, a Model Type and its Models can define allowed refund reasons and
require staff to choose one while issuing a refund. A custom refund message
remains available alongside the configured reason.

## Zero-total orders do not create manual charge artifacts

Since 3.22.0, manually charging a zero-total order creates neither a
`Transaction` nor a legacy `Payment`, and emits no
`OrderEvents.ORDER_MARKED_AS_PAID` event. When a webhook response creates a
transaction event for a zero-gross checkout, Saleor also skips
`WebhookEventAsyncType.CHECKOUT_FULLY_PAID` processing because the checkout is
already considered fully paid.

## Legacy payments cannot be mixed with transactions

Since 3.22.0, creating a legacy `Payment` for a checkout that already has a
`Transaction` is rejected. Do not combine the old and new payment APIs on one
checkout.

## Transactions support gift cards and richer queries

Since 3.23.0, gift cards can be used as a payment method through the
Transaction API. `transactions` can sort by `CREATED_AT` or `MODIFIED_AT` and
filter by transaction creation or modification ranges, or by event type and
creation time.

## Legacy payment gateways and fields are removed

Since 3.23.0, the Adyen and NP Atobarai gateway plugins are removed in favor of
their apps. The Adyen-specific `Payment.partial` field is gone.

## More legacy payment gateway plugins are removed

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

The built-in Authorize.Net, Razorpay, Braintree, Dummy, and Dummy Credit Card
plugins (`mirumee.payments.authorize_net`, `.razorpay`, `.braintree`, `.dummy`,
and `.dummy_credit_card`) are removed. Deployments still using them must
migrate before upgrading.

## Gift-card and voucher exports and webhooks are removed

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

`exportGiftCards` and `exportVoucherCodes` and their input/output types are
removed. Callers must fetch `giftCards` or `voucher` data and format it
themselves. Completion webhook and subscription types for those exports are
also removed. Migration deletes existing subscriptions to those events,
leaving a webhook with no other events inactive.
