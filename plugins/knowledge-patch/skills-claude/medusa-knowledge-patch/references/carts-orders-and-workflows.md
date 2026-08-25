# Carts, orders, and workflows

## Carts and line items

### Cart credit lines (since 2.6.0)

The Cart Module, cart types, and Core Flows now support credit lines on carts.

### Line-item title and subtitle sources (since 2.8.0)

Generated line items now take their title from the product and their subtitle from the variant, reversing the previous sources. Storefronts and integrations that display or interpret these fields must account for the breaking change.

### Pre-operation cart validation hooks (since 2.3.0)

Every cart workflow now exposes a `validate` hook that runs before its operation, allowing custom business rules to abort the workflow. For example, cart completion can require prior approval:

```ts
import { completeCartWorkflow } from "@medusajs/medusa/core-flows"

completeCartWorkflow.hooks.validate(({ cart }) => {
  if (!cart.metadata.approved_at) {
    throw new Error("Cannot complete unapproved cart")
  }
})
```

### Published-only cart additions (since 2.11.0)

`addToCartWorkflow` now permits only published products, so attempts to add unpublished products no longer proceed through the core flow.

### Workflow idempotency retention and cart serialization (since 2.10.0)

Setting a workflow as `idempotent` now prevents concurrent execution only while it is running; completed executions are no longer retained indefinitely unless a retention time is configured. All cart workflows are now idempotent, so concurrent cart mutations are serialized.

## Orders, edits, and exchanges

### Completed orders cannot be canceled (since 2.14.0)

Order cancellation now rejects completed orders. Integrations must stop offering or attempting cancellation after an order reaches completion.

### Custom order display IDs (since 2.12.0)

Orders now expose `custom_display_id` while the existing auto-incrementing integer `display_id` remains unchanged. Configure the Order Module's `generateCustomDisplayId` option to generate the new value during order creation; its callback receives an `OrderTypes.CreateOrderDTO` and a `Context`. Enabling View Configurations makes the field available for customization on the Admin order table.

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

### Customer transfers can update the order email (since 2.14.0)

Order customer-transfer requests can now update the original `order.email`, allowing the transferred order's contact email to follow the new customer when requested.

### Draft Orders are enabled by default (since 2.10.0)

The Draft Order plugin is installed by default from 2.10.0 and adds Admin flows for creating, editing, and finalizing draft orders with custom prices, line items, and shipping methods. Versions 2.4.0 through 2.9.x can use the plugin only after explicit installation and registration.

### Exported order utility workflows (since 2.8.0)

Order-related utility workflows are now exported from Core Flows for reuse in custom workflows.

### Order adjustment version migration (since 2.12.0)

The release migrations add a `version` column to order line-item adjustments, and the accompanying data migration sets each adjustment to the latest version of its associated order. Apply migrations after installing the release:

```sh
npx medusa db:migrate
```

### Order item-change metadata and matching (since 2.14.0)

An `item_update` change action now updates item metadata. When multiple order items reference one variant, line-action resolution also considers price and metadata rather than matching only by variant.

### Order-return workflow result (since 2.6.0)

The order-return workflow now returns the created order return, allowing callers to consume it directly from the workflow result.

### Product-update ordering regression (since 2.8.0)

Version 2.8.0 can return products from the Product Module service in an inconsistent order, breaking workflows such as `updateProductsWorkflow` when later operations apply data such as price updates positionally. Upgrade to 2.8.1 as soon as possible instead of remaining on 2.8.0.

## Workflow composition

### Automatic workflow-execution retention cleanup (since 2.5.0)

The workflow engine now runs an hourly job that deletes stale executions after their configured retention time and persists that value in a new `workflow_execution.retention_time` column. Retention is expressed in seconds; existing values mistakenly configured in milliseconds can make the migration fail with a PostgreSQL integer-cast error and must be corrected when running the migration manually.

### Workflow step results through context (since 2.7.0)

Workflow implementations can now access step results through the workflow context, providing another way for extension logic to consume results produced elsewhere in the workflow.
