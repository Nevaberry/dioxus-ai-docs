# Authorization, xDS, and Telemetry

Use this reference for gRPC-Go xDS RBAC policy compatibility and gRPC-Java xDS
telemetry, metric labels, or control-plane connection behavior.

## gRPC-Go permission matchers

From `go-1.82.1`, gRPC-Go supports the xDS RBAC `Metadata` and
`RequestedServerName` permission matcher fields.

The security-sensitive change is their behavior in DENY rules: these fields are
now enforced. Earlier behavior ignored them and could fail open. After an
upgrade:

- Audit DENY rules containing either field.
- Test a request that matches and one that does not match each matcher.
- Include absent, malformed, and repeated metadata cases relevant to the policy.
- Include the actual requested server names used through direct connections,
  proxies, and test environments.
- Do not remove a DENY condition merely because the earlier runtime ignored it.

## Deprecated `source_ip` principal compatibility

From `go-1.82.1`, gRPC-Go accepts the deprecated xDS RBAC `source_ip`
principal identifier and treats it as equivalent to `direct_remote_ip`.

Use the compatibility behavior when consuming older control-plane output, but
prefer `direct_remote_ip` in newly generated configuration. Test legacy and
current spellings against the same connection so migration does not change the
principal being matched.

## ORCA-to-LRS propagation

From `java-1.83.0`, gRPC-Java enables ORCA-to-LRS propagation by default. Under
gRFC A85, xDS configuration selects which fields from ORCA backend metric
reports are propagated into LRS load reports.

Implementation guidance:

- Treat propagation as active even when application code did not enable it.
- Configure the desired field selection in xDS rather than assuming every ORCA
  field should enter LRS.
- Validate backend emission, selected-field propagation, and LRS reporting as
  separate stages.
- Revisit telemetry volume and downstream processing when enabling additional
  fields.

## Aggregate-cluster backend-service labels

From `java-1.83.0`, gRPC-Java uses the leaf cluster name, not the aggregate
cluster name, as the backend-service label in metrics for xDS aggregate
clusters.

Review any consumer that keys on this label:

- Update dashboard groupings and alert filters.
- Update joins against cluster inventory.
- Expect one aggregate cluster to produce dimensions for multiple leaf
  clusters.
- Test cardinality and aggregation behavior with the deployed cluster graph.

Do not rewrite the actual xDS aggregate-cluster topology merely to preserve an
older metric label.

## Control-plane connection scoping

From `java-1.83.0`, gRPC-Java reverts the 1.81.0 behavior that reused xDS
control-plane connections across channels. Do not design or size the system on
the assumption that channels share one control-plane connection.

The reuse behavior could cause heavy xDS deployments with many targets to
exceed the control plane's `MAX_CONCURRENT_STREAMS`. New targets could then fail
to load resources, leaving their channels stuck in name resolution.

When testing or diagnosing:

1. Create a production-like number of channels and distinct targets.
2. Observe control-plane connections and concurrent resource streams.
3. Confirm every new target progresses beyond name resolution.
4. Correlate stalled channels with the control plane's stream limits.
5. Size connection and stream capacity for the channel-scoped behavior actually
   present after the revert.

## Security and operations checklist

- Re-test DENY policies now that both permission matchers are enforced.
- Accept legacy `source_ip` but emit `direct_remote_ip` for new policy.
- Select ORCA fields intentionally before they enter LRS.
- Query leaf-cluster labels for aggregate-cluster metrics.
- Load-test xDS resource delivery across many channels and targets.
