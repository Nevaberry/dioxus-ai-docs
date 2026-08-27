# Scheduling, Assets, and Deadlines

Use this reference for timetable semantics, scheduler behavior, backfills, partitions, Assets, Dag versions, and Deadline Alerts.

## Scheduling semantics

### Scheduling defaults changed

During the 3.0 upgrade, note that `catchup_by_default` now defaults to `False`. `create_cron_data_intervals` also defaults to `False`, so a bare cron `schedule=` uses `CronTriggerTimetable` rather than `CronDataIntervalTimetable`. If tasks depend on interval boundaries or derived `ds`/`ts` values, set it to `True` before upgrading. Switching it back after Airflow 3 runs already exist skips one scheduled run to avoid a duplicate `logical_date`.

### Pool capacity limits priority weight

A task's effective `priority_weight` is capped by available pool slots. An arbitrarily high weight cannot override the pool resource constraint during task ordering.

### `ALL_DONE_MIN_ONE_SUCCESS` trigger rule

Since 3.1.0, this rule runs a task after every upstream task finishes and at least one succeeds. Skipped upstream tasks retain normal skip propagation.

### Scheduler run limits can count only idle loops

Use `airflow scheduler --only-idle` to make `--num-runs` count only idle scheduler loops. A run-limited scheduler can finish processing triggered Dags and queued tasks before exiting.

```bash
airflow scheduler --num-runs 1 --only-idle
```

### Continuous Dags no longer need a start date

Since 3.2.0, a Dag with `schedule="@continuous"` may omit `start_date` and begins running as soon as it is unpaused.

## Dag versions, reruns, and backfills

### Backfills are scheduler-managed

Since 3.0.0, backfills are no longer separate CLI jobs. The scheduler manages them as ordinary Dag runs with versioning and observability; start and monitor them through the UI or REST API.

### DAG structures are versioned

Task renames, dependency changes, and other Dag structure changes are persisted, and historical versions are exposed through the UI and API. The triggerer does not initialize Dag bundles, so trigger implementations cannot live only in a bundle; they must be importable elsewhere on `sys.path`.

### Reruns can select the Dag bundle version

Since 3.3.0, `rerun_with_latest_version` decides whether clear, rerun, backfill, and `TriggerDagRunOperator` rerun operations use the original or latest bundle. Precedence is request parameter or CLI flag, Dag setting, `[core] rerun_with_latest_version`, then `False` for clear/rerun and `True` for backfill.

### Provider example Dags use dedicated bundles

Provider example Dags now use bundles named `apache-airflow-providers-<distribution>-example-dags`, or `<distribution>-example-dags` for third-party providers. API clients that located examples by filtering for `dags-folder` must change their filters. `[core] load_examples` still controls registration.

## Asset references and events

### Asset event maps require typed references

Since 3.0.0, string keys do not work with `inlet_events`, `outlet_events`, or `triggering_asset_events`. Address an Asset or alias through `Asset`, `AssetAlias`, or `Asset.ref`, or use the lookup helpers.

```python
outlet_events[Asset.ref(name="myasset")]
outlet_events[AssetAlias(name="myalias")]
outlet_events.for_asset(name="myasset")
outlet_events.for_asset_alias(name="myalias")
```

### Asset aliases can be shared across DAG files

Use `create_asset_aliases()` to define aliases shared across Dag files.

### Asset API response key renamed

Since 3.1.0, Asset API responses use `scheduled_dags`, not `consuming_dags`. It means Dags that place the Asset in their `schedule`, not every Dag that otherwise uses it.

## Partitioned scheduling

### Assets can be scheduled by partition

Since 3.2.0, Asset-aware scheduling can trigger downstream Dags for only the updated partition. Use `AllowedKeyMapper` to validate keys and `ChainMapper` to compose mappings. Temporal mapper names use `StartOfXXXMapper`, not `ToXXXMapper`. Inlet events support lazy filtering by time, order, and limit, and listeners can receive Asset-emission events.

### Partition mapping supports fan-out, rollup, and runtime keys

Airflow 3.3.0 adds `RollupMapper`, `FanOutMapper`, categorical `FixedKeyMapper`, and `SegmentWindow`. Mappings can use temporal windows, `WaitForAll` or `MinimumCount(n)`, and forward or backward fan-out. `[scheduler] partition_mapper_max_downstream_keys` provides a global downstream-key cap with a per-mapper override. `PartitionedAtRuntime` assigns partition keys when a Dag run starts.

### Partitioned Dags can be cleared and backfilled by partition

The REST API adds `clearPartitions` and bulk `/dags/{dag_id}/clearDagRuns`, with `partition_key` and `partition_date` window selectors. CLI clear and backfill commands accept partition ranges. Producer partition dates and task-emitted partition keys propagate through Asset events to partitioned consumers.

### Dag and Dag-run APIs gained state and partition controls

Since 3.3.1, the Dag-run API can filter by partition date, the Dags list can filter by any Dag-run state including failed and successful, and clearing a Dag run can preserve task instances already in finished states.

### Partition mapper types have public convenience imports

Since 3.3.1, `FanOutMapper` and partition wait policies have direct public imports.

```python
from airflow.partition_mappers import FanOutMapper, MinimumCount, WaitForAll
```

## Clearing, routing, and retention

### Dag clearing, imports, and database maintenance gained controls

Since 3.2.0, Dag clear accepts `only_new` to clear only newly added task instances. `pools import` and `connections import` accept `--action-on-existing-key`; `airflow db init` again accepts `--use-migration-files`; database cleaning can explicitly include or exclude Dags.

### Triggers can be assigned to queued triggerers

The `trigger` command accepts `--queues` to route triggers by task queue to particular Triggerer hosts. `max_trigger_to_select_per_loop` limits per-loop selection in high-availability Triggerer deployments.

### Rendered-field retention is now Dag-run based

`max_num_rendered_ti_fields_per_task` is renamed to `num_dag_runs_to_retain_rendered_fields`; the old name is deprecated. Retention counts newest Dag runs rather than task executions, so sparse or conditional tasks may retain fewer records.

### Backfill authorization uses Dag-run permission

`BaseAuthManager.is_authorized_backfill` is removed. Backfills use `requires_access_dag` for `DagAccessEntity.Run`. Update policies that granted Backfill permission without Dag-run permission.

## Deadline Alerts

### Deadline Alert callbacks are experimental and asynchronous

In 3.1.0, a deadline can be relative to Dag-run queued time or logical date, or to a fixed datetime, using a positive or negative interval and notification callback. The feature is experimental and accepts only `AsyncCallback`; synchronous callbacks are not supported there.

### Deadline Alerts support synchronous callbacks and lists

In 3.2.0, experimental `SyncCallback` executes on an executor selectable through its `executor` parameter. A Dag's `deadline` can be a list mixing synchronous and asynchronous callbacks. At that version, synchronous callbacks cannot read Connections from the metadata database.

### Synchronous deadline callbacks can use runtime secrets

Since 3.3.0, `SyncCallback` deadline handlers can access Connections and Variables. Deadline Alerts also support names, Variable-resolved intervals, Core API endpoints, and a `callback_execution_timeout` setting.

## Multi-team scheduling

### Multi-team deployments are experimental

Airflow 3.2.0 introduces experimental isolation for each team's Dags, Connections, Variables, pools, executors, resources, and permissions within one deployment.

### Multi-team enforcement extends to assets, pools, and triggers

Since 3.3.0, Asset `access_control` replaces `allow_producer_teams`; `AssetAccessControl` adds `consumer_teams` and `allow_global`. The XCom Execution API and Asset queries are team-scoped. Pool scheduling enforces ownership, pool CLI commands accept `--team-name`, and triggerers can be assigned and filtered by team.
