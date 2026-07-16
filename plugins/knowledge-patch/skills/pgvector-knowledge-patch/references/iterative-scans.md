# Iterative Scans and Filtered Search

## Why filtered approximate searches can return too few rows

HNSW and IVFFlat approximate scans retrieve candidate vectors before ordinary
PostgreSQL filters are evaluated. If a filter is selective, many candidates can
be discarded and the result can contain fewer rows than `LIMIT` even though
additional matching rows exist.

Iterative scans address this by continuing to retrieve candidates until the
query has enough matching rows or an index-specific scan limit is reached.

## HNSW iterative scans

The 0.8-guide introduced `hnsw.iterative_scan`. It defaults to `off` and accepts
two active modes:

- `strict_order` preserves distance order.
- `relaxed_order` trades exact ordering for faster search.

```sql
SET hnsw.iterative_scan = 'strict_order';

SELECT id, embedding <=> '[1,2,3]' AS distance
FROM items
WHERE category = 1
ORDER BY embedding <=> '[1,2,3]'
LIMIT 20;
```

Keep the distance `ORDER BY` immediately before `LIMIT`; that query shape lets
the planner use iterative scanning.

### Scan limits

`hnsw.max_scan_tuples` caps the number of tuples visited and defaults to
`20000`. `hnsw.scan_mem_multiplier` caps scan memory as a multiple of
`work_mem` and defaults to `1`.

```sql
SET hnsw.max_scan_tuples = 40000;
SET hnsw.scan_mem_multiplier = 2;
```

Raise these settings when selective filters still stop the iterative scan from
filling the requested limit. Tuple and memory limits are independent reasons
for the search to stop.

## IVFFlat iterative scans

Since 0.8.0, IVFFlat supports the same continue-after-filtering strategy.
Configure it with `ivfflat.iterative_scan`. When the initial scan supplies too
few filtered results, IVFFlat continues until it finds enough matches or reaches
`ivfflat.max_probes`.

## Re-establish ordering after `relaxed_order`

`relaxed_order` candidates may not be in exact distance order. Put the
approximate search and candidate limit in a subquery, then re-sort the limited
candidate set. An expression such as `distance * 1` forces the final sort.

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

## Planner costing for filtered vector searches

Vector operations now have better cost estimates for filtered searches. The
planner may correctly choose a sequential scan or conventional index instead
of HNSW, especially for a small or selective example. Use `EXPLAIN` to verify
the chosen plan rather than assuming the vector index is exercised.
