# Apps, webhooks, and telemetry

## OpenTelemetry integration (3.21.0)

Custom deployments must move from the old OpenTracing integration to an
OpenTelemetry-capable collector. Saleor can emit metrics and OTLP traces with
W3C Trace Context. A public telemetry stream omits codebase-oriented details
such as individual SQL queries.

## Opt-in synchronous-webhook circuit breaker (3.21.0)

The circuit breaker temporarily shuts down an app after its synchronous
webhooks cross an error threshold, preventing its failures from clogging the
stack. It is disabled by default. Its dry-run setup monitors events without
blocking before blocking is selectively enabled.

## Strong synchronous-webhook response validation (3.21.0)

Saleor checks response types, string lengths, and numeric ranges for these
synchronous webhooks:

- Shipping: `CHECKOUT_FILTER_SHIPPING_METHODS`,
  `ORDER_FILTER_SHIPPING_METHODS`, and
  `SHIPPING_LIST_METHODS_FOR_CHECKOUT`.
- Tax: `CHECKOUT_CALCULATE_TAXES` and `ORDER_CALCULATE_TAXES`.
- Payment and transaction: `LIST_STORED_PAYMENT_METHODS`,
  `PAYMENT_GATEWAY_INITIALIZE_SESSION`, `TRANSACTION_INITIALIZE_SESSION`,
  `TRANSACTION_PROCESS_SESSION`, `TRANSACTION_CHARGE_REQUESTED`,
  `TRANSACTION_CANCEL_REQUESTED`, and `TRANSACTION_REFUND_REQUESTED`.

Invalid shipping responses are logged and ignored. Invalid tax or payment
responses are recorded in fields such as `Checkout.tax_error`,
`Order.tax_error`, or `TransactionEvent.message`, and stop checkout or order
processing.

## No-op mutation webhook suppression (3.21.0)

`draftOrderUpdate` and `orderUpdate` do not emit update webhooks when nothing
changed. `CHECKOUT_FILTER_SHIPPING_METHODS` and
`ORDER_FILTER_SHIPPING_METHODS` are skipped when a related mutation produces
no available-method change, such as when no shipping address exists.

## Dashboard extension targets (3.22.0)

Dashboard extensions can use `NEW_TAB` to open in a browser tab or `WIDGET` to
embed an iframe in a Dashboard page. Mounting points cover categories,
collections, gift cards, draft orders, discounts, vouchers, models, and other
Dashboard areas.

## Published synchronous-webhook schemas (3.22.0)

The JSON Schemas used to validate synchronous webhooks are available from
`saleor/json_schemas.py`. Apps can validate payloads against the same
contracts as Saleor.

## Deactivated app delivery (3.22.0)

Webhook delivery is suppressed for deactivated apps. Integrations must not
expect asynchronous or synchronous webhook handling after deactivation.

## App extension and installation contracts (3.23.0)

`AppExtension` and `AppManifestExtension` replace `options`, `mount`, and
`target` with `settings`, `mountName`, and `targetName`. Manifests may still
provide string `mount` and `target` plus JSON `options`; Dashboard, rather than
Saleor, validates their contract. Apps may omit `tokenTargetUrl`, but
`appInstall` still requires `appName` and `manifestUrl`.

## Async order events and synchronous hooks (3.23.0)

Preparing asynchronous order, draft-order, or fulfillment events does not
invoke synchronous hooks such as `ORDER_CALCULATE_TAXES` or
`ORDER_FILTER_SHIPPING_METHODS`. Those hooks run only when their data is
actually requested. Integrations must not depend on an async event causing
those synchronous side effects.

## GraphQL field usage metric (3.23.0)

The `saleor.graphql.field.usage` OpenTelemetry metric counts resolver calls for
deprecated fields and custom fields declared with `monitor_usage=True`.
Operators can measure clients before removing or migrating fields.

## Product type lifecycle webhooks

> **Prerelease (`upcoming-3.24`):** This guidance may change before stable release.

Apps can subscribe to `PRODUCT_TYPE_CREATED`, `PRODUCT_TYPE_UPDATED`, and
`PRODUCT_TYPE_DELETED`. They are emitted when a product type is created,
updated, or deleted.
