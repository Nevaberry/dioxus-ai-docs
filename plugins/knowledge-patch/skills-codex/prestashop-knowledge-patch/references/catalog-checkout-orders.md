# Catalog, Checkout, and Orders

## Product management

The new back-office product page is the only product page in PrestaShop 9.0.0;
the legacy page has been removed.

Product feature values can be sorted manually or automatically.

## Shipment-based order management

Feature flags under **Advanced Parameters > New & Experimental Features**
expose shipment-based order management in 9.1.0 for non-production testing.

A single order can have shipments split, merged, and switched between carriers
instead of duplicating the order for each carrier. A shipment with a tracking
number cannot be split.

## Discount model

The feature-flagged discount system in 9.1.0 replaces legacy cart rules with:

- Catalog discounts
- Cart discounts
- Free Shipping discounts
- Free Gift discounts

It supports:

- priorities and validity dates
- automatic or promo-code application
- customer and group limits
- product-combination selection
- combined product, category, brand, supplier, country, and attribute conditions

Customizable products cannot be selected as free gifts.

## Payment and order summaries

In 9.1.0, applying a paid order status registers a payment even when invoicing
is disabled. Order summaries always show the tax total.

## Countries and free-shipping labels

Cart and order flows reject disabled countries in 9.1.0.

Multistore country lists include only countries covered by active carriers.

Free-shipping labels appear only when a discount actually grants free
shipping.

## Native one-page checkout

PrestaShop 9.2 introduces the native `ps_onepagecheckout` module, which places
the entire checkout flow on a single page.

It first appears in the 9.2 beta and should be treated as prerelease
functionality until the stable release.
