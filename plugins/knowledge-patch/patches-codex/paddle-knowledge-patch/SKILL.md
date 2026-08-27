---
name: paddle-knowledge-patch
description: Paddle
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Paddle Knowledge Patch

## Use this patch

Load this skill before changing a Paddle integration that depends on API
version selection, subscriptions, checkout, pricing, tax, transactions,
payouts, webhooks, reporting, Paddle.js, authentication, or migration.

Use the quick reference for high-impact compatibility points, then open the
topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [API versions, security, and integrations](references/api-versions-security-and-integrations.md) | Account and request versions, notification destinations, OAuth, remote MCP authentication, API keys, Paddle UI, iOS purchase flows, Paddle Classic migration |
| [Subscriptions and checkout](references/subscriptions-and-checkout.md) | History, trials, scheduled changes, retries, resumption, proration, consent, portal sessions, express checkout, upsells, recovery, checkout domains |
| [Pricing, tax, and catalog](references/pricing-tax-and-catalog.md) | Regional payment methods, currencies, locales, automatic localization, discounts, tax-aware adjustments, non-catalog items, subscription snapshots |
| [Payments, transactions, and payouts](references/payments-transactions-and-payouts.md) | Payment details, payout data and reconciliation, transaction lifecycle, post-purchase documents, sandbox behavior |
| [Webhooks, reporting, and operational limits](references/webhooks-reporting-and-operations.md) | Reports, metrics, capped list totals, report and preview limits, webhook simulation, replay, and retention |
| [Paddle.js and client-side flows](references/paddle-js-and-client-side-flows.md) | Open-checkout updates, error handling, client-side tokens, previews, and payment-method control |

## Quick reference

### Select API versions explicitly when needed

Paddle increments its sequential API version only for breaking changes. The
current version is `1`; older versions are not automatically upgraded and are
not currently deprecated. New accounts default to the latest version, and a
request without an explicit version uses the account default.

`Paddle-Version` overrides the account default. It can select a later version
for testing before the default changes, but cannot select a version earlier
than the default.

```sh
curl https://api.paddle.com/event-types \
  -H "Authorization: Bearer $PADDLE_API_KEY" \
  -H "Paddle-Version: 1"
```

Webhook notification destinations do not use the account default. Choose the
API version when creating each destination.

### Authenticate Paddle.js with client-side tokens

Paddle.js uses client-side tokens instead of seller IDs. Paddle Retain can use
the same token instead of a separate Retain API key. API operations and
corresponding webhooks are available for creating and managing client-side
tokens.

### Provision after transaction completion

A transaction can reach `paid` and emit `transaction.paid` before completed
processing. `transaction.completed` contains the fields needed for
provisioning, separating successful payment from completion of Paddle's
post-payment processing.

### Do not treat a capped estimate as an exact count

For large datasets, the estimated total in paginated list responses is capped
rather than exact. Do not interpret the estimate as the complete result count.

### Account for subscription charge and proration behavior

A subscription permits at most 20 chargeable updates per hour and 100 per day.
Proration appears on a transaction rather than as separate adjustments, so
transaction quantities, amounts, and totals may be negative. Pausing also
cancels past-due renewal transactions so they are not collected on resume.

### Respect event and notification retention

Notifications can be replayed, but events and notifications older than 90 days
are unavailable through the API.

### Distinguish checkout validation from payment errors

Paddle.js checkout events distinguish invalid or missing input from payment
errors such as having no valid payment method. Frontends can therefore handle
these as separate fallback cases.

### Preview localized prices and transaction totals

Price previews return localized, formatted prices with tax and discount
calculations. Paddle.js can preview complete transaction totals without a
server call. Preview responses can report valid payment methods, and checkout
can be restricted to a selected set.

### Update subscriptions around scheduled changes

Subscriptions with a scheduled pause or cancellation can still be updated.
Resuming a paused subscription can start a new billing period or continue the
existing one. Failed automatically collected subscription payments are retried
even when Paddle Retain is not enabled.

### Supply tax-exclusive partial-refund amounts

Setting `tax_mode` for a partial refund lets amounts be supplied tax-exclusive
for Paddle to calculate tax. Adjustment webhooks include `tax_rates_used`, with
subtotal, tax, and total grouped by rate.

### Account for sandbox delivery and refunds

Sandbox emails come from `@paddle.com`, and messages to unregistered domains
are forwarded to the account email. Sandbox refunds are approved automatically
every ten minutes.

## Task routing

### Changing API behavior or credentials

Read [API versions, security, and integrations](references/api-versions-security-and-integrations.md)
for account defaults, per-request selection, destination versions, OAuth, API
keys, Paddle UI, external iOS purchase flows, and Paddle Classic migration.

### Changing subscription or checkout behavior

Read [Subscriptions and checkout](references/subscriptions-and-checkout.md)
for history, trials, scheduled changes, retries, proration, consent, portals,
express checkout, recovery, and checkout domains.

### Changing prices, tax, discounts, or catalog usage

Read [Pricing, tax, and catalog](references/pricing-tax-and-catalog.md) for
regional payment support, currencies and locales, location-based display,
one-off discounts, discount groups, tax-aware adjustments, and inline items.

### Handling payments, transactions, payouts, or documents

Read [Payments, transactions, and payouts](references/payments-transactions-and-payouts.md)
for exposed payment data, payout fields and reconciliation, lifecycle events,
post-purchase PDF revisions, credit notes, and sandbox behavior.

### Building reporting or webhook operations

Read [Webhooks, reporting, and operational limits](references/webhooks-reporting-and-operations.md)
for report and metrics APIs, pagination totals, request limits, simulator
capabilities, replay, and retention.

### Building browser-side checkout flows

Read [Paddle.js and client-side flows](references/paddle-js-and-client-side-flows.md)
for updating open checkouts, interpreting checkout errors, client-side token
management, localized previews, complete transaction previews, and payment
method restrictions.
