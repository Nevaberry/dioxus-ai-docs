# Administration, Import, Backup, and Clusters

## Database creation and seeding

### Seed option contract (2025.06)

Cypher 25 removes `seedCredentials`; obtain cloud-seed credentials through the
cloud provider's built-in mechanism. Replace `existingDataSeedInstance` with
`existingDataSeedServer`, and use `seedSourceDatabase` to filter the restored
backup artifacts. `existingData` is deprecated and is now optional.

`CREATE DATABASE` accepts Java `Long` parameters as well as `Int` parameters.

### Cluster-local seeds for sharded property databases (2026.04.0)

Seed a sharded property database from artifacts in cluster members' seed
repository folders by passing `server://` locations in `seedUri`:

```cypher
CREATE DATABASE spd OPTIONS {
  seedUri: ["server://server-1/", "server://server-2/"]
}
```

### Seed-provider migrations

Use `CloudSeedProvider` instead of `S3SeedProvider` from 5.26. For filesystem
seeds, use `FileSeedProvider`; `URLConnectionSeedProvider` no longer supports
`file` locations in either Cypher 5 or Cypher 25.

## Backup and copy operations

### Produce compressed backup-format output (2026.04.0)

`neo4j-admin database copy` and `neo4j-admin database import` accept
`--compress` when output uses `--target-format=backup`.

### Depend on the documented inspection order (2026.04.0)

`neo4j-admin backup inspect` sorts by append index. Entries sharing an append
index are ordered by time. Automation may use that ordering contract.

### Bound copy memory by the whole operation

Since 2025.01, `neo4j-admin database copy --from-pagecache=<size>` limits
off-heap memory across both reads and writes, rather than only the source read
cache. Prefer the clearer equivalent:

```text
--max-off-heap-memory=<size>
```

### Filter user metadata in backups

Since 2025.10, include only named users and their role assignments with:

```text
--include-metadata=users=alice,bob
```

### Use current backup and migration commands

Replace deprecated invocations as follows:

```text
neo4j-admin database aggregate-backup -> neo4j-admin backup aggregate
neo4j-admin database migrate --page-cache -> --max-off-heap-memory
```

## Import workflows

### Preserve integer composite identities (2026.04.0)

Multi-column identities in `neo4j-admin import` may use `INTEGER` ID types;
they no longer need to be coerced to `STRING`.

### Apply graph types through import schemas

In 2026.05.0, full import accepts the preview command
`ALTER CURRENT GRAPH TYPE SET {…}` through `neo4j-admin database import full
--schema`.

In 2026.06.0, incremental import additionally accepts `ALTER CURRENT GRAPH
TYPE ADD/DROP/ALTER {…}` through `--schema`.

### Parse vector input safely (2026.06.0)

The `--vector-delimiter` character must differ from both `--delimiter` and
`--quote`. The importer can also read vectors directly from native Parquet
list types.

### Set bad-entry tolerance explicitly

Since 2025.12, full and incremental import default `--bad-tolerance` to `-1`,
meaning unlimited. Set a finite value when the operation must abort after a
bounded number of bad entries.

### Locate import-progress logs by release

The log layout changed twice:

- In 2026.03, progress moved from
  `server/logs/neo4j-admin-import-yyyy-MM-dd.HH.mm.ss.log` to
  `server/data/imports/dbname-yyyy-MM-dd.HH.mm.ss/import.log`.
- In 2026.04, the generated import-information directory moved back beneath
  `server/logs/`.

Discover the effective path instead of hard-coding the oldest flat filename.

## Graph types and schema administration

### Use graph types in production (2026.06.0)

`GRAPH TYPE` is generally available for schema definition, enforcement, and
validation. To obtain graph-shaped inspection output, use:

```cypher
SHOW CURRENT GRAPH TYPE AS GRAPH
```

The result contains lists of virtual nodes and relationships rather than the
string representation.

### Inspect and create constraints in Cypher 25 (2025.06)

`SHOW [NODE|RELATIONSHIP] PROPERTY UNIQUENESS CONSTRAINTS` is accepted, and
`PROPERTY` is optional. Returned type names are
`NODE_PROPERTY_UNIQUENESS` and `RELATIONSHIP_PROPERTY_UNIQUENESS`.

Do not supply `indexProvider` to index or constraint creation commands; that
option has been removed.

## Cluster allocation and topology

### Configure property-shard replicas

In Cypher 25 from 2025.12,
`dbms.setDefaultAllocationNumbers()` accepts `propertyShardReplicas`.
`dbms.showTopologyGraphConfig()` returns the same field.

### Partition concurrent writes before they begin (2026.06.0)

`CALL { … } IN CONCURRENT TRANSACTIONS` supports `DISJOINT BY`. Use it when
rows can be partitioned into disjoint write sets: scheduling occurs before
transactions begin, preventing lock contention and deadlocks in workloads
such as merges under unique constraints and relationship creation.

### Move server groups to tags

Replace catch-up strategies `connect-randomly-to-server-group` and
`connect-randomly-within-server-group` with their `*-server-tags` forms.
Move the related settings:

```text
db.cluster.raft.leader_transfer.priority_group
  -> db.cluster.raft.leader_transfer.priority_tag
server.cluster.catchup.connect_randomly_to_server_group
  -> server.cluster.catchup.connect_randomly_to_server_tags
server.groups
  -> initial.server.tags
```

## Fleet and operations management

### Discover and register local servers (2026.05.0)

The server includes local-network discovery. Run `neo4j-admin fleet discover`
to list deployments, then use `neo4j-admin` bulk registration to register them
with Fleet Manager for Aura Console display.

Enterprise Fleet Management is no longer bundled with the DBMS package as of
2026.04.0 because it is included in Neo4j. Enterprise also includes Neo4j Ops
Manager 1.15.1, which supports any-to-any Neo4j upgrades.

### Use Cypher Shell system information on Infinigraph

Cypher Shell `:sysinfo` supports Infinigraph deployments as of 2026.05.0.

## Administrative result contracts

### Handle typed and notification results (2025.06)

In Cypher 25, `SHOW TRANSACTIONS.startTime` and
`currentQueryStartTime` are `ZONED DATETIME`, not `STRING`. Unavailable values
in several transaction columns are `null`.

Administration commands using `WAIT` report cluster state as notifications,
not result rows. Revoking a privilege that cannot exist now raises an error.

### Track CDC commit time (2026.06.0)

`db.cdc.current()` returns `txCommitTime` alongside the transaction identifier,
allowing a CDC client to retrieve its most recent transaction's commit time.

Use the `db.cdc.*` namespace. The beta `cdc.current()`, `cdc.earliest()`, and
`cdc.query()` procedures are deprecated in favor of `db.cdc.current()`,
`db.cdc.earliest()`, and `db.cdc.query()`.
