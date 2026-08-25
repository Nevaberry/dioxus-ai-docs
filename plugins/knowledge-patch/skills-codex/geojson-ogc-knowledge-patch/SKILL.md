---
name: geojson-ogc-knowledge-patch
description: GeoJSON / OGC JSON-FG
version: OGC JSON-FG 1.0.0
license: MIT
metadata:
  author: Nevaberry
---


# GeoJSON and OGC JSON-FG

Use this skill when producing, validating, or negotiating GeoJSON documents
that use JSON-FG temporal data, alternate coordinate reference systems,
measures, extended geometries, feature typing, or profiles.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/core-objects.md](references/core-objects.md) | Root objects, `conformsTo`, temporal extents, reader behavior |
| [references/crs-and-measures.md](references/crs-and-measures.md) | `geometry` versus `place`, `coordRefSys`, coordinate order, dynamic and compound CRS, M values |
| [references/extended-geometries.md](references/extended-geometries.md) | Polyhedra, prisms, circular strings, compound curves, curve polygons, aggregates |
| [references/schemas-and-api.md](references/schemas-and-api.md) | Feature types, logical schemas, media types, profiles, Web API negotiation |

## Migration-sensitive rules

### Keep the GeoJSON media type

- Emit `application/geo+json`.
- Treat `application/fg+json` and `application/vnd.ogc.fg+json` as
  backward-compatibility values, not preferred media types.
- Identify the representation profile with a `profile` link.
- For Web APIs, accept `profile` on GeoJSON-producing `GET` and `HEAD`
  operations and support at least `rfc7946` and `jsonfg`.
- Default Web API responses to `rfc7946` when the client does not select a
  profile.

### Separate `geometry` from `place`

Use `geometry` for an ordinary RFC 7946 geometry in WGS 84. Omit `place` or set
it to JSON null in that case.

Use `place` when the primary geometry:

- uses an alternate CRS;
- carries measure coordinates; or
- uses an extended JSON-FG geometry type.

When `place` is present, `geometry` may be JSON null or a distinct WGS 84
fallback. The `jsonfg-plus` profile requires a non-null GeoJSON fallback for
every non-null `place`.

Never put `coordRefSys` or `measures` on `geometry`. Do not move an ordinary
point, line, polygon, or geometry collection in CRS84 without measures into
`place`.

### Declare conformance once at the root

Only a root feature, feature collection, or geometry has `conformsTo`. Always
include:

```text
http://www.opengis.net/spec/json-fg-1/1.0/conf/core
```

Add the matching class URI when the capability appears anywhere in the
document:

| Capability | URI suffix |
| --- | --- |
| Polyhedra | `polyhedra` |
| Prisms | `prisms` |
| Circular arcs and curved aggregates | `circular-arcs` |
| Measure coordinates | `measures` |
| Feature types and schemas | `types-schemas` |

Do not repeat conformance declarations on nested objects.

## Core authoring decisions

### Temporal extent

A feature's `time` is absent, JSON null, or an extensible object containing one
or more of:

- `date`: an RFC 3339 `full-date`;
- `timestamp`: an RFC 3339 `date-time` using `Z`;
- `interval`: a closed, two-item range.

Both interval endpoints must be dates or both must be timestamps. Use `..` for
an unbounded endpoint. If the object contains more than one temporal form,
their represented values must intersect.

```json
"time": {
  "interval": ["2014-04-24T10:50:18Z", ".."]
}
```

### Coordinate reference system

`coordRefSys` applies to `place` and to geometries stored in `properties`, but
never to `geometry`. Put it only on the root object; all primary geometries
therefore share that CRS.

Accepted forms are:

- a CRS URI string;
- a `Reference` object with `href` and, for a dynamic CRS, `epoch`;
- an array of references forming an ad hoc compound CRS.

When `coordRefSys` is absent, two-dimensional positions use OGC:CRS84 and
three-dimensional positions use OGC:CRS84h. Do not count a measure coordinate
when selecting that default. Follow the axis order defined by the closest CRS.
For a local unknown CRS, use the OGC `Engineering2D` or `Engineering3D` URI.

### Measure coordinates

A `measures` object has required Boolean `enabled` and optional `unit` and
`description`. When enabled, append M after all CRS coordinates:

- a 2D CRS position has `[x, y, m]`;
- a 3D CRS position has `[x, y, z, m]`.

The declaration scopes down from its containing object. A directly embedded
geometry in `geometries` or `base` cannot override it. If no enabled declaration
is in scope, positions have no M coordinate.

## Extended geometry quick reference

### Solids and extrusions

| Type | Essential shape and constraints |
| --- | --- |
| `Polyhedron` | Non-empty array of MultiPolygon-shaped shells; exterior first, then voids |
| `MultiPolyhedron` | Array of valid polyhedra |
| `Prism` | 2D `base` extruded between `lower` and `upper` on CRS axis 3 |
| `MultiPrism` | Aggregate of prism objects |

Polyhedron positions contain three CRS coordinates or four values with M.
Shells are closed, simple, watertight, nonintersecting, and use a 3D or
horizontal-plus-vertical compound CRS. Viewed from outside, exterior polygons
are counterclockwise and void polygons are clockwise.

A prism's `lower` must not exceed `upper`. Its containing CRS is 3D, but base
positions contain two CRS coordinates, plus an optional final M.

### Arcs and curved aggregates

A `CircularString` has 3, 5, 7, 9, or 11 positions, describing one through five
connected three-point arcs. Within each arc, the three positions are distinct
and non-collinear. Only the first two coordinates define the arc; Z and M are
linearly interpolated. Five positions form a circle when the first and last
positions match and the arcs have equal radii.

- `CompoundCurve` joins `LineString` and `CircularString` members end-to-end in
  `geometries`.
- Each `CurvePolygon` member is a closed line string, circular string, or
  compound curve.
- `MultiCurve` aggregates curves.
- `MultiSurface` aggregates polygons and curve polygons.

## Types and schemas

When using the `types-schemas` class:

- a root feature has a string `featureType`;
- a feature collection declares `featureType` once at collection level or on
  every contained feature;
- a homogeneous collection should declare its shared type and
  `geometryDimension`.

Use `geometryDimension` value `0` for points, `1` for curves, `2` for surfaces,
and `3` for solids or prisms. Use JSON null for mixed or unknown dimensions.

Use a URI string for `featureSchema` when all features have one type. For
multiple types, use an object mapping every feature-type code to its schema
URI. These are logical OGC API Features Part 5 schemas, not directly JSON
validation schemas. Provide a `describedby` link when clients need a
downloadable JSON Schema.

## Profile behavior

| Profile | Meaning |
| --- | --- |
| `rfc7946` | Plain RFC 7946 GeoJSON |
| `jsonfg` | Core JSON-FG |
| `jsonfg-plus` | JSON-FG with a GeoJSON fallback for every non-null `place` |

An `rfc7946` response has no `place` and no JSON-FG conformance URI.
Non-WGS 84 coordinates in that profile require prior arrangement.

Some restrictive GeoJSON clients expose only `id`, `geometry`, `bbox`, and
`properties`. For those clients, also copy JSON-FG members into `properties`.

## Validation checklist

1. Confirm that `conformsTo` occurs only at the root and contains `core`.
2. Add every extension class URI used anywhere in the document.
3. Keep ordinary WGS 84 GeoJSON in `geometry`; route alternate CRS, M, and
   extended geometry to `place`.
4. Check temporal syntax, matching interval endpoint types, and intersection.
5. Resolve the CRS, axis order, position dimension, and measure position
   together.
6. Validate topology and orientation for solids and connectivity for curves.
7. Check `featureType`, `geometryDimension`, and `featureSchema` consistency.
8. Negotiate the expected media type and profile.
9. Ignore unknown JSON-FG members when reading; map an unrecognized `place`
   geometry type to JSON null.
