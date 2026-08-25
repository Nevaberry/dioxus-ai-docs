# Brokers, Coordinators, and Storage

Use this reference for broker configuration migrations, KRaft quorum behavior, coordinator resource controls, retention, and remote or tiered storage.

## Removed broker settings and changed defaults

Remove these obsolete settings: (4.0-upgrade)

- `log.message.format.version` and `message.format.version`
- `offsets.commit.required.acks`
- `log.message.timestamp.difference.max.ms`

Replace the timestamp-difference setting with independent limits:

```properties
log.message.timestamp.before.max.ms=...
log.message.timestamp.after.max.ms=...
```

`log.message.timestamp.after.max.ms` now defaults to one hour. With `message.timestamp.type=CreateTime`, records dated more than one hour in the future are rejected unless the limit is changed.

Other default and validation changes include: (4.0-upgrade)

- The remote log manager copier and expiration pools default to `10` and reject values below `1`.
- `remote.log.manager.thread.pool.size` defaults to `2`, down from `10`; it is later deprecated in favor of `remote.log.manager.follower.thread.pool.size`. (4.2-upgrade)
- `segment.bytes` and `log.segment.bytes` have a 1 MB minimum.
- `num.recovery.threads.per.data.dir` defaults to `2`, up from `1`.

`log.cleaner.enable` is deprecated and should not be set to `false`. Its eventual removal also makes `1` the minimum for `log.cleaner.threads`. (4.1-upgrade)

## LIST validation and retention semantics

Most LIST-valued settings now reject null unless their declared default is null. Where duplicates are unsupported, Kafka ignores configured duplicates and logs a warning. Settings for which an empty list would prevent operation now reject it. Some formerly comma-separated STRING settings are typed as LIST, and `num.replica.fetchers` has a minimum of `1`. (4.2-upgrade)

An empty `cleanup.policy` means infinite retention, equivalent to both of these limits: (4.2-upgrade)

```properties
retention.ms=-1
retention.bytes=-1
```

When remote storage is enabled, local segments still obey `log.local.retention.ms` and `log.local.retention.bytes`. Without remote storage, an empty cleanup policy prevents automatic deletion, although `deleteRecords` can still remove records.

## Eligible Leader Replicas

Eligible Leader Replicas let the KRaft controller elect a replica known to be safe even when it is outside the ISR, avoiding data loss. The capability becomes available with the 4.0 protocol finalization. (4.0-upgrade)

New clusters enable ELR by default. Enabling it removes a previously defined broker-level `min.insync.replicas`; if that minimum must remain, set it at cluster level. (4.1-upgrade)

## KRaft controller lifecycle and limits

Dynamic controllers can join the KRaft voter set automatically: (4.2-upgrade)

```properties
controller.quorum.auto.join.enable=true
```

`controller.quorum.auto.join.enable` defaults to `false`. When it is enabled, shut down a controller before removing it from the voter set; an active controller otherwise joins again automatically.

Kafka 4.3 adds response-size caps for KRaft replication: (4.3.0)

```properties
controller.quorum.fetch.max.bytes=...
controller.quorum.fetch.snapshot.max.bytes=...
```

These limit data returned by KRaft Fetch and FetchSnapshot requests, respectively.

## Dynamic configuration behavior

`kafka-configs.sh --alter --delete-config` treats a missing key as a successful no-op rather than throwing `InvalidConfigurationException`. This also applies when configuring an offline broker through `--bootstrap-controller`. Dynamic quorum controllers can receive dynamic configuration changes; the earlier behavior supported only brokers and static quorum controllers. (4.3-upgrade)

## Coordinator memory and assignment controls

Kafka 4.3 introduces limits for reusable cached coordinator buffers: (4.3-upgrade)

```properties
group.coordinator.cached.buffer.max.bytes=...
share.coordinator.cached.buffer.max.bytes=...
```

`group.coordinator.background.threads` governs regular-expression subscription updates and defaults to two threads, replacing the former fixed single worker.

Assignment refresh cadence can be configured separately by group type:

```properties
group.consumer.assignment.interval.ms=1000
group.share.assignment.interval.ms=1000
group.streams.assignment.interval.ms=1000
```

The settings default to one second rather than the previous effective zero interval. Corresponding broker-side bounds and group-level settings are available.

Separate append-buffer caps bound the largest buffers coordinators may use, and new metrics report their usage: (4.3.0)

```properties
group.coordinator.append.max.buffer.size=...
share.coordinator.append.max.buffer.size=...
```

## Share-group internal storage

Share groups are production-ready, but their automatically created `__share_group_state` topic assumes a three-broker cluster by default. Before the first share group on a smaller cluster, set both values: (4.2-upgrade)

```properties
share.coordinator.state.topic.replication.factor=1
share.coordinator.state.topic.min.isr=1
```

Choose values suitable for the actual cluster and durability requirements; `1` is the small single-broker example, not a universal production recommendation.

Kafka 4.3 adds group-level controls for share delivery and locks, plus broker-enforced minima and maxima: (4.3-upgrade)

- `share.delivery.count.limit` caps delivery attempts.
- `share.partition.max.record.locks` caps acquired-record locks.
- `share.renew.acknowledge.enable` controls renewal acknowledgements.

## Remote-log manager integration

Custom `RemoteLogMetadataManager` implementations must implement `nextSegmentWithTxnIndex`. It returns the next segment metadata that carries a transaction index, allowing `READ_COMMITTED` consumers to continue correctly. (4.0-upgrade)

`TopicBasedRemoteLogMetadataManager` can defer initialization through `BrokerReadyCallback` until the broker is fully ready, preventing custom integration startup failures. (4.2.0)

Configure the internal remote metadata topic with: (4.3-upgrade)

```properties
remote.log.metadata.topic.min.isr=2
```

The default is `2`. Existing `__remote_log_metadata` topics are not implicitly corrected; inspect and, if needed, update their `min.insync.replicas` through `kafka-configs.sh`.

Properties under `remote.log.metadata.admin.` independently configure the Admin client used by `TopicBasedRemoteLogMetadataManager`.

## Tiered-storage follower bootstrap

The dynamic broker setting below defaults to `false`: (4.3-upgrade)

```properties
follower.fetch.last.tiered.offset.enable=true
```

When enabled with tiered storage, a new follower that has no local data begins at the leader's earliest pending-upload offset. It avoids refetching data already stored remotely.

`ListOffsets` version 11 defines `EARLIEST_PENDING_UPLOAD_TIMESTAMP` with timestamp value `-6`, allowing a client to query that boundary directly.

## Log-directory maintenance and storage metrics

Kafka can cordon a log directory so normal placement workflows avoid it during operational maintenance. (4.3-upgrade)

Storage metrics now report how much of its configured maximum retention each topic partition consumes. (4.3.0)

In KRaft combined broker/controller mode, `RequestHandlerAvgIdlePercent` is normalized against the combined number of threads. Separate broker and controller metrics retain per-pool visibility. (4.2.0)
