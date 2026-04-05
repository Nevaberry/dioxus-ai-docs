---
name: pgvector-knowledge-patch
description: pgvector changes since training cutoff (latest: 0.8.2) — halfvec, sparsevec, bit indexing, binary quantization, iterative index scans, subvector extraction, L1 distance. Load before working with pgvector.
license: MIT
metadata:
  author: Nevaberry
  version: "0.8.2"
---

# pgvector 0.7+ Knowledge Patch

Claude's baseline knowledge covers pgvector through 0.6.x. This skill provides features from 0.7.0 (Apr 2024) onwards.

**Source**: pgvector GitHub at https://github.com/pgvector/pgvector

## Reference Files

- **[`references/vector-types-and-indexing.md`](references/vector-types-and-indexing.md)** — halfvec, sparsevec, bit indexing, binary quantization, expression indexes, subvector extraction
- **[`references/iterative-index-scans.md`](references/iterative-index-scans.md)** — iterative scan modes, overfiltering solutions, scan limits, CTE patterns

## Quick Reference: New Vector Types (0.7.0)

| Type | Description | Max Indexed | Format |
|------|-------------|-------------|--------|
| `halfvec(n)` | Half-precision (float16) vectors | 4,000 dims | Same as vector |
| `sparsevec(n)` | Sparse vectors | 1,000 non-zero | `'{1:val,3:val}/dims'` (1-indexed) |
| `bit(n)` indexing | Binary vector search | 64,000 dims | Standard bit type |

## Quick Reference: New Functions (0.7.0)

| Function | Purpose |
|----------|---------|
| `binary_quantize(vector)` | Convert vector to bit (positive -> 1, else -> 0) |
| `subvector(vector, start, length)` | Extract subvector (1-indexed) |
| `l2_normalize(vector)` | L2 normalize a vector |
| `vector \|\| vector` | Concatenate vectors |

## Quick Reference: New Operator Classes (0.7.0)

| Type | L2 | Inner Product | Cosine |
|------|----|----|--------|
| halfvec | `halfvec_l2_ops` | `halfvec_ip_ops` | `halfvec_cosine_ops` |
| sparsevec | `sparsevec_l2_ops` | `sparsevec_ip_ops` | `sparsevec_cosine_ops` |

| Type | Hamming (`<~>`) | Jaccard (`<%>`) |
|------|-----------------|-----------------|
| bit | `bit_hamming_ops` | `bit_jaccard_ops` |

HNSW now also supports L1 distance with `vector_l1_ops`.

## Quick Reference: Iterative Index Scans (0.8.0)

Solves the "overfiltering" problem — when `WHERE` clauses with approximate indexes return too few results.

```sql
-- Enable for HNSW (strict = exact distance order; relaxed = better recall)
SET hnsw.iterative_scan = strict_order;  -- or relaxed_order
SET hnsw.max_scan_tuples = 20000;        -- default; max tuples to visit

-- Enable for IVFFlat (relaxed_order ONLY — no strict_order support)
SET ivfflat.iterative_scan = relaxed_order;
SET ivfflat.max_probes = 100;            -- max probes for iterative scans
```

## Half-Precision Expression Index (0.7.0)

```sql
CREATE INDEX ON items USING hnsw ((embedding::halfvec(3)) halfvec_l2_ops);
SELECT * FROM items ORDER BY embedding::halfvec(3) <-> '[1,2,3]' LIMIT 5;
```

## Binary Quantization Expression Index (0.7.0)

```sql
CREATE INDEX ON items USING hnsw ((binary_quantize(embedding)::bit(3)) bit_hamming_ops);
-- Re-rank for better recall:
SELECT * FROM (
    SELECT * FROM items ORDER BY binary_quantize(embedding)::bit(3) <~> binary_quantize('[1,-2,3]') LIMIT 20
) ORDER BY embedding <=> '[1,-2,3]' LIMIT 5;
```

## Iterative Scan CTE Patterns (0.8.0)

**Materialized CTE for strict ordering with relaxed scans:**
```sql
WITH relaxed_results AS MATERIALIZED (
    SELECT id, embedding <-> '[1,2,3]' AS distance FROM items
    WHERE category_id = 123 ORDER BY distance LIMIT 5
) SELECT * FROM relaxed_results ORDER BY distance + 0;
```
Note: `+ 0` is needed for Postgres 17+ to force re-sorting.

**Distance filter pattern** (place distance filter outside CTE):
```sql
WITH nearest AS MATERIALIZED (
    SELECT id, embedding <-> '[1,2,3]' AS distance FROM items ORDER BY distance LIMIT 5
) SELECT * FROM nearest WHERE distance < 5 ORDER BY distance;
```

## Array to sparsevec Cast (0.8.0)

```sql
SELECT ARRAY[1,0,2,0,3]::sparsevec;  -- '{1:1,3:2,5:3}/5'
```
