# Indexing and Query Correctness

## Index visibility and lifecycle

### SAI details in `nodetool tablestats`

`nodetool tablestats` reports selected SAI index state and query-performance
metrics through the existing table-statistics command (since 5.0.3):

```shell
nodetool tablestats
```

### Index choice when legacy 2i and SAI coexist

When a column has multiple indexes, Cassandra prioritizes a legacy secondary
index over SAI (since 5.0.4). Query plans and diagnostics should account for
that precedence.

### Empty-value indexing

Indexes reject empty values for non-literal types and other types that do not
permit empty values (since 5.0.4).

### SAI queryability after restart

Already-built SAI indexes no longer have a gap between a restarted node being
marked `UP` and its indexes becoming queryable (since 5.0.5).

### SAI state after repair flushes

When repair flushes a partial partition or row modification, SAI marks the
index as non-empty (since 5.0.5).

### SAI segments at SSTable-writer switches

Switching the current SSTable writer flushes the active SAI segment builder
(since 5.0.6), so index segment state is not left pending at the boundary.

### Expired-row notifications for secondary indexes

During compaction, secondary index implementations are notified about rows in
fully expired SSTables (since 5.0.6). Custom indexes can handle those rows
consistently.

### Segment-aware SAI checksum validation

SAI component checksums are validated per segment (since 5.0.9), matching
segmented index components to the correct checksum boundaries.

## Filtering and intersections

### Unresolved static rows in RFP

Replica filtering protection does not apply its fetch limit while a static row
remains unresolved (since 5.0.4).

### SAI intersection-query consistency

SAI intersection queries avoid consistency violations involving repaired index
matches and matches on multiple non-indexed columns (since 5.0.4).

### Numeric range intersection evaluation

`RowFilter.isMutableIntersection()` evaluates numeric ranges on a single
column correctly (since 5.0.5).

### SAI queries with composite map filters

Multi-column SAI queries do not fail when a non-indexed column is a composite
containing a map (since 5.0.5).

## Static columns, deletions, and reconciliation

### Reads after column deletion

Reading a partition whose column was deleted no longer fails with
`IndexOutOfBoundsException` (since 5.0.3).

### Complex collection-deletion serialization

Mutation serialization preserves complex deletions when a row contains
multiple collections (since 5.0.4); those deletions are no longer lost in
serialization.

### SAI queries over static columns

Single-node SAI queries involving static columns return correct results (since
5.0.5).

### Reconciliation-safe deletions

`RowFilter` does not purge deletions when reconciliation is required (since
5.0.5), preventing deletion loss while results are reconciled.

### Distributed SAI static-column tombstones

For distributed SAI queries on static columns, range tombstones are sent to
the coordinator (since 5.0.9), allowing deleted ranges to reconcile correctly.

## SSTable and ANN query execution

### Early-open BTI range queries

Range queries against early-open BTI SSTables return correct results (since
5.0.6), including before those files are fully opened.

### Score-ordered SAI ANN execution

SAI approximate-nearest-neighbor queries use score-ordered iterators (since
5.0.7), correcting result execution while improving query speed.
