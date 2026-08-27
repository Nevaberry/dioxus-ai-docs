---
name: apache-kafka-knowledge-patch
description: Apache Kafka
version: "4.3.0"
license: MIT
metadata:
  author: Nevaberry
---


# Apache Kafka Knowledge Patch

Use this skill when upgrading, configuring, operating, extending, or developing
against Apache Kafka. Start with the breaking-change checks below, then open the
topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrades-and-compatibility.md](references/upgrades-and-compatibility.md) | Rolling upgrades, feature finalization, metadata downgrade boundaries, runtimes, layouts, logging, and release safety fixes |
| [brokers-kraft-and-storage.md](references/brokers-kraft-and-storage.md) | Broker and controller configuration, KRaft, coordinators, log cleaning, retention, remote logs, tiered storage, and log directories |
| [clients-groups-and-security.md](references/clients-groups-and-security.md) | Producer, consumer, Admin, transactions, group protocols, share groups, OAuth, callbacks, and security extensions |
| [streams.md](references/streams.md) | Streams migration, rebalance protocol, state stores, RocksDB, handlers, headers, metrics, testing, and Scala |
| [connect-mirrormaker-and-tools.md](references/connect-mirrormaker-and-tools.md) | Connect APIs and plugins, MirrorMaker, command-line migrations, formatters, decoders, converters, and benchmarks |
| [observability-and-metrics.md](references/observability-and-metrics.md) | JMX renames, metric identity and semantics, plugin telemetry, feature levels, coordinator buffers, and storage visibility |

## Breaking changes first

### Upgrade only from a supported KRaft state

- Kafka brokers no longer support ZooKeeper mode. Migrate to KRaft before the
  broker upgrade.
- Ensure software and metadata versions are at least 3.3. Move older KRaft
  clusters to 3.9.x before proceeding.
- Clients, Streams applications, and Connect must be at least 2.1. Exactly-once
  Streams processing requires brokers 2.5 or later.
- Roll brokers one at a time, verify the cluster, and only then finalize the
  target feature level.
- Finalizing 4.0 or 4.3 crosses a metadata downgrade boundary. Do not promise a
  rollback across either boundary.

### Meet the runtime floor

- Run clients and Streams applications on Java 11 or later.
- Run brokers, Connect, and Kafka tools on Java 17 or later.
- Scala 2.12 is unsupported.
- KRaft configuration files live in the common `config` directory, not
  `config/kraft`.
- Convert Log4j configuration to Log4j2 and replace `KafkaLog4jAppender` with
  the Log4j2 Kafka appender.

### Replace removed broker settings

- Remove `log.message.format.version`, `message.format.version`,
  `offsets.commit.required.acks`, and `log.message.timestamp.difference.max.ms`.
- Replace the timestamp-difference limit with
  `log.message.timestamp.before.max.ms` and
  `log.message.timestamp.after.max.ms`.
- Replace `metrics.jmx.blacklist`/`metrics.jmx.whitelist` with
  `metrics.jmx.exclude`/`metrics.jmx.include`.
- Replace `delegation.token.master.key` with
  `delegation.token.secret.key`.
- Replace `remote.log.manager.thread.pool.size` with
  `remote.log.manager.follower.thread.pool.size`.
- Migrate login-module policy from
  `org.apache.kafka.disallowed.login.modules` to
  `org.apache.kafka.allowed.login.modules`.

### Update client APIs before compiling

- Replace `Consumer.poll(long)` with `poll(Duration)`.
- Replace single-partition `committed(...)` calls with the
  `Set<TopicPartition>` overloads.
- Replace `Admin.alterConfigs()` with `incrementalAlterConfigs()`.
- Use `GroupState` instead of `ConsumerGroupState`.
- Use `NotLeaderOrFollowerException` instead of
  `NotLeaderForPartitionException`.
- Replace removed partitioners rather than depending on
  `DefaultPartitioner`, `UniformStickyPartitioner`, or `onNewBatch()`.
- Use the map-based `listConsumerGroupOffsets` API and the renamed
  topic-result accessors.
- Treat `TimeoutException` and `TransactionAbortableException` as reasons to
  abort a transaction.

### Audit changed defaults

- Producer `linger.ms` defaults to `5`.
- `log.message.timestamp.after.max.ms` defaults to one hour, rejecting records
  farther in the future when using create-time timestamps.
- `segment.bytes` and `log.segment.bytes` have a 1 MB minimum.
- `num.recovery.threads.per.data.dir` defaults to `2`.
- New clusters enable Eligible Leader Replicas by default.
- Group assignment update intervals default to one second.
- `remote.log.metadata.topic.min.isr` defaults to `2`.

### Handle Streams state as a compatibility boundary

- Prefer the first maintenance release when the base release has a documented
  critical Streams defect.
- Before downgrading from a release that changed RocksDB or local state format,
  stop every instance, delete local state, and restore from changelog topics.
- Do not mechanically rename `transformValues()` to `processValues()`; follow
  the migration behavior and require the maintenance fix.
- Move from the old Processor and transformer APIs to the current Processor
  API before upgrading.
- Migrate nested `KafkaStreams.CloseOptions` to the top-level
  `org.apache.kafka.streams.CloseOptions`.
- Plan migration from `kafka-streams-scala` to the Java Streams API before
  Kafka 5.0.

## High-value operational guidance

### Finalize features deliberately

Inspect finalized and supported feature levels on every node during mixed
deployments. Finalize only after all brokers run successfully at the new
software version. Protocol behavior can change at finalization even when the
rolling restart itself appeared uneventful.

The consumer, Streams, and share protocols are governed by `group.version`,
`streams.version`, and `share.version`. Move away from
`group.coordinator.rebalance.protocols`, which is scheduled for removal.

### Size internal topics for small clusters

Before first share-group use on a cluster with fewer than three brokers, set
both of these values; the internal topic is otherwise auto-created with
three-broker assumptions:

```properties
share.coordinator.state.topic.replication.factor=1
share.coordinator.state.topic.min.isr=1
```

### Treat share groups as work queues

Share-group consumers cooperatively process individual records rather than
owning partitions exclusively. Use per-record acknowledgement, delivery
attempts, strict or batch-optimized fetch limits, lock renewal, delivery-count
limits, and record-lock limits according to the workload. Do not assume
consumer-group ordering semantics.

### Keep callbacks non-blocking and transaction-safe

Never call `KafkaProducer.flush()` from a producer callback; the producer now
rejects that deadlock-prone pattern. Return promptly. In transactional code,
abort on abortable or timeout failures instead of retrying the transaction and
risk producing duplicates.

### Configure OAuth endpoints explicitly

Allow token and JWKS endpoints through the
`org.apache.kafka.sasl.oauthbearer.allowed.urls` system property. Its default is
empty. Update callback-handler package names, and choose JWT bearer or client
assertion authentication when the identity provider requires it.

### Use coordinator and remote-log controls intentionally

Bound reusable and append buffers for group and share coordinators, size
background assignment work, and review the one-second assignment intervals.
For remote logs, set the metadata topic minimum ISR, separate metadata Admin
client properties under `remote.log.metadata.admin.`, and use the follower pool
setting instead of the deprecated generic pool.

### Plan log-directory maintenance

Use log-directory cordoning to remove a directory from ordinary placement
workflows before maintenance. With tiered storage, optionally bootstrap a new
follower at the earliest pending-upload offset and query that boundary through
the matching `ListOffsets` timestamp type.

## High-value Streams features

### Choose the rebalance protocol consciously

The broker-driven Streams protocol is production-ready in the appropriate
maintenance line. Migration from classic groups requires the documented safety
fix. Protocol-owned session, heartbeat, and standby-replica settings are group
configuration, not client configuration.

Use a fresh application identity when required, understand which topology
changes are supported, and monitor the Streams-specific task assignment,
revocation, and loss latency metrics after migration.

### Use production exception handling and dead-letter queues

Configure a production DLQ with:

```properties
errors.dead.letter.queue.topic.name=streams-errors
```

Custom production handlers must create DLQ records themselves. Use the current
handler response and method names. Global-store processing handlers require an
explicit opt-in and do not yet support DLQ output.

### Opt in to header-aware stores carefully

Use the `WithHeaders` suppliers and builders for Processor API stores. For
supported DSL stores, set `dsl.store.format=HEADERS` or select store suppliers
per operator. Header propagation is operator-specific; several aggregations,
joins, tables, and buffers currently write empty or dropped headers.

Rolling upgrades are supported, but migrated local data creates a downgrade
boundary. Clear local state before returning to an older release.

### Understand state-store offset durability

Built-in stores can keep changelog offsets inside the store. RocksDB persists
them when the memtable reaches an SST file or on a clean close, not at every
commit. After an unclean low-traffic shutdown, automatic task reinitialization
and full restore can occur without data loss.

## Implementation checklist

1. Determine the broker, metadata, client, Connect, and Streams versions.
2. Open the upgrade reference and identify finalization and downgrade limits.
3. Search configuration for removed, renamed, deprecated, and changed-default
   settings.
4. Compile clients and extensions against the target APIs.
5. Check command invocations and custom tool interfaces.
6. Review local-state and RocksDB downgrade procedures.
7. Update dashboards for renamed metrics, tags, domains, and ratio semantics.
8. Exercise group migrations, transaction abort paths, callbacks, and
   maintenance rollback in a non-production environment.
9. Prefer the documented maintenance release when a base release carries a
   critical correctness, deadlock, or resource-leak fix.
