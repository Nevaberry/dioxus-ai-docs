# Payments, Transactions, and Payouts

## Payment and payout details

PayPal payment attempts expose the payer email and billing-agreement reference.
Transaction payments expose a Paddle payment-method ID and cardholder name.

Payout totals include the exchange rate, Paddle fee rate, and fees retained on
chargebacks or refunds.

## Payout reconciliation

Payout reconciliation reports connect payouts to transaction-linked sales,
tax, fee, and FX movements. Reports can be filtered by payout period and
movement category.

## Transaction payment lifecycle

Transactions have a `paid` status and emit `transaction.paid` before completed
processing. `transaction.completed` contains the fields needed for
provisioning.

This separates successful payment from completion of Paddle's post-payment
processing.

## Post-purchase documents

Completed transactions can have customer or business names, address details,
and tax identifiers revised for generated PDFs. Refunds or credits
automatically produce credit notes.

## Sandbox behavior

Sandbox emails come from `@paddle.com`. Messages to unregistered domains are
forwarded to the account email. Sandbox refunds are approved automatically
every ten minutes.
