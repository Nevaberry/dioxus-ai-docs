# Iterative Index Scans (0.8.0)

## The Overfiltering Problem

When combining approximate nearest-neighbor search with `WHERE` clauses, the index may not return enough qualifying rows. For example, if HNSW returns 100 candidates but only 2 match your filter, you get fewer results than requested.

Iterative index scans solve this by automatically scanning more of the index until enough results are found.

## Enabling Iterative Scans

### HNSW

```sql
-- Strict ordering: results in exact distance order (slower)
SET hnsw.iterative_scan = strict_order;

-- Relaxed ordering: results may be slightly out of order (better recall, faster)
SET hnsw.iterative_scan = relaxed_order;
```

### IVFFlat

```sql
-- IVFFlat only supports relaxed_order (no strict_order)
SET ivfflat.iterative_scan = relaxed_order;
```

## Scan Limits

Control how much work iterative scans do before giving up:

```sql
-- HNSW: max tuples to visit (default 20,000)
SET hnsw.max_scan_tuples = 20000;

-- HNSW: memory budget as multiple of work_mem (default 1)
SET hnsw.scan_mem_multiplier = 2;

-- IVFFlat: max probes for iterative scans (default 100)
SET ivfflat.max_probes = 100;
```

## CTE Patterns

### Strict Ordering with Relaxed Scans

Use a materialized CTE to get relaxed scan performance with strict result ordering:

```sql
WITH relaxed_results AS MATERIALIZED (
    SELECT id, embedding <-> '[1,2,3]' AS distance FROM items
    WHERE category_id = 123 ORDER BY distance LIMIT 5
) SELECT * FROM relaxed_results ORDER BY distance + 0;
```

**Important:** The `+ 0` on the outer ORDER BY is needed for PostgreSQL 17+ to force re-sorting (otherwise the optimizer may skip the re-sort).

### Distance Filter Pattern

Place distance thresholds outside the CTE to avoid interfering with the index scan:

```sql
WITH nearest AS MATERIALIZED (
    SELECT id, embedding <-> '[1,2,3]' AS distance FROM items ORDER BY distance LIMIT 5
) SELECT * FROM nearest WHERE distance < 5 ORDER BY distance;
```

If the distance filter were inside the CTE, it would act as a `WHERE` clause that could trigger the overfiltering problem. Keeping it outside ensures the index scan returns the requested number of candidates first, then filters by distance.
