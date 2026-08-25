# Upgrades, Deprecations, and Removals

## Mandatory patch-level upgrades

### Checkpoint deadlock in 2025.06.0

The base 2025.06 release can sporadically deadlock on the checkpoint mutex.
Run production deployments on 2025.06.1 or later.

### Block-format UTF-8 defect in 2026.07.0

Neo4j 2026.07.0 has a UTF-8 encoding defect in the block format. It can cause
unexpected query failures when Cypher `trim()` is used and can make stored
string data unreadable. Upgrade affected installations to 2026.07.1.

## Store-format migration

### Migrate `high_limit` before its final compatibility window (2026.06.0)

The next LTS is the last release that can read, write, or migrate `high_limit`
databases. Before upgrading beyond that LTS, migrate every such database
offline to Block format. A remaining `high_limit` database will fail to start
and has no compatibility fallback.

### Move away from `standard`

The `standard` store format has been deprecated since 5.23. Do not select it
for new databases, and plan migration of existing stores.

## Discovery v1 removal

### Finish the cluster transition before 2025.01

Neo4j 2025.01 removes discovery service v1. Complete the v1-to-v2 transition
before the upgrade. Internal discovery traffic moves from port `5000` to
`6000`, and settings move as follows:

```text
dbms.cluster.discovery.v2.endpoints -> dbms.cluster.endpoints
dbms.kubernetes.discovery.v2.service_port_name -> dbms.kubernetes.discovery.service_port_name
server.discovery.advertised_address -> server.cluster.advertised_address
server.discovery.listen_address -> server.cluster.listen_address
```

The former `*.v2.*` names remain accepted only for the 5.26-to-2025.01
migration and should be replaced.

These discovery migration procedures are removed without replacements:

- `dbms.cluster.moveToNextDiscoveryVersion()`
- `dbms.cluster.showParallelDiscoveryState()`
- `dbms.cluster.switchDiscoveryServiceVersion()`

Their removal is why the transition must finish before upgrading.

## Renamed and removed configuration

### Replace settings renamed in 2025.01

```text
db.logs.query.annotation_data_as_json_enabled
  -> db.logs.query.annotation_data_format
dbms.cluster.catchup.client_inactivity_timeout
  -> dbms.cluster.network.client_inactivity_timeout
server.max_databases
  -> dbms.max_databases
```

### Remove settings with no replacement

Neo4j 2025.01 removes all of the following:

```text
db.tx_state.memory_allocation
dbms.cluster.discovery.log_level
dbms.cluster.discovery.type
dbms.cluster.discovery.endpoints
dbms.cluster.discovery.version
dbms.kubernetes.service_port_name
initial.dbms.database_allocator
server.memory.off_heap.block_cache_size
server.memory.off_heap.max_cacheable_block_size
server.memory.off_heap.transaction_max_size
```

### Move server groups to tags

The catch-up strategies `connect-randomly-to-server-group` and
`connect-randomly-within-server-group` are replaced by their
`*-server-tags` variants. Rename the related settings:

```text
db.cluster.raft.leader_transfer.priority_group
  -> db.cluster.raft.leader_transfer.priority_tag
server.cluster.catchup.connect_randomly_to_server_group
  -> server.cluster.catchup.connect_randomly_to_server_tags
server.groups
  -> initial.server.tags
```

### Apply new-install defaults consciously

New installations, and upgrades that replace configuration files, receive:

```text
db.logs.query.annotation_data_format: CYPHER -> JSON
server.metrics.csv.rotation.compression: NONE -> ZIP
server.panic.shutdown_on_panic: false -> true
server.logs.config: conf/server-logs.xml -> server-logs.xml
server.logs.user.config: conf/user-logs.xml -> user-logs.xml
```

Relative log-configuration paths resolve from
`server.directories.configuration`, no longer
`server.directories.neo4j_home`.

### Remove deprecated configuration entry points

- `server_policies` and `dbms.routing.load_balancing.plugin` are deprecated
  from 2025.05.
- `server.db.query_cache_size` is deprecated.
- `dbms.security.oidc.<provider>.auth_params` and
  `dbms.security.oidc.<provider>.client_id` are deprecated.

## Procedure and command migrations

### Replace cluster procedures

```text
dbms.cluster.recreateDatabase() -> dbms.recreateDatabase()
dbms.cluster.routing.getRoutingTable() -> dbms.routing.getRoutingTable()
dbms.cluster.uncordonServer() -> ENABLE SERVER
```

Cypher 25 removes these additional entry points:

```text
dbms.cluster.readReplicaToggle()
  -> dbms.cluster.secondaryReplicationDisable()
dbms.quarantineDatabase()
  -> dbms.unquarantineDatabase()
```

`dbms.setDatabaseAllocator()` is removed without replacement.

### Use specific server-management privilege

`dbms.cluster.cordonServer()`,
`dbms.cluster.setAutomaticallyEnableFreeServers()`, and
`dbms.cluster.uncordonServer()` require `SERVER MANAGEMENT`. Using an admin
privilege is deprecated.

### Move CDC procedures to the database namespace

```text
cdc.current() -> db.cdc.current()
cdc.earliest() -> db.cdc.earliest()
cdc.query() -> db.cdc.query()
```

The unqualified beta namespace is deprecated.

### Stop invoking removed upgrade procedures

Cypher 25 removes `dbms.upgrade()` and `dbms.upgradeStatus()`. Upgrade
automation must not call them.

### Rename `neo4j-admin` operations

```text
neo4j-admin database aggregate-backup -> neo4j-admin backup aggregate
neo4j-admin database migrate --page-cache -> --max-off-heap-memory
```

## Vector API migrations

In Cypher 25, replace deprecated procedures:

```text
db.index.vector.queryNodes() -> SEARCH clause
db.index.vector.queryRelationships() -> SEARCH clause
```

The following older procedures are removed:

```text
db.index.vector.createNodeIndex() -> CREATE VECTOR INDEX
db.create.setVectorProperty() -> db.create.setNodeVectorProperty()
```

## HTTP, Java, logs, and monitoring

### Replace deprecated integration contracts

- The transactional HTTP API is deprecated in 5.26. Use the HTTP Query API,
  which is enabled by default from 5.26. On earlier versions, add
  `QUERY_API_ENDPOINTS` to `server.http_enabled_modules`.
- Programmatic use of error-message text is deprecated from 2025.04. Parse
  GQLSTATUS error codes.
- The server Notification API and Result Core API `getNotifications()` are
  deprecated from 5.26.
- JSON query-log `failureReason` is deprecated from 2025.05. Use `errorInfo`.

### Replace Raft observability contracts

The HTTP `raftCommandsPerSecond` field is deprecated. Monitor
`<prefix>.cluster.raft.commit_index` across every server and check for
divergence.

`<prefix>.cluster.raft.in_flight_cache.max_bytes` and
`<prefix>.cluster.raft.in_flight_cache.max_elements` are deprecated from
2026.07 and will be removed after the next LTS. The
`<prefix>.cluster.raft.tx_retries` series has been deprecated since 2025.02.

Neo4j 2025.01 removes the old `causal_clustering.core` Raft metrics for
indexes, term, leadership, retries, in-flight cache, prefetch buffering,
message processing, replication, and last-leader messages. The three
`causal_clustering.read_replica.pull_update*` metrics move to store-copy
metrics; six `cluster.discovery` discovery-v1 metrics have no replacements.

Rename:

```text
<prefix>.store.size.total -> <prefix>.store.size.full
```

### Parse default debug output as JSON

The default `debug.log` changes from text to JSON. Keep the default appender
for supportability and add a second appender when another format is required.

## Removed public Java APIs

Neo4j 2025.01 removes Java symbols tied to retired allocation, groups,
discovery, Raft, transaction-memory, and query-annotation facilities:

```text
EnterpriseEditionSettings.{initial_database_allocator,server_groups,server_max_number_of_databases}
WaitResponseState
ClusterSettings.{DEFAULT_CLUSTER_STATE_DIRECTORY_NAME,DEFAULT_DISCOVERY_PORT,DEFAULT_RAFT_PORT,DEFAULT_TRANSACTION_PORT,catchup_connect_randomly_to_server_group,raft_leader_transfer_priority_group}
ClusterBaseSettings.DEFAULT_DISCOVERY_PORT
ClusterNetworkSettings.catchup_client_inactivity_timeout
ParallelDiscoveryMode
RemotesResolver.Type
RemotesResolver.init(Type,Configuration,LogProvider)
ClusterAddressSettings.discovery_advertised_address
DiscoverySettings.{discovery_endpoints,discovery_listen_address,discovery_log_level,discovery_type,discovery_version}
KubernetesSettings.kubernetes_service_port_name
RaftSettings.{DEFAULT_CLUSTER_STATE_DIRECTORY_NAME,DEFAULT_RAFT_PORT}
SeedDownloadStreamWrapper
SeedProviderDependencies
GraphDatabaseSettings.{TransactionStateMemoryAllocation,log_queries_annotation_data_as_json,tx_state_max_off_heap_memory,tx_state_memory_allocation,tx_state_off_heap_block_cache_size,tx_state_off_heap_max_cacheable_block_size}
```

The removed `com.neo4j.dbms.seeding.SeedProvider` has the explicit replacement
`DatabaseSeedProvider`.

## Seed providers

Replace `S3SeedProvider` with `CloudSeedProvider` from 5.26. Use
`FileSeedProvider` for filesystem seeds because `URLConnectionSeedProvider`
no longer accepts `file` locations in either Cypher 5 or Cypher 25.

## TLS and key migrations

The default `dbms.ssl.policy.*.verify_hostname` value changes from `false` to
`true`. Ensure certificates match peer hostnames before accepting the default.

PKCS #1 keys beginning with `-----BEGIN RSA PRIVATE KEY-----` still load, but
are deprecated and will be removed. Replace them with supported server keys.

## Platform and packaging removals

### Removed in 2025.01

Neo4j no longer supports macOS 11 or 12, Amazon Linux 2022 AMI, Ubuntu Server
16.04, 18.04, or 20.04, or Windows Server 2016 or 2019.

### Current deprecation plan

- Ubuntu Server 22.04, macOS 15 Sequoia, CentOS Stream 9, and Windows Server
  2022 are deprecated as of 2026.05.0.
- `debian:bullseye-slim` and `redhat/ubi9-minimal:latest` are unsupported base
  images from 2026.05.
- CentOS Stream 8.x and SysV init scripts are deprecated from 2026.01.
- RHEL 8.x, Debian 11.x, macOS 13 Ventura, and macOS 14 Sonoma are deprecated
  from 2025.10 and supported only through the 2026 LTS.

Non-TLS/SSL MinIO endpoints in the `neo4j/neo4j-admin` Helm charts are
deprecated; configure `s3Endpoint`.
