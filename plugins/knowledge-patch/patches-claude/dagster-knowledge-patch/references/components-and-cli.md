# Components and CLI

## Component authoring

### Default project structure

Components became production-ready in 1.11.0 and are the recommended structure
for new projects. Declare definitions in `defs.yaml` or typed Python `Component`
subclasses. Decorate Python helpers with `@template_var` to expose them to YAML.
`build_defs_for_component` builds definitions outside a `defs` folder, while
templates can compose Components with `load_component_at_path` and
`build_defs_at_path` on versions that still provide those helpers.

```yaml
deps:
  - "{{ load_component_at_path('dbt_ingest').asset_key_for_model('customers') }}"
```

### Loading API migration

The public `load_defs` API was deprecated in 1.11.0; use
`load_from_defs_folder(path)`. Sling and Airflow Component configuration moved
`asset_post_processors` to top-level `post_processors`.
`SlingReplicationCollectionComponent` accepts `connections` directly rather
than the deprecated `sling` YAML field or Python `resource` argument.

In 1.12.0, `ComponentLoadContext.build_defs_at_path` and
`load_component_at_path` were renamed to `build_defs` and `load_component`; the
old methods were temporarily retained. The 1.13-upgrade removed those
compatibility methods, so current templates must call
`context.build_defs(...)` and `context.load_component(...)`.

### State-backed Components

`StateBackedComponent` arrived in 1.12.0. It separates persisted discovery state
from YAML or Python configuration and supports local state, versioned storage,
and code-server snapshots. Airbyte, Fivetran, Power BI, Airflow, and dbt project
Components use this model. Generated GitHub Actions deployment workflows refresh
the state as part of deployment.

In 1.13.0, state-backed integrations such as Airbyte and Fivetran changed their
default storage to `LOCAL_FILESYSTEM` from `legacy_code_server_snapshots`.
Configure storage explicitly when the old persistence location is required.

### Template scopes

Component templates expose these namespaces as of 1.12.0:

- `dg`: automation conditions, partition definitions, and `FreshnessPolicy`.
- `context`: loading helpers and `project_root`.
- `datetime`: `datetime` and `timedelta`.

```jinja
{{ dg.AutomationCondition.on_missing() & dg.AutomationCondition.in_latest_time_window() }}
{{ dg.DailyPartitionsDefinition("2025-01-01") }}
{{ context.load_component("warehouse") }}
```

### Secret fields and YAML scalar behavior

Since 1.12.0, hide a configurable-resource parameter in the UI by setting its
Pydantic field metadata to
`json_schema_extra={"dagster__is_secret": True}`.

Since 1.13.0, quoted date-like YAML values such as `"2021-10-30"` remain strings
instead of being converted to datetimes.

## Core `dg` workflows

### Stable command groups

The stable `dg` CLI introduced in 1.11.0 unifies common workflows:

- `dg scaffold` creates project objects and artifacts.
- `dg dev` starts the local UI.
- `dg launch` launches work.
- `dg list` inspects definitions.
- `dg check` validates configuration and definitions.
- `dg utils` contains supporting utilities.

Use `create-dagster project` rather than `dagster project scaffold`. It creates
the modern `src/` and `defs/` layout, includes local `dg` configuration, and does
not require an active Python environment.

Additional 1.11.0 tools include `dg list component-tree`, `dg check toml`,
`dg mcp`, `dg api secret list`, and `dg api secret get`. Validation of
`requirements.env` is opt-in for `dg check yaml`. MCP dependencies live in the
`dagster-dg-cli` `ai` extra rather than the base CLI package.

### Removed and replaced commands

In 1.12.0, every `dagster project` command was removed in favor of
`create-dagster`. The removed `dg docs integrations` command was replaced with
`dg utils integrations`, and `dagster-cloud ci check` was deprecated in favor of
`dg plus deploy start`, which performs deployment validation.

In 1.13.0, `dg utils integrations` itself was removed. Update scripts so they do
not depend on either integrations command.

### Definition-querying APIs

The 1.12.0 `dg api` surface includes:

- `schedule list` and `schedule get`.
- `job list` and `job get`.
- `asset-check list` and `asset-check get-executions`.
- `asset get-partition-status`.

These commands query schedule, job, check-execution, and partition-status
metadata. In 1.13.0, `dg api run launch` can launch runs through the Dagster+ API.

## Scaffolding and deployment commands

Since 1.12.0, `dg scaffold build-artifacts` generates Docker and deployment
configuration for ECR, DockerHub, GHCR, ACR, or GCR. `dg scaffold github-actions`
generates CI for Serverless or Hybrid deployments.

`dg plus deploy configure` can adapt an existing project for Dagster+ and can
scaffold GitLab CI workflows. Use `dg plus login --region eu` for EU
authentication and `dg plus config view` to inspect the active CLI configuration.
The `[tool.dg.project]` table accepts `agent_queue` and `image` values used when
generating `dagster_cloud.yaml`.

`dg plus pull env` merges remote secrets into an existing `.env` without
overwriting locally defined entries (1.12.0).

## Development configuration

Since 1.12.0, `dg dev` and `dagster dev` accept database-pool controls including
`--db-pool-recycle` and `--db-pool-pre-ping`.

In 1.13.0, values for `DG_PROJECT_PYTHON_EXECUTABLE` in a project `.env` follow
`python-dotenv` syntax, including `export`, quoting, and trailing comments.
