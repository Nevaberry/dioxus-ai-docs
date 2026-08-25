# Admin API, Back Office, and Extensions

## REST/JSON Admin API

PrestaShop introduces a REST/JSON Admin API built on API Platform for
store-management integrations and automation (since 9.0.0). Endpoint coverage
is still a work in progress, so integrations must verify that each required
resource and operation is available.

## Admin API additions

The Admin API adds the following in 9.1.0:

- a `discountType` endpoint;
- position-update handling;
- refinements to combination endpoints.

Integrations targeting the 9.0 API should retest these resources against 9.1.

## Symfony-rendered back office

The back office is fully rendered with Symfony and Twig (since 9.0.0),
including migrated surfaces such as:

- Login;
- Products;
- Orders;
- Attributes;
- Statuses.

Staff can create guest customers directly in the back office for manual
orders.

## Store-maintenance console commands

Thumbnail regeneration is available from the console (since 9.1.0):

```bash
php bin/console prestashop:thumbnails:regenerate
```

Search indexing is available from the console:

```bash
php bin/console prestashop:search:index
```

Module-translation export is available from the console:

```bash
php bin/console prestashop:module:export-translations --help
```

## Extension hooks

Modules can react to default-combination changes through
`actionUpdateDefaultCombinationAfter` (since 9.1.0).

New hooks are also available around:

- module enable, disable, and upgrade events;
- `Configuration::updateValue`;
- free-shipping price calculation;
- front-office country selection;
- front-office currency selection.

## Module entity discovery

Doctrine auto-mapping for modules recognizes every subfolder under
`src/Entity`, rather than only the first one (since 9.1.0).

## Extra Properties

PrestaShop 9.2 introduces native Extra Properties. They allow custom data
fields to be attached to any PrestaShop entity without overrides.

The fields support multistore and multilingual data and are available across
the Back Office, Front Office, and Admin API.
