# Extended geometry types

JSON-FG adds solid and curved geometry types beyond RFC 7946. Put a primary
extended feature geometry in `place` and declare its conformance class at the
document root.

## Polyhedra

A `Polyhedron` has a non-empty array of shells. Each shell has the coordinate
shape of a GeoJSON `MultiPolygon`:

- the first shell is the exterior;
- later shells represent voids;
- every position has three CRS coordinates, or four values when the last is a
  measure;
- the CRS is three-dimensional or a compound of horizontal and vertical CRSs.

Every shell must be closed, simple, watertight, and nonintersecting. Viewed
from outside the solid, exterior polygons wind counterclockwise and void
polygons wind clockwise.

A `MultiPolyhedron` contains an array of valid polyhedra. Declare the
`polyhedra` conformance class when either type occurs.

## Prisms

A `Prism` extrudes a two-dimensional `base` along the third CRS axis. It has:

- `base`: a two-dimensional geometry;
- `lower`: the lower value on the third axis;
- `upper`: the upper value on the third axis.

`lower` must not exceed `upper`. The containing CRS must be three-dimensional,
but positions in `base` have only two CRS coordinates. They have three values
only when the last is an enabled measure.

A `MultiPrism` aggregates prism objects. Declare the `prisms` conformance class
for either prism type.

```json
{
  "type": "Feature",
  "conformsTo": [
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/core",
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/prisms"
  ],
  "coordRefSys": "http://www.opengis.net/def/crs/OGC/0/Engineering3D",
  "geometry": null,
  "place": {
    "type": "Prism",
    "base": {
      "type": "Polygon",
      "coordinates": [[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]]
    },
    "lower": 0,
    "upper": 10
  },
  "properties": {}
}
```

## Circular strings

A `CircularString` has exactly 3, 5, 7, 9, or 11 positions. Consecutive groups
of three positions describe one to five joined arcs. Within each arc, the
three positions must be distinct and non-collinear.

Only the first two coordinates determine the circular path. Z and M values,
when present, are linearly interpolated along it.

Five positions form a circle when:

- the first and last positions are equal; and
- the two represented arcs have equal radii.

```json
{
  "type": "CircularString",
  "coordinates": [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 0]],
  "conformsTo": [
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/core",
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/circular-arcs"
  ]
}
```

Declare the `circular-arcs` conformance class whenever a circular string or an
aggregate containing one occurs.

## Curved aggregates

`CompoundCurve` joins `LineString` and `CircularString` members end-to-end in
its `geometries` array.

Each boundary item of a `CurvePolygon` is one closed curve of these types:

- `LineString`;
- `CircularString`;
- `CompoundCurve`.

`MultiCurve` aggregates curve objects. `MultiSurface` aggregates `Polygon` and
`CurvePolygon` objects.

When measures are declared above these aggregates, embedded geometries in
`geometries` cannot override that declaration. The same restriction applies to
a prism's embedded `base`.
