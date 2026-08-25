# Retrieval, Ranking, and Filtering

## Formula-based score boosting

The points Query API can rescore prefetched vector results with a `formula`
that combines `$score` with payload conditions and numeric expressions (since
1.14.0). Conditions act as score inputs. Decay expressions can use datetime
payloads or geographic distance, and `defaults` can provide fallback payload
values.

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

## Maximal Marginal Relevance

MMR reranks points Query API results to trade relevance for diversity (since
1.15.0). `diversity` ranges from `0.0` for relevance to `1.0` for diversity;
`candidates_limit` controls the initial candidate pool.

```http
POST /collections/{collection_name}/points/query
{
  "query": {
    "nearest": [0.01, 0.45, 0.67, 0.12],
    "mmr": {"diversity": 0.5, "candidates_limit": 100}
  },
  "limit": 10
}
```

## ACORN filtered search

ACORN improves HNSW result quality when several low-selectivity filters remove
direct graph neighbors (since 1.16.0). It additionally explores neighbors of
those filtered neighbors. Enable it per query with the optional `acorn`
parameter; it needs no index-time change. Use it only on affected filtered
queries because it adds runtime overhead.

## Relevance Feedback Query

Relevance Feedback Query refines vector retrieval from context pairs containing
more- and less-relevant examples (since 1.17.0). It changes similarity scoring
across the vector space without a separate large rescoring pass or embedding
model retraining.

## Reciprocal Rank Fusion controls

The RRF `k` constant is configurable (since 1.16.0), allowing control over the
rank-decay curve when combining result sets.

Each contributing query can also receive a weight (since 1.17.0). Use weighted
RRF to keep a weak ranker from diluting stronger result sets through equal
weighting.

## Named-vector presence filter

`has_vector` selects points that contain a specified named vector (since
1.13.0). This supports heterogeneous multi-vector collections where points do
not all have the same embeddings.

```http
POST /collections/{collection_name}/points/scroll
{
  "filter": {
    "must": [
      {"has_vector": "image"}
    ]
  }
}
```

## Keyword prefix matching

Keyword filters support `"match": {"prefix": "..."}` (since 1.19.0).
Prefix support must be enabled on the keyword index before the condition can be
used.

## Per-query IDF corpora

Sparse-vector searches can provide an IDF corpus per query (since 1.19.0),
scoping IDF-based relevance to that individual search instead of relying only
on a broader corpus.

## Slice filtering

A slice condition supports sliced scrolling and deterministic sampling (since
1.19.0). Use it where repeatable partitioning or sampling is required.

## Corrected query edge cases

Several former behaviors were corrected in 1.19.0:

- An empty `min_should` with nonzero `min_count` no longer matches every point.
  Do not depend on the old match-all result.
- Scalar-quantized L2 search no longer applies an erroneous score shift. Expect
  affected result scores to change after an upgrade.
- Batch queries with a zero limit preserve the empty-result response shape.
- Recommend operations through the Query API return an error when a referenced
  point ID is missing.

## Search endpoint deprecation

Deprecated search endpoints are removed from the OpenAPI specification and are
marked deprecated in gRPC (since 1.19.0). Move generated clients and new
integrations to the points Query API.
