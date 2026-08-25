# Vector and Neural Search

Use this reference for k-NN mappings, engines, compression, hybrid ranking, semantic fields, sparse retrieval, and vector response behavior.

## Engine selection, storage, and mapping

### Faiss, Lucene, and NMSLIB

- Since 2.18, Faiss is the implicit k-NN engine. With `space_type: "cosinesimil"` and no explicit engine, indexing normalizes vectors and stored values differ from the inputs. Already-normalized vectors can use `innerproduct` for equivalent scoring without implicit normalization.
- In 2.19.0, Lucene supports binary vector indexes. Faiss supports cosine similarity and radial search without caller-side normalization.
- A 2.19.0 training-backed mapping cannot specify both a model ID and `dimension`; the dimension comes from the model's training index. `index.knn` is immutable after index creation, and `fields` searches work with `knn_vector`.
- In 3.0.0, old index-level settings for `ef_construction`, `m`, space type, and plugin enablement are removed.
- In 3.1.0, mode and compression settings are rejected for indexes created before 2.17.0. Derived vector source cannot be enabled when `index.knn=false`.

### Derived vector source

The disabled-by-default 2.19.0 implementation removes k-NN vectors from stored `_source` and injects them on reads. It covers flat mappings, object fields, and single-level nested fields. In 3.0.0 it becomes production-ready for Faiss, Lucene, and NMSLIB.

### Semantic-field mappings

- In 3.0.0, Neural Search adds a semantic field mapper.
- In 3.1.0, semantic fields can toggle chunking, use fixed-character chunking, and apply search analyzers at index creation and query time.
- In 3.2.0, generated dense `knn_vector` fields can set engine, mode, compression, and method. Semantic mappings also support ingest batch sizing, sparse prune strategies, configurable chunking, existing-embedding reuse, and `TOKEN_ID` sparse embeddings.

## Compression, quantization, and memory

### Build and search acceleration

- In 3.0.0, `memory-optimized-search` provides a lower-memory Faiss mode, and concurrent segment search is enabled by default for k-NN.
- The experimental 3.0.0 GPU path accelerates vector operations.
- k-NN 3.0.0 adds node-level circuit breakers so heterogeneous nodes can enforce different memory limits.
- GPU index builds become production-ready in 3.1.0. Remote vector index building is enabled by default with `index.knn.remote_index_build.enabled`.
- In 3.2.0, GPU builds extend beyond FP32 to FP16, byte, and binary vectors.
- A terminal remote-vector-build failure in 3.2.0 no longer falls back to a CPU build; surface the failure to operators.
- In 3.4.0, warmup works with memory-optimized search, including indexes created before 2.18.

### Binary and one-bit compression

- In 3.1.0, QAT-accelerated Zstandard compression is available through OpenSearch Custom Codecs.
- In 3.2.0, binary-quantized Faiss can use asymmetric distance computation: compare a full-precision query with compressed document vectors. Random rotation reduces information loss at 32x compression. Asymmetric distance computation also works when Lucene graph search runs on Faiss indexes.
- In 3.6.0, Lucene BBQ and Faiss scalar quantization support 1-bit vectors at 32x compression for approximate and exact search. This includes Lucene flat format and Faiss memory-optimized search; Faiss 32x defaults to the SQ 1-bit encoder.
- Also in 3.6.0, vector metadata can use Zstandard and byte vectors gain a Hamming-distance scorer.
- Remote index builds add 1-bit scalar quantization in 3.7.0.

### Rescoring and filtering

- In 2.19.0, `rescore: false` correctly disables rescoring.
- New on-disk 4x-compressed indexes rescore by default in 3.1.0. Explicitly set `rescore: false` to preserve earlier behavior.
- In 3.1.0, inner vector search results can be rescored. Lucene HNSW graph search can run over Faiss indexes with partial byte loading and early termination, and memory-optimized search supports Faiss binary indexes.
- In 3.5.0, an index setting can disable the exact-search phase that follows ANN search for Faiss efficient filters.

## Vector input and output

### Base64 vectors

- In 3.7.0, `docvalue_fields` can retrieve float, byte, and binary `knn_vector` values from Lucene and Faiss at all compression levels without reindexing. The default returned representation is Base64-encoded binary, not an array.
- In 3.8.0, `knn_vector` values can be indexed and bulk-ingested as Base64, reducing JSON-array overhead.
- A 3.8.0 search request processor can automatically remove vector fields from `_source` in k-NN responses when callers only need documents and scores.

## Nested and approximate retrieval

### Nested vectors and inner hits

- In 2.19.0, nested k-NN `inner_hits` returns multiple values with Lucene or Faiss. NMSLIB uses `expand_nested_docs`; neural k-NN queries use `expand_nested`.
- In 3.2.0, field-collapsed hybrid queries can return `inner_hits` for each collapsed group.
- In 3.4.0, SEISMIC sparse ANN supports nested fields during ingestion and querying, and its query can omit `method_parameters`.
- In 3.7.0, request-level opt-in lets batch semantic highlighting process nested-document `inner_hits` and return the relevant nested passage.

### Approximate numeric queries

In 3.2.0, approximate queries cover `HALF_FLOAT`, `FLOAT`, `DOUBLE`, `INTEGER`, `BYTE`, `SHORT`, and `UNSIGNED_LONG`, and accept `search_after`.

## Hybrid queries and score fusion

### Normalization and diagnostics

- In 2.19.0, hybrid search adds `pagination_depth` and reciprocal rank fusion. `hybrid_score_explanation` explains normalization and combination; `verbose_pipeline` exposes each search-pipeline transformation.
- In 3.0.0, hybrid search adds Z-score normalization and a lower bound for min-max normalization. Hybrid and neural query builders can use filter functions.
- Hybrid queries in 3.0.0 can return `inner_hits` for nested and parent-join results.
- In 3.1.0, the RRF normalization processor accepts custom weights. `collapse` groups and deduplicates results, and invalid nested hybrid structures are rejected.
- In 3.2.0, min-max normalization adds an upper bound.
- In 3.5.0, hybrid search supports `min_score` and gRPC execution.

### Composition restrictions

- In 3.6.0, a `hybrid` query is rejected inside compound queries such as `function_score`, `constant_score`, or `script_score`.
- In 3.8.0, hybrid queries reject `dfs_query_then_fetch` because it can produce incorrect results. Use another search type.

## Semantic, sparse, and reranking behavior

### Semantic search

- In 3.0.0, Neural Search adds sentence highlighting with a bundled QA model and custom tags, analyzer-based neural sparse queries, and a stats API.
- A neural sparse query in 3.1.0 cannot specify both a model ID and an analyzer.
- Neural Search statistics in 3.1.0 add `include_individual_nodes`, `include_all_nodes`, and `include_info`, cover more processors and algorithms, and reject invalid statistic names with a bad-request response instead of ignoring them.
- In 3.3.0, semantic highlighting can batch remote inference, and semantic fields can use the sparse two-phase processor.
- In 3.5.0, asymmetric embedding models are supported.

### Sparse and diversity retrieval

- In 3.3.0, SEISMIC provides sparse approximate-nearest-neighbor retrieval.
- k-NN and neural queries in 3.3.0 add native maximal marginal relevance.
- `lateInteractionScore` provides ColBERT-style multi-vector rescoring in Painless, and vector-field creation accepts an optional top-level `engine`.
- In 3.5.0, SEISMIC queries participate in query explanations.

### Reranking score preservation

In 3.8.0, a Neural Search reranking pipeline can choose the field used to retain the prior score, avoiding accidental overwrite of an existing document field.

## Aggregation indexes and related search structures

### Star-tree

- The 2.19.0 experimental implementation accelerates metric aggregations and date histograms containing metric aggregations.
- Star-tree becomes production-ready in 3.1.0.
- In 3.2.0, it accelerates aggregation queries over IP fields. Index, node, and shard statistics expose total, active, and elapsed-time usage. Optimization is suppressed when DLS, FLS, or field masking applies; Custom Codecs supports composite indexes.
- In 3.3.0, it accelerates `multi_terms`; search statistics add star-tree failure counts at index, node, and shard scope.

### Streaming aggregation

In 3.2.0, segment-level partial aggregation results can stream to the coordinating node, moving high-cardinality reduction work away from data nodes instead of returning one response per shard.

## Geospatial validation

OpenSearch 3.5.0 enforces coordinate limits for lines, polygons, and polygon holes. Validate generated shapes before indexing or querying.
