# Measures, feature types, and schemas

## Measure declarations

`measures` declares whether positions append an M coordinate. It is an object
with:

- required Boolean `enabled`;
- optional `unit`;
- optional `description`.

When enabled, every position appends the M value after all coordinates defined
by the CRS. A 2D CRS therefore uses three values per position; a 3D CRS uses
four. Do not count M as part of the CRS dimension.

The declaration scopes down from its containing object. A directly embedded
geometry inside `geometries` or `base` cannot override the inherited setting.
When no declaration applies, positions have no M coordinate.

Declare the root `measures` conformance class if measures occur anywhere in the
document.

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

## Feature types

The following members are used under the `types-schemas` conformance class.

A root feature must have a string `featureType`. A feature collection chooses
one of two placements:

1. Put `featureType` once at collection level.
2. Put `featureType` on every contained feature.

For a homogeneous collection, prefer the collection-level shared type and add
`geometryDimension`:

| Value | Geometry category |
| --- | --- |
| `0` | Point |
| `1` | Curve |
| `2` | Surface |
| `3` | Solid or prism |
| `null` | Mixed or unknown |

## Feature schemas

`featureSchema` identifies logical schemas conforming to OGC API Features Part
5:

- for a single feature type, use one URI string;
- for multiple feature types, use an object that maps each feature-type code
  to its schema URI.

These logical feature schemas are not directly JSON validation schemas. If a
client needs a downloadable JSON Schema, expose it through a `describedby`
link.

```json
{
  "type": "FeatureCollection",
  "featureType": "Airport",
  "featureSchema": "https://demo.ldproxy.net/zoomstack/collections/airports/schema",
  "geometryDimension": 0,
  "conformsTo": [
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/core",
    "http://www.opengis.net/spec/json-fg-1/1.0/conf/types-schemas"
  ],
  "features": []
}
```
