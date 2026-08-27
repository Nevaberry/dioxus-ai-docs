# Customers, Billing, and Self-Service

## External customer IDs

Customers have an `external_id` with dedicated get, update, and delete
operations. Customer list queries can filter by external ID.

A checkout's `external_customer_id` is copied to the customer created after
payment.

## Customer State

Customer State returns active subscriptions and granted benefits in one API
call or webhook. It correctly represents trialing subscriptions.

## Credit balances

Customer credit balances can be managed through the API and are automatically
applied to invoices. Refunding an order restores any applied credit.

## Invoice numbering

New invoice numbering defaults to a separate sequence per customer starting at
1. Organization-wide sequencing remains available in settings.

## Portal email changes and data export

Customers can change their portal email after verifying the replacement.

Customers can download a JSON export of personal data, subscriptions, orders,
and benefit grants.

## Email-domain validation

Email domains are DNS-validated during checkout and during customer or user
creation.

## Customer email controls

Organizations can disable automatic customer emails.

They can independently toggle:

- Renewal reminders sent seven days before yearly-or-longer cycles.
- Trial-conversion reminders sent three days ahead, or one day ahead for very
  short trials.
