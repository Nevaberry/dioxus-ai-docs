---
name: dbt-knowledge-patch
description: dbt Core
version: "1.12.0"
license: MIT
metadata:
  author: Nevaberry
---


# dbt Core Knowledge Patch

Use this patch when implementing, reviewing, automating, or upgrading dbt Core projects.
Start with behavior flags and deprecated interfaces, then open only the topic references needed for the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [CLI, selection, state, and automation](references/cli-selection-state-and-automation.md) | Selection, state, quiet output, sampling, parsers, docs serving, exit status, and automation |
| [Configuration, validation, and parsing](references/configuration-validation-and-parsing.md) | Behavior flags, YAML and SQL validation, project inputs, catalogs, selectors, and resource configuration |
| [Execution, incremental models, and freshness](references/execution-incremental-and-freshness.md) | Microbatch execution, hooks, retries, source and model freshness, snapshots, seeds, and empty runs |
| [Resources, tests, snapshots, and functions](references/resources-tests-and-functions.md) | Managed UDFs, unit and data tests, constraints, versioned models, macros, analyses, and resource names |
| [Runtime, adapters, and packages](references/runtime-adapters-and-packages.md) | Python and dependency floors, adapter behavior, private packages, working directories, and runtime compatibility |
| [Semantic metadata and artifacts](references/semantic-metadata-and-artifacts.md) | Semantic Layer and OSI inputs, metadata propagation, artifacts, structured logs, and telemetry |

## Breaking changes and deprecations

### Migrate generic-test arguments

With `require_generic_test_arguments_property`, generic-test inputs belong under `arguments`.
The flag defaults to `true` from Core 1.10.8, so migrate direct properties before enabling strict validation:

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

### Adopt strict resource names and freshness hooks

Core 1.10 defaults `require_resource_names_without_spaces` and
`source_freshness_run_project_hooks` to `true`. Rename resources containing spaces and make project hooks safe for
`dbt source freshness`. Temporary `false` values retain legacy behavior but emit deprecation warnings; Core 2.0 removes both flags.

### Replace deprecated command and project interfaces

- Use `--select` instead of `--models`, `--model`, or `-m`.
- Stop passing `--output` or `-o` to `dbt source freshness`.
- Replace source `overrides`, `modules.itertools`, and warn-error `include`/`exclude` terminology.
- Do not depend on project-level `quoting.snowflake_ignore_case`; it is inert from 1.10.11.
- A custom `generate_schema_name` macro should never return null; enable
  `require_valid_schema_from_generate_schema_name` while migrating.

### Prepare for stricter validation

Core validates project and resource YAML against JSON Schema, rejects duplicate YAML keys, validates SQL
`config()` calls, and diagnoses unsupported properties and unexpected Jinja. JSON Schema deprecation warnings are
on by default in Core 1.12. Treat warnings as migration work, especially when `--warn-error` is enabled.

```yaml
flags:
  validate_macro_args: true
  require_all_warnings_handled_by_warn_error: true
  require_valid_schema_from_generate_schema_name: true
```

The first two flags default to `true` in Core 1.12. Macro documentation that disagrees with the definition can
therefore fail strict builds.

### Update runtime assumptions

- Core 1.9 no longer supports Python 3.8.
- Core 1.11 no longer supports Python 3.9; use Python 3.10 or newer.
- Core 1.12 supports Python 3.14 and raises minimum versions of Click, `dbt-common`, and `dbt-adapters`.
- A `PartialSuccess` result returns a nonzero exit status from Core 1.9.1; CI must not treat it as success.
- `dbt deps`, `dbt clean`, and `dbt init` no longer change an embedded caller's working directory.

## High-value execution features

### Configure microbatch incremental models

Use `microbatch` for independently replaceable time-series batches. Set `event_time`, `begin`, and `batch_size` on
the model, and set `event_time` on every direct parent that should be auto-filtered.

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

An unconfigured parent is scanned in full for every batch. Call `.render()` on a configured `ref()` to opt that
parent out of automatic filtering. PostgreSQL also requires `unique_key`; Spark and BigQuery require
`partition_by`.

Backfills require both UTC bounds:

```bash
dbt run --event-time-start "2024-09-01" --event-time-end "2024-09-04"
```

`dbt retry` reruns only failed batches. Hooks run only on the first and last batches, and retries honor `--threads`.
See the execution reference before writing a custom strategy or depending on retry-time batch calculation.

### Handle snapshot hard deletes deliberately

`hard_deletes` accepts `ignore`, `invalidate`, or `new_record`. The last mode adds `dbt_is_deleted`; existing
snapshot tables are not migrated automatically.

```yaml
snapshots:
  - name: customer_snapshot
    config:
      unique_key: id
      strategy: timestamp
      updated_at: updated_at
      hard_deletes: new_record
```

Do not combine `hard_deletes` with legacy `invalidate_hard_deletes`. Migrate existing schema and data before
changing modes.

### Use query-driven and update-driven freshness

Sources and tables may use `loaded_at_query`. Models use config-only `freshness.build_after`; use `count` plus
`period` for elapsed-time freshness, or `updates_on` alone for an upstream-update trigger.

```yaml
models:
  - name: orders
    config:
      freshness:
        build_after:
          updates_on: any
```

Without `build_after`, model freshness is skipped.

## Managed warehouse functions

Define a function body in `functions/` and its signature in a properties file. Reference it with `function()` so
dbt qualifies the name and records the DAG dependency.

```sql
select {{ function('is_positive_int') }}(value)
from {{ ref('input_values') }}
```

```bash
dbt build --select "resource_type:function"
```

Check adapter and language support before choosing SQL, Python, or JavaScript. Function body, config, argument,
and return-type changes participate in `state:modified`. Unit tests do not create functions implicitly, so build
the function and tested model's ancestors first.

## New project and tooling inputs

- Put project variables in `vars.yml` and automatically loaded environment values in `.env`.
- Use `.sql.jinja` and `.md.jinja` suffixes where explicit Jinja-bearing extensions help tooling.
- Create schema-only seed tables with `dbt seed --empty`.
- Compose a named selector from another named selector with the `selector` method.
- Execute ad-hoc SQL or Jinja with `dbt run-operation --sql`.
- Use nested paths with `dbt ls --output json --output-keys`, such as `config.materialized`.

## Semantic and artifact checks

Core parses V2 Semantic Layer YAML and OSI documents, but model-as-Semantic-Model and column-dimension parsing
are not fully ready in Core 1.12. Validate generated manifests before downstream use. Catalog configuration,
semantic metadata, artifact fields, runtime-only `dbt ls` fields, and OpenTelemetry behavior are detailed in the
semantic metadata reference.

## Working method

When applying this patch:

1. Confirm the project's Core, adapter, Python, and package versions.
2. Read configuration notes before interpreting a warning as a local schema error.
3. Check adapter-specific limits for microbatch models and managed functions.
4. Treat behavior flags as staged migrations; document temporary opt-outs in `dbt_project.yml`.
5. Distinguish manifest fields from runtime-only CLI output before building automation.
6. Verify state/defer behavior when generated relations or functions can resolve across environments.
