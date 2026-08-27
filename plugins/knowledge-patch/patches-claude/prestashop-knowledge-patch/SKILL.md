---
name: prestashop-knowledge-patch
description: PrestaShop
version: null
license: MIT
metadata:
  author: Nevaberry
---


# PrestaShop Knowledge Patch

Use this skill for PrestaShop core, module, theme, Admin API, upgrade,
storefront, checkout, and store-maintenance work.

## How to use this skill

1. Identify whether the task concerns compatibility, storefront behavior,
   administration, integrations, or maintenance.
2. Read the matching topic reference before changing code or planning an
   upgrade.
3. Keep experimental and prerelease features clearly marked in any resulting
   implementation or recommendation.
4. For a major shop upgrade, test existing modules and themes for compatibility.
5. For an Admin API integration, verify that every required resource and
   operation is available.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compatibility, upgrades, and security](references/compatibility-upgrades-and-security.md) | Runtime and build requirements, installation defaults, Update Assistant, packages, security releases |
| [Themes and storefront](references/themes-and-storefront.md) | Hummingbird, media, presenters, SEO, products, search, checkout, orders, shipments, discounts |
| [Admin API, back office, and extensions](references/admin-api-back-office-and-extensions.md) | Admin API coverage, Symfony back office, hooks, module entities, maintenance commands, Extra Properties |

## Breaking and compatibility-sensitive changes

### Test modules and themes before a major upgrade

PrestaShop 9 is based on Symfony 6.4 LTS and supports PHP 8.1 through 8.4.
Existing modules and themes may need compatibility updates because it is a
major release, so test them before upgrading a shop.

### Use the only remaining product page

The new back-office product page is the only product page in PrestaShop 9.
The legacy product page has been removed.

### Resolve the distribution theme dynamically

Fresh PrestaShop 9.1 installations use Hummingbird 2.0 rather than Classic.
Code that needs the distribution default should call
`Theme::getDefaultTheme()` instead of hard-coding `classic`.

Theme activation can unhook modules designated by the theme.

### Account for current toolchain requirements

PrestaShop 9.1 supports PHP 8.1 through 8.5 and requires:

- Composer 2
- Node.js 20
- NPM 10

Core asset builds default to Node.js 20.19.5.

### Treat Admin API coverage as incomplete

The REST/JSON Admin API is built on API Platform, but endpoint coverage remains
a work in progress. Verify each resource and operation an integration needs.

The API later adds a `discountType` endpoint, position-update handling, and
combination-endpoint refinements. Integrations targeting the 9.0 API should
retest these resources against 9.1.

### Plan for changed update behavior

Update Assistant 7.6 supports upgrades from 9.0.x to 9.1. It checks installed
modules against the target and automatically uninstalls modules it finds
incompatible.

Beta and RC1 installations cannot be upgraded to final 9.1 with Update
Assistant; they require a fresh installation.

Regular module upgrades separate download from installation into two steps.

### Apply the security releases

PrestaShop 9.1.5 fixes five security issues and closes the 9.1.x release line
ahead of 9.2. Shops on the 8.2 branch should update to 8.2.8, which fixes five
reported vulnerabilities.

## Common development features

### Build on the Admin API

Use the REST/JSON Admin API for store-management integrations and automation,
subject to checking the required endpoint coverage.

### Add entity fields with Extra Properties

PrestaShop 9.2 introduces native Extra Properties for attaching custom data
fields to any PrestaShop entity without overrides.

The fields support multistore and multilingual data and are available across
the Back Office, Front Office, and Admin API.

### Run store-maintenance tasks from the console

Regenerate thumbnails:

```bash
php bin/console prestashop:thumbnails:regenerate
```

Build the search index:

```bash
php bin/console prestashop:search:index
```

Inspect module-translation export options:

```bash
php bin/console prestashop:module:export-translations --help
```

### Use the Hummingbird theme foundation

The initial Hummingbird foundation is optional in PrestaShop 9. It uses
Bootstrap 5, TypeScript, BEM naming, layered SCSS based on CSS `@layer`, and a
directory layout that moves away from the legacy `_dev` structure.

Bootstrap and PrestaShop-specific styles are separated for overrides.
Bootstrap dark mode can be enabled with an SCSS variable.

### Use standardized front-office presentation

Categories, manufacturers, suppliers, and stores are rendered through
Presenters for a standardized presentation path.

An experimental Symfony container is available in the front office. Modules
using it should treat it as experimental.

### Work with shipment-based order management

Feature flags under **Advanced Parameters > New & Experimental Features**
expose shipment-based order management for non-production testing.

A single order can have shipments split, merged, and switched between
carriers instead of duplicating the order for each carrier. A shipment with a
tracking number cannot be split.

### Work with the experimental discount model

The feature-flagged discount system replaces legacy cart rules with Catalog,
Cart, Free Shipping, and Free Gift discount types.

It supports priorities, validity dates, automatic or promo-code application,
customer and group limits, product-combination selection, and combined
product, category, brand, supplier, country, and attribute conditions.

Customizable products cannot be selected as free gifts.

### Preserve special characters in search

Front-office search queries accept special characters. Custom search
integrations should preserve them rather than assuming core search rejects or
strips them.

### Treat native one-page checkout as prerelease

PrestaShop 9.2 introduces the native `ps_onepagecheckout` module, which puts
the complete checkout flow on one page. It first appears in the 9.2 beta and
should be treated as prerelease functionality until the stable release.

## Operational reminders

- Debug mode can be restricted to users carrying a specific cookie.
- Installation can explicitly use a static database prefix when a
  deterministic prefix is needed.
- Fresh installations otherwise randomize the database table prefix by
  default.
- Direct access to PHP files is protected.
- Ajax controllers are marked `noindex`.
- Product URLs omit the category by default.
- Filtered product-listing pages are excluded from indexing.
- Guest ordering is available even when an account already exists.
- Applying a paid order status registers a payment even when invoicing is
  disabled.
- Order summaries always show the tax total.

Use the topic references for the complete conditions and related behavior.
