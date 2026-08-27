# Security, Configuration, and Lifecycle

## HTTP listener configuration

The HTTP, Splunk, Elasticsearch, OpenTelemetry, and Prometheus Remote Write
inputs share canonical listener settings (5.0-guide):

- `http_server.http2`
- `http_server.buffer_chunk_size`
- `http_server.buffer_max_size`
- `http_server.max_connections`
- `http_server.workers`
- `http_server.ingress_queue_event_limit`
- `http_server.ingress_queue_byte_limit`

The older `http2`, `buffer_chunk_size`, and `buffer_max_size` names remain
compatibility aliases. Prefer the `http_server.*` form in new configurations so
listener-wide limits are explicit.

## TLS policy

TLS-enabled plugins accept `tls.min_version`, `tls.max_version`, and
`tls.ciphers` (since 4.0.0). Valid minimums are `TLSv1.1`, `TLSv1.2`, and
`TLSv1.3`; valid maximums are `TLSv1.2` and `TLSv1.3`. Explicit cipher
selection applies through TLS 1.2, so do not expect `tls.ciphers` to select TLS
1.3 suites.

TLS-capable inputs can authenticate senders with mutual TLS (5.0-guide). Use
`tls.verify_client_cert on` together with the listener's `tls.crt_file` and
`tls.key_file`. Provision the trust material needed to validate client
certificates and exercise missing, expired, and untrusted certificate paths.

TLS internals use ALPN instead of NPN, support explicit session invalidation,
and clean sessions up more reliably (since 4.1.0). Recheck protocol negotiation
and connection reuse when upgrading custom TLS peers.

## OAuth 2.0

HTTP-family inputs, including HTTP and OpenTelemetry, can validate bearer
tokens (5.0-guide). The available settings are:

- `oauth2.validate`
- `oauth2.issuer`
- `oauth2.jwks_url`
- `oauth2.allowed_audience`
- `oauth2.allowed_clients`
- `oauth2.jwks_refresh_interval`

The HTTP output can acquire client-credentials tokens with `oauth2.enable`.
Client authentication supports `basic`, `post`, and `private_key_jwt`.
Coordinate issuer, audience, client allowlists, key rotation, and refresh
intervals; input validation and output token acquisition are separate roles.

## File-backed environment values

An `env` value can use a `file://` prefix (since 4.0.0). Fluent Bit loads the
file value and then applies ordinary `${...}` substitution:

```yaml
env:
  TOKEN: file://mysecret.txt
pipeline:
  outputs:
    - name: http
      header: Bearer ${TOKEN}
```

This is suitable for mounted secrets and bearer tokens. Ensure the process can
read the file, restrict its permissions, and test the deployment's secret
rotation and reload path.

## Process supervision and reloads

Supervisor mode runs a parent process that watches the Fluent Bit child,
improving recovery and graceful operation (since 4.1.0). Account for the parent
and child in process monitors, signal handling, and container lifecycle checks.

Hot reload has a timeout watchdog for reload operations that do not finish
safely (since 4.1.0). Test both successful reload and watchdog-triggered failure
behavior; a configuration parse check alone does not exercise this path.

## Build-time and platform constraints

Experimental plugins can be written in Zig when experimental features are
enabled at build time (since 4.0.0). Zig support is disabled by default and is
not recommended for production use.

Platform compatibility added in 4.1.0 includes Debian Trixie, Rocky Linux 10,
AlmaLinux 10, and CentOS Stream 10. Packaging support does not replace runtime
validation of service units, permissions, paths, and native dependencies.
