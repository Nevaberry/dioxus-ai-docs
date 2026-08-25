# Protocols and clients

## AMQP 1.0

### Authentication and token renewal (`4.1.0`)

An AMQP 1.0 client can replace a JWT before it expires without disconnecting.
If the client does not replace the token in time, RabbitMQ closes the
connection. A failed token renewal on the Stream Protocol closes that
connection immediately and the replacement token is checked again for access
to the current virtual host.

### Dynamic nodes and declarations

RabbitMQ honors `dynamic` on AMQP 1.0 sources and targets, so clients can create
exclusive queues dynamically for patterns such as RPC. The Erlang AMQP 1.0
client can declare durable entities only. When that client purges a nonexistent
queue, it returns HTTP-style status `404` (`4.0.6`).

### Message durability (`4.2.0`)

If a sender omits the AMQP 1.0 header section, RabbitMQ applies the
specification default `durable = false`. Applications requiring durable
messages must include a header with `durable = true`.

### Routing keys and filters

Put a list of string routing keys in message annotation `x-cc` to obtain the
AMQP 0-9-1 `CC`-header behavior. Property and application-property filters can
select ordered subsets of a stream, but may inspect no more than 16 properties.
For richer filtering, use stream SQL expressions as described in the streams
reference.

### Direct Reply-To

AMQP 1.0 supports Direct Reply-To, including RPC where requester and responder
use AMQP 1.0 and AMQP 0-9-1 in either combination. When an AMQP 0-9-1 responder
publishes with `mandatory`, an `amq.rabbitmq.reply-to.*` destination counts as
routed without checking whether the requester is still consuming, so it does
not by itself cause `basic.return`.

If several Direct Reply-To targets resolve to the same process, RabbitMQ sends
the message to that process only once (`4.3.5`).

### Delivery outcomes and diagnostics

A `Rejected` outcome identifies the rejecting queue and reason, such as a queue
length limit or unavailable queue, so a publisher routed to several queues can
identify the failed target. For quorum queues, `released` and `modified` with
`delivery-failed=false` do not increment `delivery-count`; `rejected` and
`modified` with `delivery-failed=true` do.

An AMQP 1.0 consumer timeout releases the delivery without detaching the link.
Single Active Consumer links on quorum queues receive active/inactive changes
immediately through flow-frame properties.

### Event exchange

The event-exchange plugin can publish its internal events as AMQP 1.0 instead
of AMQP 0-9-1, preserving complex property values such as lists and maps.

## AMQP 0-9-1

### Pre-authentication frame size (`4.1-guides`)

The minimum pre-authentication frame ceiling is 8192 bytes, up from 4096. A
client `frame_max` override must be at least 8192; leaving the server default of
131072 is recommended. Node.js `amqplib` should be 0.10.7 or later, or be
configured with a sufficiently large explicit value.

### Permission reevaluation

Refreshing connection credentials clears the permission cache and immediately
revalidates consumer permissions. Passive queue and exchange declarations now
require `configure`, matching normal declarations.

### Quorum consumer outcomes

For a timed-out quorum-queue consumer, RabbitMQ cancels only that consumer if
the client supports `consumer_cancel_notify`; otherwise it closes the channel.
`basic.nack` is a non-failure for delivery-count purposes, while
`basic.reject` is a failure.

## MQTT

### Packet sizes and properties

The default MQTT Maximum Packet Size is 16 MiB instead of 256 MiB. Override it
with `mqtt.max_packet_size_authenticated`, but never above `max_message_size`,
which also defaults to 16 MiB.

MQTT 5 validates properties strictly by packet type and rejects the prohibited
`Receive Maximum` value `0`. When a queue rejects a publish because its maximum
length has been reached, an MQTT 5 publisher receives `Quota exceeded` in
`PUBACK`.

### Authorization failures

Starting in 4.1.8, `mqtt.disconnect_on_unauthorized` chooses whether an
authorization failure closes the connection. The default is `true`; keep the
connection and return the protocol error with:

```ini
mqtt.disconnect_on_unauthorized = false
```

### Web MQTT

From 4.1.7, Web MQTT accepts WebSocket subprotocol `mqttv3.1` as well as
`mqtt`. It bounds decompressed frames using
`mqtt.max_packet_size_unauthenticated` before `CONNECT` and a larger
authenticated limit afterward, and it enforces `login_timeout`.

Configure origin validation with `web_mqtt.allow_origins`. HTTP/2 is enabled by
default for Web MQTT in 4.2. MQTT, Web MQTT, and STOMP remain blocked until all
active resource alarms clear.

### Federation

Exchange federation supports MQTTv5 consumers. See the federation reference
for mixed-version compatibility.

## STOMP and Web STOMP

STOMP subscriptions whose destinations previously used non-exclusive transient
queues now use exclusive queues. STOMP enforces frame-size limits earlier in
connection setup; Web STOMP checks the accumulated post-authentication frame
against `max_frame_size`.

Configure Web STOMP origin validation with `web_stomp.allow_origins`. HTTP/2 is
enabled by default for Web STOMP in 4.2.

## WebSocket client checklist

- Account for HTTP/2 being enabled by default on Web MQTT and Web STOMP.
- Configure origin allowlists for both plugins.
- Ensure MQTT clients send `CONNECT` before depending on the larger
  authenticated decompression ceiling.
- Ensure STOMP clients remain below the configured complete-frame size.
- Expect all three protocol families to remain blocked while any memory or
  disk alarm remains active.
