---
name: neo4j-knowledge-patch
description: Neo4j
version: "2026.06.0"
license: MIT
metadata:
  author: Nevaberry
---


# Neo4j Knowledge Patch

Use this skill when writing or reviewing Cypher, planning a Neo4j upgrade,
changing server configuration, operating imports or backups, maintaining
security rules, or adapting integrations to current result and API contracts.

Check the deployed edition and exact version before applying version-sensitive
guidance. Preserve an existing installation's retained configuration unless a
new-install default is intentionally wanted. Prefer the project's manifests,
configuration, queries, and tests when they show deployment-specific behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [Cypher and query behavior](references/cypher-and-query-behavior.md) | Language selection, query composition, path semantics, functions, runtime fixes, graph types, and vector `SEARCH` |
| [Operations, observability, and packaging](references/operations-observability-and-packaging.md) | Server settings, logs, metrics, shell, Fleet Manager, packaging, platform changes, and TLS operations |
| [Schema, indexes, import, and backup](references/schema-indexes-import-and-backup.md) | Constraints, graph schema, vector indexes, seeding, import, copy, and backup |
| [Security, access, and integrations](references/security-access-and-integrations.md) | ABAC, OIDC, privileges, APIs, CDC, GenAI, Java integration, and key migration |
| [Upgrades and breaking changes](references/upgrades-and-breaking-changes.md) | Required patch upgrades, discovery migration, renamed settings, removed APIs, store formats, and upgrade gates |

## Upgrade guards

### Avoid two defective base releases

- Do not leave production on `2025.06`: a checkpoint-mutex deadlock was fixed
  in `2025.06.1`.
- Do not leave an affected installation on `2026.07.0`: a block-format UTF-8
  defect can break `trim()` queries and can make stored strings unreadable.
  Upgrade to `2026.07.1`.

### Complete discovery migration before 2025.01

Neo4j 2025.01 removes discovery v1. Complete the v1-to-v2 transition before
upgrading, move internal discovery traffic from port `5000` to `6000`, and
replace the transitional names:

```text
dbms.cluster.discovery.v2.endpoints -> dbms.cluster.endpoints
dbms.kubernetes.discovery.v2.service_port_name -> dbms.kubernetes.discovery.service_port_name
server.discovery.advertised_address -> server.cluster.advertised_address
server.discovery.listen_address -> server.cluster.listen_address
```

The old `*.v2.*` settings remain accepted only for the 5.26-to-2025.01
migration. The discovery migration procedures are removed, so do not plan to
complete the transition after the upgrade.

### Migrate stores before the format deadline

The next LTS is the final release able to read, write, or migrate `high_limit`
databases. Before moving beyond it, perform an offline migration to Block
format. A remaining `high_limit` database will not start and has no fallback.
The older `standard` format is deprecated; do not select it for new databases
and plan migrations for existing stores.

## Configuration migration checklist

Before a 2025.01 upgrade, replace these settings:

```text
db.logs.query.annotation_data_as_json_enabled -> db.logs.query.annotation_data_format
dbms.cluster.catchup.client_inactivity_timeout -> dbms.cluster.network.client_inactivity_timeout
server.max_databases -> dbms.max_databases
db.cluster.raft.leader_transfer.priority_group -> db.cluster.raft.leader_transfer.priority_tag
server.cluster.catchup.connect_randomly_to_server_group -> server.cluster.catchup.connect_randomly_to_server_tags
server.groups -> initial.server.tags
```

Replace the `*-server-group` catch-up strategies with their `*-server-tags`
forms. Audit removed settings and public Java symbols in the upgrade reference;
many discovery, allocator, Raft, transaction-memory, and group APIs have no
replacement.

New installations, and upgrades that replace configuration files, also adopt
JSON query annotations, ZIP CSV-metric rotation, shutdown on panic, and log
configuration paths relative to `server.directories.configuration`. Retained
configuration files keep their existing values.

## Cypher language selection

Cypher 5 is frozen for compatibility, while Cypher 25 evolves. Select a
language per query when compatibility is important:

```cypher
CYPHER 25 RETURN 1 AS value
```

Language can also be selected per database at creation or alteration.
`db.query.default_language` controls new and initial databases. The distributed
`neo4j.conf` sets it to `CYPHER_25` starting in 2026.02, so a new deployment
using that file differs from earlier defaults.

### High-value Cypher 25 forms

Cypher 25 adds conditional `WHEN`/`ELSE`, sequential `NEXT`, GQL-style top-level
braces, standalone `FILTER` and `LET`, `FOR` as the GQL equivalent of `UNWIND`,
and composable administration commands. It also allows a read directly after a
write without an intervening `WITH`.

```cypher
MATCH (p:Person)
LET name = p.name
FILTER name IS NOT NULL
RETURN name
```

Choose path semantics deliberately. Trail semantics remains the default and is
explicit as `MATCH DIFFERENT RELATIONSHIPS`; `REPEATABLE ELEMENTS` permits a
relationship to repeat. `ACYCLIC` prevents repeated nodes and now works with
restrictive selectors such as `ANY`, `SHORTEST`, and `SHORTEST k GROUPS`.

When copying properties, the right side must be a map:

```cypher
SET target = properties(source)
```

Use one symbolic composite constituent reference such as
`compdb.constituent`; do not split it into separately quoted parts. Use the
complete string with `graph.byName()` when names themselves contain dots.

## Query-result compatibility

Update consumers for these contract changes:

- `SHOW TRANSACTIONS.startTime` and `currentQueryStartTime` are `ZONED
  DATETIME` in Cypher 25, and unavailable transaction values can be `null`.
- Administration commands with `WAIT` report cluster state as notifications,
  not rows; revoking an impossible privilege is an error.
- Schema procedures return Cypher names, not Java names, in `propertyTypes`.
- Cypher Shell defaults `--error-format` to `gql`; parsing scripts should set
  the desired format explicitly.
- Query API transaction IDs are six characters rather than four.
- `EXPLAIN` and `PROFILE` identify the point release, not only a broader
  version.
- `stDev()` returns `null` for empty input.

Runtime corrections can increase results: ordered `OR EXISTS` no longer loses
a row, undirected multi-type scans no longer omit sibling relationships, and
pipelined `COUNT(DISTINCT)` no longer overcounts when leveraged order is
missing. Treat changed counts as corrected semantics, not random drift.

## Vector and graph schema quick reference

Create vector indexes declaratively and query them with `SEARCH`; the older
vector query procedures are deprecated in Cypher 25. `IN` is supported inside
the vector-search filter predicate.

```cypher
MATCH (movie:Movie)
SEARCH movie IN (
  VECTOR INDEX moviePlots
  FOR $queryVector
  WHERE movie.genre IN ['Horror', 'SciFi']
  LIMIT $topK
)
RETURN movie
```

Hi-Fidelity Quantized Vector Search is enabled per index with
`vector.quantization.type` and
`vector.default_search_expansion_factor`. Existing indexes must be rebuilt to
adopt it. `GRAPH TYPE` is generally available, and
`SHOW CURRENT GRAPH TYPE AS GRAPH` returns virtual nodes and relationships.

## Import and backup safety

- Set a finite `--bad-tolerance` when imports must stop after bounded errors;
  full and incremental import otherwise default to unlimited (`-1`) from
  2025.12.
- Ensure `--vector-delimiter` differs from both `--delimiter` and `--quote`.
- Treat `--from-pagecache` on `database copy` as the operation-wide off-heap
  cap; prefer the clearer `--max-off-heap-memory` name.
- Use `--compress` with `--target-format=backup` for compressed backup output
  from `database copy` or `database import`.
- Cloud seed credentials come from provider-native mechanisms; Cypher 25 no
  longer accepts `seedCredentials`.

## Security and observability migrations

Move OIDC providers from deprecated Implicit flow to the default PKCE flow.
Use `SERVER MANAGEMENT` for server-management procedures. Native and linked
LDAP users can carry metadata tags used by ABAC rules; managing them requires
`DBMS USER METADATA MANAGEMENT`.

Branch program logic on GQLSTATUS codes, not mutable error text. Move JSON query
log consumers from `failureReason` to `errorInfo`. The default `debug.log` is
JSON after the breaking configuration change, and the default metrics filter
uses `neo4j.count` rather than deprecated `ids_in_use` metrics.

TLS hostname verification defaults to `true` after the upgrade. CBC suites are
no longer default-enabled, legacy PKCS #1 RSA private keys are deprecated, and
OpenSSL provider 3.5 or later can use `X25519MLKEM768` hybrid key exchange.

## Working method

1. Identify the exact server version, edition, Cypher language, store format,
   and whether configuration is retained or replaced.
2. For upgrades, apply both patch-release guards, then walk the discovery,
   configuration, public-API, platform, format, TLS, metrics, and logging gates.
3. For query changes, pin Cypher 5 or 25 explicitly in tests and validate result
   types, nullability, row counts, and notification handling.
4. For imports and schema work, validate delimiter, tolerance, memory, graph
   type, seed-provider, and vector-index choices before running a write.
5. Consult the indexed topic reference rather than inferring a removed name's
   replacement; several removals intentionally have none.
