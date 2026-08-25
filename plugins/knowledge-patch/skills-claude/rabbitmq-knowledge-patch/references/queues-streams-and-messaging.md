# Queues, Streams, and Messaging

Use this reference for queue and exchange declarations, quorum behavior,
Streams, AMQP semantics, Direct Reply-To, and commercial messaging features.

## Protect and configure queue resources (4.0.6, 4.1.0, 4.2.0)

### Virtual-host deletion protection

Virtual hosts can be protected from deletion through metadata.

### Stream retention policy command is a no-op

`rabbitmq-streams set_stream_retention_policy` does not change retention.
Configure Stream retention with a policy.

### Plugin-protected queues and streams

Plugins can mark queues and streams as protected from application deletion.

### Default queue type in virtual-host metadata

From 4.1.1, a new virtual host has its default queue type injected into
metadata so different definition-export methods agree.

### Disabling queue types

Administrators can disable individual queue types. Clients cannot declare new
queues or streams of a disabled type.

### Cluster-wide exchange limit

From 4.1.4, `cluster_exchange_limit` caps application-declared exchanges
cluster-wide, including protocol-standard predeclared exchanges. Use the same
value on every node.

```ini
cluster_exchange_limit = 200
```

### Disabling local-random exchanges

From 4.1.4, environments unable to preserve locality can reject declarations
of the local-random exchange type:

```ini
exchange_types.local_random.enabled = false
```

## Filter Stream messages (4.1-guides, 4.1.0, 4.2-guides)

### AMQP 1.0 stream filters

RabbitMQ supports the `properties` and `application-properties` filters from
AMQP Filter Expressions Working Draft 09. Concurrent consumers can select
different stream subsets without losing message order.

### AMQP 1.0 filter complexity limit

A property or application-property filter can inspect at most 16 properties.

### Broker-side SQL filtering for streams

AMQP 1.0 Stream consumers can combine a Bloom-filter value, which skips whole
chunks, with broker-side SQL over standard fields and application properties:

```java
String sql =
    "properties.subject = 'order.created' AND " +
    "region IN ('AMER', 'EMEA', 'APJ')";

Consumer consumer = connection.consumerBuilder()
    .queue(STREAM_NAME)
    .stream()
    .offset(FIRST)
    .filterValues("order.created")
    .filter()
        .sql(sql)
    .stream()
    .builder()
    .messageHandler((ctx, msg) -> ctx.accept())
    .build();
```

## Declare and route AMQP messages (4.0.6, 4.1.0, 4.2.0)

### AMQP 1.0 queue-purge response

The Erlang AMQP 1.0 client returns `404` when asked to purge a nonexistent
queue.

### Multiple AMQP 1.0 routing keys

An AMQP 1.0 publisher can put a list of string routing keys in the `x-cc`
message annotation, equivalent to the AMQP 0-9-1 `CC` header.

### Dynamic AMQP 1.0 nodes

Sources and targets honor the AMQP 1.0 `dynamic` field, allowing clients to
create exclusive queues dynamically for uses such as RPC.

### Durable-only Erlang AMQP declarations

The Erlang AMQP 1.0 client can declare only durable entities.

### AMQP 1.0 event-exchange publication

The event exchange plugin can publish events as AMQP 1.0, preserving complex
properties such as lists and maps.

### AMQP 1.0 durability when the header is omitted

When the AMQP 1.0 header section is absent, the specification default makes
`durable` false. Send a header with `durable=true` when persistence is needed.

### Direct Reply-To protocol changes

AMQP 1.0 supports Direct Reply-To and cross-protocol RPC with AMQP 0-9-1 in
either requester/responder direction. For a 0-9-1 responder using `mandatory`,
an `amq.rabbitmq.reply-to.*` target counts as routed without checking whether
the requester still consumes, so it does not cause `basic.return` when it is
the only target.

## Operate quorum queues and consumers (4.1.0, 4.3-guides, 4.3.0)

### Forced quorum-queue checkpoints

From 4.1.1, force matching quorum queues to checkpoint and delete eligible
on-disk segment files:

```shell
rabbitmq-queues force_checkpoint --vhost-pattern "vhost-pattern" --queue-pattern "queue-pattern"
```

### Emergency stream SAC activation

From 4.1.2, force a consumer to become active in a Stream Single Active
Consumer group:

```shell
rabbitmq-streams activate_stream_consumer --stream "stream-name" --reference "consumer-reference"
```

### Strict priorities for quorum queues

Quorum queues provide 32 strict priority levels: all higher-priority messages
are delivered first. This replaces the 4.0–4.2 two-level 2:1 interleaving
scheme. The management UI reports counts per priority.

### Native delayed retries for quorum queues

Set `x-delayed-retry-type` to `all`, `returned`, `failed`, or the default
`disabled`, with `x-delayed-retry-min` and `x-delayed-retry-max` milliseconds;
policy keys omit the `x-` prefix. Delay is
`min(delayed-retry-min * delivery-count, delayed-retry-max)`, and the maximum
defaults to the minimum. AMQP 1.0 `modified` can override the delay per message
with Unix-millisecond annotation `x-opt-delivery-time`.

### Returns no longer necessarily consume the poison-message limit

Every requeue increments `acquired-count`, but only failures increment
`delivery-count`, which drives poison-message handling. Non-failures include
AMQP 1.0 `released`, `modified` with `delivery-failed=false`, AMQP 0.9.1
`basic.nack`, suspect consumer nodes during a partition, and consumer timeout.
Failures include `rejected`, `modified` with `delivery-failed=true`,
`basic.reject`, and client or connection loss.

### Quorum-queue consumer timeout behavior

Quorum and Tanzu JMS queues evaluate consumer timeouts; classic queues and
streams do not. Timed-out AMQP 1.0 deliveries are released without link
detach. AMQP 0.9.1 cancels the consumer when `consumer_cancel_notify` is
supported, otherwise closes the channel. Precedence is consumer
`x-consumer-timeout`, queue `x-consumer-timeout`, policy `consumer-timeout`,
then global `consumer_timeout`, default `1800000` ms.

### Disconnected-consumer timeout for quorum queues

When a consumer node becomes unreachable, quorum queues wait 60 seconds by
default before returning messages. Override globally with
`consumer_disconnected_timeout`, by policy with
`consumer-disconnected-timeout`, or per queue with
`x-consumer-disconnected-timeout`.

### Dynamic quorum-queue delivery limits

Change a quorum queue's delivery limit through policy without redeclaring it.

### Quorum-queue purge scope

Purging also deletes at-least-once dead-lettered messages still pending
delivery.

## Process AMQP outcomes and exchange routing (4.3-guides, 4.3.0, 4.3.5)

### AMQP 1.0 rejection diagnostics

A `Rejected` outcome identifies the rejecting queue and reason, such as a
length limit or unavailable queue, even when one publish targets many queues.

### AMQP 1.0 single-active-consumer state notifications

AMQP 1.0 consumers on a quorum queue receive active/inactive Single Active
Consumer state immediately in flow-frame properties.

### Core `x-modulus-hash` exchange

`x-modulus-hash` moved from the sharding plugin into core. With stable
bindings, its distribution remains stable across node restarts.

### Direct Reply-To deduplication

If multiple Direct Reply-To targets resolve to the same process, RabbitMQ
delivers the message to that process once.

### Topic-exchange wildcard limit

A topic binding key can contain no more than two multi-segment `#` wildcards.
Prefer one `#` as the final segment.

## Use protocol-specific queue behavior (4.3.0)

### Exclusive queues for affected STOMP destinations

STOMP subscriptions whose destinations formerly used non-exclusive transient
queues now use exclusive queues.

## Use commercial queue and Stream capabilities (4.3-guides)

### Tanzu JMS queue type

The commercial Tanzu edition adds a Raft-backed queue optimized for Qpid JMS
and usable over AMQP 1.0, AMQP 0.9.1, STOMP, and MQTT. It supports selectors
after fields are indexed with `x-selector-fields` or policy
`selector-fields`, non-destructive `QueueBrowser` inspection with selectors,
and `MessageProducer.setDeliveryDelay(...)`.

### Tanzu RabbitMQ Stream connector for Spark

The commercial Spark Structured Streaming `rabbitmq-stream` source supports
streams and super streams, head/tail/offset/timestamp starts, field projection,
per-trigger rate limits, and AMQP payload/property access. Relevant options
include `uris`, `super.stream`, `starting.offsets`, and
`rmq.stream.select.fields`.

### Tanzu delayed-message scheduler

The community `rabbitmq-delayed-message-exchange` plugin is deprecated and
archived. Tanzu provides a Raft-backed Delayed Queue plugin using AMQP 1.0
`x-opt-delivery-time` or `x-opt-delivery-delay`, routing through exchanges at
expiry. Unlike quorum delayed retries it supports delayed fan-out, browsing,
selective purge, and warm-standby replication.
