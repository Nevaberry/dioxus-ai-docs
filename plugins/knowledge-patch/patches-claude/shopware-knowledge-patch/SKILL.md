---
name: shopware-knowledge-patch
description: Shopware
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Shopware Knowledge Patch

## Use this patch

Load this patch for Shopware Core, plugin, app, Storefront, Administration,
Store API, Admin API, deployment, or upgrade work. Open the reference that
matches the affected subsystem before changing extension points, templates,
configuration, API payloads, or infrastructure.

## Reference index

| Reference | Topics |
| --- | --- |
| [platform-operations.md](references/platform-operations.md) | Runtime and dependency requirements, builds, scheduled work, queues, cache invalidation, search infrastructure, filesystems, and hosting |
| [core-dal-and-extensions.md](references/core-dal-and-extensions.md) | DAL validation and queries, write events, entity definitions, custom fields, migrations, exceptions, scripts, and Core extension signatures |
| [apis-and-integrations.md](references/apis-and-integrations.md) | Store API and Admin API contracts, authentication, permissions, OAuth, MCP, OpenAPI, apps, and measurement systems |
| [administration.md](references/administration.md) | Administration cache hooks, Rule Builder, CMS blocks, snippets, Vue, Vite, Pinia, Meteor components, notifications, and dashboard extensions |
| [storefront-and-twig.md](references/storefront-and-twig.md) | Routing, navigation, ESI pagelets, cache hashes, forms, snippets, breadcrumbs, URLs, CMS rendering, themes, accessibility, and Twig |
| [commerce-orders-and-payments.md](references/commerce-orders-and-payments.md) | Orders, customers, addresses, cart rules, pricing, payment and shipping migrations, tax providers, documents, PDF, and ZUGFeRD |
| [media-search-and-content.md](references/media-search-and-content.md) | Thumbnail processing, media paths, product streams, SEO resolution, and mail simulation |

## Breaking changes and removals

### Platform and build compatibility

- Account for Doctrine DBAL 4, PHPUnit 11, Dompdf 3, and
  league/oauth2-server 9 when directly consuming those dependencies.
- Administration extensions with `webpack.config.js` must migrate to
  `vite.config.js`, ship a 6.7-specific build, and run on native Vue 3.
- Browser support follows Browserslist `defaults` unless `BROWSERSLIST`
  overrides it; native `URLSearchParams` replaces `query-string`.
- Declare `doctrine/inflector`, `symfony/monolog-bridge`, and
  `symfony/proxy-manager-bridge` directly when an extension uses them.

### Store API and authentication

- Stop consuming
  `orders.elements[].lineItems[].payload.purchasePrices`; Store API
  serialization removes it with no Store API replacement.
- Send OAuth scopes in singular `scope` as a space-delimited string.
  Array-valued `scopes` is rejected, and the authorization endpoint and
  controller were removed without replacement.
- Remove `MCP_SERVER`; MCP endpoints are available whenever
  `symfony/mcp-bundle` is installed, with no supported disabling flag.
- Replace removed `Cached*Route` decorators. Storefront header and footer now
  render through their ESI routes and layout entry points.
- Store API registration and login event customer entities no longer preload
  associations; subscribers must query related data explicitly.

### Payments and orders

- Payment and shipping writes and installers must provide stable
  `technicalName` values; replace migration-created `temporary_<method-id>`
  placeholders.
- Extend `AbstractPaymentHandler` rather than the deprecated payment-handler
  interfaces. Declare refund or recurring support through `supports()`.
- App payments use `manifest-3.0.xsd` and `pay-url`; asynchronous calls do not
  set payment states automatically, and finalize query parameters are in
  `requestData`.
- Replace customer default-payment usage with the last-used/current method.
  Migrated rules use `paymentMethod`, and the changed-payment-method flow is
  disabled.
- Use `order.primaryOrderDelivery` and `order.primaryOrderTransaction` rather
  than positional collection access.

### DAL and Core extensions

- Replace plugin `Resources/config/entities.xml` custom entities with
  `EntityDefinition` or attribute entities. Declare many-to-many foreign-key
  fields and implement `EntityExtension::getEntityName()`.
- Do not subclass DAL attribute classes, `IsFlowEventAware`, or
  `RuleComparison`; their inheritance contracts are closed.
- Use the moved DAL `UnmappedFieldException`. When both 6.7 feature-flag states
  must work, catch both classes because they share no exception parent.
- Replace removed Core APIs with `CreateMigrationCommand`,
  `MigrationQueryGenerator`, and `AccountService::loginByCredentials()` or
  `loginById()` where applicable.
- Move cache-state constants to `CacheStateSubscriber`, and cache-cookie and
  invalidation-header constants to `HttpCacheKeyGenerator`.
- Use `SystemConfigException` factory methods. The former system-config
  exception classes are replaced, while `trace()` and `getTrace()` are
  deprecated no-ops.

### Storefront extension points

- Replace route-state variables and `.is-ctl-*` / `.is-act-*` selectors with
  `activeRoute`, `window.activeRoute`, and `.is-active-route-*`.
- Use `addressType` instead of the deprecated address-manager Twig variable
  `type`.
- Pass `SalesChannelContext` to `sw_breadcrumb_full` and
  `sw_breadcrumb_full_by_id`.
- Replace `CookieProviderInterface` decorators with
  `CookieGroupCollectEvent` listeners; cookie Twig fields use `name` and
  `description`.
- Resolve theme files through `ThemeFilesystemResolver`; the old theme file
  importer types and `StorefrontController::setTwig()` are removed.
- Move header/footer data extensions to `HeaderPageletLoader` or
  `FooterPageletLoader` and their loaded events.
- Update product-card, selector, line-item, pagination, and icon markup for
  the current accessibility contracts.

### Administration extension points

- Register core-compatible state with `Shopware.Store.register()` and mutate
  it through actions. Remaining Vuex code uses the `mapVuex*` helpers.
- Migrate the listed basic `sw-*` components to their `mt-*` counterparts;
  account for `model-value`, checked-value exceptions, renamed variants, and
  explicit icon sizes.
- Move generic rule conditions to `sw-condition-generic` and central
  `rule_condition` errors instead of local condition-error mappings.
- Move CMS entity-select overrides to the component-specific blocks listed in
  the Administration reference.
- Move notification types from `Shopware\Administration` to
  `Shopware\Core\Framework\Notification`.

### Infrastructure and configuration

- Varnish cache tags require XKeys and can no longer be stored in Redis.
  Replace Redis `dsn` / `url` settings with named `connection` settings.
- JWT signing uses only `APP_SECRET`, which must be at least 32 characters;
  custom RSA secrets and the JWT-secret generation command are removed.
- Declare filesystem `visibility` beside `type`, not within adapter `config`.
- Run `bin/console es:index` after the Storefront Elasticsearch mapping
  changes.
- For OpenSearch 3, omit an empty mapping `properties` member or represent it
  as `{}`, never `[]`.

## High-value current features

### DAL and extension authoring

- Use `Criteria::excludeFields()` to omit eligible storage columns while
  retaining normal typed entities. Do not combine it with `addFields()`.
- Put app or plugin custom-field definitions in
  `Resources/config/custom-fields.xml`; lifecycle operations synchronize the
  fields, and `include-in-search` enables product-search indexing.
- Use `dal:validate --tolerate-foreign-key=constraint_name` only to tolerate a
  named incompatible constraint temporarily during migration.
- Plugin-side DAL writes triggered by Admin API and Sync API writes execute in
  system scope while preserving the original context source.
- `Feature::triggerDeprecationOrThrow()` accepts an optional `introducedIn`
  argument for a version-prefixed message.

### APIs and integrations

- Scope a standard integration to the intersection with an app user's ACL by
  sending a valid `sw-app-user-id`; empty or invalid values are ignored.
- Use the synchronous translation list, install, update, and remove Admin API
  actions with their matching `system:translation` privileges.
- Prepare or download media through the Admin API media download actions.
- Set Store API product listing, search, and search-suggest `limit` per request,
  subject to `shopware.api.store.max_limit`.
- Refresh MCP tools when tool-list-change notifications report that a
  toolset's advertised availability changed.

### Storefront and content

- Add non-price rule IDs through `ResolveCacheRelevantRuleIdsExtension` when
  `CACHE_REWORK` output varies by those rules.
- Add dynamic navigation inputs through `CategoryLevelLoaderCacheKeyEvent` so
  cached navigation varies with extension state.
- Use country-agnostic snippet names such as `en` and validate with
  `translation:validate`.
- Use `sw_block`, `sw_source`, `sw_include`, `sw_use`, `sw_embed`, `sw_from`,
  and `sw_import` for complete Storefront Twig import/include forms.
- Apply CMS image minimum height only in `cover` display mode.
- Use `ThumbnailGeneratedEvent` for per-file thumbnail post-processing.

### Operations

- Create a minimal plugin skeleton with `plugin:create --no-scaffold`.
- Opt into production sourcemaps only with
  `GENERATE_SOURCEMAPS=true NODE_ENV=production`.
- Consume the dedicated `webhook` transport when `WEBHOOKS_REWORK` is enabled;
  deduplicate deliveries before using the drain-to-async rollback path.
- Use the delayed-cache commands or Admin API action to inspect or flush
  queued cache tags; force invalidation only for a critical write.
- Set `SHOPWARE_SKIP_WEBINSTALLER` to a non-empty value on a read-only PaaS
  deployment that must bypass installer lock checks.
- Lower `shopware.filesystem.batch_write_size` from its default of 250 when S3
  batch operations exhaust file descriptors.

## Targeted checks

- For an order re-payment flow, verify the selected method has
  `afterOrderEnabled`; otherwise the Store API returns HTTP 403 with
  `CHECKOUT__ORDER_PAYMENT_METHOD_NOT_CHANGEABLE`.
- For document timestamp stability, configure the sales-channel business
  timezone rather than relying on an unset fallback.
- For direct product-export media URL expressions, remove manual URL encoding;
  the body renderer already applies RFC 3986 encoding.
- For custom PDF document renderers, set final bytes with
  `RenderedDocument::setContent()`.
- For ZUGFeRD corrections, call `withDocumentInformation()` before adding
  deliveries, and override `getPriceWithFallback()` rather than `getPrice()`.
