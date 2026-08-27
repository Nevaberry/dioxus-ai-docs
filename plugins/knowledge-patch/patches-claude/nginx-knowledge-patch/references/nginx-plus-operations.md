# NGINX Plus operations and modules

These features require NGINX Plus unless a section says otherwise.

## Release support and platforms

### Lifecycle policy

A Plus release reaches end of software development when the next release
ships. Critical fixes and security updates go only to the two most recent
releases. Technical support lasts 24 months from the initial release and is not
extended by patch releases. Published support end dates are:

| Release | Technical support ends |
| --- | --- |
| R33 | November 18, 2026 |
| R34 | March 31, 2027 |
| R35 | August 12, 2027 |
| R36 | November 30, 2027 |

### R36 platform matrix

R36 supports:

- AlmaLinux 8.1+, 9, and 10
- Alpine 3.20–3.22
- Amazon Linux 2 LTS and 2023
- Debian 11–13
- FreeBSD 13.5+ and 14.3+
- Oracle Linux 8.1+ and 9
- RHEL 8.1+, 9, and 10
- Rocky Linux 8.1+, 9, and 10
- SLES 15 SP6+ and 16
- Ubuntu 22.04 LTS and 24.04 LTS

Alpine 3.19 was removed in R36, and Alpine 3.20 is deprecated.

## Licensing and usage reporting

From R33, every instance needs a JWT license file in `/etc/nginx/` on Linux,
`/usr/local/etc/nginx/` on FreeBSD, or the path set by `license_token`. Usage is
reported hourly over a verified connection. Failure to complete the initial
post-install or post-upgrade report stops traffic unless the optional 180-day
`enforce_initial_report` grace period is enabled.

For restricted networks, relay reports through Instance Manager. R34 adds
report-proxy support, and R35 adds automatic license renewal.

## Identity, authorization, and certificates

### Native OIDC progression

R34 introduces native `ngx_http_oidc_module` after earlier releases used a
reference implementation. R35 adds relying-party-initiated logout and UserInfo.
R36 adds PKCE, front-channel logout, and POST client authentication.

### Variable-driven authorization

R35 adds `auth_require`, which makes an access decision from variables
available at invocation time, including key-value and njs variables. It is
especially useful with OIDC.

### Native ACME

R35 adds `ngx_http_acme_module` for ACME certificate management. R36 adds
selectable challenge types and external-account-authorization keys.

### Certificates from key-value storage

Since R18, dynamically selected TLS certificates can come from the key-value
store as well as files. Prefix the variable with `data:` when the value itself
contains certificate data.

### Automatic TLS ticket-key rotation

Since R28, TLS session-ticket encryption keys rotate automatically when
sessions use a shared-memory `ssl_session_cache`.

## Key-value and numeric maps

Key-value zones gain IP address and CIDR matching through `type=ip` in R19 and
prefix matching through `type=prefix` in R20. An individual entry can override
the zone's default expiration time.

R36 adds `num_map` modules for HTTP and stream, selecting derived variables by
numeric value or numeric range rather than string matching.

## Packaging and observability

### Official container images

R32 adds official Plus container images. By R36, module-inclusive images carry
ACME, OpenTelemetry, and the Prometheus exporter.

### Observability module migrations

The packaged OpenTelemetry tracing module arrives in R29. OpenTracing is
deprecated in R31 and removed in R34; migrate to OpenTelemetry. The ModSecurity
WAF dynamic module reached end of support and was removed in R32.

### API version gates

Legacy Upstream Conf and Extended Status modules are not distributed from R16;
replace them with the Plus API. API v7 adds per-status-code statistics, v8 adds
SSL statistics for HTTP and stream upstreams and server zones, and v9 adds
per-worker connection and request statistics.

## Custom server identity

`server_tokens` accepts a variable-bearing custom string for the error-page
signature and `Server` response header. An empty string suppresses the header;
the separate `build` value emits the configured build name with the version.

```nginx
server_tokens "";
```
