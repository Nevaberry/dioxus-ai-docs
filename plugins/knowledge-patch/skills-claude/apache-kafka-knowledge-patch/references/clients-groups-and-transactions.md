# Clients, Groups, and Transactions

Use this reference when migrating producer, consumer, Admin, and group-management code or adopting consumer and share-group protocols.

## Common client API removals

Apply these source migrations: (4.0-upgrade)

- Replace removed `DescribeLogDirsResponse.LogDirInfo` and `DescribeLogDirsResponse.ReplicaInfo` uses with `DescribeLogDirsResult.descriptions()` or `allDescriptions()`.
- Catch `NotLeaderOrFollowerException`; `NotLeaderForPartitionException` was removed.
- Stop configuring removed `DefaultPartitioner` and `UniformStickyPartitioner` classes.
- Remove implementations of the deleted `Partitioner.onNewBatch()` callback.

Kafka 4.0 clients can proactively rebootstrap if metadata has not updated within a configured timeout, and brokers can tell a client explicitly that rebootstrap is necessary. Configure this path where stale metadata could otherwise strand a client while some known brokers remain reachable. (4.0.0)

## Producer defaults and callback safety

The producer default for `linger.ms` is `5` rather than `0`; reevaluate latency-sensitive configurations and tests. Idempotence no longer silently falls back when `max.in.flight.requests.per.connection` exceeds `5`, so fix invalid combinations instead of expecting degraded behavior. (4.0-upgrade)

`KafkaProducer.flush()` detects its callback deadlock hazard and is forbidden within producer callbacks. Return from the callback without flushing. (4.1-upgrade)

Replace the misspelled constant `PARTITIONER_ADPATIVE_PARTITIONING_ENABLE_CONFIG` with `PARTITIONER_ADAPTIVE_PARTITIONING_ENABLE_CONFIG`; the former is deprecated for removal. (4.2-upgrade)

## Transaction handling and inspection

The overload `sendOffsetsToTransaction(..., String consumerGroupId)` was removed. Use the overload that carries consumer group metadata. (4.0-upgrade)

Abort a transaction on either `TimeoutException` or `TransactionAbortableException`. Retrying the same transaction can create duplicates. With the strengthened transaction protocol finalized for 4.0, producers increment the producer epoch for every transaction; this protocol behavior itself is downgrade-safe. (4.0-upgrade)

The ListTransactions API accepts a transactional-ID pattern filter, avoiding a complete listing followed by client-side filtering. (4.1.0)

`WriteTxnMarkersRequest` carries a `TransactionVersion` field. Transaction Version 2 markers can therefore enforce stricter producer-epoch validation. (4.2.0)

## Consumer API migration

Replace removed and deprecated calls as follows: (4.0-upgrade)

- `Consumer.poll(long)` becomes `poll(Duration)`. The duration overload does not wait beyond its timeout for initial partition assignment, so code that relied on the old overrun needs an explicit assignment strategy.
- Single-partition `committed(TopicPartition)` and `committed(TopicPartition, Duration)` become the `Set<TopicPartition>` overloads.
- `MockConsumer.setException()` becomes `setPollException()`.

Use `Consumer.close(CloseOptions)` to choose whether closing explicitly leaves the group. `Consumer.close(Duration)` is deprecated. This lets runtimes such as Streams control when shutdown triggers a rebalance. (4.1.0)

Each `RecordHeader` within a `ConsumerRecord` may now be read concurrently by multiple threads. The guarantee covers concurrent reads of the individual header object; it does not imply that arbitrary mutation is safe. (4.2-upgrade)

Under the consumer rebalance protocol, rack-topology changes trigger a rebalance so rack-aware assignment can adapt. (4.1.0)

## Admin API migration

### Configs, group state, and offsets

- Replace removed `Admin.alterConfigs()` with `incrementalAlterConfigs()`. (4.0-upgrade)
- A missing group ID passed to `describeConsumerGroups()` now raises `GroupIdNotFoundException` rather than returning a synthetic `DEAD` description. (4.0-upgrade)
- Replace deprecated consumer-specific `ConsumerGroupState` with group-neutral `GroupState`. (4.0-upgrade)
- List offsets with `Admin.listConsumerGroupOffsets(Map<String, ListConsumerGroupOffsetsSpec>, ...)`. (4.0-upgrade)
- Replace `UpdateFeaturesOptions.dryRun` with `validateOnly`; construct `FeatureUpdate` with `UpgradeType` instead of the boolean or `allowDowngrade` API. (4.0-upgrade)

### Topics and result accessors

- Use `DeleteTopicsResult.topicNameValues()`. (4.0-upgrade)
- Use `DescribeTopicsResult.topicNameValues()` and `allTopicNames()` instead of `values()` and `all()`. (4.0-upgrade)
- Construct `DescribeTopicsResult` with both UUID-keyed and name-keyed future maps. (4.0-upgrade)
- Supply a `Uuid` when constructing `TopicListing`. (4.0-upgrade)

### Type-neutral group listing

`Admin.listConsumerGroups()` and its `ListConsumerGroupsOptions` overload are deprecated for removal in the next major release. Select consumer groups through the cross-type API: (4.1-upgrade)

```java
admin.listGroups(ListGroupsOptions.forConsumerGroups());
```

Consumer `MemberDescription` and `ShareMemberDescription` now expose member rack identity through `rackId`. (4.2.0)

## Cross-type group operations

`kafka-groups.sh` lists all group types and protocols in a cluster, avoiding blind spots in older Admin APIs for consumer and share groups. `kafka-consumer-groups.sh` and `kafka-share-groups.sh` expose richer type-specific troubleshooting details. (4.0.0)

Group protocol availability is moving from broker configuration to finalized feature levels. `group.coordinator.rebalance.protocols` is deprecated for removal in Kafka 5.0; use `group.version`, `streams.version`, and `share.version` through `kafka-features.sh`. All protocols are otherwise enabled. (4.3-upgrade)

A consumer started with `group.protocol=classic` now logs a recommendation to adopt the new consumer rebalance protocol ahead of classic protocol deprecation. Treat this as an actionable migration warning. (4.3.0)

## Share groups as work queues

Share groups cooperatively distribute individual records instead of exclusively assigning entire partitions. They support per-record acknowledgement and delivery-attempt counts. Use them for work-queue processing; do not assume consumer-group partition ordering. (4.1-upgrade)

The preview feature was enabled explicitly at level 1:

```sh
kafka-features.sh --bootstrap-server localhost:9092 upgrade --feature share.version=1
```

Share groups are production-ready in 4.2. On a cluster with fewer than three brokers, configure `share.coordinator.state.topic.replication.factor` and `share.coordinator.state.topic.min.isr` before creating the first share group, because `__share_group_state` is created automatically using three-broker defaults. (4.2-upgrade)

## Share fetch, locks, and acknowledgement

`ShareAcquireMode` selects how the maximum fetched-record count is interpreted: (4.2.0)

- `batch_optimized` treats it as a soft limit to preserve batch efficiency.
- `record_limit` enforces it strictly.

In explicit-acknowledgement mode, use acknowledgement type `RENEW` to extend the acquisition-lock timeout for a record that needs longer processing. (4.2.0)

Share groups persist and expose per-partition lag, allowing monitoring of progress and imbalance. (4.2.0)

Kafka 4.3 adds `share.delivery.count.limit`, `share.partition.max.record.locks`, and `share.renew.acknowledge.enable`, with broker-side bounds. These cap delivery attempts and record locks and enable renewal acknowledgements at group level. (4.3-upgrade)
