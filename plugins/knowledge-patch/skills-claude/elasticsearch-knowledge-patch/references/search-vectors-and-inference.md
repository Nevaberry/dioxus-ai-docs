# Search, Vectors, Reranking, and Inference

## Semantic fields and multi-vector ranking

### `semantic_text`

`semantic_text` is generally available in 8.18.0 and integrates field mapping
with inference for semantic search. Since 9.0.0 it works with `match`,
`sparse_vector`, kNN, highlighting, multi-fields, and text-family behavior.

In 9.1.0, mappings accept `index_options`, configurable chunking, and bit
vectors. Compatible new fields default to BBQ. Empty content skips embedding;
`semantic_text` subfields are omitted from field capabilities. `sparse_vector`
mappings gain a default token-pruning setting, and sparse query token pruning
is generally available in 8.19.0.

The Fields API can retrieve indexed semantic chunks in 9.2.0. Semantic
embeddings can be included in `_source`, semantic queries can span inference
IDs, and kNN filters support nested metadata. Existing mappings can update
`inference_id` in 9.3.0. New fields default to ELSER on the Elastic Inference
Service when available and support BFloat16; GPU indexing can be used for HNSW
and `int8_hnsw`.

In 9.4.0, new semantic fields inherit DiskBBQ indexing and BFloat16 storage,
and the default inference ID and model switch to Jina v5. The text-similarity
rank retriever selects chunking defaults appropriate to its inference ID.

### `rank_vectors`

Experimental `rank_vectors` in 8.18.0 supports multi-vector, late-interaction
second-stage ranking for dense vectors, including ColBERT- and ColPali-style
workflows where HNSW indexing cost is undesirable. It supports BFloat16 in
9.3.0.

## Retriever composition and reranking

### Fusion and rescoring

Search adds a generic rescorer retriever and a weighted-sum linear retriever in
9.0.0. Quantized kNN vectors can be rescored, and BBQ indices are generally
available.

In 9.1.0, search adds a pinned retriever, `l2_norm` and minimum score for the
linear retriever, and simplified Linear and RRF retrievers. Text-similarity
reranking can optionally fail without failing the whole search.

RRF supports weighting in 9.2.0, and simplified RRF accepts per-field weights.
Simplified RRF and linear retrievers can search multiple indices, while linear
adds a top-level normalizer. Search also adds a script-based rescorer.
`text_similarity_reranker.chunk_rescorer` chunks fields and scores contextual
snippets rather than the complete field value.

MMR result diversification arrives as a retriever in 9.3.0. In 9.4.0, an ES|QL
MMR command is available and the MMR retriever accepts `semantic_text`.

## Dense-vector storage and indexing

### Quantized index controls

`rescore_vector` is generally available in 9.1.0. `oversample: 0` disables
oversampling and rescoring; BBQ indices otherwise receive a default oversample.
Quantized index types add `vector_rescore`. Existing `dense_vector` mappings
can be changed to `bbq_flat` or `bbq_hnsw`.

New 9.1 indices with dense vectors over 384 dimensions default to `bbq_hnsw`.
In 9.1.0, `vector.rescoring.directio=true` can severely slow searches when
vectors fit in memory; set it false until upgrading to 9.1.1.

### DiskBBQ

The `disk_bbq` type in 9.2.0 targets lower memory use without HNSW's memory
profile. It accepts floating-point vectors, uses one-bit quantization, and is
not recommended for low-dimensional vectors. Tune kNN with `num_candidates` or
`visit_percentage`:

```http
PUT vectors
{"mappings":{"properties":{"vector":{"type":"dense_vector","index_options":{"type":"disk_bbq"}}}}}
```

Set `vector.rescoring.directio=true` on every vector-search node to use direct
I/O for BBQ rescoring in low off-heap-memory environments. This avoids severe
page-cache latency but is slower when vectors fit in memory.

Elasticsearch 9.2.0 did not enforce the Enterprise requirement for `bbq_disk`
indices. After moving to 9.3 or later, existing indices remain usable, but new
ones require an Enterprise license.

### BFloat16 and on-disk rescoring

All dense-vector index types accept `element_type: bfloat16` in 9.3.0, halving
stored bytes per value at reduced precision and with conversion overhead.
`on_disk_rescore: true` keeps raw-vector rescoring on disk when vectors exceed
RAM:

```http
PUT vectors
{"mappings":{"properties":{"vector":{"type":"dense_vector","element_type":"bfloat16","index_options":{"type":"disk_bbq","on_disk_rescore":true}}}}}
```

Vector input can be base64. HNSW early termination defaults on. A `GPUPlugin`
supports GPU indexing from 9.2.0.

### Current index defaults and tuning

New indices default vector indexing to DiskBBQ in 9.4.0, with configurable
one-, two-, four-, or seven-bit quantization. HNSW fields add
`flat_index_threshold`, and search adds an embedding query-vector builder.

New indices also exclude vectors from `_source` by default. Source retrieval
can explicitly include or exclude vectors; reindex always carries vectors
despite transparent removal. HNSW kNN profiling includes early-termination
information.

## Vector statistics and scripting

Node and index stats expose dense-vector off-heap usage from 9.1.0. Painless
`dotProduct` and `cosineSimilarity` can combine float query vectors with byte
vector fields. ES|QL adds dense-vector KNN, Hamming distance, magnitude,
arithmetic, comparisons, aggregation, and presence functions over subsequent
releases.

## Inference request shape and endpoint controls

### Task, chunking, and rerank options

In 9.1.0, EIS sparse-inference bodies rename `model_id` to `model`. Perform
Inference exposes root `input_type` for `text_embedding` and common rerank
options. Endpoints accept `none` to disable automatic chunking and add a
recursive chunker.

Adaptive allocation can scale to zero and defaults to 24 hours. New Cohere
endpoints use Cohere V2. Services can expose aliases. In 9.2.0, inference
requests gain a configurable query timeout, chunking settings lose their upper
limit, and partial search results are disabled. Invalid endpoints can be
force-deleted if their configuration is invalid or deployment shutdown fails.

In 9.3.0, the API adds an embedding task. EIS dense and sparse services accept
`max_batch_size`; unified responses report cached tokens, and Jina AI supports
late chunking. EIS completion is available and requires a basic license.

### Provider and service additions

The 9.0.0 Inference API adds unified chat completions, more embedding and
reranking backends, node-local rate limiting, and mTLS for the hosted inference
service. Service paths acquire a version prefix, and the sparse-embedding route
changes.

Provider expansion in 9.1.0 includes a custom service; Vertex AI chat and
completion; Mistral and Hugging Face chat completion; DeepSeek; VoyageAI
embedding and rerank; and SageMaker OpenAI-compatible chat and embedding.
Cohere adds binary embeddings, Jina AI accepts an embedding type, and Bedrock
Cohere accepts task settings.

In 9.2.0, additions include ContextualAI reranking; AI21, Google Model Garden
Anthropic, Llama, and IBM watsonx completion/chat; and Azure AI reranking.
Vertex AI embeddings accept dimensions, OpenAI embedding and chat requests
accept custom headers, and Gemini accepts a thinking budget.

In 9.3.0, provider coverage adds Azure OpenAI and Groq chat completion, NVIDIA,
OpenShift AI, and Google Model Garden integrations for Meta, Mistral, Hugging
Face, and AI21. EIS adds completion.

In 9.4.0, additions include Fireworks AI chat and embedding, Amazon Bedrock
chat, Jina AI and EIS embedding tasks, and Azure OpenAI custom headers and
OAuth2. Chat-completion integrations accept multimodal input and reasoning.

### Input and error compatibility

In 9.4.0, reasoning chat requests no longer accept `max_tokens`. Base64
embedding input must be a data URI. SageMaker `ElasticTextEmbeddingPayload`
requires `similarity`. Inference timeout responses use HTTP 504. Requests in
9.3.8 and 9.4.4 cannot override `secret_parameters`.

## Sparse storage and source behavior

`sparse_vector` values can be stored outside `_source` from 9.0.0.
Synthetic-source indices also have an index setting that skips recovery source.
Sparse token pruning is generally available in 8.19.0. Empty semantic content
does not trigger embedding generation.
