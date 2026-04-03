# Vector Types and Indexing (0.7.0)

## halfvec — Half-Precision Vectors

`halfvec(n)` stores vectors in half-precision (float16) format. Can index up to 4,000 dimensions.

**Operator classes:** `halfvec_l2_ops`, `halfvec_ip_ops`, `halfvec_cosine_ops`

### Expression Index for Quantized Search

Cast full-precision vectors to halfvec in an expression index to halve storage while keeping full-precision source data:

```sql
-- Create expression index (casts vector to halfvec at index time)
CREATE INDEX ON items USING hnsw ((embedding::halfvec(3)) halfvec_l2_ops);

-- Query must match the expression exactly
SELECT * FROM items ORDER BY embedding::halfvec(3) <-> '[1,2,3]' LIMIT 5;
```

## sparsevec — Sparse Vectors

`sparsevec(n)` stores sparse vectors efficiently. Format: `'{index:value,...}/total_dims'` (1-indexed).

Can index up to 1,000 non-zero elements.

**Operator classes:** `sparsevec_l2_ops`, `sparsevec_ip_ops`, `sparsevec_cosine_ops`

```sql
-- Insert sparse vector (dimensions 1, 3, and 5 have values, total 5 dims)
INSERT INTO items (embedding) VALUES ('{1:0.5,3:0.7,5:0.2}/5');

-- Cast array to sparsevec (added in 0.8.0)
SELECT ARRAY[1,0,2,0,3]::sparsevec;  -- '{1:1,3:2,5:3}/5'
```

## bit Indexing — Binary Vector Search

Binary vectors (`bit(n)` type) can now be indexed for similarity search. Supports up to 64,000 dimensions.

**Distance operators:**
- `<~>` — Hamming distance
- `<%>` — Jaccard distance

**Operator classes:** `bit_hamming_ops`, `bit_jaccard_ops`

```sql
CREATE INDEX ON items USING hnsw (embedding bit_hamming_ops);
SELECT * FROM items ORDER BY embedding <~> B'101' LIMIT 5;
```

## binary_quantize — Vector to Bit Conversion

`binary_quantize(vector)` converts a vector to binary: positive values become 1, others become 0.

Use with expression indexes to build compact binary indexes over full-precision vectors:

```sql
-- Expression index using binary quantization
CREATE INDEX ON items USING hnsw ((binary_quantize(embedding)::bit(3)) bit_hamming_ops);

-- Two-phase search: binary quantize for fast candidate retrieval, then re-rank with original vectors
SELECT * FROM (
    SELECT * FROM items ORDER BY binary_quantize(embedding)::bit(3) <~> binary_quantize('[1,-2,3]') LIMIT 20
) ORDER BY embedding <=> '[1,-2,3]' LIMIT 5;
```

The re-ranking pattern is important for recall: binary quantization is lossy, so fetching more candidates and re-ranking with exact distances improves result quality.

## subvector — Dimensionality Reduction

`subvector(vector, start, length)` extracts a contiguous slice of a vector (1-indexed).

Use with expression indexes for dimensionality reduction:

```sql
-- Index only the first 3 dimensions
CREATE INDEX ON items USING hnsw ((subvector(embedding, 1, 3)::vector(3)) vector_l2_ops);

-- Query must match the expression
SELECT * FROM items ORDER BY subvector(embedding, 1, 3)::vector(3) <-> subvector('[1,2,3,4,5]', 1, 3)::vector(3) LIMIT 5;
```

## l2_normalize

`l2_normalize(vector)` returns the L2-normalized (unit length) version of a vector.

## Vector Concatenation

The `||` operator concatenates two vectors:

```sql
SELECT '[1,2]'::vector || '[3,4]'::vector;  -- [1,2,3,4]
```

## L1 Distance for HNSW

HNSW now supports L1 (Manhattan) distance with the `vector_l1_ops` operator class:

```sql
CREATE INDEX ON items USING hnsw (embedding vector_l1_ops);
SELECT * FROM items ORDER BY embedding <+> '[1,2,3]' LIMIT 5;
```
