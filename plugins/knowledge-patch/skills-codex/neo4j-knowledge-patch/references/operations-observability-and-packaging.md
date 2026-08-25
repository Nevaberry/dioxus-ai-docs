# Operations, Observability, and Packaging

Use this reference for server settings, page-cache I/O, Fleet Manager, command
line behavior, logs, metrics, packaging, and operational TLS defaults.

## Server and database settings

### Wildcard database filters

From 2025.12, Enterprise settings `initial.server.allowed_databases` and
`initial.server.denied_databases` accept wildcard database-name patterns. The
minimum value length is reduced from three characters to one.

### Cypher language in packaged configuration

Starting in 2026.02, distributed `neo4j.conf` explicitly sets:

```properties
db.query.default_language=CYPHER_25
```

New deployments using that file default newly created databases to Cypher 25.
Retained configuration can preserve the earlier selection.

### Asynchronous page-cache I/O

Linux deployments can opt into initial `io_uring` support for the background
page evictor and checkpointer (since `2026.04.0`):

```properties
server.memory.pagecache.async=true
```

## Fleet and deployment management

### Security-log collection

Security logs from self-managed Enterprise deployments can be collected for
the Aura console Security Log Analyzer. Register the deployment with Fleet
Manager and explicitly opt into log collection.

### Local discovery and registration

The server includes a discovery service for finding running Neo4j deployments
on the local network. `neo4j-admin fleet discover` lists the servers, and
`neo4j-admin` can bulk-register them with Fleet Manager for display in the Aura
Console (since `2026.05.0`).

### Packaging and upgrades

Enterprise Fleet Management is no longer bundled as a separate DBMS package
component because the capability is included in Neo4j. Neo4j Ops Manager
1.15.1, included with Enterprise, supports any-to-any Neo4j upgrades.

## Cypher Shell

Cypher Shell defaults `--error-format` to `gql`. Scripts that parse errors
should set the flag explicitly when they require another format.

From 2025.08, disable history for a session with:

```text
cypher-shell --history disable
```

The `:sysinfo` command supports Infinigraph deployments.

## Browser packaging

From 2026.02.3, Community Edition has a `web/` directory containing Neo4j
Browser as a ZIP. Enterprise Edition has no `web/` directory and continues to
ship Browser as a JAR in `lib/`. Packaging automation must branch by edition.

## Query-log formats and fields

For new installations, the release after the next LTS will default query
logging to JSON instead of PLAIN. Upgrades that retain `server-logs.xml` retain
their current format. PLAIN remains supported; JSON provides more information
but produces larger files.

From 2025.05, JSON query-log `failureReason` is deprecated in favor of
`errorInfo`. Update log schemas and field lookups.

Programmatic reliance on error-message text is deprecated from 2025.04 because
messages may change. Parse and branch on GQLSTATUS codes instead.

The default `debug.log` format changes from text to JSON in the 2025.01
breaking configuration. Keep the default appender for supportability and add a
second appender if another format is required.

## Metrics defaults and migrations

### Default filters

`cluster.internal.*` is no longer part of default metrics-setting values.
Those internal series were not intended for customer use; monitoring must not
depend on their implicit collection.

From 2025.03, default `server.metrics.filter` includes the `neo4j.count`
metrics class instead of deprecated `ids_in_use`. Dashboards relying on the
default filter should consume count metrics.

### Raft health

The HTTP status field `raftCommandsPerSecond` is deprecated. Monitor
`<prefix>.cluster.raft.commit_index` on every server and check for divergence.

`<prefix>.cluster.raft.in_flight_cache.max_bytes` and
`<prefix>.cluster.raft.in_flight_cache.max_elements` are deprecated from
2026.07 and will be removed after the next LTS.
`<prefix>.cluster.raft.tx_retries` has been deprecated since 2025.02 and will
also be removed.

### Removed and renamed series

The old `causal_clustering.core` Raft metrics for indexes, term, leadership,
retries, in-flight cache, prefetch buffering, message processing, replication,
and last-leader messages are removed in favor of Raft metrics. The three
`causal_clustering.read_replica.pull_update*` series move to store-copy metrics,
and six discovery-v1 series under `cluster.discovery` are removed without
replacement.

Rename `<prefix>.store.size.total` to `<prefix>.store.size.full` in dashboards
and alerts.

## Import and copy observability

Import-progress files move during the server series:

```text
2026.03: server/logs/neo4j-admin-import-yyyy-MM-dd.HH.mm.ss.log
       -> server/data/imports/dbname-yyyy-MM-dd.HH.mm.ss/import.log
2026.04: generated import-information directory moves back under server/logs/
```

From 2025.01, `neo4j-admin database copy --from-pagecache=<size>` caps off-heap
memory for the entire operation, including reads and writes. The clearer option
name is `--max-off-heap-memory=<size>`.

## TLS operations

With OpenSSL provider 3.5 or later, TLS can use `X25519MLKEM768`, a hybrid key
exchange combining X25519 with ML-KEM-768 for post-quantum protection.

From 2025.10, four Java 21 CBC cipher suites are removed from defaults, though
they remain available when explicitly configured:

```text
TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384
TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256
TLS_DHE_RSA_WITH_AES_256_CBC_SHA256
TLS_DHE_RSA_WITH_AES_128_CBC_SHA256
```

The default for `dbms.ssl.policy.*.verify_hostname` changes from `false` to
`true`; validate peer certificate hostnames before upgrade.
