# Clients, groups, transactions, and security

## Common client API migrations

### Removed types and partitioning hooks

`DescribeLogDirsResponse.LogDirInfo` and `ReplicaInfo` are removed. Use
`DescribeLogDirsResult.descriptions()` or `allDescriptions()`.

Use `NotLeaderOrFollowerException` instead of the removed
`NotLeaderForPartitionException`.

`DefaultPartitioner`, `UniformStickyPartitioner`, and
`Partitioner.onNewBatch()` are removed. Use supported partitioning behavior
and interfaces rather than recreating assumptions from those implementations.

## Producers and transactions

### Defaults and idempotence

Producer `linger.ms` defaults to `5` rather than `0`.

Idempotence no longer silently falls back when
`max.in.flight.requests.per.connection` exceeds `5`. Correct the incompatible
configuration instead of expecting a non-idempotent producer.

Replace the misspelled
`PARTITIONER_ADPATIVE_PARTITIONING_ENABLE_CONFIG` constant with
`PARTITIONER_ADAPTIVE_PARTITIONING_ENABLE_CONFIG`; the former is deprecated
for removal in Kafka 5.0.

### Transaction API and error handling

The `sendOffsetsToTransaction(..., String consumerGroupId)` overload is
removed. Use the current group metadata form.

Treat both `TimeoutException` and `TransactionAbortableException` as reasons
to abort. Retrying the transaction can produce duplicates.

`WriteTxnMarkersRequest` contains a `TransactionVersion` field so Transaction
Version 2 markers can enforce stricter epoch validation.

The ListTransactions API accepts a transactional-ID pattern filter. Prefer it
to listing every transaction and filtering locally.

### Callback restriction

`KafkaProducer.flush()` detects the deadlock risk and is prohibited from
inside a producer callback. Callback code must return without flushing.

## Consumers

### Polling and committed offsets

Replace `Consumer.poll(long)` with `poll(Duration)`. The duration overload does
not wait past its timeout for partition assignment, unlike the old overload.

Replace single-partition `committed(TopicPartition[, Duration])` calls with
the `Set<TopicPartition>` overloads.

Replace `MockConsumer.setException()` with `setPollException()`.

### Shutdown and group membership

`Consumer.close(CloseOptions)` lets callers decide whether close explicitly
leaves the consumer group. `Consumer.close(Duration)` is deprecated.

With the consumer rebalance protocol, rack-topology changes trigger a
rebalance so rack-aware assignment can react to the new topology.

Each `RecordHeader` object in a `ConsumerRecord` is safe for concurrent reads.
The guarantee applies to concurrent reads of individual header objects, not
arbitrary mutation.

Starting a consumer with the `classic` rebalance protocol emits a migration
recommendation because that protocol is planned for deprecation.

## Admin client

### Configuration and group-neutral APIs

Replace `Admin.alterConfigs()` with `incrementalAlterConfigs()`.

A missing ID passed to `describeConsumerGroups()` raises
`GroupIdNotFoundException`; it no longer returns a synthetic `DEAD`
description.

Use the group-type-neutral `GroupState` instead of the deprecated
`ConsumerGroupState`.

`Admin.listConsumerGroups()` and its `ListConsumerGroupsOptions` overload are
deprecated for removal in the next major release. Select consumer groups via:

```java
admin.listGroups(ListGroupsOptions.forConsumerGroups());
```

`kafka-groups.sh` lists all cluster groups with their type and protocol,
including consumer and share groups that older Admin usage could miss.
`kafka-consumer-groups.sh` and `kafka-share-groups.sh` provide expanded details
for their own group types.

### Result and request migrations

- Use `DeleteTopicsResult.topicNameValues()`.
- Use `DescribeTopicsResult.topicNameValues()` and `allTopicNames()` instead
  of `values()` and `all()`.
- Construct `DescribeTopicsResult` with both UUID-keyed and name-keyed future
  maps.
- Supply a `Uuid` when constructing `TopicListing`.
- Use
  `Admin.listConsumerGroupOffsets(Map<String, ListConsumerGroupOffsetsSpec>, ...)`.
- Replace `UpdateFeaturesOptions.dryRun` with `validateOnly`.
- Construct `FeatureUpdate` with `UpgradeType` rather than a boolean or
  `allowDowngrade`.

Consumer `MemberDescription` and `ShareMemberDescription` expose member rack
IDs through `rackId`.

`RemoteClusterUtils.translateOffsets()` can translate committed offsets for
multiple consumer groups in one call.

## Metadata recovery

Clients can proactively rebootstrap after metadata remains stale for a
configured timeout, and servers can signal that rebootstrap is required. Use
this facility to avoid a client remaining pinned to stale metadata merely
because one known broker is still reachable.

## Share groups

### Queue semantics and feature enablement

Share groups provide queue-style processing. Consumers cooperate over
individual records rather than exclusively owning partitions, and receive
per-record acknowledgements and delivery-attempt counts. Use them for work
queues, not for ordered stream processing.

In the preview line, explicitly enable the feature:

```sh
kafka-features.sh --bootstrap-server localhost:9092 upgrade --feature share.version=1
```

Share groups are production-ready in 4.2. For clusters with fewer than three
brokers, configure the share state topic replication factor and minimum ISR
before the first share group creates `__share_group_state`; see the broker
reference.

### Fetch limits and lock renewal

Share fetches offer two `ShareAcquireMode` values:

- `batch_optimized` treats the maximum record count as a soft limit.
- `record_limit` enforces the maximum strictly.

In explicit acknowledgement mode, `RENEW` extends acquisition-lock timeouts
for records requiring longer processing.

Share groups persist and expose share-partition lag, allowing monitoring of
progress and imbalance.

The following group-level controls have corresponding broker-side bounds:

- `share.delivery.count.limit`
- `share.partition.max.record.locks`
- `share.renew.acknowledge.enable`

Use them to limit delivery attempts and acquired-record locks and to control
renewal acknowledgements.

## Group protocol control

`group.coordinator.rebalance.protocols` is deprecated for removal in the next
major release. Protocol availability moves entirely to the `group.version`,
`streams.version`, and `share.version` feature levels managed with
`kafka-features.sh`; all protocols are otherwise enabled.

## OAuth and SASL

### Endpoint allowlist and callback packages

Admit OAuth token and JWKS endpoints through the
`org.apache.kafka.sasl.oauthbearer.allowed.urls` system property. Its default
is an empty list.

OAuth login and validator callback handlers moved from
`org.apache.kafka.common.security.oauthbearer.secured` to
`org.apache.kafka.common.security.oauthbearer`.

Replace `delegation.token.master.key` with
`delegation.token.secret.key`.

### Authentication grants

OAuth supports the `jwt-bearer` grant as well as `client_credentials`, allowing
authentication without storing a cleartext client secret in configuration.

`client_credentials` grants also support client-assertion authentication for
identity providers that require assertions.

## Login modules and principals

`org.apache.kafka.disallowed.login.modules` is deprecated. Migrate policy to
`org.apache.kafka.allowed.login.modules`.

`KafkaPrincipalBuilder` extends `KafkaPrincipalSerde`. Every custom principal
builder must implement the serialization interface as well.
