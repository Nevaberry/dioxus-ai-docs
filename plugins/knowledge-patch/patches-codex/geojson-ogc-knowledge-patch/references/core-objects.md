# Root objects and temporal data

These rules apply to JSON-FG 1.0.0 documents that extend GeoJSON root features,
feature collections, and geometries with foreign members and additional
geometry types.

## Root conformance declaration

Only the root object has a `conformsTo` array. It always contains the Core URI:

```text
http://www.opengis.net/spec/json-fg-1/1.0/conf/core
```

If any object anywhere in the document uses an extension capability, the root
also declares that capability's conformance class:

| Capability | Conformance class URI |
| --- | --- |
| Polyhedra | `http://www.opengis.net/spec/json-fg-1/1.0/conf/polyhedra` |
| Prisms | `http://www.opengis.net/spec/json-fg-1/1.0/conf/prisms` |
| Circular arcs | `http://www.opengis.net/spec/json-fg-1/1.0/conf/circular-arcs` |
| Measures | `http://www.opengis.net/spec/json-fg-1/1.0/conf/measures` |
| Types and schemas | `http://www.opengis.net/spec/json-fg-1/1.0/conf/types-schemas` |

An ordinary root geometry can therefore look like:

```json
{
  "type": "Point",
  "coordinates": [8.5, 50.1],
  "conformsTo": [
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/core"
  ]
}
```

## Feature time

The `time` member of a feature may be:

- absent;
- JSON null; or
- an extensible object containing `date`, `timestamp`, `interval`, or a
  combination of those members.

Use an RFC 3339 `full-date` for `date`. Use an RFC 3339 `date-time` ending in
`Z` for `timestamp`.

An `interval` is a closed, two-item range. Its endpoints must have the same
kind: both dates or both timestamps. The string `..` replaces either endpoint
to represent an unbounded side.

```json
{
  "time": {
    "interval": ["2014-04-24T10:50:18Z", ".."]
  }
}
```

If `date`, `timestamp`, and/or `interval` appear together, the values they
represent must intersect. Do not use multiple temporal forms to state
disjoint alternatives.

## Reader tolerance

Readers ignore unknown JSON-FG members, preserving normal foreign-member
extensibility. If a reader does not recognize the geometry type in `place`, it
maps that geometry to JSON null rather than treating it as a known geometry.
