# Queues, streams, and exchanges

## Queue protection, declaration, and metadata

Virtual hosts can carry metadata that protects them from deletion (`4.0.6`).
Plugins can likewise mark queues and streams as protected so applications
cannot delete them. Administrators can disable individual queue types; clients
then cannot declare a new queue or stream of a disabled type.

Starting in 4.1.1, a new virtual host's default queue type is injected into its
metadata, keeping definition exports consistent across export methods
(`4.1.0`).

For 4.3's transient non-exclusive queue default and CQv1 removal, follow the
migration reference before changing declarations.

## Quorum queues

### Leadership, shutdown, and checkpoints

Check matching queues for an elected leader:

```shell
rabbitmq-diagnostics check_for_quorum_queues_without_an_elected_leader \
  --vhost "vh-1" "^naming-pattern"
```

Use `--across-all-vhosts ".*"` for a cluster-wide check, but expect it to be
expensive with many queues. Before stopping a node, check quorum criticality and
wait for quorum-plus-one:

```shell
rabbitmq-diagnostics check_if_node_is_quorum_critical
rabbitmq-upgrade await_online_quorum_plus_one
```

Starting in 4.1.1, force matching queues to checkpoint and remove eligible
on-disk segment files with:

```shell
rabbitmq-queues force_checkpoint \
  --vhost-pattern "vhost-pattern" --queue-pattern "queue-pattern"
```

### Strict priorities (`4.3-guides`)

Quorum queues support 32 strict priority levels: all higher-priority messages
are delivered before any lower-priority message. This replaces the 4.0-4.2
two-level scheme that interleaved high and normal deliveries at 2:1. The
management UI reports counts for each priority.

### Delayed retries

Quorum queues can delay returned messages without a dead-letter cycle or
external scheduler. Configure queue arguments `x-delayed-retry-type`
(`disabled`, `all`, `returned`, or `failed`), `x-delayed-retry-min`, and
`x-delayed-retry-max`, or the equivalent policy keys without `x-`.

The delay is
`min(delayed-retry-min * delivery-count, delayed-retry-max)`; maximum defaults
to minimum. AMQP 1.0 can override a message's delay using the Unix-millisecond
`x-opt-delivery-time` annotation on a modified outcome.

### Delivery counts and poison handling

Every requeue increments `acquired-count`, but only failed attempts increment
`delivery-count`. Poison-message handling uses `delivery-count`, so ordinary
returns may be unlimited.

Non-failures include AMQP 1.0 `released`, `modified` with
`delivery-failed=false`, AMQP 0-9-1 `basic.nack`, a partition that makes the
consumer node suspect, and a consumer timeout. Failures include `rejected`,
`modified` with `delivery-failed=true`, `basic.reject`, and client or connection
loss.

### Consumer timeouts and disconnection

Consumer timeouts apply to quorum and Tanzu JMS queues, not classic queues or
streams. Precedence is consumer `x-consumer-timeout`, queue
`x-consumer-timeout`, policy `consumer-timeout`, then global
`consumer_timeout`; the global default is 1,800,000 ms.

For AMQP 1.0, a timed-out delivery is released without detaching its link. For
AMQP 0-9-1, RabbitMQ cancels only the affected consumer when
`consumer_cancel_notify` is supported; otherwise it closes the channel.

In `4.3.0`, a quorum queue waits 60 seconds by default before returning
messages from a consumer whose node is unreachable. Override this globally
with `consumer_disconnected_timeout`, by policy with
`consumer-disconnected-timeout`, or per queue with
`x-consumer-disconnected-timeout`.

### Delivery limits and purge

A quorum queue's delivery limit can be changed by policy without redeclaring
the queue. Purging a quorum queue also deletes at-least-once dead-lettered
messages that still await delivery.

## Streams

### Retention and replication

Set retention using a policy; the old retention-policy command is a no-op.
Stream replication can use IPv6 via `advanced.config`:

```erlang
[
  {osiris, [{replica_ip_address_family, inet6}]}
].
```

Starting in 4.1.7, select the IPv4 or IPv6 family in `rabbitmq.conf` as well.

### AMQP 1.0 filters

RabbitMQ initially supports the `properties` and `application-properties`
filters from AMQP Filter Expressions Working Draft 09. Each filter can inspect
at most 16 properties. Concurrent consumers can select different subsets of a
stream while preserving message order.

From `4.2-guides`, consumers can add a broker-side SQL expression over standard
fields and application properties. Use a Bloom-filter value to skip chunks,
then apply SQL to matching messages:

```java
Consumer consumer = connection.consumerBuilder()
    .queue(STREAM_NAME)
    .stream().offset(FIRST)
    .filterValues("order.created")
    .filter().sql("properties.subject = 'order.created' " +
                  "AND region IN ('AMER', 'EMEA', 'APJ')")
    .stream().builder()
    .messageHandler((ctx, msg) -> ctx.accept())
    .build();
```

### Single Active Consumer

From 4.1.2, an operator can make a selected Stream Single Active Consumer group
member active:

```shell
rabbitmq-streams activate_stream_consumer \
  --stream "stream-name" --reference "consumer-reference"
```

AMQP 1.0 consumers of quorum queues with Single Active Consumer receive
active/inactive changes immediately as flow-frame properties.

### Connection and frame limits (`4.3.5`)

A Stream Protocol connection accepts at most 256 publishers and 256
subscriptions. Excess attempts are rejected immediately.

Before a successful `open`, frames default to an 8192-byte limit. Increase it
only when authentication requires a larger frame:

```ini
stream.initial_frame_max = 8192
```

`stream.max_uncompressed_sub_entry_batch_size` limits the declared uncompressed
size of a sub-entry batch and defaults to 67,108,864 bytes (64 MiB). Give
publishers the same value as the broker:

```ini
stream.max_uncompressed_sub_entry_batch_size = 67108864
```

## Exchanges and routing

### Exchange counts and types

Starting in 4.1.4, `cluster_exchange_limit` caps application-declared exchanges
across the cluster, including protocol-standard predeclared exchanges. Every
node must use the same value:

```ini
cluster_exchange_limit = 200
```

Disable the local-random exchange type where load balancers cannot preserve
locality; declarations then fail:

```ini
exchange_types.local_random.enabled = false
```

In 4.3, `x-modulus-hash` moves from the sharding plugin into core. Its routing
distribution remains stable across restarts while the binding set is stable.

### Topic wildcard ceiling

A topic-exchange binding key may contain at most two multi-segment (`#`)
wildcards. Prefer a single `#` as the final segment.

### Multiple routing keys

An AMQP 1.0 publisher can place a list of string routing keys in the `x-cc`
message annotation, equivalent to the AMQP 0-9-1 `CC` header.
