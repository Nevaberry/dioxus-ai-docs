# Platform upgrades and services

## Adobe Commerce runtime and dependency floor

For Adobe Commerce 2.4.8 (`2.4.8-adobe-commerce`):

- PHP 8.4 and 8.3 are supported.
- PHP 8.2 is compatible only for upgrading.
- PHP 8.1 support is removed. An installation on PHP 8.1 must move to PHP 8.3
  before the Commerce upgrade.
- Custom test suites should move from PHPUnit 9 to PHPUnit 10.
- Notable dependency changes include Composer 2.8.x and Monolog 3.x.
- TinyMCE moves to 6.8.5, and TinyMCE 5 is removed.
- `laminas-file`, `laminas-mail`, `laminas-mime`, and `laminas-oauth` are
  replaced.

## Adobe Commerce service compatibility

Adobe Commerce 2.4.8 adds support for:

- Valkey 8.x
- MariaDB 11.4 LTS
- MySQL 8.4 LTS
- RabbitMQ 4.x

MariaDB 10.6 and MySQL 8.0 remain supported.

RabbitMQ 4 does not support classic mirrored queues. Both cloud and on-premises
deployments must migrate them to quorum queues first.

OpenSearch 2.19 is the search target. Elasticsearch is no longer compatible,
even though its Admin options and code remain deprecated.

## MySQL schema requirements

Adobe Commerce MySQL schemas now default to `utf8mb4` instead of deprecated
`utf8mb3`.

MySQL 8.4 enables `restrict_fk_on_non_standard_key` by default. Existing
Commerce schemas require one of the following during the upgrade:

```ini
restrict_fk_on_non_standard_key=OFF
```

```text
--skip-restrict-fk-on-non-standard-key
```

## Magento Open Source dependency migrations

For Magento Open Source 2.4.8 (`2.4.8-magento-open-source`):

- `league/flysystem` moves from 2.x to 3.x.
- `wikimedia/less.php` moves to 5.x.
- `php-amqplib` moves to `^3`.
- jQuery Validate moves to 1.20.0.
- Moment.js moves to 2.30.1.
- RequireJS moves to 2.3.7.
- `colinmollenhour/php-redis-session-abstract` moves to 2.0.0 and gains Redis
  session connection retries.
- Composer declares the PHP FTP extension needed for CSV imports over FTP.

The jQuery/fileUploader and ExtJS folders are removed following migration to
Uppy and jsTree. Extensions must stop importing those legacy assets.

## Magento Open Source editor integration

Magento Open Source migrates TinyMCE 5.10.2 to 7.3.0, including its Page Builder
integration. Custom editor integrations must target TinyMCE 7. Plugin widget
functions are again callable through the returned widget object for backward
compatibility.

## Magento Open Source extension compatibility

`Magento\Catalog\Model\ProductRepository` restores the Initialization Helper as
its second constructor parameter so existing subclasses retain their prior
contract.

`setup:di:compile` generates interceptor methods correctly for plugins
configured through virtual types, matching runtime compilation behavior.
