# SFCGAL Functions — PostGIS 3.5–3.6

## CG_ Prefix Migration (3.5.0)

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

## Polygon Partition Functions (3.5.0)

- `CG_YMonotonePartition(geom)` — y-monotone polygon partition
- `CG_ApproxConvexPartition(geom)` — approximate convex partition
- `CG_GreeneApproxConvexPartition(geom)` — Greene's approximate convex partition
- `CG_OptimalConvexPartition(geom)` — optimal convex partition

## CG_Visibility (3.5.0)

Computes the visibility polygon from a point within a polygon.

```sql
SELECT CG_Visibility(polygon, point);
```

## ST_ExtrudeStraightSkeleton (3.5.0)

Extrude a polygon along its straight skeleton.

```sql
SELECT ST_ExtrudeStraightSkeleton(geom);
```

## CG_3DAlphaWrapping (3.6.0)

Computes a 3D alpha wrapping of a geometry — a watertight 3D surface mesh that approximates the input.

```sql
SELECT CG_3DAlphaWrapping(geom3d, alpha, offset);
```

## SFCGAL 2 Functions (3.6.0, requires SFCGAL 2.2+)

3D transformation and partitioning functions:

- `CG_Scale(geom, sx, sy, sz)` — 3D scaling
- `CG_Translate(geom, dx, dy, dz)` — 3D translation
- `CG_Rotate(geom, angle, axis_x, axis_y, axis_z)` — 3D rotation
- `CG_Buffer3D(geom, radius)` — 3D buffer
- `CG_StraightSkeletonPartition(geom)` — partition polygon via straight skeleton
