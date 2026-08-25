# Routes, Filters, and Validation

Use this reference when authoring or validating HTTPRoute, GRPCRoute, TLSRoute,
TCPRoute, UDPRoute, filters, matches, retries, or route attachment.

## GRPCRoute

### More matches are allowed

The maximum number of `GRPCRoute` matches increased from 8 to 64 in 1.3.0.
Update generators and validators that still enforce the older ceiling.

### Spec is mandatory

`GRPCRoute.spec` became required in 1.4.0 after being accidentally optional
through `omitempty`. Existing objects without `spec` were unusable and must be
corrected before they pass the current schema.

## Percentage request mirroring

`RequestMirror` can mirror a percentage of requests for both `HTTPRoute` and
`GRPCRoute` (since 1.3.0). Percentage mirroring is a Standard-channel Extended
feature.

For HTTPRoute, implementations advertise support as
`HTTPRouteRequestPercentageMirror` in
`GatewayClass.status.supportedFeatures`. Check support rather than assuming it
from basic Route conformance.

## HTTPRoute CORS

### Experimental validation

The `CORS` filter began as an Experimental Extended HTTPRoute feature in 1.3.0
with no feature name or conformance test. Its final initial schema established
that:

- `allowCredentials` is Boolean.
- `allowMethods` cannot combine `*` with other methods.

### Boolean false is valid

Experimental CORS explicitly permits `allowCredentials: false` since 1.4.0:

```yaml
allowCredentials: false
```

Generated API libraries that used the earlier enum representation require code
changes to accept the Boolean form.

### Standard validation

The CORS filter graduated to the Standard channel in 1.5.0. CORS origins now
receive CEL validation that rejects unsupported values in the host portion.

Starting in 1.6.0, one HTTPRoute rule cannot contain more than one filter whose
type is `CORS`.

## Named HTTPRoute elements

Standard-channel `HTTPRouteRule` and `HTTPRouteMatch` gained `name` fields in
1.4.0, allowing individual rules and matches to be identified explicitly:

```yaml
rules:
- name: api
  matches:
  - name: get-v1
```

Use names when policy, status, tooling, or operational workflows need a stable
rule or match identity.

## HTTPRoute rule and retry validation

`HTTPRoute.spec.rules` requires at least one item since 1.5.0. An absent or
empty rules list is rejected.

Retry validation tightened in 1.6.0:

- Every value in `retry.codes` must be unique.
- `attempts` must be at least `1`.

Treat both as API constraints in generators and admission checks.

## TLSRoute validation and scale

Experimental `TLSRoute` moved to `v1alpha3` in 1.4.0, where `hostnames` became
required and `rules` was limited to one item.

`TLSRoute` graduated to `gateway.networking.k8s.io/v1` in 1.5.0.
Its `v1alpha2` and `v1alpha3` versions are deprecated, `v1alpha2` is no longer
shipped in the Experimental channel, and its stable CEL validation requires
Kubernetes 1.31 or later.

In 1.6.0, a TLSRoute may contain up to 4096 hostnames and 4096 rules. Validate
API server, etcd, and controller behavior using representative large
manifests before depending on those ceilings in production.

## TCPRoute and UDPRoute

`TCPRoute` and `UDPRoute` are GA at `gateway.networking.k8s.io/v1` since
1.6.0. Their `v1alpha2` versions are deprecated and will be removed.
Conformance includes a `GATEWAY-UDP` profile and a `SupportTCPRoute` feature.

A TLS listener does not support `TCPRoute` as of 1.5.0. Select the Route kind
appropriate for the listener protocol.

## ReferenceGrant validation

`ReferenceGrant` graduated to `gateway.networking.k8s.io/v1` in 1.5.0.
Its `spec` field is mandatory in 1.6.0, so schema validation rejects manifests
that omit it.

## Hostname portability

Implementations may allow or reject `HTTPRoute` and `GRPCRoute` resources on
the same hostname (since 1.6.0). Portable configurations must not depend on
coexistence. Use separate hostnames or verify the chosen implementation's
documented and tested behavior.

## Route validation checklist

1. Use current stable API versions for graduated Route kinds.
2. Require `spec` and non-empty rule lists where the schema does.
3. Apply current match, hostname, rule, and filter cardinality limits.
4. Check Extended feature support before enabling percentage mirroring.
5. Validate CORS Boolean, method, origin, and duplicate-filter constraints.
6. Enforce retry-code uniqueness and a positive attempt count.
7. Match each Route kind to a compatible listener.
8. Avoid assuming portable HTTP and gRPC coexistence on one hostname.
