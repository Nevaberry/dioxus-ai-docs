# Carts, orders, workflows, and events

## Cart workflow behavior

### Pre-operation cart validation hooks (2.3.0)

Every cart workflow exposes a `validate` hook that runs before its operation.
Custom rules can abort the workflow:

```ts
import { completeCartWorkflow } from "@medusajs/medusa/core-flows"

completeCartWorkflow.hooks.validate(({ cart }) => {
  if (!cart.metadata.approved_at) {
    throw new Error("Cannot complete unapproved cart")
  }
})
```

### Cart credit lines (2.6.0)

The Cart Module, cart types, and Core Flows support credit lines on carts.

### Zero-priced custom line items (2.6.0)

Core Flows accept `unit_price: 0` for custom line items instead of treating zero
as absent or invalid.

### Dynamic pricing-context workflow hooks (2.7.0)

Pricing-sensitive cart, order, shipping-option, claim, exchange, order-edit,
and return workflows expose `hooks.setPricingContext`. The hook returns a
`StepResponse`; its fields participate in pricing-rule selection:

```ts
import { addToCartWorkflow } from "@medusajs/medusa/core-flows"
import { StepResponse } from "@medusajs/workflows-sdk"

addToCartWorkflow.hooks.setPricingContext(() =>
  new StepResponse({ location_id: "loca_1234" })
)
```

It is also available on `createCartsWorkflow`,
`listShippingOptionsForCartWorkflow`, `refreshCartItemsWorkflow`,
`updateLineItemInCartWorkflow`, `addLineItemsToOrderWorkflow`,
`createOrderWorkflow`, and shipping-method workflows for claims, exchanges,
order edits, and returns.

### Retryable cart completion and payment recovery (2.8.0)

`completeCartWorkflow` is stored but non-idempotent. A completed failed
execution can be retried with the same cart transaction ID after correcting its
constraints; the ID still serializes concurrent attempts. Payment authorization
runs after first-party checks, and failure compensation recreates the Medusa
payment session. A capture webhook can authorize, create, and capture a payment
when Medusa has no corresponding payment.

### Workflow idempotency retention and cart serialization (2.10.0)

Setting a workflow as `idempotent` prevents concurrent execution only while it
is running. Completed executions are not retained indefinitely unless a
retention time is configured. All cart workflows are idempotent, serializing
concurrent cart mutations.

### Pricing-context identity precedence (2.12.0)

A `setPricingContext` result no longer overrides the customer and region set by
the core flow. Custom pricing context can be supplied without replacing those
built-in values.

### Cart-updated events after line-item deletion (2.13.0)

`deleteLineItemsWorkflow` emits the cart-updated event after removing line
items, so subscribers are notified of this mutation.

## Order and draft-order flows

### Order-return workflow result (2.6.0)

The order-return workflow returns the created order return, allowing callers to
consume it directly from the workflow result.

### Draft-order workflows and API endpoints (2.7.0)

Core Flows and the HTTP API provide workflows and endpoints for creating and
operating on draft orders.

### Draft Orders are enabled by default (2.10.0)

The Draft Order plugin is installed by default and adds Admin flows for
creating, editing, and finalizing draft orders with custom prices, line items,
and shipping methods. Versions 2.4.0 through 2.9.x require explicit plugin
installation and registration.

### Custom order display IDs (2.12.0)

Orders expose `custom_display_id`; the existing auto-incrementing integer
`display_id` is unchanged. Configure the Order Module's
`generateCustomDisplayId` option to generate the custom value during order
creation. The callback receives `OrderTypes.CreateOrderDTO` and a `Context`.
Enable View Configurations to customize the field on the Admin order table:

```ts
defineConfig({
  modules: [{
    resolve: "@medusajs/medusa/order",
    options: {
      generateCustomDisplayId: async () => `web-${Date.now()}`,
    },
  }],
  featureFlags: {
    view_configurations: true,
  },
})
```

### Completed orders cannot be canceled (2.14.0)

Order cancellation rejects completed orders. Integrations must stop offering or
attempting cancellation once an order reaches completion.

### Customer transfers can update the order email (2.14.0)

Order customer-transfer requests can update the original `order.email`, so the
transferred order's contact email can follow the new customer when requested.

### Order item-change metadata and matching (2.14.0)

An `item_update` change action updates item metadata. If multiple order items
refer to one variant, line-action resolution also considers price and metadata
rather than matching only by variant.

## Workflow execution and compensation

### Automatic workflow-execution retention cleanup (2.5.0)

The workflow engine runs an hourly job that deletes stale executions after
their configured retention time and persists the value in
`workflow_execution.retention_time`. Retention is in seconds. Existing values
mistakenly configured in milliseconds can make the migration fail with a
PostgreSQL integer-cast error and must be corrected when running the migration
manually.

### Queued events are cleared during workflow compensation (2.10.0)

When a workflow is compensated, `emitEventsStep` removes its queued events
instead of emitting them during rollback. Workflows that intentionally require
the old behavior must use a custom event-emitting step with no compensation
step.

## Events and notifications

### Order-edit events (2.8.0)

Core Flows and utilities expose versioned Order Edit events for subscribers to
react to order-edit lifecycle changes.

### Cart customer-transfer event (2.8.0)

The cart transfer flow emits an event when a cart is transferred to another
customer, allowing subscribers to react to the ownership change.

### Notification addressing and provider data (2.12.0)

Notifications carry `from`, `to`, and provider-data fields. Addressing and
provider-specific context are part of the notification model.

### Priority-based event processing (2.13.0)

Event processing uses numeric priorities; lower numbers run first. Critical
business events such as order placement use priority `10`, ordinary events
default to `100`, and internal system events receive the lowest processing
priority. Override priority at the message, emit, or module level.

### Custom SendGrid notification arguments (2.14.0)

Twilio SendGrid email notifications accept custom arguments, allowing
provider-specific values on outgoing messages.
