---
name: pgvector-knowledge-patch
description: pgvector
version: 0.8.5
license: MIT
metadata:
  author: Nevaberry
---


# pgvector Knowledge Patch

Use this skill when changing pgvector filtered nearest-neighbor queries,
approximate indexes, sparse vectors, extension builds, or hosted deployments.
Check the project PostgreSQL and pgvector versions before applying guidance that
names a specific release.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/iterative-scans.md](references/iterative-scans.md) | Filtered HNSW and IVFFlat searches, scan modes and limits, exact reordering, planner choices |
| [references/indexing-and-storage.md](references/indexing-and-storage.md) | Sparse-vector casts and indexes, approximate-index omissions, HNSW maintenance, 32-bit IVFFlat builds |
| [references/deployment.md](references/deployment.md) | PostgreSQL compatibility, release artifacts, portable and container builds, Windows, Neon deployment |

## Compatibility checks

### PostgreSQL 12 is unsupported on the 0.8 line

pgvector 0.8 no longer supports PostgreSQL 12. Upgrade PostgreSQL before
adopting a pgvector 0.8 release.

### Upgrade PostgreSQL 17 before building on Windows

PostgreSQL 17.0 through 17.2 can produce an unresolved
`float_to_shortest_decimal_bufn` symbol when building pgvector on Windows.
Upgrade to PostgreSQL 17.3 or newer first.

### Upgrade pgvector before IVFFlat builds on 32-bit systems

pgvector 0.8.6 fixes a buffer overflow in IVFFlat index builds on 32-bit
systems. Upgrade before building or rebuilding an IVFFlat index there.

## Filtered nearest-neighbor searches

Approximate indexes retrieve candidates before PostgreSQL applies ordinary
filters. A selective `WHERE` clause can therefore leave fewer rows than the
query's `LIMIT`. Iterative scans continue through the index until enough
matching rows are found or a scan limit is reached.

### HNSW iterative scans

HNSW iterative scanning defaults to `off`. Select the ordering behavior that
fits the query:

| `hnsw.iterative_scan` value | Behavior |
| --- | --- |
| `strict_order` | Preserve exact distance order |
| `relaxed_order` | Permit approximate ordering for faster scans |

```sql
SET hnsw.iterative_scan = 'strict_order';

SELECT id, embedding <=> '[1,2,3]' AS distance
FROM filtest
WHERE category = 1
ORDER BY embedding <=> '[1,2,3]'
LIMIT 3;
```

Keep the distance `ORDER BY` immediately before `LIMIT`; iterative scanning
depends on this query shape.

Two settings bound an HNSW iterative scan:

| Setting | Default | Purpose |
| --- | ---: | --- |
| `hnsw.max_scan_tuples` | `20000` | Limit tuples visited |
| `hnsw.scan_mem_multiplier` | `1` | Limit scan memory as a multiple of `work_mem` |

Increase these controls if a selective filter still prevents the query from
filling its limit.

### Restore exact order after a relaxed scan

Limit the approximate candidates in a subquery, then sort them again. An
expression such as `distance * 1` forces PostgreSQL to perform the final sort.

```sql
SELECT *
FROM (
  SELECT id, embedding <=> '[1,2,3]' AS distance
  FROM filtest
  WHERE category = 1
  ORDER BY embedding <=> '[1,2,3]'
  LIMIT 20
) AS candidates
ORDER BY distance * 1;
```

### IVFFlat iterative scans

Enable IVFFlat iterative scanning with `ivfflat.iterative_scan`. If filtering
leaves too few rows after the initial scan, pgvector continues searching until
it finds enough matches or reaches `ivfflat.max_probes`.

### Verify planner choices

Vector-operation cost estimates account for filtered searches. PostgreSQL may
correctly choose a sequential scan or a conventional index instead of HNSW.
Use `EXPLAIN` rather than assuming that a vector index was selected.

## Sparse vectors and approximate indexes

### Cast arrays to `sparsevec`

PostgreSQL arrays can be cast directly to `sparsevec`:

```sql
SELECT ARRAY[1, 0, 2]::sparsevec;
```

As of pgvector 0.8.6, the cast enforces the type's nonzero-element limit;
oversized array casts cannot bypass that constraint.

### Respect sparse storage and HNSW limits

A stored `sparsevec` may contain up to 16,000 nonzero elements. HNSW supports
only up to 1,000 nonzero elements and uses sparse operator classes such as
`sparsevec_l2_ops`. IVFFlat does not support `sparsevec`.

```sql
CREATE INDEX ON items USING hnsw (embedding sparsevec_l2_ops);
```

A value that is valid to store may therefore still be too large to index with
HNSW.

### Account for omitted values

HNSW and IVFFlat omit `NULL` vectors. Their cosine-distance indexes also omit
zero vectors. These omissions can reduce result counts even when scan-depth
settings are sufficient.

## Build and maintenance quick reference

### Reindex HNSW before vacuuming

Vacuuming a table with an HNSW index can be slow. Reindex the HNSW index
concurrently first, then vacuum the table.

```sql
REINDEX INDEX CONCURRENTLY index_name;
VACUUM table_name;
```

### Build portable artifacts without native CPU flags

Some platforms compile with `-march=native`. Moving that extension to a
different processor can then cause an `Illegal instruction` failure. Clear the
optimization flags for portable artifacts:

```shell
make OPTFLAGS=""
```

### Match Docker shared memory to maintenance memory

When raising `maintenance_work_mem` for a parallel HNSW build in Docker, set
the container's `--shm-size` to at least the same size or the build can fail.

```shell
docker run --shm-size=1g ...
```

## Distribution and hosted deployment

Source-build instructions pin pgvector 0.8.5. Versioned Docker tags cover
PostgreSQL 13 through 18 on Bookworm and Trixie. Homebrew installs the extension
only for its `postgresql@17` and `postgresql@18` formulas.

```shell
docker pull pgvector/pgvector:0.8.5-pg18-trixie
```

Neon supplies its latest supported pgvector release and the immediately
previous published release. Identify the actual previous release instead of
decrementing a version number, since pgvector releases are not always
sequential, and request that version explicitly when needed.

Before building HNSW or IVFFlat on Neon, set `maintenance_work_mem` for the
session to approximately the vector-index working-set size without exceeding
50–60% of available RAM. `max_parallel_maintenance_workers` defaults to `2`;
it can be raised toward the compute CPU count subject to `max_parallel_workers`
and `max_worker_processes`.

```sql
SET maintenance_work_mem = '10 GB';
SET max_parallel_maintenance_workers = 7;
```

See [references/deployment.md](references/deployment.md) before selecting an
artifact, build environment, or hosted extension version.
