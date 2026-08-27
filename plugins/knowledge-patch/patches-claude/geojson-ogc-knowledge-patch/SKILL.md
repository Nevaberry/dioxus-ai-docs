---
name: geojson-ogc-knowledge-patch
description: GeoJSON / OGC JSON-FG
version: "OGC JSON-FG 1.0.0"
license: MIT
metadata:
  author: Nevaberry
---


# GeoJSON / OGC JSON-FG Knowledge Patch

Use this skill when producing, validating, transforming, or serving JSON-FG,
especially where an RFC 7946 fallback must coexist with alternate coordinate
reference systems, measures, extended geometry types, or typed features.

Treat the reference files as normative implementation guidance. Start with the
quick rules below, then open the task-specific reference before editing data,
schemas, validators, or HTTP behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core objects, time, and CRS](references/core-objects-time-crs.md) | Root conformance declarations, temporal extents, `geometry` versus `place`, CRS forms and defaults, reader behavior |
| [Extended geometry types](references/extended-geometries.md) | Polyhedra, prisms, circular arcs, compound curves, curve polygons, multis |
| [Measures, feature types, and schemas](references/measures-types-schemas.md) | M-coordinate scoping, `featureType`, `geometryDimension`, logical feature schemas |
| [Profiles and Web APIs](references/profiles-web-api.md) | Media types, profile URIs, content negotiation, fallbacks for restrictive clients |

## Breaking and compatibility-sensitive rules

### Keep the media type stable

Use `application/geo+json` for JSON-FG representations. Treat
`application/fg+json` and `application/vnd.ogc.fg+json` only as compatibility
values for earlier implementations.

Do not infer the representation profile from a legacy media type. Use a
profile link and, for Web APIs, the `profile` query parameter.

### Separate RFC 7946 geometry from extended geometry

Use `geometry` only for an ordinary RFC 7946 geometry in WGS 84. It cannot
carry `coordRefSys` or `measures`.

Use `place` for a geometry that:

- uses an alternate CRS;
- has a measure coordinate; or
- uses a JSON-FG extended geometry type.

When `place` is present, `geometry` may be `null` or a distinct WGS 84 fallback
for GeoJSON-only readers. Do not copy alternate-CRS coordinates into
`geometry`.

An ordinary `Point`, `LineString`, `Polygon`, or collection in CRS84 without
measures does not belong in `place`; keep it in `geometry` and omit or null
`place`.

### Put CRS metadata in the right scope

`coordRefSys` applies to `place` and to geometries inside `properties`, never
to `geometry`. In core documents, declare it only on the root object, so all
primary geometries use the same CRS.

Do not assume longitude-latitude ordering after selecting another CRS.
Coordinate order follows the axis order defined by the closest applicable CRS.

### Declare conformance once, completely

Only the root object has `conformsTo`. Always include the core conformance URI:

```text
http://www.opengis.net/spec/json-fg-1/1.0/conf/core
```

If a capability occurs anywhere in the document, also add its class URI. The
recognized suffixes are:

- `polyhedra`
- `prisms`
- `circular-arcs`
- `measures`
- `types-schemas`

Nested geometries do not repeat `conformsTo`.

## Common authoring patterns

### Publish an alternate-CRS feature with a fallback

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

The two coordinate arrays describe the same feature for different readers;
they are not required to be bytewise copies.

### Select a CRS representation

Set `coordRefSys` to one of:

- a CRS URI string;
- a `Reference` object with `href`, and optionally `epoch` for a dynamic CRS;
  or
- an array of references for an ad hoc compound CRS.

If omitted, two-dimensional positions default to OGC:CRS84 and
three-dimensional positions default to OGC:CRS84h. Do not count an appended M
value when choosing between those defaults.

For a local CRS whose definition is unknown, use the OGC `Engineering2D` or
`Engineering3D` CRS URI as appropriate.

### Add a temporal extent

`time` may be absent, `null`, or an extensible object containing any of
`date`, `timestamp`, and `interval`.

```json
{
  "time": {
    "interval": ["2014-04-24T10:50:18Z", ".."]
  }
}
```

Use RFC 3339 `full-date` values for `date` and RFC 3339 `date-time` values with
`Z` for `timestamp`. An interval is a closed two-item range. Both endpoints
must be dates or both must be timestamps; `..` makes an endpoint unbounded.
When multiple temporal forms occur, their represented values must intersect.

### Append measure values consistently

Declare a `measures` object with required Boolean `enabled`; optionally add
`unit` and `description`. When enabled, append one M value after every
position's CRS coordinates:

- a 2D CRS produces three-element positions;
- a 3D CRS produces four-element positions.

The declaration scopes downward. Directly embedded geometries in `geometries`
or `base` cannot override it. Absence means that positions have no M value.

```json
{
  "type": "LineString",
  "coordRefSys": "http://www.opengis.net/def/crs/OGC/0/CRS84",
  "measures": {
    "enabled": true,
    "unit": "km",
    "description": "distance from route origin"
  },
  "coordinates": [[8.0, 50.0, 0.0], [8.1, 50.1, 15.7]],
  "conformsTo": [
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/core",
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/measures"
  ]
}
```

### Describe feature collections

Under the `types-schemas` conformance class, give a root feature a string
`featureType`. For a feature collection, either set it once at collection
level or set it on every feature.

For a homogeneous collection, declare its shared type and a
`geometryDimension`: `0` for points, `1` for curves, `2` for surfaces, and `3`
for solids or prisms. Use `null` for a mixed or unknown dimension.

Use `featureSchema` for a logical feature schema conforming to OGC API Features
Part 5. It is a URI string for one feature type or an object mapping type codes
to schema URIs for multiple types. It is not directly a JSON validation
schema; provide a `describedby` link for a downloadable JSON Schema.

## Extended geometry checklist

Before emitting an extended geometry, verify all of the following:

- the root declares the corresponding conformance class;
- the geometry is in `place` when used as a feature's primary extended shape;
- the root CRS has the dimensions required by the geometry;
- every position has the CRS coordinate count plus an M value only when
  measures are enabled;
- rings, shells, curve joins, and bounds satisfy the type-specific rules in
  [Extended geometry types](references/extended-geometries.md).

For unknown members, readers should continue processing. For an unrecognized
`place.type`, readers should treat `place` as `null` rather than rejecting the
whole feature.

## Web API checklist

For GeoJSON-producing `GET` and `HEAD` operations:

1. Support the `profile` parameter with at least `rfc7946` and `jsonfg`.
2. Prefer `rfc7946` when no profile is requested.
3. Return `application/geo+json`.
4. Add a `Link` with `rel="profile"` for the selected profile URI.
5. For `jsonfg-plus`, include a non-null RFC 7946 `geometry` fallback whenever
   `place` is non-null.

The `rfc7946` profile has neither `place` nor a JSON-FG conformance URI.
Non-WGS 84 coordinates in that profile require prior arrangement between the
parties.
