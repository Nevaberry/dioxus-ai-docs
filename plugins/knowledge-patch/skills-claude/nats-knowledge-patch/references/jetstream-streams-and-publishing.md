# JetStream Streams and Publishing

## Request validation and ingest buffering

### Strict requests by default

Since 2.12.0, JetStream strict mode is enabled by default. JSON requests with
unknown fields are rejected instead of merely logged. Update invalid clients;
use the following only as a temporary compatibility switch:

```text
jetstream {
  strict: false
}
```

### Core publish backpressure

Since 2.11.0, Core NATS publishing into JetStream is bounded per stream by
`max_buffered_size` (default `128MB`) and `max_buffered_msgs` (default `10,000`).
Earlier unbounded assumptions are unsafe. Exceeding either limit may drop
messages and return `429 JSStreamTooManyRequests`. JetStream publishers that
wait for PubAcks should not normally hit this buffer limit.

```text
jetstream {
  max_buffered_msgs: 50000
  max_buffered_size: 256mib
}
```

## Per-message TTL

Since 2.11.0, a stream must opt in with `AllowMsgTTL`; publishers may then set
`Nats-TTL` to integer seconds, a Go duration such as `1h`, or `never`.

```go
StreamConfig{AllowMsgTTL: true}
```

`never` exempts the message from stream `MaxAge`. Invalid or sub-second values
reject and discard the publish. `AllowMsgTTL` cannot be disabled after it is
enabled.

Sources and mirrors always accept and store an incoming `Nats-TTL` header, but
expire that message only if their own `AllowMsgTTL` is enabled. A direct publish
with `Nats-TTL` to a stream that has not enabled the feature is rejected.

## Subject delete markers

Since 2.11.0, `SubjectDeleteMarkerTTL` creates a marker when age-based removal
deletes the final message for a subject. The marker carries:

```text
Nats-Marker-Reason: MaxAge
Nats-TTL: 1m0s
```

Delete and purge API calls do not create markers, and mirrors cannot enable the
setting. It requires roll-ups and purge permission. Normal create or update
requests enable `AllowRollup` and clear `DenyPurge`; pedantic requests fail
instead.

Except when `MaxMsgsPer` is `1`, the marker TTL is also the minimum effective
per-message TTL. Smaller TTLs are accepted but clamped, and the stored
`Nats-TTL` header is rewritten.

## Atomic stream batch publishing

Since 2.12.0, `AllowAtomicPublish` enables all-or-nothing batches. It requires
API level 2, is incompatible with asynchronous persistence, and cannot be
enabled on mirrors.

```go
StreamConfig{AllowAtomicPublish: true}
```

Every message carries the same batch ID and a contiguous sequence. The first
publish must be a request, and the final stored message adds the commit header:

```text
Nats-Batch-Id: order-42
Nats-Batch-Sequence: 3
Nats-Batch-Commit: 1
```

Only the final message gets a normal PubAck. Its `batch` and `count` fields
identify the committed batch. A batch is limited to 1,000 messages, expires
after 10 idle seconds, and rejects `Nats-Msg-Id` and
`Nats-Expected-Last-Msg-Id`. Abandonment emits:

```text
io.nats.jetstream.advisory.v1.stream_batch_abandoned
```

## Fast and end-of-batch publishing

Since 2.14.0, `AllowBatchPublish` enables flow-controlled, high-throughput
publishing to replicated or non-replicated streams. It applies per-message
consistency checks without atomic publishing's intermediate staging.

```go
StreamConfig{AllowBatchPublish: true}
```

Both atomic and fast batches can commit with an EOB message that is not itself
persisted.

## Distributed counter streams

Since 2.12.0, `AllowMsgCounter` makes each subject an arbitrary-precision signed
counter. Every publish must carry `Nats-Incr` as a signed integer. The server
replaces the body with `{"val":"..."}` and returns the same total in the PubAck.

```go
StreamConfig{AllowMsgCounter: true}
```

```bash
nats req counter.hits '' -J -H 'Nats-Incr:+2'
```

Counter mode is creation-only, requires Limits retention and API level 2, and
is incompatible with mirrors, DiscardNew, per-message TTL, message schedules,
and publishes without a counter increment.

Sourced aggregate counters track each upstream total in `Nats-Counter-Sources`
and apply its delta. Aggregation remains eventually consistent across missed
source messages. Reset one source's contribution with a compensating negative
increment: purge does not replicate, and roll-up would destroy the combined
counter.

## JetStream message schedules

Since 2.12.0, `AllowMsgSchedules` lets one stored record produce a delayed,
recurring, or sampled message on another subject in the same stream. Each
schedule requires a unique subject. `Nats-Schedule` accepts:

- `@at <RFC3339>`;
- a six-field UTC cron expression or alias such as `@hourly`; or
- a Go-duration interval such as `@every 5m`.

```go
StreamConfig{
    AllowMsgSchedules: true,
    AllowMsgTTL:       true,
}
```

```bash
nats pub -J schedules.orders.once \
  -H 'Nats-Schedule: @at 2025-10-01T12:00:00Z' \
  -H 'Nats-Schedule-Target: orders' \
  -H 'Nats-Schedule-TTL: 5m' \
  'body'
```

`Nats-Schedule-Source` republishes the latest message on a sampled subject.
`Nats-Schedule-TTL` becomes `Nats-TTL` on generated messages, whereas
`Nats-TTL` on the schedule record limits the schedule itself. A past `@at`
fires immediately.

Schedule mode requires API level 2. It may be enabled but not disabled on an
existing stream and is rejected on sources and mirrors.

Since 2.14.0, `Nats-Schedule-Rollup` applies a roll-up to a generated message in
the same way `Nats-Schedule-TTL` applies its TTL. Streams with sources may also
disable deduplication, and fan-in streams may deduplicate across sources.

## Whole-subject transforms

Since 2.12.0, subject transforms support `partition(n)`, which deterministically
partitions from the whole subject, and `random(n)`, which selects a random
number up to `n`. The older multi-argument `partition(n, …)` remains available
for selected subject tokens.
