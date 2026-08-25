# Runtime, Adapters, and Packages

Use this reference for Python and dependency compatibility, adapter-specific behavior, packages, embedded execution, and parser/manifest boundaries.

## Core 1.9 runtime floor (1.9.0)

The 1.9 line removes Python 3.8 support and raises the minimum `dbt-adapters` version to 1.9.0.

## Working-directory behavior (1.9.0)

`dbt deps`, `dbt clean`, and `dbt init` no longer change the process working directory. Embedded callers that depended on the side effect must manage paths explicitly.

## Databricks materialization v2 (1.10-behavior-changes)

dbt-databricks 1.10.0 introduces `use_materialization_v2`, disabled by default, for its restructured materializations. It uses project-level behavior-flag configuration; no maturity release is specified.

```yaml
flags:
  use_materialization_v2: true
```

## Snowflake quoting behavior (1.10.0)

From Core 1.10.11, project-level `quoting.snowflake_ignore_case` is a no-op. Do not rely on it to change identifier casing.

## Core 1.10 runtime and dependency compatibility (1.10.0)

Core 1.10 supports Python 3.13 and either Pydantic v1 or v2. Patch releases raise the minimum JSON Schema package to 4.19.1, move to Protobuf 6, cap `sqlparse` below 0.5.5, and raise `dbt-common` to at least 1.37.3.

From 1.10.10, the `dbt-adapters` range starts at 1.16.5. Core 1.10.21 temporarily caps it below 1.24; 1.10.22 restores the upper bound to below 2.0. Resolve dependencies against the exact Core patch release rather than assuming one range for the whole minor line.

## Core 1.11 Python floor (1.11.0)

Core 1.11 drops Python 3.9. Run it on Python 3.10 or newer.

## Adapter support for managed functions (1.11-udfs)

SQL functions work on BigQuery, Snowflake, Redshift, Postgres, and Databricks. Python works on Snowflake, BigQuery, and Databricks with Unity Catalog. JavaScript works on Snowflake and BigQuery. Adapter differences in body shape, volatility, defaults, overloads, and Python runtime config are detailed in [resources-tests-and-functions.md](resources-tests-and-functions.md).

## Private Git packages (1.12.0)

Private Git packages work in both `packages.yml` and `dependencies.yml`. dbt resolves their URLs from a configured environment variable when present; otherwise, it constructs an SSH URL.

## Core 1.12 runtime compatibility (1.12.0)

Core 1.12 supports Python 3.14 and raises minimum dependencies to Click 8.3.0, `dbt-common` 1.37.3, and `dbt-adapters` 1.24.5.

## Fusion manifests and local adapter macros (1.12.1)

After loading a Fusion-generated manifest, Core reparses adapter macros from the locally installed `dbt-<adapter>` package. Execution uses macros from the user's installed adapter version rather than the adapter copy used when Fusion compiled the manifest. Pin and inspect the local adapter when compiled and executed behavior differ.

## External parser dependency (1.12.1)

The minimum `dbt-core-experimental-parser` version for the external V2 parser rises from `2.0.0a4` to `2.0.0b1`.

## Databricks config validation (1.12.1)

Core 1.12.2 recognizes `query_tags`, `zorder`, `options`, `unique_tmp_table_suffix`, and `skip_optimize` as Databricks adapter keys, preventing false `CustomKeyInConfigDeprecation` warnings.
