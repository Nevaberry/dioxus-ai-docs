# Connectors, Formats, and Python

Use this reference when implementing connectors and formats, migrating source
or sink APIs, tuning asynchronous I/O, or operating PyFlink environments.

Batch attribution: `2.0-migration`, `2.0.0`, `2.1-migration`, `1.20.3`,
`2.0.1`, `2.2-migration`, `1.20.4`, `2.0.2`, `2.1.3`, `2.3-migration`.

## Source and sink API migration

- SourceFunction, SinkFunction, Sink V1, legacy table sources/sinks, and their
  connector implementations do not run on 2.x. Choose connector releases
  migrated to Source/Sink V2 and dynamic table interfaces.
- `DataStreamScanProvider.produceDataStream` and
  `DataStreamSinkProvider.consumeDataStream` receive `ProviderContext`.
- Sink V2 creates writers with `WriterInitContext`, not `Sink.InitContext`.
  Update custom sinks, `AsyncSinkWriter` construction, and old
  `FileSink.createWriter` overrides.
- Custom output formats open with `OutputFormat.InitializationContext`, and
  master finalization receives `FinalizationContext`.
- Expanded sink topology disables unaligned checkpoints on internal
  pre-commit, commit, and post-commit connections so checkpoint-complete
  notification sees all committables. Do not generalize that rule to unrelated
  connections.

## Lookup, async, and rate-limited I/O

- Lookup connectors can request desired input distribution or partitioning
  from the planner, improving cache locality.
- Async lookup joins can preserve per-upsert-key changelog order while running
  different keys concurrently.
- Async sinks accept custom batching write strategies instead of only a fixed
  batch policy.
- A user async-function timeout callback no longer triggers unintended retries
  after the 2.0.1 correction.
- Scan Source connectors can integrate a `RateLimiter` to protect constrained
  external systems. This source rate-limiting facility is limited to the
  DataStream API.
- `SplitEnumerator` can see current runtime split distribution and rebalance
  assignments rather than assigning without load information.

## Sink correctness across checkpoints and scaling

- `GlobalCommitterOperator` and `CommitterOperator` retain and commit pending
  committables correctly across checkpoints and writer/committer scaling as of
  1.20.3.
- `SinkWriter` no longer infers end of input during rescaling as of 2.0.1.
- Exactly-once Kafka sinks in State Processor API jobs avoid the affected
  `InvalidPidMappingException` after the 2.0.1 fix.
- When an upsert key conflicts with the sink primary key, use explicit SQL
  `ON CONFLICT` behavior; implicit full-history retention is no longer the
  default.

## Serialization and file formats

- Legacy classes under `org.apache.flink.streaming.util.serialization` are
  removed, including legacy `SerializationSchema`, `DeserializationSchema`,
  and `SimpleStringSchema`.
- Legacy Avro row deserialization and legacy CSV/JSON row
  serialization/deserialization schemas are removed.
- `FileRecordFormat` and `FileSource.forRecordFileFormat(...)` are removed.
- Google Cloud Storage retries the affected HTTP 503 responses as of 2.1.3;
  the earlier GCS library dependency did not retry them.
- The native S3 plugin supplies a recoverable writer for exactly-once sinks;
  see the state/storage reference for installation, schemes, and settings.

## PyFlink compatibility and packaging

- PyFlink 2.1 adds Python 3.12 and removes Python 3.8 support.
- Python DataStream supports async functions with concurrency limits to protect
  external services and retries for transient failures.
- Flat-YAML PyFlink configuration works again in 1.20.3.
- Python CLI arguments work in session mode in 1.20.4.
- PyFlink thread mode can use a shipped `venv.zip` as its virtual environment.
- PyPI source distributions avoid the unsupported hyphenated package naming
  that caused earlier packaging problems.
- `CsvSchemaBuilder.set_null_value(...)` returns `self`, restoring fluent
  builder chaining in 1.20.4.
- `TO_TIMESTAMP_LTZ` accepts dynamic expressions and columns, not only
  literals, after the 2.0.1 fix.
- A missing `pkg_resources` module no longer breaks the affected Python path as
  of 2.0.2.

## HTTP connection behavior

Affected `304 Not Modified` responses include `Connection: close` as of
2.1.3. This prevents reuse of the response connection from poisoning proxy
connection pools.
