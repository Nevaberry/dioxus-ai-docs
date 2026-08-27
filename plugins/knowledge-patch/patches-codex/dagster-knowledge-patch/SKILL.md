---
name: dagster-knowledge-patch
description: Dagster
version: "1.13.0"
license: MIT
metadata:
  author: Nevaberry
---


# Dagster compatibility guide

Use this skill when writing, reviewing, or migrating Dagster projects. Start by
identifying the installed Dagster and integration-package versions, then apply
only guidance relevant to those versions. Project manifests, runtime behavior,
and tests take precedence when they disagree with compatibility guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Assets and automation](references/assets-and-automation.md) | Asset values, virtual assets, selections, partitions, checks, freshness, and declarative automation |
| [Components and CLI](references/components-and-cli.md) | Components, state, templates, `dg`, scaffolding, deployment commands, and configuration |
| [Data integrations](references/data-integrations.md) | dbt, Airbyte, Fivetran, Databricks, BI tools, IO managers, and new packages |
| [Operations and deployment](references/operations-and-deployment.md) | Coordinators, pools, executors, backfills, GraphQL, databases, daemons, and runtime support |
| [Platform integrations](references/platform-integrations.md) | Kubernetes, Helm, ECS, Azure, Pipes, authentication, Teams, SCIM, and Airlift |
| [Upgrades and API](references/upgrades-and-api.md) | Removed and renamed APIs, freshness migration, CLI replacement, lifecycle labels, and package changes |

## Apply breaking changes first

### Replace removed asset APIs

- Pass `AssetSpec` objects directly to `Definitions`; do not call removed
  `external_asset_from_spec` or `external_assets_from_specs` helpers.
- Pass `deps` as a sequence. For a single configured dependency, use
  `deps=[AssetDep("upstream")]`.
- Replace `Definitions.get_all_asset_specs()` with
  `Definitions.resolve_all_asset_specs()`.
- Use `include_external_assets`, not the old `include_sources` keyword, in
  `AssetSelection` calls.

### Finish the freshness migration

- Import `FreshnessPolicy` and `apply_freshness_policy` from top-level
  `dagster`.
- Replace legacy freshness and observation parameters with
  `automation_condition` plus schedule- or sensor-based automation.
- Do not call the superseded `build_.*_freshness_checks` helpers or translator
  `get_freshness_policy` methods.
- Remember that the `FreshnessDaemon` evaluates policies by default. Set
  `freshness.enabled: false` in `dagster.yaml` only when that evaluation is
  intentionally disabled.

### Update Component loading

- Load a definitions folder with `load_from_defs_folder(path)` instead of the
  deprecated, non-public `load_defs`.
- Use `context.load_component(...)` and `context.build_defs(...)`. Their
  `*_at_path` compatibility methods were removed in the 1.13 upgrade.
- Put integration Component post-processors in top-level `post_processors`.
  For Sling, pass `connections` directly rather than `sling` or `resource`.

### Replace removed commands

- Create a project with `create-dagster project`; all `dagster project`
  commands are gone.
- Use `dg utils integrations` where older code used
  `dg docs integrations`, but note that `dg utils integrations` itself is
  removed in 1.13.
- Replace `dagster-cloud ci check` with `dg plus deploy start`.
- Ensure Python is at least 3.10; Python 3.9 support was dropped in 1.12.

### Repair integration migrations

- Replace `AirbyteState` with `AirbyteJobStatusType` and remove legacy
  freshness arguments from `build_airbyte_assets()`.
- Load Looker, Power BI, and Sigma specs through their `load_*_asset_specs`
  functions, pass translator instances, and construct `Definitions` from the
  returned specs.
- Declare `psycopg2-binary` directly if a PostgreSQL deployment requires it;
  `dagster-postgres` no longer installs it transitively.
- Run `dagster instance migrate` for the MySQL `LongText` migrations.

## Account for changed defaults

### Run launch and concurrency

The queued run coordinator is the default. A running Dagster daemon is
therefore required to launch runs. To preserve immediate in-process launching,
configure `SyncInMemoryRunCoordinator` explicitly:

```yaml
run_coordinator:
  module: dagster.core.run_coordinator.sync_in_memory_run_coordinator
  class: SyncInMemoryRunCoordinator
```

Concurrency blocking is also on by default. Under op granularity, a run can be
dequeued when one op has capacity; under run granularity, every pool used by
the run needs a free slot. Current pool names may contain any non-whitespace
character, so do not preserve the older alphanumeric-only validator.

### Configuration and persisted state

- Partial run config is merged with job-level defaults for omitted fields.
- State-backed integration Components default to `LOCAL_FILESYSTEM` storage,
  not legacy code-server snapshots. Configure storage explicitly when local
  files are unsuitable.
- `DagsterDbtTranslatorSettings.enable_source_metadata` defaults to `True`,
  which can remap upstream keys from dbt source table names.
- Date-looking YAML strings remain strings instead of becoming datetimes.

### Storage and checks

- The SQLite event-log `busy_timeout` default is 30 seconds.
- BigQuery, Snowflake, and DuckDB IO managers skip empty-DataFrame writes and
  warn rather than inferring a degenerate table.
- A missing result from a blocking asset check now warns and allows downstream
  assets to proceed; an explicitly failed result still fails the step.

## Use current asset patterns

### Return and load asset values

`MaterializeResult(value=...)` sends the value through the asset IO manager and
supports `MaterializeResult[T]`. A dependent asset can dynamically load a
value through its context:

```python
import dagster as dg

@dg.asset
def upstream() -> dg.MaterializeResult[int]:
    return dg.MaterializeResult(value=42)

@dg.asset(deps=[upstream])
def downstream(context: dg.AssetExecutionContext):
    return context.load_asset_value(dg.AssetKey("upstream"))
```

### Model virtual assets

Use preview `is_virtual=True` on `@asset` or `AssetSpec` for views and derived
tables whose state follows upstream changes without explicit materialization.
Virtual assets participate in staleness, planning, and declarative automation.

### Select assets consistently

Selection expressions combine Boolean logic, lineage traversal, and attribute
filters across Components YAML and the UI. Newer selectors include `sensor:`,
`schedule:`, `job:`, `automation_type:`, and `is:`. Group names may contain
`/`, and `group:"marketing/*"` selects nested groups.

### Use partition-aware checks and context

- Give `@asset_check` or `AssetCheckSpec` a `partitions_def` matching the
  target asset.
- Read `multi_partition_key` from op, asset, or asset-check execution context
  in a multi-partition run.
- Use time-window partition `exclusions` for custom calendars.
- Filter selections by partition type, such as `partitions:"static"`.

### Automate assets and jobs

- Use `AutomationCondition.data_version_changed()` for data-version changes.
- Use `all_new_updates_have_run_tags()`,
  `any_new_update_has_run_tags()`, or `all_new_executed_with_tags()` when
  decisions depend on tags across new updates.
- Use `freshness_passed()`, `freshness_warned()`, and `freshness_failed()` to
  branch on the most recent freshness evaluation.
- In 1.13.16, preview job automation accepts an `automation_condition` on
  `define_asset_job`; wrap asset conditions with
  `any_job_root_assets_match()` or `all_job_root_assets_match()`.

## Prefer current Component and CLI workflows

For new projects, define Components in `defs.yaml` or as typed Python
`Component` subclasses. Expose template helpers with `@template_var`, and use
`load_component_at_path` or `build_defs_at_path` only when maintaining code on
the older 1.11 surface.

Use the stable `dg` command groups for routine work:

- `dg scaffold` for definitions and deployment artifacts.
- `dg dev` for local UI startup.
- `dg launch` for launches.
- `dg list` and `dg api` for definition and deployment metadata.
- `dg check` for project validation.
- `dg plus` for Dagster+ login, configuration, environment, and deployment.

State-backed Components separate discovery state from YAML or Python config.
Treat state refresh as a deployment step; generated GitHub Actions workflows
do this for integrations that use the state-backed model.

## Operate safely

- Follow GraphQL cursors: `logsForRun` and `eventConnection` return at most
  1,000 events by default.
- Expect event error fields above 500 KB to be truncated unless
  `DAGSTER_EVENT_ERROR_FIELD_SIZE_LIMIT` is set.
- Custom process executors must emit, register, and handle a failure-or-retry
  event after resource initialization failure, or the run can remain started.
- Schedule, sensor, and asset daemons distribute instigator ticks round-robin
  across code locations.
- Use `DAGSTER_MAX_BACKFILL_RETRIES`; the former asset-specific variable is
  accepted only as a fallback.

## Verify a migration

1. Confirm the core and integration package versions from the environment.
2. Search for the removed names in the upgrade reference.
3. Validate definitions with `dg check` and the applicable definition-querying
   commands.
4. Exercise asset selections, partition mappings, checks, and job defaults.
5. Start the daemon when using the queued coordinator or freshness evaluation.
6. Test database migrations, state storage, and deployment-specific overrides
   before rollout.
7. Paginate GraphQL log consumers and confirm retry behavior for custom
   executors and external integrations.
