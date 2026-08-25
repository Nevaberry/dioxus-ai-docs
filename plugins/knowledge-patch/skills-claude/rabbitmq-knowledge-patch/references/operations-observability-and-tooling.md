# Operations, Observability, and Tooling

Use this reference for health probes, diagnostics, metrics, management API
behavior, operating-system limits, logs, and administrative tools.

## Build focused health and readiness checks (4.0.6, 4.1.0)

### Metadata-store readiness checks

Use `rabbitmq-diagnostics check_if_metadata_store_is_initialized` for basic
initialization and `check_if_metadata_store_is_initialized_with_data` when
data must also be present. HTTP equivalents are
`GET /api/health/checks/metadata-store/initialized` and
`GET /api/health/checks/metadata-store/initialized/with-data`.

### Legacy all-in-one health check is a no-op

The original HTTP API “One True Health Check” no longer performs its former
aggregate check. Replace it with focused health checks.

### Client-readiness health checks

From 4.1.1, `GET /api/health/checks/below-node-connection-limit` succeeds
while the node is below its AMQP/AMQPS connection limit. The
`ready-to-serve-clients` check also requires boot completion and no maintenance
mode. Listener checks accept comma-separated protocol names.

### Quorum-leader diagnostics

Check matching quorum queues for an elected leader:

```shell
rabbitmq-diagnostics check_for_quorum_queues_without_an_elected_leader --vhost "vh-1" "^naming-pattern"
```

Use `--across-all-vhosts ".*"` for the entire cluster, but expect high cost
with many quorum queues.

## Interpret and migrate metrics (4.0.6, 4.1.0, 4.2.0, 4.3.0)

### Prometheus endpoint-origin labels

Metrics include labels that distinguish values scraped from the aggregated
endpoint from same-named metrics scraped from a per-object endpoint.

### Prometheus message-size and queue-identity metrics

Use the protocol-labeled histogram for application-published message sizes.
`queue_identity_info` identifies queue type and whether the scraped node is
its leader or follower.

### Message-size diagnostics

Estimate the distribution of message sizes moving through a cluster with:

```shell
rabbitmq-diagnostics message_size_stats
```

### Ra Prometheus metric migration

Update dashboards and alerts for the 4.2 Ra metric schema, including the
RabbitMQ quorum-queue Raft Grafana dashboard.

- Aggregated `/metrics` renames `rabbitmq_raft_log_snapshot_index` to
  `rabbitmq_raft_snapshot_index`, `rabbitmq_raft_log_last_applied_index` to
  `rabbitmq_raft_last_applied`, `rabbitmq_raft_log_commit_index` to
  `rabbitmq_raft_commit_index`, and `rabbitmq_raft_log_last_written_index` to
  `rabbitmq_raft_last_written_index`.
- It removes `rabbitmq_raft_term_total` and
  `rabbitmq_raft_entry_commit_latency_seconds`.
- It adds `rabbitmq_raft_num_segments` and `rabbitmq_raft_commit_latency_seconds`
  for internal components, plus `rabbitmq_raft_max_num_segments` and
  `rabbitmq_raft_max_commit_latency_seconds` for quorum-queue maxima.
- Per-object and detailed `family=ra_metrics` output renames
  `rabbitmq_raft_term_total` to `rabbitmq_raft_term`, adds
  `rabbitmq_raft_num_segments`, and exposes more per-queue metrics.

### Per-queue detailed metrics filtering

The Prometheus `/metrics/detailed` endpoint can filter queue metrics by queue
name.

## Control diagnostic and process overhead (4.0.6, 4.1.0, 4.2.0)

### HTTP API aggregation pool sizing

`management.delegate_count` sizes the process pool used to aggregate HTTP API
responses. It defaults to `5`; nodes with many CPU cores can use values such
as `10` or `16`.

### Open-file soft-limit override

From 4.1.4 on Linux, macOS, and BSD, the startup script recognizes
`RABBITMQ_MAX_OPEN_FILES`. It can raise a low soft limit when the hard limit is
already sufficient; it does not replace operating-system hard-limit setup.

### Queue-replica crash-log controls

Use `log.summarize_process_state` and `log.error_logger_format_depth` to limit
queue-member state logged after abnormal termination and avoid allocation
spikes from very large diagnostics.

### Resource-alarm blocking

From 4.1.6, MQTT, STOMP, and Web MQTT connections remain blocked until all
active memory and disk alarms clear.

### Resource alarms for direct in-cluster shovels

Direct AMQP 0-9-1 shovel connections are blocked by resource alarms like
network connections. This does not describe the `local` shovel protocol.

## Consume management API details correctly (4.0.6, 4.3.0, 4.3.5)

### Empty channel details are objects

An empty `channel_details` value is serialized as `{}`, not `[]`.

### User queue-list endpoint

List queues visible to a user with `GET /users/{user}/queues`.

### Connection information without statistics

Static connection data such as peer address, TLS details, and authentication
mechanism remains available through the HTTP API when statistics collection is
disabled.

### Conditional definition exports

`GET /api/definitions` supports conditional requests. Its `ETag` derives from
the metadata-store Raft index and changes as metadata writes occur.

## Select administrative tools and artifacts (4.0.6, 4.2.0, 4.3-guides)

### `rabbitmqadmin` v2

Prefer the GA standalone `rabbitmqadmin` 2.0 binary over the original tool.

### Complete source archive

Use `rabbitmq-server-4.2.0.tar.xz` for the complete 4.2.0 source distribution,
not the automatically generated repository source archive.

### Tanzu Stream Browser

The commercial Stream Browser management plugin can inspect streams and super
streams from an offset, timestamp, head, or tail; expose AMQP 1.0 sections and
segment/chunk layout; and selectively download message sections.
