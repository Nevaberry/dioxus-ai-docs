# Migration and Java APIs

## Flink 2.0 transition (`2.0-migration`)

### Runtime and state compatibility

- Java 8 is unsupported. Java 11 is the minimum, Java 17 is the default and
  recommended runtime, and Java 21 is supported. Recheck Docker images and
  source builds that previously inherited Java 11 or Java 8.
- Built-in serializers for `Map`, `List`, and `Set` are enabled by default and
  Kryo moves to 5.6. State compatibility between Flink 1.x and 2.x is not
  guaranteed; validate snapshots and savepoints rather than assuming restore.
- Flink 2.0 introduces remote primary state storage, asynchronous execution, a
  disaggregated state backend, and SQL operators with parallel async state
  access.

### Removed API families

- The Java DataSet API and Scala DataStream/DataSet APIs are removed. Use Java
  DataStream or Table API/SQL.
- `SourceFunction`, `SinkFunction`, Sink V1, legacy `TableSource`/`TableSink`,
  `TableSchema`, `TableColumn`, and `Types` are removed. Use Source/Sink V2,
  `DynamicTableSource`/`DynamicTableSink`, `Schema`, `Column`, and `DataTypes`.
- Connectors based on `SourceFunction`, `SinkFunction`, or Sink V1 do not work
  with Flink 2.x. Use connector releases explicitly migrated to the new APIs;
  Kafka, Paimon, JDBC, and Elasticsearch were planned first, with remaining
  community connectors migrating by Flink 2.3.
- Removed DataStream conveniences include `addSource(SourceFunction)`,
  `addSink(SinkFunction)`, Sink-V1 `sinkTo`, positional or string `keyBy` and
  `partitionCustom`, iterations, legacy periodic/punctuated watermark
  assignment, `readTextFile`, `writeAsText`, `writeAsCsv`, and
  `DataStreamUtils.collect*`.
- Flink's old `Time` classes and overloads for windows, allowed lateness,
  triggers, and state TTL are removed.

### Configuration and function contexts

- Replace typed legacy `Configuration` methods such as `getInteger` and
  `setLong` with `get(ConfigOption<T>)` and `set(ConfigOption<T>, T)`.
- Environment and `ExecutionConfig` object-style configuration methods are
  removed.
- Replace `RichFunction.open(Configuration)` with `open(OpenContext)`.
- UDFs get serializers, global parameters, and object-reuse facilities directly
  from `RuntimeContext`; they no longer receive the full `ExecutionConfig`.

```java
configuration.set(option, value);
T value = configuration.get(option);
```

### Connector and Table SPI changes

- `DataStreamScanProvider.produceDataStream` and
  `DataStreamSinkProvider.consumeDataStream` use `ProviderContext`.
- Projection pushdown uses `applyProjection(int[][], DataType)`.
- `FunctionDefinitionFactory` creation receives a context.
- Legacy table registration, managed-table, factory, schema, and source/sink
  provider surfaces are removed.

### Pruned state and deployment APIs

- Legacy memory/filesystem state-backend classes, many programmatic
  `CheckpointConfig` and `StreamExecutionEnvironment` setters, and the State
  Processor API savepoint reader/writer surface are removed.
- The simple `JobClient.triggerSavepoint(String)` and
  `stopWithSavepoint(boolean, String)` overloads are removed.
- Per-job deployment and legacy Hybrid Shuffle are removed. Use application
  mode; Kubernetes uses `flink run -t kubernetes-application` rather than the
  removed `run-application` action.

### Configuration-file and option migration

The distribution no longer contains or parses `flink-conf.yaml`. Convert it to
standard-YAML `config.yaml` with the migration tool. Flink 2.0 removes its
documented deprecated option set, including high-impact keys for:

- `state.backend.type`, local recovery, async state, RocksDB checkpoint paths,
  and the ForSt remote directory;
- `pipeline.*` Kryo/POJO registrations;
- `security.ssl.enabled`;
- legacy JobManager and TaskManager heap sizing;
- old web address, web port, and backpressure settings;
- adaptive-batch scheduler tuning;
- old Netty/network and Hybrid Shuffle settings.

Do not merely copy legacy keys into the new YAML file.

### Experimental DataStream API V2

DataStream V2 includes low-level streams, process functions, partitioning,
state, time, and watermark primitives, with window and join extensions. It is
unstable and not recommended for production use.

## Concrete 2.0 API breaks (`2.0.0`)

### Arguments and runtime metadata

- `AbstractParameterTool`, `ParameterTool`, and `MultipleParameterTool` are
  removed from the public Java API. Choose another CLI argument parser.
- `RuntimeContext` no longer exposes direct job ID, task name, subtask index,
  attempt number, current parallelism, or maximum-parallelism getters. Calls to
  `getJobId()`, `getTaskName*()`, `getIndexOfThisSubtask()`,
  `getAttemptNumber()`, and the parallelism getters do not compile unchanged.

### Lifecycle contexts

- Replace `OutputFormat.open(int, int)` with
  `open(OutputFormat.InitializationContext)`.
- Replace `FinalizeOnMaster.finalizeGlobal(int)` with
  `finalizeGlobal(FinalizationContext)`.
- `Sink.InitContext` and `Sink.createWriter(Sink.InitContext)` are removed. Sink
  V2 implementations use `createWriter(WriterInitContext)`.
- The old `Sink.InitContext` constructors on `AsyncSinkWriter` and the old
  `FileSink.createWriter` override are removed with that change.

### Stream, time, and serializer signatures

- Replace `JoinedStreams.WithWindow.with(...)` and
  `CoGroupedStreams.WithWindow.with(...)` with `apply(...)`. The result becomes
  a `SingleOutputStreamOperator`, not a plain `DataStream`.
- `TimeCharacteristic` plus
  `StreamExecutionEnvironment.getStreamTimeCharacteristic()` and
  `setStreamTimeCharacteristic(...)` are removed.
- `TypeSerializerSnapshot.resolveSchemaCompatibility(TypeSerializer<T>)` is
  removed. Resolve compatibility against `TypeSerializerSnapshot<T>`.

### Removed serialization and file-record APIs

The `org.apache.flink.streaming.util.serialization` classes—including its
`SerializationSchema`, `DeserializationSchema`, and `SimpleStringSchema`—are
removed. The legacy Avro row deserializer and CSV/JSON row serialization and
deserialization schemas are also removed, as are `FileRecordFormat` and
`FileSource.forRecordFileFormat(...)`.

### DataStream V2 state return types

`StateManager.getState(...)` returns the corresponding
`org.apache.flink.api.common.state.v2` list, value, map, reducing, or aggregating
state directly, not an `Optional` containing legacy state. Broadcast lookup also
returns `BroadcastState` directly.

## Related compatibility repairs

- Flink 2.2.1 fixes user-provided Scala libraries breaking the Table planner
  (`2.2.1`).
- `ResolvedSchema#getPrimaryKeyIndexes()` reports only physical-column indexes
  in Flink 2.0.1, and `ResolvedSchema` column access no longer fails for a missing
  `getDataType` method in Flink 2.2.1 (`2.0.1`, `2.2.1`).
