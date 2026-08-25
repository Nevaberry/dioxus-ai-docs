---
name: grafana-loki-knowledge-patch
description: Grafana Loki
version: 3.7.0
license: MIT
metadata:
  author: Nevaberry
---


# Grafana Loki Knowledge Patch

Use this skill when implementing, upgrading, deploying, or operating Grafana
Loki and the work may depend on recent LogQL, ingestion, storage, Helm,
Operator, deletion, API, or command-line behavior. Inspect the deployment's
Loki and chart versions before applying version-sensitive guidance, then read
every topic reference relevant to the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migrations and breaking changes](references/migrations-and-breaking-changes.md) | Promtail, deployment modes, removed configuration, changed defaults, chart ownership, and upgrade hazards |
| [Helm and deployment](references/helm-and-deployment.md) | Chart rendering, workloads, probes, persistence, DNS, caches, storage wiring, and services |
| [Ingestion, labels, and limits](references/ingestion-labels-and-limits.md) | Stream sharding, structured metadata, relabeling, distributor limits, Kafka, policies, and label discovery |
| [Operator, integrations, and observability](references/operator-integrations-and-observability.md) | Loki Operator, OTLP, OpenTelemetry tracing, Fluent integrations, monitoring, networking, and Operational UI |
| [Queries, APIs, and command-line tools](references/queries-apis-and-cli.md) | LogQL semantics, query results, endpoints, caching, Patterns, `logcli`, `lokitool`, ruler checks, and label sketches |
| [Storage, deletion, and compaction](references/storage-deletion-and-compaction.md) | Object stores, Thanos clients, SQLite delete requests, scalable deletion, deletion markers, and index gateways |

## Handle breaking changes first

### Move Promtail users to Alloy

Promtail was deprecated after its code moved into Grafana Alloy and was removed
as of 3.7.3. Use the migration documentation and configuration-conversion
utility. Do not apply that removal to Lambda-promtail, which remains separate.

Audit Promtail image extensions and health checks independently: the image no
longer contains `wget`, so scripts, probes, and derived images must provide a
different client or package the tool themselves.

### Preserve label and query semantics

Parsed labels no longer replace same-named structured metadata. Treat this as a
breaking precedence change and update pipelines or assertions that relied on
the parsed value winning.

Range-query evaluation aligns timestamps to the step grid as of 3.7.3, and the
query engine no longer silently discards `OR` operations. Recheck golden
results, alert evaluations, and cache expectations around both changes.

### Recheck scheduler capacity assumptions

Scheduler accounting uses total compute capacity, and worker threads are
shared across all scheduler connections. Both execution changes are breaking;
revisit sizing, concurrency assumptions, and performance tests rather than
carrying forward per-connection worker calculations.

### Audit removed and deprecated deployment paths

- Simple Scalable Deployment is deprecated and scheduled for removal before
  Loki 4.0.
- The community `LGTM-distributed`, `loki-canary`, `loki-distributed`, and
  `loki-simple-scalable` charts are deprecated.
- Deprecated ksonnet configurations are removed.
- BoltDB storage, legacy configuration options, and legacy API endpoints are
  deprecated and require an upgrade audit.
- The open-source Loki chart moved to the
  `grafana-community/helm-charts` repository on March 16, 2026; the GEL chart
  remains maintained separately.

### Check Operator-specific breakage

Dropping OTLP attributes through the Operator is classified as breaking.
OpenShift's default stream labels also changed, so validate tenant selectors,
dashboards, alerts, and retention rules after an Operator upgrade.

On OCP 4.20, the Operator no longer creates NetworkPolicies automatically.
Supply the required policies explicitly when isolation depends on them.

### Update container-relative paths

Loki containers now use the filesystem root as their working directory.
Derived images, entrypoints, and scripts must not assume the previous relative
path base.

## Upgrade checklist

1. Identify the Loki binary, Helm chart, and Operator versions separately.
2. Read the migration reference and inventory Promtail, ksonnet, BoltDB,
   legacy endpoints, and deprecated chart or deployment-mode dependencies.
3. Compare values files with renamed and newly templated settings, especially
   `object_store.storage_prefix`, storage generation bypasses, ruler storage,
   authentication, caches, and workload persistence.
4. Validate ingestion with empty pushes, structured metadata, OTLP byte
   accounting, policy limits, Kafka topics, and time sharding.
5. Re-run representative LogQL queries for parsed-label precedence, range
   timestamps, `OR`, offsets, `approx_topk`, JSON parsing, and byte comparisons.
6. Exercise storage, compaction, retention, and delete-request workflows with
   the deployment's actual object-store client and filesystem behavior.
7. Check Operator-generated networking, certificates, object-store addressing,
   authorization, metrics authentication, and OpenShift-specific resources.
8. Verify probes, sidecars, relative paths, Services, PVC retention, DNS, and
   topology placement in rendered manifests before rollout.

## Ingestion quick reference

### Enable tenant-scoped time sharding deliberately

Set `shard_streams.time_sharding_enabled: true` for tenants that must accept
logs far outside the ordinary out-of-order window. Loki adds
`__time_shard__`, limiting each resulting stream to at most half of
`max_chunk_age`—normally one hour.

### Treat structured metadata as a first-class ingestion path

Tenant configuration can extract structured metadata from labels, existing
metadata, or fields parsed from JSON and `logfmt` lines. Account for metadata
bytes in OTLP limits, suppress duplicates sourced from both labels and
extracted fields, and expect JSON strings to be unescaped.

Automatic log-level discovery handles nested JSON, removes colons from detected
levels, and accepts numeric boolean detected-label values. The pattern ingester
can emit detected level as structured metadata.

### Place and explain distributor enforcement

Limits may be enforced in distributors or checked there in dry-run mode.
Aggregated metric streams bypass ordinary label enforcement, and rate-limit
reasons identify stream labels rather than only a hash. Configure the
uncompressed receive ceiling with distributor `MaxRecvMsgSize` and recognize
the identifier placed on truncated lines.

### Merge policy mappings

Per-policy stream limits can override ingestion limits. Per-tenant
ingestion-policy mappings merge with defaults; they do not replace the default
mapping wholesale.

## Query and API quick reference

### Review status-code and routing changes

- An empty push request returns HTTP 422.
- Interval-limit violations return HTTP 400.
- Label-values requests work with `server.http_path_prefix`.
- Aggregated metric queries are accepted only from Logs Drilldown.
- Requests for an unknown tenant through the applied-limits endpoint return
  default limits.

### Use corrected LogQL behavior

Offsets apply correctly to `last_over_time`, `first_over_time`, and
`quantile_over_time`; `approx_topk` is mapped in all cases; the query-path JSON
parser preserves log lines; zero-byte comparisons are valid; and detected
fields recognize byte units.

Query APIs can return Parquet for columnar consumers. Query-range requests can
disable caching as of 3.7.3, and multi-tenant requests are accepted by the
Patterns API.

### Preserve label sketches

In 3.7.6, query-range `MergeLabels` preserves sketch data while merging label
responses. Consumers should use the returned sketch instead of assuming merged
results omit it.

## Storage and deletion quick reference

### Match the object-store client to its compatibility details

Loki moved object-store access to the shared Thanos client and added Swift via
`thanos.io/objstore`. Verify provider-specific behavior: custom GCS endpoints,
Swift TLS CAs, Windows MinIO delimiters, S3 region preservation, Object Lock
checksums, and legacy S3 index filenames all have distinct guidance.

### Scale deletion without moving singleton work

The experimental scalable deletion path delegates queued delete work from the
Compactor to workers. Index compaction and retention remain in the singleton
Compactor. SQLite delete-request storage uses stored completion times to narrow
query-time filtering, while object-backed deletion markers avoid local-disk
state.

## Helm and Operator quick reference

### Render values before rollout

The chart applies `tpl` in more locations, including `nameOverride`, read,
write, backend, pattern-ingester, ingester-client, and operational
configuration. Render charts in CI to catch evaluation, namespace, generated
storage, and ownership differences.

### Validate workload lifecycle

Check startup and readiness probes, SingleBinary topology spreading, canary
Deployment mode, configurable init containers, PVC access modes and labels,
retention-on-scale-down behavior, `volumeAttributesClassName`, and per-workload
`dnsConfig`.

### Treat generated Operator resources as version-sensitive

The Operator can suppress ingress, customize gateway certificates, deploy
NetworkPolicies, configure virtual-host S3 and Swift TLS, and apply
OpenTelemetry authorization semantics. Metrics authentication no longer
depends on `kube-rbac-proxy` as of 3.7.3, and AWS STS deployments receive their
region through an environment variable.

## Route work to the detailed references

- For upgrade planning, removals, changed defaults, or compatibility audits,
  read `migrations-and-breaking-changes.md` first.
- For chart values, rendered resources, workloads, persistence, caches, and
  Services, read `helm-and-deployment.md`.
- For push paths, labels, structured metadata, limits, policies, or Kafka,
  read `ingestion-labels-and-limits.md`.
- For Loki Operator, OTLP, tracing, monitoring, Fluent, or Operational UI,
  read `operator-integrations-and-observability.md`.
- For LogQL, query APIs, labels, Patterns, ruler tooling, or CLI behavior,
  read `queries-apis-and-cli.md`.
- For object storage, index gateways, compaction, retention, or deletion,
  read `storage-deletion-and-compaction.md`.
