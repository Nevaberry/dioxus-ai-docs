# Streams and Publishing

## Per-message JetStream TTL

Since 2.11.0, streams opt in with `AllowMsgTTL`; publishers then set `Nats-TTL`
to integer seconds, a Go duration such as `1h`, or `never`. The last value also
exempts the message from stream `MaxAge`. Invalid or sub-second TTLs reject and
discard the publish, and the option cannot be disabled after enablement.

```go
StreamConfig{AllowMsgTTL: true}
```

Sources and mirrors always accept and store an incoming `Nats-TTL` header but
expire from it only when their own `AllowMsgTTL` is enabled. A direct publish
with the header to a stream without the feature is rejected.

## Subject delete markers

`SubjectDeleteMarkerTTL` (since 2.11.0) creates a marker when age-based removal
deletes a subject's final message. The marker has
`Nats-Marker-Reason: MaxAge` and its own `Nats-TTL`. Explicit delete and purge
API calls do not create markers, and mirrors cannot enable the setting.

The stream must permit roll-ups and purge. Normal create/update requests enable
`AllowRollup` and clear `DenyPurge`; pedantic requests fail rather than adjusting
them. Unless `MaxMsgsPer` is 1, the marker TTL is also the minimum effective
per-message TTL: lower values are accepted but clamped, and the stored header is
rewritten.

## Stream ingest backpressure

Core NATS publishing into JetStream is bounded per stream since 2.11.0 by
`max_buffered_size` (default 128 MB) and `max_buffered_msgs` (default 10,000).
Exceeding a limit can drop messages and return `429 JSStreamTooManyRequests`.
JetStream publishing that waits for PubAcks should not normally reach the limit.

```text
jetstream {
  max_buffered_msgs: 50000
  max_buffered_size: 256mib
}
```

## Atomic stream batch publishing

`AllowAtomicPublish` (since 2.12.0) provides all-or-nothing batches. It requires
API level 2, is incompatible with asynchronous persistence, and cannot be used
on mirrors.

```go
StreamConfig{AllowAtomicPublish: true}
```

Every message uses the same `Nats-Batch-Id` and a contiguous
`Nats-Batch-Sequence`. The first must be a request. The stored final message
adds `Nats-Batch-Commit: 1`; only it receives a normal PubAck, whose `batch` and
`count` fields identify the commit.

In 2.12.0, batches are limited to 1,000 messages, expire after 10 idle seconds,
and reject `Nats-Msg-Id` and `Nats-Expected-Last-Msg-Id`. Abandonment publishes
`io.nats.jetstream.advisory.v1.stream_batch_abandoned`.

## Fast and end-of-batch publishing

`AllowBatchPublish` (since 2.14.0) enables flow-controlled, high-throughput
publishing to replicated and non-replicated streams. Each message still gets
consistency checks, but there is no atomic batch's intermediate staging.

```go
StreamConfig{AllowBatchPublish: true}
```

Both atomic and fast batches may commit through an end-of-batch message that is
not itself persisted.

## Distributed counter streams

`AllowMsgCounter` (since 2.12.0) turns every stream subject into an
arbitrary-precision signed counter. A publish must carry a signed-integer
`Nats-Incr`; the server replaces the body with `{"val":"..."}` and returns the
same total in the PubAck.

```bash
nats req counter.hits '' -J -H 'Nats-Incr:+2'
```

Counter mode is creation-only, requires Limits retention and API level 2, and
is incompatible with mirrors, DiscardNew, per-message TTL, schedules, and
counter-less publishes. Sourced aggregates track each upstream total in
`Nats-Counter-Sources` and apply its delta, so aggregation remains eventually
consistent across missed source messages. Reset one sourced contribution with a
compensating negative increment: purge does not replicate, and roll-up destroys
the combined counter.

## JetStream message schedules

`AllowMsgSchedules` (since 2.12.0) lets a stored schedule emit delayed,
recurring, or sampled messages on another subject in the same stream. Each
schedule has a unique subject. `Nats-Schedule` accepts `@at <RFC3339>`, a
six-field UTC cron or alias such as `@hourly`, or a Go duration such as
`@every 5m`. Past `@at` values fire immediately.

`Nats-Schedule-Target` selects the output subject. `Nats-Schedule-Source`
instead republishes the latest message on a sampled subject.
`Nats-Schedule-TTL` becomes `Nats-TTL` on generated messages, while `Nats-TTL`
on the stored schedule controls the schedule record itself.

Schedule mode requires API level 2, can be enabled but not disabled on an
existing stream, and is rejected on sources and mirrors. Since 2.14.0,
`Nats-Schedule-Rollup` applies a roll-up to generated messages in the same way
that `Nats-Schedule-TTL` applies TTL.

## Source deduplication controls

Since 2.14.0, a stream with sources can disable source deduplication, while a
fan-in stream can deduplicate across multiple sources. Choose the setting from
the desired cross-source identity behavior rather than assuming every source
maintains an independent duplicate window.

## Whole-subject transforms

Subject transforms since 2.12.0 include `partition(n)`, a deterministic
partition derived from the whole subject, and `random(n)`, a random number up
to `n`. The older multi-argument `partition(n, ...)` remains available when
partitioning selected subject tokens.
