# Iterative Scans and Filtered Search

## Why filtering can shorten approximate results

HNSW and IVFFlat retrieve approximate candidates before PostgreSQL evaluates
ordinary filters. A selective `WHERE` clause can remove enough candidates that
the query returns fewer rows than `LIMIT`, even when more matching rows exist.

Iterative scans continue searching the approximate index until the query finds
enough filtered matches or reaches the applicable scan limit.

## Configure HNSW iterative scans

The iterative HNSW behavior introduced in the 0.8-guide is opt-in;
`hnsw.iterative_scan` defaults to `off`.

Choose one of the active modes:

| Mode | Ordering | Typical use |
| --- | --- | --- |
| `strict_order` | Exact distance order | Correct final ranking is required directly from the scan |
| `relaxed_order` | Approximate order | Faster scanning is worth a later re-sort when needed |

```sql
SET hnsw.iterative_scan = 'strict_order';

SELECT id, embedding <=> '[1,2,3]' AS distance
FROM filtest
WHERE category = 1
ORDER BY embedding <=> '[1,2,3]'
LIMIT 3;
```

Place the distance `ORDER BY` immediately before `LIMIT`. This query shape is
required for the iterative scan.

## Tune HNSW scan limits

Two settings bound an iterative HNSW scan:

| Setting | Default | Meaning |
| --- | ---: | --- |
| `hnsw.max_scan_tuples` | `20000` | Maximum number of tuples the scan visits |
| `hnsw.scan_mem_multiplier` | `1` | Scan-memory limit as a multiple of `work_mem` |

Raise one or both only when a selective filter still prevents the query from
filling its limit. Larger values increase work, and a larger multiplier raises
the scan's memory allowance.

```sql
SET hnsw.max_scan_tuples = 40000;
SET hnsw.scan_mem_multiplier = 2;
```

## Restore exact order after a relaxed scan

`relaxed_order` can return candidates outside exact distance order. Limit a
wider candidate set inside a subquery and then sort those candidates again.
Using an expression such as `distance * 1` forces PostgreSQL to perform the
outer sort.

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

Choose the inner limit large enough to provide a useful candidate pool. Apply
the exact final limit after the outer ordering when the caller needs fewer
rows than the candidate count.

## Configure IVFFlat iterative scans

IVFFlat iterative scanning is available since 0.8.0. Enable it with
`ivfflat.iterative_scan` when post-scan filtering leaves too few results.

The index continues searching after the initial scan until it finds enough
matching rows or reaches `ivfflat.max_probes`. If the result remains short,
check that ceiling before changing unrelated query settings.

## Inspect planner choices

The filter-aware vector-operation costing in the 0.8-guide can make PostgreSQL
correctly prefer a sequential scan or a conventional index over HNSW. The
existence of a vector index does not guarantee that the planner will use it.

Run `EXPLAIN` against the actual filtered nearest-neighbor query. Separate
these cases before tuning:

- The planner selected a different access path because its estimated cost is
  lower.
- The planner selected the approximate index, but an iterative-scan limit
  stopped candidate retrieval before enough filtered rows were found.
- The approximate index omitted values that the query expected to see, such
  as `NULL` vectors or zero vectors in a cosine-distance index.

The last case is an indexing constraint, not an iterative-scan limit; see
[indexing-and-storage.md](indexing-and-storage.md).
