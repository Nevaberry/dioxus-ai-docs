# Data and analytics integrations

## Integration maturity and extension points

### New integration surfaces (since 1.11.0)

`FivetranWorkspace` is generally available. The Airflow Component and dbt
Cloud integration are beta, while the Apache Iceberg IO manager is preview.
The `dagster-snowflake-polars` package provides
`SnowflakePolarsIOManager`.

### Component extension points (since 1.11.0)

Airbyte, Fivetran, Power BI, Sling, and dlt Components expose an overridable
`get_asset_spec`. Airbyte and Fivetran also expose `execute`.
`DbtProjectComponent` exposes `get_asset_spec` and `get_asset_check_spec`.

Airbyte and Fivetran Components no longer reserve the resource keys
`io_manager`, `airbyte`, or `fivetran` that they previously claimed.

### State-backed integration Components (since 1.12.0)

Airbyte, Fivetran, Power BI, Airflow, and dbt project Components use
`StateBackedComponent`, separating discovery state from configuration. Their
default storage changes to `LOCAL_FILESYSTEM` in 1.13.0 rather than legacy
code-server snapshots.

## dbt

### Core, Fusion, and Cloud execution (since 1.11.0)

`dagster-dbt` supports dbt Core 1.10 and has preview support for dbt Fusion CLI
without code changes. When both are installed, Fusion is preferred. `dbt-core`
remains a dependency for dbt Cloud.

Set `DbtProjectComponent.cli_args` to customize execution. Control dbt Cloud
polling with `DAGSTER_DBT_CLOUD_POLL_INTERVAL` and
`DAGSTER_DBT_CLOUD_POLL_TIMEOUT`.

### Project customization (since 1.12.0)

`DbtProjectComponent.op_config_schema` customizes runtime configuration.
`DbtProject` and its Component expose `prepare_project_cli_args` for
manifest-generation arguments. `dagster-dbt` supports dbt Core 1.11 and
prefers an installed `dbt-core` for manifest parsing.

### dbt Cloud Components and partitions (since 1.12.0)

`DbtCloudComponent` loads dbt Cloud projects as assets and can add a polling
sensor for Cloud job runs. The `dbt_cloud_assets` decorator accepts
`partitions_def` for partitioned assets.

### Defaults and Component controls (since 1.13.0)

`DagsterDbtTranslatorSettings.enable_source_metadata` defaults to `True`, so
dbt source table names remap upstream asset keys by default.

`DbtCloudComponent` adds custom `translation`. The Component and workspace
accept a configurable job pool. `DbtProjectComponent.include_metadata` accepts
`"insights"` for Dagster+ Insights tracking from YAML.

The preview `SnowflakeDbtProjectComponent` orchestrates dbt natively on
Snowflake. dbt views can become virtual assets automatically with
`enable_dbt_views_as_virtual_assets`.

## Airbyte

### OSS and Enterprise workspaces (since 1.11.0)

`AirbyteWorkspaceComponent`, renamed from
`AirbyteCloudWorkspaceComponent`, and `@airbyte_assets` support Airbyte OSS and
Enterprise as well as Cloud.

### Execution controls (since 1.12.0)

`AirbyteWorkspace` supports:

- `poll_previous_running_sync`;
- `max_items_per_page`;
- `poll_interval` and `poll_timeout`;
- `cancel_on_termination`.

### Transient retry configuration (since 1.13.16)

`dagster-airbyte` honors `request_max_retries` for transient API failures. A
sync no longer fails after the first transient error when retries were
configured.

## Fivetran

### Observability and retries (since 1.12.0)

The polling sensor converts externally triggered Fivetran syncs into Dagster
materializations. `FivetranWorkspace` supports `request_backoff_factor`,
`retry_on_reschedule`, and resync operations for request failures and
quota-rescheduled syncs.

### Column metadata (since 1.13.0)

The Fivetran Component can set `fetch_column_metadata` to include column-level
metadata.

## Databricks

### Pipes and Asset Bundles (since 1.11.0)

Databricks adds `PipesDatabricksServerlessClient` and a preview
`DatabricksAssetBundleComponent`. Serverless tasks support Spark Python and
Python Wheel forms. `PipesDatabricksClient` supports `notebook_task`.

### Job discovery and cancellation (since 1.12.0)

`DatabricksWorkspaceComponent` discovers jobs as assets and cancels a job when
its Dagster run is terminated. `DatabricksAssetBundleComponent` can be
subsetted by task at the job level and uses the Databricks CLI to resolve
bundle variable references.

### Federated credentials (since 1.13.0)

`DatabricksClientResource.credentials_strategy` accepts the Databricks SDK
`CredentialsStrategy` protocol for federated or custom authentication.

## BI and semantic integrations

### Tableau controls (since 1.12.0)

`TableauComponent` can make embedded and published datasource assets
materializable with `enable_embedded_datasource_refresh` and the source-spelled
`enable_published_datsource_refresh`. Filter workbooks and projects with
`workbook_selector` and `project_selector`.

### Additional Components (since 1.12.0)

Components are available for Sigma, Looker, Tableau, Omni, Census, and
Polytomic. AWS, Azure, and GCP also provide declarative resource Components.

### Loader migration (1.13-upgrade)

`DagsterLookerResource.build_defs`, `PowerBIWorkspace.build_defs`, and
`SigmaOrganization.build_defs` were removed. Load specs through
`load_looker_asset_specs`, `load_powerbi_asset_specs`, or
`load_sigma_asset_specs`, and pass the results to `Definitions`.

These loaders require translator instances rather than translator classes.
Deprecated translator key helpers are also gone; implement
`get_asset_spec(...)` and derive keys from its returned spec.

```python
defs = Definitions(
    assets=load_looker_asset_specs(
        looker_resource,
        dagster_looker_translator=MyTranslator(),
    )
)
```

## Other ingestion Components

### dlt, Sling, and Airflow migration (since 1.11.0)

Sling and Airflow Components use top-level `post_processors` instead of
`asset_post_processors`. `SlingReplicationCollectionComponent` takes
`connections` directly rather than `sling` in YAML or `resource` in Python.

### Partitioned dlt loads (since 1.13.0)

`DltLoadCollectionComponent` accepts `partitions_def` and `backfill_policy`.

## IO managers and storage

### BigQuery write modes (since 1.12.0)

Set `BigQueryIOManager.write_mode` to `truncate`, `replace`, or `append`.

### Empty DataFrames (since 1.13.0)

BigQuery, Snowflake, and DuckDB IO managers skip writes for empty DataFrames
and log a warning rather than creating a table from degenerate inferred types.

### S3 object keys and table metadata (since 1.13.0)

`PickledObjectS3IOManager` uses an empty key prefix when none is provided.
`TableMetadataSet.storage_kind` records the backing table system, including
Snowflake, Databricks, or BigQuery.

## New packages and runtime compatibility

### ClickHouse, Soda, and Snowflake dbt (since 1.13.0)

The `dagster-clickhouse`, `dagster-clickhouse-pandas`, and
`dagster-clickhouse-polars` packages supply native resources, IO managers, and
`dg` Components. Preview integrations include `SodaScanComponent` for Soda
Core and `SnowflakeDbtProjectComponent` for Snowflake-native dbt orchestration.

### Delta Lake requirement (since 1.11.0)

`dagster-deltalake` and `dagster-deltalake-polars` require
`deltalake>=1.0.0`; their user-facing APIs are otherwise unchanged.
