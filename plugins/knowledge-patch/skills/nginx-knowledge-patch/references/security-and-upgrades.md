# Security and upgrade boundaries

Use fixed-version boundaries as upgrade gates. A feature-series label alone is not sufficient when the fix landed in a later patch release.

## Contents

- [HTTP/3 and QUIC](#http3-and-quic)
- [TLS, OCSP, and encrypted upstreams](#tls-ocsp-and-encrypted-upstreams)
- [HTTP/2, gRPC, and upstream parsers](#http2-grpc-and-upstream-parsers)
- [Rewrite and charset processing](#rewrite-and-charset-processing)
- [Mail authentication](#mail-authentication)
- [WebDAV, MP4, and XML](#webdav-mp4-and-xml)
- [Protocol and signed-link hardening](#protocol-and-signed-link-hardening)

## HTTP/3 and QUIC

### Upgrade older HTTP/3 deployments

- CVE-2024-24989 is a major NULL-pointer dereference affecting NGINX 1.25.3.
- CVE-2024-24990 is a major use-after-free affecting 1.25.0 through 1.25.3.

Upgrade these deployments to 1.25.4 or later.

NGINX 1.25.0 through 1.25.5 and 1.26.0 also contain four medium-severity HTTP/3 flaws:

- CVE-2024-32760: buffer overwrite.
- CVE-2024-31079: stack overflow and use-after-free.
- CVE-2024-35200: NULL-pointer dereference.
- CVE-2024-34161: memory disclosure.

Upgrade the second group to 1.26.1, 1.27.0, or a later release.

### Limit stateless resets

NGINX 1.28.3 limits both the size and rate of QUIC stateless reset packets.

### Validate a migrated address

NGINX 1.30.1 fixes CVE-2026-40460 by withholding a migrated client address from new QUIC streams until the address has been validated, closing an HTTP/3 spoofing path.

### Reject crafted QUIC sessions safely

NGINX 1.31.2 fixes CVE-2026-42530, a use-after-free triggered by a crafted QUIC session that can corrupt worker memory or crash a worker.

## TLS, OCSP, and encrypted upstreams

### Isolate SNI virtual-server sessions

NGINX 1.27.4 fixes CVE-2025-23419. Before the fix, a TLS 1.3 session established for one SNI virtual server could be reused in another and bypass client-certificate verification. Upgrade deployments that combine TLS 1.3, SNI, and client certificates.

### Prevent plaintext injection from SSL backends

NGINX 1.28.2 fixes CVE-2026-1642 by preventing plaintext injection into responses from SSL backends.

### Honor an OCSP client-certificate rejection

NGINX 1.28.3 fixes CVE-2026-28755 by preventing a stream TLS handshake from succeeding after OCSP rejects the client certificate.

### Process OCSP DNS responses safely

NGINX 1.30.1 fixes CVE-2026-40701, a use-after-free during DNS response processing when `ssl_ocsp` is enabled.

## HTTP/2, gRPC, and upstream parsers

### Construct proxied requests safely

- NGINX 1.30.1 fixes CVE-2026-42926, data injection into requests proxied to HTTP/2 backends when `proxy_set_body` is used.
- NGINX 1.30.3 fixes CVE-2026-42055, a heap overflow from crafted HTTP/2 or gRPC proxy requests when `ignore_invalid_headers off` is combined with large `large_client_header_buffers` values.

### Parse upstream response protocols safely

NGINX 1.30.1 fixes CVE-2026-42946, a heap overread while processing crafted SCGI or uWSGI responses. It also fixes incorrect transfer of proxied HTTP/0.9, SCGI, or uWSGI responses when the first line is only partially read.

## Rewrite and charset processing

### Patch rewrite captures

- NGINX 1.30.1 fixes CVE-2026-42945, a crafted-request heap overflow in `ngx_http_rewrite_module` that could permit arbitrary code execution.
- NGINX 1.30.2 fixes CVE-2026-9256, another potentially exploitable heap overflow in configurations with overlapping captures.

### Patch UTF-8 decoding

UTF-8 decoding through `charset_map` receives overread fixes in NGINX 1.30.1 for CVE-2026-42934 and in 1.30.3 for CVE-2026-48142.

## Mail authentication

- NGINX 1.28.1 fixes CVE-2025-53859, worker-memory disclosure to the authentication server through crafted credentials used with `ngx_mail_smtp_module`'s `none` authentication method.
- NGINX 1.28.3 fixes CVE-2026-27651, a crash during CRAM-MD5 or APOP authentication retry.
- NGINX 1.28.3 fixes CVE-2026-28753, PTR-record injection into `auth_http` requests and backend SMTP XCLIENT commands.

## WebDAV, MP4, and XML

### Keep MP4 processing on a fixed release

CVE-2024-7347 is a low-severity buffer overread in `ngx_http_mp4_module`. It affects NGINX 1.5.13 through 1.27.0 and is fixed at 1.26.2 and 1.27.1.

NGINX 1.28.3 fixes two later crafted-MP4 flaws: CVE-2026-27784, which includes 32-bit platforms, and CVE-2026-32647. Both can crash `ngx_http_mp4_module` and may have greater impact.

### Constrain WebDAV paths and relationships

NGINX 1.28.3 fixes CVE-2026-27654, a buffer overflow in WebDAV COPY or MOVE requests handled in a location with `alias`. The flaw could change the source or destination path and escape the document root.

From 1.31.0, `ngx_http_dav_module` rejects COPY or MOVE when source and destination are identical or have a parent-child collection relationship.

### Keep external XSLT entities disabled

FreeNginx no longer loads external character entities declared in an internal DTD subset by default. Enable `xml_external_entities` only where external entity loading is intentional and its trust boundary is understood.

## Protocol and signed-link hardening

### Reject hop-by-hop HTTP/2 and HTTP/3 fields

From 1.31.0, NGINX rejects HTTP/2 and HTTP/3 requests containing `Connection`, `Proxy-Connection`, `Keep-Alive`, `Transfer-Encoding`, or `Upgrade`. It accepts `TE` only when the field value is `trailers`.

### Compare secure links in constant time

NGINX 1.31.2 compares `secure_link` hashes in constant time, reducing comparison-timing leakage during signed-link validation.
