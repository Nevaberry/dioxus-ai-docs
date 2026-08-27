# Search, Relevance, and Query Insights

Use this reference for relevance evaluation, experiment APIs, Learning to Rank, Query Insights, live queries, workload routing, and search diagnostics.

## Search scoring and request templates

### Scoring baseline

OpenSearch 3.0.0 changes the default scorer from `LegacyBM25Similarity` to `BM25Similarity`. Recalibrate score thresholds and ranking tests when migrating.

### Deferred templates

Since 2.19.0, a `template` query can retain unresolved placeholders until a search request processor assigns them. Use this when pipeline context, inference, or request metadata supplies values late.

## Search Relevance Workbench

### Evaluation and experiments

- In 3.1.0, Search Relevance Workbench compares algorithms and evaluates quality using User Behavior Insights. It supports hybrid experiments, imports externally created judgments, exposes statistics at `/_plugin/_search_relevance`, and represents judgments as ratings rather than scores.
- In 3.2.0, the new interface is the default with an opt-out. Dashboards visualizes evaluation and hybrid-experiment results. Implicit judgments filter User Behavior Insights events by date; hybrid-optimizer and pointwise experiments can run as scheduled tasks.
- Agentic search joins single-query and pairwise comparison tools in 3.4.0. Experiments can be scheduled or descheduled in the UI, and experiment, search-configuration, query-set, and judgment-list views support GUID filtering.
- Search Relevance Workbench becomes generally available in 3.5.0.

### Judgments and resource search

- In 3.5.0, LLM-based judgments accept custom prompt templates, and the comparison UI can reuse search configurations.
- Search Configurations, Judgments, Query Sets, and Experiments each have a `_search` endpoint that accepts OpenSearch DSL from 3.5.0.
- In 3.7.0, Dashboards imports CSV judgment sets with up to 10,000 rows.
- In 3.8.0, LLM-as-a-Judge works through any ML Commons connector while retaining the earlier connector interface. Judgment metadata reports success and failure counts and lists failed queries instead of silently dropping unrated documents.

### Experiment inputs and integrity

- In 3.6.0, Query Sets can be created manually from plain text, key-value, JSON Lines, or NDJSON, and the workbench supports multiple data sources.
- Evaluations in 3.6.0 add Recall@K, mean reciprocal rank, and DCG@K. Binary metrics such as Precision and MAP derive relevance thresholds dynamically from percentiles.
- In 3.8.0, search configurations accept ScriptService-backed Mustache variables alongside `%SearchText%`, allowing parameters such as category, brand, or status.
- Experiments in 3.8.0 store SHA-256 signatures for query sets, judgments, and search configurations. `GET /_plugins/_search_relevance/experiments/{id}/validate` reports `VALID`, `DRIFTED`, or `UNAVAILABLE`; create and update validate that referenced resources exist.

### Hybrid optimizer

The 3.7.0 optimizer adds Z-score normalization and RRF across selected `rank_constant` values. It evaluates 82 variants per query, and experiments can opt into selected techniques.

### Relevance Agent

The disabled-by-default 3.6.0 Relevance Agent analyzes user behavior, proposes ranking changes, and validates them through offline evaluation in a multi-agent Dashboards flow.

## Learning to Rank

The Learning to Rank plugin introduced in 2.19.0 rescores with lightweight models such as XGBoost and RankLib. It uses `.ltrstore*` as a system index and provides settings, statistics, a circuit breaker, and read/full-access security roles.

In 3.2.0, Learning to Rank can evaluate XGBoost models whose input features contain missing values.

## Query Insights

### Historical top queries

- In 2.19.0, Dashboards adds historical top-N queries, drill-downs, configuration, and retention. The backend adds fetch-by-ID and automatic expiration; the custom local-index-name setting is removed.
- In 3.1.0, Query Insights can exclude selected indexes, attach metric labels to historical records, and report `isCancelled` in Live Queries. Dashboards adds dedicated Live Queries and Workload Management views.
- In 3.4.0, Dashboards adds version-aware Query Insights settings and multiple-data-source support on Live Queries; its Workload Management view can use security attributes.
- In 3.5.0, Top-N records can include username and user roles. Wrapper endpoints around settings provide finer-grained access control, and the Top-N view integrates workload-group filtering and sorting.
- In 3.6.0, Top-N data can export timestamp-organized JSON to remote blob repositories, with S3 supported. Dashboards adds P90/P99 statistics plus distribution, line, and heatmap views.

### Live Queries

- The 3.0.0 inflight/live-queries API provides real-time monitoring. The top-queries API adds `verbose`, and Dashboards renders returned columns dynamically.
- In 3.2.0, Dashboards supports multiple data sources for Inflight Queries, and the reader search limit rises to 500.
- In 3.3.0, Live Queries can filter by workload group, with bidirectional navigation between query and group views.
- In 3.6.0, Live Queries adds shard-level task details and an on-demand finished-query cache. Failed queries receive an explicit tag.
- In 3.8.0, Live Queries identity records can include username, roles, and backend roles for authorization-aware analysis.

### Profiling and recommendations

- In 3.6.0, an asynchronous rule-based service analyzes top-N queries and returns recommendations with confidence and estimated impact.
- In 3.7.0, Dev Tools gains a Query Insights profiler with shard timings and a collapsible query tree. Query Details links to it, and the Top Queries API can inline recommendations with the `recommendations` parameter.

### Authorization filtering

From 3.6.0, Query Insights can filter by username and shared backend roles so non-admin users see only authorized records.

## Workload Management

### Routing and automatic tagging

- In 3.1.0, index-based rules automatically tag requests with workload groups, avoiding a required explicit header on every search.
- In 3.3.0, automatic tagging expands from index patterns to principal attributes such as username and role.

### Per-group search controls

In 3.7.0, workload groups can override search timeout, cancellation interval, maximum bucket count, and other settings for every routed request.

## Search-result diagnostics

### Cardinality execution hints

OpenSearch 2.19.1 accepts an execution hint for cardinality aggregations. Only emit it to compatible targets.

### Search experiment and query explanations

Use vector and neural query explanations for search evaluation where available: Faiss explain covers exact, ANN, radial, and disk search in 3.0.0, and SEISMIC participates in explanation in 3.5.0.
