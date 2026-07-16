# Raster and GDAL

Batch attribution: `3.5.0` and `3.6.0`.

## Library requirement

As of PostGIS 3.5.4, `postgis_raster` requires GDAL 2.4 or newer.

## Clip pixels touched by a geometry

Raster `ST_Clip` adds a `touched` option. Enable it when clipping should include
pixels touched by the input geometry, rather than relying only on the prior
pixel-selection behavior.

All raster `ST_Clip` overloads were replaced during the same development line.
Rebuild materialized views that depend on them; see
[Compatibility and upgrades](compatibility-and-upgrades.md).

## Aggregate, remap, and intersect

- Use `ST_AsRasterAgg` to aggregate geometries into raster output.
- Use `ST_ReclassExact` for fast remapping by exact source values.
- Use `ST_IntersectionFractions` to calculate intersection fractions. It
  requires GEOS 3.14 or newer.

## Removed ambiguous overload

The unusably ambiguous `ST_ApproxQuantile(raster, double precision)` signature
has been removed. Rewrite calls so they select a remaining, unambiguous
overload rather than relying on casts to restore the deleted signature.

## Route GDAL diagnostics to PostgreSQL logs

Enable the `postgis.gdal_cpl_debug` GUC to emit GDAL CPL debugging messages
through PostgreSQL logging:

```sql
SET postgis.gdal_cpl_debug = ON;
```

Scope the setting appropriately for the diagnostic session and inspect the
server logs for the emitted GDAL messages.
