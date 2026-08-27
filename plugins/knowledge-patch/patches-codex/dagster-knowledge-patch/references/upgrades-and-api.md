# Upgrades and API migration

## API lifecycle and package ownership

### Lifecycle decorators (since 1.10.0)

Dagster distinguishes `@preview`, `@beta`, and `@superseded` APIs, with
matching annotations and warnings. `@experimental` and its annotations and
warnings were removed; choose `@preview` or `@beta` instead.

### Package support changes (since 1.10.0)

`dagster-blueprints` was removed. Components under development became its
conceptual successor. `dagster-sdf` moved to the community-supported
repository.

## Freshness migration

### New and legacy policy names (since 1.11.0)

The old `FreshnessPolicy` became `LegacyFreshnessPolicy`. On the 1.11 surface,
importing `FreshnessPolicy` from top-level `dagster` errors; legacy code can
temporarily import the deprecated alias from `dagster.deprecated`.

The `freshness_policy` field on assets and specs carries the new policy type,
and `ResolvedAssetSpec` resolvers can set it.

### Stable top-level imports (1.12-upgrade)

`FreshnessPolicy` and `apply_freshness_policy` moved out of preview and are
exported by top-level `dagster`. Replace imports from
`dagster.preview.freshness`:

```python
from dagster import FreshnessPolicy, apply_freshness_policy
```

The `FreshnessDaemon` runs by default to evaluate policies. Disable that
behavior explicitly only when automatic evaluation is unwanted:

```yaml
freshness:
  enabled: false
```

### Remove legacy parameters (1.13-upgrade)

`@observable_source_asset` no longer accepts `legacy_freshness_policy` or
`auto_observe_interval_minutes`. Use `automation_condition` with schedule- or
sensor-based automation.

Legacy freshness-policy parameters were also removed from `AssetsDefinition`,
`AssetOut`, and `load_assets_from_*` helpers. dbt and Sling translators no
longer expose `get_freshness_policy` or parse legacy freshness policies from
integration configuration.

## Asset API migration

### External asset helpers (1.13-upgrade)

`external_asset_from_spec` and `external_assets_from_specs` were removed. Pass
`AssetSpec` objects directly to `Definitions`, or construct an
`AssetsDefinition` from them.

```python
from dagster import AssetSpec, Definitions

defs = Definitions(assets=[AssetSpec("my_asset")])
```

### Dependency sequences (1.13-upgrade)

The `deps` argument no longer accepts one bare `AssetKey`. Wrap a dependency
in a sequence, and use `AssetDep` when it needs configuration such as a
partition mapping.

```python
from dagster import AssetDep, asset

@asset(deps=[AssetDep("upstream")])
def downstream(): ...
```

### Asset-spec resolution (1.13-upgrade)

`Definitions.get_all_asset_specs()` was removed. Call
`Definitions.resolve_all_asset_specs()`.

### Asset-selection keyword (since 1.10.0)

Use `include_external_assets` instead of the renamed `include_sources`
keyword on `AssetSelection` APIs.

## Component migration

### Definitions-folder loading (since 1.11.0)

`load_defs` is deprecated and no longer public. Use
`load_from_defs_folder(path)`.

Sling and Airflow Components replaced `asset_post_processors` with top-level
`post_processors`. `SlingReplicationCollectionComponent` receives
`connections` directly rather than the deprecated `sling` YAML field or
Python `resource` argument.

### Loading helper names (since 1.12.0)

`ComponentLoadContext.build_defs_at_path` and `load_component_at_path` became
`build_defs` and `load_component`. The old names remained temporarily for
compatibility.

### Removed compatibility helpers (1.13-upgrade)

`ComponentLoadContext.load_component_at_path` and `build_defs_at_path` are
removed. Use `context.load_component(...)` and `context.build_defs(...)`.

## CLI migration

### Project scaffolding (since 1.11.0)

`create-dagster project` superseded `dagster project scaffold` and creates the
modern `src/` plus `defs/` layout.

### Removed and renamed commands (since 1.12.0)

- All `dagster project` commands are removed; use `create-dagster`.
- Replace removed `dg docs integrations` with `dg utils integrations`.
- Replace deprecated `dagster-cloud ci check` with
  `dg plus deploy start`, which validates the deployment.

### Further CLI changes (since 1.13.0)

`dg utils integrations` is now removed. `dg api run launch` launches runs
through the Dagster+ API.

## Integration API migration

### Airbyte removals (1.13-upgrade)

Replace removed `AirbyteState` with `AirbyteJobStatusType`.
`build_airbyte_assets()` no longer accepts `legacy_freshness_policy` or
`auto_materialize_policy`.

### Looker, Power BI, and Sigma loaders (1.13-upgrade)

The following `build_defs` methods were removed:

- `DagsterLookerResource.build_defs`;
- `PowerBIWorkspace.build_defs`;
- `SigmaOrganization.build_defs`.

Call `load_looker_asset_specs`, `load_powerbi_asset_specs`, or
`load_sigma_asset_specs`, and pass the returned specs to `Definitions`. These
loaders require translator instances, not classes.

```python
defs = Definitions(
    assets=load_looker_asset_specs(
        looker_resource,
        dagster_looker_translator=MyTranslator(),
    )
)
```

Deprecated translator key helpers were also removed. Custom translators should
implement `get_asset_spec(...)` and derive keys from its returned spec.

## Upgrade checks

1. Search source and YAML for all removed method, field, and command names.
2. Validate that Components use current loading helpers and state storage.
3. Confirm freshness policies are imported from top-level `dagster` and that
   daemon evaluation is intentional.
4. Validate asset dependency sequences, external specs, partition mappings,
   and duplicate asset keys.
5. Run database migrations and declare PostgreSQL drivers explicitly.
6. Exercise custom executors against resource initialization failures.
7. Validate integration translator instances and generated asset specs.
