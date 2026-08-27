# Engine, SQL, and Schema

## Suppressing autocommit rollbacks

As of 2.0.51, set `skip_autocommit_rollback=True` when the dialect can detect
that a DBAPI connection is already in autocommit and rollback calls are
unwanted:

```python
from sqlalchemy import create_engine

engine = create_engine(
    url,
    isolation_level="AUTOCOMMIT",
    skip_autocommit_rollback=True,
)
```

The option also suppresses the rollback normally issued when a pooled
connection is returned. Suppression depends on dialect-level autocommit
detection; do not use it as a reason to skip rollback in transactional work.

## Standalone constraint isolation

In 2.0.51, `AddConstraint` and `DropConstraint` accept
`isolate_from_table`. The option defaults to `True`. Pass `False` when a
constraint should remain eligible for inline creation within its table's
`CREATE TABLE` sequence:

```python
from sqlalchemy.schema import AddConstraint

ddl = AddConstraint(constraint, isolate_from_table=False)
```

Review DDL ordering when metadata-level table creation and explicit constraint
DDL are both present.

## `GROUPS` window frames

`over()` and `FunctionElement.over()` accept `groups=` in 2.0.51, parallel to
the existing window-frame options:

```python
from sqlalchemy import func

running = func.sum(t.c.amount).over(
    order_by=t.c.id,
    groups=(None, 0),
)
```

The tuple renders an unbounded-preceding-to-current-group frame. Confirm that
the database supports SQL `GROUPS` frames.

## Decimal return scale without native decimals

In 2.0.52, DBAPIs that do not return native decimals honor
`Numeric(decimal_return_scale=n)` during conversion. Previously the setting
could be ignored in favor of `Numeric.scale`. Processed `Decimal` values may
therefore have a different number of fractional digits after an upgrade; test
serialization, equality, and rounding assumptions that depend on scale.

## Independent defaults in metadata copies

`Table.to_metadata()` in 2.0.52 copies column default and on-update objects
instead of sharing them with the source table. This includes sequences and
server-side defaults. Each copied object remains associated with the copied
column and metadata, so code inspecting a copied table should expect distinct
object identities and ownership.
