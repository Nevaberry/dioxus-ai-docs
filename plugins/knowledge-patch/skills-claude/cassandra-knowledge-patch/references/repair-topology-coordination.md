# Repair, Topology, and Coordination

## Gossip and endpoint state

### Restart-safe gossip state

Delayed gossip shutdown messages do not overwrite a restarted node's fresh
startup state (since 5.0.3), preventing a restarted node from remaining falsely
marked down.

### Token metadata consistency check

`nodetool checktokenmetadata` checks whether `TokenMetadata` is synchronized
with gossip endpoint state (since 5.0.3):

```shell
nodetool checktokenmetadata
```

### Endpoint state for non-normal nodes

Gossip-only and bootstrapping nodes receive DC, rack, and host-ID endpoint
state (since 5.0.3).

### Gossip convergence during multi-field updates

Gossip converges when multiple fields in an endpoint state are updated
concurrently (since 5.0.5).

## Hints and batchlog placement

### Hint expiry origin

Hint expiry calculates TTL from the request start time rather than the timeout
time (since 5.0.3).

### Hint delivery during schema mismatch

Hints may be delivered while schemas mismatch (since 5.0.3); a mismatch no
longer categorically blocks delivery.

### Configurable batchlog endpoint strategies

Batchlog endpoint selection supports `random_remote`, `prefer_local`,
`dynamic_remote`, and `dynamic` (since 5.0.3):

```yaml
batchlog_endpoint_strategy: dynamic_remote
```

## Paxos and replica coordination

### Mixed-version Paxos stability

Mixed-version Paxos operation does not hang on TTL commits or enter an infinite
loop (since 5.0.4).

### Parallel transfer limits

`MAX_PARALLEL_TRANSFERS` is honored correctly (since 5.0.5).

### Deterministic TTL updates

Updating a column with a new TTL but the same expiration time is deterministic
(since 5.0.5), avoiding replica repair mismatches.

### Documented Paxos v2 configuration

The shipped `cassandra.yaml` includes the Paxos v2 option and its configuration
information (since 5.0.9), making the choice visible in the standard template.

## Repair behavior

### Long-running repairs

Long-running repairs are not automatically failed prematurely (since 5.0.4).

### `StorageService` JMX availability during bootstrap

The `StorageService` JMX MBean is available during bootstrap (since 5.0.5),
enabling repair and topology management visibility before normal state.

## AutoRepair scheduler

### Built-in automated repair

Cassandra includes the CEP-37 in-process automated repair scheduler (since
5.0.8), so recurring repair orchestration can run inside Cassandra instead of
requiring an entirely external scheduler.

### Minimum AutoRepair task duration

The scheduler has a minimum repair-task-duration setting (since 5.0.8),
allowing scheduled work to be bounded by a minimum run time.

### `preview_repaired` AutoRepair type

AutoRepair supports `preview_repaired` as a repair type (since 5.0.8).

### Mixed-major-version AutoRepair shutdown

The repair scheduler stops when it detects two major Cassandra versions (since
5.0.8). Do not assume scheduled repairs continue during a mixed-major rolling
upgrade.

### Disk protection for full AutoRepair

Full AutoRepair observes disk protection (since 5.0.8), preventing scheduled
full repair from proceeding without regard to disk-protection conditions.

### AutoRepair progress observability

AutoRepair reports expected versus actual repair bytes and expected versus
actual keyspaces (since 5.0.8).

### Parallel AutoRepair execution

AutoRepair supports `parallel_repair_count` greater than one without an
`AssertionError` in `hasReplicaWithOngoingRepair` (since 5.0.9), allowing
parallel repair configurations to operate as configured.
