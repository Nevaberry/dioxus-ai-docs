# Oracle and SQL Server

## Oracle vectors

The Oracle dialect provides the `VECTOR` type and the `l2_distance`,
`cosine_distance`, and `inner_product` operations. It also supports
`oracle_vector` index options and `oracle_fetch_approximate` for
`Select.fetch()`.

Sparse-vector support is available through `SparseVector` and
`VectorStorageType`. Select the dense or sparse representation that matches
the database column and the operations used by the query. These facilities
are available in 2.0.51.

## Oracle table tablespaces

Set `oracle_tablespace` on a `Table` to choose its creation tablespace:

```python
Table(
    "event",
    metadata,
    Column("id", Integer),
    oracle_tablespace="USERS",
)
```

## SQL Server aioodbc batching

The `mssql+aioodbc` dialect honors `fast_executemany`. Enable it on an async
engine when the workload should use pyodbc batching:

```python
engine = create_async_engine(url, fast_executemany=True)
```

## Conditional SQL Server index drops

On SQL Server 2016 and later, `DropIndex(index, if_exists=True)` emits the
supported `DROP INDEX IF EXISTS` form. The flag is no longer ignored, so use
it when a migration must tolerate an already-absent index.

## ODBC connection-parameter quoting

The pyodbc connector brace-quotes driver names, pass-through parameter names,
and pass-through values containing `}`. This prevents braces or semicolons in
parameter names from being parsed as extra ODBC connection attributes.

This safer parsing behavior is from 2.0.52. Continue to pass parameters as
parameters; do not preassemble ambiguous connection-string fragments.
