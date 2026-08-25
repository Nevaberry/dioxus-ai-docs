# Upgrades and compatibility

Use this reference before upgrading or downgrading TimescaleDB, PostgreSQL, or
container images, and when retiring private or experimental APIs.

## PostgreSQL support boundaries

- 2.19.0 is the final TimescaleDB minor release supporting PostgreSQL 14.
  Upgrade PostgreSQL before moving beyond it.
- 2.23.0 supports PostgreSQL 15, 16, 17, and 18, with existing features
  available on PostgreSQL 18. At that point PostgreSQL 15 support was announced
  through June 2026, but the first release dropping it was not yet specified.
- 2.28.0 is the final minor series supporting PostgreSQL 15. Its 2.28.x patch
  releases continue that support; 2.29 supports only PostgreSQL 16, 17, and 18.

## Hypercore removal

The experimental `hypercore` table access method arrived in 2.18.0, was
deprecated in 2.21.0, and was removed in 2.22.0. An upgrade to 2.22 or later is
blocked while any relation still uses it. Convert every such relation to heap:

```sql
DO $$
DECLARE
    relid regclass;
BEGIN
    FOR relid IN
        SELECT cl.oid
        FROM pg_class AS cl
        JOIN pg_am AS am ON am.oid = cl.relam
        WHERE am.amname = 'hypercore'
    LOOP
        EXECUTE format('ALTER TABLE %s SET ACCESS METHOD heap', relid);
    END LOOP;
END
$$;
```

## Compression and sparse-index migrations

### Boolean-compression downgrade

The custom boolean compression algorithm was opt-in early access in 2.19.0;
older releases cannot read its encoded type. Before downgrading data that used
it, run:

```text
timescaledb-extras/utils/2.19.0-downgrade_new_compression_algorithms.sql
```

Boolean compression became enabled by default in 2.20.0, so account for it
even when the enablement GUC was never set explicitly.

### Bloom sparse-index rebuild

Bloom indexes on chunks compressed before 2.24.0 use a hash that could vary
with build options and silently miss matching rows after a package change.
Decompress and recompress affected chunks to rebuild the indexes. Chunks
compressed after upgrading need no action.

For the official AMD64 APT package the hash did not change, so server
configuration can permit the legacy format for reads instead:

```ini
timescaledb.read_legacy_bloom1_v1 = on
```

### `int2` bloom upgrade block

Bloom sparse indexes on compressed `int2` columns can omit rows matching a
`SELECT` predicate. The 2.27.0 upgrade is blocked while affected indexes are
present. Drop them manually first.

### Composite bloom metadata

TimescaleDB 2.27.0 does not automatically use composite bloom filters created
by 2.26.0 because metadata naming changed. Run:

```text
timescaledb-extras/utils/2.27.x-fix-composite-bloom-columns.sql
```

This migration changes only catalog metadata; recompression is unnecessary.

## Continuous-aggregate migrations

WAL-based invalidation was a 2.22.0 tech preview, gained an explicit GUC in
2.23.0, and was removed in 2.25.0. Return to trigger-based invalidation before
upgrading.

The release after 2.24.0 was scheduled to remove the deprecated partial
continuous-aggregate format. Migrate any remaining view before moving on:

```sql
SELECT cagg_migrate('<CONTINUOUS_AGGREGATE_NAME>');
```

Replace the experimental `timescaledb_experimental.policies` view and its
`add_policies`, `alter_policies`, `show_policies`, `remove_policies`, and
`remove_all_policies` functions with the Jobs API; these were scheduled for
removal on the same timeline.

## Removed APIs and behavior

- The internal `_timescaledb_functions.create_chunk_table` helper was removed
  in 2.20.0. Do not call internal chunk-creation functions.
- The experimental `time_bucket_ng` function and `_timescaledb_debug` schema
  were removed in 2.25.0. Migrate SQL and tooling that depends on them.
- Adaptive chunking was removed as a backward-incompatible change in 2.28.0.
  Stop relying on adaptive chunk sizing before upgrade.
- `_timescaledb_catalog.chunk_constraint` stopped being a table in 2.28.0.
  A temporary compatibility view preserves current queries, but that view is
  also scheduled for removal. Move integrations to informational views.

## Compression-setting downgrade check

Compression settings are applied at compression time and support `ALTER TABLE
RESET` since 2.22.0. A downgrade is blocked if the `orderby` setting is `NULL`;
normalize such settings before attempting it.

## Query-correctness upgrade boundaries

- The 2.26.0 release corrects a data-loss path for client-ordered Direct
  Compress with `INSERT ... SELECT` from a compressed hypertable. Avoid that
  combination on earlier releases.
- The 2.26.0 release also corrects wrong results or crashes from cross-type
  comparisons against a partitioning column.
- In 2.29.2, compressed SkipScan no longer loses uncompressed rows when sort
  keys differ from distinct keys and no longer attaches to mismatched index
  paths under `MergeAppend`.
- In 2.29.2, min/max sparse-index pushdown correctly handles `IS NULL`.
  Earlier releases can return wrong results for that predicate.

## Container images

TimescaleDB stopped building Bitnami images in 2.18.0. Move container
deployments to the official `timescale/timescaledb-ha` image.
