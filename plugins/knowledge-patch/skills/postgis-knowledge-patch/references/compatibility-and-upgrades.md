# Compatibility and Upgrades

Batch attribution: `3.5.0`, `3.6.0`, and `supported-branch-patches`.

## Runtime compatibility

### PostGIS 3.5

- PostGIS 3.5.0 requires PostgreSQL 12–17, GEOS 3.8 or newer, and PROJ
  6.1 or newer.
- GEOS 3.12 or newer is required to expose every feature in that release.
- `postgis_sfcgal` requires SFCGAL 1.4 or newer; SFCGAL 1.5 is required for
  every SFCGAL feature.
- Later 3.5 patch releases add PostgreSQL 18 build support.
- As of 3.5.4, `postgis_raster` requires GDAL 2.4 or newer.

### PostGIS 3.6

- The base 3.6.0 release supports PostgreSQL 12 through PostgreSQL 18 beta 3
  and requires GEOS 3.8 or newer plus PROJ 6.1 or newer.
- GEOS 3.14 or newer is required to expose every feature.
- SFCGAL 2.2 or newer is required to expose every SFCGAL feature.
- The branch supports final PostgreSQL 18 as of 3.6.1.

## Build and packaging changes

- Install `xmllint` when building comments.
- Install DocBook 5 XSL when building HTML documentation.
- Do not expect comments inside the PostGIS extensions; they are no longer
  packaged there.
- Pass `--without-tiger` to omit the Tiger geocoder from a 3.6 build.
- Remove deployment steps for the deleted `WFS_locks` extra package.

## Extension upgrade checks

### Replaced SQL functions

- The record overload of `ST_AsGeoJSON` changed so a column can supply the
  feature ID. Rebuild dependent views and materialized views.
- Every `ST_Clip` variant was replaced. Rebuild materialized views that invoke
  any of those overloads.

Treat these as replacement events rather than ordinary compatible function
updates, because stored dependencies can retain the former function identity.

### Geometry-column discovery

The base 3.6.0 release removed constraint checking from the
`geometry_columns` view. Version 3.6.1 restored constraint parsing. Re-test
metadata tooling that learned the temporary 3.6.0 behavior.

### Topology dependencies

Topology domains can be upgraded. Topology functions formerly restricted to
`integer` identifiers were replaced by `bigint` forms that accept both
`integer` and `bigint` arguments. Inspect dependent objects and overload
resolution during extension upgrades, and perform the corruption repair
described in [Topology](topology.md).

## Supported patch lines

The supported-branch patch releases recorded for this patch are 3.6.2, 3.5.5,
3.4.5, 3.3.9, 3.2.9, 3.1.13, and 3.0.12. Releases 3.1.13 and 3.0.12 are the
final releases of their end-of-life series. Upgrade installations on the 3.0
or 3.1 series to a supported branch.
