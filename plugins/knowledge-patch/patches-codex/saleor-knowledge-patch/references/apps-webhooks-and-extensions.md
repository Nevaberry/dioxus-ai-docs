# Apps, Webhooks, and Extensions

## Synchronous webhooks have an opt-in circuit breaker

Since 3.21.0, the circuit breaker can temporarily shut down an app after its
synchronous webhooks cross an error threshold, preventing its failures from
clogging the stack. It is disabled by default. Dry-run setup can monitor events
without blocking before blocking is enabled selectively.

## Synchronous webhook responses are strongly validated

Since 3.21.0, Saleor validates response types, string lengths, and numeric
ranges for these shipping webhooks:

- `CHECKOUT_FILTER_SHIPPING_METHODS`
- `ORDER_FILTER_SHIPPING_METHODS`
- `SHIPPING_LIST_METHODS_FOR_CHECKOUT`

It applies the same validation to tax webhooks `CHECKOUT_CALCULATE_TAXES` and
`ORDER_CALCULATE_TAXES`, and to these payment and transaction webhooks:

- `LIST_STORED_PAYMENT_METHODS`
- `PAYMENT_GATEWAY_INITIALIZE_SESSION`
- `TRANSACTION_INITIALIZE_SESSION`
- `TRANSACTION_PROCESS_SESSION`
- `TRANSACTION_CHARGE_REQUESTED`
- `TRANSACTION_CANCEL_REQUESTED`
- `TRANSACTION_REFUND_REQUESTED`

Invalid shipping responses are logged and ignored. Invalid tax or payment
responses are recorded in fields such as `Checkout.tax_error`,
`Order.tax_error`, or `TransactionEvent.message` and stop checkout or order
processing.

## Legacy plugin-manager hooks are removed

Since 3.21.0, plugin-manager methods `perform_mutation` and
`change_user_address` are removed.

## Checkout subscriptions are filterable

Since 3.21.0, filterable subscriptions are available for `checkoutCreated`,
`checkoutUpdated`, `checkoutFullyPaid`, and `checkoutMetadataUpdated`.

## Variant metadata updates emit both events

Since 3.21.0, updating variant metadata emits both
`PRODUCT_VARIANT_METADATA_UPDATED` and `PRODUCT_VARIANT_UPDATED` when those
events are subscribed.

## Extensions support tabs, widgets, and more mounting points

Since 3.22.0, Dashboard extensions can use `NEW_TAB` to open in a new browser
tab or `WIDGET` to embed an iframe in a Dashboard page. New mounting points
cover categories, collections, gift cards, draft orders, discounts, vouchers,
models, and other Dashboard areas.

## Synchronous webhook schemas ship with Saleor

Since 3.22.0, the JSON Schemas used for synchronous-webhook validation are
available from `saleor/json_schemas.py`. Apps can validate payloads against the
same contracts as Saleor.

## Deactivated apps receive no webhooks

Since 3.22.0, webhook delivery is suppressed for deactivated apps.
Integrations must not expect asynchronous or synchronous webhook handling to
continue after deactivation.

## App extension and installation contracts change

Since 3.23.0, `AppExtension` and `AppManifestExtension` remove `options`,
`mount`, and `target` in favor of `settings`, `mountName`, and `targetName`.
Manifests may still supply string `mount`/`target` and JSON `options`, with
Dashboard rather than Saleor validating their contract. Apps may omit
`tokenTargetUrl`, but `appInstall` still requires `appName` and `manifestUrl`.

## Async order events do not pre-fire synchronous webhooks

Since 3.23.0, preparing asynchronous order, draft-order, or fulfillment events
does not invoke synchronous hooks such as `ORDER_CALCULATE_TAXES` or
`ORDER_FILTER_SHIPPING_METHODS`. Those hooks run only when their data is
actually requested. Integrations must not depend on async events for those
synchronous side effects.

## Product type lifecycle webhooks are available

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Apps can subscribe to `PRODUCT_TYPE_CREATED`, `PRODUCT_TYPE_UPDATED`, and
`PRODUCT_TYPE_DELETED`, emitted when a product type is created, updated, or
deleted.
