# Management API and observability

## Health and readiness APIs

The original all-in-one HTTP “One True Health Check” is a no-op in `4.0.6`.
Replace it with focused endpoints.

Metadata-store checks distinguish initialization from initialization with
data:

- `GET /api/health/checks/metadata-store/initialized`
- `GET /api/health/checks/metadata-store/initialized/with-data`

Starting in 4.1.1, `GET /api/health/checks/below-node-connection-limit`
succeeds while a node is below its AMQP/AMQPS connection limit.
`GET /api/health/checks/ready-to-serve-clients` also requires the node to be
booted and outside maintenance mode. Listener checks accept comma-separated
protocol names.

## HTTP API behavior

### Response shapes and static connection data

An empty `channel_details` value is serialized as an object (`{}`), not an
array (`[]`). Client decoders should use the object shape.

Static connection details—including peer address, TLS details, and
authentication mechanism—remain available when statistics collection is
disabled (`4.3.0`).

### User and queue endpoints

The API provides `GET /users/{user}/queues`. A user tagged `protected` cannot
be modified or deleted through the HTTP API, though the CLI can remove the tag
or delete and recreate the user.

### Definition exports and imports

`GET /api/definitions` supports conditional requests. Its `ETag` comes from
the metadata-store Raft index and changes when metadata is written (`4.3.5`).

Require a `.json` extension for management UI and HTTP API definition uploads
with:

```ini
management.definitions.require_json_extension = true
```

The default is `false`. Content is validated as JSON whether or not filename
enforcement is enabled.

### Authentication and authorization controls

Protect the `/api` reference with:

```ini
management.require_auth_for_api_reference = true
```

HTTP API access can use a separate authentication backend chain. Federation
link restart actions and Shovel `DELETE` operations require `policymaker`.
When explicitly enabled, an HTTP backend can expose a custom `deny <Reason>`
authorization failure to AMQP clients.

## Management HTTP behavior

`management.delegate_count` sizes the process pool used to aggregate HTTP API
response data. It defaults to `5`; nodes with many CPU cores may benefit from a
higher value such as `10` or `16`.

Configure the response `Referrer-Policy` through
`management.headers.referrer_policy`. Set
`management.http.hide_allow_header = true` to suppress `Allow`, except on
`405 Method Not Allowed` responses where HTTP requires it.

After a cluster upgrade, clear browser cache, local storage, session storage,
and cookies for management UI domains if stale JavaScript state causes errors
(`4.1-guides`).

## Encrypted UI credentials

With `management.credential_encryption_secret`, `POST /api/login` returns an
AES-256-GCM-encrypted `rmqe.` token. Browsers send
`Authorization: Bearer rmqe.<token>`. Use one secret on every node and wait
until all nodes have been upgraded before enabling the feature.

## Prometheus metrics

### Endpoint origin and message-size metrics

Metrics include labels distinguishing values scraped from the aggregated
endpoint from same-named values scraped per object. RabbitMQ also exposes a
histogram of application-published message sizes labeled by protocol and a
`queue_identity_info` metric labeled with queue type and the scraped node's
leader/follower relationship (`4.1.0`).

The `/metrics/detailed` endpoint can filter detailed queue metrics by queue
name.

### Ra metric migration (`4.2.0`)

Update alerts and dashboards using `rabbitmq_raft*` or
`rabbitmq_detailed_raft*`. Use a 4.2-compatible RabbitMQ quorum-queue Raft
Grafana dashboard.

Aggregated `/metrics` renames:

| Old | New |
| --- | --- |
| `rabbitmq_raft_log_snapshot_index` | `rabbitmq_raft_snapshot_index` |
| `rabbitmq_raft_log_last_applied_index` | `rabbitmq_raft_last_applied` |
| `rabbitmq_raft_log_commit_index` | `rabbitmq_raft_commit_index` |
| `rabbitmq_raft_log_last_written_index` | `rabbitmq_raft_last_written_index` |

Aggregated output removes `rabbitmq_raft_term_total` and
`rabbitmq_raft_entry_commit_latency_seconds`. It adds:

- `rabbitmq_raft_num_segments` for internal components
- `rabbitmq_raft_max_num_segments` for the largest quorum-queue segment count
- `rabbitmq_raft_commit_latency_seconds` for internal components
- `rabbitmq_raft_max_commit_latency_seconds` for the highest quorum-queue
  latency

Per-object and detailed `family=ra_metrics` output renames
`rabbitmq_raft_term_total` to `rabbitmq_raft_term`, adds
`rabbitmq_raft_num_segments`, and exposes additional per-queue metrics.

## Diagnostics and logs

Estimate cluster message-size distribution with:

```shell
rabbitmq-diagnostics message_size_stats
```

Use `log.summarize_process_state` and `log.error_logger_format_depth` to bound
queue-replica crash output and avoid allocation spikes. Authentication logs use
category `user`, with successes at `info` and failures at `warning`.
