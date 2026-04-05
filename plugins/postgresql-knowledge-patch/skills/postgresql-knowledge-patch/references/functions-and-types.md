# Functions & Types

## uuidv7() — Timestamp-Ordered UUIDs (18)

Built-in UUID v7 generation (time-sortable). Also added `uuidv4()` as explicit alias for `gen_random_uuid()`.

```sql
SELECT
  uuidv7();

-- e.g. '019271a4-5c00-7d3e-8f4a-2b1c3d4e5f60'
SELECT
  uuidv4();

-- same as gen_random_uuid()
```

## New Array Functions (18)

```sql
SELECT array_sort(ARRAY[3,1,2]);          -- {1,2,3}
SELECT array_sort(ARRAY[3,1,2], 'desc');  -- {3,2,1}
SELECT array_reverse(ARRAY[1,2,3]);       -- {3,2,1}
```

## casefold() — Unicode Case Folding (18)

More accurate than `lower()` for case-insensitive comparison (handles characters with multiple case equivalents).

```sql
SELECT casefold('Straße');  -- 'strasse'
```

## crc32() / crc32c() (18)

```sql
SELECT crc32('hello'::bytea);   -- CRC-32 checksum
SELECT crc32c('hello'::bytea);  -- CRC-32C (Castagnoli) checksum
```

## random(min, max) (17)

```sql
SELECT random(1, 100);          -- integer in [1, 100]
SELECT random(1::bigint, 100);  -- bigint
SELECT random(1.0, 10.0);      -- numeric
```
## Interval Infinity (17)

`interval` now supports `+/-infinity`:

```sql
SELECT 'infinity'::interval;
SELECT '-infinity'::interval;
```

## MIN()/MAX() on Arrays and Composites (18)

```sql
SELECT max(ARRAY[1,2,3]), min(ARRAY[4,5,6]);  -- works on array columns
```

## EXTRACT(WEEK ...) (18)

```sql
SELECT EXTRACT(WEEK FROM date '2025-01-15');  -- ISO week number
```

## Integer <-> bytea Casting (18)

```sql
SELECT 255::int::bytea;               -- '\x000000ff'
SELECT '\x000000ff'::bytea::int;      -- 255
```
