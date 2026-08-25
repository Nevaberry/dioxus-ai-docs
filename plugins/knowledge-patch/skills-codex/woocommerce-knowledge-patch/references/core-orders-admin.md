# Core, Orders, and Admin

## Reserved order-item metadata

WooCommerce 11.0.0 no longer persists reserved order-item meta keys entered
through the admin's Add meta button. Admin tooling must use non-reserved keys
for custom order-item data.

## Removed order-item action timing

WooCommerce 11.0.0 changes the timing of
`woocommerce_removed_order_items` while deferring order-item database deletion
until `save()`. Integrations observing removed items must account for the new
save-time lifecycle.

## Failed-order stock restoration

Starting in WooCommerce 11.0, moving an order to `failed` restores stock that
the order previously reduced. Custom order and inventory handlers must avoid
duplicating that restock.

## Shop queried-object type

In WooCommerce 11.0, `get_queried_object()` on the Shop page returns a
`WP_Post` rather than a `WP_Post_Type`. Update type checks and property access
that assumed the previous object type.

## Product shipping-class taxonomy

WooCommerce 11.0 makes `product_shipping_class` non-public. Extensions must
not rely on that taxonomy being publicly exposed.

## Product editor beta

WooCommerce 10.9 begins the final deprecation window for the product editor
beta, which WooCommerce 11.0 removes. Stores continue with the classic product
editor. Extensions must not depend on the beta editor remaining available
after 11.0.
