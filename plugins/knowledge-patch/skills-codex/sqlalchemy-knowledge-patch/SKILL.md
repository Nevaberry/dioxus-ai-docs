---
name: sqlalchemy-knowledge-patch
description: SQLAlchemy
version: 2.0.51
license: MIT
metadata:
  author: Nevaberry
---


# SQLAlchemy Knowledge Patch

Use this skill when changing SQLAlchemy ORM mappings, annotations, dataclass
integration, SQL expressions, engines, schema objects, async connections, or
dialect-specific code. Before applying compatibility-sensitive guidance, check
the installed SQLAlchemy and Python versions together with the database server
and DBAPI driver versions.

## Reference index

| Reference | Topics |
| --- | --- |
| [Python, ORM, and typing](references/python-orm-and-typing.md) | Python runtime support, annotation maps, dataclass fields, composites, loader options, and aliases |
| [Engine, SQL, and schema](references/engine-sql-and-schema.md) | Autocommit rollback, constraints, window frames, numeric conversion, and metadata copies |
| [PostgreSQL](references/postgresql.md) | asyncpg isolation, JSONB index migration, constraints, arrays, and reflection |
| [MySQL, MariaDB, and SQLite](references/mysql-mariadb-and-sqlite.md) | Async pooling, limited deletes, locking reads, DDL names, drivers, network types, and strict tables |
| [Oracle and SQL Server](references/oracle-and-sql-server.md) | Vectors, tablespaces, aioodbc batching, index drops, and ODBC connection quoting |

## Check migrations and deprecations first

### Rebuild affected PostgreSQL JSONB expression indexes

On PostgreSQL 14 and later, JSONB subscripting renders with square brackets:

```sql
data['key']
```

JSON expressions still use arrow syntax. PostgreSQL matches expression indexes
by rendered text, so an index created from the older JSONB arrow expression is
not selected for the newly rendered expression. Drop and recreate every
affected expression index as part of the SQLAlchemy upgrade, and compare the
generated SQL and query plans before and after the migration.

### Replace invalid loader-option strings

A dotted loader-option string ending in `"*"`, such as
`Load(A).joinedload("bs.*")`, now raises `ArgumentError`; string attribute names
are rejected instead of silently matching nothing. The bare wildcard remains a
special valid form:

```python
Load(A).lazyload("*")
```

Use mapped class attributes for non-wildcard loader paths.

### Build explicit subqueries before `aliased()`

Passing `select()` or `union()` directly to `aliased()` is deprecated and
becomes an error in SQLAlchemy 2.1. Make the coercion explicit:

```python
user_alias = aliased(User, select(User).subquery())
```

### Treat annotation-map unions as exact keys

`registry.type_annotation_map` resolves a union entry only for that exact
union. An entry keyed by `float | Decimal` does not also map `Mapped[float]`.
PEP 604 and `typing.Union` spellings resolve consistently, so duplicate entries
are unnecessary solely to cover both spellings.

PEP 695 aliases can resolve through their own map entry, their immediate
target, or a generic alias whose target wraps
`Annotated[..., mapped_column(...)]`. Recursive alias-chain traversal and
implicit `NewType` resolution are deprecated in the 2.0 line and disallowed in
2.1. Add explicit map entries or flatten those aliases.

### Rename MariaDB-specific DDL options

Under a `mariadb://` URL, `mysql_with_parser` and `mysql_using` warn. Use
`mariadb_with_parser` and `mariadb_using`, or supply both prefixes when one
metadata definition must support MySQL and MariaDB.

### Recheck decimal conversion scale

For DBAPIs without native decimal support,
`Numeric(decimal_return_scale=n)` now controls conversion scale rather than
being ignored in favor of `Numeric.scale`. Tests that compare processed
`Decimal` values may observe a different number of fractional digits.

### Do not rely on shared defaults after `Table.to_metadata()`

Copied tables now receive copies of column defaults and on-update objects,
including sequences and server-side defaults. They are associated with the
copied columns and metadata, so identity checks against the source objects must
be removed.

## Account for connection and pooling behavior

### Suppress rollback only for detected autocommit

Use `skip_autocommit_rollback=True` when rollback calls are unwanted and the
dialect can detect DBAPI autocommit:

```python
engine = create_engine(
    url,
    isolation_level="AUTOCOMMIT",
    skip_autocommit_rollback=True,
)
```

This also suppresses rollback on pool return. It is not a general mechanism for
skipping rollback during transactional operation.

### Choose the async SQLite pool explicitly when needed

The `aiosqlite` dialect defaults to `AsyncAdaptedQueuePool`. Applications that
require a new connection per checkout must opt into `NullPool`:

```python
engine = create_async_engine(url, poolclass=NullPool)
```

### Let asyncpg inherit server isolation deliberately

When SQLAlchemy has no client isolation level configured, its asyncpg wrapper
passes `None` to the driver and the server-level setting applies. Set a client
isolation level only when the application intends to override the server.

## Use the newer ORM and SQL capabilities

### Add metadata to generated dataclass fields

ORM attribute constructors that accept dataclass options also accept
`dataclass_metadata`, forwarding it to the generated dataclass field:

```python
name: Mapped[str] = mapped_column(
    dataclass_metadata={"ui": "label"},
)
```

Read it through `dataclasses.fields()`. This metadata belongs to the dataclass
field rather than the SQLAlchemy schema object's `Column.info` mapping.

### Apply loader options to composites

`defer()`, `undefer()`, and `load_only()` accept mapped composite attributes:

```python
stmt = select(Location).options(load_only(Location.point))
```

Pass the composite attribute, not a string name.

### Control standalone constraint isolation

`AddConstraint` and `DropConstraint` accept `isolate_from_table`, defaulting to
`True`. Pass `False` when the constraint must remain eligible for inline
creation in the table's `CREATE TABLE` sequence:

```python
ddl = AddConstraint(constraint, isolate_from_table=False)
```

Review DDL ordering when explicit constraint DDL and metadata-level creation
are mixed.

### Express `GROUPS` window frames

`over()` and `FunctionElement.over()` accept `groups=` alongside the other
frame styles:

```python
running = func.sum(t.c.amount).over(
    order_by=t.c.id,
    groups=(None, 0),
)
```

This tuple means unbounded preceding through the current group. Confirm that
the target database supports SQL `GROUPS` frames.

## Verify runtime and dialect assumptions

- Python 3.14 installs `greenlet` automatically and supports more deferred
  annotation cases. Initial free-threaded runtime fixes do not imply that a
  free-threaded 2.0 PyPI wheel exists; those wheels are a 2.1 feature.
- Python 3.15 support is tested in the newer maintenance release represented
  in the detailed runtime reference.
- Empty PostgreSQL arrays can use `array([], type_=Integer)` to render the
  required cast. PostgreSQL constraint and reflection metadata also gained
  richer dialect-specific information.
- MySQL and MariaDB support integer-only limited deletes. MySQL 8.0.1 and later
  can render `FOR SHARE` with `NOWAIT` or `SKIP LOCKED` for locking reads.
- Modern MySQL-Connector/Python is supported again, but MariaDB needs explicit
  charset and collation settings and this driver does not use server-side
  cursors.
- SQLite supports `sqlite_strict=True`, including together with
  `sqlite_with_rowid=False`.
- Oracle supports dense and sparse vectors, vector distance operations,
  vector indexes, approximate fetch, and table tablespaces.
- The SQL Server aioodbc dialect honors `fast_executemany`; SQL Server 2016 and
  later can emit `DROP INDEX IF EXISTS`.
- pyodbc connection-string components receive safer brace quoting, including
  parameter names containing semicolons or closing braces.
