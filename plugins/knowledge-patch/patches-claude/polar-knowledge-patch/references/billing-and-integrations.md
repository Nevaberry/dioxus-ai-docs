# Billing and integrations

## Metrics API

Select requested values with the `metrics` query parameter. The deprecated
`focus_metrics` parameter has been removed.

Metrics calculations exclude pending and unpaid orders. They include only paid
and refunded orders.

## Customer credit balances

Manage customer credit balances through the API. Credit is automatically
applied to invoices. Refunding an order restores the credit that was applied.

## Invoice numbering

New invoice numbering defaults to a separate sequence for each customer,
starting at 1. Organization-wide sequencing remains available in settings.

## OAuth2 authorization

When an OAuth2 authorization request omits scope, it receives the client's
configured default scope.

Trusted first-party clients save grants without displaying an authorization
prompt.

## Organization SSO

Scale organizations can configure and enforce OpenID Connect SSO. Anyone
authenticated by the configured provider becomes an organization member
without an invitation.

## Customer self-service

A customer can change the email address in the portal after verifying the
replacement address.

Customers can download a JSON export containing personal data, subscriptions,
orders, and benefit grants.

## Email validation and controls

Email domains are validated through DNS during checkout and during customer or
user creation.

An organization can disable automatic customer emails. It can independently
toggle these reminders:

- renewal reminders sent seven days before yearly or longer billing cycles;
  and
- trial-conversion reminders sent three days before conversion, or one day
  before conversion for very short trials.

## Ready-made integrations

Polar provides a TypeScript Better Auth billing plugin.

The Zapier integration currently provides webhook-backed event triggers. It
does not provide actions that change Polar resources.
