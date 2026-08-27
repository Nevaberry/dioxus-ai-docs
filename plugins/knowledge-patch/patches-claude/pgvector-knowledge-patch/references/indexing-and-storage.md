# Indexing and Storage

This reference groups sparse-vector and index-maintenance guidance from
`0.8-guide`, `current-reference`, and `0.8.6`.

## Cast PostgreSQL arrays to sparse vectors

Arrays can be cast directly to `sparsevec`.

```sql
SELECT ARRAY[1, 0, 2]::sparsevec;
```

In pgvector 0.8.6, array-to-`sparsevec` casts enforce the type's nonzero-element
limit. Oversized casts no longer bypass the constraint.

## Index sparse vectors with HNSW

Stored `sparsevec` values can contain up to 16,000 nonzero elements. HNSW can
index `sparsevec` values with at most 1,000 nonzero elements, using an operator
class such as `sparsevec_l2_ops`.

```sql
CREATE INDEX ON items USING hnsw (embedding sparsevec_l2_ops);
```

IVFFlat does not support `sparsevec`. Because storage and HNSW have different
limits, a sparse vector can be valid in a column but too large for an HNSW
index.

## Allow for values omitted from approximate indexes

HNSW and IVFFlat exclude `NULL` vectors. Cosine-distance indexes built with
either method also exclude zero vectors.

When an approximate-index query returns fewer rows than expected, distinguish
these index omissions from insufficient scan depth. Raising scan limits cannot
make an omitted value part of the index.

## Maintain HNSW indexes before vacuuming

Vacuuming a table with an HNSW index can be slow. Rebuild the HNSW index
concurrently before vacuuming the table:

```sql
REINDEX INDEX CONCURRENTLY index_name;
VACUUM table_name;
```

## Protect IVFFlat builds on 32-bit systems

pgvector 0.8.6 fixes a buffer overflow during IVFFlat index builds on 32-bit
systems. Upgrade before building or rebuilding an IVFFlat index on such a
system.
