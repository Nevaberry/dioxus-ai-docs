# Plugins, APIs, and User Interface

## QGIS 4 plugin migration

### Advertise compatibility with a version range

The `qgis4-plugin-migration` guidance uses `qgisMinimumVersion` and the
optional `qgisMaximumVersion` as the compatibility contract. When the maximum
is absent, QGIS assumes support only through the end of the minimum version's
major line. To retain QGIS 3.22 support and join the QGIS 4 Ready list, use:

```ini
[general]
qgisMinimumVersion=3.22
qgisMaximumVersion=4.99
```

The Ready list includes a plugin if either bound is at least 4.0.

### Remove `supportsQt6`

`supportsQt6=True` has been removed from QGIS core and is not recognized. It
cannot advertise QGIS 4 support; remove it and use the version range.

### Complete the Qt 6 migration first

Replace Qt 5-only APIs and direct `PyQt5` imports with Qt 6 equivalents,
preferably through `qgis.PyQt`, and test on QGIS 4 before widening plugin
metadata. Repository uploads run `pyqgis4-checker`; its Qt6 Check tab identifies
affected files and lines, but findings do not block upload or approval.

## Settings, themes, and UI extension

### Isolated settings

Since 4.2, QGIS 4 stores settings separately from QGIS 3. First startup makes a
one-time, lossless copy of the loaded QGIS 3 profile. Later changes do not
synchronize, so installation, profile-management, and enterprise-deployment
scripts must target the new location.

### Plugin-delivered application themes

Since 4.0, plugins can ship themes and custom application styles. Installing a
plugin can therefore change the application's appearance without a matching
core theme.

### User-defined menus and toolbars

Since 4.0, users can create menus and toolbars instead of only customizing
built-in ones. Since 4.2, a Processing algorithm can be assigned to one of
these UI containers; its action opens the parameter and execution dialog.

## Widgets and application services

### Value Relation ordering

Since 3.42, Value Relation widgets can reverse their order or sort choices by a
specified field.

### GPS plugin controls

Since 3.44, PyQGIS exposes `QgsAppGpsTools` through `iface.gpsTools()`. Create a
feature from the current track with:

```python
iface.gpsTools().createFeatureFromGpsTrack()
```

Change the track symbol and update its geometry with:

```python
iface.gpsTools().setGpsTrackLineSymbol(line_symbol)
```

### Topocentric CRS selection

Since 4.2, QGIS supports topocentric coordinate reference systems. The CRS
chooser enables an origin-point widget when Topocentric CRS is selected
explicitly.

## Expression APIs

### String and CRS functions

Since 3.44, string forms of `repeat` and `reverse` are available. Use
`crs_from_text` for authority codes, WKT, or PROJ definitions and
`crs_to_authid` to obtain an `authority:id` string:

```text
repeat('ab', 3)
reverse('abc')
crs_to_authid(crs_from_text('EPSG:4326'))
```

### Magnetic-model functions

Since 4.0, expressions provide `magnetic_declination`,
`magnetic_inclination`, `magnetic_declination_rate_of_change`, and
`magnetic_inclination_rate_of_change`. They return angles or annual rates at a
point.

### Time-zone functions

Since 4.0, `timezone_from_id`, `timezone_id`, and `get_timezone` create or
inspect IANA time zones. `convert_timezone` changes a datetime to the equivalent
time in another zone. `set_timezone` replaces the zone without changing the
date or time components.

### Cubic Bézier and joined concatenation

Since 4.2, `scale_cubic_bezier` performs cubic Bézier interpolation and can
convert MapBox `cubic-bezier` styles. `concat_ws(separator, ...)` ignores NULL
arguments; `concat_ws('-', 'a', NULL, 'b')` returns `a-b`.

## Geometry and layer APIs

### Direct GEOS access and dimensional arrays

Since 3.42, PyQGIS exposes `QgsGeos` directly for GEOS-specific operations not
available from the base `QgsGeometryEngine`. `QgsGeometry.as_numpy()` preserves
dimensionality, returning XY, XYZ, XYM, or XYZM coordinates as applicable.

### Geometry and GeoPandas additions

Since 4.0, `QgsGeometry.area3D()` returns surface area for polygons, polyhedral
surfaces, TINs, and collections; it returns zero for points and lines.
`QgsGeometryUtilsBase::pointsAreCollinear` accepts 2D and 3D points, and
`QgsGeometryUtilsBase::points3DAreCollinear` is available explicitly.
`QgsVectorLayer.as_geopandas()` converts geometry and attributes to a GeoPandas
dataframe when GeoPandas is installed.

### Layer-tree custom nodes

Since 4.0, `QgsLayerTreeCustomNode` lets APIs represent non-layer application
objects in layer trees. This is used by synchronized elevation profiles and is
available to other tree-based extensions.

## 3D plugin extension points

Since 4.0, plugins can derive tools from `Qgs3DMapTool`, apply the cross-section
tool's four clipping planes, and use `Qgs3DMapCanvas.castRay()` to obtain and
manage 3D hits through `QgsRay3D`.

## Project trust and translated metadata

### Granular embedded-Python trust

Since 4.0, project trust is separate for macros, expression functions, actions,
and attribute-form initialization code. The trust dialog previews code, while
global policy can allow or deny execution by project or path.

### Translatable metadata

Since 4.0, key project and layer metadata can be translated. Those localized
values can feed layout labels, map decorations, and other consumers.
