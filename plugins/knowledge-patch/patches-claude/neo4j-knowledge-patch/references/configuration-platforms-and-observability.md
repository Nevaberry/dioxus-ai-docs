# Configuration, Platforms, APIs, and Observability

## Server configuration

### Select the default Cypher language deliberately

Starting in 2026.02, the distributed `neo4j.conf` explicitly contains:

```properties
db.query.default_language=CYPHER_25
```

New deployments using that file therefore create databases with Cypher 25 as
their default language. This packaged-file behavior supersedes the earlier
implicit Cypher 5 default; retained or customized configuration may differ.

### Filter initial database placement with wildcards

From 2025.12, Enterprise Edition accepts wildcard database-name patterns in
`initial.server.allowed_databases` and `initial.server.denied_databases`. The
minimum value length is one character rather than three.

### Enable asynchronous page-cache I/O on Linux (2026.04.0)

Initial `io_uring` support covers the background page evictor and checkpointer:

```properties
server.memory.pagecache.async=true
```

This setting is opt-in.

### Remove or replace deprecated configuration entry points

- The `server_policies` load-balancing plugin and
  `dbms.routing.load_balancing.plugin` are deprecated from 2025.05.
- `server.db.query_cache_size` is deprecated.
- `dbms.security.oidc.<provider>.auth_params` and
  `dbms.security.oidc.<provider>.client_id` are deprecated.

See the upgrade reference for the larger 2025.01 removed-setting map.

## Installation and platform behavior

### Account for Browser packaging

From 2026.02.3, Community Edition contains `web/` with Neo4j Browser as a ZIP.
Enterprise Edition has no `web/` directory and continues to ship Browser as a
JAR in `lib/`.

### Plan around platform deprecations (2026.05.0)

Ubuntu Server 22.04, macOS 15 Sequoia, CentOS Stream 9, and Windows Server
2022 are deprecated supported platforms and will be removed later.

Additional lifecycle changes apply by platform family:

- `debian:bullseye-slim` and `redhat/ubi9-minimal:latest` are unsupported base
  images from 2026.05.
- CentOS Stream 8.x and SysV init scripts are deprecated from 2026.01.
- RHEL 8.x, Debian 11.x, macOS 13 Ventura, and macOS 14 Sonoma are deprecated
  from 2025.10 and supported only through the 2026 LTS.
- Neo4j 2025.01 removes support for macOS 11 and 12, Amazon Linux 2022 AMI,
  Ubuntu Server 16.04, 18.04, and 20.04, and Windows Server 2016 and 2019.

### Configure Helm object-storage endpoints

Non-TLS/SSL MinIO endpoints in the `neo4j/neo4j-admin` Helm charts are
deprecated. Configure the replacement `s3Endpoint`.

## Query and HTTP APIs

### Store longer transaction identifiers (2026.04.0)

Query API transaction IDs are six characters instead of four. Remove schema,
validation, or storage assumptions that require exactly four characters.

### Move from the transactional HTTP API

The transactional HTTP API is deprecated in 5.26 in favor of the HTTP Query
API. Query API is enabled by default from 5.26. On earlier releases, enable it
by adding `QUERY_API_ENDPOINTS` to `server.http_enabled_modules`.

### Branch on GQLSTATUS, not message text

Programmatic dependence on error-message text is deprecated from 2025.04
because messages may change. Parse and branch on GQLSTATUS error codes.

## Cypher Shell and plan-output contracts

### Pin error formatting when parsing stderr (2025.06)

Cypher Shell now defaults `--error-format` to `gql`. Scripts requiring a
different representation must set the flag explicitly.

### Disable shell history when required

From 2025.08, start a session without persisted history using:

```text
cypher-shell --history disable
```

### Accept point-release plan versions (2026.04.0)

`EXPLAIN` and `PROFILE` now report the underlying Neo4j point release
consistently. Parsers and snapshot comparisons must allow the more detailed
version.

## Logging

### Prepare for JSON query logging (2026.05.0)

For new installations, the release after the next LTS will default query logs
to JSON rather than PLAIN. Upgrades that retain `server-logs.xml` keep their
existing format, and PLAIN remains supported. JSON carries more information
but creates larger files; size retention and downstream schemas accordingly.

The JSON query-log field `failureReason` is deprecated from 2025.05. Read
`errorInfo` instead.

### Treat the default debug log as JSON

The default `debug.log` changes from text to JSON. Keep the default appender
for supportability; add another appender if a second format is required.
Existing consumers of the default file must parse JSON.

### Apply new-install logging defaults

For new installations and upgrades that replace configuration files:

```text
db.logs.query.annotation_data_format: CYPHER -> JSON
server.metrics.csv.rotation.compression: NONE -> ZIP
server.panic.shutdown_on_panic: false -> true
server.logs.config: conf/server-logs.xml -> server-logs.xml
server.logs.user.config: conf/user-logs.xml -> user-logs.xml
```

Relative `server.logs.config` and `server.logs.user.config` values now resolve
from `server.directories.configuration`, not
`server.directories.neo4j_home`.

## Metrics

### Do not rely on internal cluster metrics (2025.06)

`cluster.internal.*` is no longer part of the default metrics-setting values.
Those metrics are not a customer contract; monitoring must not depend on
implicit collection.

### Replace IDs-in-use defaults with counts

From 2025.03, default `server.metrics.filter` includes the `neo4j.count`
metrics class instead of deprecated `ids_in_use`. Update default-filter-based
dashboards to consume the count metrics.

### Replace the Raft status field

The HTTP status field `raftCommandsPerSecond` is deprecated. Monitor
`<prefix>.cluster.raft.commit_index` on every server and check for divergent
values.

### Retire deprecated Raft series

- `<prefix>.cluster.raft.in_flight_cache.max_bytes` and
  `<prefix>.cluster.raft.in_flight_cache.max_elements` are deprecated from
  2026.07 and will be removed after the next LTS.
- `<prefix>.cluster.raft.tx_retries` has been deprecated since 2025.02 and
  will be removed later.

### Migrate removed and renamed metric series

The old `causal_clustering.core` Raft metrics for indexes, term, leadership,
retries, in-flight cache, prefetch buffering, message processing, replication,
and last-leader messages are removed in favor of the Raft metrics.

The three `causal_clustering.read_replica.pull_update*` metrics move to
store-copy metrics. The six discovery-v1 metrics under `cluster.discovery`
have no replacements.

Rename dashboard and alert references:

```text
<prefix>.store.size.total -> <prefix>.store.size.full
```

## Fleet security-log collection (2026.04.0)

Security logs from a self-managed Enterprise Edition deployment can be shown
in the Aura console Security Log Analyzer. Register the deployment with Fleet
Manager and explicitly opt in to log collection.

## Java integration contracts

### Stop consuming legacy notification APIs

The server-side Notification API and Result Core API
`getNotifications()` are deprecated from 5.26. Migrate Java integrations away
from these entry points.

### Parse schema property types as Cypher names (2025.06)

`db.schema.nodeTypeProperties()` and `db.schema.relTypeProperties()` return
Cypher type names, not Java type names, in `propertyTypes`. Update validators
and deserializers that encode the former vocabulary.

The removed public Java surface associated with discovery, Raft, allocators,
server groups, transaction memory, and query annotations is enumerated in the
upgrade reference.
