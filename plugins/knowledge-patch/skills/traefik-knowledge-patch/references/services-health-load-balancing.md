# Services, Health Checks, And Load Balancing

Use this reference for backend health, balancing strategy, service-wide
middleware, failover, stickiness, and traffic mirroring.

## Health checks

- Health checks can use a distinct interval while a backend is unhealthy (since
  3.5.0), allowing failed servers to be probed at a different cadence.
- Services support native TCP health checks for non-HTTP backends (since 3.6.0).
- Passive health checks can infer service health from observed traffic (since
  3.6.0).
- Health-check paths must be path-only values; absolute URLs fail validation
  (since 3.7.0).

## Load-balancing strategies

- Server load balancers support `p2c` (since 3.4.0).
- `Least Time` sends requests to servers with the lowest response times and is
  available in file and Kubernetes CRD service configuration (since 3.6.0).
- `HighestRandomWeight` provides probabilistic balancing and is available through
  Kubernetes CRDs (since 3.6.0).

## Service middleware and failover

- Middleware can attach directly to an HTTP service and applies to every router
  that uses it (since 3.7.0). This also enables Gateway API filters on HTTP
  backends.
- Failover services can switch on response status codes, and `TraefikService`
  CRDs can express the failover directly (since 3.7.0):

  ```yaml
  apiVersion: traefik.io/v1alpha1
  kind: TraefikService
  metadata:
    name: api-failover
  spec:
    failover:
      service: api-primary
      fallback: api-backup
      healthCheck: {}
      errors:
        status: ["500-504"]
  ```

## Sticky sessions

- Sticky-session cookies accept a configurable path (since 3.3.0).
- Sticky-session cookies accept a configurable domain (since 3.4.0).

## Mirroring

- HTTP mirror services expose `mirrorBody` so request-body copying can be
  disabled per mirror (since 3.2.0).
- Empty request bodies with unknown length are handled correctly by mirroring as
  of 3.6.21.
