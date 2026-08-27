---
name: dagster-knowledge-patch
description: Dagster
version: "1.13.0"
license: MIT
metadata:
  author: Nevaberry
---


# Dagster Knowledge Patch

Use this skill when upgrading or maintaining Dagster definitions, Components,
automation, execution infrastructure, storage, deployment configuration, or
integration packages. Check the installed Dagster and integration-package
versions first, then open the reference that matches the task.

## Working Method

1. Inspect `dagster`, integration-package, Python, and deployment-chart versions.
2. Identify removed or renamed APIs before changing behavior.
3. Validate definitions with `dg check` or the applicable definitions command.
4. For daemon, executor, storage, or launcher changes, test failure and retry paths.
5. Consult the topic references for exact settings, defaults, and integration details.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Assets and automation](references/assets-and-automation.md) | Asset definitions, checks, freshness, partitions, selections, ownership, and automation |
| [Components and CLI](references/components-and-cli.md) | Components, templates, scaffolding, `dg`, configuration, and API queries |
| [Deployment and storage](references/deployment-and-storage.md) | Helm, Kubernetes, ECS, databases, authentication, state, and storage defaults |
| [Execution and operations](references/execution-and-operations.md) | Coordinators, pools, executors, backfills, GraphQL, logs, sensors, and Pipes |
| [Integrations](references/integrations.md) | dbt, Airbyte, Fivetran, Databricks, BI tools, IO managers, and other packages |
| [Upgrade and compatibility](references/upgrade-and-compatibility.md) | Removed APIs, renamed settings, package lifecycle, Python, and dependency requirements |

## Upgrade-Critical Changes

### Run launching requires the daemon by default

The queued run coordinator is the default. Ensure the Dagster daemon is running,
or explicitly restore immediate in-process launching:

```yaml
run_coordinator:
  module: dagster.core.run_coordinator.sync_in_memory_run_coordinator
  class: SyncInMemoryRunCoordinator
```

Concurrency-key and pool blocking is also enabled by default. At op granularity,
a run may dequeue when one op can run; at run granularity, every pool used by the
run needs a free slot.

### Replace removed asset APIs

- Rename `include_sources` to `include_external_assets` on `AssetSelection` APIs.
- Pass `AssetSpec` objects directly to `Definitions`; do not call
  `external_asset_from_spec` or `external_assets_from_specs`.
- Pass `deps` as a sequence, even for one dependency. Use `AssetDep` when a
  partition mapping or other dependency configuration is required.
- Replace `Definitions.get_all_asset_specs()` with
  `Definitions.resolve_all_asset_specs()`.

```python
from dagster import AssetDep, AssetSpec, Definitions, asset

@asset(deps=[AssetDep("upstream")])
def downstream():
    ...

defs = Definitions(assets=[AssetSpec("external_table"), downstream])
```

### Follow the freshness API transition

`FreshnessPolicy` first replaced the legacy top-level type and later returned to
the top-level `dagster` module with `apply_freshness_policy`. Use:

```python
from dagster import FreshnessPolicy, apply_freshness_policy
```

Freshness evaluation runs by default. Disable it only when intentional:

```yaml
freshness:
  enabled: false
```

Remove legacy freshness and observation parameters from source assets, asset
definitions, outputs, integration translators, and asset-loading helpers. Express
freshness through policies and schedule- or sensor-backed automation conditions.

### Update Component loading

For current Component code, call `context.load_component(...)` and
`context.build_defs(...)`. The older `load_component_at_path` and
`build_defs_at_path` compatibility methods were removed. Outside a `defs` folder,
use `load_from_defs_folder(path)` rather than the deprecated `load_defs`.

Component configuration also moved toward top-level `post_processors`, direct
resource fields, typed `Component` subclasses, and persisted discovery state.
Read the Components reference before migrating custom YAML or templates.

### Use the modern CLI surface

Use `create-dagster project` for a new project and `dg` for development,
scaffolding, checks, launching, listing, utilities, and Dagster+ workflows. All
`dagster project` commands are removed. `dg docs integrations` moved to
`dg utils integrations`, which was subsequently removed; do not script either
legacy command.

Replace `dagster-cloud ci check` with `dg plus deploy start`. It validates the
deployment as part of the deploy flow.

### Check runtime and database dependencies

Python 3.10 is the minimum after Python 3.9 support was dropped. Most libraries
support Python 3.14, while deployment tooling supports the documented subset.
Dagster also supports protobuf 6.x and no longer imposes the old Click `<8.2` cap.

MySQL deployments need `dagster instance migrate` for the `LongText` migrations.
PostgreSQL users must declare `psycopg2-binary` themselves if they rely on it;
`dagster-postgres` no longer installs it transitively.

## High-Value Current Patterns

### Define Components in YAML or typed Python

Components are suitable as the default structure for new projects. Definitions
can live in `defs.yaml` or typed `Component` subclasses, and `@template_var`
exposes Python helpers to templates.

```yaml
deps:
  - "{{ load_component_at_path('dbt_ingest').asset_key_for_model('customers') }}"
```

When authoring against the newer template scope, use `context.load_component`
and access automation conditions, partitions, and freshness types through `dg`.
State-backed Components separate persisted discovery state from YAML or Python
configuration and support local state, versioned storage, and snapshots.

### Return and load asset values

`MaterializeResult(value=...)` invokes the asset IO manager and supports generic
typing. `AssetExecutionContext.load_asset_value` loads another asset through its
IO manager without making it a function parameter.

```python
import dagster as dg

@dg.asset
def upstream() -> dg.MaterializeResult[int]:
    return dg.MaterializeResult(value=42)

@dg.asset(deps=[upstream])
def downstream(context: dg.AssetExecutionContext):
    return context.load_asset_value(dg.AssetKey("upstream"))
```

### Use unified asset selections

Selection expressions combine lineage traversal, Boolean logic, and attribute
filters across Components YAML, the Asset Catalog, saved selections, alerts, and
insights. Current attributes include `sensor:`, `schedule:`, `job:`,
`automation_type:`, and `is:`. Hierarchical groups use `/` and wildcard matching.

```text
sensor:daily_refresh
automation_type:schedule
group:"marketing/*"
is:materializable
```

### Model virtual assets explicitly

Use the preview `is_virtual` parameter for views or derived tables that reflect
upstream changes without explicit materialization. Virtual assets participate in
staleness, execution planning, and declarative automation.

```python
import dagster as dg

view = dg.AssetSpec("reporting_view", is_virtual=True)
```

### Automate from data, freshness, or job roots

- `AutomationCondition.data_version_changed()` responds to data-version changes.
- Freshness passed, warned, and failed conditions branch on the latest evaluation.
- Run-tag predicates inspect newly materialized or executed updates.
- Preview job automation applies an asset condition to any or all root assets and
  launches one run for the job when the wrapped condition matches.

```python
import dagster as dg

refresh_job = dg.define_asset_job(
    "refresh_job",
    automation_condition=dg.AutomationCondition.any_job_root_assets_match(
        dg.AutomationCondition.on_missing()
    ),
)
```

## Operational Guardrails

- Custom process executors must emit and register a failure-or-retry event when
  resource initialization fails, or a run can remain stuck in `started`.
- GraphQL event queries are paginated at 1,000 events by default; follow cursors.
- Event error fields above 500 KB are truncated unless the environment limit is
  changed deliberately.
- A partial run config inherits omitted values from the job-level defaults.
- Validate matching partition definitions for partition-aware asset checks.
- Empty DataFrames are skipped by BigQuery, Snowflake, and DuckDB IO managers.
- Date-looking quoted YAML values remain strings.
- Inspect storage and deployment defaults before rolling out state-backed
  integrations, Kubernetes inheritance, authentication, or database changes.

## Validation Checklist

- Run definition validation and resolve duplicate asset keys or invalid mappings.
- Confirm the daemon, coordinator, pool granularity, and concurrency limits.
- Exercise retries, cancellation, backfills, and failure sensors in staging.
- Page through GraphQL logs rather than assuming the first response is complete.
- Confirm integration package versions and their separate dependency floors.
- Review generated deployment artifacts before applying them.
