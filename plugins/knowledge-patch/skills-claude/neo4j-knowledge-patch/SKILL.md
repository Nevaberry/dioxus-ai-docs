---
name: neo4j-knowledge-patch
description: Neo4j
version: 2026.06.0
license: MIT
metadata:
  author: Nevaberry
---


# Neo4j Knowledge Patch

Use this skill when upgrading, configuring, querying, administering, or
integrating with current Neo4j installations. Start with the breaking-change
checks, then open the topic reference that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [Administration, import, backup, and clusters](references/administration-import-backup-and-clusters.md) | `neo4j-admin`, seeds, backup, import, graph types, clustering, Fleet Manager, and store migration |
| [Configuration, platforms, and observability](references/configuration-platforms-and-observability.md) | Settings, defaults, supported platforms, logs, metrics, Query API, Cypher Shell, and Java APIs |
| [Cypher language and query runtime](references/cypher-language-and-query-runtime.md) | Cypher 5/25 selection, syntax, semantics, functions, planner behavior, and correctness fixes |
| [Security, access control, and TLS](references/security-access-and-tls.md) | ABAC, PBAC, OIDC, privileges, auth rules, TLS, keys, and security logs |
| [Upgrades, deprecations, and removals](references/upgrades-deprecations-and-removals.md) | Urgent patch upgrades, discovery migration, renamed and removed settings, procedures, formats, and platforms |
| [Vector search and GenAI](references/vector-search-and-genai.md) | Vector indexes, `SEARCH`, vector import, embeddings, token utilities, and provider configuration |

## Upgrade gates

### Avoid known data and checkpoint defects

- Do not remain on 2025.06.0 in production; use 2025.06.1 or later to avoid a
  sporadic checkpoint-mutex deadlock.
- Do not remain on 2026.07.0. Its block-format UTF-8 defect can make strings
  unreadable and can break queries using `trim()`; upgrade to 2026.07.1.
- Before moving beyond the next LTS, migrate every `high_limit` database
  offline to Block format. That LTS is the last release able to read, write,
  or migrate `high_limit`; later releases refuse to start such databases.

### Complete discovery migration before a 2025.01 upgrade

Discovery v1 is removed in 2025.01. Finish the v1-to-v2 transition first,
move internal discovery traffic from port `5000` to `6000`, and adopt the
current setting names:

```text
dbms.cluster.discovery.v2.endpoints -> dbms.cluster.endpoints
dbms.kubernetes.discovery.v2.service_port_name -> dbms.kubernetes.discovery.service_port_name
server.discovery.advertised_address -> server.cluster.advertised_address
server.discovery.listen_address -> server.cluster.listen_address
```

The old `*.v2.*` names are accepted only to bridge the 5.26-to-2025.01
migration. The discovery migration procedures themselves are gone in
2025.01, so do not plan to finish the transition after upgrading.

### Update configuration deliberately

For an upgrade that replaces configuration files, account for these new
defaults:

```text
db.logs.query.annotation_data_format: CYPHER -> JSON
server.metrics.csv.rotation.compression: NONE -> ZIP
server.panic.shutdown_on_panic: false -> true
server.logs.config: conf/server-logs.xml -> server-logs.xml
server.logs.user.config: conf/user-logs.xml -> user-logs.xml
```

Relative log-configuration paths now resolve from
`server.directories.configuration`. The TLS hostname-verification default is
also `true`; verify certificates and advertised hostnames rather than relying
on the former disabled default.

Replace renamed settings and remove unsupported ones before startup. In
particular, move server groups to server tags, query annotation configuration
to `db.logs.query.annotation_data_format`, catch-up inactivity to
`dbms.cluster.network.client_inactivity_timeout`, and the database cap to
`dbms.max_databases`.

## Choose the Cypher language explicitly

Cypher 5 is the frozen compatibility language; Cypher 25 is the evolving
language. A database can select its language at creation or alteration,
`db.query.default_language` controls new and initial databases, and a query
can override it:

```cypher
CYPHER 25 RETURN 1 AS value
```

Although databases originally defaulted to Cypher 5, packaged `neo4j.conf`
sets `db.query.default_language=CYPHER_25` starting in 2026.02. Treat the
effective database setting and deployment configuration as authoritative.

When moving a query to Cypher 25, review these semantic changes:

- A node or relationship cannot be the right side of a property-copying
  `SET`; write `SET target = properties(source)`.
- Imported variables in `COLLECT`, `COUNT`, and `EXISTS` subquery expressions
  are constants, not aggregation grouping keys. Empty matches can still
  produce an aggregate result.
- `stDev()` returns `null` on empty input.
- U+0085 is whitespace, formerly deprecated identifier characters are
  rejected, and parameter starts follow the broader GQL identifier set.
- Composite constituents use one symbolic reference such as
  `compdb.constituent`, not separately escaped components.

## Use current Cypher 25 composition features

Conditional branches use `WHEN`/`ELSE`, sequential composition uses `NEXT`,
and GQL-style braces can wrap top-level and composite-query arguments.
Standalone `FILTER` and `LET` avoid artificial `WITH` boundaries, including
between writes and reads:

```cypher
MATCH (p:Person)
LET name = p.name
FILTER name IS NOT NULL
RETURN name
```

Other high-use forms include:

- `FOR item IN list` as the GQL equivalent of `UNWIND`.
- `IS LABELED` and `IS NOT LABELED` as GQL label predicates.
- `RETURN ALL` and `WITH ALL` to retain duplicates explicitly.
- `REPEATABLE ELEMENTS` for walk semantics and
  `MATCH DIFFERENT RELATIONSHIPS` for explicit trail semantics.
- `ACYCLIC` with `ANY`, `SHORTEST`, `SHORTEST k`, `ALL SHORTEST`, or
  `SHORTEST k GROUPS` to forbid repeated nodes.
- `string.indexOf`, `string.join`, and `string.regexReplace` in place of the
  deprecated matching `apoc.text.*` functions.

Composable administration commands include `SHOW INDEXES`, `SHOW
CONSTRAINTS`, `SHOW CURRENT GRAPH TYPE`, `SHOW FUNCTIONS`, `SHOW PROCEDURES`,
`SHOW SETTINGS`, `SHOW TRANSACTIONS`, `SHOW DATABASES`, and `TERMINATE
TRANSACTIONS`.

## Prefer current administration contracts

### Import and backup

- `neo4j-admin database copy` and `import` accept `--compress` with
  `--target-format=backup`.
- Full and incremental import default `--bad-tolerance` to unlimited (`-1`);
  set a finite value when bad input must stop the job.
- `--from-pagecache` now caps off-heap memory for the entire copy. Prefer the
  clearer `--max-off-heap-memory` name.
- Vector delimiters must differ from both the field delimiter and quote;
  native Parquet list values can supply vectors directly.
- Multi-column import identities may use `INTEGER` ID types.

Use `neo4j-admin backup aggregate` instead of the deprecated `database
aggregate-backup`, and use `--max-off-heap-memory` instead of `--page-cache`
for `database migrate`.

### Seeds and graph types

Cloud seed credentials now come from provider mechanisms; `seedCredentials`
is removed. Use `existingDataSeedServer` instead of
`existingDataSeedInstance`, and use `seedSourceDatabase` to select a restored
backup artifact. For filesystem seeds, use `FileSeedProvider`; the URL
connection provider no longer accepts `file` locations.

`GRAPH TYPE` is production-ready. Full import accepts `ALTER CURRENT GRAPH
TYPE SET {…}` through `--schema`, while incremental import accepts
`ADD`/`DROP`/`ALTER`. Use `SHOW CURRENT GRAPH TYPE AS GRAPH` when consumers
need virtual-node and virtual-relationship lists rather than a string.

## Adopt current vector search

Use the Cypher 25 `SEARCH` clause instead of the deprecated
`db.index.vector.queryNodes()` and `db.index.vector.queryRelationships()`.
Its filter predicate supports `IN`:

```cypher
MATCH (movie:Movie)
SEARCH movie IN (
  VECTOR INDEX moviePlots
  FOR $queryVector
  WHERE movie.genre IN ['Horror', 'SciFi']
  LIMIT $topK
)
RETURN movie.title, movie.rating
```

Hi-Fidelity Quantized Vector Search is preview functionality. Enable binary
quantization and an expansion factor per index; rebuild existing indexes to
use it. Keep full-precision vectors available because results are reranked
against them.

## Protect concurrent writes and runtime correctness

Use `DISJOINT BY` with `CALL { … } IN CONCURRENT TRANSACTIONS` when the key
partition is known. It schedules disjoint write work before transactions
begin, avoiding lock contention and deadlocks in operations such as unique
merges and relationship creation.

Do not preserve workarounds that compensate for fixed runtime bugs without
retesting. The pipelined runtime now returns correct `COUNT(DISTINCT)` results
without leveraged order, preserves rows for ordered `OR EXISTS` subqueries,
and no longer undercounts undirected multi-type scans.

The parallel runtime disables its Repeat-over-VarExpand heuristic by default
to avoid excessive memory for variable-length patterns with input cardinality
one. Re-enable it for a specific query only when measured:

```cypher
CYPHER parallelRepeatHeuristic=enabled
MATCH (a:A {prop: 123}) ((n)-[r:R]->(m))+ (b)
RETURN a, b
```

## Keep integrations on structured contracts

- Query API transaction identifiers are six characters; do not enforce the
  former four-character shape.
- Parse GQLSTATUS codes rather than mutable error-message text.
- Cypher Shell defaults `--error-format` to `gql`; scripts needing another
  format must request it explicitly.
- `SHOW TRANSACTIONS` time fields are `ZONED DATETIME`, unavailable values may
  be `null`, and `WAIT` cluster state arrives as notifications rather than
  result rows.
- Schema procedures report Cypher type names in `propertyTypes`, not Java type
  names.
- `EXPLAIN` and `PROFILE` identify the point release, so plan parsers must
  accept the more detailed version string.

For all renamed APIs, procedures, metrics, settings, platform removals, and
security migrations, use the linked topic references as the implementation
checklist rather than guessing compatibility aliases.
