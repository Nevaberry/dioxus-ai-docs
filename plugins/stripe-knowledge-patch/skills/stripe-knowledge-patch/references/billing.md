# Billing: Flexible Mode & Credit Grants

## Billing Mode (Flexible)

New subscription billing mode with improved proration, metered pricing, and trial support. Default in Clover+.

```ts
const subscription = await stripe.subscriptions.create({
  customer: 'cus_xxx',
  items: [{ price: 'price_xxx' }],
  billing_mode: 'flexible',  // or omit -- default in Clover+
});
```

Features:
- Mixed intervals (monthly + annual items on same subscription)
- Billing thresholds for usage-based billing
- Partial payments on invoices

## Billing Credits (Credit Grants)

Prepaid/promotional credits for usage-based billing. Only applies to metered prices using Meters (not legacy Usage Records).

```ts
const grant = await stripe.billing.creditGrants.create({
  customer: 'cus_xxx',
  amount: { type: 'monetary', monetary: { value: 1000, currency: 'usd' } },
  applicability_config: {
    scope: { price_type: 'metered' },
  },
  category: 'paid',  // or 'promotional'
  effective_at: Math.floor(Date.now() / 1000),
  expires_at: Math.floor(Date.now() / 1000) + 86400 * 90,
});
```

Credits apply after discounts, before taxes. Can set price-level applicability and custom priority with multiple grants.
