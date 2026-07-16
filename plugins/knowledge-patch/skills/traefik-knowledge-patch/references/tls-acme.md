# TLS And ACME

Use this reference for ACME resolver identity and challenge timing, certificate
features, TLS protocol controls, and patched certificate selection.

## ACME accounts and certificate issuance

- Each ACME certificate resolver can use its own account email address and
  custom CA certificates (since 3.2.0). Resolvers no longer need to share an
  email or trust configuration.
- `certificatesDuration` supports a 30-day duration for certificates issued with
  that lifetime (since 3.2.0).
- ACME exposes controls for challenge propagation checks (since 3.3.0).
- `acme.profile` selects a certificate profile, and `acme.emailAddresses`
  supplies multiple contact addresses (since 3.4.0).
- ACME-managed certificates support OCSP stapling (since 3.5.0).
- `acme.httpChallenge.delay` controls HTTP challenge timing, and the ACME
  provider HTTP timeout is configurable (since 3.5.0).
- ACME adds `CertificateTimeout` (since 3.7.0).

## TLS options and upstream security

- TLS configuration can disable session tickets (since 3.4.0).
- TLS supports the post-quantum-secure `X25519MLKEM768` curve (since 3.5.0).
- `ServersTransport` can restrict upstream cipher suites (since 3.7.0).
- Fragmented TLS ClientHello messages are supported (since 3.7.0).
- A `TLSStore` whose Secret is missing no longer takes down unrelated
  configuration (since 3.7.0).

## Patched SNI and certificate behavior

- Patched 3.7 behavior isolates TLS options for the same host on different entry
  points, applies SNI checks to routers without host rules, and selects
  certificates deterministically when several certificates share a SAN (3.7.0
  batch).
