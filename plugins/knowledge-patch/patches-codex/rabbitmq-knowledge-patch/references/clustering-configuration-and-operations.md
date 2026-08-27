# Clustering, configuration, and operations

## Cluster formation and metadata stores

### Timeouts, retries, and registration (`4.0.6`)

Khepri's default cluster-formation timeout is five minutes, matching Mnesia.
Peer discovery accepts an infinite retry count as well as positive integers:

```ini
cluster_formation.discovery_retry_limit = infinity
```

When Consul supplies discovery but another system such as Nomad owns service
registration, disable Consul registration independently:

```ini
cluster_formation.registration.enabled = false
```

A reset former Mnesia cluster member now attempts to leave its old cluster and
retries joining the new cluster, matching Khepri behavior.

### Metadata readiness

Use separate checks for basic initialization and initialization with data:

```shell
rabbitmq-diagnostics check_if_metadata_store_is_initialized
rabbitmq-diagnostics check_if_metadata_store_is_initialized_with_data
```

The HTTP equivalents are:

- `GET /api/health/checks/metadata-store/initialized`
- `GET /api/health/checks/metadata-store/initialized/with-data`

The legacy all-in-one health check is a no-op; select the focused health check
that represents the readiness condition automation actually needs.

## Rolling operations and quorum safety

Before stopping a node, verify that no quorum queue, stream, or internal
component would lose its online quorum. Upgrade automation can wait for
quorum-plus-one:

```shell
rabbitmq-diagnostics check_if_node_is_quorum_critical
rabbitmq-upgrade await_online_quorum_plus_one
```

Mixed versions are only a temporary rolling-upgrade state. Delay all
new-series features until every node is upgraded, and complete the transition
within a few hours. Do not upgrade a whole cluster through grow-then-shrink;
reserve it for decommissioning one node.

## Runtime compatibility and process limits

RabbitMQ 4.1 requires at least Erlang/OTP 26.2 and supports OTP 27.x
(`4.1-guides`). RabbitMQ 4.3.x requires Erlang/OTP 27.0 or later; a node fails
to start on an older runtime (`4.3.5`). Check the runtime before a broker
upgrade.

Starting in 4.1.4, Unix-family startup scripts honor
`RABBITMQ_MAX_OPEN_FILES`. It can raise a low soft limit when the hard limit is
already high enough, but it does not replace operating-system hard-limit
configuration.

RabbitMQ auto-tunes AMQP listener user-space TCP buffers, so
`tcp_listen_options.buffer` is ignored. Kernel `recbuf` and `sndbuf` values are
still effective.

## Client-readiness health checks

Starting in 4.1.1 (`4.1.0`):

- `GET /api/health/checks/below-node-connection-limit` succeeds while a node is
  below its AMQP/AMQPS connection limit.
- `GET /api/health/checks/ready-to-serve-clients` additionally requires a
  booted node outside maintenance mode.
- Protocol-listener checks accept comma-separated protocol names.

Use these endpoints for probes instead of the no-op legacy mega-check.

## Resource alarms

From 4.1.6, MQTT, STOMP, and Web MQTT connections remain blocked until every
active memory and disk alarm is gone. Clearing only one of several alarms does
not unblock them.

Direct AMQP 0-9-1 Shovel connections within a cluster are also blocked by
resource alarms in `4.2.0`, matching network Shovel connections. This behavior
does not apply to the new `local` Shovel protocol.

## Capacity and feature controls

### Exchange and queue-type controls

`cluster_exchange_limit` caps exchanges applications can declare across the
cluster, including protocol-standard predeclared exchanges. Configure the same
number on every node:

```ini
cluster_exchange_limit = 200
```

Administrators can disable individual queue types; attempts to declare a new
queue or stream of a disabled type fail. The local-random exchange type can
also be disabled:

```ini
exchange_types.local_random.enabled = false
```

### Stream limits

A Stream Protocol connection has wire-format limits of 256 publishers and 256
subscriptions. Pre-authentication frames default to an 8192-byte maximum, and
uncompressed sub-entry batches default to 64 MiB. See the queues and streams
reference before changing these values.

## Diagnostics and logging controls

Estimate the distribution of message sizes flowing through the cluster with:

```shell
rabbitmq-diagnostics message_size_stats
```

Use `log.summarize_process_state` and `log.error_logger_format_depth` to limit
queue-replica state emitted after an abnormal termination. This avoids memory
allocation spikes caused by very large crash reports.

Authentication events use the `user` logging category: successful logins are
logged at `info` and failed attempts at `warning`.

## Configuration safety checks

- Beginning in 4.1.4, a configured authentication or authorization backend
  from a known but disabled plugin makes startup fail.
- Beginning in 4.1.4, `default_password` and `ssl_options.password` are treated
  as encrypted only with the `encrypted:` prefix.
- Use the same `cluster_exchange_limit` and management credential-encryption
  secret on every node.
- Remove inert partition-handling settings before 4.3, and confirm Khepri is
  enabled before the first 4.3 node boots.
