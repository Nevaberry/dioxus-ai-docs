# Kafka Streams

## API and broker compatibility

Kafka Streams requires brokers 2.1 or later. Exactly-once processing requires
brokers 2.5 or later because EOS v1 is unsupported.

Deprecated public APIs from Kafka 3.6 or earlier were removed, except
`JoinWindows.of()` and `JoinWindows.grace()`. Removed APIs include:

- the old Processor API
- `KStream.through()`
- transformer APIs
- `KStream.branch()`
- old window builders
- `KafkaStreams.setUncaughtExceptionHandler()`

Migrating `transformValues()` to `processValues()` is not a mechanical rename.
Use the dedicated migration behavior and require the critical maintenance fix
included in 4.0.1.

The configuration names `default.deserialization.exception.handler` and
`default.production.exception.handler` are deprecated. Use
`deserialization.exception.handler` and `production.exception.handler`.

`Topology.AutoOffsetReset` is deprecated. Use
`org.apache.kafka.streams.AutoOffsetReset` and the matching current methods on
`Topology` and `Consumed`.

## Processor customization and joins

A configured `ProcessorWrapper` can inspect or replace any topology processor.
`StreamsConfig.PROCESSOR_WRAPPER_CLASS_CONFIG` takes effect while building the
topology and is picked up only by a `StreamsBuilder` or `Topology` constructor
that receives `TopologyConfig`.

Foreign-key KTable joins have Java and Scala overloads accepting a `BiFunction`
that derives the foreign key from both key and value.

## Handler behavior and dead-letter queues

### Production failures

`ProductionExceptionHandler` is invoked for retriable `TimeoutException`.
The default response is `RETRY`. A custom handler can return `CONTINUE` or
`FAIL` to prevent an endless retry cycle.

With `DefaultProductionExceptionHandler`, configure a production dead-letter
queue with:

```properties
errors.dead.letter.queue.topic.name=streams-errors
```

A custom production handler must construct its own DLQ records and may ignore
that setting.

Migrate the handler API as follows:

- `ProductionExceptionHandlerResponse` becomes
  `ProductionExceptionHandler.Response`.
- `handle` becomes `handleError`.
- `handleSerializationException` becomes `handleSerializationError`.

### Global-store failures

`ProcessingExceptionHandler` can handle errors from global stores and global
KTables as well as ordinary stream tasks. Opt in with:

```properties
processing.exception.handler.global.enabled=true
```

The handler runs on the global thread. DLQ handling is not available there.

## Broker-driven rebalance protocol

### Early-access constraints

The initial protocol is disabled by default, requires matching 4.1 brokers and
clients, and should be exercised only on a new disposable cluster. Enable
unstable features on controllers and brokers, unstable APIs on brokers, and
the Streams protocol in the application:

```properties
# controllers and brokers
unstable.feature.versions.enable=true
# brokers
unstable.api.versions.enable=true
# Streams application
group.protocol=streams
```

If storage was formatted with unstable APIs enabled and without an explicit
metadata version, `streams.version` can already be finalized at level 1.
Otherwise inspect and enable it:

```sh
kafka-features.sh --bootstrap-server localhost:9092 describe
kafka-features.sh --bootstrap-server localhost:9092 upgrade --feature streams.version=1
```

In the early-access line, migration between classic and Streams protocols is
unsupported in both directions. Use an `application.id` that has never named a
classic Streams application and is not used by any consumer `group.id` or
share-group ID. Deleting an old consumer group also deletes its offsets.

The early protocol:

- rejects static membership through `instance.id`
- supports only the sticky assignor
- does not support regex topic subscriptions
- does not support offset resets
- does not support significant topology changes
- continues to support Interactive Queries

A significant topology change requires a new streams group.

### Production use and migration

The core protocol is production-ready in 4.2. Offline migration from a classic
group is unsafe on 4.2.0 and requires 4.2.1 or later. Newly created Streams
groups are not affected by that defect.

Use `kafka-streams-groups.sh` to list, describe, and delete streams groups.
Streams-specific group metadata is also available through the Admin client.

Under this protocol, these values are group settings and are ignored in client
configuration:

- `streams.session.timeout.ms`
- `streams.heartbeat.interval.ms`
- `streams.num.standby.replicas`

Alter them through group configuration:

```sh
kafka-configs.sh --bootstrap-server localhost:9092 --alter \
  --entity-type groups --entity-name wordcount \
  --add-config streams.num.standby.replicas=1
```

### Thread lifecycle

`KafkaStreams.removeStreamThread()` does not guarantee that its consumer has
left the group when the call returns. Removal occurs only after the associated
`StreamThread.run()` completes.

## Internal resources and state directory permissions

Enable explicit naming validation to make startup fail if any internal
changelog topic, repartition topic, or associated store still has an
auto-generated name:

```java
props.put(StreamsConfig.ENSURE_EXPLICIT_INTERNAL_RESOURCE_NAMING_CONFIG, true);
```

Allow the operating-system group to write state-store directories created by
Streams with:

```properties
allow.os.group.write.access=true
```

`state.cleanup.dir.max.age.ms` purges local state directories and checkpoint
files at startup when their modification age exceeds the configured limit.

## Close and scheduling APIs

Use top-level `org.apache.kafka.streams.CloseOptions` and
`KafkaStreams.close(CloseOptions)` instead of nested
`KafkaStreams.CloseOptions`. The top-level options control both timeout and
whether the consumer leaves or remains in its group.

Punctuation scheduling can take an explicit start time rather than deriving it
from nondeterministic registration time.

`org.apache.kafka.streams.errors.BrokerNotFoundException` is deprecated for
removal in Kafka 5.0.

## Windowed serialization

`window.size.ms` and `windowed.inner.class.serde` belong to the TimeWindowed
and SessionWindowed serializers and deserializers rather than `StreamsConfig`.

## RocksDB compatibility

### Earlier format transition

Streams moved from RocksDB 7.9.2 to 9.7.3 and may write file format 6, which
older Streams releases cannot read. Before downgrading from 4.0.x, stop the
application, delete local RocksDB state, and let the older version restore
from changelog topics.

Custom `rocksdb.config.setter` implementations must account for:

- removal of `AccessHint`
- removal of compressed-cache methods on `BlockBasedTableConfig`
- removal of `TickerType.NO_FILE_CLOSES`
- use of `setCache()` for compressed block caches
- `Options.setLogger()` accepting `LoggerInterface`

The Streams `number-open-files` metric therefore reports a constant `-1`.

### Store-managed changelog offsets

Streams persists changelog offsets inside each state store instead of one
per-task `.checkpoint` file. Existing checkpoint files migrate automatically
on first startup.

Custom `StateStore` implementations can opt in through:

- `managesOffsets()`
- `commit(Map<TopicPartition, Long>)`
- `committedOffset(TopicPartition)`

For RocksDB stores, an offset becomes durable when the memtable flushes to an
SST file or the store closes cleanly. Kafka does not force a flush for every
commit.

After an unclean exit, a low-traffic store can restart from an offset earlier
than the changelog start. Streams logs `OffsetOutOfRangeException` or
`TaskCorruptedException`, reinitializes the task, and performs a full restore
without data loss.

Built-in RocksDB stores hold these offsets in an `offsets` column family that
Kafka Streams 4.2 and older cannot open. Before downgrading from 4.3.x, stop
each instance, delete its local `state.dir`, and allow the older release to
restore from changelogs. In-place downgrade is unsupported.

## Header-aware state stores

### Processor API stores

Opt-in store suppliers and matching builders end in `WithHeaders`. They
include:

- `persistentTimestampedKeyValueStoreWithHeaders` with
  `timestampedKeyValueStoreWithHeadersBuilder`
- the corresponding window-store supplier and builder
- `persistentSessionStoreWithHeaders` with
  `sessionStoreWithHeadersBuilder`

Headerless stores are unchanged. `TopologyTestDriver` and Interactive Queries
support header-aware stores. Existing `store()` facades still expose a value
or `ValueAndTimestamp`, not headers.

The changelog format is unchanged. Legacy rows return empty headers until
rewritten, and RocksDB data migrates lazily on access. Rolling upgrade is
supported. Once local data has migrated, downgrade requires deleting that
local state and restoring it from the changelog.

### DSL stores

Set the global format for supported DSL operators with:

```java
Properties props = new Properties();
props.put(StreamsConfig.DSL_STORE_FORMAT_CONFIG, "HEADERS");
```

The `dsl.store.format` setting accepts `DEFAULT` or `HEADERS`. The
`DslStoreFormat` API enum contains `PLAIN`, `TIMESTAMPED`, and `HEADERS`; it
does not contain `DslStoreFormat.DEFAULT`.

Choose per-operator behavior with a custom `DslStoreSuppliers` passed to
`Materialized.withStoreType(...)` or with explicit header-aware suppliers.
The older boolean timestamp constructors and accessors on DSL store parameter
types are deprecated.

Current DSL header behavior is operator-specific:

- aggregations write empty headers
- KTable-KTable joins write empty headers
- materialized `KTable.mapValues` writes empty headers
- `KStream.toTable()` and `StreamsBuilder.table()` write empty headers
- stream-stream join stores retain source headers but do not merge result
  headers
- `suppress()` buffers lose headers
- left and outer stream-stream join buffers lose headers

## Observability

### Runtime and identity

The broker-side client metrics plugin can collect Streams runtime metrics.
Numeric `INFO`-level counterparts cover values that cannot be represented as
strings by broker-side collection; a thread-level string metric remains
available through JMX.

The global consumer instance ID is the global stream-thread name plus
`-global-consumer`, rather than only the thread name.

### Rebalance metrics

Streams groups expose these thread-level metrics only under the Streams
rebalance protocol:

- `tasks-revoked-latency-avg` and `tasks-revoked-latency-max`
- `tasks-assigned-latency-avg` and `tasks-assigned-latency-max`
- `tasks-lost-latency-avg` and `tasks-lost-latency-max`

Move monitoring from consumer rebalance-listener metrics to these names after
protocol migration. The `client-state` metric includes an `application-id`
tag.

### Ratio semantics

Thread `commit-ratio`, `process-ratio`, `punctuate-ratio`, and `poll-ratio`
metrics report action time divided by total elapsed time over the rolling
measurement window.

The same semantics apply to state-updater `active-restore-ratio`,
`standby-restore-ratio`, `idle-ratio`, and `checkpoint-ratio`. The effective
window follows `metrics.sample.window.ms` and `metrics.num.samples`.

In-memory state stores expose metrics for the number of keys they hold.

## Deprecation inventory

The 4.0 line newly deprecated:

- `MockProcessorContext`
- Transformer and ValueTransformer types and suppliers
- `ForeachProcessor`
- leaking `Joined` getters
- internal public configuration-description variables
- `DUMMY_THREAD_INDEX`
- StreamsResetter `intermediateTopicsOption`

`kafka-streams-scala` and `org.apache.kafka.streams.scala` are deprecated and
will be removed in Kafka 5.0. Migrate applications to the Java Streams API.

The `Bytes` utility is now a supported public Streams API and appears in the
generated Javadoc.
