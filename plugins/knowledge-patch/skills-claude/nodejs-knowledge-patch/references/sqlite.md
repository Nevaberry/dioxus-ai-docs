# SQLite

Use this reference for sqlite work.

## `SQLTagStore.size` is a getter (`24.13.0`)

In 24.13.1, read `SQLTagStore.prototype.size` as a property rather than calling it as a method.

```js
import { DatabaseSync } from 'node:sqlite';

const store = new DatabaseSync(':memory:').createTagStore();
console.log(store.size);
```

## Binary values from SQLite user-defined functions (`23.8.0`)

SQLite user-defined functions may now return `ArrayBufferView` values such as typed arrays and `DataView` objects.

```js
import { DatabaseSync } from 'node:sqlite';
const db = new DatabaseSync(':memory:');
db.function('bytes', () => new Uint8Array([1, 2, 3]));
```

## Built-in SQLite math functions (`23.7.0`)

The bundled SQLite build now enables SQL math functions, so queries such as `SELECT sqrt(81)` work without a separately compiled extension.

## Cached SQLite tagged templates (`24.9.0`)

`DatabaseSync.createTagStore()` creates a tagged-template query store that binds interpolated values as parameters and reuses cached prepared statements.

```js
const sql = db.createTagStore();
sql.run`INSERT INTO users (name) VALUES (${name})`;
const user = sql.get`SELECT * FROM users WHERE name = ${name}`;
```

## Configurable SQLite defensive mode (`25.1.0`)

`node:sqlite` now allows a database connection's SQLite defensive flag to be set, so applications can explicitly control defensive-mode policy.

## Connection-wide SQLite bigint reads (`24.4.0`)

`DatabaseSync` accepts `readBigInts` at connection creation, making integer results from that connection use `BigInt` without configuring each statement separately.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync('data.db', { readBigInts: true });
```

## Grouped SQLite constants (`23.5.0`)

`node:sqlite` now aggregates its constants under a single `constants` property, so consumers can access related values from that namespace.

```js
import { constants } from 'node:sqlite';
```

## Numbered SQLite parameters are positional (`24.7.0`)

`node:sqlite` now handles `?NNN` placeholders as positional parameters, so their values can be supplied as positional arguments rather than named-parameter object properties.

```js
const statement = db.prepare('SELECT ?1 AS value');
const row = statement.get('hello');
```

## Opt-in unknown SQLite parameters (`23.11.0`)

`StatementSync.setAllowUnknownNamedParameters(true)` permits a named-parameter object to contain keys that do not occur in the SQL. Unknown names are rejected by default, which helps catch binding typos.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync(':memory:');
const statement = db.prepare('SELECT $name AS name');
statement.setAllowUnknownNamedParameters(true);
statement.get({ $name: 'pencil', $unused: 1 });
```

## Public, disposable SQLite sessions (`24.9.0`)

`node:sqlite` now exports the `Session` class, so objects returned by `DatabaseSync.createSession()` have a public class for imports and `instanceof` checks. Sessions also support explicit resource management for deterministic cleanup.

```js
import { DatabaseSync, Session } from 'node:sqlite';

const db = new DatabaseSync(':memory:');
using session = db.createSession();
console.log(session instanceof Session); // true
```

## Read-only SQLite connections (`23.2.0`)

`DatabaseSync` accepts a `readOnly` open option for connections that must not modify the database.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync('data.db', { readOnly: true });
```

## SQLite busy timeouts and aggregate functions (`24.0.0`)

`DatabaseSync` accepts a `timeout` option for locked-database waits, and databases can register aggregate SQL functions.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync('app.db', { timeout: 5_000 });
db.aggregate('total', {
  start: 0,
  step: (sum, value) => sum + value,
});
```

## SQLite can be omitted from custom builds (`24.1.0`)

Custom Node.js builds can now exclude SQLite. Code intended to run on custom builds must feature-detect `node:sqlite` instead of assuming its presence from the Node.js version alone.

## SQLite conflict handlers receive the conflict type (`23.6.0`)

Conflict-resolution handlers for the SQLite Session Extension now receive the conflict type, allowing them to choose a response based on the specific changeset conflict.

## SQLite connection state and disposal (`23.11.0`)

`DatabaseSync.isOpen` reports whether a connection is open, and `DatabaseSync[Symbol.dispose]()` closes it through the explicit resource-management protocol.

## SQLite custom functions (`23.5.0`)

`node:sqlite` databases can now register custom SQL functions.

## SQLite defensive mode is the default (`25.5.0`)

`node:sqlite` now enables SQLite defensive mode by default. Applications that require the previous, less restrictive policy must explicitly change the connection's defensive setting rather than relying on its default.

## SQLite loadable extensions (`23.5.0`)

`node:sqlite` adds `db.loadExtension()` support for loading SQLite extensions.

## SQLite online backups (`23.8.0`)

`node:sqlite` now exposes SQLite's online backup API.

## SQLite percentile extension (`26.0.0`)

The bundled `node:sqlite` build enables SQLite's Percentile extension, making its aggregate SQL functionality available without a custom SQLite build.

## SQLite preparation options (`25.5.0`)

SQLite statement preparation now accepts an options argument, allowing statement behavior to be selected when the statement is prepared.

## SQLite result-column metadata (`23.11.0`)

`StatementSync.columns()` returns metadata describing the result columns of a prepared statement.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync(':memory:');
const statement = db.prepare('SELECT 1 AS answer');
console.log(statement.columns());
```

## SQLite Session Extension (`23.3.0`)

`node:sqlite` now supports the SQLite Session Extension, enabling applications to record database changes as changesets or patchsets for transfer and application elsewhere.

## SQLite statement authorization (`24.10.0`)

`DatabaseSync.setAuthorizer()` exposes SQLite's authorization callback, allowing a connection to permit, deny, or ignore operations before SQLite executes them.

```js
import { constants, DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync(':memory:');
db.setAuthorizer((actionCode) => {
  if (actionCode === constants.SQLITE_DROP_TABLE) {
    return constants.SQLITE_DENY;
  }
  return constants.SQLITE_OK;
});
```

## Stricter `node:sqlite` defaults (`23.0.0`)

SQLite foreign-key constraints are enabled by default, while double-quoted string compatibility is disabled: double quotes identify names, and string literals must use single quotes. `StatementSync.sourceSQL` and `StatementSync.expandedSQL` are string-valued properties.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync(':memory:');
db.prepare("SELECT 'text'").get(); // string literals use single quotes
```

## Typed-array SQLite bindings (`23.7.0`)

`StatementSync` now accepts `TypedArray` and `DataView` values as SQL parameters; for example, `statement.run(new Uint8Array([1, 2, 3]))` binds array-buffer-backed binary data directly.

## URL and Buffer SQLite locations (`23.10.0`)

`DatabaseSync` now accepts `URL` and `Buffer` values as database locations in addition to strings.

```js
import { DatabaseSync } from 'node:sqlite';

const db = new DatabaseSync(new URL('./data.db', import.meta.url));
```
