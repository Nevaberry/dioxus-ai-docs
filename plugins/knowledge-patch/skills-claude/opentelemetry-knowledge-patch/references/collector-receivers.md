# Collector Receivers

## Cross-receiver schemas and input handling

### Metric units and SQL Server lock timeouts (`collector-0.157.0`)

UCUM unit corrections affect the Tail Sampling processor and the Apache Spark,
Chrony, HAProxy, Memcached, MongoDB, NGINX, NSX-T, Redfish, Splunk Enterprise,
and SQL Server receivers. The opt-in `sqlserver.lock.timeout.rate` metric emits
separate `all` and `nonzero` points with the required
`sqlserver.lock.timeout.type` attribute.

### Honored timeout and connection settings (`collector-0.157.0`)

The SQL Query receiver applies `timeout` to log queries. The Splunk HEC
receiver honors `read_header_timeout` and `write_timeout` rather than
overriding both with a fixed 20-second timeout.

## File, journal, and webhook input

### File Log ordering criteria (`2026-08-stable`)

`ordering_criteria.top_n: 0` matches all files rather than behaving as `1`.
Set `1` explicitly to retain single-file selection. With `sort_by`, the
implicit default of `1` is deprecated. The default-off
`filelog.requireExplicitTopN` gate makes an omitted `top_n` a startup error.

### Journald and webhook provenance (`collector-0.157.0`)

Set `include_log_record_original` on Journald to preserve raw `journalctl`
input as `log.record.original`. The Webhook Event receiver supports HMAC
signature verification for incoming requests.

### RabbitMQ and File Stats telemetry (`collector-0.157.0`)

RabbitMQ has default-off `rabbitmq.exchange.messages.published_in` and
`rabbitmq.exchange.messages.published_out` metrics with exchange-name and
exchange-type resource attributes. File Stats can opt `file.include` into
`file.count`.

## AWS and Datadog receivers

### ECS image tags and Kubernetes application labels (`collector-0.157.0`)

The AWS ECS Container Metrics receiver migrates `container.image.tag` to
`container.image.tags`. The Datadog receiver maps `kube_app_*` tags to
`app.kubernetes.io/*` resource attributes across traces, metrics, and logs.
It translates native Datadog span links and span events, preferring native
fields over metadata fallbacks.

### CloudWatch subscription filters (`2026-08-stable`)

The AWS Lambda receiver adds `aws.log.subscription_filter.names` when the
decoded CloudWatch event contains filter names.

## MySQL and PostgreSQL

### MySQL resource identity (`collector-0.157.0`)

MySQL enables a deterministic endpoint-derived `service.instance.id` by
default. Optional resource attributes are `service.name`—defaulting to
`unknown_service:mysql`—`service.namespace`, `db.system.version`, and
`db.system.name`.

### MySQL metrics (`2026-08-stable`)

MySQL adds replica-thread, open-temporary-table, and InnoDB data-I/O and
pending-operation metrics. Default-off additions are `mysql.file.open`,
`mysql.table.open`, and `mysql.thread.slow_launch`. `mysql.commands` accepts
`alter_table`, `create_index`, `create_table`, and `optimize` values.

### PostgreSQL semantic conventions (`collector-0.157.0`)

The alpha, default-off `receiver.postgresql.useOTelSemconv` gate creates one
resource per server with `server.address`, `server.port`, and a UUID-v5
`service.instance.id`; metrics carry `db.namespace`, `db.collection.name`,
and `postgresql.index.name`. This gate is mutually exclusive with
`receiver.postgresql.separateSchemaAttr`. The default-off
`postgresql.query.conflicts` metric reports standby recovery conflicts.

## Oracle Database

### Metric families and namespace (`collector-0.157.0`)

Opt-in OS metrics include `oracledb.system.cpu.count`,
`oracledb.system.memory.limit`, and `oracledb.system.process.count`.
Default-off families cover transactions, locks, recovery, sessions, JVM,
health, and efficiency. Opt-in `oracledb.sga.usage` and
`oracledb.sga.limit` are available, and `db.server.session.wait_sample`
carries `db.namespace`.

### Query normalization and tablespaces (`2026-08-stable`)

Top-query and query-sample collection normalizes obfuscated `db.query.text`,
which changes downstream signatures while preserving identifier quotation.
Raw-SQL comment tags remain in `db.query.comment_tags`. Three
tablespace-health metrics are Opt-In. On a multi-PDB CDB root, also opt into
`oracle.db.pdb` or same-named tablespaces are aggregated across PDBs.

## SQL Server

### Expanded metric families (`collector-0.157.0`)

SQL Server adds default-off lock, connection, cursor, worker-thread, CLR,
task, and stored-procedure metrics. New index metrics are
`sqlserver.index.fragmentation`, `sqlserver.index.page.count`,
`sqlserver.index.size`, `sqlserver.index.page.utilization`, and
`sqlserver.index.record.count`; they require `CONNECT ANY DATABASE` and
`VIEW ANY DEFINITION`.

### Query normalization and connection pooling (`2026-08-stable`)

Top-query and query-sample obfuscation normalizes whitespace, comments,
aliases, and qualified identifiers. Unparseable statements are obfuscated
rather than dropped, so derived query identifiers can change. Metrics and
logs receivers each share one tunable pool configured with
`connection_pool.max_open`, `max_idle`, `max_lifetime`, and `max_idle_time`;
open and idle defaults derive from enabled scrapers.

## Apache and additional scrapers

### Apache metric migration (`2026-08-stable`)

`apache.worker.limit` is an UpDownCounter. The receiver adds
`apache.request.rate`, default-off `apache.traffic.rate`, and
`apache.worker.limit`. `receiver.apache.enableNewFormatMetrics` emits new
names alongside old ones. Also enable
`receiver.apache.disableOldFormatMetrics` to emit only
`apache.connection.active`, `apache.connection.status`,
`apache.request.count`, `apache.worker.status`, `apache.worker.active`, and
`apache.worker.idle`; renamed attributes are `apache.connection.state`,
`apache.worker.state`, `apache.process.level`, and `cpu.mode`.

### DNS Check and Kubelet Stats (`2026-08-stable`)

DNS Check has a complete scraper that emits metrics and resource attributes.
Kubelet Stats can opt into `k8s.node.filesystem.inode.count` and
`k8s.node.filesystem.inode.free`.
