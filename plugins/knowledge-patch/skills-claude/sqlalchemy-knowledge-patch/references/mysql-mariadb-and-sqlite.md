# MySQL, MariaDB, and SQLite

## MySQL and MariaDB delete limits

`Delete.with_dialect_options()` accepts the integer-only `mysql_limit` and
`mariadb_limit` options:

```python
delete(t).with_dialect_options(mysql_limit=100)
```

Choose the prefix for the target dialect and pass an integer value.

## MySQL locking reads

On MySQL 8.0.1 and later, a read lock can render as `FOR SHARE` and combine
with `NOWAIT` or `SKIP LOCKED`. For example:

```python
select(t).with_for_update(read=True, skip_locked=True)
```

The delete-limit and locking-read additions are from 2.0.51.

## MariaDB-specific DDL option names

Under a `mariadb://` URL, `mysql_with_parser` and `mysql_using` emit
deprecation warnings. Replace them with:

- `mariadb_with_parser`;
- `mariadb_using`; or
- both the `mysql_` and `mariadb_` forms when the same metadata must support
  both dialects.

Treat the warning as a forward-compatibility issue.

## MySQL-Connector/Python

The `mysql+mysqlconnector://` dialect supports modern MySQL and MariaDB
again. MariaDB connections require explicit charset and collation settings.
The driver does not use server-side cursors, so do not design streaming
behavior around them.

## MariaDB network types

The MariaDB dialect supports the `INET4` and `INET6` SQL types. Use the
dialect-specific types when mapping MariaDB network-address columns.

## Async SQLite pooling

The `aiosqlite` dialect defaults to `AsyncAdaptedQueuePool` instead of
`NullPool`. If connection-per-use behavior is required, opt in explicitly:

```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

engine = create_async_engine(url, poolclass=NullPool)
```

Audit assumptions about connection state and lifetime when accepting the
queue-pool default.

## SQLite strict tables

Set `sqlite_strict=True` to create a `STRICT` table:

```python
Table(
    "event",
    metadata,
    Column("id", Integer),
    sqlite_strict=True,
)
```

The option composes with `sqlite_with_rowid=False`; both may be set on the
same `Table`.
