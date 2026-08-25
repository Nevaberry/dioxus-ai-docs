# Consumers and Sourcing

## Overflow pull-consumer groups

Since 2.11.0, a pull consumer can set one `PriorityGroups` entry with
`PriorityPolicy: "overflow"` and explicit acknowledgements. Every pull supplies
the group and may include `min_pending` and `min_ack_pending`; delivery starts
when either supplied threshold is met.

```go
ConsumerConfig{
    PriorityGroups: []string{"jobs"},
    PriorityPolicy: "overflow",
    AckPolicy:      "explicit",
}
```

```json
{"group":"jobs","min_pending":1000,"min_ack_pending":1000}
```

## Pinned-client pull-consumer groups

`PriorityPolicy: "pinned_client"` (since 2.11.0) selects one client while other
pulls wait as standbys. It coordinates new work but does not revoke work already
in flight. The selected client stores `Nats-Pin-Id` from the response and sends
it as `id` on later pulls. After a `423` mismatch, clear the ID and retry without
one.

```go
ConsumerConfig{
    PriorityGroups:  []string{"jobs"},
    PriorityPolicy:  "pinned_client",
    PriorityTimeout: 2 * time.Minute,
    AckPolicy:       "explicit",
}
```

Force reselection by publishing `{"group":"jobs"}` to
`$JS.API.CONSUMER.UNPIN.<STREAM>.<CONSUMER>`. Only `PriorityTimeout` is
updatable; the consumer cannot enter or leave grouped mode or change policies.

## Prioritized pull-consumer groups

`PriorityPolicy: "prioritized"` (since 2.12.0) lets a grouped pull receive work
sooner than overflow policy would. This lowers threshold waiting at the cost of
work potentially flip-flopping between clients. It uses explicit
acknowledgements and the same single `PriorityGroups` entry shape.

## Consumer pausing

`PauseUntil` (since 2.11.0) suspends delivery until a deadline. Set it when
creating the consumer or through the pause API. Delivery resumes automatically,
and heartbeats continue during the pause so clients do not interpret it as a
failure.

## Mirror promotion

Since 2.12.0, a mirror can be promoted into a primary stream for disaster
recovery. Delete the old primary or remove its subjects first, promote the
mirror second, and only then configure the promoted stream to listen on those
subjects. This ordering prevents two primaries from ingesting the same traffic.

## Reliable WorkQueue and Interest sourcing

Since 2.14.0, mirrors and sources of WorkQueue or Interest streams use durable,
replicated consumers instead of ephemeral `AckNone` consumers. Server-managed
consumers are visible as `JS_MIRROR_<suffix>` or `JS_SRC_<suffix>` and use
`AckFlowControl`, acknowledging only after the receiver persists messages.

An `AckFlowControl` consumer requires flow control and heartbeats, behaves like
`AckAll`, forbids `AckWait` and `BackOff`, and requires `MaxDeliver: -1`.
`MaxAckPending` bounds messages sent but not yet acknowledged; at the bound,
sourcing pauses and forces a flow-control acknowledgement.

For explicit lifecycle or security control, pre-create the durable consumer and
reference its name and delivery subject:

```json
{
  "name": "source",
  "consumer": {
    "name": "source-consumer",
    "deliver_subject": "source.consumer.deliver.subject"
  }
}
```

With a pre-created consumer, start sequence/time and filter settings belong on
the consumer, not `StreamSource`. This enables policies such as
`last_per_subject` and `ReplayPolicy=original`. A WorkQueue stream still cannot
have overlapping filtered consumers.

During mixed-version upgrades, older peers may log an unknown `sourcing` field
while an upgraded server retries the earlier consumer form. Downgrading to 2.12
returns these sources to less reliable ephemeral mode and can interrupt sourcing
during transition. `AckFlowControl` consumers remain offline until 2.14 support
returns.

## Consumer delivery-state reset

Since 2.14.0, publish an empty payload or `{"seq": N}` to
`$JS.API.CONSUMER.RESET.<STREAM>.<CONSUMER>`. An empty payload resets pending,
redelivery, delivered, and consumer ack-floor state while preserving the stream
ack floor. A positive sequence makes the next delivered message have a stream
sequence of at least `N`.

```bash
nats req '$JS.API.CONSUMER.RESET.ORDERS.WORKER' '{"seq":100}'
```

Arbitrary sequence reset is limited to `all`, `by_start_sequence`, and
`by_start_time` delivery policies and cannot violate the configured start
bound. The response includes the updated configuration and state plus
`ResetSeq`. A client must tolerate another actor resetting a non-ordered
consumer, which can make its delivery sequence non-monotonic.

## Replicated deletion and leader changes

Since 2.11.0, deletes in replicated Interest and WorkQueue streams are ordered
through Raft proposals, which may increase replication traffic. A new leader
waits for its Raft log to synchronize before serving reads or writes.
Replicated consumers redeliver unacknowledged messages after leader changes.
Configured start sequences are honored except on hidden source or mirror
consumers.
