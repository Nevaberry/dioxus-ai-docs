# Indexing, Storage, and Quantization

## Incremental HNSW indexing

Qdrant can extend an existing HNSW graph as new points arrive rather than
rebuilding the entire graph (since 1.14.0). The incremental path initially
applies only to upserts. Deletes and updates still trigger a full rebuild, so
do not estimate indexing cost from insert-only workloads alone.

## HNSW vector placement

Set collection HNSW `inline_storage` to `true` to store vector data in HNSW
nodes and reduce random disk reads (since 1.16.0):

```json
{
  "hnsw_config": {
    "inline_storage": true
  }
}
```

Quantization must also be enabled. Inline storage consumes additional storage
but can perform implicit rescoring from the original vector kept with each
node.

Individual payload field indexes can be excluded from HNSW participation (since
1.17.0). Exclude fields that are not used with dense-vector queries to avoid
unnecessary graph edges.

## Low-bit binary quantization

Binary storage gained 1.5-bit and 2-bit modes (since 1.15.0). Compared with
32-bit vectors, the modes provide approximately:

| Mode | Compression | Tradeoff |
| --- | ---: | --- |
| 1 bit | 32× | Maximum compression |
| 1.5 bit | 24× | Intermediate compression and accuracy |
| 2 bit | 16× | Represents zero explicitly and can preserve more accuracy |

The 2-bit mode can be especially useful for vectors below roughly 1,000
dimensions.

## Asymmetric quantization

Stored and query vectors can use different quantization algorithms (since
1.15.0), notably binary storage with scalar-quantized queries. This keeps disk
and RAM use near binary quantization while improving precision and reducing the
need for rescoring.

## TurboQuant

TurboQuant rotates vectors before compression, avoiding the centered-vector
distribution expected by binary quantization (since 1.18.0). It supports
cosine, dot-product, and L2 distance. Relative to scalar quantization it offers
twice the compression with similar recall and speed; at binary-equivalent
storage sizes it favors recall over speed.

The 4-bit TurboQuant representation can be used as the primary vector-storage
datatype (since 1.19.0). A deployment can store only quantized vectors instead
of retaining originals, reducing disk use at the cost of not having those
original vectors available.

## Component memory policy

Collection components share a `"memory"` setting with `"cold"`, `"cached"`,
and `"pinned"` modes (since 1.19.0). Select memory behavior separately for each
component instead of assuming one collection-wide placement strategy.

## Immutable-segment mmap default

Single-file mmap vector storage is enabled by default for immutable segments
(since 1.19.0). Capacity plans and benchmarks should account for the new
default instead of assuming the earlier vector-storage behavior.

## GPU index construction

Vulkan-capable GPUs can build HNSW indexes using preconfigured on-premises
container images (since 1.13.0). Multiple GPUs can index segments concurrently,
and GPU construction supports all Qdrant quantization options and data types.
Confirm detection and actual use in Qdrant logs.
