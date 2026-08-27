# Assets and automation

## Asset definitions and values

### External assets in selections (since 1.10.0)

The `include_sources` keyword on `AssetSelection` APIs was renamed to
`include_external_assets`. Update callers to the new keyword.

### Values through results and execution context (since 1.11.0)

`MaterializeResult(value=...)` invokes the asset IO manager and can be typed as
`MaterializeResult[T]`. `AssetExecutionContext.load_asset_value` dynamically
loads another asset through its IO manager, avoiding a required function
parameter for the upstream value.

```python
import dagster as dg

@dg.asset
def upstream() -> dg.MaterializeResult[int]:
    return dg.MaterializeResult(value=42)

@dg.asset(deps=[upstream])
def downstream(context: dg.AssetExecutionContext):
    return context.load_asset_value(dg.AssetKey("upstream"))
```

### Virtual assets (since 1.13.0)

The preview `is_virtual` parameter on `@asset` and `AssetSpec` represents a
view or derived table that reflects upstream changes without explicit
materialization. Virtual assets participate in staleness calculation,
execution planning, and declarative automation. Set
`enable_dbt_views_as_virtual_assets` to mark dbt views automatically.

```python
import dagster as dg

view = dg.AssetSpec("reporting_view", is_virtual=True)
```

### Kinds, owners, inputs, and table metadata (since 1.12.0 and 1.13.0)

- An asset can have as many as 10 kind annotations, up from three.
- `define_asset_job` and `build_schedule_from_partitioned_job` accept
  `owners`. Owners on asset jobs are validated while definitions load.
- Team-owner strings on jobs, schedules, and sensors may contain special
  characters.
- Op and asset input annotations accept `typing.Mapping` and
  `typing.Sequence`.
- `TableMetadataSet.storage_kind` identifies a backing system such as
  Snowflake, Databricks, or BigQuery.

## Selection expressions and organization

### Unified selection language (since 1.11.0)

Selection expressions combine lineage traversal, attribute filters, and
Boolean logic. The same form is used by Components YAML, the Asset Catalog,
saved selections, alerts, and insights. Run Gantt views have analogous op
selections.

### Partition and automation selectors (since 1.12.0 and 1.13.0)

Filter by partition-definition type, for example:

```text
partitions:"static"
```

Additional selection attributes are `sensor:`, `schedule:`, `job:`, and
`automation_type:`. The `is:` filter selects by asset type. A schedule or
sensor selector includes both directly selected assets and assets in jobs
targeted by that instigator.

```text
sensor:daily_refresh
automation_type:schedule
is:materializable
```

### Hierarchical asset groups (since 1.13.0)

Group names can use `/` separators and render as nested groups. Wildcard group
selection is supported:

```text
group:"marketing/*"
```

## Freshness and declarative automation

### Data-version changes (since 1.10.0)

`AutomationCondition.data_version_changed()` triggers when an asset's data
version changes.

### Run-tag conditions (since 1.11.0)

`AutomationCondition.all_new_updates_have_run_tags()` and
`any_new_update_has_run_tags()` inspect all new materializations since the
previous tick rather than only the latest run.
`all_new_executed_with_tags()` supplies a related tag filter for newly
executed partitions.

### Freshness evaluation branches (since 1.12.0)

Use `AutomationCondition.freshness_passed()`, `freshness_warned()`, and
`freshness_failed()` to branch on the latest freshness evaluation. The older
`build_.*_freshness_checks` helpers are superseded by freshness policies.
dbt and Sling translators no longer expose `get_freshness_policy` or parse
legacy policies from integration configuration.

### Declarative Automation for jobs (since 1.13.16)

As a preview feature, `define_asset_job` accepts `automation_condition`. Wrap
an asset-level condition in `AutomationCondition.any_job_root_assets_match()`
or `all_job_root_assets_match()` to launch one job run when its root assets
satisfy that condition. Evaluation history appears on the job page's
Automation tab.

```python
import dagster as dg

refresh_job = dg.define_asset_job(
    "refresh_job",
    automation_condition=dg.AutomationCondition.any_job_root_assets_match(
        dg.AutomationCondition.on_missing()
    ),
)
```

## Asset checks and retry behavior

### Evaluations, hooks, and targeted retries (since 1.11.0)

Ops can yield `AssetCheckEvaluation`. The `@asset` decorator accepts `hooks`
for success and failure callbacks. During re-execution, Dagster can retry only
the failed assets in a failed multi-asset step rather than rerunning every
asset in that step.

### Partition-aware checks (since 1.12.0)

`@asset_check` and `AssetCheckSpec` accept `partitions_def`, allowing checks to
run against individual partitions. The supplied partition definition must
match the target asset's definition.

### Edge behavior and history (since 1.13.0)

- Checks can target assets whose names contain dots.
- When a blocking check produces no result, downstream assets proceed with a
  warning. An emitted failed check still fails the step.
- Wiping an asset or selected partitions also clears the matching asset-check
  history.

## Partitions, schedules, and backfills

### Custom-calendar exclusions (since 1.11.0)

Time-window partition definitions accept `exclusions`, which omit selected
dates or times from a custom calendar.

### Multi-partition execution context (since 1.12.0)

`OpExecutionContext`, `AssetExecutionContext`, and
`AssetCheckExecutionContext` expose `multi_partition_key` during a
multi-partition run.

### Backfill and schedule controls (since 1.11.0)

`BackfillPolicy` is generally available. Backfill submission uses a thread
pool with four daemon workers by default. Asset backfills can receive run
config. A failed backfill cancels its in-progress runs before terminating.
`RunRequest` from a schedule can select a subset of asset checks.
