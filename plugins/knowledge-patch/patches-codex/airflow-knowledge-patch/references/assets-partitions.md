# Assets, partitions, and state

## Typed asset-event access

String keys do not work with `inlet_events`, `outlet_events`, or
`triggering_asset_events`. Address events with `Asset`, `AssetAlias`,
`Asset.ref`, or the lookup helpers. (3.0.0)

```python
from airflow.sdk import Asset, AssetAlias

outlet_events[Asset.ref(name="myasset")]
outlet_events[AssetAlias(name="myalias")]
outlet_events.for_asset(name="myasset")
outlet_events.for_asset_alias(name="myalias")
```

Use `create_asset_aliases()` to define aliases shared across Dag files.
(3.0.0)

Asset API responses use `scheduled_dags`, not `consuming_dags`. The field means
Dags that place the asset in `schedule`; it does not include every Dag that
uses the asset in another way. (3.1.0)

## Partition-aware asset scheduling

Asset-aware scheduling can trigger downstream Dags only for the updated
partition. `AllowedKeyMapper` validates keys, `ChainMapper` composes mappings,
and temporal mapper names use `StartOfXXXMapper` rather than `ToXXXMapper`.
Inlet events can be lazily filtered by time, order, and limit. Listeners can
receive asset-emission events. (3.2.0)

## Partition mapping

Mapping can express fan-out, rollup, categorical keys, temporal windows, and
runtime assignment. (3.3.0)

- `RollupMapper` combines input partitions.
- `FanOutMapper` expands a partition forward or backward.
- Categorical `FixedKeyMapper` maps explicit keys.
- `SegmentWindow` describes temporal windows.
- `WaitForAll` and `MinimumCount(n)` control readiness.
- `PartitionedAtRuntime` assigns keys when the Dag run begins.

Limit downstream expansion with
`[scheduler] partition_mapper_max_downstream_keys`; a mapper can override the
global cap.

`FanOutMapper` and the wait policies have public convenience imports in the
`3.3.1` batch:

```python
from airflow.partition_mappers import FanOutMapper, MinimumCount, WaitForAll
```

## Clearing, backfills, and event propagation

Partitioned Dags can be cleared and backfilled over partition ranges. The REST
API provides `clearPartitions` and bulk
`/dags/{dag_id}/clearDagRuns`; requests can select `partition_key` and a
`partition_date` window. CLI clear and backfill operations accept partition
ranges as well. Producer partition dates and task-emitted partition keys flow
through asset events to partitioned consumers. (3.3.0)

The Dag-run API can filter by partition date. The Dags list can filter by any
Dag-run state, including failed and successful states, and clearing a Dag run
can preserve task instances already in finished states. (3.3.1)

## Task and asset state stores

The Task SDK accessors `task_state_store` and `asset_state_store` persist JSON
state. Both support `get`, `set`, `delete`, and `clear`, plus expiration and
retention; task state can survive retries and runs and optionally clear on
success. Core and Execution APIs expose the stores, and triggers can read asset
state. (3.3.0)

The metadata database is the default store. Select a worker-side implementation
with `[workers] state_store_backend`; configure retention garbage collection
and row-size limits for the chosen deployment. `task_state_store.clear()` no
longer accepts `all_map_indices`.

## Multi-team asset and scheduling boundaries

Multi-team deployments initially isolate team Dags, Connections, Variables,
pools, executors, resources, and permissions. This surface is experimental in
the `3.2.0` batch.

Team enforcement later extends across assets, pools, XCom, and triggerers.
(3.3.0)

- Replace Asset SDK `allow_producer_teams` with `access_control`.
- `AssetAccessControl` adds `consumer_teams` and `allow_global`.
- Asset queries and the XCom Execution API are team-scoped.
- Pool scheduling enforces team ownership; pool CLI commands accept
  `--team-name`.
- Triggerers can be assigned and filtered by team.
