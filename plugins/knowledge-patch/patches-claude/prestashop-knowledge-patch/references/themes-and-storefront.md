# Themes and Storefront

## Hummingbird theme foundation

Hummingbird is a new optional theme foundation rather than the PrestaShop 9
default (since 9.0.0). It uses:

- Bootstrap 5;
- TypeScript;
- BEM naming;
- a directory layout that moves away from the legacy `_dev` structure;
- layered SCSS based on CSS `@layer`.

Bootstrap and PrestaShop-specific styles are separated for overrides.
Bootstrap dark mode can be enabled with an SCSS variable.

## Hummingbird as the distribution default

Fresh PrestaShop 9.1 installations use Hummingbird 2.0 instead of Classic
(since 9.1.0). Code that needs the distribution default can call
`Theme::getDefaultTheme()` rather than hard-coding `classic`.

Theme activation can unhook modules designated by the theme.

## Storefront media and cart notices

The front office supports WebP and AVIF natively (since 9.0.0). It can notify
a visitor when the viewed product is already in their cart, and it allows
guest ordering even when an account already exists.

Product breadcrumbs follow the category through which the product was
accessed.

## Front-office presentation services

Categories, manufacturers, suppliers, and stores are rendered through
Presenters for a standardized presentation path (since 9.0.0).

An experimental Symfony container is available in the front office. Modules
using it should treat it as experimental.

## SEO and URL defaults

Product URLs omit the category by default (since 9.0.0). Shops can remove the
default-language prefix to avoid redirects when another language is added.

Inactive categories can issue either 301 or 302 redirects. Filtered
product-listing pages are excluded from indexing.

## Product management

The new back-office product page is the only product page; the legacy page has
been removed (since 9.0.0). Product feature values can be sorted manually or
automatically.

## Shipment-based order management

Feature flags under **Advanced Parameters > New & Experimental Features**
expose shipment-based order management for non-production testing (since
9.1.0).

A single order can have shipments split, merged, and switched between
carriers instead of duplicating the order for each carrier. A shipment with a
tracking number cannot be split.

## Experimental discount model

The feature-flagged discount system replaces legacy cart rules with Catalog,
Cart, Free Shipping, and Free Gift discount types (since 9.1.0).

It supports:

- priorities and validity dates;
- automatic or promo-code application;
- customer and group limits;
- product-combination selection;
- combined product, category, brand, supplier, country, and attribute
  conditions.

Customizable products cannot be selected as free gifts.

## Checkout and order behavior

Applying a paid order status registers a payment even when invoicing is
disabled (since 9.1.0). Order summaries always show the tax total.

Cart and order flows reject disabled countries. Multistore country lists
include only countries covered by active carriers. Free-shipping labels appear
only when a discount actually grants free shipping.

## Front-office search

Search queries accept special characters (since 9.1.0). Custom search
integrations should preserve them rather than assuming core search rejects or
strips them.

## Native one-page checkout

PrestaShop 9.2 introduces the native `ps_onepagecheckout` module, which places
the entire checkout flow on a single page. It first appears in the 9.2 beta
and should be treated as prerelease functionality until the stable release.
