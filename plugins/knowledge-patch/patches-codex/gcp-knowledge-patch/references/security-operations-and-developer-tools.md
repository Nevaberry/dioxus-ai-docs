# Security, Operations, and Developer Tools

Use this reference for security, operations, and developer tools compatibility details and current behavior.

## IAM, policy, and access control

### Cloud API Registry (2025-12)

Preview Cloud API Registry in the Google Cloud console can view and manage the MCP servers and tools that an agent is allowed to access.


### Legacy SQL access restriction (2026-02)

Effective June 1, 2026, an organization or project with no Legacy SQL use from November 1, 2025 through June 1, 2026 loses Legacy SQL access. Prior users keep existing workloads, but new Legacy SQL workloads might not be allowed.


## Billing, quotas, and resource governance

### Organization-wide search-index accounting (2025-06)

The GA `INFORMATION_SCHEMA.SEARCH_INDEXES_BY_ORGANIZATION` view reports search-index consumption against an organization's regional limit, broken down by project and table.


### Per-second reservation telemetry (2025-09)

The GA `INFORMATION_SCHEMA.RESERVATIONS_TIMELINE.per_second_details` field reports reservation capacity, usage, and autoscale utilization per second.


## Observability, diagnostics, and developer tooling

### `AI.AGG` availability (2026-04)

The Preview `AI.AGG` function semantically aggregates unstructured input from natural-language instructions, but support was temporarily disabled on April 13, 2026.


### Administrative job comparison (2025-10)

The Preview administrative jobs explorer adds a job-details page whose Performance tab combines the execution graph, SQL, history, performance variance, and system load; it can also compare two jobs.


### Advertising transfer controls (2025-03)

Google Ad Manager transfers can repeat every four hours or more, default to eight hours, and skip match tables with `load_match_tables = FALSE`. Search Ads transfers expose PMax data in `CartDataSalesStats`, `ProductAdvertised`, `ProductAdvertisedDeviceStats`, and `ProductAdvertisedConversionActionAndDeviceStats`.


### Colab Data Apps (2026-04)

Preview Colab Data Apps turn Colab notebook analyses into interactive applications.


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


### Facebook Ads `AdInsightsMMM` transfers paused (2026-07)

Support for the `AdInsightsMMM` report is temporarily disabled because of upstream schema changes. Existing Facebook Ads transfers continue to run but omit that report's data.


### Facebook Ads transfer type change (2026-04)

Starting July 25, 2026, the Facebook Ads connector maps `AdInsightsActions.ActionValue` from `INT` to `FLOAT`.


### Google Ads transfer MFA (2026-04)

Starting May 7, 2026, new Google Ads transfer configurations that use individual-user authentication require multi-factor authentication.


### Google Gen AI SDK for C# (2025-10)

The Preview C# SDK supports `GenerateContentAsync`, `GenerateContentStreamAsync`, `GenerateImagesAsync`, and the Live API methods `SendClientContentAsync`, `SendRealtimeInputAsync`, and `SendToolResponseAsync`.


### History-based optimization default (2025-09)

History-based query optimizations are enabled by default; projects or organizations where they were previously disabled can explicitly re-enable them.


### Materialized-view smart-tuning scope (2025-04)

GA smart-tuning can optimize a materialized view when it is in the same project as one of its base tables or in the project that runs the query.


### Merchant Center multi-client best sellers (2025-06)

The GA Merchant Center best sellers report supports multi-client accounts: `aggregator_id` can be used to query the tables, and `BestSellersEntityProductMapping` maps best-selling entities to products in sub-account inventory.


### Multi-series ARIMA_PLUS_XREG forecasting (2025-06)

The `TIME_SERIES_ID_COL` option for forecasting multiple time series with one `ARIMA_PLUS_XREG` multivariate model is GA.


### Optimized managed AI functions (2026-04)

Preview optimized mode for `AI.IF` and `AI.CLASSIFY` reduces LLM token consumption and query latency on large datasets.


### Partitioned TreeAH vector indexes (2025-06)

In Preview, the `PARTITION BY` clause of `CREATE VECTOR INDEX` can partition TreeAH indexes, enabling partition pruning and lower I/O.


### Query text heatmap (2025-11)

The Preview query text heatmap maps SQL text to execution stages that consume more slot time and exposes their query-plan details.


### RAG cross-corpus retrieval (2026-04)

Public-Preview cross-corpus retrieval lets `AsyncRetrieveContexts` and `AskContexts` retrieve contexts or generate answers from multiple RAG corpora in one operation.


### Search-index column granularity (2025-03)

Preview search indexes can store extra column information by setting column granularity, allowing search queries to be optimized further.


### Session IDs in reusable SQL objects (2026-04)

The GA `@@session_id` system variable is available inside SQL user-defined functions, table functions, and logical views.


### Shared-dataset usage fields (2025-10)

The GA `INFORMATION_SCHEMA.SHARED_DATASET_USAGE` view adds `shared_resource_id`, `shared_resource_type`, and `referenced_tables`; the last field identifies each base table and its processed bytes for external-table and routine usage.


### Single-table `AI.DETECT_ANOMALIES` (2026-05)

GA `AI.DETECT_ANOMALIES` can take one input table containing both historical and target data.


### Single-vector `VECTOR_SEARCH` syntax (2026-03)

In Preview, an alternate `VECTOR_SEARCH` call syntax can improve query performance when searching for one vector.


### SQL user-defined aggregate functions (2025-03)

GA SQL user-defined aggregate functions can be created with `CREATE AGGREGATE FUNCTION`.


### Stateful continuous queries (2026-04)

Preview continuous queries can retain information across rows or time intervals and use stateful `JOIN` operations and windowed aggregations.


### Stored-column usage for vector search (2025-01)

At GA, query-job information exposes `StoredColumnsUsage` for vector searches that use stored columns.


### TimesFM evaluation (2025-10)

The built-in TimesFM capability is GA: `AI.FORECAST` accepts a larger context window, and `AI.EVALUATE` compares forecast output with a historical reference time series.


### TimesFM forecasting and anomaly functions (2026-03)

GA `AI.DETECT_ANOMALIES` accepts a custom context window, and GA `AI.FORECAST` can specify the latest timestamp for forecasting. `AI.EVALUATE` accepts a custom context window and returns mean absolute scaled error.


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


### Virtual Try-On endpoint migration (2026-01)

Virtual Try-On is GA at `virtual-try-on-001`; applications using `virtual-try-on-preview-08-04` should migrate to the new endpoint.
