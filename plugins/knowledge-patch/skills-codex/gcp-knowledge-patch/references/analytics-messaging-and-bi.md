# Analytics, Messaging, and BI

Use this reference for analytics, messaging, and bi compatibility details and current behavior.

## GoogleSQL, functions, and query execution

### `MATCH_RECOGNIZE` GA (2025-11)

The BigQuery `MATCH_RECOGNIZE` clause for filtering and aggregating row-pattern matches is GA.


### BigQuery `AI.KEY_DRIVERS` (2026-04)

The Preview `AI.KEY_DRIVERS` function identifies data segments that cause statistically significant changes to a summable metric.


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


### BigQuery conversational analytics additions (2026-03)

Preview conversational analytics can use `ObjectRef` data such as Cloud Storage images and PDFs, call `AI.FORECAST`, `AI.DETECT_ANOMALIES`, and `AI.GENERATE`, start chats from query results, and produce partition-aware SQL. Agent-created jobs carry a `ca-bq-job=true` label for cost, audit, and performance analysis, and the console offers clickable follow-up questions.


### BigQuery conversational analytics Preview (2026-01)

Conversational analytics advances from early access to Preview and can use supported BigQuery ML functions in verified queries and chat, in addition to chatting with data or custom agents and exposing agents outside BigQuery.


### BigQuery conversational analytics reaches GA (2026-06)

GA conversational analytics adds agent model-stage selection, per-conversation thinking mode, clarifying questions, response citations, parameters in verified queries, support for `AI.KEY_DRIVERS`, `AI.IF`, `AI.SCORE`, `AI.CLASSIFY`, `AI.SIMILARITY`, and `AI.SEARCH`, and US/EU MREP locations governing resource storage and ML processing. Creating a conversation directly with a dataset remains Preview.


### BigQuery daily token quotas temporarily unavailable (2026-06)

Daily token quotas for controlling generative AI function costs were announced at GA on June 8, but support for configuring them was temporarily disabled on June 15.


### BigQuery Data Transfer billing label migration (2026-05)

On August 11, 2026, the billing label changes from `goog-bq-feature-type: DATA_TRANSFER_SERVICE` to `goog-bq-feature-type: data_transfer_service` and expands to orchestration, load, and merge costs. Billing exports, dashboards, and reporting queries should accept both labels during the transition.


### BigQuery data-preparation source and operations (2025-08)

Data preparations are now represented as SQLX and pipe-query syntax for CI/CD review. Preview Gemini-assisted operations add aggregation and table-data deduplication.


### BigQuery database transfers (2025-12)

BigQuery Data Transfer Service sources for Oracle, MySQL, and PostgreSQL are GA, while Microsoft SQL Server is in Preview.


### BigQuery DataFrames 2.0 (2025-04)

BigQuery DataFrames 2.0 introduces breaking API changes alongside security, performance, and feature updates. Its partial ordering mode is GA and can generate more efficient queries.


### BigQuery dataset insights (2026-02)

Preview dataset insights generate dataset summaries, infer cross-table relationships, build relationship graphs and cross-table queries, and suggest analytical questions.


### BigQuery generative AI function surface (2025-11)

GA `AI.GENERATE` handles free-text, entity-extraction, and structured-output tasks over text, images, audio, video, and documents; Preview `AI.EMBED` and `AI.SIMILARITY` create multimodal embeddings and semantic-similarity scores, and the scalar AI functions support end-user-credential authentication. The GA table-valued functions are `AI.GENERATE_TABLE`, `AI.GENERATE_TEXT`, and `AI.GENERATE_EMBEDDING`; the latter two are preferred replacements for their `ML.*` counterparts and use simplified output column names.


### BigQuery geospatial result maps (2025-08)

In Preview, BigQuery Studio can display geospatial query results on an interactive map.


### BigQuery global queries (2026-02)

Preview global queries can reference data stored in multiple regions from one BigQuery query.


### BigQuery Go client 1.70.0 (2025-09)

The Go client adds `Reservation.max_slots` and `scaling_mode` for flexible reservations, load and extract job completion ratios, managed-writer protobuf conversion overrides, and load or external-table controls for custom time formats, multiple null markers, and source-column matching.


### BigQuery Go client 1.72.0 (2025-11)

The client adds `BACKGROUND_CHANGE_DATA_CAPTURE`, `BACKGROUND_COLUMN_METADATA_INDEX`, and `BACKGROUND_SEARCH_INDEX_REFRESH` reservation assignment types plus reservation IAM policy get, set, and test methods. It also adds reservation-group creation and modification support and exposes continuous queries in job configuration.


### BigQuery Go reservation APIs (2025-03)

Go client 1.67.0 adds `enable_gemini_in_bigquery` to assignments, `replication_status` to reservations, the `CONTINUOUS` assignment job type, and `MetadataCacheMode` on `ExternalDataConfig`.


### BigQuery Graph (2026-04)

Preview BigQuery Graph creates graphs directly over entity and relationship tables without replicating the data and queries them with Graph Query Language. BigQuery Studio can model and visualize graphs; graphs also support natural-language queries, descriptions and synonyms, and measures queried by flattening with `GRAPH_EXPAND` and aggregating with `AGG`.


### BigQuery IAM tags in SQL (2025-06)

At GA, SQL can manage IAM tags on BigQuery datasets and tables.


### BigQuery insight scans (2026-02)

Data-documentation scans can generate only SQL queries, only table and column descriptions, or all insights. A one-time scan can start immediately without a separate run operation and can use a TTL to delete itself after completion.


### BigQuery Java client 2.58 release candidate (2025-12)

The `2.58.0-rc1` client lets job creation and `waitFor` accept `RetryOptions` and `BigQueryRetryConfig`; it adds `columnNameCharacterMap` to `LoadJobConfiguration`, max staleness and `MetadataCacheMode` to `ExternalTableDefinition`, a custom `ExceptionHandler` on `BigQueryOptions`, and lossless timestamps, `maxTimeTravelHours`, `java.time`, `getArray`, and `wasNull` support. It also makes `listTables` return clustering and labels, makes `executeSelect()` use supplied credentials, preserves ASCII-control-character load settings, handles empty results without null-pointer failures, and retries `IOException` through its retry exception handler.


### BigQuery Java query timeouts (2025-11)

The Java BigQuery client 2.56.0 adds `queryWithTimeout` for a client-side wait limit.


### BigQuery job controls in client libraries (2025-05)

Java client 2.50.0 and Go client 1.68.0 add the `WRITE_TRUNCATE_DATA` write disposition and per-job reservation assignment. Python client 3.33.0 also adds job-reservation support.


### BigQuery managed AI function updates (2026-02)

In Preview, `AI.CLASSIFY` can classify an input into multiple categories. At GA, custom output schemas for `AI.GENERATE` and `AI.GENERATE_TABLE` can attach descriptions to their fields.


### BigQuery notebook cell types (2025-10)

Preview notebooks can run BigQuery SQL directly in SQL cells and generate customizable charts from any DataFrame in visualization cells.


### BigQuery on-demand query limit (2025-10)

The default `QueryUsagePerDay` limit is now 200 TiB for new projects; existing-project defaults are derived from the previous 30 days of usage. Projects using reservations or custom cost controls are unaffected.


### BigQuery performance assistance (2026-06)

Preview Gemini assistance can monitor performance, analyze capacity and cost, recommend SQL query optimizations for BigQuery editions, and troubleshoot performance from Jobs explorer, Job details, Job history, and Capacity management.


### BigQuery pipe operators (2025-07)

GA pipe queries add the `WITH` operator for common table expressions, named windows, and the `DISTINCT` operator.

```sql
FROM `project.dataset.events`
|> DISTINCT;
```


### BigQuery pipe syntax (2025-04)

GA pipe syntax provides a linear alternative to conventional BigQuery query structure.


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


### BigQuery Reference panel (2025-08)

The GA Reference panel previews schemas for tables, snapshots, views, and materialized views in query and notebook editors. In the query editor it can also insert field names or snippets and open referenced resources in a new tab.


### BigQuery repositories and pipelines (2025-03)

Preview repositories and workspaces provide Git version control directly in BigQuery or through a third-party Git provider. In the console, workflows are renamed pipelines; GA pipelines can schedule SQL queries or notebooks and configure notebook runtimes and sharing, while data-preparation pipeline tasks are in Preview.


### BigQuery Studio destinations (2025-09)

Saved queries can be opened from Explorer in Connected Sheets at GA. GA data-canvas destination table nodes can persist query results to a new or existing table.


### BigQuery Studio model creation and comments (2025-07)

In Preview, the console can create BigQuery ML models. Users can also add, reply to, and link to comments on notebooks, data canvases, data preparation files, and saved queries.


### BigQuery Studio session defaults (2025-01)

The Preview BigQuery Studio **Settings** page can define defaults that are applied whenever a session starts.


### BigQuery token accounting (2026-05)

Preview `AI.COUNT_TOKENS` estimates token counts for text input. For supported generative AI functions, query token usage can also expose input, output, thought, and cache tokens per modality.


### BigQuery transfer sources (2025-03)

The Google Ads transfer supports GA custom reports expressed as GAQL queries, and a Preview Google Analytics 4 transfer can ingest reporting and configuration data.


### Cloud resource connections in GoogleSQL (2026-04)

At GA, `CREATE CONNECTION`, `ALTER CONNECTION SET OPTIONS`, and `DROP CONNECTION` can manage Cloud resource connections. `GRANT` and `REVOKE` also accept the `connection` user type and the `PROJECT` resource type for connection and project access.


### Continuous queries (2025-05)

GA continuous queries are long-lived SQL statements that continuously process incoming BigQuery data, including ML inference. They support custom job-ID prefixes for monitoring, dedicated Cloud Monitoring metrics, and slot autoscaling.


### Continuous-query aggregation functions (2026-06)

Preview BigQuery continuous queries can use `ARRAY_AGG` and `STRING_AGG`.


### Data Agent Kit extension (2026-07)

The Preview Data Agent Kit extension lets agent coding environments browse BigQuery datasets, manage pipelines, run queries, and perform other BigQuery tasks directly in the development environment.


### Data-clean-room query templates (2025-08)

Preview query templates can predefine and restrict which queries may run in a BigQuery data clean room.


### Dataform job priority (2025-10)

BigQuery pipeline schedules can configure Dataform workflow queries as interactive jobs that start promptly or lower-priority batch jobs through `InvocationConfig`.


### Flexible BigQuery reservations (2025-04)

In public Preview, a query can select its reservation at runtime, IAM policies can be attached directly to reservations, and a reservation can have a maximum slot limit. Idle slots can also be shared approximately equally among reservations in one admin project.


### Gemini Cloud Assist for BigQuery operations (2026-01)

In Preview, Gemini Cloud Assist can analyze job history, including slow or resource-intensive queries, and discover resources across projects from questions about schemas or table contents.


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


### Identity-based BigQuery reservation routing (2026-06)

An optional `principal` property on a reservation assignment can route queries by the executing user, service account, or third-party identity.


### Incremental database transfers (2026-04)

In Preview, BigQuery Data Transfer Service can run incremental transfers from MySQL, Oracle, PostgreSQL, ServiceNow, and Microsoft SQL Server.


### JavaScript user-defined aggregate functions (2025-02)

At GA, BigQuery's `CREATE AGGREGATE FUNCTION` statement can define a JavaScript user-defined aggregate function.


### Model selection for BigQuery managed AI functions (2026-01)

`AI.IF`, `AI.SCORE`, and `AI.CLASSIFY` accept an optional endpoint argument for selecting the model used by the function.


### Optional BigQuery job creation (2025-05)

GA optional job creation mode reduces latency for eligible small queries used in dashboards and exploration by applying automatic optimization and caching.


### Parameterized queries in the BigQuery console (2026-02)

The GA BigQuery query editor can now submit parameterized queries.


### PostgreSQL and SQL Server metadata transfers (2026-07)

Preview BigQuery Data Transfer Service support can transfer PostgreSQL and Microsoft SQL Server metadata into Knowledge Catalog, expanding the existing database-metadata transfer sources.


### Pub/Sub JavaScript UDF metadata (2025-04)

For Pub/Sub JavaScript UDF message transforms, the `message_id` metadata field is optional rather than required.


### Publishing data insights to the catalog (2025-11)

In Preview, query recommendations and generated table and column descriptions can be published as data insights to Dataplex Universal Catalog.


### PySpark in BigQuery notebooks (2025-05)

At GA, a BigQuery notebook can create a serverless Spark session and run PySpark code.


### Query location system variable (2025-02)

The Preview `@@location` system variable can set the location in which a BigQuery query runs.

```sql
SET @@location = 'us';
SELECT 1;
```


### Query text heatmap reaches GA (2026-03)

The GA BigQuery execution-graph heatmap maps SQL text to execution steps and highlights the steps consuming more slot time.


### Query text in execution graphs (2025-05)

In Preview, a BigQuery execution graph can show which query text corresponds to its stage steps.


### Saved-query autosave (2025-05)

In Preview, changes made to saved BigQuery queries are saved automatically.


### Saving BigQuery results to Cloud Storage (2025-08)

At GA, BigQuery can save query results directly to Cloud Storage.


### Shared and role-authorized stored procedures (2025-11)

In Preview, BigQuery sharing listings can include SQL stored procedures, and stored procedures can use role-based authorization.


### Table parameters for BigQuery TVFs (2025-09)

In Preview, a BigQuery table-valued function can declare table parameters.


### TimesFM 2.5 anomaly detection (2025-11)

BigQuery ML adds TimesFM 2.5 support to `AI.FORECAST`, `AI.EVALUATE`, and `AI.DETECT_ANOMALIES`. The new Preview `AI.DETECT_ANOMALIES` function uses historical time-series data as a baseline for anomaly detection.


## BigQuery ML, AI, search, and multimodal analysis

### Automatic BigQuery ML quota synchronization (2025-07)

BigQuery ML automatically detects Vertex AI model-quota increases and adjusts quotas for BigQuery ML functions that use those models, removing the previous email-based increase process.


### Autonomous embedding generation and `AI.SEARCH` (2025-12)

Preview BigQuery tables created with `CREATE TABLE` can maintain an embedding column from a source column, regenerating affected embeddings when source data is added or changed. `AI.SEARCH` performs semantic search over tables configured for autonomous embedding generation.


### Autonomous embedding generation reaches GA (2026-06)

GA autonomous embedding generation can be enabled on new or existing tables with `CREATE TABLE` or `ALTER TABLE`; BigQuery maintains the embedding column as source-column data is added or changed.


### BigQuery `AI.AGG` restored (2026-05)

Preview `AI.AGG` is available again for natural-language semantic aggregation of unstructured input.


### BigQuery `AI.KEY_DRIVERS` restored (2026-06)

Preview support for `AI.KEY_DRIVERS`, temporarily disabled in May, is restored.


### BigQuery `AI.KEY_DRIVERS` suspension (2026-05)

Preview support for `AI.KEY_DRIVERS` was temporarily disabled on May 14, 2026.


### BigQuery embedding and similarity functions reach GA (2026-03)

BigQuery remote models can use `gemini-embedding-001` or an open embedding model deployed from Vertex Model Garden or Hugging Face, then generate embeddings with `AI.GENERATE_EMBEDDING`; `AI.EMBED` can instead use the Gemini endpoint directly. `AI.EMBED` and `AI.SIMILARITY` are GA for text and image embeddings and for text-to-text, image-to-image, or cross-modal similarity.


### BigQuery hybrid search (2026-06)

Preview `VECTOR_SEARCH` can combine semantic and lexical search, `AI.SEARCH` supports `HYBRID` mode on autonomously embedded tables, and vector indexes can include keyword information to accelerate the lexical portion.


### BigQuery managed AI functions (2025-10)

Preview `AI.IF`, `AI.SCORE`, and `AI.CLASSIFY` use natural-language criteria to filter or join text and multimodal data, rank it, or classify text into user-defined categories.


### BigQuery ML bucket output formats (2025-02)

`ML.BUCKETIZE` and `ML.QUANTILE_BUCKETIZE` accept an `output_format` argument that can return `bin_<bucket_index>`, interval notation, or a JSON-formatted string.


### BigQuery ML contribution analysis (2025-04)

GA contribution analysis models can be created with `CREATE MODEL` and queried with `ML.GET_INSIGHTS` to explain changes in multidimensional key metrics. They support summable, summable-ratio, and summable-by-category metrics, with `top_k_insights_by_apriori_support` and `pruning_method` model options.


### BigQuery ML embedding remote models (2025-09)

Preview BigQuery ML remote models can use `gemini-embedding-001` or an open embedding model such as E5 deployed from Model Garden or Hugging Face to Vertex AI, then generate embeddings with `ML.GENERATE_EMBEDDING`.


### BigQuery ML Gemini 2.5 tuning (2025-09)

BigQuery ML remote models based on `gemini-2.5-pro` or `gemini-2.5-flash-lite` can be supervised-tuned.


### BigQuery ML Gemini tuning (2025-05)

BigQuery ML remote models based on `gemini-2.0-flash-001` or `gemini-2.0-flash-lite-001` can be supervised-tuned.


### BigQuery ML monitoring visualizations (2025-03)

Preview charts can visualize output from `ML.VALIDATE_DATA_SKEW` and `ML.VALIDATE_DATA_DRIFT` model-monitoring functions.


### BigQuery ML remote-model evaluation (2025-01)

GA remote models can target open text-generation models from Vertex Model Garden or Hugging Face that are deployed to Vertex AI, then use `ML.GENERATE_TEXT` and `ML.EVALUATE`. In Preview, `ML.EVALUATE` can also evaluate Anthropic Claude models, with their BigQuery ML quotas aligned to Vertex AI quotas.


### BigQuery multimodal workflows (2025-05)

Preview multimodal support uses `ObjectRef` values in tables and `ObjectRefRuntime` values in analysis and transformation workflows. BigQuery ML and BigQuery DataFrames can analyze multimodal data or generate embeddings, multimodal DataFrames can transform images and chunk PDFs, and Python UDFs can perform those image and PDF transformations.


### Claude remote models in BigQuery ML (2025-03)

GA BigQuery ML remote models can target Anthropic Claude on Vertex AI, use `ML.GENERATE_TEXT` for table-backed generation, and use `ML.EVALUATE` for evaluation.


### Data Science Agent prompt inputs (2025-09)

Preview prompts can reference BigQuery ML and DataFrames, use `@` to search project tables, use `+` to find files to upload, and use Apache Spark or PySpark keywords.


### Direct `ObjectRef` input for BigQuery AI functions (2026-06)

GA BigQuery AI functions accept `ObjectRef` values directly, without first calling `OBJ.GET_ACCESS_URL`.


### Gemini 3 in BigQuery AI functions (2025-11)

BigQuery generative AI functions can use Gemini 3.0, but must specify the full global endpoint:

```text
https://aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/global/publishers/google/models/gemini-3-pro-preview
```


### Multi-series ARIMA_PLUS_XREG forecasting (2025-01)

The Preview `TIME_SERIES_ID_COL` option lets one BigQuery ML `ARIMA_PLUS_XREG` multivariate time-series model forecast multiple series.

```sql
OPTIONS(MODEL_TYPE = 'ARIMA_PLUS_XREG', TIME_SERIES_ID_COL = 'series_id')
```


### Multimodal Gemini embeddings in BigQuery (2026-04)

Preview `gemini-embedding-2-preview` lets `AI.EMBED`, `AI.SIMILARITY`, and `AI.GENERATE_EMBEDDING` create one embedding from combined text, image, audio, video, and PDF inputs.


### Provisioned Throughput from BigQuery ML (2025-06)

At GA, `ML.GENERATE_TEXT` and `AI.GENERATE` can use Vertex AI Provisioned Throughput with supported Gemini models.


### Raster region statistics (2025-04)

Preview `ST_REGIONSTATS` combines raster and vector data for geospatial analysis in BigQuery.


### Slot-based EmbeddingGemma (2026-04)

Preview `AI.EMBED` and `AI.SIMILARITY` can use the built-in `embeddinggemma-300m` text model, which generates embeddings at scale with BigQuery slots.


### TimesFM forecasting (2025-04)

Preview `AI.FORECAST` uses BigQuery ML's built-in TimesFM model for univariate forecasting without creating or training a model of your own.


### TimesFM functions in Connected Sheets (2026-07)

Connected Sheets can directly use pre-trained TimesFM models through `AI.FORECAST` and `AI.DETECT_ANOMALIES`; this integration is GA.


### TreeAH vector indexes (2025-05)

GA BigQuery vector indexes support the `TreeAH` index type, which uses ScaNN and is intended for batch processing from thousands to hundreds of thousands of embeddings.


## Data preparation, notebooks, pipelines, and Studio

### BigQuery data canvas assistant (2025-04)

The Preview Gemini-powered data canvas assistant can construct and modify a data canvas from prompts to answer analytics questions.


### BigQuery Data Engineering Agent (2025-10)

The Preview Data Engineering Agent uses Gemini to build and modify pipelines that ingest data into BigQuery.


### BigQuery data preparation (2025-01)

BigQuery data preparation accepts Gemini natural-language suggestions and lets a preparation be tested before it is deployed and scheduled for production runs.


### BigQuery data preparation additions (2025-07, 2025-09)

GA data preparation can flatten a JSON column in one operation, and Access Transparency now covers data-preparation activity. In Preview, an undeployed data preparation can be run manually in development using the developer's Google Account credentials.

Preview data preparations can load files from Cloud Storage, and GA data preparations can unnest an array so each element becomes a separate row.


### BigQuery data preparation lifecycle and IAM (2025-04)

BigQuery data preparation is GA, including visual pipelines and Dataform scheduling. Its required permissions can be granted through `roles/bigquery.studioUser` and `roles/cloudaicompanion.user`, plus access to the prepared data; `roles/bigquery.dataEditor` and `roles/serviceusage.serviceUsageConsumer` are no longer required.


### BigQuery Data Science Agent (2025-08)

The Preview Data Science Agent runs inside Colab Enterprise notebooks to automate exploratory analysis, machine-learning tasks, and insight generation. Its table selector can scope an analysis to one or more BigQuery tables.


### BigQuery Data Science Agent reaches GA (2026-05)

The Data Science Agent for Colab Enterprise and BigQuery is GA.


### BigQuery data-preparation operations GA (2025-11)

Gemini-assisted aggregation and deduplication in BigQuery data preparations are GA.


### BigQuery Notebook code generation (2025-04)

Gemini-generated Python in BigQuery Notebooks can use relevant table names from the project. Including `BigFrames` in the prompt generates code that uses BigQuery DataFrames, in Preview.


### BigQuery notebook gallery (2026-04)

The GA notebook gallery in the BigQuery web UI provides a central hub for discovering and using prebuilt notebook templates.


### BigQuery pipeline controls (2025-09)

BigQuery pipelines can select their processing location automatically at GA, and can include tables and views as pipeline tasks in Preview.


### BigQuery pipeline SQLX defaults (2025-11)

At GA, a pipeline's SQLX options can set a default project and dataset that apply to every task.


### BigQuery Studio visibility settings (2025-06)

Preview project- and organization-level **Configuration settings** can show or hide BigQuery Studio user-interface elements for the selected scope.


### Code-asset folder operations (2026-04)

GA BigQuery code-asset folders add bulk move and delete operations, folder-content refresh, and full breadcrumb paths filtered by resource permissions.


### Extended user-credential access for BigQuery workflows (2026-06)

In Preview, a data preparation running or scheduled with Google Account credentials can receive Google Drive access, while a pipeline can receive Google Drive, Bigtable, and Knowledge Catalog access.


### Gemini assistance in BigQuery notebooks (2025-06)

In Preview, Colab Enterprise notebooks in BigQuery can use Gemini to explain code and to fix and explain Python errors.


### Gemini in BigQuery IAM roles (2025-05)

The BigQuery Studio User and BigQuery Studio Admin roles now include permissions to use Gemini in BigQuery features.


### Organization-scoped Explorer search (2025-12)

GA BigQuery Studio Explorer searches now return results from the current organization, with a drop-down for switching organizations.


### Scheduled BigQuery notebooks (2025-06)

At GA, scheduled notebooks can be created and managed through the **Schedule details** pane in BigQuery Studio.


### Selective BigQuery pipeline runs (2026-02)

GA BigQuery pipelines can run all tasks, selected tasks, or tasks selected by tag.


### Table Explorer moves to the Reference panel (2026-06)

Table Explorer behavior is scheduled to move into BigQuery's **Reference** panel in July 2026 or later.


### Table-triggered BigQuery pipelines (2026-06)

Preview trigger-based scheduling can automatically execute a BigQuery pipeline when specified BigQuery tables are updated.


## Transfers, sharing, and Connected Sheets

### Additional BigQuery transfer sources (2025-12)

Preview BigQuery Data Transfer Service sources add Klaviyo and HubSpot. In Preview, transfers can also ingest from Amazon S3, Azure Blob Storage, and Cloud Storage into BigLake Iceberg tables in BigQuery.


### Advertising-transfer backfill retention (2026-05)

Starting June 1, 2026, BigQuery Data Transfer Service backfills for Google Ads, Search Ads 360, and Google Analytics 4 stop populating dates more than 37 months before the current date.


### Analytics Hub access expansion (2025-03)

Analytics Hub egress controls and data-clean-room subscriptions are available with every BigQuery edition and with on-demand pricing.


### Analytics Hub Marketplace APIs for Go (2025-06)

Go client 1.69.0 adds Analytics Hub and Marketplace integration, including `allow_only_metadata_sharing`, `CommercialInfo`, `DestinationDataset`, routine shared resources, and the `delete_commercial` and `revoke_commercial` request fields.


### BigQuery Data Transfer defaults and IAM (2025-10)

`bigquerydatatransfer.googleapis.com` is enabled by default for new projects. Starting March 17, 2026, creating or updating a transfer configuration requires `bigquery.datasets.getIamPolicy` and `bigquery.datasets.setIamPolicy` on its target dataset.


### BigQuery Data Transfer sources (2025-10)

Preview transfers add PayPal and Stripe. Facebook Ads, Salesforce, Salesforce Marketing Cloud, and ServiceNow transfers are GA.


### BigQuery Data Transfer updates (2025-11)

Google Ads transfers support Google Ads API v21. Preview Salesforce transfers can use incremental rather than full transfers.


### BigQuery Pipelines & Connections page (2026-03)

The Preview **Pipelines & Connections** page provides guided BigQuery-specific configuration for BigQuery Data Transfer Service, Datastream, and Pub/Sub integration workflows.


### BigQuery policy controls reach GA (2026-06)

Custom Organization Policy constraints on supported BigQuery sharing data-exchange and listing fields, and IAM deny policies for BigQuery resources, are GA.


### BigQuery reservation groups reach GA (2026-05)

Reservation groups, which prioritize idle-slot sharing among member reservations, are GA.


### Commercial BigQuery sharing listings (2025-07)

At GA, BigQuery sharing listings can be commercialized through Google Cloud Marketplace.


### Connected Sheets pivot-table capacity (2025-10)

BigQuery-backed pivot tables in Connected Sheets now support 200,000 rows, up from 100,000.


### Custom constraints for BigQuery sharing (2025-10)

Preview custom Organization Policy constraints can restrict supported fields on BigQuery sharing data exchanges and listings.


### Database metadata transfers to Knowledge Catalog (2026-06)

In Preview, the BigQuery Data Transfer Service can transfer Oracle and MySQL metadata into Knowledge Catalog.


### Facebook Ads transfer reports (2026-06)

The BigQuery Data Transfer Service Facebook Ads connector can transfer `AdInsightsMMM`, `Ads`, `AdCreatives`, `AdSets`, `Campaigns`, `AdImages`, `AdLabels`, `Businesses`, and `CustomAudiences` reports.


### Hive transfer resource status (2026-03)

Preview resource-level status reporting for Hive managed-table transfers shows per-table progress and granular errors in BigQuery Data Transfer Service.


### Mailchimp and Shopify transfers (2026-01)

Preview BigQuery Data Transfer Service connectors can ingest data from Mailchimp and Shopify.


### Multi-region BigQuery sharing listings (2025-09)

In Preview, one BigQuery sharing listing can be configured for multiple regions for shared datasets and linked dataset replicas.


### Multi-region BigQuery sharing listings reach GA (2026-05)

Configuring one BigQuery sharing listing for multiple regions is GA.


### MySQL and PostgreSQL transfers (2025-01)

The BigQuery Data Transfer Service can ingest from MySQL and PostgreSQL sources in Preview.


### Pub/Sub streams through BigQuery sharing (2025-05)

At GA, BigQuery sharing can distribute Pub/Sub streaming data, with client-library support and provider usage metrics. The Go client also supports subscriber-email logging for shared streams.


### Snowflake transfers (2025-05)

In Preview, BigQuery Data Transfer Service can schedule automated transfers from Snowflake.


### YouTube transfer reach reports (2026-02)

BigQuery Data Transfer Service transfers from YouTube Channel and YouTube Content Owner now support reach reports.


## Administration, reservations, clients, and observability

### Apache Arrow Storage Write API input (2025-04)

In Preview, the BigQuery Storage Write API can stream data in Apache Arrow format.


### BigQuery `ObjectRef` functions reach GA (2026-03)

GA `ObjectRef` functions support direct or delegated access, and `OBJ.MAKE_REF` automatically fetches current Cloud Storage metadata into `ref.details`. `OBJ.GET_READ_URL` returns a `STRUCT` containing a read URL and status columns and renders image results in the console when a write URL is unnecessary.


### BigQuery Agent Analytics plugin (2025-11)

The Agent Development Kit plugin streams agent prompts, tool use, and responses directly to BigQuery through the Storage Write API for performance analysis and visualization.


### BigQuery CMEK key rotation (2025-07)

At GA, updating a table with its existing Cloud KMS key updates the table's encryption key, so key rotation does not require changing the key resource.


### BigQuery conversational analytics (2025-10)

Early-access conversational analytics lets users chat with BigQuery data, create custom agents, and make those agents available outside BigQuery.


### BigQuery custom constraints on additional resources (2026-04)

Preview custom organization policies can allow or deny specific operations on BigQuery tables, data policies, and row access policies.


### BigQuery custom organization constraints (2025-05)

Preview custom Organization Policy constraints can restrict supported fields on BigQuery resources.


### BigQuery DataFrames in dbt (2025-05)

In Preview, the `dbt-bigquery` adapter can execute Python code defined in BigQuery DataFrames.


### BigQuery dataset undelete (2026-02)

At GA, a deleted BigQuery dataset can be restored within its time-travel window to its state at deletion.


### BigQuery fluid scaling reaches GA (2026-06)

GA fluid scaling bills autoscaling reservations per second with no minimum duration.


### BigQuery Go disaster-recovery fields (2025-10)

Go client 1.71.0 adds `FailoverReservationRequest.failover_mode` for choosing `HARD` or `SOFT` failover and `Reservation.replication_status.soft_failover_start_time` for observing an active soft failover.


### BigQuery hybrid search temporarily disabled (2026-07)

Support for combining semantic and lexical search with `VECTOR_SEARCH` is temporarily disabled.


### BigQuery Java and Python client additions (2025-07)

`google-cloud-bigquery` 3.35.0 adds `null_markers`, `source_column_match`, date and time format and time-zone controls for load and external configurations, plus `UpdateMode`, `dataset_view`, and `total_slot_ms`. Java client 2.53.0 adds custom time-zone and timestamp support and OpenTelemetry support for BigQuery RPCs.


### BigQuery Java client 2.57 (2025-12)

Java client 2.57.0 adds `timestamp_precision` to `Field`, introduces `DataFormatOptions` for controlling BigQuery data-type output, and relaxes client-side validation of BigQuery entity IDs.


### BigQuery Java OpenTelemetry integration (2025-06)

BigQuery Java client 2.52.0 integrates OpenTelemetry into retries and jobs.


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


### BigQuery Omni VPC allowlists (2025-01)

GA BigQuery Omni VPC allowlists can restrict access to AWS S3 buckets and Azure Blob Storage to specific BigQuery Omni VPCs.


### BigQuery Python UDFs reach GA (2026-05)

Python user-defined functions are GA.


### BigQuery regression re-execution audit identity (2026-05)

BigQuery can re-execute side-effect-free instructions at no cost or resource consumption to detect regressions. Data Access logs can identify these executions as `bigquery-adminbot@system.gserviceaccount.com`.


### BigQuery remote MCP server (2025-12)

The Preview BigQuery remote MCP server lets LLM agents perform data-related tasks against BigQuery.


### BigQuery replication metrics (2026-03)

GA Cloud Monitoring metrics report dataset-replication latency and network-egress bytes for BigQuery cross-region replication and managed disaster recovery.


### BigQuery reservation groups (2025-10)

Preview reservation groups make member reservations share idle slots with one another before releasing those slots to other reservations in the admin project.


### BigQuery resource utilization charts (2025-02)

Preview resource utilization charts add metrics views and more chart-configuration options for monitoring BigQuery resources.


### BigQuery Storage partition request limit (2025-05)

The Go BigQuery storage client documents an increase from 100 to 900 partitions that can be inserted, updated, or deleted in one request.


### BigQuery table parameters restored (2026-01)

Support for table parameters in table-valued functions is restored after its temporary disablement.


### BigQuery workload-management constraints (2026-05)

Preview custom organization policies can allow or deny operations on reservations, assignments, capacity commitments, and BI reservations.


### Catalog-published data quality results (2025-06)

At GA, a data quality scan can publish its latest results as metadata on the Dataplex Universal Catalog entry for the source table. Existing scans must be edited and have publishing re-enabled before they publish to the catalog.


### CDC custom ordering (2025-03)

GA BigQuery change data capture can use `_CHANGE_SEQUENCE_NUMBER` to control the ordering of streaming `UPSERT` operations.


### Change data capture naming (2026-01)

BigQuery change data capture is now named **BigQuery change data capture ingestion**.


### Column metadata indexing (2025-05)

GA column metadata indexing is available for both BigQuery tables and external tables.


### Conditional dataset IAM (2025-01)

BigQuery dataset ACLs support conditional IAM access at GA, and Java client 2.46.0 can configure IAM conditions on datasets.


### Conversational analytics glossaries (2026-02)

Preview BigQuery conversational analytics agents can use custom glossary terms created and reviewed in BigQuery, and users can review terms imported from Dataplex Universal Catalog for an agent.


### Cross-region BigQuery load and export (2025-05)

At GA, batch loads and exports can move data between any region or multi-region in one `bq load`, `LOAD DATA`, `bq extract`, or `EXPORT DATA` operation.


### Data policies directly on BigQuery columns (2025-07)

In Preview, data policies can be associated directly with columns for database-level access control, masking, and transformation rules.


### Dataform CMEK organization policy (2025-03)

Dataform supports the CMEK organization policy.


### Dataset custom constraints GA (2025-11)

Custom Organization Policy constraints on specific fields of BigQuery dataset resources are GA.


### Dataset IAM permission enforcement (2025-05)

Starting March 17, 2026, viewing dataset access controls or querying `INFORMATION_SCHEMA.OBJECT_PRIVILEGES` requires `bigquery.datasets.getIamPolicy`. Updating dataset access controls, or creating a dataset with access controls through the API, requires `bigquery.datasets.setIamPolicy`; early enforcement can be enabled before that date.


### Default BigQuery connections (2025-03)

Preview default connections let a project define reusable Cloud resource connections that are selected by default.


### Default Gemini API enablement for BigQuery (2025-07)

The `cloudaicompanion.googleapis.com` API is enabled by default for most BigQuery projects, except opted-out projects and projects linked to accounts based in EMEA regions.


### Direct BigQuery column data policies reach GA (2026-02)

Associating data policies directly with BigQuery columns for access control, masking, and transformation is now GA.


### External files in BigQuery data preparations (2026-03)

At GA, BigQuery data preparations can clean, transform, and enrich files from Cloud Storage and Google Drive.


### External-data loading options reach GA (2026-01)

For BigQuery `CREATE EXTERNAL TABLE` and `LOAD DATA`, `time_zone`, the date and time format options, `null_markers`, and `source_column_match` are now GA.


### Gemini API enablement for European BigQuery projects (2026-03)

The Gemini for Google Cloud API, `cloudaicompanion.googleapis.com`, is now enabled for existing BigQuery projects in the European jurisdiction.


### Gemini CLI for BigQuery (2025-09)

Beta Gemini CLI extensions provide natural-language search, exploration, analysis, forecasting, and contribution analysis against BigQuery from the command line.


### Gemini in BigQuery data jurisdiction (2026-02)

Gemini in BigQuery processes data in the same `US` or `EU` jurisdiction as the associated datasets, or in a user-selected processing location.


### Global BigQuery default location (2026-03)

At GA, an organization or project can set a global default location that BigQuery uses when a request neither specifies a location nor lets BigQuery infer one.


### Iceberg external tables in materialized views (2025-06)

At GA, BigQuery materialized views can reference Iceberg external tables without first migrating the data to BigQuery-managed storage.


### KLL approximate quantiles (2025-03)

Preview KLL quantile functions efficiently compute approximate quantiles in BigQuery.


### Managed disaster recovery soft failover (2025-09)

BigQuery managed disaster recovery supports soft failover at GA.


### Materialized views over active CDC tables (2026-04)

At GA, BigQuery materialized views can be created over tables with active change data capture ingestion.


### Open-source BigQuery JDBC driver (2026-01)

The Google-developed open-source JDBC driver for connecting Java applications to BigQuery is available in Preview.


### Open-source BigQuery JDBC driver reaches GA (2026-06)

The Google-developed open-source JDBC driver for connecting Java applications to BigQuery is GA.


### Organization policies for BigQuery routines (2026-03)

Preview custom organization-policy constraints can allow or deny specific operations on BigQuery routines.


### Project-wide metadata scan administration (2025-07)

The GA **Metadata curation** page can manage data profile and data quality scans across a BigQuery project.


### Pub/Sub external import topics (2025-03)

Pub/Sub import topics can ingest streaming data from Azure Event Hubs, Amazon Managed Streaming for Apache Kafka, and Confluent Cloud.


### Pub/Sub Go resource tags and ingestion diagnostics (2025-10)

Go Pub/Sub v2.3.0 adds tags to `Subscription`, `Topic`, and `CreateSnapshotRequest` for their corresponding create requests. It also adds `AwsKinesisFailureReason.ApiViolationReason` for Kinesis ingestion failures.


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


### Python user-defined functions (2025-04)

Preview BigQuery Python UDFs can use additional libraries and call external APIs.


### Reservation labels (2025-10)

At GA, BigQuery reservations can carry labels for organization and billing analysis.


### Routine-level IAM (2025-05)

In Preview, IAM access controls can be applied directly to BigQuery routines.


### Row-level policy subqueries (2025-03)

GA BigQuery row-level access policies can contain subqueries and work with BigLake managed tables and the BigQuery Storage Read API.


### Salted random-hash masking (2026-01)

The `RANDOM_HASH` predefined BigQuery masking rule returns a salted hash of a column value and provides stronger protection than the standard SHA-256 masking rule.


### Source date and time parsing (2025-06)

In Preview, BigQuery `CREATE EXTERNAL TABLE` and `LOAD DATA` accept `time_zone`, `date_format`, `datetime_format`, `time_format`, and `timestamp_format` options for parsing source files.


### Strict act-as enforcement for BigQuery workflows (2026-01)

Dataform workflows, BigQuery notebooks, pipelines, and data preparations now enforce strict act-as mode project-wide, so every repository must use a custom service account instead of the default Dataform service agent. Grant `roles/iam.serviceAccountUser` to that default agent and the relevant principals or automatic releases can fail.


### Table parameters temporarily disabled (2025-10)

BigQuery temporarily disabled table parameters in table-valued functions after their September Preview release.


### TransUnion entity resolution (2025-10)

BigQuery entity resolution supports TransUnion at GA.


### Unsupported BigQuery organization defaults (2025-06)

The `default_sql_dialect_option` and `query_runtime` configuration settings are unsupported at the organization level.


### User credentials for BigQuery pipelines (2025-05)

In Preview, Google Account user credentials can authorize creating, scheduling, and running pipelines and scheduling notebooks and data preparations.
