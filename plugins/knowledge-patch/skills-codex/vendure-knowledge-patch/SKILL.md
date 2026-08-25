---
name: vendure-knowledge-patch
description: Vendure
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Vendure Knowledge Patch

Use this skill when working with current Vendure behavior, upgrades, APIs,
Dashboard extensions, operational tooling, or official integrations.

Treat the linked references as the detailed source for implementation work.
Start with the breaking and security-sensitive notes below before applying a
more focused reference.

## Reference index

| Reference | Topics |
| --- | --- |
| [Security, authentication, and policy](references/security-auth-and-policy.md) | Security fixes, production credentials, external login linking, API keys, row-level authorization, proxy trust, passwords, customer assignment |
| [Catalog, assets, and search](references/catalog-assets-and-search.md) | MIME types, channel-aware products and stock, shared options, catalog APIs, filters, custom fields, assets, translation fallbacks |
| [Orders, checkout, tax, and payments](references/orders-checkout-and-payments.md) | Cart mutations, calculation and merge strategies, coupons, atomic operations, tax, shipping, payment, inventory |
| [Platform, data, and operations](references/platform-data-and-operations.md) | Settings Store, migrations, lifecycle hooks, scheduled tasks, queues, telemetry, CLI, scaffolding |
| [Dashboard development](references/dashboard-development.md) | Packages, build modes, routing, authentication, shell extensions, forms, queries, tables, bulk actions, merchant workflows |
| [Integrations and public exports](references/integrations-and-public-exports.md) | Email, Mollie, Stripe, Sentry, GraphiQL, public core exports, direct dependencies |

## Breaking and upgrade-sensitive changes

### Replace legacy asset MIME names in explicit allow-lists

The unreleased line upgrades `file-type` to `^21.3.1` and uses these IANA MIME
names:

- `audio/flac`
- `video/matroska`
- `application/vnd.apache.arrow.file`
- `application/vnd.apache.parquet`

Replace the former `x-` names in explicit
`assetOptions.permittedFileTypes` lists. The default wildcard list is
unaffected.

### Remove the default production superadmin password

From 3.7, production startup fails while the default superadmin password is
configured.

### Require verified provider email for account linking

A custom `AuthenticationStrategy` must return `verified: true` for a
provider-verified email before an external login can link to an existing
account. This does not affect creation of a new account.

### Use context-first Settings Store calls

Since 3.4.2, prefer:

```ts
SettingsStoreService.get<T>(ctx, key)
SettingsStoreService.getMany(ctx, keys)
SettingsStoreService.set<T>(ctx, key, value)
SettingsStoreService.setMany(ctx, values)
```

The old argument order remains temporarily accepted.

### Review coupon-code identity

From 3.7, promotion coupon matching is case-insensitive. This is breaking for
stores that treated case variants as distinct coupon codes.

### Review email compatibility

In 3.7, the email plugin moves from MJML 4 to 5 and nodemailer 6 to 9. Review
custom templates and transports for compatibility.

### Declare health-check dependencies directly

From 3.7, `@nestjs/terminus` is no longer supplied transitively. Custom health
checks must declare it directly.

### Update integration configuration and dependencies

- The Sentry plugin moves to `@sentry/nestjs`, which changes its
  configuration.
- MolliePlugin moves to the Payments API and requires
  `@mollie/api-client@4.3.3` for the 3.4 upgrade.
- The old AdminUiPlugin `compatibilityMode` is deprecated.

## Security fixes to account for

### 3.7.2

3.7.2 closes:

- Unauthorized draft-line adjustment.
- Administrator password-reset privilege escalation.
- Cross-channel Promotion and FacetValue deletion.
- Cross-channel Asset and StockLocation writes.

### Earlier fixes

- 3.5.3 addresses native-auth timing enumeration.
- 3.6.2 addresses `languageCode` and Postgres-search SQL injection.
- 3.6.4 addresses asset-import SSRF.
- 3.6.5 addresses Dashboard XSS, SQLite list-query denial of service, and Shop
  API list-data exposure.

## Authentication and authorization

### API-key authentication

3.6 adds core API-key authentication and Dashboard key management. API-key
sessions resolve their `Administrator` through the key owner.

### Row-level authorization

Use `EntityAccessControlStrategy` as the extension point for row-level access
control.

### Request and account policy

- `ApiOptions` accepts `trustProxy`.
- The password validation strategy supports `maxLength` and enforces a default
  maximum.
- From 3.7, `CustomerChannelAssignmentStrategy` controls automatic
  customer-to-channel assignment.

## Catalog and inventory essentials

### Channel-aware product behavior

- Product lookup by slug is channel-scoped.
- `assignProductsToChannel` assigns the Product and its variants.
- Assigning a variant to a channel seeds a `StockLevel`.
- New variants inherit every channel of their Product.
- Numeric `stockOnHand` writes target the active channel's stock location.

### Shared product options

In 3.6, `ProductOptionGroup` and `ProductOption` become shared, channel-aware
entities. CSV import supports shared option groups, and the Dashboard has an
Option Groups management page.

### Search and filtering

- DefaultSearchPlugin accepts `collectionIds` and `collectionSlugs`.
- Tax-rate lists can filter by `zoneId` and `categoryId`.
- Collection queries expose `productVariantCount`.
- Product and variant tooling supports SKU filtering.
- Elasticsearch can `groupBySKU` for multi-vendor stores.

## Orders and checkout essentials

### Shop API additions

The Shop API adds `addItemsToOrder` for multiple lines and a mutation for
changing the active order's currency. `AddPaymentToOrderResult` can return
`CouponRemovedDuringCheckoutError` when checkout invalidates a coupon.

### Calculation and merge strategies

- `OrderTaxCalculationStrategy` configures order-level tax calculation.
- `OrderLineDiscountDistributionStrategy` controls discount proration.
- `OrderMergeStrategy` may be asynchronous.

### Atomic behavior

`OrderService.mergeOrders()` is atomic and concurrency-safe. State-machine
transitions roll back atomically when a hook fails.

### Coupon accounting

Usage limits apply to auto-applied promotions and concurrent checkout races.
Draft and seller orders are excluded from the corresponding counts.

## Operations quick reference

### Required migrations

- The 3.4 Settings Store requires a new table.
- 3.4 adds indexes for `Order.orderPlacedAt` and `JobItem.createdAt`.
- DefaultCachePlugin users upgrading through 3.2 need `precision(3)` on
  `CacheItem.expiresAt`.
- 3.6 provides `migrateAssetTranslationData()` for the asset-translation
  change.

### Server and work orchestration

- `BootstrappedEvent` signals server readiness.
- `onBeforeAppListen` exposes the Nest application immediately before the
  server starts listening.
- Scheduled tasks can be triggered manually and receive a `RequestContext`.
- A built-in database job-cleanup task is available.
- Job options support priority.
- BullMQ honors configured Redis prefixes for queue and buffer storage.

### CLI and project setup

The CLI supports non-interactive operation, `schema`, `dev`, `build`, `start`,
and the `doctor` project check. New projects include the React Dashboard and
can optionally scaffold a Next.js storefront. Scaffolded projects read the
server port from `VENDURE_SERVER_PORT`.

## Dashboard extension essentials

Dashboard extensions can define unauthenticated routes, TanStack Router
`validateSearch`, and router-plugin options. The Dashboard supports
bearer-token authentication and custom React providers.

Extensions can replace the login screen, provide static or functional
`navSections`, add header `toolbarItems`, extend the `ActionBar`, and
conditionally add or replace page blocks. Navigation, custom fields, widgets,
and custom pages can be permission-gated.

For forms, queries, tables, bulk actions, saved views, and merchant workflows,
use [Dashboard development](references/dashboard-development.md).
