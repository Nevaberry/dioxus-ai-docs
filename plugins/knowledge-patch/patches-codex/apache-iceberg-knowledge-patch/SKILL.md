---
name: apache-iceberg-knowledge-patch
description: Apache Iceberg
version: "1.11.0"
license: MIT
metadata:
  author: Nevaberry
---


# Apache Iceberg Compatibility and Feature Guidance

Use this skill when upgrading Apache Iceberg, choosing an engine runtime,
working with table format v3 or early v4 APIs, configuring a REST catalog,
maintaining table metadata, or integrating cloud storage and authentication.

Treat a project's dependency manifest, engine runtime, table format version,
catalog implementation, and deployed behavior as authoritative. Apply only
guidance that is available in the project's Iceberg version.

## Reference index

| Reference | Topics |
| --- | --- |
| [compatibility-and-upgrades](references/compatibility-and-upgrades.md) | Runtime support, removed and deprecated integrations, changed behavior, artifact and API caveats |
| [table-format-schema-and-types](references/table-format-schema-and-types.md) | Row lineage, deletion vectors, Variant, geo types, defaults, encryption metadata, format-v4 foundations |
| [maintenance-statistics-and-io](references/maintenance-statistics-and-io.md) | Snapshot expiration, rewrites, partition/content statistics, Parquet, Avro, file-format APIs |
| [rest-and-catalogs](references/rest-and-catalogs.md) | REST contracts, retries, scan planning, ETags, idempotency, views, UDFs, Hive behavior |
| [spark](references/spark.md) | Spark procedures, metadata columns, streaming, schema evolution, rewrites, runtime-specific features |
| [flink-and-kafka](references/flink-and-kafka.md) | Flink sinks and maintenance, lineage and types, Kafka Connect transforms and safeguards |
| [cloud-storage-and-security](references/cloud-storage-and-security.md) | AWS, Azure, GCP, Aliyun, credentials, KMS, endpoints, proxies, storage schemes |

## Upgrade blockers and removals

Check runtime compatibility before changing dependencies:

- Spark 3.3 support is removed; do not carry its runtime artifact into a newer
  deployment. Spark 3.4 is deprecated where Spark 4.1 support is available.
- Flink 1.18 and 1.19 support are removed in successive updates. Flink 2.0 and
  2.1 integrations are available.
- Java 17 is required by the newest guidance.
- Hadoop 2 support and the Hive runtime are removed.
- The Spark module no longer includes the Apache DataFusion Comet integration.
  Earlier Comet vectorized reads are therefore not a portable upgrade target.
- Deprecated AWS, core, Flink, and Parquet APIs removed at the 1.10 boundary
  must be replaced before upgrading. Deprecated `DynConstructors` and
  `DynMethods` methods are no longer public.
- The Open API module no longer publishes a runtime JAR. Depend on the
  appropriate API or implementation artifact instead.

Also account for changed behavior:

- Listing a missing Hive namespace throws `NoSuchNamespaceException`.
- Spark explicitly rejects migration of bucketed tables.
- Spark rejects `ADD COLUMN` with a default value even though Iceberg schema
  evolution supports defaults.
- Spark's `maxRecordPerMicrobatch` is a soft limit.
- Default REST routes do not register namespace, table, or view `HEAD`
  endpoints.
- Iceberg 1.9.0 reports `unknown` through the version API because of a build
  bug; do not treat that value as proof of an unknown deployed artifact.

See [compatibility-and-upgrades](references/compatibility-and-upgrades.md) for
the exact transition points and additional compatibility checks.

## Format-v3 invariants

For every format-v3 table, including an upgraded table:

1. Treat row lineage as required and always enabled.
2. Preserve `_row_id` and `_last_updated_sequence_number` through reads,
   rewrites, and compaction where the engine supports them.
3. Account for equality-delete interaction with lineage.
4. Permit `source-id` in v3 metadata and expect a null
   `current-snapshot-id` to be serialized for v3 or later metadata when there
   is no current snapshot.
5. Keep deletion vectors attached to their referenced data files throughout
   rewrite and cleanup planning.

Do not emit a lineage-enabling update for a v3 table merely to turn lineage
on. Older metadata introduced `EnableRowLineage` and `added-rows`, but the
later REST contract removes that update for v3 because lineage is mandatory.
Be careful with persisted field IDs because the lineage IDs were reassigned
when the feature was introduced.

New position-delete files should not embed deleted row data; that form is
deprecated. Prefer deletion vectors or position deletes without copied row
values as appropriate for the writer and table format.

See [table-format-schema-and-types](references/table-format-schema-and-types.md)
for deletion-vector lifecycle rules and lineage support by engine.

## Types, defaults, and nullability

- `Variant` is a first-class type with serialized-buffer APIs, expression
  extraction, file-format mappings, metrics, Spark/Flink support, and
  shredding controls. Verify reader and writer support independently.
- `UnknownType` and unknown values are supported in core and selected engine
  and file-format paths.
- Geometry, geography, native bounding boxes, and `INTERSECTS` enable spatial
  pruning, but special geo objects have defined metrics-bound behavior.
- Nanosecond timestamps require matching engine and Parquet, ORC, or Flink
  support. Avro `timestamp-millis` reads remain accepted.
- A required child below an optional struct can still materialize as null
  when its parent is absent. Do not infer global non-nullability from the
  child's required flag.
- Readers can materialize Iceberg defaults, and `UpdateSchema` can assign
  them. Validate engine-specific DDL restrictions before relying on this.

## REST safety defaults

For mutating REST catalog calls:

1. Send an `Idempotency-Key` for retryable commits, creates, and drops.
2. Use table ETags to revalidate cached metadata and to detect concurrent
   changes after commits.
3. Retry only operations and status codes permitted by the configured policy.
   In particular, do not assume 502, 503, or 504 will be retried.
4. Treat storage credentials returned by scan planning as scoped response
   data and refresh or replace them through the configured credential path.

Remote planning can cover ordinary, incremental, and metadata-table scans.
Honor a table's planning-mode override instead of applying the catalog-wide
setting blindly. Servers may also advertise namespace separators, return
dependencies in `referenced-by`, support view registration, and expose
partition-statistics updates.

See [rest-and-catalogs](references/rest-and-catalogs.md) before implementing a
client, server, or proxy.

## Maintenance and rewrite checklist

Before running expiration, compaction, or rewrite work:

- Choose the requested snapshot-expiration cleanup behavior, including
  `cleanExpiredMetadata`, core `cleanupMode`, or Spark
  `cleanupLevel=None`.
- Preserve or deliberately remove deletion vectors with their affected data
  files; avoid orphaning vector files.
- Decide whether partition statistics need incremental refresh or rewriting.
- Apply file-count caps, snapshot filters, branch selection, partition order,
  and executor-cache settings where relevant.
- Validate source and destination locations for snapshot-table operations.
- Stream orphan-removal results when collecting them centrally would be too
  expensive.
- Observe manifest rewrite events, commit metrics, and snapshot-manager
  metrics through the configured reporter.

See [maintenance-statistics-and-io](references/maintenance-statistics-and-io.md)
for core APIs and [spark](references/spark.md) or
[flink-and-kafka](references/flink-and-kafka.md) for engine controls.

## Spark quick reference

Use the built-in actions and procedures instead of reconstructing metadata
operations externally:

- `RewriteTablePath` rewrites table paths and also handles partition-statistics
  files in newer implementations.
- `ComputeTableStats` computes table statistics; partition statistics have
  their own action and procedure.
- `rewrite_data_files` supports filters, branch targeting, format-v2 delete
  migration, and configurable controls.
- `rewrite_manifests` supports custom ordering through `sort_by`.
- `expire_snapshots` and remove-orphan-files expose cleanup and result
  streaming controls.

Spark 4.x adds important format-v3, key-metadata, Variant, unknown-type, and
schema-evolution behavior. Check the precise runtime-specific matrix in
[spark](references/spark.md).

## Flink and Kafka quick reference

Flink's Dynamic Sink can evolve schemas and partitions, route records to
multiple tables, create tables, write deletion vectors, drop columns, and run
post-commit maintenance. Configure locks, branches, filters, operator
identity, parallelism, distribution, and rewrite behavior deliberately.

Kafka Connect can normalize Debezium and AWS DMS records, configure control
consumer-group and transactional-ID prefixes, ingest JSON into Variant, and
validate table UUIDs at commit. UUID validation is a safety boundary against
writing to a replaced table.

## Cloud and encryption checklist

- Configure table encryption with the required table master-key identity and
  select the intended KMS through `encryption.kms-type`.
- Keep manifest lists and metadata integrity in the encryption threat model,
  and allow key-encryption-key rotation.
- Prefer explicitly configured credential providers where precedence rules
  allow them.
- Plan scheduled refresh for long-running `S3FileIO` and `GCSFileIO`.
- Validate cross-region S3, chunked encoding, proxy, KMS endpoint, Azure
  token, GCP impersonation, BigQuery metastore, and Aliyun RRSA settings
  against the deployed provider.

See [cloud-storage-and-security](references/cloud-storage-and-security.md) for
the provider-specific options.

## Working method

When applying this guidance:

1. Identify the exact Iceberg library, engine runtime, catalog, table format,
   file formats, and cloud providers in use.
2. Read the relevant topic references before editing configuration or code.
3. Separate reader capability from writer capability; support is often
   asymmetric.
4. Preserve table-format invariants across every engine and maintenance job.
5. Test REST retries, ETag conflicts, credential refresh, and interrupted
   rewrites rather than checking only the successful path.
6. Verify actual manifests, metadata tables, metrics, and engine results after
   a migration.
