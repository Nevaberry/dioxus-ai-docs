# Upgrades and compatibility

This topic guide carries the exact included batch identifiers
`4.0-upgrade`, `4.0.0`, `4.1-upgrade`, `4.1.0`, `4.2-upgrade`, `4.2.0`,
`4.3-upgrade`, and `4.3.0`.

## Rolling upgrade and feature finalization

### KRaft prerequisites

Kafka 4.0 and later brokers are KRaft-only. Migrate ZooKeeper clusters to
KRaft before upgrading. Both the software and metadata versions must be at
least 3.3 before rolling from 3.3.x–3.9.x. Move a KRaft cluster older than 3.3
to 3.9.x first. Clients, Streams applications, and Connect must be at least
2.1; independently verify non-Apache client compatibility.

Roll brokers individually and verify cluster health before finalization:

```sh
bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.0
```

The new group coordinator uses the `group.coordinator` configuration prefix.
Finalizing 4.0 enables the next-generation consumer rebalance protocol. Once a
group uses it, the cluster cannot downgrade below 3.4.1. Finalization also
enables the strengthened transaction protocol, in which 4.0 producers bump the
producer epoch for each transaction; that protocol itself can be downgraded.
Eligible Leader Replicas also become available so the controller can elect
known-safe replicas outside the ISR without data loss.

The 4.0 metadata level changes metadata and cannot be downgraded.

### Later metadata boundaries

The 4.2 metadata level contains no metadata changes, so metadata downgrade is
supported if none of the intermediate metadata versions between the current
and target versions contains changes.

After rolling and verifying 4.3 brokers, finalize explicitly:

```sh
bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3
```

The 4.3 metadata level changes metadata, so metadata cannot be downgraded
across that boundary.

The `describeFeatures` operation accepts optional `--node-id` for per-node
feature discovery during transitions. It reports one broker's supported
features and helps find mixed-node discrepancies.

## Runtime, packaging, and logging

### Java and Scala

Clients and Streams applications require Java 11; brokers, Connect, and tools
require Java 17. Java 23 is supported in the 4.0 line, and Java 25 is supported
starting in 4.2. Scala 2.12 is unsupported.

Kafka Connect's API surface moved from Java EE to Jakarta EE 10 and requires
Java 17. Check integrations coupled to the former API packages.

### Layout and logging

KRaft properties moved from `config/kraft` into the common `config` directory.

Kafka uses Log4j2. Convert existing configuration with `log4j-transform-cli`
and replace the removed `KafkaLog4jAppender` with the Log4j2 Kafka appender.

Kafka 4.0.0 mistakenly rotated `state-change.log` as
`stage-change.log.[date]`; 4.0.1 restores `state-change.log.[date]`.

Custom Log4j2 configurations should replace the `kafka.log.LogCleaner` logger
with `org.apache.kafka.storage.internals.log.LogCleaner` and add both
`org.apache.kafka.storage.internals.log.LogCleaner$CleanerThread` and
`org.apache.kafka.storage.internals.log.Cleaner` to `CleanerAppender`.

## Maintenance-release safety floors

### Streams maintenance releases

Prefer Kafka Streams 4.1.1 or later over 4.1.0. The base release has a critical
memory leak affecting range scans, session and sliding windows, stream-stream
joins, and foreign-key joins; 4.1.1 also fixes possible data loss.

Prefer Kafka Streams 4.3.1 over 4.3.0. The base release can leak RocksDB
column-family resources during cascading task closes and grow native memory
without bound. The maintenance release also fixes stale-offset restart
failure.

Kafka 4.3.1 additionally fixes Admin partition-leader operations that could
hang after the cached leader left the cluster.

### Share groups, transactions, and protocol migration

Kafka 4.2.1 fixes a critical share-group deadlock and a rolling-upgrade failure
that could raise `UnsupportedVersionException` in clusters using transactional
producers.

Offline migration from classic to Streams groups is unsafe on 4.2.0 and is
supported starting with 4.2.1. Newly created Streams groups are unaffected.
The core broker-driven Streams rebalance feature set is production-ready in
4.2, but use the maintenance release for classic-group migration.

## Upgrade audit

Before each rollout:

1. Record broker software, metadata, and finalized feature levels.
2. Verify Java and client floors for brokers, tools, Connect, and applications.
3. Search configurations and launch scripts for removed names and old package
   locations.
4. Compile custom clients, plugins, callbacks, principal builders, remote-log
   implementations, and Streams stores against the target artifacts.
5. Verify internal-topic replication settings against cluster size.
6. Rehearse finalization and rollback, including local Streams state cleanup.
7. Update monitoring for metric renames, tag changes, and domain moves.
8. Roll one broker at a time and verify health before feature finalization.

Do not infer metadata downgrade safety from software downgrade support. Check
every intermediate metadata level, and treat 4.0 and 4.3 finalization as
explicit one-way boundaries.
