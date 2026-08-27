# Billing, Invoicing, and Subscriptions

## Billing alerts and meters

### Usage-based Billing Alerts API (`2024-09-30.acacia`)

Billing Alerts are resources with API endpoints, subscription- and
subscription-item-scoped contextual filters, and triggered-alert event and
webhook support. Configure and observe usage thresholds through the API rather
than polling them externally.

### Meter Events v2 (`2024-09-30.acacia`)

Use the new v2 endpoints to submit Meter Events. Treat them as a separate v2
contract; do not assume v1 request and response shapes.

### Meter aggregation and events (`2025-03-31.basil`)

Meters support the `last` aggregation formula, which bills from the final event
in a time range instead of summing events. Event types also cover Billing Meters
and billing credits.

### Legacy usage and preview removal (`2025-03-31.basil`)

Replace Upcoming Invoice API methods with Create Preview Invoice. Legacy
usage-based billing is removed, so migrate those integrations before selecting
this contract.

## Invoice models and processing

### Pricing, tax, and provenance (`2025-03-31.basil`)

The newer price model replaces top-level price fields on Invoice Items and
Invoice Line Items. Replacement tax representations likewise supersede
top-level tax properties on Invoices, Invoice Line Items, and Credit Note Line
Items. Invoicing resources add `parent` to describe how they were generated.
Migrate serializers and field access, and accept the provenance shape.

### Multiple payments and manual tax (`2025-03-31.basil`)

An Invoice can receive multiple partial payments. Reconciliation must not
assume that one payment settles it. Manual tax amounts expose jurisdiction level
and taxability reason; preserve both.

### Rendering templates (`2024-09-30.acacia`)

Invoice Rendering Templates are API resources with retrieve and archive
operations. Invoices and Customers can reference a template, and templates
support versions. Persist both template and intended version when reproducible
rendering matters.

### Bulk and timed processing (`2024-09-30.acacia`)

Invoices support bulk line-item operations and automatic finalization at a
configured time. Due and overdue Invoice events can replace per-line mutations
and external due-date polling where appropriate.

### Credit Notes (`2024-09-30.acacia`)

Credit Notes add email types. Deserializers and exhaustive handling must accept
the additional values.

### Invoice presentation inherited from upstream (`2026-07-29.dahlia`)

Subscription Schedules and Quotes can specify Invoice descriptions, footers,
and custom fields. Preserve these presentation settings so generated Invoices
can inherit them.

### Subscription metadata in previews (`2026-07-29.dahlia`)

Invoice previews accept subscription metadata. Include the intended metadata
when the preview must reflect the planned Subscription context.

### Alipay for send-invoice collection (`2026-07-29.dahlia`)

Invoices and Subscriptions using send-invoice collection support Alipay. Do not
restrict Alipay to immediate-collection surfaces.

## Discounts, coupons, and promotion sources

### Coupon and stacked-discount migration (`2025-03-31.basil`)

Discount coupons require an end time. The singular coupon and promotion-code
parameters used with stackable discounts are removed; use the remaining
duration and multi-discount contracts.

### Promotion and discount source shapes (`2025-09-30.clover`)

Promotion Codes reference Coupons through a polymorphic promotion field.
Discounts add `source` and remove `coupon`; resolve discount origin through
`source`.

### Proration discount details (`2025-09-30.clover`)

Proration discount amounts can be itemized. Consumers must accept the breakdown
instead of assuming discounts are only aggregate.

### Item discounts in pending updates (`2026-07-29.dahlia`)

Pending Subscription updates support item-level discounts. Builders must not
assume all pending discounts apply only to the Subscription.

## Subscription lifecycle and schedules

### Item-level billing periods (`2025-03-31.basil`)

Read billing periods from individual Subscription Items; they no longer live on
the Subscription.

### Schedule phase contracts (`2025-09-30.clover`)

Stop sending the removed Subscription Schedule `iterations` parameter.
Phase-end computation accounts for billing-cycle-anchor changes, so projected
phase dates can change when an anchor resets.

### Phase trials (`2026-07-29.dahlia`)

Subscription Schedule phases add `trial`. Builders and serializers should use
and preserve phase-level trial configuration.

### Portal update behavior and trials

Billing Portal subscription-update configuration no longer has to update
products and prices (`2024-09-30.acacia`), so other update behavior can be
enabled without forcing catalog changes. Customer Portal configuration also
adds trial behavior (`2025-09-30.clover`).

## Flexible billing

### Default mode (`2025-09-30.clover`)

New Subscriptions default to flexible billing mode. Set the intended mode
explicitly when lifecycle behavior must remain stable across an API-version
upgrade.

### Migration semantics

Migrating an existing Subscription to flexible billing requires API version
`2025-06-30.basil` or later and is irreversible. It changes only new activity;
it does not recalculate existing resources such as pending proration Invoice
Items. After migration:

- credit prorations use the originally debited amount;
- usage is charged at the price in effect when reported; and
- the billing-cycle anchor is never reset automatically.

### Subscription schedules

An active Subscription with a schedule can migrate only through the migrate
API, not the Dashboard, and the schedule's `billing_mode` updates automatically.
A schedule that has not started and has no active Subscription must be canceled
and recreated as flexible. A schedule created with `from_subscription` inherits
the mode and rejects an explicit `billing_mode`.

## Billing credits

### Scope and invoice eligibility

Credit Grants can represent prepaid or promotional credit for the business's
own products and services. They cannot represent gift cards, stored value,
third-party payments, or digital-wallet balances.

They apply only to metered Subscription Items reported through Meters when all
of these conditions hold:

- Invoice `period_end >= effective_at`;
- if present, `period_end < expires_at`;
- currency matches; and
- balance exists at Invoice finalization.

They do not apply to one-off Invoices, one-time setup items, licensed prices, or
legacy Usage Records.

### Application order and commitment

Credits apply after discounts and before taxes and `invoice_credit_balance`.
A grant can be scoped to selected metered prices. Allocation on drafts and
previews is provisional; credit becomes committed only at Invoice finalization.

Allocation follows this order:

1. Invoice finalization order.
2. Line order within an Invoice.
3. Lower numeric grant priority.
4. Earlier expiration.
5. Promotional category.
6. Earlier effective time.
7. Earlier creation time.

### Grant state and reversals

Grant states are pending, granted, depleted, expired, and voided. Void a grant
only before any portion has been applied; otherwise expire its remaining
credit. Voiding an Invoice restores its applied balance and immediately expires
that balance if the grant is already past `expires_at`. A Credit Note does not
restore credit; issue a new grant instead.

### Ledger balances and the grant limit

Credit Balance Summary distinguishes available balance from ledger balance.
The latter is backed by immutable, append-only Credit Balance Transactions.

A Customer can have at most 100 unused grants. Count a grant from pending state
or positive ledger balance, not available balance. A grant reserved on a draft
Invoice can therefore still count while its available balance is zero.
