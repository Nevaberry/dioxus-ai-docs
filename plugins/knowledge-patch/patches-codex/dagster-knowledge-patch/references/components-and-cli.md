# Components and CLI

## Authoring Components

### Components as the project default (since 1.11.0)

Components are the recommended starting point for new projects. Declare them
in `defs.yaml` or implement typed Python `Component` subclasses. Decorate
Python helpers with `@template_var` to expose them to YAML.

`build_defs_for_component` builds definitions outside a `defs` folder.
Templates can compose components with `load_component_at_path` and
`build_defs_at_path` on the 1.11 surface.

```yaml
deps:
  - "{{ load_component_at_path('dbt_ingest').asset_key_for_model('customers') }}"
```

### Loading and configuration migration (since 1.11.0)

`load_defs` is deprecated and no longer public; use
`load_from_defs_folder(path)`. Sling and Airflow Components replaced
`asset_post_processors` with top-level `post_processors`.
`SlingReplicationCollectionComponent` takes `connections` directly rather
than the deprecated `sling` YAML field or Python `resource` argument.

### State-backed Components (since 1.12.0)

`StateBackedComponent` separates persisted discovery state from YAML or Python
configuration. It supports local state, versioned storage, and code-server
snapshots. Airbyte, Fivetran, Power BI, Airflow, and dbt project Components use
this model. Generated GitHub Actions deployment workflows refresh their state.

### Local state default (since 1.13.0)

State-backed integrations such as Airbyte and Fivetran now default to
`LOCAL_FILESYSTEM` storage rather than `legacy_code_server_snapshots`.
Configure storage when local persistence does not match the deployment model.

## Template scope and configuration

### Current loading helpers (since 1.12.0)

`ComponentLoadContext.build_defs_at_path` and `load_component_at_path` were
renamed to `build_defs` and `load_component`, with the old forms retained only
for compatibility before their 1.13 removal.

Component templates expose:

- automation conditions, partition definitions, and `FreshnessPolicy` through
  `dg`;
- loading helpers and `project_root` through `context`;
- `datetime` and `timedelta` through `datetime`.

```jinja
{{ dg.AutomationCondition.on_missing() & dg.AutomationCondition.in_latest_time_window() }}
{{ dg.DailyPartitionsDefinition("2025-01-01") }}
{{ context.load_component("warehouse") }}
```

### Resource typing and secret fields (since 1.11.0 and 1.12.0)

Configurable resource fields accept union annotations such as `Foo | Bar`.
Hide a resource parameter in the UI by adding
`json_schema_extra={"dagster__is_secret": True}` to its Pydantic field.

### YAML scalar behavior (since 1.13.0)

Date-like YAML strings such as `"2021-10-30"` stay strings rather than being
converted to datetimes.

## Project creation and local development

### Stable `dg` workflow (since 1.11.0)

The `dg` CLI groups project work under:

- `dg scaffold` for scaffolding;
- `dg dev` for the local UI;
- `dg launch` for launches;
- `dg list` for definitions;
- `dg check` for validation;
- `dg utils` for utilities.

`create-dagster project` supersedes `dagster project scaffold`. It creates the
modern `src/` plus `defs/` layout, includes local `dg` setup, and does not
require an active Python environment.

### Additional development tools (since 1.11.0)

Available commands include `dg list component-tree`, `dg check toml`,
`dg mcp`, `dg api secret list`, and `dg api secret get`.
`requirements.env` validation is opt-in for `dg check yaml`. MCP dependencies
live in the `dagster-dg-cli` `ai` extra rather than the base CLI.

## Scaffolding and deployment commands

### Deployment artifacts (since 1.12.0)

`dg scaffold build-artifacts` generates Docker and deployment configuration
for ECR, DockerHub, GHCR, ACR, or GCR. `dg scaffold github-actions` generates
Serverless- or Hybrid-aware CI. `dg plus deploy configure` prepares an existing
project for Dagster+ and can also scaffold GitLab CI workflows.

### Removed and replacement commands (since 1.12.0)

All `dagster project` commands were removed in favor of `create-dagster`.
`dg docs integrations` became `dg utils integrations`.
`dagster-cloud ci check` is deprecated; use `dg plus deploy start`, which also
performs deployment validation.

### Definition-querying API (since 1.12.0)

The `dg api` surface includes:

- `schedule list` and `schedule get`;
- `job list` and `job get`;
- `asset-check list` and `asset-check get-executions`;
- `asset get-partition-status`.

These commands cover schedule, job, check-execution, and partition-status
metadata.

### Dagster+ authentication and project configuration (since 1.12.0)

- Authenticate in the EU region with `dg plus login --region eu`.
- Inspect active CLI configuration with `dg plus config view`.
- Set `agent_queue` and `image` under `[tool.dg.project]` for generated
  `dagster_cloud.yaml`.
- `dg plus pull env` merges secrets into an existing `.env` without replacing
  locally defined entries.

### CLI changes (since 1.13.0)

`dg utils integrations` was removed. Use `dg api run launch` to launch through
the Dagster+ API. Values for `DG_PROJECT_PYTHON_EXECUTABLE` in a project
`.env` follow `python-dotenv` rules, including `export`, quoting, and trailing
comments.
