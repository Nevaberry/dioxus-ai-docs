# MySQL, MariaDB, and SQLite

## Async SQLite pooling default

In 2.0.51, the `aiosqlite` dialect defaults to `AsyncAdaptedQueuePool` instead
of `NullPool`. Code requiring a new connection per checkout must select
`NullPool` explicitly:

```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

engine = create_async_engine(url, poolclass=NullPool)
```

## Limited deletes and locking reads

MySQL and MariaDB `DELETE` statements accept integer-only `mysql_limit` and
`mariadb_limit` through `Delete.with_dialect_options()` in 2.0.51:

```python
stmt = delete(t).with_dialect_options(mysql_limit=100)
```

On MySQL 8.0.1 and later, a locking read such as
`select(t).with_for_update(read=True, skip_locked=True)` can render `FOR SHARE`
with `NOWAIT` or `SKIP LOCKED`.

## MariaDB-specific DDL option names

With a `mariadb://` URL in 2.0.51, `mysql_with_parser` and `mysql_using` emit
deprecation warnings. Replace them with `mariadb_with_parser` and
`mariadb_using`. Supply both the `mysql_` and `mariadb_` variants when the same
metadata definition must work with both dialects.

## MySQL-Connector/Python

The `mysql+mysqlconnector://` dialect supports modern MySQL and MariaDB again
in 2.0.51. MariaDB connections require explicit charset and collation
settings. Server-side cursors remain disabled for this driver.

## MariaDB network types

The MariaDB dialect supports the `INET4` and `INET6` SQL types as of 2.0.51.

## SQLite strict tables

Use `sqlite_strict=True` in 2.0.51 to create a SQLite `STRICT` table:

```python
event = Table(
    "event",
    metadata,
    Column("id", Integer),
    sqlite_strict=True,
)
```

This composes with `sqlite_with_rowid=False`; both options can be set on the
same `Table`.
