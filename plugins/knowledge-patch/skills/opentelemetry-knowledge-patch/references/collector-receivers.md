# Collector Receivers

The details in this reference apply to the Collector 0.157.0 batch.

## Metric schemas and UCUM units

UCUM unit corrections affect:

- The tail-sampling processor.
- Apache Spark, Chrony, HAProxy, Memcached, MongoDB, NGINX, NSX-T, Redfish,
  Splunk Enterprise, and SQL Server receivers.

The SQL Server receiver's Opt-In `sqlserver.lock.timeout.rate` emits separate
`all` and `nonzero` points. Each point has the required
`sqlserver.lock.timeout.type` attribute.

## AWS ECS and Datadog

### AWS ECS Container Metrics

The receiver migrates `container.image.tag` to `container.image.tags`.

### Datadog

The Datadog receiver:

- Maps `kube_app_*` tags to `app.kubernetes.io/*` resource attributes for
  traces, metrics, and logs.
- Translates native Datadog span links and span events.
- Prefers native fields over metadata fallbacks.
- Uses a beta, default-on 128-bit trace-ID gate that reconstructs every span
  in a payload.

## MySQL

The MySQL receiver enables a deterministic, endpoint-derived
`service.instance.id` by default.

Optional resource attributes are:

- `service.name`, defaulting to `unknown_service:mysql`.
- `service.namespace`.
- `db.system.version`.
- `db.system.name`.

## PostgreSQL

The alpha, default-off `receiver.postgresql.useOTelSemconv` gate:

- Uses one resource per server.
- Places `server.address` and `server.port` on that resource.
- Generates a UUID-v5 `service.instance.id`.
- Places `db.namespace`, `db.collection.name`, and
  `postgresql.index.name` on metrics.

The gate is mutually exclusive with
`receiver.postgresql.separateSchemaAttr`.

The receiver also adds the default-off `postgresql.query.conflicts` metric for
standby recovery conflicts.

## Oracle Database

The Oracle Database receiver adds Opt-In operating-system metrics including:

- `oracledb.system.cpu.count`.
- `oracledb.system.memory.limit`.
- `oracledb.system.process.count`.

It also adds default-off metric groups for transactions, locks, recovery,
sessions, JVM behavior, health, and efficiency.

Additional Opt-In metrics include:

- `oracledb.sga.usage`.
- `oracledb.sga.limit`.

`db.server.session.wait_sample` now carries `db.namespace`.

## RabbitMQ and file stats

### RabbitMQ

Default-off exchange metrics are:

- `rabbitmq.exchange.messages.published_in`.
- `rabbitmq.exchange.messages.published_out`.

They use exchange name and exchange type as resource attributes.

### File Stats

The File Stats receiver can opt `file.include` into `file.count`.

## SQL Server expansion

The SQL Server receiver adds default-off metrics for:

- Locks and connections.
- Cursors and worker threads.
- CLR and tasks.
- Stored procedures.

New index metrics are:

- `sqlserver.index.fragmentation`.
- `sqlserver.index.page.count`.
- `sqlserver.index.size`.
- `sqlserver.index.page.utilization`.
- `sqlserver.index.record.count`.

Index metrics additionally require `CONNECT ANY DATABASE` and
`VIEW ANY DEFINITION`.

## Journald and webhook provenance

- With `include_log_record_original`, the Journald receiver preserves raw
  `journalctl` input as `log.record.original`.
- The Webhook Event receiver supports HMAC signature verification for incoming
  requests.

## Timeout behavior

- The SQL Query receiver applies `timeout` to log queries.
- The Splunk HEC receiver honors `read_header_timeout` and `write_timeout`
  instead of replacing both with a fixed 20-second timeout.
