# Payments and refunds

## Refund and invoice mutation contracts (3.21.0)

`OrderGrantRefundCreateInput.transactionId` is required. `invoiceRequest` no
longer errors when an app subscribed to `INVOICE_REQUESTED` is installed
without the removed invoice plugin.

## Transaction webhook amount fallback (3.21.0)

`TransactionAction.amount` is non-null in refund, charge, and cancelation
request subscription payloads. Cancelation requests carry a decimal amount
rather than `null`.

Apps may omit `amount` from responses to `TRANSACTION_CHARGE_REQUESTED`,
`TRANSACTION_REFUND_REQUESTED`, `TRANSACTION_CANCELATION_REQUESTED`,
`TRANSACTION_INITIALIZE_SESSION`, and `TRANSACTION_PROCESS_SESSION`; Saleor
then uses the payload's `action.amount`.

## Structured payment-method details (3.22.0)

Payment apps can provide `PaymentMethodDetails` through transaction mutations
or webhooks. It can contain card brand, first and last four digits, expiration,
or a non-card method name. Transactions created before 3.22 are not
backfilled, and apps must explicitly support the fields. Integrations that
stored these values in `TransactionItem` metadata should migrate to the
structured object.

## Exact fractional money representation (3.22.0)

`Money.fractionalAmount` and `Money.fractionDigits` let payment integrations
use an integer amount plus currency precision instead of relying on
floating-point operations.

## Refund reason configuration (3.22.0)

A Model Type and its Models can define allowed refund reasons and require
staff to select one when issuing a refund. A custom refund message remains
available alongside the configured reason.

## Zero-total order charging (3.22.0)

Manually charging a zero-total order creates neither a `Transaction` nor a
legacy `Payment`, and emits no `OrderEvents.ORDER_MARKED_AS_PAID` event. When a
webhook response creates a transaction event for a zero-gross checkout,
Saleor skips `WebhookEventAsyncType.CHECKOUT_FULLY_PAID` processing because
the checkout is already considered fully paid.

## Legacy payments and Transactions (3.22.0)

Creating a legacy `Payment` for a checkout that already has a `Transaction`
is rejected. Do not combine the old and new payment APIs on one checkout.

## Gift cards and transaction queries (3.23.0)

Gift cards can be used as a payment method through the Transaction API.
`transactions` can sort by `CREATED_AT` or `MODIFIED_AT` and filter by
transaction creation or modification ranges, or by event type and creation
time.
