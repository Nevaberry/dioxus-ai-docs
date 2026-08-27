# Operations and Recovery

## Strict JetStream requests

Strict mode is enabled by default since 2.12.0. JetStream JSON requests with
unknown fields are rejected instead of only logged. Correct invalid clients;
use this compatibility setting only as a temporary migration aid:

```text
jetstream {
  strict: false
}
```

## Configuration digests

Since 2.11.0, the server's `-t` flag hashes its configuration file, while
`varz.config_digest` exposes the running configuration's hash. A mismatch
detects an on-disk change that has not been loaded.

## Health checks, shutdown status, and names

Since 2.11.0, `js-server-only` does not check meta-leader health. Use
`js-meta-only` when meta-group health is the intended signal. Graceful
`SIGTERM` shutdown exits with status 0. Server, cluster, and gateway names
containing spaces are rejected at startup.

## JetStream asset API levels

JetStream assigns 2.11.x API support level 1 and advertises it through `jsz`,
`varz`, and `$JS.API.INFO`. Server-managed assets record metadata keys
`_nats.ver`, `_nats.level`, and `_nats.req.level`. Reconciliation tools must
ignore these dynamic values. Level-dependent 2.11.0 fields include a nonzero
`PauseUntil` and the message-TTL settings.

## Windows TPM-backed filestore keys

Since 2.11.0, JetStream filestore encryption keys on Windows can be protected by
the machine TPM rather than only by storage accessible to an attacker with
physical access.

## Filestore memory behavior

Since 2.12.0, elastic filestore caches can be released under memory pressure,
so RSS may be higher or lower depending on workload. Size `GOMEMLIMIT` for
memory actually available to the server, including container reservations,
rather than extrapolating from older RSS behavior.

## Filestore write-error containment

Since 2.14.0, a filestore write error freezes only the affected stream, emits a
`write error` log entry, and fails health checks. Core traffic and other streams
continue. A replicated stream can fail over, but the affected server must
restart to recover.

## Raft overload containment

Since 2.14.0, Raft bounds memory and disk growth when proposals arrive faster
than they can commit. A lagging leader steps down for a healthier peer. If a
majority is overloaded, the cluster stays degraded until capacity catches up.

## Replicated in-memory recovery

During recovery of a replicated in-memory stream after all but one replica have
restarted, every replica may need to be available rather than merely a quorum
while the server chooses the data-preserving state. Plan 2.12.0 recovery around
full replica availability when this condition applies.

## Stream-state rebuilds on downgrade

The first 2.11.0-to-2.10 restart rebuilds changed stream-state files by
rescanning message blocks. No data is lost, but CPU rises and the node takes
longer to become healthy.

The first 2.12.0-to-2.11 restart performs a similar rescan. Downgrade to 2.11.9
or newer so assets using 2.12-only features are placed safely offline.

## Sourcing downgrade behavior

Downgrading durable WorkQueue or Interest sourcing introduced in 2.14.0 to 2.12
returns sources to the less reliable ephemeral form and can interrupt sourcing
during transition. `AckFlowControl` consumers remain offline until a supporting
server is restored. During a mixed-version upgrade, an older peer may log an
unknown `sourcing` field while the upgraded server retries the older form.
