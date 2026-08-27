# Operations, Topology, and Repair

Use this reference for cluster lifecycle, topology, repair, guardrails, and
management-interface behavior.

## Gossip and topology

### Protect fresh state after restart (since 5.0.3)

Delayed gossip shutdown messages no longer overwrite a restarted node's fresh
startup state. A restarted node should not remain falsely marked down because an
old shutdown update arrived late.

### Check token metadata against gossip (since 5.0.3)

`nodetool checktokenmetadata` checks whether `TokenMetadata` is synchronized
with gossip endpoint state. Use it when ownership and endpoint state disagree.

```shell
nodetool checktokenmetadata
```

### Populate state for non-normal nodes (since 5.0.3)

Gossip-only and bootstrapping nodes receive DC, rack, and host-ID endpoint
state. Consumers should not assume those fields exist only after a node becomes
normal.

### Converge concurrent endpoint updates (since 5.0.5)

Gossip converges when multiple endpoint-state fields are updated concurrently.
Do not retain workarounds that serialize otherwise independent state updates.

### Use the corrected failure-detector default (since 5.0.7)

The default maximum interval for the failure detector is calculated correctly.
Clusters that did not override it can observe different failure-detection
timing, so recalibrate alerts against current behavior.

## Hints, Paxos, and request handling

### Calculate hint expiry from request start (since 5.0.3)

Hint expiry uses request start time, not timeout time, when calculating TTL.
Capacity and delivery reasoning should use the request's original clock origin.

### Deliver hints during schema mismatch (since 5.0.3)

A schema mismatch no longer categorically blocks hint delivery. Monitor schema
agreement separately rather than inferring it from a lack of hint delivery.

### Keep mixed-version Paxos progressing (since 5.0.4)

Mixed-version Paxos no longer hangs on TTL commits or enters an infinite loop.
When validating an upgrade, include Paxos writes with TTLs in the test matrix.

## Bootstrap, streaming, and transfer

### Use `StorageService` JMX during bootstrap (since 5.0.5)

The `StorageService` JMX MBean is available while a node is bootstrapping.
Bootstrap monitoring can use the standard management interface without waiting
for the node to become normal.

### Honor parallel transfer limits (since 5.0.5)

`MAX_PARALLEL_TRANSFERS` is honored correctly. Size transfer concurrency from
the configured value rather than compensating for the former overrun.

### Fall back for legacy SSTables (since 5.0.7)

Zero-copy streaming is disabled automatically for legacy SSTables that use the
old Bloom-filter format. They use a compatible streaming path instead; plan for
the different performance profile until those files are rewritten.

## Management and observability

### Inspect SAI through table statistics (since 5.0.3)

`nodetool tablestats` reports selected SAI index state and query-performance
metrics through the existing table-statistics command.

```shell
nodetool tablestats
```

### Manage guardrails with `nodetool` (since 5.0.5)

`nodetool getguardrailsconfig` and `setguardrailsconfig` expose guardrail
configuration through their simplified command interface.

```shell
nodetool getguardrailsconfig
```

### Start with a configured disk limit (since 5.0.5)

First boot no longer crashes when `data_disk_usage_max_disk_size` is configured
before the data directory exists.

### Drop prepared statements through JMX (since 5.0.6)

`StorageService.dropPreparedStatements` is exposed through JMX. Operators can
invalidate prepared statements through the management interface.

### Read the native connection cap through JMX (since 5.0.6)

`StorageProxyMBean` exposes `NativeTransportMaxConcurrentConnectionsPerIp` for
management clients that inspect the per-IP native transport limit.

### Do not expect heap dumps for handled exceptions (since 5.0.7)

Exceptions that Cassandra catches and handles no longer generate heap dumps.
Incident collection must not wait for a dump artifact in this case.

### Disable a tripped disk guardrail (since 5.0.7)

The disk-usage guardrail can be disabled after its failure threshold has been
reached. Operators can recover from a tripped state without keeping the
guardrail enabled.

### Use corrected direct-memory metrics (since 5.0.7)

`nodetool gcstats` reports direct-memory usage correctly. Update monitoring
thresholds that were calibrated against the former incorrect values.

## Repair execution

### Allow genuinely long repairs (since 5.0.4)

Long-running repairs are not failed automatically just because they exceed the
former premature cutoff. Monitor progress and failure signals instead of elapsed
time alone.

### Schedule repair in-process (since 5.0.8)

Built-in AutoRepair provides an in-process scheduler for recurring repair work.
External orchestration is no longer the only scheduling option, but ownership
should remain unambiguous: avoid scheduling the same work twice.

### Set a minimum task duration (since 5.0.8)

The AutoRepair scheduler has a minimum repair-task-duration setting. Use it to
bound scheduled work by a minimum run time.

### Preview repaired data (since 5.0.8)

AutoRepair accepts `preview_repaired` as a repair type. Use it when the scheduled
task should preview repaired-data consistency rather than perform a full repair.

### Stop during mixed-major upgrades (since 5.0.8)

The scheduler stops when it detects two Cassandra major versions. Provide
separate repair coverage during a mixed-major-version upgrade and verify that
scheduling resumes after the cluster converges on one major version.

### Protect disk during full repair (since 5.0.8)

Disk protection guards full AutoRepair. Scheduled full repairs do not proceed
without regard to disk-protection conditions.

### Track expected and actual work (since 5.0.8)

AutoRepair reporting includes expected versus actual repair bytes and expected
versus actual keyspaces. Use both dimensions to detect stalled or incomplete
scheduled work.

### Run repairs in parallel (since 5.0.9)

`parallel_repair_count` values greater than one no longer trigger an
`AssertionError` in `hasReplicaWithOngoingRepair`. Parallel AutoRepair can run
at the configured concurrency; continue sizing it for cluster capacity.
