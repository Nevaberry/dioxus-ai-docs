# Services and data migrations

The migration requirements in this reference are from `13-known-issues`.

## RabbitMQ

### Convert queues before the operating-system upgrade

Classic HA queues must become quorum queues before upgrading. There is no direct
Bookworm-to-Trixie broker upgrade path.

Debian's reset procedure removes `/var/lib/rabbitmq/mnesia` after the OS upgrade and
then restarts the service. Inventory durable definitions and application-owned state,
preserve what is required, and prove that it can be recreated before accepting that
destructive step.

## MariaDB

### Require a clean 10.11 shutdown

MariaDB 11.8 cannot crash-recover a crashed 10.11 data directory. Stop MariaDB before
the package upgrade and confirm `Shutdown complete` in its logs.

If the stop was unclean, recover the directory under 10.11 first. Then stop it cleanly
and re-check the logs before moving to 11.8.

## Dovecot

### Port configuration before downtime begins

Dovecot 2.4 uses a configuration format incompatible with earlier releases, and the
`replicator` feature is removed. Port and test the production mail configuration
before the OS upgrade. Do not rely on converting it during a maintenance window with
the service already unavailable.

## Bacula

### Reserve time, migration space, and dump space

The director database schema migration can take hours or days. It temporarily needs
about twice the database's current disk use, plus space for a dump under
`/var/cache/dbconfig-common/backups`.

Measure free space and migration duration in advance. Exhausting disk during the
migration can corrupt the database, so define a stop threshold and recovery plan
before upgrading.
