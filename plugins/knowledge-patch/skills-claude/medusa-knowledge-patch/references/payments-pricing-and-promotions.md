# Payments, pricing, and promotions

## Payments and refunds

### Ad-hoc order refunds and refund reasons (since 2.11.0)

Orders can now be refunded without a return, exchange, or negative difference due. Admin-managed Refund Reasons categorize these refunds, which create corresponding order credit lines and cannot exceed the captured amount; upgrades must run `npx medusa db:migrate` for the schema changes.

### Captured payment sessions during cart completion (since 2.13.0)

Cart completion can now process a payment session that is already in the `captured` state instead of failing because the session has advanced past authorization.

### Fulfillment- and payment-status filters removed (since 2.6.0)

HTTP validators and request types no longer expose fulfillment- and payment-status filters, so clients must stop sending those fields in filtered requests.

### Multiple payment account holders per customer (since 2.7.0)

A customer can now have account holders for multiple payment providers. Custom payment code must replace `customer.account_holder` with `customer.account_holders` and select the entry matching the desired `provider_id`; projects without account-holder customizations are unaffected.

### Order cancellation settles associated payments (since 2.2.0)

Canceling an order now also cancels its payments. Uncaptured payments are canceled immediately; captured payments trigger an attempted refund for the captured amount.

### OXXO payments through Stripe (since 2.12.0)

The Stripe payment provider now supports OXXO payments with a configurable expiration period.

### Payment model fields removed (since 2.3.0)

The Payment Module no longer stores `region_id` on Payment Collections or `cart_id`, `order_id`, and `customer_id` on payments. Code and integrations that read or write those fields must be updated when moving to 2.3.0.

### Payment-method creation (since 2.4.0)

The Payment Module now supports creating payment methods, so integrations can register them through the module rather than only listing existing saved methods.

### Payment-provider contract redesigned for V2 (since 2.5.0)

Payment-provider methods now take dedicated single input objects such as `InitiatePaymentInput`, `AuthorizePaymentInput`, `CapturePaymentInput`, and `RefundPaymentInput`; this also applies to update, delete, retrieve, cancel, status, list-method, and save-method operations. Providers must throw errors instead of returning them to the Payment Module, and custom providers must update their implementations to the new signatures.

Providers can optionally implement `createAccountHolder` and `deleteAccountHolder`. The Store API endpoint `POST /store/payment-collections/:id/payment-sessions` no longer accepts a caller-supplied `context`, so storefronts must remove that field from session-creation requests.

### Retryable cart completion and payment recovery (since 2.8.0)

`completeCartWorkflow` is now stored but non-idempotent, so a completed failed execution can be retried with the same cart transaction ID after its constraints are corrected; the transaction ID still serializes concurrent attempts. Payment authorization now runs after first-party checks, failure compensation recreates the Medusa payment session, and a capture webhook can authorize, create, and capture a payment when Medusa has no corresponding payment yet.

### Saved payment-method listing (since 2.3.0)

The Payment Module and Stripe provider now support listing saved payment methods, so integrations no longer need a provider-specific workaround merely to enumerate them.

### Zero-balance and recoverable payment completion (since 2.7.0)

A cart whose balance is zero can now complete without a payment. Payment handling also preserves sessions through certain Stripe errors so webhooks can reconcile them, and attempts to cancel payment when webhook-driven cart completion fails.

## Pricing and currency

### Custom-price items without variant prices (since 2.13.0)

Adding a custom-price line item no longer throws when its variant has no stored prices. Custom pricing can therefore supply the effective price without requiring a variant price record.

### Dynamic pricing-context workflow hooks (since 2.7.0)

Pricing-sensitive cart, order, shipping-option, claim, exchange, order-edit, and return workflows now expose `hooks.setPricingContext`. The hook returns a `StepResponse` whose fields participate in pricing-rule selection:

```ts
import { addToCartWorkflow } from "@medusajs/medusa/core-flows"
import { StepResponse } from "@medusajs/workflows-sdk"

addToCartWorkflow.hooks.setPricingContext(() =>
  new StepResponse({ location_id: "loca_1234" })
)
```

The hook is also available on `createCartsWorkflow`, `listShippingOptionsForCartWorkflow`, `refreshCartItemsWorkflow`, `updateLineItemInCartWorkflow`, `addLineItemsToOrderWorkflow`, `createOrderWorkflow`, and the shipping-method workflows for claims, exchanges, order edits, and returns.

### Full pricing context for draft-order items (since 2.14.0)

Adding items to a draft order now resolves them with the full pricing context, so context-dependent prices are selected consistently during draft-order creation and editing.

### Multiple-value pricing rules (since 2.9.0)

Price calculation now correctly handles rules that contain multiple values.

### Pacific franc currency support (since 2.9.0)

Pacific franc is now included among Medusa's supported currencies.

### Pricing-context identity precedence (since 2.12.0)

A `setPricingContext` hook result no longer overrides the customer and region established by the core flow, so custom pricing context can be supplied without replacing those built-in values.

### Repository-wide currency-code normalization (since 2.14.0)

Currency-code formatting, validation, and storage are now normalized consistently across commerce modules and APIs, including cart, order, payment, and pricing behavior.

### Sale price lists preserve lower prices (since 2.3.0)

A Sale-type price list no longer overrides an already lower applicable price, so sale pricing does not inadvertently make an item more expensive.

### Variant updates preserve prices (since 2.5.0)

Updating variants no longer unintentionally unsets their prices, changing the expected behavior for integrations that previously had to restore prices after an update.

### Zero-priced custom line items (since 2.6.0)

Core Flows now accept `unit_price: 0` for custom line items instead of treating zero as an absent or invalid value.

## Promotions

### Cart-wide `once` promotion allocation (since 2.11.0)

The new `once` allocation method applies a promotion to at most `max_quantity` items across the whole cart rather than per line item. It requires `max_quantity`, prioritizes the lowest-priced eligible items, and distributes the allocation sequentially until that quota is exhausted.

### Currency-aware promotion actions (since 2.9.0)

Promotion action calculation now checks currency when determining applicable actions, so currency participates in promotion applicability.

### Fixed-value Buy/Get promotions (since 2.14.0)

Buy/Get promotion handling now supports the fixed discount type instead of assuming only the previously handled discount behavior.

### Free-shipping promotions by Shipping Option Type (since 2.10.0)

Admin promotions can now grant free shipping only for selected Shipping Option Types, allowing rules such as free Standard shipping without also making Express shipping free.

### Invalid promotion codes fail the request (since 2.9.0)

Applying an invalid promotion code now throws instead of succeeding without applying it. Storefronts should handle an HTTP 400 response whose message identifies the invalid code rather than checking the cart's promotions after the request.

### Per-customer promotion limits (since 2.11.0)

Campaign budgets can use the new `USE_BY_ATTRIBUTE` type and an attribute such as `customer_id` or `email`; the budget's `limit` then applies separately to each attribute value. Usage is stored in `CampaignBudgetUsage` and registered during cart completion.

### Promotion carry-over on exchanges (since 2.12.0)

The exchange flow now offers a **Carry over promotions** option. Enabling it applies the original promotions to outbound exchange items so the customer is not charged again for the discounted amount.

### Promotion lifecycle statuses (since 2.3.0)

Promotions can now be `active`, `inactive`, or `draft`. Existing promotions migrate to `active`, while newly created promotions default to `draft` unless a status is explicitly supplied.

### Promotion metadata (since 2.12.0)

The Promotion model now has a metadata column for storing custom values directly on a promotion.

### Promotion-code management in the JS SDK (since 2.14.0)

The JavaScript SDK now exposes methods for managing promotion codes, so clients no longer need to make raw requests for those operations.

### Promotion-level usage limits (since 2.12.0)

A promotion can now have its own usage limit, independently of campaign-wide and per-customer or per-email campaign limits.

### Soft-delete-aware promotion uniqueness (since 2.6.0)

Promotion uniqueness now applies only to non-deleted promotions, so a unique value held by a soft-deleted promotion can be reused.

### Tax-inclusive promotion adjustment basis (since 2.9.0)

In a tax-inclusive context, a line item's promotion `applicableTotal` is now based on its total including tax, matching the basis used for the promotion value. Previous versions used the tax-exclusive subtotal and could calculate an incorrect adjustment.
