# Products, Inventory, and Fulfillment

## Fulfillment-hold authorization and ownership

`node` and `nodes` return `null` for a fulfillment hold outside the app's
fulfillment-order scope. The hold ownership determines the required scope:

| Hold | Required scope |
| --- | --- |
| Merchant-managed | `read_merchant_managed_fulfillment_orders` |
| App-assigned | `read_assigned_fulfillment_orders` |
| Third-party | `read_third_party_fulfillment_orders` |
| Marketplace | `read_marketplace_fulfillment_orders` |

Replace `FulfillmentHold.heldBy` with `heldByApp`. Use `heldByApp.title` for
the former string value.

## Multiple holds and SKU sharing

A fulfillment order can carry multiple independently releasable holds in
`2025-01`.

`fulfillmentServiceCreate` defaults `permitsSkuSharing` to `true`, allowing
stock at multiple fulfillment services or merchant-managed locations unless
the input overrides it.

## Product and shop root-query migrations

These fields moved from `Shop` to `QueryRoot`:

- `collectionSavedSearches`
- `draftOrderSavedSearches`
- `marketingEvents`
- `orderSavedSearches`
- `productByHandle`
- `productSavedSearches`

`uploadedImagesByIds` was replaced by `files`.

`productTags`, `productTypes`, and `productVendors` also moved to root
connections. They use cursor pagination instead of a 250-item cap. Replace
`ShopFeatures.multiLocation` with `locationsCount`.

## Product validation and variant limits

`ProductInput.handle` is checked for uniqueness when supplied.

A single Storefront `product` or `productByHandle` query can request up to
2,000 variants. That limit does not apply when multiple product queries share
a request or when variants are reached through another path.

## REST product-image GraphQL IDs

In REST Admin `2025-01`, `admin_graphql_api_id` for a product image is a
`gid://shopify/MediaImage/...`, not a `gid://shopify/ProductImage/...`.
Migrations should use `medias.id` instead of `medias.legacy_id` or
`product_images.id`. Older API versions retain the old GID.

## Inventory accounting and physical inventory

Draft-order and transfer or shipment inventory is moving from `reserved` to
`committed`. A physical-inventory feature preview is available.

## Inventory-level lifecycle

`inventoryLevels` and `inventoryLevel` accept `includeInactive`.
`InventoryLevel.isActive` exposes the result.

Reactivating a level with `inventoryActivate` now preserves its `available`
quantity.

## Inventory-transfer data

Inventory transfers can have metafield definitions and metafield values.
Their webhooks now include origin and destination location IDs.

## Fulfillment and exchange reads

`OrderDisplayFulfillmentStatus` returns `FULFILLMENT_NOT_REQUIRED` when an
order has nothing to fulfill.

`FulfillmentOrderLineItem.shippingLine` and these `ExchangeLineItem` fields
expose additional fulfillment context:

- `productId`
- `title`
- `variantSku`
- `variantTitle`

## Carrier-service profile behavior

New carrier services are no longer added automatically to the default
shipping profile.

## Collection and product publishing APIs

A new Collection model and APIs require migration attention. Product variants
can be published independently of their product. `CollectionSortOrder` adds
`MOST_RELEVANT`.

## Shipping-label purchase

Shipping labels can be purchased through the GraphQL Admin API.

## Removed inventory error

The `ITEM_NOT_STOCKED_AT_LOCATION` error has been removed.
