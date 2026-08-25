# Compatibility, Upgrades, and Installation

## Pre-upgrade checks and rollback boundaries

### Stored-expression validation (9.2-9.3)

Run `mysqld --check-table-functions=ABORT` during upgrade preparation. It checks
functions used in constraints, default expressions, partitioning expressions,
and virtual columns. `ABORT` is the default and stops on invalid tables;
`--check-table-functions=WARN` logs the failures and allows an interactive
repair.

### Innovation-release downgrades (9.2-9.3)

Beginning with 9.3, downgrades between individual Innovation releases are not
supported. This includes point-release rollback, such as 9.3.1 to 9.3.0. Restore
from a compatible backup or rebuild instead of starting an older binary on the
upgraded data directory.

### Spatial-index upgrade safety (9.2-9.3)

Before upgrading to 9.2, drop spatial indexes and recreate them afterward. If an
index was carried through the upgrade, recreate it before using the table.
Downgrading can reintroduce the corruption risk. In 9.3,
`CHECK TABLE ... EXTENDED` additionally compares each spatial-index minimum
bounding rectangle with the geometry MBR in the clustered record.

## Removed and deprecated facilities

### Version Tokens (9.2-9.3)

The Version Tokens plugin, its `version_tokens_*()` functions,
`VERSION_TOKEN_ADMIN`, and the `version_tokens_session` variables were deprecated
in 9.2 and removed in 9.3. Remove plugin-loading and application dependencies.

### Removed server, replication, and NDB options (9.2-9.3)

- `replica_parallel_workers` has a minimum of `1`, not `0`.
- `innodb_undo_tablespaces`, `innodb_log_file_size`, and
  `innodb_log_files_in_group` are removed.
- NDB `ndb_restore --restore-privilege-tables` is removed.

### Plugin API and keyring plugins (9.4-9.6)

The server plugin API and `--early-plugin-load` are deprecated. Loading any
keyring plugin emits a deprecation warning. Migrate integrations to components.

### Removed legacy settings and semisynchronous plugins (9.4-9.6)

`temptable_use_mmap`, `group_replication_allow_local_lower_version_join`, and
`replica_parallel_type` are removed. The `semisync_master` and `semisync_slave`
plugins are removed; use `semisync_source` and `semisync_replica`.

### Legacy hashing functions (9.4-9.6)

`MD5()` and `SHA1()` were deprecated in 9.4 and moved out of the server in 9.6.
Install the `classic_hashing` component only for applications that still require
them, and plan to migrate those callers.

## Installation and platform support

### Platform and Configurator support (9.2-9.3)

Enterprise Linux 10 is supported. Windows MySQL Configurator gained a CLI in 9.2
that initially handled only `configure`; from 9.3, its other `--action`
operations execute as well.

### Rootless and side-by-side packages (9.4-9.6)

Debian packages can run under non-root users for rootless installation. Different
Innovation and LTS releases can also be installed side by side.

### Enterprise Linux 7 removal (9.7.2)

Enterprise Linux 7 and the related generic glibc 2.17 builds are no longer
supported. Move deployments to a supported operating system before upgrading.

## Clone across LTS releases

### Newer LTS compatibility (9.7.0)

The Clone plugin supports cloning between consecutive LTS versions higher than
9.7.0. Still validate donor and recipient version compatibility before relying on
Clone as an upgrade or provisioning path.
