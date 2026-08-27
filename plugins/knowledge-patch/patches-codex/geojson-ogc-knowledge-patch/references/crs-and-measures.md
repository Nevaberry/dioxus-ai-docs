# Coordinate reference systems and measures

## Choosing `geometry` and `place`

Keep an ordinary RFC 7946 geometry in WGS 84 in `geometry`, with `place` absent
or JSON null.

Put the primary geometry in `place` if it uses an alternate CRS, includes a
measure coordinate, or has an extended JSON-FG type. In that case, `geometry`
may be JSON null or may contain a distinct WGS 84 fallback for GeoJSON-only
readers.

The `geometry` value cannot carry `coordRefSys` or `measures`. Conversely, do
not put an ordinary point, line, polygon, or geometry collection in CRS84 with
no measures in `place`.

```json
{
  "type": "Feature",
  "conformsTo": [
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/core"
  ],
  "coordRefSys": "http://www.opengis.net/def/crs/EPSG/0/27700",
  "geometry": {
    "type": "Point",
    "coordinates": [-6.2580609, 55.6824121]
  },
  "place": {
    "type": "Point",
    "coordinates": [132440.63, 651435.92]
  },
  "properties": {}
}
```

## `coordRefSys`

`coordRefSys` controls `place` and geometries in `properties`; it never
controls `geometry`. Put it only on the root object. Consequently, all primary
geometries in the root document share a CRS.

The member accepts:

1. A CRS URI string.
2. A reference object:

   ```json
   {
     "type": "Reference",
     "href": "https://example.com/crs",
     "epoch": 2017.23
   }
   ```

   Use `epoch` for a dynamic CRS.
3. An array of reference values describing an ad hoc compound CRS.

If `coordRefSys` is absent, use OGC:CRS84 for two-dimensional positions and
OGC:CRS84h for three-dimensional positions. Ignore any appended measure
coordinate when deciding whether the spatial position is 2D or 3D.

Coordinate order follows the axis order defined by the closest CRS. Do not
assume longitude-first ordering for a CRS that defines different axes.

For coordinates in a local system whose CRS is unknown, use the URI for OGC
`Engineering2D` or `Engineering3D`, according to spatial dimension.

## Measure declaration and position layout

`measures` is an object with:

- required Boolean `enabled`;
- optional `unit`;
- optional `description`.

With measures enabled, every position appends M after the CRS coordinates:

| Spatial CRS | Position |
| --- | --- |
| 2D | `[x, y, m]` |
| 3D | `[x, y, z, m]` |

The declaration applies recursively below its containing object. A geometry
directly embedded in a `geometries` or `base` member cannot override the
inherited declaration. When no declaration is present, no M coordinate is in
scope.

```json
{
  "type": "LineString",
  "coordRefSys": "http://www.opengis.net/def/crs/OGC/0/CRS84",
  "measures": {
    "enabled": true,
    "unit": "km",
    "description": "distance from route origin"
  },
  "coordinates": [
    [8.0, 50.0, 0.0],
    [8.1, 50.1, 15.7]
  ],
  "conformsTo": [
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/core",
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/measures"
  ]
}
```
