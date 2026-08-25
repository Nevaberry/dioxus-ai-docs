# Iterative Scans and Filtered Search

This reference organizes filtered-search guidance from `0.8-guide` and
`0.8.0` by query task.

## Why filters can leave a short result set

Approximate HNSW and IVFFlat indexes gather candidates before PostgreSQL
applies ordinary filters. If a filter is selective, too few candidates may
survive to satisfy `LIMIT`. Iterative scanning lets the index continue looking
until enough matching rows are found or its configured limit is reached.

## Configure HNSW iterative scans

HNSW iterative scanning is opt-in and defaults to `off`. Set
`hnsw.iterative_scan` to one of these modes:

| Mode | Ordering behavior |
| --- | --- |
| `strict_order` | Exact distance order |
| `relaxed_order` | Approximate order with faster scanning |

```sql
SET hnsw.iterative_scan = 'strict_order';

SELECT id, embedding <=> '[1,2,3]' AS distance
FROM filtest
WHERE category = 1
ORDER BY embedding <=> '[1,2,3]'
LIMIT 3;
```

The distance `ORDER BY` must appear immediately before `LIMIT` for iterative
scanning to apply.

## Tune HNSW scan limits

`hnsw.max_scan_tuples` defaults to `20000` and limits the tuples an iterative
scan visits. `hnsw.scan_mem_multiplier` defaults to `1` and limits scan memory
as a multiple of `work_mem`.

If a selective filter still leaves fewer rows than requested, increase the
tuple limit, the memory multiplier, or both.

## Re-establish exact order after `relaxed_order`

First bound the candidate set in a subquery. Then sort the candidates by a
derived expression such as `distance * 1`, which forces PostgreSQL to perform
the final exact sort.

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

The inner `LIMIT` controls how many approximate candidates are reconsidered.

## Configure IVFFlat iterative scans

Set `ivfflat.iterative_scan` to enable iterative behavior for an IVFFlat
index. When the initial scan yields too few filtered rows, the index continues
searching until it finds enough or reaches `ivfflat.max_probes`.

## Inspect filter-aware plans

Vector-operation costing for filtered searches can lead PostgreSQL to prefer a
sequential scan or a conventional index over HNSW. That choice can be correct;
the mere presence of a vector index does not require the planner to use it.

Run `EXPLAIN` on the real filtered query and verify the selected plan before
changing scan-depth controls or forcing a different access path.
