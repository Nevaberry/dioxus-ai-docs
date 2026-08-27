# Vector Search and Ranking

Use this reference for vector storage, HNSW indexing, quantization, Query API
composition, ranking, sparse relevance, filtering, and compatibility-sensitive
result behavior.

## HNSW construction and storage

### Vulkan GPU HNSW indexing (since 1.13.0)

Qdrant can build HNSW indexes on modern Vulkan-capable GPUs from major hardware
vendors. It supports concurrent segment indexing across multiple GPUs and all
Qdrant quantization choices and data types.

For on-premises deployment, use a preconfigured GPU container image. Confirm
GPU detection and actual use in the logs; the presence of hardware alone does
not prove that indexing took the GPU path.

### Incremental HNSW indexing (since 1.14.0)

When new points are upserted, Qdrant can extend an existing HNSW graph rather
than rebuild the whole graph. The incremental path applies only to new-point
upserts in this implementation. Deletes and updates still trigger a full
rebuild, so size maintenance windows and optimizer load accordingly.

### Inline vector storage (since 1.16.0)

Set collection HNSW `inline_storage` to `true` to keep vector data in HNSW
nodes and reduce random disk reads. Quantization must also be enabled. The
layout consumes additional storage but can implicitly rescore from the original
vector stored with each node.

```json
{
  "hnsw_config": {
    "inline_storage": true
  }
}
```

Measure disk growth, cache behavior, and latency before enabling it on a large
collection.

### Per-field HNSW participation (since 1.17.0)

Configure individual payload field indexes not to be reflected in the HNSW
index when those fields are never used to filter dense-vector queries. This
avoids extra graph edges and their build and storage cost while retaining the
payload index for other access paths.

## Quantization

### 1.5-bit and 2-bit binary modes (since 1.15.0)

The binary storage modes provide these compression tradeoffs relative to
32-bit vectors:

| Mode | Approximate compression | Characteristic |
|---|---:|---|
| 1-bit | 32× | Maximum binary compression |
| 1.5-bit | 24× | Intermediate space/accuracy choice |
| 2-bit | 16× | Represents zero explicitly |

Two-bit quantization can preserve accuracy better for vectors below roughly
1,000 dimensions. Benchmark with the deployed embedding distribution rather
than selecting solely by dimension.

### Asymmetric quantization (since 1.15.0)

Stored vectors and query vectors may use different algorithms. A notable setup
stores binary vectors while scalar-quantizing queries. It keeps disk and RAM
near binary quantization while improving precision and reducing the need for
rescoring.

### TurboQuant (since 1.18.0)

TurboQuant rotates vectors before compression, so it does not require the
centered vector distribution expected by binary quantization. It supports
cosine, dot-product, and L2 distance.

Compared with scalar quantization, it offers about twice the compression with
similar recall and speed. At storage sizes comparable to binary quantization,
it favors recall over speed. Benchmark against the distance metric and latency
budget of the real workload.

### Four-bit TurboQuant as primary storage (since 1.19.0)

TurboQuant's 4-bit representation can be the primary vector-storage datatype.
Qdrant can retain only quantized vectors instead of originals, reducing disk
use. Because originals are absent, confirm that accuracy and any rescoring
workflow remain acceptable before making it primary storage.

## Formula scoring

### Rescore prefetched results (since 1.14.0)

The points Query API accepts a `formula` that combines `$score` with payload
conditions and numeric expressions. Conditions can contribute score inputs;
decay expressions can use datetime values or geographic distance. Supply
`defaults` for missing payload values when the expression requires them.

```http
POST /collections/{collection_name}/points/query
{
  "prefetch": {
    "query": [0.2, 0.8],
    "limit": 50
  },
  "query": {
    "formula": {
      "sum": [
        "$score",
        {
          "mult": [
            0.5,
            {"key": "tag", "match": {"any": ["h1", "h2"]}}
          ]
        }
      ]
    }
  }
}
```

Keep prefetch large enough to contain candidates that business boosting could
promote. Formula scoring cannot recover a candidate omitted from prefetch.

## Diversity, fusion, and feedback

### Maximal Marginal Relevance (since 1.15.0)

MMR reranks nearest-neighbor candidates to trade relevance for diversity.
`diversity` ranges from `0.0` for relevance to `1.0` for diversity.
`candidates_limit` controls the initial candidate pool.

```http
POST /collections/{collection_name}/points/query
{
  "query": {
    "nearest": [0.01, 0.45, 0.67, 0.12],
    "mmr": {
      "diversity": 0.5,
      "candidates_limit": 100
    }
  },
  "limit": 10
}
```

Tune diversity and candidate count together; a tiny pool limits how much the
reranker can diversify.

### Configurable RRF constant (since 1.16.0)

The `k` constant in Reciprocal Rank Fusion is configurable. It controls how
quickly contribution declines with rank. Validate the setting using relevance
judgments from all fused result sources.

### Relevance Feedback Query (since 1.17.0)

Provide context pairs with more- and less-relevant examples to refine vector
retrieval. Feedback changes similarity scoring across the vector space without
requiring a large separate rescoring pass or retraining the embedding model.
Use representative positive and negative examples; misleading context can
shift retrieval in the wrong direction.

### Weighted RRF (since 1.17.0)

Assign a weight to each query contributing to RRF. This prevents a weak ranker
from diluting stronger result sets through equal weighting. Calibrate weights
and `k` together against end-to-end metrics.

## Filtered and sparse retrieval

### Per-query ACORN (since 1.16.0)

ACORN improves HNSW recall when multiple low-selectivity filters remove direct
graph neighbors. It also explores neighbors of those neighbors. Enable it with
the optional query-time `acorn` parameter; no index-time change is required.

Reserve ACORN for affected filtered queries because the extra traversal adds
runtime overhead. Compare recall and latency with representative filters.

### Per-query IDF corpus (since 1.19.0)

Sparse-vector search can receive an IDF corpus with the individual query. Use
it when IDF-based relevance must be scoped to a query-specific corpus rather
than the collection's broader statistics. Keep the supplied corpus consistent
with the sparse vector construction used for that request.

### Slice filtering (since 1.19.0)

A slice filter condition supports sliced scrolling and deterministic sampling.
Use stable slice configuration when parallel workers must partition a scroll or
when a reproducible sample is required.

## Corrected query behavior

### Empty `min_should` (since 1.19.0)

An empty `min_should` with nonzero `min_count` no longer incorrectly matches
every point. Remove tests or application logic that used the old match-all bug;
construct an explicit match-all condition when that is the desired behavior.

### Scalar-quantized L2 scores (since 1.19.0)

Scalar-quantized L2 search no longer applies the erroneous score shift. Scores
can change after upgrade even when result identity is similar. Recalibrate
absolute score thresholds and compare rankings, not just raw score snapshots.

### Zero-limit batch result shape (since 1.19.0)

Batch queries with a limit of zero preserve the empty-result response shape.
Update serializers and fixtures that encoded the earlier inconsistent shape.

### Missing recommend point IDs (since 1.19.0)

Recommend operations through the Query API return an error when a referenced
point ID is missing. Validate IDs or handle this request error; do not assume a
missing positive or negative example will be silently ignored.

### Legacy search endpoints (since 1.19.0)

Deprecated search endpoints are removed from the OpenAPI specification and
marked deprecated in gRPC. Migrate retrieval implementations to the Query API.
Regenerate OpenAPI clients and remove dependencies on paths that no longer
appear in the specification.

## Retrieval validation checklist

- Confirm GPU HNSW use in logs and account for full rebuilds on delete/update.
- Compare quantization choices on recall, score stability, RAM, disk, and
  latency.
- Size formula prefetch and MMR candidates for the reranking opportunity.
- Calibrate RRF `k`, weights, and feedback examples with labeled queries.
- Enable ACORN only for filter shapes that benefit from it.
- Test sparse IDF inputs and slice partitioning for determinism.
- Revisit score thresholds, empty filters, zero limits, and missing IDs after
  upgrading.
- Generate clients from the current API specification and use Query API paths.
