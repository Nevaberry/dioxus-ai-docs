# Upgrades and Compatibility

## PostgreSQL compatibility boundaries

TimescaleDB 2.19.0 is the last minor release supporting PostgreSQL 14. Upgrade
PostgreSQL before installing a later minor.

TimescaleDB 2.23.0 supports PostgreSQL 15, 16, 17, and 18, with existing
features available on PostgreSQL 18. PostgreSQL 15 support was announced
through June 2026, without naming the first TimescaleDB release that would drop
it at that point.

TimescaleDB 2.28.0 resolves that boundary: 2.28.x is the final minor series
supporting PostgreSQL 15, while 2.29 supports only PostgreSQL 16, 17, and 18.
Upgrade PostgreSQL before moving beyond TimescaleDB 2.28.

## Hypercore access-method removal

The experimental `hypercore` table access method introduced in 2.18.0 was
deprecated in 2.21.0 and removed in 2.22.0. Upgrading to 2.22 or later is
blocked while any relation uses it. Convert all such relations back to heap:

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

The removed access method and the supported columnstore feature are distinct;
do not disable columnstore merely because `hypercore` must be removed.

## Columnstore naming deprecations

Since 2.18.0, use columnstore-named APIs and reloptions in new code. The older
compression names are deprecated for removal in the next major release:

- `decompress_chunk` becomes `convert_to_rowstore`; `compress_chunk` becomes
  `convert_to_columnstore`.
- Compression policy helpers become `add_columnstore_policy` and
  `remove_columnstore_policy`.
- Compression stats and settings views become their corresponding
  columnstore-named views.
- `timescaledb.compress`, `timescaledb.compress_segmentby`, and
  `timescaledb.compress_orderby` become `timescaledb.enable_columnstore`,
  `timescaledb.segmentby`, and `timescaledb.orderby`.

## Compression downgrade and upgrade checks

The early-access boolean algorithm in 2.19.0 creates a type older releases
cannot read. Before downgrading below 2.19, run timescaledb-extras
`utils/2.19.0-downgrade_new_compression_algorithms.sql`. Boolean compression is
enabled by default from 2.20.0.

Experimental UUID compression in 2.22.0 did not guarantee backward
compatibility. It was disabled by default through
`timescaledb.enable_uuid_compression`, then UUIDv7 compression became enabled
by default in 2.23.0.

In 2.22.0, downgrades are blocked when the `orderby` compression setting is
`NULL`. Resolve that setting before attempting a downgrade.

## Sparse-index migrations

Bloom sparse indexes on chunks compressed before 2.24.0 use a hash scheme that
could vary with build options and silently miss rows after a package change.
They are disabled on upgrade. Decompress and recompress affected chunks to
rebuild them. For the official APT AMD64 package, the scheme did not change;
those installations may enable legacy reads in server configuration:

```ini
timescaledb.read_legacy_bloom1_v1 = on
```

Before upgrading to 2.27.0, drop bloom sparse indexes on compressed `int2`
columns. They can omit predicate matches, and the upgrade is blocked while
they exist.

TimescaleDB 2.27 does not automatically use composite bloom filters made by
2.26 because metadata naming changed. Run timescaledb-extras
`utils/2.27.x-fix-composite-bloom-columns.sql`; it renames catalog columns and
does not require recompression.

## Removed continuous-aggregate paths

The tech-preview WAL invalidation path introduced in 2.22.0 and given an
explicit enablement GUC in 2.23.0 was removed in 2.25.0. Return deployments to
trigger-based invalidation before upgrading.

TimescaleDB 2.24.0 announced removal of the deprecated partial
continuous-aggregate format in the next release. Migrate affected aggregates:

```sql
SELECT cagg_migrate('<CONTINUOUS_AGGREGATE_NAME>');
```

The experimental `timescaledb_experimental.policies` view and the
`add_policies`, `alter_policies`, `show_policies`, `remove_policies`, and
`remove_all_policies` helpers were also slated for removal. Replace them with
the Jobs API.

## Other removals and private APIs

- `_timescaledb_functions.create_chunk_table` was removed in 2.20.0.
- `time_bucket_ng` and `_timescaledb_debug` were removed in 2.25.0.
- Adaptive chunking was removed as a backward-incompatible change in 2.28.0;
  stop relying on adaptive chunk sizing before upgrading.
- `_timescaledb_catalog.chunk_constraint` stopped being a table in 2.28.0. A
  temporary compatibility view preserves current query behavior, but it will
  also be removed. Move integrations to public informational views.

## Correctness-driven minimum versions

Upgrade to at least 2.26.0 before combining client-ordered Direct Compress with
`INSERT ... SELECT` from a compressed hypertable; an earlier data-loss path was
fixed there. That release also fixed wrong results or crashes from cross-type
comparisons against partition columns.

Upgrade to 2.29.2 before relying on affected compressed SkipScan `DISTINCT`
queries over mixed compressed and uncompressed rows. This patch also fixes
wrong results from `IS NULL` min/max sparse-index pushdown.

## Container image migration

TimescaleDB stopped building Bitnami images in 2.18.0. Move container
deployments to the official `timescale/timescaledb-ha` image.
