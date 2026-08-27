# Protocols, Clustering, and Federation

Use this reference for cluster formation, discovery, wire-protocol limits,
WebSocket listeners, federation, Shovels, and replication networking.

## Form and recover clusters (4.0.6, 4.1.0)

### Khepri cluster-formation timeout

Khepri's default cluster-formation timeout is five minutes, matching Mnesia.

### Optional Consul registration

Let Consul provide discovery without registering services when another system
owns registration:

```ini
cluster_formation.registration.enabled = false
```

### Infinite peer-discovery retries

`cluster_formation.discovery_retry_limit` accepts `infinity` as well as
positive integers.

### Reset Mnesia nodes can rejoin

A reset former Mnesia cluster member attempts to leave the cluster and retries
joining it, matching Khepri behavior.

### Kubernetes peer-discovery seed model

Kubernetes peer discovery no longer depends on the Kubernetes API. At first
formation it attempts to join node index `0` as the seed; the change is
backwards compatible.

### IPv6-only AWS peer discovery

From 4.1.7, AWS peer discovery uses IPv6 discovery endpoints in IPv6-only
environments.

## Configure Stream replication networking (4.0.6, 4.1.0)

### IPv6 stream replication

Select IPv6 for Stream replication in `advanced.config`:

```erlang
[
  {osiris, [{replica_ip_address_family, inet6}]}
].
```

### Stream replication IP family in `rabbitmq.conf`

From 4.1.7, select the IPv4 or IPv6 family for replication in
`rabbitmq.conf`; the earlier `advanced.config` mechanism remains available.

## Respect protocol frame and packet limits (4.1-guides, 4.3.5)

### AMQP 0-9-1 pre-authentication frame limit

The pre-authentication maximum frame is 8192 bytes. Client `frame_max`
overrides must be at least 8192; the recommended server default is 131072.
Node.js `amqplib` needs 0.10.7 or later unless configured with a larger value.

### MQTT maximum packet size

The default MQTT Maximum Packet Size is 16 MiB. Override it with
`mqtt.max_packet_size_authenticated`, never above `max_message_size`, whose
default is also 16 MiB.

### Stream connection resource limits

A Stream Protocol connection supports at most 256 publishers and 256
subscriptions. Exceeding either wire-format limit is rejected immediately.

### Pre-authentication Stream frame limit

Before a successful Stream `open`, frames default to an 8192-byte ceiling.
Raise it only when authentication requires a larger frame:

```ini
stream.initial_frame_max = 8192
```

### Stream sub-entry decompression limit

`stream.max_uncompressed_sub_entry_batch_size` caps the declared uncompressed
size of a published sub-entry batch and defaults to 67108864 bytes (64 MiB).
Use the same value in publishers and on the broker.

```ini
stream.max_uncompressed_sub_entry_batch_size = 67108864
```

### STOMP frame-size enforcement

STOMP enforces frame limits earlier during setup. Web STOMP checks accumulated
post-authentication frame size against `max_frame_size`.

## Configure TCP and WebSocket transports (4.1-guides, 4.1.0, 4.2.0, 4.3.0)

### Auto-tuned AMQP user-space TCP buffers

AMQP listeners auto-tune their user-space TCP buffer, so
`tcp_listen_options.buffer` is ignored. Kernel `recbuf` and `sndbuf` settings
are unaffected.

### MQTT 3.1 over WebSocket

From 4.1.7, Web MQTT accepts the `mqttv3.1` WebSocket subprotocol as well as
`mqtt`.

### HTTP/2 WebSocket defaults

Web MQTT and Web STOMP enable HTTP/2 for WebSocket connections by default.

### WebSocket connection protections

Web MQTT bounds decompressed frames at
`mqtt.max_packet_size_unauthenticated`, raises the ceiling after successful
`CONNECT`, and enforces `login_timeout`. Configure origin validation with
`web_mqtt.allow_origins` and `web_stomp.allow_origins`.

## Handle MQTT protocol outcomes (4.3.0, 4.3.5)

### MQTT 5.0 queue-limit feedback

If a target queue rejects a publish because its maximum length is reached, an
MQTT 5.0 publisher receives `Quota exceeded` in `PUBACK`.

### Strict MQTT 5 property validation

MQTT 5 rejects properties invalid for their packet type and rejects the
prohibited `Receive Maximum` value `0`.

## Operate federation and Shovels (4.1.0, 4.2.0, 4.3.0, 4.3.5)

### MQTTv5 consumers over exchange federation

Exchange federation supports MQTTv5 consumers.

### Mixed-version exchange federation

RabbitMQ 4.1.8 restores exchange-federation compatibility in mixed
4.2.x/4.1.x multi-node clusters.

### Federation connection-close timeout

From 4.1.8, configure separate AMQP 0-9-1 close timeouts for exchange and
queue federation, in milliseconds up to 5000:

```ini
federation.exchanges.connection_close_timeout = 3000
federation.queues.connection_close_timeout = 3000
```

### Local shovels

The `local` Shovel protocol consumes and publishes inside one cluster over
AMQP 1.0, reusing intra-cluster connections and internal flow APIs. It cannot
connect different clusters.

### Named Shovel source consumers

Use `src-consumer-name` as the source consumer tag for AMQP 0-9-1 or local
Shovels, or as the AMQP 1.0 source link identifier.

### Dynamic Shovel TTL

Dynamic Shovels accept `src-delete-after-duration` and delete themselves after
at least the configured duration.

## Integrate broker-side protocol extensions (4.2.0)

### Native-protocol message interceptors

Incoming and outgoing broker-side interceptors cover AMQP 1.0, AMQP 0-9-1,
MQTTv3, and MQTTv5. Plugins can validate, annotate, or produce side effects;
optional built-ins add outgoing timestamps or the publishing MQTT client ID.
