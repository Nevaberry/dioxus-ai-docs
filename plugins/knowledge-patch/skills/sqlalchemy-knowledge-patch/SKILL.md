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
dialect-specific code. Check the installed SQLAlchemy, Python, database
server, and DBAPI versions before applying compatibility-sensitive advice.

## Reference index

| Reference | Topics |
| --- | --- |
| [Python, ORM, and typing](references/python-orm-and-typing.md) | Python 3.14 and free-threading, annotation maps and aliases, dataclass field metadata, deferred composites |
| [Engine, SQL, and schema](references/engine-sql-and-schema.md) | Autocommit rollback suppression, standalone constraint isolation, `GROUPS` window frames |
| [PostgreSQL](references/postgresql.md) | asyncpg isolation, JSONB subscripts and index migration, constraint options, typed arrays, reflection |
| [MySQL, MariaDB, and SQLite](references/mysql-mariadb-and-sqlite.md) | Async SQLite pooling, strict tables, limited deletes, locking reads, MariaDB DDL names, Connector/Python, network types |
| [Oracle and SQL Server](references/oracle-and-sql-server.md) | Oracle vectors and tablespaces, aioodbc batching, conditional index drops |

## Check compatibility and migrations first

### Rebuild affected PostgreSQL JSONB expression indexes

On PostgreSQL 14 and later, JSONB subscripting renders with square brackets:

```sql
data['key']
```

JSON expressions continue to use arrow syntax. PostgreSQL matches an
expression index by rendered text, so an index built from the older JSONB
arrow expression will not be selected for the new expression. Drop and
recreate every affected expression index during the SQLAlchemy upgrade.

Inspect generated SQL and query plans before and after the migration; do not
assume that a logically equivalent old expression index remains usable.

### Treat annotation-map unions as exact keys

`registry.type_annotation_map` resolves a union entry only for the exact union.
An entry keyed by `float | Decimal` does not also map `Mapped[float]`.
PEP 604 unions and `typing.Union` resolve consistently, so do not duplicate
entries solely because the spelling differs.

PEP 695 aliases can resolve through:

- an explicit entry for the alias;
- an entry for its immediate target; or
- a generic alias whose target wraps
  `Annotated[..., mapped_column(...)]`.

Do not depend on recursive alias-chain traversal or implicit `NewType`
resolution. Those forms are deprecated in the 2.0 line and rejected in 2.1.
Add explicit map entries or flatten aliases before an upgrade.

### Rename MariaDB-specific DDL options

Under a `mariadb://` URL, `mysql_with_parser` and `mysql_using` warn. Use:

- `mariadb_with_parser`;
- `mariadb_using`; or
- both the `mysql_` and `mariadb_` forms when one metadata definition must
  support both dialects.

Warnings here identify a forward-compatibility issue, not merely cosmetic
renaming.

### Account for async default changes

The `aiosqlite` dialect uses `AsyncAdaptedQueuePool` by default. Code that
requires a new connection per checkout must opt back into `NullPool`:

```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

engine = create_async_engine(url, poolclass=NullPool)
```

For asyncpg, leaving SQLAlchemy's isolation level unset now lets the server
setting apply. Configure an isolation level explicitly only when the
application intends to override the server.

### Verify Python runtime assumptions

Python 3.14 installs `greenlet` automatically through SQLAlchemy's dependency
metadata. Deferred annotations now cover relationship targets in
`MappedAsDataclass` and unresolved names encountered during ORM
introspection.

Free-threaded Python 3.13t and 3.14t have initial runtime fixes in this
SQLAlchemy line, but free-threaded PyPI wheels are a 2.1 feature. Plan for the
actual artifact available in the deployment environment rather than assuming
a 2.0 wheel exists.

## High-value ORM features

### Attach metadata to generated dataclass fields

ORM attribute constructors that accept dataclass options also accept
`dataclass_metadata`. SQLAlchemy forwards the mapping to the generated
dataclass field:

```python
from sqlalchemy.orm import Mapped, mapped_column

name: Mapped[str] = mapped_column(
    dataclass_metadata={"ui": "label"},
)
```

Use `dataclasses.fields()` to read the resulting field metadata. Keep this
separate from `Column.info`, which describes a SQLAlchemy schema object.

### Apply loader options to composites

`defer()`, `undefer()`, and `load_only()` accept composite attributes:

```python
from sqlalchemy import select
from sqlalchemy.orm import load_only

stmt = select(Location).options(load_only(Location.point))
```

Pass the mapped composite attribute, not a string name. This allows loading
plans to describe the composite at the ORM level.

## High-value Core and engine features

### Avoid redundant rollback in autocommit

Use `skip_autocommit_rollback=True` when the dialect can determine that a
connection is already in DBAPI autocommit and rollback calls are unwanted:

```python
from sqlalchemy import create_engine

engine = create_engine(
    url,
    isolation_level="AUTOCOMMIT",
    skip_autocommit_rollback=True,
)
```

This includes the rollback normally issued when a pooled connection is
returned. The suppression depends on dialect-level autocommit detection; it
is not a general instruction to skip rollback in transactional operation.

### Choose standalone constraint isolation deliberately

`AddConstraint` and `DropConstraint` accept `isolate_from_table`, which
defaults to `True`. Pass `False` when the constraint must remain eligible for
inline creation as part of the table's `CREATE TABLE` sequence:

```python
from sqlalchemy.schema import AddConstraint

ddl = AddConstraint(constraint, isolate_from_table=False)
```

Review DDL ordering when changing this value, especially when metadata-level
create operations and explicit constraint DDL are mixed.

### Express `GROUPS` window frames

`over()` and `FunctionElement.over()` accept `groups=` alongside the existing
frame styles:

```python
from sqlalchemy import func

running = func.sum(t.c.amount).over(
    order_by=t.c.id,
    groups=(None, 0),
)
```

The tuple above renders an unbounded-preceding-to-current-group frame. Confirm
that the target database supports SQL `GROUPS` frames.

## Dialect decision points

### PostgreSQL

- `UniqueConstraint` and `PrimaryKeyConstraint` accept
  `postgresql_include`.
- Foreign-key `ON DELETE SET NULL` and `SET DEFAULT` actions can include a
  column list.
- `array([], type_=Integer)` emits the cast required for an empty array.
- Reflection preserves non-default type collations and reports non-default
  index operator classes in `dialect_options["postgresql_ops"]`.

### MySQL and MariaDB

- `Delete.with_dialect_options()` accepts integer-only `mysql_limit` and
  `mariadb_limit`.
- MySQL 8.0.1 and later supports locking reads rendered as `FOR SHARE` with
  `NOWAIT` or `SKIP LOCKED`.
- Modern MySQL-Connector/Python support is restored; MariaDB connections need
  explicit charset and collation, and this driver does not use server-side
  cursors.
- MariaDB exposes `INET4` and `INET6`.

### SQLite

Use `sqlite_strict=True` for a `STRICT` table. It composes with
`sqlite_with_rowid=False`, so both options may be set on the same `Table`.

### Oracle

The dialect includes dense and sparse vector types, distance operations,
vector-index options, and approximate fetch support. Tables can also set
`oracle_tablespace`.

### SQL Server

The async aioodbc dialect honors `fast_executemany`. SQL Server 2016 and later
also receives `DROP INDEX IF EXISTS` from `DropIndex(..., if_exists=True)`.
