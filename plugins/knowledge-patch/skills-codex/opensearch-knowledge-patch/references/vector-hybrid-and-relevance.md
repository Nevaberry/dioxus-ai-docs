# Vector, Hybrid, and Search Relevance

## Defining vector mappings and source behavior

### Engine and mapping rules

In 2.19.0, Lucene supports binary vector indexes, and Faiss supports cosine similarity and radial search without caller-side normalization. Nested k-NN `inner_hits` can return multiple values with Lucene or Faiss. NMSLIB uses `expand_nested_docs`, while neural k-NN queries use `expand_nested`.

A training-backed mapping cannot contain both a trained artifact identifier and `dimension`; the dimension comes from the training index. `index.knn` is immutable after index creation, `fields` searches work with `knn_vector`, and `rescore: false` actually disables rescoring.

Faiss became the implicit k-NN engine in 2.18. With `space_type: "cosinesimil"` and no explicit engine, vectors are normalized at indexing time and stored values differ from input. Already-normalized vectors can use `innerproduct` for equivalent scoring without implicit normalization.

### Derived vector source

The 2.19.0 experimental derived-source feature removes k-NN vectors from stored JSON `_source` and reinjects them when reading a document. It supports flat mappings, object fields, and single-level nested fields and is disabled by default.

Derived vector source becomes production-ready across Faiss, Lucene, and NMSLIB in 3.0.0. Since 3.1.0, enabling it while `index.knn=false` is rejected. Mode and compression settings are also rejected for indexes created before 2.17.0.

### Retrieving and transmitting vectors

Since 3.7.0, `docvalue_fields` can retrieve float, byte, and binary `knn_vector` values from Lucene and Faiss indexes at any compression level without reindexing. The default representation is Base64 binary rather than an array.

Since 3.8.0, `knn_vector` values can be ingested as Base64, reducing JSON-array serialization overhead for indexing and bulk requests. A search request processor can also exclude vector fields from response `_source` when only documents and scores are needed.

## Building and executing vector indexes

### Defaults and remote builds

Concurrent segment search is enabled by default for k-NN in 3.0.0. In 3.1.0, GPU index builds become production-ready, remote vector builds are enabled by default through `index.knn.remote_index_build.enabled`, and new OnDisk indexes with 4x compression rescore by default. Set `rescore: false` for the older behavior.

A terminal remote-vector-build failure no longer falls back to CPU in 3.2.0. GPU indexing in that release expands from FP32 to FP16, byte, and binary vectors. Remote builds support 1-bit scalar quantization in 3.7.0.

### Faiss execution controls

In 3.0.0, Faiss explanation covers exact, ANN, radial, and disk-based searches. `memory-optimized-search` reduces memory use, and node-level circuit breakers support heterogeneous memory limits. Remove legacy index-level `ef_construction`, `m`, space-type, and plugin-enablement settings.

Since 3.1.0, Lucene HNSW graph search can execute on existing Faiss indexes with partial byte loading and early termination. Memory-optimized search supports Faiss binary indexes, and inner vector results can be rescored.

The 3.4.0 warmup path supports memory-optimized search, including indexes created before 2.18. Since 3.5.0, an index setting can disable the exact-search phase that follows ANN when Faiss efficient filters are used.

### Compression, quantization, and distance

In 3.2.0, binary-quantized Faiss indexes can use asymmetric distance computation, comparing a full-precision query vector with compressed documents. Random rotation reduces information loss at 32x compression, and asymmetric distance also works when Lucene graph search executes on Faiss indexes.

In 3.6.0, Lucene BBQ and Faiss scalar quantization support 1-bit vectors at 32x compression for approximate and exact search. This includes Lucene flat format and Faiss memory-optimized search; Faiss 32x defaults to the SQ 1-bit encoder. Vector metadata can use Zstandard, and byte vectors gain a Hamming-distance scorer.

### Approximate queries

Since 3.2.0, approximate queries support `HALF_FLOAT`, `FLOAT`, `DOUBLE`, `INTEGER`, `BYTE`, `SHORT`, and `UNSIGNED_LONG`, and accept `search_after`.

## Building hybrid search pipelines

### Fusion, normalization, and diagnostics

Hybrid search in 2.19.0 adds `pagination_depth` for large result sets and reciprocal rank fusion as a rank-based alternative. `hybrid_score_explanation` explains normalization and combination, while `verbose_pipeline` exposes transformations across search-pipeline processors.

In 3.0.0, hybrid pipelines add Z-score normalization and a lower bound for min-max normalization. Hybrid and neural query builders accept filter functions, and nested or parent-join results can return `inner_hits`.

In 3.1.0, RRF accepts custom weights. `collapse` groups and deduplicates by field, and invalid nested hybrid structures are rejected. In 3.2.0, min-max adds an upper bound and collapsed groups can return their own `inner_hits`.

Neural Search in 3.5.0 supports hybrid queries over gRPC and `min_score` on hybrid searches. The 3.7.0 hybrid optimizer adds Z-score and RRF over selected `rank_constant` values, evaluates 82 variants per query, and can opt into selected techniques.

### Composition restrictions

Since 3.6.0, a `hybrid` query is rejected when nested in a compound query such as `function_score`, `constant_score`, or `script_score`.

Since 3.8.0, hybrid queries reject `dfs_query_then_fetch`, which can produce incorrect results. Use a supported search type.

## Authoring deferred and inference-driven searches

The 2.19.0 `template` query deliberately leaves placeholders unresolved until a search request processor fills them. ML inference search-request extensions can supply extra input fields required by an inference endpoint.

## Configuring semantic and sparse search

### Semantic fields and highlighting

Neural Search 3.0.0 adds semantic sentence highlighting with a bundled QA artifact and custom tags, a semantic field mapper, analyzer-based neural sparse queries, and a statistics API.

Since 3.1.0, semantic fields can enable or disable chunking, use fixed-character-length chunks, and apply search analyzers at index creation and query time. A neural sparse query cannot provide both an analyzer and an artifact identifier. The stats API adds `include_individual_nodes`, `include_all_nodes`, and `include_info`, covers more processors and algorithms, and returns a bad request for invalid statistic names.

In 3.2.0, semantic fields can configure generated dense `knn_vector` engine, mode, compression, and method. They also gain ingest batch sizing, sparse prune strategies, configurable chunking, existing-embedding reuse, and `TOKEN_ID` sparse embeddings.

In 3.3.0, the semantic-highlighting response processor can batch remote inference. Semantic fields can use the sparse two-phase processor. Since 3.7.0, batch highlighting can process nested-document `inner_hits` through request-level opt-in and return the relevant nested passage.

### Sparse and multi-vector retrieval

OpenSearch 3.3.0 adds SEISMIC sparse approximate-nearest-neighbor retrieval. k-NN and neural queries gain native maximal marginal relevance, `lateInteractionScore` supports ColBERT-style multi-vector rescoring, and vector-field creation accepts an optional top-level `engine`.

In 3.4.0, SEISMIC supports nested fields at ingestion and query time, and its query may omit `method_parameters`. It participates in query explanation in 3.5.0, when Neural Search also adds asymmetric embedding support.

Since 3.8.0, a reranking pipeline can choose the field that retains the previous score, avoiding accidental overwrite of an existing document field.

## Accelerating aggregations with star-tree

In 2.19.0, disabled-by-default experimental star-tree supports metric aggregations and date histograms containing metric aggregations. It becomes production-ready in 3.1.0.

In 3.2.0, star-tree accelerates aggregations whose queries target IP fields. Index, node, and shard stats expose total, active, and elapsed-time usage. Optimization is suppressed when DLS, FLS, or field masking is active.

In 3.3.0, star-tree adds `multi_terms` acceleration and failure counts to index-, node-, and shard-level search statistics.

## Evaluating relevance

### Search Relevance Workbench

Introduced in 3.1.0, Search Relevance Workbench compares search algorithms and evaluates User Behavior Insights, including hybrid experiments and imported external judgments. Its API root is `/_plugin/_search_relevance`; it exposes statistics and represents judgments as ratings, not scores.

In 3.2.0, the new Workbench interface becomes the default with an opt-out. It visualizes evaluation and hybrid-experiment results, filters implicit-judgment events by date, and schedules hybrid-optimizer and pointwise experiments.

In 3.4.0, the UI schedules and deschedules experiments and compares agentic search in single-query and pairwise tools. Experiment, search-configuration, query-set, and judgment-list views accept GUID filters.

Search Relevance Workbench is generally available in 3.5.0. It adds customizable prompt templates for automated judgments, lets the comparison UI reuse search configurations, and adds OpenSearch-DSL `_search` endpoints for Search Configurations, Judgments, Query Sets, and Experiments.

In 3.6.0, Workbench supports multiple data sources and manual Query Set creation from text, key-value, JSON Lines, or NDJSON. Evaluations add Recall@K, mean reciprocal rank, and DCG@K; binary-dependent Precision and MAP use dynamic percentile-based relevance thresholds. A disabled-by-default Relevance Agent uses a multi-agent workflow to analyze behavior, propose changes, and validate them offline.

In 3.7.0, Dashboards imports CSV judgment sets up to 10,000 rows directly. In 3.8.0, automated judgments work through any ML Commons connector, and metadata reports success and failure counts plus failed queries rather than silently dropping unrated documents.

Search configurations in 3.8.0 accept ScriptService-backed Mustache variables in addition to `%SearchText%`. Experiments record SHA-256 signatures for query sets, judgments, and search configurations; `GET /_plugins/_search_relevance/experiments/{id}/validate` reports `VALID`, `DRIFTED`, or `UNAVAILABLE`, and create/update validates referenced resources.

### Learning to Rank

The 2.19.0 Learning to Rank plugin rescores with lightweight ranking artifacts such as XGBoost and RankLib. It stores data in the `.ltrstore*` system index and provides settings, statistics, a circuit breaker, and read/full-access Security roles.

Since 3.2.0, Learning to Rank can evaluate XGBoost inputs containing missing feature values.
