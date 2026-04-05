# PostGIS Raster & Topology (3.6.0–3.6.1)

## ST_AsRasterAgg (3.6.0)

Aggregate function that converts a set of geometries into a single raster.

```sql
-- Rasterize geometries into a single output raster
SELECT
  ST_AsRasterAgg (geom, scalex := 1.0, scaley := -1.0)
FROM
  my_table;
```

## ST_ReclassExact (3.6.0)

Fast raster value remapping using exact value matching (not ranges like `ST_Reclass`).

```sql
-- Remap specific pixel values: 1->10, 2->20, 3->30
SELECT ST_ReclassExact(rast, 1, ARRAY[1,10, 2,20, 3,30]::integer[]);
```

## ST_IntersectionFractions (3.6.0, requires GEOS 3.14)

Returns the fraction of each raster cell covered by a geometry intersection. Useful for accurate area-weighted calculations when geometries don't align with raster cells.

## Topology Bigint Migration (3.6.0)

Topology IDs changed from `integer` to `bigint`. Topology functions that accepted integer now accept bigint. Existing topologies need domain upgrades during `postgis_extensions_upgrade()`.

## Topology Utilities (3.6.0)

New utility functions for topology management:

```sql
-- Total disk size of all topology tables
SELECT TotalTopologySize('my_topology');

-- Check if topology precision is sufficient
SELECT ValidateTopologyPrecision('my_topology');

-- Snap topology to its declared precision
SELECT MakeTopologyPrecise('my_topology');
```

## TopoGeometry Fix (3.6.1)

After upgrading to 3.6.1, run if you have topogeometry columns:

```sql
SELECT topology.FixCorruptTopoGeometryColumn(schema_name, table_name, feature_column)
FROM topology.layer;
```
