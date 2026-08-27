# Admin API and Extensions

## Admin API availability

PrestaShop 9.0.0 introduces a REST/JSON Admin API built on API Platform for
store-management integrations and automation.

Endpoint coverage is still a work in progress. Integrations must verify that
each required resource and operation is available.

## Admin API additions

In 9.1.0, the Admin API adds:

- a `discountType` endpoint
- position-update handling
- refinements to combination endpoints

Integrations targeting the 9.0 API should retest these resources against 9.1.

## Symfony-rendered back office

The back office in 9.0.0 is fully rendered with Symfony and Twig. Migrated
surfaces include Login, Products, Orders, Attributes, and Statuses.

Staff can create guest customers directly in the back office for manual
orders.

## Hooks

PrestaShop 9.1.0 lets modules react to default-combination changes through
`actionUpdateDefaultCombinationAfter`.

It also adds hooks around:

- module enable events
- module disable events
- module upgrade events
- `Configuration::updateValue`
- free-shipping price calculation
- front-office country selection
- front-office currency selection

## Module entity discovery

Doctrine auto-mapping for modules in 9.1.0 recognizes every subfolder under
`src/Entity`, rather than only the first one.

## Extra Properties

PrestaShop 9.2 introduces native Extra Properties, allowing custom data fields
to be attached to any PrestaShop entity without overrides.

The fields support multistore and multilingual data. They are available across
the Back Office, Front Office, and Admin API.
