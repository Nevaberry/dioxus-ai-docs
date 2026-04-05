# Breaking Changes — PostGIS 3.5–3.6

## 3.5.0: SFCGAL CG_ Prefix Migration

All SFCGAL functions renamed from `ST_` to `CG_` prefix. Old `ST_` names are deprecated.

```sql
-- Old (deprecated):
SELECT
  ST_StraightSkeleton (geom);

-- New:
SELECT
  CG_StraightSkeleton (geom);

-- Applies to all SFCGAL functions: CG_Intersection, CG_3DIntersects,
-- CG_Difference, CG_Union, CG_Triangulate, CG_Area, CG_3DDistance, CG_Distance, etc.
```

## 3.5.0: ST_DFullyWithin Behavior Change

Now defined as `ST_Contains(ST_Buffer(A, R), B)` — geometry B must be entirely within distance R of geometry A.

## 3.5.0: ST_GeneratePoints Seed Change

Improved performance algorithm means old seeded pseudo-random point sets will produce different results. Regenerate if reproducibility matters.

## 3.5.1: ST_TileEnvelope Clips to Tile Plane Extent

`ST_TileEnvelope` now clips returned envelopes to the tile grid's valid extent. Previously it could return envelopes extending beyond the tile plane boundaries. Code relying on unclipped tile envelopes may produce different results.

## 3.6.0: geometry_columns View No Longer Checks Constraints

The `geometry_columns` view no longer reads CHECK constraints to determine geometry type/SRID. Only typmod-based column definitions are recognized. Tables using old-style CHECK constraints for geometry metadata won't appear correctly in `geometry_columns`. Fix by recreating columns with typmod:

```sql
-- Old (CHECK constraint style, no longer detected):
ALTER TABLE t ADD COLUMN geom geometry;
ALTER TABLE t ADD CONSTRAINT enforce_srid CHECK (ST_SRID(geom) = 4326);

-- New (typmod style, required for 3.6+):
ALTER TABLE t ADD COLUMN geom geometry(Point, 4326);
```

**Note:** 3.6.1 partially reverted this — `geometry_columns` parses table constraints again (#5978).

## 3.6.0: ST_NumGeometries/ST_GeometryN on TIN and PolyhedralSurface

TIN and PolyhedralSurface are now treated as unitary geometries by `ST_NumGeometries` and `ST_GeometryN`. Use `ST_NumPatches`/`ST_PatchN` for patch-level access instead.

```sql
-- Before 3.6: ST_NumGeometries(tin) returned patch count
-- After 3.6:  ST_NumGeometries(tin) returns 1
-- Use instead:
SELECT ST_NumPatches(tin);
SELECT ST_PatchN(tin, 1);
```

## 3.6.0: Topology Bigint Support

Topology IDs changed from `integer` to `bigint`. Topology functions that accepted integer now accept bigint. Existing topologies need domain upgrades during `postgis_extensions_upgrade()`.
