# Fulfillment, inventory, shipping, and tax

## Stock locations and shipping setup

### Stock location addresses are one-to-one (2.2.0)

The stock-location-to-address relationship is one-to-one. Apply the
accompanying migration when upgrading:

```sh
npx medusa db:migrate
```

### Shipping profiles are required and fulfillment shipping can be overridden (2.5.0)

Products require a Shipping Profile when created. The upgrade data-migration
script assigns existing products to a profile whose name contains `default`,
case-insensitively, if one exists. Ensure that profile exists when running
`medusa db:migrate`.

`POST /admin/orders/:id/fulfillments` accepts optional `shipping_option_id`,
which replaces the option selected when the order was placed:

```ts
const fulfillment = {
  ...fulfillmentInput,
  shipping_option_id: "so_1234",
}
```

### Backorders without stock locations (2.7.0)

A backorder-enabled variant can be added to a cart even if no stock locations
exist.

### Shipping Option Type management and migration (2.10.0)

Shipping Option Types can be managed through Admin, the API, and the JS SDK and
selected while creating or updating a Shipping Option. The migration removes
placeholder types with code `type-code`, changes their associations to a new
`Default` type with code `default`, and leaves custom types unchanged.

### Shipping Option metadata (2.11.0)

Shipping Option API endpoints expose metadata, allowing integrations to persist
custom values on shipping options.

## Fulfillment and reservations

### Empty fulfillments are rejected (2.6.0)

The dashboard, API, and Core Flows reject fulfillments containing no items.

### Calculated shipping in RMA flows (2.7.0)

Return, claim, and exchange flows support calculated shipping. The Admin RMA
flow can leave shipping unset when no shipping method should apply.

### Inventory-kit fulfillment reservations (2.7.0)

Fulfillment reservation handling supports inventory kits, so the reservation
flow accounts for kit-backed fulfillment.

### Shipment notification suppression in events (2.7.0)

The shipment-created event carries `no_notification`, allowing event consumers
to preserve the caller's notification-suppression choice.

### Inventory-kit fulfillment transitions (2.8.0)

Mark-as-shipped and mark-as-delivered flows handle inventory-kit items, so
kit-backed fulfillments transition correctly through those states.

### Reservation recreation on fulfillment cancellation (2.8.0)

Canceling a fulfillment recreates its inventory reservations, restoring the
allocation for later fulfillment attempts.

### Fulfillment after disabling managed inventory (2.12.0)

A variant changed from managed to unmanaged inventory is fulfillable; the
transition no longer leaves it blocked from fulfillment.

### Reservations during draft-order conversion (2.12.0)

Converting a draft order to a regular order creates its inventory reservations
as part of the conversion flow.

### Fulfillment creator propagation (2.13.0)

Core fulfillment flows forward `created_by` into fulfillment input, making the
initiating actor available to fulfillment creation and related audit logic.

### Delivery workflow notification suppression (2.14.0)

`markOrderFulfillmentAsDeliveredWorkflow` accepts `no_notification`, allowing
delivery marking to preserve the notification-suppression intent already
available to shipment flows.

### Versioned shipping-method adjustments (2.14.0)

Shipping-method adjustments are versioned. Core Flows includes the previously
missing creation path for versioned adjustments.

## Tax behavior

### Tax lines only for regular products (2.7.0)

Cart and order flows assign tax lines only to regular product items instead of
every item type.

### Custom tax providers and region migration (2.8.0)

The Tax Module loads custom tax providers, and Admin can choose or change the
provider assigned to each Tax Region. On the first server start after upgrade,
the migration assigns the default system provider to any region without a
custom provider. Top-level regions also validate their provider.

### Shipping-option-specific tax rates (2.10.0)

Tax Regions can define tax rates for individual Shipping Options independently
of product-specific tax rates.
