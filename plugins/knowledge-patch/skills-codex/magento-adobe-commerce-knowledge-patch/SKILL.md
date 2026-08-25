---
name: magento-adobe-commerce-knowledge-patch
description: Magento / Adobe Commerce
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Magento Open Source and Adobe Commerce Compatibility

Use this skill when upgrading, extending, operating, or integrating Magento Open
Source or Adobe Commerce and the work touches current platform, GraphQL,
extension, frontend, or operational behavior.

Keep product-specific guidance separate: Adobe Commerce-only behavior is marked
as such, while Magento Open Source guidance is identified independently.

## Reference index

| Reference | Topics |
| --- | --- |
| [platform-and-operations.md](references/platform-and-operations.md) | PHP and dependency floors, services, search, MySQL, security administration, indexing, ACL, configuration locks, CLI, cache, cron, Varnish, and regional configuration |
| [graphql-cart-and-checkout.md](references/graphql-cart-and-checkout.md) | Cart pricing, addresses, checkout errors, payment visibility, website scope, and cart input behavior |
| [graphql-customers-orders-and-returns.md](references/graphql-customers-orders-and-returns.md) | Customer confirmation and addresses, order fields and lookup, cancellation, totals, gifts, and returns |
| [catalog-api-and-runtime.md](references/catalog-api-and-runtime.md) | Catalog GraphQL and REST behavior, stock, product images, reCAPTCHA, custom scalars, query complexity, tokens, and product layouts |
| [extensions-and-frontend.md](references/extensions-and-frontend.md) | Braintree, editor and JavaScript migrations, extension compatibility, critical CSS, LESS, source maps, and static deployment |

## Upgrade gates

### PHP and test tooling

Adobe Commerce supports PHP 8.4 and 8.3. PHP 8.2 is compatible only for an
upgrade, and PHP 8.1 support is removed.

An installation on PHP 8.1 must move to PHP 8.3 before the Commerce upgrade.

Move custom test suites from PHPUnit 9 to PHPUnit 10.

### Message queues and search

RabbitMQ 4 does not support classic mirrored queues.

For cloud and on-premises deployments, migrate classic mirrored queues to
quorum queues before moving to RabbitMQ 4.

OpenSearch 2.19 is the search target. Elasticsearch is no longer compatible,
although its Admin options and code remain deprecated.

### MySQL schema settings

MySQL schemas default to `utf8mb4` rather than deprecated `utf8mb3`.

MySQL 8.4 enables `restrict_fk_on_non_standard_key` by default. Existing
Commerce schemas require one of these settings during upgrade:

```ini
restrict_fk_on_non_standard_key=OFF
```

```text
--skip-restrict-fk-on-non-standard-key
```

### Removed legacy assets and editor levels

Magento Open Source removes the jQuery/fileUploader and ExtJS folders after
migration to Uppy and jsTree. Extensions must stop importing those assets.

Custom Magento Open Source editor integrations must target TinyMCE 7. Adobe
Commerce uses TinyMCE 6.8.5 and removes TinyMCE 5.

## Security, permissions, and locked settings

Duo 2FA uses Web SDK v4 and Universal Prompt. Its Admin configuration requires
a Client ID and Secret, and the OTP Window default is `29` rather than `1`.

Encryption-key changes and re-encryption of supported configuration, payment,
and custom-field data are CLI-only.

Permissions introduced by custom modules are not automatically granted to
existing roles.

Values locked with `config:set --lock-env` or `--lock-conf` cannot be changed
through Admin forms.

SRI hashes are stored under `pub/static` by area and survive cache flushes.

## GraphQL client contract changes

### Cart mutation errors

`updateCartItems` returns a successful response containing mapped error details,
including `InsufficientStockError`, instead of throwing.

Clients must inspect the returned errors.

### Customer and guest cancellation

`cancelOrder` is available only to registered customers.

Guest cancellation starts with `requestGuestOrderCancel`, which requires an
order token, and completes with `confirmCancelOrder`.

Partially shipped orders cannot be canceled.

### Guest order lookup

Guest order lookup uses `lastname` instead of `postcode`.

Matching guest orders are associated with a customer account by email.

### Totals and checkout

`OrderTotal.subtotal` is deprecated in favor of `subtotal_excl_tax` and
`subtotal_incl_tax`.

Zero-total checkout exposes only the Free payment method.

### Runtime behavior

The default maximum GraphQL query complexity is `1000`, raised from `300`.

Requests made with expired customer tokens return HTTP 401.

## Indexing and operational behavior

New indexers default to **Update by Schedule**; existing indexer modes are
preserved.

Switching an index back to **Update on Save** removes its unused changelog
tables and marks the index invalid.

Maintenance-mode IP allowlists accept CIDR ranges.

`maintenance:status` reports **enabled/disabled** rather than **active/not
active**.

The built-in full-page cache removes marketing query parameters in the same
way as Varnish. The Varnish exclusion set includes `gad_source`, `srsltid`, and
`msclkid`.

Redis cache garbage collection enables Lua mode by default to avoid cache-tag
cleanup races.

## Extension and frontend highlights

The bundled Braintree extension moves shipping-method selection into PayPal and
Google Pay modals and makes the review page optional.

It removes Sofort and Giropay and sends PayPal carrier and tracking details when
an order ships.

A critical-head block places critical CSS before other assets.

Developer-mode server-side LESS compilation emits source maps, and
Grunt-generated source-map paths omit the `/pub` prefix.

Static deployment excludes CSS belonging to disabled modules.

## Applying the guidance

Use the platform reference for environment and upgrade constraints, then select
the GraphQL or extension reference that matches the integration being changed.

Preserve distinctions between Adobe Commerce and Magento Open Source when
applying dependency, editor, GraphQL, and bundled-extension behavior.
