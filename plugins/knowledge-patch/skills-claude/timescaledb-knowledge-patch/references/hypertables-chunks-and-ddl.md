# Hypertables, Chunks, and DDL

## Declarative hypertables

TimescaleDB 2.20.0 introduced declarative hypertable creation through `CREATE
TABLE ... WITH`, let existing hypertables use the `columnstore` alias for
`enable_columnstore`, and allowed chunk interval changes through a reloption:

```sql
ALTER TABLE metrics SET (timescaledb.columnstore = true);
ALTER TABLE metrics SET (timescaledb.chunk_time_interval = '1 day');
```

The declarative API gained `columnstore` at creation time in 2.21.0:

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

Apache 2 Edition stopped requiring explicit `columnstore=false` in 2.22.0.
In 2.23.0, `partition_column` became optional, and declarative creation with
columnstore enabled began creating the columnstore policy automatically.

The expert `timescaledb.default_chunk_time_interval` GUC controls the default
interval for new hypertables since 2.26.0. Leave it unchanged unless
specifically recommended. Negative `chunk_interval` values are rejected since
2.27.0.

## Reloptions and table persistence

A single `ALTER TABLE SET` can mix PostgreSQL and TimescaleDB options since
2.23.0:

```sql
ALTER TABLE metrics SET (
    fillfactor = 90,
    timescaledb.columnstore = true
);
```

Use `ALTER TABLE ONLY` to apply hypertable reloptions to future chunks only:

```sql
ALTER TABLE ONLY metrics
SET (timescaledb.orderby = 'time DESC');
```

Hypertables can be made unlogged since 2.23.0, trading durability for faster
large imports:

```sql
ALTER TABLE metrics SET UNLOGGED;
```

The database owner can configure hypertables and policies since 2.28.0.

## Chunk split, merge, attach, and detach

Chunk merging arrived in 2.18.0. `split_chunk` could divide a large
uncompressed chunk at a chosen time in 2.20.0; chunk merging remains
unsupported for multidimensional hypertables. In 2.21.0, `split_chunk` gained
compressed-chunk support, and uncompressed chunks gained manual attachment and
detachment resembling PostgreSQL partition operations. Concurrent chunk merge
mode arrived in 2.24.0.

## Constraints and column changes

Columnstore-related constraint support developed incrementally:

- Compressed hypertables accept `DROP NOT NULL` since 2.18.0.
- Compressed chunks accept `SET NOT NULL` since 2.19.0.
- Since 2.20.0, columnstore tables allow foreign keys, compressed chunks allow
  `CHECK` constraints and columns carrying them, and `ADD COLUMN` may include a
  unique constraint.
- Since 2.24.0, `ALTER COLUMN TYPE` works on a columnstore-enabled hypertable
  only if no compressed chunks exist.
- Since 2.25.0, compressed columns accept any immutable constant expression as
  a default.
- Since 2.28.0, an unsafe update to a unique column on a compressed chunk is
  rejected rather than executed.

Creating a child table that inherits from a hypertable is explicitly rejected
since 2.27.0.

## Triggers and event hooks

Hypertables support transition-table triggers since 2.18.0, but creating one
directly on a chunk is rejected. Chunk-creation event triggers arrived in
2.20.0 behind `timescaledb.enable_event_triggers`, default `OFF`.

`ENABLE TRIGGER` and `DISABLE TRIGGER` work on hypertables since 2.27.0:

```sql
ALTER TABLE metrics DISABLE TRIGGER metrics_validate;
ALTER TABLE metrics ENABLE TRIGGER metrics_validate;
```

## UUIDv7 partitioning and retention

UUIDv7 columns can be hypertable partition columns since 2.22.0. Chunk
boundaries derive from their embedded timestamps. Since 2.24.0, `time_bucket`
accepts UUIDv7 and returns a timezone-aware timestamp; the chunks informational
view also presents UUIDv7 ranges as timestamps. Retention policies support
UUIDv7-partitioned hypertables since 2.25.0:

```sql
SELECT add_retention_policy('events', INTERVAL '30 days');
```

## Publications and data modification

Since 2.25.0, new chunks are automatically added to a publication that
contains their hypertable. Cross-type comparisons against a partitioning
column no longer risk wrong results or crashes after the 2.26.0 fix.

Hypertables correctly handle `MERGE WHEN NOT MATCHED BY SOURCE` since 2.28.0.

## Metadata and private catalogs

Primary-dimension information became available in the information schema in
2.20.0, alongside APIs for the hypertable invalidation log and materialization
invalidations. Prefer those public surfaces.

`_timescaledb_catalog.chunk_constraint` stopped being a table in 2.28.0. A
temporary compatibility view preserves current query behavior, but that view
will also be removed. Move integrations away from this private catalog object
and onto TimescaleDB informational views.

The internal `_timescaledb_functions.create_chunk_table` helper was removed in
2.20.0; do not build tooling on it.
