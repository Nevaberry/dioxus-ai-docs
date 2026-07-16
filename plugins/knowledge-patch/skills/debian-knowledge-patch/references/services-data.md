# Services and data migrations

## RabbitMQ queues and broker state

Convert classic HA queues to quorum queues before upgrading. There is no direct
Bookworm-to-Trixie broker upgrade path.

Debian's recommended reset is to remove `/var/lib/rabbitmq/mnesia` after the operating
system upgrade and restart the service. Preserve or recreate any needed state before
using this destructive procedure.

## MariaDB crash-recovery boundary

MariaDB 11.8 cannot perform crash recovery on a crashed 10.11 data directory. Stop
MariaDB before upgrading and confirm `Shutdown complete` in its logs.

If shutdown was unclean, recover under 10.11 and then stop it cleanly again before the
major upgrade.

## Dovecot configuration migration

Dovecot 2.4 uses a configuration format incompatible with earlier releases, and the
`replicator` feature has been removed. Port and test production mail configurations
before the operating system upgrade instead of accepting extended downtime during it.

## Bacula database schema

The Bacula director database migration can take hours or days. It temporarily needs
about twice the database's current disk use, plus room for a dump under
`/var/cache/dbconfig-common/backups`.

Running out of disk space during the migration can corrupt the database.

## WirePlumber custom configuration

WirePlumber uses a new configuration system. Defaults need no action, but port custom
setups by using `/usr/share/doc/wireplumber/NEWS.Debian.gz`.

## Legacy timezone names

Names outside the region/city scheme, including `US/*`, moved to `tzdata-legacy`.
The system timezone is converted automatically. Databases and services that copied an
old name may still require `tzdata-legacy` to remain installed.
