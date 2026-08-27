# Consumers, Mirrors, and Sources

## Pull-consumer priority groups

### Overflow policy

Since 2.11.0, a pull consumer may configure one `PriorityGroups` entry with
`PriorityPolicy: "overflow"`. It requires `AckPolicy: "explicit"`. Every pull
must supply the group and may supply `min_pending` and `min_ack_pending`;
delivery starts when either supplied threshold is met.

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

### Pinned-client policy

Since 2.11.0, `PriorityPolicy: "pinned_client"` selects one client for delivery
while other pulls wait as standbys. It coordinates new work but does not revoke
work already in flight.

```go
ConsumerConfig{
    PriorityGroups:  []string{"jobs"},
    PriorityPolicy:  "pinned_client",
    PriorityTimeout: 2 * time.Minute,
    AckPolicy:       "explicit",
}
```

The selected client stores the `Nats-Pin-Id` response header and sends it as
`id` on later pulls. After a `423` mismatch, clear the ID and retry without it.
An administrator can force reselection by publishing `{"group":"jobs"}` to:

```text
$JS.API.CONSUMER.UNPIN.<STREAM>.<CONSUMER>
```

Only `PriorityTimeout` is updatable. A consumer cannot switch into or out of
grouped mode or change its priority policy after creation.

### Prioritized policy

Since 2.12.0, `PriorityPolicy: "prioritized"` lets a grouped pull request
receive work sooner than overflow thresholds would, at the cost of work
potentially moving back and forth between clients.

```go
ConsumerConfig{
    PriorityGroups: []string{"jobs"},
    PriorityPolicy: "prioritized",
    AckPolicy:      "explicit",
}
```

## Consumer pausing

Since 2.11.0, `PauseUntil` suspends delivery until a deadline. Set it at
creation or through the pause API. Delivery resumes automatically, and
heartbeats continue during the pause so clients do not infer a failure.

## Reliable WorkQueue and Interest sourcing

Since 2.14.0, mirrors and sources of WorkQueue or Interest streams use durable,
replicated consumers instead of ephemeral `AckNone` consumers. Server-managed
consumers are visible as `JS_MIRROR_<suffix>` or `JS_SRC_<suffix>` and use
`AckFlowControl`; they acknowledge only after the receiving server persists the
message.

An `AckFlowControl` consumer:

- requires flow control and heartbeats;
- behaves like `AckAll`;
- forbids `AckWait` and `BackOff`;
- requires `MaxDeliver: -1`; and
- uses `MaxAckPending` to bound unacknowledged sourcing before delivery pauses
  and a flow-control acknowledgement is forced.

For explicit lifecycle or security control, pre-create the durable consumer and
reference its name and delivery subject in the source:

```json
{
  "name": "source",
  "consumer": {
    "name": "source-consumer",
    "deliver_subject": "source.consumer.deliver.subject"
  }
}
```

With a pre-created consumer, put starting sequence or time and filters on the
consumer rather than `StreamSource`. This supports policies such as
`last_per_subject` and `ReplayPolicy=original`. A WorkQueue stream still cannot
have overlapping filtered consumers.

During a mixed-version upgrade, older peers may log an unknown `sourcing` field
while the upgraded server retries the old consumer form. A downgrade to 2.12
returns these sources to the less reliable ephemeral mode, may interrupt
sourcing, and leaves `AckFlowControl` consumers offline until 2.14 is restored.

## Consumer delivery-state reset

Since 2.14.0, publish an empty payload or `{"seq": N}` to:

```text
$JS.API.CONSUMER.RESET.<STREAM>.<CONSUMER>
```

An empty payload resets pending, redelivery, delivered, and consumer ack-floor
state while retaining the stream ack floor. A positive sequence makes the next
delivered message have a stream sequence of at least `N`.

```bash
nats req '$JS.API.CONSUMER.RESET.ORDERS.WORKER' '{"seq":100}'
```

Arbitrary sequence reset is limited to `all`, `by_start_sequence`, and
`by_start_time` delivery policies and cannot violate the configured start
bound. The response includes the updated configuration and state plus
`ResetSeq`. Clients must tolerate another process resetting a non-ordered
consumer and making its delivery sequence non-monotonic.

## Mirror promotion

Since 2.12.0, a mirror can be promoted to a primary for disaster recovery.
Delete the old primary or remove its subjects first, promote the mirror second,
and only then configure the promoted stream to listen on those subjects. This
ordering prevents two primaries from ingesting the same traffic.

## Replication and leader changes

Since 2.11.0, deletes in replicated Interest and WorkQueue streams are ordered
through Raft proposals, which can increase replication traffic. A new leader
waits for its Raft log to synchronize before reads or writes. Replicated
consumers redeliver unacknowledged messages after leader changes.

Configured consumer start sequences are honored except for hidden source and
mirror consumers.
