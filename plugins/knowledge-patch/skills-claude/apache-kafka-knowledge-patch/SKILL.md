---
name: apache-kafka-knowledge-patch
description: Apache Kafka
version: 4.3.0
license: MIT
metadata:
  author: Nevaberry
---


# Apache Kafka Knowledge Patch

Use this skill when upgrading, configuring, extending, or operating Apache Kafka and its clients, Kafka Streams, Kafka Connect, MirrorMaker, KRaft, share groups, or tiered storage. Inspect the project's actual broker, client, metadata, and Java versions before applying version-dependent advice.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrades-and-runtime.md](references/upgrades-and-runtime.md) | Safe release selection, KRaft upgrade gates, feature finalization, metadata downgrade limits, Java and logging migrations |
| [brokers-and-storage.md](references/brokers-and-storage.md) | Broker configuration, ELR, coordinators, KRaft quorum, log cleaning, retention, tiered and remote storage |
| [clients-groups-and-transactions.md](references/clients-groups-and-transactions.md) | Producer, consumer, Admin, transactions, group protocols, share groups, client APIs |
| [kafka-streams.md](references/kafka-streams.md) | Streams migrations, rebalance protocol, handlers, state stores, headers, metrics, RocksDB |
| [connect-and-mirrormaker.md](references/connect-and-mirrormaker.md) | Connect runtime and REST changes, plugin APIs and versions, converters, MirrorMaker 2 |
| [security-observability-and-tools.md](references/security-observability-and-tools.md) | OAuth and SASL, principal builders, JMX and telemetry, metric migrations, CLI option changes |

## Upgrade safety first

### Establish the cluster mode and floor

- Kafka brokers are KRaft-only. Migrate any ZooKeeper cluster before attempting a broker upgrade.
- Do not roll an old KRaft cluster directly when its software or metadata version is below 3.3. Move it to 3.9.x first.
- Before a 4.0 broker roll, require Kafka clients, Streams, and Connect at 2.1 or later; exactly-once Streams workloads require brokers 2.5 or later.
- Verify non-Apache client compatibility independently.
- Brokers, Connect, and Kafka tools require Java 17; clients and Streams require Java 11. Java 25 is supported by Kafka 4.2.

### Prefer fixed maintenance releases

- Avoid Kafka Streams 4.1.0 because range scans, windows, and joins can leak memory; use 4.1.1 or later.
- Use at least 4.2.1 for share-group deadlock fixes, transactional rolling-upgrade safety, and offline classic-to-Streams group migration.
- Avoid Kafka Streams 4.3.0 because cascading task closes can leak RocksDB column-family resources; use 4.3.1 or later.

### Finalize deliberately

After rolling every broker and validating cluster health, finalize the intended release:

```sh
bin/kafka-features.sh --bootstrap-server localhost:9092 upgrade --release-version 4.3
```

- Do not assume rolling new binaries changes every protocol. Feature finalization activates metadata and protocol behavior.
- Metadata downgrade is impossible across feature levels that contain metadata changes, including 4.0 and 4.3.
- The 4.2 metadata level itself contains no metadata changes, but downgrade is safe only if no crossed intermediate level contains them.
- Inspect finalized, minimum-supported, and maximum-supported feature metrics before planning a downgrade.

## Breaking configuration changes

### Broker and common configuration

- Remove `log.message.format.version`, `message.format.version`, `offsets.commit.required.acks`, and `log.message.timestamp.difference.max.ms`.
- Replace the timestamp-difference limit with `log.message.timestamp.before.max.ms` and `log.message.timestamp.after.max.ms`. The latter defaults to one hour and can reject future-dated `CreateTime` records.
- Replace `metrics.jmx.blacklist`/`whitelist` with `metrics.jmx.exclude`/`include`.
- Replace `delegation.token.master.key` with `delegation.token.secret.key`.
- Replace `remote.log.manager.thread.pool.size` with `remote.log.manager.follower.thread.pool.size`.
- Treat LIST settings strictly: null, duplicates, and empty lists may now be rejected or warned about according to each setting.

### Logging and metrics

- Kafka uses Log4j2. Convert old configuration with `log4j-transform-cli` and replace `KafkaLog4jAppender` with the Log4j2 Kafka appender.
- Update custom cleaner logging to the `org.apache.kafka.storage.internals.log` logger names.
- Migrate nanosecond totals to `bufferpool-wait-time-ns-total`, `io-wait-time-ns-total`, and `io-time-ns-total`.
- Prefer AppInfo metrics tagged with `client-id`; the untagged forms are being removed.
- Move monitoring to unchanged consumer topic names rather than dot-to-underscore variants.

## Client migration essentials

### Producer and transactions

- Account for the producer `linger.ms` default of `5`.
- Idempotence no longer silently falls back when `max.in.flight.requests.per.connection` exceeds `5`; fix the configuration.
- Never call `KafkaProducer.flush()` from a producer callback.
- Treat both `TimeoutException` and `TransactionAbortableException` as transaction-abort conditions; do not retry the same transaction and risk duplicates.
- Replace the removed `sendOffsetsToTransaction(..., String consumerGroupId)` overload with the group-metadata form.

### Consumer and Admin

- Replace `Consumer.poll(long)` with `poll(Duration)` and account for its strict timeout during assignment.
- Use set-based `committed(...)` overloads and `MockConsumer.setPollException()`.
- Migrate `Admin.alterConfigs()` to `incrementalAlterConfigs()`.
- Use `GroupState`, type-neutral group listing, UUID-aware topic APIs, and the current result accessor names.
- Prefer `Consumer.close(CloseOptions)`; `close(Duration)` is deprecated.

### Group protocols

- Use `kafka-groups.sh` for cross-type group discovery.
- Treat share groups as record-level cooperative work queues, not ordered partition streams.
- For clusters with fewer than three brokers, set share-state topic replication and minimum ISR before the first share group creates `__share_group_state`.
- Enable protocols through `group.version`, `streams.version`, and `share.version` feature levels; `group.coordinator.rebalance.protocols` is deprecated.
- Plan migration away from the classic consumer rebalance protocol.

## Kafka Streams essentials

### Removed and renamed APIs

- Migrate off the old Processor API, transformers, `KStream.through()`, `KStream.branch()`, old window builders, and the old uncaught-exception handler.
- Follow the dedicated `transformValues()` to `processValues()` migration; it is not a mechanical rename and requires the 4.0.1 fix.
- Use `deserialization.exception.handler` and `production.exception.handler`.
- Use top-level `org.apache.kafka.streams.CloseOptions`.
- Migrate `ProductionExceptionHandlerResponse` to `ProductionExceptionHandler.Response` and the handler methods to `handleError` and `handleSerializationError`.

### Rebalance protocol

- The broker-driven Streams protocol is production-ready in 4.2, but offline migration from classic groups needs 4.2.1.
- Do not reuse an `application.id` that identifies a classic Streams app or another group when testing the early protocol.
- Administer Streams groups with `kafka-streams-groups.sh`; protocol-owned session, heartbeat, and standby settings are group configurations.
- Significant topology changes may require a new Streams group.

### State and downgrade safety

- Before downgrading from 4.0.x after RocksDB format migration, delete local state and restore it from changelogs.
- Kafka Streams 4.3 stores changelog offsets in state stores. RocksDB uses an `offsets` column family that older releases cannot open.
- Before downgrading from 4.3.x, stop each instance, delete its local `state.dir`, and restore from changelogs.
- Header-aware stores are opt-in. A rolling upgrade works, but migrated local data likewise requires clearing before downgrade.

### Exception handling and DLQs

- A `ProductionExceptionHandler` is called for retriable producer timeouts; explicitly choose retry, continue, or fail.
- Configure `errors.dead.letter.queue.topic.name` when using `DefaultProductionExceptionHandler`; custom handlers must build DLQ records themselves.
- Enable global-store processing exception handling with `processing.exception.handler.global.enabled=true`; global-thread DLQ handling is not available.

## Connect and MirrorMaker essentials

- Connect requires Java 17 and Jakarta EE 10-compatible integrations.
- Replace `GET /connectors/{connector}/tasks-config` with `GET /connectors/{connector}/tasks`.
- Use `include`/`exclude` instead of removed `whitelist`/`blacklist` settings.
- Do not override the removed task assignment hooks or single-argument `SourceTask.commitRecord` hook.
- MirrorMaker 1 is removed; use MirrorMaker 2 and brokers that support incremental alter configs.
- Use MirrorMaker `exclude` settings and plan migration to the new metric-name formats.
- Use side-by-side Connect plugin versions for controlled upgrades and rollbacks.

## CLI migration essentials

- Pass `--bootstrap-server` endpoints as one comma-separated value.
- Replace whitelist-style options with `--include` or `--topics-include`.
- Migrate generic `--property`, `--config`, and command-property options to each tool's typed replacement.
- Custom console readers and dump-log decoders must implement the APIs under `org.apache.kafka.tools.api`.
- Use the current formatter packages under `org.apache.kafka.tools.consumer`.
- Treat `kafka-topics --delete-config` as deprecated; `kafka-configs.sh --alter --delete-config` is idempotent for missing keys.

## Operational checks

Before declaring an upgrade complete:

1. Confirm broker software, metadata, and production feature levels on every node.
2. Verify Java runtimes and KRaft-only configuration.
3. Check group coordinators, transaction workloads, client rebootstrap, and rack-aware assignment.
4. Verify remote-log metadata ISR, follower pools, and tiered-storage behavior.
5. Compare metric names, domains, tags, and ratio semantics with dashboards and alerts.
6. Exercise Connect plugins, MirrorMaker replication policy, and custom security callbacks.
7. Restart Streams workloads from both clean and existing local state, then validate restore and downgrade procedures.

Consult the topic references for exact APIs, defaults, limitations, and version-specific attribution before editing production configuration or code.
