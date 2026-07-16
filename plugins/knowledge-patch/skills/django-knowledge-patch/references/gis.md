# GIS and Spatial Features

Batch attribution: `5.1`, `5.2`, `6.0`.

## Contents

- [Spatial database operations](#spatial-database-operations)
- [Curved and measured geometries](#curved-and-measured-geometries)
- [OGR geometry APIs](#ogr-geometry-apis)
- [GeoIP2 inputs and result fields](#geoip2-inputs-and-result-fields)
- [GeoIP2 database selection](#geoip2-database-selection)
- [Geometry widgets](#geometry-widgets)
- [GIS API migrations](#gis-api-migrations)

## Spatial database operations

Support depends on both Django and the spatial database version:

- `BoundingCircle` works on SpatiaLite 5.1+ (since `5.1`).
- `Collect` works on MySQL 8.0.24+ (since `5.1`).
- MySQL supports the `coveredby` and `covers` lookups (since `5.2`).
- MariaDB 12.0.1+ supports `coveredby`, `isvalid`, `Collect`, `GeoHash`, and `IsValid` (since
  `6.0`).
- `Rotate`, the `geom_type` lookup, and the `GeometryType()` function are available in `6.0`.

Check the exact operation and database combination rather than assuming every spatial backend has
the same function set.

`FromWKB()` and `FromWKT()` accept an optional `srid` (since `5.1`). Oracle ignores that argument,
so do not depend on it to assign or transform the SRID there.

## Curved and measured geometries

GDAL integration supports these curved geometry types (since `5.2`):

- `CurvePolygon`
- `CompoundCurve`
- `CircularString`
- `MultiSurface`
- `MultiCurve`

Use `OGRGeometry.has_curve` to detect curved content, `get_linear_geometry()` to obtain a linear
form, and `get_curve_geometry()` to obtain the curved representation.

For measured dimensions:

- `OGRGeometry.is_measured`, `.m`, and `set_measured()` are available since `5.1`.
- `GEOSGeometry.hasm` is available since `6.0`.

Do not conflate a measured M dimension with the Z dimension.

## OGR geometry APIs

OGR geometries expose `is_3d` and `set_3d()` (since `5.1`). Assigning to `coord_dim` is deprecated;
call `set_3d()` explicitly.

`centroid` works for every supported OGR geometry type (since `5.1`), rather than only the subset
that formerly exposed it.

## GeoIP2 inputs and result fields

`GeoIP2` accepts `ipaddress.IPv4Address` and `ipaddress.IPv6Address` instances in addition to
textual addresses (since `5.1`).

Country results add:

- Continent data.
- European Union membership.

City results add:

- Accuracy radius.
- Region name.
- `metro_code` as the current name for `dma_code`.
- `region_code` as the current name for `region`.

The old `dma_code` and `region` keys remain available, so consumers can migrate without an
all-at-once schema change.

## GeoIP2 database selection

When initialized with a directory containing both city and country databases, `GeoIP2` opens only
the city database when one is available (since `5.1`). Pass the country database file path
explicitly when the operation must use that database.

## Geometry widgets

`BaseGeometryWidget.base_layer` selects the JavaScript map's base layer (since `6.0`). Built-in
geometry widgets no longer render inline JavaScript. Update custom geometry-widget templates that
copied or extended the previous inline-script markup, and verify their media assets and map
initialization under Content Security Policy.

## GIS API migrations

- Replace `GeoIP2.coords()` with `GeoIP2.lon_lat()`.
- Replace `GeoIP2.open()` with the `GeoIP2` constructor.
- Replace assignment to `OGRGeometry.coord_dim` with `set_3d()`.
