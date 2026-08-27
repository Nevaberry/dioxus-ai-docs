# Storage Formats and File I/O

## Default values in readers

Parquet and Avro readers apply Iceberg default values when materializing the
Iceberg data model as of 1.8.0. Spark and Flink Parquet reads support those
defaults. The Flink Avro path adds default-value support in 1.9.0.

Reader implementations must distinguish a missing field that receives a
default from an explicitly present null.

## Variant storage

Iceberg 1.9.0 supports Variant across these storage paths:

- Read and write in Parquet.
- Avro representation as a logical type.
- ORC generic handling.
- Inclusion in Parquet metrics.

Parquet uses the Variant logical annotation from Parquet 1.16.0 starting with
Iceberg 1.10.0.

In 1.11.0, `Parquet.DataWriteBuilder.variantShreddingFunc()` configures Variant
shredding for generic Parquet writes.

## Timestamp, unknown, UUID, and literal handling

Core and generic data models add nanosecond-timestamp and unknown-type support
in 1.9.0. Parquet and ORC paths support the corresponding representations.
Flink Avro and Parquet support `timestamp(9)` and unknown values.

In 1.10.0, Arrow-backed Parquet readers add nanosecond-timestamp support, and
Spark reads dictionary-encoded UUID values.

The `1.11.0-guides` Flink Avro and Parquet readers and writers add UUID
support. Iceberg 1.11.0 core readers accept Avro's `timestamp-millis` logical
type.

`StringLiteral` can convert to fixed-length binary and binary values in
1.11.0.

## Vectorized Parquet reads

The Arrow-backed Parquet readers add v2, `DELTA_BINARY_PACKED`, and
nanosecond-timestamp support in 1.10.0.

Iceberg 1.11.0 adds vectorized support for:

- `DELTA_LENGTH_BYTE_ARRAY`
- `DELTA_BYTE_ARRAY`
- `BYTE_STREAM_SPLIT`

Test the actual encoding mix produced by writers; support for one delta
encoding does not imply support for all of them in an older runtime.

## Parquet writer and statistics controls

In 1.10.0, a table property can use a column prefix to enable Parquet column
statistics for selected columns.

In 1.11.0, `write.parquet.page-version` selects the Parquet page version for
writers.

Metrics lower and upper bounds retain their original value type as of 1.10.0,
including the clarified bound semantics for special geo objects.

## Pluggable File Format API

The `1.11.0-guides` File Format API uses `FormatModel` to describe a format's
identifier, readers, writers, configuration, and capabilities.
`FormatModelRegistry` decouples engines from Parquet, ORC, Avro, Arrow, and
future registered implementations.

Core entry points include:

```java
FormatModelRegistry.register(FormatModel)
FormatModelRegistry.readBuilder(fileFormat, clazz, inputFile)
FormatModelRegistry.dataWriteBuilder(fileFormat, clazz, outputFile)
FormatModelRegistry.equalityDeleteWriteBuilder(fileFormat, clazz, outputFile)
FormatModelRegistry.positionDeleteWriteBuilder(fileFormat, clazz, outputFile)
```

The API and generic-engine integrations are complete in this guidance, but the
compatibility test kit is still in progress. Do not treat registration alone
as proof that a third-party format passes every compatibility case.

## ADLS paths

`ADLSFileIO` supports locations using the WASB scheme as of 1.8.0.

Azure access-token authentication is configured with `adls.token` in 1.10.0.
Custom token-credential providers are supported in the
`1.11.0-guides` behavior.

## S3 and GCS credentials

AWS and GCP support multiple storage-credential prefixes in 1.10.0. This lets
one integration resolve credentials for more than one storage scope.

Long-running `S3FileIO` and `GCSFileIO` instances refresh held storage
credentials on a schedule in 1.11.0. Credential providers must remain usable
after startup and support scheduled replacement.

## Encryption effects on storage

In the `1.11.0-guides` encryption behavior, manifest lists are encrypted as
well as table data/metadata paths, and key-encryption keys can rotate
automatically. File-copy or path-rewrite tooling must carry encrypted manifest
artifacts without assuming their contents are plaintext.

