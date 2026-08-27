# Billing, Invoicing, and Subscriptions

## Invoice schema and reconciliation

### Pricing, tax, and provenance (`2025-03-31.basil`)

Top-level price fields on Invoice Items and Invoice Line Items are replaced by
the newer price model. Top-level tax properties are also replaced on Invoices,
Invoice Line Items, and Credit Note Line Items. Migrate serializers and field
access to the replacement representations. Manual tax amounts expose
jurisdiction level and taxability reason, and invoicing resources have a
`parent` field describing how they were generated.

Invoices can receive multiple partial payments, so reconciliation must not
assume that one payment settles an invoice.

### Payment capture outcomes (`2025-03-31.basil`)

Partial capture or payment cancellation no longer creates a Refund. Derive the
outcome from the payment objects instead of waiting for a Refund. Vault and
Forward upstream timeouts return HTTP 402.

### Rendering, line operations, and timing (`2024-09-30.acacia`)

Invoice Rendering Templates are API resources with retrieve and archive
operations, references on Invoices and Customers, and template versions.
Persist both the template and intended version when rendering must be
reproducible.

Invoices also support bulk line-item operations, events for becoming due or
overdue, and automatic finalization at a configured time. These contracts can
replace per-line mutation and external due-date polling.

### Upstream invoice presentation (`2026-07-29.dahlia`)

Subscription Schedules and Quotes can specify invoice descriptions, footers,
and custom fields. Generated invoices can carry those presentation settings.
Invoice previews also accept subscription metadata, allowing preview callers to
include the intended subscription context.

## Subscriptions, schedules, discounts, and portal

### Item-level periods and API removals (`2025-03-31.basil`)

Billing periods move from the Subscription to individual Subscription Items.
Use item-level periods. Upcoming Invoice methods are replaced by Create Preview
Invoice, and legacy usage-based billing is removed; migrate both before taking
this contract.

Subscription-mode Checkout Sessions postpone Subscription creation until
payment completes. Code must not assume the Subscription exists while checkout
is in progress, and billing details may change after an initial payment attempt.

### Coupon and multi-discount contracts (`2025-03-31.basil`)

Discount coupons without an end time are no longer supported. The singular
coupon and promotion-code parameters used with stackable discounts are also
removed. Use the remaining duration and multi-discount contracts.

### Schedule and discount-source migrations (`2025-09-30.clover`)

Subscription Schedules remove `iterations`. Billing-cycle-anchor changes now
affect phase-end computation, so stop sending `iterations` and allow projected
phase dates to change when an anchor resets.

Promotion Codes reference Coupons through a polymorphic promotion field.
Discounts add `source` and remove `coupon`; resolve discount origin through the
source representation.

### Flexible billing default (`2025-09-30.clover`)

New Subscriptions default to flexible billing mode. Set the intended mode
explicitly when lifecycle behavior must remain stable across an API-version
upgrade.

### Trials, proration, and pending updates

Customer Portal configuration adds trial behavior and proration discount
amounts can be itemized (`2025-09-30.clover`). Accept both the control and the
breakdown instead of assuming aggregate discounts only.

Subscription Schedule phases add a `trial` property, and pending subscription
updates support item-level discounts (`2026-07-29.dahlia`). Preserve phase-level
trial configuration and do not assume pending discounts are subscription-wide.

### Billing Portal updates (`2024-09-30.acacia`)

Billing Portal subscription-update configuration no longer has to update
products and prices. Other subscription-update behavior can be enabled without
forcing catalog changes.

## Usage metering and alerts

### Alerts and Meter Events v2 (`2024-09-30.acacia`)

Billing Alert resources and endpoints support contextual filters scoped to
subscriptions and subscription items, plus triggered-alert events and webhooks.
Usage thresholds can be configured and observed through the API instead of
being polled externally.

New v2 endpoints accept Meter Events. Treat them as a distinct v2 contract; do
not assume v1 meter-event request or response shapes.

### Meter aggregation and events (`2025-03-31.basil`)

Meters add a `last` aggregation formula, billing from the final event in a time
range instead of summing events. New webhook event types cover Billing Meters
and billing credits.

## Billing-credit grants (`billing-and-payments-v2`)

### Scope and invoice eligibility

Credit grants can represent prepaid or promotional credit for the business's
own products and services, but not gift cards, stored value, third-party
payments, or digital-wallet balances. They apply only to Meter-reported metered
subscription items—not one-off invoices, one-time setup items, licensed prices,
or legacy Usage Records.

Eligibility requires matching currency, balance at finalization, and
`period_end >= effective_at`; when an expiry exists, it also requires
`period_end < expires_at`.

### Allocation and ordering

Credits apply after discounts but before taxes and `invoice_credit_balance`.
They can be scoped to selected metered prices. Draft and preview allocations
are provisional because credit commits only at invoice finalization.

Allocation follows invoice finalization order, line order within an invoice,
then lower numeric grant priority, earlier expiration, promotional category,
earlier effective time, and earlier creation time.

### Lifecycle, reversals, and ledgers

Grants progress through pending, granted, depleted, expired, or voided states.
Void a grant only before any portion has been applied; otherwise expire its
remaining credit. Voiding an invoice restores the applied balance and
immediately expires it if the grant is already past `expires_at`. A Credit Note
does not restore credit and requires a new grant.

Credit Balance Summary separates available balance from ledger balance backed
by immutable, append-only Credit Balance Transactions. A customer can have at
most 100 unused grants, counted from pending state or positive ledger balance,
not available balance. A grant reserved on a draft invoice can still count when
its available balance is zero.

## Flexible billing migration (`billing-and-payments-v2`)

Migration requires API version `2025-06-30.basil` or later and is irreversible.
It affects only new activity and does not recalculate existing resources such
as pending proration Invoice Items. After migration, credit prorations use the
originally debited amount, usage is charged at the price in effect when
reported, and the billing-cycle anchor is never reset automatically.

An active subscription with a schedule can migrate only through the migrate
API, not the Dashboard; the schedule's `billing_mode` updates automatically. A
not-yet-started schedule without an active subscription must be canceled and
recreated as flexible. A schedule created with `from_subscription` inherits the
mode and rejects an explicitly supplied `billing_mode`.

## Billing payment-method surfaces

Billing adds Multibanco (`2024-09-30.acacia`). Hosted Invoice Pages add Klarna
and configurable payment-method saving for one-time payments
(`2025-03-31.basil`), then add MB WAY (`2026-07-29.dahlia`). Send-invoice
Invoices and Subscriptions also support Alipay (`2026-07-29.dahlia`). Preserve
each method on the surface where it is documented.
