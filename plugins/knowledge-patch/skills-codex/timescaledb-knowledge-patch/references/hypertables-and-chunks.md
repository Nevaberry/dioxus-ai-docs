# Hypertables and chunks

Use this reference for declarative hypertable DDL, dimensions, UUIDv7
partitioning, triggers, and chunk lifecycle operations.

## Declarative hypertable DDL

Hypertables can be created through `CREATE TABLE ... WITH` since 2.20.0. The
declarative API accepts `columnstore` at creation time since 2.21.0:

```sql
CREATE TABLE metrics (
    time timestamptz NOT NULL,
    device_id text,
    value double precision
) WITH (
    tsdb.hypertable,
    tsdb.partition_column = 'time',
    tsdb.columnstore
);
```

In 2.23.0, `partition_column` became optional, and enabling columnstore in a
declarative definition began creating the columnstore policy automatically.
In Apache 2 Edition since 2.22.0, declarative creation no longer needs an
explicit `columnstore=false` option.

Existing hypertables can change their chunk interval through a reloption since
2.20.0:

```sql
ALTER TABLE metrics SET (timescaledb.chunk_time_interval = '1 day');
```

The expert `timescaledb.default_chunk_time_interval` GUC controls the default
for new hypertables since 2.26.0. Leave it unchanged unless specifically
recommended. Negative `chunk_interval` values are rejected as of 2.27.0.

Primary-dimension information has been exposed in the information schema since
2.20.0. Prefer that public metadata to private catalogs.

## Partition columns and table modes

UUIDv7 columns can partition hypertables since 2.22.0; chunk boundaries derive
from their embedded timestamps. Since 2.24.0, `time_bucket` accepts UUIDv7 and
the chunks informational view renders UUIDv7 ranges as timestamps. Retention
policies support UUIDv7 partitioning since 2.25.0:

```sql
SELECT add_retention_policy('events', INTERVAL '30 days');
```

Hypertables can be made unlogged since 2.23.0, trading durability for faster
large imports:

```sql
ALTER TABLE metrics SET UNLOGGED;
```

Cross-type comparisons against partition columns no longer risk wrong results
or crashes as of 2.26.0.

Adaptive chunking was removed in 2.28.0. Stop relying on adaptive chunk sizing
before upgrading. Creating a child table that inherits from a hypertable is
explicitly rejected since 2.27.0.

## Trigger behavior

Since 2.18.0, hypertables support transition-table triggers, but creating such
a trigger directly on a chunk is rejected.

Chunk-creation event triggers can run since 2.20.0. They default off behind:

```sql
SET timescaledb.enable_event_triggers = on;
```

Since 2.27.0, trigger state can be changed at the hypertable level:

```sql
ALTER TABLE metrics DISABLE TRIGGER metrics_validate;
ALTER TABLE metrics ENABLE TRIGGER metrics_validate;
```

## Attach, detach, split, and merge chunks

Uncompressed chunks can be manually attached to or detached from a hypertable
since 2.21.0, providing PostgreSQL-like partition attachment and detachment.

`split_chunk` was introduced for large uncompressed chunks in 2.20.0 and
extended to compressed chunks in 2.21.0. It divides at a specified time.

Chunk merging is supported since 2.18.0, but not for multidimensional
hypertables as clarified in 2.20.0. A concurrent merge mode is available since
2.24.0.

## Columnstore-related DDL

Compressed hypertables accept `DROP NOT NULL` since 2.18.0, and compressed
chunks accept `SET NOT NULL` since 2.19.0. Since 2.20.0, columnstore tables
permit foreign keys, compressed chunks permit `CHECK` constraints and columns
that carry them, and `ADD COLUMN` can include a unique constraint.

Since 2.24.0, `ALTER COLUMN TYPE` is allowed while columnstore is enabled if no
chunks are compressed:

```sql
ALTER TABLE metrics ALTER COLUMN value TYPE double precision;
```

## Publications, ownership, and `MERGE`

New chunks are automatically added to a hypertable's publication since
2.25.0.

The database owner can configure hypertables and policies since 2.28.0.
Hypertables also correctly handle `MERGE WHEN NOT MATCHED BY SOURCE` as of
2.28.0.
