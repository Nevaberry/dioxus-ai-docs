# Compatibility, Upgrades, and Installation

Use this reference before changing server binaries, data directories,
platforms, packages, or plugin/component loading.

## Preflight and rollback

### Check stored expressions before upgrade

Since `9.2-9.3`, `mysqld --check-table-functions` checks functions used in
constraints, defaults, partitioning expressions, and virtual columns during an
upgrade. Its default value, `ABORT`, stops on invalid tables. `WARN` logs the
problems and permits interactive repair.

```console
mysqld --check-table-functions=ABORT
```

### Do not downgrade between Innovation releases

Beginning with 9.3, downgrades between individual Innovation releases are
unsupported. This includes point-release rollback, such as 9.3.1 to 9.3.0.
Restore a pre-upgrade backup or rebuild instead of opening the upgraded data
directory with an older server.

### Protect spatial indexes

Before upgrading to 9.2, drop spatial indexes and recreate them afterward. If
an index remains through the upgrade, recreate it before using the table.
Downgrading reintroduces the corruption risk. In 9.3,
`CHECK TABLE ... EXTENDED` also verifies that a spatial-index minimum bounding
rectangle matches the geometry MBR in the clustered record.

### Clone between newer LTS releases

Since `9.7.0`, the Clone plugin supports cloning between consecutive LTS
versions higher than 9.7.0. Confirm that both endpoints form such a consecutive
pair before choosing Clone as the migration path.

## Remove unsupported configuration

### Removed server and NDB options

MySQL 9.3 makes these compatibility changes:

- `replica_parallel_workers` can no longer be `0`; its minimum is `1`.
- `innodb_undo_tablespaces`, `innodb_log_file_size`, and
  `innodb_log_files_in_group` are removed.
- NDB's deprecated `ndb_restore --restore-privilege-tables` option is removed.

Remove these settings and options before starting the newer binaries.

### Move away from the plugin API

In `9.4-9.6`, the server plugin API and `--early-plugin-load` are deprecated.
Loading any keyring plugin produces a deprecation warning. Plan component
migrations instead of adding new plugin-based integrations.

### Replace removed legacy facilities

The following are removed:

- `temptable_use_mmap`
- `group_replication_allow_local_lower_version_join`
- `replica_parallel_type`
- the `semisync_master` and `semisync_slave` plugins

Use `semisync_source` and `semisync_replica` for semisynchronous replication.
Security-specific component replacements and the Version Tokens removal are in
[Security, Authentication, and Components](security-authentication-and-components.md).

## Packages, platforms, and configuration tools

### Supported installation forms

- Enterprise Linux 10 is supported.
- Debian packages can run under a non-root user for rootless installations.
- Different Innovation and LTS releases can be installed side by side.

Treat side-by-side installation as separate instances; it does not make an
in-place downgrade supported.

### MySQL Configurator actions

Windows MySQL Configurator gained a command-line interface in 9.2. Initially it
could only `configure`; in 9.3, its other `--action` operations also execute.
Configurator can also enable the Enterprise Firewall component or upgrade an
existing firewall-plugin installation.

### Move off Enterprise Linux 7

As of `9.7.2`, Enterprise Linux 7 and the associated generic glibc 2.17 builds
are unsupported. Move those deployments to a supported operating system before
upgrading MySQL.
