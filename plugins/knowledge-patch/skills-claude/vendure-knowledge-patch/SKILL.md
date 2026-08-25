---
name: vendure-knowledge-patch
description: Vendure
version: null
license: MIT
metadata:
  author: Nevaberry
---



# Vendure Knowledge Patch

Use this skill when implementing or upgrading a Vendure server, Shop or Admin
API, Dashboard extension, storefront integration, payment or email integration,
or operational tooling. Check the breaking-change notes first, then open only
the reference that matches the work.

## Reference index

| Reference | Topics |
|---|---|
| [security-and-access.md](references/security-and-access.md) | Security fixes, production credentials, external login linking, API keys, row-level access, proxy and password policy, customer assignment |
| [catalog-assets-and-search.md](references/catalog-assets-and-search.md) | Channels, stock, shared options, assets, search and list filters, custom fields, translation fallbacks |
| [orders-checkout-and-payments.md](references/orders-checkout-and-payments.md) | Cart mutations, order strategies and atomicity, promotions, tax, payments, shipping, order events |
| [dashboard-and-project-tooling.md](references/dashboard-and-project-tooling.md) | CLI, scaffolding, Dashboard packaging and builds, routing, extensions, forms, tables, merchant workflows |
| [platform-configuration-and-operations.md](references/platform-configuration-and-operations.md) | Settings Store, migrations, lifecycle hooks, jobs, telemetry, GraphiQL, public exports, direct dependencies |
| [integrations-and-observability.md](references/integrations-and-observability.md) | Email, Mollie, Stripe, Sentry |

## Breaking changes and upgrade checks

### Replace legacy asset MIME names

The unreleased line upgrades `file-type` to `^21.3.1`. In explicit
`assetOptions.permittedFileTypes` lists, replace the former `x-` names with:

- `audio/flac`
- `video/matroska`
- `application/vnd.apache.arrow.file`
- `application/vnd.apache.parquet`

The default wildcard list is unaffected.

### Remove the default production password

From 3.7, production startup fails while the default superadmin password is
configured.

### Review email templates and transports

In 3.7, the email plugin moves from MJML 4 to 5 and nodemailer 6 to 9. Review
custom templates and transports for compatibility.

### Declare health-check dependencies directly

From 3.7, `@nestjs/terminus` is no longer supplied transitively. Custom health
checks must declare it directly.

### Account for case-insensitive coupon matching

From 3.7, promotion coupon matching is case-insensitive. This breaks stores
that treated case variants as distinct coupon codes.

### Replace deprecated Dashboard compatibility mode

`DashboardPlugin` is exported from `@vendure/dashboard`; the old AdminUiPlugin
`compatibilityMode` is deprecated.

## Security-critical upgrade notes

- 3.7.2 closes unauthorized draft-line adjustment, administrator
  password-reset privilege escalation, cross-channel Promotion and FacetValue
  deletion, and cross-channel Asset and StockLocation writes.
- 3.6.5 addresses Dashboard XSS, SQLite list-query denial of service, and Shop
  API list-data exposure.
- 3.6.4 addresses asset-import SSRF.
- 3.6.2 addresses `languageCode` and Postgres-search SQL injection.
- 3.5.3 addresses native-auth timing enumeration.

Read [security-and-access.md](references/security-and-access.md) when the work
touches authentication, authorization, channel boundaries, proxy trust,
password validation, or customer assignment.

## Required migrations

- The 3.4 Settings Store requires a new table.
- 3.4 adds indexes for `Order.orderPlacedAt` and `JobItem.createdAt`.
- DefaultCachePlugin users upgrading through 3.2 need `precision(3)` on
  `CacheItem.expiresAt`.
- 3.6 provides `migrateAssetTranslationData()` for the asset-translation
  change.

## Authentication and authorization

### External account linking

A custom `AuthenticationStrategy` must return `verified: true` for a
provider-verified email before an external login can link to an existing
account. Creating a new account is unaffected.

### API keys and entity access

3.6 adds core API-key authentication and Dashboard key management. API-key
sessions resolve their `Administrator` through the key owner.
`EntityAccessControlStrategy` is the extension point for row-level access
control.

## Settings Store

3.4 introduces `SettingsStore` for global and scoped configuration. Read and
write permissions are added later, and a Dashboard management page arrives in
3.6.

Since 3.4.2, prefer the context-first service signatures; the old order remains
temporarily accepted:

```ts
SettingsStoreService.get<T>(ctx, key)
SettingsStoreService.getMany(ctx, keys)
SettingsStoreService.set<T>(ctx, key, value)
SettingsStoreService.setMany(ctx, values)
```

## Channel-aware catalog rules

- Product lookup by slug is channel-scoped.
- `assignProductsToChannel` assigns the Product and its variants.
- Assigning a variant to a channel seeds a `StockLevel`.
- New variants inherit every channel of their Product.
- Numeric `stockOnHand` writes target the active channel's stock location.
- In 3.6, `ProductOptionGroup` and `ProductOption` are shared, channel-aware
  entities; CSV import supports shared option groups, and the Dashboard has an
  Option Groups management page.

## Order and checkout behavior

- The Shop API adds `addItemsToOrder` and a mutation for changing the active
  order's currency.
- `AddPaymentToOrderResult` can return
  `CouponRemovedDuringCheckoutError` when checkout invalidates a coupon.
- `OrderTaxCalculationStrategy` configures order-level tax calculation.
- `OrderLineDiscountDistributionStrategy` controls discount proration.
- `OrderMergeStrategy` may be asynchronous.
- `OrderService.mergeOrders()` is atomic and concurrency-safe.
- State-machine transitions roll back atomically when a hook fails.

Read [orders-checkout-and-payments.md](references/orders-checkout-and-payments.md)
before changing promotion usage, tax, payment eligibility, shipping, or order
event handling.

## Dashboard entry points

- New projects include the React Dashboard and can optionally scaffold a
  Next.js storefront.
- Generated Dashboard configuration uses API URL `auto`.
- Scaffolded projects read the server port from `VENDURE_SERVER_PORT`.
- Dashboard builds support Vite 7, user stylesheets, and opt-in pre-bundling
  through `useExperimentalBundle`.
- Extensions can add unauthenticated routes, TanStack Router `validateSearch`,
  router-plugin options, bearer-token authentication, and custom React
  providers.

Open [dashboard-and-project-tooling.md](references/dashboard-and-project-tooling.md)
for shell extension points, permissions, forms, queries, tables, bulk actions,
saved views, and merchant workflows.

## Operations and integration entry points

- `ApiOptions` accepts `trustProxy`.
- `BootstrappedEvent` signals server readiness, and `onBeforeAppListen`
  exposes the Nest application immediately before listening starts.
- Scheduled tasks can be triggered manually, receive a `RequestContext`, and
  include a built-in database job-cleanup task.
- Job options support priority; BullMQ honors configured Redis prefixes for
  queue and buffer storage.
- 3.3 introduces `@vendure/telemetry-plugin` and tracing across services,
  cache, scheduled tasks, and job queues.
- Email generators may be asynchronous, and `SMTPTransportOptions` accepts
  pooled-SMTP settings.
