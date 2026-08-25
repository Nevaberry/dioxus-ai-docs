# Operations, Upgrades, and Recovery

## Health checks, shutdown, and names

Since 2.11.0, `js-server-only` no longer checks meta-leader health. Use
`js-meta-only` when meta-group health is the intended signal. Graceful
`SIGTERM` shutdown exits with status `0`. Server, cluster, or gateway names
containing spaces are rejected at startup.

## JetStream asset API levels

The 2.11.0 server line assigns JetStream API support level `1`, advertises it
through `jsz`, `varz`, and `$JS.API.INFO`, and records these server-managed
asset metadata keys:

- `_nats.ver`
- `_nats.level`
- `_nats.req.level`

Reconciliation tools must ignore those dynamic metadata values. Level-dependent
fields include nonzero `PauseUntil` and the message-TTL settings.

API level 2 is required for atomic publishing, counter streams, and message
schedules introduced with 2.12.0. Check the advertised level rather than
assuming a feature is available uniformly during a rolling upgrade.

## Replicated deletion and leader changes

Since 2.11.0, deletes in replicated Interest and WorkQueue streams go through
Raft proposals, potentially increasing replication traffic. A new leader waits
for its Raft log to synchronize before serving reads or writes. Replicated
consumers redeliver unacknowledged messages after a leader change. Configured
consumer start sequences remain honored except for hidden source and mirror
consumers.

## Stream-state rebuilds during downgrade

On the first 2.11-to-2.10 restart, changed stream-state files are rebuilt by
rescanning message blocks. No message data is lost, but CPU use rises and the
node takes longer to become healthy.

The first 2.12-to-2.11 restart performs the same kind of rebuild. Use 2.11.9 or
newer as the downgrade target so assets using 2.12-only features are placed
safely offline.

## Replicated in-memory recovery

Since 2.12.0, recovery of a replicated in-memory stream after all but one
replica have restarted may require every replica rather than only a quorum
while the server chooses the data-preserving state. Do not force quorum-only
recovery when the server is waiting for the safer state.

## Filestore memory sizing

Since 2.12.0, elastic filestore caches can be released under memory pressure,
so RSS may be higher or lower depending on workload. Size `GOMEMLIMIT` for the
memory actually available to the server, including container reservations,
rather than relying on an earlier RSS pattern.

## Filestore write-error containment

Since 2.14.0, a filestore write error freezes only the affected stream, writes
a `write error` log entry, and fails health checks. Core traffic and other
streams continue, and a replicated stream can fail over. Restart the affected
server to recover the frozen stream.

## Raft overload containment

Since 2.14.0, Raft bounds memory and disk growth when proposals arrive faster
than they can commit. A lagging leader steps down for a healthier peer. If a
majority is overloaded, the cluster remains degraded until capacity catches
up; leadership changes cannot supply missing majority capacity.

## Reliable-source upgrade and downgrade behavior

When upgrading to 2.14.0, mixed-version peers may temporarily log an unknown
`sourcing` field while the upgraded node retries the former consumer form.
Downgrading to 2.12 returns WorkQueue and Interest sources to ephemeral mode,
can interrupt sourcing during transition, and leaves `AckFlowControl` consumers
offline until 2.14 is restored.

## Operational upgrade checklist

1. Inspect `varz`, `jsz`, and `$JS.API.INFO` for server versions, API levels,
   health, and asset state.
2. Confirm the destination version understands every stream feature and
   configuration block currently in use.
3. Budget CPU and readiness time for stream-block rescans across state-format
   boundaries.
4. Wait for required replicas when recovering replicated in-memory streams.
5. Treat dynamic `_nats.*` metadata as server-owned.
6. After a filestore write error, verify failover and restart the affected
   server rather than expecting an online thaw.
