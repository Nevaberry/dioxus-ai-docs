# Core objects, time, and coordinate reference systems

These rules apply to JSON-FG root features, feature collections, and
geometries (since 1.0.0). JSON-FG extends GeoJSON through foreign members and
additional geometry types.

## Root conformance declarations

Only a root object has `conformsTo`. Its array always contains:

```text
http://www.opengis.net/spec/json-fg-1/1.0/conf/core
```

Add a capability class URI whenever that capability appears anywhere below the
root:

| Capability | Class URI |
| --- | --- |
| Polyhedra | `http://www.opengis.net/spec/json-fg-1/1.0/conf/polyhedra` |
| Prisms | `http://www.opengis.net/spec/json-fg-1/1.0/conf/prisms` |
| Circular arcs | `http://www.opengis.net/spec/json-fg-1/1.0/conf/circular-arcs` |
| Measures | `http://www.opengis.net/spec/json-fg-1/1.0/conf/measures` |
| Feature types and schemas | `http://www.opengis.net/spec/json-fg-1/1.0/conf/types-schemas` |

Do not put `conformsTo` on nested features or geometries.

```json
{
  "type": "Point",
  "coordinates": [8.5, 50.1],
  "conformsTo": [
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/core"
  ]
}
```

## Temporal extent

A feature's `time` member may be absent, `null`, or an extensible object. The
object can carry one or more of:

- `date`: an RFC 3339 `full-date`;
- `timestamp`: an RFC 3339 `date-time` using `Z`;
- `interval`: a closed two-item range.

The two bounded interval endpoints must use the same form: both dates or both
timestamps. Use the string `..` as either endpoint to mean unbounded. When an
object supplies multiple temporal forms, their values must intersect.

```json
{
  "time": {
    "interval": ["2014-04-24T10:50:18Z", ".."]
  }
}
```

## Choosing `geometry` and `place`

`geometry` is the RFC 7946 compatibility channel. Put an ordinary WGS 84
GeoJSON geometry there and omit or null `place`.

`place` is the JSON-FG channel for a primary geometry that has any of these
properties:

- coordinates use a CRS other than WGS 84;
- positions append a measure value;
- the geometry uses a JSON-FG extended type.

With a non-null `place`, `geometry` can be `null` or a distinct WGS 84 fallback
for GeoJSON-only readers. The fallback must remain a valid RFC 7946 geometry.
It cannot have `coordRefSys` or `measures`.

Do not put an ordinary point, line, polygon, or collection in CRS84 without
measures in `place`; use `geometry`.

## `coordRefSys` scope and forms

`coordRefSys` applies to `place` and to geometry values carried in
`properties`. It never applies to `geometry`. Core documents allow it only on
the root object, which gives all primary geometries a shared CRS.

The value can be:

1. A CRS URI.
2. A `Reference` object. Use `href` for the CRS URI and `epoch` when a dynamic
   CRS needs a coordinate epoch.
3. An array of references for an ad hoc compound CRS.

```json
{
  "type": "Reference",
  "href": "https://example.test/crs/dynamic",
  "epoch": 2017.23
}
```

When `coordRefSys` is absent, two-dimensional positions default to OGC:CRS84
and three-dimensional positions default to OGC:CRS84h. An appended measure
coordinate does not affect that dimension choice.

Coordinate order follows the axis order defined by the nearest applicable CRS;
do not force RFC 7946 longitude-latitude order on other CRSs. For a local,
unknown CRS, use the OGC `Engineering2D` or `Engineering3D` CRS URI.

```json
{
  "type": "Feature",
  "conformsTo": [
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/core"
  ],
  "coordRefSys": "http://www.opengis.net/def/crs/EPSG/0/27700",
  "geometry": {"type": "Point", "coordinates": [-6.2580609, 55.6824121]},
  "place": {"type": "Point", "coordinates": [132440.63, 651435.92]},
  "properties": {}
}
```

## Forward-compatible reading

Ignore unknown JSON-FG members so documents can grow foreign members safely.
If `place` has an unrecognized geometry type, map the `place` value to `null`;
do not reject the entire enclosing object solely for that type.
