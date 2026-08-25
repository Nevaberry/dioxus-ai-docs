# Configuration, Validation, and Parsing

Use this reference for behavior flags, schema diagnostics, project inputs, catalogs, selector configuration, and resource properties.

## Column and source configuration (1.9.0)

Columns accept a `config` mapping. Source freshness can also live under `config`, and explicit null freshness values are preserved.

```yaml
sources:
  - name: raw
    config:
      freshness:
        warn_after: {count: 12, period: hour}

models:
  - name: orders
    columns:
      - name: id
        config:
          meta:
            owner: analytics
```

## Resource names and freshness hooks (1.10-behavior-changes)

Core 1.10 changes the defaults of `require_resource_names_without_spaces` and `source_freshness_run_project_hooks` from `false` to `true`. Names containing spaces are rejected by default, and `dbt source freshness` runs project hooks by default.

Temporary compatibility opt-outs belong in the version-controlled `flags` block:

```yaml
flags:
  require_resource_names_without_spaces: false
  source_freshness_run_project_hooks: false
```

Explicit `false` values keep legacy behavior but continue to emit deprecation warnings. Core 2.0 removes both flags and always uses the new behavior.

## Generic-test argument nesting (1.10-behavior-changes)

Core 1.10.5 introduces `require_generic_test_arguments_property` with default `false`; Core 1.10.8 changes the default to `true`. When enabled, put generic-test inputs under `arguments`:

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

## Macro-argument and warning handling (1.10-behavior-changes)

`validate_macro_args` warns when documented macro arguments disagree with the macro definition. `require_all_warnings_handled_by_warn_error` can stop a build under `--warn-error`. Both begin disabled and mature to default `true` in Core 1.12.

```yaml
flags:
  validate_macro_args: true
  require_all_warnings_handled_by_warn_error: true
```

## Schema validation and diagnostics (1.10.0)

Core validates `dbt_project.yml` and resource YAML against JSON Schema, checks duplicate YAML keys, and validates `{{ config(...) }}` in model SQL even when static parsing is unavailable. It warns about unexpected Jinja blocks and unsupported custom keys or properties. Some schema checks are adapter-gated and some arrive as preview deprecations.

Diagnostics identify their event, summarize repeated violations, and can be expanded to show every instance. Under Core 1.12, JSON Schema-based deprecation warnings are raised by default.

## Source overrides and Jinja interfaces (1.10.0)

Source `overrides` and `modules.itertools` are deprecated. Migrate configurations and macros rather than suppressing their diagnostics.

## Catalog integration V1 (1.10.0)

Core parses `catalogs.yml`; from 1.10.12, parsing also happens during `parse`, `seed`, and `test`. Catalog integration configuration accepts `file_format`.

For V1 integrations, `catalog_database` may override the database name for any catalog type and has the highest priority during database-name generation.

## Resource-name and ref search flags (1.11.0)

`require_unique_project_resource_names` restores an error for duplicate node names within one project. `require_ref_searches_node_package_before_root` makes an ambiguous package-internal `ref()` search the referencing node's package before the root project.

```yaml
flags:
  require_unique_project_resource_names: true
  require_ref_searches_node_package_before_root: true
```

## Schema-name and resource-name validation (1.12.0)

A custom `generate_schema_name` macro returning null is deprecated behind `require_valid_schema_from_generate_schema_name`:

```yaml
flags:
  require_valid_schema_from_generate_schema_name: true
```

Source and Semantic Model names containing spaces warn. `REQUIRE_SOURCE_AND_SEMANTIC_MODEL_NAMES_WITHOUT_SPACES` can turn that validation into an error.

## Additional project inputs (1.12.0)

Project variables may be declared in `vars.yml`, environment variables may load automatically from `.env`, and SQL or Markdown files may use explicit Jinja suffixes such as `.sql.jinja` and `.md.jinja`.

## Catalog configuration V2 (1.12.0)

Enable `catalogs.yml` V2 with the `use_catalogs_v2` behavior flag. Catalog configuration is loaded by every command that requires a manifest.

```yaml
flags:
  use_catalogs_v2: true
```

## Data-test configuration opt-ins (1.12.0)

Data tests may use `sql_header` behind `require_sql_header_in_test_configs`. Unit tests and generic data tests may pass custom `ref()` keyword arguments behind `support_custom_ref_kwargs`.

```yaml
flags:
  require_sql_header_in_test_configs: true
  support_custom_ref_kwargs: true
```

## Macro and analysis configuration (1.12.0)

Macro properties accept a `config` mapping with `meta` and `docs`. Analyses can be enabled or disabled in `dbt_project.yml` at project or folder scope.

```yaml
macros:
  - name: cents_to_dollars
    config:
      meta: {owner: finance}
      docs: {show: true}

analyses:
  my_project:
    staging:
      +enabled: false
```

## Databricks schema-recognized keys (1.12.1)

Core 1.12.2 recognizes `query_tags`, `zorder`, `options`, `unique_tmp_table_suffix`, and `skip_optimize` as Databricks adapter config keys. These supported keys no longer generate false `CustomKeyInConfigDeprecation` warnings during JSON Schema validation.
