# Python and Connector Compatibility

## PyFlink runtime and packaging

### Supported Python versions (`2.1-migration`)

PyFlink 2.1 adds Python 3.12 and removes Python 3.8 support. Align CI images,
virtual environments, and cluster workers before changing the Flink runtime.

### Configuration and CLI repairs (`1.20.3`, `1.20.4`)

- Flink 1.20.3 restores flat-YAML configuration in PyFlink.
- Flink 1.20.4 makes Python CLI arguments work in session mode.
- PyFlink thread mode can use a shipped `venv.zip` as its environment.
- PyPI source distributions avoid the unsupported hyphenated naming that caused
  packaging failures.
- `CsvSchemaBuilder.set_null_value(...)` returns `self`, allowing fluent builder
  chaining.

### Expression and dependency repairs

- PyFlink `TO_TIMESTAMP_LTZ` accepts columns and other non-literal expressions
  rather than only literals (`2.0.1`).
- A Flink 2.0.2 Python path no longer raises `ModuleNotFoundError` when
  `pkg_resources` is absent (`2.0.2`).

### Python async functions (`2.2-migration`)

Python DataStream jobs can call external services asynchronously with concurrency
limits and transient-failure retries. Size concurrency to protect the service and
make retry side effects safe.

## Connector API migration (`2.0-migration`)

Connectors based on `SourceFunction`, `SinkFunction`, or Sink V1 do not run on
Flink 2.x. Use versions built for Source/Sink V2. New Kafka, Paimon, JDBC, and
Elasticsearch connector releases were planned immediately after 2.0.0; the
remaining community connector migrations were planned through Flink 2.3.

Connector and Table SPI implementers must also account for:

- `ProviderContext` on `DataStreamScanProvider.produceDataStream` and
  `DataStreamSinkProvider.consumeDataStream`;
- `applyProjection(int[][], DataType)` for projection pushdown;
- a creation context for `FunctionDefinitionFactory`;
- removal of legacy registration, managed-table, factory, schema, and provider
  surfaces.

## Lookup connectors and joins

- Lookup connectors can request planner input distribution or partitioning,
  allowing lookup records to be placed for more effective caching
  (`2.0-migration`).
- Async lookup joins can preserve per-upsert-key changelog order while handling
  different keys concurrently (`2.1-migration`).
- Delta joins support CDC sources without `DELETE`, source-adjacent projections
  and filters, and lookup caching (`2.2-migration`).
- Flink 2.1.2 recognizes indexed join keys and fixes a delta-join lookup-cache
  `ClassCastException` (`2.1.2`).

## Async sinks (`2.1-migration`)

Async sinks can supply pluggable batching write strategies instead of using only
the fixed batching policy. Combine this with the Sink V2
`WriterInitContext` lifecycle described in the migration reference.

## Paimon and materialized tables (`2.0.0`)

Flink SQL can call Paimon compaction and snapshot, branch, or tag maintenance
procedures with named and optional parameters. Paimon is the only catalog that
supports Materialized Tables in Flink 2.0.0.

## Protobuf runtime (`2.2-migration`)

`protobuf-java` moves from 3.21.7 to 4.32.1, corresponding to Protocol Buffers
32. It supports `edition = "2023"` and `edition = "2024"`. Existing proto2 and
proto3 definitions remain compatible. Proto3 optional-field presence no longer
requires `protobuf.read-default-values: true`.
