# Queries, Schema, and Indexing

Use this reference for query correctness, schema rendering and compatibility,
SAI, legacy secondary indexes, row filtering, and clustering order.

## CQL schema and query semantics

### Read partitions after column deletion (since 5.0.3)

Reading a partition whose column was deleted no longer fails with
`IndexOutOfBoundsException`. Regression tests should retain the delete-then-read
sequence when applications depend on it.

### Use descending UDT and vector keys (since 5.0.3)

Frozen UDTs and vectors can be clustering keys ordered with `DESC`.

```cql
CREATE TYPE coordinates (x int, y int);
CREATE TABLE samples (
    sensor_id uuid,
    position frozen<coordinates>,
    embedding vector<float, 3>,
    PRIMARY KEY (sensor_id, position, embedding)
) WITH CLUSTERING ORDER BY (position DESC, embedding DESC);
```

### Render UDTs in snapshot schema CQL (since 5.0.3)

Snapshot-generated schema CQL includes definitions for UDTs used as reverse
clustering columns. Restore tooling should execute those definitions before the
dependent table statement.

### Include views in `DESCRIBE TABLE` (since 5.0.4)

`DESCRIBE TABLE` includes the table's materialized views. Schema capture tools
must avoid separately appending the same view definitions a second time.

### Compute descending extrema correctly (since 5.0.4)

The built-in `min` and `max` functions return correct results for clustering
columns ordered descending. Do not invert their results as a client-side
workaround.

### Restrict `BytesType` compatibility (since 5.0.7)

`BytesType` is compatible only with scalar types. Schema evolution and schema
inspection tools must reject compatibility with non-scalar types.

## Filtering and reconciliation

### Keep unresolved static rows in RFP (since 5.0.4)

Replica filtering protection does not apply its fetch limit while a static row
remains unresolved. This prevents the row from being prematurely excluded from
distributed reconciliation.

### Evaluate numeric range intersections (since 5.0.5)

`RowFilter.isMutableIntersection()` evaluates numeric ranges on one column
correctly. Planning or extension code can use its result without compensating
for the former same-column range error.

## Index selection and accepted values

### Prefer a legacy index when it coexists with SAI (since 5.0.4)

If one column has both a legacy secondary index and SAI, Cassandra prioritizes
the legacy secondary index. Query plans and performance tests must account for
that choice.

### Reject invalid empty values (since 5.0.4)

Indexes do not accept empty values for non-literal types or other types that
forbid empty values. Validate such values before indexing rather than expecting
the index to store them.

### Notify indexes about fully expired rows (since 5.0.6)

During compaction, secondary index implementations receive notifications for
rows in fully expired SSTables. Custom index implementations should handle the
callback consistently with other row-removal paths.

## SAI query correctness

### Preserve intersection consistency (since 5.0.4)

SAI intersection queries avoid consistency violations involving repaired index
matches and matches on multiple non-indexed columns. Remove client-side query
splitting that existed only to avoid those cases.

### Query composite map filters (since 5.0.5)

Multi-column SAI queries work when a non-indexed column is a composite that
contains a map. The filter no longer fails merely because of that structure.

### Query static columns on one node (since 5.0.5)

Single-node SAI queries involving static columns return correct results. Keep
static and regular column expectations distinct in result validation.

### Execute ANN in score order (since 5.0.7)

SAI approximate-nearest-neighbor queries use score-ordered iterators. This
corrects result execution and improves query speed; do not re-sort a truncated
result set as a substitute for server-side score ordering.

### Reconcile distributed static tombstones (since 5.0.9)

For SAI queries on static columns, range tombstones are sent to the coordinator
so deleted ranges can be reconciled. Distributed tests should cover deletion
and replica divergence, not only single-node reads.

## SAI lifecycle and storage integration

### Mark indexes queryable after restart (since 5.0.5)

Already-built SAI indexes no longer have a gap between the node being marked
`UP` and the indexes becoming queryable. Clients need not delay solely to cover
that former state transition.

### Mark state after repair flushes (since 5.0.5)

When repair flushes a partial partition or row modification, SAI marks the index
as non-empty. Index state therefore reflects repair-produced data.

### Flush segments at writer switches (since 5.0.6)

Switching the current SSTable writer flushes the active SAI segment builder.
Index segment state is not left pending across the writer boundary.

### Force the optimized status format (since 5.0.7)

`IndexStatusManager` can be forced to use the optimized index-status format
when automatic selection is undesirable. Apply the override consistently
across nodes that exchange or consume index status.

### Validate checksums per segment (since 5.0.9)

SAI component checksum validation operates per segment. Segmented index
components are checked against their own checksum boundaries rather than a
whole-component assumption.
