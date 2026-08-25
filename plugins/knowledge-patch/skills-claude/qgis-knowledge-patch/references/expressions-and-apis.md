# Expressions and APIs

Use this reference for expression syntax and semantics, PyQGIS geometry and GPS
access, GeoPandas conversion, SFCGAL wrappers, 3D plugin extension points, and
CRS construction.

## `QgsGeos` in PyQGIS (since 3.42)

PyQGIS exposes `QgsGeos` directly, making GEOS-specific functionality that is
not available through the base `QgsGeometryEngine` accessible to Python code.

## Dimensional `QgsGeometry.as_numpy()` output (since 3.42)

`QgsGeometry.as_numpy()` preserves dimensionality. Geometries carrying Z
and/or M values return XYZ, XYM, or XYZM coordinates instead of always
returning XY.

## String and CRS expression functions (since 3.44)

Expressions include string forms of `repeat` and `reverse`, `crs_from_text`
for authority codes, WKT, or PROJ definitions, and `crs_to_authid` for an
`authority:id` result:

```qgis
repeat('ab', 3)
reverse('abc')
crs_to_authid(crs_from_text('EPSG:4326'))
```

## GPS controls for plugins (since 3.44)

PyQGIS exposes `QgsAppGpsTools` through `iface.gpsTools()`. Plugins can create
a feature from the current track or replace the track's line symbol:

```python
iface.gpsTools().createFeatureFromGpsTrack()
iface.gpsTools().setGpsTrackLineSymbol(line_symbol)
```

The symbol setter also updates the track geometry.

## Magnetic-model expressions (since 4.0)

Use `magnetic_declination`, `magnetic_inclination`,
`magnetic_declination_rate_of_change`, and
`magnetic_inclination_rate_of_change` for angles or annual rates at a point.

## Time-zone expressions (since 4.0)

`timezone_from_id`, `timezone_id`, and `get_timezone` create or inspect IANA
time zones. `convert_timezone` changes a datetime to the equivalent time in
another zone. `set_timezone` replaces the zone without changing the date or
time components.

## Native SFCGAL integration (since 4.0)

QGIS can use SFCGAL via `QgsSfcgalEngine` and the conversion-reducing
`QgsSfcgalGeometry` wrapper. Approximate Medial Axis creates a simplified line
skeleton from a shape's 2D projection and ignores Z.

## Geometry and GeoPandas APIs (since 4.0)

`QgsGeometry.area3D()` returns surface area for polygons, polyhedral surfaces,
TINs, and collections, and zero for points and lines.
`QgsGeometryUtilsBase::pointsAreCollinear` handles 2D and 3D points, alongside
the new `QgsGeometryUtilsBase::points3DAreCollinear`.
`QgsVectorLayer.as_geopandas()` converts a layer and its attributes to a
GeoPandas dataframe when GeoPandas is installed.

## PyQGIS 3D extension points (since 4.0)

Plugins can derive canvas tools from `Qgs3DMapTool`, apply the cross-section
tool's four clipping planes, and call `Qgs3DMapCanvas.castRay()`. Ray hits are
obtained and managed through `QgsRay3D`.

## Cubic Bézier scaling and joined concatenation (since 4.2)

`scale_cubic_bezier` performs cubic Bézier interpolation and can convert
MapBox `cubic-bezier` styles. `concat_ws(separator, ...)` ignores NULL
arguments:

```qgis
concat_ws('-', 'a', NULL, 'b')  -- a-b
```

## Topocentric CRS support (since 4.2)

QGIS supports topocentric coordinate reference systems. The CRS chooser shows
an origin-point widget when Topocentric CRS is explicitly selected.
