---
name: woocommerce-knowledge-patch
description: WooCommerce
version: null
license: MIT
metadata:
  author: Nevaberry
---


# WooCommerce Knowledge Patch

Use this skill for WooCommerce work involving core compatibility, order and
inventory integrations, storefront extensions, or the named payment and
subscription extensions below.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core and storefront](references/core-and-storefront.md) | Core security status, product editing, Shop page queries, shipping classes, Mini-Cart, COGS, MCP, and email previews |
| [Orders and inventory](references/orders-and-inventory.md) | Reserved order-item meta, removed-item timing, and stock restoration for failed orders |
| [Payments and subscriptions](references/payments-and-subscriptions.md) | Stripe for WooCommerce, Adaptive Pricing, WooCommerce Subscriptions, and PayPal Standard |

## Security and upgrade priorities

### WooCommerce core

The release index marks WooCommerce 11.0.1, released on 2026-08-10, as
stable. Only the latest core version is considered fully secure.

Do not treat downloadable legacy point-release packages as evidence that a
fully secure supported branch exists.

### Stripe for WooCommerce

Update Stripe for WooCommerce to the latest available release to receive the
August 2026 security update.

Patched Stripe for WooCommerce releases also correct a payment-validation
issue that affects some stores using Adaptive Pricing. Upgrade affected stores
to a patched release.

### WooCommerce Subscriptions

Update every production and staging site that runs WooCommerce Subscriptions
to version 9.1.0.

### PayPal Standard

PayPal Standard is sunsetting. Plan a migration away from it using the upgrade
path available in PayPal 4.1.0.

## WooCommerce 11.0 integration changes

### Reserved order-item meta in the admin

WooCommerce 11.0.0 no longer persists reserved order-item meta keys entered
through the admin **Add meta** button.

Admin tooling must use non-reserved keys for custom order-item data.

### Removed order-item lifecycle

WooCommerce 11.0.0 changes when `woocommerce_removed_order_items` runs while
deferring order-item database deletion until `save()`.

Integrations that observe removed items must account for the new save-time
lifecycle.

### Failed-order stock restoration

Starting in WooCommerce 11.0, moving an order to `failed` restores stock that
the order previously reduced.

Custom order and inventory handlers must not duplicate that restock.

### Shop page queried object

In WooCommerce 11.0, `get_queried_object()` on the Shop page returns a
`WP_Post` rather than a `WP_Post_Type`.

Update type checks and property access that assumed the previous object type.

### Product shipping classes

WooCommerce 11.0 makes the `product_shipping_class` taxonomy non-public.

Extensions must not rely on that taxonomy being publicly exposed.

### Product editor beta removal

WooCommerce 10.9 begins the final deprecation window for the product editor
beta. The beta editor is removed in 11.0, and stores continue with the classic
product editor.

Extensions must not depend on the beta editor remaining available after 11.0.

## Capability boundaries

### Core COGS and MCP beta

WooCommerce 10.3.0 is the release where cost of goods sold came to core and
MCP entered beta.

Use 10.3.0 as the compatibility boundary for integrations that depend on
those capabilities.

### Interactivity API Mini-Cart

WooCommerce 10.4.0 is the release where the Interactivity API Mini-Cart went
live.

Test theme and extension compatibility for that Mini-Cart implementation
against 10.4.0 or newer.

### Email previews

WooCommerce 9.8.0 introduced email previews alongside modernized designs.

Use 9.8.0 as the minimum release when relying on the preview workflow.

## Compatibility checklist

### Core and store administration

- Treat only the latest WooCommerce core version as fully secure.
- Treat legacy point releases as downloadable packages, not proof of a fully
  secure supported branch.
- Use non-reserved keys when admin tooling adds custom order-item data.
- Do not depend on the product editor beta after WooCommerce 11.0.

### Order and inventory integrations

- Account for the save-time lifecycle around
  `woocommerce_removed_order_items` and deferred database deletion.
- Do not restock a second time when moving a stock-reducing order to `failed`
  under WooCommerce 11.0 or newer.

### Themes and extensions

- Expect a `WP_Post` from `get_queried_object()` on the Shop page under
  WooCommerce 11.0.
- Do not rely on public exposure of the `product_shipping_class` taxonomy
  under WooCommerce 11.0.
- Test Interactivity API Mini-Cart compatibility against WooCommerce 10.4.0
  or newer.

### Capability-dependent integrations

- Use WooCommerce 10.3.0 as the boundary for core cost of goods sold and the
  MCP beta.
- Require WooCommerce 9.8.0 when relying on the email preview workflow.

### Payment and subscription extensions

- Update Stripe for WooCommerce to the latest available release for the
  August 2026 security update.
- Upgrade affected Adaptive Pricing stores to a Stripe for WooCommerce
  release containing the payment-validation patch.
- Update WooCommerce Subscriptions to 9.1.0 on production and staging sites.
- Plan migration away from PayPal Standard through the path in PayPal 4.1.0.

## Applying this guidance

Use the reference that matches the component being changed:

1. For WooCommerce core, theme, or storefront compatibility, read
   [Core and storefront](references/core-and-storefront.md).
2. For order storage, hooks, or inventory behavior, read
   [Orders and inventory](references/orders-and-inventory.md).
3. For the named payment and subscription extensions, read
   [Payments and subscriptions](references/payments-and-subscriptions.md).
