# Upgrades and Runtime Compatibility

Use this reference to select safe maintenance releases, establish upgrade prerequisites, finalize KRaft feature levels, and plan downgrade recovery.

## Release safety fixes

- Prefer Kafka Streams 4.1.1 or later over 4.1.0. Version 4.1.0 has a critical memory leak affecting range scans, session and sliding windows, stream-stream joins, and foreign-key joins; 4.1.1 also fixes a potential data-loss issue. (4.1-upgrade)
- Use at least 4.2.1 when share groups, transactional producers during a rolling upgrade, or offline classic-to-Streams group migration are involved. It fixes a critical share-group deadlock, an `UnsupportedVersionException` rolling-upgrade failure, and the unsafe 4.2.0 offline migration path. Newly created Streams groups are not affected by that migration defect. (4.2-upgrade)
- Prefer Kafka Streams 4.3.1 over 4.3.0. Version 4.3.0 can leak native memory without bound because RocksDB column-family resources are not released during cascading task closes. Version 4.3.1 also fixes stale-offset restart failures and Admin partition-leader operations that can hang after the cached leader leaves. (4.3-upgrade)

## KRaft-only broker upgrade

Kafka brokers no longer support ZooKeeper mode. Migrate a ZooKeeper cluster to KRaft before moving to Kafka 4.x. For the 4.0 transition: (4.0-upgrade)

- Both broker software and the KRaft metadata version must be at least 3.3 before the roll.
- A KRaft cluster older than 3.3 should move to 3.9.x first.
- Supported source broker releases are 3.3.x through 3.9.x.
- Kafka clients, Kafka Streams, and Kafka Connect must be at least 2.1. Verify third-party clients independently.
- Roll brokers one at a time, verify the entire cluster, and only then finalize the release level.

Kafka 4.0 moved KRaft configuration files from `config/kraft` into the common `config` directory. Update packaging, mounts, deployment scripts, and documentation that still refer to the old layout.

## Feature finalization and protocol activation

Finalizing a release is a separate, explicit operation after the rolling binary upgrade:

```sh
bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.0
bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3
```

At the 4.0 finalization boundary: (4.0-upgrade)

- The new group coordinator is active and uses the `group.coordinator.*` tuning namespace.
- The next-generation consumer rebalance protocol is enabled. Once a group uses it, the cluster cannot be downgraded below 3.4.1.
- The strengthened transaction protocol is enabled. A 4.0 producer increments its producer epoch for every transaction; unlike the metadata boundary, this protocol can be safely downgraded.
- Eligible Leader Replicas become available, allowing the KRaft controller to elect a known-safe out-of-ISR replica without data loss.

At the 4.3 finalization boundary, metadata changes make downgrade across the 4.3 level impossible. (4.3-upgrade)

## Metadata downgrade rules

Do not infer downgrade safety only from the current level:

- The 4.0 metadata level contains metadata changes and cannot be downgraded. (4.0-upgrade)
- The 4.2 metadata level adds no metadata changes, so that level is downgrade-compatible by itself. A requested downgrade still fails safety requirements if any metadata version crossed between source and target contains changes. (4.2-upgrade)
- The 4.3 metadata level contains metadata changes and cannot be crossed in a downgrade. (4.3-upgrade)

Kafka exposes generic finalized, minimum-supported, and maximum-supported metrics for every production feature. Use them to spot per-cluster compatibility constraints, and use `describeFeatures --node-id` to inspect one broker during a mixed-version transition. (4.2.0)

## Java and Scala runtime requirements

For the 4.0 runtime transition: (4.0-upgrade)

- Clients and Kafka Streams require Java 11 or later.
- Brokers, Kafka Connect, and Kafka tools require Java 17 or later.
- Java 23 is supported.
- Scala 2.12 is no longer supported.

Kafka 4.2 adds support for Java 25. (4.2.0)

Kafka Connect also adopts Jakarta EE 10 APIs. Integrations compiled against the former Java EE surface need compatibility testing, in addition to the Java 17 runtime change. (4.0.0)

## Log4j2 migration and log compatibility

Kafka has moved from Log4j to Log4j2. Convert existing configurations with `log4j-transform-cli`, and replace the removed `KafkaLog4jAppender` with the Log4j2 Kafka appender. (4.0-upgrade)

Kafka 4.0.0 mistakenly rotates `state-change.log` as `stage-change.log.[date]`. Kafka 4.0.1 restores the expected `state-change.log.[date]` name; account for both spellings in log collection during the transition. (4.0-upgrade)

For custom cleaner logging, replace the `kafka.log.LogCleaner` logger with `org.apache.kafka.storage.internals.log.LogCleaner`, and add both of these logger names to `CleanerAppender`: (4.1-upgrade)

```text
org.apache.kafka.storage.internals.log.LogCleaner$CleanerThread
org.apache.kafka.storage.internals.log.Cleaner
```

## Local state and downgrade recovery

### RocksDB format introduced by Kafka Streams 4.0

Kafka Streams moved RocksDB from 7.9.2 to 9.7.3 and can write file format 6, which older Streams versions cannot read. Before downgrading from 4.0.x: (4.0-upgrade)

1. Stop the application.
2. Delete its local RocksDB state.
3. Start the older version and restore state from changelog topics.

Custom `rocksdb.config.setter` implementations must accommodate removed `AccessHint`, removed compressed-cache methods on `BlockBasedTableConfig`, and removed `TickerType.NO_FILE_CLOSES`. Configure compressed block caches with `setCache()`. `Options.setLogger()` now accepts `LoggerInterface`. Because of the RocksDB change, the Streams `number-open-files` metric reports a constant `-1`.

### Store-owned changelog offsets introduced by Kafka Streams 4.3

Kafka Streams persists changelog offsets within each state store rather than in one per-task `.checkpoint` file. Existing checkpoint files migrate automatically on first startup. Built-in RocksDB stores put the data in an `offsets` column family that Kafka Streams 4.2 and older cannot open. (4.3-upgrade)

For RocksDB, the offset becomes durable when the memtable is flushed to an SST file or the store closes cleanly; every commit does not force a flush. After an unclean exit, a quiet store can restart behind the changelog start offset. Kafka may log `OffsetOutOfRangeException` or `TaskCorruptedException`, reinitialize the task, and perform a full restore without data loss.

An in-place downgrade from 4.3.x is unsupported. Stop each instance, delete its local `state.dir`, and let the older version restore from changelogs.

Header-aware RocksDB stores also migrate data lazily when records are accessed. Rolling upgrade is supported, but once local rows have migrated, downgrade likewise requires clearing local state and restoring it from the changelog. (4.3-upgrade)
