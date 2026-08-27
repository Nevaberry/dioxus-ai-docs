# GIS and Spatial Features

Load this reference for GeoDjango expressions and lookups, OGR and GEOS geometry,
GeoIP2, spatial widgets, backend capability checks, and geometry input validation.

## Check operation support by backend

### Spatial functions and lookups

- `BoundingCircle` works on SpatiaLite 5.1+, and `Collect` works on MySQL
  8.0.24+. (`5.1`)
- `FromWKB()` and `FromWKT()` accept an optional `srid`; Oracle ignores that
  argument. (`5.1`)
- MySQL supports `coveredby` and `covers` lookups. (`5.2`)
- MariaDB 12.0.1+ supports `coveredby`, `isvalid`, `Collect`, `GeoHash`,
  and `IsValid`. (`6.0`)
- `Rotate`, the `geom_type` lookup, and `GeometryType()` add rotation and
  geometry-type query operations. (`6.0`)

## Work with OGR, GDAL, and GEOS geometry

OGR geometry exposes `is_3d` and `set_3d()`. Measured-geometry support includes
`is_measured`, `m`, and `set_measured()`. `centroid` is available on every
supported geometry type. (`5.1`)

GDAL supports `CurvePolygon`, `CompoundCurve`, `CircularString`,
`MultiSurface`, and `MultiCurve`. Use `OGRGeometry.has_curve`,
`get_linear_geometry()`, and `get_curve_geometry()` to inspect or convert curved
geometry. (`5.2`)

`GEOSGeometry.hasm` exposes the measured dimension. (`6.0`)

Replace deprecated assignment to `OGRGeometry.coord_dim` with `set_3d()`.
(`5.1`)

## Pass GeoIP2 inputs and choose databases (`5.1`)

`GeoIP2` accepts `ipaddress.IPv4Address` and `IPv6Address` objects.

Country results include continent data and EU membership. City results include
accuracy radius and region name. The result also exposes `dma_code` as
`metro_code` and `region` as `region_code` while retaining the old keys.

When initialized with a directory containing country and city databases,
`GeoIP2` opens only the city database when available. Pass the country database
file path explicitly when country-database behavior is required.

Replace `GeoIP2.coords()` with `lon_lat()` and `GeoIP2.open()` with the
constructor.

## Update map widgets (`6.0`)

`BaseGeometryWidget.base_layer` selects a JavaScript map base layer. Built-in
geometry widgets no longer render inline JavaScript, so update custom widget
templates that depended on the old inline script.

## Validate spatial lookup values (`5.2.17`)

Spatial lookups reject dictionaries and strings that are not valid
`GEOSGeometry` values when those inputs would be passed to `GDALRaster`. This
is backward incompatible. Model-field assignment still accepts those input
types, so validate untrusted data before constructing a lookup.

## Limit nested geometry collections (`5.2.17`)

WKT accepts at most 198 nested `GEOMETRYCOLLECTION` objects. WKB accepts at most
198 collections in total across breadth and depth. `GEOSGeometry`, GIS form
fields, and GIS model fields accept `max_geom_collections` to lower or customize
the limit. GeoJSON input is unaffected.

```python
from django.contrib.gis.geos import GEOSGeometry

geometry = GEOSGeometry(
    "GEOMETRYCOLLECTION EMPTY",
    max_geom_collections=50,
)
```
