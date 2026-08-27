# Ingestion, Labels, and Limits

Use this reference for push-path design, tenant overrides, structured metadata,
distributor enforcement, Kafka ingestion, label discovery, and stream shaping.

## Time-shard long out-of-order streams

Since 3.4.0, time-sharded ingestion can be enabled per tenant:

```yaml
shard_streams:
  time_sharding_enabled: true
```

With `shard_streams.time_sharding_enabled`, Loki injects a `__time_shard__`
label. Each resulting stream spans at most half of `max_chunk_age`, normally
one hour. This keeps very old entries from being rejected merely for falling
too far behind within one long-lived stream.

The Loki Operator can enable this behavior for managed stacks as of 3.5.0.
Treat the generated tenant override and the stream-cardinality effect as part
of the rollout review.

## Extract structured metadata during ingestion

A tenant-scoped feature introduced in 3.4.0 can extract fields into structured
metadata. Sources can be:

- ordinary stream labels;
- existing structured-metadata keys;
- keys parsed from `logfmt` lines;
- keys parsed from JSON log lines.

In 3.6.0, JSON structured-metadata strings are unescaped, and duplicate
metadata is suppressed when the same item comes from both a stream label and
an extracted field. Test pipelines that previously observed escaped or
duplicated values.

Fluent Bit v4's `out_loki` plugin can send structured metadata. The pattern
ingester can emit a detected log level as structured metadata. Operator-managed
OTLP integration places the log-level attribute in structured metadata as of
3.4.0.

## Discover levels and fields

Automatic log-level discovery detects nested JSON fields and removes colons
from detected levels as of 3.5.0. Detected labels accept numeric boolean values
as of 3.6.0. Detected fields also recognize byte units, and LogQL can compare
against zero-byte values, following the 3.4.0 query and detection changes.

## Relabel and filter Lambda-promtail input

Lambda-promtail accepts Prometheus-style relabel configurations as of 3.4.0.
Use them to mutate or filter entries before sending them to Loki. Its Terraform
deployment also exposes an S3 bucket-notification filter-prefix variable, which
can narrow the object events delivered to the function.

Lambda-promtail is not included in Promtail's deprecation or removal. Do not
apply the Alloy migration requirement to this component solely because of its
name.

## Place limit checks in distributors

Since 3.5.0, limits can be enforced in distributors or evaluated there in
dry-run mode. Dry-run lets operators observe the effect before rejecting
traffic.

Aggregated metric streams are exempt from ordinary label enforcement.
Rate-limit reasons identify stream labels instead of exposing only a hash,
which makes rejected traffic actionable. OTLP entry-metadata bytes are counted
correctly toward the applicable limits.

The distributor adds `MaxRecvMsgSize` in 3.6.0 for the uncompressed inbound
message-size ceiling. Size this against expanded payloads, not merely compressed
wire bytes. The distributor also marks lines it truncates with an identifier so
downstream consumers can distinguish truncation.

Push requests with no streams return HTTP 422 as of 3.4.0. Treat that response
as invalid input rather than a successful no-op.

## Preserve service identity

An automatically discovered `service_name` is retained for retention decisions
and usage tracking as of 3.4.0. Account for the retained identity when
validating usage attribution and retention behavior.

## Configure policy-specific limits

As of 3.6.0, stream limits can be overridden per ingestion policy. Default
policy mappings merge with tenant-specific mappings rather than being replaced
by them. Compute the effective merged mapping before diagnosing an unexpected
limit, and avoid assuming a tenant block erases every default.

## Use tenant-specific Kafka topics

Kafka-backed ingestion supports tenant-specific topics as of 3.5.0. Choose the
topic mapping alongside tenant isolation, capacity, retention, and operational
ownership.

In 3.6.0, Loki components can consume Kafka records and maintain multiple Kafka
clients. The Helm chart exposes `block_builder` configuration for deploying
this path. Validate client lifecycle, topic routing, and block-builder topology
together.

## Hide internal aggregated-metric labels

The internal `__aggregated_metric__` label is hidden from `/series` and
`/labels` as of 3.6.0. Do not build discovery clients that require the internal
label to appear in those responses, even though aggregated metric streams have
special enforcement behavior during ingestion.

## Handle parsed-label collisions

In 3.7.0, a parsed label no longer overrides structured metadata with the same
name. This is a breaking precedence rule. Avoid ambiguous duplicate names when
possible; otherwise expect structured metadata to retain precedence and update
tests and query assumptions.

## Ingestion validation checklist

- Test long out-of-order entries with and without tenant time sharding.
- Measure the cardinality introduced by `__time_shard__`.
- Verify JSON and `logfmt` extraction, unescaping, and duplicate suppression.
- Include OTLP metadata bytes in limit tests.
- Exercise distributor enforcement and dry-run with aggregated metric streams.
- Send an expanded payload near `MaxRecvMsgSize` and inspect truncated-line
  identifiers.
- Resolve the merged default and tenant policy mappings.
- Validate tenant Kafka topics with every deployed Kafka client and block
  builder.
- Recheck label discovery and collision behavior through `/series`, `/labels`,
  and representative LogQL queries.
