# Profiles, media types, and Web APIs

## Media type

Serve JSON-FG as `application/geo+json`. The older
`application/fg+json` and `application/vnd.ogc.fg+json` media types exist only
for backward compatibility.

## Representation profiles

Use these OGC profile URI endings:

| Ending | Representation |
| --- | --- |
| `rfc7946` | Plain RFC 7946 GeoJSON |
| `jsonfg` | Core JSON-FG |
| `jsonfg-plus` | JSON-FG with a GeoJSON fallback for every non-null `place` |

For `jsonfg-plus`, every non-null `place` is accompanied by a non-null RFC 7946
geometry in `geometry`.

Declare the selected full profile URI in a `Link` with `rel="profile"`:

```http
GET /collections/airports/items?profile=jsonfg
Accept: application/geo+json

Link: <http://www.opengis.net/def/profile/OGC/0/jsonfg>; rel="profile"
```

## Web API negotiation

A conforming JSON-FG Web API supports a `profile` parameter on
GeoJSON-producing `GET` and `HEAD` operations. It supports at least `rfc7946`
and `jsonfg`, and should default to `rfc7946` when the client does not select a
profile.

The `rfc7946` profile has no `place` member and no JSON-FG conformance URI.
Non-WGS 84 coordinates in this profile are permitted only by prior arrangement
between the parties.

## Restrictive GeoJSON clients

Some clients expose only `id`, `geometry`, `bbox`, and `properties`. When such
clients must retain JSON-FG metadata, copy the JSON-FG members into
`properties` as well as publishing them in their normal locations.
