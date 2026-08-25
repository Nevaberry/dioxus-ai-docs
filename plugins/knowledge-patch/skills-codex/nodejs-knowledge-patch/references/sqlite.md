# SQLite

## Connection defaults and options

- In 23.0.0, foreign-key constraints are enabled by default and SQLite's
  double-quoted-string compatibility is disabled. Double quotes identify names;
  string literals use single quotes. `StatementSync.sourceSQL` and
  `StatementSync.expandedSQL` are string-valued properties.
- In 23.2.0, `DatabaseSync` accepts `readOnly: true` for a connection that must
  not modify the database.
- In 23.10.0, `DatabaseSync` accepts `URL` and `Buffer` database locations in
  addition to strings.
- In 24.0.0, `DatabaseSync` accepts `timeout` for locked-database waits.
- In 24.4.0, `DatabaseSync` accepts `readBigInts` at connection creation so all
  integer results use `BigInt` without per-statement configuration.
- In 25.1.0, a connection's SQLite defensive flag is configurable.
- In 25.5.0, defensive mode is enabled by default. Applications needing the
  earlier, less restrictive policy must change the connection setting rather
  than relying on the old default.

## Connection state, cleanup, and authorization

- In 23.11.0, `DatabaseSync.isOpen` reports connection state and
  `DatabaseSync[Symbol.dispose]()` closes through explicit resource management.
- In 24.10.0, `DatabaseSync.setAuthorizer()` exposes SQLite's authorizer, which
  can permit, deny, or ignore operations before execution.
- In 24.1.0, custom Node builds can omit SQLite. Feature-detect `node:sqlite`
  when supporting custom builds instead of assuming availability from the
  version.

## Statements and parameters

- In 23.7.0, `StatementSync` accepts `TypedArray` and `DataView` SQL parameters
  as array-buffer-backed binary data.
- In 23.11.0, `StatementSync.columns()` returns result-column metadata.
- Also in 23.11.0, unknown named parameters are rejected by default;
  `StatementSync.setAllowUnknownNamedParameters(true)` permits extra keys in a
  binding object.
- In 24.7.0, `?NNN` placeholders are positional and can receive values as
  positional arguments rather than named-object properties.
- In 25.5.0, statement preparation accepts an options argument for choosing
  behavior at prepare time.

## Sessions and changesets

- In 23.3.0, `node:sqlite` supports the SQLite Session Extension for recording
  changes as changesets or patchsets and applying them elsewhere.
- In 23.6.0, conflict-resolution handlers receive the conflict type and can
  choose a response for that changeset conflict.
- In 24.9.0, `node:sqlite` publicly exports `Session`, so objects returned by
  `DatabaseSync.createSession()` support imports and `instanceof`. Sessions
  also implement explicit resource management.

## Functions and extensions

- In 23.5.0, SQLite constants are grouped under the exported `constants`
  property. Connections can register custom SQL functions and load extensions
  with `db.loadExtension()`.
- In 23.7.0, the bundled SQLite enables SQL math functions.
- In 23.8.0, user-defined functions may return `ArrayBufferView` values such as
  typed arrays and `DataView`.
- In 24.0.0, databases can register aggregate SQL functions.
- In 26.0.0, the bundled SQLite enables the Percentile extension and its
  aggregate SQL functionality.

## Backup and query caching

- In 23.8.0, `node:sqlite` exposes SQLite's online backup API.
- In 24.9.0, `DatabaseSync.createTagStore()` creates a tagged-template query
  store that parameterizes interpolated values and reuses cached prepared
  statements.
- In 24.13.0, the 24.13.1 API exposes `SQLTagStore.prototype.size` as a getter;
  read `store.size` rather than calling it.
