# Catalog, Inventory, and Fulfillment

## Fulfillment-hold authorization

`node` and `nodes` return `null` for a fulfillment hold outside the app's
fulfillment-order scope. The required scopes are:

| Hold ownership | Scope |
| --- | --- |
| Merchant-managed | `read_merchant_managed_fulfillment_orders` |
| App-assigned | `read_assigned_fulfillment_orders` |
| Third-party | `read_third_party_fulfillment_orders` |
| Marketplace | `read_marketplace_fulfillment_orders` |

Replace `FulfillmentHold.heldBy` with `heldByApp`, or with `heldByApp.title` for the
former string value.

## Multiple holds and SKU sharing

In `2025-01`, a fulfillment order can carry multiple independently releasable holds.

`fulfillmentServiceCreate` defaults `permitsSkuSharing` to `true`, allowing stock at
multiple fulfillment services or merchant-managed locations unless the input
overrides it.

## Root-query migrations

The following moved from `Shop` to `QueryRoot`:

- `collectionSavedSearches`
- `draftOrderSavedSearches`
- `marketingEvents`
- `orderSavedSearches`
- `productByHandle`
- `productSavedSearches`

`uploadedImagesByIds` was replaced by `files`.

`productTags`, `productTypes`, and `productVendors` moved to root connections with
cursor pagination instead of a 250-item cap. Replace `ShopFeatures.multiLocation`
with `locationsCount`.

## Product handle and variant limits

`ProductInput.handle` is checked for uniqueness when supplied.

A single Storefront `product` or `productByHandle` query can request up to 2,000
variants. This limit does not apply when multiple product queries share one request
or when variants are reached through another path.

## Bundle representations

Use `AbandonedCheckoutLineItem.components` and Customer API `LineItem.group` to
render bundle components beneath their parent. Order-create webhooks identify bundled
line items with `sales_line_item_group_id`.

## REST product-image GraphQL IDs

In REST Admin `2025-01`, a product image's `admin_graphql_api_id` is a
`gid://shopify/MediaImage/...`, not a `gid://shopify/ProductImage/...`.

Use `medias.id` for migrations rather than `medias.legacy_id` or
`product_images.id`. Older API versions retain the old GID.

## Inventory accounting and physical inventory

Draft-order and transfer/shipment inventory is moving from `reserved` to `committed`.
A physical-inventory feature preview is available.

## Inventory-level lifecycle

`inventoryLevels` and `inventoryLevel` accept `includeInactive`, and
`InventoryLevel.isActive` exposes the result. Reactivating a level with
`inventoryActivate` preserves its `available` quantity.

## Fulfillment and exchange reads

`OrderDisplayFulfillmentStatus` returns `FULFILLMENT_NOT_REQUIRED` when an order has
nothing to fulfill. `FulfillmentOrderLineItem.shippingLine` provides additional
fulfillment context.

`ExchangeLineItem` exposes `productId`, `title`, `variantSku`, and `variantTitle`.

## Collection and product publishing

A new Collection model and APIs require migration attention. Product variants can be
published independently of their product, and `CollectionSortOrder` adds
`MOST_RELEVANT`.

## Removed inventory error

The `ITEM_NOT_STOCKED_AT_LOCATION` error has been removed.
