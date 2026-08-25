---
name: sqlalchemy-knowledge-patch
description: SQLAlchemy
version: 2.0.51
license: MIT
metadata:
  author: Nevaberry
---


# SQLAlchemy Knowledge Patch

Use this skill when changing SQLAlchemy ORM mappings, type annotations,
engines, schema objects, SQL expressions, async connections, or
dialect-specific code.

Before applying compatibility-sensitive guidance:

1. Check the installed SQLAlchemy and Python versions.
2. Identify the database server, dialect, and DBAPI versions.
3. Inspect generated SQL for schema or expression changes.
4. Treat project manifests, migrations, code, and tests as authoritative.

## Reference index

| Reference | Topics |
| --- | --- |
| [Python, ORM, and typing](references/python-orm-and-typing.md) | Python runtime support, annotations, dataclasses, composites, loader options, aliases |
| [Engine, SQL, and schema](references/engine-sql-and-schema.md) | Autocommit rollback, constraints, window frames, numeric conversion, metadata copies |
| [PostgreSQL](references/postgresql.md) | asyncpg isolation, JSONB migration, constraints, arrays, reflection |
| [MySQL, MariaDB, and SQLite](references/mysql-mariadb-and-sqlite.md) | Delete limits, locking reads, DDL names, connector behavior, network types, async pools, strict tables |
| [Oracle and SQL Server](references/oracle-and-sql-server.md) | Vectors, tablespaces, aioodbc batching, index drops, ODBC quoting |

## Upgrade and deprecation checks

### Rebuild affected PostgreSQL JSONB expression indexes

On PostgreSQL 14 and later, JSONB subscripting renders with square brackets:

```sql
data['key']
```

JSON expressions continue to use arrow syntax. PostgreSQL matches an
expression index by rendered text, so an index created from the older JSONB
arrow expression will not be selected. Drop and recreate each affected
expression index during the SQLAlchemy upgrade, then inspect generated SQL and
query plans.

### Make `aliased()` subqueries explicit

Passing a `select()` or `union()` directly to `aliased()` warns while implicit
subquery coercion remains available. It raises in SQLAlchemy 2.1. Build the
subquery explicitly:

```python
alias = aliased(User, select(User).subquery())
```

### Treat annotation-map unions as exact keys

An entry for `float | Decimal` in `registry.type_annotation_map` does not map
`Mapped[float]`. PEP 604 and `typing.Union` spellings resolve consistently.

PEP 695 aliases may resolve through an entry for the alias, an entry for its
immediate target, or a generic alias around
`Annotated[..., mapped_column(...)]`. Do not rely on recursive alias-chain
traversal or implicit `NewType` resolution; add explicit entries or flatten
the aliases before SQLAlchemy 2.1.

### Remove dotted loader wildcards

A dotted string ending in `"*"`, such as
`Load(A).joinedload("bs.*")`, raises `ArgumentError`; loader options reject
string attribute names. Use mapped attributes for paths. A bare wildcard such
as `Load(A).lazyload("*")` remains valid.

### Rename MariaDB-specific DDL options

With a `mariadb://` URL, `mysql_with_parser` and `mysql_using` warn. Use
`mariadb_with_parser` and `mariadb_using`, or provide both prefixes when one
metadata definition must support MySQL and MariaDB.

## Behavior changes to audit

### Async connection defaults

The `aiosqlite` dialect defaults to `AsyncAdaptedQueuePool`. Opt into a fresh
connection per checkout explicitly:

```python
from sqlalchemy.pool import NullPool

engine = create_async_engine(url, poolclass=NullPool)
```

For asyncpg, leaving the client isolation level unset passes `None` to the
driver, allowing the server isolation setting to apply instead of forcing
`READ COMMITTED`.

### Decimal conversion scale

For DBAPIs without native decimal support,
`Numeric(decimal_return_scale=n)` now controls the conversion scale instead
of being ignored in favor of `Numeric.scale`. Audit code and tests that depend
on the number of fractional digits in processed `Decimal` values.

### Independent defaults in metadata copies

`Table.to_metadata()` copies column default and on-update objects, including
sequences and server-side defaults. Copied defaults belong to the copied
columns and metadata; identity checks must expect distinct objects rather than
shared instances.

### Suppress autocommit rollbacks deliberately

Use `skip_autocommit_rollback=True` only when the dialect can detect DBAPI
autocommit:

```python
engine = create_engine(
    url,
    isolation_level="AUTOCOMMIT",
    skip_autocommit_rollback=True,
)
```

This also suppresses rollback on pool return. It is not a general instruction
to omit rollback from transactional connections.

## High-value ORM and Core features

### Add metadata to generated dataclass fields

ORM attribute constructors that accept dataclass options accept
`dataclass_metadata`, which is forwarded to the generated dataclass field:

```python
name: Mapped[str] = mapped_column(
    dataclass_metadata={"ui": "label"},
)
```

### Apply loader options to composites

`defer()`, `undefer()`, and `load_only()` accept mapped composite attributes:

```python
stmt = select(Location).options(load_only(Location.point))
```

Pass the mapped attribute rather than a string.

### Express `GROUPS` window frames

`over()` and `FunctionElement.over()` accept `groups=` alongside the existing
frame styles:

```python
running = func.sum(t.c.amount).over(
    order_by=t.c.id,
    groups=(None, 0),
)
```

The tuple renders an unbounded-preceding-to-current-group frame. Confirm that
the target database supports SQL `GROUPS` frames.

### Control standalone constraint isolation

`AddConstraint` and `DropConstraint` accept `isolate_from_table`, defaulting
to `True`. Pass `False` when a constraint must remain eligible for inline
creation in the table's `CREATE TABLE` sequence:

```python
ddl = AddConstraint(constraint, isolate_from_table=False)
```

Review DDL ordering when metadata creation and explicit constraint DDL mix.

## Dialect quick reference

### PostgreSQL

- `UniqueConstraint` and `PrimaryKeyConstraint` accept
  `postgresql_include`.
- Foreign-key `ON DELETE SET NULL` and `SET DEFAULT` actions accept column
  lists.
- `array([], type_=Integer)` renders the cast required for an empty array.
- Reflection retains non-default type collations and exposes non-default
  index operator classes in `dialect_options["postgresql_ops"]`.

### MySQL, MariaDB, and SQLite

- `Delete.with_dialect_options()` accepts integer-only `mysql_limit` and
  `mariadb_limit`.
- MySQL 8.0.1 and later supports locking reads rendered as `FOR SHARE` with
  `NOWAIT` or `SKIP LOCKED`.
- Modern MySQL-Connector/Python is supported; MariaDB needs explicit charset
  and collation, and this driver does not use server-side cursors.
- MariaDB provides `INET4` and `INET6`.
- SQLite tables accept `sqlite_strict=True`, including together with
  `sqlite_with_rowid=False`.

### Oracle and SQL Server

- Oracle provides dense and sparse vector types, distance operations, vector
  index options, approximate fetch support, and `oracle_tablespace`.
- The SQL Server aioodbc dialect honors `fast_executemany`.
- SQL Server 2016 and later emits `DROP INDEX IF EXISTS` for
  `DropIndex(..., if_exists=True)`.
- The pyodbc connector brace-quotes driver names and pass-through parameter
  names or values when needed to prevent connection-string misparsing.

## Python runtime notes

Python 3.14 receives automatic `greenlet` installation. Deferred annotation
handling covers relationship targets in `MappedAsDataclass` and unresolved
names during ORM introspection. Free-threaded Python 3.13t and 3.14t have
initial runtime fixes, but free-threaded package-index wheels are a SQLAlchemy
2.1 feature. SQLAlchemy 2.0.52 adds and tests Python 3.15 support.
