# Security, Observability, and Tools

Use this reference for authentication and principal extensions, JMX or telemetry migrations, and Kafka command-line compatibility.

## OAuth and SASL configuration

SASL OAUTHBEARER token and JWKS endpoints are denied unless admitted through the JVM system property below, whose default is an empty list: (4.0-upgrade)

```text
org.apache.kafka.sasl.oauthbearer.allowed.urls
```

Set only the required endpoint URLs. Account for this property in broker and client JVM launch configuration, not only Kafka properties.

OAuth login and validator callback handlers moved from `org.apache.kafka.common.security.oauthbearer.secured` to `org.apache.kafka.common.security.oauthbearer`. Update imports and configured callback class names. (4.0-upgrade)

Kafka OAuth supports the `jwt-bearer` grant in addition to `client_credentials`, allowing authentication without a cleartext client secret in Kafka configuration. (4.1.0)

OAuth `client_credentials` grants also support client-assertion authentication for providers that require signed assertions. (4.3.0)

## Login modules, tokens, and principals

Replace the broker setting `delegation.token.master.key` with `delegation.token.secret.key`. (4.0-upgrade)

`org.apache.kafka.disallowed.login.modules` is deprecated. Define the accepted set through `org.apache.kafka.allowed.login.modules`. (4.2-upgrade)

`KafkaPrincipalBuilder` now extends `KafkaPrincipalSerde`. Every custom principal builder must implement the serialization and deserialization contract from `KafkaPrincipalSerde`, including builders that previously needed only principal construction. (4.2-upgrade)

## JMX reporter migration

Rename reporter filters: (4.0-upgrade)

```properties
metrics.jmx.exclude=...
metrics.jmx.include=...
```

`metrics.jmx.blacklist` and `metrics.jmx.whitelist` were removed. `auto.include.jmx.reporter` and the `JmxReporter(String)` constructor were also removed. `metric.reporters` now defaults to `org.apache.kafka.common.metrics.JmxReporter`; do not add compatibility code that expects the old auto-include switch.

MX4J enablement through `kafka_mx4jenable` is deprecated for removal in the next major release. Remove MX4J-specific startup dependencies. (4.2-upgrade)

## Metric name and unit migrations

Replace old time-total metrics with nanosecond-explicit names: (4.0-upgrade)

| Removed | Replacement |
| --- | --- |
| `bufferpool-wait-time-total` | `bufferpool-wait-time-ns-total` |
| `io-waittime-total` | `io-wait-time-ns-total` |
| `iotime-total` | `io-time-ns-total` |

Consumer topic metrics are emitted with unchanged topic names as well as legacy names that replace dots with underscores. Move monitoring to unchanged-name metrics; transformed names are removed in Kafka 5.0. (4.1.0)

Untagged AppInfo `start-time-ms`, `commit-id`, and `version` are deprecated for removal in 5.0. Their replacements include a `client-id` tag. Update queries and label cardinality assumptions. (4.2-upgrade)

JMX domain changes include: (4.2-upgrade)

- `AssignmentsManager.QueuedReplicaToDirAssignments` moves from `org.apache.kafka.server` to `kafka.server`.
- `RemoteLogReaderTaskQueueSize` and `RemoteLogReaderAvgIdlePercent` move from `org.apache.kafka.storage.internals.log` to `kafka.log.remote`.

`ControllerEventManager` and `MetadataLoader` expose `AvgIdleRatio`, where `0.0` means always busy and `1.0` means always idle. Do not invert this interpretation.

In combined KRaft mode, `RequestHandlerAvgIdlePercent` is normalized using the combined broker and controller thread count; separate broker and controller metrics retain per-pool visibility. (4.2.0)

Partition storage metrics report the fraction of maximum retention currently consumed. (4.3.0)

## Plugin and client telemetry

Producer, consumer, and Admin plugins can implement `Monitorable` to register metrics. Kafka adds tags identifying the plugin and exposes them under `kafka.CLIENT:type=plugins`. (4.1.0)

Connect connectors and tasks register metrics through their contexts; other Connect worker and connector plugin types implement `Monitorable`. Use the injected identity tags instead of inventing overlapping plugin labels. (4.1.0)

Client-telemetry receiver context exposes the negotiated push interval. Custom receivers can use the actual interval to expire stale series instead of relying on a fixed guess. (4.2.0)

Kafka publishes finalized, minimum-supported, and maximum-supported levels for every production feature. These generic metrics make upgrade and downgrade compatibility observable without individually querying each feature. (4.2.0)

Share groups persist share-partition lag metrics so monitoring can detect consumption delays and imbalance. (4.2.0)

## Bootstrap and option removal in Kafka tools

`--bootstrap-server` accepts a single comma-separated endpoint list, not endpoints separated by spaces. (4.0-upgrade)

Removed option migrations include: (4.0-upgrade)

- Console consumer `--whitelist` becomes `--include`.
- Replica verification `--topic-white-list` becomes `--topics-include`.
- Verifiable consumer `--broker-list` becomes `--bootstrap-server`.
- ACL tool `--authorizer`, `--authorizer-properties`, and `--zk-tls-config-file` are removed; connect through `--bootstrap-server` or `--bootstrap-controller`.
- `kafka-topics --delete-config` is deprecated.

`kafka-configs.sh` requires broker support for `incrementalAlterConfigs`, so its target brokers must be Kafka 2.3 or later. (4.0-upgrade)

## Custom tool extension APIs

Custom console producer readers implement `org.apache.kafka.tools.api.RecordReader`. Custom dump-log decoders implement `org.apache.kafka.tools.api.Decoder`. Consumer formatter classes moved under `org.apache.kafka.tools.consumer`. (4.0-upgrade)

Old package redirections were removed for the feature, cluster, latency, state-change, Streams reset, and JMX tools. Update scripts and Java launchers to their current entry points. `ZkSecurityMigrator` was removed. (4.0-upgrade)

## Standardized command-line names

The older forms below are deprecated for removal in Kafka 5.0. (4.2-upgrade)

### Record and formatter options

- Console producer `--max-partition-memory-bytes` becomes `--batch-size`.
- Console consumer and share consumer `--property` become `--formatter-property`.
- Console producer `--property` becomes `--reader-property`.
- Consumer and share-consumer performance tools replace `--messages` with `--num-records`.
- `ConsumerPerformance` accepts `--include` with a topic regular expression in place of a single `--topic`.

### Command properties

- Console-tool `--consumer-property` and `--producer-property` become `--command-property`.
- Producer-performance `--producer-props` becomes `--command-property`.
- Consumer and share-consumer performance tools also accept `--command-property`.

### Configuration files

- `kafka-cluster --config` becomes `--command-config`.
- Console, performance, and verifiable tools use `--consumer.config` or `--producer.config` as appropriate.
- Leader election uses `--admin.config`.
- The Streams application reset tool uses `--config-file`.

## Tool capabilities

The producer performance test accepts optional `--warmup-records`. Warmup sends are excluded from steady-state statistics so JVM and connection startup do not distort the result. (4.2.0)

`describeFeatures --node-id` reports the supported features of a particular broker, which is useful for finding mixed-node capability differences during transitions. (4.2.0)

`EndToEndLatency` uses named arguments, accepts optional record keys and headers, and aligns renamed arguments with common Kafka CLI conventions. Update positional invocations. (4.2.0)

`kafka-configs.sh --alter --delete-config` treats a missing key as an idempotent no-op, including configuration of an offline broker through `--bootstrap-controller`. (4.3-upgrade)
