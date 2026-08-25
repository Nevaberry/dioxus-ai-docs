---
name: shopware-knowledge-patch
description: Shopware
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Shopware Knowledge Patch

Use this skill for Shopware development, upgrades, extension compatibility,
Store API or Admin API integration, Storefront customization, Administration
customization, and deployment configuration. Start with the quick checks below,
then open the task-specific reference before changing code or configuration.

## Reference index

| Reference | Topics |
| --- | --- |
| [Administration](references/administration.md) | Vite and Vue 3, Pinia, Meteor components, CMS and rule-condition extension points, notifications, dashboard, sourcemaps |
| [Storefront](references/storefront.md) | ESI pagelets, route state, navigation, forms, snippets, accessibility, Twig, themes, cookies, feeds, images |
| [APIs and integrations](references/apis-and-integrations.md) | Store API and Admin API contracts, MCP, translations, media downloads, sessions, integration ACLs, OpenAPI |
| [Data and search](references/data-and-search.md) | DAL contracts, criteria, indexing, product streams, Elasticsearch/OpenSearch, cache keys, SEO, entities |
| [Extensions and framework](references/extensions-and-framework.md) | Plugins, apps, custom fields, scheduled tasks, Symfony, Composer, exceptions, hooks, configuration |
| [Operations and infrastructure](references/operations-and-infrastructure.md) | Platform baseline, cache, queues, Redis, Varnish, filesystems, PaaS, JWT, Shopware Services, CLI setup |
| [Commerce and documents](references/commerce-and-documents.md) | Payments, orders, customers, rules, addresses, tax providers, documents, ZUGFeRD, measurements |

## Breaking-change triage

### Administration build and state

- Migrate custom Administration builds from `webpack.config.js` to
  `vite.config.js` and distribute a 6.7-specific build.
- Native Vue 3 is in use and components are async by default. Guard template
  refs or use `@vue:mounted`.
- Core state uses `Shopware.Store`; register Pinia stores with
  `Shopware.Store.register()` and mutate state in actions.
- Replace migrated `sw-*` basic components with their `mt-*` equivalents and
  account for their changed value, event, and prop contracts.

See [Administration](references/administration.md).

### Storefront chrome and extension points

- Store API `Cached*Route` decorators are removed.
- Header and footer now render through `/header` and `/footer` ESI requests,
  with new layout entry points and `base_esi_header` / `base_esi_footer`.
- Header/footer data belongs in their pagelet loaders and loaded events, not
  `GenericPageLoader`, `Page`, or `ErrorTemplateStruct`.
- Use `activeRoute`, `window.activeRoute`, and `.is-active-route-*` instead of
  the former controller/action state.

See [Storefront](references/storefront.md).

### Payment and customer contracts

- Extend `AbstractPaymentHandler`; the former sync, async, prepared, refund,
  and recurring handler interfaces are deprecated.
- App manifests use `manifest-3.0.xsd` and `pay-url` rather than `capture-url`.
- Payment and shipping API writes and plugin installers must supply a stable
  `technicalName`.
- Customer default-payment behavior is removed in favor of the last-used or
  current method.

See [Commerce and documents](references/commerce-and-documents.md).

### DAL and extension definitions

- Plugin `Resources/config/entities.xml` custom entities are unsupported; use
  an `EntityDefinition` or attribute entities.
- Many-to-many mapping definitions must declare foreign-key fields, and
  `EntityExtension::getEntityName()` is mandatory.
- Search-result wrappers are separating from collections. Call collection
  methods on `$result->getEntities()` and iterate `searchResult.entities`.
- `Criteria::excludeFields()` can omit storage columns without returning
  partial entities, but cannot be combined with `addFields()`.

See [Data and search](references/data-and-search.md).

### Cache, queues, and infrastructure

- Cache invalidation is delayed through the `shopware.invalidate_cache`
  scheduled task; the prior delay switch is removed.
- Under `WEBHOOKS_REWORK`, explicitly consume the `webhook` transport or
  deliveries accumulate.
- Varnish requires XKeys; cache tags can no longer be stored in Redis.
- Redis DSNs now belong to named connections, and dependent configuration uses
  `connection` keys rather than `dsn` or `url`.
- JWTs use only `APP_SECRET`, which must contain at least 32 characters.

See [Operations and infrastructure](references/operations-and-infrastructure.md).

## High-use migration recipes

### Create a minimal plugin

```bash
bin/console plugin:create MyPlugin MyNamespace --no-scaffold
```

`--no-scaffold` creates only the required plugin skeleton.

### Validate foreign keys for MySQL 8.4

`dal:validate` rejects a foreign key that does not reference a complete primary
or unique key. Versioned entities commonly need the missing `version_id`.
Temporarily tolerate a constraint during migration with:

```bash
bin/console dal:validate --tolerate-foreign-key=constraint_name
```

### Opt into production sourcemaps

Set `GENERATE_SOURCEMAPS=true` together with `NODE_ENV=production`:

```bash
GENERATE_SOURCEMAPS=true NODE_ENV=production composer build:js:admin
GENERATE_SOURCEMAPS=true NODE_ENV=production composer build:js:storefront
```

Other production values keep sourcemaps disabled; non-production builds always
generate them.

### Consume and roll back webhook transport

With `WEBHOOKS_REWORK` enabled, consume `webhook` explicitly, preferably before
the other transports:

```bash
bin/console messenger:consume webhook async low_priority
```

For rollback, stop webhook workers and run:

```bash
bin/console webhook:drain-to-async
```

Draining can redeliver messages, so receivers must deduplicate using
`X-Shopware-Event-Id` or body `eventId`. Recover crashed rows left as `running`
before draining.

### Flush delayed cache invalidations

- Use `sw-force-cache-invalidate: 1` for a critical Admin API write.
- Run `cache:clear:delayed` or call `DELETE /api/_action/cache-delayed` to flush
  queued tags.
- Run `cache:watch:delayed` to inspect queued tags.

### Configure a custom Storefront route name

Allowlist route names that do not use the `frontend`, `widgets`, or `payment`
prefixes:

```yaml
storefront:
  router:
    allowed_routes: [swag.test.foo-bar]
```

### Exclude heavy DAL fields

```php
$criteria->excludeFields(['description', 'keywords']);
```

Excluded properties keep their typed entity defaults. Unknown, required, or
write-protected top-level fields cannot be excluded.

### Configure read-only deployments

Set a non-empty value to bypass web-installer and `install.lock` checks and
avoid writes to the project root and public `.htaccess`:

```bash
SHOPWARE_SKIP_WEBINSTALLER=1
```

### Update installed translations

The daily `translation.update` task performs the same refresh as
`translation:update` and `POST /api/_action/translation/update`. Disable it
with:

```bash
bin/console scheduled-task:deactivate translation.update
```

When no translations are installed, the task makes no remote request.

### Start a local Shopware CLI project

With Docker and Shopware CLI installed:

```bash
shopware-cli project create mystore
cd mystore
make up
make setup
```

The generated default serves the Storefront at `http://127.0.0.1:8000`, the
Administration at `http://127.0.0.1:8000/admin`, and uses `admin` / `shopware`.

## Task routing

- For a template, component, or Administration override, read
  [Administration](references/administration.md) or
  [Storefront](references/storefront.md) before selecting an extension point.
- For routes, schemas, ACLs, webhooks, MCP, translations, or media transfer,
  read [APIs and integrations](references/apis-and-integrations.md).
- For DAL definitions, queries, indexing, product streams, search, and cache
  relevance, read [Data and search](references/data-and-search.md).
- For plugin/app lifecycle, framework APIs, exceptions, constraints, custom
  fields, and scheduled handlers, read
  [Extensions and framework](references/extensions-and-framework.md).
- For workers, caching, filesystems, hosting, environment variables, Redis,
  Varnish, or service reconciliation, read
  [Operations and infrastructure](references/operations-and-infrastructure.md).
- For checkout, payments, customers, orders, rules, addresses, documents, or
  units, read [Commerce and documents](references/commerce-and-documents.md).
