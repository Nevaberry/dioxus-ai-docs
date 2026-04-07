# NTRIP Protocol Details

## NTRIP v1 vs v2 Wire Protocol

RTKLIB only supports NTRIP v1. Critical detail for custom NTRIP client implementations.

### v1 Client Request

```
GET /mountPt HTTP/1.0\r\n
User-Agent: NTRIP theSoftware/theRevision\r\n
Authorization: Basic dXNlcjpwYXNzd29yZA==\r\n
\r\n
```

### v1 Responses

```
ICY 200 OK\r\n         # success — binary RTCM follows
SOURCETABLE 200 OK\r\n  # sourcetable (also returned on error)
```

### v1 Server (Base Station Push)

Uses `SOURCE` keyword instead of standard HTTP methods.

### v2 Additions

- `Host:` header required
- `Ntrip-Version: Ntrip/2.0` header
- Standard `HTTP/1.1 200 OK` response (instead of `ICY`)
- Chunked transfer encoding supported
- Servers use `POST` instead of `SOURCE`

**Important:** Some HTTP libraries reject `ICY 200 OK` as non-standard — must handle explicitly in custom implementations.

## GGA Requirement for VRS

VRS (Virtual Reference Station) and NEAR mountpoints require the client to send NMEA GGA sentences periodically so the caster can generate position-specific corrections.

In rtkrcv.conf:
- Set `nmeacycle` (ms) to control GGA send interval (e.g., `5000` for 5 seconds)
- Provide approximate position via `ant2-postype=single`

**Without GGA, VRS streams may send no data or stale corrections.**

## RTK2go Connection Details

Free public NTRIP caster at `rtk2go.com:2101` (unsecure, v1+v2) or `:2102` (TLS, v2 only).

### As Client (Rover)

- User: your email address
- Password: `none`
- Select mountpoint from sourcetable

### As Server (Base Station)

- Requires reservation at rtk2go.com
- Assigned password upon registration
- Mountpoint name rules:
  - No spaces
  - Case-sensitive
  - ASCII only
  - Avoid generic names like "Test" or "F9P"

### RTKLIB Limitation

RTKLIB can only connect as server with Rev1 — do not request Rev2 reservations for RTKLIB-based stations.
