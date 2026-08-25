# Subscriptions and Portal

## Subscription history

The subscription history API provides a chronological record of changes over a
subscription's lifetime. Each recorded change includes:

- when it occurred;
- why it occurred;
- who made it.

## Paid and cardless trials

Paid trials can charge a reduced amount for the trial period while keeping both
the trial amount and recurring amount on the same price.

Cardless trials allow a customer to start without supplying a payment method.

## Scheduled changes, retries, and resumption

A subscription with a scheduled pause or cancellation can still be updated.

When a paused subscription resumes, it can either start a new billing period or
continue the existing one.

Failed automatically collected subscription payments are retried even if
Paddle Retain is not enabled.

## Chargeable updates and proration

A subscription allows no more than 20 chargeable updates per hour and 100 per
day.

Proration appears on a transaction rather than in separate adjustments.
Transaction quantities, amounts, and totals may consequently be negative.

Pausing a subscription cancels past-due renewal transactions. Those
transactions are not collected when the subscription resumes.

## Subscription checkout consent

Subscription checkout requires explicit consent before saving a payment
method.

California customers see a confirmation for subsequent recurring charges.

For South Korean subscriptions, API and webhook data expose renewal consent
state through `consent_requirements`.

## Customer portal sessions and cancellation

Customer portal sessions generate authenticated links that automatically log a
customer in.

Legacy subscription management-link responses now return customer portal
links. Cancellation Flows can run inside the portal as the subscription
offboarding experience.

## Recurring non-catalog items and snapshots

Recurring non-catalog items can be added when updating a subscription.

Subscription items contain complete price and product snapshots from the time
each item was added.

For non-catalog transactions and one-time subscription charges, see
[Catalog, transactions, and tax](catalog-transactions-and-tax.md#non-catalog-transactions-and-charges).
