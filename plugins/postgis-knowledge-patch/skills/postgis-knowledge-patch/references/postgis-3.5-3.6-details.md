# PostGIS 3.5–3.6 Detailed Reference

Detailed changelog for PostGIS features added after 3.4 (Claude's baseline knowledge).

## Breaking Changes

### 3.5.0 — SFCGAL Functions Renamed to CG_ Prefix
All SFCGAL functions moved from `ST_` to `CG_` prefix. Old `ST_` names deprecated but still work.
New CG_ wrappers added: `CG_Intersection`, `CG_3DIntersects`, `CG_Intersects`, `CG_Difference`, `CG_Union` (+ aggregate), `CG_Triangulate`, `CG_Area`, `CG_3DDistance`, `CG_Distance`.
`CG_StraightSkeleton` now accepts optional parameter to use M as distance in result.

### 3.5.0 — ST_DFullyWithin Behavior Change
Semantics changed to `ST_Contains(ST_Buffer(A, R), B)`. Existing queries may return different results.

### 3.5.0 — ST_AsGeoJSON(record) — Column as Feature ID
Can now promote a table column as the GeoJSON Feature `id`. Signature changed — materialized views using `ST_AsGeoJSON(record ..)` need rebuilding.

### 3.5.0 — ST_GeneratePoints Seed Breaking Change
Seeded pseudo-random points produce different results. Regenerate if reproducibility matters.

### 3.5.0 — ST_Clip `touched` Parameter (Raster)
`ST_Clip` now supports a `touched` option to include pixels touched by the clipping geometry, not just those with center inside. All ST_Clip variants replaced — materialized views need rebuilding.

```sql
-- Include pixels touched by geometry, not just centers-inside
SELECT
  ST_Clip (rast, geom, touched => true)
FROM
  raster_table;
```

### 3.5.1 — ST_TileEnvelope Clips to Tile Plane Extent
`ST_TileEnvelope` now clips returned envelopes to the tile plane extent (valid projection bounds). Previously envelopes could extend beyond. Existing queries at edge tiles may return smaller geometries.

### 3.6.0 — TIN/PolyhedralSurface Accessor Change
`ST_NumGeometries`/`ST_GeometryN` now treat TIN and PolyhedralSurface as unitary (return 1). Use `ST_NumPatches`/`ST_PatchN` for patch-level access instead.

### 3.6.0 — Topology Bigint Support
Topology IDs now support `bigint`. Integer-accepting topology functions replaced with bigint versions (accept both).

### 3.6.0 — Removed: st_approxquantile(raster, double precision)
Dropped due to ambiguous signature. Use the variant with additional parameters.

## New Vector Functions

### 3.5.0
- `ST_HasZ(geometry)` / `ST_HasM(geometry)` — boolean Z/M dimension checks
- `ST_CurveN(geometry, n)` / `ST_NumCurves(geometry)` — CompoundCurve accessors
- `ST_RemoveIrrelevantPointsForView(geometry, ...)` — viewport-based point simplification
- `ST_RemoveSmallParts(geometry, ...)` — removes small polygon parts (slivers)

### 3.6.0
- `ST_CoverageClean(geom[])` — edge-match and gap-remove polygonal coverages (GEOS 3.14)

## New Raster Functions

### 3.6.0
- `ST_AsRasterAgg(...)` — aggregate function to create a raster from a set of geometries
- `ST_ReclassExact(rast, ...)` — quickly remap exact values in a raster
- `ST_IntersectionFractions(rast, geom)` — raster pixel/geometry intersection fractions (GEOS 3.14)

## New Topology Functions

### 3.5.0
- `TopoGeo_LoadGeometry(topology, geometry, tolerance)` — loads geometry into a topology

### 3.6.0
- `ValidateTopologyPrecision` / `MakeTopologyPrecise` — validate and fix topology precision issues

## New SFCGAL Functions

### 3.5.0 (require SFCGAL 1.5)
- `CG_Visibility(polygon, point)` — visibility polygon from a point
- `CG_YMonotonePartition`, `CG_ApproxConvexPartition`, `CG_GreeneApproxConvexPartition`, `CG_OptimalConvexPartition` — polygon partitioning
- `ST_ExtrudeStraightSkeleton(geometry)` — extrude along straight skeleton

### 3.6.0 (require SFCGAL 2.2)
- `CG_Simplify` — 3D geometry simplification
- `CG_3DAlphaWrapping` — 3D alpha wrapping (tight surface around point set)
- `CG_Scale`, `CG_Translate`, `CG_Rotate` — 3D affine transformations
- `CG_Buffer3D` — 3D buffering
- `CG_StraightSkeletonPartition` — partition polygon via straight skeleton
- SFCGAL now supports M coordinates (SFCGAL >= 1.5.0)
