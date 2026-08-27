# Federation, Shovels, and extensions

## Federation

### Protocol and mixed-version support (`4.1.0`)

Exchange federation works with MQTTv5 consumers. RabbitMQ 4.1.8 restores
exchange-federation compatibility in mixed 4.2.x/4.1.x multi-node clusters;
keep mixed versions only for a rolling upgrade.

### Connection-close timeout

Starting in 4.1.8, configure the AMQP 0-9-1 close timeout separately for
exchange and queue federation. Values are milliseconds and cannot exceed 5000:

```ini
federation.exchanges.connection_close_timeout = 3000
federation.queues.connection_close_timeout = 3000
```

### Management permissions

Restarting a federation link through management requires the `policymaker`
user tag (`4.3.0`).

## Shovels

### Local protocol (`4.2.0`)

Use Shovel protocol option `local` to consume and publish within one cluster.
It uses AMQP 1.0, reuses intra-cluster connections, and invokes internal
consumption, publishing, and credit-flow APIs rather than opening separate TCP
connections. It cannot connect different clusters.

Direct AMQP 0-9-1 in-cluster Shovel connections are blocked by resource alarms
just like network connections. That alarm behavior does not apply to the
`local` protocol.

### Source consumer names and lifetime

Set `src-consumer-name` to choose the AMQP 0-9-1 or local source consumer tag,
or the AMQP 1.0 source link identifier. Dynamic Shovels accept
`src-delete-after-duration`, which deletes the Shovel after at least the
specified duration (`4.3.5`).

Deleting a Shovel through management requires `policymaker`.

## Peer discovery

The Kubernetes peer-discovery plugin no longer relies on the Kubernetes API.
During first formation it attempts to join the node at index `0` as the seed;
the behavior remains backward compatible.

The AWS peer-discovery plugin uses IPv6 discovery endpoints in IPv6-only
environments starting in 4.1.7. Consul discovery can be used without Consul
service registration:

```ini
cluster_formation.registration.enabled = false
```

An infinite peer-discovery retry count is also valid:

```ini
cluster_formation.discovery_retry_limit = infinity
```

## Plugin extension points

Plugins can mark queues and streams as protected against application deletion.
Native-protocol incoming and outgoing message interceptors support AMQP 1.0,
AMQP 0-9-1, MQTTv3, and MQTTv5. Custom interceptors can validate, annotate, or
perform side effects; optional built-ins add outgoing timestamps or the
publishing MQTT client's ID.

The event-exchange plugin can publish internal events as AMQP 1.0, preserving
list and map properties that AMQP 0-9-1 cannot preserve in the same way.

Third-party plugins should use the dedicated data directory preserved during a
Mnesia-to-Khepri migration. Non-whitelisted directories inside the node data
directory may be removed when migration completes.

## Tanzu extensions (`4.3-guides`)

### JMS queue type

The commercial Tanzu edition adds a Raft-backed JMS queue optimized for Qpid
JMS and usable through AMQP 1.0, AMQP 0-9-1, STOMP, and MQTT. It supports:

- Broker-side selectors after fields are indexed with queue argument
  `x-selector-fields` or policy key `selector-fields`.
- Non-destructive `QueueBrowser` inspection with selectors.
- `MessageProducer.setDeliveryDelay(...)`.

Consumer-timeout semantics for this queue type match quorum queues.

### Stream connector for Spark

The Tanzu RabbitMQ Stream connector provides a `rabbitmq-stream` Spark
Structured Streaming source for streams and super streams. It supports starting
at head, tail, offset, or timestamp; field projection; per-trigger rate limits;
and AMQP payload/property access. Important options include `uris`,
`super.stream`, `starting.offsets`, and `rmq.stream.select.fields`.

### Stream Browser

The commercial Stream Browser management plugin inspects streams and super
streams from an offset, timestamp, head, or tail. It exposes AMQP 1.0 sections
and the segment/chunk layout and can selectively download message sections.

### Delayed Queue

The archived community `rabbitmq-delayed-message-exchange` plugin is
deprecated. Tanzu's Raft-backed Delayed Queue schedules messages using AMQP 1.0
`x-opt-delivery-time` or `x-opt-delivery-delay`, then routes through exchanges
when the delay expires.

Unlike quorum-queue delayed retries, it supports delayed fan-out. It also
provides browsing, selective purge, and warm-standby replication.
