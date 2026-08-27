# Extended geometries

## Polyhedra

A `Polyhedron` stores a non-empty array of shells. Each shell has the
coordinate shape of a MultiPolygon. The first shell is the exterior; each
later shell describes a void.

Positions contain three spatial coordinates, or four values when the last is a
measure. Use a three-dimensional CRS or a compound CRS combining horizontal
and vertical components.

Every shell must be:

- closed;
- simple;
- watertight;
- nonintersecting with the other shells.

When viewed from outside the solid, exterior polygons run counterclockwise and
void polygons run clockwise. A `MultiPolyhedron` contains valid polyhedra.

Declare the root class URI ending in `polyhedra` if either type occurs.

## Prisms

A `Prism` extrudes a two-dimensional `base` between `lower` and `upper` values
on the third axis of the containing CRS. `lower` must be less than or equal to
`upper`.

The containing CRS is three-dimensional. Positions in `base` have two spatial
coordinates, or three values when the final value is a measure. A
`MultiPrism` aggregates prism objects.

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
      "coordinates": [
        [[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]
      ]
    },
    "lower": 0,
    "upper": 10
  },
  "properties": {}
}
```

Declare the root class URI ending in `prisms` when a prism occurs.

## Circular strings

A `CircularString` has 3, 5, 7, 9, or 11 positions. Those lengths represent
one through five connected three-point circular arcs.

For each arc:

- the three positions are distinct;
- the three positions are non-collinear;
- only the first two coordinates determine the circular geometry;
- Z and M values are linearly interpolated.

Five positions describe a circle when the first and last positions are equal
and the connected arcs have equal radii.

```json
{
  "type": "CircularString",
  "coordinates": [
    [1, 0],
    [0, 1],
    [-1, 0],
    [0, -1],
    [1, 0]
  ],
  "conformsTo": [
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/core",
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/circular-arcs"
  ]
}
```

## Curved aggregates

- `CompoundCurve` places `LineString` and `CircularString` members in
  `geometries`; consecutive members join end-to-end.
- A `CurvePolygon` is built from closed line strings, circular strings, or
  compound curves.
- `MultiCurve` aggregates curve geometries.
- `MultiSurface` aggregates polygons and curve polygons.

Declare the root class URI ending in `circular-arcs` whenever circular strings
or these curved aggregate capabilities occur.
