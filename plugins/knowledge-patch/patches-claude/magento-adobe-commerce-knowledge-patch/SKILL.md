---
name: magento-adobe-commerce-knowledge-patch
description: Magento / Adobe Commerce
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Magento Open Source and Adobe Commerce

Use this skill when upgrading or extending Magento Open Source or Adobe Commerce,
especially around PHP and service compatibility, GraphQL contracts, Admin and CLI
behavior, frontend assets, payments, gifts, or returns. Keep product-specific advice
scoped to the named product: similarly named components do not always use the same
dependency level or expose the same behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [Platform upgrades and services](references/platform-upgrades-and-services.md) | PHP, Composer dependencies, databases, search, queues, editors, and extension compatibility |
| [Administration and operations](references/administration-and-operations.md) | Security administration, indexers, ACLs, configuration locks, CLI, caching, cron, Varnish, and frontend output |
| [GraphQL carts and catalog](references/graphql-carts-and-catalog.md) | Cart pricing and errors, checkout, addresses, catalog, inventory, product search, and runtime behavior |
| [GraphQL customers and orders](references/graphql-customers-and-orders.md) | Customer confirmation and addresses, order filters and fields, cancellation, reordering, and guest association |
| [Payments, gifts, and returns](references/payments-gifts-and-returns.md) | Braintree modals, payment methods, totals, gift cards and wrapping, rewards, store credit, and RMAs |

## Upgrade blockers first

### Move Adobe Commerce installations off PHP 8.1

Adobe Commerce supports PHP 8.4 and 8.3. PHP 8.2 is compatible only for
upgrading, and PHP 8.1 support is removed. Move an installation on PHP 8.1 to
PHP 8.3 before upgrading Commerce.

### Migrate classic mirrored RabbitMQ queues

RabbitMQ 4 does not support classic mirrored queues. Before using it, migrate
those queues to quorum queues in both cloud and on-premises deployments.

### Prepare MySQL 8.4 schemas

MySQL 8.4 enables `restrict_fk_on_non_standard_key` by default. During an
existing Commerce schema upgrade, use either:

- `restrict_fk_on_non_standard_key=OFF`
- `--skip-restrict-fk-on-non-standard-key`

MySQL schemas now default to `utf8mb4` rather than deprecated `utf8mb3`.

### Replace Elasticsearch with OpenSearch

Adobe Commerce targets OpenSearch 2.19. Elasticsearch is no longer compatible,
although its Admin options and code remain deprecated.

### Stop importing removed frontend libraries

Magento Open Source removes the jQuery/fileUploader and ExtJS folders after
migrating to Uppy and jsTree. Extensions must stop importing those legacy
assets.

### Respect product-specific TinyMCE levels

- Adobe Commerce uses TinyMCE 6.8.5 and removes TinyMCE 5.
- Magento Open Source uses TinyMCE 7.3.0, including Page Builder integration;
  custom editor integrations must target TinyMCE 7.
- In Magento Open Source, plugin widget functions are again callable through
  the returned widget object for backward compatibility.

## GraphQL contract changes

### Inspect `updateCartItems` errors in successful responses

In Adobe Commerce, `updateCartItems` returns a successful response with mapped
error details, including `InsufficientStockError`, instead of throwing. Clients
must inspect the returned errors.

### Use the current guest-order cancellation flow

`cancelOrder` is registered-customer-only. Guest cancellation uses
`requestGuestOrderCancel` with an order token, followed by
`confirmCancelOrder`. Partially shipped orders cannot be canceled.

### Update guest-order lookup

Guest order lookup uses `lastname` instead of `postcode`.

### Update deprecated order subtotal consumers

In Adobe Commerce, `OrderTotal.subtotal` is deprecated. Use
`subtotal_excl_tax` and `subtotal_incl_tax`.

### Handle expired customer tokens as authentication failures

GraphQL requests made with expired customer tokens return HTTP 401.

## Frequently used GraphQL additions

### Cart pricing and availability

`CartItemPrices` adds:

- `original_item_price`, explicitly pre-discount
- `original_row_total`
- `row_total_including_catalog_discounts_only`

`CartPrices` adds `grand_total_excluding_tax`, and `CartItemInterface` adds
`not_available_message`.

### Cart addresses and checkout

Cart addresses gain an address-book identifier, and `ShippingCartAddress` adds
`same_as_billing`. Zero-total checkout exposes only the Free payment method.
`StoreConfig` exposes per-store terms-and-conditions settings.

For Magento Open Source, `setShippingAddressesOnCart` accepts
`pickup_location_code` without a customer address ID or address object.
`customerCart` creates an empty cart when no quote exists.

### Customer and order access

Customers gain `resendConfirmationEmail` and paginated `customer.addressesV2`.
`CustomerOrders` adds `date_of_first_order` plus `created_at`, `status`, and
`grand_total` filters.

`CustomerOrder` adds `is_virtual`, `available_actions`, `customer_info`, and
`order_status_change_date`. Order addresses can return custom attributes, and
`OrderItemPrices` supplies detailed pre-discount prices.

### Catalog queries

`ProductInterface.quantity` returns available stock or `null` according to
Admin settings. `StoreConfig` exposes grouped- and configurable-product image
selection, and `trackViewedProduct` is callable by guests and customers.

For Magento Open Source, OAuth1 REST product GET requests work with SKUs that
contain `/`. Category filtering with `category_uid` and
`includeDirectChildrenOnly` returns only direct children. Multi-field product
sorting works when sort fields come through variables, and product-search
`total_count` is no longer capped at 10,000 matches.

## Administration and extension checks

### Review indexer and role behavior

New indexers default to **Update by Schedule**, while existing modes remain
unchanged. Switching an index to **Update on Save** removes its unused
changelog tables and marks it invalid.

Permissions introduced by custom modules are not automatically granted to
existing roles. Review those roles after adding such permissions.

### Honor locked configuration

Values locked by `config:set --lock-env` or `--lock-conf` cannot be changed
through Admin forms.

### Compile dependency injection defensively

In Adobe Commerce, `setup:di:compile` fails when a preference names a missing
or excluded class. In Magento Open Source, it correctly generates interceptor
methods for plugins configured through virtual types, matching runtime
compilation behavior.

`Magento\Catalog\Model\ProductRepository` restores the Initialization Helper
as its second constructor parameter so existing subclasses retain their prior
contract.

### Parse the indexer lock environment value correctly

Magento Open Source parses this as Boolean `false`, so it disables application
locking as intended:

```dotenv
MAGENTO_DC_INDEXER__USE_APPLICATION_LOCK=false
```

## Operational quick reference

- `dev:di:info` can target an application area instead of only GLOBAL.
- Magento CLI supports Symfony `CommandLoaderInterface` for deferred command
  initialization.
- Maintenance-mode IP allowlists accept CIDR ranges.
- `maintenance:status` reports **enabled/disabled** rather than
  **active/not active**.
- Encryption-key changes and supported-data re-encryption are CLI-only.
- The System > Support > Data Collector tool is removed.
- Cron groups running in separate processes retain both standard output and
  standard error in logs.
- Admin provides an **Export VCL for Varnish 7** action.

## Cache and frontend quick reference

The built-in full-page cache removes marketing query parameters in the same way
as Varnish. Varnish exclusions include `gad_source`, `srsltid`, and `msclkid`,
preventing campaign parameters from multiplying cache entries. Redis cache
garbage collection enables Lua mode by default to avoid cache-tag cleanup
races.

A critical-head block places critical CSS before other assets. Developer-mode
server-side LESS compilation emits source maps, and Grunt-generated source-map
paths omit the `/pub` prefix. Static deployment excludes CSS from disabled
modules.

For the complete product-scoped details, follow the reference index rather than
generalizing behavior between Adobe Commerce and Magento Open Source.
