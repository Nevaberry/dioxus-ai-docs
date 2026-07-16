# SQLite

Connections, prepared statements, sessions, functions, extensions, backups, and build options in `node:sqlite`.

## Contents

- [Connections and safety](#connections-and-safety)
- [Statements, parameters, and rows](#statements-parameters-and-rows)
- [Functions and extensions](#functions-and-extensions)
- [Sessions and backups](#sessions-and-backups)
- [Build and distribution](#build-and-distribution)

## Connections and safety

### Buffer and URL SQLite locations (since 23.10.0)

`DatabaseSync` now accepts `Buffer` and `URL` values as database locations, so an ESM-relative database can be opened with `new DatabaseSync(new URL('./app.db', import.meta.url))`.

### Connection-wide SQLite bigint reads (since 24.4.0)

`DatabaseSync` accepts a connection-level `readBigInts` option. `new DatabaseSync('app.db', { readBigInts: true })` makes statements from that connection return SQLite integers as `BigInt` values without per-statement configuration.

### Defensive SQLite by default (since 25.5.0)

`node:sqlite` now enables defensive mode by default, so new database connections no longer start with the mode disabled.

### Read-only SQLite connections (since 23.2.0)

`DatabaseSync` now accepts a `readOnly` open option. Use `new DatabaseSync('app.db', { readOnly: true })` when the connection must not modify the database.

### Safer `node:sqlite` defaults (since 23.0.0)

SQLite connections now enable foreign-key enforcement and disable double-quoted string literals by default. Legacy behavior can be requested explicitly when constructing the database.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync(':memory:', {
  enableForeignKeyConstraints: false,
  enableDoubleQuotedStringLiterals: true,
});
```

### SQLite busy timeouts and array rows (since 24.0.0)

`DatabaseSync` accepts a millisecond `timeout` open option for waiting on a locked database. A prepared statement can opt into positional array rows with `setReturnArrays(true)`.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync('app.db', { timeout: 5_000 });
const statement = db.prepare('SELECT 1 AS value');
statement.setReturnArrays(true);
console.log(statement.get()); // [1]
```

### SQLite defensive mode (since 25.1.0)

`DatabaseSync.setDefensive(active)` can now enable or disable SQLite defensive mode. When enabled, SQLite blocks SQL features that could deliberately corrupt the database file.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync('app.db');
db.setDefensive(true);
```

### SQLite without a startup flag (since 23.4.0)

`node:sqlite` no longer requires `--experimental-sqlite`; it can now be imported directly without that CLI flag.


## Statements, parameters, and rows

### Cached SQLite tagged templates (since 24.9.0)

`DatabaseSync.createTagStore()` creates a tagged-template query store that safely binds interpolated values and caches prepared statements. Use `` const sql = db.createTagStore(); sql.get`SELECT * FROM users WHERE id = ${id}` `` instead of interpolating values into SQL text.

### Iterating SQLite statement results (since 23.4.0)

`StatementSync.prototype.iterate()` now provides an iterator over a prepared statement's result rows: `for (const row of statement.iterate()) console.log(row)`.

### Numbered SQLite parameters (since 24.7.0)

`node:sqlite` now handles `?NNN` placeholders as positional parameters rather than named bindings.

### SQL tag-store size property (since 25.4.0)

`SQLTagStore.prototype.size` is now a getter. Read `store.size` rather than calling `store.size()`.

### SQLite binary view parameters (since 23.7.0)

`StatementSync` accepts typed arrays and `DataView` instances as bound values, so binary data does not first need to be copied into a `Uint8Array`.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync(':memory:');
db.exec('CREATE TABLE blobs (data BLOB)');
db.prepare('INSERT INTO blobs VALUES (?)').run(new Uint16Array([1, 2]));
```

### SQLite preparation options (since 25.5.0)

`DatabaseSync.prepare()` now accepts an options argument, allowing statement behavior to be selected when the statement is created.

### SQLite result-column metadata (since 23.11.0)

`StatementSync.prototype.columns()` returns metadata for a prepared statement's result columns, for example `db.prepare('SELECT 1 AS answer').columns()`.

### SQLite statement SQL properties (since 23.0.0)

`StatementSync.sourceSQL` and `StatementSync.expandedSQL` are now string-valued properties rather than methods. Read `statement.sourceSQL` and `statement.expandedSQL` without calling them.

### Unknown SQLite named parameters (since 23.11.0)

Statements can opt into ignoring unrecognized named bindings with `statement.setAllowUnknownNamedParameters(true)`, which is useful when a shared parameter object contains values that a particular query does not use.


## Functions and extensions

### Binary results from SQLite functions (since 23.8.0)

Callbacks registered as SQLite user-defined functions may now return `ArrayBufferView` values, including typed arrays and `DataView`, directly as binary results.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync(':memory:');
db.function('signature', () => new Uint8Array([0xca, 0xfe]));
const row = db.prepare('SELECT signature() AS value').get();
```

### Built-in SQLite math functions (since 23.7.0)

The bundled SQLite build now enables SQL math functions, so `db.prepare('SELECT sqrt(81) AS root').get()` works without loading an extension.

### SQLite aggregate functions (since 24.0.0)

`DatabaseSync.aggregate()` registers custom aggregate functions; the required `step` callback receives the current accumulator and returns its next value. Optional result and inverse callbacks can finalize the result or define a window aggregate.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync(':memory:');
db.exec('CREATE TABLE data(n); INSERT INTO data VALUES (2), (3), (4)');
db.aggregate('product', {
  start: 1,
  step: (value, n) => value * n,
});
console.log(db.prepare('SELECT product(n) AS value FROM data').get().value); // 24
```

### SQLite authorization callbacks (since 24.10.0)

`DatabaseSync.setAuthorizer()` installs a callback that can allow, deny, or ignore SQLite operations while statements are prepared. Return `constants.SQLITE_OK`, `constants.SQLITE_DENY`, or `constants.SQLITE_IGNORE` according to the action code.

### SQLite constants and custom functions (since 23.5.0)

`node:sqlite` now groups its constants under a single `constants` property, and `DatabaseSync` can register custom SQL functions for use by prepared statements and queries.

### SQLite extension entry points (since 24.18.0)

`DatabaseSync.loadExtension()` accepts an `entryPoint` argument for libraries whose initialization function does not use the default name: `db.loadExtension('./extension.so', 'sqlite3_custom_init')`.

### SQLite percentile extension (since 26.0.0)

The bundled `node:sqlite` build now enables SQLite's Percentile extension, making that extension's aggregate SQL functionality available without a custom SQLite build.

### SQLite Session Extension (since 23.3.0)

The experimental `node:sqlite` module can now record a database session as a changeset and apply it to another database with `DatabaseSync.createSession()` and `DatabaseSync.applyChangeset()`.

```js
import { DatabaseSync } from 'node:sqlite';

const source = new DatabaseSync(':memory:');
const target = new DatabaseSync(':memory:');
for (const db of [source, target]) db.exec('CREATE TABLE data(key INTEGER PRIMARY KEY, value TEXT)');
const session = source.createSession();
source.exec("INSERT INTO data VALUES (1, 'hello')");
target.applyChangeset(session.changeset());
```

Distributors using `--shared-sqlite` must build SQLite with both `SQLITE_ENABLE_SESSION` and `SQLITE_ENABLE_PREUPDATE_HOOK`.


## Sessions and backups

### Exported, disposable SQLite sessions (since 24.9.0)

`node:sqlite` now exports `Session`, and session objects participate in explicit resource management. A session created with `using session = db.createSession()` is closed at scope exit and can be tested against the exported class.

### SQLite changeset conflict types (since 23.6.0)

The conflict-resolution handler used while applying a SQLite changeset now receives the conflict type, allowing it to choose a resolution based on why the conflict occurred.

### SQLite online backups (since 23.8.0)

`node:sqlite` now exposes an online backup API for copying an open database to a file.

```js
import { backup, DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync('app.db');
await backup(db, 'app.backup.db');
```


## Build and distribution

### Optional SQLite source builds (since 24.1.0)

Node can now be built without SQLite, so custom distributions may omit `node:sqlite`; deployments that depend on it should verify that the target build includes the module.
