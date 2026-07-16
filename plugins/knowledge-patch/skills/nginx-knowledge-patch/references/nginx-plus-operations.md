# NGINX Plus operations and modules

Everything in this reference is specific to NGINX Plus unless stated otherwise.

## Contents

- [Release lifecycle and platforms](#release-lifecycle-and-platforms)
- [Licensing and reporting](#licensing-and-reporting)
- [Authentication and certificates](#authentication-and-certificates)
- [Configuration primitives](#configuration-primitives)
- [Images, tracing, and API](#images-tracing-and-api)
- [Health checks and key-value data](#health-checks-and-key-value-data)

## Release lifecycle and platforms

### Apply the servicing window

Each release reaches End of Software Development when the next version is released. Critical bug and security fixes are applied only to the two most recent releases. Technical support lasts 24 months from the initial release and is not extended by patch releases. R36 support ends November 30, 2027.

### Check the R36 platform matrix

R36 supports:

- AlmaLinux 8.1+, 9, and 10.
- Alpine 3.20 through 3.22.
- Amazon Linux 2 LTS and 2023.
- Debian 11 through 13.
- FreeBSD 13.5+ and 14.3+.
- Oracle Linux 8.1+ and 9.
- RHEL 8.1+, 9, and 10.
- Rocky Linux 8.1+, 9, and 10.
- SLES 15 SP6+ and 16.
- Ubuntu 22.04 and 24.04 LTS.

R36 removes Alpine 3.19; deprecates Alpine 3.20; and adds Debian 13, Rocky Linux 10, and SLES 16.

## Licensing and reporting

### Install a per-instance license token

From R33, every instance requires a JWT license file. Its default directory is `/etc/nginx/` on Linux and `/usr/local/etc/nginx/` on FreeBSD. Set `license_token` in the `mgmt` context to select another path.

### Permit usage reports and renewal

R33 sends an hourly usage report over a verified connection and requires an initial report after installation or upgrade. Without that initial report, traffic processing stops unless the optional 180-day `enforce_initial_report` grace period is enabled.

Restricted networks can relay reports through NGINX Instance Manager. R34 adds proxy support for reporting, and R35 adds automatic license renewal.

## Authentication and certificates

### Use native OIDC

R34 introduces `ngx_http_oidc_module`. R35 adds relying-party-initiated logout and the UserInfo endpoint. R36 adds PKCE, front-channel logout, and POST client authentication.

### Automate ACME certificates

R35 introduces `ngx_http_acme_module` for native ACME certificate management. R36 adds ACME challenge configuration and external-account-authorization keys.

### Decide access with variables

R35 adds `ngx_http_auth_require_module`. `auth_require` can base an access decision on any variable available when it runs, including key-value-store and njs variables. It is especially useful with OIDC.

### Apply JWT and JWE controls

JWT support evolves across releases:

- R24 adds JWE.
- R25 adds signed-then-encrypted nested JWTs with `auth_jwt_type nested`, extra validation conditions with `auth_jwt_require`, `$jwt_payload`, multiple key-file or key-request directives in one context, and RSA-OAEP for JWE.
- R26 adds `auth_jwt_key_cache`.
- R27 lets `auth_jwt_require` choose the error status for a failed extra condition.

### Load certificates from key-value data

Dynamic server certificates can come from files or the key-value store. Prefix a variable with `data:` when the variable contains certificate data rather than a file name.

```nginx
ssl_certificate     data:$certificate;
ssl_certificate_key data:$certificate_key;
```

### Rotate TLS session tickets automatically

Since R28, NGINX Plus rotates TLS session-ticket encryption keys automatically when `ssl_session_cache` uses shared memory.

## Configuration primitives

### Map numeric ranges

R36 adds `num_map` modules to HTTP and stream. Like `map`, they create a variable from another value, but they can match numeric values and numeric ranges.

### Control header and trailer inheritance

R36 adds `add_header_inherit` and `add_trailer_inherit`. Child configuration levels can explicitly control how response header and trailer definitions are inherited from a parent.

### Re-evaluate geo variables

R36 adds the `volatile` parameter to `geo`. Mark a result volatile when its value must be re-evaluated instead of cached.

### Customize server identity

NGINX Plus `server_tokens` accepts a custom string containing variables for the error-page signature and the `Server` response header. An empty string suppresses the header. The separate `build` value emits the configured build name together with the version.

```nginx
server_tokens "";
```

### Account for the TLS protocol default

R34 defaults to TLS 1.2 and TLS 1.3 when the linked OpenSSL supports them. With OpenSSL 1.0.0 or older, the fallback defaults remain TLS 1.0 and TLS 1.1.

### Check QUIC and OpenSSL requirements

R36 supports QUIC 0-RTT with OpenSSL 3.5.1 or newer. On OS revisions that moved to OpenSSL 3.5, including RHEL 9.7 and 10.1, NGINX Plus requires OpenSSL 3.5.0 or newer to operate correctly.

## Images, tracing, and API

### Use the official image module set

Official NGINX Plus container images begin with R32. At R36, the images with popular modules include ACME, OpenTelemetry, and the Prometheus exporter.

### Migrate from OpenTracing

The OpenTracing dynamic module was deprecated in R31 and is unavailable from R34. Migrate to the OpenTelemetry distributed-tracing module, which incorporates its features.

### Track the API schema

- API version 7 adds per-status-code HTTP statistics for upstreams, server zones, and location zones.
- API version 8 adds SSL statistics for HTTP and stream upstreams and server zones, later extended with the SSL endpoint.
- API version 9 adds per-worker accepted, dropped, active, and idle connection counts, plus total and current request counts.
- The Prometheus-njs module supports API version 9.

## Health checks and key-value data

### Gate traffic on health checks

The `mandatory` health-check parameter prevents a newly added upstream server from receiving traffic before it passes a check. Later releases add:

- Arbitrary-variable requirements to `match`.
- `type=grpc` for gRPC health checks.
- `persistent` state across reloads for mandatory HTTP and stream checks.
- `keepalive_time` for HTTP health-check connections.

### Match, synchronize, and expire key-value entries

The key-value store can synchronize through Zone Synchronization and expire entries. `keyval_zone type=ip` matches IP addresses and CIDR ranges. Individual entries can override the zone's default expiration, and `type=prefix` matches the beginning of strings.

## Related protocol modules

Read [stream-mail-and-protocols.md](stream-mail-and-protocols.md) for NGINX Plus cross-module stream handoff, MQTT modules, and cloud-specific PROXY protocol TLVs. Read [upstreams-and-proxying.md](upstreams-and-proxying.md) for Plus state files, queues, per-attempt proxy controls, endpoint variables, and upstream key logging.
