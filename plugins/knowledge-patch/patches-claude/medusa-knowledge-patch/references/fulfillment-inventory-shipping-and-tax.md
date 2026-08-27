# Fulfillment, inventory, shipping, and tax

## Fulfillment

### Empty fulfillments are rejected (since 2.6.0)

The dashboard, API, and Core Flows now prevent creation of fulfillments that contain no items.

### Fulfillment creator propagation (since 2.13.0)

Core fulfillment flows now forward `created_by` into the fulfillment input, making the initiating actor available to fulfillment creation and related audit logic.

## Inventory and reservations

### Backorders without stock locations (since 2.7.0)

A backorder-enabled variant can now be added to a cart even when no stock locations exist.

### Fulfillment after disabling managed inventory (since 2.12.0)

A variant changed from managed inventory to unmanaged inventory is now fulfillable, so that transition no longer leaves the variant blocked from fulfillment.

### Inventory location-level batch request rename (since 2.3.0)

`POST /admin/inventory-items/:id/location-levels/batch` now accepts singular `create` and `delete` properties instead of `creates` and `deletes`, and adds `update`. Existing clients must change their request bodies:

```http
POST /admin/inventory-items/:id/location-levels/batch
Content-Type: application/json

{"create":[],"update":[],"delete":[]}
```

### Inventory-kit fulfillment reservations (since 2.7.0)

Fulfillment reservation handling now supports inventory kits, so kit-backed fulfillment is accounted for by the reservation flow.

### Inventory-kit fulfillment transitions (since 2.8.0)

The mark-as-shipped and mark-as-delivered flows now handle inventory-kit items, so kit-backed fulfillments transition correctly through those states.

### Missing variant inventory is nullable (since 2.11.0)

In `GET /store/products`, a variant whose sales-channel locations have no inventory levels now returns `inventory_quantity: null` instead of `0`. Storefronts must distinguish missing inventory data from a known zero quantity.

### Product workflow inventory input typing (since 2.3.0)

The `createProductsWorkflow` input type now includes `inventory_items`, allowing TypeScript callers to supply inventory-item data without casts or type overrides.

### Reservation recreation on fulfillment cancellation (since 2.8.0)

Canceling a fulfillment now recreates its inventory reservations, restoring the allocation for subsequent fulfillment attempts.

### Reservations during draft-order conversion (since 2.12.0)

Converting a draft order to a regular order now creates its inventory reservations as part of the conversion flow.

### Stock location addresses are one-to-one (since 2.2.0)

The stock-location-to-address relationship changed to one-to-one. Upgrades must apply the accompanying migration:

```sh
npx medusa db:migrate
```

### Stock-location creation hook (since 2.6.0)

`createStockLocationsWorkflow` now exposes a hook for extending stock-location creation.

### Stock-location metadata in Admin (since 2.14.0)

Admin now provides a metadata form for Stock Locations, allowing operators to view and edit their custom metadata from the dashboard.

## Shipping and delivery

### Calculated shipping in RMA flows (since 2.7.0)

Return, claim, and exchange flows now support calculated shipping, and the Admin RMA flow can leave shipping unset when no shipping method should be applied.

### Delivery marking no longer takes a request body (since 2.4.0)

The Admin JS SDK and request types no longer require the redundant body when marking a fulfillment as delivered. Callers written for the previous signature should omit that payload.

### Shipping Option metadata (since 2.11.0)

Shipping Option API endpoints now expose metadata, allowing integrations to persist custom values on shipping options.

### Shipping Option Type cardinality change (since 2.12.0)

The Shipping Option-to-Shipping Option Type relationship changed from one-to-one to many-to-one, and the related property was renamed. This is a breaking schema change for custom code that uses the relation and is applied by the release migrations.

### Shipping Option Type management and migration (since 2.10.0)

Shipping Option Types can now be managed through Admin, the API, and the JS SDK, and selected when creating or updating a Shipping Option. The migration removes placeholder types with code `type-code`, replaces their associations with a new `Default` type whose code is `default`, and leaves custom types unchanged.

### Shipping profiles are required and fulfillment shipping can be overridden (since 2.5.0)

Products now require a Shipping Profile when they are created. The upgrade data-migration script assigns existing products to a profile whose name contains `default` case-insensitively, if one exists, so that profile should be in place when running `medusa db:migrate`.

`POST /admin/orders/:id/fulfillments` accepts an optional `shipping_option_id` that replaces the option selected when the order was placed:

```ts
const fulfillment = {
  ...fulfillmentInput,
  shipping_option_id: "so_1234",
}
```

### Versioned shipping-method adjustments (since 2.14.0)

Shipping-method adjustments are now versioned, and Core Flows includes the previously missing creation path for versioned adjustments.

## Tax

### Custom tax providers and region migration (since 2.8.0)

The Tax Module now loads custom tax providers, and Admin can choose or change the provider assigned to each Tax Region. On the first server start after upgrade, the migration assigns the default system provider to every region that does not already specify a custom provider; top-level regions also validate their provider.

### Shipping-option-specific tax rates (since 2.10.0)

Tax Regions can now define tax rates for individual Shipping Options, independently of product-specific tax rates.

### Tax lines only for regular products (since 2.7.0)

Cart and order flows now assign tax lines only to regular product items, rather than applying them to every item type.
