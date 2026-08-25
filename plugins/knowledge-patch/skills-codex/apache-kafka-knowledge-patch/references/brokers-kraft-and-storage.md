# Brokers, KRaft, and storage

## Removed settings and changed defaults

Remove `log.message.format.version`, `message.format.version`,
`offsets.commit.required.acks`, and
`log.message.timestamp.difference.max.ms`. Replace the last setting with:

- `log.message.timestamp.before.max.ms`
- `log.message.timestamp.after.max.ms`

The after-limit defaults to one hour. With
`message.timestamp.type=CreateTime`, records more than one hour in the future
are rejected.

The minimum for `segment.bytes` and `log.segment.bytes` is 1 MB.
`num.recovery.threads.per.data.dir` defaults to `2` rather than `1`.

The remote log manager copier and expiration pools default to `10` and reject
values below `1`. The older `remote.log.manager.thread.pool.size` default
changed from `10` to `2`, but that property is now deprecated; configure
follower work through `remote.log.manager.follower.thread.pool.size`.

`log.cleaner.enable` is deprecated and should not be set to `false`. Its
eventual removal also makes `1` the lower bound for `log.cleaner.threads`.

## Eligible Leader Replicas

Eligible Leader Replicas let the KRaft controller elect replicas known to be
safe even when they are outside the ISR. New clusters enable ELR by default.
Enabling it removes an existing broker-level `min.insync.replicas`; preserve
that policy by setting the value at cluster level.

## Configuration validation and retention

Most LIST-typed settings reject null unless their default is null. Where
duplicates are unsupported, Kafka ignores configured duplicates with a
warning. Empty lists are rejected when they would prevent correct operation.
Several comma-separated STRING settings are now typed as LIST. The minimum for
`num.replica.fetchers` is `1`.

An empty `cleanup.policy` means infinite retention, equivalent to both
`retention.ms=-1` and `retention.bytes=-1`.

With remote storage, local segments continue to follow
`log.local.retention.ms` and `log.local.retention.bytes`. Without remote
storage, those local segments are not deleted automatically, although
`deleteRecords` can remove them.

## KRaft controller operation

### Automatic voter joining

`controller.quorum.auto.join.enable` allows a controller to join the voter set
automatically and defaults to `false`:

```properties
controller.quorum.auto.join.enable=true
```

When enabled, stop a controller before removing it from the voter set;
otherwise it immediately joins again.

### Dynamic controller configuration

`kafka-configs.sh --alter --delete-config` treats a missing key as a no-op
instead of raising `InvalidConfigurationException`. This also applies while
managing an offline broker through `--bootstrap-controller`.

Dynamic quorum controllers can receive dynamic configuration changes. Earlier
support was limited to brokers and static quorum controllers.

### Fetch response limits

Use `controller.quorum.fetch.max.bytes` to cap data returned by KRaft Fetch
requests and `controller.quorum.fetch.snapshot.max.bytes` to cap data returned
by FetchSnapshot requests.

## Group and share coordinators

### Small-cluster share state

Share groups are production-ready. On clusters with fewer than three brokers,
set the internal-topic values before creating the first share group:

```properties
share.coordinator.state.topic.replication.factor=1
share.coordinator.state.topic.min.isr=1
```

`__share_group_state` is created automatically, and its normal defaults require
three brokers.

### Cached resources and assignment work

`group.coordinator.cached.buffer.max.bytes` and
`share.coordinator.cached.buffer.max.bytes` bound coordinator buffers retained
for reuse.

`group.coordinator.background.threads` controls regular-expression
subscription updates and defaults to two threads instead of the former fixed
single thread.

These settings control assignment update intervals:

- `group.consumer.assignment.interval.ms`
- `group.share.assignment.interval.ms`
- `group.streams.assignment.interval.ms`

Each defaults to one second, replacing the former effective value of zero.
Corresponding broker bounds and group-level settings are available.

### Append buffers

`group.coordinator.append.max.buffer.size` and
`share.coordinator.append.max.buffer.size` cap each coordinator's maximum
append buffer. Monitor the corresponding buffer-usage metrics when tuning
these limits.

## Remote logs and tiered storage

### Metadata implementation contract

Custom `RemoteLogMetadataManager` implementations must implement
`nextSegmentWithTxnIndex`. It returns next-segment metadata carrying a
transaction index for `READ_COMMITTED` consumers.

`TopicBasedRemoteLogMetadataManager` can defer initialization with the
`BrokerReadyCallback` interface until the broker is fully ready. Custom
remote-log integrations should use this to avoid premature initialization
failure.

### Metadata topic and Admin client

`remote.log.metadata.topic.min.isr` controls the minimum ISR for
`__remote_log_metadata` and defaults to `2`. Existing topics do not
automatically acquire the intended value; inspect and, if necessary, correct
their `min.insync.replicas` with `kafka-configs.sh`.

Settings under `remote.log.metadata.admin.` independently configure the Admin
client used by `TopicBasedRemoteLogMetadataManager`.

### Follower bootstrap

`follower.fetch.last.tiered.offset.enable` is dynamic and defaults to `false`.
When enabled with tiered storage, a new follower with no local data begins at
the leader's earliest pending-upload offset instead of downloading data that
already exists remotely.

`ListOffsets` version 11 provides
`EARLIEST_PENDING_UPLOAD_TIMESTAMP` (`-6`) so clients can query that offset.

## Log-directory maintenance

Kafka supports cordoning log directories. Cordon a directory to take it out of
normal placement workflows while performing operational maintenance.
