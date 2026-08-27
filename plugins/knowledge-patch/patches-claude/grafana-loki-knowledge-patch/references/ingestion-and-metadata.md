# Ingestion, labels, and structured metadata

## Per-tenant time-sharded ingestion (3.4.0)

Enable long out-of-order ingestion per tenant:

```yaml
shard_streams:
  time_sharding_enabled: true
```

Loki injects a `__time_shard__` label so each generated stream spans at most
half of `max_chunk_age`, normally one hour. This prevents sufficiently old logs
from being rejected merely for falling too far behind the current stream.

The Loki Operator can enable time-based stream sharding as of 3.5.0.

## Ingest-time structured metadata extraction (3.4.0)

A per-tenant feature extracts fields into structured metadata during ingestion.
Sources can be ordinary labels, existing structured-metadata keys, or keys
parsed from `logfmt` and JSON lines.

Design extraction rules so that metadata remains queryable without multiplying
stream-label cardinality.

## OTLP and automatic labels

### Environment and log level (3.4.0)

OTLP ingestion includes `deployment.environment.name` in its default label set.
The Operator places the log-level attribute in structured metadata.

### Operator attribute dropping (3.5.0)

The Operator can drop OTLP attributes. This is classified as breaking, so
compare generated attributes, stream labels, metadata, and affected queries
when upgrading an Operator-managed deployment.

## Push-request and service-name behavior (3.4.0)

A push request with no streams returns HTTP 422. Clients must not treat an
empty batch as a successful no-op.

An automatically discovered `service_name` is retained for retention decisions
and usage tracking. Account for that retained identity when reasoning about
tenant usage or retention.

## Distributor limit enforcement (3.5.0)

Limits can be enforced in distributors or checked there in dry-run mode.
Aggregated-metric streams are exempt from ordinary label enforcement.

Rate-limit reasons identify stream labels rather than only a hash, improving
diagnosis. OTLP entry-metadata bytes are counted correctly, so capacity and
limits must include metadata overhead.

## Distributor request handling (3.6.0)

Set the uncompressed message-size ceiling with `MaxRecvMsgSize`. Size it for the
expanded request, not compressed wire bytes.

When the distributor truncates a log line, it marks that line with an
identifier. Preserve that signal in downstream processing and diagnostics.

## Policy-specific stream limits (3.6.0)

Stream limits can be overridden per ingestion policy. Default ingestion-policy
mappings merge with per-tenant mappings rather than being replaced wholesale,
so calculate effective behavior from both layers.

## Log-level and detected-field discovery

### Nested JSON levels (3.5.0)

Automatic log-level discovery recognizes nested JSON fields and removes colons
from detected levels.

### Numeric booleans and byte units (3.4.0, 3.6.0)

Detected fields recognize byte units. Detected labels accept numeric boolean
values.

## Structured-metadata normalization (3.6.0)

JSON strings placed in structured metadata are unescaped. When the same
metadata is sourced from both stream labels and extracted fields, Loki
suppresses the duplicate.

The pattern ingester emits detected level as structured metadata. Include this
source when designing metadata schemas for persisted patterns.

## Internal aggregated-metric labels (3.6.0)

The internal `__aggregated_metric__` label is hidden from `/series` and
`/labels`. Do not depend on those endpoints to reveal or filter by the internal
marker.

## Parsed-label precedence (3.7.0)

Parsed labels no longer override same-named structured metadata. This is a
breaking semantic change. Make collisions explicit in parsers and tests so
queries use the intended value.
