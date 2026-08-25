# Observability and Reliability

## Logging and Prometheus compatibility

Structured log messages include more contextual data from 1.17. Rules that
match complete lines or literal message strings should instead target stable
fields and be updated for the new shape.

The ACME request metrics below replace their `path` label with bounded
cardinality `action` in 1.19:

- `certmanager_acme_client_request_count`
- `certmanager_acme_client_request_duration_seconds`

Rewrite dashboards and alerts. Use Prometheus relabeling or recording rules
only when preserving the older high-cardinality semantics is necessary.

With chart monitoring enabled in 1.20, the metrics label is consistently
`cert-manager` instead of changing with release name or namespace. In 1.21,
the metrics endpoint and port name are fixed to `/metrics` and `http-metrics`.

## Certificate and challenge metrics

The following certificate validity metrics are available from 1.18:

- `certmanager_certificate_not_before_timestamp_seconds`
- `certmanager_certificate_not_after_timestamp_seconds`

The 1.19 `certmanager_certificate_challenge_status` metric exposes challenge
state for alerting and monitoring.

## Issuance failure behavior

- ACME authorization waits for up to two minutes from 1.17.3, reducing early
  `error waiting for authorization` failures.
- From 1.18.5, a returned certificate whose public key does not match its CSR
  is rejected before Secret storage and retries with backoff rather than
  entering an endless reissuance loop.
- TLS handshake timeouts, DNS errors, and context cancellation during ACME
  nonce retrieval or authorization waiting use workqueue backoff in 1.21
  instead of terminally failing the Challenge.
- An already-expired certificate returned by an issuer stops issuance instead
  of triggering an infinite reissuance loop (`1.21`).
- DigitalOcean DNS-01 uses regulated retries and records complete errors as
  Challenge events (`1.20`).

## Controller and webhook recovery

While a Certificate is deleting, its controller does not create replacement
CertificateRequests or Secrets (`1.17`).

After host suspension or VM live migration, the webhook uses wall-clock
polling to detect a missed serving-certificate renewal and recovers within one
minute of resume (`1.21`).

For Certificate durations longer than roughly three years,
`renewBeforePercentage` is calculated correctly in 1.21. Earlier behavior can
reject the value or calculate the wrong renewal time.

Version 1.21.1 fixes a 1.21.0 controller panic when
`spec.renewal.policy: Disabled` is configured. It also lets an ACME DNS-01
issuer recover after its missing credential Secret is created.
