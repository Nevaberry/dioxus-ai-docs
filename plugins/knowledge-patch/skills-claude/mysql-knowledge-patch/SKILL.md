---
name: mysql-knowledge-patch
description: MySQL
version: 9.7.0
license: MIT
metadata:
  author: Nevaberry
---


# MySQL Knowledge Patch

Use this skill when writing MySQL SQL, planning an upgrade, changing
authentication or replication, sizing a server, operating InnoDB, or adopting
JSON Duality Views and stored JavaScript. Check the relevant reference before
relying on older defaults, plugins, client behavior, or downgrade procedures.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compatibility, Upgrades, and Installation](references/compatibility-upgrades-and-installation.md) | Upgrade checks, rollback limits, removed facilities, spatial-index safety, Clone, packages, platform support |
| [Security, Authentication, and Components](references/security-authentication-and-components.md) | Privileges, authentication policy, password storage, roles, connection control, keyrings, firewall, masking |
| [Replication and High Availability](references/replication-and-high-availability.md) | Version compatibility, encrypted connections, GTIDs, Group Replication, retries, binary-log behavior |
| [SQL, Schema, and Optimizer](references/sql-schema-and-optimizer.md) | Primary-key equivalents, DDL algorithms, keywords, collation, subqueries, EXPLAIN, temporal validation, optimizer behavior |
| [JSON Duality Views and MLE](references/json-duality-and-mle.md) | Duality View definition and DML, stored JavaScript types and APIs, reusable libraries, WebAssembly |
| [Server, InnoDB, and Resource Sizing](references/server-innodb-and-resource-sizing.md) | Containers and cgroups, automatic sizing, change buffering, log writers, Thread Pool, redo diagnostics |
| [Clients, Observability, and Audit](references/clients-observability-and-audit.md) | mysql and mysqldump, Option Tracker, telemetry, account locks, diagnostics, Audit Log |

## Check migration blockers first

### Do not automate Innovation-release rollback

Downgrades between individual Innovation releases are unsupported, including a
rollback between point releases. Treat rollback as restore or rebuild work, not
as starting an older binary over the upgraded data directory.

### Protect spatial indexes during upgrade

Before an affected upgrade, drop spatial indexes and recreate them afterward.
If they remain through the upgrade, recreate them before querying their tables.
Use `CHECK TABLE ... EXTENDED` afterward to compare each spatial-index MBR with
the geometry MBR stored in the clustered record.

### Validate stored expressions

Ask the server to inspect functions used in constraints, defaults, partitioning
expressions, and virtual columns:

```console
mysqld --check-table-functions=ABORT
```

`ABORT` is the default and stops on invalid tables. Use `WARN` only when an
interactive repair procedure is ready.

### Replace removed and deprecated facilities

- Remove Version Tokens plugin loading, functions, privileges, and variables.
- Migrate server plugins and keyring plugins to components; the plugin API and
  `--early-plugin-load` are deprecated.
- Replace `semisync_master` and `semisync_slave` with `semisync_source` and
  `semisync_replica`.
- Install `classic_hashing` only when an application still needs `MD5()` or
  `SHA1()`.
- Remove configuration for settings that no longer exist, including
  `innodb_log_file_size`, `innodb_log_files_in_group`, and
  `innodb_undo_tablespaces`.

Read [Compatibility, Upgrades, and Installation](references/compatibility-upgrades-and-installation.md)
for the full removal and installation details.

## Update security configuration deliberately

### Stop depending on privilege-cache flushes

Account-management statements update privileges directly. `FLUSH PRIVILEGES`,
its dedicated privilege, related mysqladmin commands, SIGHUP-based flushing,
and using the statement to clear the caching-SHA-2 cache are deprecated.

### Choose password storage independently of clients

`caching_sha2_password` can store credentials with PBKDF2 and SHA-512,
including for X Protocol authentication. Administrators can change or enforce
the storage format without client changes. Review the digest-round setting as
well; its newer default is `10000`.

### Account for automatic role activation

`activate_mandatory_roles` is enabled by default. When
`activate_all_roles_on_login` is off, mandatory roles supplement default
roles. When it is on, mandatory and granted roles activate regardless of the
new setting.

### Use components and policy DDL

Prefer the connection-control, firewall, and keyring components over their
deprecated plugin predecessors. Enterprise masking policies attach to
base-table columns and can use `CURRENT_ROLE_IN()` or `CURRENT_USER_IN()` as
policy gatekeepers.

## Recheck changed command and server defaults

### Enable mysql client commands explicitly

Most commands in the **mysql** client are disabled unless requested:

```console
mysql --commands=ON
```

Audit interactive tooling and scripts that expect client-side commands.

### Make replication intent explicit

Replication connections now default to encryption, and GTID mode defaults on.
Confirm certificates and topology behavior instead of assuming an unencrypted
or anonymous setup. A lower-version replica requires
`replica_allow_higher_version_source` before accepting a higher-version source.

### Re-baseline plans and diagnostics

`explain_format` defaults to `TREE`, while JSON EXPLAIN defaults to format
version 2. Consumers must recognize schema `2.0`, the reduced top-level shape,
and `lookup_references`.

### Recheck automatic sizing

The server observes container CPU and memory limits, including cpuset
assignments. `server_memory` limits the physical-memory value used to derive
defaults; it is not a hard cap on process memory. Explicitly configured values
remain the safest way to preserve a tuned deployment.

## Use current SQL and schema behavior

### Avoid unnecessary generated invisible primary keys

A `UNIQUE NOT NULL` key is a primary-key equivalent for `CREATE` and `ALTER`.
It satisfies `sql_require_primary_key=ON` and prevents an extra generated
invisible primary key when `sql_generate_invisible_primary_key=ON`:

```sql
CREATE TABLE events (
  event_id BIGINT NOT NULL UNIQUE,
  payload JSON
);
```

### Expect empty-table column changes to use INPLACE

For an empty InnoDB table, adding or dropping a column selects `INPLACE`
rather than `INSTANT` by default. This avoids consuming a row version; do not
assert `INSTANT` in automation unless that algorithm is specifically required.

### Opt into the Hypergraph Optimizer at the right scope

The Hypergraph Optimizer is available in Community Edition and can be selected
at session, global, persisted, startup, or statement scope:

```sql
SET optimizer_switch='hypergraph_optimizer=on';
```

## Adopt JSON Duality View DML consciously

Duality View definitions grant or deny `INSERT`, `UPDATE`, and `DELETE` per
table. Runtime DML is checked against those tags. Community Server permits all
three DML forms through the views and supports auto-increment columns,
including automatic primary-key generation.

Documents selected from a Duality View include `_metadata.etag`. Use the four
`JSON_DUALITY_VIEW*` Information Schema tables to inspect the mapping instead
of reverse-engineering the generated document.

## Build stored JavaScript with the expanded MLE APIs

Stored JavaScript accepts `ENUM`, `SET`, `BIT`, and full `DECIMAL`/`NUMERIC`
input, output, binding, and return paths. Decimal values are strings by default;
request `decimalType=NUMBER` only when JavaScript numeric precision is
acceptable.

Reusable libraries support create, alter, status, comments, routine `USING`
clauses, and dynamic imports. A WebAssembly library can be encoded as
hexadecimal or base64:

```sql
CREATE LIBRARY math_wasm
  LANGUAGE WASM
  AS '0061736d...';
```

WebAssembly libraries cannot call MySQL-specific APIs or WASI system, clock,
or I/O services. See [JSON Duality Views and MLE](references/json-duality-and-mle.md)
for transaction, routine-call, localization, and memory details.

## Make telemetry and audit configuration explicit

Telemetry logs, metrics, and traces default off, and OTLP endpoints have no
default. Configure each signal and endpoint deliberately. Linux exporters may
be placed in separate network namespaces, and exporter credentials may come
from external secret-header providers.

The component-based Audit Log supports time-based rotation and startup recovery
from invalid filters. Pick a recovery mode explicitly where logging everything,
logging nothing, and aborting startup have materially different risks.
