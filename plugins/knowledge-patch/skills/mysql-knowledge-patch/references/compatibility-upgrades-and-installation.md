# Compatibility, Upgrades, and Installation

Use this reference before changing server binaries, package layouts, plugins, or
stored data. The guidance is grouped by migration task rather than release order.

## Upgrade and downgrade guardrails

### Innovation releases cannot be downgraded

Beginning with the behavior captured in batch 9.2-9.3, downgrades between
individual Innovation releases are unsupported. This includes point-release
rollback such as 9.3.1 to 9.3.0. Recover by restoring or rebuilding instead of
starting an older binary on the upgraded data directory.

### Validate stored expressions during upgrade

The `--check-table-functions` server option checks functions used by:

- constraints;
- default expressions;
- partitioning expressions; and
- virtual columns.

Its default value, `ABORT`, stops an upgrade when a table is invalid. Running
`mysqld --check-table-functions=WARN` logs invalid tables and permits interactive
repair. Do not use `WARN` without a repair plan.

### Rebuild spatial indexes safely

Before upgrading to MySQL 9.2 (in batch 9.2-9.3), drop spatial indexes and
recreate them after the upgrade. If an index was carried across, recreate it
immediately before using its table. A downgrade reintroduces the corruption risk.

In MySQL 9.3, `CHECK TABLE ... EXTENDED` also verifies that a spatial-index
minimum bounding rectangle matches the geometry MBR in the clustered record.
Include that check in post-upgrade validation.

### Account for system-account authentication changes

An upgrade from MySQL 5.7 to a later series changes the server-created `mysql.sys`
and `mysql.session` accounts from `mysql_native_password` to
`caching_sha2_password`. Check monitoring and maintenance paths that authenticate
as those accounts.

## Remove obsolete configuration

### Removed server settings and NDB option

The following are removed in batch 9.2-9.3:

- `replica_parallel_workers=0`; the minimum is now `1`;
- `innodb_undo_tablespaces`;
- `innodb_log_file_size`;
- `innodb_log_files_in_group`; and
- NDB `ndb_restore --restore-privilege-tables`.

The following are removed in batch 9.4-9.6:

- `temptable_use_mmap`;
- `group_replication_allow_local_lower_version_join`;
- `replica_parallel_type`;
- the `semisync_master` plugin; and
- the `semisync_slave` plugin.

Use `semisync_source` and `semisync_replica` for semisynchronous replication.
Remove obsolete names rather than leaving ignored settings in configuration.

### Version Tokens is gone

MySQL 9.2 deprecated the Version Tokens plugin, all `version_tokens_*()`
functions, the `VERSION_TOKEN_ADMIN` privilege, and the
`version_tokens_session` variables. MySQL 9.3 removes the plugin. Remove plugin
loading and migrate any coordination scheme that uses its tokens.

### The plugin API is being replaced by components

The server plugin API and `--early-plugin-load` are deprecated in batch
9.4-9.6. Loading any keyring plugin emits a deprecation warning. Prefer the
corresponding component and its component configuration.

### Move legacy hashes to a component

`MD5()` and `SHA1()` were deprecated in MySQL 9.4 and moved out of the server in
MySQL 9.6. Install the `classic_hashing` component only when an application still
requires those functions; otherwise migrate stored hashes and SQL calls.

## Installation and platform behavior

### Rootless and side-by-side installation

In batch 9.4-9.6, Debian packages can run under non-root users for rootless
installations. Different Innovation and LTS releases can also be installed side
by side. Keep paths, service identities, ports, sockets, and data directories
distinct.

### Platform and Configurator support

Enterprise Linux 10 is supported in batch 9.2-9.3. On Windows, MySQL
Configurator gained a CLI in MySQL 9.2. Its initial `configure`-only limitation
was lifted in MySQL 9.3, so other `--action` operations execute as well.

### Clone compatibility

As recorded in batch 9.7.0, the Clone plugin supports cloning between consecutive
LTS versions higher than 9.7.0. This is a consecutive-LTS allowance, not general
cross-version compatibility; verify both endpoints before automating a clone.

## Edition availability

Community Edition in batch 9.7.0 includes these components:

- Replication Applier Metrics;
- Group Replication Flow Control Statistics;
- Group Replication Resource Manager;
- Group Replication Primary Election; and
- Telemetry.

Community Edition also gains the Hypergraph Optimizer and DML through JSON
Duality Views. Edition availability does not enable or configure these features
automatically.
