# Oracle and SQL Server

## Oracle vector types and expressions

The Oracle dialect provides `VECTOR` for dense vector columns. Its comparator
supports:

- `l2_distance`;
- `cosine_distance`; and
- `inner_product`.

Use these operations on a vector expression when constructing similarity or
distance ordering rather than spelling an Oracle vector function as
unstructured SQL.

Sparse vectors are represented by `SparseVector`, and
`VectorStorageType` describes vector storage choices. Preserve dense-versus-
sparse representation and storage type when generating schema or binding
values.

Oracle vector indexes accept the `oracle_vector` dialect option. Keep vector
index configuration in that Oracle-specific option rather than placing it in
generic index keyword arguments.

`Select.fetch()` accepts `oracle_fetch_approximate` for Oracle approximate
vector fetching:

```python
stmt = (
    select(items)
    .order_by(items.c.embedding.l2_distance(query_vector))
    .fetch(10, oracle_fetch_approximate=True)
)
```

Approximate fetching has different accuracy and execution characteristics
from an exact ordered fetch, so enable it deliberately.

## Oracle table tablespaces

Set `oracle_tablespace` on `Table` to select the creation tablespace:

```python
from sqlalchemy import Column, Integer, MetaData, Table

event = Table(
    "event",
    MetaData(),
    Column("id", Integer),
    oracle_tablespace="USERS",
)
```

The option affects Oracle table DDL. Keep environment-specific tablespace
names configurable when the same metadata is deployed to databases with
different storage layouts.

## aioodbc batching on SQL Server

The `mssql+aioodbc` dialect honors `fast_executemany`. Enable it on the async
engine when batched parameter execution should use the driver's accelerated
path:

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    url,
    fast_executemany=True,
)
```

Test the actual parameter shapes and driver because the option changes the
execution path used for batches.

## Conditional SQL Server index drops

On SQL Server 2016 and later, `DropIndex` honors `if_exists=True` and emits the
server-supported `IF EXISTS` form:

```python
from sqlalchemy.schema import DropIndex

ddl = DropIndex(index, if_exists=True)
```

Older behavior ignored this flag for SQL Server. Code targeting SQL Server
2016 or later can now use the SQLAlchemy DDL object for an idempotent drop
instead of wrapping the statement in hand-written existence checks.
