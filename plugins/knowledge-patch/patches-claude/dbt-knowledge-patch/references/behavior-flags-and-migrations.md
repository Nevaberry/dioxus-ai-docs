# Behavior Flags and Migrations

## Resource Names and Freshness Hooks

The `1.10-behavior-changes` batch makes two previously optional behaviors the
Core 1.10 defaults:

- `require_resource_names_without_spaces: true` rejects resource names that
  contain spaces.
- `source_freshness_run_project_hooks: true` makes `dbt source freshness` run
  project hooks.

Temporary compatibility opt-outs belong in the version-controlled `flags`
block of `dbt_project.yml`:

```yaml
flags:
  require_resource_names_without_spaces: false
  source_freshness_run_project_hooks: false
```

Explicit `false` values preserve the legacy behavior but continue to emit
deprecation warnings. Core 2.0 removes both flags and always uses the new
behavior.

## Generic Test Arguments

Core 1.10.5 introduces `require_generic_test_arguments_property` with a
default of `false`; 1.10.8 changes the default to `true`. When enabled, nest
generic-test arguments below `arguments` instead of placing them directly
under the test name.

```yaml
flags:
  require_generic_test_arguments_property: true

models:
  - name: orders
    columns:
      - name: status
        data_tests:
          - accepted_values:
              arguments:
                values: [placed, shipped, completed]
```

## Macro Arguments and Warning Handling

Core 1.10 introduces two opt-ins:

- `validate_macro_args` warns when documented macro arguments do not match the
  macro definition. `--warn-error` promotes these warnings to errors.
- `require_all_warnings_handled_by_warn_error` can stop a build when
  `--warn-error` is set.

Both begin with a `false` default and mature to `true` in Core 1.12.

```yaml
flags:
  validate_macro_args: true
  require_all_warnings_handled_by_warn_error: true
```

## Databricks Materialization V2

dbt-databricks 1.10.0 introduces `use_materialization_v2`, disabled by
default, to choose restructured materializations. Configure it as a project
behavior flag. No maturity release is specified.

```yaml
flags:
  use_materialization_v2: true
```

## Validation Defaults

The `1.10.0` changes begin JSON Schema validation of `dbt_project.yml` and
resource YAML. Validation also detects duplicate YAML keys, validates
`{{ config(...) }}` in model SQL even when static parsing is unavailable, and
warns about unexpected Jinja blocks and unsupported custom keys or properties.

Schema checks are adapter-gated, and some diagnostics begin as preview
deprecations. Diagnostics carry event names, summarize repeated violations,
and can be expanded to show every instance.

In `1.12.0`, JSON Schema-based deprecation warnings are raised by default.
Also:

- A custom `generate_schema_name` macro that returns null is deprecated behind
  `require_valid_schema_from_generate_schema_name`.
- Source and Semantic Model names containing spaces warn.
- `REQUIRE_SOURCE_AND_SEMANTIC_MODEL_NAMES_WITHOUT_SPACES` converts that name
  validation into an error.

```yaml
flags:
  require_valid_schema_from_generate_schema_name: true
```

## Deprecated Interfaces

Core 1.10 deprecates these interfaces:

- `dbt source freshness --output` and `-o`.
- The source `overrides` property.
- `modules.itertools` in Jinja.
- Model-selection aliases `--models`, `--model`, and `-m`; use `--select`.
- The terms `include` and `exclude` in warn-error options.

From 1.10.11, project-level `quoting.snowflake_ignore_case` is a no-op. Do not
rely on it to change identifier casing.

Core 1.12.2 warns when the installed dbt version is deprecated. This behavior
is recorded in the `1.12.1` batch.

## Snapshot Hard-Delete Migration

The `1.9-guides` behavior adds `hard_deletes` modes:

- `ignore` is the default and does not record source deletion.
- `invalidate` closes the current row by setting `dbt_valid_to`.
- `new_record` records deletion as a new row and adds `dbt_is_deleted`.

```yaml
snapshots:
  - name: my_snapshot
    config:
      unique_key: id
      strategy: timestamp
      updated_at: updated_at
      hard_deletes: new_record
```

Legacy `invalidate_hard_deletes` remains supported but cannot be combined with
`hard_deletes`. Existing tables are not migrated automatically, so migrate
their schema and data before changing modes; otherwise, use the setting only
for new snapshots. PostgreSQL, BigQuery, Snowflake, and Redshift support the
configuration.

## Resource and Package Lookup Compatibility

Core `1.11.0` adds two behavior flags:

```yaml
flags:
  require_unique_project_resource_names: true
  require_ref_searches_node_package_before_root: true
```

`require_unique_project_resource_names` restores an error for duplicate node
names within one project. `require_ref_searches_node_package_before_root`
makes an ambiguous package-internal `ref()` search the referencing node's
package before the root project.

## Latest-Version Relation Pointers

Core 1.12 can create an unversioned relation pointer, such as `dim_customers`,
for the latest version of a versioned model. Enable pointers project-wide with
`latest_version_pointer_enabled_by_default` or per model with
`latest_version_pointer`.

```yaml
flags:
  latest_version_pointer_enabled_by_default: true
```

Pointer collision checks honor quoting and case. Unquoted floating versions,
such as `v: 4.5`, are no longer silently discarded.
