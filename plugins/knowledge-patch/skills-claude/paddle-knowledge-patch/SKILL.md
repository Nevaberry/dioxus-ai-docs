---
name: paddle-knowledge-patch
description: Paddle
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Paddle Knowledge Patch

Use this skill when implementing or reviewing Paddle Billing integrations that
touch API versioning, authentication, subscriptions, checkout, pricing, tax,
transactions, reporting, payouts, webhooks, or migration from Paddle Classic.

## Reference index

| Reference | Topics |
| --- | --- |
| [API and security](references/api-and-security.md) | API defaults and per-request pinning, OAuth apps, hosted MCP authentication, API keys, client-side tokens, pagination totals |
| [Subscriptions and portal](references/subscriptions-and-portal.md) | History, trials, scheduled changes, retries, resumption, proration, consent, portal sessions, recurring non-catalog items |
| [Checkout and storefront](references/checkout-and-storefront.md) | Express and recovery flows, domains, Paddle UI, iOS purchase flows, regional methods, localization, Paddle.js updates and previews |
| [Catalog, transactions, and tax](references/catalog-transactions-and-tax.md) | Transaction discounts, discount groups, tax-aware adjustments, non-catalog transactions, payment lifecycle, post-purchase documents |
| [Reporting, payments, and payouts](references/reporting-payments-and-payouts.md) | Reports, account metrics, payment details, payout details, reconciliation, operational limits |
| [Webhooks and operations](references/webhooks-and-operations.md) | Destination versions, simulation, replay, retention, sandbox behavior, Paddle Classic migration |

## Highest-impact compatibility rules

### Pin API behavior deliberately

Paddle increments its sequential API version only for breaking changes. The
current version is `1`; older versions are neither automatically upgraded nor
currently deprecated. New accounts default to the latest version, and a
request without an explicit version uses its account default.

`Paddle-Version` overrides the account default for one request. It can select a
later version for testing before the account default changes, but cannot select
a version earlier than that default.

```sh
curl https://api.paddle.com/event-types \
  -H "Authorization: Bearer $PADDLE_API_KEY" \
  -H "Paddle-Version: 1"
```

Webhook notification destinations are different: select an API version when
creating each destination because they do not use the account default.

### Do not treat estimated list totals as exact

For large datasets, the estimated total in a paginated list response is capped.
Do not interpret that estimate as the complete result count.

### Provision on transaction completion

Transactions now have a `paid` status. Paddle emits `transaction.paid` after
successful payment but before its post-payment processing completes.
`transaction.completed` contains the fields needed for provisioning.

### Account for negative proration values

Proration is represented on a transaction rather than as separate adjustments.
Transaction quantities, amounts, and totals may therefore be negative.

A subscription permits at most 20 chargeable updates per hour and 100 per day.
Pausing a subscription cancels past-due renewal transactions so they are not
collected when the subscription resumes.

### Respect event and notification retention

Notifications may be replayed, but events and notifications older than 90 days
are unavailable through the API.

## Authentication quick reference

### Server-side and app access

Apps may connect through OAuth instead of API keys, and merchants can manage
connected third-party apps in the dashboard. The hosted Paddle MCP server uses
browser-based OAuth for live accounts, requires an API key for sandbox, and
exposes the API through three tools in its remote codemode interface.

Enhanced API keys have a standardized format and support permissions, expiry
dates, and usage tracking. Paddle may detect exposed keys in public GitHub
repositories and alert or disable them. An AWS Secrets Manager integration can
rotate keys on a schedule without downtime.

### Browser access

Paddle.js authenticates with client-side tokens instead of seller IDs. Paddle
Retain can use the same token instead of a separate Retain API key. Client-side
tokens can be created and managed through API operations, with corresponding
webhooks.

## Subscription quick reference

### Lifecycle and retries

The subscription history API records changes chronologically across a
subscription's lifetime, including when each change occurred, why it occurred,
and who made it.

Subscriptions with a scheduled pause or cancellation may still be updated.
Resuming a paused subscription may start a new billing period or continue the
existing one. Failed automatically collected subscription payments are retried
even when Paddle Retain is not enabled.

### Trials and consent

Paid trials can charge a reduced trial-period amount while retaining trial and
recurring amounts on the same price. Cardless trials let customers begin
without a payment method.

Subscription checkout requires explicit consent before saving a payment
method. California customers see confirmation for later recurring charges.
South Korean subscriptions expose renewal-consent state through
`consent_requirements` in API and webhook data.

### Portal and cancellation

Customer portal sessions produce authenticated links that automatically log a
customer in. Legacy subscription management-link responses now return customer
portal links. Cancellation Flows can run within the portal as the subscription
offboarding experience.

## Checkout quick reference

### Checkout modes

Express checkout prioritizes Apple Pay on mobile and Google Pay on Android and
Chrome. Early-access post-purchase upsell checkout supports reduced-friction
one-click purchases. Automated abandoned-checkout emails may include an
optional recovery discount.

Hosted checkout can use branded custom subdomains as an early-access feature.
Four API operations list and inspect approved checkout domains and trigger
Apple Pay verification.

### Open-checkout updates and errors

Paddle.js can update items, discounts, customer information, and custom data on
an open checkout. Checkout events distinguish invalid or missing input from
payment errors such as no valid payment method, allowing separate frontend
fallback handling.

### Previews and method selection

Price previews return localized, formatted prices with tax and discount
calculations. Paddle.js can preview complete transaction totals without a
server call. Preview responses can report valid payment methods, and checkout
can be restricted to a selected set.

## Pricing, tax, and catalog quick reference

A transaction may receive a one-off discount object without a catalog discount.
Discount groups organize catalog discounts and can be fetched, renamed, or
archived through the API. Discount codes are case-insensitive.

For partial refunds, setting `tax_mode` allows tax-exclusive amounts so Paddle
can calculate tax. Adjustment webhooks include `tax_rates_used`, grouping
subtotal, tax, and total by rate. Transaction totals expose tax charged after
credits.

Transactions and one-time subscription charges may use inline product or price
attributes without catalog entries. Recurring non-catalog items may be added
when updating a subscription. Subscription items preserve complete price and
product snapshots from when each item was added.

## Reporting and operational quick reference

Paddle offers subscriptions, checkouts, balance, catalog, and transaction or
adjustment line-item reports, along with seven API operations for account
time-series metrics. Reports can be created and downloaded through the API, and
webhooks are available for report workflows.

Payout reconciliation reports connect payouts to transaction-linked sales,
tax, fee, and foreign-exchange movements. They can be filtered by payout period
and movement category. Report creation is limited to 100 per day; price and
transaction preview operations allow 1,000 requests per minute per IP address.

## Applying the patch

1. Identify the integration surface involved.
2. Open every indexed reference that matches that surface.
3. Apply the specific compatibility rules and limits from those references.
4. Preserve distinctions between live and sandbox, account and destination
   defaults, payment and completion, recurring and one-time behavior, and
   stable and early-access features.
