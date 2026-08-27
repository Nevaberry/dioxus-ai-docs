# Routes, Filters, and Attachment

Use this reference when authoring Route objects, implementing match and
filter behavior, or evaluating how Routes attach to Gateways.

## Validate GRPCRoute structure and match counts

The maximum number of GRPCRoute matches increased from 8 to 64 in 1.3.0.
Controllers and generated clients should accept the larger list while still
enforcing the upper bound.

GRPCRoute `spec` became required in 1.4.0 after having been accidentally
optional through `omitempty`. Existing objects without `spec` were unusable
and must be corrected before they can pass the newer schema.

## Validate HTTPRoute rules and retries

`HTTPRoute.spec.rules` requires at least one item as of 1.5.0. An absent or
empty rules list is invalid.

Retry configuration validation tightened in 1.6.0:

- every entry in `retry.codes` must be unique; and
- `attempts` must be at least 1.

Deduplicate generated code lists rather than depending on a controller to
normalize them after admission.

## Mirror a percentage of requests

Beginning with 1.3.0, `RequestMirror` can mirror a percentage of requests for
both HTTPRoute and GRPCRoute. Percentage mirroring is Standard-channel
behavior at the Extended feature level.

For HTTPRoute, an implementation advertises the capability as
`HTTPRouteRequestPercentageMirror` in
`GatewayClass.status.supportedFeatures`. Check that feature before emitting a
portable configuration that depends on partial mirroring.

## Configure CORS filters

The HTTPRoute `CORS` filter began as an Experimental, Extended feature in
1.3.0 with no feature name or conformance test. Its `allowCredentials` field
is Boolean, and `allowMethods` cannot contain `*` together with other
methods.

Gateway API 1.4.0 explicitly permits:

```yaml
allowCredentials: false
```

Generated libraries written for the earlier enum representation need to
adopt the Boolean shape.

CORS graduated to the Standard channel in 1.5.0. CORS origins also gained
CEL validation that rejects unsupported values in the host portion, so
validate generated origins before submitting the Route.

As of 1.6.0, a single HTTPRoute rule cannot contain more than one filter with
type `CORS`. Consolidate the configuration into one filter.

## Delegate external authentication

Experimental HTTP external authentication became available for HTTPRoute in
1.4.0. It lets the Route delegate authorization to an external service.
Treat availability as implementation-dependent experimental behavior.

Experimental authentication expanded to Gateway-level configuration in
1.5.0. When both levels are available, evaluate which scope owns the
authentication decision instead of assuming the Route is the only policy
attachment point.

## Name rules and matches

Standard-channel `HTTPRouteRule` and `HTTPRouteMatch` gained a `name` field
in 1.4.0. Name individual rules and matches when controllers, policies, or
observability need a stable explicit identifier.

```yaml
rules:
- name: api
  matches:
  - name: get-v1
```

## Account for default Gateway attachment

The Experimental default-Gateway API introduced in 1.4.0 lets Gateways
program selected Routes by default. This creates an attachment path in
addition to ordinary explicit attachment.

Controller implementations must evaluate default eligibility, and Route
owners must account for a Route being programmed through that mechanism.
Do not infer that the lack of an ordinary explicit attachment necessarily
means the Route is unattached.

## Scale TLSRoute only after representative testing

A TLSRoute can contain up to 4096 hostnames and 4096 rules as of 1.6.0.
Before relying on those limits in production, validate representative large
objects against:

- API server admission and request sizing;
- etcd storage and update behavior; and
- the target controller's reconciliation behavior.

The schema limit describes accepted shape, not a performance guarantee.

## Keep HTTP and gRPC hostname use portable

Starting in 1.6.0, implementations may either allow or reject HTTPRoute and
GRPCRoute resources on the same hostname. Portable configurations must not
assume coexistence. Separate hostnames or verify the selected
implementation's behavior.
