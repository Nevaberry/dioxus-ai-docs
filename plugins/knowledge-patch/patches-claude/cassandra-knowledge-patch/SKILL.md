---
name: cassandra-knowledge-patch
description: Apache Cassandra
version: "5.0.8"
license: MIT
metadata:
  author: Nevaberry
---


# Apache Cassandra Knowledge Patch

## Purpose

Load this skill when designing, upgrading, operating, or debugging Apache
Cassandra. It concentrates compatibility details that affect CQL, schema,
indexes, storage, repair, topology, configuration, security, observability,
clients, and command-line tooling.

Start from the deployed cluster and application reality:

1. Determine the Cassandra version on every node involved in the change.
2. Check whether the cluster is mixed-version or fully upgraded.
3. Identify the storage format, index implementations, compaction strategy,
   and repair mode in use.
4. Read the topic reference that matches the operation.
5. Validate changes on representative data and with the same management path
   used in production.

Do not infer behavior from configuration templates alone. Runtime state, JMX,
virtual tables, `nodetool`, schema output, and logs may each expose a different
part of the operational picture.

## Reference index

| Reference | Topics |
| --- | --- |
| [Configuration, Security, and Observability](references/configuration-security-observability.md) | YAML, authorizers, guardrails, virtual settings, JMX, logging, runtime support, and security controls |
| [CQL, Schema, Clients, and Tools](references/cql-schema-clients-and-tools.md) | Native protocol, CQL types and DDL, `cqlsh`, `nodetool`, stress tooling, source builds, and `CQLSSTableWriter` |
| [Indexing and Query Correctness](references/indexing-and-query-correctness.md) | SAI, legacy secondary indexes, filtering, tombstones, static columns, ANN, and query reconciliation |
| [Repair, Topology, and Coordination](references/repair-topology-coordination.md) | AutoRepair, Paxos, gossip, hints, bootstrap, batchlog placement, and streaming coordination |
| [Storage, SSTables, and Recovery](references/storage-sstables-and-recovery.md) | Commitlog, compaction, snapshots, SSTable formats, corruption handling, and recovery |

## High-impact compatibility checks

### Tightened security boundaries

- Expect authorization that older maintenance releases accidentally permitted
  on data centers, authorizer paths, or system keyspaces to be rejected.
- A regular user cannot bind an identity to a superuser. Run that provisioning
  step with appropriately privileged credentials.
- Password changes are rate-limited. Rotation automation needs bounded retry
  behavior rather than rapid repeated requests.
- Audit logging configuration is validated during startup. Treat a startup
  rejection as a configuration error instead of assuming the logger will
  ignore malformed settings.
- Grants are supported on the `system_views` and
  `system_virtual_schema` virtual keyspaces when monitoring roles need them.

See [Configuration, Security, and Observability](references/configuration-security-observability.md)
for the complete set of authorization, redaction, and obfuscation changes.

### Automation and CLI changes

- Use `nodetool import -cd` as the short form of `--copy-data`; `-p` conflicts
  and is no longer the short option.
- Do not make tool wrappers depend on incidental sourcing of
  `cassandra-env.sh`; tools skip it when it is unnecessary.
- Treat invalid or filesystem-unsafe table and snapshot names as DDL or command
  validation failures.
- `cqlsh` can disable persistent history, and supported Python runtimes include
  Python 3.12 and 3.13.
- `nodetool getguardrailsconfig` and `setguardrailsconfig` expose guardrail
  configuration through their simplified interfaces.
- Use `nodetool checktokenmetadata` when comparing token metadata with gossip
  endpoint state.

See [CQL, Schema, Clients, and Tools](references/cql-schema-clients-and-tools.md)
for exact tool and client compatibility notes.

### Virtual settings consumers

Consumers of `system_views.settings` must:

- parse complex values as JSON;
- tolerate settings whose keys are not strings;
- expect security-sensitive values to be redacted; and
- handle the restored, broader set of configuration rows.

Do not use the view as a secret-retrieval mechanism. See
[Configuration, Security, and Observability](references/configuration-security-observability.md)
for JMX and metrics changes that often affect the same inventory systems.

### AutoRepair operations

Built-in AutoRepair provides an in-process scheduler with minimum task-duration
control, `preview_repaired` support, disk protection for full repair, and
expected-versus-actual progress reporting for bytes and keyspaces.

Operational constraints matter:

- the scheduler stops when two major Cassandra versions are detected;
- full repair observes disk-protection conditions; and
- `parallel_repair_count` values greater than one are supported without the
  previous ongoing-repair assertion failure.

During a mixed-major upgrade, retain external repair planning because the
built-in scheduler does not continue. See
[Repair, Topology, and Coordination](references/repair-topology-coordination.md).

### SAI and query correctness

When investigating a query result, distinguish index availability from node
availability and distinguish local correctness from distributed
reconciliation:

- built SAI indexes are queryable when a restarted node is marked `UP`;
- writer switches flush active SAI segment builders;
- repair flushes correctly mark non-empty index state;
- static-column queries and their range tombstones reconcile correctly;
- intersection queries preserve repaired and non-indexed matches;
- segmented index components use segment-aware checksum boundaries; and
- ANN execution uses score-ordered iterators.

Legacy secondary indexes take priority when they coexist with SAI on a column.
Empty values remain invalid for non-literal or otherwise incompatible indexed
types. See [Indexing and Query Correctness](references/indexing-and-query-correctness.md).

### Deletions and reconciliation

Correctness fixes cover several distinct deletion paths:

- mutation serialization preserves complex deletions across multiple
  collections;
- `RowFilter` retains deletions needed for result reconciliation;
- Full Query Logging batches support null-value tombstones;
- reading a partition after a column deletion no longer fails with an index
  bounds exception; and
- secondary indexes are notified about rows in fully expired SSTables.

Do not paper over a suspected deletion bug by changing consistency levels or
rebuilding an unrelated index. Identify the affected serialization, filtering,
logging, or compaction path first.

### Storage and recovery safety

- Direct I/O commitlog flushes preserve data safely.
- Commitlog recovery skips sync blocks correctly after CRC errors.
- A corrupt SSTable found during compaction is marked suspected and associated
  buffer-pool resources are released.
- Runtime failures while writing the TOC remain runtime failures rather than
  being reclassified as filesystem errors.
- Memory-mapped trie indexes larger than 2 GiB are readable.
- Early-open BTI range queries return correct results.
- Legacy SSTables with the old Bloom-filter format automatically fall back
  from zero-copy streaming.

See [Storage, SSTables, and Recovery](references/storage-sstables-and-recovery.md)
before changing compaction, streaming, snapshot, or recovery procedures.

## Upgrade and incident workflow

### Before an upgrade

1. Inventory node versions, Java runtime, SSTable formats, indexes, and repair
   scheduling.
2. Review tightened authorization, schema compatibility, configuration
   validation, and tool option changes.
3. Confirm monitoring parsers handle JSON and redacted virtual settings and
   corrected metric values.
4. Exercise mixed-version Paxos, streaming fallback, hints, and repair behavior
   in a staging topology.
5. Verify disk limits against a first-boot node and compaction space estimates
   against compressed table sizes.

### After a restart or bootstrap

1. Confirm gossip endpoint state includes DC, rack, and host ID for
   bootstrapping or gossip-only nodes.
2. Check token metadata consistency with `nodetool checktokenmetadata`.
3. Confirm SAI queryability rather than relying only on node `UP` state.
4. Use the bootstrap-available `StorageService` JMX MBean when automation needs
   management visibility before the node reaches normal state.
5. Check the corrected failure-detector timing if defaults are in use.

### During a correctness incident

1. Record whether the query uses SAI, legacy 2i, static columns, composite map
   filters, numeric ranges, or descending clustering columns.
2. Determine whether repair, reconciliation, tombstones, an early-open SSTable,
   or an SSTable-writer boundary is involved.
3. Preserve evidence from logs, `nodetool tablestats`, schema descriptions,
   and relevant virtual tables.
4. For storage faults, distinguish corruption, checksum, commitlog CRC, and
   TOC write paths before choosing remediation.
5. Do not expect a heap dump for an exception Cassandra handled internally.

## Authoring and review guidance

When proposing Cassandra code or automation:

- keep examples explicit about keyspace, table, consistency, and topology;
- prefer long CLI options in scripts unless the short form is documented;
- treat redacted values as intentionally unavailable;
- account for mixed-version behavior during rolling upgrades;
- avoid assuming node liveness implies index readiness;
- validate CQL type compatibility, especially vectors, UDT clustering keys,
  and `BytesType` schema evolution; and
- test deletion and tombstone semantics with reconciliation and repair in mind.

Use the references as compatibility constraints, then verify the final behavior
against the target cluster, its schema, and its operational configuration.
