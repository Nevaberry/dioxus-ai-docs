# Geometry and Processing

Batch attribution: `3.5.0`, `3.6-new-functions`, and `3.6.0`.

## Operators and collection access

### Geometry inequality

Geometry has an explicit `<>` operator. Both `<>` and `!=` therefore avoid the
former non-unique-operator error. TopoGeometry has different comparison
requirements; see [Topology](topology.md).

### TIN and polyhedral surfaces

`ST_NumGeometries` and `ST_GeometryN` treat a TIN or `PolyhedralSurface` as one
geometry rather than exposing its patches. Use `ST_NumPatches` and `ST_PatchN`
for patch counts and patch access.

### Curved and display geometry

- Use `ST_CurveN` and `ST_NumCurves` for consistent curved-geometry access.
- Use `ST_RemoveIrrelevantPointsForView` to remove points irrelevant at a
  target view.
- Use `ST_RemoveSmallParts` to remove small geometry parts for display.

## Changed generation and measurement behavior

- The optimized `ST_GeneratePoints` implementation produces a different
  pseudorandom sequence for a supplied seed. Regenerate exact-output fixtures
  and persisted results that relied on the former sequence.
- `ST_DFullyWithin(A, B, R)` behaves as
  `ST_Contains(ST_Buffer(A, R), B)`.
- `ST_Length` returns `0` for a `CurvePolygon`.
- Starting with 3.5.1, `ST_TileEnvelope` clips generated envelopes to the
  tile-plane extent. Calls that previously extended beyond the plane can
  return different bounds.

## GEOS 3.13 RelateNG behavior

- Relate matrices can differ under the multi-valent endpoint boundary-node
  rule.
- Invalid `MultiPolygon` values whose components share boundaries can produce
  different relate results. Apply `ST_MakeValid` before relating them.
- A zero-length `LineString` is treated as the equivalent `Point`.

## Clean polygon coverages

`ST_CoverageClean` is a GEOS 3.14-or-newer window function. It converts a dirty
polygonal coverage into edge-matched, non-overlapping polygons and closes gaps
smaller than `gapMaximumWidth`.

```sql
SELECT id,
       ST_CoverageClean(geom, 0.5, -1, 'MERGE_LONGEST_BORDER') OVER () AS geom
FROM parcels;
```

- `snappingDistance = -1` selects a distance automatically and is the default.
- `snappingDistance = 0` disables snapping.
- Assign overlapping areas with `MERGE_LONGEST_BORDER` (the default),
  `MERGE_MAX_AREA`, `MERGE_MIN_AREA`, or `MERGE_MIN_INDEX`.

## SFCGAL naming and capabilities

SFCGAL functions use the `CG_` prefix; their former `ST_` names are deprecated.
Use `CG_StraightSkeleton` in place of `ST_StraightSkeleton`. Its optional
parameter uses the M ordinate as distance in the result.

New SFCGAL-backed operations include:

- Partitioning: `CG_YMonotonePartition`, `CG_ApproxConvexPartition`,
  `CG_GreeneApproxConvexPartition`, and `CG_OptimalConvexPartition`.
- Visibility and overlay: `CG_Visibility`, `CG_Intersection`, `CG_Difference`,
  and `CG_Union`; `CG_Union` also has an aggregate form.
- Predicates: `CG_3DIntersects` and `CG_Intersects`.
- Construction and measurement: `CG_Triangulate`, `CG_Area`,
  `CG_3DDistance`, `CG_Distance`, and `ST_ExtrudeStraightSkeleton`.

SFCGAL-backed geometry supports M ordinates with SFCGAL 1.5 or newer. PostGIS
also adds `CG_3DAlphaWrapping`; SFCGAL 2 supplies 3D buffering and
straight-skeleton partitioning operations. Check
[Compatibility and upgrades](compatibility-and-upgrades.md) for the library
version needed to expose the complete feature set.
