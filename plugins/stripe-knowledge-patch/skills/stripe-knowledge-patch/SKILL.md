---
name: stripe-knowledge-patch
description: "Stripe changes since training cutoff (latest: 2026-03-25.dahlia) -- named API versions, stripe-node v21 Decimal type, stripe-python v15 dict removal, Billing Mode, Accounts v2, Event Destinations. Load before working with Stripe."
license: MIT
metadata:
  author: Nevaberry
  version: "2026-03-25.dahlia"
---

# Stripe Knowledge Patch (Acacia to Dahlia)

Claude's baseline knowledge covers the Stripe API through 2024-06-20 and stripe-node ~16.x / stripe-python ~10.x. This skill covers changes from Acacia (2024-09-30) through Dahlia (2026-03-25).

## API Version Timeline

| Version | Date | Key Changes |
|---------|------|-------------|
| Acacia | 2024-09-30 | Named version scheme begins |
| Basil | 2025-03-31 | `total_count` removed, deferred subscription creation, Meters API |
| Clover | 2025-09-30 | Billing Mode `flexible` becomes default |
| Dahlia | 2026-03-25 | Decimal types, Checkout UI mode renames, Stripe.js renames |

Format: `YYYY-MM-DD.name` (e.g., `2025-03-31.basil`). Monthly additive releases reuse the same name.

## SDK Breaking Changes Quick Reference

### stripe-node v21 (Dahlia) -- Decimal Fields

All `decimal_string` fields changed from `string` to `Stripe.Decimal`:

```ts
// Reading: now Stripe.Decimal, not string
const rate = session.currency_conversion.fx_rate;
rate.toString(); // "1.23"
rate.toNumber(); // 1.23

// Writing: must use Decimal.from()
unit_amount_decimal: Stripe.Decimal.from('9.99')

// Arithmetic
a.add(b); a.sub(b); a.mul(b); a.div(b, 6, 'half-up');
```

Minimum Node version: 18. Webhook parsing throws if wrong method used (v1 vs v2).

### stripe-python v15 (Dahlia) -- No More dict Inheritance

```python
# BROKEN in v15:
customer.get("name")     # AttributeError
customer.items()          # Returns subscription items, not dict items!
dict(customer)            # Empty dict
for key in customer: ...  # No longer iterates

# Use instead:
customer.name             # Attribute access
customer["name"]          # Bracket notation
customer.to_dict()        # Get plain dict
```

Decimal fields: use `decimal.Decimal("9.99")` not `"9.99"`. Min Python: 3.9.

### Basil Breaking Changes

- **`total_count` removed** from list endpoints -- no more `list.total_count`
- **Checkout subscription creation deferred** -- subscription created after payment, not on session creation
- **Legacy usage-based billing removed** -- migrate to Meters API
- **Upcoming Invoice API replaced** -- use `stripe.invoices.createPreview()`

## Stripe.js Method Renames (Dahlia)

| Removed | Replacement |
|---------|-------------|
| `stripe.initCheckout()` | `stripe.initCheckoutElements()` |
| `stripe.initEmbeddedCheckout()` | `stripe.createEmbeddedCheckoutPage()` |
| `stripe.confirmCardPayment()` | `stripe.confirmPayment()` |
| `stripe.confirmCardSetup()` | `stripe.confirmSetup()` |
| `stripe.handleCardAction()` | `stripe.handleNextAction()` |

`elements.update()` now returns a Promise. Layout `radios` no longer accepts boolean -- use `'accordion'` or `'tabs'`.

## Checkout Session UI Modes (Dahlia)

| Old Value | New Value |
|-----------|-----------|
| `embedded` | `embedded_page` |
| `custom` (preview) | `elements` |
| -- | `form` |
| -- | `hosted_page` |

```ts
const session = await stripe.checkout.sessions.create({
  ui_mode: 'elements',
  mode: 'payment',
  line_items: [{ price: 'price_xxx', quantity: 1 }],
});
```

## Billing Mode (Flexible)

Default in Clover+. Supports mixed intervals, billing thresholds, partial payments.

```ts
const subscription = await stripe.subscriptions.create({
  customer: 'cus_xxx',
  items: [{ price: 'price_xxx' }],
  billing_mode: 'flexible',  // default in Clover+, explicit in Basil
});
```

See [`billing.md`](references/billing.md) for Credit Grants API.

## Billing Credits (Credit Grants)

Prepaid/promotional credits for metered prices (Meters API only, not legacy Usage Records).

```ts
const grant = await stripe.billing.creditGrants.create({
  customer: 'cus_xxx',
  amount: { type: 'monetary', monetary: { value: 1000, currency: 'usd' } },
  applicability_config: { scope: { price_type: 'metered' } },
  category: 'paid',  // or 'promotional'
  effective_at: Math.floor(Date.now() / 1000),
  expires_at: Math.floor(Date.now() / 1000) + 86400 * 90,
});
```

Credits apply after discounts, before taxes.

## Event Destinations API

Unified API for webhooks, Amazon EventBridge, and Azure Event Grid.

```ts
const destination = await stripe.v2.core.eventDestinations.create({
  type: 'webhook_endpoint',
  url: 'https://example.com/webhook',
  enabled_events: ['payment_intent.succeeded'],
});

// Test connectivity
await stripe.v2.core.events.ping({ destination: destination.id });
```

See [`event-destinations.md`](references/event-destinations.md) for thin vs snapshot events.

## Accounts v2 (Connect)

Configuration-based capabilities replace old account types. One Account for both connected accounts and customers.

```ts
const account = await stripe.v2.core.accounts.create({
  contact_email: 'jenny@example.com',
  display_name: 'Jenny Rosen',
  identity: { country: 'us', entity_type: 'company' },
  configuration: {
    merchant: { capabilities: { card_payments: { requested: true } } },
    customer: { capabilities: { automatic_indirect_tax: { requested: true } } },
  },
  defaults: {
    currency: 'usd',
    responsibilities: { fees_collector: 'stripe', losses_collector: 'stripe' },
  },
  include: ['configuration.merchant', 'configuration.customer', 'identity', 'requirements'],
});
```

Configurations: `merchant` (accept payments), `customer` (be charged), `recipient` (receive transfers). V2 responses return `null` for unincluded properties -- use `include` param. See [`accounts-v2.md`](references/accounts-v2.md).

## Payment Line Items

L2/L3 transaction data for interchange savings (commercial cards), better auth rates, and reconciliation.

```ts
const paymentIntent = await stripe.paymentIntents.create({
  amount: 5000,
  currency: 'usd',
  payment_method_types: ['card'],
  payment_line_items: [
    {
      product_code: 'SKU-123',
      product_description: 'Widget',
      quantity: 2,
      unit_cost: 2000,
      tax_amount: 500,
      discount_amount: 0,
      total_amount: 4500,
    },
  ],
});
```

## Crypto Payments (Basil+)

Stablecoin payments that settle as fiat in your Stripe balance.

```ts
const pi = await stripe.paymentIntents.create({
  amount: 1000,
  currency: 'usd',
  payment_method_types: ['crypto'],
});
```

## stripe-python v15 Decimal Fields

```python
from decimal import Decimal

stripe.Price.create(
    unit_amount_decimal=Decimal("9.99"),  # not "9.99"
    currency="usd",
    recurring={"interval": "month"},
    product="prod_xxx",
)
```

V2 Amount types consolidated to `stripe.v2.Amount`. See [`sdk-breaking-changes.md`](references/sdk-breaking-changes.md).

## Reference Files

| File | Contents |
|------|----------|
| [`sdk-breaking-changes.md`](references/sdk-breaking-changes.md) | Full stripe-node v21 and stripe-python v15 migration details |
| [`billing.md`](references/billing.md) | Billing Mode (Flexible), Credit Grants, metered pricing |
| [`accounts-v2.md`](references/accounts-v2.md) | Accounts v2 (Connect) configuration-based capabilities |
| [`event-destinations.md`](references/event-destinations.md) | Unified webhook/EventBridge/Event Grid API |
| [`payments.md`](references/payments.md) | Payment Line Items (L2/L3), Crypto Payments |
