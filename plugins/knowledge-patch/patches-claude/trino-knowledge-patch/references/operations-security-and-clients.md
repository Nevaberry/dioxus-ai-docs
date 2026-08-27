# Operations, Security, and Clients

Use this reference for runtime upgrades, configuration, resource groups,
authentication, observability, Web UI, CLI, JDBC, and event-listener operations.

## Runtime and packaging

- JDBC and CLI require Java 11 or newer (470). Server runtime moved to JDK 24 in
  476, while the 473-474 Docker image already used JDK 24. Building and running
  Trino requires JDK 25 as of 479; the 478 image uses JDK 25.0.0 build 36.
- RPM packages are no longer published (471). Use the tarball, container image,
  or the `trino-packages` build setup.
- Every catalog must be deployed on every node (477). Trino can load plugins
  from multiple directories (478).
- The HTTP server event-listener plugin is no longer bundled with the server or
  Docker distribution (477); install it separately when required.

## Upgrade-sensitive configuration

- Rename HTTP client prefixes `workerInfo` and `memoryManager` to `worker-info`
  and `memory-manager` (472).
- `query.max-memory-per-node` and `memory.heap-headroom-per-node` accept values
  relative to maximum heap size (476). `task.scale-writers.max-writer-memory-percentage`
  caps writer memory (480).
- Remove defunct `task.statistics-cpu-timer-enabled` (479).
- Remove `enable-large-dynamic-filters`, `enable_large_dynamic_filters`,
  `dynamic-filtering.small*`, `dynamic-filtering.large-broadcast*`, and
  `deprecated.http-server.authentication.oauth2.groups-field` (480).
- `retry-policy.allowed` restricts selectable retry policies (478).
- `query.max-write-physical-size` and session property
  `query_max_write_physical_size` cap physical output (477).

## Resource groups, catalogs, and system metadata

- Resource-group selectors accept `originalUser` and `authenticatedUser`
  (473-474), then `queryText` as a regular expression (479).
- Set `resource-groups.db-migrations-enabled=false` to disable automatic schema
  migration for database-backed resource groups. Soft memory limits are
  optional (476), and physical scan volume is tracked (477).
- `system.metadata.tables_authorization`, `schemas_authorization`, and
  `functions_authorization` expose ownership (477).
- Trino refuses to drop the `system` catalog (475).
- Release 477 hid failed catalogs from `system.metadata.catalogs`; release 478
  deliberately reversed this. Failed catalogs are now visible and droppable.
- `system.runtime.tasks` adds `internal_network_input_bytes` and removes
  `raw_input_bytes` and `raw_input_rows` (477).

## Authentication and authorization

- Ranger reads custom XML configuration files named in
  `access-control.properties` (471). LDAP can provide group membership
  (473-474).
- `SET SESSION AUTHORIZATION` and `RESET SESSION AUTHORIZATION` preserve roles
  (472). Impersonation checks honor role-derived access (475), and group grants
  apply while session authorization is active (477).
- Open Policy Agent requests include `queryId` (478).
- ANNOUNCE-based discovery enables automatically generated internal TLS
  certificates (479).
- Restrict OAuth sign-in to a domain with
  `http-server.authentication.oauth2.domain-hint` (483).

## Web UI and spooling

- The Web UI can filter by client tags (469). The preview UI can cancel or
  preempt running queries (482).
- In 483 the redesigned UI moved to `/ui`; the previous UI is at `/ui/legacy`
  and disabled by default. Set `web-ui.legacy.enabled=true` only when needed.
- Session properties configure spooling behavior (469). CLI and JDBC spooling
  work with private certificate chains (469), and custom connector types can be
  serialized over the protocol (482).

## JDBC and CLI clients

- `io.trino.jdbc.QueryStats` includes planning, analysis, and finishing times;
  physical input/written bytes; internal network input; and physical input time
  (469).
- `Connection.isValid(int)` validates both connection and credentials. The
  `validateConnection` JDBC property controls validation (469).
- The JDBC driver provides `javax.sql.DataSource` (472).
- `ResultSetMetaData.getColumnClassName()` returns correct Java class names for
  map, row, zoned time/timestamp, varbinary, and null values (480).
- `PreparedStatement.setBigDecimal()` accepts scientific notation such as
  `0E-10` (481).
- Persist external-auth tokens between processes with
  `externalAuthenticationTokenCache=SYSTEM`; tokens live under `~/.trino/`
  (481). `accessToken` connections refresh OAuth tokens when the server has
  `http-server.authentication.oauth2.refresh-tokens=true` (481).
- JDBC supports arbitrary `extraHeaders`, and CLI supports repeated
  `--extra-header` values (479).
- JDBC and CLI support `variant`; older CLIs display values as JSON (481).

## Metrics, logging, tracing, and query visibility

- JMX exports `blockedQueries` (470). The `/metrics` endpoint reports coordinator
  and worker counts (480).
- Set `log.console-format=JSON` for structured console logs (471).
- `EXPLAIN ANALYZE` reports split count and split-distribution time (471), and
  verbose output reports file-system-cache reads for major lakehouse connectors
  (477).
- Export OpenTelemetry traces over HTTP protobuf with
  `tracing.exporter.protocol=http/protobuf` (475).
- Event listeners receive more input-table metrics and dynamic-filter statistics
  (475), query `FINISHING` duration (479), and connector split-source metrics via
  `QueryInputMetadata#connectorMetrics` (481).

## Event-listener configuration

- Kafka client settings moved out of
  `kafka-event-listener.client-config-overrides`; point
  `kafka-event-listener.config.resources` to a separate properties file (476).
  `kafka-event-listener.max-request-size` and `.batch-size` tune batching (477).
- MySQL event-listener initialization failure does not stop startup when
  `mysql-event-listener.terminate-on-initialization-failure=false` (477).
- `http-event-listener.connect-http-method` selects the listener's HTTP method
  (477).
- OpenLineage adds user identifiers to `trino_query_context`, `query_id` to
  `trino_metadata`, and `openlineage-event-listener.job.name-format` for job
  facet naming (477).
