# Indexing and Storage

## Cast arrays to sparse vectors

PostgreSQL arrays can be cast directly to `sparsevec`.

```sql
SELECT ARRAY[1, 0, 2]::sparsevec;
```

Since 0.8.6, an array-to-`sparsevec` cast enforces the type's nonzero-element
limit. Oversized arrays can no longer bypass the constraint through a cast.
Validate or reduce sparse inputs before casting them.

## Keep storage and HNSW limits separate

A stored `sparsevec` value may contain as many as 16,000 nonzero elements. An
HNSW index supports no more than 1,000 nonzero elements, so a valid stored
value may still be unindexable.

HNSW supports sparse operator classes such as `sparsevec_l2_ops`:

```sql
CREATE INDEX ON items USING hnsw (embedding sparsevec_l2_ops);
```

Use the operator class that matches the query's distance operation. IVFFlat
does not support `sparsevec`.

## Account for values omitted from approximate indexes

HNSW and IVFFlat do not index `NULL` vectors. Their cosine-distance indexes
also omit zero vectors.

These omissions can make a nearest-neighbor query return fewer rows after an
approximate index is added, even when the query's scan-depth settings are high
enough. Inspect the column values and operator class before increasing scan
limits.

## Upgrade before IVFFlat builds on 32-bit systems

pgvector 0.8.6 fixes a buffer overflow during IVFFlat index builds on 32-bit
systems. Upgrade before creating, reindexing, or otherwise rebuilding an
IVFFlat index on a 32-bit deployment.

This fix concerns the build path. Query-time probe or iterative-scan settings
do not make an affected build safe.

## Reindex HNSW before vacuuming

Vacuuming a table with an HNSW index can be slow. Reindex the HNSW index
concurrently first, and then vacuum the table.

```sql
REINDEX INDEX CONCURRENTLY index_name;
VACUUM table_name;
```

Run the commands separately and replace the placeholders with the actual index
and table names. The concurrent reindex reduces blocking compared with a plain
reindex, but it still consumes build resources; plan memory and worker limits
for the deployment.

For container shared-memory sizing and hosted compute controls, see
[deployment.md](deployment.md).
