# Core and Storefront

## Core release security status

The release index marks WooCommerce 11.0.1, released on 2026-08-10, as the
stable release. It says that only the latest core version is considered fully
secure.

Legacy point releases remain downloadable as packages. Their availability is
not evidence of a fully secure supported branch.

## Product editor compatibility

WooCommerce 10.9 starts the final deprecation window for the product editor
beta. WooCommerce 11.0 removes that beta editor, with stores continuing to use
the classic product editor.

Extensions must not depend on the beta editor remaining available after
WooCommerce 11.0.

## Shop page queried object

On the Shop page in WooCommerce 11.0, `get_queried_object()` returns a
`WP_Post`. It previously returned a `WP_Post_Type`.

Update type checks and property access that assumed the previous object type.

## Product shipping-class taxonomy

WooCommerce 11.0 makes `product_shipping_class` a non-public taxonomy.

Extensions must not depend on public exposure of that taxonomy.

## Core cost of goods sold and MCP beta

WooCommerce 10.3.0 brought cost of goods sold to core and put MCP into beta.

Use WooCommerce 10.3.0 as the compatibility boundary for integrations that
depend on those capabilities.

## Interactivity API Mini-Cart

The Interactivity API Mini-Cart went live in WooCommerce 10.4.0.

Test theme and extension compatibility for that Mini-Cart implementation
against WooCommerce 10.4.0 or newer.

## Email preview workflow

WooCommerce 9.8.0 introduced email previews alongside modernized designs.

Use WooCommerce 9.8.0 as the minimum release when relying on the preview
workflow.
