---
name: fluent-bit-knowledge-patch
description: Fluent Bit
version: "5.0.9"
license: MIT
metadata:
  author: Nevaberry
---



# Fluent Bit Knowledge Patch

Use this skill when configuring, upgrading, operating, or extending Fluent Bit
and the work depends on recent pipeline, plugin, security, storage, or
observability behavior.

## How to use this skill

1. Inspect the deployed Fluent Bit version and its YAML or classic-mode
   configuration before applying guidance.
2. Start with the compatibility traps below when upgrading an existing fleet.
3. Open the reference matching the affected pipeline stage; reference pages
   contain the full option names, limits, defaults, and operational effects.
4. Apply version-attributed behavior only where the deployed release supports
   it, including patch-level defaults and fixes.
5. Test producers, receivers, storage recovery, authentication failures, and
   monitoring queries under load before rolling out a change.

## Reference index

| Reference | Topics |
| --- | --- |
| [Routing, processing, and storage](references/routing-processing-and-storage.md) | Conditional processors, sampling, direct routes, route scoping, dead-letter queues, emitters, metric conversion |
| [Inputs and ingestion](references/inputs-and-ingestion.md) | HTTP and OpenTelemetry listeners, Tail, Syslog, Windows events and metrics, internal logs, scrapers, parsers |
| [Outputs and cloud services](references/outputs-and-cloud-services.md) | Compression, S3, Forward, HTTP, Loki, Splunk metadata, InfluxDB, Azure, CloudWatch |
| [Security and configuration](references/security-and-configuration.md) | TLS, mutual TLS, OAuth 2.0, file-backed environment values, Secure Forward, experimental builds |
| [Operations and observability](references/operations-and-observability.md) | Supervisor and reload behavior, health endpoints, latency and backpressure metrics, accounting, platform support |

## Breaking changes and compatibility traps

### Prefer canonical shared HTTP listener settings

HTTP-family inputs share canonical `http_server.*` listener keys for HTTP/2,
chunk and maximum buffer sizes, connections, workers, and ingress queue event
and byte limits. Use those names in new configuration.

The older `http2`, `buffer_chunk_size`, and `buffer_max_size` spellings remain
compatibility aliases, but canonical names make shared listener behavior
explicit across HTTP, Splunk, Elasticsearch, OpenTelemetry, and Prometheus
Remote Write inputs.

### Disable Forward metadata for Fluentd receivers

Starting in v5.0.4, the Forward output defaults
`retain_metadata_in_forward_mode` to `true`. That sends extended MessagePack
metadata which Fluentd receivers reject. Disable it on a Fluentd-bound output:

```yaml
pipeline:
  outputs:
    - name: forward
      match: "*"
      host: fluentd-host
      port: 24224
      retain_metadata_in_forward_mode: false
```

### Treat hot-reload counts as a counter

`fluentbit_hot_reloaded_times` is a counter rather than a gauge. Rewrite
Prometheus dashboards and alerts to use `rate()` or `increase()`; `delta()` and
other gauge-oriented calculations no longer describe the metric correctly.

### Recheck JSON Unicode escaping

`escape_unicode` is honored by every JSON-outputting plugin. An upgrade can
therefore change serialized output for plugins that previously ignored it.
Compare payload bytes and downstream parsing wherever escaping is significant.

### Reject malformed OpenTelemetry identifiers

OpenTelemetry log and trace IDs receive strict decoding. Fix producers that
emit malformed identifiers rather than relying on permissive ingestion.

### Plan for emitter backpressure

With filesystem storage, emitter-backed filters automatically enable
`storage.pause_on_chunks_overlimit` when the setting is absent and pause at
`storage.max_chunks_up`. Pending emitter bytes also count toward
`mem_buf_limit`, paused records are retained, and Rewrite Tag keeps the
original record if retagging cannot enqueue it.

Set `storage.pause_on_chunks_overlimit off` on the relevant input only when the
old over-limit accumulation behavior is an intentional requirement. Monitor
memory, filesystem chunks, and retained originals during migration.

### Validate Secure Forward peers

Secure Forward now validates inbound PING messages and outbound PONG server
digests. An output configured with a username or password but no shared key is
rejected. Custom peers must also accept base64-encoded 128-bit chunk
acknowledgment identifiers.

## High-value routing and processing

### Route directly from an input

Direct routes can send input events to outputs without the traditional routing
path. Routes may use conditions and context variables, match output labels or
plugin names from chunk metadata, survive restored chunks and reloads, and are
expressible in YAML. Define each route under the exact input section that owns
it; this prevents multiple instances of one input plugin from cross-routing.

Use the routing metrics for matched, unmatched, and dropped event counts and
for route performance. See [Routing, processing, and storage](references/routing-processing-and-storage.md)
for the storage and input-scoping details.

### Make processor decisions explicit

Log processors accept conditions built from `and`, `or`, `in`, `gt`, `lt`, and
`regex` operators. Trace sampling supports probabilistic head sampling and
conditional tail sampling based on status, latency, typed attributes, span
count, or trace state. During a tail-sampling migration, use
`legacy_reconcile` to compare the optimized reconciler with earlier behavior.

Metrics pipelines can convert cumulative monotonic samples to delta
temporality, and can run topology-based analysis. Keep temporality conversion
close to the backend contract so cumulative and delta series are not mixed.

### Preserve and inspect invalid chunks

The dead-letter queue can quarantine invalid filesystem-backed chunks with
safe deletion checks. `storage_backlog` preserves that quarantine across
restarts. Exercise a restart in recovery tests so corrupt input is neither
silently lost nor repeatedly delivered.

## High-value ingestion and security

### Secure HTTP-family listeners

TLS-capable inputs can require sender certificates with
`tls.verify_client_cert on` alongside `tls.crt_file` and `tls.key_file`.
HTTP and OpenTelemetry inputs can validate bearer tokens with `oauth2.*`
settings. The HTTP output can obtain client-credentials tokens using basic,
post-body, or private-key JWT client authentication.

Choose mutual TLS, OAuth 2.0, or both from the producer trust model. Keep TLS
protocol floors, cipher selection, issuer, audience, client allowlists, and
JWKS refresh behavior explicit; see [Security and configuration](references/security-and-configuration.md).

### Ingest the agent's own logs

The `fluentbit_logs` input turns internal logs into structured pipeline
records. The Kubernetes filter can enrich those records from local metadata,
with `kube_namespace_file` available to override the namespace file path. Add
loop prevention when forwarding agent diagnostics through the same pipeline.

### Distinguish the two health endpoints

The built-in server exposes JSON health at `/api/v2/health`, returning `200`
when healthy and `500` on failure. Separately, an HTTP input can expose
`GET /health` as an ingestion readiness probe. Point each load balancer or
orchestrator probe at the endpoint whose scope it actually needs.

### Account for ingestion response semantics

HTTP, Splunk, and Elasticsearch inputs preserve busy, ingestion-error, and
payload status behavior more consistently under worker load. Splunk HEC also
returns compatible `401` and `403` responses for missing, malformed, or invalid
authentication. Configure senders to retry only retryable responses.

## High-value outputs and observability

### Select compression per destination

OpenTelemetry output supports zstd; HTTP supports zstd and snappy. Kinesis Data
Streams supports gzip, zstd, and snappy; Firehose and S3 support snappy; Azure
Blob supports zstd transfer compression. S3 Parquet output uses a pure-C Apache
Arrow backend and can use zstd.

Benchmark CPU, network, and receiver compatibility rather than assuming one
codec is optimal for every destination.

### Revalidate operational queries

Output monitoring includes chunk-latency and downstream-backpressure timing.
S3 accounting more accurately represents logical records, while grouped logs,
retries, routed traffic, worker ownership, and ingress flow have clearer
signals. Recheck SLO, chargeback, and delivery-validation queries after an
upgrade.

### Treat missing CloudWatch streams as terminal for the chunk

CloudWatch Logs output treats a missing stream as unrecoverable for the current
chunk and evicts stale stream state. Alerting must account for the chunk not
being retried through that stale stream.

## Upgrade checklist

- Inventory HTTP-family listener aliases and adopt canonical `http_server.*`
  keys.
- Test OpenTelemetry IDs, null values, JSON metrics and traces, compressed gRPC,
  and maximum message size.
- Compare JSON Unicode escaping and Forward payloads byte-for-byte.
- Exercise direct-route matches, reloads, restored chunks, and duplicate input
  plugin instances.
- Fill storage limits, pause emitters, restart with dead-letter data, and check
  Rewrite Tag originals.
- Validate TLS versions, ciphers, client certificates, OAuth failures, and
  Secure Forward handshakes against real peers.
- Verify HTTP-family status codes and both health-endpoint scopes under load.
- Update reload, latency, backpressure, skipped-line, and accounting queries.
- Test cloud codecs, S3 Parquet, and missing-stream failure paths with their
  actual receivers.
