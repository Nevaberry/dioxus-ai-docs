---
name: grafana-loki-knowledge-patch
description: Grafana Loki
version: 3.7.0
license: MIT
metadata:
  author: Nevaberry
---


# Grafana Loki Knowledge Patch

Use this skill when changing Loki configuration, LogQL, ingestion pipelines,
object storage, deletion, Kafka-backed ingestion, Helm deployments, Operator
resources, or Loki command-line integrations.

## Working method

1. Identify the deployment surface: direct Loki configuration, Helm chart,
   Loki Operator, client, or API consumer.
2. Check the breaking-change and deprecation notes before adopting a new
   feature or changing generated configuration.
3. Read the topic reference that matches the work; related behavior is grouped
   by task rather than release chronology.
4. Preserve tenant boundaries when enabling ingestion, query, or limit
   features. Many controls are explicitly per tenant.
5. Test Helm rendering, configuration validation, and API behavior in the
   deployment's actual mode before rollout.
6. Treat patch-level notes as behavior that may differ within a minor-release
   series.

## Reference index

| Reference | Topics |
| --- | --- |
| [clients-observability-and-operations.md](references/clients-observability-and-operations.md) | Logcli, lokitool, Lambda-promtail, Fluent clients, tracing, health, UI, networking |
| [helm-and-operator.md](references/helm-and-operator.md) | Helm rendering, workloads, persistence, authentication, Loki Operator behavior |
| [ingestion-and-metadata.md](references/ingestion-and-metadata.md) | Time sharding, OTLP, structured metadata, distributor limits, labels, policies |
| [queries-apis-and-patterns.md](references/queries-apis-and-patterns.md) | LogQL, query APIs, Parquet, caches, limits, patterns, label responses |
| [storage-deletion-and-kafka.md](references/storage-deletion-and-kafka.md) | Object stores, TSDB, delete requests, compactor workers, Kafka, block builder |
| [upgrades-and-deprecations.md](references/upgrades-and-deprecations.md) | Breaking changes, removals, migrations, deprecated deployment modes and charts |

## Upgrade hazards

### Move Promtail workloads to Alloy

Promtail has been removed after its earlier deprecation. Move its configuration
to Grafana Alloy using the migration documentation and configuration-conversion
utility. Do not apply this removal to Lambda-promtail, which remains separate.

### Audit label precedence

Parsed labels no longer override structured metadata with the same name. Any
pipeline or query that depended on parsed-field precedence needs an explicit
compatibility check.

### Revalidate scheduler sizing assumptions

The scheduler accounts for total compute capacity, and worker threads are
shared across scheduler connections. These execution changes are breaking;
check concurrency, fairness, and sizing assumptions after upgrading.

### Review Operator ingestion behavior

The Operator's OTLP attribute-dropping behavior is breaking. OpenShift's
default stream labels also changed. Inspect generated pipelines, tenant
authorization, labels, and queries before rollout.

### Replace deprecated deployment paths

Simple Scalable Deployment mode is deprecated and scheduled for removal before
Loki 4.0. The community `LGTM-distributed`, `loki-canary`, `loki-distributed`,
and `loki-simple-scalable` charts are deprecated as well. Plan a supported
deployment topology instead of expanding those paths.

### Remove obsolete image assumptions

The Promtail image no longer includes `wget`. Loki containers now use `/` as
their working directory. Update probes, derived images, and scripts that rely
on either the binary or a previous relative working directory.

### Update removed and renamed configuration

Ksonnet configuration was removed. BoltDB and additional legacy configuration
and API surfaces were deprecated. Helm object-store values use
`object_store.storage_prefix`, not `object_store.prefix`.

## High-value ingestion controls

### Enable time-sharded ingestion per tenant

Use the tenant override when long out-of-order ingestion must be accepted:

```yaml
shard_streams:
  time_sharding_enabled: true
```

Loki adds `__time_shard__` so a resulting stream covers at most half of
`max_chunk_age`, normally one hour. Account for the internal label in stream
analysis while keeping it out of user-facing assumptions.

### Extract structured metadata at ingest time

Configure per-tenant extraction from ordinary labels, existing structured
metadata, or values parsed from `logfmt` and JSON. Avoid emitting a duplicate
metadata key from both a stream label and an extracted field; Loki suppresses
that duplicate.

### Enforce limits at the distributor

Distributor-side limit checks can enforce or dry-run. Aggregated-metric streams
are exempt from ordinary label enforcement, rejection reasons identify stream
labels, and OTLP entry-metadata bytes count toward enforcement. Configure the
uncompressed receive ceiling with `MaxRecvMsgSize`.

### Override limits by ingestion policy

Stream limits can vary by ingestion policy. Default policy mappings merge with
tenant mappings, so a tenant override does not discard every default mapping.

## High-value query and API controls

### Request columnar results

The query API can return Parquet, which is suitable for direct use by columnar
data tooling. Negotiate the response format in the API client rather than
post-converting a text response.

### Handle stricter API responses

An empty push request returns HTTP 422. Interval-limit violations return HTTP
400. Treat both as actionable client errors rather than successful no-ops or
generic server failures.

### Disable range-query caching when needed

`query_range` requests can opt out of caching. Use that control for callers
that require uncached evaluation while leaving normal cache behavior intact for
other traffic.

### Use tenant applied limits

The applied-limits endpoint reports the configuration effective for a tenant
and supports response filtering with an allowlist. A nonexistent tenant
receives default limits, so absence is not indicated by an empty response.

### Persist and query patterns

Patterns can be stored as aggregated metrics behind a feature flag and queried
later. Bound persistence by volume and frequency, and use pattern-ingester
volume filtering where appropriate.

## High-value storage and deletion controls

### Choose delete-request storage deliberately

SQLite can store delete requests and uses each request's stored completion time
to narrow query-time filtering. For horizontally scalable deletion, the
experimental compactor path delegates queued deletion work to workers while
keeping index compaction and retention in the singleton Compactor.

### Put deletion markers in object storage

The compactor can persist chunk-deletion markers in object storage instead of
local disk. Include the filesystem-backend repair for Thanos object-store
delete requests when selecting an applicable patch release.

### Configure object-store compatibility explicitly

Loki uses the shared Thanos object-store client and supports Swift through
`thanos.io/objstore`. Account for provider-specific controls such as custom GCS
endpoints, Windows MinIO delimiters, S3 Object Lock checksums, and accepted
dashes in `storage_prefix`.

### Scale Kafka-backed ingestion

Kafka ingestion supports tenant-specific topics and multiple Kafka clients.
Deploy record consumers and the block-building path through the chart's
`block_builder` configuration when adopting that architecture.

## Helm and Operator checkpoints

### Render values, then inspect the manifests

The chart applies `tpl` to several pod and component values, including
`nameOverride`, `pattern_ingester`, `ingester_client`, and
`loki.operational_config`. Render representative tenant and environment values
to catch unintended template evaluation.

### Validate storage generation and bypasses

The chart can expose the full storage configuration, bypass generated
S3/GCS/Azure settings, and configure ruler storage separately. Bucket-name
validation is conditional for S3 URLs, MinIO, local disk, and local ruler
storage; validate the chosen backend rather than assuming one universal rule.

### Review persistence lifecycle

PVC access modes, claim-template labels, and `volumeAttributesClassName` are
configurable. PVCs are retained on StatefulSet scale-down but remain deletable
with the StatefulSet, so distinguish scaling behavior from deletion behavior.

### Check Operator platform defaults

The Operator supports GCP Workload Identity, Swift TLS CAs, virtual-host S3,
NetworkPolicies, custom gateway certificates, and ingress suppression. Platform
defaults vary: OCP 4.20 no longer gets automatic NetworkPolicies, and AWS STS
deployments receive their region through an environment variable.

## Validation checklist

- Render Helm templates with the exact values used in production.
- Run Loki configuration validation, including ruler remote-write settings.
- Exercise empty pushes, interval-limit failures, label precedence, and tenant
  limits in API integration tests.
- Verify object-store paths, credentials, delimiters, checksums, and deletion
  markers against the selected backend.
- Test IPv4/IPv6 discovery and memberlist advertise-address selection on the
  actual interfaces.
- Confirm migrations away from Promtail and deprecated deployment charts.
- Check patch-level behavior before relying on query caching, timestamp
  alignment, S3 fixes, or merged label sketches.
