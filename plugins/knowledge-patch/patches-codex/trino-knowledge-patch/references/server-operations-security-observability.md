# Server operations, security, and observability

Use this reference for coordinator and worker configuration, fault-tolerant
execution, authentication and authorization, Web UI changes, and telemetry.

## Cluster deployment and runtime

- Deploy every catalog on every node (477).
- Multiple plugin directories can be configured (478).
- Failed catalogs were omitted from `system.metadata.catalogs` in 477. From
  478 onward they appear and can be dropped.
- The `system` catalog is protected from `DROP CATALOG` (475).
- The Docker image uses JDK 24 in batch 473-474 and JDK 25.0.0 build 36 in
  478. The server requires JDK 24 from 476; building and running requires JDK
  25 from 479.
- The server RPM is no longer published (471).
- The HTTP server event-listener plugin is no longer bundled (477).

## Memory, write, and retry limits

`query.max-memory-per-node` and `memory.heap-headroom-per-node` accept values
relative to maximum heap size (476). Resource groups no longer require a soft
memory limit (476).

Limit physical query output with `query.max-write-physical-size` or its
`query_max_write_physical_size` session property (477):

```properties
query.max-write-physical-size=100GB
```

`task.scale-writers.max-writer-memory-percentage` caps the percentage of
memory available to table writers (480). Administrators can constrain
user-selectable retry policies with `retry-policy.allowed` (478).

Remove the defunct `task.statistics-cpu-timer-enabled` setting (479). Remove
the retired large and small dynamic-filter configuration and session
properties (480).

## Exchange managers and spooling storage

Fault-tolerant exchange storage has broader compatibility with S3-compatible
stores (470). When an HDFS-like implementation rejects the directory scheme,
the validation can be skipped (470):

```properties
exchange.hdfs.skip-directory-scheme-validation=true
```

Azure-backed exchange storage works with workload identity (471). The
Exchange Manager configuration file location is configurable rather than
fixed (479).

Alluxio-backed exchange storage is no longer supported (482). Azure exchange
spooling exposes `exchange.azure.max-connections`,
`exchange.azure.pending-acquire-max-count`, and
`exchange.azure.connection-acquisition-timeout` for HTTP connection-pool
tuning (483).

## Resource groups

- Disable automatic database-backed resource-group schema migrations with
  `resource-groups.db-migrations-enabled=false` (476).
- A soft memory limit is optional (476).
- Resource groups track physical data scans (477).
- Selectors accept `originalUser` and `authenticatedUser` (batch 473-474).
- Selectors accept `queryText` as a regular expression over submitted SQL
  (479).

## Authentication, authorization, and policy

### User and group identity

- An LDAP group provider can supply group membership (batch 473-474).
- Ranger reads custom XML configuration files named in
  `access-control.properties` (471).
- Role-derived privileges are honored for impersonation checks (475).
- Group-derived grants are honored under `SET SESSION AUTHORIZATION` (477).
- `SET SESSION AUTHORIZATION` and `RESET SESSION AUTHORIZATION` do not clear
  roles (472).

### OAuth and OPA

OAuth single sign-on can restrict accounts to a domain with
`http-server.authentication.oauth2.domain-hint` (483):

```properties
http-server.authentication.oauth2.domain-hint=example.com
```

Remove `deprecated.http-server.authentication.oauth2.groups-field` (480).
Open Policy Agent authorization requests include the query `queryId` (478).

### Authorization metadata

Ownership is exposed through `system.metadata.tables_authorization`,
`system.metadata.schemas_authorization`, and
`system.metadata.functions_authorization` (477).

## Internal TLS and transport

With `ANNOUNCE` node discovery, Trino automatically generates certificates for
internal cluster TLS (479). This concerns internal communication; configure
client-facing TLS and trust chains separately.

The JDBC driver and CLI can use protocol spooling against clusters with a
private certificate chain (469). Per-session spooling controls and client
details are in the client reference.

## Web UI

- Query lists can be filtered by client tags (469).
- The preview UI can cancel or preempt a running query (482).
- The redesigned UI is served at `/ui` (483). The old UI moved to
  `/ui/legacy`, is disabled by default, and can be restored with:

  ```properties
  web-ui.legacy.enabled=true
  ```

## Logging, metrics, and query diagnostics

Emit console logs as JSON (471):

```properties
log.console-format=JSON
```

Observability additions include:

- JMX exports `blockedQueries` (470).
- JMX connector results include values even when coordinator and worker MBeans
  differ (470).
- `EXPLAIN ANALYZE` includes split count and total split distribution time
  (471).
- `EXPLAIN ANALYZE VERBOSE` includes bytes read from the file-system cache for
  Delta Lake, Hive, and Iceberg (477).
- `/metrics` reports coordinator and worker counts (480).
- `system.runtime.tasks` adds `internal_network_input_bytes` and removes
  `raw_input_bytes` and `raw_input_rows` (477).
- Hive AWS SDK retry metrics separate logical client retries from lower-level
  HTTP retries (469).

Export OpenTelemetry traces over HTTP with protobuf (475):

```properties
tracing.exporter.protocol=http/protobuf
```

## Event listeners

### Event data

- Event listeners receive additional input-table metrics, and
  `QueryCompletedEvent` includes dynamic-filter statistics (475).
- Event listeners receive query time spent in `FINISHING` (479).
- `QueryInputMetadata#connectorMetrics` exposes connector split-source metrics
  (481).
- OpenLineage adds user-identifying fields to `trino_query_context`, `query_id`
  to `trino_metadata`, and
  `openlineage-event-listener.job.name-format` for the job facet name (477).

### HTTP event listener

Select the HTTP method with `http-event-listener.connect-http-method` (477).
The plugin is not included in the server or container distribution from 477,
so deployment must provide it.

### Kafka event listener

`kafka-event-listener.client-config-overrides` was removed (476). Put Kafka
client settings in a separate file:

```properties
kafka-event-listener.config.resources=/etc/trino/kafka-event-listener-client.properties
```

Control payload and batching with `kafka-event-listener.max-request-size` and
`kafka-event-listener.batch-size` (477).

### MySQL event listener

When `mysql-event-listener.terminate-on-initialization-failure` is disabled, a
listener initialization failure no longer terminates server startup (477).

Connector and event-listener SPI removals are listed in the plugin-development
reference.
