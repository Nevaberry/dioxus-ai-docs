---
name: postgis-knowledge-patch
description: "PostGIS changes since training cutoff (latest: 3.6.1) — breaking changes, new spatial/raster/SFCGAL functions, topology bigint migration. Load before working with PostGIS."
version: "3.6.1"
license: MIT
metadata:
  author: Nevaberry
---

# PostGIS Knowledge Patch

Covers PostGIS 3.5.0–3.6.1 (2024-09-25 through 2025-11-13). Claude Opus 4.6 knows PostGIS through 3.4. It is **unaware** of the features and breaking changes below.

## Index

| Topic | Reference | Key content |
|---|---|---|
| Breaking changes | [references/breaking-changes.md](references/breaking-changes.md) | geometry_columns typmod, SFCGAL CG_ prefix, ST_DFullyWithin, TIN/PolyhedralSurface, topology bigint |
| Spatial functions | [references/spatial-processing.md](references/spatial-processing.md) | ST_RemoveIrrelevantPointsForView, ST_RemoveSmallParts, ST_CoverageClean, dimension helpers |
| SFCGAL functions | [references/sfcgal-functions.md](references/sfcgal-functions.md) | CG_ prefix migration, polygon partitions, 3D transforms, alpha wrapping |
| Raster & topology | [references/raster-and-topology.md](references/raster-and-topology.md) | ST_AsRasterAgg, ST_ReclassExact, topology bigint utilities, topogeometry fix |

---

## Version Requirements

| Version | PostgreSQL | GEOS | Proj | SFCGAL |
|---|---|---|---|---|
| 3.5.x | 12–17 | 3.8+ | 6.1+ | 1.5+ (full features) |
| 3.6.x | 12–18 | 3.8+ (3.14+ for all) | 6.1+ | 2.2+ (full features) |

---

## Breaking Changes Quick Reference

| Version | Change | Impact |
|---|---|---|
| 3.5.0 | SFCGAL `ST_` → `CG_` prefix | All SFCGAL functions renamed; old names deprecated |
| 3.5.0 | `ST_DFullyWithin` redefined | Now `ST_Contains(ST_Buffer(A,R), B)` — B must be entirely within distance R |
| 3.5.0 | `ST_GeneratePoints` seed change | Different pseudo-random output for same seed |
| 3.5.1 | `ST_TileEnvelope` clips to extent | Returns clipped envelopes; unclipped results no longer possible |
| 3.6.0 | `geometry_columns` ignores CHECK constraints | Must use typmod: `geom geometry(Point, 4326)` |
| 3.6.0 | `ST_NumGeometries`/`ST_GeometryN` on TIN | Returns 1 for TIN/PolyhedralSurface; use `ST_NumPatches`/`ST_PatchN` |
| 3.6.0 | Topology IDs → bigint | Integer→bigint; run `postgis_extensions_upgrade()` |
| 3.6.1 | `geometry_columns` partial revert | CHECK constraints parsed again (#5978) |

---

## Critical: geometry_columns Typmod (3.6.0+)

The most impactful breaking change. Old CHECK-constraint-style columns may not appear in `geometry_columns`:

```sql
-- Old (CHECK constraint style — unreliable in 3.6.0, partially restored in 3.6.1):
ALTER TABLE t
ADD COLUMN geom geometry;

ALTER TABLE t
ADD CONSTRAINT enforce_srid CHECK (ST_SRID (geom) = 4326);

-- Correct (typmod style — always works):
ALTER TABLE t
ADD COLUMN geom geometry (Point, 4326);
```

---

## SFCGAL CG_ Prefix Migration (3.5.0+)

All SFCGAL functions renamed from `ST_` to `CG_`. Old `ST_` names are deprecated:

```sql
-- Old (deprecated):          -- New:
ST_StraightSkeleton(geom)     CG_StraightSkeleton(geom)
ST_Triangulate(geom)           CG_Triangulate(geom)
ST_3DIntersects(a, b)          CG_3DIntersects(a, b)
ST_3DDistance(a, b)             CG_3DDistance(a, b)
-- Applies to ALL SFCGAL functions: CG_Intersection, CG_Difference,
-- CG_Union, CG_Area, CG_Distance, etc.
```

---

## TIN/PolyhedralSurface Access (3.6.0+)

`ST_NumGeometries`/`ST_GeometryN` now treat TIN and PolyhedralSurface as unitary. Use patch accessors:

```sql
-- Before 3.6: ST_NumGeometries(tin) returned patch count
-- After 3.6:  ST_NumGeometries(tin) returns 1
-- Use instead:
SELECT ST_NumPatches(tin);
SELECT ST_PatchN(tin, 1);
```

---

## Common New Function Examples

```sql
-- View-dependent simplification (3.5.0) — fast tile rendering
SELECT ST_RemoveIrrelevantPointsForView(
  geom,
  ST_MakeEnvelope(12, 12, 18, 18),  -- view bounds
  true                                -- cartesian_hint (optional)
);
-- Warning: may produce self-intersections — use ST_MakeValid if needed

-- Remove small polygon parts before rendering (3.5.0)
SELECT ST_RemoveSmallParts(geom, 50, 50);

-- Dimension checks (3.5.0) — cleaner than ST_CoordDim
SELECT ST_HasZ('POINT Z (1 2 3)'::geometry);  -- true
SELECT ST_HasM('POINT M (1 2 3)'::geometry);   -- true

-- Clean coverage gaps (3.6.0, GEOS 3.14+)
SELECT ST_CoverageClean(geom) FROM coverage_table;

-- Aggregate geometries to raster (3.6.0)
SELECT ST_AsRasterAgg(geom, scalex := 1.0, scaley := -1.0) FROM my_table;

-- Exact-value raster reclassification (3.6.0)
SELECT ST_ReclassExact(rast, 1, ARRAY[1,10, 2,20, 3,30]::integer[]);

-- Topology utilities (3.6.0)
SELECT TotalTopologySize('my_topology');
SELECT ValidateTopologyPrecision('my_topology');
SELECT MakeTopologyPrecise('my_topology');
```

---

## New Spatial Functions Quick Reference

| Function | Version | Description |
|---|---|---|
| `ST_RemoveIrrelevantPointsForView(geom, box2d, cartesian_hint)` | 3.5.0 | Remove points outside view bounds (fast, may self-intersect) |
| `ST_RemoveSmallParts(geom, w, h)` | 3.5.0 | Remove parts with bbox smaller than w×h |
| `ST_HasZ(geom)` / `ST_HasM(geom)` | 3.5.0 | Boolean dimension checks |
| `ST_CurveN(geom, n)` / `ST_NumCurves(geom)` | 3.5.0 | CompoundCurve component access |
| `ST_CoverageClean(geom)` | 3.6.0 | Clean polygonal coverage gaps (GEOS 3.14+) |
| `ST_AsRasterAgg(geom, ...)` | 3.6.0 | Aggregate geometries to single raster |
| `ST_ReclassExact(rast, band, values)` | 3.6.0 | Exact-value raster reclassification |
| `ST_IntersectionFractions(rast, geom)` | 3.6.0 | Cell coverage fractions (GEOS 3.14+) |

---

## New SFCGAL Functions Quick Reference

| Function | Version | Description |
|---|---|---|
| `CG_YMonotonePartition(geom)` | 3.5.0 | Y-monotone polygon partition |
| `CG_ApproxConvexPartition(geom)` | 3.5.0 | Approximate convex partition |
| `CG_GreeneApproxConvexPartition(geom)` | 3.5.0 | Greene's approximate convex partition |
| `CG_OptimalConvexPartition(geom)` | 3.5.0 | Optimal convex partition |
| `CG_Visibility(polygon, point)` | 3.5.0 | Visibility polygon from a point |
| `ST_ExtrudeStraightSkeleton(geom)` | 3.5.0 | Extrude along straight skeleton |
| `CG_3DAlphaWrapping(geom, alpha, offset)` | 3.6.0 | Watertight 3D surface mesh |
| `CG_Scale(geom, sx, sy, sz)` | 3.6.0 | 3D scaling (SFCGAL 2.2+) |
| `CG_Translate(geom, dx, dy, dz)` | 3.6.0 | 3D translation (SFCGAL 2.2+) |
| `CG_Rotate(geom, angle, ax, ay, az)` | 3.6.0 | 3D rotation (SFCGAL 2.2+) |
| `CG_Buffer3D(geom, radius)` | 3.6.0 | 3D buffer (SFCGAL 2.2+) |
| `CG_StraightSkeletonPartition(geom)` | 3.6.0 | Partition via straight skeleton (SFCGAL 2.2+) |

---

## Topology Utilities (3.6.0)

| Function | Description |
|---|---|
| `TotalTopologySize(topology_name)` | Total disk size of all topology tables |
| `ValidateTopologyPrecision(topology_name)` | Check if topology precision is sufficient |
| `MakeTopologyPrecise(topology_name)` | Snap topology to its declared precision |

---

## 3.6.1 Fix for TopoGeometry
After upgrading to 3.6 .1,
run if you have topogeometry columns:

```sql
SELECT topology.FixCorruptTopoGeometryColumn(schema_name, table_name, feature_column)
FROM topology.layer;
```

---

## Reference Files

| File | Contents |
|---|---|
| [breaking-changes.md](references/breaking-changes.md) | geometry_columns, TIN/PolyhedralSurface, topology bigint, ST_DFullyWithin, ST_TileEnvelope, ST_GeneratePoints |
| [sfcgal-functions.md](references/sfcgal-functions.md) | CG_ prefix migration, partitioning, visibility, 3D alpha wrapping, scaling/rotation/translation, Buffer3D |
| [spatial-processing.md](references/spatial-processing.md) | ST_RemoveIrrelevantPointsForView, ST_RemoveSmallParts, ST_CoverageClean, ST_IntersectionFractions, ST_HasZ/M, ST_CurveN |
| [raster-and-topology.md](references/raster-and-topology.md) | ST_AsRasterAgg, ST_ReclassExact, ST_IntersectionFractions, topology bigint, utilities, topogeometry fix |
