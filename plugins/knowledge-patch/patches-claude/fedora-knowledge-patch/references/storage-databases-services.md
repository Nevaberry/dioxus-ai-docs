# Storage, Databases, and Network Services

## Contents

- Storage and encryption
- Database transitions
- Directory, mail, proxy, and application services

## Storage and encryption

### dm-vdo support (41)

Fedora provides the `dm-vdo` device-mapper target and the `vdoformat`,
`vdostats`, and `vdoforcerebuild` commands in the `vdo` tools package. Manage
VDO through LVM2 where possible. Existing kvdo volumes need migration-specific
checks before conversion.

### Stratis snapshot reversion (41)

Use the `schedule-revert` and `cancel-revert` filesystem subcommands to replace
a Stratis filesystem with one of its snapshots. A scheduled revert happens
only when the pool next starts, such as after stopping and restarting the pool
or the relevant service or system.

### Stratis supports multiple encryption bindings (42)

Stratis 3.8 supports as many as 15 keyring or Clevis bindings on one encrypted
pool. Pool start can try all bindings with `--unlock-method=any`, select one
with `--token-slot`, accept a passphrase with `--capture-key`, or read a key
with `--keyfile-path`. Unbind and ambiguous rebind operations also require the
token slot.

## Database transitions

### Redis-to-Valkey migration (41)

An upgrade replaces Redis with Valkey through `valkey-compat`. The package
migrates common configuration and data layouts and supplies Redis-compatible
systemd unit aliases. Treat it as transitional and migrate deployment names,
units, configuration, and automation to Valkey directly.

### PostgreSQL 15 is retired (42)

Fedora 42 keeps PostgreSQL 16 as the default and 17 as an alternative but
removes 15. For a remaining 15 installation, back it up and either dump and
restore or replace the packages, install `postgresql-upgrade`, and run
`postgresql-setup --upgrade`.

### PostgreSQL 18 becomes the default stream (43)

Unversioned `postgresql` and `libpq` move from PostgreSQL 16 to 18 while Fedora
retains its parallel versioned packaging. Plan the database upgrade rather
than treating the unversioned package update as ABI-neutral.

### MySQL 8.4 becomes the distribution default (43)

Fedora uses versioned MySQL families such as `mysql8.0-server` and
`mysql8.4-server`. The distribution default moves from 8.0 to 8.4; select a
versioned family explicitly when the deployment cannot follow the default.

### MariaDB 11.8 becomes the distribution default (44)

Unversioned packages such as `mariadb-server` select MariaDB 11.8 instead of
10.11. Administrators must perform the database upgrade. The previous line
remains available as versioned `mariadb10.11-*` packages.

### `community-mysql` package names disappear (44)

All `community-mysql*` package names are removed. Stop installing, depending
on, or checking for those names; use Fedora's current MySQL package families.

## Directory, mail, proxy, and application services

### Apache Traffic Server uses YAML configuration (42)

Traffic Server 10 automatically converts
`/etc/trafficserver/records.config` to `records.yaml`. APIs and features
removed in the 10.x major line require additional manual migration.

### Cockpit Files replaces Navigator (42)

`cockpit-files` obsoletes `cockpit-navigator` and provides a **File browser**
under Cockpit's **Tools** menu. It covers Navigator's operations except symlink
creation; use another method for that workflow.

### Dovecot moves to the 2.4 major line (43)

Treat Fedora's move from Dovecot 2.3.x to 2.4.x as a major-version migration
for the mail server, its configuration, plugins, and dependent services.

### 389 Directory Server requires LMDB (43)

Berkeley DB is no longer a supported active backend for 389 Directory Server.
Migrate existing BDB deployments to LMDB; any remaining BDB access is for
migration only.

### Tomcat moves from 9.0 to 10.1 (43)

Fedora's Tomcat server, related libraries, and services move from 9.0.x to
10.1.x. Port applications and deployment configuration for this major server
transition.
