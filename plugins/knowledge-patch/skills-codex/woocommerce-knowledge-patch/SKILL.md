---
name: woocommerce-knowledge-patch
description: WooCommerce
version: null
license: MIT
metadata:
  author: Nevaberry
---


# WooCommerce Knowledge Patch

Use this skill for WooCommerce core, extension, payment, subscription, theme,
order, inventory, product-editor, and release-compatibility work.

## How to use this patch

1. Identify whether the work concerns core behavior, an extension security
   update, or a feature compatibility boundary.
2. Read the matching reference file before changing an integration.
3. Apply version-specific guidance only where the item names that version.
4. Preserve `may`, `should`, and `must` conditions when carrying guidance into
   implementation or review.
5. Do not extend a stated compatibility boundary to unrelated capabilities.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core, orders, and admin](references/core-orders-admin.md) | Order-item metadata and removal, failed-order stock, Shop queried objects, shipping classes, product editor |
| [Payments and subscriptions](references/payments-subscriptions.md) | Stripe for WooCommerce, Adaptive Pricing, WooCommerce Subscriptions, PayPal Standard |
| [Features and release policy](references/features-release-policy.md) | Secure core release policy, COGS, MCP beta, Interactivity API Mini-Cart, email previews |

## Breaking core changes

### Reserved order-item metadata

WooCommerce 11.0.0 no longer persists reserved order-item meta keys entered
through the admin's Add meta button.

Admin tooling must use non-reserved keys for custom order-item data.

### Removed order-item lifecycle

WooCommerce 11.0.0 changes when `woocommerce_removed_order_items` runs while
deferring order-item database deletion until `save()`.

Integrations that observe removed items must account for the new save-time
lifecycle.

### Failed-order stock restoration

Starting in WooCommerce 11.0, moving an order to `failed` restores stock that
the order previously reduced.

Custom order and inventory handlers must avoid duplicating that restock.

### Shop queried-object type

In WooCommerce 11.0, `get_queried_object()` on the Shop page returns a
`WP_Post` rather than a `WP_Post_Type`.

Update type checks and property access that assumed the previous object type.

### Product shipping-class visibility

WooCommerce 11.0 makes `product_shipping_class` non-public.

Extensions must not rely on that taxonomy being publicly exposed.

## Deprecations and migrations

### Product editor beta

WooCommerce 10.9 begins the final deprecation window for the product editor
beta. WooCommerce 11.0 removes it, and stores continue with the classic product
editor.

Extensions must not depend on the beta editor remaining available after 11.0.

### PayPal Standard

PayPal Standard is sunsetting.

Plan a migration away from it using the upgrade path available in PayPal
4.1.0.

## Security updates

### Stripe for WooCommerce

Update Stripe for WooCommerce to the latest available release to receive the
August 2026 security update.

### WooCommerce Subscriptions

Update every production and staging site running WooCommerce Subscriptions to
version 9.1.0.

### Stripe Adaptive Pricing

Patched Stripe for WooCommerce releases correct a payment-validation issue
affecting some stores that use Adaptive Pricing.

Those stores should upgrade to a patched release.

### Core release support

The release index marks WooCommerce 11.0.1, released on 2026-08-10, as stable
and says only the latest core version is considered fully secure.

Treat downloadable legacy point releases as packages, not as evidence of a
fully secure supported branch.

## Feature compatibility

### Cost of goods sold and MCP beta

WooCommerce 10.3.0 is where cost of goods sold came to core and MCP entered
beta.

Use 10.3.0 as the compatibility boundary for integrations that depend on
those capabilities.

### Interactivity API Mini-Cart

WooCommerce 10.4.0 is where the Interactivity API Mini-Cart went live.

Test theme and extension compatibility for that Mini-Cart implementation
against 10.4.0 or newer.

### Email previews

WooCommerce 9.8.0 introduced email previews alongside modernized designs.

Use 9.8.0 as the minimum release when relying on the preview workflow.

## Review checklist

### Orders and inventory

- Check admin order-item metadata for reserved keys.
- Check removed-item observers against the save-time lifecycle.
- Check custom failed-order handlers for duplicate restocking.

### Store and product integrations

- Check Shop-page queried-object type assumptions.
- Check extensions for reliance on public `product_shipping_class` exposure.
- Check product-editor dependencies for reliance on the removed beta editor.

### Payments and subscriptions

- Apply the Stripe for WooCommerce security update.
- Apply the WooCommerce Subscriptions 9.1.0 security update to production and
  staging sites.
- Upgrade affected Adaptive Pricing stores to a patched Stripe for
  WooCommerce release.
- Plan the PayPal Standard migration through the PayPal 4.1.0 upgrade path.

### Feature dependencies

- Use 10.3.0 for integrations that depend on core cost of goods sold or the
  MCP beta.
- Test Interactivity API Mini-Cart compatibility against 10.4.0 or newer.
- Require 9.8.0 when relying on email previews.

### Core release assessment

- Do not treat availability of a legacy point-release package as evidence of
  a fully secure supported branch.
- Use the release-index statement that only the latest core version is
  considered fully secure.
