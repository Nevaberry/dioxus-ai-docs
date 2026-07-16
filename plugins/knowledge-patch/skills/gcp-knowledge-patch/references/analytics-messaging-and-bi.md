# Analytics, Messaging, and BI

Use this reference for BigQuery SQL and administration, BigLake, data preparation and pipelines, transfers and sharing, Pub/Sub, Connected Sheets, and client behavior.

## Contents

- [SQL, functions, and query behavior](#sql-functions-and-query-behavior)
- [Data preparation, pipelines, notebooks, and Studio](#data-preparation-pipelines-notebooks-and-studio)
- [Lakehouse, indexing, search, and storage interfaces](#lakehouse-indexing-search-and-storage-interfaces)
- [Transfers, sharing, messaging, and BI](#transfers-sharing-messaging-and-bi)
- [Capacity, performance, and operations](#capacity-performance-and-operations)
- [Clients, connections, and interoperability](#clients-connections-and-interoperability)

## SQL, functions, and query behavior

### `MATCH_RECOGNIZE` GA (2025-11)

The BigQuery `MATCH_RECOGNIZE` clause for filtering and aggregating row-pattern matches is GA.

### Additional BigQuery transfer sources (2025-12)

Preview BigQuery Data Transfer Service sources add Klaviyo and HubSpot. In Preview, transfers can also ingest from Amazon S3, Azure Blob Storage, and Cloud Storage into BigLake Iceberg tables in BigQuery.

### BigQuery `JSON_FLATTEN` (2025-11)

Preview `JSON_FLATTEN` extracts non-array values that are direct children of a JSON value or descendants through one or more consecutively nested arrays.

```sql
SELECT JSON_FLATTEN(JSON '{"items":[{"id":1},{"id":2}]}');
```

### BigQuery `MATCH_RECOGNIZE` (2025-07)

The Preview `MATCH_RECOGNIZE` clause filters and aggregates matches across ordered rows.

```sql
SELECT *
FROM `project.dataset.events`
MATCH_RECOGNIZE (
  PARTITION BY user_id
  ORDER BY event_time
  MEASURES
    FIRST(open_event.event_time) AS opened_at,
    LAST(close_event.event_time) AS closed_at
  PATTERN (open_event close_event)
  DEFINE
    open_event AS event_type = 'open',
    close_event AS event_type = 'close'
);
```

### BigQuery `ObjectRef` functions reach GA (2026-03)

GA `ObjectRef` functions support direct or delegated access, and `OBJ.MAKE_REF` automatically fetches current Cloud Storage metadata into `ref.details`. `OBJ.GET_READ_URL` returns a `STRUCT` containing a read URL and status columns and renders image results in the console when a write URL is unnecessary.

### BigQuery advanced runtime (2025-06)

The Preview BigQuery advanced runtime can be used to improve query execution time and slot usage.

### BigQuery advanced runtime default (2026-03)

The BigQuery advanced runtime is now the default runtime for every project.

### BigQuery advanced runtime rollout (2025-09)

The advanced runtime is GA and is scheduled to become the default for every project between September 15, 2025 and early 2026.

### BigQuery client feature rollout (2025-06)

Job creation mode is GA in Python client 3.34.0, Go client 1.69.0, Node.js client 8.1.0, and Java client 2.51.0. Node.js 8.1.0 also adds per-job reservation assignment, Go 1.69.0 adds dataset view and update modes, and Java 2.51.0 adds fine-grained dataset ACL support.

### BigQuery code-asset folders (2025-11)

Preview folders can organize and control access to notebooks, saved queries, data canvases, and data-preparation files.

### BigQuery Data Transfer sources (2025-10)

Preview transfers add PayPal and Stripe. Facebook Ads, Salesforce, Salesforce Marketing Cloud, and ServiceNow transfers are GA.

### BigQuery Data Transfer updates (2025-11)

Google Ads transfers support Google Ads API v21. Preview Salesforce transfers can use incremental rather than full transfers.

### BigQuery DataFrames 2.0 (2025-04)

BigQuery DataFrames 2.0 introduces breaking API changes alongside security, performance, and feature updates. Its partial ordering mode is GA and can generate more efficient queries.

### BigQuery DataFrames in dbt (2025-05)

In Preview, the `dbt-bigquery` adapter can execute Python code defined in BigQuery DataFrames.

### BigQuery dataset insights (2026-02)

Preview dataset insights generate dataset summaries, infer cross-table relationships, build relationship graphs and cross-table queries, and suggest analytical questions.

### BigQuery dataset undelete (2026-02)

At GA, a deleted BigQuery dataset can be restored within its time-travel window to its state at deletion.

### BigQuery fluid scaling reaches GA (2026-06)

GA fluid scaling bills autoscaling reservations per second with no minimum duration.

### BigQuery geospatial result maps (2025-08)

In Preview, BigQuery Studio can display geospatial query results on an interactive map.

### BigQuery global queries (2026-02)

Preview global queries can reference data stored in multiple regions from one BigQuery query.

### BigQuery Go client 1.70.0 (2025-09)

The Go client adds `Reservation.max_slots` and `scaling_mode` for flexible reservations, load and extract job completion ratios, managed-writer protobuf conversion overrides, and load or external-table controls for custom time formats, multiple null markers, and source-column matching.

### BigQuery Go client 1.72.0 (2025-11)

The client adds `BACKGROUND_CHANGE_DATA_CAPTURE`, `BACKGROUND_COLUMN_METADATA_INDEX`, and `BACKGROUND_SEARCH_INDEX_REFRESH` reservation assignment types plus reservation IAM policy get, set, and test methods. It also adds reservation-group creation and modification support and exposes continuous queries in job configuration.

### BigQuery Go disaster-recovery fields (2025-10)

Go client 1.71.0 adds `FailoverReservationRequest.failover_mode` for choosing `HARD` or `SOFT` failover and `Reservation.replication_status.soft_failover_start_time` for observing an active soft failover.

### BigQuery Graph (2026-04)

Preview BigQuery Graph creates graphs directly over entity and relationship tables without replicating the data and queries them with Graph Query Language. BigQuery Studio can model and visualize graphs; graphs also support natural-language queries, descriptions and synonyms, and measures queried by flattening with `GRAPH_EXPAND` and aggregating with `AGG`.

### BigQuery insight scans (2026-02)

Data-documentation scans can generate only SQL queries, only table and column descriptions, or all insights. A one-time scan can start immediately without a separate run operation and can use a TTL to delete itself after completion.

### BigQuery Java and Python client additions (2025-07)

`google-cloud-bigquery` 3.35.0 adds `null_markers`, `source_column_match`, date and time format and time-zone controls for load and external configurations, plus `UpdateMode`, `dataset_view`, and `total_slot_ms`. Java client 2.53.0 adds custom time-zone and timestamp support and OpenTelemetry support for BigQuery RPCs.

### BigQuery Java client 2.57 (2025-12)

Java client 2.57.0 adds `timestamp_precision` to `Field`, introduces `DataFormatOptions` for controlling BigQuery data-type output, and relaxes client-side validation of BigQuery entity IDs.

### BigQuery Java client 2.58 release candidate (2025-12)

The `2.58.0-rc1` client lets job creation and `waitFor` accept `RetryOptions` and `BigQueryRetryConfig`; it adds `columnNameCharacterMap` to `LoadJobConfiguration`, max staleness and `MetadataCacheMode` to `ExternalTableDefinition`, a custom `ExceptionHandler` on `BigQueryOptions`, and lossless timestamps, `maxTimeTravelHours`, `java.time`, `getArray`, and `wasNull` support. It also makes `listTables` return clustering and labels, makes `executeSelect()` use supplied credentials, preserves ASCII-control-character load settings, handles empty results without null-pointer failures, and retries `IOException` through its retry exception handler.

### BigQuery Java OpenTelemetry integration (2025-06)

BigQuery Java client 2.52.0 integrates OpenTelemetry into retries and jobs.

### BigQuery Java query timeouts (2025-11)

The Java BigQuery client 2.56.0 adds `queryWithTimeout` for a client-side wait limit.

### BigQuery job controls in client libraries (2025-05)

Java client 2.50.0 and Go client 1.68.0 add the `WRITE_TRUNCATE_DATA` write disposition and per-job reservation assignment. Python client 3.33.0 also adds job-reservation support.

### BigQuery metastore (2025-01)

Preview BigQuery metastore provides shared metadata for BigQuery and Apache Spark and supports both BigQuery tables and open formats such as Apache Iceberg.

### BigQuery metastore Iceberg integrations (2025-04)

GA BigQuery metastore support can create, view, modify, and delete Apache Iceberg resources, connect the metastore to Apache Flink, and apply fine-grained access control to metastore Iceberg tables.

### BigQuery name-based set operations (2025-02)

The GA `BY NAME` and `CORRESPONDING` modifiers align set-operation inputs by column name instead of by position.

```sql
SELECT 1 AS id, 'a' AS label
UNION ALL BY NAME
SELECT 'b' AS label, 2 AS id;
```

### BigQuery Node.js client 8.0 (2025-05)

The Node.js BigQuery client 8.0.0 requires Node.js 18 or later.

### BigQuery notebook cell types (2025-10)

Preview notebooks can run BigQuery SQL directly in SQL cells and generate customizable charts from any DataFrame in visualization cells.

### BigQuery notebook gallery (2026-04)

The GA notebook gallery in the BigQuery web UI provides a central hub for discovering and using prebuilt notebook templates.

### BigQuery on-demand query limit (2025-10)

The default `QueryUsagePerDay` limit is now 200 TiB for new projects; existing-project defaults are derived from the previous 30 days of usage. Projects using reservations or custom cost controls are unaffected.

### BigQuery pipe operators (2025-07)

GA pipe queries add the `WITH` operator for common table expressions, named windows, and the `DISTINCT` operator.

```sql
FROM `project.dataset.events`
|> DISTINCT;
```

### BigQuery pipe syntax (2025-04)

GA pipe syntax provides a linear alternative to conventional BigQuery query structure.

### BigQuery pipeline controls (2025-09)

BigQuery pipelines can select their processing location automatically at GA, and can include tables and views as pipeline tasks in Preview.

### BigQuery pipeline SQLX defaults (2025-11)

At GA, a pipeline's SQLX options can set a default project and dataset that apply to every task.

### BigQuery Pipelines & Connections page (2026-03)

The Preview **Pipelines & Connections** page provides guided BigQuery-specific configuration for BigQuery Data Transfer Service, Datastream, and Pub/Sub integration workflows.

### BigQuery product renames (2025-04)

Dataplex Catalog is now named BigQuery universal catalog, combining its catalog capabilities with the runtime capabilities of BigQuery metastore. Analytics Hub is now named BigQuery sharing; its functionality and endpoints are unchanged.

### BigQuery Python client 3.28.0 (2025-01)

`google-cloud-bigquery` 3.28.0 was yanked because it is incompatible with `pandas-gbq`. The release added materialized-view `allowNonIncrementalDefinition`, table `maxStaleness`, dataset resource tags, query-result `max_stream_count`, and preservation of unknown REST fields in `SchemaField`.

### BigQuery Python client 3.30.0 (2025-03)

The client adds a rounding-mode enum, `foreign_type_info` on tables, and table resource tags. `Client.query()` now retries 404 responses.

### BigQuery Python client 3.31.0 (2025-03)

`RowIterator` exposes query text and total bytes processed, and the client adds Python 3.13 and Protobuf 6.x support. Python 3.7 and 3.8 are no longer supported runtimes.

### BigQuery Python client 3.32 and 3.33 (2025-05)

Version 3.32.0 was yanked because of a performance regression; it introduced Preview incremental results, dataset access-policy versions and conditions, `AccessEntry.condition`, `BigLakeConfiguration`, and `WRITE_TRUNCATE_DATA`. Version 3.33.0 adds `autodetect_schema` to `update_table`, dtype parameters to `to_geodataframe`, and job reservations.

### BigQuery Python UDFs reach GA (2026-05)

Python user-defined functions are GA.

### BigQuery Reference panel (2025-08)

The GA Reference panel previews schemas for tables, snapshots, views, and materialized views in query and notebook editors. In the query editor it can also insert field names or snippets and open referenced resources in a new tab.

### BigQuery remote MCP server (2025-12)

The Preview BigQuery remote MCP server lets LLM agents perform data-related tasks against BigQuery.

### BigQuery replication metrics (2026-03)

GA Cloud Monitoring metrics report dataset-replication latency and network-egress bytes for BigQuery cross-region replication and managed disaster recovery.

### BigQuery repositories and pipelines (2025-03)

Preview repositories and workspaces provide Git version control directly in BigQuery or through a third-party Git provider. In the console, workflows are renamed pipelines; GA pipelines can schedule SQL queries or notebooks and configure notebook runtimes and sharing, while data-preparation pipeline tasks are in Preview.

### BigQuery reservation groups (2025-10)

Preview reservation groups make member reservations share idle slots with one another before releasing those slots to other reservations in the admin project.

### BigQuery reservation groups reach GA (2026-05)

Reservation groups, which prioritize idle-slot sharing among member reservations, are GA.

### BigQuery resource utilization charts (2025-02)

Preview resource utilization charts add metrics views and more chart-configuration options for monitoring BigQuery resources.

### BigQuery Storage partition request limit (2025-05)

The Go BigQuery storage client documents an increase from 100 to 900 partitions that can be inserted, updated, or deleted in one request.

### BigQuery Studio destinations (2025-09)

Saved queries can be opened from Explorer in Connected Sheets at GA. GA data-canvas destination table nodes can persist query results to a new or existing table.

### BigQuery Studio session defaults (2025-01)

The Preview BigQuery Studio **Settings** page can define defaults that are applied whenever a session starts.

### BigQuery Studio visibility settings (2025-06)

Preview project- and organization-level **Configuration settings** can show or hide BigQuery Studio user-interface elements for the selected scope.

### BigQuery table parameters restored (2026-01)

Support for table parameters in table-valued functions is restored after its temporary disablement.

### BigQuery transfer sources (2025-03)

The Google Ads transfer supports GA custom reports expressed as GAQL queries, and a Preview Google Analytics 4 transfer can ingest reporting and configuration data.

### BigQuery workload-management constraints (2026-05)

Preview custom organization policies can allow or deny operations on reservations, assignments, capacity commitments, and BI reservations.

### Cloud resource connections in GoogleSQL (2026-04)

At GA, `CREATE CONNECTION`, `ALTER CONNECTION SET OPTIONS`, and `DROP CONNECTION` can manage Cloud resource connections. `GRANT` and `REVOKE` also accept the `connection` user type and the `PROJECT` resource type for connection and project access.

### Commercial BigQuery sharing listings (2025-07)

At GA, BigQuery sharing listings can be commercialized through Google Cloud Marketplace.

### Continuous-query aggregation functions (2026-06)

Preview BigQuery continuous queries can use `ARRAY_AGG` and `STRING_AGG`.

### Cross-region BigQuery load and export (2025-05)

At GA, batch loads and exports can move data between any region or multi-region in one `bq load`, `LOAD DATA`, `bq extract`, or `EXPORT DATA` operation.

### Custom paths for BigQuery remote functions (2026-06)

GA remote functions can include a custom path suffix in the endpoint URL, allowing multiple functions to share one Cloud Run service while routing to different paths.

### Data-clean-room query templates (2025-08)

Preview query templates can predefine and restrict which queries may run in a BigQuery data clean room.

### Default BigQuery connections (2025-03)

Preview default connections let a project define reusable Cloud resource connections that are selected by default.

### Direct `ObjectRef` input for BigQuery AI functions (2026-06)

GA BigQuery AI functions accept `ObjectRef` values directly, without first calling `OBJ.GET_ACCESS_URL`.

### Flexible BigQuery reservations (2025-04)

In public Preview, a query can select its reservation at runtime, IAM policies can be attached directly to reservations, and a reservation can have a maximum slot limit. Idle slots can also be shared approximately equally among reservations in one admin project.

### Global BigQuery default location (2026-03)

At GA, an organization or project can set a global default location that BigQuery uses when a request neither specifies a location nor lets BigQuery infer one.

### GoogleSQL `WITH` expressions (2025-08)

GA `WITH` expressions define temporary variables within a single expression.

```sql
SELECT WITH(
  subtotal AS 100,
  tax AS subtotal * 0.2,
  subtotal + tax
);
```

### GoogleSQL chained function calls (2025-08)

GA chained-call syntax makes nested function calls read in evaluation order; the initial value, then each call's result, becomes the first argument to the next function.

```sql
SELECT ('one two three')
  .REPLACE('one', '1')
  .REPLACE('two', '2')
  .REPLACE('three', '3');
```

### GoogleSQL default for CLI and API queries (2025-07)

Beginning August 1, 2025, CLI and API queries default to GoogleSQL. Requests that still need LegacySQL must select it explicitly or set `default_sql_dialect_option` to `'default_legacy_sql'` at project or organization scope.

### GoogleSQL multi-level aggregation (2026-07)

Preview multi-level aggregation allows one aggregate function to be passed to another aggregate function. For example, the inner `SUM` groups by category before the outer `AVG` runs:

```sql
SELECT AVG(SUM(amount) GROUP BY category) AS average_category_total
FROM sales;
```

### JavaScript user-defined aggregate functions (2025-02)

At GA, BigQuery's `CREATE AGGREGATE FUNCTION` statement can define a JavaScript user-defined aggregate function.

### KLL approximate quantiles (2025-03)

Preview KLL quantile functions efficiently compute approximate quantiles in BigQuery.

### Multi-region BigQuery sharing listings (2025-09)

In Preview, one BigQuery sharing listing can be configured for multiple regions for shared datasets and linked dataset replicas.

### Multi-region BigQuery sharing listings reach GA (2026-05)

Configuring one BigQuery sharing listing for multiple regions is GA.

### Open-source BigQuery JDBC driver (2026-01)

The Google-developed open-source JDBC driver for connecting Java applications to BigQuery is available in Preview.

### Open-source BigQuery JDBC driver reaches GA (2026-06)

The Google-developed open-source JDBC driver for connecting Java applications to BigQuery is GA.

### Optional BigQuery job creation (2025-05)

GA optional job creation mode reduces latency for eligible small queries used in dashboards and exploration by applying automatic optimization and caching.

### Parameterized queries in the BigQuery console (2026-02)

The GA BigQuery query editor can now submit parameterized queries.

### Pub/Sub JavaScript UDF metadata (2025-04)

For Pub/Sub JavaScript UDF message transforms, the `message_id` metadata field is optional rather than required.

### Pub/Sub streams through BigQuery sharing (2025-05)

At GA, BigQuery sharing can distribute Pub/Sub streaming data, with client-library support and provider usage metrics. The Go client also supports subscriber-email logging for shared streams.

### PySpark in BigQuery notebooks (2025-05)

At GA, a BigQuery notebook can create a serverless Spark session and run PySpark code.

### Python UDF execution and observability (2026-04)

Preview Python UDFs add vectorized Apache Arrow `RecordBatch` execution, Cloud Monitoring metrics, and the `container_request_concurrency` option. They also gain 10 GiB image-storage and 30-mutations-per-minute quotas per project and region, while costs appear in `INFORMATION_SCHEMA.JOBS.external_service_costs` and the Job API's `ExternalServiceCosts` field.

### Python user-defined functions (2025-04)

Preview BigQuery Python UDFs can use additional libraries and call external APIs.

### Query location system variable (2025-02)

The Preview `@@location` system variable can set the location in which a BigQuery query runs.

```sql
SET @@location = 'us';
SELECT 1;
```

### Query text heatmap (2025-11)

The Preview query text heatmap maps SQL text to execution stages that consume more slot time and exposes their query-plan details.

### Query text heatmap reaches GA (2026-03)

The GA BigQuery execution-graph heatmap maps SQL text to execution steps and highlights the steps consuming more slot time.

### Query text in execution graphs (2025-05)

In Preview, a BigQuery execution graph can show which query text corresponds to its stage steps.

### Saved-query autosave (2025-05)

In Preview, changes made to saved BigQuery queries are saved automatically.

### Saving BigQuery results to Cloud Storage (2025-08)

At GA, BigQuery can save query results directly to Cloud Storage.

### Scheduled BigQuery notebooks (2025-06)

At GA, scheduled notebooks can be created and managed through the **Schedule details** pane in BigQuery Studio.

### Selective BigQuery pipeline runs (2026-02)

GA BigQuery pipelines can run all tasks, selected tasks, or tasks selected by tag.

### Session IDs in reusable SQL objects (2026-04)

The GA `@@session_id` system variable is available inside SQL user-defined functions, table functions, and logical views.

### SQL user-defined aggregate functions (2025-03)

GA SQL user-defined aggregate functions can be created with `CREATE AGGREGATE FUNCTION`.

### Table parameters for BigQuery TVFs (2025-09)

In Preview, a BigQuery table-valued function can declare table parameters.

### Table parameters temporarily disabled (2025-10)

BigQuery temporarily disabled table parameters in table-valued functions after their September Preview release.

### Table-triggered BigQuery pipelines (2026-06)

Preview trigger-based scheduling can automatically execute a BigQuery pipeline when specified BigQuery tables are updated.

### Unsupported BigQuery organization defaults (2025-06)

The `default_sql_dialect_option` and `query_runtime` configuration settings are unsupported at the organization level.

### User credentials for BigQuery pipelines (2025-05)

In Preview, Google Account user credentials can authorize creating, scheduling, and running pipelines and scheduling notebooks and data preparations.


## Data preparation, pipelines, notebooks, and Studio

### BigQuery data preparation (2025-01)

BigQuery data preparation accepts Gemini natural-language suggestions and lets a preparation be tested before it is deployed and scheduled for production runs.

### BigQuery data preparation additions

**2025-07.**

GA data preparation can flatten a JSON column in one operation, and Access Transparency now covers data-preparation activity. In Preview, an undeployed data preparation can be run manually in development using the developer's Google Account credentials.

**2025-09.**

Preview data preparations can load files from Cloud Storage, and GA data preparations can unnest an array so each element becomes a separate row.

### BigQuery data-preparation operations GA (2025-11)

Gemini-assisted aggregation and deduplication in BigQuery data preparations are GA.

### BigQuery data-preparation source and operations (2025-08)

Data preparations are now represented as SQLX and pipe-query syntax for CI/CD review. Preview Gemini-assisted operations add aggregation and table-data deduplication.

### Code-asset folder operations (2026-04)

GA BigQuery code-asset folders add bulk move and delete operations, folder-content refresh, and full breadcrumb paths filtered by resource permissions.

### Context-aware data preparation joins (2025-02)

Preview BigQuery data preparation can provide context-aware join-operation recommendations from Gemini.

### External files in BigQuery data preparations (2026-03)

At GA, BigQuery data preparations can clean, transform, and enrich files from Cloud Storage and Google Drive.

### Organization-scoped Explorer search (2025-12)

GA BigQuery Studio Explorer searches now return results from the current organization, with a drop-down for switching organizations.

### Table Explorer moves to the Reference panel (2026-06)

Table Explorer behavior is scheduled to move into BigQuery's **Reference** panel in July 2026 or later.


## Lakehouse, indexing, search, and storage interfaces

### Apache Arrow Storage Write API input (2025-04)

In Preview, the BigQuery Storage Write API can stream data in Apache Arrow format.

### BigLake Iceberg REST catalog federation (2025-10)

The BigLake metastore Iceberg REST catalog is GA and adds BigQuery catalog federation and catalog management in the Google Cloud console.

### BigLake Iceberg table partitioning (2025-11)

BigLake tables for Apache Iceberg in BigQuery support partitioning in Preview.

### BigLake Iceberg transactions (2025-08)

In Preview, BigLake Iceberg tables in BigQuery support multi-statement transactions.

### BigLake metastore Iceberg REST catalog (2025-06)

The Preview Apache Iceberg REST catalog in BigLake metastore lets open-source query engines access Iceberg data in Cloud Storage through a shared catalog.

### BigLake product transitions (2025-06)

BigQuery metastore is renamed BigLake metastore and is GA, while the previous BigLake metastore is renamed BigLake metastore (classic). BigQuery tables for Apache Iceberg are renamed BigLake tables for Apache Iceberg in BigQuery and are also GA.

### BigQuery hybrid search (2026-06)

Preview `VECTOR_SEARCH` can combine semantic and lexical search, `AI.SEARCH` supports `HYBRID` mode on autonomously embedded tables, and vector indexes can include keyword information to accelerate the lexical portion.

### BigQuery hybrid search temporarily disabled (2026-07)

Support for combining semantic and lexical search with `VECTOR_SEARCH` is temporarily disabled.

### Column metadata indexing (2025-05)

GA column metadata indexing is available for both BigQuery tables and external tables.

### Dataform-managed BigLake Iceberg tables (2025-11)

At GA, Dataform can automate creation of BigLake tables for Apache Iceberg in BigQuery.

### External-data loading options reach GA (2026-01)

For BigQuery `CREATE EXTERNAL TABLE` and `LOAD DATA`, `time_zone`, the date and time format options, `null_markers`, and `source_column_match` are now GA.

### External-data null and column matching (2025-07)

In Preview, `CREATE EXTERNAL TABLE` and `LOAD DATA` accept `null_markers` for multiple CSV null strings and `source_column_match` to match loaded columns by name or position.

```sql
CREATE EXTERNAL TABLE `project.dataset.events` (
  id INT64,
  event_time TIMESTAMP
)
OPTIONS (
  format = 'CSV',
  uris = ['gs://bucket/events.csv'],
  skip_leading_rows = 1,
  null_markers = ['NULL', 'N/A'],
  source_column_match = 'NAME'
);
```

### Iceberg external tables in materialized views (2025-06)

At GA, BigQuery materialized views can reference Iceberg external tables without first migrating the data to BigQuery-managed storage.

### Iceberg external-table time travel (2025-09)

GA BigQuery queries can read snapshots retained in an Iceberg external table's metadata with `FOR SYSTEM_TIME AS OF`.

```sql
SELECT * FROM `project.dataset.iceberg_table`
FOR SYSTEM_TIME AS OF TIMESTAMP '2025-09-15 12:00:00+00';
```

### Iceberg merge-on-read (2025-03)

GA Iceberg external tables support merge-on-read, including queries over position deletes and equality deletes.

### Iceberg REST catalog credential vending (2025-09)

In Preview, Lakehouse runtime's Iceberg REST catalog can vend credentials so catalog users do not need direct access to the underlying Cloud Storage buckets.

### Iceberg version 3 external tables (2026-04)

Preview BigQuery Apache Iceberg external tables support Iceberg version 3, including binary deletion vectors.

### Organization-wide search-index accounting (2025-06)

The GA `INFORMATION_SCHEMA.SEARCH_INDEXES_BY_ORGANIZATION` view reports search-index consumption against an organization's regional limit, broken down by project and table.

### Partitioned TreeAH vector indexes (2025-06)

In Preview, the `PARTITION BY` clause of `CREATE VECTOR INDEX` can partition TreeAH indexes, enabling partition pruning and lower I/O.

### Raster region statistics (2025-04)

Preview `ST_REGIONSTATS` combines raster and vector data for geospatial analysis in BigQuery.

### Search-index column granularity (2025-03)

Preview search indexes can store extra column information by setting column granularity, allowing search queries to be optimized further.

### Single-vector `VECTOR_SEARCH` syntax (2026-03)

In Preview, an alternate `VECTOR_SEARCH` call syntax can improve query performance when searching for one vector.

### Stored-column usage for vector search (2025-01)

At GA, query-job information exposes `StoredColumnsUsage` for vector searches that use stored columns.

### TreeAH vector indexes (2025-05)

GA BigQuery vector indexes support the `TreeAH` index type, which uses ScaNN and is intended for batch processing from thousands to hundreds of thousands of embeddings.

### Vector-index drift and rebuilds (2025-07)

Preview `VECTOR_INDEX.STATISTICS` reports how far indexed table data has drifted since index creation, and `ALTER VECTOR INDEX REBUILD` rebuilds an index when needed.

```sql
SELECT *
FROM VECTOR_INDEX.STATISTICS(
  TABLE `project.dataset.items`, 'items_embedding_idx'
);

ALTER VECTOR INDEX items_embedding_idx
ON `project.dataset.items` REBUILD;
```


## Transfers, sharing, messaging, and BI

### Advertising transfer controls (2025-03)

Google Ad Manager transfers can repeat every four hours or more, default to eight hours, and skip match tables with `load_match_tables = FALSE`. Search Ads transfers expose PMax data in `CartDataSalesStats`, `ProductAdvertised`, `ProductAdvertisedDeviceStats`, and `ProductAdvertisedConversionActionAndDeviceStats`.

### Advertising-transfer backfill retention (2026-05)

Starting June 1, 2026, BigQuery Data Transfer Service backfills for Google Ads, Search Ads 360, and Google Analytics 4 stop populating dates more than 37 months before the current date.

### Analytics Hub access expansion (2025-03)

Analytics Hub egress controls and data-clean-room subscriptions are available with every BigQuery edition and with on-demand pricing.

### Analytics Hub Marketplace APIs for Go (2025-06)

Go client 1.69.0 adds Analytics Hub and Marketplace integration, including `allow_only_metadata_sharing`, `CommercialInfo`, `DestinationDataset`, routine shared resources, and the `delete_commercial` and `revoke_commercial` request fields.

### Connected Sheets pivot-table capacity (2025-10)

BigQuery-backed pivot tables in Connected Sheets now support 200,000 rows, up from 100,000.

### Facebook Ads `AdInsightsMMM` transfers paused (2026-07)

Support for the `AdInsightsMMM` report is temporarily disabled because of upstream schema changes. Existing Facebook Ads transfers continue to run but omit that report's data.

### Facebook Ads transfer reports (2026-06)

The BigQuery Data Transfer Service Facebook Ads connector can transfer `AdInsightsMMM`, `Ads`, `AdCreatives`, `AdSets`, `Campaigns`, `AdImages`, `AdLabels`, `Businesses`, and `CustomAudiences` reports.

### Facebook Ads transfer type change (2026-04)

Starting July 25, 2026, the Facebook Ads connector maps `AdInsightsActions.ActionValue` from `INT` to `FLOAT`.

### Google Ads transfer MFA (2026-04)

Starting May 7, 2026, new Google Ads transfer configurations that use individual-user authentication require multi-factor authentication.

### Mailchimp and Shopify transfers (2026-01)

Preview BigQuery Data Transfer Service connectors can ingest data from Mailchimp and Shopify.

### Merchant Center multi-client best sellers (2025-06)

The GA Merchant Center best sellers report supports multi-client accounts: `aggregator_id` can be used to query the tables, and `BestSellersEntityProductMapping` maps best-selling entities to products in sub-account inventory.

### Pub/Sub external import topics (2025-03)

Pub/Sub import topics can ingest streaming data from Azure Event Hubs, Amazon Managed Streaming for Apache Kafka, and Confluent Cloud.

### Pub/Sub Go subscriber shutdown controls (2025-09)

Pub/Sub Go v2.1.0 adds subscriber shutdown options.

### Pub/Sub Go v2 library (2025-05)

The Pub/Sub v2 Go library is Alpha and should not be used in production.

### Pub/Sub Go v2.0 (2025-07)

The new Go v2.0.0 library has renamed generated admin clients and a migration guide from v1. Its `StreamingPullResponse.acknowledge_confirmation` and `modify_ack_deadline_confirmation` fields are not guaranteed to be populated.

### Pub/Sub Java streaming-pull keepalive (2025-12)

Java client 1.144.0 made protocol version `v1` the default and added keepalive-based stream teardown. Version 1.144.1 lowers the Subscriber protocol version again, disabling the streaming-pull keepalive behavior.

### Pub/Sub Java subscriber shutdown settings (2025-10)

Java Pub/Sub client 1.143.0 adds `SubscriberShutdownSettings` for configuring subscriber shutdown.

### Pub/Sub Kafka ingestion protos (2025-01)

The Java Pub/Sub client 1.136.0 adds Kafka-based sources to the `IngestionDataSourceSettings` and `IngestionFailureEvent` protos.

### Pub/Sub message-transform client migration (2025-03)

Go client 1.48.0 adds message transforms to `Topic` and `Subscription`. Go 1.48.0, Java 1.138.0, and Python 2.29.0 deprecate the transform `enabled` field and replace it with `disabled`.

### Pub/Sub message-transform clients (2025-02)

Python Pub/Sub client 2.28.0 and Java client 1.137.0 add message-transform support to `Topic` and `Subscription`.

### Pub/Sub Python clients 2.32 and 2.33 (2025-11)

Version 2.32.0 adds Python 3.14, debug logging, and `StreamingPullRequest` protocol-version support. Version 2.33.0 exposes resource tags and `AwsKinesisFailureReason.ApiViolationReason` and deprecates the `credentials_file` argument.

### Pub/Sub Python mTLS (2025-12)

Python Pub/Sub client 2.34.0 supports mTLS certificates when available.

### Pub/Sub schema violation diagnostics (2025-06)

Java Pub/Sub client 1.140.0 and Python client 2.30.0 add `SchemaViolationReason` to `IngestionFailureEvent`.

### Pub/Sub single message transforms (2025-06)

Single Message Transforms are GA and can be configured on topics or subscriptions to modify message data and attributes inside Pub/Sub.

### Pub/Sub streaming protocol version (2025-10)

Go Pub/Sub v2.2.0 and Java Pub/Sub 1.142.0 add protocol-version support to `StreamingPullRequest`.

### Pub/Sub transformation-failure diagnostics (2025-07)

Python client 2.31.0, Java client 1.141.0, and Go v2.0.0 add `MessageTransformationFailureReason` to `IngestionFailureEvent`. Python 2.31.0 also surfaces fatal stream errors to the future and adjusts the set of retryable error codes.

### Snowflake transfers (2025-05)

In Preview, BigQuery Data Transfer Service can schedule automated transfers from Snowflake.

### YouTube transfer reach reports (2026-02)

BigQuery Data Transfer Service transfers from YouTube Channel and YouTube Content Owner now support reach reports.


## Capacity, performance, and operations

### Administrative job comparison (2025-10)

The Preview administrative jobs explorer adds a job-details page whose Performance tab combines the execution graph, SQL, history, performance variance, and system load; it can also compare two jobs.

### BigQuery Go reservation APIs (2025-03)

Go client 1.67.0 adds `enable_gemini_in_bigquery` to assignments, `replication_status` to reservations, the `CONTINUOUS` assignment job type, and `MetadataCacheMode` on `ExternalDataConfig`.

### History-based optimization default (2025-09)

History-based query optimizations are enabled by default; projects or organizations where they were previously disabled can explicitly re-enable them.

### Managed disaster recovery soft failover (2025-09)

BigQuery managed disaster recovery supports soft failover at GA.

### Per-second reservation telemetry (2025-09)

The GA `INFORMATION_SCHEMA.RESERVATIONS_TIMELINE.per_second_details` field reports reservation capacity, usage, and autoscale utilization per second.

### Reservation labels (2025-10)

At GA, BigQuery reservations can carry labels for organization and billing analysis.


## Clients, connections, and interoperability

### Catalog-published data quality results (2025-06)

At GA, a data quality scan can publish its latest results as metadata on the Dataplex Universal Catalog entry for the source table. Existing scans must be edited and have publishing re-enabled before they publish to the catalog.

### Colab Data Apps (2026-04)

Preview Colab Data Apps turn Colab notebook analyses into interactive applications.

### Continuous queries (2025-05)

GA continuous queries are long-lived SQL statements that continuously process incoming BigQuery data, including ML inference. They support custom job-ID prefixes for monitoring, dedicated Cloud Monitoring metrics, and slot autoscaling.

### Data product renames (2026-04)

Dataproc is now Managed Service for Apache Spark; BigLake is Google Cloud Lakehouse; BigLake metastore is Lakehouse runtime catalog; Dataplex Universal Catalog is Knowledge Catalog; and Looker Studio is Data Studio. API, client-library, CLI, and IAM names remain unchanged, but Data Studio moves from `lookerstudio.google.com` to `datastudio.google.com`, so proxy ACLs might require the new domain.

### Data-service remote MCP servers (2026-03)

Preview remote MCP servers let agents manage Pub/Sub topics, subscriptions, and snapshots and publish messages; create, manage, and run BigQuery data transfers; and use BigQuery Migration Service to translate SQL to GoogleSQL, generate DDL, and explain translations.

### Dataform job priority (2025-10)

BigQuery pipeline schedules can configure Dataform workflow queries as interactive jobs that start promptly or lower-priority batch jobs through `InvocationConfig`.

### Dataplex automatic discovery (2025-04)

GA Dataplex automatic discovery scans Cloud Storage data, extracts and catalogs metadata, and creates BigLake, external, or object tables.

### Materialized-view smart-tuning scope (2025-04)

GA smart-tuning can optimize a materialized view when it is in the same project as one of its base tables or in the project that runs the query.

### Project-wide metadata scan administration (2025-07)

The GA **Metadata curation** page can manage data profile and data quality scans across a BigQuery project.

### Publishing data insights to the catalog (2025-11)

In Preview, query recommendations and generated table and column descriptions can be published as data insights to Dataplex Universal Catalog.

### Shared-dataset usage fields (2025-10)

The GA `INFORMATION_SCHEMA.SHARED_DATASET_USAGE` view adds `shared_resource_id`, `shared_resource_type`, and `referenced_tables`; the last field identifies each base table and its processed bytes for external-table and routine usage.

### Source date and time parsing (2025-06)

In Preview, BigQuery `CREATE EXTERNAL TABLE` and `LOAD DATA` accept `time_zone`, `date_format`, `datetime_format`, `time_format`, and `timestamp_format` options for parsing source files.

### Stateful continuous queries (2026-04)

Preview continuous queries can retain information across rows or time intervals and use stateful `JOIN` operations and windowed aggregations.

### TransUnion entity resolution (2025-10)

BigQuery entity resolution supports TransUnion at GA.
