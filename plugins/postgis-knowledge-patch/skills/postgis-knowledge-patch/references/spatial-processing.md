# PostGIS Spatial Processing Functions (3.5.0–3.6.0)

## ST_RemoveIrrelevantPointsForView (3.5.0)

Removes points irrelevant for rendering within a specific bounding box. Faster than `ST_ClipByBox2D` because it doesn't compute intersection points (but may produce self-intersections).

```sql
-- Remove points not needed for rendering within the view box
SELECT
  ST_RemoveIrrelevantPointsForView (
    geom,
    ST_MakeEnvelope (12, 12, 18, 18), -- view bounds (box2d)
    true -- cartesian_hint (optional, default false)
  );

-- Warning: result may be invalid for polygons — use ST_MakeValid if needed
```

## ST_RemoveSmallParts (3.5.0)

Removes parts whose bounding box is smaller than given thresholds. Useful for removing small islands/holes before map rendering.

```sql
-- Remove parts smaller than 50x50 coordinate units
SELECT ST_RemoveSmallParts(geom, 50, 50);
-- Works on (MULTI)POLYGON and (MULTI)LINESTRING
```

## ST_CoverageClean (3.6.0, requires GEOS 3.14)

Cleans polygonal coverages by edge-matching and removing gaps between adjacent polygons.

```sql
-- Clean a coverage (set of non-overlapping polygons)
SELECT ST_CoverageClean(geom) FROM coverage_table;
```

## ST_IntersectionFractions (3.6.0, requires GEOS 3.14)

Returns the fraction of each raster cell covered by a geometry intersection.

## ST_HasZ / ST_HasM (3.5.0)

Boolean dimension check helpers replacing the need to check `ST_CoordDim` or `ST_NDims`:

```sql
SELECT ST_HasZ('POINT Z (1 2 3)'::geometry);  -- true
SELECT ST_HasM('POINT M (1 2 3)'::geometry);   -- true
```

## ST_CurveN / ST_NumCurves (3.5.0)

Accessors for components of curved geometries (CompoundCurve, etc.):

```sql
SELECT ST_NumCurves(geom);       -- number of curves in a CompoundCurve
SELECT ST_CurveN(geom, 1);       -- extract Nth curve (1-based)
```
