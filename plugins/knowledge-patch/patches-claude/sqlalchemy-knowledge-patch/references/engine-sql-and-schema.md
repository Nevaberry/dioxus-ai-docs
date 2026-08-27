# Engine, SQL, and Schema

## Autocommit rollback suppression

Use `skip_autocommit_rollback=True` when the dialect can determine that the
DBAPI connection is already in autocommit and rollback calls are unwanted:

```python
from sqlalchemy import create_engine

engine = create_engine(
    url,
    isolation_level="AUTOCOMMIT",
    skip_autocommit_rollback=True,
)
```

This suppresses DBAPI `.rollback()` calls, including the rollback normally
issued when a pooled connection is returned. Suppression depends on
dialect-level autocommit detection; do not use it as a general substitute for
rollback in transactional operation. This option is available in 2.0.51.

## Standalone constraint isolation

`AddConstraint` and `DropConstraint` accept `isolate_from_table`, which
defaults to `True`. Pass `False` to keep a constraint eligible for inline
creation in the table's `CREATE TABLE` sequence:

```python
from sqlalchemy.schema import AddConstraint

ddl = AddConstraint(constraint, isolate_from_table=False)
```

Review DDL ordering when changing this setting, particularly when combining
metadata-level creation with explicit constraint DDL.

## `GROUPS` window frames

`over()` and `FunctionElement.over()` accept `groups=` in parallel with the
existing frame options:

```python
from sqlalchemy import func

running = func.sum(t.c.amount).over(
    order_by=t.c.id,
    groups=(None, 0),
)
```

The example describes an unbounded-preceding-to-current-group frame. Verify
that the target database supports SQL `GROUPS` frames.

## Decimal return scale

On DBAPIs that do not return native decimals,
`Numeric(decimal_return_scale=n)` controls conversion scale. It is no longer
ignored in favor of `Numeric.scale`. After moving to 2.0.52, processed
`Decimal` values may therefore contain a different number of fractional
digits. Audit serialization, equality assertions, and other code that depends
on that scale.

## Independent defaults in `Table.to_metadata()`

`Table.to_metadata()` copies column default and on-update objects rather than
sharing them with the source table. This includes sequences and server-side
defaults. Each copied object remains associated with the copied column and
metadata, so code that inspects these objects must expect distinct identities.
