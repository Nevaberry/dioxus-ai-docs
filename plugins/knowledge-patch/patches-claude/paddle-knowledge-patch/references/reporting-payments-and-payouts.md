# Reporting, Payments, and Payouts

## Reports and account metrics

Paddle provides these report categories:

- subscriptions;
- checkouts;
- balance;
- catalog;
- transaction and adjustment line items.

Seven API operations provide account time-series metrics.

Reports can be created and downloaded through the API. Webhooks are available
for report workflows.

## Payment details

PayPal payment attempts expose the payer email and billing-agreement reference.

Transaction payments expose a Paddle payment-method ID and the cardholder name.

## Payout details

Payout totals include:

- exchange rate;
- Paddle fee rate;
- fees retained on chargebacks or refunds.

## Payout reconciliation

Payout reconciliation reports connect payouts to transaction-linked:

- sales movements;
- tax movements;
- fee movements;
- foreign-exchange movements.

The reports can be filtered by payout period and movement category.

## Operational limits

Report creation is limited to 100 reports per day.

Price and transaction preview operations allow 1,000 requests per minute per
IP address.
