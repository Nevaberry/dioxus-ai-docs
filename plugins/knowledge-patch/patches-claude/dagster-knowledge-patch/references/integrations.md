# Integrations

## Integration-wide Component behavior

### Pools and extension points

The `dagster-dbt`, `dagster-dlt`, and `dagster-sling` integrations gained pool
support in 1.10.0.

Since 1.11.0, Airbyte, Fivetran, Power BI, Sling, and dlt Components expose an
overridable `get_asset_spec`. Airbyte and Fivetran also expose `execute`, while
`DbtProjectComponent` exposes `get_asset_spec` and `get_asset_check_spec`.
Airbyte and Fivetran Components no longer reserve their former `io_manager`,
`airbyte`, or `fivetran` resource keys.

### State-backed discovery

Airbyte, Fivetran, Power BI, Airflow, and dbt project Components adopted
`StateBackedComponent` in 1.12.0. Generated GitHub Actions workflows refresh
their persisted discovery state during deployment. In 1.13.0, state-backed
integrations default to `LOCAL_FILESYSTEM` rather than
`legacy_code_server_snapshots`.

## dbt

### Engines and execution controls

As of 1.11.0, `dagster-dbt` supports dbt Core 1.10 and preview use of the dbt
Fusion CLI without code changes. `dbt-core` remains required for dbt Cloud, and
Fusion is preferred when both engines are installed.

`DbtProjectComponent.cli_args` customizes execution. The environment variables
`DAGSTER_DBT_CLOUD_POLL_INTERVAL` and `DAGSTER_DBT_CLOUD_POLL_TIMEOUT` control
dbt Cloud polling (1.11.0).

In 1.12.0, `DbtProjectComponent.op_config_schema` can define runtime config.
`DbtProject` and the Component expose `prepare_project_cli_args` for
manifest-generation arguments. `dagster-dbt` supports dbt Core 1.11 and prefers
an installed `dbt-core` for manifest parsing.

### Cloud, partitions, and translation

`DbtCloudComponent` loads dbt Cloud projects as assets and can add a polling
sensor for Cloud job runs as of 1.12.0. The `dbt_cloud_assets` decorator accepts
`partitions_def` for partitioned assets.

In 1.13.0, `DagsterDbtTranslatorSettings.enable_source_metadata` defaults to
`True`, so dbt source table names remap upstream asset keys by default.
`DbtCloudComponent` adds custom `translation`; the Component and workspace
accept a configurable job pool. `DbtProjectComponent.include_metadata` accepts
`"insights"` for Dagster+ Insights tracking in YAML.

dbt views can be represented as virtual assets with
`enable_dbt_views_as_virtual_assets` (1.13.0).

## Airbyte

`AirbyteWorkspaceComponent`, renamed from `AirbyteCloudWorkspaceComponent`, and
`@airbyte_assets` support Airbyte OSS and Enterprise as of 1.11.0.

In 1.12.0, `AirbyteWorkspace` adds `poll_previous_running_sync`,
`max_items_per_page`, `poll_interval`, `poll_timeout`, and
`cancel_on_termination` controls.

The 1.13-upgrade removed `AirbyteState`; use `AirbyteJobStatusType`.
`build_airbyte_assets()` also removed `legacy_freshness_policy` and
`auto_materialize_policy`.

As of 1.13.16, transient Airbyte API failures honor `request_max_retries` rather
than failing a sync after its first transient error.

## Fivetran

`FivetranWorkspace` became GA in 1.11.0.

In 1.12.0, the integration adds a polling sensor that represents externally
triggered syncs as materializations. `FivetranWorkspace` also supports
`request_backoff_factor`, `retry_on_reschedule`, and resync operations for
request failures and quota-rescheduled syncs.

The Fivetran Component can opt into column-level metadata through
`fetch_column_metadata` as of 1.13.0.

## Databricks

Dagster 1.11.0 added `PipesDatabricksServerlessClient`, a preview
`DatabricksAssetBundleComponent`, Spark Python and Python Wheel serverless tasks,
and `notebook_task` support in `PipesDatabricksClient`.

In 1.12.0, `DatabricksWorkspaceComponent` discovers Databricks jobs as assets and
cancels them when their Dagster run terminates. `DatabricksAssetBundleComponent`
is subsettable by task at the job level and uses the Databricks CLI to resolve
bundle variable references.

`DatabricksClientResource.credentials_strategy` accepts the Databricks SDK
`CredentialsStrategy` protocol for federated or custom authentication as of
1.13.0.

## Looker, Power BI, and Sigma

The 1.13-upgrade removed `DagsterLookerResource.build_defs`,
`PowerBIWorkspace.build_defs`, and `SigmaOrganization.build_defs`. Load specs
with `load_looker_asset_specs`, `load_powerbi_asset_specs`, or
`load_sigma_asset_specs`, then pass them to `Definitions`. Loader translator
arguments now require instances rather than classes.

```python
defs = Definitions(
    assets=load_looker_asset_specs(
        looker_resource,
        dagster_looker_translator=MyTranslator(),
    )
)
```

Deprecated translator key helpers were also removed. Override
`get_asset_spec(...)` and derive keys from its returned `AssetSpec`.

## Tableau and other BI Components

Since 1.12.0, `TableauComponent` can make embedded and published datasource
assets materializable with `enable_embedded_datasource_refresh` and
`enable_published_datsource_refresh`. Filter workbooks and projects with
`workbook_selector` and `project_selector`.

The 1.12.0 Component catalog also added Sigma, Looker, Tableau, Omni, Census, and
Polytomic, plus declarative AWS, Azure, and GCP resource Components.

## Airflow, Sling, and dlt

The Airflow Component was beta in 1.11.0. Sling and Airflow moved
`asset_post_processors` to top-level `post_processors`, and
`SlingReplicationCollectionComponent` moved from `sling`/`resource` configuration
to direct `connections`.

In 1.12.0, dbt and Sling translators removed `get_freshness_policy` and stopped
parsing legacy freshness-policy configuration.

`DltLoadCollectionComponent` accepts `partitions_def` and `backfill_policy` as of
1.13.0.

## Cloud data and IO managers

### Snowflake, BigQuery, Iceberg, and Delta Lake

The `dagster-snowflake-polars` package introduced
`SnowflakePolarsIOManager` in 1.11.0. The Apache Iceberg IO manager was preview.

Since 1.12.0, `BigQueryIOManager.write_mode` may be `truncate`, `replace`, or
`append`.

In 1.13.0, BigQuery, Snowflake, and DuckDB IO managers skip empty-DataFrame
writes and warn. They do not create a degenerate table from inferred types.

`dagster-deltalake` and `dagster-deltalake-polars` require `deltalake>=1.0.0`
as of 1.11.0, without a user-facing API change.

### ClickHouse and Snowflake-native dbt

The 1.13.0 `dagster-clickhouse`, `dagster-clickhouse-pandas`, and
`dagster-clickhouse-polars` packages provide native resources, IO managers, and
`dg` Components. Preview additions include `SodaScanComponent` for Soda Core and
`SnowflakeDbtProjectComponent` for native dbt orchestration on Snowflake.

## Azure and Pipes

Dagster Pipes added `PipesAzureMLClient` and Azure Blob Storage support in
1.12.0.

In 1.13.0, ADLS2 and Blob Storage utilities, resources, Components, and compute
logging accept `endpoint_suffix` for sovereign clouds; the compute-log Helm
setting is `endpointSuffix`.

## Microsoft Teams

Since 1.10.0, `dagster-msteams` can send Adaptive Card messages to PowerAutomate
flows.

## Dagstermill and Airlift

In 1.13.0, `dagstermill` requires `papermill>=2.0.0` and raises its default
Jupyter kernel-startup timeout from 60 to 120 seconds. `dagster-airlift` supports
Python 3.12, 3.13, and 3.14.
