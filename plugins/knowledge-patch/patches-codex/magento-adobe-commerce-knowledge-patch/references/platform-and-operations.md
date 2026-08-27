# Platform and Operations

## Adobe Commerce runtime and dependency floor

For Adobe Commerce (`2.4.8-adobe-commerce`), PHP 8.4 and PHP 8.3 are supported.
PHP 8.2 is compatible only for upgrading, and PHP 8.1 support is removed. An
installation on PHP 8.1 must move to PHP 8.3 before the Commerce upgrade.

Custom test suites should move from PHPUnit 9 to PHPUnit 10. Other dependency
changes include:

- Composer 2.8.x
- Monolog 3.x
- TinyMCE 6.8.5, with TinyMCE 5 removed
- Replacement of `laminas-file`, `laminas-mail`, `laminas-mime`, and
  `laminas-oauth`

## Adobe Commerce services and search

The supported service set adds Valkey 8.x, MariaDB 11.4 LTS, MySQL 8.4 LTS,
and RabbitMQ 4.x. MariaDB 10.6 and MySQL 8.0 remain supported.

RabbitMQ 4 does not support classic mirrored queues. Both cloud and on-premises
deployments must migrate classic mirrored queues to quorum queues before moving
to RabbitMQ 4.

OpenSearch 2.19 is the search target. Elasticsearch is no longer compatible,
although its Admin options and code remain deprecated.

## MySQL schemas

MySQL schemas default to `utf8mb4` instead of deprecated `utf8mb3`.

MySQL 8.4 enables `restrict_fk_on_non_standard_key` by default. During the
upgrade, existing Commerce schemas require either:

```ini
restrict_fk_on_non_standard_key=OFF
```

or the server option:

```text
--skip-restrict-fk-on-non-standard-key
```

## Security administration

Duo 2FA uses Web SDK v4 and Universal Prompt. Admin configuration requires a
Client ID and Secret. The OTP Window default changes from `1` to `29`.

Encryption-key changes and re-encryption of supported configuration, payment,
and custom-field data are CLI-only.

SRI hashes live under `pub/static` by area and therefore survive cache flushes.

The **System > Support > Data Collector** tool is removed.

## Indexing, ACL, and locked configuration

New indexers default to **Update by Schedule**, while existing indexer modes are
preserved. Switching an index back to **Update on Save** removes its unused
changelog tables and marks it invalid.

Permissions introduced by custom modules are no longer automatically granted
to existing roles.

Values locked with `config:set --lock-env` or `config:set --lock-conf` cannot be
changed through Admin forms.

## Adobe Commerce CLI behavior

`dev:di:info` can target an application area instead of only GLOBAL.

`setup:di:compile` fails on preferences for missing or excluded classes.

Magento CLI supports Symfony `CommandLoaderInterface` for deferred command
initialization.

Maintenance-mode IP allowlists accept CIDR ranges. `maintenance:status`
reports **enabled/disabled** instead of **active/not active**.

## Cache behavior

The built-in full-page cache removes marketing query parameters in the same way
as Varnish, preventing campaign parameters from multiplying cache entries.
Varnish exclusions include `gad_source`, `srsltid`, and `msclkid`.

Redis cache garbage collection enables Lua mode by default to avoid cache-tag
cleanup races.

## Magento Open Source dependencies

Magento Open Source (`2.4.8-magento-open-source`) changes these dependencies:

- `league/flysystem` moves from 2.x to 3.x.
- `wikimedia/less.php` moves to 5.x.
- `php-amqplib` moves to `^3`.
- jQuery Validate moves to 1.20.0.
- Moment.js moves to 2.30.1.
- RequireJS moves to 2.3.7.
- `colinmollenhour/php-redis-session-abstract` moves to 2.0.0 and adds Redis
  session connection retries.
- Composer declares the PHP FTP extension needed for CSV imports over FTP.

## Magento Open Source environment and scheduled work

`MAGENTO_DC_INDEXER__USE_APPLICATION_LOCK` parses `false` as a Boolean rather
than a truthy string, so this setting disables application locking as intended:

```dotenv
MAGENTO_DC_INDEXER__USE_APPLICATION_LOCK=false
```

Cron groups running in separate processes retain both standard output and
standard error in logs.

Admin adds an **Export VCL for Varnish 7** action.

## Region configuration during upgrades

When an upgrade adds a country with required states or regions, it adds only
that country to `general/region/state_required`. It does not reset the
merchant's configured list to the default set.
