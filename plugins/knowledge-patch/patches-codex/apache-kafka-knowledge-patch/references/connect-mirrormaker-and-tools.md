# Connect, MirrorMaker, and tools

## Kafka Connect compatibility

### REST and task extension changes

The deprecated endpoint:

```text
GET /connectors/{connector}/tasks-config
```

is removed. Use:

```text
GET /connectors/{connector}/tasks
```

Custom tasks must not override
`SinkTask.onPartitionsRevoked(Collection)` or
`SinkTask.onPartitionsAssigned(Collection)`.

The single-argument `SourceTask.commitRecord(SourceRecord)` hook is removed.

### Transform and API migrations

`ReplaceField` uses `include` and `exclude`; its `whitelist` and `blacklist`
settings are removed.

Connect uses Jakarta EE 10 APIs rather than the former Java EE surface and
requires Java 17. Recompile and test integrations that directly depend on
those APIs.

All plugin types implement the `ConnectPlugin` interface, providing
configurable components with a common method set and improving discovery.

### Plugin versions

A Connect cluster can install and run multiple versions of the same plugin.
This applies to connectors, converters, transformations, and predicates, and
allows plugin upgrades and rollback without maintaining separate clusters.

### Client override policy

`AllowlistConnectorClientConfigOverridePolicy` restricts connector client
overrides through `connector.client.config.override.allowlist`.

This policy becomes the default in Kafka 5.0, when
`PrincipalConnectorClientConfigOverridePolicy` is removed.

### JSON schemas

`JsonConverter` accepts optional `schema.content`, allowing the schema to be
provided externally instead of embedded in every JSON message.

## MirrorMaker

### Migration to MirrorMaker 2

MirrorMaker 1 is removed. Use the Connect-based MirrorMaker 2.

`MirrorSourceConnector` removes `use.incremental.alter.configs`, requires
target brokers 2.3 or later, and always includes the source alias in its
metrics.

Replace:

- `config.properties.blacklist` with its `exclude` counterpart
- `topics.blacklist` with its `exclude` counterpart
- `groups.blacklist` with its `exclude` counterpart

Replication policies distinguish truly internal Kafka topics from names that
only look internal. Internal-looking user topics can now replicate. This
affects both `ReplicationPolicy` and `DefaultReplicationPolicy`.

### Metric names

Existing MirrorMaker metric names are deprecated for removal in Kafka 5.0.
`metric.names.formats` lets `MirrorSourceConnector` and
`MirrorCheckpointConnector` opt in to the replacement names.

`RemoteClusterUtils.translateOffsets()` can translate committed offsets for
several consumer groups in one request.

## Command-line compatibility

### Removed arguments and interfaces

`--bootstrap-server` accepts comma-separated endpoints only, not a
space-separated list.

Use these replacements:

| Tool | Removed or deprecated | Replacement |
| --- | --- | --- |
| console consumer | `--whitelist` | `--include` |
| replica verification | `--topic-white-list` | `--topics-include` |
| verifiable consumer | `--broker-list` | `--bootstrap-server` |
| ACL tool | `--authorizer`, `--authorizer-properties`, `--zk-tls-config-file` | `--bootstrap-server` or `--bootstrap-controller` |
| topics tool | `kafka-topics --delete-config` | manage configuration through the supported configuration path |

Custom console-producer readers must implement
`org.apache.kafka.tools.api.RecordReader`. Custom dump-log decoders must
implement `org.apache.kafka.tools.api.Decoder`.

Formatter classes moved under `org.apache.kafka.tools.consumer`.

Old package redirections were removed for the feature, cluster, latency,
state-change, streams-reset, and JMX tools. Update direct Java invocations and
scripts to their current packages.

`ZkSecurityMigrator` is removed.

`kafka-configs.sh` requires broker support for `incrementalAlterConfigs`, which
means Kafka 2.3 or later.

### Standardized tool arguments

The old forms in this table are scheduled for removal in Kafka 5.0:

| Tool or scope | Old | Current |
| --- | --- | --- |
| console producer | `--max-partition-memory-bytes` | `--batch-size` |
| console consumer and share consumer | `--property` | `--formatter-property` |
| console producer | `--property` | `--reader-property` |
| consumer/share-consumer performance | `--messages` | `--num-records` |
| console tools | `--consumer-property`, `--producer-property` | `--command-property` |
| producer performance | `--producer-props` | `--command-property` |
| `kafka-cluster` | `--config` | `--command-config` |

The consumer performance tools also accept `--command-property`.
`ConsumerPerformance` accepts `--include` with a topic regular expression
instead of only one `--topic`.

For configuration files, use `--consumer.config` or `--producer.config` with
console, performance, and verifiable tools; use `--admin.config` with leader
election and `--config-file` with the Streams application reset tool.

## Test and benchmark tools

### Producer performance

The producer performance test accepts optional `--warmup-records`. Warmup
records are excluded from steady-state statistics so startup effects do not
distort the results.

### End-to-end latency

`EndToEndLatency` uses named arguments, supports optional message keys and
headers, and uses Kafka's standardized command-line names.
