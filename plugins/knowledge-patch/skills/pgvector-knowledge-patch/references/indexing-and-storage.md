# Indexing and Storage

## Storage limits versus approximate-index limits

The base types accept more data than some approximate indexes can index:

| Type | Storage maximum | HNSW | IVFFlat |
| --- | ---: | --- | --- |
| `vector` | 16,000 dimensions | Up to 2,000 dimensions | Supported, up to 2,000 dimensions |
| `halfvec` | 16,000 dimensions | Up to 4,000 dimensions | Supported, up to 4,000 dimensions |
| `bit` | 64,000 bits | Up to 64,000 bits | Supported, up to 64,000 bits |
| `sparsevec` | 16,000 nonzero elements | Up to 1,000 nonzero elements | Not supported |

HNSW also supports sparse vectors, L1 distance, and Jaccard distance.

## Rows omitted from approximate indexes

All approximate indexes omit `NULL` embeddings. Cosine indexes additionally
omit zero vectors. These omissions can lower result counts independently of
filters, iterative-scan limits, or probe settings.

## Sparse vectors

### Literals and indexes

A `sparsevec(n)` literal has the form `{index:value,...}/dimensions`. Indices
are one-based, consistent with PostgreSQL arrays.

```sql
INSERT INTO items (embedding) VALUES ('{1:1,3:2,5:3}/5');
CREATE INDEX ON items USING hnsw (embedding sparsevec_cosine_ops);
```

Choose the corresponding `sparsevec_*_ops` operator class for the distance
metric. PostgreSQL arrays can be cast directly to `sparsevec` (since the 0.8
line), so array-valued inputs do not need an intermediate literal.

## Binary-quantized HNSW indexes

Binary quantization reduces HNSW index size, but Hamming distance is lossy. Use
it to retrieve a larger candidate set, then re-rank those candidates with the
original embeddings to preserve recall.

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

## Subvector expression indexes

Index a cast `subvector` expression to narrow the first-stage search. Retrieve a
wider candidate set, then re-rank it using the complete embedding. The indexed
expression, dimension cast, and operator class must match the query expression.

```sql
CREATE INDEX ON items USING hnsw
  ((subvector(embedding, 1, 3)::vector(3)) vector_cosine_ops);
```

## Mixed dimensions in one column

An unconstrained `vector` column can contain embeddings with different
dimensions. Each approximate index, however, must target rows of one dimension.
Use a partial expression index and repeat both its predicate and cast in every
nearest-neighbor query that should use it.

```sql
CREATE INDEX ON embeddings USING hnsw
  ((embedding::vector(3)) vector_l2_ops)
  WHERE model_id = 123;

SELECT * FROM embeddings
WHERE model_id = 123
ORDER BY embedding::vector(3) <-> '[3,1,2]'
LIMIT 5;
```

## Preserve higher precision while indexing

When stored values must retain more precision than the index type, keep them in
`double precision[]` or `numeric[]`. Optionally constrain the dimension that
must be convertible, then build a lower-precision expression index for search.

```sql
ALTER TABLE items
  ADD CHECK (vector_dims(embedding::vector) = 3);

CREATE INDEX ON items USING hnsw
  ((embedding::vector(3)) vector_l2_ops);
```

## HNSW vacuum maintenance

Vacuuming a table with an HNSW index can be slow. Reindex the HNSW index
concurrently before vacuuming the table.

```sql
REINDEX INDEX CONCURRENTLY index_name;
VACUUM table_name;
```
