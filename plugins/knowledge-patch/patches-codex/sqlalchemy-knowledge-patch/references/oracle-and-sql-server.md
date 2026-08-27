# Oracle and SQL Server

## Oracle vectors

In 2.0.51, the Oracle dialect provides the `VECTOR` type and its
`l2_distance`, `cosine_distance`, and `inner_product` operations. It also
supports `oracle_vector` index options and `oracle_fetch_approximate` for
`Select.fetch()`. Sparse vectors use `SparseVector` and `VectorStorageType`.

## Oracle table tablespaces

Oracle tables can select their creation tablespace with the 2.0.51 dialect
option `oracle_tablespace`:

```python
event = Table(
    "event",
    metadata,
    Column("id", Integer),
    oracle_tablespace="USERS",
)
```

## SQL Server aioodbc batching

The `mssql+aioodbc` dialect honors `fast_executemany` in 2.0.51:

```python
engine = create_async_engine(url, fast_executemany=True)
```

## Conditional SQL Server index drops

On SQL Server 2016 and later with SQLAlchemy 2.0.51,
`DropIndex(index, if_exists=True)` emits the supported `IF EXISTS` form rather
than ignoring the flag.

## Safer pyodbc parameter quoting

In 2.0.52, the pyodbc connector brace-quotes driver names, pass-through
parameter names, and pass-through values containing `}`. This prevents closing
braces, and semicolons embedded in a parameter name, from being parsed as
additional ODBC connection attributes.
