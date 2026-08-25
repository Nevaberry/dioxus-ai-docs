# Schema, Indexes, Import, and Backup

Use this reference for schema commands, vector-index construction, seeding,
bulk import, database copy, and backup tooling.

## Constraint commands

Cypher 25 accepts:

```cypher
SHOW NODE PROPERTY UNIQUENESS CONSTRAINTS
SHOW RELATIONSHIP PROPERTY UNIQUENESS CONSTRAINTS
```

`PROPERTY` is optional. Returned constraint type names are
`NODE_PROPERTY_UNIQUENESS` and `RELATIONSHIP_PROPERTY_UNIQUENESS`. Consumers of
`SHOW` output must use those names.

The `indexProvider` option has been removed from index and constraint creation
commands. Remove it from generated DDL.

## Graph type schema

`GRAPH TYPE` is generally available in `2026.06.0` for production schema
definition, enforcement, and validation. Inspect the graph-shaped form with:

```cypher
SHOW CURRENT GRAPH TYPE AS GRAPH
```

The result contains lists of virtual nodes and relationships rather than the
string representation.

For full import, `neo4j-admin database import full --schema` accepts the
preview `ALTER CURRENT GRAPH TYPE SET {…}` command (since `2026.05.0`).
Incremental import later adds `ALTER CURRENT GRAPH TYPE ADD/DROP/ALTER {…}`
through the same `--schema` option.

## Hi-Fidelity quantized vector indexes

The preview Hi-Fidelity Quantized Vector Search expands a search over
quantized vectors, then reranks with full-precision vectors. Enable it per
index with a quantization type and default search expansion factor:

```cypher
CREATE VECTOR INDEX moviePlots IF NOT EXISTS
FOR (m:Movie)
ON m.embedding
OPTIONS {indexConfig: {
  `vector.quantization.type`: 'binary',
  `vector.default_search_expansion_factor`: 2.0,
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}}
```

An existing vector index must be rebuilt to adopt Hi-Fidelity quantization.

Use declarative `CREATE VECTOR INDEX` instead of removed
`db.index.vector.createNodeIndex()`. For property updates, replace removed
`db.create.setVectorProperty()` with `db.create.setNodeVectorProperty()`.

## Database seeding

Cypher 25 removes `seedCredentials`. Cloud-seed credentials must come from each
cloud provider's native credential mechanism.

It also makes these option changes:

- Replace `existingDataSeedInstance` with `existingDataSeedServer`.
- Use `seedSourceDatabase` to filter restored backup artifacts.
- `existingData` is deprecated and now optional.
- `CREATE DATABASE` accepts Java `Long` parameters as well as `Int`.

For a sharded property database, `CREATE DATABASE` can seed from artifacts in
cluster members' seed-repository folders by using `server://` values in
`seedUri` (since `2026.04.0`):

```cypher
CREATE DATABASE spd OPTIONS {
  seedUri: ["server://server-1/", "server://server-2/"]
}
```

For filesystem locations, use `FileSeedProvider`;
`URLConnectionSeedProvider` no longer accepts `file` in either Cypher 5 or 25.
`S3SeedProvider` is replaced by `CloudSeedProvider` from 5.26.

## Full and incremental import

### Composite identities

Multi-column identities in `neo4j-admin import` can use `INTEGER` ID types
instead of being forced to `STRING`. Composite keys can retain their intended
type.

### Vector values

`--vector-delimiter` must differ from both `--delimiter` and `--quote`. The
importer can read vector values directly from native Parquet list types.

### Bad-entry tolerance

From 2025.12, full and incremental import default `--bad-tolerance` to `-1`,
meaning unlimited, rather than `1000`. Set a finite value when the operation
must stop after a bounded number of bad entries.

### Progress-log locations

In 2026.03, import progress moves from:

```text
server/logs/neo4j-admin-import-yyyy-MM-dd.HH.mm.ss.log
```

to:

```text
server/data/imports/dbname-yyyy-MM-dd.HH.mm.ss/import.log
```

In 2026.04, the generated import-information directory moves back beneath
`server/logs/`. Operational tooling should account for the installation's
exact point in that transition.

## Database copy

From 2025.01, `neo4j-admin database copy --from-pagecache=<size>` is the maximum
off-heap memory for the complete copy operation, covering reads and writes. It
is not merely the source read cache. The clearer equivalent is:

```text
--max-off-heap-memory=<size>
```

For `neo4j-admin database migrate`, replace deprecated `--page-cache` with the
same `--max-off-heap-memory` option.

## Backup-format output

`neo4j-admin database copy` and `neo4j-admin database import` accept
`--compress` when producing backup-format output with
`--target-format=backup`.

Replace deprecated `neo4j-admin database aggregate-backup` with:

```text
neo4j-admin backup aggregate
```

`neo4j-admin backup inspect` orders results by append index, using time to
order entries that share an append index. Consumers may rely on that ordering
contract.

## Backup metadata filtering

From 2025.10, backup metadata can be limited to named users so only those users
and their role assignments are included:

```text
--include-metadata=users=alice,bob
```

## Property-shard allocation

In Cypher 25 from 2025.12, `dbms.setDefaultAllocationNumbers()` accepts a
`propertyShardReplicas` input. `dbms.showTopologyGraphConfig()` returns the
same field.
