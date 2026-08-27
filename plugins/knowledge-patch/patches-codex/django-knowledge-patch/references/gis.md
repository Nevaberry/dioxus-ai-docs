# GIS and Spatial Features

## Use backend-specific spatial operations

Spatial capabilities remain conditional on database versions:

- `BoundingCircle` works with SpatiaLite 5.1+ (since 5.1).
- `Collect` works with MySQL 8.0.24+ (since 5.1).
- MySQL supports the `coveredby` and `covers` spatial lookups (since 5.2).
- MariaDB 12.0.1+ supports `coveredby`, `isvalid`, `Collect`, `GeoHash`, and `IsValid`
  (since 6.0).

`FromWKB()` and `FromWKT()` accept an optional `srid`; Oracle ignores that argument (since 5.1).
Treat every capability as a backend/version check, not a portable guarantee.

## Work with dimensions, measures, curves, and geometry types

OGR geometries expose `is_3d` and `set_3d()`. Measured geometries expose `is_measured`, `m`, and
`set_measured()`. `centroid` is available on every supported geometry type (since 5.1). Replace
assignment to `OGRGeometry.coord_dim` with `set_3d()`.

GDAL integration supports `CurvePolygon`, `CompoundCurve`, `CircularString`, `MultiSurface`, and
`MultiCurve`. Use `OGRGeometry.has_curve`, `get_linear_geometry()`, and `get_curve_geometry()` to
inspect and convert curved geometry (since 5.2).

For GEOS and database expressions, `GEOSGeometry.hasm`, `Rotate`, the `geom_type` lookup, and
`GeometryType()` add measured-dimension, rotation, and geometry-type operations (since 6.0).

## Handle GeoIP2 inputs and database selection

`GeoIP2` accepts strings plus `ipaddress.IPv4Address` and `ipaddress.IPv6Address` objects.
Country results include continent data and EU membership. City results include accuracy radius
and region name; `metro_code` and `region_code` are the preferred names for the values also kept
under the older `dma_code` and `region` keys (since 5.1).

When given a directory containing both city and country databases, `GeoIP2` opens only the city
database when one is available. Pass the country database file path explicitly when country-only
database selection matters.

Replace `GeoIP2.coords()` with `lon_lat()` and `GeoIP2.open()` with the constructor.

## Validate spatial lookup inputs

The 5.2.17 patch restricts spatial lookup inputs: a lookup no longer accepts a `dict` or a string
that is not valid `GEOSGeometry` when that value would be passed to `GDALRaster`. This is a
backward-incompatible validation change. Field assignment still accepts these types, so validate
untrusted input at the lookup boundary rather than assuming assignment and lookup use identical
coercion.

## Limit nested geometry collections

WKT input permits at most 198 nested `GEOMETRYCOLLECTION` objects. WKB input permits at most 198
collections in total across breadth and depth. GeoJSON input is unaffected (5.2.17).

`GEOSGeometry`, GIS form fields, and GIS model fields accept `max_geom_collections` to customize
the limit:

```python
from django.contrib.gis.geos import GEOSGeometry

geometry = GEOSGeometry(
    "GEOMETRYCOLLECTION EMPTY",
    max_geom_collections=50,
)
```

Choose a lower application limit when parsing untrusted or resource-sensitive payloads.

## Update geometry widgets

`BaseGeometryWidget.base_layer` selects the JavaScript map base layer (since 6.0). Built-in
geometry widgets no longer render inline JavaScript, so custom widget templates that copied or
extended the former markup may need to load or initialize scripts differently.

## Respect dependency floors

GIS upgrades must also satisfy the platform floors in [upgrading.md](upgrading.md), including the
PROJ, GDAL, PostGIS, and optional `geoip2` requirements. Run database-specific GIS tests whenever
using an operation or lookup that is gated by a precise server version.
