# Assets and Automation

## Asset definition compatibility

### External selections and specifications

In 1.10.0, `AssetSelection` renamed `include_sources` to
`include_external_assets`. Use the new keyword.

The 1.13-upgrade removed `external_asset_from_spec` and
`external_assets_from_specs`. Pass `AssetSpec` instances directly to
`Definitions`, or build an `AssetsDefinition` from the specs.

```python
from dagster import AssetSpec, Definitions

defs = Definitions(assets=[AssetSpec("my_asset")])
```

### Dependency and resolution APIs

The 1.13-upgrade requires `deps` to be a sequence; a single `AssetKey` is no
longer accepted. Wrap one dependency in a list and use `AssetDep` when it needs a
partition mapping or other configuration.

```python
from dagster import AssetDep, asset

@asset(deps=[AssetDep("upstream")])
def downstream():
    ...
```

Also replace the removed `Definitions.get_all_asset_specs()` method with
`Definitions.resolve_all_asset_specs()`.

### Materialized values and context loading

Since 1.11.0, `MaterializeResult(value=...)` sends the value through the asset IO
manager and supports `MaterializeResult[T]`. An `AssetExecutionContext` can call
`load_asset_value` to load another asset through its IO manager without accepting
that asset as a function parameter.

```python
import dagster as dg

@dg.asset
def upstream() -> dg.MaterializeResult[int]:
    return dg.MaterializeResult(value=42)

@dg.asset(deps=[upstream])
def downstream(context: dg.AssetExecutionContext):
    return context.load_asset_value(dg.AssetKey("upstream"))
```

### Virtual assets

In 1.13.0, the preview `is_virtual` parameter on `@asset` and `AssetSpec` models
views or derived tables that reflect upstream changes without explicit
materialization. Virtual assets take part in staleness calculations, execution
planning, and declarative automation. dbt views can opt in automatically through
`enable_dbt_views_as_virtual_assets`.

```python
import dagster as dg

view = dg.AssetSpec("reporting_view", is_virtual=True)
```

### Kinds, ownership, input types, and metadata

- Since 1.12.0, an asset may carry up to 10 kind annotations rather than three.
- Since 1.13.0, `define_asset_job` and
  `build_schedule_from_partitioned_job` accept `owners`; owners are validated
  when definitions load, and team-owner strings for jobs, schedules, and sensors
  may contain special characters.
- Since 1.13.0, op and asset inputs accept `typing.Mapping` and
  `typing.Sequence` annotations.
- `TableMetadataSet.storage_kind` records the backing table system, such as
  Snowflake, Databricks, or BigQuery (1.13.0).

## Freshness

### Policy migration

In 1.11.0, the previous `FreshnessPolicy` became `LegacyFreshnessPolicy` and a
top-level `FreshnessPolicy` import errored. The deprecated alias remained under
`dagster.deprecated`, while asset and spec `freshness_policy` fields accepted the
new policy type and `ResolvedAssetSpec` resolvers could set it.

The 1.12-upgrade moved `FreshnessPolicy` and `apply_freshness_policy` out of
preview and exported them from top-level `dagster`:

```python
from dagster import FreshnessPolicy, apply_freshness_policy
```

Freshness evaluation now runs by default through `FreshnessDaemon`. Disable it
only when automatic evaluation is unwanted:

```yaml
freshness:
  enabled: false
```

The 1.13-upgrade removed `legacy_freshness_policy` and
`auto_observe_interval_minutes` from `@observable_source_asset`, and removed
legacy freshness-policy parameters from `AssetsDefinition`, `AssetOut`, and
`load_assets_from_*` helpers. Use policies plus schedule- or sensor-based
automation conditions.

### Freshness checks and condition branches

Since 1.12.0, the `build_.*_freshness_checks` helpers are superseded by freshness
policies. dbt and Sling translators no longer implement `get_freshness_policy`
or parse legacy policy configuration. Automation can branch with
`AutomationCondition.freshness_passed()`, `freshness_warned()`, and
`freshness_failed()` using the latest evaluation.

## Automation conditions

### Data-version and run-tag predicates

Since 1.10.0, `AutomationCondition.data_version_changed()` can react to an
asset's data-version change.

Since 1.11.0, `all_new_updates_have_run_tags()` and
`any_new_update_has_run_tags()` inspect every new materialization since the
previous tick rather than only the latest run. `all_new_executed_with_tags()`
provides a related tag predicate for newly executed partitions.

### Declarative job automation

In 1.13.16, preview job automation lets `define_asset_job` accept an
`automation_condition`. Wrap an asset-level condition with
`AutomationCondition.any_job_root_assets_match()` or
`all_job_root_assets_match()` to launch one job run when its root assets satisfy
the condition. The job page exposes evaluation history on its Automation tab.

```python
import dagster as dg

refresh_job = dg.define_asset_job(
    "refresh_job",
    automation_condition=dg.AutomationCondition.any_job_root_assets_match(
        dg.AutomationCondition.on_missing()
    ),
)
```

## Asset checks

- Since 1.11.0, ops may yield `AssetCheckEvaluation`, and `@asset` accepts
  `hooks` for success and failure callbacks.
- Re-execution can retry only the failed assets inside a failed multi-asset step
  instead of rerunning every asset in that step (1.11.0).
- Since 1.12.0, `@asset_check` and `AssetCheckSpec` accept `partitions_def` for
  per-partition checks. It must match the target asset's partition definition.
- In 1.13.0, checks may target asset names containing dots. A missing result from
  a blocking check warns and allows downstream assets to proceed, while an
  emitted failed check still fails the step. Wiping an asset or its partitions
  also clears its asset-check history.

## Partitions and selections

### Custom calendars and multipartitions

Time-window partition definitions accept `exclusions` for omitted dates or times
since 1.11.0. Since 1.12.0, `OpExecutionContext`, `AssetExecutionContext`, and
`AssetCheckExecutionContext` expose `multi_partition_key` in multi-partition
runs.

### Unified selection expressions

Since 1.11.0, asset selections combine lineage traversal, attribute filters, and
Boolean logic with shared syntax across Components YAML, the Asset Catalog,
saved selections, alerts, and insights. Run Gantt views provide analogous op
selections. Selection can filter by partition-definition type, such as
`partitions:"static"` (1.12.0).

In 1.13.0, selections added `sensor:`, `schedule:`, `job:`,
`automation_type:`, and `is:` attributes. Schedule and sensor selectors include
assets in targeted jobs as well as directly selected assets.

```text
sensor:daily_refresh
automation_type:schedule
is:materializable
```

Asset group names may now contain `/`, render hierarchically, and support
wildcards such as `group:"marketing/*"` (1.13.0).

## Definition validation

Since 1.11.0, definition validation rejects invalid partition mappings, including
time-partitioned dependencies with different time zones. `Definitions` and
`AssetsDefinition` also reject distinct `AssetSpec` objects that share an asset
key. Run validation before deployment.
