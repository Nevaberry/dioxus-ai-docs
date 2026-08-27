# Extensions, Modules, and Foreign Data Wrappers

Use this reference when writing or deploying extensions, foreign data
wrappers, test hooks, or bundled modules. Version-sensitive items are from the
`17.0` and `18.0` batches.

## Adapt extension and access-method integrations

PostgreSQL 17 supports custom wait-event registration. Foreign data wrappers
and custom scans must also handle pushed-down joins that carry non-join
qualifications.

Bundled access-method changes include:

- `ltree` supports hash indexes, hash joins, and hash aggregation.
- `unaccent.rules` can represent whitespace and quotes.
- `pg_amcheck --checkunique` verifies unique constraints.

PostgreSQL 18 adds `PG_MODULE_MAGIC_EXT`, allowing an extension to report its
name and version through `pg_get_loaded_modules()`. Extensions can register
custom `EXPLAIN` options and use cumulative statistics.

## Use the expanded injection-point test API

PostgreSQL 18 separates injection-point loading from execution through
`INJECTION_POINT_LOAD()` and `INJECTION_POINT_CACHED()`. Injection points can
receive runtime arguments, and `IS_INJECTION_POINT_ATTACHED()` tests whether a
named point is attached.

## Inspect internals and manage shared-buffer caches

PostgreSQL 18 adds `pg_logicalinspect` for inspecting logical snapshots and
`pg_overexplain` for debug-level plan details. amcheck adds
`gin_index_check()` for GIN verification.

`pg_buffercache_evict_relation()` and `pg_buffercache_evict_all()` evict
unpinned shared buffers. Treat these as operationally disruptive cache tools,
not ordinary monitoring calls.

## Configure extension discovery

`extension_control_path` selects the locations searched for extension control
files in PostgreSQL 18. Account for it in packaging and deployment code rather
than assuming the compiled-in extension directory is the only source.

## Use SCRAM passthrough for remote connections

PostgreSQL 18 `postgres_fdw` option `use_scram_passthrough` forwards the
client's SCRAM authentication instead of storing remote credentials. It uses
libpq's `scram_client_key` and `scram_server_key`; dblink supports the same
passthrough.

`postgres_fdw_get_connections()` now reports transaction use, closed state,
user name, and remote backend PID.

## Tolerate bad file_fdw rows deliberately

PostgreSQL 18 `file_fdw` adds `on_error`, `log_verbosity`, and `reject_limit`,
matching tolerant `COPY` behavior. Bound rejections rather than allowing an
unlimited number of malformed rows to disappear.

## Configure bundled validation modules

`passwordcheck.min_password_length` sets the minimum accepted password length.
The `isn.weak` setting controls whether invalid check digits are accepted.

## Select pgcrypto behavior

PostgreSQL 18 pgcrypto supports `sha256crypt`, `sha512crypt`, and CFB cipher
mode. `fips_mode()` reports server state, while `builtin_crypto_enabled` can
disable built-in non-FIPS cryptographic functions.
