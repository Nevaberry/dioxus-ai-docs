# Authorization, xDS, and Telemetry

## Enforced Go RBAC permission matchers

gRPC-Go supports the xDS RBAC `Metadata` and `RequestedServerName` permission
matcher fields. In DENY rules they are enforced rather than ignored; the prior
behavior could fail open.

Audit existing DENY policies that contain either field. Test both matching and
non-matching metadata and requested server names, and confirm that a matching
permission denies the RPC as intended.

## Header matcher validation and canonicalization

Since go-1.83.1, gRPC-Go applies header-name validation and canonicalization to
nested `Principal` and `Permission` rules and to non-lowercase header names.
Specifically, it:

- rejects `:scheme` matchers;
- rejects matchers with the `grpc-` prefix;
- maps `host` to `:authority`; and
- canonicalizes non-lowercase names instead of letting mixed-case matchers
  silently match nothing.

This closes another fail-open path for DENY rules. Test accepted lowercase and
mixed-case inputs, both rejected name classes, `host`/`:authority` behavior,
and nested principal and permission locations. Treat rejected configuration as
a deployment error rather than weakening the rule to make it load.

## Deprecated `source_ip` compatibility

gRPC-Go accepts the deprecated xDS RBAC principal identifier `source_ip` and
treats it as equivalent to `direct_remote_ip`. Continue accepting legacy input
where migration compatibility is required, but emit `direct_remote_ip` when
creating or rewriting configuration.

Keep an equivalence test until the legacy spelling has been removed from all
configuration producers and stored resources.

## ORCA metrics propagated to LRS

gRPC Java enables ORCA-to-LRS propagation by default. Under gRFC A85, xDS
configuration selects which fields from backend ORCA metric reports are copied
into LRS load reports.

Review field selection as part of control-plane configuration. Verify that the
chosen ORCA fields appear in LRS and that fields not selected are not assumed to
be present by aggregation, dashboards, or policy consumers.

## Aggregate-cluster metric labels use the leaf

For xDS aggregate clusters, gRPC Java uses the leaf cluster name rather than the
aggregate cluster name as the backend-service label in metrics.

Update queries, dashboards, alerts, joins, and cardinality estimates that group
or filter by this label. Validate a request routed through an aggregate cluster
and confirm that its emitted backend-service dimension names the selected leaf.

## Control-plane connections are channel-scoped

gRPC Java reverted the connection-reuse behavior introduced in 1.81.0. Do not
design capacity or diagnostics around an assumption that channels share an xDS
control-plane connection.

The reuse behavior was problematic under heavy xDS use with many targets: it
could exceed the control plane's `MAX_CONCURRENT_STREAMS`, prevent new targets
from loading resources, and leave their channels stuck in name resolution.

Test with a production-like count of channels and targets. Observe control-plane
stream capacity, resource delivery, and channel resolution together so a stalled
target is not misdiagnosed as an application resolver error.
