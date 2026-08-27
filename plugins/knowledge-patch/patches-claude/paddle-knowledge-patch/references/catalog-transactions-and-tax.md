# Catalog, Transactions, and Tax

## Transaction discounts

A transaction can receive a one-off discount object without creating a catalog
discount.

Discount groups organize catalog discounts. They can be fetched, renamed, or
archived through the API.

Discount codes are case-insensitive.

## Tax-aware adjustments

For a partial refund, setting `tax_mode` allows amounts to be supplied
tax-exclusive so Paddle can calculate tax.

Adjustment webhooks include `tax_rates_used`. It groups subtotal, tax, and
total by rate.

Transaction totals expose the tax charged after credits.

## Non-catalog transactions and charges

Transactions and one-time subscription charges can use inline product or price
attributes without catalog entries.

Recurring non-catalog subscription items and stored snapshots are covered in
[Subscriptions and portal](subscriptions-and-portal.md#recurring-non-catalog-items-and-snapshots).

## Transaction payment lifecycle

Transactions have a `paid` status. Paddle emits `transaction.paid` before
completed processing.

`transaction.completed` includes the fields required for provisioning. This
separates successful payment from completion of Paddle's post-payment
processing.

## Post-purchase documents

After a transaction completes, the following details can be revised for its
generated PDFs:

- customer or business names;
- address details;
- tax identifiers.

Refunds and credits automatically produce credit notes.
