# Engine, SQL, and Schema

## Suppressing autocommit rollback

An engine can avoid DBAPI `.rollback()` calls when its dialect detects that
the connection is in autocommit:

```python
from sqlalchemy import create_engine

engine = create_engine(
    url,
    isolation_level="AUTOCOMMIT",
    skip_autocommit_rollback=True,
)
```

The option also suppresses the rollback normally performed when a connection
returns to the pool. It is specifically coupled to dialect autocommit
detection. Do not treat it as a general rollback-disable switch for
connections that may have an open transaction.

This is useful for a database or proxy where a rollback round trip in
autocommit is redundant or costly. Validate support with the actual dialect:
the safety of skipping the call depends on correctly identifying autocommit.

## Standalone constraint isolation

`AddConstraint` and `DropConstraint` accept `isolate_from_table`. Its default
is `True`:

```python
from sqlalchemy.schema import AddConstraint, DropConstraint

add = AddConstraint(constraint)
drop = DropConstraint(constraint)
```

Pass `isolate_from_table=False` when the constraint should remain eligible for
inline creation in the table's `CREATE TABLE` sequence:

```python
add = AddConstraint(
    constraint,
    isolate_from_table=False,
)
```

This choice matters when the same metadata participates in both table-level
creation and explicitly executed constraint DDL. Decide whether the
constraint is standalone or inline before assembling the DDL sequence so it
is neither unexpectedly separated nor emitted twice.

## `GROUPS` window frames

Both the top-level `over()` function and `FunctionElement.over()` accept a
`groups` frame specification. It follows the tuple form used by the existing
window-frame parameters:

```python
from sqlalchemy import func, select

group_total = func.sum(t.c.amount).over(
    order_by=t.c.id,
    groups=(None, 0),
)

stmt = select(t.c.id, group_total)
```

`(None, 0)` means unbounded preceding through the current group. `GROUPS`
frames count peer groups determined by the window ordering, unlike `ROWS`,
which counts physical rows. Use the frame style that matches the query's
semantics and check that the target server implements `GROUPS`.
