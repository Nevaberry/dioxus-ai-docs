# Payment Line Items & Crypto Payments

## Payment Line Items

Send L2/L3 transaction data with PaymentIntents for interchange savings (commercial cards), better auth rates (Klarna/PayPal), and reconciliation.

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

Accept stablecoin payments that settle as fiat in your Stripe balance.

```ts
const pi = await stripe.paymentIntents.create({
  amount: 1000,
  currency: 'usd',
  payment_method_types: ['crypto'],
});
```
