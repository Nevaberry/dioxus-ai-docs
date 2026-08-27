# Services and data migrations

Stateful services need application-specific preparation before the operating
system upgrade. Make verified backups, estimate temporary disk use, and test
the migration path with representative data.

## RabbitMQ

### Convert queues before upgrading

Convert classic HA queues to quorum queues before the OS upgrade. There is no
direct broker upgrade path from Bookworm to Trixie.

Debian's recommended reset procedure removes
`/var/lib/rabbitmq/mnesia` after the OS upgrade and then restarts RabbitMQ.
Inventory definitions, messages, credentials, policies, and cluster state;
preserve or arrange to recreate everything required before applying that
destructive reset.

## MariaDB

### Require a clean 10.11 shutdown

MariaDB 11.8 cannot crash-recover a crashed 10.11 data directory. Before the
major upgrade:

1. Stop MariaDB under 10.11.
2. Confirm `Shutdown complete` in the logs.
3. Only then proceed to 11.8.

If shutdown was unclean, recover the directory with MariaDB 10.11, verify the
data, and stop it cleanly again before installing 11.8.

## Dovecot

### Port configuration before the OS upgrade

Dovecot 2.4 uses a configuration format incompatible with earlier releases,
and the `replicator` feature has been removed. Port the production
configuration and test authentication, delivery, retrieval, TLS, and any
replacement replication design before starting the OS upgrade.

## Bacula

### Reserve time and disk for the schema migration

The director database migration can take hours or days. It temporarily needs
about twice the database's current disk usage, plus room for a dump under
`/var/cache/dbconfig-common/backups`.

Measure free space on every affected filesystem before beginning. Exhausting
disk space during the migration can corrupt the database, so stop rather than
starting with marginal headroom.

## WirePlumber

### Port custom configuration

WirePlumber uses a new configuration system. Default installations need no
action, but custom setups must be ported using
`/usr/share/doc/wireplumber/NEWS.Debian.gz` and tested for the intended audio
routing and policy behavior.

## Timezone compatibility

### Keep tzdata-legacy for copied legacy names

Timezone names outside the region/city scheme, including `US/*`, moved to
`tzdata-legacy`. The system timezone is converted automatically, but a database
or service may have copied an old identifier into its own configuration or
data. Search those consumers and keep `tzdata-legacy` installed until every
legacy name is migrated.

All service migration items in this reference come from batch
`13-known-issues`.
