# Table Format, Types, and Schema

## Format v3 row lineage

### Metadata model

Iceberg 1.8.0 adds the `EnableRowLineage` metadata update and the `added-rows`
snapshot field. Core operations can populate the lineage fields, and the row-
lineage field IDs were reassigned in that release.

Starting in 1.9.0, row lineage is enabled and required for every format-v3
table, including a table upgraded to v3. Format v3 also permits equality
deletes with row lineage and defines their interaction. It permits `source-id`,
and core writes a null `current-snapshot-id` for v3-and-later table metadata.

REST lineage fields were added in 1.10.0, while the metadata update that enables
lineage was removed from REST because lineage is always enabled for a format-v3
table. Spark Avro and vectorized Arrow-backed Parquet readers gained lineage
support, Spark 4.0 handles lineage through conditional nullification, and
compaction preserves it.

Flink readers expose `_row_id` and `_last_updated_sequence_number` and preserve
lineage through `RewriteDataFiles` in the `1.11.0-guides` behavior. Any custom
reader or rewriter must preserve the same invariant.

## Deletion vectors

The 1.8.0 specification and core library add deletion-vector reads and writes;
the AWS integration can write them too. Spark can write deletion vectors for
format-v3 tables and exposes them in the `position_deletes` metadata table.

In Iceberg 1.9.0, the Spark integration can rewrite format-v2 deletes into
format-v3 deletion vectors. Its readers expose `_row_id` and
`_last_updated_sequence_number`.

The 1.10.0 specification clarifies the writer requirements that prevent
orphaned deletion vectors:

- Data-file rewrites propagate relevant deletion vectors.
- Rewrites remove dangling deletion vectors.
- Cleanup tracks the affected data files.
- Partition statistics account for deletion vectors.

The Flink Dynamic Sink adds deletion-vector writes in the
`1.11.0-guides` behavior.

## Position deletes

In 1.11.0, position-delete files that embed the deleted row data are
deprecated. New writers should not rely on carrying row values in position
deletes.

## Variant and unknown types

Iceberg 1.8.0 adds `Variant` to the specification and type API. Core can read
and construct its serialized buffers. The type API also adds `UnknownType`.

In 1.9.0:

- The public Variant API adds an extract expression.
- Parquet can read and write Variant values and include them in metrics.
- Avro represents Variant as a logical type.
- ORC generics can handle Variant.
- Core and generic data models support unknown values and nanosecond
  timestamps, with corresponding Parquet and ORC handling.

Spark can read Variant in 1.10.0, and the Spark 4.0 integration can read and
write the unknown type. Flink 2.1 adds Variant and nanosecond-timestamp support
in the `1.11.0-guides` behavior. Kafka Connect can ingest semi-structured JSON
directly into a Variant column. Spark 4.0 and 4.1 can write shredded Variant
values.

Generic Parquet writes can configure Variant shredding with
`Parquet.DataWriteBuilder.variantShreddingFunc()` in 1.11.0.

## Geospatial types and pruning

The 1.9.0 table specification adds a geo type, and core supports geometry and
geography types. In 1.10.0, the specification clarifies lower- and upper-bound
behavior for special geo objects, while metrics retain the original value type
of lower and upper bounds.

The `1.11.0-guides` behavior adds native geospatial bounding-box types and the
`INTERSECTS` predicate. These support spatial partition pruning and file
skipping.

## Defaults and schema evolution

Parquet and Avro readers can apply Iceberg default values as of 1.8.0. Spark
and Flink Parquet reads support them too.

`UpdateSchema` can assign default values while evolving a schema in 1.9.0.
Flink's Avro path also gains default-value support.

In 1.10.0, the table specification prevents struct-field conflicts in default
values. Spark still does not support `ADD COLUMN` with a default value and
reports it as unsupported.

Spark schema conversion supports Iceberg default values in 1.11.0.

## Nullability and literal conversion

In 1.11.0, a required field nested below an optional struct is recognized as
capable of producing null when the optional parent is absent. Schema
converters must not make that child globally non-null.

Also in 1.11.0, `StringLiteral` can convert to fixed-length binary and binary
values.

## Format-v4 foundations

The `1.11.0-guides` batch introduces adaptive metadata-tree foundations for
table format v4:

- `TrackedFile`
- `TrackingInfo`
- `ContentInfo`
- `ManifestStats`
- Their implementations, builders, and partition support

These are foundations, not a reason to assume every engine implements a full
format-v4 workflow.

## Other table-model behavior

A single fast append can add files belonging to multiple partition specs as of
1.8.0. Writers should preserve each file's correct spec association rather
than splitting the append solely because specs differ.

The `1.11.0-guides` SQL UDF specification stores versioned, portable functions
in Iceberg catalogs and permits multiple SQL-dialect representations.
