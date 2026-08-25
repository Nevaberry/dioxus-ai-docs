# Migrations and Observability

## New migration capabilities

SQLx 0.9 adds support for:

- `no_tx` migrations that do not run in a transaction;
- skipping migrations;
- building a migrator with `Migrator::with_migrations()`.

Use `no_tx` only for migration operations that cannot run inside a database transaction, and account for the absence of transactional rollback in the surrounding deployment process.

## Builder return types

These migrator setters now return `&mut Self`:

- `set_ignore_missing()`
- `set_locking()`

Update code that expected either call to consume and return the migrator. The mutable-reference return supports configuration through a mutable instance.

## `Migrate` trait changes

The `Migrate` trait changed significantly in the `0.9.0-changelog` batch. Revisit custom implementations and generic bounds instead of expecting source compatibility with SQLx 0.7 or 0.8.

`resolve_blocking()` is hidden and SemVer-exempt. It is not a stable integration point and should not be called or reproduced as part of an external migration abstraction.

## Tracing field correction

The tracing field formerly emitted with a misspelling has been corrected:

| Old field | Current field |
| --- | --- |
| `aquired_after_secs` | `acquired_after_secs` |

Update log parsers, structured-field allowlists, dashboards, alerts, and tests that match the old spelling.
