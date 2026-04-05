# Accounts v2 (Connect)

New API with configuration-based capabilities replacing the old account types. One Account object serves both connected accounts and customers.

```ts
const account = await stripe.v2.core.accounts.create({
  contact_email: 'jenny@example.com',
  display_name: 'Jenny Rosen',
  identity: {
    country: 'us',
    entity_type: 'company',
  },
  configuration: {
    merchant: {  // Accept payments
      capabilities: { card_payments: { requested: true } },
    },
    customer: {  // Can also be charged as a customer
      capabilities: { automatic_indirect_tax: { requested: true } },
    },
  },
  defaults: {
    currency: 'usd',
    responsibilities: { fees_collector: 'stripe', losses_collector: 'stripe' },
  },
  include: ['configuration.merchant', 'configuration.customer', 'identity', 'requirements'],
});
```

## Configurations

| Configuration | Purpose |
|--------------|---------|
| `merchant` | Accept payments |
| `customer` | Be charged as a customer |
| `recipient` | Receive transfers |

V2 responses return `null` for unincluded properties -- use the `include` param to request the data you need.
