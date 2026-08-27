# Migration, APIs, and Configuration

Use this reference for 1.x-to-2.x upgrades, compilation failures, configuration
conversion, and custom extension migration.

Batch attribution: `2.0-migration`, `2.0.0`.

## Runtime and configuration prerequisites

- Replace `flink-conf.yaml` with standard-YAML `config.yaml`. The 2.x
  distribution neither ships nor parses the legacy file; use the supplied
  migration tool rather than renaming an old nonstandard file blindly.
- Java 8 is unsupported. Java 11 is the minimum, Java 17 is the default and
  recommended runtime, and Java 21 is supported. Recheck Docker bases and
  source-build toolchains because their default changes with the distribution.
- Replace legacy typed `Configuration` accessors such as `getInteger` and
  `setLong` with `get(ConfigOption<T>)` and `set(ConfigOption<T>, T)`.
- Environment and `ExecutionConfig` object-style configuration methods are
  removed. `RichFunction.open(Configuration)` becomes `open(OpenContext)`;
  obtain serializer, global parameters, and object-reuse facilities directly
  from `RuntimeContext`.
- Do not carry forward removed options. High-impact removals cover
  `state.backend.type`, `state.backend.local-recovery`, `state.backend.async`,
  `state.backend.rocksdb.checkpointdir`, `state.backend.forst.remote-dir`,
  `pipeline.*` Kryo/POJO registration, `security.ssl.enabled`, legacy
  JobManager/TaskManager heap settings, old web address/port/backpressure
  settings, adaptive-batch controls, legacy Netty/network controls, and Hybrid
  Shuffle controls.

## API families removed in 2.0

### Batch, streaming, and table surfaces

- Java DataSet and Scala DataStream/DataSet are removed. Migrate to Java
  DataStream or Table API/SQL.
- `SourceFunction`, `SinkFunction`, Sink V1, legacy `TableSource`/`TableSink`,
  `TableSchema`, `TableColumn`, and `Types` are removed. Use Source/Sink V2,
  `DynamicTableSource`/`DynamicTableSink`, `Schema`, `Column`, and `DataTypes`.
- Removed DataStream conveniences include `addSource(SourceFunction)`,
  `addSink(SinkFunction)`, Sink-V1 `sinkTo`, positional/string `keyBy` and
  `partitionCustom`, iterations, legacy periodic/punctuated watermark
  assignment, `readTextFile`, `writeAsText`, `writeAsCsv`, and
  `DataStreamUtils.collect*`.
- Flink `Time` and its window, allowed-lateness, trigger, and state-TTL
  overloads are removed.
- `TimeCharacteristic` and the environment's get/set time-characteristic
  methods are removed; do not retain explicit stream-time selection.
- `AbstractParameterTool`, `ParameterTool`, and `MultipleParameterTool` are no
  longer public API. Replace them with an application-owned argument parser.

### Function and format lifecycles

- `RuntimeContext` no longer exposes direct getters for job ID, task name,
  subtask index, attempt number, current parallelism, or maximum parallelism.
  Calls to `getJobId()`, `getTaskName*()`, `getIndexOfThisSubtask()`,
  `getAttemptNumber()`, and the parallelism getters must be redesigned.
- `OutputFormat.open(int, int)` becomes
  `open(OutputFormat.InitializationContext)`.
- `FinalizeOnMaster.finalizeGlobal(int)` becomes
  `finalizeGlobal(FinalizationContext)`.
- `Sink.createWriter(Sink.InitContext)` becomes
  `createWriter(WriterInitContext)`. `Sink.InitContext`, corresponding
  `AsyncSinkWriter` constructors, and the old `FileSink.createWriter` override
  are removed.
- Windowed `JoinedStreams` and `CoGroupedStreams` replace `with(...)` with
  `apply(...)`; the result is a `SingleOutputStreamOperator`, not a plain
  `DataStream`.

### Serialization and state-facing types

- Kryo moves to 5.6, and new built-in `Map`, `List`, and `Set` serializers are
  enabled by default. State compatibility between 1.x and 2.x is not
  guaranteed; validate restore and migration explicitly.
- Custom serializer snapshots resolve compatibility against another
  `TypeSerializerSnapshot<T>`. The overload taking `TypeSerializer<T>` is
  removed.
- `org.apache.flink.streaming.util.serialization` and its serialization,
  deserialization, and simple-string schemas are removed. The legacy Avro row
  deserializer and legacy CSV/JSON row schemas are also removed.
- `FileRecordFormat` and `FileSource.forRecordFileFormat(...)` are removed.
- DataStream V2 `StateManager.getState(...)` returns the matching V2 list,
  value, map, reducing, or aggregating state directly, not an `Optional` of a
  legacy state. Broadcast state is likewise returned directly.

## Connector and Table SPI migration

- `DataStreamScanProvider.produceDataStream` and
  `DataStreamSinkProvider.consumeDataStream` receive `ProviderContext`.
- Projection pushdown uses `applyProjection(int[][], DataType)`.
- `FunctionDefinitionFactory` creation receives a context.
- Legacy table registration, managed-table, factory, schema, and source/sink
  provider surfaces are removed.
- Connectors built on `SourceFunction`, `SinkFunction`, or Sink V1 do not work
  on 2.x. Obtain a connector release migrated to modern APIs; Kafka, Paimon,
  JDBC, and Elasticsearch were first in the migration plan, with remaining
  community connectors targeted through Flink 2.3.

## Deployment, state, and client removals

- Per-job deployment is removed; SQL Gateway supports application-mode SQL
  execution as its replacement. Kubernetes applications use
  `flink run -t kubernetes-application`, not the removed `run-application`
  action.
- Legacy Hybrid Shuffle is removed.
- Legacy memory/filesystem state backend classes, many programmatic
  `CheckpointConfig` and `StreamExecutionEnvironment` setters, and the State
  Processor API savepoint reader/writer surface are removed.
- The simple `JobClient.triggerSavepoint(String)` and
  `stopWithSavepoint(boolean, String)` overloads are removed.
- `sql-client.sh -u/--update` is removed. Store update statements in a file and
  run `sql-client.sh -f updates.sql`.

## Experimental DataStream V2

Flink 2.0 introduces low-level streams, process functions, partitioning, state,
time, watermark, window, and join primitives under DataStream API V2. The API
is experimental and unstable; do not make it the production migration target
without accepting source-compatibility risk.
