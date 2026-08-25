# Operations and infrastructure

## Platform and dependency baseline

### Tested database and PHP combinations (since 6.7.13.0)

Shopware 6.7.13.0 is tested on PHP 8.2, 8.4, and 8.5 with MySQL 8 and MariaDB
11.

### Major dependency upgrades

Direct consumers must account for Doctrine DBAL 4, PHPUnit 11, Dompdf 3, and
league/oauth2-server 9. Storefront build customizations must test the upgraded
webpack loaders and plugins rather than assume Shopware's transitive versions
remain compatible.

## Setup and deployment

### Shopware CLI local project

With Docker and Shopware CLI installed, create an interactive local project
and use the generated Make targets:

```bash
shopware-cli project create mystore
cd mystore
make up
make setup
```

The default environment serves Storefront at `http://127.0.0.1:8000` and
Administration at `http://127.0.0.1:8000/admin`, with `admin` / `shopware`
credentials.

### Read-only PaaS deployments

Set any non-empty `SHOPWARE_SKIP_WEBINSTALLER` value to bypass the web
installer and `install.lock` checks. This avoids writes to the project root and
public `.htaccess` on read-only filesystems.

```bash
SHOPWARE_SKIP_WEBINSTALLER=1
```

### Bundle, messaging, and cache defaults

Enable `Shopware\Core\Service\Service` in `config/bundles.php` unless Symfony
Flex applies the recipe. Messages larger than 256 KB are rejected unless
`shopware.messenger.enforce_message_size: false`. Per-item configuration,
snippet, and theme cache-tagging keys have been removed.

## Services and scheduled jobs

### Shopware Services reconciliation (since 6.7.13.0)

The daily `services.install` scheduled task installs newly registered services
and upgrades installed services to the latest registry revision. The process
is idempotent and needs no configuration beyond enabling services.

### Automatic translation updates (since 6.7.13.0)

The daily `translation.update` task performs the same refresh as
`translation:update` and `POST /api/_action/translation/update`. When no
translations are installed, it makes no remote request. Change its
`scheduled_task.run_interval`, or disable it with:

```bash
bin/console scheduled-task:deactivate translation.update
```

## Cache invalidation

The removed `shopware.cache.invalidation.delay` switch is replaced by the
`shopware.invalidate_cache` scheduled-task interval, which defaults to five
minutes.

- Use `sw-force-cache-invalidate: 1` for a critical Admin API write.
- Use `cache:clear:delayed` or `DELETE /api/_action/cache-delayed` to flush
  queued tags.
- Use `cache:watch:delayed` to inspect queued tags.

## Webhook transport

With `WEBHOOKS_REWORK` enabled in 6.7, workers must consume `webhook`
explicitly—preferably before `async` and `low_priority`—or deliveries build up.
The default admin-worker list includes it, but custom
`shopware.admin_worker.transports` lists must add it.

```bash
bin/console messenger:consume webhook async low_priority
```

To roll back, stop webhook workers and run
`bin/console webhook:drain-to-async`. Draining may redeliver messages, so
receivers must deduplicate using `X-Shopware-Event-Id` or the body `eventId`.
Crashed rows left as `running` need manual recovery before draining.

## Varnish and Redis

Varnish cache tags can no longer be stored in Redis. Install the XKeys module
and remove `shopware.http_cache.reverse_proxy.use_varnish_xkey` / `redis_url`.
Define each Redis DSN as a named connection. Then replace the invalidation,
increment, number-range, and cart `dsn` / `url` settings with their respective
`connection` settings.

## Filesystems

### S3 batch writes

`shopware.filesystem.batch_write_size` controls
`AsyncAwsS3WriteBatchAdapter` batches and defaults to 250. Reduce it when batch
operations exhaust file descriptors.

```yaml
shopware:
  filesystem:
    batch_write_size: 100
```

### Visibility placement

Declare filesystem `visibility` beside `type`, not inside the adapter's
`config` object.

## Database and JWT bootstrap

`SQL_SET_DEFAULT_SESSION_VARIABLES` has no effect because `MySQLFactory`
applies MySQL session settings. JWTs are signed only with `APP_SECRET`, which
must be at least 32 characters. `shopware.api.jwt_key.use_app_secret`, custom
RSA JWT secrets, and `system:generate-jwt-secret` are removed.
