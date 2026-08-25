# Maintenance, Statistics, and Rewrites

## Snapshot expiration

Core snapshot expiration can remove unused partition specs as of 1.8.0. The
Flink integration also gains snapshot-expiration support.

In 1.10.0, `ExpireSnapshots.cleanExpiredMetadata` lets callers control cleanup
of expired metadata.

Iceberg 1.11.0 adds `cleanupMode` to core snapshot expiration. Spark's
`expire_snapshots` supports `cleanupLevel=None` when expiration should perform
no cleanup.

Choose the cleanup behavior explicitly. Expiring snapshot references and
deleting associated metadata or data are separable concerns.

## Partition statistics

Core adds partition-statistics readers and writers in 1.9.0.

In 1.10.0:

- Core supports incremental partition-statistics refresh.
- Iceberg corrects the field IDs written to partition-statistics files.
- Spark adds an action and a procedure for computing partition statistics.
- Partition statistics account for deletion vectors.

In the `1.11.0-guides` APIs, a composable and filterable Partition Stats Scan
replaces the single-shot reader. Scans can expose their `FileIO`.

The REST protocol adds `SetPartitionStatisticsUpdate` and
`RemovePartitionStatisticsUpdate` in the same guidance.

In 1.11.0, `RewriteTablePath` rewrites partition-statistics files along with
the other table artifacts.

## Content statistics

The `1.11.0-guides` Content Stats API exposes file-level values including
bounds and null counts. The Partition Stats Scan API can filter and compose
partition-statistics work instead of forcing a single all-at-once read.

In 1.10.0, metrics preserve the original value type of lower and upper bounds.
Consumers should not coerce bounds to a different logical type when evaluating
or reporting them.

## Rewrite architecture

Core 1.9.0 adds a `FileRewritePlanner` implementation and separates rewrite
planning from execution through distinct planner and runner interfaces. This
allows callers to plan a bounded set of work and execute it independently.

Core 1.10.0 can cap the number of files in a rewrite.

Spark rewrite controls across these APIs include:

- Case-sensitive filtering and a configurable delete-file ratio from 1.8.0.
- Incremental table-path filtering by snapshot ID in 1.10.0.
- Custom partition order for `RewriteManifest` in 1.10.0.
- Optional executor-cache disabling for file-deletion work in 1.10.0.
- Branch targeting for `rewrite_data_files` in 1.11.0.
- `sort_by` ordering for `rewrite_manifests` in 1.11.0.

Flink 1.10.0 `RewriteDataFiles` accepts filters. In the
`1.11.0-guides` behavior it accepts a dynamic filter, can target a branch, and
operates under the table-maintenance coordinator lock.

## Deletion-vector maintenance

The 1.10.0 lifecycle rules require data-file rewrites to propagate applicable
deletion vectors and remove dangling ones. Cleanup tracks affected data files,
and partition-statistics maintenance includes deletion vectors.

Plan the data files and their deletion vectors as one unit. A rewrite that
commits the new data files but loses or strands a vector is invalid.

## Events and metrics

Manifest rewrites emit an update event and commit metrics as of 1.9.0.
`SnapshotManager` can report metrics through `MetricsReporter`.

Use the event to observe that an update occurred and the commit metrics to
measure its result. Do not infer a successful commit solely from rewrite work
being planned.

## Fast append across specs

A 1.8.0 fast append can add files belonging to multiple partition specs in one
operation. Maintenance code must retain each file's spec identity rather than
assuming a fast append has a single partition spec.

## Orphan cleanup

Flink table maintenance supports orphan-file deletion in 1.10.0.

Spark's remove-orphan-files operation adds `stream-results` in 1.11.0, which
returns results without collecting all of them into one response.

Coordinate orphan deletion with snapshots, branches, deletion vectors,
statistics files, and in-progress commits so live auxiliary files are not
mistaken for orphans.

## Maintenance checklist

1. Resolve the target table, branch, and snapshot boundary.
2. Select cleanup mode independently from snapshot selection.
3. Refresh or rewrite partition statistics when their referenced content
   changes.
4. Preserve lineage and deletion-vector associations.
5. Bound file counts and use filters in the planner.
6. Acquire the configured Flink coordinator or ZooKeeper lock where relevant.
7. Observe the commit event and metrics, not only the planning result.
8. Stream large orphan-result sets and delay deletion until liveness is known.
