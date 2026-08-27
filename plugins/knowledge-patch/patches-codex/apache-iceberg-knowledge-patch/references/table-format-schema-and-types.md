# Table format, schema, and types

Use this reference for format-v3 behavior, deletion vectors, row lineage,
schema evolution, logical types, encryption metadata, and early format-v4
interfaces.

## Deletion vectors

### Read, write, and metadata exposure

Iceberg 1.8.0 adds deletion-vector read and write support to the table
specification and core library. The AWS integration can write them as well.
Spark can write deletion vectors for format-v3 tables and exposes them
through the `position_deletes` metadata table.

Spark can rewrite format-v2 deletes as format-v3 deletion vectors as of
1.9.0. Flink's Dynamic Sink adds deletion-vector writes in the
1.11.0-guides batch.

### Lifecycle invariants

The 1.10.0 specification clarifies write requirements intended to prevent
orphaned deletion vectors:

- Data-file rewrites must propagate applicable deletion vectors and remove
  dangling vectors.
- Cleanup must track the affected data files.
- Partition statistics must account for deletion vectors.

Treat the vector and its referenced data file as one lifecycle relationship
during rewrite, expiration, and orphan cleanup. Do not copy, drop, or rewrite
one side without reconciling the other.

Position-delete files that embed deleted-row data are deprecated in 1.11.0.
New writers should avoid relying on carried row values.

## Row lineage

### Metadata and field IDs

The 1.8.0 specification introduces the `EnableRowLineage` metadata update and
the snapshot `added-rows` field. Core operations can populate the lineage
fields. This update also reassigns the row-lineage field IDs, so implementations
must use the specified IDs rather than early assumptions.

### Format-v3 requirements

As of 1.9.0, row lineage is enabled and required for every format-v3 table,
including a table upgraded to v3. The specification permits equality deletes
with lineage and defines their interaction. Format v3 also permits
`source-id`, and core writes a null `current-snapshot-id` in v3-or-later table
metadata when no current snapshot exists.

The REST lineage contract in 1.10.0 carries the lineage fields but removes the
update for enabling lineage, because v3 tables always have it enabled.

Engine handling includes:

- Spark readers expose `_row_id` and `_last_updated_sequence_number` as of
  1.9.0.
- Spark's Avro and vectorized Arrow-backed Parquet readers handle lineage in
  1.10.0. Spark 4.0 applies conditional nullification and preserves lineage
  through compaction.
- Flink can read both metadata columns and preserve them through
  `RewriteDataFiles` in 1.11.0-guides.

## Variant and unknown types

### Variant

The 1.8.0 specification and type API add `Variant`; core can read and
construct its serialized buffers.

The 1.9.0 public API adds a Variant extract expression. Variant can be read
and written in Parquet, represented as an Avro logical type, handled by ORC
generics, and included in Parquet metrics.

Further integrations include:

- Parquet adopts the Variant logical annotation from Parquet 1.16.0 in
  Iceberg 1.10.0.
- Spark can read Variant values in 1.10.0.
- Spark 4.0 and 4.1 can write shredded Variant data in 1.11.0-guides.
- Flink 2.1 supports Variant in 1.11.0-guides.
- Kafka Connect can ingest semi-structured JSON into Variant columns in
  1.11.0-guides.
- Generic Parquet writes expose
  `Parquet.DataWriteBuilder.variantShreddingFunc()` in 1.11.0.

Reader support, writer support, and shredding support are separate
capabilities; check each path used by a pipeline.

### Unknown values

The type API adds `UnknownType` in 1.8.0. Core and generic data models add
unknown-value support in 1.9.0, with Parquet and ORC handling. Flink Avro and
Parquet paths also handle unknown values. Spark 4.0 can read and write the
unknown type in 1.10.0.

## Time and binary types

Core and generic data models add nanosecond timestamps in 1.9.0, along with
Parquet and ORC support. Flink Avro and Parquet support `timestamp(9)` in that
batch, and Flink 2.1 adds broader nanosecond-timestamp support in
1.11.0-guides.

Core Avro readers accept the `timestamp-millis` logical type as of 1.11.0.
`StringLiteral` can convert to fixed-length binary and binary values as of
1.11.0.

## Geospatial types and predicates

The 1.9.0 table specification adds a geo type, while core adds geometry and
geography types.

The 1.10.0 specification clarifies lower- and upper-bound behavior for special
geo objects. Metrics retain the original value type for lower and upper
bounds; do not normalize away that type when comparing or serializing bounds.

The 1.11.0-guides batch adds native geospatial bounding-box types and the
`INTERSECTS` predicate. Engines can use these for spatial partition pruning
and file skipping.

## Defaults and nullability

Parquet and Avro readers can apply Iceberg data-model defaults as of 1.8.0.
Spark and Flink Parquet reads support them too.

In 1.9.0:

- `UpdateSchema` can assign defaults during schema evolution.
- The Flink Avro path gains default-value support.

In 1.10.0, the table specification avoids struct-field conflicts in default
values. Spark does not support `ADD COLUMN` with a default and reports the
operation as unsupported.

In 1.11.0, Spark schema conversion supports Iceberg defaults. A required field
nested beneath an optional struct is recognized as capable of producing null
when the parent is absent. Schema consumers must propagate parent nullability
rather than treating the nested `required` flag as globally non-null.

## Encryption metadata

The 1.10.0 table and REST specifications add encryption keys and the API adds
table-metadata keys. `KeyManagementClient` implementations are available for
AWS and GCP.

The 1.11.0-guides batch makes table encryption usable through a Hive table
property containing the table master-key ID. Manifest lists are encrypted,
key-encryption keys can rotate automatically, and
`encryption.kms-type` selects AWS, Azure, or GCP KMS. Hive catalogs validate
encrypted-table metadata integrity.

## Format-v4 foundations

The 1.11.0-guides batch introduces `TrackedFile`, `TrackingInfo`,
`ContentInfo`, and `ManifestStats`, along with implementations, builders, and
partition support. These are foundations for an adaptive metadata tree in
table format v4, not a signal to treat every surrounding v4 capability as
complete.

