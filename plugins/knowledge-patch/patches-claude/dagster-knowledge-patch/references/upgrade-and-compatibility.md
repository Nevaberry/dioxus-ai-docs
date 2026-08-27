# Upgrade and Compatibility

## API lifecycle labels

Dagster 1.10.0 distinguishes `@preview`, `@beta`, and `@superseded` APIs with
matching annotations and warnings. `@experimental` and its annotations and
warnings were removed; classify unstable APIs as preview or beta instead.

## Core API removals and replacements

### Assets and selections

- In 1.10.0, rename the `AssetSelection` keyword `include_sources` to
  `include_external_assets`.
- The 1.13-upgrade removed `external_asset_from_spec` and
  `external_assets_from_specs`; pass `AssetSpec` values directly to
  `Definitions` or build an `AssetsDefinition`.
- The 1.13-upgrade requires a sequence for `deps`, even for one `AssetKey`.
  Wrap dependencies in a list and use `AssetDep` for configured dependencies.
- Replace the removed `Definitions.get_all_asset_specs()` with
  `Definitions.resolve_all_asset_specs()` (1.13-upgrade).

### Freshness and observation

The freshness transition spans several releases and must be applied according to
the installed version:

- In 1.11.0, the former `FreshnessPolicy` became `LegacyFreshnessPolicy`.
  Importing `FreshnessPolicy` from top-level `dagster` errored; a deprecated
  legacy alias remained in `dagster.deprecated`.
- The 1.12-upgrade exported the current `FreshnessPolicy` and
  `apply_freshness_policy` from top-level `dagster`. Replace imports from
  `dagster.preview.freshness`.
- In 1.12.0, `build_.*_freshness_checks` was superseded by freshness policies,
  and the dbt and Sling translators removed `get_freshness_policy` and legacy
  policy parsing.
- The 1.13-upgrade removed `legacy_freshness_policy` and
  `auto_observe_interval_minutes` from `@observable_source_asset`, and removed
  legacy policy parameters from `AssetsDefinition`, `AssetOut`, and
  `load_assets_from_*`. Use `automation_condition` with schedule- or
  sensor-driven automation.

### Component loaders

In 1.11.0, `load_defs` became deprecated and non-public; use
`load_from_defs_folder(path)`. In 1.12.0,
`ComponentLoadContext.load_component_at_path` and `build_defs_at_path` were
renamed to `load_component` and `build_defs`, with aliases retained temporarily.
The 1.13-upgrade removed the aliases; use `context.load_component(...)` and
`context.build_defs(...)`.

### CLI commands

- `create-dagster project` superseded `dagster project scaffold` in 1.11.0.
- All `dagster project` commands were removed in 1.12.0.
- `dg docs integrations` was removed in favor of `dg utils integrations` in
  1.12.0; `dg utils integrations` was then removed in 1.13.0.
- `dagster-cloud ci check` was deprecated in 1.12.0; use
  `dg plus deploy start` for deployment validation and launch.

## Integration API removals

### Airbyte

The 1.13-upgrade removed `AirbyteState`; use `AirbyteJobStatusType`.
`build_airbyte_assets()` no longer accepts `legacy_freshness_policy` or
`auto_materialize_policy`.

### Looker, Power BI, and Sigma

The 1.13-upgrade removed `DagsterLookerResource.build_defs`,
`PowerBIWorkspace.build_defs`, and `SigmaOrganization.build_defs`. Use
`load_looker_asset_specs`, `load_powerbi_asset_specs`, or
`load_sigma_asset_specs`, then pass the specs to `Definitions`. Pass translator
instances, not translator classes.

Deprecated translator key helpers were removed. Custom translators should
override `get_asset_spec(...)` and derive keys from the returned specification.

### Sling and Airflow configuration

In 1.11.0, Sling and Airflow Components removed `asset_post_processors` in favor
of top-level `post_processors`. `SlingReplicationCollectionComponent` accepts
`connections` directly rather than the deprecated `sling` YAML field or Python
`resource` argument.

## Package lifecycle

`dagster-blueprints` was removed in 1.10.0; Components are its conceptual
successor. `dagster-sdf` moved to the community-supported repository.

Integration maturity in 1.11.0 included GA `FivetranWorkspace`, beta Airflow
Component and dbt Cloud integration, and a preview Apache Iceberg IO manager.
Treat each maturity label as part of its API-stability contract.

New integration packages in 1.13.0 include `dagster-clickhouse`,
`dagster-clickhouse-pandas`, and `dagster-clickhouse-polars`. Preview Components
include `SodaScanComponent` and `SnowflakeDbtProjectComponent`.

## Python and dependency support

### Python

Dagster 1.11.0 added Python 3.13 support. In 1.12.0, Python 3.9 support was
dropped, making Python 3.10 the minimum. The core package and most libraries
support Python 3.14; `dg plus deploy` supports Python 3.13 and 3.14.

`dagster-airlift` supports Python 3.12, 3.13, and 3.14 as of 1.13.0.

### Core and integration dependencies

Dagster 1.11.0 supports protobuf 6.x and removed its Click `<8.2` cap.
`dagster-deltalake` and `dagster-deltalake-polars` require
`deltalake>=1.0.0`, with no user-facing API change.

In 1.13.0, `dagstermill` requires `papermill>=2.0.0` and its default Jupyter
kernel-startup timeout increased from 60 to 120 seconds.

`dagster-postgres` stopped installing `psycopg2-binary` transitively in 1.12.0.
Projects that use it must declare the package directly. MySQL deployments must
run `dagster instance migrate` for the 1.12.0 `LongText` migrations.

## Configuration compatibility

Configurable resource fields accept union annotations such as `Foo | Bar` since
1.11.0.

Concurrency pool names were restricted to letters, digits, dashes, and
underscores in 1.10.0. The restriction was relaxed in 1.12.0 to permit any
non-whitespace character.

Quoted date-like YAML values remain strings in 1.13.0 rather than being coerced
to datetimes. Project `.env` values for `DG_PROJECT_PYTHON_EXECUTABLE` use
`python-dotenv` syntax, including `export`, quoting, and trailing comments.

## Upgrade verification

1. Pin and inspect the core, CLI, integration, Python, and chart versions.
2. Search for removed decorators, loader methods, freshness parameters, CLI
   commands, and integration `build_defs` calls.
3. Run definitions validation to catch duplicate asset keys and incompatible
   partition mappings.
4. Run database migrations and verify explicit driver dependencies.
5. Exercise daemon startup, custom executor failures, pool blocking, retries,
   backfills, and integration state persistence before production rollout.
