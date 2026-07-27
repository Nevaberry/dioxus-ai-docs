# MySQL, MariaDB, and SQLite

## Async SQLite pooling

The `aiosqlite` dialect defaults to `AsyncAdaptedQueuePool`, replacing the
previous connection-per-use behavior of `NullPool`. Existing code may now
reuse connections and retain connection-scoped state for the lifetime of a
pool entry.

Opt into `NullPool` explicitly when every use must create and close a distinct
connection:

```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

engine = create_async_engine(
    "sqlite+aiosqlite:///app.db",
    poolclass=NullPool,
)
```

Review tests or hooks that assumed a newly opened connection on every
checkout.

## SQLite `STRICT` tables

Set `sqlite_strict=True` on `Table` to emit a SQLite `STRICT` table:

```python
from sqlalchemy import Column, Integer, MetaData, Table

event = Table(
    "event",
    MetaData(),
    Column("id", Integer),
    sqlite_strict=True,
)
```

Strict typing composes with a table that omits the rowid:

```python
event = Table(
    "event",
    MetaData(),
    Column("id", Integer, primary_key=True),
    sqlite_strict=True,
    sqlite_with_rowid=False,
)
```

The two dialect options control separate SQLite table characteristics and may
be enabled together.

## Limited deletes on MySQL and MariaDB

MySQL and MariaDB `DELETE` statements accept their respective integer-only
limit options through `Delete.with_dialect_options()`:

```python
from sqlalchemy import delete

mysql_stmt = delete(t).with_dialect_options(mysql_limit=100)
mariadb_stmt = delete(t).with_dialect_options(mariadb_limit=100)
```

Supply an integer, not an arbitrary SQL expression. Choose the option matching
the compiled dialect when building dialect-specific statements.

## MySQL locking reads

On MySQL 8.0.1 and later, a read lock can render as `FOR SHARE` and combine
with `NOWAIT` or `SKIP LOCKED`:

```python
stmt = select(t).with_for_update(
    read=True,
    skip_locked=True,
)
```

Set `nowait=True` instead when immediate failure is required. Gate this SQL by
the actual MySQL server version.

## MariaDB-specific DDL option names

When compiling through `mariadb://`, the MySQL-prefixed index options
`mysql_with_parser` and `mysql_using` emit deprecation warnings. Prefer:

- `mariadb_with_parser`; and
- `mariadb_using`.

If one metadata definition must compile for both MySQL and MariaDB, provide
both dialect prefixes with equivalent values. Do not suppress the warning and
assume the `mysql_` spelling will remain the MariaDB API.

## MySQL-Connector/Python

The `mysql+mysqlconnector://` dialect again supports modern MySQL and MariaDB.
For MariaDB, configure charset and collation explicitly in the connection
settings; do not rely on implicit defaults.

Server-side cursors remain disabled for MySQL-Connector/Python. Streaming or
memory assumptions must reflect the driver's actual cursor behavior rather
than the capability of another MySQL DBAPI.

## MariaDB network types

The MariaDB dialect supports the server-native `INET4` and `INET6` SQL types.
Use the dialect types when a schema must preserve those database types through
DDL generation or reflection instead of reducing them to generic character
columns.
