# NTRIP Protocol

NTRIP (Networked Transport of RTCM via Internet Protocol) streams RTCM3 corrections over HTTP. Two versions are in use.

## v1 vs v2 Comparison

| Feature | NTRIP v1 | NTRIP v2 |
|---------|----------|----------|
| HTTP version | HTTP/1.0 | HTTP/1.1 |
| Success response | `ICY 200 OK` | `HTTP/1.1 200 OK` |
| Content-Type | none | `gnss/data` |
| Chunked transfer | no | yes |
| Base station upload | `SOURCE` command | `POST` method |
| Version header | none | `Ntrip-Version: Ntrip/2.0` |

## Client Connection Examples

```
# v1 request (HTTP/1.0, simpler)
GET /mountPt HTTP/1.0
User-Agent: NTRIP software/version
Authorization: Basic dXNlcjpwYXNzd29yZA==

# v1 success response
ICY 200 OK

# v2 request (HTTP/1.1, adds Host + version header)
GET /mountPt HTTP/1.1
Host: caster.example.com:2101
Ntrip-Version: Ntrip/2.0
User-Agent: NTRIP software/version
Authorization: Basic dXNlcjpwYXNzd29yZA==

# v2 success response
HTTP/1.1 200 OK
Content-Type: gnss/data
```

## Authentication

Authorization is Base64-encoded `user:password` in a standard HTTP `Authorization: Basic` header. Same mechanism for both versions.

## Practical Notes

- **RTKLIB only supports v1.** Most low-cost GNSS devices also only support v1.
- **VRS (Virtual Reference Station) casters** require the client to send NMEA GGA position sentences before corrections are streamed. The caster uses the client position to generate a virtual base station.
- Default caster port is **2101**.
- Sourcetable is fetched with `GET / HTTP/1.0` (v1) or `GET / HTTP/1.1` (v2) — returns a list of available mountpoints with metadata.

## Base Station Upload

```
# v1: SOURCE command (non-standard HTTP)
SOURCE password /mountPt
Source-Agent: software/version

# v2: standard POST
POST /mountPt HTTP/1.1
Host: caster.example.com:2101
Ntrip-Version: Ntrip/2.0
Authorization: Basic dXNlcjpwYXNzd29yZA==
Transfer-Encoding: chunked
```
