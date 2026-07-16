# Billing, Invoicing, and Subscriptions

## Breaking billing migrations

### Pricing, tax, and discount shapes

- In `2025-03-31.basil`, Invoice Items and Invoice Line Items replace top-level price fields with pricing configurations.
- Invoices, Invoice Line Items, and Credit Note Line Items replace top-level tax properties with tax configurations. Manual invoice tax amounts add jurisdiction level and taxability reason.
- Coupons without an end time are unsupported. Parameters on Coupons and Promotion Codes that belonged to the singular-discount model are removed when stackable discounts are used.
- In `2025-09-30.clover`, Promotion Codes refer to coupons through a polymorphic `promotion` field, and Discounts replace `coupon` with `source`.

### Invoice payment and period assumptions

- An Invoice can have multiple payments, including partial payments. Never assume one payment settles the Invoice (`2025-03-31.basil`).
- Billing periods live on Subscription Items; subscription-level current-period start and end fields are removed.
- Partial capture and payment cancellation no longer create a Refund object. Base refund logic on actual Refund resources and events.

### Preview and legacy usage APIs

- Use Create Preview Invoice in place of Upcoming Invoice methods.
- Legacy usage-based billing is removed. Report usage through Meters.
- Invoicing resources expose a `parent` field that identifies how each resource was generated.

## Subscription lifecycle

### Flexible billing defaults and explicit selection

- New Subscriptions default to flexible billing mode in `2025-09-30.clover`. Set `billing_mode` explicitly if classic lifecycle behavior is required.
- Creating or fully modifying a flexible Subscription through the API requires `2025-06-30.basil` or later.
- Migration changes only subsequent activity. It does not recalculate existing resources such as pending proration Invoice Items.
- The selected mode and proration display behavior are nested under `billing_mode`.

```sh
curl https://api.stripe.com/v1/subscriptions \
  -u "$STRIPE_SECRET_KEY:" \
  -H "Stripe-Version: 2025-06-30.basil" \
  -d "items[0][price]=$PRICE_ID" \
  -d "customer=$CUSTOMER_ID" \
  -d "billing_mode[type]=flexible" \
  -d "billing_mode[flexible][proration_discounts]=itemized"
```

### Mode inheritance and Dashboard scope

- When creating a Subscription Schedule with `from_subscription`, omit `billing_mode`; the Schedule inherits the Subscription's mode, and specifying both produces an error.
- Changing modes requires a new Subscription.
- The Dashboard billing-mode default affects the Dashboard subscription editor and Dashboard-created Payment Links and Pricing Tables.
- That Dashboard setting does not select the mode for API-created Subscriptions or migrations. This is separate from the API-version behavior under which newly created Subscriptions default to flexible mode.

### Schedules, anchors, trials, and proration

- Subscription Schedule phases no longer accept `iterations`; express phase length with supported duration fields (`2025-09-30.clover`).
- Phase-end computation now accounts for billing-cycle-anchor changes.
- Customer Portal configurations can define trial behavior.
- Proration discount amounts can be itemized, which changes line-level rendering.
- In `2026-03-25.dahlia`, Checkout Session subscription creation can set a pending-invoice-item interval for the billing interval of pending items.
- Subscriptions add a retention-policy cancellation reason. Event consumers and exhaustive switches must accept it.

### Subscription-item Trial Offers

The public-preview Trial Offers API creates and manages trials for individual Subscription Items (`2026-03-25.dahlia`). Keep this contract isolated from stable subscription code.

## Invoice operations and rendering

### Automation and line items

- Bulk Invoice Line Item operations and automatic Invoice finalization are available (`2024-09-30.acacia`).
- Billing emits events when Invoices become due or overdue.
- Credit Notes add email types.
- Invoice Items and Invoice Line Items accept decimal quantities with up to 12 decimal places on create and update (`2026-03-25.dahlia`).
- Credit Note Line Items expose metadata.

### Rendering templates

Invoice Rendering Templates are API resources with retrieve, archive, and version operations. Associate them with Invoices or Customers (`2024-09-30.acacia`).

### Hosted Invoice Page

- The Hosted Invoice Page supports Klarna (`2025-03-31.basil`).
- It can save a payment method for later one-time payments.

## Billing credits

### Credit Grant lifecycle

A Credit Grant progresses through `pending`, `granted`, `depleted`, `expired`, or `voided` states.

- Omit `effective_at` to make the grant immediately effective.
- Set `expires_at` or call the expire endpoint to end remaining credit.
- Void a grant only if none of it has ever been applied to an Invoice.
- Once any credit has been applied, expire the remainder instead of voiding it.

### Eligibility and application point

Billing credits apply only to Subscription Items whose metered Prices report usage through Meters. They do not apply to:

- one-off Invoices;
- one-time Subscription Invoice Items;
- licensed Prices; or
- legacy Usage Records.

The Invoice `period_end` must be within the Credit Grant's effective and expiration window, and currencies must match. Stripe applies the credit after discounts but before taxes and the Customer's `invoice_credit_balance`.

### Applicability and allocation order

- An applicability scope can restrict a grant to selected metered Prices.
- Across Invoices, the Invoice that finalizes first consumes credit first.
- Within one Invoice, lines consume credit in displayed order.
- Competing grants are ordered by lower numeric `priority`, earlier `expires_at`, `promotional` category, earlier `effective_at`, and earlier creation time.

### Finalization and balance views

- Credit is consumed only when an Invoice finalizes. Preview and draft allocations are provisional and can change if another Invoice finalizes first.
- Shared provisional credit can delay billing-threshold triggers.
- `ledger_balance` reflects the immutable ledger.
- `available_balance` also accounts for expired credit and transactions not yet recorded in the ledger.

### Restoration

- Voiding an Invoice reinstates its applied credit. If the grant is already past `expires_at`, the restored amount expires immediately.
- A Credit Note does not restore applied billing credit. Issue a new Credit Grant when restoration is required.

### Unused-grant limit

A Customer can have at most 100 unused grants. An unvoided, unexpired grant counts when it is pending or has a positive `ledger_balance`. Because counting uses `ledger_balance`, a grant with zero available balance can still count until invoice finalization, depletion, expiration, or voiding.

## Meters, alerts, and test controls

### Billing Alerts and Meter Events v2

In `2024-09-30.acacia`, Billing Alert resources and endpoints add contextual filters, Subscription and Subscription Item support, and triggered-alert events for webhook consumers. Meter Events v2 endpoints are also available.

Meters add a `last` aggregation formula in `2025-03-31.basil`. New webhook types cover Billing Meters and billing credits.

### Test Clocks and Billing Portal

- Advancing `test_helpers.test_clock` accepts `target_frozen_time` (`2024-09-30.acacia`).
- Test Clock helpers require status details.
- Billing Portal updates do not have to change Subscription products or Prices.

## Adaptive Pricing subscriptions

Adaptive Pricing Subscriptions expose `presentment_details` in `2026-03-25.dahlia`, extending customer-facing currency presentation data from Checkout to Subscriptions.
