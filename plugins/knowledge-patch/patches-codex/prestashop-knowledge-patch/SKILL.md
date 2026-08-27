---
name: prestashop-knowledge-patch
description: PrestaShop
version: null
license: MIT
metadata:
  author: Nevaberry
---


# PrestaShop Knowledge Patch

Use this skill when upgrading PrestaShop, developing modules or themes,
integrating the Admin API, or checking current storefront and order behavior.
Start with the quick references below, then open the task-specific reference for
the complete guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [platform-upgrades-security.md](references/platform-upgrades-security.md) | Runtime and build requirements, Update Assistant, installation and debugging security, maintenance releases, distribution packages |
| [themes-storefront-seo.md](references/themes-storefront-seo.md) | Hummingbird, front-office presentation services, media, search, URLs, redirects, and indexing |
| [admin-api-extensions.md](references/admin-api-extensions.md) | Admin API, Symfony-rendered back office, hooks, module entities, and Extra Properties |
| [catalog-checkout-orders.md](references/catalog-checkout-orders.md) | Product management, experimental discounts and shipments, checkout, payments, countries, and one-page checkout |

## Breaking changes and upgrade checks

### Theme default changed

Fresh PrestaShop 9.1 installations use Hummingbird 2.0 instead of Classic.
Code that needs the distribution default should call:

```php
Theme::getDefaultTheme()
```

Do not hard-code `classic` for that purpose. Theme activation can also unhook
modules designated by the theme.

### Legacy product page removed

In PrestaShop 9.0.0, the new back-office product page is the only product page;
the legacy page has been removed.

### Major-version compatibility

PrestaShop 9 is based on Symfony 6.4 LTS. Because it is a major release,
existing modules and themes may need compatibility updates and should be tested
before a shop upgrade.

### Runtime and build matrix

| Context | Requirements |
| --- | --- |
| PrestaShop 9.0.0 | PHP 8.1 through 8.4 |
| PrestaShop 9.1.0 | PHP 8.1 through 8.5; Composer 2; Node.js 20; NPM 10 |
| 9.1 core assets | Node.js 20.19.5 by default |

### Upgrade-path constraints

Update Assistant 7.6 supports upgrades from 9.0.x to 9.1. It checks installed
modules against the target version and automatically uninstalls modules it
finds incompatible.

Beta and RC1 installations cannot be upgraded to final 9.1 with Update
Assistant; they require a fresh installation.

Regular module upgrades separate download from installation into two steps in
9.1.0.

## Experimental and prerelease functionality

### Shipment-based order management

Feature flags under **Advanced Parameters > New & Experimental Features**
expose shipment-based order management for non-production testing in 9.1.0.
A single order can have shipments split, merged, and switched between carriers
instead of duplicating the order for each carrier. A shipment with a tracking
number cannot be split.

### Discount model

The feature-flagged 9.1.0 discount system replaces legacy cart rules with four
discount types:

- Catalog
- Cart
- Free Shipping
- Free Gift

It supports priorities, validity dates, automatic or promo-code application,
customer and group limits, product-combination selection, and combined product,
category, brand, supplier, country, and attribute conditions. Customizable
products cannot be selected as free gifts.

### Front-office container

An experimental Symfony container is available in the front office as of
9.0.0. Modules using it should treat it as experimental.

### Native one-page checkout

PrestaShop 9.2 introduces the native `ps_onepagecheckout` module, placing the
entire checkout flow on one page. It first appears in the 9.2 beta and should
be treated as prerelease functionality until the stable release.

## Admin API checks

PrestaShop 9.0.0 introduces a REST/JSON Admin API built on API Platform for
store-management integrations and automation. Endpoint coverage is still a
work in progress, so integrations must verify that every required resource and
operation is available.

In 9.1.0, the Admin API adds a `discountType` endpoint, position-update
handling, and refinements to combination endpoints. Integrations targeting the
9.0 API should retest these resources against 9.1.

## Theme migration snapshot

Hummingbird in 9.0.0 is optional rather than the default. Its foundation uses:

- Bootstrap 5
- TypeScript
- BEM naming
- a directory layout that moves away from the legacy `_dev` structure
- layered SCSS based on CSS `@layer`

Bootstrap and PrestaShop-specific styles are separated for overrides.
Bootstrap dark mode can be enabled with an SCSS variable.

## Storefront behavior to preserve

PrestaShop 9.0.0 adds native WebP and AVIF support, an option to notify a
visitor when the viewed product is already in their cart, and guest ordering
even when an account already exists. Product breadcrumbs follow the category
through which the product was accessed.

Search queries accept special characters in 9.1.0. Custom search integrations
should preserve them instead of assuming core search rejects or strips them.

Product URLs omit the category by default in 9.0.0. Shops can remove the
default-language prefix to avoid redirects when another language is added.
Inactive categories can issue either 301 or 302 redirects, and filtered
product-listing pages are excluded from indexing.

## Extension quick reference

PrestaShop 9.1.0 adds `actionUpdateDefaultCombinationAfter` and hooks around:

- module enable, disable, and upgrade events
- `Configuration::updateValue`
- free-shipping price calculation
- front-office country or currency selection

Doctrine auto-mapping for modules recognizes every subfolder under
`src/Entity`, rather than only the first one.

PrestaShop 9.2 introduces native Extra Properties. They attach custom data
fields to any PrestaShop entity without overrides, support multistore and
multilingual data, and are available across the Back Office, Front Office, and
Admin API.

## Maintenance CLI

PrestaShop 9.1.0 provides console commands for thumbnail regeneration, search
indexing, and module-translation export:

```bash
php bin/console prestashop:thumbnails:regenerate
php bin/console prestashop:search:index
php bin/console prestashop:module:export-translations --help
```

## Security and maintenance snapshot

PrestaShop 9.1.0 fixes stored XSS in back-office templates
(`GHSA-35pf-37c6-jxjv`), improper use of the validation framework
(`GHSA-283w-xf3q-788v`), and exposure of sensitive product attributes in the
front office. Ajax controllers are marked `noindex` to keep internal endpoints
out of search indexes.

PrestaShop 9.1.5 fixes five security issues and closes the 9.1.x release line
ahead of 9.2. Shops remaining on the 8.2 branch should update to 8.2.8, which
fixes five reported vulnerabilities.
