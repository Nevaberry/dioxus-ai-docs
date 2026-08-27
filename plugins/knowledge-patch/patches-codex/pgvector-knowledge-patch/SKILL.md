---
name: pgvector-knowledge-patch
description: pgvector
version: "0.8.5"
license: MIT
metadata:
  author: Nevaberry
---


# pgvector Knowledge Patch

Use this skill when changing pgvector queries, approximate indexes, extension
builds, or deployments. Start with the compatibility and correctness notes
below, then open the topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/iterative-scans.md](references/iterative-scans.md) | Filtered HNSW and IVFFlat searches, scan modes and limits, exact reordering, planner choices |
| [references/indexing-and-storage.md](references/indexing-and-storage.md) | Sparse-vector limits, array casts, index omissions, 32-bit IVFFlat safety, HNSW maintenance |
| [references/deployment.md](references/deployment.md) | PostgreSQL compatibility, release artifacts, portable builds, container memory, Windows, hosted deployments |

## Breaking compatibility change

### PostgreSQL 12 is unsupported

Do not adopt the pgvector 0.8 release line on PostgreSQL 12. Upgrade the
database server to PostgreSQL 13 or newer first.

This affects extension upgrades as well as new installations: verify the
server version before changing the installed extension package or running
`ALTER EXTENSION vector UPDATE`.

See [references/deployment.md](references/deployment.md) for supported artifact
and platform combinations.

## Apply the 32-bit IVFFlat fix before building

pgvector 0.8.6 fixes a buffer overflow in IVFFlat index builds on 32-bit
systems. Upgrade before creating or rebuilding an IVFFlat index on such a
system.

Treat this as a build-safety requirement, not a query-tuning change. Existing
scan settings do not mitigate the faulty build path.

See
[references/indexing-and-storage.md](references/indexing-and-storage.md) for
the related array-to-`sparsevec` enforcement change.

## Use iterative scans for selective filters

Approximate indexes gather candidates before PostgreSQL applies ordinary
filters. A selective `WHERE` clause can therefore leave fewer rows than the
query's `LIMIT`. Iterative scans continue through the index until enough
matching rows are found or a scan limit is reached.

### HNSW modes

HNSW iterative scanning is off by default. Select a mode for the session:

| Setting | Behavior |
| --- | --- |
| `off` | Use the initial approximate scan only |
| `strict_order` | Continue scanning while preserving exact distance order |
| `relaxed_order` | Continue scanning with looser ordering for faster scans |

```sql
SET hnsw.iterative_scan = 'strict_order';

SELECT id, embedding <=> '[1,2,3]' AS distance
FROM items
WHERE category = 1
ORDER BY embedding <=> '[1,2,3]'
LIMIT 20;
```

Keep the distance `ORDER BY` immediately before `LIMIT`; iterative scanning
depends on this query shape.

If filtering still prevents the query from filling its limit, tune these
controls:

| Setting | Default | Effect |
| --- | ---: | --- |
| `hnsw.max_scan_tuples` | `20000` | Maximum tuples visited by an iterative scan |
| `hnsw.scan_mem_multiplier` | `1` | Scan-memory cap as a multiple of `work_mem` |

### IVFFlat mode

Enable `ivfflat.iterative_scan` when an initial filtered IVFFlat scan returns
too few rows. The scan continues until it fills the result limit or reaches
`ivfflat.max_probes`.

### Re-sort relaxed HNSW results

When final ordering must be exact, retrieve a wider candidate set in a
subquery and sort it again. An expression such as `distance * 1` forces the
outer sort.

```sql
SELECT *
FROM (
  SELECT id, embedding <=> '[1,2,3]' AS distance
  FROM items
  WHERE category = 1
  ORDER BY embedding <=> '[1,2,3]'
  LIMIT 20
) AS candidates
ORDER BY distance * 1;
```

See [references/iterative-scans.md](references/iterative-scans.md) for the full
filtered-search workflow and planner checks.

## Verify the chosen query plan

Filtered-search costing can make a sequential scan or a conventional index
cheaper than HNSW. Do not infer index use merely from the presence of a vector
index. Run `EXPLAIN` on the real query shape and inspect the chosen plan.

Before increasing iterative-scan limits, distinguish a planner choice from an
approximate scan that stopped too early.

## Respect sparse-vector limits

PostgreSQL arrays can be cast directly to `sparsevec`:

```sql
SELECT ARRAY[1, 0, 2]::sparsevec;
```

Current casts enforce the sparse type's nonzero-element limit. Code that once
used an oversized array cast to bypass that constraint must instead reduce or
partition the data.

Stored sparse vectors can contain up to 16,000 nonzero elements, while an HNSW
index supports at most 1,000. IVFFlat does not support `sparsevec`.

```sql
CREATE INDEX ON items USING hnsw (embedding sparsevec_l2_ops);
```

Choose a matching sparse operator class and validate the indexed values
against the lower HNSW limit.

## Account for approximate-index omissions

HNSW and IVFFlat omit `NULL` vectors. Cosine-distance variants also omit zero
vectors. These exclusions can reduce result counts even when iterative-scan
depth is sufficient.

Check the stored values and operator class before treating a short result set
as a scan-limit problem.

## Build portable extension artifacts

Some platforms compile with `-march=native`. A binary moved to a different
processor can then fail with `Illegal instruction`. Clear the optimization
flags for a portable build:

```shell
make OPTFLAGS=""
```

When a parallel HNSW build uses increased `maintenance_work_mem` inside
Docker, give the container at least the same amount of shared memory:

```shell
docker run --shm-size=1g ...
```

See [references/deployment.md](references/deployment.md) before selecting a
source tag, container tag, package-manager formula, or Windows toolchain.

## Size hosted index builds deliberately

For Neon index builds, set session `maintenance_work_mem` near the vector
index's working-set size without exceeding roughly 50–60% of available RAM.
The default `max_parallel_maintenance_workers` is `2`; raise it toward the
compute's CPU count only within `max_parallel_workers` and
`max_worker_processes`.

```sql
SET maintenance_work_mem = '10 GB';
SET max_parallel_maintenance_workers = 7;
```

Confirm the available compute resources before applying these example values.

## Maintain HNSW indexes before vacuuming

Vacuuming a table with an HNSW index can be slow. Reindex the HNSW index
concurrently before vacuuming the table:

```sql
REINDEX INDEX CONCURRENTLY index_name;
VACUUM table_name;
```

See
[references/indexing-and-storage.md](references/indexing-and-storage.md) for
the maintenance sequence and indexing constraints.
