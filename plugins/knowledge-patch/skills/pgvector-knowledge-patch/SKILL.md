---
name: pgvector-knowledge-patch
description: pgvector 0.8.5 compatibility. Use for pgvector work.
license: MIT
version: "0.8.5"
metadata:
  author: Nevaberry
---

# pgvector Knowledge Patch

Baseline: pgvector through 0.7.4, covering `vector`, `halfvec`, `sparsevec`, and `bit`; IVFFlat and HNSW; standard distance operators; and basic index tuning. This patch covers the 0.8-guide and 0.8.0 additions plus the current reference and hosted-deployment guidance through pgvector 0.8.5.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/iterative-scans.md](references/iterative-scans.md) | Filtered HNSW and IVFFlat searches, scan modes and limits, result ordering, planner costing |
| [references/indexing-and-storage.md](references/indexing-and-storage.md) | Type and index limits, sparse vectors, quantization, expression and partial indexes, omissions, maintenance |
| [references/deployment.md](references/deployment.md) | PostgreSQL compatibility, source and container builds, portability, hosted version windows, build resources |

## Breaking compatibility change

### PostgreSQL 12 is no longer supported

pgvector 0.8 requires PostgreSQL 13 or newer. Upgrade the database server before
adopting the 0.8 line. Current source-build instructions pin pgvector 0.8.5,
and published containers cover PostgreSQL 13 through 18.

```sh
docker pull pgvector/pgvector:0.8.5-pg18-trixie
```

See [references/deployment.md](references/deployment.md) for container variants,
portable compilation, and hosted-platform constraints.

## Iterative scans for filtered nearest-neighbor queries

Approximate indexes retrieve candidates before PostgreSQL applies ordinary
filters. A selective `WHERE` clause can therefore leave fewer rows than the
requested `LIMIT`. Iterative scans continue looking for candidates until they
find enough matches or reach their scan limits.

### HNSW

HNSW iterative scanning is off by default. Choose one of two modes:

| Setting | Behavior |
| --- | --- |
| `strict_order` | Preserves exact distance order |
| `relaxed_order` | Allows looser ordering for better search performance |

```sql
SET hnsw.iterative_scan = 'strict_order';

SELECT id, embedding <=> '[1,2,3]' AS distance
FROM items
WHERE category = 1
ORDER BY embedding <=> '[1,2,3]'
LIMIT 20;
```

Keep the distance `ORDER BY` immediately before `LIMIT` so the planner can use
the iterative scan.

HNSW scan controls are:

| Setting | Default | Purpose |
| --- | ---: | --- |
| `hnsw.max_scan_tuples` | `20000` | Caps tuples visited |
| `hnsw.scan_mem_multiplier` | `1` | Caps scan memory as a multiple of `work_mem` |

Raise one or both when a selective filter still prevents the scan from filling
the limit.

```sql
SET hnsw.max_scan_tuples = 40000;
SET hnsw.scan_mem_multiplier = 2;
```

### IVFFlat

IVFFlat also supports iterative scans. Enable `ivfflat.iterative_scan`; the scan
continues after an initial filtered result shortage until it finds enough rows
or reaches `ivfflat.max_probes`.

### Restore exact order after a relaxed scan

Limit candidates inside a subquery, then sort them again. Use an expression
such as `distance * 1` to force PostgreSQL to perform the final sort.

```sql
SELECT * FROM (
  SELECT id, embedding <=> '[1,2,3]' AS distance
  FROM items
  WHERE category = 1
  ORDER BY embedding <=> '[1,2,3]'
  LIMIT 20
) AS candidates
ORDER BY distance * 1;
```

Do not assume a filtered query uses the vector index. Improved vector-operation
costing can correctly favor a sequential scan or a conventional index. Inspect
the actual choice with `EXPLAIN`.

## Current type and index limits

Storage capacity and approximate-index capacity are different:

| Type | Storage maximum | HNSW maximum | IVFFlat support |
| --- | ---: | ---: | --- |
| `vector` | 16,000 dimensions | 2,000 dimensions | Yes, up to 2,000 dimensions |
| `halfvec` | 16,000 dimensions | 4,000 dimensions | Yes, up to 4,000 dimensions |
| `bit` | 64,000 bits | 64,000 bits | Yes, up to 64,000 bits |
| `sparsevec` | 16,000 nonzero elements | 1,000 nonzero elements | No |

HNSW additionally supports sparse vectors, L1 distance, and Jaccard distance.
All approximate indexes omit `NULL` embeddings; cosine indexes also omit zero
vectors. Account for these omissions when result counts are unexpectedly low.

## Re-rank lossy or narrowed candidate searches

### Binary quantization

A binary-quantized HNSW index is smaller, but Hamming distance should select
candidates rather than produce the final ranking. Retrieve more candidates than
the final limit, then re-rank with the original vectors.

```sql
CREATE INDEX ON items USING hnsw
  ((binary_quantize(embedding)::bit(3)) bit_hamming_ops);

SELECT * FROM (
  SELECT * FROM items
  ORDER BY binary_quantize(embedding)::bit(3)
    <~> binary_quantize('[1,-2,3]')
  LIMIT 20
) AS candidates
ORDER BY embedding <=> '[1,-2,3]'
LIMIT 5;
```

### Subvectors

Use an expression index to search a cast subvector, request a wider candidate
set, and re-rank by the full embedding. The query expression, cast, and operator
class must exactly match the indexed expression.

```sql
CREATE INDEX ON items USING hnsw
  ((subvector(embedding, 1, 3)::vector(3)) vector_cosine_ops);
```

## Index mixed dimensions safely

An unconstrained `vector` column can store mixed dimensions, but each index must
target one dimension. Use a partial expression index and repeat both its cast
and predicate in the nearest-neighbor query.

```sql
CREATE INDEX ON embeddings USING hnsw
  ((embedding::vector(3)) vector_l2_ops)
  WHERE model_id = 123;

SELECT * FROM embeddings
WHERE model_id = 123
ORDER BY embedding::vector(3) <-> '[3,1,2]'
LIMIT 5;
```

## Sparse vectors

Sparse literals use `{index:value,...}/dimensions` and one-based indexes.
PostgreSQL arrays can be cast directly to `sparsevec`. HNSW indexes use the
matching `sparsevec_*_ops` operator class.

```sql
INSERT INTO items (embedding) VALUES ('{1:1,3:2,5:3}/5');
CREATE INDEX ON items USING hnsw (embedding sparsevec_cosine_ops);
```

## Build and maintenance essentials

- For a build artifact that will run on another machine, clear `OPTFLAGS` to
  avoid `-march=native` illegal-instruction failures: `make OPTFLAGS=""`.
- For parallel HNSW builds in a container, set container shared memory to at
  least `maintenance_work_mem`, for example `docker run --shm-size=1g ...`.
- HNSW vacuuming can be slow. Run `REINDEX INDEX CONCURRENTLY index_name;`
  before `VACUUM table_name;`.
- On hosted compute, size `maintenance_work_mem` to the vector-index working set
  without exceeding roughly 50–60% of RAM, and tune parallel maintenance
  workers within the server's global worker limits.

Consult the indexed references before changing index definitions, filtered
query shape, build resources, extension versions, or deployment targets.
