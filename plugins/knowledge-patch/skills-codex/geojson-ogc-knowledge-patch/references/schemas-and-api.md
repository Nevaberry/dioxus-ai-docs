# Feature schemas and Web API profiles

## Feature types and geometry dimension

Under the `types-schemas` conformance class, a root feature has a string
`featureType`.

A feature collection either:

- declares `featureType` once at collection level; or
- declares `featureType` on every feature.

A homogeneous collection should declare the shared feature type and a
`geometryDimension`:

| Value | Geometry category |
| --- | --- |
| `0` | Point |
| `1` | Curve |
| `2` | Surface |
| `3` | Solid or prism |
| JSON null | Mixed or unknown |

## Logical feature schemas

When all features have one type, `featureSchema` is a URI string. When
multiple types occur, it is an object mapping each feature-type code to that
type's schema URI.

These schema resources are logical schemas conforming to OGC API Features Part
5. They are not directly JSON-validation schemas. If consumers need a
downloadable JSON Schema, publish a `describedby` link.

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

## Media type

Use `application/geo+json` as the preferred media type. The older
`application/fg+json` and `application/vnd.ogc.fg+json` media types remain
only for backward compatibility.

## Representation profiles

| URI ending | Representation |
| --- | --- |
| `rfc7946` | Plain RFC 7946 GeoJSON |
| `jsonfg` | Core JSON-FG |
| `jsonfg-plus` | JSON-FG in which every non-null `place` has a non-null GeoJSON fallback in `geometry` |

Declare the selected profile URI using a link whose relation is `profile`.

```http
GET /collections/airports/items?profile=jsonfg
Accept: application/geo+json

Link: <http://www.opengis.net/def/profile/OGC/0/jsonfg>; rel="profile"
```

## Web API negotiation

A conforming JSON-FG Web API supports the `profile` parameter on
GeoJSON-producing `GET` and `HEAD` operations. It supports at least `rfc7946`
and `jsonfg`, and should use `rfc7946` by default.

In the `rfc7946` profile:

- `place` does not occur;
- no JSON-FG conformance URI occurs;
- non-WGS 84 coordinates are allowed only by prior arrangement.

Some restrictive GeoJSON clients expose only the standard members `id`,
`geometry`, `bbox`, and `properties`. To keep JSON-FG values visible to those
clients, publishers should also copy JSON-FG members into `properties`.
