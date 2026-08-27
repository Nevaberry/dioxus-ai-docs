# Kafka Connect and MirrorMaker

Use this reference when upgrading Connect workers, connector extensions, converters, connector client overrides, or cross-cluster replication.

## Runtime and REST compatibility

Kafka Connect requires Java 17 and uses Jakarta EE 10 APIs rather than the previous Java EE APIs. Test integrations coupled to the old API packages before rollout. (4.0.0)

The deprecated task-configuration endpoint was removed: (4.0.0)

```text
GET /connectors/{connector}/tasks-config   # removed
GET /connectors/{connector}/tasks          # use this
```

## Task and transformation API removals

The `ReplaceField` transformation uses `include` and `exclude`; its `whitelist` and `blacklist` settings were removed. (4.0-upgrade)

Custom tasks must not override the removed `SinkTask.onPartitionsRevoked(Collection)` or `SinkTask.onPartitionsAssigned(Collection)` hooks. The single-argument `SourceTask.commitRecord(SourceRecord)` hook was also removed; update implementations to the supported callback surface. (4.0-upgrade)

## Plugin metrics and common interface

Connect worker and connector plugins can register their own metrics. Connectors and tasks register through their context; other plugin categories implement `Monitorable`. Kafka supplies plugin-identifying tags. (4.1.0)

All Connect plugin types implement `ConnectPlugin`, giving configurable components a shared method surface and improving plugin discovery. Account for the common interface in custom plugin hierarchies and scanners. (4.3.0)

## Side-by-side plugin versions

A Connect cluster can install and run multiple versions of the same plugin, including connectors, converters, transformations, and predicates. Use this for controlled plugin upgrades and rollback without creating a separate Connect cluster. Pin the intended version rather than relying on ambiguous discovery. (4.1.0)

## Connector client override policy

`AllowlistConnectorClientConfigOverridePolicy` restricts per-connector client overrides to names configured in: (4.2-upgrade)

```properties
connector.client.config.override.allowlist=...
```

This becomes the default policy in Kafka 5.0, when `PrincipalConnectorClientConfigOverridePolicy` is removed. Define the allowlist before that default changes if connectors depend on overrides.

## JSON schemas supplied out of band

`JsonConverter` accepts optional `schema.content`, allowing an external schema instead of embedding a schema object in every JSON message. Coordinate the supplied schema with producer and consumer expectations; the setting changes where the schema comes from, not schema compatibility rules. (4.2.0)

## MirrorMaker 2 migration

MirrorMaker 1 was removed. Use the Kafka Connect-based MirrorMaker 2. (4.0-upgrade)

`MirrorSourceConnector` made these compatibility changes: (4.0-upgrade)

- Removed `use.incremental.alter.configs`; it always relies on incremental alter configs and therefore requires target brokers 2.3 or later.
- Always adds the source alias to metrics.
- Renamed `config.properties.blacklist`, `topics.blacklist`, and `groups.blacklist` to their corresponding `exclude` settings.

Replication policies now distinguish actual internal Kafka topics from names that merely look internal. Internal-looking application topics can therefore replicate. Review filters and naming assumptions in both custom `ReplicationPolicy` implementations and `DefaultReplicationPolicy` deployments. (4.0-upgrade)

## Offset translation and metric names

`RemoteClusterUtils.translateOffsets()` accepts several consumer groups in one call, enabling batch translation of committed offsets during cross-cluster migration or failover. (4.3.0)

Existing MirrorMaker metrics are deprecated for removal in Kafka 5.0. Set `metric.names.formats` on `MirrorSourceConnector` and `MirrorCheckpointConnector` to opt into the new metric names, then migrate dashboards before the old names disappear. (4.3.0)
