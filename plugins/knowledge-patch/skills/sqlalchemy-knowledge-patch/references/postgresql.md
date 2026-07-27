# PostgreSQL

## asyncpg and server isolation

When the application does not configure a client isolation level, the asyncpg
wrapper passes `None` to the driver. That leaves the server-level isolation
setting in control instead of forcing `READ COMMITTED`.

This distinction is important when `default_transaction_isolation` is set at
the database, role, or server level. To override that policy, set the
SQLAlchemy isolation level explicitly; otherwise, expect the server setting
to win.

## JSONB subscript rendering and expression indexes

On PostgreSQL 14 and later, a JSONB subscript renders with bracket notation:

```sql
data['key']
```

The PostgreSQL `JSON` type continues to use arrow syntax. Keep the two
rendering behaviors distinct when reviewing compiled SQL.

PostgreSQL requires a textual expression match before it can use an
expression index. An index created from the former JSONB arrow rendering does
not match a query compiled with the bracket rendering, even when the
expressions are logically equivalent. During an upgrade:

1. inventory indexes whose expressions contain SQLAlchemy-rendered JSONB
   subscripts;
2. compile representative expressions against PostgreSQL 14 or later;
3. drop and recreate indexes whose stored expression uses the old text; and
4. verify index selection with the actual query plan.

Changing application queries without rebuilding an affected index can cause a
silent performance regression.

## Included columns on constraints

`UniqueConstraint` and `PrimaryKeyConstraint` accept
`postgresql_include`:

```python
from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy import UniqueConstraint

account = Table(
    "account",
    MetaData(),
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    UniqueConstraint(
        "email",
        postgresql_include=["id"],
    ),
)
```

The named columns are emitted as PostgreSQL `INCLUDE` columns for the backing
constraint index. Keep uniqueness or primary-key membership in the positional
constraint columns; the included list is for additional stored columns.

## Column lists in referential actions

PostgreSQL foreign keys can carry a column list in `ON DELETE SET NULL (...)`
or `ON DELETE SET DEFAULT (...)`. Preserve the parenthesized column list in
the configured referential action when only part of a composite foreign key
should receive the null or default action.

This is PostgreSQL-specific SQL. Confirm the target server version and do not
expect another dialect to accept the same action text.

## Typed empty array literals

PostgreSQL cannot infer the element type of a completely empty array literal.
Pass `type_` to `array()`:

```python
from sqlalchemy import Integer, select
from sqlalchemy.dialects.postgresql import array

stmt = select(array([], type_=Integer))
```

The expression renders the required cast:

```sql
ARRAY[]::INTEGER
```

Pass the intended element type through `type_` so SQLAlchemy can render the
cast for the otherwise untyped empty literal.

## Reflection fidelity

PostgreSQL reflection preserves a non-default collation on a reflected type.
Schema-diff and round-trip tooling should compare that reflected collation
instead of assuming the database default.

Reflected index dictionaries also expose non-default operator classes:

```python
index_info["dialect_options"]["postgresql_ops"]
```

The value is keyed by column name. Consume it from `dialect_options` when
reconstructing an index or comparing reflected metadata; do not look for
operator classes only in the generic index fields.
