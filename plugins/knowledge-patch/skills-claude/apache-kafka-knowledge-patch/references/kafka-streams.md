# Kafka Streams

Use this reference for Streams source migrations, group protocols, exception handlers, state compatibility, header-aware stores, and observability.

## Compatibility floor and removed APIs

Kafka Streams requires brokers 2.1 or later. Exactly-once processing requires brokers 2.5 or later because EOS v1 is no longer supported. (4.0-upgrade)

Deprecated public APIs from Kafka 3.6 or earlier were removed, except for `JoinWindows.of()` and `JoinWindows.grace()`. Major removals include: (4.0-upgrade)

- The old Processor API
- `KStream.through()`
- Transformer and ValueTransformer APIs and suppliers
- `KStream.branch()`
- Old window builders
- `KafkaStreams.setUncaughtExceptionHandler()`

Migrating `transformValues()` to `processValues()` is not a mechanical rename. Follow the dedicated migration guidance and require the critical fix shipped in 4.0.1.

Rename handler configuration keys:

```properties
deserialization.exception.handler=...
production.exception.handler=...
```

The former `default.deserialization.exception.handler` and `default.production.exception.handler` keys are deprecated.

## Processor and topology APIs

Foreign-key KTable joins have Java and Scala overloads that accept a `BiFunction`, allowing the foreign key to be derived from both the input key and value. (4.0-upgrade)

Replace `Topology.AutoOffsetReset` with `org.apache.kafka.streams.AutoOffsetReset` and use the matching methods on `Topology` and `Consumed`. (4.0-upgrade)

A configured `ProcessorWrapper` can inspect or replace every topology processor. `StreamsConfig.PROCESSOR_WRAPPER_CLASS_CONFIG` is applied while the topology is built and is recognized only when the `StreamsBuilder` or `Topology` constructor receives a `TopologyConfig`. (4.0-upgrade)

Kafka Streams can require stable names for every internal changelog topic, repartition topic, and associated state store. Turn on the validation during development or a controlled migration: (4.1-upgrade)

```java
props.put(StreamsConfig.ENSURE_EXPLICIT_INTERNAL_RESOURCE_NAMING_CONFIG, true);
```

Startup fails while any checked internal resource still has an automatically generated name.

## Production exception handling and DLQs

`ProductionExceptionHandler` is invoked for retriable producer `TimeoutException`. The default response is `RETRY`, which can repeat indefinitely. A custom handler may return `CONTINUE` or `FAIL`. (4.0-upgrade)

With `DefaultProductionExceptionHandler`, configure a dead-letter topic to forward records that encounter production exceptions: (4.2-upgrade)

```properties
errors.dead.letter.queue.topic.name=streams-errors
```

A custom production handler must build the DLQ records itself and may ignore this setting.

Migrate handler APIs as follows: (4.2-upgrade)

- `ProductionExceptionHandlerResponse` becomes `ProductionExceptionHandler.Response`.
- `handle` becomes `handleError`.
- `handleSerializationException` becomes `handleSerializationError`.

`ProcessingExceptionHandler` can handle failures from global stores and global KTables in addition to normal tasks. Opt in with: (4.3-upgrade)

```properties
processing.exception.handler.global.enabled=true
```

The configured handler runs on the global thread. DLQ handling is not yet supported on that path.

## Streams rebalance protocol

### Early-access constraints

The broker-driven protocol first requires matching brokers and clients, controller and broker unstable feature support, broker unstable API support, and application opt-in: (4.1-upgrade)

```properties
# controllers and brokers
unstable.feature.versions.enable=true
# brokers
unstable.api.versions.enable=true
# Streams application
group.protocol=streams
```

Use only a new disposable cluster for the early-access form. If storage was formatted with unstable APIs enabled and no explicit metadata version, `streams.version` might already be finalized at `1`; otherwise inspect and enable it:

```sh
kafka-features.sh --bootstrap-server localhost:9092 describe
kafka-features.sh --bootstrap-server localhost:9092 upgrade --feature streams.version=1
```

Do not migrate a classic Streams application to or from the early-access protocol. Use a new `application.id` that has never represented a classic Streams application and is not any consumer `group.id` or share-group ID. Deleting an old consumer group first also deletes its offsets.

Early access rejects static membership through `instance.id`, permits only the sticky assignor, and does not support regex topic subscriptions, offset resets, or significant topology changes. Use a new Streams group for a significant topology change. Interactive Queries remain supported.

### Administration and production readiness

Use `kafka-streams-groups.sh` to list, describe, and delete Streams groups; the Admin client also exposes Streams-specific metadata. Under this protocol, these are group-level settings and are ignored in application client configuration: (4.1-upgrade)

- `streams.session.timeout.ms`
- `streams.heartbeat.interval.ms`
- `streams.num.standby.replicas`

Alter them as group configuration:

```sh
kafka-configs.sh --bootstrap-server localhost:9092 --alter \
  --entity-type groups --entity-name wordcount \
  --add-config streams.num.standby.replicas=1
```

The protocol's core feature set is production-ready in 4.2. Offline classic-to-Streams group migration requires 4.2.1 because 4.2.0 has an unsafe migration defect; newly created Streams groups are unaffected. (4.2-upgrade)

## Thread lifecycle and closing

`KafkaStreams.removeStreamThread()` no longer guarantees that the removed thread's consumer has left its group when the method returns. Removal finishes only after the associated `StreamThread.run()` exits. (4.2-upgrade)

Use top-level `org.apache.kafka.streams.CloseOptions` and `KafkaStreams.close(CloseOptions)` instead of deprecated `KafkaStreams.CloseOptions`. The replacement carries both the close timeout and the leave-group choice. (4.2-upgrade)

Punctuation scheduling can take an explicit start time instead of deriving it from nondeterministic registration time, making schedules reproducible. (4.2-upgrade)

## Serialization and window configuration

`window.size.ms` and `windowed.inner.class.serde` are owned by the TimeWindowed and SessionWindowed serializers and deserializers, not `StreamsConfig`. Configure the SerDes directly. (4.1.0)

## State directory permissions and cleanup

Grant the operating-system group write access to newly created state-store directories with: (4.2-upgrade)

```properties
allow.os.group.write.access=true
```

`state.cleanup.dir.max.age.ms` removes stale local state directories and checkpoint files at startup when their modification age exceeds the configured threshold. (4.3-upgrade)

## Store-managed changelog offsets

Kafka Streams stores changelog offsets in each state store rather than one per-task `.checkpoint` file. Existing checkpoint files migrate automatically at first startup. A custom `StateStore` opts into the behavior with: (4.3-upgrade)

- `managesOffsets()`
- `commit(Map<TopicPartition, Long>)`
- `committedOffset(TopicPartition)`

RocksDB persists the offset when its memtable flushes to an SST file or when the store closes cleanly, not by forcing a flush on every commit. After an unclean exit, a low-traffic store may restart from an offset older than the changelog beginning. Kafka logs `OffsetOutOfRangeException` or `TaskCorruptedException`, reinitializes the task, and fully restores without data loss.

Built-in RocksDB stores use a new `offsets` column family that Kafka Streams 4.2 and older cannot open. An in-place downgrade from 4.3.x is unsupported: stop each instance, clear its local `state.dir`, and restore from changelogs.

The earlier RocksDB 9.7.3 migration can also produce file format 6, unreadable by older Streams releases. Clear and restore local state before downgrading from 4.0.x. Custom RocksDB setters must also migrate removed cache, access-hint, ticker, and logger APIs. (4.0-upgrade)

## Header-aware Processor API stores

Opt-in suppliers and builders end in `WithHeaders`. The provided pairs include: (4.3-upgrade)

- `persistentTimestampedKeyValueStoreWithHeaders` with `timestampedKeyValueStoreWithHeadersBuilder`
- The corresponding persistent timestamped window-store supplier and window-store builder
- `persistentSessionStoreWithHeaders` with `sessionStoreWithHeadersBuilder`

Existing headerless stores do not change. `TopologyTestDriver` and Interactive Queries support the new store types, but existing `store()` facades continue to expose plain values or `ValueAndTimestamp`, not headers.

The changelog wire format is unchanged. Legacy rows return empty headers until rewritten, while RocksDB rows migrate lazily on access. Rolling upgrade is supported; after local data migrates, downgrade requires clearing it and restoring from the changelog.

## Header-aware DSL stores

Select headers globally for supported DSL operators with: (4.3-upgrade)

```java
Properties props = new Properties();
props.put(StreamsConfig.DSL_STORE_FORMAT_CONFIG, "HEADERS");
```

The `dsl.store.format` configuration accepts `DEFAULT` or `HEADERS`. The `DslStoreFormat` API enum instead has `PLAIN`, `TIMESTAMPED`, and `HEADERS`; it does not define `DslStoreFormat.DEFAULT`.

Select a format per operator with custom `DslStoreSuppliers` passed to `Materialized.withStoreType(...)`, or pass explicit header-aware suppliers. Boolean timestamp constructors and accessors on the DSL store parameter types are deprecated.

Header propagation is intentionally limited:

- Aggregations, KTable-KTable joins, materialized `KTable.mapValues`, `KStream.toTable()`, and `StreamsBuilder.table()` store empty headers.
- Stream-stream joins retain source headers but do not merge result headers.
- `suppress()` buffers and left/outer stream-stream join buffers lose headers.

## Streams metrics

The broker-side client metrics plugin can collect Streams runtime metrics. Numeric `INFO`-level forms represent values that collection cannot encode as strings, while a thread-level string form remains available through JMX. The global consumer instance ID is the global stream-thread name plus `-global-consumer`, not only the thread name. (4.0-upgrade)

For the Streams rebalance protocol, monitor these thread-level metrics: (4.2-upgrade)

- `tasks-revoked-latency-avg` and `tasks-revoked-latency-max`
- `tasks-assigned-latency-avg` and `tasks-assigned-latency-max`
- `tasks-lost-latency-avg` and `tasks-lost-latency-max`

They are populated only under that protocol. Use them in place of consumer rebalance-listener metrics, and expect the `client-state` metric to carry an `application-id` tag.

Thread `commit-ratio`, `process-ratio`, `punctuate-ratio`, and `poll-ratio`, plus state-updater `active-restore-ratio`, `standby-restore-ratio`, `idle-ratio`, and `checkpoint-ratio`, now mean action time divided by total elapsed time over the rolling measurement window. `metrics.sample.window.ms` and `metrics.num.samples` determine the effective window. (4.3-upgrade)

Kafka Streams exposes the number of keys in in-memory state stores. The `Bytes` utility is also a public, documented Streams API. (4.3.0)

## Deprecations to remove before Kafka 5.0

Kafka 4.0 deprecates these public or exposed types and fields: (4.0-upgrade)

- `MockProcessorContext`
- Transformer and ValueTransformer types and suppliers
- `ForeachProcessor`
- Leaking `Joined` getters
- Public internal config-description variables
- `DUMMY_THREAD_INDEX`
- StreamsResetter `intermediateTopicsOption`

`org.apache.kafka.streams.errors.BrokerNotFoundException` is also deprecated for next-major removal. (4.2-upgrade)

The `kafka-streams-scala` library and `org.apache.kafka.streams.scala` package are deprecated and will be removed in Kafka 5.0. Migrate to the Java Streams API. (4.3-upgrade)
