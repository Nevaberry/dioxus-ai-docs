# Payments, pricing, and promotions

## Payment lifecycle and methods

### Order cancellation settles associated payments (2.2.0)

Canceling an order cancels its payments. Uncaptured payments are canceled
immediately; captured payments trigger an attempted refund for the captured
amount.

### Saved payment-method listing (2.3.0)

The Payment Module and Stripe provider support listing saved payment methods,
so integrations need no provider-specific workaround solely to enumerate them.

### Payment-method creation (2.4.0)

The Payment Module supports creating payment methods, allowing integrations to
register them through the module rather than only listing saved methods.

### Zero-balance and recoverable payment completion (2.7.0)

A cart with a zero balance can complete without a payment. Payment handling
preserves sessions through certain Stripe errors so webhooks can reconcile
them, and attempts to cancel payment when webhook-driven cart completion fails.

### Ad-hoc order refunds and refund reasons (2.11.0)

Orders can be refunded without a return, exchange, or negative difference due.
Admin-managed Refund Reasons categorize these refunds. Refunds create matching
order credit lines and cannot exceed the captured amount. Apply the schema
changes on upgrade:

```sh
npx medusa db:migrate
```

### OXXO payments through Stripe (2.12.0)

The Stripe payment provider supports OXXO payments with a configurable
expiration period.

### Captured payment sessions during cart completion (2.13.0)

Cart completion can process a payment session already in `captured` state
instead of failing because it has moved past authorization.

## Pricing behavior

### Sale price lists preserve lower prices (2.3.0)

A Sale-type price list no longer overrides an already lower applicable price,
so sale pricing does not make an item more expensive.

### Multiple-value pricing rules (2.9.0)

Price calculation correctly handles rules containing multiple values.

### Custom-price items without variant prices (2.13.0)

Adding a custom-price line item no longer throws when its variant has no stored
prices. Custom pricing can supply the effective price without a variant price
record.

### Full pricing context for draft-order items (2.14.0)

Adding draft-order items resolves them with the full pricing context, so
context-dependent prices are selected consistently while creating and editing
draft orders.

### Repository-wide currency-code normalization (2.14.0)

Currency-code formatting, validation, and storage are normalized consistently
across commerce modules and APIs, including cart, order, payment, and pricing
behavior.

### Pacific franc currency support (2.9.0)

Pacific franc is included among Medusa's supported currencies.

## Promotion state and validation

### Promotion lifecycle statuses (2.3.0)

Promotions can be `active`, `inactive`, or `draft`. Existing promotions migrate
to `active`; new promotions default to `draft` unless a status is supplied.

### Soft-delete-aware promotion uniqueness (2.6.0)

Promotion uniqueness applies only to non-deleted promotions, so a unique value
held by a soft-deleted promotion can be reused.

### Invalid promotion codes fail the request (2.9.0)

Applying an invalid promotion code throws instead of succeeding without an
application. Storefronts should handle an HTTP 400 response whose message
identifies the invalid code rather than checking the cart's promotions after
the request.

### Promotion metadata (2.12.0)

The Promotion model has a metadata column for values stored directly on a
promotion.

### Promotion-code management in the JS SDK (2.14.0)

The JavaScript SDK exposes methods for managing promotion codes, so clients do
not need raw requests for those operations.

## Promotion calculation and limits

### Tax-inclusive promotion adjustment basis (2.9.0)

In a tax-inclusive context, a line item's promotion `applicableTotal` is based
on its total including tax, matching the basis used for the promotion value.
Previous versions used the tax-exclusive subtotal and could calculate an
incorrect adjustment.

### Currency-aware promotion actions (2.9.0)

Promotion action calculation checks currency when finding applicable actions,
so currency participates in promotion applicability.

### Free-shipping promotions by Shipping Option Type (2.10.0)

Admin promotions can grant free shipping only for selected Shipping Option
Types, allowing Standard shipping to be free without also making Express
shipping free.

### Per-customer promotion limits (2.11.0)

Campaign budgets can use `USE_BY_ATTRIBUTE` and an attribute such as
`customer_id` or `email`. The budget `limit` applies separately to each
attribute value. Usage is stored in `CampaignBudgetUsage` and registered during
cart completion.

### Cart-wide `once` promotion allocation (2.11.0)

The `once` allocation method applies a promotion to at most `max_quantity`
items across the entire cart rather than per line item. It requires
`max_quantity`, prioritizes the lowest-priced eligible items, and distributes
the allocation sequentially until the quota is exhausted.

### Promotion-level usage limits (2.12.0)

A promotion can have its own usage limit independently of campaign-wide and
per-customer or per-email campaign limits.

### Promotion carry-over on exchanges (2.12.0)

The exchange flow offers **Carry over promotions**. Enabling it applies the
original promotions to outbound exchange items so the customer is not charged
again for the discounted amount.

### Fixed-value Buy/Get promotions (2.14.0)

Buy/Get promotion handling supports the fixed discount type rather than
assuming only the previously handled discount behavior.
