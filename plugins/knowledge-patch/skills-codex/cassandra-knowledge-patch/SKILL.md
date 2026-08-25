---
name: cassandra-knowledge-patch
description: Apache Cassandra
version: 5.0.8
license: MIT
metadata:
  author: Nevaberry
---


# Apache Cassandra Knowledge Patch

Use this skill when writing, reviewing, upgrading, or operating Apache Cassandra
code, CQL, configuration, and tooling. Start with the compatibility-sensitive
items below, then load the topic reference that matches the task.

## How to apply this skill

1. Identify the Cassandra version, SSTable format, index implementations, Java
   runtime, and whether the cluster is in a mixed-version state.
2. For upgrades, check changed validation, authorization, command-line options,
   virtual-table representations, and operational defaults before changing
   automation.
3. For query or storage correctness, identify whether SAI, legacy secondary
   indexes, BTI, static columns, tombstones, repair, or descending clustering
   order is involved.
4. For operations, verify gossip, token metadata, disk guardrails, repair
   scheduling, and JMX visibility against live cluster state.
5. Treat compatibility fallbacks as safeguards, not as reasons to postpone
   format upgrades or mixed-version completion.

## Reference index

| Reference | Topics |
| --- | --- |
| [Operations, topology, and repair](references/operations-topology-and-repair.md) | Gossip, token metadata, hints, bootstrap, JMX, failure detection, streaming, guardrails, and AutoRepair |
| [Protocols and tooling](references/protocols-and-tooling.md) | Native protocol, serialization, `cqlsh`, `nodetool`, build tooling, Java, FQL, and `CQLSSTableWriter` |
| [Queries, schema, and indexing](references/queries-schema-and-indexing.md) | CQL behavior, schema, SAI, legacy secondary indexes, filtering, clustering order, and index lifecycle |
| [Security and configuration](references/security-and-configuration.md) | Authorization, identities, audit logging, password handling, YAML, virtual settings, and extensions |
| [Storage and data path](references/storage-and-data-path.md) | SSTables, compaction, commitlog, snapshots, caches, deletion reconciliation, and disk sizing |

## Breaking and behavior-sensitive changes

### Update `nodetool import` automation

The short option for `nodetool import --copy-data` is `-cd`. Replace scripts
that use the conflicting `-p` form.

```shell
nodetool import -cd keyspace_name table_name /path/to/sstables
```

### Expect tighter authorization

Operations that previously crossed DC, authorizer, or system-keyspace
boundaries may now be rejected. A non-superuser also cannot bind an identity to
a superuser. Test provisioning and role-management flows with their real
service accounts.

Password changes are rate-limited. Rotation automation should back off instead
of assuming rapid repeated changes will succeed.

### Do not depend on tool environment side effects

`nodetool` and related tools avoid sourcing `cassandra-env.sh` when it is not
needed. Put required settings in supported tool configuration or the caller's
environment instead of relying on incidental script side effects.

### Parse virtual settings defensively

Complex values in `system_views.settings` are JSON, sensitive values are
redacted, previously omitted settings are visible, and mappings may contain
non-string keys. Inventory consumers must handle all four conditions without
expecting secrets.

### Revalidate schema and snapshot names

Long table names that would exceed filesystem filename limits are rejected.
Snapshot operations also reject invalid snapshot names, while valid snapshot
directory names that older SSTable path checks rejected are accepted. Keep
identifier generation within Cassandra's validation rules.

### Recheck type compatibility

`BytesType` compatibility applies only to scalar types. Schema migration tools
must not assume it is compatible with collections or other non-scalar types.

### Plan around mixed-version safeguards

The automated repair scheduler stops when it detects two Cassandra major
versions. Mixed-version upgrades need an explicit repair plan and monitoring;
do not assume scheduled repairs remain active.

## Operations quick reference

### Check topology consistency

Use the token-metadata check when gossip state and ownership appear inconsistent.

```shell
nodetool checktokenmetadata
```

Restarted nodes are protected from delayed shutdown gossip, and multi-field
endpoint updates converge correctly. Still compare gossip, token metadata, and
the node's current lifecycle state before taking topology action.

### Configure and observe AutoRepair

Built-in AutoRepair provides in-process scheduling, a minimum task-duration
setting, `preview_repaired`, disk protection for full repair, and reporting of
expected versus actual bytes and keyspaces. Parallel repair counts greater than
one are supported. Monitor the scheduler and account for its mixed-major-version
shutdown behavior.

### Inspect guardrails

Use the guardrail commands instead of scraping configuration indirectly.

```shell
nodetool getguardrailsconfig
```

The disk-usage guardrail can be disabled after it trips, and first boot works
when `data_disk_usage_max_disk_size` is set before the data directory exists.

### Recalibrate corrected metrics

`nodetool gcstats` reports direct memory correctly, and `nodetool tablestats`
includes selected SAI state and query-performance details. Alert thresholds may
need adjustment after an upgrade.

## Query and indexing quick reference

### Define descending complex clustering keys

Frozen UDTs and vectors can be descending clustering keys. Snapshot schema CQL
also carries the required UDT definitions.

```cql
CREATE TYPE coordinates (x int, y int);
CREATE TABLE samples (
    sensor_id uuid,
    position frozen<coordinates>,
    embedding vector<float, 3>,
    PRIMARY KEY (sensor_id, position, embedding)
) WITH CLUSTERING ORDER BY (position DESC, embedding DESC);
```

### Account for index selection and lifecycle

When a column has both a legacy secondary index and SAI, Cassandra prioritizes
the legacy index. SAI availability after restart, writer switches, repair
flushes, segment checksum validation, ANN score ordering, and distributed
static-column tombstones all have correctness-sensitive handling described in
the indexing reference.

### Validate filtering edge cases

Correct behavior covers descending `min`/`max`, numeric range intersections,
unresolved static rows, static-column SAI queries, composite map filters,
repaired intersection matches, and reads after column deletion. Use targeted
regression tests when an application depends on these cases.

## Storage quick reference

### Size compaction using compressed estimates

Free-space admission checks use each table's estimated compressed size. Unified
Compaction also validates minimum and target size combinations. Review disk
headroom and reject invalid compaction settings before rollout.

### Preserve deletion semantics

Complex collection deletions, reconciliation-required deletions, deterministic
TTL updates, and expired-row index notifications all avoid earlier data or index
divergence paths. Do not recreate older client-side workarounds that discard
tombstone or reconciliation information.

### Handle damaged or legacy storage safely

Compaction marks corrupt SSTables suspected and releases buffer-pool resources;
commitlog recovery skips CRC-damaged sync blocks correctly. Legacy Bloom-filter
SSTables fall back from zero-copy streaming, and pre-table-ID snapshot schemas
can be loaded.

## Configuration and tooling quick reference

### Validate configuration before startup

Audit logging options are sanitized and validated during startup. The default
YAML's optional settings remain parseable when uncommented, and reflectively
loaded extensions are type-checked before initialization.

Batchlog endpoint selection accepts `random_remote`, `prefer_local`,
`dynamic_remote`, and `dynamic`.

```yaml
batchlog_endpoint_strategy: dynamic_remote
```

### Use supported runtimes and build paths

The server fully supports Java 17. `cqlsh` supports Python 3.12 and 3.13,
`cassandra-stress` negotiates TLS 1.3 automatically, source distributions build
with `ant artifacts`, and documentation generation does not require Go.

```shell
ant artifacts
```

### Use current writer capabilities

`CQLSSTableWriter` can notify clients when it emits an SSTable, choose BTI or
Big format, and serialize vectors containing `date` or `time` values. Choose
formats deliberately and attach production callbacks before bulk generation.
