# Extensions, Modules, and Foreign Data Wrappers

## Use extension-facing additions (17.0)

`ltree` supports hash indexes, hash joins, and hash aggregation.
`unaccent.rules` can represent whitespace and quotes. Use
`pg_amcheck --checkunique` to verify unique constraints. Extensions can
register custom wait events. Foreign data wrappers and custom scans must
handle pushed-down joins that include non-join qualifications.

## Locate extension controls (18.0)

`extension_control_path` selects the locations searched for extension control
files.

## Report extension identity and integrate with testing (18.0)

`PG_MODULE_MAGIC_EXT` lets an extension expose its name and version through
`pg_get_loaded_modules()`. Extensions can register custom `EXPLAIN` options and
use cumulative statistics.

Injection-point testing separates loading and running through
`INJECTION_POINT_LOAD()` and `INJECTION_POINT_CACHED()`, supports runtime
arguments, and reports attachment with `IS_INJECTION_POINT_ATTACHED()`.

## Inspect plans, logical snapshots, and caches (18.0)

The `pg_logicalinspect` extension inspects logical snapshots, while
`pg_overexplain` adds debug-level plan details. amcheck's `gin_index_check()`
verifies GIN indexes. `pg_buffercache_evict_relation()` and
`pg_buffercache_evict_all()` evict unpinned shared buffers.

## Pass SCRAM through foreign connections (18.0)

Set the `postgres_fdw` option `use_scram_passthrough` to forward the client's
SCRAM authentication rather than storing credentials. It uses libpq's
`scram_client_key` and `scram_server_key`; dblink supports the same passthrough.

`file_fdw` has `on_error`, `log_verbosity`, and `reject_limit` controls that
match tolerant `COPY` behavior.

## Configure bundled modules and inspect FDW connections (18.0)

`passwordcheck.min_password_length` configures the minimum password length.
`isn.weak` controls whether invalid check digits are accepted.
`postgres_fdw_get_connections()` reports transaction use, closed state, user
name, and remote backend PID.

## Select pgcrypto algorithms and FIPS behavior (18.0)

pgcrypto supports `sha256crypt`, `sha512crypt`, and CFB cipher mode.
`fips_mode()` reports server state, and `builtin_crypto_enabled` can disable
built-in non-FIPS cryptographic functions.
