# Security and upgrade boundaries

Apply fixed releases before relying on configuration workarounds. A feature
series is not a security boundary: later patch releases can carry fixes absent
from the initial stable or mainline release.

## Current-series gates

### Security boundaries within 1.29.x

The `1.29.0` series requires several later patch releases:

- Use 1.29.1 or newer for the `ngx_mail_smtp_module` `none`-authentication
  memory disclosure, CVE-2025-53859.
- Use 1.29.5 or newer to prevent plaintext injection into responses received
  from SSL backends, CVE-2026-1642.
- Use 1.29.7 or newer for WebDAV `COPY`/`MOVE` with `alias`
  (CVE-2026-27654), MP4 parsing flaws (CVE-2026-27784 and CVE-2026-32647),
  mail authentication retry crashes (CVE-2026-27651), PTR-record injection
  into `auth_http` and SMTP `XCLIENT` (CVE-2026-28753), and stream
  client-certificate OCSP bypass (CVE-2026-28755).

### Security boundaries within 1.30.x

The initial `1.30.0` release lacks fixes delivered in later patch releases:

- Use 1.30.1 or newer for request injection with `proxy_set_body` and HTTP/2
  backends (CVE-2026-42926), a rewrite-module heap overflow
  (CVE-2026-42945), SCGI or uWSGI response overreads (CVE-2026-42946), a
  UTF-8 `charset_map` response overread (CVE-2026-42934), HTTP/3 migration
  address spoofing (CVE-2026-40460), and an `ssl_ocsp` DNS-response
  use-after-free (CVE-2026-40701).
- Use 1.30.2 or newer for the overlapping-capture rewrite heap overflow,
  CVE-2026-9256.
- Use 1.30.3 or newer for the heap overflow involving
  `ignore_invalid_headers off`, large `large_client_header_buffers`, and a
  crafted request proxied to HTTP/2 or gRPC (CVE-2026-42055), and for another
  UTF-8 `charset_map` response overread (CVE-2026-48142).

### HTTP/3 boundary after 1.31.0

Use 1.31.2 or newer when HTTP/3 is enabled. Earlier builds can hit a
use-after-free while processing a crafted QUIC session, corrupting worker
memory or crashing the worker (CVE-2026-42530).

## TLS and early HTTP/3 floors

### Client-verification context isolation

CVE-2025-23419 affects 1.11.4 through 1.27.3. Use 1.26.3, 1.27.4, or a newer
release.

### Early HTTP/3 flaws

- CVE-2024-24989 and CVE-2024-24990 require 1.25.4 or newer.
- CVE-2024-32760, CVE-2024-31079, CVE-2024-35200, and CVE-2024-34161 affect
  1.25.0 through 1.25.5 and 1.26.0; use 1.26.1, 1.27.0, or newer.

## Module and parser floors

### MP4 parser

- CVE-2024-7347 requires 1.26.2 or 1.27.1.
- CVE-2022-41741 and CVE-2022-41742 require 1.22.1 or 1.23.2.
- CVE-2018-16845 is fixed in 1.14.1 and 1.15.6.
- CVE-2012-2089 is fixed in 1.0.15 and 1.1.19.

### Resolver

- CVE-2021-23017 affects 0.6.18 through 1.20.0 and is fixed in 1.20.1 and
  1.21.0.
- CVE-2016-0742, CVE-2016-0746, and CVE-2016-0747 require 1.8.1 or 1.9.10.
- CVE-2011-4315 requires 1.0.10 or 1.1.8.

### HTTP/2 resource exhaustion

- CVE-2019-9511, CVE-2019-9513, and CVE-2019-9516 affect 1.9.5 through
  1.17.2 and require 1.16.1 or 1.17.3.
- CVE-2018-16843 and CVE-2018-16844 require 1.14.1 or 1.15.6.

### Legacy request processing

- CVE-2017-7529, the range-filter integer overflow, is fixed in 1.12.1 and
  1.13.3.
- CVE-2016-4450, the request-body NULL dereference, is fixed in 1.10.1 and
  1.11.1.

### Legacy TLS, mail, and SPDY

- CVE-2014-3616 requires 1.6.2 or 1.7.5.
- CVE-2014-3556, the STARTTLS injection, requires 1.6.1 or 1.7.4.
- CVE-2014-0088 is fixed in 1.5.11; CVE-2014-0133 is fixed in 1.4.7 and
  1.5.12.

### Legacy request and backend-response parsing

- CVE-2013-4547 requires 1.4.4 or 1.5.7.
- CVE-2013-2028 requires 1.4.1 or 1.5.0.
- CVE-2013-2070 requires 1.2.9, 1.4.1, or 1.5.0.
- CVE-2012-1180 requires 1.0.14 or 1.1.17.

## Platform and earliest-branch floors

### nginx/Windows

- CVE-2011-4963 requires nginx/Windows 1.2.1 or 1.3.1.
- CVE-2010-2266 requires at least 0.7.67 or 0.8.41.
- CVE-2010-2263 requires at least 0.7.66 or 0.8.40.
- Windows 8.3 filename issues require at least 0.7.65 or 0.8.33.

### Earliest portable-build issues

- CVE-2009-3555 requires 0.7.64 or 0.8.23.
- CVE-2009-3898 requires 0.7.63 or 0.8.17.
- CVE-2009-2629 and CVE-2009-3896 have branch-specific fixes beginning at
  0.5.38, 0.6.39, 0.7.62, and 0.8.15 or 0.8.14, respectively.

### Unsanitized error-log data

CVE-2009-4487 is listed as affecting all versions, with no non-vulnerable
release. Treat error-log data as unsanitized; do not rely on an upgrade to
change that property.

## Reporting and patch verification

Report NGINX security issues to `F5SIRT@f5.com` or use the methods in the
project's `SECURITY.md`. Verify published security patches against one of the
NGINX PGP public keys.
