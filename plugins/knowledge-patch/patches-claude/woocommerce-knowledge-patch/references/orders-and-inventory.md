# Orders and Inventory

## Reserved order-item meta in admin tooling

WooCommerce 11.0.0 no longer persists reserved order-item meta keys that are
entered through the admin **Add meta** button.

Use non-reserved keys for custom order-item data added by admin tooling.

## Removed order-item action timing

WooCommerce 11.0.0 changes the timing of
`woocommerce_removed_order_items`. Order-item database deletion is deferred
until `save()`.

Integrations that observe removed items must account for this save-time
lifecycle.

## Stock restoration for failed orders

Starting in WooCommerce 11.0, moving an order to `failed` restores stock that
the order previously reduced.

Custom order and inventory handlers must avoid duplicating that restock.
