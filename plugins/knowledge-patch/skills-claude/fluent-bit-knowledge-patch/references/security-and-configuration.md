# Security and Configuration

## TLS protocol and cipher controls

TLS-enabled plugins accept `tls.min_version`, `tls.max_version`, and
`tls.ciphers` since 4.0.0. Supported protocol values are asymmetric:

- `tls.min_version`: `TLSv1.1`, `TLSv1.2`, or `TLSv1.3`
- `tls.max_version`: `TLSv1.2` or `TLSv1.3`
- `tls.ciphers`: explicit cipher selection through TLS 1.2

Choose a deliberate minimum and maximum that both endpoints support. Do not
expect `tls.ciphers` to select TLS 1.3 cipher suites.

Version 4.1.0 replaces NPN with ALPN support and adds explicit TLS session
invalidation plus improved session cleanup. Retest protocol negotiation and
long-lived reconnect behavior when upgrading a TLS endpoint.

## Input-side mutual TLS

TLS-capable inputs can require and verify client certificates using
`tls.verify_client_cert on` from the `5.0-guide` source batch. Configure it
with the listener's normal certificate and key:

```yaml
tls.verify_client_cert: on
tls.crt_file: /path/to/server.crt
tls.key_file: /path/to/server.key
```

Test a trusted client, an untrusted client, a missing certificate, and an
expired certificate before making verification mandatory for a production
listener.

## OAuth 2.0

HTTP-based inputs, including HTTP and OpenTelemetry, can validate bearer tokens
with the following `5.0-guide` settings:

- `oauth2.validate`
- `oauth2.issuer`
- `oauth2.jwks_url`
- `oauth2.allowed_audience`
- `oauth2.allowed_clients`
- `oauth2.jwks_refresh_interval`

Keep issuer and audience comparison aligned with the token authority, restrict
client identifiers, and choose a refresh interval that rotates signing keys
without imposing needless JWKS traffic.

The HTTP output enables client-credentials token acquisition with
`oauth2.enable`. Its supported client-authentication methods are `basic`,
`post`, and `private_key_jwt`. Select the method required by the authorization
server and keep private keys out of inline configuration.

## File-backed environment values

An `env` value can use `file://` to read a secret or bearer token from a file
since 4.0.0. Normal `${...}` substitution applies after the file is read:

```yaml
env:
  TOKEN: file://mysecret.txt
pipeline:
  outputs:
    - name: http
      header: Bearer ${TOKEN}
```

Limit file permissions to the Fluent Bit runtime identity and make secret-file
rotation part of the configuration reload procedure.

## Secure Forward validation

Version 5.0.9 tightens both sides of the Secure Forward protocol:

- the input validates handshake PING messages;
- the output validates the server digest in PONG messages;
- username or password configuration on an output is rejected unless a shared
  key is also configured; and
- chunk acknowledgment tokens are base64-encoded 128-bit identifiers.

Update custom Forward peers to accept the acknowledgment-token representation
and confirm their PING, PONG, and shared-key behavior before deploying the
stricter peer.

## Experimental Zig plugins

Version 4.0.0 allows plugins to be written in Zig only when experimental
features are enabled at build time. Zig plugin support is disabled by default
and is not recommended for production use. Keep experiments isolated from the
production plugin ABI and build pipeline.
