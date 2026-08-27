# Upgrades and Breaking Changes

Use this reference to plan upgrade order, configuration rewrites, API rebuilds,
and platform or store-format migration.

## Required maintenance releases

### Checkpoint deadlock in 2025.06

The base `2025.06` release can sporadically deadlock on the checkpoint mutex.
Run production deployments on `2025.06.1` or later, where the defect is fixed.

### Block-format UTF-8 defect in 2026.07.0

Neo4j `2026.07.0` has a block-format UTF-8 defect that can cause unexpected
failures in Cypher `trim()` and, in some cases, make stored string data
unreadable. Upgrade affected installations to `2026.07.1`.

## Discovery migration gate

Neo4j 2025.01 removes discovery service v1. A cluster must complete its v1-to-v2
transition before upgrading. Internal discovery traffic moves from port `5000`
to `6000`, and settings move as follows:

```text
dbms.cluster.discovery.v2.endpoints -> dbms.cluster.endpoints
dbms.kubernetes.discovery.v2.service_port_name -> dbms.kubernetes.discovery.service_port_name
server.discovery.advertised_address -> server.cluster.advertised_address
server.discovery.listen_address -> server.cluster.listen_address
```

The old `*.v2.*` names remain accepted for the 5.26-to-2025.01 migration, but
should be replaced. These migration procedures are removed without replacement:

```text
dbms.cluster.moveToNextDiscoveryVersion()
dbms.cluster.showParallelDiscoveryState()
dbms.cluster.switchDiscoveryServiceVersion()
```

The removal means an operator cannot defer the discovery transition until
after upgrading.

## Groups become tags

Replace `connect-randomly-to-server-group` and
`connect-randomly-within-server-group` with their `*-server-tags` forms. Rename
the related settings:

```text
db.cluster.raft.leader_transfer.priority_group -> db.cluster.raft.leader_transfer.priority_tag
server.cluster.catchup.connect_randomly_to_server_group -> server.cluster.catchup.connect_randomly_to_server_tags
server.groups -> initial.server.tags
```

## Configuration removals and replacements

Neo4j 2025.01 replaces:

```text
db.logs.query.annotation_data_as_json_enabled -> db.logs.query.annotation_data_format
dbms.cluster.catchup.client_inactivity_timeout -> dbms.cluster.network.client_inactivity_timeout
server.max_databases -> dbms.max_databases
```

The following settings are removed without replacements:

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

Also migrate the deprecated `server_policies` load-balancing plugin and its
`dbms.routing.load_balancing.plugin` setting. The settings
`server.db.query_cache_size`, `dbms.security.oidc.<provider>.auth_params`, and
`dbms.security.oidc.<provider>.client_id` are deprecated as well.

## New-install defaults

These changes apply to new installations and to upgrades that replace existing
configuration files:

```text
db.logs.query.annotation_data_format: CYPHER -> JSON
server.metrics.csv.rotation.compression: NONE -> ZIP
server.panic.shutdown_on_panic: false -> true
server.logs.config: conf/server-logs.xml -> server-logs.xml
server.logs.user.config: conf/user-logs.xml -> user-logs.xml
```

Relative `server.logs.config` and `server.logs.user.config` paths are resolved
from `server.directories.configuration`, not
`server.directories.neo4j_home`. Retained configuration does not silently gain
the new-install values.

Starting in 2026.02, the packaged `neo4j.conf` explicitly sets
`db.query.default_language=CYPHER_25`; new deployments using that file default
newly created databases to Cypher 25.

## Removed public Java surface

Neo4j 2025.01 removes public Java symbols tied to retired allocators, groups,
discovery, Raft, transaction memory, and query annotations:

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

Replace removed `com.neo4j.dbms.seeding.SeedProvider` with
`DatabaseSeedProvider`. The server-side Notification API and Result Core
`getNotifications()` are separately deprecated from 5.26; Java integrations
should stop using them.

## Logging and metric compatibility

The default `debug.log` format changes from text to JSON. Keep the default
appender for supportability; add another appender if a second format is needed.
Consumers of the default file must accept JSON.

The old `causal_clustering.core` Raft series for indexes, term, leadership,
retries, in-flight cache, prefetch buffering, message processing, replication,
and last-leader messages are removed in favor of Raft metrics. The three
`causal_clustering.read_replica.pull_update*` metrics move to store-copy
metrics. Six discovery-v1 series under `cluster.discovery` have no replacement.

Rename `<prefix>.store.size.total` to `<prefix>.store.size.full` in dashboards
and alerts.

## Supported-platform transitions

Neo4j 2025.01 removes support for macOS 11 and 12, the Amazon Linux 2022 AMI,
Ubuntu Server 16.04, 18.04, and 20.04, and Windows Server 2016 and 2019.

Further retirement notices require advance planning:

- Ubuntu Server 22.04, macOS 15 Sequoia, CentOS Stream 9, and Windows Server
  2022 are deprecated in `2026.05.0` and will be removed later.
- From 2026.05, `debian:bullseye-slim` and
  `redhat/ubi9-minimal:latest` are unsupported as base images.
- CentOS Stream 8.x and SysV init scripts are deprecated from 2026.01.
- RHEL 8.x, Debian 11.x, macOS 13 Ventura, and macOS 14 Sonoma are deprecated
  from 2025.10 and supported only through the 2026 LTS.

## Administrative procedure removals

`dbms.setDatabaseAllocator()` is removed without replacement. Cypher 25 also
removes deprecated `dbms.upgrade()` and `dbms.upgradeStatus()`; remove these
calls from administrative automation.

Cluster entry points migrate as follows:

```text
dbms.cluster.recreateDatabase() -> dbms.recreateDatabase()
dbms.cluster.routing.getRoutingTable() -> dbms.routing.getRoutingTable()
dbms.cluster.uncordonServer() -> ENABLE SERVER
dbms.cluster.readReplicaToggle() -> dbms.cluster.secondaryReplicationDisable()
dbms.quarantineDatabase() -> dbms.unquarantineDatabase()
```

## TLS and seed-provider behavior

`dbms.ssl.policy.*.verify_hostname` changes its default from `false` to `true`.
After upgrading, TLS policies verify peer hostnames unless retained
configuration explicitly fixes the value.

`URLConnectionSeedProvider` no longer accepts `file` locations in Cypher 5 or
Cypher 25. Use `FileSeedProvider` for filesystem seeds.

## Store-format deadline

The next LTS is the last release that can read, write, or migrate `high_limit`
databases. Migrate them offline to Block format before upgrading beyond that
LTS. A remaining `high_limit` database fails to start and has no compatibility
fallback.

The `standard` store format has been deprecated since 5.23. Do not select it
for new databases, and plan to move existing stores away from it.
