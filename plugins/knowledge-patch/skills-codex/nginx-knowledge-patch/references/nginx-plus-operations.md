# NGINX Plus operations and modules

## Release and support lifecycle

A Plus release reaches end of software development when the next release
ships. Critical fixes and security updates are applied only to the two most
recent releases. Technical support lasts 24 months from the initial release
and is not extended by patches.

Published support end dates are November 18, 2026 for R33; March 31, 2027 for
R34; August 12, 2027 for R35; and November 30, 2027 for R36.

## R36 platform matrix

R36 supports:

- AlmaLinux 8.1+, 9, and 10
- Alpine 3.20 through 3.22
- Amazon Linux 2 LTS and 2023
- Debian 11 through 13
- FreeBSD 13.5+ and 14.3+
- Oracle Linux 8.1+ and 9
- RHEL 8.1+, 9, and 10
- Rocky Linux 8.1+, 9, and 10
- SLES 15 SP6+ and 16
- Ubuntu 22.04 LTS and 24.04 LTS

Alpine 3.19 was removed in R36, and Alpine 3.20 is deprecated.

## Licensing and usage reporting

From R33, each instance requires a JWT license file at `/etc/nginx/` on Linux,
`/usr/local/etc/nginx/` on FreeBSD, or the path given by `license_token`.
Instances report usage hourly over a verified connection. A successful initial
report is required after install or upgrade; otherwise traffic stops unless the
optional 180-day `enforce_initial_report` grace period is enabled.

Use Instance Manager as a relay on restricted networks. R34 adds report-proxy
support, and R35 adds automatic license renewal.

## Identity, authorization, and certificates

### Native OIDC progression

After earlier releases provided an OIDC reference implementation, R34
introduces the native `ngx_http_oidc_module`. R35 adds
relying-party-initiated logout and UserInfo. R36 adds PKCE, front-channel
logout, and POST client authentication.

### Native ACME

R35 adds `ngx_http_acme_module` for certificate management. R36 adds selectable
ACME challenges and external-account-authorization keys.

### Variable-driven authorization

R35 adds `auth_require`, which decides access from variables available at
invocation time, including key-value and njs variables. It is particularly
useful with OIDC.

## Data maps and certificate storage

### Numeric range maps

R36 adds `num_map` modules to HTTP and stream, selecting derived variables by
numeric values or numeric ranges.

### Key-value matching and expiry

Key-value zones add address and CIDR matching through `type=ip` in R19 and
prefix matching through `type=prefix` in R20. Individual entries can override
the zone's default expiration.

### Certificates from key-value storage

Since R18, dynamically selected TLS certificates can come from key-value
storage or files. Prefix a variable with `data:` when its value contains the
certificate data itself.

## Packaging and observability

### Official container images

R32 adds official Plus container images. By R36, module-inclusive images carry
ACME, OpenTelemetry, and the Prometheus exporter.

### Observability module removals

The packaged OpenTelemetry tracing module arrives in R29. OpenTracing is
deprecated in R31 and removed in R34; migrate to OpenTelemetry. The ModSecurity
WAF dynamic module reached end of support and was removed in R32.

### Plus API gates

Legacy Upstream Conf and Extended Status modules are absent from R16 onward;
use the Plus API. API v7 adds per-status-code statistics, v8 adds SSL statistics
for HTTP and stream upstreams and server zones, and v9 adds per-worker
connection and request statistics.

## TLS session tickets

Since R28, TLS session-ticket encryption keys rotate automatically when
sessions use a shared-memory `ssl_session_cache`.

## Custom server identity

With Plus, `server_tokens` accepts a variable-bearing custom string for the
error-page signature and `Server` response header. An empty string suppresses
the header; `build` emits the configured build name with the version.

```nginx
server_tokens "";
```
