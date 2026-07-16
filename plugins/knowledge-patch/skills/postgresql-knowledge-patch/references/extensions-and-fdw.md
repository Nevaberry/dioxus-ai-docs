# Extensions, Modules, and Foreign Data Wrappers

Batch attribution: `17.0`, `18.0`.

## Locate and identify extensions

`extension_control_path` selects directories in which the server looks for
extension control files.

Extension binaries can use `PG_MODULE_MAGIC_EXT` to report their name and
version through `pg_get_loaded_modules()`.

## Integrate with planning, waits, and cumulative statistics

Extensions can register custom `EXPLAIN` options, custom wait events, and
cumulative statistics.

Foreign data wrappers and custom scans must correctly handle pushed-down joins
that include non-join qualifications.

## Use expanded extension capabilities

`ltree` supports hash indexes, hash joins, and hash aggregation.
`unaccent.rules` can represent whitespace and quotation marks.
`pg_amcheck --checkunique` verifies unique constraints.

The `amcheck` function `gin_index_check()` verifies GIN indexes.
`pg_buffercache_evict_relation()` and `pg_buffercache_evict_all()` evict
unpinned shared buffers.

The `pg_logicalinspect` extension inspects logical snapshots.
`pg_overexplain` adds debug-level plan details.

## Test extension behavior with injection points

Injection-point testing separates loading from running with
`INJECTION_POINT_LOAD()` and `INJECTION_POINT_CACHED()`. Injection points
accept runtime arguments, and `IS_INJECTION_POINT_ATTACHED()` reports whether a
point is attached.

## Pass SCRAM credentials through foreign connections

`postgres_fdw` option `use_scram_passthrough` forwards client SCRAM
authentication instead of storing credentials. It uses libpq's
`scram_client_key` and `scram_server_key` support. `dblink` supports the same
passthrough.

`postgres_fdw_get_connections()` reports transaction use, closed state, user
name, and remote backend PID.

## Tolerate malformed file_fdw rows

`file_fdw` accepts `on_error`, `log_verbosity`, and `reject_limit` controls
matching tolerant `COPY FROM` behavior.

## Configure bundled security and validation modules

`passwordcheck.min_password_length` configures the module's minimum password
length. `isn.weak` controls whether invalid check digits are accepted.

pgcrypto supports `sha256crypt`, `sha512crypt`, and CFB cipher mode.
`fips_mode()` reports the server's FIPS state, and `builtin_crypto_enabled` can
disable built-in non-FIPS cryptographic functions.

Trusted PL/Perl rejects changes to `%ENV`. The untrusted `plperlu` language
retains that capability.
