---
name: nats-knowledge-patch
description: NATS Server
version: 2.14.0
license: MIT
metadata:
  author: Nevaberry
---


# NATS Server Knowledge Patch

Use this skill when configuring, upgrading, operating, or writing clients for
NATS Server and JetStream. Check the project or deployment's actual server
version before applying version-dependent advice, and prefer its configuration,
code, and observed behavior when they differ.

## Reference index

| Reference | Topics |
| --- | --- |
| [Consumers and sourcing](references/consumers-and-sourcing.md) | Priority groups, pausing, promotion, durable sourcing, consumer reset |
| [Networking and accounts](references/networking-and-accounts.md) | Tracing, accounts, leafnodes, routes, gateways, TLS, MQTT, ACK subjects |
| [Operations and recovery](references/operations-and-recovery.md) | Strict requests, health, metadata, storage, overload, upgrades and downgrades |
| [Streams and publishing](references/streams-and-publishing.md) | TTL, delete markers, buffering, batches, counters, schedules, transforms |

## Start with compatibility hazards

### JetStream requests reject unknown fields

Strict request validation is enabled by default. Remove unknown JSON fields
from clients instead of relying on the compatibility escape hatch. If a staged
migration needs the earlier behavior temporarily:

```text
jetstream {
  strict: false
}
```

### Core-to-JetStream ingestion is bounded

Core NATS publishes entering a stream can be dropped with
`429 JSStreamTooManyRequests` after either per-stream buffer limit is reached.
Publishers that need confirmation should use JetStream publishing and await
PubAcks. Tune only after measuring:

```text
jetstream {
  max_buffered_msgs: 50000
  max_buffered_size: 256mib
}
```

The defaults are 10,000 messages and 128 MB.

### Downgrades can rebuild or offline assets

Before moving back from servers with newer JetStream features, verify that the
destination release can safely recognize those assets. A first restart across
a stream-state format boundary may rescan message blocks, increasing CPU and
delaying health without losing data. WorkQueue and Interest sources also fall
back to less reliable ephemeral sourcing when downgraded from durable sourcing;
`AckFlowControl` consumers stay offline until a supporting server returns.

### ACK permissions must allow both subject formats

Clients and permissions should accept both legacy and domain/account-aware ACK
and flow-control subjects. Catch-all `$JS.ACK.>` and `$JS.FC.>` rules already
work; narrow rules such as `$JS.ACK.<stream>.>` do not cover the v2 layout.
Always publish the reply subject received from the server unchanged.

## Publishing quick reference

### Choose the right batch mode

| Need | Stream option | Semantics |
| --- | --- | --- |
| All-or-nothing commit | `AllowAtomicPublish` | Stages a contiguous batch and acknowledges only its commit |
| High throughput with per-message checks | `AllowBatchPublish` | Flow-controlled fast publishing without atomic staging |

Atomic publishing requires API level 2, rejects asynchronous persistence, and
cannot be used on mirrors. Every atomic message carries one `Nats-Batch-Id` and
a contiguous `Nats-Batch-Sequence`; the last carries `Nats-Batch-Commit: 1`.
Fast and atomic batches can use a non-persisted end-of-batch commit message.

### Enable per-message TTL deliberately

Set `AllowMsgTTL` on the stream before publishers send `Nats-TTL`:

```go
StreamConfig{AllowMsgTTL: true}
```

Accepted values are integer seconds, Go durations such as `1h`, and `never`.
Invalid or sub-second values reject the publish. `never` also bypasses stream
`MaxAge`, and `AllowMsgTTL` cannot later be disabled. Sources and mirrors store
the header but expire from it only when their own stream enables the feature.

### Treat schedules as stored control messages

`AllowMsgSchedules` lets one stored message emit another message in the same
stream. Use `Nats-Schedule` with `@at`, a six-field UTC cron expression, an
alias, or `@every`; route with `Nats-Schedule-Target` or sample through
`Nats-Schedule-Source`. `Nats-Schedule-TTL` transfers to generated messages as
`Nats-TTL`, while the schedule record's own `Nats-TTL` limits that record.

Schedule subjects must be unique. The feature requires API level 2, cannot be
disabled after enablement, and is rejected on sources and mirrors.

### Counter streams accept increments, not ordinary messages

With `AllowMsgCounter`, every subject is an arbitrary-precision signed counter.
Publish `Nats-Incr` as a signed integer; the server stores and acknowledges the
new value. Counter mode is creation-only, requires Limits retention and API
level 2, and conflicts with mirrors, DiscardNew, message TTL, schedules, and
publishes without an increment.

## Consumer and sourcing quick reference

### Configure grouped pulls consistently

Grouped pull consumers require explicit acknowledgements and one
`PriorityGroups` entry. Pick a policy deliberately:

| Policy | Delivery behavior |
| --- | --- |
| `overflow` | Starts after the request's `min_pending` or `min_ack_pending` threshold is met |
| `pinned_client` | Selects one client and leaves others as standbys |
| `prioritized` | Gives the request work sooner, but work may flip-flop between clients |

For pinned clients, retain the `Nats-Pin-Id` response header and send it as
`id` on later pulls. On a `423` mismatch, clear it and retry without an ID.
Only `PriorityTimeout` is updatable; grouped mode and policy cannot be changed
in place.

### Pause without declaring failure

Set `PauseUntil` at consumer creation or through the pause API. Delivery resumes
at the deadline, but heartbeats continue, so consumers should not interpret the
pause as a failed server or connection.

### Durable sourcing moves the acknowledgement boundary

WorkQueue and Interest mirrors/sources use visible, replicated consumers named
`JS_MIRROR_<suffix>` or `JS_SRC_<suffix>`. Their `AckFlowControl` policy
acknowledges only after the receiving server persists data. It requires flow
control and heartbeats, acts like `AckAll`, forbids `AckWait` and `BackOff`, and
requires `MaxDeliver: -1`.

Use `MaxAckPending` to bound unacknowledged sourcing. For explicit lifecycle or
security control, pre-create the durable and reference its name and delivery
subject; then put start and filter settings on that consumer, not on the
`StreamSource`.

### Reset delivery state with concurrency in mind

Publish an empty body or `{"seq": N}` to:

```text
$JS.API.CONSUMER.RESET.<STREAM>.<CONSUMER>
```

An empty reset clears pending, redelivery, delivered, and consumer ack-floor
state while retaining the stream ack floor. A positive `seq` requests that the
next stream sequence be at least `N`, subject to delivery-policy bounds. Client
code must tolerate another actor resetting a non-ordered consumer and making
its delivery sequence non-monotonic.

## Networking quick reference

### Harden leafnode behavior per link

Use `handshake_first: true` inside the TLS block when TLS must precede the NATS
protocol handshake. Leafnode remotes can be added or removed on reload, and an
existing solicited remote can be suppressed with `disabled: true`.

The default leafnode dial timeout is one second. Increase `dial_timeout` globally
or on an individual remote for high-latency links:

```text
leafnodes {
  dial_timeout: 5s
}
```

### Preserve user trace context

Set `Nats-Trace-Dest` to an inbox to receive distributed hop events. Add
`Nats-Trace-Only: true` to propagate tracing without delivering the message.
Servers preserve an existing `traceparent`; tracing logic should not assume it
will be rewritten.

## Operations quick reference

### Distinguish server and metadata health

`js-server-only` does not check the JetStream meta leader. Use `js-meta-only`
when meta-group health is the intended signal. Graceful `SIGTERM` exits with
status 0. Reject spaces in server, cluster, and gateway names before startup.

### Detect unapplied configuration changes

Run the server with `-t` to hash a configuration file and compare that result
with `varz.config_digest`, the digest of the running configuration. A mismatch
indicates that the on-disk configuration has not been loaded.

### Contain storage and consensus overload

A filestore write error freezes only the affected stream, logs `write error`,
and fails health checks. Other streams and core traffic continue, a replicated
stream may fail over, and the affected server must restart to recover.

Raft bounds memory and disk growth when proposals outpace commits. A lagging
leader steps down for a healthier peer; if a majority is overloaded, capacity
must recover before the cluster leaves its degraded state.

## Applying this skill

1. Determine the running server versions and whether a mixed-version upgrade or
   downgrade is in progress.
2. Identify the affected surface: streams/publishing, consumers/sourcing,
   networking/accounts, or operations/recovery.
3. Open the matching reference and check creation-only, restart-only,
   non-reloadable, and downgrade constraints before changing configuration.
4. Update client parsers and permissions before enabling protocol-format flags.
5. Exercise failure paths: PubAck rejection, leader changes, reset races,
   recovery, and configuration reloads.
