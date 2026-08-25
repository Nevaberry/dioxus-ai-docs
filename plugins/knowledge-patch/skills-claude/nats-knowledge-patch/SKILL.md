---
name: nats-knowledge-patch
description: NATS Server
version: 2.14.0
license: MIT
metadata:
  author: Nevaberry
---


# NATS Server Knowledge Patch

Use this skill when configuring or operating NATS Server, designing JetStream
streams and consumers, publishing advanced message forms, or preparing an
upgrade or downgrade. Check the deployed server version and mixed-version
cluster state before applying version-dependent settings.

## Working method

1. Inspect the server configuration, `varz`, `jsz`, and `$JS.API.INFO` as
   relevant to establish the running feature level and effective settings.
2. Treat server-managed metadata and hidden source or mirror consumers as
   implementation state; do not overwrite or reconcile them as user metadata.
3. Check whether a configuration change is reloadable or restart-only before
   applying it. In particular, `feature_flags` cannot be reloaded.
4. For JetStream publishing, distinguish Core publishes, ordinary PubAck-based
   publishes, atomic batches, and fast batches. Their buffering, acknowledgement,
   and failure semantics differ.
5. Before enabling a stream feature, check creation-only restrictions,
   incompatible retention or stream modes, API level, and downgrade behavior.
6. When changing ACK or flow-control formats, audit permissions, imports,
   exports, and client parsers before changing server emission.
7. During recovery, prefer the state-preserving path even when it requires
   waiting for more replicas or a stream restart.

## Reference index

| Reference | Topics |
| --- | --- |
| [Consumers, mirrors, and sources](references/consumers-mirrors-and-sources.md) | Pull priority groups, pauses, resets, mirror promotion, reliable sourcing |
| [JetStream streams and publishing](references/jetstream-streams-and-publishing.md) | Strict requests, TTL, markers, buffering, batches, counters, schedules |
| [Networking, security, and observability](references/networking-security-and-observability.md) | Leafnodes, TLS, tracing, ACK subjects, metadata, events, configuration digests |
| [Operations, upgrades, and recovery](references/operations-upgrades-and-recovery.md) | Health checks, API levels, downgrade rebuilds, recovery, filestore and Raft containment |

## Upgrade-critical changes

### Strict JetStream requests

JetStream rejects unknown JSON request fields by default. Fix clients that emit
invalid fields. Use this only as a temporary compatibility bridge:

```text
jetstream {
  strict: false
}
```

### Bounded Core-to-JetStream ingest

Core NATS publishing into a stream is bounded by both message count and bytes.
The defaults are 10,000 messages and 128 MB per stream. Overflow can drop
messages and report `429 JSStreamTooManyRequests`; publishers waiting for
PubAcks should not normally reach this path.

```text
jetstream {
  max_buffered_msgs: 50000
  max_buffered_size: 256mib
}
```

### Health and shutdown semantics

`js-server-only` does not test meta-leader health. Select `js-meta-only` when
the meta group is the desired signal. A graceful `SIGTERM` exits successfully,
and startup rejects server, cluster, or gateway names containing spaces.

### Downgrade safeguards

Use 2.11.9 or newer for a downgrade from a server using 2.12-only assets so
unsupported assets are placed safely offline. The first restart across the
2.12-to-2.11 or 2.11-to-2.10 state-format boundary rescans message blocks,
temporarily raising CPU usage and delaying health without losing data.

Before downgrading from a server configured with `feature_flags`, remove the
entire block if the destination does not recognize it. Downgrading reliable
WorkQueue or Interest sources to 2.12 returns them to ephemeral sourcing and
leaves `AckFlowControl` consumers offline until 2.14 is restored.

### ACK and flow-control subject migration

Servers parse legacy and domain/account-aware subjects but emit the legacy form
by default. To test domain-aware emission, enable the restart-only flag:

```text
feature_flags {
  js_ack_fc_v2: true
}
```

Rules matching `$JS.ACK.>` or `$JS.FC.>` cover both forms. Rules scoped as
`$JS.ACK.<stream>.>` or `$JS.FC.<stream>.>` need revision. Clients must accept
the 9-token legacy form and domain-aware forms with 11 or more tokens, and must
publish the received reply subject unchanged.

## JetStream publishing quick reference

### Per-message TTL and subject markers

Set `AllowMsgTTL` on the stream, then publish `Nats-TTL` as integer seconds, a
Go duration, or `never`. Invalid or sub-second TTLs reject the publish. The
feature cannot be disabled once enabled, and `never` also bypasses `MaxAge`.

`SubjectDeleteMarkerTTL` creates a marker only when age removal deletes the
last message for a subject. It requires roll-ups and purge permission; API
deletes and purges do not create markers, and mirrors cannot enable it.

### Choose the right batch mode

Use `AllowAtomicPublish` for all-or-nothing staging and a single final PubAck.
It requires API level 2, rejects asynchronous persistence, cannot be used on a
mirror, and limits a batch to 1,000 messages with a 10-second idle expiry.

Use `AllowBatchPublish` for flow-controlled throughput with per-message
consistency checks and no intermediate atomic staging. Either batch mode may
end with an EOB message that is not persisted.

### Counters and schedules

`AllowMsgCounter` creates arbitrary-precision signed counters, one per subject.
Every publish must include `Nats-Incr`; counter mode is creation-only and has
strict incompatibilities. Sourced aggregation is eventually consistent and
must be corrected with compensating increments, not purge or roll-up.

`AllowMsgSchedules` stores one schedule per unique subject. Use `Nats-Schedule`
with `@at`, a six-field UTC cron expression, an alias, or `@every`; keep the
schedule record's TTL distinct from the generated message's TTL.

## Consumer and sourcing quick reference

### Grouped pull consumers

Grouped consumers require explicit acknowledgements and one priority group.
Choose among:

- `overflow`: deliver once either supplied pending threshold is met.
- `pinned_client`: select one active client while other pulls wait as standbys.
- `prioritized`: favor an eligible request sooner, with possible flip-flopping.

For pinned clients, retain the `Nats-Pin-Id`, retry without it after a `423`
mismatch, and use the unpin API for administrative reselection. Only the
priority timeout is updatable after creation.

### Reliable sources and mirrors

WorkQueue and Interest sources use visible, durable replicated consumers whose
names begin `JS_SRC_` or `JS_MIRROR_`. They use `AckFlowControl` and acknowledge
only after the receiver persists the message. Pre-create and reference a durable
consumer when lifecycle, permissions, starting position, filters, or replay
policy must be controlled explicitly.

### Reset delivery state deliberately

Request `$JS.API.CONSUMER.RESET.<STREAM>.<CONSUMER>` with an empty body for a
state reset that retains the stream ack floor, or `{"seq": N}` to make the next
stream sequence at least `N`. Other processes may reset a non-ordered consumer,
so delivery sequence is not guaranteed to remain monotonic.

## Networking and operations quick reference

### Leafnode connection control

Use `handshake_first` for TLS before the NATS protocol handshake. Solicited
remotes can be toggled with reloadable `disabled`; the whole remotes section can
also be added or removed on reload. Set global or per-remote `dial_timeout` for
high-latency links; its default is one second.

### Detect configuration drift

Run the server with `-t` to generate the file digest and compare it with
`varz.config_digest`. A mismatch means the on-disk configuration differs from
the running configuration.

### Contain overloaded or failed storage

A filestore write error freezes only the affected stream and fails health
checks; restart that server to recover. Other streams and Core traffic continue,
and a replicated stream may fail over. Raft bounds proposal growth, steps down
a lagging leader when a healthier peer exists, and remains degraded when a
majority lacks capacity.

### Preserve observability context

For distributed message traces, publish `Nats-Trace-Dest` and optionally
`Nats-Trace-Only: true`; trace-only mode emits hops without subscriber delivery.
Existing `traceparent` values are preserved.

## Final checks

- Confirm every stream feature is valid for its retention, mirror/source, and
  persistence mode.
- Confirm grouped pull requests carry the configured group and pinned clients
  handle reselection.
- Confirm custom ACK/flow-control permissions match every parsed subject form.
- Confirm memory sizing reflects the server's real container or host budget.
- Confirm downgrade targets understand the configuration and asset features in
  use before restarting any node.
