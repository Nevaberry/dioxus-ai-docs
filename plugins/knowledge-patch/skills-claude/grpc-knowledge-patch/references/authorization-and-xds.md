# Authorization, xDS, and Telemetry

Use this reference when changing gRPC-Go RBAC policy handling or gRPC-Java xDS
reporting, metrics, and control-plane connectivity.

## Go RBAC permission matchers (`go-1.82.1`)

gRPC-Go xDS RBAC supports the `Metadata` and `RequestedServerName` permission
matcher fields. These fields are enforced in DENY rules rather than ignored.
The earlier ignored behavior could fail open.

For each field, test:

- a matching value that activates the DENY rule;
- a non-matching value that does not activate that rule;
- an absent value where absence is possible; and
- composition with the surrounding permission rule structure used in the
  deployed policy.

Audit existing DENY policies before an upgrade, especially policies that
included either field but appeared not to affect requests.

## Deprecated `source_ip` compatibility (`go-1.82.1`)

gRPC-Go accepts the deprecated xDS RBAC principal identifier `source_ip` and
treats it as equivalent to `direct_remote_ip`.

Accept legacy configuration that still supplies `source_ip`, but generate
`direct_remote_ip` in new configuration. Keep equivalence coverage until the
legacy input is no longer supported by the application or its control plane.

## Go RBAC header matcher hardening (`go-1.83.1`)

Header-name validation and canonicalization apply to nested `Principal` and
`Permission` rules and to non-lowercase names. gRPC-Go:

- rejects `:scheme` matchers;
- rejects matchers whose names begin with `grpc-`;
- maps `host` to `:authority`; and
- handles mixed-case header names instead of allowing them to silently match
  nothing.

The mixed-case behavior matters most in DENY rules: a matcher that silently
matched nothing could let a request fail open.

Build a regression matrix covering a normal lowercase name, a non-lowercase
name, `host`, `:scheme`, and a `grpc-`-prefixed name in both nested principal
and permission locations used by the policy. Verify rejection for forbidden
names, `host`/`:authority` equivalence, and enforcement of the intended DENY
case.

## ORCA-to-LRS propagation (`java-1.83.0`)

gRPC-Java enables ORCA-to-LRS propagation by default. Under gRFC A85, xDS
configuration selects which fields from backend ORCA metric reports propagate
into LRS load reports.

Review the selected fields as an explicit telemetry contract. Test that a
selected field reaches the LRS report and that an unselected field does not.
Also check the default-enabled path when application code has no separate
opt-in.

## Aggregate-cluster metric labels (`java-1.83.0`)

For xDS aggregate clusters, gRPC-Java uses the leaf cluster name, not the
aggregate cluster name, as the backend-service metric label.

Update metric queries, dashboards, alerts, joins, and cardinality assumptions
that group by this label. Test with an aggregate cluster whose leaf name is
distinct so the expected dimension is unambiguous.

## Channel-scoped control-plane connections (`java-1.83.0`)

gRPC-Java does not reuse xDS control-plane connections across channels. This
reverts the connection reuse behavior introduced earlier.

In deployments with many targets, channel-scoped connections can interact
with the control plane's `MAX_CONCURRENT_STREAMS`. If the stream capacity is
exhausted, new targets may fail to load resources and their channels may
remain stuck in name resolution.

Capacity and diagnosis checks should include:

1. Create a production-like number of channels and targets.
2. Observe control-plane connections and concurrent streams.
3. Track whether every target loads its resources.
4. Correlate channels stuck in name resolution with stream capacity.
5. Keep a smaller under-capacity case to distinguish configuration failure
   from capacity exhaustion.
