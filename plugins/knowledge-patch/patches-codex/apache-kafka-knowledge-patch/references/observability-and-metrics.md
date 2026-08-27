# Observability and metrics

## JMX configuration and reporter defaults

Replace the removed JMX selection settings:

- `metrics.jmx.blacklist` becomes `metrics.jmx.exclude`
- `metrics.jmx.whitelist` becomes `metrics.jmx.include`

`auto.include.jmx.reporter` and the `JmxReporter(String)` constructor are
removed. `metric.reporters` defaults to
`org.apache.kafka.common.metrics.JmxReporter`.

MX4J support through `kafka_mx4jenable` is deprecated for removal in the next
major release.

## Metric name migrations

Replace these total metrics with their explicit nanosecond forms:

| Removed | Current |
| --- | --- |
| `bufferpool-wait-time-total` | `bufferpool-wait-time-ns-total` |
| `io-waittime-total` | `io-wait-time-ns-total` |
| `iotime-total` | `io-time-ns-total` |

The untagged AppInfo `start-time-ms`, `commit-id`, and `version` metrics are
deprecated for removal in Kafka 5.0. Their replacements carry a `client-id`
tag.

Update JMX domain selectors for:

| Metric | Former domain | Current domain |
| --- | --- | --- |
| `AssignmentsManager.QueuedReplicaToDirAssignments` | `org.apache.kafka.server` | `kafka.server` |
| `RemoteLogReaderTaskQueueSize` | `org.apache.kafka.storage.internals.log` | `kafka.log.remote` |
| `RemoteLogReaderAvgIdlePercent` | `org.apache.kafka.storage.internals.log` | `kafka.log.remote` |

Consumer topic metrics are also emitted with topic names unchanged instead of
replacing dots with underscores. Move dashboards to unchanged topic names; the
transformed variants are scheduled for removal in Kafka 5.0.

## Plugin-owned metrics

Producer, consumer, and Admin client plugins can implement `Monitorable` to
register metrics. Kafka adds plugin-identifying tags and exposes them under:

```text
kafka.CLIENT:type=plugins
```

Connect workers and connector plugins can also register metrics. Connectors
and tasks use their context; other plugin types implement `Monitorable`.

The broker-side client metrics plugin can collect Streams runtime metrics.
Use the numeric `INFO`-level counterparts for values broker-side collection
cannot represent as strings. The thread-level string metric remains available
through JMX.

## Feature and controller visibility

Kafka exports generic finalized, minimum-supported, and maximum-supported
level metrics for every production feature. Use them to observe upgrade and
downgrade compatibility without individually querying each feature.

`ControllerEventManager` and `MetadataLoader` expose `AvgIdleRatio`, where
`0.0` means always busy and `1.0` means always idle.

In KRaft combined mode, `RequestHandlerAvgIdlePercent` is normalized using the
combined broker-and-controller thread count. Separate broker and controller
metrics retain per-pool visibility.

## Telemetry cadence

Client telemetry receiver interfaces expose the push interval through their
receiver context. Custom receivers should expire stale metrics according to
the reporting cadence supplied by each client.

## Coordinator and group metrics

The group and share coordinator append-buffer settings have matching
buffer-usage metrics. Monitor those metrics when applying
`group.coordinator.append.max.buffer.size` or
`share.coordinator.append.max.buffer.size`.

Share groups persist share-partition lag metrics. Use them to track work
progress and identify partition imbalance.

Streams groups expose task assignment, revocation, and loss latency metrics
only while using the broker-driven Streams protocol. See the Streams reference
for their exact names and the `client-state` tag change.

## Storage metrics

Storage metrics expose the share of maximum retention currently consumed by
each topic partition.

In-memory Streams state stores expose the current key count.

The Streams `number-open-files` metric reports `-1` after the RocksDB API
transition removed the usable file-close ticker.

## Ratio interpretation

Streams thread and state-updater ratio metrics represent action time divided
by total elapsed time across the rolling window. Their effective observation
window is controlled by `metrics.sample.window.ms` and
`metrics.num.samples`; compare ratios only when those settings are understood.

Do not interpret `AvgIdleRatio` as an idle percentage metric with a different
scale: its documented range is already `0.0` through `1.0`.
