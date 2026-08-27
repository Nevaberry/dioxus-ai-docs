# Platform, Builds, and Operations

## Runtime and dependency requirements

### Tested platform versions (6.7.13.0)

Shopware 6.7.13.0 is tested on PHP 8.2, 8.4, and 8.5, with MySQL 8 and MariaDB 11.

### Dependency baseline

The 6.7 dependency baseline includes Doctrine DBAL 4, PHPUnit 11, Dompdf 3, and league/oauth2-server 9. Direct consumers must account for these major upgrades. Storefront build customizations must test the upgraded webpack loaders and plugins instead of assuming Shopware's transitive versions remain compatible.

### Formerly transitive Composer packages (6.7.13.0)

`doctrine/inflector`, `symfony/monolog-bridge`, and `symfony/proxy-manager-bridge` are deprecated as Shopware dependencies and will disappear in the next major. Extensions using them must declare them in their own `composer.json`.

## Local development and production builds

### Shopware CLI local-project quickstart (developer-release-notes-index)

With Docker and Shopware CLI installed, create an interactive local project and use its generated Make targets to start and initialize it:

```bash
shopware-cli project create mystore
cd mystore
make up
make setup
```

The default environment serves the Storefront at `http://127.0.0.1:8000` and Administration at `http://127.0.0.1:8000/admin`, with `admin` / `shopware` credentials.

### Minimal plugin skeletons (6.7.13.0)

`plugin:create` accepts `--no-scaffold` to generate only the required plugin skeleton:

```bash
bin/console plugin:create MyPlugin MyNamespace --no-scaffold
```

### Production sourcemaps (6.7.13.0)

Production sourcemaps are opt-in. Set `GENERATE_SOURCEMAPS=true` with `NODE_ENV=production` for Storefront webpack and Administration, extension, or Storefront-component Vite builds. Other values preserve the production default of no sourcemaps; non-production builds always generate them.

```bash
GENERATE_SOURCEMAPS=true NODE_ENV=production composer build:js:admin
GENERATE_SOURCEMAPS=true NODE_ENV=production composer build:js:storefront
```

## Scheduled work and upgrade repairs

### Shopware Services reconciliation (6.7.13.0)

The daily `services.install` task upgrades installed services to the latest registry revision and installs newly registered services. Reconciliation is idempotent and needs no configuration beyond enabling services.

### Automatic translation updates (6.7.13.0)

The daily `translation.update` task performs the same refresh as `translation:update` and `POST /api/_action/translation/update`. It makes no remote request when no translations are installed. Change its `scheduled_task.run_interval`, or disable it with:

```bash
bin/console scheduled-task:deactivate translation.update
```

### Description teaser backfill (6.7.13.0)

`product.description_teaser.indexer` runs once through the post-update flow and no longer runs under `bin/console dal:refresh:index`. It repairs missing or stale teasers for pre-6.7.12 products; subsequent product writes synchronize the field directly.

### Scheduled-task execution contracts (6.7.13.0)

Container-registered handlers need no changes. Manually instantiated `ScheduledTaskHandler` objects must receive a `ScheduledTaskExecutor` through `setScheduledTaskExecutor()`. Inline handler orchestration and `markTaskRunning()`, `markTaskFailed()`, and `rescheduleTask()` are deprecated. Implement `DynamicallyScheduledTaskHandler::getNextExecutionTime()` for a non-default next run time.

Custom `ScheduledTaskHandler` constructors also require `LoggerInterface` as their second dependency.

## Queues, caches, and search infrastructure

### Dedicated webhook transport

With `WEBHOOKS_REWORK` enabled in 6.7, workers must consume `webhook`, preferably before `async` and `low_priority`, or deliveries accumulate. The default admin-worker list includes it; custom `shopware.admin_worker.transports` lists must add it.

```bash
bin/console messenger:consume webhook async low_priority
```

To roll back, stop webhook workers and run `bin/console webhook:drain-to-async`. Draining can redeliver messages, so receivers must deduplicate using `X-Shopware-Event-Id` or the body `eventId`. Manually recover crashed rows left as `running` before draining.

### Delayed cache invalidation

The removed `shopware.cache.invalidation.delay` switch is replaced by the `shopware.invalidate_cache` scheduled-task interval, which defaults to five minutes. Use `sw-force-cache-invalidate: 1` for a critical Admin API write, `cache:clear:delayed` or `DELETE /api/_action/cache-delayed` to flush queued tags, and `cache:watch:delayed` to inspect them.

### Storefront Elasticsearch reindex

`TranslatedField::$useForSorting` identifies sortable Elasticsearch fields, and search avoids nested queries. Run `bin/console es:index` after upgrading so the new mappings and implementation take effect.

### OpenSearch 3 empty object mappings

OpenSearch 3 rejects an array-valued empty `properties` member. Omit an empty `properties` member or use an object:

```json
{"customFields":{"type":"object","properties":{}}}
```

## Filesystems and deployment

### Read-only web-installer bypass

Set any non-empty `SHOPWARE_SKIP_WEBINSTALLER` value to skip the web installer and `install.lock` checks, avoiding writes to the project root and public `.htaccess` on read-only filesystems.

```bash
SHOPWARE_SKIP_WEBINSTALLER=1
```

### S3 batch size

`shopware.filesystem.batch_write_size` controls `AsyncAwsS3WriteBatchAdapter` batches and defaults to 250. Reduce it when batch operations exhaust file descriptors.

```yaml
shopware:
  filesystem:
    batch_write_size: 100
```

### Filesystem visibility

Declare filesystem `visibility` beside `type`, not inside the adapter's `config` object.

### Varnish XKeys and named Redis connections

Varnish cache tags can no longer be stored in Redis. Install the XKeys module and remove `shopware.http_cache.reverse_proxy.use_varnish_xkey` and `redis_url`. Define each Redis DSN as a named connection, then replace invalidation, increment, number-range, and cart `dsn` / `url` keys with their corresponding `connection` keys.

### Hosting defaults

Enable `Shopware\Core\Service\Service` in `config/bundles.php` unless Symfony Flex applies the recipe. Search indices inherit shard and replica counts from the server. Messages over 256 KB are rejected unless `shopware.messenger.enforce_message_size: false`. Per-item configuration, snippet, and theme cache-tagging keys have been removed.

### Database session and JWT bootstrap settings

`SQL_SET_DEFAULT_SESSION_VARIABLES` has no effect because `MySQLFactory` applies MySQL session settings. JWTs are signed only with `APP_SECRET`, which must be at least 32 characters. `shopware.api.jwt_key.use_app_secret`, custom RSA JWT secrets, and `system:generate-jwt-secret` are removed.
