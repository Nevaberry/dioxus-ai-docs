# Spatial and geometry

Use this reference before changing coordinate order, CRS declarations, geometry
serialization, or extension loading. These spatial changes come from batch
`1.5.0`.

## Axis-order migration

Spherical and spheroidal distance, perimeter, area, and within functions, as
well as `ST_Transform`, are migrating away from the legacy interpretation:

- legacy behavior: `x = latitude`, `y = longitude`;
- conventional behavior: `x = longitude`, `y = latitude`.

In 1.5.0, leaving `geometry_always_xy` unset produces a warning. Opt into the
new behavior explicitly:

```sql
SET geometry_always_xy = true;
```

To preserve legacy behavior temporarily during a controlled migration:

```sql
SET geometry_always_xy = false;
```

The unset state is scheduled to become an error in 2.0, and `true` is scheduled
to become the default in 2.1. Explicit configuration avoids silently changing
results at either transition.

Test known asymmetric coordinate pairs: values where swapping latitude and
longitude still lands in a valid numeric range can otherwise produce plausible
but incorrect results.

## Core `GEOMETRY` type

`GEOMETRY` is a core DuckDB type in 1.5.0. Most geometry functions remain in
the `spatial` extension, so having the type available does not imply that every
spatial operation is built in.

The type accepts an optional coordinate reference system:

```sql
CREATE TABLE places (
    id INTEGER,
    geom GEOMETRY('OGC:CRS84')
);
```

Spatial functions reject inputs whose CRS types disagree. Treat that rejection
as a useful type boundary: transform data deliberately rather than removing CRS
information merely to make a call type-check.

The core includes a small set of CRS definitions. Loading `spatial` registers
more than 7,000 EPSG definitions and provides most geometry functions.

```sql
INSTALL spatial;
LOAD spatial;
```

## Geometry representation boundaries

Geometry storage now uses little-endian WKB internally. Callers should not
depend on the storage representation or byte order. Move geometry through the
supported conversion functions:

- `ST_AsWKT` for text output;
- `ST_AsWKB` for binary output;
- `ST_GeomFromText` for text input; and
- `ST_GeomFromWKB` for binary input.

For example:

```sql
SELECT ST_AsWKT(geom) FROM places;
SELECT ST_AsWKB(geom) FROM places;
```

Use these boundaries in application protocols, fixtures, exports, and tests.
Do not compare or generate DuckDB's internal geometry bytes directly.

## Migration checklist

1. Inventory distance, perimeter, area, within, and transform calls.
2. Determine the coordinate convention used by every input dataset.
3. Set `geometry_always_xy` explicitly for each relevant connection.
4. Test with known coordinates whose swapped result is observably wrong.
5. Add compatible CRS types to schema boundaries where practical.
6. Load `spatial` when functions or the wider EPSG registry are needed.
7. Replace internal-byte assumptions with WKT/WKB conversion functions.
8. Plan to remove legacy axis-order pinning before the later default change.
