# Collector Receivers

## Metric units and schema changes

UCUM corrections affect the Tail Sampling processor and these receivers:
Apache Spark, Chrony, HAProxy, Memcached, MongoDB, NGINX, NSX-T, Redfish,
Splunk Enterprise, and SQL Server.

The SQL Server opt-in `sqlserver.lock.timeout.rate` metric emits distinct
`all` and `nonzero` points with required
`sqlserver.lock.timeout.type`.

## AWS and Datadog

- AWS ECS Container Metrics uses `container.image.tags`, replacing
  `container.image.tag`.
- Datadog maps `kube_app_*` tags to `app.kubernetes.io/*` Resource attributes
  for traces, metrics, and logs.
- Datadog translates native span links and span events and prefers native
  fields over metadata fallbacks.
- The beta, default-on Datadog 128-bit trace-ID gate reconstructs every span
  in a payload.

## MySQL

The receiver enables deterministic endpoint-derived `service.instance.id` by
default. Optional Resource attributes are:

- `service.name`, defaulting to `unknown_service:mysql`
- `service.namespace`
- `db.system.version`
- `db.system.name`

Metric additions cover replica threads, open temporary tables, and InnoDB
data I/O and pending operations. Default-off metrics include `mysql.file.open`,
`mysql.table.open`, and `mysql.thread.slow_launch`. `mysql.commands` adds
`alter_table`, `create_index`, `create_table`, and `optimize` values.

## PostgreSQL

The alpha, default-off `receiver.postgresql.useOTelSemconv` gate creates one
Resource per server with `server.address`, `server.port`, and UUID-v5
`service.instance.id`. It moves `db.namespace`, `db.collection.name`, and
`postgresql.index.name` onto metrics.

This gate is mutually exclusive with
`receiver.postgresql.separateSchemaAttr`. The receiver also adds the
default-off `postgresql.query.conflicts` metric for standby recovery
conflicts.

## Oracle Database

### Metric families

Opt-in OS metrics include `oracledb.system.cpu.count`,
`oracledb.system.memory.limit`, and `oracledb.system.process.count`. Additional
default-off families cover transactions, locks, recovery, sessions, JVM,
health, and efficiency. Opt-in `oracledb.sga.usage` and
`oracledb.sga.limit` are available. `db.server.session.wait_sample` carries
`db.namespace`.

### Query and tablespace behavior

Top-query and query-sample collection normalizes obfuscated `db.query.text`.
This can change downstream signatures, preserves identifier quotation, and
continues to emit raw-SQL comment tags as `db.query.comment_tags`.

Three tablespace-health metrics are Opt-In. For a multi-PDB CDB root, also
enable `oracle.db.pdb`; otherwise same-named tablespaces are aggregated across
PDBs.

## RabbitMQ and File Stats

- RabbitMQ adds default-off `rabbitmq.exchange.messages.published_in` and
  `rabbitmq.exchange.messages.published_out` with exchange-name and
  exchange-type Resource attributes.
- File Stats can opt `file.include` into `file.count`.

## SQL Server

### Expanded metrics and permissions

Default-off additions cover locks, connections, cursors, worker threads, CLR,
tasks, and stored procedures. New index metrics are:

- `sqlserver.index.fragmentation`
- `sqlserver.index.page.count`
- `sqlserver.index.size`
- `sqlserver.index.page.utilization`
- `sqlserver.index.record.count`

Index metrics require both `CONNECT ANY DATABASE` and `VIEW ANY DEFINITION`.

### Query normalization and pooling

Top-query and query-sample obfuscation normalizes whitespace, comments,
aliases, and qualified identifiers. Unparseable statements are obfuscated
instead of dropped, so derived query identifiers can change.

Metrics and logs receivers each share one tunable pool. Configure
`connection_pool.max_open`, `max_idle`, `max_lifetime`, and `max_idle_time`;
open and idle defaults derive from enabled scrapers.

## Log input provenance and ordering

- Journald can retain raw `journalctl` input as `log.record.original` with
  `include_log_record_original`.
- Webhook Event supports HMAC signature verification.
- File Log `ordering_criteria.top_n: 0` matches all files, not one. Set `1`
  explicitly to preserve the old behavior.
- When `sort_by` is present, the implicit `top_n: 1` default is deprecated.
  The default-off `filelog.requireExplicitTopN` gate makes omission a startup
  error.

## Apache migration

`apache.worker.limit` is an UpDownCounter. Additions include
`apache.request.rate` and default-off `apache.traffic.rate`.

`receiver.apache.enableNewFormatMetrics` emits new names with the old names.
Also enable `receiver.apache.disableOldFormatMetrics` to emit only:

- `apache.connection.active` and `apache.connection.status`
- `apache.request.count`
- `apache.worker.status`, `apache.worker.active`, and `apache.worker.idle`

The accompanying attributes are `apache.connection.state`,
`apache.worker.state`, `apache.process.level`, and `cpu.mode`.

## Additional receiver coverage

- DNS Check has a complete scraper that emits metrics and Resource
  attributes.
- AWS Lambda adds `aws.log.subscription_filter.names` when the decoded
  CloudWatch event contains subscription filters.
- Kubelet Stats can opt into `k8s.node.filesystem.inode.count` and
  `k8s.node.filesystem.inode.free` (batch `2026-08-stable`).
- Google Cloud Pub/Sub Push log support is alpha.
- Podman Stats reports block-I/O byte metrics with unit `By`.

## Honored timeout settings

- SQL Query applies `timeout` to log queries.
- Splunk HEC honors `read_header_timeout` and `write_timeout` rather than
  replacing them with a fixed 20-second timeout.
