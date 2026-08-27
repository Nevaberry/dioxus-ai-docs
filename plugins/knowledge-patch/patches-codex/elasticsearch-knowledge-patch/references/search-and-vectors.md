# Search, Semantic Fields, and Vectors

## Semantic and sparse search

### `semantic_text` is generally available (8.18.0)

`semantic_text` provides an integrated field mapping and inference workflow for
semantic search. Inference-specific defaults are in
[inference.md](inference.md).

### Query and highlighting support (9.0.0)

`semantic_text` works with `match`, `sparse_vector`, and kNN vector queries and
with highlighting. It supports multi-fields and participates in text-family
behavior.

### Sparse-vector token pruning (8.19.0)

Token pruning for `sparse_vector` queries is generally available rather than
technical preview.

### Semantic field storage and query controls (9.2.0)

The Fields API can retrieve indexed `semantic_text` chunks, and semantic
embeddings can be included in `_source`. Reindex always includes vector values
despite transparent removal from `_source`. kNN filters support nested
metadata, semantic queries can span multiple inference IDs, and HNSW kNN
profiling supports early termination.

## Retrievers, ranking, and rescoring

### Multi-vector reranking with `rank_vectors` (8.18.0)

Experimental `rank_vectors` supports multi-vector late-interaction second-stage
reranking, including ColBERT- and ColPali-style workloads. Use it when HNSW
indexing is too costly but reranking can improve relevance.

### Rescorer and linear retrievers (9.0.0)

Search adds a generic rescorer retriever backed by request rescoring and a
linear retriever that computes weighted sums over sub-retrievers. Quantized kNN
vectors can be rescored, and BBQ indices are generally available.

### Retriever additions (9.1.0)

Search adds a pinned retriever, `l2_norm` normalization and minimum score for
the linear retriever, and simplified Linear and RRF retrievers.
Text-similarity reranking can optionally be allowed to fail.

### Retriever weighting and normalization (9.2.0)

RRF supports weights, and simplified RRF syntax supports per-field weights.
Simplified RRF and linear retrievers can query multiple indices. The linear
retriever has a top-level normalizer.

### Scripted and contextual rescoring (9.2.0)

Search adds a script rescorer. `text_similarity_reranker.chunk_rescorer` chunks
fields and scores contextual snippets rather than the entire field text.

### MMR result diversification (9.3.0)

Search adds an MMR retriever for result diversification.

## Vector mappings and index types

### Storage outside `_source` (9.0.0)

`sparse_vector` values can be stored outside `_source`. Synthetic-source
indices have an index setting that skips recovery source.

### Quantized mapping and rescoring (9.1.0)

`rescore_vector` is generally available. `oversample: 0` bypasses oversampling
and rescoring, while BBQ indices receive a default oversample. Quantized index
types accept `vector_rescore`. Existing `dense_vector` mappings can be updated
to `bbq_flat` or `bbq_hnsw`.

### DiskBBQ indexes (9.2.0)

`disk_bbq` targets lower-memory operation without HNSW's memory profile. It
accepts only floating-point vectors, uses one-bit quantization, and is not
recommended for low-dimensional vectors. Tune kNN with `num_candidates` or
`visit_percentage`.

```http
PUT vectors
{"mappings":{"properties":{"vector":{"type":"dense_vector","index_options":{"type":"disk_bbq"}}}}}
```

### BFloat16 and on-disk rescoring (9.3.0)

Every `dense_vector` index type accepts `element_type: bfloat16`, halving bytes
per value with reduced precision and conversion overhead. Set
`on_disk_rescore: true` when raw rescoring vectors exceed RAM.

```http
PUT vectors
{"mappings":{"properties":{"vector":{"type":"dense_vector","element_type":"bfloat16","index_options":{"type":"disk_bbq","on_disk_rescore":true}}}}}
```

### Vector indexing and input changes (9.3.0)

Vector values can be indexed from base64, `rank_vectors` supports BFloat16, and
HNSW early termination defaults on. `semantic_text` can optionally use GPU
indexing for HNSW and `int8_hnsw`.

### Vector index controls (9.4.0)

New indices default vector indexing to DiskBBQ. Configure DiskBBQ quantization
at 1, 2, 4, or 7 bits. HNSW fields add `flat_index_threshold`; search adds an
embedding query-vector builder.

## Rescoring I/O and memory

### Direct I/O for BBQ rescoring (9.2.0)

Set `vector.rescoring.directio=true` on every vector-search node to bypass
page-cache pressure in low off-heap-memory environments. This can slow searches
when vectors fit in memory, so benchmark the tradeoff.

### Vector retrieval, statistics, and scripting (9.1.0)

Source retrieval can include or exclude vectors. Node and index stats expose
dense-vector off-heap usage. Painless `dotProduct` and `cosineSimilarity`
accept float vectors with byte-vector fields.

### GPU vector indexing (9.2.0)

`GPUPlugin` supports indexing vectors on a GPU.

Affected-version direct-I/O and GPU issues are in
[deprecations-and-known-issues.md](deprecations-and-known-issues.md).

## Cross-project search and diagnostics

### Cross-project search routing (9.3.0)

Cross-project search and `project_routing` apply to `_search`, `_async_search`,
`_msearch`, EQL, field capabilities, SQL, and JDBC. Point-in-time creation and
closure can span projects. Cross-project search defaults to minimizing round
trips.

### Cross-project and SQL clients (9.4.0)

Project routing extends to templated searches, data streams, scrolls, and the
SQL CLI. The SQL CLI and JDBC client accept API-key authentication.

### Search diagnostics and async results (9.4.0)

Query logging covers `_search`, ES|QL, EQL, and SQL. A search-task watchdog can
log hot threads for slow searches. Async retrieval accepts
`return_intermediate_results` to control in-progress partial output, and async
task status exposes `keep_alive`.
