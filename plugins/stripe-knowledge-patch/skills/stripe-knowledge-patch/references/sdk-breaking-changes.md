# SDK Breaking Changes (Dahlia)

## stripe-node v21 -- Decimal Type

All `decimal_string` fields changed from `string` to `Stripe.Decimal` (vendored BigInt-backed type, zero deps). Affected fields: `unit_amount_decimal`, `quantity_decimal`, `fx_rate`, `amount_decimal`, etc.

```ts
import Stripe from 'stripe';

// Reading: rate is now Stripe.Decimal, not string
const rate = session.currency_conversion.fx_rate;
rate.toString(); // "1.23"
rate.toNumber(); // 1.23

// Writing: must use Decimal.from(), not raw string
const price = await stripe.prices.create({
  unit_amount_decimal: Stripe.Decimal.from('9.99'),
  currency: 'usd',
  recurring: { interval: 'month' },
  product: 'prod_xxx',
});

// Arithmetic
const a = Stripe.Decimal.from('10.50');
a.add(b); a.sub(b); a.mul(b); a.div(b, 6, 'half-up');
```

Minimum Node version raised to 18. Webhook parsing now throws if you use the wrong method (v1 vs v2).

## stripe-python v15 -- StripeObject No Longer Inherits from dict

`StripeObject` dropped `dict` inheritance. `.get()`, `.keys()`, `.values()`, `.items()`, `dict(obj)`, `for key in obj` all break.

```python
# BROKEN in v15:
customer.get("name")        # AttributeError
customer.items()             # Now returns subscription items, not dict.items()
dict(customer)               # Empty
for key in customer: ...     # No longer iterates

# FIXED:
customer.name                # Attribute access still works
customer["name"]             # Bracket notation still works
customer.to_dict()           # Get a plain dict (recurses)
customer.to_dict().get("name", "default")  # Replace .get()
```

Decimal fields changed from `str` to `decimal.Decimal`:

```python
from decimal import Decimal

stripe.Price.create(
    unit_amount_decimal=Decimal("9.99"),  # not "9.99"
    currency="usd",
    recurring={"interval": "month"},
    product="prod_xxx",
)
```

Minimum Python version raised to 3.9. V2 Amount types consolidated to `stripe.v2.Amount`.

## Basil Breaking Changes (2025-03-31)

- **`total_count` removed from lists**: `list.total_count` expansion no longer supported
- **Checkout subscription creation deferred**: Checkout Sessions for subscriptions now create the subscription *after* payment completes (not on session creation)
- **Legacy usage-based billing removed**: Migrate to Meters API
- **Upcoming Invoice API replaced**: Use `stripe.invoices.createPreview()` instead of the old upcoming invoice endpoint
