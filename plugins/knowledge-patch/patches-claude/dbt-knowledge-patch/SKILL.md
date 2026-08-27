---
name: dbt-knowledge-patch
description: dbt Core
version: "1.12.0"
license: MIT
metadata:
  author: Nevaberry
---


# dbt Core Knowledge Patch

Use this skill when maintaining dbt projects, packages, macros, automation, or
adapter integrations that rely on current Core behavior. Start with the quick
references below, then open the topic file that matches the task.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Behavior Flags and Migrations](references/behavior-flags-and-migrations.md) | Default changes, validation, deprecations, snapshot migration, compatibility flags |
| [CLI, Artifacts, and Runtime](references/cli-artifacts-and-runtime.md) | Commands, output, parser integration, artifacts, telemetry, dependency floors |
| [Incremental Models, Snapshots, and Freshness](references/incremental-snapshots-and-freshness.md) | Microbatch execution, retries, hard deletes, source and model freshness |
| [Managed Functions](references/managed-functions.md) | SQL, Python, and JavaScript UDF resources, overloads, selection, deferral |
| [Project Configuration and Semantic Layer](references/project-config-and-semantic-layer.md) | YAML, metadata, catalogs, Semantic Layer V2, OSI, packages, analyses |
| [Testing, Selection, and State](references/testing-selection-and-state.md) | Unit/data tests, selectors, state comparison, resource selection |

## Migration Priorities

Audit behavior flags before an upgrade. Keep compatibility opt-outs in the
version-controlled `flags` block of `dbt_project.yml`, and remove them after
the project adopts the new behavior.

```yaml
flags:
  require_resource_names_without_spaces: true
  source_freshness_run_project_hooks: true
  require_generic_test_arguments_property: true
  validate_macro_args: true
  require_all_warnings_handled_by_warn_error: true
```

Important default transitions:

- `require_resource_names_without_spaces` and
  `source_freshness_run_project_hooks` default to `true` in Core 1.10. Their
  legacy opt-outs warn and disappear in Core 2.0.
- `require_generic_test_arguments_property` arrives disabled in 1.10.5 and
  defaults to `true` in 1.10.8. Put generic-test inputs under `arguments`.
- `validate_macro_args` and `require_all_warnings_handled_by_warn_error`
  arrive disabled in 1.10 and default to `true` in 1.12.
- JSON Schema deprecation warnings are on by default in 1.12. Correct invalid
  project and resource YAML instead of depending on permissive parsing.

See [Behavior Flags and Migrations](references/behavior-flags-and-migrations.md)
for validation switches, adapter-specific flags, and deprecated interfaces.

## Generic Test Argument Shape

Use the nested form expected by the matured behavior flag:

```yaml
models:
  - name: orders
    columns:
      - name: status
        data_tests:
          - accepted_values:
              arguments:
                values: [placed, shipped, completed]
```

The older `tests:` key remains accepted alongside `data_tests:` without a
deprecation warning.

## Microbatch Models

For time-series incrementals, set `incremental_strategy: microbatch` together
with `event_time`, `begin`, and `batch_size`. Write SQL for one batch; dbt
automatically filters direct `ref()` and `source()` parents that have their own
`event_time` configuration.

```sql
{{ config(
    materialized='incremental',
    incremental_strategy='microbatch',
    event_time='event_occurred_at',
    begin='2020-01-01',
    batch_size='day',
    lookback=3
) }}

select * from {{ ref('stg_events') }}
```

- Configure `event_time` on every direct parent that should be pruned.
- Use `.render()` on a configured `ref()` to opt that parent out of filtering.
- Use both `--event-time-start` and `--event-time-end` for a backfill.
- Treat `event_time`, `begin`, and CLI bounds as UTC.
- PostgreSQL needs `unique_key`; Spark and BigQuery need `partition_by`.
- `dbt retry` reruns only failed batches.

Core 1.10 exposes the `batch` Jinja context. Pre-hooks run on the first batch,
post-hooks on the last, and retries honor `--threads`. From 1.10.20, retries
recompute batches using the original invocation time.

See [Incremental Models, Snapshots, and Freshness](references/incremental-snapshots-and-freshness.md)
for all strategy options, custom strategies, and freshness configuration.

## Snapshot Hard Deletes

Choose `hard_deletes: ignore`, `invalidate`, or `new_record`. `new_record`
adds `dbt_is_deleted`; `invalidate` closes the current row with `dbt_valid_to`.
Do not combine `hard_deletes` with legacy `invalidate_hard_deletes`.

Existing snapshot tables are not migrated automatically. Migrate schema and
data before changing an existing snapshot to a different hard-delete mode.

## Managed Functions

Define warehouse functions as DAG resources with a body under `functions/`
and a YAML properties entry. Invoke one with `function()` so dbt records the
dependency and emits its qualified warehouse name.

```sql
select {{ function('is_positive_int') }}(value)
from {{ ref('input_values') }}
```

```bash
dbt build --select "resource_type:function"
dbt build --select is_positive_int
```

Core supports SQL functions on BigQuery, Snowflake, Redshift, Postgres, and
Databricks; Python functions on Snowflake, BigQuery, and Databricks with Unity
Catalog; and JavaScript functions on Snowflake and BigQuery. Adapter rules,
overloads, deferral, and test setup are in
[Managed Functions](references/managed-functions.md).

## Freshness

Source and table configs may use `loaded_at_query` instead of a column-based
timestamp. Model freshness is config-only and is skipped unless `build_after`
is present.

```yaml
models:
  - name: orders
    config:
      freshness:
        build_after:
          updates_on: any
```

In Core 1.10, a time-based `build_after` requires both `count` and `period`.
Core 1.11 also permits `updates_on` without either time field.

## Empty and Sample Execution

- `dbt build --sample ...` limits work for sampled execution; sampling follows
  referenced seeds and snapshot dependency graphs.
- `dbt seed --empty` creates seed relations without loading rows.
- Snapshots support `--empty`, and Jinja can inspect `flags.EMPTY`.
- Before a unit test that calls a managed function, build the function and
  model ancestors with `dbt build --select "+my_model_to_test" --empty`.

## Selection, State, and Tests

- Select a unit test directly with `unit_test:test_order_total`.
- `dbt test` accepts `--resource-type` and `--exclude-resource-type`, including
  corresponding environment-variable flags.
- With `--favor-state`, dbt favors a deferred relation only when its node is
  not selected in the current command.
- `state_modified_compare_more_unrendered_values` expands unrendered property
  comparison while ignoring rendered Jinja in configs.
- A named selector may reuse another named selector via `method: selector`.

See [Testing, Selection, and State](references/testing-selection-and-state.md)
for custom test refs, SQL headers, package lookup, and function state behavior.

## CLI and Automation Checks

- `dbt show --quiet` and `dbt compile --quiet` retain their machine-readable
  command results while suppressing event logs.
- A `PartialSuccess` result exits nonzero from 1.9.1 onward.
- `dbt docs serve` binds to `127.0.0.1` unless `--host` is supplied.
- `dbt deps`, `dbt clean`, and `dbt init` do not change the caller's working
  directory; embedded callers must manage paths explicitly.
- Prefer `--select`; `--models`, `--model`, and `-m` are deprecated.
- `dbt run-operation --sql` executes ad-hoc SQL or Jinja without a wrapper
  macro, and its macros may `ref()` private or protected models.

## External Parser Integration

`--use-v2-parser` runs an external parser and loads its `manifest.json` into
Core. Choose the command with `--v2-parser`, `DBT_ENGINE_V2_PARSER`, or project
flags. Core 1.12 initially requires `dbt-core-experimental-parser>=2.0.0a4`;
the 1.12.2 behavior raises that minimum to `2.0.0b1`.

```bash
dbt parse --use-v2-parser \
  --v2-parser "dbt-core-experimental-parser parse"
```

For runtime floors, dependency bounds, artifacts, structured logs, OpenTelemetry,
and Fusion manifests, open
[CLI, Artifacts, and Runtime](references/cli-artifacts-and-runtime.md).
