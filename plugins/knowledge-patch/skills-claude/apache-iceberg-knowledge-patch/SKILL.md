---
name: apache-iceberg-knowledge-patch
description: Apache Iceberg
version: 1.11.0
license: MIT
metadata:
  author: Nevaberry
---


# Apache Iceberg Knowledge Patch

Use this skill when implementing, reviewing, upgrading, or operating Apache
Iceberg tables and integrations. Start from the project's pinned Iceberg,
engine, and table-format versions. Treat manifests, metadata JSON, catalog
configuration, code, and tests as the authority for the deployment in front of
you.

## How to use this skill

1. Identify the Iceberg library/runtime version, engine version, catalog type,
   file formats, and table format version.
2. Read the compatibility and runtime notes before changing dependencies.
3. Select the reference for the subsystem being changed.
4. Check cross-cutting effects: format-v3 lineage and deletion vectors affect
   readers, rewrites, statistics, and cleanup; encryption affects metadata and
   file I/O; remote planning affects REST authorization and credentials.
5. Preserve the existing table's format and operational invariants unless the
   task explicitly includes a migration.
6. Verify behavior with the actual engine and catalog combination. Features in
   core are not automatically supported by every Spark, Flink, REST, or file-
   format path.

## Reference index

| Reference | Topics |
| --- | --- |
| [compatibility-and-runtime.md](references/compatibility-and-runtime.md) | Java, Spark, Flink, Hadoop, Hive, removed artifacts, API caveats |
| [table-format-types-and-schema.md](references/table-format-types-and-schema.md) | Format v3/v4, row lineage, deletion vectors, Variant, geo, defaults, schema semantics |
| [catalog-rest-and-security.md](references/catalog-rest-and-security.md) | REST protocol, scan planning, catalogs, authentication, encryption, cloud credentials |
| [spark.md](references/spark.md) | Spark procedures, rewrites, metadata columns, streaming, migration, Variant |
| [flink-kafka-and-streaming.md](references/flink-kafka-and-streaming.md) | Flink sources/sinks and maintenance, Kafka Connect ingestion |
| [storage-formats-and-io.md](references/storage-formats-and-io.md) | Parquet, Avro, ORC, Arrow, file-format registry, ADLS and object-store I/O |
| [maintenance-statistics-and-rewrites.md](references/maintenance-statistics-and-rewrites.md) | Expiration, partition/content statistics, rewrite planning, events and metrics |

## Breaking changes and deprecations

### Runtime matrix

- Java 17 is the minimum runtime in the current guidance.
- Spark 3.3 is removed; Spark 3.4 is deprecated. Spark 4.0 and 4.1 have
  dedicated support, but feature availability differs between them.
- Hadoop 2 support is removed.
- Flink 1.18 and 1.19 are removed. Flink 2.0 and 2.1 are supported, with some
  types and features requiring 2.1.
- The old Hive runtime and the Spark-module Comet integration are removed.
  Do not infer that HiveCatalog or all vectorized reading is removed.
- The Open API module no longer publishes a runtime JAR. Depend on the
  appropriate API artifacts instead of that removed artifact.

### Behavioral traps

- Iceberg 1.9.0 reports `unknown` through its version API because of a build
  bug; 1.9.1 fixes it. Do not use that result alone to reject a 1.9.0 runtime.
- Listing a missing Hive namespace now throws `NoSuchNamespaceException`
  instead of returning an empty list.
- Default REST routes do not register namespace, table, or view `HEAD`
  endpoints.
- REST retry behavior is status- and idempotency-sensitive. Do not wrap all
  failures in an unconditional retry loop.
- Spark streaming's `maxRecordPerMicrobatch` is a soft target, not a strict
  maximum.
- Spark rejects bucketed-table migration and overlapping snapshot-table
  locations rather than attempting unsafe conversions.
- Position-delete files that embed deleted row data are deprecated. New
  writers should not depend on row payloads in position deletes.

## Format v3 quick reference

### Row lineage is mandatory

Format-v3 tables always have row lineage enabled, including tables upgraded to
v3. There is no opt-in REST metadata update in later behavior.

- Readers may expose `_row_id` and `_last_updated_sequence_number`.
- Rewriters and compactors must preserve lineage.
- Equality deletes may coexist with lineage under the format rules.
- Metadata uses the current lineage field IDs and snapshots can carry
  `added-rows`.
- A null `current-snapshot-id` is valid in v3-and-later table metadata.

When debugging missing lineage, inspect the table format version, engine read
path, and whether an intermediate rewrite preserved the fields.

### Deletion vectors

Deletion vectors are a format-v3 delete representation, not an isolated Spark
optimization.

- Core supports reads and writes; AWS and Spark write paths also support them.
- Spark exposes them through the `position_deletes` metadata table and can
  migrate format-v2 deletes into format-v3 deletion vectors.
- Writers must follow lifecycle requirements that prevent orphaned vectors.
- Data-file rewrites must propagate live vectors and remove dangling ones.
- Cleanup and partition statistics must account for affected data files.

Do not copy, rewrite, or expire files independently of their deletion-vector
relationships.

## Types and schema quick reference

- Variant is supported by the type and expression APIs and by multiple storage
  formats. Engine support is narrower: confirm both read and write paths, and
  configure shredding where applicable.
- Geometry/geography, geospatial bounding boxes, and `INTERSECTS` enable
  spatial pruning, but metrics-bound semantics for special geo objects must be
  preserved.
- Nanosecond timestamps and unknown values have dedicated type support. Check
  the exact engine/file-format path before assuming round-trip support.
- A required child below an optional struct can still produce null when the
  parent is absent. Do not map it to a globally non-null consumer field.
- Readers can apply Iceberg defaults, and schema evolution can assign them,
  but Spark `ADD COLUMN ... DEFAULT` remains unsupported.
- Default values must not conflict with struct fields.

## REST catalog quick reference

### Safe reads and mutations

- Revalidate cached metadata with ETags and handle `304 Not Modified`.
- Use the ETag returned by commit responses to detect concurrent changes.
- Supply `Idempotency-Key` for retryable creates, commits, and drops so a
  repeated request does not apply a mutation twice.
- Treat `404` from `/v1/config` as a nonexistent warehouse.

### Remote planning

REST catalogs can plan ordinary, incremental, and metadata-table scans.
`LoadTableResult` can advertise `scan-planning-mode`; tables can opt out of
catalog-level planning. When requesting `include-credentials`, keep returned
storage credentials scoped to the planned work and its authorization context.

### Client configuration

Account for HTTP user agent, TLS, proxy, authentication refresh, optional token
exchange, and cross-region S3 settings. Remote services can advertise a
namespace separator, return `referenced-by` dependencies, and expose S3 signing
through the main protocol specification.

## Spark quick reference

- `RewriteTablePath` rewrites table paths and also rewrites partition-
  statistics files. Incremental rewrites can filter content by snapshot ID.
- `ComputeTableStats` computes table statistics; partition statistics also
  have an action and procedure.
- Core rewrite work can separate planning from execution and cap file counts.
  Spark adds case-sensitive filters, delete-ratio controls, and branch
  targeting to its rewrite workflow.
- `rewrite_manifests` supports custom partition ordering and a `sort_by`
  parameter.
- Remove-orphan-files can stream results instead of collecting one response.
- Spark 4.0/4.1 can write shredded Variant values; both expose adaptive split-
  sizing session configuration.
- Spark 4.1 manifest metadata tables expose key metadata.

Before running a procedure, check whether it is table-, snapshot-, or branch-
scoped and whether it rewrites auxiliary statistics or deletion vectors.

## Flink and ingestion quick reference

- Flink's Dynamic Sink evolves schema and partitions, fans out across tables,
  and can create tables. It also supports deletion vectors, column drops,
  case-insensitive matching, SQL options, and post-commit maintenance.
- The v2 sink derives default parallelism from the input stream and supports
  compaction, rewrites, and range distribution.
- Maintenance supports coordinator/ZooKeeper locking, branch selection,
  dynamic filters, snapshot expiration, and orphan-file deletion.
- Stable writer identities can use `uid-suffix` to avoid UID hash collisions.
- Kafka Connect supports Debezium and AWS DMS transforms, configurable control-
  group and transactional-ID prefixes, Variant ingestion, and table-UUID
  validation at commit time.

## Encryption and credentials quick reference

- Table metadata can carry encryption keys; key-management clients exist for
  AWS, Azure, and GCP paths.
- Hive tables can enable encryption with a table master-key property. Manifest
  lists are encrypted too, key-encryption keys can rotate, and metadata
  integrity is validated.
- Use `encryption.kms-type` to select the KMS integration and configure any
  provider-specific endpoint, token, impersonation, or credential-key option.
- Long-lived `S3FileIO` and `GCSFileIO` instances refresh held storage
  credentials on a schedule. Design custom providers for repeated refresh,
  not one-time startup credentials.

## Review checklist

- Confirm library, engine, catalog, table-format, and file-format versions.
- Check every writer/reader pair for the types and encodings in use.
- Preserve row lineage and deletion-vector relationships during rewrites.
- Include metadata, manifests, statistics, and encryption material in path or
  storage migrations.
- Make REST mutations idempotent and concurrency-aware.
- Scope maintenance to the intended snapshot, branch, and table.
- Check cleanup mode before expiration or orphan deletion.
- Verify cloud credential precedence and refresh behavior.
- Exercise the real catalog and engine path in tests; core capability alone is
  not proof of integration support.
